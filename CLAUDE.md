# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based domain analyzer that captures all network requests made when visiting a website using Selenium WebDriver with Chrome in headless mode. The tool extracts unique domains from captured requests and saves them to text files for analysis.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run the main domain analyzer
python3 domain_analyzer.py
```

### Testing
```bash
# Run all tests
pytest test/test_domain_analyzer.py

# Run tests with verbose output
pytest -v test/test_domain_analyzer.py
```

## Architecture

### Core Components

- `domain_analyzer.py`: Main module containing the domain analysis logic
  - `analyze_domain()`: Primary function that orchestrates browser automation and domain extraction
  - `capture_request()`: Helper function that extracts domains from network requests
  - Uses Selenium WebDriver with Chrome/Chromium in headless mode
  - Implements Chrome DevTools Protocol for network interception

- `test/test_domain_analyzer.py`: Test suite with mocked WebDriver interactions
  - Uses pytest fixtures for setup/teardown and mocking
  - Tests both valid URL processing and error handling

### Key Dependencies

- Selenium 4.10.0 for browser automation
- webdriver-manager for automatic ChromeDriver management
- pytest for testing framework

### Output Structure

Results are saved as text files in the `data/` directory with the naming pattern:
`{analyzed_domain}_connected_domains.txt`

## System Requirements

- Ubuntu 20.04+ (optimized for Ubuntu systems)
- Python 3.6+
- Chrome/Chromium browser installed
- ChromeDriver (automatically managed by webdriver-manager)