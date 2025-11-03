"""
Security Coverage Boost Tests - Phase 3.

Focused tests to increase security module coverage to 95%+.
Targets specific uncovered security-critical lines.
"""

import sys
import os
import unittest
import pytest
from pathlib import Path
import tempfile
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner.utils import validate_extension_id
from vscode_scanner.cache_manager import CacheManager


@pytest.mark.security
class TestExtensionIDValidation(unittest.TestCase):
    """Test extension ID validation security."""

    def test_valid_extension_id_with_single_dot(self):
        """Test valid extension ID with exactly one dot."""
        self.assertTrue(validate_extension_id("microsoft.python"))
        self.assertTrue(validate_extension_id("esbenp.prettier-vscode"))
        self.assertTrue(validate_extension_id("GitHub.copilot"))

    def test_invalid_extension_id_multiple_dots(self):
        """Test rejection of extension IDs with multiple dots (lines 400-402)."""
        # Multiple dots should fail the "exactly one dot" check
        self.assertFalse(validate_extension_id("microsoft.python.tools"))
        self.assertFalse(validate_extension_id("a.b.c.d"))
        self.assertFalse(validate_extension_id("publisher.name.extra"))

    def test_invalid_extension_id_no_dots(self):
        """Test rejection of extension IDs with no dots (lines 400-402)."""
        # No dots should fail the "exactly one dot" check
        self.assertFalse(validate_extension_id("microsoftpython"))
        self.assertFalse(validate_extension_id("extension"))

    def test_invalid_extension_id_empty_publisher(self):
        """Test rejection of extension IDs with empty publisher (lines 404-406)."""
        # Empty publisher part should fail validation
        self.assertFalse(validate_extension_id(".extension"))

    def test_invalid_extension_id_empty_name(self):
        """Test rejection of extension IDs with empty name (lines 404-406)."""
        # Empty name part should fail validation
        self.assertFalse(validate_extension_id("publisher."))

    def test_invalid_extension_id_both_empty(self):
        """Test rejection of extension IDs with both parts empty (lines 404-406)."""
        # Both parts empty should fail validation
        self.assertFalse(validate_extension_id("."))

    def test_invalid_extension_id_path_traversal(self):
        """Test rejection of path traversal attempts."""
        self.assertFalse(validate_extension_id("../../../etc/passwd"))
        self.assertFalse(validate_extension_id("..\\..\\..\\windows\\system32"))

    def test_invalid_extension_id_sql_injection(self):
        """Test rejection of SQL injection attempts."""
        self.assertFalse(validate_extension_id("'; DROP TABLE scan_cache; --"))
        self.assertFalse(validate_extension_id("publisher'; DELETE FROM"))

    def test_invalid_extension_id_special_chars(self):
        """Test rejection of dangerous special characters."""
        self.assertFalse(validate_extension_id("publisher|name"))
        self.assertFalse(validate_extension_id("publisher&name"))
        self.assertFalse(validate_extension_id("publisher;name"))


@pytest.mark.security
class TestCacheDatabaseMigration(unittest.TestCase):
    """Test cache database migration checking (lines 450-475)."""

    def setUp(self):
        """Set up temporary cache directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary cache directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_migration_not_needed_for_new_database(self):
        """Test migration check returns False for new database (line 451)."""
        # Create cache manager with fresh directory
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        # Check if migration is needed (should be False for new database)
        migration_needed = cache_manager._check_if_migration_needed()

        # New database should not need migration
        self.assertFalse(migration_needed)

    def test_migration_not_needed_for_fresh_install(self):
        """Test migration check returns False when no table exists (line 465)."""
        # Create database file but no tables
        db_path = self.cache_dir / "cache.db"
        conn = sqlite3.connect(str(db_path))
        conn.close()

        # Create cache manager
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        # Check if migration is needed
        migration_needed = cache_manager._check_if_migration_needed()

        # Fresh install (no tables) should not need migration
        self.assertFalse(migration_needed)

    def test_v1_schema_raises_helpful_error(self):
        """Test v1.0 schema raises ValueError with helpful message."""
        # Create v1.0 schema database with metadata table
        db_path = self.cache_dir / "cache.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create old table schema (v1.0)
        cursor.execute(
            """
            CREATE TABLE scan_cache (
                extension_id TEXT PRIMARY KEY,
                scan_data TEXT NOT NULL,
                scan_timestamp TEXT NOT NULL
            )
        """
        )

        # Create metadata table with v1.0 version
        cursor.execute(
            """
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """
        )
        cursor.execute(
            "INSERT INTO metadata (key, value) VALUES ('schema_version', '1.0')"
        )
        conn.commit()
        conn.close()

        # Try to create cache manager - should raise ValueError
        with self.assertRaises(ValueError) as context:
            CacheManager(cache_dir=str(self.cache_dir))

        # Check error message is helpful
        error_message = str(context.exception)
        self.assertIn("v1.0 detected", error_message)
        self.assertIn("no longer supported", error_message)
        self.assertIn("upgrade to v3.5.x", error_message)

    def test_migration_check_handles_sqlite_error(self):
        """Test migration check returns False on SQLite error (line 474-475)."""
        # Create corrupted database file
        db_path = self.cache_dir / "cache.db"
        with open(db_path, "wb") as f:
            f.write(b"NOT A VALID SQLITE DATABASE")

        # Create cache manager
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        # Check if migration is needed (should handle error gracefully)
        migration_needed = cache_manager._check_if_migration_needed()

        # Corrupted database should return False
        self.assertFalse(migration_needed)


if __name__ == "__main__":
    unittest.main()
