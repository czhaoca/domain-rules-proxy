import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import shutil
import socket

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain_analyzer import (
    analyze_domain, capture_request, resolve_domain_to_ips, resolve_domains_to_ips,
    detect_page_type, simulate_scroll_interactions, simulate_user_interactions
)

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

@patch('domain_analyzer.resolve_domains_to_ips')
@patch('domain_analyzer.simulate_user_interactions')
def test_analyze_domain(mock_interactions, mock_resolve_ips, mock_webdriver, mock_service, setup_teardown):
    # Mock the requests that will be captured by CDP (including one direct IP)
    mock_requests = [
        {'request': {'url': 'https://example.com/page'}},
        {'request': {'url': 'https://cdn.example.com/style.css'}},
        {'request': {'url': 'https://api.example.com/data'}},
        {'request': {'url': 'https://192.168.1.1/resource'}},  # Direct IP
        {'request': {'url': 'https://ads.thirdparty.com/ad'}},
    ]

    # Mock user interactions to return success
    mock_interactions.return_value = True
    
    # Mock DNS resolution
    mock_resolve_ips.return_value = {
        'example.com': {'ipv4': ['93.184.216.34'], 'ipv6': ['2606:2800:220:1:248:1893:25c8:1946']},
        'cdn.example.com': {'ipv4': ['93.184.216.35'], 'ipv6': []},
        'api.example.com': {'ipv4': ['93.184.216.36'], 'ipv6': []},
        'ads.thirdparty.com': {'ipv4': ['203.0.113.1'], 'ipv6': []}
    }

    # Mock the CDP listener functionality
    cdp_listeners = {}
    
    def mock_add_cdp_listener(event, callback):
        if event not in cdp_listeners:
            cdp_listeners[event] = []
        cdp_listeners[event].append(callback)
    
    def mock_execute_cdp_cmd(command, params):
        pass  # Mock the CDP command execution
    
    # Mock driver.get to trigger CDP events when called
    def mock_driver_get(url):
        # Simulate CDP events being fired when navigating to URL
        if "Network.requestWillBeSent" in cdp_listeners:
            for request in mock_requests:
                for callback in cdp_listeners["Network.requestWillBeSent"]:
                    callback(**request)
    
    # Configure the mock driver
    mock_webdriver.add_cdp_listener = mock_add_cdp_listener
    mock_webdriver.execute_cdp_cmd = mock_execute_cdp_cmd
    mock_webdriver.get = mock_driver_get

    # Run the analysis with interaction level none to avoid complex mocking
    test_url = 'https://example.com'
    result = analyze_domain(test_url, output_dir=TEST_DATA_DIR, interaction_level='none')

    # Check if files were created
    domains_filename = os.path.join(TEST_DATA_DIR, 'example.com_connected_domains.txt')
    ips_filename = os.path.join(TEST_DATA_DIR, 'example.com_connected_ips.txt')
    mapping_filename = os.path.join(TEST_DATA_DIR, 'example.com_domain_ip_mapping.txt')
    
    assert os.path.exists(domains_filename)
    assert os.path.exists(ips_filename)
    assert os.path.exists(mapping_filename)

    # Check the domains file contents
    with open(domains_filename, 'r') as f:
        domains_content = f.read().splitlines()

    expected_domains = {
        'example.com',
        'cdn.example.com',
        'api.example.com',
        'ads.thirdparty.com'
    }

    assert set(domains_content) == expected_domains
    
    # Check the result structure
    assert isinstance(result, dict)
    assert 'domains' in result
    assert 'direct_ips' in result
    assert 'domain_ip_mapping' in result
    
    assert result['domains'] == expected_domains
    assert '192.168.1.1' in result['direct_ips']
    
    # Check that IP resolution was called
    mock_resolve_ips.assert_called_once_with(expected_domains)

def test_invalid_url(mock_webdriver, mock_service, setup_teardown):
    with pytest.raises(ValueError, match="Invalid URL. Please include http:// or https://"):
        analyze_domain('example.com', output_dir=TEST_DATA_DIR, interaction_level='none')

@patch('domain_analyzer.socket.getaddrinfo')
def test_resolve_domain_to_ips(mock_getaddrinfo):
    # Mock successful IPv4 and IPv6 resolution
    mock_getaddrinfo.side_effect = [
        # IPv4 resolution
        [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80))],
        # IPv6 resolution  
        [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2606:2800:220:1:248:1893:25c8:1946', 80, 0, 0))]
    ]
    
    result = resolve_domain_to_ips('example.com')
    
    assert result['ipv4'] == ['93.184.216.34']
    assert result['ipv6'] == ['2606:2800:220:1:248:1893:25c8:1946']
    
    # Verify getaddrinfo was called correctly
    assert mock_getaddrinfo.call_count == 2

