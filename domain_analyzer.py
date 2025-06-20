from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from urllib.parse import urlparse
import time
import os
import threading
import socket
import ipaddress
from datetime import datetime
import argparse
import sys

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

def detect_page_type(url, driver):
    """
    Detect the type of page to apply appropriate interaction strategies
    """
    domain = urlparse(url).netloc.lower()
    
    # Check for specific page types
    if 'google.com' in domain:
        return 'search_engine'
    elif any(social in domain for social in ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']):
        return 'social_media'
    elif any(stream in domain for stream in ['youtube.com', 'netflix.com', 'twitch.tv', 'qq.com']):
        return 'streaming'
    elif any(shop in domain for shop in ['amazon.com', 'ebay.com', 'shopify.com']):
        return 'ecommerce'
    else:
        # Try to detect SPA characteristics
        try:
            # Look for common SPA indicators
            spa_indicators = driver.execute_script("""
                return {
                    hasReact: !!window.React,
                    hasVue: !!window.Vue,
                    hasAngular: !!window.angular || !!window.ng,
                    hasPushState: !!window.history.pushState,
                    hasFetch: !!window.fetch
                };
            """)
            if any(spa_indicators.values()):
                return 'spa'
        except:
            pass
    
    return 'generic'

def simulate_scroll_interactions(driver, wait_time=2):
    """
    Simulate scrolling to trigger lazy-loaded content
    """
    try:
        # Get initial page height
        initial_height = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll to middle of page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(wait_time)
        
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_time)
        
        # Check if new content was loaded (page height changed)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height > initial_height:
            # Content was loaded, scroll again
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait_time)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(wait_time / 2)
        
        return True
    except Exception as e:
        print(f"Scroll interaction failed: {e}")
        return False

def simulate_search_interaction(driver, page_type):
    """
    Simulate search interactions based on page type
    """
    try:
        search_selectors = [
            'input[name="q"]',  # Google, common search
            'input[type="search"]',
            'input[placeholder*="search" i]',
            'input[placeholder*="Search" i]',
            '#search',
            '.search-input',
            '[data-testid*="search"]'
        ]
        
        for selector in search_selectors:
            try:
                search_box = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                if page_type == 'search_engine':
                    search_box.clear()
                    search_box.send_keys("test query")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(3)  # Wait for search results
                elif page_type == 'ecommerce':
                    search_box.clear()
                    search_box.send_keys("laptop")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(2)
                elif page_type == 'streaming':
                    search_box.clear()
                    search_box.send_keys("music")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(2)
                else:
                    search_box.clear()
                    search_box.send_keys("test")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(2)
                
                return True
            except (TimeoutException, NoSuchElementException):
                continue
        
        return False
    except Exception as e:
        print(f"Search interaction failed: {e}")
        return False

def simulate_click_interactions(driver, max_clicks=3):
    """
    Simulate clicking on common interactive elements
    """
    clicked_count = 0
    
    try:
        # Common interactive element selectors (safe ones that won't navigate away)
        clickable_selectors = [
            'button:not([type="submit"]):not(.close):not(.exit)',
            '.btn:not(.btn-danger):not(.delete)',
            '[role="button"]:not(.close)',
            '.dropdown-toggle',
            '.menu-item',
            '.tab:not(.active)',
            '.accordion-header',
            'details summary',
            '[data-toggle]:not([data-toggle="modal"])'
        ]
        
        for selector in clickable_selectors:
            if clicked_count >= max_clicks:
                break
                
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements[:2]:  # Limit to 2 elements per selector
                    if clicked_count >= max_clicks:
                        break
                    
                    try:
                        # Check if element is visible and clickable
                        if element.is_displayed() and element.is_enabled():
                            # Scroll element into view
                            driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(0.5)
                            
                            # Try to click
                            element.click()
                            clicked_count += 1
                            time.sleep(2)  # Wait for any AJAX requests
                            
                    except (WebDriverException, Exception):
                        # Continue if click fails
                        continue
            except Exception:
                continue
        
        return clicked_count > 0
    except Exception as e:
        print(f"Click interaction failed: {e}")
        return False

def simulate_hover_interactions(driver):
    """
    Simulate hovering over elements to trigger dropdowns or tooltips
    """
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        
        hover_selectors = [
            '.dropdown',
            '.menu-item',
            'nav a',
            '.nav-link',
            '[data-hover]'
        ]
        
        actions = ActionChains(driver)
        
        for selector in hover_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements[:2]:  # Limit to 2 elements per selector
                    try:
                        if element.is_displayed():
                            actions.move_to_element(element).perform()
                            time.sleep(1)  # Wait for hover effects
                    except Exception:
                        continue
            except Exception:
                continue
        
        return True
    except Exception as e:
        print(f"Hover interaction failed: {e}")
        return False

