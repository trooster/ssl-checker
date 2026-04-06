"""
Integration tests for the application API
"""
import unittest
import json
import os
from datetime import datetime, timedelta
from app import create_app, Config
from app.database import get_db


class TestConfig(Config):
    """Test configuration"""
    SECRET_KEY = 'test-secret-key-change-in-production'
    DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests


class TestAPIEndpoints(unittest.TestCase):
    """API endpoint tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()
    
    def setUp(self):
        """Initialize database for each test"""
        with self.app.app_context():
            db = get_db()
            # Create tables
            db.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fqdn TEXT UNIQUE NOT NULL,
                    customer_number TEXT,
                    customer_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.execute('''
                CREATE TABLE IF NOT EXISTS ssl_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fqdn TEXT NOT NULL,
                    issuer TEXT,
                    issuer_type TEXT,
                    expiry_date TIMESTAMP,
                    days_remaining INTEGER,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (fqdn) REFERENCES urls(fqdn) ON DELETE CASCADE,
                    UNIQUE(fqdn)
                )
            ''')
            db.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db = get_db()
            db.connection.close()  # Close connection for each test
    
    def test_add_url_success(self):
        """Test adding a valid URL"""
        response = self.client.post('/api/urls', 
                                    data=json.dumps({
                                        'fqdn': 'https://www.google.com',
                                        'customer_number': '12345',
                                        'customer_name': 'Test Customer'
                                    }),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('url_id', data)
    
    def test_add_url_missing_fqdn(self):
        """Test adding URL without FQDN should fail"""
        response = self.client.post('/api/urls', 
                                    data=json.dumps({
                                        'customer_number': '12345'
                                    }),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_add_url_invalid_protocol(self):
        """Test adding URL without https:// should fail"""
        response = self.client.post('/api/urls', 
                                    data=json.dumps({
                                        'fqdn': 'http://example.com',
                                        'customer_number': '12345'
                                    }),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_urls_empty(self):
        """Test getting URLs from empty database"""
        response = self.client.get('/api/urls')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('urls', data)
        self.assertIn('count', data)
    
    def test_sort_by_days_remaining(self):
        """Test sorting by days remaining"""
        response = self.client.get('/api/urls?sort_by=days_remaining')
        self.assertEqual(response.status_code, 200)
    
    def test_sort_by_customer_name(self):
        """Test sorting by customer name"""
        response = self.client.get('/api/urls?sort_by=customer_name')
        self.assertEqual(response.status_code, 200)
    
    def test_sort_by_fqdn(self):
        """Test sorting by FQDN"""
        response = self.client.get('/api/urls?sort_by=fqdn')
        self.assertEqual(response.status_code, 200)
    
    def test_sort_asc(self):
        """Test ascending sort order"""
        response = self.client.get('/api/urls?sort_order=asc')
        self.assertEqual(response.status_code, 200)
    
    def test_url_not_found_after_add(self):
        """Test that we can add and retrieve a URL"""
        # Add URL
        add_response = self.client.post('/api/urls', 
                                        data=json.dumps({
                                            'fqdn': 'https://www.github.com',
                                            'customer_number': '67890',
                                            'customer_name': 'GitHub'
                                        }),
                                        content_type='application/json')
        self.assertEqual(add_response.status_code, 201)
        
        # Get URLs
        get_response = self.client.get('/api/urls?sort_by=fqdn')
        self.assertEqual(get_response.status_code, 200)
        data = json.loads(get_response.data)
        
        self.assertGreaterEqual(len(data['urls']), 1)
        self.assertEqual(data['urls'][0]['customer_name'], 'GitHub')


class TestURLValidation(unittest.TestCase):
    """Tests for URL validation"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()
    
    def setUp(self):
        """Initialize database for each test"""
        with self.app.app_context():
            db = get_db()
            db.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fqdn TEXT UNIQUE NOT NULL,
                    customer_number TEXT,
                    customer_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.commit()
    
    def test_url_missing_protocol(self):
        """Test that URL without protocol fails"""
        response = self.client.post('/api/urls', 
                                    data=json.dumps({
                                        'fqdn': 'example.com',
                                        'customer_name': 'Test'
                                    }),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_url_with_http(self):
        """Test that http:// protocol fails"""
        response = self.client.post('/api/urls', 
                                    data=json.dumps({
                                        'fqdn': 'http://example.com',
                                        'customer_name': 'Test'
                                    }),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_invalid_fqdn_format(self):
        """Test that invalid FQDN format fails"""
        response = self.client.post('/api/urls', 
                                    data=json.dumps({
                                        'fqdn': 'not-a-url',
                                        'customer_name': 'Test'
                                    }),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
