from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import json
import time

def analyze_domain(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Enable network interception
    driver.execute_cdp_cmd("Network.enable", {})

    # Create a list to store the requests
    requests = []

    # Define a callback to capture network requests
    def capture_request(request):
        requests.append(request)

    # Add the listener
    driver.execute_cdp_cmd("Network.setRequestInterception", {"patterns": [{"urlPattern": "*"}]})
    driver.on_request = capture_request

    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load (adjust the time as needed)
        time.sleep(5)

        # Process the captured requests
        domains = set()
        for request in requests:
            parsed_url = urlparse(request['url'])
            if parsed_url.netloc:
                domains.add(parsed_url.netloc)

        # Save the results
        base_domain = urlparse(url).netloc
        filename = f"{base_domain}_connected_domains.txt"
        with open(filename, 'w') as f:
            for domain in sorted(domains):
                f.write(f"{domain}\n")

        print(f"Analysis complete. Results saved to {filename}")

    finally:
        # Close the browser
        driver.quit()

# Example usage
if __name__ == "__main__":
    target_url = input("Enter the URL to analyze: ")
    analyze_domain(target_url)