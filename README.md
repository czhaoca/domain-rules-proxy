# Domain Analyzer

## Overview

 Domain Analyzer is a Python script designed to run on Ubuntu systems. It analyzes all domains connected when visiting a specified website. Using Selenium with Chrome in headless mode, it captures network requests made during page load and saves the list of unique domains to a text file.

## Features

- Runs on Ubuntu systems
- Simulates browser behavior using Selenium with Chrome in headless mode
- Captures all network requests during page load
- Extracts unique domains from the captured requests
- Saves results to a text file named after the analyzed domain

## Requirements

- Ubuntu 20.04 or later
- Python 3.6+
- Google Chrome or Chromium browser
- Selenium WebDriver
- ChromeDriver (automatically managed by webdriver_manager)

## Installation

1. Update your system:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

2. Install Python and pip if not already installed:
   ```
   sudo apt install python3 python3-pip -y
   ```

3. Install Chrome or Chromium:
   ```
   sudo apt install chromium-browser -y
   ```

4. Clone the repository or download the script files:
   ```
   git clone https://github.com/yourusername/ubuntu-domain-analyzer.git
   cd ubuntu-domain-analyzer
   ```

5. Install the required Python packages:
   ```
   pip3 install selenium webdriver-manager
   ```

## Usage

1. Run the script:
   ```
   python3 domain_analyzer.py
   ```

2. Enter the full URL of the website you want to analyze when prompted (including `http://` or `https://`).

3. The script will run the analysis and save the results in a text file named `[analyzed_domain]_connected_domains.txt` in the same directory.

## Configuration

The script uses default settings that should work for most users. However, you can modify the following parameters in the `domain_analyzer.py` file if needed:

- `chrome_options`: Add or remove Chrome options as needed.
- `time.sleep(5)`: Adjust the wait time after page load if necessary.

## Troubleshooting

- If you encounter a `WebDriverException`, ensure that Chromium is installed correctly:
  ```
  sudo apt install --reinstall chromium-browser
  ```
- If the script fails to capture any domains, try increasing the `time.sleep()` value to allow more time for the page to load completely.
- For SSL certificate errors, you may need to add the `--ignore-certificate-errors` option to `chrome_options`.

## Extending the Script

To capture IP addresses in addition to domains, modify the script as follows:

1. Add the `socket` library to the imports.
2. Modify the domain processing loop to include IP resolution.
3. Update the file writing section to include IP addresses.

Note that adding IP resolution will significantly increase the runtime of the script.

## Security Considerations

- The script runs Chrome in headless mode, which is generally safe but could potentially execute malicious JavaScript. Always be cautious when analyzing untrusted websites.
- Ensure your Chrome/Chromium browser is up-to-date to mitigate potential security risks.
- Consider running the script in a sandboxed environment for analyzing particularly untrusted sites.

## Testing

To run the test suite:

1. Install pytest:
   ```
   pip3 install pytest
   ```

2. Run the tests:
   ```
   pytest test_domain_analyzer.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue in the GitHub repository.