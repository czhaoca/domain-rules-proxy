import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import shutil

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain_analyzer import analyze_domain, capture_request

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture(scope="module")
def setup_teardown():
    # Setup
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    yield
    
    # Teardown
    shutil.rmtree(TEST_DATA_DIR)

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

def test_analyze_domain(mock_webdriver, mock_service, setup_teardown):
    # Mock the requests captured by the WebDriver
    mock_requests = [
        {'url': 'https://example.com/page'},
        {'url': 'https://cdn.example.com/style.css'},
        {'url': 'https://api.example.com/data'},
        {'url': 'https://ads.thirdparty.com/ad'},
    ]

    # Create a set to store domains
    domains = set()

    # Use the actual capture_request function
    def side_effect(request):
        capture_request(request, domains)

    # Set up the mock driver's on_request attribute
    mock_webdriver.on_request = side_effect

    # Run the analysis
    test_url = 'https://example.com'
    result_domains = analyze_domain(test_url, output_dir=TEST_DATA_DIR)

    # Simulate requests being processed
    for request in mock_requests:
        mock_webdriver.on_request(request)

    # Check if the file was created
    expected_filename = os.path.join(TEST_DATA_DIR, 'example.com_connected_domains.txt')
    assert os.path.exists(expected_filename)

    # Check the contents of the file
    with open(expected_filename, 'r') as f:
        content = f.read().splitlines()

    expected_domains = {
        'example.com',
        'cdn.example.com',
        'api.example.com',
        'ads.thirdparty.com'
    }

    assert set(content) == expected_domains
    assert result_domains == expected_domains

def test_invalid_url(mock_webdriver, mock_service, setup_teardown):
    with pytest.raises(ValueError, match="Invalid URL. Please include http:// or https://"):
        analyze_domain('example.com', output_dir=TEST_DATA_DIR)

if __name__ == '__main__':
    pytest.main()