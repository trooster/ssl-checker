# SSL Certificate Monitor - Feature Roadmap

## ✅ Completed Features

### Core Functionality
- [x] SSL certificate monitoring with smart caching system
- [x] Admin panel for CRUD operations on URLs
- [x] Sortable dashboard with color-coded status indicators
- [x] Automatic issuer detection (Let's Encrypt, Sectigo, DigiCert, Amazon, etc.)
- [x] RESTful API for data operations
- [x] Manual certificate refresh functionality
- [x] Daily automatic certificate refresh via scheduler
- [x] Docker deployment support

### Database & Caching
- [x] SQLite database with proper schema
- [x] SSL cache table with expiry date, days remaining, issuer info
- [x] Smart caching based on certificate urgency (<30 days = 12h, 30-90 days = daily)
- [x] FQDN matching without/without https:// prefix

### API Endpoints
- [x] GET /api/urls - Fetch all URLs with sorting
- [x] POST /api/urls - Add new URL
- [x] PUT /api/urls/<id> - Update URL
- [x] DELETE /api/urls/<id> - Delete URL
- [x] POST /api/certs/<fqdn>/refresh - Force certificate refresh

### Frontend
- [x] Modern responsive design with Bootstrap 5
- [x] Dashboard with color-coded status (green=active, yellow=warning, red=expired)
- [x] Admin panel for certificate management
- [x] Delete functionality with confirmation
- [x] Sortable columns (expiry date, customer name, FQDN, etc.)

### DevOps & Testing
- [x] Docker container with Dockerfile and docker-compose.yml
- [x] `.env.example` configuration template
- [x] Comprehensive README with installation instructions
- [x] Test suite with build_and_test.sh script
- [x] Git repository with proper commit history

## 🚧 Pending Features (Enhanced SSL Details)

### ID: 18 - Enhanced SSL Certificate Viewer
**Status:** Pending

**Description:** 
Create an enhanced view panel/modal showing detailed certificate information:

**Required Fields:**
- **Certificate Details:**
  - Serial Number
  - Signature Algorithm
  - Version
  - Subject Alternative Names (SANs)
  - Not Before / Not After dates (full format)
  
- **Issuer Information:**
  - Common Name
  - Organization
  - Organizational Unit
  - Country
  - State/Province
  - Locality/City

- **Subject/Owner Information:**
  - Common Name (CN)
  - Organization (O)
  - Organizational Unit (OU)
  - Country (C)
  - State/Province (ST)
  - Locality (L)

- **Additional Certificate Properties:**
  - Fingerprint (SHA-256, MD5)
  - Public Key Algorithm
  - Public Key Size (bits)
  - Key Usage
  - Extended Key Usage
  - Basic Constraints (CA status)
  - CRL Distribution Points
  - Authority Information Access (OCSP, ISSUER)
  - Subject Key Identifier
  - Authority Key Identifier

- **Raw Certificate Data:**
  - Full certificate in PEM format
  - Full certificate in DER format (hex)
  - All OpenSSL command output (openssl x509 -text -in cert.pem)

**UI Requirements:**
- Modal/popup from certificate row
- Copy-to-clipboard functionality for raw data
- Tree-view or collapsible sections for organized display
- Visual icons for different certificate properties
- Export button for full certificate details

**Technical Requirements:**
- New API endpoint: `GET /api/certs/<fqdn>/details`
- Enhanced ssl_checker.py with full certificate extraction
- Enhanced certificate display template with modal component
- Proper markdown formatting for raw certificate data

---

## 🚧 Pending Features (URL Validation)

### ID: 19 - URL Validation System
**Status:** Pending

**Description:**
Validate SSL URLs before saving to ensure they are valid and reachable.

**Required Features:**
1. **URL Format Validation:**
   - Proper URL structure validation (URL parsing libraries)
   - Protocol validation (https:// only for now)
   - FQDN format validation (valid domain name characters)
   - No IP addresses (optional rule for SSL certs)

2. **Reachability Check:**
   - TCP connection test to host:port
   - HTTP HEAD request verification
   - SSL handshake verification
   - Response code check (success vs error)

3. **User Feedback:**
   - Loading indicator during validation
   - Success message with certificate preview
   - Error messages with specific validation failures
   - Option to continue anyway if user wants

4. **Validation States:**
   - ✅ Valid URL and reachable
   - ⚠️ Invalid URL format
   - ❌ URL not reachable (server error)
   - ⏳ Timeout during validation

**Technical Implementation:**
- New API endpoints for validation tests:
  - `POST /api/validate/url` - Validate URL format
  - `POST /api/validate/reachable` - Test server reachability
- Async validation with timeout (5 seconds)
- Connection timeout and SSL handshake timeout handling
- User-friendly error messages

**Security Considerations:**
- Rate limiting for validation attempts
- Connection timeout to prevent hanging
- No open proxy vulnerability
- Validate against known safe URL patterns

---

## 🚧 Pending Features (Custom Port Support)

### ID: 20 - Custom Port Port Support
**Status:** Pending

**Description:**
Allow users to specify custom ports for SSL certificate checks beyond the default HTTPS port 443.

**Required Features:**
1. **Port Field in Forms:**
   - Input field for custom port (default: 443)
   - Port range validation (1-65535)
   - Common port shortcuts (8443, 8080, 4430, etc.)

2. **Data Model Updates:**
   - Add `port` column to `urls` table
   - Add `port` column to `ssl_cache` table
   - Migration script for existing data

3. **SSL Check Logic:**
   - Parse URL for custom port
   - Default to 443 if no port specified
   - Support both http:// and https:// with custom ports
   - SSL handshake on specified port

4. **UI Updates:**
   - Add port input field to admin form
   - Display port in dashboard table
   - Visual indicator for custom ports (vs default 443)
   - Quick port selection dropdown

5. **API Updates:**
   - Support port parameter in API requests
   - Update certificate check to use custom port
   - Validation endpoint for custom port URLs

**Database Schema Changes:**
```sql
ALTER TABLE urls ADD COLUMN port INTEGER DEFAULT 443;
ALTER TABLE ssl_cache ADD COLUMN port INTEGER DEFAULT 443;
```

**Frontend Requirements:**
- Port input with placeholder "443 (default)"
- Validation: numeric input, min=1, max=65535
- Common ports dropdown: 8443, 8080, 4430, 9443, etc.
- Toggle between custom and default port

**Technical Considerations:**
- SSL certificate matching for wildcard ports support
- Different certificate behavior on non-standard ports
- Firewall/ACL considerations for custom ports
- Connection timeout handling for custom ports

**Validation Rules:**
- Port must be numeric
- Port must be between 1-65535
- If port=443, treat as default HTTPS
- If port≠443, add to display and validation message

---

## 🚧 Pending Features (Slack Notifications)

### ID: 21 - Slack Notification System
**Status:** Pending

**Description:**
Implement Slack notifications for SSL certificate events and alerts.

**Required Features:**
1. **Notification Triggers:**
   - Certificate expiring soon (<30 days remaining)
   - Certificate already expired
   - Certificate renewal success (after refresh)
   - Server unreachable during check
   - Weekly digest report

2. **Alert Severity Levels:**
   - 🔴 CRITICAL: Certificate expired
   - 🟡 WARNING: Certificate expiring soon (<90 days)
   - ℹ️ INFO: Certificate checked successfully
   - ⚠️ ERROR: Server unreachable

3. **Slack Integration:**
   - Slack App configuration (OAuth tokens)
   - Incoming Webhooks setup
   - Slack Bolt framework for message formatting
   - Message formatting with Slack blocks

4. **Message Formats:**
   ```python
   # Critical Expiration Alert
   {
       "text": "🔴 SSL Certificate Expiration Alert",
       "blocks": [
           {"type": "header", "text": {"type": "plain_text", "text": "🔴 Certificate Expired"}},
           {"type": "section", "fields": [
               {"type": "mrkdwn", "text": "*Certificate:* `example.com`"},
               {"type": "mrkdwn", "text": "*Expired:* 2024-01-15"},
               {"type": "mrkdwn", "text": "*Days Overdue:* -30"}
           ]},
           {"type": "actions", "elements": [
               {"type": "button", "text": {"type": "plain_text", "text": "View Details"}, "url": "https://ssl-checker.example.com/admin?edit=123"}
           ]}
       ]
   }
   ```

5. **Configuration:**
   - Environment variable: `SLACK_WEBHOOK_URL`
   - Environment variable: `SLACK_CHANNEL` (optional)
   - Environment variable: `SLACK_USER_ID` (optional)
   - Notification threshold settings in config
   - Quiet hours configuration (no notifications during night)

6. **Testing:**
   - Test notifications for each trigger type
   - Webhook URL validation
   - Connection testing utility
   - Debug mode for verbose logging

7. **User Preferences:**
   - Admin can enable/disable notifications
   - Threshold configuration (30 days, 14 days, etc.)
   - Email vs Slack notification toggle
   - Notification frequency control

**Database Schema:**
```sql
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY,
    enabled BOOLEAN DEFAULT TRUE,
    threshold_days INTEGER DEFAULT 30,
    slack_webhook TEXT,
    quiet_hours_start TEXT,
    quiet_hours_end TEXT,
    updated_at TIMESTAMP
);
```

**Technical Implementation:**
- Slack Bolt Python framework
- aiohttp for async HTTP calls to Slack API
- Retry logic with exponential backoff
- Error handling and logging
- Message history tracking
- Rate limiting compliance

---

## 📋 Implementation Priority

### High Priority
1. **URL Validation (ID: 19)** - Prevents useless entries in database
2. **Custom Port Support (ID: 20)** - Extends functionality to non-standard SSL setups
3. **Slack Notifications (ID: 21)** - Immediate operational value for alerts

### Medium Priority
4. **Enhanced SSL Details (ID: 18)** - Improves debugging and troubleshooting

---

## 🔗 References

- **SSL Certificate Parsing:** [OpenSSL x509 documentation](https://www.openssl.org/docs/man1.1.1/man1/x509.html)
- **Slack Bolt Framework:** [Python SDK](https://slack.dev/bolt-python/tutorial/getting-started)
- **URL Validation:** [RFC 3986 URI syntax](https://datatracker.ietf.org/doc/html/rfc3986)
- **Custom SSL Ports:** [Common SSL/TLS port list](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers)

---

## 📝 Notes

- All features should be backward compatible with existing data
- Implement proper migration scripts for database schema changes
- Update README.md after each feature implementation
- Write tests for new functionality before deployment
- Follow existing code patterns and style conventions
