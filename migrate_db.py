import sqlite3

# Connect to database
conn = sqlite3.connect('ssl_monitor.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== Database Migration to Support Custom Ports ===")

# Check current tables
print("\nCurrent tables:")
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(f"  - {row[0]}")

# Create temporary backed up table
cursor.execute("ALTER TABLE urls ADD COLUMN ssl_port INTEGER DEFAULT 443")
print("\n✓ Added ssl_port column to urls table")

# Handle ssl_cache - we need to drop and recreate since UNIQUE constraint changed
print("\nDropping and recreating ssl_cache table...")

# Get existing data
cursor.execute("SELECT * FROM ssl_cache")
existing_data = cursor.fetchall()

# Drop existing table
cursor.execute("DROP TABLE IF EXISTS ssl_cache")

# Recreate table with new schema
cursor.execute('''
    CREATE TABLE ssl_cache (
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

# Restore existing data
if existing_data:
    for row in existing_data:
        cursor.execute('''
            INSERT INTO ssl_cache (id, fqdn, ssl_port, issuer, issuer_type, expiry_date, days_remaining, checked_at, status)
            VALUES (?, ?, 443, ?, ?, ?, ?, ?, ?)
        ''', (
            row['id'], row['fqdn'], row['issuer'], row['issuer_type'], 
            row['expiry_date'], row['days_remaining'], row['checked_at'], row['status']
        ))

print(f"✓ Recreated ssl_cache with {len(existing_data)} rows")

# Create new index
cursor.execute("CREATE INDEX IF NOT EXISTS idx_ssl_cache_port ON ssl_cache(ssl_port)")
print("✓ Created index on ssl_port")

# Commit changes
conn.commit()

# Verify schema
print("\n=== Updated Schema ===")
print("\nURLS table:")
for row in cursor.execute("PRAGMA table_info(urls)"):
    print(f"  {row[1]}: {row[2]}")

print("\nSSL_CACHE table:")
for row in cursor.execute("PRAGMA table_info(ssl_cache)"):
    print(f"  {row[1]}: {row[2]}")

print("\nIndexes:")
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='ssl_cache'"):
    print(f"  {row[0]}")

conn.close()
print("\n✓ Migration complete!")
