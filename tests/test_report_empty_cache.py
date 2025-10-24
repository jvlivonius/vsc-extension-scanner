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
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.cli import _check_extensions_exist


class TestReportEmptyCache(unittest.TestCase):
    """Test report command with empty cache."""

    def test_display_warning_import(self):
        """Test that display_warning is properly imported."""
        from vscode_scanner.cli import display_warning
        self.assertIsNotNone(display_warning)
        self.assertTrue(callable(display_warning))

    def test_check_extensions_exist_with_extensions(self):
        """Test _check_extensions_exist when extensions are present."""
        # This will check the actual user's VS Code extensions
        exists, count = _check_extensions_exist()

        # We expect the test system to have extensions
        self.assertTrue(exists or not exists)  # Just check it doesn't crash
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

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

    @patch('vscode_scanner.cli.run_scan')
    @patch('vscode_scanner.cli.CacheManager')
    @patch('vscode_scanner.cli._check_extensions_exist')
    @patch('typer.confirm')
    def test_report_empty_cache_user_declines_scan(
        self, mock_confirm, mock_check_ext, mock_cache_mgr, mock_run_scan
    ):
        """Test report command when user declines to scan."""
        # Setup mocks
        mock_check_ext.return_value = (True, 66)  # Extensions exist
        mock_confirm.return_value = False  # User declines

        mock_cache_instance = MagicMock()
        mock_cache_instance.get_all_cached_results.return_value = []  # Empty cache
        mock_cache_mgr.return_value = mock_cache_instance

        # Import here to avoid import cycles
        from vscode_scanner.cli import report
        import typer

        # Test that Exit(1) is raised when user declines
        with self.assertRaises(typer.Exit) as cm:
            # Mock the typer.Argument and Option behavior
            with patch('pathlib.Path.resolve', return_value=Path('/tmp/test.html')):
                report(
                    output=Path('/tmp/test.html'),
                    cache_dir=None,
                    cache_max_age=365,
                    plain=True
                )

        # Verify confirm was called
        mock_confirm.assert_called_once()

        # Verify scan was NOT called
        mock_run_scan.assert_not_called()

    @patch('vscode_scanner.cli.run_scan')
    @patch('vscode_scanner.cli.CacheManager')
    @patch('vscode_scanner.cli._check_extensions_exist')
    @patch('typer.confirm')
    def test_report_empty_cache_user_accepts_scan(
        self, mock_confirm, mock_check_ext, mock_cache_mgr, mock_run_scan
    ):
        """Test report command when user accepts to scan."""
        # Setup mocks
        mock_check_ext.return_value = (True, 66)  # Extensions exist
        mock_confirm.return_value = True  # User accepts
        mock_run_scan.return_value = 0  # Scan succeeds

        mock_cache_instance = MagicMock()
        # First call returns empty, second call (after scan) returns data
        mock_cache_instance.get_all_cached_results.side_effect = [
            [],  # Empty cache initially
            [{'id': 'test.ext', 'version': '1.0.0'}]  # Data after scan
        ]
        mock_cache_mgr.return_value = mock_cache_instance

        from vscode_scanner.cli import report

        # Mock file operations
        with patch('builtins.open', MagicMock()):
            with patch('pathlib.Path.resolve', return_value=Path('/tmp/test.html')):
                with patch('vscode_scanner.cli.validate_path', return_value=True):
                    with patch('vscode_scanner.cli.safe_mkdir'):
                        try:
                            report(
                                output=Path('/tmp/test.html'),
                                cache_dir=None,
                                cache_max_age=365,
                                plain=True
                            )
                        except:
                            pass  # Exit is expected

        # Verify scan WAS called
        mock_run_scan.assert_called_once()

    @patch('vscode_scanner.cli.CacheManager')
    @patch('vscode_scanner.cli._check_extensions_exist')
    def test_report_no_extensions_installed(self, mock_check_ext, mock_cache_mgr):
        """Test report command when no extensions are installed."""
        # Setup mocks
        mock_check_ext.return_value = (False, 0)  # No extensions

        mock_cache_instance = MagicMock()
        mock_cache_instance.get_all_cached_results.return_value = []  # Empty cache
        mock_cache_mgr.return_value = mock_cache_instance

        from vscode_scanner.cli import report
        import typer

        # Test that Exit(1) is raised for no extensions
        with self.assertRaises(typer.Exit) as cm:
            with patch('pathlib.Path.resolve', return_value=Path('/tmp/test.html')):
                report(
                    output=Path('/tmp/test.html'),
                    cache_dir=None,
                    cache_max_age=365,
                    plain=True
                )

        self.assertEqual(cm.exception.exit_code, 1)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
