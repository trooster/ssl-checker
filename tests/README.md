# SSL Certificate Monitor Test Script

This script helps verify the installation and functionality of the SSL Monitor application.

## Prerequisites
- Python 3.8+
- Docker and docker-compose (optional)

## Quick Tests

### 1. Basic Installation Test
```bash
pip install -r requirements.txt
```

### 2. Unit Tests
```bash
python -m pytest tests/test_ssl_checker.py -v
```

### 3. Integration Tests
```bash
python -m pytest tests/test_api.py -v
```

### 4. Docker Build Test
```bash
docker-compose build
docker-compose up -d
```

### 5. Health Check
```bash
# After starting the container
curl http://localhost:4444/api/urls
```

## Test Scenarios

### Adding a Real Certificate
```bash
# Add a test certificate via API
curl -X POST http://localhost:4444/api/urls \
  -H "Content-Type: application/json" \
  -d '{"fqdn": "https://www.google.com", "customer_name": "Google"}'
```

### Manual Refresh Test
```bash
# Force refresh for a specific domain
curl -X POST http://localhost:4444/api/certs/www.google.com/refresh
```

### Sorting Tests
```bash
# Sort by days remaining
curl "http://localhost:4444/api/urls?sort_by=days_remaining"

# Sort by customer name
curl "http://localhost:4444/api/urls?sort_by=customer_name"

# Sort by FQDN
curl "http://localhost:4444/api/urls?sort_by=fqdn"
```

## Common Issues

### Database Errors
- Check file permissions on database file
- Ensure sqlite3 is installed

### SSL Check Failures
- Verify network connectivity to target domains
- Check DNS resolution
- Ensure the target domain has a valid SSL certificate

### Docker Issues
- Check container logs: `docker-compose logs ssl-monitor`
- Verify port 4444 is available
- Check volume permissions

## Automated Testing

The test suite covers:
- URL validation and format checking
- SSL certificate information extraction
- Cache refresh logic
- API endpoint functionality
- Sorting functionality
- Duplicate URL handling

Run all tests at once:
```bash
python -m pytest tests/ -v --tb=short
```

## Exit Codes

- `0`: All tests passed
- `1`: Tests failed
- `2`: Test abort due to import errors
