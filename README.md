# Domain Rules Proxy

## Overview

Domain Rules Proxy is a network analysis tool designed to help network administrators identify all domains and IP addresses that need to be whitelisted in restrictive firewall environments. When clients need to access mainstream services (like Google, streaming platforms, or LLM services) through a whitelist-only network configuration, this tool captures all the required domains and IPs that must be allowed for full functionality.

The tool uses Selenium WebDriver with Chrome in headless mode to simulate real browser behavior, capturing all network requests made during page load and interaction, then extracts unique domains and IP addresses for firewall rule creation.

## Use Cases

- **Corporate Firewall Configuration**: Identify domains needed for employee access to business-critical web services
- **Educational Network Setup**: Configure student network access with minimal required whitelist rules
- **Secure Environment Analysis**: Determine network dependencies for applications in high-security environments
- **Proxy Rule Generation**: Create comprehensive forwarding rules for proxy servers in restricted networks

## Features

- Runs on Ubuntu systems with Chrome/Chromium support
- Simulates realistic browser behavior including JavaScript execution
- Captures all network requests during page load and user interactions
- Extracts unique domains and IP addresses from captured traffic
- Resolves domains to IPv4 and IPv6 addresses using DNS lookups
- Handles direct IP connections and domain-based connections separately
- **Enhanced user interaction simulation** with configurable interaction levels
- **Smart page type detection** for targeted interaction strategies
- **Comprehensive interaction simulation**: scrolling, searching, clicking, hovering
- Generates whitelist-ready domain and IP lists with timestamp information
- Supports batch analysis of multiple target websites
- Exports results in firewall-friendly formats

## Requirements

- Ubuntu 20.04 or later
- Python 3.6+
- Google Chrome or Chromium browser
- Selenium WebDriver
- ChromeDriver (automatically managed by webdriver_manager)

## Project Structure

```
domain-rules-proxy/
│
├── domain_analyzer.py          # Main analysis script
├── README.md
├── requirements.txt
├── CLAUDE.md                   # Development guidance
├── .gitignore
│
├── data/                       # Analysis output files
│   └── (domain and IP lists saved here)
│
├── dev/                        # Development resources
│   └── llm/                    # Pre-analyzed LLM service domains
│       ├── alphabet-services.txt
│       ├── llm-services.txt
│       └── streaming_services.txt
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
   git clone https://github.com/czhaoca/domain-rules-proxy.git
   cd domain-rules-proxy
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

### Basic Analysis

1. Run the domain analyzer:
   ```bash
   # Interactive mode with default medium interaction level
   python3 domain_analyzer.py
   
   # Direct URL with specific interaction level
   python3 domain_analyzer.py https://example.com --interaction-level high
   
   # Fast analysis without user interactions
   python3 domain_analyzer.py https://example.com --interaction-level none
   
   # Custom timing for slower sites
   python3 domain_analyzer.py https://example.com --initial-wait 10 --interaction-wait 5
   ```

2. If no URL is provided as argument, enter the full URL when prompted (including `http://` or `https://`).

3. The script will simulate browser behavior with user interactions and capture all network requests, then save results in the `data` folder:
   - `[analyzed_domain]_connected_domains.txt` - List of all domains accessed
   - `[analyzed_domain]_connected_ips.txt` - IP addresses resolved from domains and direct connections
   - `[analyzed_domain]_domain_ip_mapping.txt` - Combined mapping of domains to their IP addresses

### Interaction Levels

The tool supports different levels of user interaction simulation:

- **none**: Static page load only (fastest)
- **low**: Basic scrolling to trigger lazy-loaded content
- **medium** (default): Scrolling + search interactions + hover effects + limited clicking
- **high**: All interactions + more aggressive clicking on interactive elements

Different page types are automatically detected and have tailored interaction strategies:
- **Search engines**: Perform search queries
- **E-commerce**: Search for products
- **Streaming services**: Search for content
- **Social media**: Scroll and interact with feeds
- **SPAs**: Handle dynamic navigation

### Example Use Cases

**Analyzing Google Search Access:**
```bash
python3 domain_analyzer.py
# Enter: https://www.google.com
# Output: 
#   - google.com_connected_domains.txt with all required domains
#   - google.com_connected_ips.txt with resolved IP addresses
#   - google.com_domain_ip_mapping.txt with domain-to-IP mappings
```

**Corporate Network Setup:**
Use the generated domain lists to configure firewall whitelist rules, ensuring employees can access necessary web services while maintaining network security.

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