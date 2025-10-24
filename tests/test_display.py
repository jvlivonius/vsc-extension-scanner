#!/usr/bin/env python3
"""
Unit tests for display.py module.

Tests Rich formatting components, table generation, and display logic.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner import display


class TestShouldUseRich(unittest.TestCase):
    """Test the should_use_rich() detection logic."""

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('sys.stdout.isatty')
    def test_use_rich_in_tty(self, mock_isatty):
        """Test that Rich is used in a TTY environment."""
        mock_isatty.return_value = True
        self.assertTrue(display.should_use_rich())

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('sys.stdout.isatty')
    def test_no_rich_when_not_tty(self, mock_isatty):
        """Test that Rich is disabled when stdout is not a TTY."""
        mock_isatty.return_value = False
        self.assertFalse(display.should_use_rich())

    @patch('vscode_scanner.display.RICH_AVAILABLE', False)
    def test_no_rich_when_not_available(self):
        """Test that Rich is disabled when not installed."""
        self.assertFalse(display.should_use_rich())

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('sys.stdout.isatty')
    def test_plain_flag_disables_rich(self, mock_isatty):
        """Test that --plain flag disables Rich."""
        mock_isatty.return_value = True
        self.assertFalse(display.should_use_rich(plain_flag=True))

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('sys.stdout.isatty')
    @patch.dict(os.environ, {'NO_COLOR': '1'})
    def test_no_color_env_disables_rich(self, mock_isatty):
        """Test that NO_COLOR environment variable disables Rich."""
        mock_isatty.return_value = True
        self.assertFalse(display.should_use_rich())

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('sys.stdout.isatty')
    @patch.dict(os.environ, {'CI': '1'})
    def test_ci_env_disables_rich(self, mock_isatty):
        """Test that CI environment disables Rich."""
        mock_isatty.return_value = True
        self.assertFalse(display.should_use_rich())

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('sys.stdout.isatty')
    @patch.dict(os.environ, {'TERM': 'dumb'})
    def test_dumb_terminal_disables_rich(self, mock_isatty):
        """Test that TERM=dumb disables Rich."""
        mock_isatty.return_value = True
        self.assertFalse(display.should_use_rich())


class TestTableGeneration(unittest.TestCase):
    """Test table generation functions."""

    def setUp(self):
        """Set up test data."""
        self.sample_results = [
            {
                'name': 'python',
                'display_name': 'Python',
                'version': '2024.10.0',
                'risk_level': 'low',
                'security_score': 95,
                'vulnerabilities': {'count': 0}
            },
            {
                'name': 'prettier',
                'display_name': 'Prettier',
                'version': '10.1.0',
                'risk_level': 'medium',
                'security_score': 82,
                'vulnerabilities': {'count': 0}
            },
            {
                'name': 'eslint',
                'display_name': 'ESLint',
                'version': '2.4.2',
                'risk_level': 'high',
                'security_score': 65,
                'vulnerabilities': {'count': 2}
            }
        ]

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_create_results_table(self):
        """Test creating results table with sample data."""
        table = display.create_results_table(self.sample_results)
        self.assertIsNotNone(table)
        # Verify table has correct number of columns
        self.assertEqual(len(table.columns), 4)

    @patch('vscode_scanner.display.RICH_AVAILABLE', False)
    def test_create_results_table_no_rich(self):
        """Test that table returns None when Rich is not available."""
        table = display.create_results_table(self.sample_results)
        self.assertIsNone(table)

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_create_results_table_with_limit(self):
        """Test table creation with result limiting."""
        # Create list with more than 10 items
        many_results = self.sample_results * 5  # 15 items
        table = display.create_results_table(many_results, show_all=False)
        self.assertIsNotNone(table)
        # Should show 10 + 1 "more" row = 11 rows total (plus header)
        self.assertEqual(len(table.rows), 11)

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_create_cache_stats_table(self):
        """Test creating cache statistics table."""
        stats = {
            'from_cache': 30,
            'fresh_scans': 12,
        }
        table = display.create_cache_stats_table(stats)
        self.assertIsNotNone(table)
        self.assertEqual(len(table.columns), 3)


class TestScanDashboard(unittest.TestCase):
    """Test the ScanDashboard class."""

    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        dashboard = display.ScanDashboard(total_extensions=42)
        self.assertEqual(dashboard.total, 42)
        self.assertEqual(dashboard.current, 0)
        self.assertEqual(dashboard.clean_count, 0)

    def test_dashboard_update(self):
        """Test dashboard state updates."""
        dashboard = display.ScanDashboard(total_extensions=42)

        dashboard.update(
            current=10,
            current_extension="ms-python.python",
            clean_count=8,
            issues_count=2
        )

        self.assertEqual(dashboard.current, 10)
        self.assertEqual(dashboard.current_extension, "ms-python.python")
        self.assertEqual(dashboard.clean_count, 8)
        self.assertEqual(dashboard.issues_count, 2)

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_dashboard_generate_panel(self):
        """Test dashboard panel generation."""
        dashboard = display.ScanDashboard(total_extensions=10)
        dashboard.update(
            current=5,
            current_extension="test.extension",
            clean_count=4,
            issues_count=1
        )

        panel = dashboard.generate_panel()
        self.assertIsNotNone(panel)

    @patch('vscode_scanner.display.RICH_AVAILABLE', False)
    def test_dashboard_no_rich(self):
        """Test dashboard returns None when Rich not available."""
        dashboard = display.ScanDashboard(total_extensions=10)
        panel = dashboard.generate_panel()
        self.assertIsNone(panel)


class TestDisplayFunctions(unittest.TestCase):
    """Test display helper functions."""

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('vscode_scanner.display.Console')
    def test_display_success(self, mock_console_class):
        """Test display_success with Rich."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console

        display.display_success("Test message", use_rich=True)
        mock_console.print.assert_called_once()

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('vscode_scanner.display.Console')
    def test_display_error(self, mock_console_class):
        """Test display_error with Rich."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console

        display.display_error("Test error", use_rich=True)
        mock_console.print.assert_called_once()

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    @patch('vscode_scanner.display.Console')
    def test_display_warning(self, mock_console_class):
        """Test display_warning with Rich."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console

        display.display_warning("Test warning", use_rich=True)
        mock_console.print.assert_called_once()

    @patch('builtins.print')
    def test_display_success_plain(self, mock_print):
        """Test display_success in plain mode."""
        display.display_success("Test message", use_rich=False)
        mock_print.assert_called_once()
        args = mock_print.call_args[0]
        self.assertIn("Test message", args[0])


