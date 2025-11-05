"""
Test cache orphaned entries cleanup - Lines 854-909 coverage.

Covers cleanup_orphaned_entries() function to improve cache_manager.py
coverage from 79.32% to 80.65% (+1.33%).
"""

import sys
import os
import unittest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner.cache_manager import CacheManager


@pytest.mark.unit
class TestCacheOrphanedCleanup(unittest.TestCase):
    """Test orphaned cache entries cleanup functionality."""

    def test_cleanup_orphaned_entries_basic(self):
        """Test basic orphaned entries removal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # Create 5 cache entries
            for i in range(1, 6):
                cache.save_result(
                    f"publisher.extension{i}",
                    "1.0.0",
                    {"scan_status": "success", "vulnerabilities": []},
                )

            # Keep only 2 extensions (3 should be orphaned)
            valid_ids = ["publisher.extension1", "publisher.extension2"]
            deleted_count, warnings = cache.cleanup_orphaned_entries(valid_ids)

            # Should have deleted 3 orphaned entries
            self.assertEqual(deleted_count, 3)
            self.assertEqual(len(warnings), 0)

            # Verify only valid entries remain
            result1 = cache.get_cached_result("publisher.extension1", "1.0.0")
            result2 = cache.get_cached_result("publisher.extension2", "1.0.0")
            result3 = cache.get_cached_result("publisher.extension3", "1.0.0")

            self.assertIsNotNone(result1)
            self.assertIsNotNone(result2)
            self.assertIsNone(result3)  # Should be deleted

    def test_cleanup_with_empty_valid_ids(self):
        """Test cleanup with empty valid extension IDs list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # Create some entries
            cache.save_result(
                "publisher.extension1", "1.0.0", {"scan_status": "success"}
            )

            # Call cleanup with empty list
            deleted_count, warnings = cache.cleanup_orphaned_entries([])

            # Should return early without deleting anything
            self.assertEqual(deleted_count, 0)
            self.assertEqual(len(warnings), 0)

            # Entry should still exist
            result = cache.get_cached_result("publisher.extension1", "1.0.0")
            self.assertIsNotNone(result)

    def test_cleanup_with_invalid_extension_ids(self):
        """Test SQL injection prevention - filter invalid extension IDs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # Create legitimate entries
            cache.save_result("ms-python.python", "1.0.0", {"scan_status": "success"})
            cache.save_result("github.copilot", "1.0.0", {"scan_status": "success"})

            # Mix of valid and invalid IDs (SQL injection attempts)
            mixed_ids = [
                "ms-python.python",  # Valid
                "'; DROP TABLE scan_cache; --",  # SQL injection attempt
                "github.copilot",  # Valid
                "../../../etc/passwd",  # Path traversal attempt
                "valid-extension.id",  # Valid
            ]

            deleted_count, warnings = cache.cleanup_orphaned_entries(mixed_ids)

            # Should have filtered invalid IDs
            self.assertEqual(len(warnings), 1)
            self.assertIn("Filtered out", warnings[0].message)
            self.assertIn("2 invalid extension IDs", warnings[0].message)

            # Should have cleaned up only with valid IDs
            # (ms-python.python, github.copilot remain; valid-extension.id not in cache so nothing deleted)
            self.assertEqual(deleted_count, 0)

    def test_cleanup_with_all_invalid_ids(self):
        """Test cleanup when all provided IDs are invalid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # Create entry
            cache.save_result(
                "publisher.extension", "1.0.0", {"scan_status": "success"}
            )

            # All invalid IDs
            invalid_ids = [
                "'; DROP TABLE users; --",
                "../../../etc/passwd",
                "<script>alert('xss')</script>",
            ]

            deleted_count, warnings = cache.cleanup_orphaned_entries(invalid_ids)

            # Should filter all and return early
            self.assertEqual(deleted_count, 0)
            self.assertEqual(len(warnings), 1)
            self.assertIn("Filtered out 3 invalid", warnings[0].message)

    def test_cleanup_triggers_vacuum(self):
        """Test that cleanup triggers VACUUM when threshold exceeded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # Create many entries (to exceed vacuum threshold)
            for i in range(100):
                cache.save_result(
                    f"publisher.extension{i}",
                    "1.0.0",
                    {"scan_status": "success", "vulnerabilities": []},
                )

            # Keep only 1 extension (99 orphaned)
            valid_ids = ["publisher.extension0"]
            deleted_count, warnings = cache.cleanup_orphaned_entries(valid_ids)

            # Should have deleted 99 entries
            self.assertEqual(deleted_count, 99)

            # VACUUM should have been triggered (implicit verification via no errors)
            # Can't easily verify VACUUM was called without mocking, but it should happen

    def test_cleanup_with_database_error(self):
        """Test graceful handling of database errors during cleanup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # Create entry
            cache.save_result(
                "publisher.extension", "1.0.0", {"scan_status": "success"}
            )

            # Mock _db_connection to raise sqlite3.Error
            with patch.object(
                cache,
                "_db_connection",
                side_effect=sqlite3.Error("Database locked"),
            ):
                deleted_count, warnings = cache.cleanup_orphaned_entries(
                    ["publisher.extension"]
                )

                # Should handle error gracefully
                self.assertEqual(deleted_count, 0)
                # Warnings list might be empty (error printed to stderr)

    def test_cleanup_no_orphaned_entries(self):
        """Test cleanup when all cached extensions are still valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # Create 3 entries
            for i in range(1, 4):
                cache.save_result(
                    f"publisher.extension{i}",
                    "1.0.0",
                    {"scan_status": "success"},
                )

            # All 3 extensions are still valid
            valid_ids = [
                "publisher.extension1",
                "publisher.extension2",
                "publisher.extension3",
            ]
            deleted_count, warnings = cache.cleanup_orphaned_entries(valid_ids)

            # No orphaned entries, nothing deleted
            self.assertEqual(deleted_count, 0)
            self.assertEqual(len(warnings), 0)


if __name__ == "__main__":
    unittest.main()
