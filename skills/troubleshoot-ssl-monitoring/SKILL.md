---
title: Troubleshooting SSL Certificate Monitor
description: Diagnose and fix common issues with the Flask SSL certificate monitoring application
tags: [ssl, flask, sqlite, jinja2, troubleshooting]
name: troubleshoot-ssl-monitoring
---

# SSL Certificate Monitor Troubleshooting Guide

## Common Issues and Solutions

### 1. Socket SSL Error in Python 3

**Problem:** Using `socket.ssl.SSLError` (Python 2 style) causes AttributeError in Python 3.

**Error:**
```
AttributeError: module 'socket' has no attribute 'ssl'
```

**Solution:**
```python
# Wrong (Python 2 style)
except socket.ssl.SSLError:

# Correct (Python 3)
import ssl
except ssl.SSLError:
```

### 2. Jinja2 Template Rendering Issues with NULL Values

**Problem:** Template shows `-` when data exists in database. This happens because:

- `None` in Python → `null` in Jinja2 → `is none` check required
- Using `== None` vs `is none` causes TypeErrors
- Missing `is not none` check before numeric comparisons

**Solution:**
```jinja2
{# Always check is not none before numeric comparisons #}
{% if url.days_remaining is not none and url.days_remaining < 0 %}
    <span class="badge bg-danger">{{ url.days_remaining }} days</span>
{% elif url.days_remaining is not none and url.days_remaining < 30 %}
    <span class="badge bg-warning">{{ url.days_remaining }} days</span>
{% elif url.days_remaining is not none %}
    <span class="badge bg-success">{{ url.days_remaining }} days</span>
{% else %}
    <span class="text-muted">-</span>
{% endif %}
```

### 3. SQL JOIN Matching Issues

**Problem:** URLs with protocol prefixes (`https://`) don't match cache entries (`login.werkstap.nl`).

**Solution:**
```sql
LEFT JOIN ssl_cache sc ON LOWER(u.fqdn) LIKE LOWER('%' || sc.fqdn || '%')
```

Or clean the FQDN before inserting:
```python
domain = url_fqdn.replace('https://', '').replace('http://', '')
```

### 4. Flask Caching Issues

**Problem:** Changes to database don't appear in web interface.

**Solution:** Restart Flask app:
```bash
pkill -f 'python run.py'
python run.py
```

Or add `@app.after_request` to clear db connections.

### 5. TLS 1.2 Connection Failures

**Problem:** SSL handshake fails on modern servers requiring TLS 1.2+.

**Solution:**
```python
import ssl
context = ssl.create_default_context()
# context.check_hostname = False  # if needed
# context.verify_mode = ssl.CERT_NONE  # if needed
```

### 6. Cache Entry Missing After Adding URL

**Problem:** Adding a URL works but certificate data shows `-` in UI.

**Diagnosis:**
1. Check `ssl_cache` table for matching entry
2. Verify JOIN query matches FQDNs correctly
3. Check if SSL check failed during initial add

**Solution:**
Refresh cache manually via API:
```bash
curl -X POST http://localhost:4444/api/urls/refresh
```

## Database Schema Reference

```sql
-- URLs table
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fqdn TEXT UNIQUE NOT NULL,
    ssl_port INTEGER DEFAULT 443,
    customer_number TEXT,
    customer_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- SSL cache table
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
```

## Quick Debug Commands

```bash
# Check database contents
sqlite3 ssl_monitor.db "SELECT * FROM urls;"
sqlite3 ssl_monitor.db "SELECT * FROM ssl_cache;"

# Test SQL query directly
python3 -c "import sqlite3; conn = sqlite3.connect('ssl_monitor.db'); rows = conn.execute('SELECT * FROM ssl_cache LIMIT 10').fetchall(); print(rows)"

# Check Flask logs
tail -f /tmp/ssl-monitor.log
```
