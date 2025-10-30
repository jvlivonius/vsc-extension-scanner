#!/usr/bin/env python3
"""
Test Suite: Report Command Tests
Purpose: Test report generation command functionality
Coverage: vscode_scanner.cli report command (HTML/JSON/CSV generation)

This test suite validates report generation from cached data including:
- JSON report generation
- HTML report generation
- CSV export generation
- Parameter validation (cache_max_age)
- Empty cache handling
- Path validation
- Error handling

Mocking Strategy:
- Mock CacheManager to avoid filesystem operations
- Mock OutputFormatter and HTMLReportGenerator
- Mock file operations (open/write)
- Use temporary directories for path validation
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

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
# JSON Report Generation Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestReportJSONGeneration(unittest.TestCase):
    """Test suite for JSON report generation.

    **Purpose:** Ensure JSON reports are generated correctly from cached data.

    **Scope:**
    - Generate JSON from cached results
    - Parameter validation
    - Empty cache handling
    - Path validation
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "report.json")

        # Mock cached results
        self.mock_results = [
            {
                "extension_id": "publisher.extension1",
                "version": "1.0.0",
                "risk_level": "low",
                "vulnerabilities": [],
            }
        ]

        # Mock formatted results
        self.mock_formatted = {
            "extensions": self.mock_results,
            "summary": {"total": 1, "vulnerabilities": 0},
        }

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("builtins.open", new_callable=mock_open)
    @patch("vscode_scanner.cli.safe_mkdir")
    def test_json_report_generation(
        self, mock_mkdir, mock_file, mock_formatter_class, mock_cache_class
    ):
        """Test successful JSON report generation."""
        # Arrange
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = self.mock_results
        mock_cache_class.return_value = mock_cache

        mock_formatter = MagicMock()
        mock_formatter.format_output.return_value = self.mock_formatted
        mock_formatter_class.return_value = mock_formatter

        # Act
        result = self.runner.invoke(cli.app, ["report", self.output_file, "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg=f"Should succeed. Output: {result.stdout}"
        )
        mock_cache.get_all_cached_results.assert_called_once()
        mock_formatter.format_output.assert_called_once()

    @patch("vscode_scanner.cache_manager.CacheManager")
    def test_json_report_with_empty_cache(self, mock_cache_class):
        """Test JSON report generation with empty cache."""
        # Arrange
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = []
        mock_cache_class.return_value = mock_cache

        # Act
        result = self.runner.invoke(cli.app, ["report", self.output_file, "--plain"])

        # Assert
        # Should fail with empty cache (exit code 1 or 2)
        self.assertNotEqual(
            result.exit_code,
            0,
            msg=f"Should fail with empty cache. Output: {result.stdout}",
        )

    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("builtins.open", new_callable=mock_open)
    @patch("vscode_scanner.cli.safe_mkdir")
    def test_json_report_with_custom_max_age(
        self, mock_mkdir, mock_file, mock_formatter_class, mock_cache_class
    ):
        """Test JSON report with custom cache_max_age."""
        # Arrange
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = self.mock_results
        mock_cache_class.return_value = mock_cache

        mock_formatter = MagicMock()
        mock_formatter.format_output.return_value = self.mock_formatted
        mock_formatter_class.return_value = mock_formatter

        # Act
        result = self.runner.invoke(
            cli.app, ["report", self.output_file, "--cache-max-age", "30", "--plain"]
        )

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should accept valid max_age")
        mock_cache.get_all_cached_results.assert_called_with(max_age_days=30)

    def test_json_report_invalid_max_age(self):
        """Test JSON report with invalid cache_max_age."""
        # Act
        result = self.runner.invoke(
            cli.app, ["report", self.output_file, "--cache-max-age", "0", "--plain"]
        )

        # Assert
        self.assertEqual(result.exit_code, 2, msg="Should reject invalid max_age")


# ============================================================
# HTML Report Generation Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestReportHTMLGeneration(unittest.TestCase):
    """Test suite for HTML report generation.

    **Purpose:** Ensure HTML reports are generated correctly from cached data.

    **Scope:**
    - Generate HTML from cached results
    - HTML template rendering
    - Error handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "report.html")

        # Mock cached results
        self.mock_results = [
            {
                "extension_id": "publisher.extension1",
                "version": "1.0.0",
                "risk_level": "low",
                "vulnerabilities": [],
            }
        ]

        # Mock formatted results
        self.mock_formatted = {
            "extensions": self.mock_results,
            "summary": {"total": 1, "vulnerabilities": 0},
        }

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("vscode_scanner.html_report_generator.HTMLReportGenerator")
    @patch("builtins.open", new_callable=mock_open)
    @patch("vscode_scanner.cli.safe_mkdir")
    def test_html_report_generation(
        self,
        mock_mkdir,
        mock_file,
        mock_html_class,
        mock_formatter_class,
        mock_cache_class,
    ):
        """Test successful HTML report generation."""
        # Arrange
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = self.mock_results
        mock_cache_class.return_value = mock_cache

        mock_formatter = MagicMock()
        mock_formatter.format_output.return_value = self.mock_formatted
        mock_formatter_class.return_value = mock_formatter

        mock_html_gen = MagicMock()
        mock_html_gen.generate_report.return_value = "<html>Report</html>"
        mock_html_class.return_value = mock_html_gen

        # Act
        result = self.runner.invoke(cli.app, ["report", self.output_file, "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg=f"Should succeed. Output: {result.stdout}"
        )
        mock_html_gen.generate_report.assert_called_once_with(self.mock_formatted)

    @patch("vscode_scanner.cache_manager.CacheManager")
    def test_html_report_with_empty_cache(self, mock_cache_class):
        """Test HTML report generation with empty cache."""
        # Arrange
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = []
        mock_cache_class.return_value = mock_cache

        # Act
        result = self.runner.invoke(cli.app, ["report", self.output_file, "--plain"])

        # Assert
        # Should fail with empty cache (exit code 1 or 2)
        self.assertNotEqual(
            result.exit_code,
            0,
            msg=f"Should fail with empty cache. Output: {result.stdout}",
        )

    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("vscode_scanner.html_report_generator.HTMLReportGenerator")
    @patch("builtins.open", new_callable=mock_open)
    @patch("vscode_scanner.cli.safe_mkdir")
    def test_html_report_with_custom_cache_dir(
        self,
        mock_mkdir,
        mock_file,
        mock_html_class,
        mock_formatter_class,
        mock_cache_class,
    ):
        """Test HTML report with custom cache directory."""
        # Arrange
        custom_dir = os.path.join(self.temp_dir, "custom_cache")
        os.makedirs(custom_dir)

        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = self.mock_results
        mock_cache_class.return_value = mock_cache

        mock_formatter = MagicMock()
        mock_formatter.format_output.return_value = self.mock_formatted
        mock_formatter_class.return_value = mock_formatter

        mock_html_gen = MagicMock()
        mock_html_gen.generate_report.return_value = "<html>Report</html>"
        mock_html_class.return_value = mock_html_gen

        # Act
        result = self.runner.invoke(
            cli.app, ["report", self.output_file, "--cache-dir", custom_dir, "--plain"]
        )

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg="Should accept custom cache directory"
        )


# ============================================================
# CSV Export Generation Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestReportCSVGeneration(unittest.TestCase):
    """Test suite for CSV export generation.

    **Purpose:** Ensure CSV exports are generated correctly from cached data.

    **Scope:**
    - Generate CSV from cached results
    - CSV formatting
    - Error handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "export.csv")

        # Mock cached results
        self.mock_results = [
            {
                "extension_id": "publisher.extension1",
                "version": "1.0.0",
                "risk_level": "low",
                "vulnerabilities": [],
            }
        ]

        # Mock formatted results
        self.mock_formatted = {
            "extensions": self.mock_results,
            "summary": {"total": 1, "vulnerabilities": 0},
        }

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.cache_manager.CacheManager")
    @patch("vscode_scanner.output_formatter.OutputFormatter")
    @patch("builtins.open", new_callable=mock_open)
    @patch("vscode_scanner.cli.safe_mkdir")
    def test_csv_export_generation(
        self, mock_mkdir, mock_file, mock_formatter_class, mock_cache_class
    ):
        """Test successful CSV export generation."""
        # Arrange
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = self.mock_results
        mock_cache_class.return_value = mock_cache

        mock_formatter = MagicMock()
        mock_formatter.format_output.return_value = self.mock_formatted
        mock_formatter.format_csv.return_value = "extension_id,version\npub.ext1,1.0.0"
        mock_formatter_class.return_value = mock_formatter

        # Act
        result = self.runner.invoke(cli.app, ["report", self.output_file, "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg=f"Should succeed. Output: {result.stdout}"
        )
        mock_formatter.format_csv.assert_called_once()

    @patch("vscode_scanner.cache_manager.CacheManager")
    def test_csv_export_with_empty_cache(self, mock_cache_class):
        """Test CSV export with empty cache."""
        # Arrange
        mock_cache = MagicMock()
        mock_cache.get_init_messages.return_value = []
        mock_cache.get_all_cached_results.return_value = []
        mock_cache_class.return_value = mock_cache

        # Act
        result = self.runner.invoke(cli.app, ["report", self.output_file, "--plain"])

        # Assert
        # Should fail with empty cache (exit code 1 or 2)
        self.assertNotEqual(
            result.exit_code,
            0,
            msg=f"Should fail with empty cache. Output: {result.stdout}",
        )


# ============================================================
# Report Path Validation Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
class TestReportPathValidation(unittest.TestCase):
    """Test suite for report path validation.

    **Purpose:** Ensure output paths are validated correctly.

    **Scope:**
    - Invalid file extensions
    - Path traversal prevention
    - Permission errors
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

    def test_report_invalid_extension(self):
        """Test that invalid file extensions are rejected."""
        # Arrange
        output_file = os.path.join(self.temp_dir, "report.txt")

        # Act
        result = self.runner.invoke(cli.app, ["report", output_file, "--plain"])

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should reject invalid file extension"
        )
        self.assertIn(".json, .html, or .csv", result.stdout.lower())

    def test_report_invalid_output_path(self):
        """Test that invalid output paths are rejected."""
        # Act
        result = self.runner.invoke(
            cli.app, ["report", "../../../etc/passwd", "--plain"]
        )

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should reject path traversal attempts"
        )

    def test_report_invalid_cache_dir(self):
        """Test that invalid cache directories are rejected."""
        # Arrange
        output_file = os.path.join(self.temp_dir, "report.json")

        # Act
        result = self.runner.invoke(
            cli.app,
            ["report", output_file, "--cache-dir", "../../../etc/passwd", "--plain"],
        )

        # Assert
        self.assertEqual(
            result.exit_code, 2, msg="Should reject invalid cache directory"
        )


# ============================================================
# Test Runner
# ============================================================


def run_tests():
    """Run the test suite and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestReportJSONGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestReportHTMLGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestReportCSVGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestReportPathValidation))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Report Command Test Summary")
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
