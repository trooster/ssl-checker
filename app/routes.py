"""
Main request routes and API endpoints
"""
from flask import Blueprint, render_template, request, jsonify, g, current_app, redirect, url_for, flash
from .database import get_db
from .ssl_checker import get_ssl_info, extract_domain, extract_readable_name
from datetime import datetime


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main overview page showing all SSL certificates"""
    sort_by = request.args.get('sort_by', 'days_remaining')
    sort_order = request.args.get('sort_order', 'asc')
    
    db = get_db()
    
    # Build query with sorting
    query = '''
        SELECT 
            u.id,
            u.fqdn,
            u.customer_number,
            u.customer_name,
            COALESCE(sc.issuer, 'Unknown') as issuer,
            COALESCE(sc.issuer_type, 'unknown') as issuer_type,  
            COALESCE(sc.expiry_date, 'N/A') as expiry_date,
            COALESCE(sc.days_remaining, null) as days_remaining,
            COALESCE(sc.checked_at, 'Never') as checked_at,
            COALESCE(sc.status, 'unknown') as status
        FROM urls u
        LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
    '''
    
    # Add sorting - support days_remaining, customer_name, fqdn
    sort_mappings = {
        'days_remaining': 'sc.days_remaining',
        'customer_name': 'u.customer_name',
        'fqdn': 'u.fqdn',
        'expiry_date': 'sc.expiry_date'
    }
    
    sort_field = sort_mappings.get(sort_by, 'sc.days_remaining')
    order = 'ASC' if sort_order == 'asc' else 'DESC'
    
    query += f' ORDER BY {sort_field} {order}'
    
    urls = db.execute(query).fetchall()
    
    return render_template('index.html', urls=urls, sort_by=sort_by, sort_order=sort_order)


@main_bp.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin page for managing URLs"""
    url_id = request.args.get('edit', type=int)
    delete_id = request.args.get('delete', type=int)
    edit_url = {}
    db = get_db()
    
    if request.method == 'GET' and delete_id:
        # Handle deletion via GET parameters
        db.execute('DELETE FROM urls WHERE id = ?', (delete_id,))
        db.commit()
        flash('Certificate deleted successfully', 'success')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST' and delete_id:
        # Handle deletion via POST from form submission
        db.execute('DELETE FROM urls WHERE id = ?', (delete_id,))
        db.commit()
        flash('Certificate deleted successfully', 'success')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST' and url_id:
        # Handle form submission
        data = request.form
        
        # Check if URL already exists (for updates)
        existing = db.execute(
            'SELECT id FROM urls WHERE fqdn = ? AND id != ?',
            (data['fqdn'], url_id)
        ).fetchone()
        
        if existing:
            flash('URL already exists, cannot update', 'error')
            return redirect(url_for('main.admin', edit=url_id))
        
        # Update the URL
        db.execute('''
            UPDATE urls 
            SET fqdn = ?,
                customer_number = ?,
                customer_name = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (data['fqdn'], data.get('customer_number', ''), data.get('customer_name', ''), url_id))
        db.commit()
        flash('Certificate updated successfully', 'success')
        return redirect(url_for('main.admin'))
    
    if request.method == 'POST':
        # Handle new URL addition
        data = request.form
        
        # Check if URL already exists
        existing = db.execute(
            'SELECT id FROM urls WHERE fqdn = ?',
            (data['fqdn'],)
        ).fetchone()
        
        if existing:
            flash('URL already exists', 'error')
        else:
            db.execute('''
                INSERT INTO urls (fqdn, customer_number, customer_name)
                VALUES (?, ?, ?)
            ''', (data['fqdn'], data.get('customer_number', ''), data.get('customer_name', '')))
            db.commit()
            flash('Certificate added successfully', 'success')
        
        # Redirect to overview page after adding
        return redirect(url_for('main.index'))
    
    if url_id:
        edit_url = db.execute(
            'SELECT * FROM urls WHERE id = ?',
            (url_id,)
        ).fetchone()
    
    return render_template('admin.html', edit_url=edit_url)


@main_bp.route('/api/urls', methods=['GET'])
def get_urls():
    """API endpoint to get all URLs (supports sorting)"""
    sort_by = request.args.get('sort_by', 'days_remaining')
    sort_order = request.args.get('sort_order', 'asc')
    
    db = get_db()
    
    query = '''
        SELECT 
            u.id,
            u.fqdn,
            u.customer_number,
            u.customer_name,
            COALESCE(sc.issuer, 'Unknown') as issuer,
            COALESCE(sc.issuer_type, 'unknown') as issuer_type,
            COALESCE(sc.expiry_date, 'N/A') as expiry_date,
            COALESCE(sc.days_remaining, null) as days_remaining,
            COALESCE(sc.checked_at, 'Never') as checked_at,
            COALESCE(sc.status, 'unknown') as status
        FROM urls u
        LEFT JOIN ssl_cache sc ON 
            LOWER(REPLACE(LOWER(u.fqdn), 'https://', '')) LIKE '%' || LOWER(sc.fqdn) || '%'
            OR LOWER(u.fqdn) LIKE '%' || LOWER(REPLACE(sc.fqdn, 'https://', '')) || '%'
    '''
    
    sort_mappings = {
        'days_remaining': 'sc.days_remaining',
        'customer_name': 'u.customer_name',
        'fqdn': 'u.fqdn',
        'expiry_date': 'sc.expiry_date'
    }
    
    sort_field = sort_mappings.get(sort_by, 'sc.days_remaining')
    order = 'ASC' if sort_order == 'asc' else 'DESC'
    
    query += f' ORDER BY {sort_field} {order}'
    
    urls = db.execute(query).fetchall()
    
    return jsonify({
        'urls': [dict(url) for url in urls],
        'count': len(urls)
    })


@main_bp.route('/api/urls', methods=['POST'])
def add_url():
    """API endpoint to add a new URL with full validation"""
    from .url_utils import validate_and_check_url
    from datetime import datetime
    
    data = request.get_json()
    fqdn = data.get('fqdn')
    customer_number = data.get('customer_number')
    customer_name = data.get('customer_name')
    
    if not fqdn:
        return jsonify({'error': 'FQDN is required'}), 400
    
    # Validate URL format and check reachability
    validation = validate_and_check_url(fqdn)
    
    if not validation.valid:
        return jsonify({
            'error': 'Validation failed',
            'details': validation.message,
            'domain': validation.domain,
            'reachable': validation.reachable
        }), 400
    
    # Domain validation passed, add URL
    try:
        db = get_db()
        db.execute('''
            INSERT INTO urls (fqdn, customer_number, customer_name)
            VALUES (?, ?, ?)
        ''', (fqdn, customer_number, customer_name))
        db.commit()
        
        # Immediately check the certificate and save to cache
        cert_info, error = get_ssl_info(fqdn)
        
        # Always save to cache - with actual data if available, placeholder otherwise
        domain_name = extract_domain(fqdn)
        
        if cert_info is not None and not error:
            # Use actual certificate data
            days = cert_info.get('days_remaining')
            if hasattr(cert_info.get('expiry_date'), 'strftime'):
                expiry = cert_info['expiry_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                expiry = str(cert_info.get('expiry_date', 'N/A'))
            issuer = cert_info.get('issuer', 'Unknown')
            issuer_type = cert_info.get('issuer_type', 'unknown')
            checked = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Determine status based on days remaining
            if days is not None and days != 'N/A':
                if days < 0:
                    status = 'expired'
                elif days < 30:
                    status = 'critical'
                elif days < 90:
                    status = 'warning'
                else:
                    status = 'active'
            else:
                status = 'unknown'
                expiry = 'N/A'
                days = None
        else:
            # No certificate info available (DNS error or similar)
            days = None
            expiry = 'N/A'
            issuer = 'Unknown'
            issuer_type = 'unknown'
            checked = 'Never'
            status = 'unknown'
        
        # Insert or update cache entry
        db.execute('''
            INSERT OR REPLACE INTO ssl_cache (fqdn, issuer, issuer_type, expiry_date, days_remaining, checked_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (domain_name, issuer, issuer_type, expiry, days, checked, status))
        db.commit()
            
        return jsonify({
            'success': True,
            'message': 'URL added and certificate initialized',
            'url_id': db.execute('SELECT last_insert_rowid()').fetchone()[0]
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/urls/validate', methods=['POST'])
def validate_url():
    """API endpoint to validate a URL format and reachability without adding it"""
    from .url_utils import validate_and_check_url
    
    data = request.get_json()
    fqdn = data.get('fqdn')
    
    if not fqdn:
        return jsonify({'error': 'FQDN is required'}), 400
    
    # Validate URL format and check reachability
    validation = validate_and_check_url(fqdn)
    
    return jsonify({
        'valid': validation.valid,
        'message': validation.message,
        'domain': validation.domain,
        'reachable': validation.reachable,
        'https_available': validation.https_available
    })


@main_bp.route('/api/urls/<int:url_id>', methods=['PUT'])
def update_url(url_id):
    """API endpoint to update an existing URL"""
    data = request.get_json()
    fqdn = data.get('fqdn')
    customer_number = data.get('customer_number')
    customer_name = data.get('customer_name')
    
    # Check if URL exists
    db = get_db()
    existing = db.execute(
        'SELECT id FROM urls WHERE id = ?',
        (url_id,)
    ).fetchone()
    
    if not existing:
        return jsonify({'error': 'URL not found'}), 404
    
    try:
        db.execute('''
            UPDATE urls 
            SET fqdn = ?,
                customer_number = ?,
                customer_name = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (fqdn, customer_number, customer_name, url_id))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'URL updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/urls/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    """API endpoint to delete a URL"""
    db = get_db()
    
    # Check if URL exists
    existing = db.execute(
        'SELECT id FROM urls WHERE id = ?',
        (url_id,)
    ).fetchone()
    
    if not existing:
        return jsonify({'error': 'URL not found'}), 404
    
    try:
        db.execute('DELETE FROM urls WHERE id = ?', (url_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'URL deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/certs/<string:fqdn>/refresh', methods=['POST'])
def refresh_cert(fqdn):
    """API endpoint to force refresh SSL certificate for a specific domain"""
    from .ssl_checker import extract_domain
    try:
        db = get_db()
        cert_info, error = get_ssl_info(fqdn)
        
        if cert_info:
            # Use the extracted domain name for matching (without https://)
            domain_name = cert_info['fqdn']
            
            # Update or insert cache entry
            existing = db.execute(
                'SELECT id FROM ssl_cache WHERE fqdn LIKE ?',
                (f'%{domain_name}%',)
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
            
            return jsonify({
                'success': True,
                'message': 'Certificate refreshed',
                'data': cert_info
            })
        else:
            # Still return success but note that we couldn't fetch cert
            return jsonify({
                'success': True,
                'message': 'Certificate refresh attempted',
                'data': None,
                'error': error
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/api/certs/<string:fqdn>/details', methods=['GET'])
def get_certificate_details(fqdn):
    """
    Get detailed SSL certificate information.
    Returns comprehensive certificate properties for inspection.
    """
    try:
        from .ssl_extended import get_full_certificate_info
        cert_info, error = get_full_certificate_info(fqdn)
        
        if not cert_info or error:
            return jsonify({
                'success': False,
                'error': error or 'Could not fetch certificate details'
            }), 400
        
        return jsonify({
            'success': True,
            'data': cert_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/api/query/expiring')
def query_expiring():
    """
    API endpoint to query certificates expiring within N days
    Used by MCP server for agent queries
    """
    days = request.args.get('days', 30, type=int)
    
    db = get_db()
    query = '''
        SELECT 
            u.id,
            u.fqdn,
            u.customer_number,
            u.customer_name,
            COALESCE(sc.issuer, 'Unknown') as issuer,
            COALESCE(sc.issuer_type, 'unknown') as issuer_type,
            COALESCE(sc.expiry_date, 'N/A') as expiry_date,
            COALESCE(sc.days_remaining, null) as days_remaining,
            COALESCE(sc.checked_at, 'Never') as checked_at,
            COALESCE(sc.status, 'unknown') as status
        FROM urls u
        LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
        WHERE sc.days_remaining IS NOT NULL
          AND sc.days_remaining <= ?
        ORDER BY sc.days_remaining ASC
    '''
    
    certificates = db.execute(query, (days,)).fetchall()
    
    result = []
    for cert in certificates:
        result.append({
            'id': cert['id'],
            'fqdn': cert['fqdn'],
            'customer_number': cert['customer_number'],
            'customer_name': cert['customer_name'],
            'issuer': cert['issuer'],
            'issuer_type': cert['issuer_type'],
            'expiry_date': cert['expiry_date'],
            'days_remaining': cert['days_remaining'],
            'checked_at': cert['checked_at'],
            'status': cert['status']
        })
    
    return jsonify({
        'success': True,
        'certificates': result,
        'count': len(result)
    })


@main_bp.route('/api/query/expired')
def query_expired():
    """
    API endpoint to query all expired certificates
    Used by MCP server for agent queries
    """
    db = get_db()
    
    query = '''
        SELECT 
            u.id,
            u.fqdn,
            u.customer_number,
            u.customer_name,
            COALESCE(sc.issuer, 'Unknown') as issuer,
            COALESCE(sc.issuer_type, 'unknown') as issuer_type,
            COALESCE(sc.expiry_date, 'N/A') as expiry_date,
            COALESCE(sc.days_remaining, null) as days_remaining,
            COALESCE(sc.checked_at, 'Never') as checked_at,
            COALESCE(sc.status, 'unknown') as status
        FROM urls u
        LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
        WHERE sc.days_remaining IS NOT NULL
          AND sc.days_remaining < 0
        ORDER BY sc.days_remaining ASC
    '''
    
    certificates = db.execute(query).fetchall()
    
    result = []
    for cert in certificates:
        result.append({
            'id': cert['id'],
            'fqdn': cert['fqdn'],
            'customer_number': cert['customer_number'],
            'customer_name': cert['customer_name'],
            'issuer': cert['issuer'],
            'issuer_type': cert['issuer_type'],
            'expiry_date': cert['expiry_date'],
            'days_remaining': cert['days_remaining'],
            'checked_at': cert['checked_at'],
            'status': cert['status']
        })
    
    return jsonify({
        'success': True,
        'certificates': result,
        'count': len(result)
    })


@main_bp.route('/api/query/customer')
def query_customer():
    """
    API endpoint to query certificates for a specific customer
    Used by MCP server for agent queries
    """
    customer_name = request.args.get('name', '', type=str)
    
    if not customer_name:
        return jsonify({
            'success': False,
            'error': 'customer_name parameter is required'
        }), 400
    
    db = get_db()
    
    query = '''
        SELECT 
            u.id,
            u.fqdn,
            u.customer_number,
            u.customer_name,
            COALESCE(sc.issuer, 'Unknown') as issuer,
            COALESCE(sc.issuer_type, 'unknown') as issuer_type,
            COALESCE(sc.expiry_date, 'N/A') as expiry_date,
            COALESCE(sc.days_remaining, null) as days_remaining,
            COALESCE(sc.checked_at, 'Never') as checked_at,
            COALESCE(sc.status, 'unknown') as status
        FROM urls u
        LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
        WHERE u.customer_name LIKE ?
        ORDER BY u.created_at DESC
    '''
    
    certificates = db.execute(query, ('%' + customer_name + '%',)).fetchall()
    
    result = []
    for cert in certificates:
        result.append({
            'id': cert['id'],
            'fqdn': cert['fqdn'],
            'customer_number': cert['customer_number'],
            'customer_name': cert['customer_name'],
            'issuer': cert['issuer'],
            'issuer_type': cert['issuer_type'],
            'expiry_date': cert['expiry_date'],
            'days_remaining': cert['days_remaining'],
            'checked_at': cert['checked_at'],
            'status': cert['status']
        })
    
    return jsonify({
        'success': True,
        'certificates': result,
        'count': len(result)
    })


@main_bp.route('/api/status')
def get_status():
    """
    API endpoint to get server status
    Used by MCP server for health checks
    """
    db = get_db()
    
    # Count certificates
    cert_count = db.execute('SELECT COUNT(*) as count FROM urls').fetchone()['count']
    
    # Count expired
    expired_count = db.execute('''
        SELECT COUNT(*) as count FROM urls u
        LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
        WHERE sc.days_remaining IS NOT NULL AND sc.days_remaining < 0
    ''').fetchone()['count']
    
    # Count expiring soon
    expiring_count = db.execute('''
        SELECT COUNT(*) as count FROM urls u
        LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
        WHERE sc.days_remaining IS NOT NULL AND sc.days_remaining >= 0 AND sc.days_remaining <= 30
    ''').fetchone()['count']
    
    return jsonify({
        'status': 'healthy',
        'timestamp': '2024-04-07T00:00:00Z',
        'certificates_monitored': cert_count,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_count
    })


@main_bp.route('/api/ping')
def ping():
    """Ping endpoint for health checks"""
    return jsonify({
        'status': 'ok',
        'message': 'SSL Certificate Monitor is running',
        'timestamp': datetime.now().isoformat()
    })


def status_for_days(days_remaining):
    """Helper to determine status based on days remaining"""
    if days_remaining < 0:
        return 'expired'
    elif days_remaining < 30:
        return 'expiring_soon'
    elif days_remaining < 90:
        return 'warning'
    else:
        return 'active'
