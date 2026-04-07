#!/usr/bin/env python3
"""
SSL Certificate Refresh Script
Runs automatically via cron to refresh all certificate cache entries.
"""

import sys
sys.path.insert(0, '/home/joris/ssl-checker')

from app.ssl_checker import get_ssl_info, extract_domain
from app.database import get_db
from datetime import datetime


def refresh_all_certificates():
    """Refresh certificate data for all URLs in the database."""
    # Import after path setup
    from flask import g
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        db = get_db()
    
    # Get all URLs
    urls = db.execute('SELECT id, fqdn FROM urls').fetchall()
    
    print(f"Found {len(urls)} URLs to check")
    
    for url in urls:
        url_id = url['id']
        fqdn = url['fqdn']
        
        try:
            # Get fresh certificate data
            cert_info, error = get_ssl_info(fqdn)
            
            if cert_info and not error:
                # Extract data from certificate
                days_remaining = cert_info.get('days_remaining')
                expiry_date = cert_info.get('expiry_date', 'N/A')
                
                # Format expiry date properly
                if hasattr(expiry_date, 'strftime'):
                    expiry_str = expiry_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    expiry_str = str(expiry_date)
                
                # Determine status
                if days_remaining is not None and days_remaining < 0:
                    status = 'expired'
                elif days_remaining is not None and days_remaining < 30:
                    status = 'critical'
                elif days_remaining is not None and days_remaining < 90:
                    status = 'warning'
                else:
                    status = 'active'
                
                # Update cache
                domain = extract_domain(fqdn)
                db.execute('''
                    INSERT OR REPLACE INTO ssl_cache 
                    (fqdn, issuer, issuer_type, expiry_date, days_remaining, checked_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    domain,
                    cert_info.get('issuer', 'Unknown'),
                    cert_info.get('issuer_type', 'unknown'),
                    expiry_str,
                    days_remaining,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    status
                ))
                
                print(f"✓ Updated {fqdn}: {days_remaining} days, status: {status}")
            else:
                print(f"✗ Failed to refresh {fqdn}: {error}")
                
        except Exception as e:
            print(f"✗ Error refreshing {fqdn}: {str(e)}")
    
        db.commit()
        print(f"\nRefresh complete. Updated {len(urls)} certificates.")


if __name__ == '__main__':
    refresh_all_certificates()
