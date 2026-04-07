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
- [x] POST /api/urls - Add new URL (with validation)
- [x] PUT /api/urls/<id> - Update URL
- [x] DELETE /api/urls/<id> - Delete URL
- [x] POST /api/certs/<fqdn>/refresh - Force certificate refresh
- [x] GET /api/certs/<fqdn>/details - Get full certificate details (ID: 18 ✅)

### Frontend
- [x] Modern responsive design with Bootstrap 5
- [x] Dashboard with color-coded status (green=active, yellow=warning, red=expired)
- [x] Admin panel for certificate management
- [x] Delete functionality with confirmation
- [x] Sortable columns (expiry date, customer name, FQDN, etc.)
- [x] Enhanced SSL details modal with full certificate information
- [x] Issuer name display (organization name only, no badge noise)
- [x] URL validation feedback (success/failure messages)

### DevOps & Testing
- [x] Docker container with Dockerfile and docker-compose.yml
- [x] `.env.example` configuration template
- [x] Comprehensive README with installation instructions
- [x] Test suite with build_and_test.sh script
- [x] Git repository with proper commit history

## ✅ Completed Features

### ID: 18 - Enhanced SSL Certificate Viewer (COMPLETED ✅)

**Status:** Completed

**Description:** 
Complete enhanced certificate details viewer with modal popup:

**Implemented Features:**
- ✅ API endpoint: `GET /api/certs/<fqdn>/details`
- ✅ Full certificate details including:
  - Serial Number, Version, Key Algorithm
  - Subject Alternative Names (SANs)
  - Not Before / Not After dates
  - Issuer details (CN, Organization, Country, OU)
  - Subject/owner information
  - SHA-256 fingerprint
  - Key usage, Extended key usage
  - Basic constraints

**UI Requirements:** 
- ✅ Modal/popup from certificate row
- ✅ Clean issuer name display (organization only)
- ✅ Copy-to-clipboard functionality for raw data
- ✅ Tree-view or collapsible sections
- ✅ Visual icons for different certificate properties

**Technical Implementation:**
- ✅ Enhanced SSL checker with openssl integration
- ✅ Extract issuer organization name correctly (organizationName camelCase)
- ✅ Certificate details template with modal component
- ✅ Proper markdown formatting for raw certificate data

**Files Modified:**
- `app/ssl_extended.py` - New module with get_full_certificate_info()
- `app/ssl_checker.py` - Enhanced issuer parsing with organizationName support
- `app/routes.py` - Added /api/certs/<fqdn>/details endpoint
- `app/templates/index.html` - Enhanced certificate details modal
- `app/templates/admin.html` - Enhanced SSL details popup

**Test Results:**
- ✅ Let's Encrypt: Shows "Let's Encrypt" correctly
- ✅ DigiCert: Shows "DigiCert EV RSA CA G2"
- ✅ Cloudflare: Shows "Cloudflare TLS Issuing ECC CA 1"
- ✅ Sectigo: Shows "Sectigo Public Server Authentication CA DV R36"

---

### ID: 19 - URL Validation System (COMPLETED ✅)

**Status:** Completed

**Description:** 
Validate SSL URLs before saving to ensure they are valid and reachable.

**Required Features:**
1. **URL Format Validation:**
   - ✅ Proper URL structure validation
   - ✅ Protocol validation (https:// only)
   - ✅ FQDN format validation (valid domain name characters)
   - ✅ No consecutive dots, valid labels

2. **Reachability Check:**
   - ✅ TCP connection test to host:port
   - ✅ SSL handshake verification
   - ✅ User feedback with detailed error messages

3. **User Feedback:**
   - ✅ Loading indicator during validation
   - ✅ Success message with certificate preview
   - ✅ Error message with specific validation issues

**Files Modified:**
- `app/url_utils.py` - URL validation functions
- `app/routes.py` - Validation before URL save

---

### ID: 20 - Custom Port Support (COMPLETED ✅)

**Status:** Completed

**Description:** 
Allow users to specify a custom port for SSL checks.

**Features:**
- ✅ Custom port extraction from URLs (e.g., https://example.com:8443)
- ✅ SSL checker uses custom port instead of hardcoded 443
- ✅ Default to 443 if no port specified
- ✅ Full integration with URL validation

**Files Modified:**
- `app/url_utils.py` - extract_port_from_url() function
- `app/ssl_checker.py` - get_ssl_info() uses custom port
- `app/routes.py` - Validation with custom port support
- New API endpoint: `GET /api/certs/<fqdn>/details`
- Enhanced ssl_checker.py with full certificate extraction
- Enhanced certificate display template with modal component
- Proper markdown formatting for raw certificate data

---

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
WHERE customer_name LIKE '%customer_name%'\nORDER BY created_at DESC;\n```\n\n---\n\n## ✅ Completed Features\n\n### ID: 22 - MCP Server Integration (COMPLETED ✅)\n\n**Status:** Completed\n\n**Description:**\nModel Context Protocol server for agent integration with SSL certificate monitoring.\n\n**Implemented Features:**\n- ✅ MCP server with stdio transport\n- ✅ Tool: `add_certificate` - Add new certificates to monitor\n- ✅ Tool: `list_certificates` - List all monitored certificates\n- ✅ Tool: `query_expiring` - Get certificates expiring in N days\n- ✅ Tool: `query_expired` - Get expired certificates\n- ✅ Tool: `query_customer` - Get certificates for specific customer\n- ✅ Tool: `refresh_certificate` - Manually refresh certificate\n- ✅ Tool: `get_certificate_details` - Get full certificate details\n- ✅ Tool: `delete_certificate` - Remove certificates from monitoring\n\n**Technical Implementation:**\n- Python MCP server using pydantic models\n- Integration with existing ssl_checker module\n- Database queries via existing get_db() function\n- Structured JSON responses with certificate data\n- Error handling with descriptive messages\n\n**Files Modified:**\n- `app/mcp_server.py` - MCP server implementation\n- `app/mcp_tools.py` - MCP tool definitions\n- `app/mcp_models.py` - Pydantic models for data structures\n\n**Agent Usage Examples:**\n```\n# Query certificates expiring soon\nAgent: \"Which SSL certificates are expiring in the next 60 days?\"\nMCP Server returns: {\"certificates\": [...], \"count\": 2}\n\n# List all certificates\nAgent: \"List all monitored SSL certificates\"\nMCP Server returns: {\"certificates\": [...], \"count\": 5}\n\n# Find expired certificates\nAgent: \"Find all expired certificates\"\nMCP Server returns: {\"certificates\": [...], \"count\": 1}\n```\n\n---\n\n## 📝 Implementation Notes\n
- Prioritize MCP server development for agent integration
- Ensure backward compatibility with existing web interface
- Write comprehensive documentation for MCP API usage
- Include examples of agent queries and expected outputs
- Plan for future MCP protocol extensions (real-time updates, etc.)
