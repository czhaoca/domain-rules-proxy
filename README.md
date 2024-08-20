# Domain Analyzer

## Overview

Domain Analyzer is a Python script designed to run on Ubuntu systems. It analyzes all domains connected when visiting a specified website. Using Selenium with Chrome in headless mode, it captures network requests made during page load and saves the list of unique domains to a text file.

## Features

- Runs on Ubuntu systems
- Simulates browser behavior using Selenium with Chrome in headless mode
- Captures all network requests during page load
- Extracts unique domains from the captured requests
- Saves results to a text file in the `data` folder

## Requirements

- Ubuntu 20.04 or later
- Python 3.6+
- Google Chrome or Chromium browser
- Selenium WebDriver
- ChromeDriver (automatically managed by webdriver_manager)

## Project Structure

```
ubuntu-domain-analyzer/
│
├── domain_analyzer.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── (output files will be saved here)
│
└── test/
    └── test_domain_analyzer.py
```

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

4. Clone the repository:
   ```
   git clone https://github.com/yourusername/ubuntu-domain-analyzer.git
   cd ubuntu-domain-analyzer
   ```

5. Create a virtual environment (optional but recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

6. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```
   python3 domain_analyzer.py
   ```

2. Enter the full URL of the website you want to analyze when prompted (including `http://` or `https://`).

3. The script will run the analysis and save the results in a text file named `[analyzed_domain]_connected_domains.txt` in the `data` folder.

## Testing

To run the test suite:

1. Ensure you're in the project root directory.

2. Run the tests:
   ```
   pytest test/test_domain_analyzer.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue in the GitHub repository.