from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from urllib.parse import urlparse
import time
import os

def analyze_domain(url):
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL. Please include http:// or https://")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the WebDriver for Chromium
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Enable network interception
    driver.execute_cdp_cmd("Network.enable", {})

    # Create a set to store the domains
    domains = set()

    # Define a callback to capture network requests
    def capture_request(request):
        parsed_url = urlparse(request['url'])
        if parsed_url.netloc:
            domains.add(parsed_url.netloc)

    # Add the listener
    driver.on_request = capture_request

    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load (adjust the time as needed)
        time.sleep(5)

        # Save the results
        base_domain = urlparse(url).netloc
        filename = f"{base_domain}_connected_domains.txt"
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