#!/usr/bin/env python3
"""
Test database integrity check functionality
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

import pytest

# Module-level marker for all tests in this file
pytestmark = pytest.mark.integration

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner.cache_manager import CacheManager


def test_normal_database():
    """Test that a normal database passes integrity check."""
    print("TEST 1: Normal database integrity check")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / ".vscan"

        # Create cache manager (will create database)
        cache = CacheManager(cache_dir=str(cache_dir))

        # Verify database exists
        assert cache.cache_db.exists(), "Database should exist"

        # Manually run integrity check
        integrity_ok = cache._verify_database_integrity()
        assert integrity_ok, "Database integrity check should pass"

        # Save a test result
        test_result = {
            "name": "test-extension",
            "version": "1.0.0",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
            "scan_status": "success",
        }
        cache.save_result("test.extension", "1.0.0", test_result)

        # Verify we can read it back
        cached = cache.get_cached_result("test.extension", "1.0.0")
        assert cached is not None, "Should retrieve cached result"

        print("✓ Normal database passed integrity check")
        print("✓ Can save and retrieve results")
        print()


def test_corrupted_database():
    """Test that a corrupted database is detected and handled."""
    print("TEST 2: Corrupted database detection and recovery")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / ".vscan"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Create a normal database first
        cache = CacheManager(cache_dir=str(cache_dir))
        db_path = cache.cache_db

        # Save a test result
        test_result = {
            "name": "test-extension",
            "version": "1.0.0",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
            "scan_status": "success",
        }
        cache.save_result("test.extension", "1.0.0", test_result)

        print(f"✓ Created normal database at {db_path}")

        # Corrupt the database by truncating it
        with open(db_path, "wb") as f:
            f.write(b"CORRUPTED DATABASE FILE")

        print("✓ Corrupted database file")

        # Try to create cache manager again - should detect corruption
        print("✓ Attempting to initialize cache manager with corrupted DB...")
        cache2 = CacheManager(cache_dir=str(cache_dir))

        # Check that backup was created
        backup_files = list(cache_dir.glob("cache.db.corrupted.*"))
        assert len(backup_files) > 0, "Backup file should exist"
        print(f"✓ Backup created: {backup_files[0].name}")

        # New database should be created and functional
        assert cache2.cache_db.exists(), "New database should exist"

        # Verify new database works
        integrity_ok = cache2._verify_database_integrity()
        assert integrity_ok, "New database should pass integrity check"
        print("✓ New database created and passes integrity check")

        # Verify we can use new database
        cache2.save_result("test.extension2", "2.0.0", test_result)
        cached = cache2.get_cached_result("test.extension2", "2.0.0")
        assert cached is not None, "Should work with new database"
        print("✓ New database is functional")
        print()


def test_invalid_sqlite_header():
    """Test that a database with invalid SQLite header is handled."""
    print("TEST 3: Invalid SQLite header handling")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / ".vscan"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Create a file with invalid SQLite header
        db_path = cache_dir / "cache.db"
        with open(db_path, "wb") as f:
            # SQLite databases should start with "SQLite format 3\000"
            # Write something else instead
            f.write(b"INVALID SQLITE HEADER" + b"\x00" * 100)

        print(f"✓ Created database file with invalid header at {db_path}")

        # Try to initialize - should detect corruption and recover
        print("✓ Attempting to initialize cache manager with invalid DB...")
        cache = CacheManager(cache_dir=str(cache_dir))

        # Should have created backup and new database
        backup_files = list(cache_dir.glob("cache.db.corrupted.*"))
        assert (
            len(backup_files) > 0
        ), f"Backup should be created, found: {list(cache_dir.glob('*'))}"
        print(f"✓ Backup created: {backup_files[0].name}")

        # Verify new database is functional
        integrity_ok = cache._verify_database_integrity()
        assert integrity_ok, "New database should pass integrity check"
        print("✓ New database is functional")
        print()


def main():
    """Run all tests."""
    print("=" * 50)
    print("Database Integrity Check Tests")
    print("=" * 50)
    print()

    try:
        test_normal_database()
        test_corrupted_database()
        test_invalid_sqlite_header()

        print("=" * 50)
        print("ALL TESTS PASSED ✓")
        print("=" * 50)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
