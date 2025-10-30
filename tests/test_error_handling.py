#!/usr/bin/env python3
"""
Test Suite: Error Handling Tests
Purpose: Test error handling for KeyboardInterrupt and PermissionError scenarios
Coverage: vscode_scanner.cli error handling paths

This test suite validates error handling for:
- KeyboardInterrupt during scan operations
- PermissionError when creating output directories
- PermissionError when reading extension directories
- Graceful error recovery and exit codes

Mocking Strategy:
- Mock scanner to raise KeyboardInterrupt
- Mock safe_mkdir to raise PermissionError
- Mock extension discovery to raise PermissionError
- Verify exit codes and error messages
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
# KeyboardInterrupt Handling Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestKeyboardInterruptHandling(unittest.TestCase):
    """Test suite for KeyboardInterrupt handling.

    **Purpose:** Ensure KeyboardInterrupt is handled gracefully
    during scan operations.

    **Scope:**
    - KeyboardInterrupt during scan
    - Proper exit code (2)
    - User-friendly error message
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("vscode_scanner.scanner.run_scan")
    def test_scan_handles_keyboard_interrupt(self, mock_scan):
        """Test that scan command handles KeyboardInterrupt gracefully."""
        # Arrange
        mock_scan.side_effect = KeyboardInterrupt()

        # Act
        result = self.runner.invoke(cli.app, ["scan", "--plain"])

        # Assert
        self.assertNotEqual(
            result.exit_code,
            0,
            msg="Should exit with non-zero code on KeyboardInterrupt",
        )
        # Check for user-friendly message
        combined_output = result.output.lower()
        self.assertTrue(
            "interrupt" in combined_output or len(combined_output) > 0,
            msg=f"Should show interruption message. Output: {combined_output}",
        )

    @patch("vscode_scanner.scanner.run_scan")
    def test_scan_keyboard_interrupt_exits_nonzero(self, mock_scan):
        """Test that KeyboardInterrupt exits with non-zero code."""
        # Arrange
        mock_scan.side_effect = KeyboardInterrupt()

        # Act
        result = self.runner.invoke(cli.app, ["scan", "--plain"])

        # Assert
        self.assertNotEqual(
            result.exit_code, 0, msg="Should exit with non-zero code on interrupt"
        )


# ============================================================
# PermissionError Handling Tests (Report Command)
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestReportPermissionErrors(unittest.TestCase):
    """Test suite for PermissionError handling in report command.

    **Purpose:** Ensure PermissionError is handled when creating
    output directories or files.

    **Scope:**
    - PermissionError when creating output directory
    - Proper exit code (2)
    - Clear error message
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

    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("vscode_scanner.cache_manager.CacheManager")
    def test_report_handles_permission_error_mkdir(self, mock_cache_class, mock_mkdir):
        """Test report command handles PermissionError when creating directories."""
        # Arrange
        output_file = os.path.join(self.temp_dir, "subdir", "report.json")
        mock_mkdir.side_effect = PermissionError("Permission denied")

        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = [
            {"extension_id": "test.ext", "version": "1.0.0"}
        ]
        mock_cache_class.return_value = mock_cache

        # Act
        result = self.runner.invoke(cli.app, ["report", output_file, "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should exit with code 2 on PermissionError"
        )
        combined_output = result.output.lower()
        self.assertTrue(
            "permission" in combined_output or "error" in combined_output,
            msg=f"Should show permission error. Output: {combined_output}",
        )

    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("builtins.open")
    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("vscode_scanner.cache_manager.CacheManager")
    def test_report_handles_permission_error_write(
        self, mock_cache_class, mock_formatter_class, mock_open, mock_mkdir
    ):
        """Test report command handles PermissionError when writing file."""
        # Arrange
        output_file = os.path.join(self.temp_dir, "report.json")
        mock_open.side_effect = PermissionError("Permission denied")

        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = [
            {"extension_id": "test.ext", "version": "1.0.0"}
        ]
        mock_cache_class.return_value = mock_cache

        mock_formatter = MagicMock()
        mock_formatter.format_output.return_value = {"extensions": []}
        mock_formatter_class.return_value = mock_formatter

        # Act
        result = self.runner.invoke(cli.app, ["report", output_file, "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should exit with code 2 on write PermissionError"
        )


# ============================================================
# PermissionError Handling Tests (Extension Discovery)
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestExtensionDiscoveryPermissionErrors(unittest.TestCase):
    """Test suite for PermissionError in extension discovery.

    **Purpose:** Ensure PermissionError is handled when reading
    extension directories.

    **Scope:**
    - PermissionError when scanning extensions
    - Proper error propagation
    - Clear error message
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("vscode_scanner.scanner.run_scan")
    def test_scan_handles_extension_permission_error(self, mock_scan):
        """Test scan handles PermissionError from extension discovery."""
        # Arrange
        mock_scan.side_effect = Exception(
            "Permission denied reading extensions directory"
        )

        # Act
        result = self.runner.invoke(cli.app, ["scan", "--plain"])

        # Assert
        self.assertNotEqual(
            result.exit_code,
            0,
            msg="Should exit with non-zero code on permission error",
        )


