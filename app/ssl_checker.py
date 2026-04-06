"""
SSL Certificate checking utilities
"""
import ssl
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import re


def get_ssl_info(fqdn: str) -> Tuple[Optional[Dict], str]:  # (info, error_msg)
    """
    Extract SSL certificate information from a domain.
    
    Args:
        fqdn: Fully qualified domain name (e.g., 'example.com' from 'https://example.com')
        
    Returns:
        Tuple of (certificate_info dict or None, error message)
        info contains: issuer, expiry_date, days_remaining, issuer_type
    """
    try:
        # Extract domain from URL if full URL provided
        domain = extract_domain(fqdn)
        
        # Connect to the SSL/TLS endpoint
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Parse certificate
                expiry_date = datetime.strptime(
                    cert['notAfter'], '%b %d %H:%M:%S %Y %Z'
                )
                
                # Calculate days remaining
                days_remaining = (expiry_date - datetime.now()).days
                
                # Extract issuer information
                issuer_dict = {}
                for issuer_entry in cert.get('issuer', []):
                    for sub_entry in issuer_entry:
                        if isinstance(sub_entry, tuple) and len(sub_entry) >= 2:
                            key, value = sub_entry[0], sub_entry[1]
                            issuer_dict[key] = value
                
                issuer_name = extract_issuer_name(issuer_dict)
                issuer_type = determine_issuer_type(issuer_dict, issuer_name)
                
                return {
                    'fqdn': domain,
                    'issuer': issuer_name,
                    'issuer_type': issuer_type,
                    'expiry_date': expiry_date,
                    'days_remaining': days_remaining
                }, ''
    
    except socket.timeout:
        return None, "Connection timeout"
    except socket.gaierror:
        return None, "DNS resolution failed"
    except Exception as e:
        return None, str(e)


def extract_domain(url: str) -> str:
    """Extract domain from URL, removing protocol and ports"""
    # Remove protocol
    domain = url.replace('https://', '').replace('http://', '')
    # Remove port if present
    domain = domain.split(':')[0]
    # Remove trailing slash
    domain = domain.rstrip('/')
    return domain


def extract_issuer_name(issuer_dict: Dict[str, str]) -> str:
    """Extract readable issuer name from certificate issuer dict"""
    name_parts = []
    # Common issuer field order: Common Name, Organization, Organizational Unit
    for key in ['CN', 'commonName', 'O', 'ORGANIZATIONNAME', 'OU', 'ORGANIZATIONALUNITNAME']:
        if key in issuer_dict:
            name_parts.append(issuer_dict[key])
    
    return ' - '.join(name_parts) if name_parts else 'Unknown Issuer'


def determine_issuer_type(issuer_dict: Dict[str, str], issuer_name: str) -> str:
    """
    Determine the type of certificate issuer
    Returns: 'letsencrypt', 'sectigo', 'digiCert', 'comodo', 'other', or 'unknown'
    """
    issuer_normalized = issuer_name.lower()
    
    # Let's Encrypt patterns
    lets_encrypt_patterns = ["let's encrypt", "letsencrypt", "l.e"]
    if any(pattern in issuer_normalized for pattern in lets_encrypt_patterns):
        return 'letsencrypt'
    
    # Sectigo patterns (formerly Comodo)
    sectigo_patterns = ['sectigo', 'sectigo limited']
    if any(pattern in issuer_normalized for pattern in sectigo_patterns):
        return 'sectigo'
    
    # DigiCert patterns
    digicert_patterns = ['digicert', 'digicert trusted']
    if any(pattern in issuer_normalized for pattern in digicert_patterns):
        return 'digiCert'
    
    # Comodo patterns (now Sectigo, but keeping for backward compat)
    comodo_patterns = ['comodo', 'positive']
    if any(pattern in issuer_normalized for pattern in comodo_patterns):
        return 'comodo'
    
    # GoDaddy patterns
    godaddy_patterns = ['godaddy', 'gd']
    if any(pattern in issuer_normalized for pattern in godaddy_patterns):
        return 'godaddy'
    
    # Cloudflare patterns
    cloudflare_patterns = ['cloudflare']
    if any(pattern in issuer_normalized for pattern in cloudflare_patterns):
        return 'cloudflare'
    
    return 'other'


def should_refresh_cache(days_remaining: int, checked_at: datetime, expiration_hours: int) -> bool:
    """
    Determine if cache should be refreshed based on days remaining and expiration time
    
    Caching strategy:
    - Critical (< 30 days): refresh hourly
    - Warning (30-90 days): refresh every 12 hours  
    - Safe (> 90 days): refresh daily
    """
    hours_since_check = (datetime.now() - checked_at).total_seconds() / 3600
    
    if days_remaining < 30:
        # Critical: check every hour
        return hours_since_check > 1
    elif days_remaining < 90:
        # Warning: check every 12 hours
        return hours_since_check > 12
    else:
        # Safe: check daily
        return hours_since_check > 300
        # Actually, 24 hours for safety
        return hours_since_check > 24
