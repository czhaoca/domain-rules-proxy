# Domain Analyzer

Domain Analyzer is a Python script that uses Selenium to analyze all domains connected when visiting a specified website. It captures network requests made during page load and saves the list of unique domains to a text file.

## Features

- Simulates browser behavior using Selenium with Chrome in headless mode
- Captures all network requests during page load
- Extracts unique domains from the captured requests
- Saves results to a text file named after the analyzed domain

## Requirements

- Python 3.6+
- Chrome browser
- Selenium WebDriver
- ChromeDriver (automatically managed by webdriver_manager)

## Quick Start

1. Install the required packages:
   ```
   pip install selenium webdriver-manager
   ```

2. Run the script:
   ```
   python domain_analyzer.py
   ```

3. Enter the URL you want to analyze when prompted.

4. Find the results in a text file named `[analyzed_domain]_connected_domains.txt`.

## Documentation

For detailed setup instructions and usage information, please refer to the `docs/setup.md` file.

## Testing

To run the test suite, execute:
```
python test_domain_analyzer.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.