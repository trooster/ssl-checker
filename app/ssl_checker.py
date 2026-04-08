"""
SSL Certificate utilities for checking and extracting certificate information.
"""
import ssl
import socket
import re
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


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
    
    if 'lets encrypt' in issuer_lower or 'letsencrypt' in issuer_lower:
        return 'Let\'s Encrypt'
    elif 'sectigo' in issuer_lower or 'comodo' in issuer_lower:
        return 'Sectigo'
    elif 'digicert' in issuer_lower:
        return 'DigiCert'
    elif 'cloudflare' in issuer_lower:
        return 'Cloudflare'
    elif 'namecheap' in issuer_lower:
        return 'Namecheap'
    elif 'ssl.com' in issuer_lower:
        return 'SSL.com'
    elif 'google' in issuer_lower:
        return 'Google Trust Services'
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
    org_value = (
        issuer_dict.get('O') or
        issuer_dict.get('ORGANIZATIONNAME') or
        issuer_dict.get('organizationName') or
        ''
    )
    if org_value:
        return org_value.strip()

    cn_value = issuer_dict.get('CN') or issuer_dict.get('commonName') or ''
    if cn_value:
        return cn_value.strip()

    return 'Unknown Issuer'


def get_ssl_info(fqdn: str) -> Tuple[Optional[Dict], str]:
    """
    Extract SSL certificate information from a domain.
    """
    from .url_utils import extract_port_from_url
    
    try:
        domain = extract_domain(fqdn)
        port = extract_port_from_url(fqdn)
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((domain, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                der_cert = ssock.getpeercert(binary_form=True)
                
                if not der_cert:
                    return None, "Could not extract DER certificate"
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.der') as tmp:
                    tmp.write(der_cert)
                    tmp.flush()
                    tmp_name = tmp.name
                
                try:
                    # Parse dates with openssl
                    dates_result = subprocess.run(
                        ['openssl', 'x509', '-noout', '-dates', '-in', tmp_name],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    not_before = None
                    not_after = None
                    if dates_result.returncode == 0:
                        for line in dates_result.stdout.split('\n'):
                            if 'notBefore=' in line:
                                not_before_str = line.replace('notBefore=', '').strip()
                                not_before = datetime.strptime(not_before_str, '%b %d %H:%M:%S %Y %Z')
                            if 'notAfter=' in line:
                                not_after_str = line.replace('notAfter=', '').strip()
                                not_after = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                    
                    days_remaining = None
                    if not_after:
                        days_remaining = (not_after - datetime.now()).days
                    
                    # Get issuer
                    issuer_result = subprocess.run(
                        ['openssl', 'x509', '-noout', '-issuer', '-in', tmp_name],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    issuer_name = 'Unknown'
                    if issuer_result.returncode == 0:
                        issuer_line = issuer_result.stdout.strip()
                        issuer_name = issuer_line.replace('issuer=', '').strip()
                        org_match = re.search(r'O=([^,]+)', issuer_name)
                        if org_match:
                            issuer_name = org_match.group(1).strip()
                    
                    # Parse subject for subject_cn
                    subject_result = subprocess.run(
                        ['openssl', 'x509', '-noout', '-subject', '-in', tmp_name],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    subject_cn = 'Unknown'
                    if subject_result.returncode == 0:
                        subject_line = subject_result.stdout.strip()
                        cn_match = re.search(r'CN\s*=\s*([^,/]+)', subject_line)
                        if cn_match:
                            subject_cn = cn_match.group(1).strip()
                    
                    # Get serial number
                    serial_result = subprocess.run(
                        ['openssl', 'x509', '-noout', '-serial', '-in', tmp_name],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    serial_number = 'Unknown'
                    if serial_result.returncode == 0:
                        serial_line = serial_result.stdout.strip()
                        serial_number = serial_line.replace('serial=', '').strip()
                    
                    # Get SHA256 fingerprint
                    fp_result = subprocess.run(
                        ['openssl', 'x509', '-noout', '-fingerprint', '-sha256', '-in', tmp_name],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    sha256_fingerprint = 'N/A'
                    if fp_result.returncode == 0:
                        fp_line = fp_result.stdout.strip()
                        sha256_fingerprint = fp_line.replace('sha256 Fingerprint=', '').strip()
                    
                    issuer_type = determine_issuer_type({}, issuer_name)
                    
                    return {
                        'fqdn': domain,
                        'issuer': issuer_name,
                        'issuer_type': issuer_type,
                        'expiry_date': not_after,
                        'days_remaining': days_remaining,
                        'not_before': not_before,
                        'serial_number': serial_number,
                        'version': 3,
                        'sha256_fingerprint': sha256_fingerprint,
                        'subject_cn': subject_cn,
                        'pem': 'PLACEHOLDER',
                    }, ''
                    
                finally:
                    os.unlink(tmp_name)
                    
    except socket.timeout:
        return None, "Connection timeout"
    except socket.gaierror:
        return None, "DNS resolution failed"
    except Exception as e:
        return None, str(e)
