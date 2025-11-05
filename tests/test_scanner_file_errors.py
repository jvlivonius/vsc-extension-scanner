"""
Test scanner file error handling - Lines 165, 176 coverage.

Covers FileNotFoundError and generic exception handling in scanner.py
to improve coverage from 80.48% to 80.62% (+0.14%).
"""

import sys
import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner import scanner


@pytest.mark.unit
class TestScannerFileErrors(unittest.TestCase):
    """Test file error handling in scanner."""

    def test_file_not_found_error_plain_mode(self):
        """Test FileNotFoundError handling in plain mode (line 167)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use non-existent extensions directory
            nonexistent_dir = str(Path(tmpdir) / "nonexistent" / "extensions")

            # Run scan with non-existent directory
            result = scanner.run_scan(
                extensions_dir=nonexistent_dir,
                quiet=False,
                workers=1,
                no_cache=True,
            )

            # Should return error code 2
            self.assertEqual(result, 2)

    def test_generic_discovery_exception_plain_mode(self):
        """Test generic exception during discovery in plain mode (line 176)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_dir = str(Path(tmpdir) / "extensions")
            Path(extensions_dir).mkdir()

            # Mock _discover_extensions to raise generic exception
            with patch(
                "vscode_scanner.scanner._discover_extensions",
                side_effect=Exception("Generic discovery error"),
            ):
                # Run scan
                result = scanner.run_scan(
                    extensions_dir=extensions_dir,
                    quiet=False,
                    workers=1,
                    no_cache=True,
                )

            # Should return error code 2
            self.assertEqual(result, 2)

    def test_file_not_found_error_rich_mode(self):
        """Test FileNotFoundError handling in Rich mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use non-existent extensions directory
            nonexistent_dir = str(Path(tmpdir) / "nonexistent")

            # Run scan with Rich mode (default)
            result = scanner.run_scan(
                extensions_dir=nonexistent_dir,
                quiet=False,
                workers=1,
                no_cache=True,
            )

            # Should return error code 2
            self.assertEqual(result, 2)

    def test_generic_exception_rich_mode(self):
        """Test generic exception handling in Rich mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_dir = str(Path(tmpdir) / "extensions")
            Path(extensions_dir).mkdir()

            # Mock _discover_extensions to raise exception
            with patch(
                "vscode_scanner.scanner._discover_extensions",
                side_effect=RuntimeError("Discovery failed"),
            ):
                # Run scan with Rich mode
                result = scanner.run_scan(
                    extensions_dir=extensions_dir,
                    quiet=False,
                    workers=1,
                    no_cache=True,
                )

            # Should return error code 2
            self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
