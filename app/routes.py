"""
Main request routes and API endpoints
"""
from flask import Blueprint, render_template, request, jsonify, g, current_app, redirect, url_for, flash
from .database import get_db
from .ssl_checker import get_ssl_info, extract_domain


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
        return redirect(url_for('main.admin'))
    
    if request.method == 'POST' and delete_id:
        # Handle deletion via POST from form submission
        db.execute('DELETE FROM urls WHERE id = ?', (delete_id,))
        db.commit()
        flash('Certificate deleted successfully', 'success')
        return redirect(url_for('main.admin'))
    
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
        
        return redirect(url_for('main.admin'))
    
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
        LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
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
    """API endpoint to add a new URL"""
    data = request.get_json()
    fqdn = data.get('fqdn')
    customer_number = data.get('customer_number')
    customer_name = data.get('customer_name')
    
    if not fqdn:
        return jsonify({'error': 'FQDN is required'}), 400
    
    # Validate URL format (must start with https://)
    if not fqdn.startswith('https://'):
        return jsonify({'error': 'URL must start with https://'}), 400
    
    # Extract domain and validate format
    domain = extract_domain(fqdn)
    if not domain or '.' not in domain:
        return jsonify({'error': 'Invalid FQDN format'}), 400
    
    try:
        db = get_db()
        db.execute('''
            INSERT INTO urls (fqdn, customer_number, customer_name)
            VALUES (?, ?, ?)
        ''', (fqdn, customer_number, customer_name))
        db.commit()
        
        # Immediately check the certificate
        cert_info, error = get_ssl_info(fqdn)
        if cert_info and error:
            print(f"Warning: Could not fetch SSL info for {fqdn}: {error}")
        
        return jsonify({
            'success': True,
            'message': 'URL added successfully',
            'url_id': db.execute('SELECT last_insert_rowid()').fetchone()[0]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
            return jsonify({
                'success': False,
                'error': f"Could not fetch certificate: {error}"
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


from datetime import datetime