def wait_for_network_idle(driver, max_wait=10, idle_time=2):
    """
    Wait for network activity to settle down
    """
    try:
        start_time = time.time()
        last_request_time = start_time
        
        # Simple approach: wait for a period without new network requests
        # In a real implementation, you might monitor CDP network events
        while time.time() - start_time < max_wait:
            # Check if page is still loading
            ready_state = driver.execute_script("return document.readyState")
            if ready_state == "complete":
                # Wait for idle time
                if time.time() - last_request_time >= idle_time:
                    break
            else:
                last_request_time = time.time()
            
            time.sleep(0.5)
        
        return True
    except Exception:
        return False

def simulate_user_interactions(driver, url, interaction_level='medium'):
    """
    Simulate various user interactions to trigger additional network requests
    """
    print(f"Simulating user interactions (level: {interaction_level})...")
    
    try:
        # Detect page type for targeted interactions
        page_type = detect_page_type(url, driver)
        print(f"Detected page type: {page_type}")
        
        interactions_performed = []
        
        if interaction_level in ['low', 'medium', 'high']:
            # Basic scrolling (always performed)
            if simulate_scroll_interactions(driver):
                interactions_performed.append("scrolling")
        
        if interaction_level in ['medium', 'high']:
            # Search interactions
            if simulate_search_interaction(driver, page_type):
                interactions_performed.append("search")
            
            # Hover interactions
            if simulate_hover_interactions(driver):
                interactions_performed.append("hover")
        
        if interaction_level == 'high':
            # Click interactions (more aggressive)
            if simulate_click_interactions(driver, max_clicks=5):
                interactions_performed.append("clicking")
        elif interaction_level == 'medium':
            # Limited click interactions
            if simulate_click_interactions(driver, max_clicks=2):
                interactions_performed.append("clicking")
        
        # Wait for any triggered network activity to complete
        wait_for_network_idle(driver)
        
        if interactions_performed:
            print(f"Performed interactions: {', '.join(interactions_performed)}")
        else:
            print("No interactions could be performed")
        
        return len(interactions_performed) > 0
        
    except Exception as e:
        print(f"User interaction simulation failed: {e}")
        return False

def analyze_domain(url, output_dir='data', interaction_level='medium', initial_wait=5, interaction_wait=3):
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
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for the initial page to load and network requests to complete
        print(f"Waiting {initial_wait}s for initial page load...")
        time.sleep(initial_wait)
        
        # Capture domains from initial load
        initial_domain_count = len(domains)
        initial_ip_count = len(direct_ips)
        
        # Perform user interactions if enabled
        if interaction_level and interaction_level != 'none':
            simulate_user_interactions(driver, url, interaction_level)
            
            # Wait for additional network requests triggered by interactions
            print(f"Waiting {interaction_wait}s for interaction-triggered requests...")
            time.sleep(interaction_wait)
        
        # Report on additional domains discovered through interactions
        interaction_domains = len(domains) - initial_domain_count
        interaction_ips = len(direct_ips) - initial_ip_count
        
        if interaction_domains > 0 or interaction_ips > 0:
            print(f"Interactions discovered {interaction_domains} additional domains and {interaction_ips} additional IPs")

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
            f.write(f"# Analysis for: {url}\n")
            f.write(f"# Interaction level: {interaction_level}\n")
            f.write(f"# Initial domains: {initial_domain_count}, interaction domains: {interaction_domains}\n")
            f.write(f"# Initial IPs: {initial_ip_count}, interaction IPs: {interaction_ips}\n\n")
            
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
            f.write(f"# Analysis for: {url}\n")
            f.write(f"# Interaction level: {interaction_level}\n\n")
            
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

def main():
    parser = argparse.ArgumentParser(
        description="Analyze domains and IP addresses from website network traffic with user interaction simulation"
    )
    parser.add_argument(
        'url', 
        nargs='?', 
        help='URL to analyze (if not provided, will prompt for input)'
    )
    parser.add_argument(
        '--interaction-level', 
        choices=['none', 'low', 'medium', 'high'], 
        default='medium',
        help='Level of user interaction simulation (default: medium)'
    )
    parser.add_argument(
        '--output-dir', 
        default='data',
        help='Output directory for results (default: data)'
    )
    parser.add_argument(
        '--initial-wait', 
        type=int, 
        default=5,
        help='Seconds to wait after initial page load (default: 5)'
    )
    parser.add_argument(
        '--interaction-wait', 
        type=int, 
        default=3,
        help='Seconds to wait after interactions (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Get URL from argument or prompt user
    if args.url:
        target_url = args.url
    else:
        target_url = input("Enter the URL to analyze: ")
    
    try:
        print(f"Starting analysis with interaction level: {args.interaction_level}")
        result = analyze_domain(
            target_url,
            output_dir=args.output_dir,
            interaction_level=args.interaction_level,
            initial_wait=args.initial_wait,
            interaction_wait=args.interaction_wait
        )
        
        print(f"\nAnalysis Summary:")
        print(f"  Total domains: {len(result['domains'])}")
        print(f"  Direct IPs: {len(result['direct_ips'])}")
        print(f"  Domains with resolved IPs: {len(result['domain_ip_mapping'])}")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()