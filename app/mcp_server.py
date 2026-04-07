#!/usr/bin/env /home/joris/ssl-checker/venv/bin/python3
"""
MCP Server for SSL Certificate Monitor
Implements the Model Context Protocol (MCP) for AI agent integration
"""
import asyncio
import json
import sys
from pathlib import Path

# Add the parent directory to path to find app module
script_dir = Path(__file__).parent
if str(script_dir.parent) not in sys.path:
    sys.path.insert(0, str(script_dir.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from app.ssl_checker import get_ssl_info, extract_domain
from app.database import get_db

def status_for_days(days_remaining):
    """Determine status based on days remaining"""
    if days_remaining is None:
        return 'unknown'
    if days_remaining < 0:
        return 'expired'
    elif days_remaining < 30:
        return 'critical'
    elif days_remaining < 90:
        return 'warning'
    else:
        return 'active'

# Initialize MCP server
app = Server(name='ssl-cert-monitor', version='2.0.0')

async def add_certificate(args: dict):
    """Add a new certificate to monitor"""
    from datetime import datetime
    
    fqdn = args.get('fqdn')
    customer_number = args.get('customer_number')
    customer_name = args.get('customer_name')
    
    if not fqdn:
        return {'error': 'FQDN is required'}
    
    db = get_db()
    
    try:
        db.execute('''
            INSERT INTO urls (fqdn, customer_number, customer_name)
            VALUES (?, ?, ?)
        ''', (fqdn, customer_number, customer_name))
        db.commit()
        
        cert_info, error = get_ssl_info(fqdn)
        
        if cert_info and not error:
            domain = extract_domain(fqdn)
            days = cert_info.get('days_remaining')
            expiry = cert_info.get('expiry_date', 'N/A')
            issuer = cert_info.get('issuer', 'Unknown')
            issuer_type = cert_info.get('issuer_type', 'unknown')
            
            if hasattr(expiry, 'strftime'):
                expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
            else:
                expiry_str = str(expiry)
            
            cert_status = status_for_days(days)
            
            db.execute('''
                INSERT OR REPLACE INTO ssl_cache (fqdn, issuer, issuer_type, expiry_date, days_remaining, checked_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (domain, issuer, issuer_type, expiry_str, days, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cert_status))
            db.commit()
            
            return {
                'success': True,
                'message': 'Certificate added and checked',
                'data': {
                    'fqdn': fqdn,
                    'days_remaining': days,
                    'expiry_date': expiry_str,
                    'status': cert_status
                }
            }
        else:
            domain = extract_domain(fqdn)
            db.execute('''
                INSERT OR REPLACE INTO ssl_cache (fqdn, issuer, issuer_type, expiry_date, days_remaining, checked_at, status)
                VALUES (?, 'Unknown', 'unknown', 'N/A', NULL, 'Never', 'unknown')
            ''', (domain,))
            db.commit()
            
            return {
                'success': True,
                'message': 'Certificate added (failed to check)',
                'error': error
            }
            
    except Exception as e:
        db.rollback()
        return {'error': str(e)}

async def list_certificates(args: dict):
    """List all certificates"""
    db = get_db()
    
    sort_by = args.get('sort_by', 'days_remaining')
    sort_order = args.get('sort_order', 'asc')
    
    valid_sort = ['days_remaining', 'expiry_date', 'customer_name', 'fqdn']
    sort_field = sort_by if sort_by in valid_sort else 'days_remaining'
    order = 'ASC' if sort_order == 'asc' else 'DESC'
    
    query = f'''
        SELECT u.id, u.fqdn, u.customer_number, u.customer_name,
               sc.issuer, sc.issuer_type, sc.expiry_date, sc.days_remaining, sc.status
        FROM urls u
        LEFT JOIN ssl_cache sc ON LOWER(REPLACE(LOWER(u.fqdn), 'https://', '')) LIKE '%' || LOWER(sc.fqdn) || '%'
        OR LOWER(u.fqdn) LIKE '%' || LOWER(REPLACE(sc.fqdn, 'https://', '')) || '%'
        ORDER BY {sort_field} {order}
    '''
    
    certs = db.execute(query).fetchall()
    
    return {
        'certificates': [
            {
                'id': c['id'],
                'fqdn': c['fqdn'],
                'customer_number': c['customer_number'],
                'customer_name': c['customer_name'],
                'issuer': c['issuer'],
                'issuer_type': c['issuer_type'],
                'expiry_date': c['expiry_date'],
                'days_remaining': c['days_remaining'],
                'status': c['status']
            } for c in certs
        ]
    }

async def get_certificate_details(args: dict):
    """Get detailed certificate information"""
    fqdn = args.get('fqdn')
    
    db = get_db()
    url = db.execute('SELECT * FROM urls WHERE fqdn = ? OR fqdn LIKE ?', (fqdn, f'%{fqdn}%')).fetchone()
    
    if not url:
        return {'error': 'Certificate not found'}
    
    cert_info, error = get_ssl_info(fqdn)
    
    if cert_info and not error:
        return cert_info
    else:
        domain = extract_domain(fqdn)
        cache = db.execute('SELECT * FROM ssl_cache WHERE fqdn LIKE ?', (f'%{domain}%',)).fetchone()
        return dict(cache) if cache else {'error': 'No certificate data available'}

async def refresh_certificate(args: dict):
    """Refresh certificate data"""
    fqdn = args.get('fqdn')
    
    cert_info, error = get_ssl_info(fqdn)
    
    if cert_info and not error:
        from datetime import datetime
        db = get_db()
        
        domain = extract_domain(fqdn)
        days = cert_info.get('days_remaining')
        expiry = cert_info.get('expiry_date', 'N/A')
        
        if hasattr(expiry, 'strftime'):
            expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
        else:
            expiry_str = str(expiry)
        
        issuer = cert_info.get('issuer', 'Unknown')
        issuer_type = cert_info.get('issuer_type', 'unknown')
        
        cert_status = status_for_days(days)
        
        db.execute('''
            INSERT OR REPLACE INTO ssl_cache (fqdn, issuer, issuer_type, expiry_date, days_remaining, checked_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (domain, issuer, issuer_type, expiry_str, days, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cert_status))
        db.commit()
        
        return {
            'success': True,
            'message': 'Certificate refreshed',
            'data': cert_info
        }
    else:
        return {'error': f'Failed to refresh certificate: {error}'}

async def delete_certificate(args: dict):
    """Delete a certificate"""
    cert_id = args.get('id')
    
    db = get_db()
    url = db.execute('SELECT * FROM urls WHERE id = ?', (cert_id,)).fetchone()
    
    if not url:
        return {'error': 'Certificate not found'}
    
    db.execute('DELETE FROM urls WHERE id = ?', (cert_id,))
    db.commit()
    
    domain = extract_domain(url['fqdn'])
    db.execute('DELETE FROM ssl_cache WHERE fqdn LIKE ?', (f'%{domain}%',))
    db.commit()
    
    return {
        'success': True,
        'message': 'Certificate deleted',
        'deleted_id': cert_id
    }

async def query_expiring(args: dict):
    """Get certificates expiring within specified days"""
    days = args.get('days', 30)
    
    db = get_db()
    certs = db.execute('''
        SELECT * FROM ssl_cache WHERE days_remaining IS NOT NULL AND days_remaining <= ? AND days_remaining > 0
        ORDER BY days_remaining ASC
    ''', (days,)).fetchall()
    
    return {
        'expiring': [
            {
                'fqdn': c['fqdn'],
                'days_remaining': c['days_remaining'],
                'expiry_date': c['expiry_date'],
                'issuer': c['issuer']
            } for c in certs
        ],
        'count': len(certs)
    }

async def query_expired():
    """Get expired certificates"""
    db = get_db()
    certs = db.execute('''
        SELECT * FROM ssl_cache WHERE days_remaining IS NOT NULL AND days_remaining < 0
        ORDER BY days_remaining ASC
    ''').fetchall()
    
    return {
        'expired': [
            {
                'fqdn': c['fqdn'],
                'days_remaining': c['days_remaining'],
                'expiry_date': c['expiry_date'],
                'issuer': c['issuer']
            } for c in certs
        ],
        'count': len(certs)
    }

async def query_customer(args: dict):
    """Get certificates for a customer"""
    customer_name = args.get('customer_name')
    
    db = get_db()
    certs = db.execute('''
        SELECT * FROM urls WHERE customer_name LIKE ?
    ''', (f'%{customer_name}%',)).fetchall()
    
    return {
        'certificates': [
            {
                'id': c['id'],
                'fqdn': c['fqdn'],
                'customer_number': c['customer_number'],
                'customer_name': c['customer_name']
            } for c in certs
        ],
        'count': len(certs)
    }

@app.list_tools()
async def list_tools():
    """List available tools"""
    return [
        Tool(
            name='add_certificate',
            description='Add a new SSL certificate to monitor',
            inputSchema={
                'type': 'object',
                'properties': {
                    'fqdn': {'type': 'string', 'description': 'Fully qualified domain name with https:// prefix'},
                    'customer_number': {'type': 'string', 'description': 'Optional customer number'},
                    'customer_name': {'type': 'string', 'description': 'Optional customer name'}
                },
                'required': ['fqdn']
            }
        ),
        Tool(
            name='list_certificates',
            description='List all monitored SSL certificates with optional sorting',
            inputSchema={
                'type': 'object',
                'properties': {
                    'sort_by': {
                        'type': 'string',
                        'enum': ['days_remaining', 'expiry_date', 'customer_name', 'fqdn'],
                        'default': 'days_remaining'
                    },
                    'sort_order': {
                        'type': 'string',
                        'enum': ['asc', 'desc'],
                        'default': 'asc'
                    }
                }
            }
        ),
        Tool(
            name='get_certificate_details',
            description='Get detailed SSL certificate information',
            inputSchema={
                'type': 'object',
                'properties': {
                    'fqdn': {'type': 'string', 'description': 'Fully qualified domain name'}
                },
                'required': ['fqdn']
            }
        ),
        Tool(
            name='refresh_certificate',
            description='Manually refresh SSL certificate information for a domain',
            inputSchema={
                'type': 'object',
                'properties': {
                    'fqdn': {'type': 'string', 'description': 'Fully qualified domain name'}
                },
                'required': ['fqdn']
            }
        ),
        Tool(
            name='delete_certificate',
            description='Delete a certificate from monitoring',
            inputSchema={
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': 'Certificate ID'}
                },
                'required': ['id']
            }
        ),
        Tool(
            name='query_expiring',
            description='Get certificates expiring within specified days',
            inputSchema={
                'type': 'object',
                'properties': {
                    'days': {'type': 'integer', 'default': 30}
                }
            }
        ),
        Tool(
            name='query_expired',
            description='Get all expired certificates',
            inputSchema={},
        ),
        Tool(
            name='query_customer',
            description='Get certificates for a specific customer',
            inputSchema={
                'type': 'object',
                'properties': {
                    'customer_name': {'type': 'string'}
                },
                'required': ['customer_name']
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute a tool call"""
    try:
        if name == 'add_certificate':
            return await add_certificate(arguments)
        elif name == 'list_certificates':
            return await list_certificates(arguments)
        elif name == 'get_certificate_details':
            return await get_certificate_details(arguments)
        elif name == 'refresh_certificate':
            return await refresh_certificate(arguments)
        elif name == 'delete_certificate':
            return await delete_certificate(arguments)
        elif name == 'query_expiring':
            return await query_expiring(arguments)
        elif name == 'query_expired':
            return await query_expired()
        elif name == 'query_customer':
            return await query_customer(arguments)
        else:
            return {'error': f'Unknown tool: {name}'}
    except Exception as e:
        return {'error': str(e)}

async def main():
    """Main entry point"""
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == '__main__':
    asyncio.run(main())
