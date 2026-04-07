"""
Database schema and initialization for SSL Monitor Application
"""
import sqlite3
from flask import current_app, g


def get_db():
    """Get database connection for current request context"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_URI'].replace('sqlite:///', ''),
            check_same_thread=False
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(app):
    """Initialize database tables"""
    with app.app_context():
        db = get_db()
        
        # URLs table with SSL port
        db.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fqdn TEXT UNIQUE NOT NULL,
                ssl_port INTEGER DEFAULT 443,
                customer_number TEXT,
                customer_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # SSL cache table with configurable expiration per URL
        db.execute('''
            CREATE TABLE IF NOT EXISTS ssl_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fqdn TEXT NOT NULL,
                ssl_port INTEGER DEFAULT 443,
                issuer TEXT,
                issuer_type TEXT,
                expiry_date TIMESTAMP,
                days_remaining INTEGER,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (fqdn) REFERENCES urls(fqdn) ON DELETE CASCADE,
                UNIQUE(fqdn, ssl_port)
            )
        ''')
        
        # Create indexes for performance
        db.execute('CREATE INDEX IF NOT EXISTS idx_ssl_cache_checked_at ON ssl_cache(checked_at)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_ssl_cache_days_remaining ON ssl_cache(days_remaining)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_ssl_cache_port ON ssl_cache(ssl_port)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_urls_customer_name ON urls(customer_name)')
        
        db.commit()


def close_db(error):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()
