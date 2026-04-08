"""
Unit tests for database utilities (database.py)
"""
import unittest
import pytest
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock

# Create a test Flask app context for database tests
from app import create_app


class TestDatabaseSchema(unittest.TestCase):
    """Tests for database schema initialization"""

    def setUp(self):
        """Set up test database"""
        self.test_db_path = '/tmp/test_schema.db'
        # Clean up any existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_database_file_created(self):
        """Test that database file is created"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        app.config['TESTING'] = True

        with app.app_context():
            from app.database import init_db, get_db
            init_db(app)

            # Verify database file was created
            self.assertTrue(os.path.exists(self.test_db_path))

            # Verify tables exist
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = cursor.fetchall()
            table_names = [t[0] for t in tables]

            self.assertIn('urls', table_names)
            self.assertIn('ssl_cache', table_names)
            conn.close()


class TestDatabaseConnection(unittest.TestCase):
    """Tests for database connection handling"""

    def setUp(self):
        self.test_db_path = '/tmp/test_conn.db'
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_get_db_creates_connection(self):
        """Test that get_db creates a connection when none exists"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'

        with app.app_context():
            from app.database import get_db
            db = get_db()
            self.assertIsNotNone(db)

    def test_get_db_returns_same_connection(self):
        """Test that get_db returns the same connection within context"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'

        with app.app_context():
            from app.database import get_db
            db1 = get_db()
            db2 = get_db()
            self.assertIs(db1, db2)

    def test_close_db_removes_connection(self):
        """Test that close_db removes connection from g"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'

        with app.app_context():
            from app.database import get_db, close_db, g
            db = get_db()
            self.assertIn('db', g)

            close_db(None)
            self.assertNotIn('db', g)


class TestDatabaseTables(unittest.TestCase):
    """Tests for database table structure"""

    def setUp(self):
        self.test_db_path = '/tmp/test_tables.db'
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_urls_table_columns(self):
        """Test that urls table has expected columns"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        app.config['TESTING'] = True

        with app.app_context():
            from app.database import init_db, get_db
            init_db(app)

            db = get_db()
            cursor = db.execute("PRAGMA table_info(urls)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}

            expected_columns = ['id', 'fqdn', 'ssl_port', 'customer_number',
                              'customer_name', 'created_at', 'updated_at']
            for col in expected_columns:
                self.assertIn(col, columns, f"Column {col} not found in urls table")

    def test_ssl_cache_table_columns(self):
        """Test that ssl_cache table has expected columns"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        app.config['TESTING'] = True

        with app.app_context():
            from app.database import init_db, get_db
            init_db(app)

            db = get_db()
            cursor = db.execute("PRAGMA table_info(ssl_cache)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}

            expected_columns = ['id', 'fqdn', 'ssl_port', 'issuer', 'issuer_type',
                              'expiry_date', 'days_remaining', 'checked_at', 'status']
            for col in expected_columns:
                self.assertIn(col, columns, f"Column {col} not found in ssl_cache table")

    def test_indexes_created(self):
        """Test that expected indexes are created"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        app.config['TESTING'] = True

        with app.app_context():
            from app.database import init_db, get_db
            init_db(app)

            db = get_db()
            cursor = db.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            indexes = [row[0] for row in cursor.fetchall()]

            expected_indexes = [
                'idx_ssl_cache_checked_at',
                'idx_ssl_cache_days_remaining',
                'idx_ssl_cache_port',
                'idx_urls_customer_name'
            ]
            for idx in expected_indexes:
                self.assertIn(idx, indexes, f"Index {idx} not found")


class TestDatabaseConstraints(unittest.TestCase):
    """Tests for database constraints and relationships"""

    def setUp(self):
        self.test_db_path = '/tmp/test_constraints.db'
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_fqdn_unique_constraint(self):
        """Test that fqdn has UNIQUE constraint"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        app.config['TESTING'] = True

        with app.app_context():
            from app.database import init_db, get_db
            init_db(app)

            db = get_db()
            cursor = db.execute("PRAGMA table_info(urls)")
            columns = [dict(row) for row in cursor]

            # Check that fqdn has NOT NULL constraint (notnull=1)
            fqdn_col = next((c for c in columns if c['name'] == 'fqdn'), None)
            self.assertIsNotNone(fqdn_col)
            self.assertEqual(fqdn_col['notnull'], 1, "fqdn should have NOT NULL constraint")

            # Check for unique index (auto-generated from UNIQUE constraint)
            cursor = db.execute("PRAGMA index_list(urls)")
            indexes = [dict(row) for row in cursor]
            has_unique = any(idx['unique'] == 1 for idx in indexes)
            self.assertTrue(has_unique, "fqdn should have UNIQUE constraint (via autoindex)")

    def test_ssl_cache_fqdn_foreign_key(self):
        """Test that ssl_cache has foreign key to urls"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        app.config['TESTING'] = True

        with app.app_context():
            from app.database import init_db, get_db
            init_db(app)

            db = get_db()
            cursor = db.execute("PRAGMA foreign_key_list(ssl_cache)")
            foreign_keys = cursor.fetchall()

            # Check that fqdn has a foreign key
            self.assertGreater(len(foreign_keys), 0,
                             "ssl_cache should have foreign key on fqdn")


class TestDatabaseFunctions(unittest.TestCase):
    """Tests for database utility functions"""

    def setUp(self):
        self.test_db_path = '/tmp/test_functions.db'
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_db_connection_has_row_factory(self):
        """Test that get_db returns connection with Row factory"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'

        with app.app_context():
            from app.database import get_db
            db = get_db()
            self.assertIsNotNone(db.row_factory)

    def test_multiple_connections_same_context(self):
        """Test that multiple connections in same context work correctly"""
        app = create_app()
        app.config['DATABASE_URI'] = f'sqlite:///{self.test_db_path}'

        with app.app_context():
            from app.database import get_db
            db1 = get_db()
            db2 = get_db()

            # Verify they're the same connection
            self.assertIs(db1, db2)

            # Verify both can execute queries
            result1 = db1.execute("SELECT 1")
            result2 = db2.execute("SELECT 2")
            self.assertEqual(result1.fetchone()[0], 1)
            self.assertEqual(result2.fetchone()[0], 2)


if __name__ == '__main__':
    unittest.main()
