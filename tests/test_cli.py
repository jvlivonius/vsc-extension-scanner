#!/usr/bin/env python3
"""
Unit tests for cli.py module.

Tests Typer CLI framework, commands, and parameter validation.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from typer.testing import CliRunner
    from vscode_scanner import cli

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    print("Warning: Typer not available, skipping CLI tests")


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestCLICommands(unittest.TestCase):
    """Test CLI commands and basic invocation."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_version_flag(self):
        """Test --version flag."""
        result = self.runner.invoke(cli.app, ["--version"])
        self.assertIn("version", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_help_flag(self):
        """Test --help flag."""
        result = self.runner.invoke(cli.app, ["--help"])
        self.assertIn("scan", result.stdout.lower())
        self.assertIn("cache", result.stdout.lower())
        self.assertIn("config", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_scan_help(self):
        """Test scan command help."""
        result = self.runner.invoke(cli.app, ["scan", "--help"])
        self.assertIn("output", result.stdout.lower())
        self.assertIn("publisher", result.stdout.lower())
        self.assertIn("cache", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_cache_stats_help(self):
        """Test cache stats subcommand help."""
        result = self.runner.invoke(cli.app, ["cache", "stats", "--help"])
        self.assertIn("cache", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_cache_clear_help(self):
        """Test cache clear subcommand help."""
        result = self.runner.invoke(cli.app, ["cache", "clear", "--help"])
        self.assertIn("clear", result.stdout.lower())
        self.assertIn("force", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestScanCommand(unittest.TestCase):
    """Test scan command with various parameters."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_scan_basic(self):
        """Test basic scan command - just verify it doesn't crash."""
        # Since we can't easily mock the scanner, just test validation
        result = self.runner.invoke(
            cli.app,
            [
                "scan",
                "--publisher",
                "test",
                "--no-cache",
                "--plain",
                "--quiet",
                "--extensions-dir",
                "/nonexistent",
            ],
        )

        # Should fail because directory doesn't exist, but that's expected
        # Just verify the command structure works and proper error handling
        # Check both stderr and output since Typer may output errors to either
        error_text = ""
        try:
            error_text = result.stderr.lower()
        except (ValueError, AttributeError):
            error_text = result.output.lower()

        self.assertTrue(
            "error" in error_text
            or "nonexistent" in error_text
            or result.exit_code == 2,
            f"Expected error handling, got exit_code={result.exit_code}, output={error_text[:100]}",
        )

    def test_scan_with_filters(self):
        """Test scan command accepts filter arguments."""
        # Just test that the arguments are accepted
        result = self.runner.invoke(
            cli.app,
            [
                "scan",
                "--publisher",
                "microsoft",
                "--min-risk-level",
                "high",
                "--include-ids",
                "test.extension",
                "--help",
            ],
        )

        # Help should work regardless of other args
        self.assertEqual(result.exit_code, 0)
        self.assertIn("publisher", result.stdout.lower())

    def test_scan_with_output(self):
        """Test scan command accepts output parameter."""
        result = self.runner.invoke(
            cli.app, ["scan", "--output", "/tmp/test.json", "--help"]
        )

        # Help should work
        self.assertEqual(result.exit_code, 0)
        self.assertIn("output", result.stdout.lower())

    def test_scan_invalid_risk_level(self):
        """Test scan with invalid risk level."""
        result = self.runner.invoke(
            cli.app, ["scan", "--min-risk-level", "invalid", "--plain", "--quiet"]
        )

        self.assertNotEqual(result.exit_code, 0)
        # Check both stderr and output since Typer may output errors to either
        try:
            error_text = result.stderr.lower()
        except (ValueError, AttributeError):
            error_text = result.output.lower()
        self.assertIn("error", error_text)

    def test_scan_conflicting_cache_options(self):
        """Test scan with conflicting cache options."""
        result = self.runner.invoke(
            cli.app, ["scan", "--no-cache", "--refresh-cache", "--plain", "--quiet"]
        )

        self.assertNotEqual(result.exit_code, 0)
        # Check both stderr and output since Typer may output errors to either
        try:
            error_text = result.stderr.lower()
        except (ValueError, AttributeError):
            error_text = result.output.lower()
        self.assertIn("error", error_text)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestCacheStatsCommand(unittest.TestCase):
    """Test cache-stats command (Phase 2, Task 2.3)."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.cli.CacheManager")
    def test_cache_stats_displays_stats(self, mock_cache_manager_class):
        """Test cache stats displays statistics successfully."""
        # Mock CacheManager instance
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.get_cache_stats.return_value = {
            "total_entries": 10,
            "total_size": 1024,
            "by_age": {"fresh": 8, "stale": 2},
            "by_risk": {"low": 5, "medium": 3, "high": 2},
            "with_vulnerabilities": 3,
        }

        result = self.runner.invoke(cli.app, ["cache", "stats", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_cache_manager.get_cache_stats.assert_called_once_with(max_age_days=7)

    def test_cache_stats_invalid_max_age_below_min(self):
        """Test cache stats rejects cache-max-age below minimum."""
        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-max-age", "0", "--plain"]
        )

        self.assertEqual(result.exit_code, 2)
        # Typer validates before function runs, error in output
        self.assertIn("Error", result.output)

    def test_cache_stats_invalid_max_age_above_max(self):
        """Test cache stats rejects cache-max-age above maximum."""
        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-max-age", "1000", "--plain"]
        )

        self.assertEqual(result.exit_code, 2)
        # Typer validates before function runs, error in output
        self.assertIn("Error", result.output)

    @patch("vscode_scanner.cli.validate_path")
    def test_cache_stats_invalid_cache_dir(self, mock_validate):
        """Test cache stats handles invalid cache directory path."""
        mock_validate.side_effect = ValueError("Invalid cache directory path")

        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-dir", "../invalid", "--plain"]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)

    @patch("vscode_scanner.cli.CacheManager")
    def test_cache_stats_handles_exception(self, mock_cache_manager_class):
        """Test cache stats handles CacheManager exceptions."""
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.get_cache_stats.side_effect = Exception("Cache error")

        result = self.runner.invoke(cli.app, ["cache", "stats", "--plain"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestCacheClearCommand(unittest.TestCase):
    """Test cache-clear command (Phase 2, Task 2.3)."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.cli.CacheManager")
    def test_cache_clear_with_force(self, mock_cache_manager_class):
        """Test cache clear with --force flag skips confirmation."""
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.clear_cache.return_value = 10

        result = self.runner.invoke(cli.app, ["cache", "clear", "--force", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_cache_manager.clear_cache.assert_called_once()
        self.assertIn("Cleared 10 cache entries", result.stdout)

    @patch("typer.confirm")
    @patch("vscode_scanner.cli.CacheManager")
    def test_cache_clear_with_confirmation(
        self, mock_cache_manager_class, mock_confirm
    ):
        """Test cache clear proceeds when user confirms."""
        mock_confirm.return_value = True
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.clear_cache.return_value = 5

        result = self.runner.invoke(cli.app, ["cache", "clear", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_confirm.assert_called_once()
        mock_cache_manager.clear_cache.assert_called_once()
        self.assertIn("Cleared 5 cache entries", result.stdout)

    @patch("typer.confirm")
    def test_cache_clear_cancelled_by_user(self, mock_confirm):
        """Test cache clear cancelled when user declines confirmation."""
        mock_confirm.return_value = False

        result = self.runner.invoke(cli.app, ["cache", "clear", "--plain"])

        self.assertEqual(result.exit_code, 1)
        mock_confirm.assert_called_once()
        self.assertIn("cancelled", result.stdout.lower())

    @patch("vscode_scanner.cli.validate_path")
    def test_cache_clear_invalid_cache_dir(self, mock_validate):
        """Test cache clear handles invalid cache directory path."""
        mock_validate.side_effect = ValueError("Invalid cache directory path")

        result = self.runner.invoke(
            cli.app,
            ["cache", "clear", "--cache-dir", "../invalid", "--force", "--plain"],
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)

    @patch("typer.confirm")
    @patch("vscode_scanner.cli.CacheManager")
    def test_cache_clear_handles_exception(
        self, mock_cache_manager_class, mock_confirm
    ):
        """Test cache clear handles CacheManager exceptions."""
        mock_confirm.return_value = True
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.clear_cache.side_effect = Exception("Cache error")

        result = self.runner.invoke(cli.app, ["cache", "clear", "--plain"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.stdout)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestReportCommand(unittest.TestCase):
    """Test report command (Phase 2, Task 2.4)."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_report_generates_json(
        self,
        mock_open_file,
        mock_safe_mkdir,
        mock_cache_manager_class,
        mock_formatter_class,
    ):
        """Test report command generates JSON report successfully."""
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

        result = self.runner.invoke(cli.app, ["report", "report.json", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_cache_manager.get_all_cached_results.assert_called_once()
        self.assertIn("JSON report generated", result.output)

    @patch("vscode_scanner.html_report_generator.HTMLReportGenerator")
    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_report_generates_html(
        self,
        mock_open_file,
        mock_safe_mkdir,
        mock_cache_manager_class,
        mock_formatter_class,
        mock_html_gen_class,
    ):
        """Test report command generates HTML report successfully."""
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

        # Mock HTMLReportGenerator
        mock_html_gen = MagicMock()
        mock_html_gen_class.return_value = mock_html_gen
        mock_html_gen.generate_report.return_value = "<html>Test Report</html>"

        result = self.runner.invoke(cli.app, ["report", "report.html", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_html_gen.generate_report.assert_called_once()
        self.assertIn("HTML report generated", result.output)

    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_report_generates_csv(
        self,
        mock_open_file,
        mock_safe_mkdir,
        mock_cache_manager_class,
        mock_formatter_class,
    ):
        """Test report command generates CSV export successfully."""
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
        mock_formatter.format_csv.return_value = "extension_id,risk_level\ntest.ext,low"

        result = self.runner.invoke(cli.app, ["report", "report.csv", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_formatter.format_csv.assert_called_once()
        self.assertIn("CSV export generated", result.output)

    @patch("vscode_scanner.cli.safe_mkdir")
    def test_report_invalid_extension(self, mock_safe_mkdir):
        """Test report command rejects unsupported file extension."""
        result = self.runner.invoke(cli.app, ["report", "report.txt", "--plain"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("must have .json, .html, or .csv extension", result.output)

    @patch("vscode_scanner.cli.validate_path")
    def test_report_invalid_output_path(self, mock_validate):
        """Test report command handles invalid output path."""
        mock_validate.side_effect = ValueError("Invalid output path")

        result = self.runner.invoke(cli.app, ["report", "../invalid.json", "--plain"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Invalid output path", result.output)

    @patch("vscode_scanner.cli._check_extensions_exist")
    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.utils.safe_mkdir")
    def test_report_cache_empty(
        self, mock_safe_mkdir, mock_cache_manager_class, mock_check_exts
    ):
        """Test report command fails when cache is empty."""
        # Mock CacheManager returning empty cache
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.get_all_cached_results.return_value = []

        # Mock extensions exist
        mock_check_exts.return_value = (True, 5)

        result = self.runner.invoke(cli.app, ["report", "report.json", "--plain"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Cache is empty", result.output)

    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.utils.safe_mkdir")
    def test_report_handles_exception(self, mock_safe_mkdir, mock_cache_manager_class):
        """Test report command handles CacheManager exceptions."""
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.get_all_cached_results.side_effect = Exception("Cache error")

        result = self.runner.invoke(cli.app, ["report", "report.json", "--plain"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error generating report", result.output)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestCLIErrorHandling(unittest.TestCase):
    """Test CLI error handling (Phase 2, Task 2.5)."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.utils.safe_mkdir")
    @patch("builtins.open")
    def test_report_handles_permission_error(
        self, mock_open, mock_safe_mkdir, mock_cache_manager_class
    ):
        """Test report command handles PermissionError when writing file."""
        mock_cache_manager = MagicMock()
        mock_cache_manager_class.return_value = mock_cache_manager
        mock_cache_manager.get_init_messages.return_value = []
        mock_cache_manager.get_all_cached_results.return_value = [
            {"extension_id": "test.ext", "risk_level": "low"}
        ]

        # Simulate permission error on file write
        mock_open.side_effect = PermissionError("Permission denied")

        result = self.runner.invoke(cli.app, ["report", "report.json", "--plain"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error generating report", result.output)

    # NOTE: No test for config init path validation - config commands use hardcoded
    # ~/.vscanrc path (not user input), so validate_path() is not called. Only commands
    # that accept user-provided paths (cache --cache-dir, scan --extensions-dir, etc.)
    # require path validation. See config_manager.py:get_config_path() for details.

    @patch("vscode_scanner.utils.validate_path")
    def test_cache_stats_handles_path_traversal(self, mock_validate):
        """Test cache stats rejects path traversal attempts."""
        mock_validate.side_effect = ValueError("Path traversal detected")

        result = self.runner.invoke(
            cli.app, ["cache", "stats", "--cache-dir", "../../etc", "--plain"]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)

    @patch("vscode_scanner.utils.validate_path")
    def test_cache_clear_handles_path_traversal(self, mock_validate):
        """Test cache clear rejects path traversal attempts."""
        mock_validate.side_effect = ValueError("Path traversal detected")

        result = self.runner.invoke(
            cli.app,
            ["cache", "clear", "--cache-dir", "../../etc", "--force", "--plain"],
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error", result.output)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestParameterValidation(unittest.TestCase):
    """Test parameter validation."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_delay_bounds(self):
        """Test delay parameter bounds."""
        # Test too small
        result = self.runner.invoke(
            cli.app, ["scan", "--delay", "0.05", "--plain", "--quiet"]
        )
        self.assertNotEqual(result.exit_code, 0)

        # Test too large
        result = self.runner.invoke(
            cli.app, ["scan", "--delay", "100", "--plain", "--quiet"]
        )
        self.assertNotEqual(result.exit_code, 0)

    def test_max_retries_bounds(self):
        """Test max-retries parameter bounds."""
        # Test negative
        result = self.runner.invoke(
            cli.app, ["scan", "--max-retries", "-1", "--plain", "--quiet"]
        )
        self.assertNotEqual(result.exit_code, 0)

        # Test too large
        result = self.runner.invoke(
            cli.app, ["scan", "--max-retries", "100", "--plain", "--quiet"]
        )
        self.assertNotEqual(result.exit_code, 0)

    def test_cache_max_age_bounds(self):
        """Test cache-max-age parameter bounds."""
        # Test zero
        result = self.runner.invoke(
            cli.app, ["cache-stats", "--cache-max-age", "0", "--plain"]
        )
        self.assertNotEqual(result.exit_code, 0)

        # Test too large
        result = self.runner.invoke(
            cli.app, ["cache-stats", "--cache-max-age", "1000", "--plain"]
        )
        self.assertNotEqual(result.exit_code, 0)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestConfigCommands(unittest.TestCase):
    """Tests for config subcommands (Phase 2, Task 2.2)."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.config_manager.create_default_config")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_init_creates_default_config(self, mock_get_path, mock_create):
        """Test config init creates default configuration file."""
        mock_get_path.return_value = Path("/tmp/.vscanrc")
        mock_create.return_value = Path("/tmp/.vscanrc")

        result = self.runner.invoke(cli.app, ["config", "init", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_create.assert_called_once_with(force=False)
        self.assertIn("Created configuration file", result.stdout)

    @patch("vscode_scanner.config_manager.create_default_config")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_init_with_force_flag(self, mock_get_path, mock_create):
        """Test config init with --force flag overwrites existing config."""
        mock_get_path.return_value = Path("/tmp/.vscanrc")
        mock_create.return_value = Path("/tmp/.vscanrc")

        result = self.runner.invoke(cli.app, ["config", "init", "--force", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_create.assert_called_once_with(force=True)

    @patch("vscode_scanner.config_manager.create_default_config")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_init_file_exists_error(self, mock_get_path, mock_create):
        """Test config init handles FileExistsError gracefully."""
        mock_get_path.return_value = Path("/tmp/.vscanrc")
        mock_create.side_effect = FileExistsError("Config file already exists")

        result = self.runner.invoke(cli.app, ["config", "init", "--plain"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("already exists", result.stdout)
        self.assertIn("--force", result.stdout)

    @patch("vscode_scanner.config_manager.config_exists")
    @patch("vscode_scanner.config_manager.load_config")
    @patch("vscode_scanner.config_manager.get_config_path")
    @patch("vscode_scanner.config_manager.get_default_value")
    def test_config_show_displays_current_config(
        self, mock_default, mock_path, mock_load, mock_exists
    ):
        """Test config show displays current configuration."""
        mock_exists.return_value = True
        mock_path.return_value = Path("/tmp/.vscanrc")
        mock_load.return_value = (
            {
                "scan": {"delay": 1.5, "max_retries": 3},
                "cache": {"enabled": True, "cache_max_age": 7},
                "output": {},
            },
            [],  # No warnings
        )
        mock_default.side_effect = lambda s, o: {
            ("scan", "delay"): 1.5,
            ("scan", "max_retries"): 3,
            ("cache", "enabled"): True,
            ("cache", "cache_max_age"): 7,
        }.get((s, o))

        result = self.runner.invoke(cli.app, ["config", "show", "--plain"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configuration File", result.stdout)
        self.assertIn("scan.delay", result.stdout)
        self.assertIn("1.5", result.stdout)

    @patch("vscode_scanner.config_manager.config_exists")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_show_no_config_file(self, mock_path, mock_exists):
        """Test config show handles missing config file gracefully."""
        mock_exists.return_value = False
        mock_path.return_value = Path("/tmp/.vscanrc")

        result = self.runner.invoke(cli.app, ["config", "show", "--plain"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("No configuration file found", result.stdout)
        self.assertIn("vscan config init", result.stdout)

    @patch("vscode_scanner.config_manager.config_exists")
    @patch("vscode_scanner.config_manager.update_config_value")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_set_updates_value(self, mock_path, mock_update, mock_exists):
        """Test config set updates configuration value."""
        mock_exists.return_value = True
        mock_path.return_value = Path("/tmp/.vscanrc")

        result = self.runner.invoke(
            cli.app, ["config", "set", "scan.delay", "2.0", "--plain"]
        )

        self.assertEqual(result.exit_code, 0)
        mock_update.assert_called_once()
        self.assertIn("scan.delay", result.stdout)
        self.assertIn("2.0", result.stdout)

    @patch("vscode_scanner.config_manager.config_exists")
    def test_config_set_no_config_file(self, mock_exists):
        """Test config set creates config if it doesn't exist."""
        mock_exists.return_value = False

        # Mock the config creation side effect
        with patch(
            "vscode_scanner.config_manager.create_default_config"
        ) as mock_create:
            mock_create.return_value = Path("/tmp/.vscanrc")
            with patch("vscode_scanner.config_manager.update_config_value"):
                result = self.runner.invoke(
                    cli.app, ["config", "set", "scan.delay", "2.0", "--plain"]
                )

                # Should create config first
                self.assertEqual(result.exit_code, 0)

    @patch("vscode_scanner.config_manager.config_exists")
    @patch("vscode_scanner.config_manager.load_config")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_get_retrieves_value(self, mock_path, mock_load, mock_exists):
        """Test config get retrieves configuration value."""
        mock_exists.return_value = True
        mock_path.return_value = Path("/tmp/.vscanrc")
        mock_load.return_value = (
            {"scan": {"delay": 2.5, "max_retries": 3}, "cache": {}, "output": {}},
            [],
        )

        result = self.runner.invoke(cli.app, ["config", "get", "scan.delay", "--plain"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("2.5", result.stdout)

    @patch("vscode_scanner.config_manager.load_config")
    @patch("vscode_scanner.config_manager.get_default_value")
    def test_config_get_no_config_file(self, mock_default, mock_load):
        """Test config get returns default values when no config file exists."""
        # Config get always returns values (defaults if no config file)
        mock_load.return_value = (
            {"scan": {"delay": 1.5}, "cache": {}, "output": {}},
            [],
        )
        mock_default.return_value = 1.5

        result = self.runner.invoke(cli.app, ["config", "get", "scan.delay", "--plain"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("1.5", result.stdout)
        self.assertIn("default", result.stdout)

    @patch("typer.confirm")
    @patch("vscode_scanner.config_manager.config_exists")
    @patch("vscode_scanner.config_manager.delete_config")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_reset_restores_defaults(
        self, mock_path, mock_delete, mock_exists, mock_confirm
    ):
        """Test config reset deletes config file to restore defaults."""
        mock_exists.return_value = True
        mock_path.return_value = Path("/tmp/.vscanrc")
        mock_confirm.return_value = True

        result = self.runner.invoke(cli.app, ["config", "reset", "--plain"])

        self.assertEqual(result.exit_code, 0)
        mock_delete.assert_called_once()
        self.assertIn("deleted", result.stdout.lower())

    @patch("typer.confirm")
    @patch("vscode_scanner.config_manager.config_exists")
    @patch("vscode_scanner.config_manager.delete_config")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_reset_cancelled_by_user(
        self, mock_path, mock_delete, mock_exists, mock_confirm
    ):
        """Test config reset cancelled when user declines confirmation."""
        mock_exists.return_value = True
        mock_path.return_value = Path("/tmp/.vscanrc")
        mock_confirm.return_value = False

        result = self.runner.invoke(cli.app, ["config", "reset", "--plain"])

        self.assertEqual(result.exit_code, 1)  # Exit code 1 when cancelled
        mock_delete.assert_not_called()
        self.assertIn("cancelled", result.stdout.lower())

    @patch("vscode_scanner.config_manager.config_exists")
    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_reset_no_config_file(self, mock_path, mock_exists):
        """Test config reset handles missing config file gracefully."""
        mock_exists.return_value = False
        mock_path.return_value = Path("/tmp/.vscanrc")

        result = self.runner.invoke(cli.app, ["config", "reset", "--plain"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("No configuration file to reset", result.stdout)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestCLIValidators(unittest.TestCase):
    """Tests for CLI input validator functions (Phase 2, Task 2.1)."""

    def test_bounded_int_validator_valid_range(self):
        """Test bounded_int_validator accepts values within range."""
        # Test minimum boundary
        result = cli.bounded_int_validator(1, 1, 10, "workers")
        self.assertEqual(result, 1)

        # Test maximum boundary
        result = cli.bounded_int_validator(10, 1, 10, "workers")
        self.assertEqual(result, 10)

        # Test middle value
        result = cli.bounded_int_validator(5, 1, 10, "workers")
        self.assertEqual(result, 5)

    def test_bounded_int_validator_below_min(self):
        """Test bounded_int_validator rejects values below minimum."""
        import typer

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_int_validator(0, 1, 10, "workers")
        self.assertIn("must be between 1 and 10", str(ctx.exception))

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_int_validator(-5, 1, 10, "workers")
        self.assertIn("must be between 1 and 10", str(ctx.exception))

    def test_bounded_int_validator_above_max(self):
        """Test bounded_int_validator rejects values above maximum."""
        import typer

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_int_validator(11, 1, 10, "workers")
        self.assertIn("must be between 1 and 10", str(ctx.exception))

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_int_validator(100, 1, 10, "workers")
        self.assertIn("must be between 1 and 10", str(ctx.exception))

    def test_bounded_float_validator_valid_range(self):
        """Test bounded_float_validator accepts values within range."""
        # Test minimum boundary
        result = cli.bounded_float_validator(0.0, 0.0, 10.0, "delay")
        self.assertEqual(result, 0.0)

        # Test maximum boundary
        result = cli.bounded_float_validator(10.0, 0.0, 10.0, "delay")
        self.assertEqual(result, 10.0)

        # Test middle value
        result = cli.bounded_float_validator(5.5, 0.0, 10.0, "delay")
        self.assertEqual(result, 5.5)

        # Test fractional value
        result = cli.bounded_float_validator(2.75, 0.0, 10.0, "delay")
        self.assertEqual(result, 2.75)

    def test_bounded_float_validator_below_min(self):
        """Test bounded_float_validator rejects values below minimum."""
        import typer

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_float_validator(-0.1, 0.0, 10.0, "delay")
        self.assertIn("must be between 0.0 and 10.0", str(ctx.exception))

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_float_validator(-5.5, 0.0, 10.0, "delay")
        self.assertIn("must be between 0.0 and 10.0", str(ctx.exception))

    def test_bounded_float_validator_above_max(self):
        """Test bounded_float_validator rejects values above maximum."""
        import typer

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_float_validator(10.1, 0.0, 10.0, "delay")
        self.assertIn("must be between 0.0 and 10.0", str(ctx.exception))

        with self.assertRaises(typer.BadParameter) as ctx:
            cli.bounded_float_validator(100.0, 0.0, 10.0, "delay")
        self.assertIn("must be between 0.0 and 10.0", str(ctx.exception))

    def test_bounded_int_validator_edge_cases(self):
        """Test bounded_int_validator with edge case scenarios."""
        # Test single value range
        result = cli.bounded_int_validator(5, 5, 5, "workers")
        self.assertEqual(result, 5)

        # Test negative range
        result = cli.bounded_int_validator(-5, -10, -1, "workers")
        self.assertEqual(result, -5)

    def test_bounded_float_validator_edge_cases(self):
        """Test bounded_float_validator with edge case scenarios."""
        # Test very small range
        result = cli.bounded_float_validator(0.5, 0.5, 0.5, "delay")
        self.assertEqual(result, 0.5)

        # Test negative range
        result = cli.bounded_float_validator(-2.5, -10.0, -1.0, "delay")
        self.assertEqual(result, -2.5)

        # Test precision
        result = cli.bounded_float_validator(1.23456789, 0.0, 10.0, "delay")
        self.assertAlmostEqual(result, 1.23456789, places=7)


def run_tests():
    """Run all tests."""
    if not TYPER_AVAILABLE:
        print("Skipping CLI tests - Typer not available")
        return 0

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCLICommands))
    suite.addTests(loader.loadTestsFromTestCase(TestScanCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheStatsCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheClearCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestReportCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestCLIErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestParameterValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestCLIValidators))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
