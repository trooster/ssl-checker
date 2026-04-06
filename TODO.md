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

---

## 🚧 Pending Features (MCP Server & Agent API)

### ID: 22 - MCP Server & Agent API Integration
**Status:** Pending

**Description:**
Create an MCP (Model Context Protocol) server and dedicated API endpoints for 
agent integration, allowing AI agents (like Hermes Agent) to interact with the
SSL certificate monitoring system programmatically.

**Required Features:**

1. **MCP Server Implementation:**
   - **Server:** `sslc-mcp-server` or similar
   - **Protocol:** Model Context Protocol
   - **Connectivity:** Hermes Agent, custom client, or web-based interface
   - **Transport:** Stdio or HTTP-based MCP server

2. **MCP Tools/Functions:**
   ```python
   # Tool: add_ssl_certificate
   "description": "Add a new SSL certificate to monitor"
   "inputSchema": {
       "fqdn": "string - The domain name to monitor (e.g., example.com)",
       "customer_number": "string - Optional customer ID",
       "customer_name": "string - Optional customer name",
       "port": "integer - Port number (default: 443)"
   }

   # Tool: list_ssl_certificates
   "description": "List all monitored SSL certificates"
   "inputSchema": {
       "sort_by": "string - Sort field (expiry, fqdn, customer_name, days_remaining)",
       "sort_order": "string - 'asc' or 'desc'",
       "limit": "integer - Limit results"
   }

   # Tool: get_certificate_details
   "description": "Get detailed SSL certificate information for a domain"
   "inputSchema": {
       "fqdn": "string - The domain name"
   }

   # Tool: delete_certificate
   "description": "Remove a certificate from monitoring"
   "inputSchema": {
       "id": "integer - Certificate ID to delete"
   }

   # Tool: refresh_certificate
   "description": "Force immediate SSL certificate check"
   "inputSchema": {
       "fqdn": "string - The domain name"
   }
   ```

3. **Advanced Query API:**
   - **Endpoint:** `GET /api/query/expiring`
   - **Purpose:** Find certificates expiring in specific timeframe
   - **Parameters:**
     ```
     GET /api/query/expiring?days=60
     # Returns: All certificates expiring in next 60 days
     ```
   
   - **Query Examples:**
     - "Which certificates are expiring in the next 2 months?"
     - "Show certificates expiring in less than 30 days"
     - "List all expired certificates"
     - "Find certificates with less than 90 days remaining"
     - "Get certificates for specific customer (filter by customer_name)"

4. **Natural Language Query Interface:**
   ```python
   # AI Agent can ask:
   "Which SSL certificates are expiring in the next 2 months?"
   # Returns formatted response with certificate details
   ```

5. **Agent Integration Workflow:**
   - Agent queries MCP server via stdio or HTTP
   - Agent receives JSON responses with certificate data
   - Agent can:
     - Add new certificates to monitor
     - Query certificates by expiration date
     - Get full certificate details
     - Trigger manual certificate refreshes
     - Delete certificates from monitoring

6. **Example Agent Query Flow:**
   ```
   User: "Check all SSL certificates and report any expiring soon"
   Agent → MCP Server → list_ssl_certificates()
   MCP Server → returns sorted list
   Agent → filters for days<90
   Agent → report: "3 certificates expiring in next 90 days"
   ```

7. **API Enhancements:**
   - **New Query Endpoints:**
     - `GET /api/query/expiring?days=N` - Certificates expiring in N days
     - `GET /api/query/expired` - All expired certificates
     - `GET /api/query/customer?name=NAME` - Certificates for customer
   
   - **Batch Operations:**
     - `POST /api/bulk/add` - Add multiple certificates at once
     - `POST /api/bulk/refresh` - Refresh all certificates

**Integration with Hermes Agent:**
- MCP server running as standalone service
- Hermes Agent connects via MCP protocol
- Agent can query: "Show me certificates expiring in 60 days"
- Agent receives structured JSON response
- Agent can generate reports in natural language

**Technical Requirements:**
- Python MCP server framework (mcp-server or similar)
- HTTP-based MCP client/server architecture
- Integration with existing SSL checker module
- Authentication via API keys or environment variables
- Logging and audit trail for agent actions

**Security Considerations:**
- API key authentication for MCP server
- Rate limiting for agent queries
- Input validation for user-submitted FQDNs
- Authorization for agent operations

**Example MCP Server Code Structure:**
```python
from mcp import Server
from ssl_checker import get_ssl_info, get_db

server = Server("ssl-cert-monitor")

@server.tool()
def add_certificate(fqdn: str, customer_number: str = "", customer_name: str = ""):
    """Add a new SSL certificate to monitor"""
    # Implementation here

@server.tool()
def list_certificates(sort_by: str = "expiry", sort_order: str = "asc"):
    """List all monitored certificates"""
    # Implementation here

@server.tool()
def query_expiring(days: int = 30):
    """Get certificates expiring in specified number of days"""
    # Implementation with SQL query filtering
```

**Usage Example for Agent:**
```
Agent: "I need to find certificates expiring soon"
Agent calls MCP Server tool: query_expiring(days=60)
MCP Server returns:
{
    "certificates": [
        {"fqdn": "example.com", "expiry": "2026-06-15", "days_left": 70},
        {"fqdn": "api.example.org", "expiry": "2026-05-20", "days_left": 45}
    ]
}
Agent reports: "Found 2 certificates expiring in the next 60 days"
```

**Database Queries:**
```sql
-- Certificates expiring in N days
SELECT * FROM urls u
LEFT JOIN ssl_cache sc ON u.fqdn LIKE '%' || sc.fqdn || '%'
WHERE sc.days_remaining IS NOT NULL 
  AND sc.days_remaining <= 60
ORDER BY sc.days_remaining ASC;

-- All expired certificates
SELECT * FROM urls u
LEFT JOIN ssl_cache sc ON u.fqdn LIKE '%' || sc.fqdn || '%'
WHERE sc.days_remaining IS NOT NULL 
  AND sc.days_remaining < 0
ORDER BY sc.days_remaining ASC;

-- Certificates for specific customer
SELECT * FROM urls
WHERE customer_name LIKE '%customer_name%'
ORDER BY created_at DESC;
```

---

## 📝 Implementation Notes

- Prioritize MCP server development for agent integration
- Ensure backward compatibility with existing web interface
- Write comprehensive documentation for MCP API usage
- Include examples of agent queries and expected outputs
- Plan for future MCP protocol extensions (real-time updates, etc.)
