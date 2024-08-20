# Domain Analyzer Setup Guide

This guide provides detailed instructions for setting up and using the Domain Analyzer script.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- Google Chrome browser

## Installation

1. Clone the repository or download the script files to your local machine.

2. Open a terminal or command prompt and navigate to the project directory.

3. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

4. Install the required packages:
   ```
   pip install selenium webdriver-manager
   ```

## Configuration

The script uses default settings that should work for most users. However, you can modify the following parameters in the `domain_analyzer.py` file if needed:

- `chrome_options`: Add or remove Chrome options as needed.
- `time.sleep(5)`: Adjust the wait time after page load if necessary.

## Usage

1. Run the script:
   ```
   python domain_analyzer.py
   ```

2. When prompted, enter the full URL of the website you want to analyze (including `http://` or `https://`).

3. The script will run the analysis and save the results in a text file named `[analyzed_domain]_connected_domains.txt` in the same directory.

## Troubleshooting

- If you encounter a `WebDriverException`, ensure that you have Google Chrome installed on your system.
- If the script fails to capture any domains, try increasing the `time.sleep()` value to allow more time for the page to load completely.
- For SSL certificate errors, you may need to add the `--ignore-certificate-errors` option to `chrome_options`.

## Extending the Script

To capture IP addresses in addition to domains:

1. Add the `socket` library to the imports:
   ```python
   import socket
   ```

2. Modify the domain processing loop to include IP resolution:
   ```python
   domains_and_ips = set()
   for request in requests:
       parsed_url = urlparse(request['url'])
       if parsed_url.netloc:
           domain = parsed_url.netloc
           try:
               ip = socket.gethostbyname(domain)
               domains_and_ips.add(f"{domain} ({ip})")
           except socket.gaierror:
               domains_and_ips.add(domain)
   ```

3. Update the file writing section to use `domains_and_ips` instead of `domains`.

Note that adding IP resolution will significantly increase the runtime of the script.

## Security Considerations

- The script runs Chrome in headless mode, which is generally safe but could potentially execute malicious JavaScript. Always be cautious when analyzing untrusted websites.
- Ensure your Chrome browser is up-to-date to mitigate potential security risks.

For any additional help or to report issues, please open an issue in the project's GitHub repository.