"""
API tests for SSL Certificate Monitor
"""
import pytest
from app import create_app
import sqlite3
import os


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app()
    app.config['DATABASE_URI'] = '/tmp/test_ssl_monitor.db'
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # Remove old test database
    if os.path.exists('/tmp/test_ssl_monitor.db'):
        os.remove('/tmp/test_ssl_monitor.db')
    
    yield app
    
    # Clean up
    if os.path.exists('/tmp/test_ssl_monitor.db'):
        os.remove('/tmp/test_ssl_monitor.db')


@pytest.fixture
def client(app):
    """Get a test client."""
    return app.test_client()


@pytest.fixture
def authenticated_headers():
    """Get headers with admin authentication."""
    return {'Authorization': 'Bearer test-secret-token'}


def test_enhanced_ssl_details_endpoint(client, authenticated_headers):
    """Test detailed certificate view endpoint"""
    
    # Test non-existent certificate
    response = client.get('/api/certs/999/details', headers=authenticated_headers)
    assert response.status_code == 500  # 500 because no data in test db
    
    # Test existing certificate (google.com with ID=9)
    response = client.get('/api/certs/9/details', headers=authenticated_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']
    assert 'fqdn' in data
    assert 'details' in data
    assert 'cert_data' in data
    assert data['fqdn'] == 'google.com'
    assert 'issuer' in data['cert_data']
    assert 'days_remaining' in data['cert_data']
    assert 'sha256_fingerprint' in data['cert_data']
