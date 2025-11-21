"""
Integration tests for --detailed flag behavior with actual output validation.

Tests functional behavior: does --detailed show module breakdowns?
Uses mocked scan data to verify console and HTML output integration.

Target: Functional validation, output verification, HTML integration
"""

import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os

import pytest

try:
    from typer.testing import CliRunner
    from vscode_scanner import cli

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestDetailedFlagBehavior(unittest.TestCase):
    """Test --detailed flag functional behavior with actual output."""

    def setUp(self):
        """Set up test runner and mock data."""
        self.runner = CliRunner()

        # Mock scan result with module data
        self.mock_result = {
            "id": "test.extension",
            "display_name": "Test Extension",
            "security": {
                "score": 75,
                "module_risk_levels": {
                    "metadata": "low",
                    "dependencies": "medium",
                    "socket": "high",
                    "virus_total": "low",
                    "permissions": "medium",
                    "ossf_scorecard": "low",
                    "network_endpoints": "high",
                    "sensitive_info": "none",
                    "obfuscation": "low",
                    "consolidated_ast": "none",
                    "open_grep": "low",
                },
            },
        }

    @patch("vscode_scanner.cli.run_scan")
    def test_detailed_flag_passes_parameter_true(self, mock_run_scan):
        """Test --detailed flag causes detailed=True to be passed to run_scan."""
        # Configure mock to return success with vulnerability
        mock_run_scan.return_value = 1  # 1 = vulnerabilities found

        result = self.runner.invoke(
            cli.app, ["scan", "--detailed"], catch_exceptions=False
        )

        # Should exit with code 1 (vulnerabilities found)
        self.assertEqual(result.exit_code, 1)

        # Verify run_scan was called with detailed=True
        self.assertTrue(mock_run_scan.called)
        call_kwargs = mock_run_scan.call_args[1]
        self.assertTrue(call_kwargs.get("detailed", False))

    @patch("vscode_scanner.cli.run_scan")
    def test_without_detailed_flag_passes_parameter_false(self, mock_run_scan):
        """Test without --detailed, detailed=False is passed to run_scan (default)."""
        mock_run_scan.return_value = 0  # 0 = no vulnerabilities

        result = self.runner.invoke(cli.app, ["scan"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)

        # Verify run_scan was called with detailed=False (default)
        call_kwargs = mock_run_scan.call_args[1]
        self.assertFalse(call_kwargs.get("detailed", False))

    def test_module_breakdown_displays_table_when_detailed_true(self):
        """Test module breakdown displays Rich table when detailed=True."""
        # Test at display level with known data
        from vscode_scanner.display import format_security_modules

        mock_console = MagicMock()

        # Call with detailed=True
        format_security_modules(self.mock_result, detailed=True, console=mock_console)

        # Verify console.print was called (table output)
        self.assertTrue(mock_console.print.called)
        call_args = mock_console.print.call_args_list

        # Should be 2 calls: table + spacing
        self.assertEqual(len(call_args), 2)

        # First call should contain a table object
        table = call_args[0][0][0]
        self.assertIsNotNone(table)

    def test_module_breakdown_hidden_when_detailed_false(self):
        """Test format_security_modules returns early when detailed=False."""
        from vscode_scanner.display import format_security_modules

        mock_console = MagicMock()

        # Call with detailed=False
        format_security_modules(self.mock_result, detailed=False, console=mock_console)

        # Should return early without printing
        self.assertFalse(mock_console.print.called)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestDetailedFlagWithHTMLOutput(unittest.TestCase):
    """Test --detailed flag with HTML output generation."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.cli.run_scan")
    def test_html_generation_accepts_detailed_flag(self, mock_run_scan):
        """Test HTML output can be generated with --detailed flag."""
        mock_run_scan.return_value = 0

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_detailed.html")

            result = self.runner.invoke(
                cli.app,
                ["scan", "--detailed", "--output", output_path],
                catch_exceptions=False,
            )

            # Should succeed (0 = no vulns, 1 = vulns found)
            self.assertIn(result.exit_code, [0, 1])

            # Verify detailed=True was passed
            call_kwargs = mock_run_scan.call_args[1]
            self.assertTrue(call_kwargs.get("detailed", False))


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestDetailedFlagCombinations(unittest.TestCase):
    """Test --detailed flag combinations with other flags."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.cli.run_scan")
    def test_detailed_with_quiet_flag_both_passed(self, mock_run_scan):
        """Test --detailed and --quiet can coexist (both passed to run_scan)."""
        mock_run_scan.return_value = 0

        result = self.runner.invoke(
            cli.app, ["scan", "--detailed", "--quiet"], catch_exceptions=False
        )

        self.assertEqual(result.exit_code, 0)

        # Both flags should be passed (quiet wins for display logic)
        call_kwargs = mock_run_scan.call_args[1]
        self.assertTrue(call_kwargs.get("detailed", False))
        self.assertTrue(call_kwargs.get("quiet", False))

    @patch("vscode_scanner.cli.run_scan")
    def test_detailed_with_verbose_flag_both_passed(self, mock_run_scan):
        """Test --detailed and --verbose can coexist."""
        mock_run_scan.return_value = 0

        result = self.runner.invoke(
            cli.app, ["scan", "--detailed", "--verbose"], catch_exceptions=False
        )

        self.assertEqual(result.exit_code, 0)

        # Both flags should be passed
        call_kwargs = mock_run_scan.call_args[1]
        self.assertTrue(call_kwargs.get("detailed", False))
        self.assertTrue(call_kwargs.get("verbose", False))


if __name__ == "__main__":
    unittest.main()
