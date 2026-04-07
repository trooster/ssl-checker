# SSL Certificate Monitor

Web application to monitor SSL certificate expiry dates. Features include:

- **Admin Panel**: Manage URLs with optional customer information
- **SSL Monitoring**: Track certificate expiry dates, issuer,type, and days remaining
- **Caching**: Intelligent caching with configurable refresh rates
- **Sorting**: Sort by days remaining, expiry date, customer name, or FQDN
- **Enhanced Details**: View full certificate details including issuer, subject, SANs
- **URL Validation**: Validate URLs before adding with reachability checks
- **Custom Ports**: Support for非-standard SSL ports (e.g., :8443)

## Features

### 1. URL Management (Admin Panel)
- Add new domains with optional customer information
- Edit existing entries
- Delete entries
- View a 11 overview of all monitored certificates

### 2. SSL Certificate Monitoring
- Display expiry date and days remaining
- Show certificate issuer (Let's Encrypt, Sectigo, DigiCert, etc.)
- Status indicators:
  - **Active**: > 90 days remaining
  - **Warning**: 30-90 days remaining
  - **Expiring Soon**: < 30 days remaining
  - **Expired**: < 0 days (negative days shown)

### 3. Enhanced Certificate Details
View comprehensive certificate information:
- Full issuer details (O, CN, etc.)
- Subject information
- Validity period (notBefore, notAfter)
- Serial number and version
- Algorithm details (key algorithm, signature algorithm)
- SAN (Subject Alternative Names)
- SHA256 fingerprint

### 4. URL Validation
- Validates HTTPS protocol
- Checks domain format
- Tests server reachability before adding
- Provides helpful error messages

### 5. Custom Port Support
- Automatically detects port from URL (default: 443)
- Supports custom ports (e.g., `https://example.com:8443`)

## Technical Details

### Database
- SQLite-based storage
- Two main tables: `urls` and `ssl_cache`
- Intelligent caching with configurable refresh rates

### Caching Strategy
- Less than 30 days: Refresh every 12 hours
- 30-90 days: Daily refresh
- More than 90 days: Weekly refresh

### API Endpoints

#### GET `/api/urls`
Get all monitored URLs (supports sorting):
- `sort_by`: days_remaining (default), fqdn, customer_name, expiry_date
- `sort_order`: asc (default), desc

#### POST `/api/urls`
Add new URL:
```json
{
  "fqdn": "https://example.com",
  "customer_number": "12345",
  "customer_name": "Example Customer"
}
```

#### GET `/api/certs/<fqdn>/details`
Get full certificate details for a domain

#### POST `/api/certs/<fqdn>/refresh`
Force refresh certificate data

## Installation

### From Source
```bash
# Clone repository
git clone <your-repo-url>
cd ssl-checker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

### Using Docker
coming soon...

## Configuration

No external configuration needed. All settings are in the code.

## Testing

### Using curl
```bash
# Test API
curl http://localhost:4444/api/urls

# Add URL
curl -X POST http://localhost:4444/api/urls \
  -H "Content-Type: application/json" \
  -d '{"fqdn":"https://example.com"}'

# Get certificate details
curl http://localhost:4444/api/certs/example.com/details
```

### Manual Testing Checklist
- [ ] Add new URL with valid domain
- [ ] Verify URL validation rejects invalid URLs
- [ ] Check certificate data is correctly stored
- [ ] Verify sorting works correctly
- [ ] Test custom port support
- [ ] Check enhanced certificate details endpoint

## Development

### Project Structure
```
ssl-checker/
├── app/
│   ├── __init__.py
│   ├── routes.py        # Flask routes and API endpoints
│   ├── database.py      # Database connection and queries
│   ├── ssl_checker.py   # SSL certificate utilities
│   ├── ssl_extended.py  # Enhanced certificate utilities
│   ├── url_utils.py     # URL validation utilities
│   └── templates/       # HTML templates
├── run.py               # Application entry point
└── README.md            # This file
```

### Adding New Features
1. Add validation logic in `url_utils.py`
2. Add certificate utilities in `ssl_checker.py` or `ssl_extended.py`
3. Add API endpoints in `routes.py`
4. Update templates in `templates/`
5. Tests before committing

## License
MIT License

## Support
For issues or questions, please open an issue on GitHub.
