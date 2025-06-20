from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from urllib.parse import urlparse
import time
import os
import threading
import socket
import ipaddress
from datetime import datetime

def capture_request(request, domains, direct_ips):
    parsed_url = urlparse(request['url'])
    if parsed_url.netloc:
        # Check if netloc is already an IP address
        try:
            netloc = parsed_url.netloc
            if netloc.startswith('['):
                # IPv6 address with brackets like [::1] or [::1]:8080
                if ']:' in netloc:
                    # Has port: [::1]:8080
                    ipv6_part = netloc.split(']:')[0] + ']'
                    ipaddress.ip_address(ipv6_part[1:-1])
                else:
                    # No port: [::1]
                    ipaddress.ip_address(netloc[1:-1])
                direct_ips.add(netloc)
            else:
                # IPv4 address, possibly with port
                hostname = netloc.split(':')[0]
                ipaddress.ip_address(hostname)
                direct_ips.add(netloc)
        except ValueError:
            # It's a domain name, not an IP
            domains.add(netloc)

def resolve_domain_to_ips(domain):
    """
    Resolve a domain to its IP addresses (both IPv4 and IPv6)
    Returns a dictionary with 'ipv4' and 'ipv6' lists
    """
    ips = {'ipv4': [], 'ipv6': []}
    
    try:
        # Get IPv4 addresses
        ipv4_info = socket.getaddrinfo(domain, None, socket.AF_INET)
        for info in ipv4_info:
            ip = info[4][0]
            if ip not in ips['ipv4']:
                ips['ipv4'].append(ip)
    except socket.gaierror:
        pass  # IPv4 resolution failed
    
    try:
        # Get IPv6 addresses
        ipv6_info = socket.getaddrinfo(domain, None, socket.AF_INET6)
        for info in ipv6_info:
            ip = info[4][0]
            if ip not in ips['ipv6']:
                ips['ipv6'].append(ip)
    except socket.gaierror:
        pass  # IPv6 resolution failed
    
    return ips

def resolve_domains_to_ips(domains):
    """
    Resolve multiple domains to their IP addresses
    Returns a dictionary mapping domains to their IPs
    """
    domain_ip_mapping = {}
    
    for domain in domains:
        # Skip if domain contains port number, extract just the hostname
        hostname = domain.split(':')[0]
        ips = resolve_domain_to_ips(hostname)
        if ips['ipv4'] or ips['ipv6']:
            domain_ip_mapping[domain] = ips
    
    return domain_ip_mapping

def analyze_domain(url, output_dir='data'):
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL. Please include http:// or https://")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")

    # Set up the WebDriver for Chromium
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Create sets to store domains and direct IPs
    domains = set()
    direct_ips = set()
    
    # Enable CDP network domain
    driver.execute_cdp_cmd("Network.enable", {})
    
    # Create locks for thread-safe operations
    domains_lock = threading.Lock()
    ips_lock = threading.Lock()

    try:
        # Define event handler for network requests
        def handle_request_will_be_sent(**kwargs):
            request_url = kwargs.get('request', {}).get('url', '')
            if request_url:
                parsed_url = urlparse(request_url)
                if parsed_url.netloc:
                    # Check if netloc is already an IP address
                    try:
                        netloc = parsed_url.netloc
                        if netloc.startswith('['):
                            # IPv6 address with brackets like [::1] or [::1]:8080
                            if ']:' in netloc:
                                # Has port: [::1]:8080
                                ipv6_part = netloc.split(']:')[0] + ']'
                                ipaddress.ip_address(ipv6_part[1:-1])
                            else:
                                # No port: [::1]
                                ipaddress.ip_address(netloc[1:-1])
                            with ips_lock:
                                direct_ips.add(netloc)
                        else:
                            # IPv4 address, possibly with port
                            hostname = netloc.split(':')[0]
                            ipaddress.ip_address(hostname)
                            with ips_lock:
                                direct_ips.add(netloc)
                    except ValueError:
                        # It's a domain name, not an IP
                        with domains_lock:
                            domains.add(netloc)
        
        # Add event listener for network requests
        driver.add_cdp_listener("Network.requestWillBeSent", handle_request_will_be_sent)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load and network requests to complete
        time.sleep(5)

        # Resolve domains to IP addresses
        print("Resolving domains to IP addresses...")
        domain_ip_mapping = resolve_domains_to_ips(domains)

        # Save the results
        base_domain = urlparse(url).netloc
        os.makedirs(output_dir, exist_ok=True)
        
        # Save domain results
        domains_filename = f"{output_dir}/{base_domain}_connected_domains.txt"
        with open(domains_filename, 'w') as f:
            for domain in sorted(domains):
                f.write(f"{domain}\n")

        # Save IP results
        ips_filename = f"{output_dir}/{base_domain}_connected_ips.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(ips_filename, 'w') as f:
            f.write(f"# IP addresses resolved at {timestamp}\n")
            f.write(f"# Analysis for: {url}\n\n")
            
            # Write direct IPs first
            if direct_ips:
                f.write("# Direct IP connections:\n")
                for ip in sorted(direct_ips):
                    f.write(f"{ip}\n")
                f.write("\n")
            
            # Write resolved IPs grouped by domain
            if domain_ip_mapping:
                f.write("# Domain-resolved IP addresses:\n")
                for domain in sorted(domain_ip_mapping.keys()):
                    ips = domain_ip_mapping[domain]
                    f.write(f"# {domain}\n")
                    
                    # Write IPv4 addresses
                    for ipv4 in ips['ipv4']:
                        f.write(f"{ipv4}  # {domain} (IPv4)\n")
                    
                    # Write IPv6 addresses
                    for ipv6 in ips['ipv6']:
                        f.write(f"{ipv6}  # {domain} (IPv6)\n")
                    
                    f.write("\n")

        # Create combined mapping file
        mapping_filename = f"{output_dir}/{base_domain}_domain_ip_mapping.txt"
        with open(mapping_filename, 'w') as f:
            f.write(f"# Domain to IP mapping generated at {timestamp}\n")
            f.write(f"# Analysis for: {url}\n\n")
            
            if direct_ips:
                f.write("Direct IP connections:\n")
                for ip in sorted(direct_ips):
                    f.write(f"  {ip}\n")
                f.write("\n")
            
            if domain_ip_mapping:
                f.write("Domain to IP mappings:\n")
                for domain in sorted(domain_ip_mapping.keys()):
                    ips = domain_ip_mapping[domain]
                    f.write(f"{domain}:\n")
                    
                    for ipv4 in ips['ipv4']:
                        f.write(f"  {ipv4} (IPv4)\n")
                    
                    for ipv6 in ips['ipv6']:
                        f.write(f"  {ipv6} (IPv6)\n")
                    
                    f.write("\n")

        print(f"Analysis complete. Results saved to:")
        print(f"  Domains: {domains_filename}")
        print(f"  IPs: {ips_filename}")
        print(f"  Mapping: {mapping_filename}")
        
        # Return results for testing
        return {
            'domains': domains,
            'direct_ips': direct_ips,
            'domain_ip_mapping': domain_ip_mapping
        }

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    target_url = input("Enter the URL to analyze: ")
    try:
        analyze_domain(target_url)
    except ValueError as e:
        print(f"Error: {e}")