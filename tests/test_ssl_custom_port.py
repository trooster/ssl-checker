"""
Unit tests for SSL utilities with custom port support (ssl_custom_port.py)
"""
import unittest
import pytest
from datetime import datetime
from app.ssl_custom_port import (
    get_ssl_info_custom_port,
    extract_issuer_name
)


class TestIssuerNameExtraction(unittest.TestCase):
    """Tests for issuer name extraction from custom port certs"""

    def test_empty_dict(self):
        issuer_dict = []
        self.assertEqual(extract_issuer_name(issuer_dict), 'Unknown')

    def test_basic_issuer_list(self):
        # Format: [['CN', 'Test CA']]
        issuer_dict = [['CN', 'Test CA']]
        self.assertEqual(extract_issuer_name(issuer_dict), 'Test CA')

    def test_issuer_with_org(self):
        issuer_dict = [
            ['CN', 'Test CA'],
            ['O', 'Test Organization']
        ]
        self.assertEqual(extract_issuer_name(issuer_dict), 'Test CA')

    def test_nested_list_structure(self):
        issuer_dict = [
            ['commonName', 'Test CA']
        ]
        self.assertEqual(extract_issuer_name(issuer_dict), 'Test CA')

    def test_multiple_entries_first_is_key(self):
        issuer_dict = [
            ['O', 'Test Organization'],
            ['C', 'US']
        ]
        # First entry should be O
        result = extract_issuer_name(issuer_dict)
        self.assertEqual(result, 'Test Organization')

    def test_tuple_format(self):
        issuer_dict = [
            ('CN', 'Test CA')
        ]
        self.assertEqual(extract_issuer_name(issuer_dict), 'Test CA')


class TestCustomPortSSLInfo(unittest.TestCase):
    """Tests for SSL info extraction on custom ports"""

    def test_invalid_domain(self):
        """Test with a non-existent domain"""
        cert_info, error = get_ssl_info_custom_port('nonexistent-domain-12345.com', 443)
        self.assertIsNone(cert_info)
        self.assertIsNotNone(error)
        # DNS resolution error is expected
        self.assertIn('failed', error.lower() or error.lower())

    def test_default_port_443(self):
        """Test that default port 443 works"""
        # We use a known unreachable IP range for testing
        cert_info, error = get_ssl_info_custom_port('https://192.0.2.1', 443)
        self.assertIsNone(cert_info)
        self.assertIsNotNone(error)

    def test_custom_port_format(self):
        """Test with custom port specified in FQDN"""
        cert_info, error = get_ssl_info_custom_port('https://192.0.2.1:8443', 8443)
        self.assertIsNone(cert_info)
        self.assertIsNotNone(error)

    def test_returns_tuple(self):
        """Test that function always returns a tuple"""
        result = get_ssl_info_custom_port('invalid.com', 443)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_error_message_on_failure(self):
        """Test that error message is provided on failure"""
        cert_info, error = get_ssl_info_custom_port('invalid-domain-test.com', 443)
        self.assertIsNone(cert_info)
        self.assertIsInstance(error, str)
        self.assertGreater(len(error), 0)

    def test_port_443_with_invalid_domain(self):
        """Test port 443 with invalid domain"""
        cert_info, error = get_ssl_info_custom_port('invalid-test-12345.com', 443)
        self.assertIsNone(cert_info)
        self.assertIsInstance(error, str)

    def test_port_8443_with_invalid_domain(self):
        """Test port 8443 with invalid domain"""
        cert_info, error = get_ssl_info_custom_port('invalid-test-12345.com', 8443)
        self.assertIsNone(cert_info)
        self.assertIsInstance(error, str)

    def test_port_9443_with_invalid_domain(self):
        """Test port 9443 with invalid domain"""
        cert_info, error = get_ssl_info_custom_port('invalid-test-12345.com', 9443)
        self.assertIsNone(cert_info)
        self.assertIsInstance(error, str)


class TestPortHandling(unittest.TestCase):
    """Tests for port handling in custom port SSL functions"""

    def test_port_443_invalid(self):
        cert_info, error = get_ssl_info_custom_port('invalid.com', 443)
        self.assertIsNone(cert_info)

    def test_port_8443_invalid(self):
        cert_info, error = get_ssl_info_custom_port('invalid.com', 8443)
        self.assertIsNone(cert_info)

    def test_port_9443_invalid(self):
        cert_info, error = get_ssl_info_custom_port('invalid.com', 9443)
        self.assertIsNone(cert_info)


if __name__ == '__main__':
    unittest.main()
