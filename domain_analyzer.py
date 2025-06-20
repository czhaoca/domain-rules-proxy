from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from urllib.parse import urlparse
import time
import os
import threading

def capture_request(request, domains):
    parsed_url = urlparse(request['url'])
    if parsed_url.netloc:
        domains.add(parsed_url.netloc)

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

    # Create a set to store the domains
    domains = set()
    
    # Enable CDP network domain
    driver.execute_cdp_cmd("Network.enable", {})
    
    # Create a lock for thread-safe domain set operations
    domains_lock = threading.Lock()

    try:
        # Define event handler for network requests
        def handle_request_will_be_sent(**kwargs):
            request_url = kwargs.get('request', {}).get('url', '')
            if request_url:
                parsed_url = urlparse(request_url)
                if parsed_url.netloc:
                    with domains_lock:
                        domains.add(parsed_url.netloc)
        
        # Add event listener for network requests
        driver.add_cdp_listener("Network.requestWillBeSent", handle_request_will_be_sent)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load and network requests to complete
        time.sleep(5)

        # Save the results
        base_domain = urlparse(url).netloc
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/{base_domain}_connected_domains.txt"
        with open(filename, 'w') as f:
            for domain in sorted(domains):
                f.write(f"{domain}\n")

        print(f"Analysis complete. Results saved to {filename}")
        return domains  # Return the set of domains for testing purposes

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    target_url = input("Enter the URL to analyze: ")
    try:
        analyze_domain(target_url)
    except ValueError as e:
        print(f"Error: {e}")