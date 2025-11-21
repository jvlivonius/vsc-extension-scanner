#!/usr/bin/env python3
"""
Test report command with empty cache scenarios.

Tests:
1. Bug fix: display_warning import is available
2. Empty cache with extensions - decline scan
3. Empty cache with extensions - accept scan (mocked)
4. No extensions installed scenario
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.cli import _check_extensions_exist


@pytest.mark.integration
class TestReportEmptyCache(unittest.TestCase):
    """Test report command with empty cache."""

    def test_check_extensions_exist_with_extensions(self):
        """Test _check_extensions_exist when extensions are present."""
        # This will check the actual user's VS Code extensions
        exists, count = _check_extensions_exist()

        # Verify the function returns sensible values
        self.assertIsInstance(exists, bool)
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

        # If extensions exist, count should be > 0; if not, count should be 0
        if exists:
            self.assertGreater(count, 0, "If exists=True, count should be positive")
        else:
            self.assertEqual(count, 0, "If exists=False, count should be zero")

    def test_check_extensions_exist_no_extensions(self):
        """Test _check_extensions_exist when no extensions exist."""
        # Use a non-existent directory
        exists, count = _check_extensions_exist(extensions_dir="/nonexistent/path")

        self.assertFalse(exists)
        self.assertEqual(count, 0)

    def test_check_extensions_exist_empty_directory(self):
        """Test _check_extensions_exist with empty directory."""
        import tempfile
        import os

        # Create temporary empty directory
        with tempfile.TemporaryDirectory() as tmpdir:
            exists, count = _check_extensions_exist(extensions_dir=tmpdir)

            self.assertFalse(exists)
            self.assertEqual(count, 0)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
