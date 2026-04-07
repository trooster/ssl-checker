# SSL Certificate Monitor

⚠️ **SECURITY WARNING: This application does not use any authentication!**  
**DO NOT run this application on public IP addresses or exposed internet-facing servers.**  
This is a development/demo application intended for local/private network use only.

A web application for monitoring SSL certificate expiration dates across multiple domains with automatic caching and refresh scheduling.

## Features
## Features
- **SSL Certificate Monitoring**: Automatically checks SSL certificate expiration dates for multiple domains
- **Enhanced Certificate Details**: Comprehensive certificate information including full details:
  - Certificate issuer and owner information
  - Full certificate validity periods
  - Serial numbers and certificate versions
  - Subject Alternative Names (SANs) list
  - SHA-256 fingerprints (when available)
  - Detailed certificate extensions
  - Full certificate chain information view
- **Smart Caching**: Smart caching strategy based on expiry dates:
  - Critical certificates (< 30 days): Check hourly
  - Warning certificates (30-90 days): Check every 12 hours  
  - Safe certificates (> 90 days): Check daily
- **Issuer Detection**: Automatically identifies certificate providers (Let's Encrypt, Sectigo, DigiCert, Comodo, GoDaddy, Cloudflare, etc.)
- **Customizable Metadata**: Store customer numbers and names for each certificate
- **Intuitive Dashboard**: Clean, responsive web interface with sortable columns and color-coded status indicators
- **Real-time Updates**: Manual certificate refresh capability with detailed view
- **RESTful API**: Full CRUD operations plus enhanced certificate details endpoints
- **MCP Server**: Model Context Protocol server for agent integration

## Quick Start

### Using Docker (Recommended)

### POST `/api/certs/<fqdn>/refresh`
```bash
curl -X POST "http://localhost:4444/api/certs/google.com/refresh" -H "Authorization: Bearer your-token"
```\n\n### GET `/api/certs/<id>/details`\n\nRetrieve detailed certificate information including full certificate data.\n\n**Returns complete certificate details**:
- Basic certificate information (FQDN, SSL expiry, issuer, days remaining)
- Issuer details (CN, organization, country, organizational unit)
- Subject/owner information (CN, organization)
- Certificate validity period (not before, not after)
- Serial number and version
- Key algorithm and size information
- Subject Alternative Names (SANs) list
- SHA-256 fingerprint (if available)
- Certificate extensions

**Example**:

```bash
# Get detailed info for certificate with ID 9
curl -s 'http://localhost:4444/api/certs/9/details' \
  -H 'Authorization: Bearer your-token' | python3 -m json.tool

# Sample response:
{
    "success": true,
    "fqdn": "google.com",
    "details": {
        "basic_info": {
            "fqdn": "google.com",
            "url_id": 9,
            "customer_number": null,
            "customer_name": "Google Test"
        },
        "issuer_info": {
            "CN": "WR2",
            "O": "Google Trust Services",
            "C": "US"
        },
        "subject_info": {
            "CN": "*.google.com"
        },
        "validity": {
            "not_before": "Mar 16 08:36:32 2026 GMT",
            "not_after": "Jun  8 08:36:31 2026 GMT"
        },
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "key_info": {
            "algorithm": "RSA",
            "key_size": "N/A"
        },
        "fingerprint": {
            "sha256": "N/A",
            "md5": "N/A (requires openssl)"
        },
        "extensions": {
            "version": 3,
            "san": [
                "DNS: *.google.com",
                "DNS: *.appengine.google.com",
                ...
            ]
        }
    },
    "cert_data": {
        "fqdn": "google.com",
        "issuer": "WR2 - Google Trust Services",
        "issuer_type": "Other",
        "expiry_date": "2026-06-08 08:36:31",
        "days_remaining": 61,
        "not_before": "2026-03-16 08:36:32",
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "sha256_fingerprint": "N/A",
        "subject_cn": "*.google.com",
        "pem": "PLACEHOLDER"
    }
}
```

**Accessing from UI**:
- Navigate to `/admin` → Find your certificate → Click "View Certificate Details" button
- Opens modal with comprehensive certificate information
- See all SSL certificate technical details

## Certificate Types Detection

The application automatically identifies SSL certificate issuers. Supported issuers:
- Let's Encrypt
- Sectigo (formerly Comodo)
- DigiCert
- GeoTrust
- GlobalSign
- Buypass
- Zauner
- Amazon (Certificate Manager)
- Google Trust Services
- Cloudflare
- Namecheap
- SSL.com
- Other (unrecognized issuers)

### POST `/api/certs/<fqdn>/refresh`
```bash
curl -X POST "http://localhost:4444/api/certs/google.com/refresh" -H "Authorization: Bearer your-token"
```\n\n### GET `/api/certs/<id>/details`\n\nRetrieve detailed certificate information including full certificate data.\n\n**Returns complete certificate details**:
- Basic certificate information (FQDN, SSL expiry, issuer, days remaining)
- Issuer details (CN, organization, country, organizational unit)
- Subject/owner information (CN, organization)
- Certificate validity period (not before, not after)
- Serial number and version
- Key algorithm and size information
- Subject Alternative Names (SANs) list
- SHA-256 fingerprint (if available)
- Certificate extensions

**Example**:

```bash
# Get detailed info for certificate with ID 9
curl -s 'http://localhost:4444/api/certs/9/details' \
  -H 'Authorization: Bearer your-token' | python3 -m json.tool

# Sample response:
{
    "success": true,
    "fqdn": "google.com",
    "details": {
        "basic_info": {
            "fqdn": "google.com",
            "url_id": 9,
            "customer_number": null,
            "customer_name": "Google Test"
        },
        "issuer_info": {
            "CN": "WR2",
            "O": "Google Trust Services",
            "C": "US"
        },
        "subject_info": {
            "CN": "*.google.com"
        },
        "validity": {
            "not_before": "Mar 16 08:36:32 2026 GMT",
            "not_after": "Jun  8 08:36:31 2026 GMT"
        },
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "key_info": {
            "algorithm": "RSA",
            "key_size": "N/A"
        },
        "fingerprint": {
            "sha256": "N/A",
            "md5": "N/A (requires openssl)"
        },
        "extensions": {
            "version": 3,
            "san": [
                "DNS: *.google.com",
                "DNS: *.appengine.google.com",
                ...
            ]
        }
    },
    "cert_data": {
        "fqdn": "google.com",
        "issuer": "WR2 - Google Trust Services",
        "issuer_type": "Other",
        "expiry_date": "2026-06-08 08:36:31",
        "days_remaining": 61,
        "not_before": "2026-03-16 08:36:32",
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "sha256_fingerprint": "N/A",
        "subject_cn": "*.google.com",
        "pem": "PLACEHOLDER"
    }
}
```

**Accessing from UI**:
- Navigate to `/admin` → Find your certificate → Click "View Certificate Details" button
- Opens modal with comprehensive certificate information
- See all SSL certificate technical details

## Certificate Types Detection

The application automatically identifies SSL certificate issuers. Supported issuers:
- Let's Encrypt
- Sectigo (formerly Comodo)
- DigiCert
- GeoTrust
- GlobalSign
- Buypass
- Zauner
- Amazon (Certificate Manager)
- Google Trust Services
- Cloudflare
- Namecheap
- SSL.com
- Other (unrecognized issuers)

3. **Access the application**:
   - Open your browser and navigate to: `http://localhost:4444`
   - Go to `/admin` to add certificates
   - View SSL status on the main page

### POST `/api/certs/<fqdn>/refresh`
```bash
curl -X POST "http://localhost:4444/api/certs/google.com/refresh" -H "Authorization: Bearer your-token"
```\n\n### GET `/api/certs/<id>/details`\n\nRetrieve detailed certificate information including full certificate data.\n\n**Returns complete certificate details**:
- Basic certificate information (FQDN, SSL expiry, issuer, days remaining)
- Issuer details (CN, organization, country, organizational unit)
- Subject/owner information (CN, organization)
- Certificate validity period (not before, not after)
- Serial number and version
- Key algorithm and size information
- Subject Alternative Names (SANs) list
- SHA-256 fingerprint (if available)
- Certificate extensions

**Example**:

```bash
# Get detailed info for certificate with ID 9
curl -s 'http://localhost:4444/api/certs/9/details' \
  -H 'Authorization: Bearer your-token' | python3 -m json.tool

# Sample response:
{
    "success": true,
    "fqdn": "google.com",
    "details": {
        "basic_info": {
            "fqdn": "google.com",
            "url_id": 9,
            "customer_number": null,
            "customer_name": "Google Test"
        },
        "issuer_info": {
            "CN": "WR2",
            "O": "Google Trust Services",
            "C": "US"
        },
        "subject_info": {
            "CN": "*.google.com"
        },
        "validity": {
            "not_before": "Mar 16 08:36:32 2026 GMT",
            "not_after": "Jun  8 08:36:31 2026 GMT"
        },
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "key_info": {
            "algorithm": "RSA",
            "key_size": "N/A"
        },
        "fingerprint": {
            "sha256": "N/A",
            "md5": "N/A (requires openssl)"
        },
        "extensions": {
            "version": 3,
            "san": [
                "DNS: *.google.com",
                "DNS: *.appengine.google.com",
                ...
            ]
        }
    },
    "cert_data": {
        "fqdn": "google.com",
        "issuer": "WR2 - Google Trust Services",
        "issuer_type": "Other",
        "expiry_date": "2026-06-08 08:36:31",
        "days_remaining": 61,
        "not_before": "2026-03-16 08:36:32",
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "sha256_fingerprint": "N/A",
        "subject_cn": "*.google.com",
        "pem": "PLACEHOLDER"
    }
}
```

**Accessing from UI**:
- Navigate to `/admin` → Find your certificate → Click "View Certificate Details" button
- Opens modal with comprehensive certificate information
- See all SSL certificate technical details

## Certificate Types Detection

The application automatically identifies SSL certificate issuers. Supported issuers:
- Let's Encrypt
- Sectigo (formerly Comodo)
- DigiCert
- GeoTrust
- GlobalSign
- Buypass
- Zauner
- Amazon (Certificate Manager)
- Google Trust Services
- Cloudflare
- Namecheap
- SSL.com
- Other (unrecognized issuers)

### Using Python Directly

### POST `/api/certs/<fqdn>/refresh`
```bash
curl -X POST "http://localhost:4444/api/certs/google.com/refresh" -H "Authorization: Bearer your-token"
```\n\n### GET `/api/certs/<id>/details`\n\nRetrieve detailed certificate information including full certificate data.\n\n**Returns complete certificate details**:
- Basic certificate information (FQDN, SSL expiry, issuer, days remaining)
- Issuer details (CN, organization, country, organizational unit)
- Subject/owner information (CN, organization)
- Certificate validity period (not before, not after)
- Serial number and version
- Key algorithm and size information
- Subject Alternative Names (SANs) list
- SHA-256 fingerprint (if available)
- Certificate extensions

**Example**:

```bash
# Get detailed info for certificate with ID 9
curl -s 'http://localhost:4444/api/certs/9/details' \
  -H 'Authorization: Bearer your-token' | python3 -m json.tool

# Sample response:
{
    "success": true,
    "fqdn": "google.com",
    "details": {
        "basic_info": {
            "fqdn": "google.com",
            "url_id": 9,
            "customer_number": null,
            "customer_name": "Google Test"
        },
        "issuer_info": {
            "CN": "WR2",
            "O": "Google Trust Services",
            "C": "US"
        },
        "subject_info": {
            "CN": "*.google.com"
        },
        "validity": {
            "not_before": "Mar 16 08:36:32 2026 GMT",
            "not_after": "Jun  8 08:36:31 2026 GMT"
        },
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "key_info": {
            "algorithm": "RSA",
            "key_size": "N/A"
        },
        "fingerprint": {
            "sha256": "N/A",
            "md5": "N/A (requires openssl)"
        },
        "extensions": {
            "version": 3,
            "san": [
                "DNS: *.google.com",
                "DNS: *.appengine.google.com",
                ...
            ]
        }
    },
    "cert_data": {
        "fqdn": "google.com",
        "issuer": "WR2 - Google Trust Services",
        "issuer_type": "Other",
        "expiry_date": "2026-06-08 08:36:31",
        "days_remaining": 61,
        "not_before": "2026-03-16 08:36:32",
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "sha256_fingerprint": "N/A",
        "subject_cn": "*.google.com",
        "pem": "PLACEHOLDER"
    }
}
```

**Accessing from UI**:
- Navigate to `/admin` → Find your certificate → Click "View Certificate Details" button
- Opens modal with comprehensive certificate information
- See all SSL certificate technical details

## Certificate Types Detection

The application automatically identifies SSL certificate issuers. Supported issuers:
- Let's Encrypt
- Sectigo (formerly Comodo)
- DigiCert
- GeoTrust
- GlobalSign
- Buypass
- Zauner
- Amazon (Certificate Manager)
- Google Trust Services
- Cloudflare
- Namecheap
- SSL.com
- Other (unrecognized issuers)

### POST `/api/certs/<fqdn>/refresh`
```bash
curl -X POST "http://localhost:4444/api/certs/google.com/refresh" -H "Authorization: Bearer your-token"
```\n\n### GET `/api/certs/<id>/details`\n\nRetrieve detailed certificate information including full certificate data.\n\n**Returns complete certificate details**:
- Basic certificate information (FQDN, SSL expiry, issuer, days remaining)
- Issuer details (CN, organization, country, organizational unit)
- Subject/owner information (CN, organization)
- Certificate validity period (not before, not after)
- Serial number and version
- Key algorithm and size information
- Subject Alternative Names (SANs) list
- SHA-256 fingerprint (if available)
- Certificate extensions

**Example**:

```bash
# Get detailed info for certificate with ID 9
curl -s 'http://localhost:4444/api/certs/9/details' \
  -H 'Authorization: Bearer your-token' | python3 -m json.tool

# Sample response:
{
    "success": true,
    "fqdn": "google.com",
    "details": {
        "basic_info": {
            "fqdn": "google.com",
            "url_id": 9,
            "customer_number": null,
            "customer_name": "Google Test"
        },
        "issuer_info": {
            "CN": "WR2",
            "O": "Google Trust Services",
            "C": "US"
        },
        "subject_info": {
            "CN": "*.google.com"
        },
        "validity": {
            "not_before": "Mar 16 08:36:32 2026 GMT",
            "not_after": "Jun  8 08:36:31 2026 GMT"
        },
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "key_info": {
            "algorithm": "RSA",
            "key_size": "N/A"
        },
        "fingerprint": {
            "sha256": "N/A",
            "md5": "N/A (requires openssl)"
        },
        "extensions": {
            "version": 3,
            "san": [
                "DNS: *.google.com",
                "DNS: *.appengine.google.com",
                ...
            ]
        }
    },
    "cert_data": {
        "fqdn": "google.com",
        "issuer": "WR2 - Google Trust Services",
        "issuer_type": "Other",
        "expiry_date": "2026-06-08 08:36:31",
        "days_remaining": 61,
        "not_before": "2026-03-16 08:36:32",
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "sha256_fingerprint": "N/A",
        "subject_cn": "*.google.com",
        "pem": "PLACEHOLDER"
    }
}
```

**Accessing from UI**:
- Navigate to `/admin` → Find your certificate → Click "View Certificate Details" button
- Opens modal with comprehensive certificate information
- See all SSL certificate technical details

## Certificate Types Detection

The application automatically identifies SSL certificate issuers. Supported issuers:
- Let's Encrypt
- Sectigo (formerly Comodo)
- DigiCert
- GeoTrust
- GlobalSign
- Buypass
- Zauner
- Amazon (Certificate Manager)
- Google Trust Services
- Cloudflare
- Namecheap
- SSL.com
- Other (unrecognized issuers)

3. **Access the application**:
   - Open your browser and navigate to: `http://localhost:4444`

## Usage

### Adding Certificates

1. Navigate to `/admin`
2. Fill in the form:
   - **FQDN**: The full URL (e.g., `https://example.com`) - required
   - **Customer Number**: Optional identifier
   - **Customer Name**: Optional name for the certificate owner
3. Click "Add Certificate"

### Viewing SSL Status

The main dashboard displays:
- All certificates sorted by expiration date (soonest first by default)
- Days remaining until expiry (negative if expired)
- Certificate issuer/type
- Customer information (if provided)
- Color-coded status indicators:
  - 🔴 **Red**: Expired certificates
  - 🟡 **Yellow**: Expiring within 30 days
  - 🔵 **Blue**: Warning status (30-90 days remaining)
  - 🟢 **Green**: Safe certificates (>90 days remaining)

### Sorting and Filtering

- Click on any column header to sort by that field
- Toggle between ascending and descending order
- Default sort: Days remaining ascending (expiring certificates first)

### Manual Certificate Refresh

Click the refresh icon (🔄) next to any certificate to force a manual SSL certificate check.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URI` | Database location | `sqlite:///ssl_monitor.db` |
| `CACHE_EXPIRATION_HOURS` | Cache refresh frequency | `24` |
| `SECRET_KEY` | Flask secret key | Random generated |
| `SLACK_WEBHOOK_URL` | Webhook for Slack notifications | Empty |

### Adding Future Notifications

To enable email/Slack notifications for expiring certificates (future enhancement):

1. Add `SLACK_WEBHOOK_URL` environment variable
2. Implement notification logic in `app/scheduler.py`
3. Send alerts for certificates expiring within configured thresholds

## API Endpoints

### GET `/api/urls`

Retrieve all URLs with SSL certificate information.

**Query Parameters**:
- `sort_by`: Field to sort by (`days_remaining`, `customer_name`, `fqdn`, `expiry_date`)
- `sort_order`: Sort order (`asc`, `desc`)

### POST `/api/certs/<fqdn>/refresh`
```bash
curl -X POST "http://localhost:4444/api/certs/google.com/refresh" -H "Authorization: Bearer your-token"
```\n\n### GET `/api/certs/<id>/details`\n\nRetrieve detailed certificate information including full certificate data.\n\n**Returns complete certificate details**:
- Basic certificate information (FQDN, SSL expiry, issuer, days remaining)
- Issuer details (CN, organization, country, organizational unit)
- Subject/owner information (CN, organization)
- Certificate validity period (not before, not after)
- Serial number and version
- Key algorithm and size information
- Subject Alternative Names (SANs) list
- SHA-256 fingerprint (if available)
- Certificate extensions

**Example**:

```bash
# Get detailed info for certificate with ID 9
curl -s 'http://localhost:4444/api/certs/9/details' \
  -H 'Authorization: Bearer your-token' | python3 -m json.tool

# Sample response:
{
    "success": true,
    "fqdn": "google.com",
    "details": {
        "basic_info": {
            "fqdn": "google.com",
            "url_id": 9,
            "customer_number": null,
            "customer_name": "Google Test"
        },
        "issuer_info": {
            "CN": "WR2",
            "O": "Google Trust Services",
            "C": "US"
        },
        "subject_info": {
            "CN": "*.google.com"
        },
        "validity": {
            "not_before": "Mar 16 08:36:32 2026 GMT",
            "not_after": "Jun  8 08:36:31 2026 GMT"
        },
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "key_info": {
            "algorithm": "RSA",
            "key_size": "N/A"
        },
        "fingerprint": {
            "sha256": "N/A",
            "md5": "N/A (requires openssl)"
        },
        "extensions": {
            "version": 3,
            "san": [
                "DNS: *.google.com",
                "DNS: *.appengine.google.com",
                ...
            ]
        }
    },
    "cert_data": {
        "fqdn": "google.com",
        "issuer": "WR2 - Google Trust Services",
        "issuer_type": "Other",
        "expiry_date": "2026-06-08 08:36:31",
        "days_remaining": 61,
        "not_before": "2026-03-16 08:36:32",
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "sha256_fingerprint": "N/A",
        "subject_cn": "*.google.com",
        "pem": "PLACEHOLDER"
    }
}
```

**Accessing from UI**:
- Navigate to `/admin` → Find your certificate → Click "View Certificate Details" button
- Opens modal with comprehensive certificate information
- See all SSL certificate technical details

## Certificate Types Detection

The application automatically identifies SSL certificate issuers. Supported issuers:
- Let's Encrypt
- Sectigo (formerly Comodo)
- DigiCert
- GeoTrust
- GlobalSign
- Buypass
- Zauner
- Amazon (Certificate Manager)
- Google Trust Services
- Cloudflare
- Namecheap
- SSL.com
- Other (unrecognized issuers)

### POST `/api/urls`

Add a new URL to monitor.

**Body**:
```json
{
  "fqdn": "https://example.com",
  "customer_number": "12345",
  "customer_name": "Example Customer"
}
```

### PUT `/api/urls/<id>`

Update an existing URL.

**Body**:
```json
{
  "fqdn": "https://updated-domain.com",
  "customer_name": "Updated Customer Name"
}
```

### DELETE `/api/urls/<id>`

Delete an URL to stop monitoring.

### POST `/api/certs/<fqdn>/refresh`

Force refresh SSL certificate information.

## Project Structure

```
ssl-checker/
├── app/
│   ├── __init__.py         # Application factory
│   ├── __main__.py         # Module entry point
│   config.py               # Configuration settings
│   database.py             # Database schema and operations
│   ssl_checker.py          # SSL certificate checking logic
│   scheduler.py            # Background task scheduler
│   routes.py               # Web routes and API endpoints
│   templates/
│   │   ├── index.html      # Main dashboard
│   │   └── admin.html      # Certificate management
│   └── static/
│       ├── css/           # Additional CSS files
│       └── js/            # JavaScript files
├── tests/
│   ├── test_ssl_checker.py  # Unit tests
│   └── test_api.py          # Integration tests
├── data/                   # SQLite database file (auto-generated)
├── logs/                   # Application logs
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Dockerfile
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Caching Strategy

The application uses a smart caching system to reduce unnecessary SSL checks:

1. **Initial Check**: When a certificate is added, it's checked immediately
2. **Status Determination**: Based on days remaining:
   - `< 30 days`: Critical status
   - `30-90 days`: Warning status
   - `> 90 days`: Safe status
3. **Refresh Schedule**:
   - Critical: Refresh every hour
   - Warning: Refresh every 12 hours
   - Safe: Refresh daily
4. **Background Scheduler**: Automatically runs certificate checks based on status

## Adding New Certificate Types

To add support for new certificate authorities:

1. Edit `app/ssl_checker.py`
2. Add patterns to the `determine_issuer_type()` function
3. Update the CSS styling to include badge styles for the new type

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_ssl_checker.py -v
python -m pytest tests/test_api.py -v
```

### Testing SSL Certificate Checking (Manual)

To test with real certificates:

1. Start the application
2. Add a known domain with a valid certificate
3. Verify the certificate details appear correctly
4. Check the caching schedule by inspecting logs

## Troubleshooting

### Common Issues

**Database errors**:
- Check that the `data/` directory is writable
- Ensure database URI points to a valid location

**SSL check failures**:
- Verify the domain is accessible and has a valid SSL certificate
- Check firewall rules and network connectivity

**Container startup issues**:
- Check logs: `docker-compose logs`
- Ensure no other service is using port 4444
- Verify environment variables are correctly set

### Logs

### POST `/api/certs/<fqdn>/refresh`
```bash
curl -X POST "http://localhost:4444/api/certs/google.com/refresh" -H "Authorization: Bearer your-token"
```\n\n### GET `/api/certs/<id>/details`\n\nRetrieve detailed certificate information including full certificate data.\n\n**Returns complete certificate details**:
- Basic certificate information (FQDN, SSL expiry, issuer, days remaining)
- Issuer details (CN, organization, country, organizational unit)
- Subject/owner information (CN, organization)
- Certificate validity period (not before, not after)
- Serial number and version
- Key algorithm and size information
- Subject Alternative Names (SANs) list
- SHA-256 fingerprint (if available)
- Certificate extensions

**Example**:

```bash
# Get detailed info for certificate with ID 9
curl -s 'http://localhost:4444/api/certs/9/details' \
  -H 'Authorization: Bearer your-token' | python3 -m json.tool

# Sample response:
{
    "success": true,
    "fqdn": "google.com",
    "details": {
        "basic_info": {
            "fqdn": "google.com",
            "url_id": 9,
            "customer_number": null,
            "customer_name": "Google Test"
        },
        "issuer_info": {
            "CN": "WR2",
            "O": "Google Trust Services",
            "C": "US"
        },
        "subject_info": {
            "CN": "*.google.com"
        },
        "validity": {
            "not_before": "Mar 16 08:36:32 2026 GMT",
            "not_after": "Jun  8 08:36:31 2026 GMT"
        },
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "key_info": {
            "algorithm": "RSA",
            "key_size": "N/A"
        },
        "fingerprint": {
            "sha256": "N/A",
            "md5": "N/A (requires openssl)"
        },
        "extensions": {
            "version": 3,
            "san": [
                "DNS: *.google.com",
                "DNS: *.appengine.google.com",
                ...
            ]
        }
    },
    "cert_data": {
        "fqdn": "google.com",
        "issuer": "WR2 - Google Trust Services",
        "issuer_type": "Other",
        "expiry_date": "2026-06-08 08:36:31",
        "days_remaining": 61,
        "not_before": "2026-03-16 08:36:32",
        "serial_number": "ACE65BAACA2AE1D80998CA59B3269D53",
        "version": 3,
        "sha256_fingerprint": "N/A",
        "subject_cn": "*.google.com",
        "pem": "PLACEHOLDER"
    }
}
```

**Accessing from UI**:
- Navigate to `/admin` → Find your certificate → Click "View Certificate Details" button
- Opens modal with comprehensive certificate information
- See all SSL certificate technical details

## Certificate Types Detection

The application automatically identifies SSL certificate issuers. Supported issuers:
- Let's Encrypt
- Sectigo (formerly Comodo)
- DigiCert
- GeoTrust
- GlobalSign
- Buypass
- Zauner
- Amazon (Certificate Manager)
- Google Trust Services
- Cloudflare
- Namecheap
- SSL.com
- Other (unrecognized issuers)

## Security Considerations

- Default SECRET_KEY should be changed in production
- Consider implementing authentication for admin functions
- Use HTTPS for the application itself in production
- Regularly update Python dependencies

## Future Enhancements

- [ ] Email notifications for expiring certificates
- [ ] Slack notifications integration
- [ ] Historical certificate data reporting
- [ ] Certificate renewal automation
- [ ] Bulk operations (import/export)
- [ ] Multiple language support
- [ ] Export to CSV/PDF
- [ ] Certificate hierarchy visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is open source and available for personal and commercial use.

## Support

For issues or questions, please create an issue on the project repository.
