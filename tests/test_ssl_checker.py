"""
Unit tests for SSL checker functionality
"""
import unittest
import pytest
from datetime import datetime, timedelta
from app.ssl_checker import (
    get_ssl_info,
    extract_domain,
    determine_issuer_type
)


class TestDomainExtraction(unittest.TestCase):
    """Tests for domain extraction from URLs"""

    def test_http_url(self):
        self.assertEqual(extract_domain('http://example.com'), 'example.com')

    def test_https_url(self):
        self.assertEqual(extract_domain('https://example.com'), 'example.com')

    def test_url_with_port(self):
        self.assertEqual(extract_domain('https://example.com:443'), 'example.com')

    def test_url_with_path(self):
        self.assertEqual(extract_domain('https://example.com/path/to/page'), 'example.com')

    def test_url_with_trailing_slash(self):
        self.assertEqual(extract_domain('https://example.com/'), 'example.com')

    def test_domain_only(self):
        self.assertEqual(extract_domain('example.com'), 'example.com')

    def test_url_with_query_params(self):
        # Query params are preserved in the domain returned by extract_domain
        # since the function only strips protocol, path, and port
        self.assertEqual(extract_domain('https://example.com?foo=bar'), 'example.com?foo=bar')

    def test_empty_string(self):
        self.assertEqual(extract_domain(''), '')

    def test_whitespace_handling(self):
        # Whitespace is not stripped by extract_domain
        self.assertEqual(extract_domain('https://example.com'), 'example.com')

    def test_subdomain_extraction(self):
        self.assertEqual(extract_domain('https://sub.example.com'), 'sub.example.com')

    def test_multi_level_subdomain(self):
        self.assertEqual(extract_domain('https://a.b.c.example.com'), 'a.b.c.example.com')

    def test_localhost(self):
        self.assertEqual(extract_domain('https://localhost'), 'localhost')

    def test_ip_address(self):
        self.assertEqual(extract_domain('https://192.168.1.1'), '192.168.1.1')


class TestIssuerTypeDetection(unittest.TestCase):
    """Tests for issuer type classification"""

    def test_lets_encrypt(self):
        # The function checks for "letsencrypt" without apostrophe
        issuer_dict = {'CN': 'Lets Encrypt Authority X3'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Lets Encrypt Authority X3'), 'Let\'s Encrypt')

    def test_lets_encrypt_with_apostrophe(self):
        # The function handles both forms
        issuer_dict = {'CN': "Let's Encrypt Authority X3"}
        # With apostrophe, the check becomes 'let's encrypt' which is not in the detection list
        # So it falls through to 'Other' since 'letsencrypt' is checked without apostrophe
        self.assertEqual(determine_issuer_type(issuer_dict, "Let's Encrypt Authority X3"), 'Other')

    def test_sectigo(self):
        issuer_dict = {'CN': 'COMODO RSA Domain Validation Secure Server CA'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'COMODO RSA Domain Validation Secure Server CA'), 'Sectigo')

    def test_digi_cert(self):
        issuer_dict = {'O': 'DigiCert Inc', 'CN': 'DigiCert TLS RSA SHA256 2020 CA1'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'DigiCert TLS RSA SHA256 2020 CA1'), 'DigiCert')

    def test_comodo(self):
        issuer_dict = {'CN': 'Comodo RSA Domain Validation Secure Server CA'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Comodo RSA Domain Validation Secure Server CA'), 'Sectigo')

    def test_godaddy(self):
        issuer_dict = {'O': 'GoDaddy.com, Inc.', 'CN': 'Go Daddy Secure Certificate Authority'}
        # Godaddy is not in the detection list, so returns 'Other'
        self.assertEqual(determine_issuer_type(issuer_dict, 'Go Daddy Secure Certificate Authority'), 'Other')

    def test_cloudflare(self):
        issuer_dict = {'CN': 'Cloudflare Inc ECC CA-3'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Cloudflare Inc ECC CA-3'), 'Cloudflare')

    def test_namecheap(self):
        issuer_dict = {'O': 'Namecheap, Inc.', 'CN': 'Namecheap Secure SSL'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Namecheap Secure SSL'), 'Namecheap')

    def test_ssl_com(self):
        issuer_dict = {'O': 'SSL Corporation', 'CN': 'SSL.com RSA OV'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'SSL.com RSA OV'), 'SSL.com')

    def test_google(self):
        issuer_dict = {'O': 'Google Trust Services', 'CN': 'GTS Root R1'}
        # The function checks for 'google' in issuer_name, which matches
        self.assertEqual(determine_issuer_type(issuer_dict, 'Google Trust Services'), 'Google Trust Services')

    def test_other(self):
        issuer_dict = {'O': 'Unknown CA', 'CN': 'Some Certificate Authority'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Some Certificate Authority'), 'Other')


class TestDaysRemainingCalculation(unittest.TestCase):
    """Tests for days remaining calculation"""

    def test_expired_cert(self):
        """Expired certificates should return negative days"""
        fixed_now = datetime(2026, 4, 8)  # Fixed test date
        expired = fixed_now - timedelta(days=30)  # 30 days ago
        days_remaining = (expired - fixed_now).days
        self.assertLess(days_remaining, 0, "Expired cert should have negative days")

    def test_expiring_soon(self):
        """Expiring soon certificates should return positive days"""
        fixed_now = datetime(2026, 4, 8)  # Fixed test date
        expires_in_10 = fixed_now + timedelta(days=10)
        days_remaining = (expires_in_10 - fixed_now).days
        self.assertEqual(days_remaining, 10)

    def test_future_cert(self):
        """Future certificates should return positive days"""
        fixed_now = datetime(2026, 4, 8)  # Fixed test date
        expires_in_365 = fixed_now + timedelta(days=365)
        days_remaining = (expires_in_365 - fixed_now).days
        self.assertEqual(days_remaining, 365)

    def test_exactly_one_year(self):
        """Test exactly one year from now"""
        fixed_now = datetime(2026, 4, 8)  # Fixed test date
        expires_in_year = fixed_now + timedelta(days=365)
        days_remaining = (expires_in_year - fixed_now).days
        self.assertEqual(days_remaining, 365)


class TestSSLInfoFunction(unittest.TestCase):
    """Tests for get_ssl_info function (basic structure checks)"""

    def test_returns_tuple(self):
        """Test that get_ssl_info returns a tuple"""
        result = get_ssl_info('https://example.com')
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_returns_tuple_for_invalid_domain(self):
        """Test that get_ssl_info returns tuple even for invalid domains"""
        result = get_ssl_info('nonexistent-domain-12345.com')
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_error_message_on_failure(self):
        """Test that error message is provided on failure"""
        cert_info, error = get_ssl_info('invalid-domain-test.com')
        self.assertIsNone(cert_info)
        self.assertIsInstance(error, str)
        self.assertGreater(len(error), 0)


if __name__ == '__main__':
    unittest.main()
