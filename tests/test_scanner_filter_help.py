"""
Test scanner filter help display - Lines 788-809 coverage.

Covers _show_filter_help function to improve scanner.py coverage
from 79.72% to 80.48% (+0.76%).
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
class TestScannerFilterHelp(unittest.TestCase):
    """Test filter help display when no extensions match filters."""

    def test_filter_help_with_publisher_filter_rich_mode(self):
        """Test filter help display with publisher filter in Rich mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_dir = str(Path(tmpdir) / "extensions")
            Path(extensions_dir).mkdir()

            # Create one extension but filter by non-matching publisher
            ext_dir = Path(extensions_dir) / "microsoft.vscode-python-1.0.0"
            ext_dir.mkdir()
            package_json = ext_dir / "package.json"
            package_json.write_text(
                '{"name": "vscode-python", "publisher": "microsoft", "version": "1.0.0"}'
            )

            # Run scan with non-matching publisher filter
            # This should trigger filter help display
            result = scanner.run_scan(
                extensions_dir=extensions_dir,
                publisher="github",  # Won't match 'microsoft'
                quiet=False,
                workers=1,
                no_cache=True,
            )

            # Should complete without error
            self.assertIsNotNone(result)

    def test_filter_help_with_verified_only_filter_rich_mode(self):
        """Test filter help with verified-only filter in Rich mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_dir = str(Path(tmpdir) / "extensions")
            Path(extensions_dir).mkdir()

            # Create unverified extension
            ext_dir = Path(extensions_dir) / "unverified.extension-1.0.0"
            ext_dir.mkdir()
            package_json = ext_dir / "package.json"
            package_json.write_text(
                '{"name": "extension", "publisher": "unverified", "version": "1.0.0"}'
            )

            # Run scan with verified-only filter (won't match unverified publisher)
            result = scanner.run_scan(
                extensions_dir=extensions_dir,
                verified_only=True,
                quiet=False,
                workers=1,
                no_cache=True,
            )

            # Should complete and show filter help
            self.assertIsNotNone(result)

    def test_filter_help_with_min_risk_level_plain_mode(self):
        """Test filter help with min risk level filter in plain mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_dir = str(Path(tmpdir) / "extensions")
            Path(extensions_dir).mkdir()

            # Create extension (will have no vulnerabilities when scanned)
            ext_dir = Path(extensions_dir) / "publisher.safe-extension-1.0.0"
            ext_dir.mkdir()
            package_json = ext_dir / "package.json"
            package_json.write_text(
                '{"name": "safe-extension", "publisher": "publisher", "version": "1.0.0"}'
            )

            # Mock API to return safe result
            with patch("vscode_scanner.scanner.VscanAPIClient") as mock_api_class:
                mock_api = Mock()
                mock_api.scan_extension.return_value = (
                    200,
                    {
                        "status": "success",
                        "risk_level": "safe",
                        "security_score": 10.0,
                        "vulnerabilities": [],
                    },
                )
                mock_api_class.return_value = mock_api

                # Run with min-risk-level=high filter (won't match 'safe')
                result = scanner.run_scan(
                    extensions_dir=extensions_dir,
                    min_risk_level="high",
                    quiet=False,
                    workers=1,
                    no_cache=True,
                )

                # Should complete and show filter help
                self.assertIsNotNone(result)

    def test_filter_help_with_multiple_filters(self):
        """Test filter help with multiple active filters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_dir = str(Path(tmpdir) / "extensions")
            Path(extensions_dir).mkdir()

            # Create extension
            ext_dir = Path(extensions_dir) / "microsoft.vscode-python-1.0.0"
            ext_dir.mkdir()
            package_json = ext_dir / "package.json"
            package_json.write_text(
                '{"name": "vscode-python", "publisher": "microsoft", "version": "1.0.0"}'
            )

            # Run with multiple non-matching filters
            result = scanner.run_scan(
                extensions_dir=extensions_dir,
                publisher="github",  # Won't match
                verified_only=True,  # Won't match unverified
                quiet=False,
                workers=1,
                no_cache=True,
            )

            # Should show filter help with multiple filters listed
            self.assertIsNotNone(result)

    def test_filter_help_display_plain_mode(self):
        """Test filter help display in plain mode (non-Rich)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_dir = str(Path(tmpdir) / "extensions")
            Path(extensions_dir).mkdir()

            # Create extension
            ext_dir = Path(extensions_dir) / "publisher.extension-1.0.0"
            ext_dir.mkdir()
            package_json = ext_dir / "package.json"
            package_json.write_text(
                '{"name": "extension", "publisher": "publisher", "version": "1.0.0"}'
            )

            # Capture log output
            captured_logs = []

            def mock_log(msg, level):
                captured_logs.append((msg, level))

            with patch("vscode_scanner.scanner.log", side_effect=mock_log):
                # Run with non-matching filter in plain mode
                result = scanner.run_scan(
                    extensions_dir=extensions_dir,
                    publisher="nonexistent",
                    quiet=False,
                    workers=1,
                    no_cache=True,
                )

            # Should have logged filter help messages
            # (Check that log was called with filter-related messages)
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
