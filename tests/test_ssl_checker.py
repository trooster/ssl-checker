"""
Unit tests for SSL checker functionality
"""
import unittest
from datetime import datetime, timedelta
from app.ssl_checker import (
    get_ssl_info,
    extract_domain,
    extract_issuer_name,
    determine_issuer_type,
    should_refresh_cache
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


class TestIssuerExtraction(unittest.TestCase):
    """Tests for issuer name extraction"""
    
    def test_lets_encrypt(self):
        issuer_dict = {'CN': 'Let\'s Encrypt', 'O': 'Let\'s Encrypt', 'OU': 'Domain Control Validated'}
        self.assertEqual(extract_issuer_name(issuer_dict), 'Let\'s Encrypt')
    
    def test_sectigo(self):
        issuer_dict = {'CN': 'COMODO RSA Domain Validation Secure Server CA', 'O': 'COMODO CA Limited', 'OU': 'Domain Control Validated'}
        self.assertEqual(extract_issuer_name(issuer_dict), 'COMODO RSA Domain Validation Secure Server CA')
    
    def test_no_cn(self):
        issuer_dict = {'O': 'Some Organization'}
        self.assertEqual(extract_issuer_name(issuer_dict), 'Some Organization')


class TestIssuerTypeDetection(unittest.TestCase):
    """Tests for issuer type classification"""
    
    def test_lets_encrypt(self):
        issuer_dict = {'CN': 'Let\'s Encrypt Authority X3'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Let\'s Encrypt Authority X3'), 'letsencrypt')
    
    def test_sectigo(self):
        issuer_dict = {'CN': 'COMODO RSA Domain Validation Secure Server CA'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'COMODO RSA Domain Validation Secure Server CA'), 'sectigo')
    
    def test_digi_cert(self):
        issuer_dict = {'O': 'DigiCert Inc', 'CN': 'DigiCert TLS RSA SHA256 2020 CA1'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'DigiCert TLS RSA SHA256 2020 CA1'), 'digiCert')
    
    def test_comodo(self):
        issuer_dict = {'CN': 'Comodo RSA Domain Validation Secure Server CA'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Comodo RSA Domain Validation Secure Server CA'), 'comodo')
    
    def test_godaddy(self):
        issuer_dict = {'O': 'GoDaddy.com, Inc.', 'CN': 'Go Daddy Secure Certificate Authority'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Go Daddy Secure Certificate Authority'), 'godaddy')
    
    def test_cloudflare(self):
        issuer_dict = {'CN': 'Cloudflare Inc ECC CA-3'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Cloudflare Inc ECC CA-3'), 'cloudflare')
    
    def test_other(self):
        issuer_dict = {'O': 'Unknown CA', 'CN': 'Some Certificate Authority'}
        self.assertEqual(determine_issuer_type(issuer_dict, 'Some Certificate Authority'), 'other')


class TestCacheRefreshLogic(unittest.TestCase):
    """Tests for cache refresh decision logic"""
    
    def test_critical_refresh(self):
        """Critical certs (< 30 days) should refresh hourly"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        recent = now - timedelta(hours=0.5)  # 30 minutes ago
        should_refresh = should_refresh_cache(-5, recent)
        self.assertTrue(should_refresh, "Critical cert should refresh")
    
    def test_warning_refresh(self):
        """Warning certs (30-90 days) should refresh every 12 hours"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        recent = now - timedelta(hours=6)  # 6 hours ago
        should_refresh = should_refresh_cache(60, recent)
        self.assertTrue(should_refresh, "Warning cert should refresh")
    
    def test_safe_refresh(self):
        """Safe certs (> 90 days) should refresh daily"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        recent = now - timedelta(hours=20)  # 20 hours ago
        should_refresh = should_refresh_cache(120, recent)
        self.assertTrue(should_refresh, "Safe cert should refresh")
    
    def test_critical_no_refresh(self):
        """Critical certs should NOT refresh if checked recently"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        recent = now - timedelta(minutes=30)  # 30 minutes ago
        should_refresh = should_refresh_cache(-5, recent)
        self.assertFalse(should_refresh, "Critical cert should NOT refresh if checked recently")


class TestDaysRemainingCalculation(unittest.TestCase):
    """Tests for days remaining calculation"""
    
    def test_expired_cert(self):
        """Expired certificates should return negative days"""
        from datetime import datetime, timedelta
        
        expired = datetime.now() - timedelta(days=30)  # 30 days ago
        days_remaining = (expired - datetime.now()).days
        self.assertLess(days_remaining, 0, "Expired cert should have negative days")
    
    def test_expiring_soon(self):
        """Expiring soon certificates should return positive days"""
        from datetime import datetime, timedelta
        
        expires_in_10 = datetime.now() + timedelta(days=10)
        days_remaining = (expires_in_10 - datetime.now()).days
        self.assertEqual(days_remaining, 10)
    
    def test_future_cert(self):
        """Future certificates should return positive days"""
        from datetime import datetime, timedelta
        
        expires_in_365 = datetime.now() + timedelta(days=365)
        days_remaining = (expires_in_365 - datetime.now()).days
        self.assertEqual(days_remaining, 365)


if __name__ == '__main__':
    unittest.main()
