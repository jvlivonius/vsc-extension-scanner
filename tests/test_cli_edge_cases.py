"""
CLI edge case tests for cli.py

Tests CLI command error handling paths to improve coverage from 67.55% to 75%+.
Focuses on scan validation flags.
"""

import unittest
import pytest
from typer.testing import CliRunner


@pytest.mark.unit
class TestScanValidation(unittest.TestCase):
    """Test scan command validation logic."""

    def setUp(self):
        """Set up test fixtures."""
        from vscode_scanner.cli import app

        self.runner = CliRunner()
        self.app = app

    def test_scan_conflicting_verification_flags(self):
        """Scan with both --verified-only and --unverified-only returns error."""
        # Act
        result = self.runner.invoke(
            self.app, ["scan", "--verified-only", "--unverified-only"]
        )

        # Assert
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Cannot use --verified-only and --unverified-only", result.stdout)

    def test_scan_conflicting_vulnerability_flags(self):
        """Scan with both --with-vulnerabilities and --without-vulnerabilities returns error."""
        # Act
        result = self.runner.invoke(
            self.app, ["scan", "--with-vulnerabilities", "--without-vulnerabilities"]
        )

        # Assert
        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "Cannot use --with-vulnerabilities and --without-vulnerabilities",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
