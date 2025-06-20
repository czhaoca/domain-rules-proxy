#!/usr/bin/env python3

import pytest
import socket
from unittest.mock import patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain_analyzer import resolve_domain_to_ips, resolve_domains_to_ips

class TestIPResolution:
    """Test suite for IP resolution functionality"""
    
    @patch('domain_analyzer.socket.getaddrinfo')
    def test_resolve_single_domain_success(self, mock_getaddrinfo):
        """Test successful resolution of a single domain to both IPv4 and IPv6"""
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
        assert mock_getaddrinfo.call_count == 2
    
    @patch('domain_analyzer.socket.getaddrinfo')
    def test_resolve_single_domain_ipv4_only(self, mock_getaddrinfo):
        """Test domain resolution when only IPv4 is available"""
        # Mock IPv4 success, IPv6 failure
        mock_getaddrinfo.side_effect = [
            [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80))],
            socket.gaierror("IPv6 not available")
        ]
        
        result = resolve_domain_to_ips('example.com')
        
        assert result['ipv4'] == ['93.184.216.34']
        assert result['ipv6'] == []
    
    @patch('domain_analyzer.socket.getaddrinfo')
    def test_resolve_single_domain_dns_failure(self, mock_getaddrinfo):
        """Test domain resolution failure for both IPv4 and IPv6"""
        mock_getaddrinfo.side_effect = socket.gaierror("Name resolution failed")
        
        result = resolve_domain_to_ips('nonexistent.example')
        
        assert result['ipv4'] == []
        assert result['ipv6'] == []
    
    @patch('domain_analyzer.socket.getaddrinfo')
    def test_resolve_single_domain_multiple_ips(self, mock_getaddrinfo):
        """Test domain with multiple IP addresses"""
        # Mock multiple IPv4 addresses
        mock_getaddrinfo.side_effect = [
            [
                (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.35', 80))
            ],
            []  # No IPv6
        ]
        
        result = resolve_domain_to_ips('example.com')
        
        assert len(result['ipv4']) == 2
        assert '93.184.216.34' in result['ipv4']
        assert '93.184.216.35' in result['ipv4']
        assert result['ipv6'] == []
    
    @patch('domain_analyzer.resolve_domain_to_ips')
    def test_resolve_multiple_domains(self, mock_resolve_single):
        """Test resolution of multiple domains"""
        # Mock individual domain resolution
        mock_resolve_single.side_effect = [
            {'ipv4': ['93.184.216.34'], 'ipv6': []},
            {'ipv4': ['203.0.113.1'], 'ipv6': ['2001:db8::1']}
        ]
        
        domains = {'example.com', 'test.example.org'}
        result = resolve_domains_to_ips(domains)
        
        assert len(result) == 2
        assert 'example.com' in result
        assert 'test.example.org' in result
        assert result['example.com']['ipv4'] == ['93.184.216.34']
        assert result['test.example.org']['ipv6'] == ['2001:db8::1']
    
    @patch('domain_analyzer.resolve_domain_to_ips')
    def test_resolve_domains_with_ports(self, mock_resolve_single):
        """Test domain resolution with port numbers"""
        mock_resolve_single.side_effect = [
            {'ipv4': ['93.184.216.34'], 'ipv6': []},
            {'ipv4': ['203.0.113.1'], 'ipv6': []}
        ]
        
        domains = {'example.com:8080', 'test.example.org:443'}
        result = resolve_domains_to_ips(domains)
        
        assert len(result) == 2
        assert 'example.com:8080' in result
        assert 'test.example.org:443' in result
        
        # Verify hostname extraction (port removed for DNS lookup)
        mock_resolve_single.assert_any_call('example.com')
        mock_resolve_single.assert_any_call('test.example.org')
    
    @patch('domain_analyzer.resolve_domain_to_ips')
    def test_resolve_domains_filter_empty_results(self, mock_resolve_single):
        """Test that domains with no IP addresses are filtered out"""
        mock_resolve_single.side_effect = [
            {'ipv4': ['93.184.216.34'], 'ipv6': []},  # Has IPs
            {'ipv4': [], 'ipv6': []}  # No IPs
        ]
        
        domains = {'example.com', 'failed.example.org'}
        result = resolve_domains_to_ips(domains)
        
        assert len(result) == 1
        assert 'example.com' in result
        assert 'failed.example.org' not in result
    
    def test_resolve_empty_domain_set(self):
        """Test resolution with empty domain set"""
        result = resolve_domains_to_ips(set())
        assert result == {}

if __name__ == '__main__':
    pytest.main([__file__, '-v'])