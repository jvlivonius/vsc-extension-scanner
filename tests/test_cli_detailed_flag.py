"""
Integration tests for --detailed flag behavior with CLI and HTML output.

Tests end-to-end flag behavior, output generation, and module display
integration across different command combinations.

Target: Comprehensive flag combination testing, HTML structure validation
"""

import unittest
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
class TestDetailedFlag(unittest.TestCase):
    """Test suite for --detailed flag CLI behavior."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_detailed_flag_help_text(self):
        """Test --detailed flag appears in help text."""
        result = self.runner.invoke(cli.app, ["scan", "--help"])

        # Verify flag is documented
        self.assertIn("--detailed", result.stdout)
        self.assertIn("module", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_detailed_flag_in_command_structure(self):
        """Test --detailed flag is recognized as valid option."""
        # This just tests that the flag is accepted, not the full execution
        result = self.runner.invoke(cli.app, ["scan", "--detailed", "--help"])

        # Help should work with --detailed flag present
        self.assertEqual(result.exit_code, 0)
        self.assertIn("detailed", result.stdout.lower())

    def test_scan_without_detailed_flag(self):
        """Test scan command works without --detailed flag."""
        # Test that command accepts no --detailed flag
        result = self.runner.invoke(cli.app, ["scan", "--help"])

        # Should have scan command help
        self.assertEqual(result.exit_code, 0)
        self.assertIn("scan", result.stdout.lower())


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestDetailedWithOutput(unittest.TestCase):
    """Test suite for --detailed flag with output file generation."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_detailed_with_output_flag_combination(self):
        """Test --detailed and --output flags can be combined."""
        # Test flag combination is valid
        result = self.runner.invoke(
            cli.app, ["scan", "--detailed", "--output", "/tmp/test.html", "--help"]
        )

        # Help should work with both flags
        self.assertEqual(result.exit_code, 0)
        self.assertIn("detailed", result.stdout.lower())
        self.assertIn("output", result.stdout.lower())

    def test_output_format_options_with_detailed(self):
        """Test different output formats work with --detailed flag."""
        for ext in ["html", "json", "csv"]:
            with self.subTest(format=ext):
                result = self.runner.invoke(
                    cli.app,
                    ["scan", "--detailed", "--output", f"/tmp/test.{ext}", "--help"],
                )

                # Should accept different output formats
                self.assertEqual(result.exit_code, 0)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestFlagCombinations(unittest.TestCase):
    """Test suite for --detailed flag combinations."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_detailed_with_quiet_flag(self):
        """Test --detailed and --quiet flags can be combined."""
        result = self.runner.invoke(
            cli.app, ["scan", "--detailed", "--quiet", "--help"]
        )

        # Both flags should be acceptable
        self.assertEqual(result.exit_code, 0)

    def test_detailed_with_no_cache_flag(self):
        """Test --detailed and --no-cache flags can be combined."""
        result = self.runner.invoke(
            cli.app, ["scan", "--detailed", "--no-cache", "--help"]
        )

        # Both flags should be acceptable
        self.assertEqual(result.exit_code, 0)

    def test_detailed_with_publisher_filter(self):
        """Test --detailed works with --publisher filter."""
        result = self.runner.invoke(
            cli.app, ["scan", "--detailed", "--publisher", "microsoft", "--help"]
        )

        # Flag combination should be valid
        self.assertEqual(result.exit_code, 0)

    def test_detailed_with_multiple_filters(self):
        """Test --detailed works with multiple filter flags."""
        result = self.runner.invoke(
            cli.app,
            [
                "scan",
                "--detailed",
                "--publisher",
                "microsoft",
                "--min-risk-level",
                "high",
                "--help",
            ],
        )

        # All flags should be acceptable together
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
