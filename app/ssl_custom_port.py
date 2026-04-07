"""
SSL utilities for checking certificates on custom ports
"""
import ssl
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple


def get_ssl_info_custom_port(fqdn: str, port: int = 443) -> Tuple[Optional[Dict], str]:
    """
    Extract SSL certificate from a domain on a specific port.
    
    Args:
        fqdn: Domain name or full URL
        port: Port to connect to (default: 443)
        
    Returns:
        Tuple of (cert_info or None, error_message)
    """
    try:
        from .ssl_checker import extract_domain, determine_issuer_type
        
        # Extract domain
        domain = extract_domain(fqdn)
        
        # Connect to the specified port
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Parse certificate
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_remaining = (expiry_date - datetime.now()).days
                
                # Extract issuer information
                issuer_dict = cert.get('issuer', [])
                issuer = extract_issuer_name(issuer_dict) if issuer_dict else 'Unknown'
                
                if isinstance(issuer_dict, list) and issuer_dict and isinstance(issuer_dict[0], list):
                    issuer_full_name = extract_issuer_name(issuer_dict)
                else:
                    issuer_full_name = extract_issuer_name(cert.get('issuer', [])) if 'issuer' in cert else 'Unknown'
                
                # Determine issuer type
                issuer_type = determine_issuer_type(issuer_dict, issuer) if issuer_dict else 'Other'
                
                # Check if certificate is expired or close to expiry
                if days_remaining < 0:
                    status = 'expired'
                elif days_remaining < 30:
                    status = 'critical'
                elif days_remaining < 90:
                    status = 'warning'
                else:
                    status = 'active'
                
                cert_info = {
                    'fqdn': domain,
                    'port': port,
                    'issuer': issuer,
                    'issuer_type': issuer_type,
                    'expiry_date': expiry_date,
                    'days_remaining': days_remaining,
                    'checked_at': None,  # Will be set by caller
                    'status': status,
                    'notBefore': cert.get('notBefore', 'N/A'),
                    'notAfter': cert.get('notAfter', 'N/A'),
                    'serialNumber': cert.get('serialNumber', 'N/A'),
                    'version': cert.get('version', 'Unknown'),
                    'issuer_dict': issuer_dict,
                    'subject_dict': cert.get('subject', []),
                    'subjectAltName': cert.get('subjectAltName', []),
                }
                
                return cert_info, ''
                
    except socket.timeout:
        return None, f"Connection timeout to {domain}:{port}"
    except socket.gaierror:
        return None, f"DNS resolution failed for {domain}"
    except ssl.SSLError as e:
        return None, f"SSL error: {str(e)}"
    except Exception as e:
        return None, str(e)


def extract_issuer_name(issuer_dict: list) -> str:
    """
    Extract issuer common name from certificate issuer list.
    
    Args:
        issuer_dict: Certificate issuer information as list of lists
        
    Returns:
        String with issuer name
    """
    if not issuer_dict:
        return 'Unknown'
    
    # First entry is usually the CN
    if issuer_dict[0]:
        for entry in issuer_dict:
            if entry:
                return entry[0][1] if len(entry) > 1 and len(entry[0]) > 1 else str(entry)
    
    return 'Unknown'
