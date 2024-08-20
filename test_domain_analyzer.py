import unittest
from unittest.mock import patch, MagicMock
from domain_analyzer import analyze_domain
import os

class TestDomainAnalyzer(unittest.TestCase):

    @patch('domain_analyzer.webdriver.Chrome')
    @patch('domain_analyzer.Service')
    def test_analyze_domain(self, mock_service, mock_chrome):
        # Mock the WebDriver and its methods
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock the requests captured by the WebDriver
        mock_requests = [
            {'url': 'https://example.com/page'},
            {'url': 'https://cdn.example.com/style.css'},
            {'url': 'https://api.example.com/data'},
            {'url': 'https://ads.thirdparty.com/ad'},
        ]
        mock_driver.execute_cdp_cmd.return_value = mock_requests

        # Run the analysis
        test_url = 'https://example.com'
        analyze_domain(test_url)

        # Check if the file was created
        expected_filename = 'example.com_connected_domains.txt'
        self.assertTrue(os.path.exists(expected_filename))

        # Check the contents of the file
        with open(expected_filename, 'r') as f:
            content = f.read().splitlines()

        expected_domains = [
            'example.com',
            'cdn.example.com',
            'api.example.com',
            'ads.thirdparty.com'
        ]

        self.assertEqual(set(content), set(expected_domains))

        # Clean up the created file
        os.remove(expected_filename)

    def test_invalid_url(self):
        with self.assertRaises(Exception):
            analyze_domain('not_a_valid_url')

if __name__ == '__main__':
    unittest.main()