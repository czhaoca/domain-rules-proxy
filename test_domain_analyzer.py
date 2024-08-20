import pytest
from unittest.mock import patch, MagicMock
from domain_analyzer import analyze_domain
import os

@pytest.fixture
def mock_webdriver():
    with patch('domain_analyzer.webdriver.Chrome') as mock_chrome:
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        yield mock_driver

@pytest.fixture
def mock_service():
    with patch('domain_analyzer.Service') as mock_service:
        yield mock_service

def test_analyze_domain(mock_webdriver, mock_service):
    # Mock the requests captured by the WebDriver
    mock_requests = [
        {'url': 'https://example.com/page'},
        {'url': 'https://cdn.example.com/style.css'},
        {'url': 'https://api.example.com/data'},
        {'url': 'https://ads.thirdparty.com/ad'},
    ]
    mock_webdriver.execute_cdp_cmd.return_value = mock_requests

    # Run the analysis
    test_url = 'https://example.com'
    analyze_domain(test_url)

    # Check if the file was created
    expected_filename = 'example.com_connected_domains.txt'
    assert os.path.exists(expected_filename)

    # Check the contents of the file
    with open(expected_filename, 'r') as f:
        content = f.read().splitlines()

    expected_domains = [
        'example.com',
        'cdn.example.com',
        'api.example.com',
        'ads.thirdparty.com'
    ]

    assert set(content) == set(expected_domains)

    # Clean up the created file
    os.remove(expected_filename)

def test_invalid_url(mock_webdriver, mock_service):
    with pytest.raises(Exception):
        analyze_domain('not_a_valid_url')

if __name__ == '__main__':
    pytest.main()