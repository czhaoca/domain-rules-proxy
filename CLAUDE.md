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
# Run with default medium interaction level
python3 domain_analyzer.py

# Run with specific URL and interaction level
python3 domain_analyzer.py https://example.com --interaction-level high

# Run without interactions for basic analysis
python3 domain_analyzer.py https://example.com --interaction-level none

# Show all available options
python3 domain_analyzer.py --help
```

### Testing
```bash
# Run all tests
pytest test/

# Run tests with verbose output
pytest -v test/

# Run specific test files
pytest test/test_domain_analyzer.py
pytest test/test_ip_resolution.py

# Run tests with coverage
pytest --cov=domain_analyzer test/
```

## Architecture

### Core Components

- `domain_analyzer.py`: Main module containing the domain analysis logic
  - `analyze_domain()`: Primary function that orchestrates browser automation and domain extraction
  - `capture_request()`: Helper function that extracts domains from network requests
  - `simulate_user_interactions()`: Enhanced user interaction simulation
  - `detect_page_type()`: Smart page type detection for targeted interactions
  - Uses Selenium WebDriver with Chrome/Chromium in headless mode
  - Implements Chrome DevTools Protocol for network interception
  - Supports configurable interaction levels: none, low, medium, high

- `test/test_domain_analyzer.py`: Main test suite with mocked WebDriver interactions
  - Uses pytest fixtures for setup/teardown and mocking
  - Tests both valid URL processing and error handling
  - Includes tests for IP resolution functions

- `test/test_ip_resolution.py`: Dedicated test suite for IP resolution functionality
  - Tests `resolve_domain_to_ips()` function with various scenarios
  - Tests `resolve_domains_to_ips()` function for bulk domain resolution
  - Covers IPv4/IPv6 resolution, DNS failures, and edge cases

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