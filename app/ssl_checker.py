"""
SSL Certificate checking utilities
"""
import ssl
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import re


def extract_domain(url: str) -> str:
    """
    Extract domain name from URL.
    
    Args:
        url: URL or FQDN
        
    Returns:
        Clean domain name without protocol
    """
    # Remove protocol
    domain = url.replace('https://', '').replace('http://', '')
    # Remove path
    domain = domain.split('/')[0]
    # Remove port if present
    domain = domain.split(':')[0]
    return domain.lower()


def determine_issuer_type(issuer_dict: dict, issuer_name: str) -> str:
    """
    Determine the type of SSL certificate issuer.
    
    Args:
        issuer_dict: Extracted issuer information dict
        issuer_name: Human readable issuer name
        
    Returns:
        Type of issuer: 'Let's Encrypt', 'Sectigo', 'DigiCert', 'Other', etc.
    """
    issuer_lower = issuer_name.lower()
    
    if 'letsencrypt' in issuer_lower or 'lencr' in issuer_lower:
        return 'Let\'s Encrypt'
    elif 'sectigo' in issuer_lower or 'comodo' in issuer_lower:
        return 'Sectigo'
    elif 'digicert' in issuer_lower:
        return 'DigiCert'
    elif 'geotrust' in issuer_lower:
        return 'GeoTrust'
    elif 'globalsign' in issuer_lower:
        return 'GlobalSign'
    elif 'buypass' in issuer_lower:
        return 'Buypass'
    elif 'zahner' in issuer_lower:
        return 'Zauner'
    elif 'amazon' in issuer_lower:
        return 'Amazon'
    elif 'google' in issuer_lower:
        return 'Google Trust Services'
    elif 'cloudflare' in issuer_lower:
        return 'Cloudflare'
    elif 'namecheap' in issuer_lower:
        return 'Namecheap'
    elif 'ssl.com' in issuer_lower:
        return 'SSL.com'
    else:
        return 'Other'


def extract_certificate_fields(issuer_entries):
    """Convert issuer/subject entries dict into a simple dict."""
    result = {}
    for issuer_entry in issuer_entries:
        for sub_entry in issuer_entry:
            if isinstance(sub_entry, tuple) and len(sub_entry) >= 2:
                key, value = sub_entry[0], sub_entry[1]
                result[key] = value
            elif isinstance(sub_entry, str):
                result[sub_entry] = sub_entry
    return result


def extract_readable_name(issuer_dict):
    """Extract readable issuer name from certificate issuer dict, preserving order."""
    # Common order: CN, Organization, Organizational Unit
    cn_value = issuer_dict.get('CN') or issuer_dict.get('commonName') or ''
    org_value = issuer_dict.get('O') or issuer_dict.get('ORGANIZATIONNAME') or ''
    ou_value = issuer_dict.get('OU') or issuer_dict.get('ORGANIZATIONALUNITNAME') or ''
    
    parts = []
    if cn_value: parts.append(cn_value)
    if org_value: parts.append(org_value)
    if ou_value: parts.append(ou_value)
    
    return ' - '.join(parts) if parts else 'Unknown Issuer'


def get_ssl_info(fqdn: str) -> Tuple[Optional[Dict], str]:  # (info, error_msg)
    """
    Extract SSL certificate information from a domain.
    
    Args:
        fqdn: Fully qualified domain name (e.g., 'example.com' from 'https://example.com')
        
    Returns:
        Tuple of (certificate_info dict or None, error message)
        info contains: issuer, expiry_date, days_remaining, issuer_type, and full details
    """
    try:
        # Extract domain from URL if full URL provided
        domain = extract_domain(fqdn)
        
        # Connect to the SSL/TLS endpoint
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        
                # Parse certificate data (getpeercert returns dict, not DER bytes)
                expiry_date = datetime.strptime(
                    cert['notAfter'], '%b %d %H:%M:%S %Y %Z'
                )
        
                # Calculate days remaining
                days_remaining = (expiry_date - datetime.now()).days
        
                # Extract issuer and subject information
                issuer_dict = extract_certificate_fields(cert.get('issuer', []))
                subject_dict = extract_certificate_fields(cert.get('subject', []))
        
                # Extract all certificate details
                serial_number = cert.get('serialNumber', 'Unknown')
                not_before = datetime.strptime(
                    cert.get('notBefore', 'Unknown'), '%b %d %H:%M:%S %Y %Z'
                )
        
                # Get certificate version
                version = cert.get('version', 'Unknown')
        
                # Fingerprint
                digest = cert.get('digest', {})
                if isinstance(digest, dict):
                    sha256_val = digest.get('SHA256')
                    if sha256_val is not None and isinstance(sha256_val, (bytes, bytearray)):
                        sha256_fingerprint = ':'.join(f'{b:02X}' for b in sha256_val)
                    elif sha256_val is not None and isinstance(sha256_val, str):
                        sha256_fingerprint = sha256_val.replace(':', '')
                        sha256_fingerprint = ':'.join(f'{ord(c):02X}' for c in sha256_fingerprint)
                    else:
                        sha256_fingerprint = 'N/A'
                else:
                    sha256_fingerprint = 'N/A (not found in cert)'
        
                # Subject Alternative Names (SANs)
                san_entries = cert.get('subjectAltName', [])
                san_list = []
                for entry_type, entry_value in san_entries:
                    san_list.append(f"{entry_type}: {entry_value}")
                san_string = '\n'.join(san_list)
        
                # Certificate PEM extraction - use openssl for full data
                cert_pem = 'PLACEHOLDER: Use OpenSSL CLI to export actual PEM data'
        
                issuer_name = extract_readable_name(issuer_dict)
                issuer_type = determine_issuer_type(issuer_dict, issuer_name)
        
                return {
                    'fqdn': domain,
                    'issuer': issuer_name,
                    'issuer_type': issuer_type,
                    'expiry_date': expiry_date,
                    'days_remaining': days_remaining,
                    'not_before': not_before,
                    'serial_number': serial_number,  # Don't try to convert hex serial number
                    'version': version,
                    'sha256_fingerprint': sha256_fingerprint,
                    'san_string': san_string,
                    'subject_cn': subject_dict.get('CN', subject_dict.get('commonName', 'Unknown')),
                    'pem': cert_pem,
                }, ''
    except socket.timeout:
        return None, "Connection timeout"
    except socket.gaierror:
        return None, "DNS resolution failed"
    except Exception as e:
        return None, str(e)
