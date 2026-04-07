"""
Extended SSL Certificate utilities for detailed certificate information
"""
import ssl
import socket
from datetime import datetime
from typing import Dict, Optional, Tuple


def get_full_certificate_info(fqdn: str) -> Tuple[Optional[Dict], str]:
    """
    Extract comprehensive SSL certificate information.
    
    Args:
        fqdn: Full domain name with optional protocol prefix
        
    Returns:
        Tuple of (full_cert_dict or None, error_msg)
        dict contains: basic info + detailed properties
    """
    try:
        from .ssl_checker import extract_domain, get_ssl_info
        
        # Get basic info first
        basic_info, error = get_ssl_info(fqdn)
        if not basic_info:
            if error:
                return None, error
            return None, "Could not retrieve certificate"
        
        # Connect to SSL to get full details
        domain = extract_domain(fqdn)
        
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Extract all certificate details
                cert_info = {
                    'fqdn': domain,
                    'issuer': basic_info.get('issuer', 'Unknown'),
                    'issuer_type': basic_info.get('issuer_type', 'unknown'),
                    'expiry_date': basic_info.get('expiry_date', 'Unknown'),
                    'days_remaining': basic_info.get('days_remaining', None),
                    'not_before': cert.get('notBefore', 'Unknown'),
                    'serial_number': cert.get('serialNumber', 'Unknown'),
                    'version': cert.get('version', 3),
                    'subject': extract_certificate_subject(cert),
                    'issuer_details': extract_certificate_issuer_details(cert),
                    'fingerprint_sha256': cert.get('sha256Digest', 'N/A'),
                    'fingerprint_md5': 'N/A (requires openssl)',
                    'san_list': cert.get('subjectAltName', []),
                    'san_string': ', '.join([str(san[1]) for san in cert.get('subjectAltName', [])]),
                    'key_algorithm': extract_key_algorithm(cert),
                    'key_size': extract_key_size(cert),
                    'signature_algorithm': cert.get('signatureAlgorithm', 'Unknown'),
                    'basic_constraints': extract_basic_constraints(cert),
                    'key_usage': extract_key_usage(cert),
                    'extended_key_usage': extract_extended_key_usage(cert)
                }
                
                return cert_info, ''
                
    except socket.timeout:
        return None, "Connection timeout"
    except socket.gaierror:
        return None, "DNS resolution failed"
    except Exception as e:
        return None, str(e)


def extract_certificate_subject(cert: dict) -> dict:
    """Extract subject/owner information from certificate."""
    subject = {}
    for sub_entry in cert.get('subject', []):
        for key, value in sub_entry:
            subject[key] = value
    return subject


def extract_certificate_issuer_details(cert: dict) -> dict:
    """Extract detailed issuer information."""
    issuer = {}
    for issuer_entry in cert.get('issuer', []):
        for key, value in issuer_entry:
            issuer[key] = value
    return issuer


def extract_sha256_fingerprint(cert: dict) -> str:
    """Extract SHA-256 fingerprint from certificate."""
    sha256_hash = cert.get('sha256Digest', 'N/A')
    return sha256_hash


def extract_md5_fingerprint(cert: dict) -> str:
    """Extract MD5 fingerprint from certificate - not available from Python's getpeercert()."""
    return 'N/A (requires openssl)'


def extract_key_algorithm(cert: dict) -> str:
    """Extract public key algorithm."""
    return cert.get('publicKeyAlgorithm', 'Unknown')


def extract_key_size(cert: dict) -> Optional[int]:
    """Extract public key size in bits."""
    return cert.get('publicKeySizes', {}).get('RSA') or cert.get('publicKey', {}).get('size')


def extract_basic_constraints(cert: dict) -> dict:
    """Extract basic constraints (CA status)."""
    constraints = {}
    for entry in cert.get('versionData', {}).get('extensions', []):
        if entry[0] == 'Basic Constraints':
            constraints['is_ca'] = entry[1].get('CA', False)
            constraints['path_len'] = entry[1].get('CACerts')
    return constraints


def extract_key_usage(cert: dict) -> dict:
    """Extract key usage extensions."""
    usage = {}
    for entry in cert.get('extensions', []):
        if entry[0] == 'Key Usage':
            usage['digital_signature'] = entry[1].get('digitalSignature', False)
            usage['key_encipherment'] = entry[1].get('keyEncipherment', False)
            usage['content_commitment'] = entry[1].get('contentCommitment', False)
            usage['key_agreement'] = entry[1].get('keyAgreement', False)
            break
    return usage


def extract_extended_key_usage(cert: dict) -> list:
    """Extract extended key usage."""
    usage = []
    for entry in cert.get('extensions', []):
        if entry[0] == 'Extended Key Usage':
            usage = entry[1]  # List of OID names
            break
    return usage
