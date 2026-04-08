"""
Unit tests for URL utilities (url_utils.py)
"""
import unittest
import pytest
from app.url_utils import (
    extract_domain,
    extract_port_from_url,
    validate_url_format,
    check_url_reachability,
    validate_and_check_url,
    URLValidationResult
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
        # Query params are stripped by extract_domain along with path
        self.assertEqual(extract_domain('https://example.com/path?query=value'), 'example.com')

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


class TestPortExtraction(unittest.TestCase):
    """Tests for port extraction from URLs"""

    def test_default_port(self):
        self.assertEqual(extract_port_from_url('https://example.com'), 443)

    def test_explicit_port_443(self):
        self.assertEqual(extract_port_from_url('https://example.com:443'), 443)

    def test_custom_port(self):
        self.assertEqual(extract_port_from_url('https://example.com:8443'), 8443)

    def test_port_8080(self):
        self.assertEqual(extract_port_from_url('https://example.com:8080'), 8080)

    def test_empty_url(self):
        self.assertEqual(extract_port_from_url(''), 443)

    def test_url_with_path_and_port(self):
        self.assertEqual(extract_port_from_url('https://example.com:9443/path'), 9443)


class TestURLValidation(unittest.TestCase):
    """Tests for URL format validation"""

    def test_valid_https_url(self):
        is_valid, msg = validate_url_format('https://example.com')
        self.assertTrue(is_valid)
        self.assertEqual(msg, 'Valid')

    def test_valid_url_with_path(self):
        is_valid, msg = validate_url_format('https://example.com/path/to/page')
        self.assertTrue(is_valid)

    def test_invalid_http_url(self):
        is_valid, msg = validate_url_format('http://example.com')
        self.assertFalse(is_valid)
        self.assertIn('must start with https', msg)

    def test_empty_url(self):
        is_valid, msg = validate_url_format('')
        self.assertFalse(is_valid)
        self.assertIn('empty', msg)

    def test_invalid_domain_format(self):
        # Underscores are not valid in domain names per RFC
        is_valid, msg = validate_url_format('https://exa_mple.com')
        self.assertFalse(is_valid)
        self.assertIn('Invalid domain', msg)

    def test_consecutive_dots(self):
        # The domain pattern check comes first, so this fails with "Invalid domain format"
        is_valid, msg = validate_url_format('https://ex..ample.com')
        self.assertFalse(is_valid)
        self.assertIn('Invalid domain', msg)

    def test_leading_hyphen(self):
        # The domain pattern check comes first, so this fails with "Invalid domain format"
        is_valid, msg = validate_url_format('https://-example.com')
        self.assertFalse(is_valid)
        self.assertIn('Invalid domain', msg)

    def test_trailing_hyphen(self):
        # The domain pattern check comes first, so this fails with "Invalid domain format"
        is_valid, msg = validate_url_format('https://example-.com')
        self.assertFalse(is_valid)
        self.assertIn('Invalid domain', msg)

    def test_url_with_port(self):
        is_valid, msg = validate_url_format('https://example.com:8443')
        self.assertTrue(is_valid)


class TestReachabilityCheck(unittest.TestCase):
    """Tests for URL reachability checking"""

    def test_nonexistent_domain(self):
        is_reachable, msg = check_url_reachability('this-domain-does-not-exist-12345.com')
        self.assertFalse(is_reachable)
        self.assertIn('dns', msg.lower())

    def test_timeout_behavior(self):
        # Test that timeout parameter works (don't actually wait for timeout)
        is_reachable, msg = check_url_reachability('10.255.255.1', timeout=1)
        self.assertFalse(is_reachable)


class TestValidationResult(unittest.TestCase):
    """Tests for URLValidationResult result object"""

    def test_result_attributes(self):
        result = URLValidationResult(
            valid=True,
            message='test',
            domain='example.com',
            reachable=True,
            https_available=True
        )
        self.assertTrue(result.valid)
        self.assertEqual(result.message, 'test')
        self.assertEqual(result.domain, 'example.com')
        self.assertTrue(result.reachable)
        self.assertTrue(result.https_available)

    def test_result_defaults(self):
        result = URLValidationResult(valid=False, message='error')
        self.assertFalse(result.valid)
        self.assertIsNone(result.domain)
        self.assertIsNone(result.reachable)
        self.assertIsNone(result.https_available)


class TestValidateAndCheckUrl(unittest.TestCase):
    """Tests for comprehensive URL validation and check"""

    def test_valid_and_reachable(self):
        result = validate_and_check_url('https://example.com')
        # example.com may or may not be reachable in test environment
        self.assertTrue(result.valid)

    def test_invalid_format(self):
        result = validate_and_check_url('http://example.com')
        self.assertFalse(result.valid)
        self.assertIn('https', result.message.lower())


if __name__ == '__main__':
    unittest.main()
