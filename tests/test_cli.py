#!/usr/bin/env python3
"""
Unit tests for cli.py module.

Tests Typer CLI framework, commands, and parameter validation.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
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
        self.assertIn("cache-stats", result.stdout.lower())
        self.assertIn("cache-clear", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_scan_help(self):
        """Test scan command help."""
        result = self.runner.invoke(cli.app, ["scan", "--help"])
        self.assertIn("output", result.stdout.lower())
        self.assertIn("publisher", result.stdout.lower())
        self.assertIn("cache", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_cache_stats_help(self):
        """Test cache-stats command help."""
        result = self.runner.invoke(cli.app, ["cache-stats", "--help"])
        self.assertIn("cache", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)

    def test_cache_clear_help(self):
        """Test cache-clear command help."""
        result = self.runner.invoke(cli.app, ["cache-clear", "--help"])
        self.assertIn("clear", result.stdout.lower() or result.stdout.lower())
        self.assertIn("force", result.stdout.lower())
        self.assertEqual(result.exit_code, 0)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestScanCommand(unittest.TestCase):
    """Test scan command with various parameters."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_scan_basic(self):
        """Test basic scan command - just verify it doesn't crash."""
        # Since we can't easily mock the scanner, just test validation
        result = self.runner.invoke(cli.app, [
            "scan",
            "--publisher", "test",
            "--no-cache",
            "--plain", "--quiet",
            "--extensions-dir", "/nonexistent"
        ])

        # Should fail because directory doesn't exist, but that's expected
        # Just verify the command structure works
        self.assertIn("error", result.stdout.lower() or "nonexistent" in result.stdout.lower() or result.exit_code == 2)

    def test_scan_with_filters(self):
        """Test scan command accepts filter arguments."""
        # Just test that the arguments are accepted
        result = self.runner.invoke(cli.app, [
            "scan",
            "--publisher", "microsoft",
            "--min-risk-level", "high",
            "--include-ids", "test.extension",
            "--help"
        ])

        # Help should work regardless of other args
        self.assertEqual(result.exit_code, 0)
        self.assertIn("publisher", result.stdout.lower())

    def test_scan_with_output(self):
        """Test scan command accepts output parameter."""
        result = self.runner.invoke(cli.app, [
            "scan",
            "--output", "/tmp/test.json",
            "--help"
        ])

        # Help should work
        self.assertEqual(result.exit_code, 0)
        self.assertIn("output", result.stdout.lower())

    def test_scan_invalid_risk_level(self):
        """Test scan with invalid risk level."""
        result = self.runner.invoke(cli.app, [
            "scan",
            "--min-risk-level", "invalid",
            "--plain", "--quiet"
        ])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.stdout.lower())

    def test_scan_conflicting_quiet_verbose(self):
        """Test scan with conflicting --quiet and --verbose."""
        result = self.runner.invoke(cli.app, [
            "scan",
            "--quiet",
            "--verbose",
            "--plain"
        ])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.stdout.lower())

    def test_scan_conflicting_cache_options(self):
        """Test scan with conflicting cache options."""
        result = self.runner.invoke(cli.app, [
            "scan",
            "--no-cache",
            "--refresh-cache",
            "--plain", "--quiet"
        ])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.stdout.lower())


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestCacheStatsCommand(unittest.TestCase):
    """Test cache-stats command."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_cache_stats_basic(self):
        """Test basic cache-stats command structure."""
        # Test help works
        result = self.runner.invoke(cli.app, ["cache-stats", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("cache", result.stdout.lower())

    def test_cache_stats_with_custom_age(self):
        """Test cache-stats accepts custom max age parameter."""
        # Test that parameter is accepted
        result = self.runner.invoke(cli.app, [
            "cache-stats",
            "--cache-max-age", "14",
            "--help"
        ])
        self.assertEqual(result.exit_code, 0)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestCacheClearCommand(unittest.TestCase):
    """Test cache-clear command."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_cache_clear_help(self):
        """Test cache-clear command help."""
        result = self.runner.invoke(cli.app, ["cache-clear", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("force", result.stdout.lower())

    def test_cache_clear_force_flag(self):
        """Test cache-clear accepts --force flag."""
        # Test that --force flag is accepted (with help to avoid actual clear)
        result = self.runner.invoke(cli.app, [
            "cache-clear",
            "--force",
            "--help"
        ])
        self.assertEqual(result.exit_code, 0)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestParameterValidation(unittest.TestCase):
    """Test parameter validation."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_delay_bounds(self):
        """Test delay parameter bounds."""
        # Test too small
        result = self.runner.invoke(cli.app, [
            "scan",
            "--delay", "0.05",
            "--plain", "--quiet"
        ])
        self.assertNotEqual(result.exit_code, 0)

        # Test too large
        result = self.runner.invoke(cli.app, [
            "scan",
            "--delay", "100",
            "--plain", "--quiet"
        ])
        self.assertNotEqual(result.exit_code, 0)

    def test_max_retries_bounds(self):
        """Test max-retries parameter bounds."""
        # Test negative
        result = self.runner.invoke(cli.app, [
            "scan",
            "--max-retries", "-1",
            "--plain", "--quiet"
        ])
        self.assertNotEqual(result.exit_code, 0)

        # Test too large
        result = self.runner.invoke(cli.app, [
            "scan",
            "--max-retries", "100",
            "--plain", "--quiet"
        ])
        self.assertNotEqual(result.exit_code, 0)

    def test_cache_max_age_bounds(self):
        """Test cache-max-age parameter bounds."""
        # Test zero
        result = self.runner.invoke(cli.app, [
            "cache-stats",
            "--cache-max-age", "0",
            "--plain"
        ])
        self.assertNotEqual(result.exit_code, 0)

        # Test too large
        result = self.runner.invoke(cli.app, [
            "cache-stats",
            "--cache-max-age", "1000",
            "--plain"
        ])
        self.assertNotEqual(result.exit_code, 0)


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
    suite.addTests(loader.loadTestsFromTestCase(TestParameterValidation))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
