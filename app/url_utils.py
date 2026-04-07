"""
URL and SSL utilities
"""
import ssl
import socket
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, NamedTuple

class URLValidationResult(NamedTuple):
    """Validation result for URL checking"""
    valid: bool
    message: str
    domain: str = None
    reachable: bool = None
    https_available: bool = None


def validate_url_format(url: str) -> Tuple[bool, str]:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove whitespace
    url = url.strip()
    
    if not url:
        return False, "URL is empty"
    
    # Check if it looks like an SSL URL (https://)
    if not url.startswith('https://'):
        return False, "URL must start with https://"
    
    # Extract domain
    domain = extract_domain(url)
    
    if not domain:
        return False, "Invalid domain in URL"
    
    # Validate domain format (basic check)
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if not re.match(domain_pattern, domain):
        return False, f"Invalid domain format: {domain}"
    
    # Check for consecutive dots
    if '..' in domain:
        return False, "Domain contains consecutive dots"
    
    # Check for leading/trailing dashes in labels
    labels = domain.split('.')
    for label in labels:
        if label.startswith('-') or label.endswith('-'):
            return False, f"Domain label '{label}' cannot start or end with hyphen"
    
    return True, "Valid"


def check_url_reachability(domain: str, timeout: int = 5) -> Tuple[bool, str]:
    """
    Check if a domain is reachable on port 443 (SSL).
    
    Args:
        domain: Domain name to check
        timeout: Connection timeout in seconds
        
    Returns:
        Tuple of (is_reachable, message)
    """
    try:
        # Try to resolve and connect
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # If we can complete SSL handshake, the server is reachable
                ssock.getpeername()
                return True, "Server is reachable"
    except socket.timeout:
        return False, "Connection timeout"
    except socket.gaierror:
        return False, "DNS resolution failed"
    except ConnectionRefusedError:
        return False, "Connection refused (SSL service not running)"
    except ssl.SSLError as e:
        return False, f"SSL error: {str(e)}"
    except Exception as e:
        return False, f"Connection test failed: {str(e)}"


def validate_and_check_url(url: str) -> URLValidationResult:
    """
    Comprehensive URL validation and reachability check.
    
    Args:
        url: URL to validate and check
        
    Returns:
        URLValidationResult with validation status and details
    """
    # Validate format
    is_valid, msg = validate_url_format(url)
    if not is_valid:
        return URLValidationResult(valid=False, message=msg)
    
    domain = extract_domain(url)
    
    # Check reachability
    reachable, reach_msg = check_url_reachability(domain)
    
    if not reachable:
        return URLValidationResult(valid=False, message=reach_msg, domain=domain, reachable=False)
    
    # Try to get SSL certificate to confirm HTTPS is available
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    return URLValidationResult(
                        valid=True, 
                        message="Valid and reachable",
                        domain=domain,
                        reachable=True,
                        https_available=True
                    )
    except ssl.SSLError:
        pass  # SSL available but cert issue, still valid for monitoring
    
    return URLValidationResult(
        valid=True, 
        message="Valid but SSL cert issue",
        domain=domain,
        reachable=True,
        https_available=True
    )


def extract_port_from_url(url: str) -> int:
    """
    Extract port number from URL.
    
    Args:
        url: URL with optional port (e.g., https://example.com:8443)
        
    Returns:
        Port number (default 443 for HTTPS)
    """
    if not url:
        return 443
    
    # Parse URL to get port
    # Format: https://domain:port or https://domain
    import re
    match = re.search(r':(\d+)', url.split('://')[-1].split('/')[0])
    if match:
        return int(match.group(1))
    return 443  # Default HTTPS port


def extract_domain(url: str) -> str:
    """
    Extract domain name from URL.
    
    Args:
        url: URL or FQDN
        
    Returns:
        Clean domain name without protocol
    """
    if not url:
        return ""
    
    # Remove whitespace
    url = url.strip()
    
    # Remove protocol
    domain = url.replace('https://', '').replace('http://', '')
    
    # Remove port if present (handle : before /)
    # First, check if there's a port after https://domain
    if '://' in domain:
        domain = domain.split('://')[1]
    
    # Remove path
    domain = domain.split('/')[0]
    
    # Remove port
    domain = domain.split(':')[0]
    
    # Remove trailing port pattern for IPv6
    if domain.startswith('['):
        domain = domain.split(']')[0] + ']'
    
    return domain.lower()
