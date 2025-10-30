#!/usr/bin/env python3
"""
Test Suite: Cache Command Tests
Purpose: Test cache stats and clear command functionality
Coverage: vscode_scanner.cli cache commands (cache stats, cache clear)

This test suite validates cache command operations including:
- Cache statistics display
- Cache clearing with confirmation
- Parameter validation
- Error handling
- Rich vs plain output modes

Mocking Strategy:
- Mock CacheManager to avoid filesystem operations
- Mock typer.confirm for confirmation prompt testing
- Use temporary directories for path validation
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Check if typer is available
try:
    import typer
    from typer.testing import CliRunner

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False

if TYPER_AVAILABLE:
    from vscode_scanner import cli


# ============================================================
# Cache Stats Command Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestCacheStatsCommand(unittest.TestCase):
    """Test suite for 'cache stats' command.

    **Purpose:** Ensure cache statistics display works correctly
    with various parameters and error conditions.

    **Scope:**
    - Display cache statistics
    - Parameter validation (cache_max_age)
    - Custom cache directory handling
    - Rich vs plain output modes
    - Error handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

        # Mock cache statistics data
        self.mock_stats = {
            "total_entries": 10,
            "total_size": 1024000,
            "stale_entries": 2,
            "risk_distribution": {"low": 5, "medium": 3, "high": 2},
            "extensions_with_vulns": 3,
        }

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.cli.CacheManager")
    def test_stats_displays_cache_information(self, mock_cache_manager_class):
        """Test that cache stats displays cache information."""
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.get_cache_stats.return_value = self.mock_stats
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "stats", "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg=f"Should succeed. Output: {result.stdout}"
        )
        mock_instance.get_cache_stats.assert_called_once()

    @patch("vscode_scanner.cli.CacheManager")
    def test_stats_with_custom_max_age(self, mock_cache_manager_class):
        """Test cache stats with custom max_age parameter."""
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.get_cache_stats.return_value = self.mock_stats
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-max-age", "14", "--plain"]
        )

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should accept valid max_age")
        mock_instance.get_cache_stats.assert_called_with(max_age_days=14)

    @patch("vscode_scanner.cli.CacheManager")
    def test_stats_with_custom_cache_dir(self, mock_cache_manager_class):
        """Test cache stats with custom cache directory."""
        # Arrange
        custom_dir = os.path.join(self.temp_dir, "custom_cache")
        os.makedirs(custom_dir)

        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.get_cache_stats.return_value = self.mock_stats
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-dir", custom_dir, "--plain"]
        )

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg="Should accept valid custom cache directory"
        )
        # Verify CacheManager was initialized with custom directory
        call_args = mock_cache_manager_class.call_args
        self.assertIsNotNone(call_args[1].get("cache_dir"))

    def test_stats_invalid_max_age_below_minimum(self):
        """Test that cache-max-age below 1 is rejected."""
        # Act
        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-max-age", "0", "--plain"]
        )

        # Assert
        self.assertEqual(result.exit_code, 2, msg="Should reject max_age below minimum")
        # Error messages may appear in stdout or stderr
        combined_output = result.output.lower()
        self.assertTrue(
            "must be between" in combined_output or "invalid value" in combined_output,
            msg=f"Should show validation error. Output: {combined_output}",
        )

    def test_stats_invalid_max_age_above_maximum(self):
        """Test that cache-max-age above 365 is rejected."""
        # Act
        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-max-age", "400", "--plain"]
        )

        # Assert
        self.assertEqual(result.exit_code, 2, msg="Should reject max_age above maximum")
        # Error messages may appear in stdout or stderr
        combined_output = result.output.lower()
        self.assertTrue(
            "must be between" in combined_output or "invalid value" in combined_output,
            msg=f"Should show validation error. Output: {combined_output}",
        )

    def test_stats_with_invalid_cache_dir_path(self):
        """Test that invalid cache directory paths are rejected."""
        # Act
        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-dir", "../../../etc/passwd", "--plain"]
        )

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should reject path traversal attempts"
        )

    @patch("vscode_scanner.cli.CacheManager")
    def test_stats_with_plain_flag(self, mock_cache_manager_class):
        """Test that --plain flag disables rich formatting."""
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.get_cache_stats.return_value = self.mock_stats
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "stats", "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed with plain output")
        # Plain output should not contain ANSI escape codes
        self.assertNotIn(
            "\x1b[", result.stdout, msg="Plain output should not have ANSI codes"
        )

    @patch("vscode_scanner.cli.CacheManager")
    def test_stats_handles_cache_manager_errors(self, mock_cache_manager_class):
        """Test that cache manager errors are handled gracefully."""
        # Arrange
        mock_cache_manager_class.side_effect = Exception("Database error")

        # Act
        result = self.runner.invoke(cli.app, ["cache", "stats", "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should exit with error code on exception"
        )
        # Error messages may appear in stdout or stderr
        combined_output = result.output.lower()
        self.assertTrue(
            "error" in combined_output or len(combined_output) > 0,
            msg=f"Should show error message. Output: {combined_output}",
        )

    @patch("vscode_scanner.cli.CacheManager")
    def test_stats_displays_cache_warnings(self, mock_cache_manager_class):
        """Test that cache initialization warnings are displayed."""
        # Arrange
        from vscode_scanner.types import CacheWarning

        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = [
            CacheWarning(message="Cache rebuild required", context="test")
        ]
        mock_instance.get_cache_stats.return_value = self.mock_stats
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "stats", "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed despite warnings")
        self.assertIn("warning", result.stdout.lower())