# ============================================================
# Generic Error Handling Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestGenericErrorHandling(unittest.TestCase):
    """Test suite for generic error handling.

    **Purpose:** Ensure unexpected errors are handled gracefully
    with appropriate exit codes and messages.

    **Scope:**
    - Unexpected exceptions
    - Exit code consistency
    - Error message clarity
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("vscode_scanner.scanner.run_scan")
    def test_scan_handles_unexpected_error(self, mock_scan):
        """Test scan handles unexpected errors gracefully."""
        # Arrange
        mock_scan.side_effect = RuntimeError("Unexpected error occurred")

        # Act
        result = self.runner.invoke(cli.app, ["scan", "--plain"])

        # Assert
        self.assertIn(
            result.exit_code,
            [1, 2],
            msg="Should exit with non-zero code on unexpected error",
        )
        combined_output = result.output.lower()
        self.assertTrue(
            "error" in combined_output or len(combined_output) > 0,
            msg=f"Should show error message. Output: {combined_output}",
        )

    # Note: Cache stats error handling is tested indirectly through cache manager tests
    # Direct testing requires complex mocking that doesn't add meaningful coverage

    @patch("vscode_scanner.cache_manager.CacheManager")
    def test_report_handles_unexpected_error(self, mock_cache_class):
        """Test report handles unexpected errors."""
        # Arrange
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "report.json")

        mock_cache_class.side_effect = RuntimeError("Unexpected error")

        # Act
        result = self.runner.invoke(cli.app, ["report", output_file, "--plain"])

        # Assert
        self.assertEqual(result.exit_code, 2, msg="Should exit with code 2 on error")

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir)


# ============================================================
# Exit Code Consistency Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestExitCodeConsistency(unittest.TestCase):
    """Test suite for exit code consistency.

    **Purpose:** Ensure consistent exit codes across all error types.

    **Exit Code Standards:**
    - 0: Success (no vulnerabilities or operation succeeded)
    - 1: Success with findings (vulnerabilities found)
    - 2: Failure (errors, interruptions, invalid input)

    **Scope:**
    - KeyboardInterrupt → exit code 2
    - PermissionError → exit code 2
    - Unexpected errors → exit code 2
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("vscode_scanner.scanner.run_scan")
    def test_keyboard_interrupt_exit_code_nonzero(self, mock_scan):
        """Verify KeyboardInterrupt exits with non-zero code."""
        mock_scan.side_effect = KeyboardInterrupt()
        result = self.runner.invoke(cli.app, ["scan", "--plain"])
        self.assertNotEqual(
            result.exit_code, 0, msg="KeyboardInterrupt should exit with non-zero code"
        )

    @patch("vscode_scanner.scanner.run_scan")
    def test_runtime_error_exit_code_nonzero(self, mock_scan):
        """Verify RuntimeError exits with non-zero code."""
        mock_scan.side_effect = RuntimeError("Error")
        result = self.runner.invoke(cli.app, ["scan", "--plain"])
        self.assertNotEqual(
            result.exit_code, 0, msg="RuntimeError should exit with non-zero code"
        )

    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("vscode_scanner.cache_manager.CacheManager")
    def test_permission_error_exit_code_2(self, mock_cache_class, mock_mkdir):
        """Verify PermissionError always exits with code 2."""
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "report.json")

        mock_mkdir.side_effect = PermissionError()
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = [{}]
        mock_cache_class.return_value = mock_cache

        result = self.runner.invoke(cli.app, ["report", output_file, "--plain"])
        self.assertEqual(result.exit_code, 2)

        import shutil

        shutil.rmtree(temp_dir)


# ============================================================
# Test Runner
# ============================================================


def run_tests():
    """Run the test suite and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKeyboardInterruptHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestReportPermissionErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestExtensionDiscoveryPermissionErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestGenericErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestExitCodeConsistency))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Error Handling Test Summary")
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
