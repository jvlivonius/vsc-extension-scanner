"""
CLI Coverage Boost Tests - Phase 2.

Focused tests to increase CLI coverage from 57.58% to 80%.
Targets specific uncovered lines identified in coverage analysis.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if Typer CLI testing is available
TYPER_AVAILABLE = True
try:
    from typer.testing import CliRunner
    import typer
    import pytest
    from vscode_scanner import cli
except ImportError:
    TYPER_AVAILABLE = False


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestBoundedValidators(unittest.TestCase):
    """Test bounded_int_validator and bounded_float_validator functions."""

    def test_bounded_int_validator_valid_value(self):
        """Test bounded_int_validator accepts valid integer."""
        result = cli.bounded_int_validator(5, min_val=1, max_val=10, name="test")
        self.assertEqual(result, 5)

    def test_bounded_int_validator_below_min(self):
        """Test bounded_int_validator rejects value below minimum."""
        with self.assertRaises(typer.BadParameter) as context:
            cli.bounded_int_validator(0, min_val=1, max_val=10, name="test-param")
        self.assertIn("must be between 1 and 10", str(context.exception))

    def test_bounded_int_validator_above_max(self):
        """Test bounded_int_validator rejects value above maximum."""
        with self.assertRaises(typer.BadParameter) as context:
            cli.bounded_int_validator(11, min_val=1, max_val=10, name="test-param")
        self.assertIn("must be between 1 and 10", str(context.exception))

    def test_bounded_float_validator_valid_value(self):
        """Test bounded_float_validator accepts valid float."""
        result = cli.bounded_float_validator(
            5.5, min_val=1.0, max_val=10.0, name="test"
        )
        self.assertEqual(result, 5.5)

    def test_bounded_float_validator_below_min(self):
        """Test bounded_float_validator rejects value below minimum."""
        with self.assertRaises(typer.BadParameter) as context:
            cli.bounded_float_validator(
                0.5, min_val=1.0, max_val=10.0, name="test-param"
            )
        self.assertIn("must be between 1.0 and 10.0", str(context.exception))

    def test_bounded_float_validator_above_max(self):
        """Test bounded_float_validator rejects value above maximum."""
        with self.assertRaises(typer.BadParameter) as context:
            cli.bounded_float_validator(
                11.0, min_val=1.0, max_val=10.0, name="test-param"
            )
        self.assertIn("must be between 1.0 and 10.0", str(context.exception))


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestReportCommandErrors(unittest.TestCase):
    """Test report command error handling for file operations."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_report_json_write_error(
        self,
        mock_open_file,
        mock_safe_mkdir,
        mock_cache_manager_class,
        mock_formatter_class,
    ):
        """Test report command handles JSON file write errors."""
        # Configure mock_open to raise error on write
        mock_file_handle = mock_open_file.return_value.__enter__.return_value
        mock_file_handle.write.side_effect = IOError("Disk full")

        # Mock CacheManager
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.get_all_cached_results.return_value = [
            {"extension_id": "test.ext", "risk_level": "low"}
        ]

        # Mock OutputFormatter
        mock_formatter = MagicMock()
        mock_formatter_class.return_value = mock_formatter
        mock_formatter.format_output.return_value = {
            "extensions": [{"extension_id": "test.ext", "risk_level": "low"}]
        }

        result = self.runner.invoke(cli.app, ["report", "report.json"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestScanCommandConflictingFilters(unittest.TestCase):
    """Test scan command rejects conflicting filter flags."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_scan_verified_and_unverified_conflict(self):
        """Test scan command rejects both --verified-only and --unverified-only."""
        result = self.runner.invoke(
            cli.app, ["scan", "--verified-only", "--unverified-only"]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "Cannot use --verified-only and --unverified-only together", result.output
        )

    def test_scan_with_and_without_vulnerabilities_conflict(self):
        """Test scan command rejects both --with-vulnerabilities and --without-vulnerabilities."""
        result = self.runner.invoke(
            cli.app, ["scan", "--with-vulnerabilities", "--without-vulnerabilities"]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "Cannot use --with-vulnerabilities and --without-vulnerabilities",
            result.output,
        )


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestScanCommandPathValidation(unittest.TestCase):
    """Test scan command path validation for output, extensions-dir, cache-dir."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch(
        "vscode_scanner.cli.validate_path",
        side_effect=ValueError("Invalid output path"),
    )
    def test_scan_invalid_output_path(self, mock_validate):
        """Test scan command rejects invalid output path."""
        result = self.runner.invoke(
            cli.app, ["scan", "--output", "../../../etc/passwd"]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)
        self.assertIn("Invalid output path", result.output)

    @patch("vscode_scanner.cli.validate_path")
    def test_scan_invalid_extensions_dir_path(self, mock_validate):
        """Test scan command rejects invalid extensions directory path."""

        # Make validate_path fail only for extensions-dir call
        def validate_side_effect(path, allow_absolute=True, path_type=""):
            if path_type == "extensions directory":
                raise ValueError("Invalid extensions directory")
            return path

        mock_validate.side_effect = validate_side_effect

        result = self.runner.invoke(
            cli.app, ["scan", "--extensions-dir", "/invalid/path"]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)
        self.assertIn("Invalid extensions directory", result.output)

    @patch("vscode_scanner.cli.validate_path")
    def test_scan_invalid_cache_dir_path(self, mock_validate):
        """Test scan command rejects invalid cache directory path."""

        # Make validate_path fail only for cache-dir call
        def validate_side_effect(path, allow_absolute=True, path_type=""):
            if path_type == "cache directory":
                raise ValueError("Invalid cache directory")
            return path

        mock_validate.side_effect = validate_side_effect

        result = self.runner.invoke(cli.app, ["scan", "--cache-dir", "/invalid/path"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)
        self.assertIn("Invalid cache directory", result.output)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestScanCommandExceptionHandling(unittest.TestCase):
    """Test scan command exception handling (KeyboardInterrupt, unexpected errors)."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.cli.run_scan", side_effect=KeyboardInterrupt())
    def test_scan_keyboard_interrupt(self, mock_run_scan):
        """Test scan command handles KeyboardInterrupt (Ctrl+C)."""
        result = self.runner.invoke(cli.app, ["scan"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("interrupted by user", result.output)

    @patch(
        "vscode_scanner.cli.run_scan", side_effect=RuntimeError("Unexpected failure")
    )
    def test_scan_unexpected_exception(self, mock_run_scan):
        """Test scan command handles unexpected exceptions."""
        result = self.runner.invoke(cli.app, ["scan"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Unexpected error", result.output)
        self.assertIn("RuntimeError", result.output)


if __name__ == "__main__":
    unittest.main()