# ============================================================
# Cache Clear Command Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestCacheClearCommand(unittest.TestCase):
    """Test suite for 'cache clear' command.

    **Purpose:** Ensure cache clearing works correctly with
    confirmation prompts and force options.

    **Scope:**
    - Clear cache with confirmation
    - Force clear without confirmation
    - Custom cache directory handling
    - User cancellation
    - Error handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.cli.CacheManager")
    @patch("vscode_scanner.cli.typer.confirm")
    def test_clear_with_confirmation_confirmed(
        self, mock_confirm, mock_cache_manager_class
    ):
        """Test cache clear with user confirmation."""
        # Arrange
        mock_confirm.return_value = True
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.clear_cache.return_value = 10
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "clear", "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed when confirmed")
        mock_confirm.assert_called_once()
        mock_instance.clear_cache.assert_called_once()
        self.assertIn("cleared", result.stdout.lower())

    @patch("vscode_scanner.cli.CacheManager")
    @patch("vscode_scanner.cli.typer.confirm")
    def test_clear_with_confirmation_cancelled(
        self, mock_confirm, mock_cache_manager_class
    ):
        """Test cache clear when user cancels confirmation."""
        # Arrange
        mock_confirm.return_value = False
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "clear", "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 1, msg="Should exit with code 1 when cancelled"
        )
        mock_confirm.assert_called_once()
        mock_instance.clear_cache.assert_not_called()
        self.assertIn("cancelled", result.stdout.lower())

    @patch("vscode_scanner.cli.CacheManager")
    def test_clear_with_force_flag(self, mock_cache_manager_class):
        """Test cache clear with --force flag skips confirmation."""
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.clear_cache.return_value = 10
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "clear", "--force", "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed without confirmation")
        mock_instance.clear_cache.assert_called_once()
        self.assertIn("cleared", result.stdout.lower())

    @patch("vscode_scanner.cli.CacheManager")
    def test_clear_with_force_shorthand(self, mock_cache_manager_class):
        """Test cache clear with -f shorthand for force."""
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.clear_cache.return_value = 10
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "clear", "-f", "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should accept -f shorthand")
        mock_instance.clear_cache.assert_called_once()

    @patch("vscode_scanner.cli.CacheManager")
    def test_clear_with_custom_cache_dir(self, mock_cache_manager_class):
        """Test cache clear with custom cache directory."""
        # Arrange
        custom_dir = os.path.join(self.temp_dir, "custom_cache")
        os.makedirs(custom_dir)

        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.clear_cache.return_value = 10
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(
            cli.app, ["cache", "clear", "--force", "--cache-dir", custom_dir, "--plain"]
        )

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg="Should accept valid custom cache directory"
        )
        # Verify CacheManager was initialized with custom directory
        call_args = mock_cache_manager_class.call_args
        self.assertIsNotNone(call_args[1].get("cache_dir"))

    def test_clear_with_invalid_cache_dir_path(self):
        """Test that invalid cache directory paths are rejected."""
        # Act
        result = self.runner.invoke(
            cli.app,
            [
                "cache",
                "clear",
                "--force",
                "--cache-dir",
                "../../../etc/passwd",
                "--plain",
            ],
        )

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should reject path traversal attempts"
        )

    @patch("vscode_scanner.cli.CacheManager")
    def test_clear_displays_entry_count(self, mock_cache_manager_class):
        """Test that clear displays number of entries cleared."""
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = []
        mock_instance.clear_cache.return_value = 42
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "clear", "--force", "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed")
        self.assertIn("42", result.stdout, msg="Should display entry count")

    @patch("vscode_scanner.cli.CacheManager")
    def test_clear_handles_cache_manager_errors(self, mock_cache_manager_class):
        """Test that cache manager errors are handled gracefully."""
        # Arrange
        mock_cache_manager_class.side_effect = Exception("Database locked")

        # Act
        result = self.runner.invoke(cli.app, ["cache", "clear", "--force", "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should exit with error code on exception"
        )
        # Error messages may appear in stdout or stderr
        combined_output = result.output.lower()
        self.assertTrue(
            "error" in combined_output or len(combined_output) > 0,
            msg=f"Should show error message. Output: {combined_output}",
        )

    @patch("vscode_scanner.cli.CacheManager")
    def test_clear_displays_cache_warnings(self, mock_cache_manager_class):
        """Test that cache initialization warnings are displayed."""
        # Arrange
        from vscode_scanner.types import CacheWarning

        mock_instance = MagicMock()
        mock_instance.get_init_messages.return_value = [
            CacheWarning(message="Cache rebuild required", context="test")
        ]
        mock_instance.clear_cache.return_value = 10
        mock_cache_manager_class.return_value = mock_instance

        # Act
        result = self.runner.invoke(cli.app, ["cache", "clear", "--force", "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed despite warnings")
        self.assertIn("warning", result.stdout.lower())


# ============================================================
# Test Runner
# ============================================================


def run_tests():
    """Run the test suite and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCacheStatsCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheClearCommand))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Cache Command Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_tests())
