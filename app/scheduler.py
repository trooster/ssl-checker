"""
Background scheduler for SSL certificate refresh
"""
import schedule
import time
from datetime import datetime
from .database import get_db, close_db
from .ssl_checker import get_ssl_info


def refresh_stale_certs():
    """Refresh SSL certificate data that is stale"""
    db = get_db()
    
    # Get all URLs
    urls = db.execute('SELECT fqdn FROM urls').fetchall()
    
    for url_entry in urls:
        fqdn = url_entry['fqdn']
        
        # Get current cache entry
        cache = db.execute(
            'SELECT days_remaining, checked_at, status FROM ssl_cache WHERE fqdn = ?',
            (fqdn,)
        ).fetchone()
        
        if not cache:
            # No cache entry, force refresh
            force_refresh_cert(fqdn, db)
            continue
        
        # Calculate if we should refresh based on our strategy
        hours_since_check = (datetime.now() - cache['checked_at']).total_seconds() / 3600
        
        if hours_since_check > 24:  # Daily refresh
            force_refresh_cert(fqdn, db)


def force_refresh_cert(fqdn: str, db):
    """Force refresh SSL certificate for a specific domain"""
    try:
        cert_info, error = get_ssl_info(fqdn)
        
        if cert_info:
            # Update or insert cache entry
            existing = db.execute(
                'SELECT id FROM ssl_cache WHERE fqdn = ?',
                (fqdn,)
            ).fetchone()
            
            if existing:
                db.execute('''
                    UPDATE ssl_cache 
                    SET issuer = ?,
                        issuer_type = ?,
                        expiry_date = ?,
                        days_remaining = ?,
                        checked_at = ?,
                        status = ?
                    WHERE fqdn = ?
                ''', (
                    cert_info['issuer'],
                    cert_info['issuer_type'],
                    cert_info['expiry_date'],
                    cert_info['days_remaining'],
                    datetime.now(),
                    status_for_days(cert_info['days_remaining']),
                    fqdn
                ))
            else:
                db.execute('''
                    INSERT INTO ssl_cache 
                        (fqdn, issuer, issuer_type, expiry_date, days_remaining, checked_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fqdn,
                    cert_info['issuer'],
                    cert_info['issuer_type'],
                    cert_info['expiry_date'],
                    cert_info['days_remaining'],
                    datetime.now(),
                    status_for_days(cert_info['days_remaining'])
                ))
            
            db.commit()
            print(f"✓ Refreshed SSL cert for {fqdn}: {cert_info['days_remaining']} days remaining")
        else:
            print(f"✗ Failed to refresh SSL cert for {fqdn}: {error}")
            
    except Exception as e:
        print(f"✗ Error refreshing {fqdn}: {str(e)}")


def status_for_days(days_remaining: int) -> str:
    """Determine status based on days remaining"""
    if days_remaining < 0:
        return 'expired'
    elif days_remaining < 30:
        return 'expiring_soon'
    elif days_remaining < 90:
        return 'warning'
    else:
        return 'active'


def run_scheduler():
    """Run the SSL refresh scheduler"""
    refresh_stale_certs()
    schedule.every(24).hours.do(refresh_stale_certs)
    
    print("SSL Monitor Scheduler started")
    print("Refreshing certificates on a daily basis...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
