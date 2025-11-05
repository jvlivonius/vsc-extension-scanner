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


if __name__ == "__main__":
    unittest.main()