class TestProgressBar(unittest.TestCase):
    """Test progress bar creation."""

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_create_scan_progress(self):
        """Test creating scan progress bar."""
        progress = display.create_scan_progress(verbose=False)
        self.assertIsNotNone(progress)

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_create_scan_progress_verbose(self):
        """Test creating verbose progress bar."""
        progress = display.create_scan_progress(verbose=True)
        self.assertIsNotNone(progress)
        # Verbose mode should have more columns

    @patch('vscode_scanner.display.RICH_AVAILABLE', False)
    def test_create_scan_progress_no_rich(self):
        """Test progress returns None when Rich not available."""
        progress = display.create_scan_progress()
        self.assertIsNone(progress)


class TestFilterSummary(unittest.TestCase):
    """Test filter summary table generation."""

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_create_filter_summary_with_filters(self):
        """Test creating filter summary when filters are active."""
        # Create a mock args object
        class Args:
            publisher = "microsoft"
            include_ids = None
            exclude_ids = None
            min_risk_level = "high"

        table = display.create_filter_summary_table(Args(), 100, 25)
        self.assertIsNotNone(table)

    @patch('vscode_scanner.display.RICH_AVAILABLE', True)
    def test_create_filter_summary_no_filters(self):
        """Test creating filter summary when no filters are active."""
        class Args:
            publisher = None
            include_ids = None
            exclude_ids = None
            min_risk_level = None

        table = display.create_filter_summary_table(Args(), 100, 100)
        self.assertIsNone(table)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestShouldUseRich))
    suite.addTests(loader.loadTestsFromTestCase(TestTableGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestScanDashboard))
    suite.addTests(loader.loadTestsFromTestCase(TestDisplayFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestProgressBar))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterSummary))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