@patch('domain_analyzer.socket.getaddrinfo')
def test_resolve_domain_to_ips_dns_failure(mock_getaddrinfo):
    # Mock DNS resolution failure
    mock_getaddrinfo.side_effect = socket.gaierror("Name resolution failed")
    
    result = resolve_domain_to_ips('nonexistent.example')
    
    assert result['ipv4'] == []
    assert result['ipv6'] == []

@patch('domain_analyzer.resolve_domain_to_ips')
def test_resolve_domains_to_ips(mock_resolve_single):
    # Mock individual domain resolution
    mock_resolve_single.side_effect = [
        {'ipv4': ['93.184.216.34'], 'ipv6': []},
        {'ipv4': ['203.0.113.1'], 'ipv6': ['2001:db8::1']}
    ]
    
    domains = {'example.com', 'test.example.com:8080'}
    result = resolve_domains_to_ips(domains)
    
    assert len(result) == 2
    assert 'example.com' in result
    assert 'test.example.com:8080' in result
    
    # Verify the hostname extraction (port removed)
    mock_resolve_single.assert_any_call('example.com')
    mock_resolve_single.assert_any_call('test.example.com')

def test_capture_request_with_domain():
    domains = set()
    direct_ips = set()
    request = {'url': 'https://example.com/page'}
    
    capture_request(request, domains, direct_ips)
    
    assert 'example.com' in domains
    assert len(direct_ips) == 0

def test_capture_request_with_ip():
    domains = set()
    direct_ips = set()
    request = {'url': 'https://192.168.1.1/resource'}
    
    capture_request(request, domains, direct_ips)
    
    assert len(domains) == 0
    assert '192.168.1.1' in direct_ips

def test_capture_request_with_ipv6():
    domains = set()
    direct_ips = set()
    request = {'url': 'https://[2001:db8::1]/resource'}
    
    capture_request(request, domains, direct_ips)
    
    assert len(domains) == 0
    assert '[2001:db8::1]' in direct_ips

def test_detect_page_type():
    # Mock driver for page type detection
    mock_driver = MagicMock()
    mock_driver.execute_script.return_value = {
        'hasReact': False,
        'hasVue': False,
        'hasAngular': False,
        'hasPushState': True,
        'hasFetch': True
    }
    
    # Test different page types
    assert detect_page_type('https://google.com/search', mock_driver) == 'search_engine'
    assert detect_page_type('https://youtube.com/watch', mock_driver) == 'streaming'
    assert detect_page_type('https://facebook.com/profile', mock_driver) == 'social_media'
    assert detect_page_type('https://amazon.com/products', mock_driver) == 'ecommerce'
    assert detect_page_type('https://example.com/app', mock_driver) == 'spa'

def test_simulate_scroll_interactions():
    # Test that function exists and can be called
    mock_driver = MagicMock()
    # Configure return values properly
    mock_driver.execute_script.return_value = 1000
    
    # Call the function with a mock driver
    result = simulate_scroll_interactions(mock_driver, wait_time=0)
    
    # Just verify the function ran and made script calls
    assert mock_driver.execute_script.called
    # Result can be True or False based on execution, just check it's boolean
    assert isinstance(result, bool)

@patch('domain_analyzer.detect_page_type')
@patch('domain_analyzer.simulate_scroll_interactions')
@patch('domain_analyzer.simulate_search_interaction')
@patch('domain_analyzer.simulate_hover_interactions')
@patch('domain_analyzer.simulate_click_interactions')
def test_simulate_user_interactions(
    mock_click, mock_hover, mock_search, mock_scroll, mock_detect
):
    mock_driver = MagicMock()
    mock_detect.return_value = 'generic'
    mock_scroll.return_value = True
    mock_search.return_value = True
    mock_hover.return_value = True
    mock_click.return_value = True
    
    # Test medium interaction level
    result = simulate_user_interactions(mock_driver, 'https://example.com', 'medium')
    assert result is True
    
    # Verify appropriate functions were called
    mock_scroll.assert_called_once()
    mock_search.assert_called_once()
    mock_hover.assert_called_once()
    mock_click.assert_called_once_with(mock_driver, max_clicks=2)

if __name__ == '__main__':
    pytest.main()