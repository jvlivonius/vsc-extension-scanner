#!/usr/bin/env python3
"""
Unit Tests for OutputWriter Module

Tests the pure functions, I/O operations, and orchestration logic
for output generation and file writing.
"""

import sys
import os
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.output_writer import OutputWriter


@pytest.mark.unit
class TestOutputWriterFormatDetection(unittest.TestCase):
    """Test format detection (pure function)."""

    def test_detect_csv_format(self):
        """Test CSV format detection."""
        result = OutputWriter.detect_format(Path("report.csv"))
        self.assertEqual(result, "csv")

    def test_detect_html_format(self):
        """Test HTML format detection (.html)."""
        result = OutputWriter.detect_format(Path("report.html"))
        self.assertEqual(result, "html")

    def test_detect_htm_format(self):
        """Test HTML format detection (.htm)."""
        result = OutputWriter.detect_format(Path("report.htm"))
        self.assertEqual(result, "html")

    def test_detect_json_format(self):
        """Test JSON format detection (.json)."""
        result = OutputWriter.detect_format(Path("output.json"))
        self.assertEqual(result, "json")

    def test_detect_json_format_no_extension(self):
        """Test JSON format as default (no extension)."""
        result = OutputWriter.detect_format(Path("output"))
        self.assertEqual(result, "json")

    def test_detect_json_format_unknown_extension(self):
        """Test JSON format as default (unknown extension)."""
        result = OutputWriter.detect_format(Path("output.txt"))
        self.assertEqual(result, "json")

    def test_detect_format_case_insensitive(self):
        """Test format detection is case-insensitive."""
        self.assertEqual(OutputWriter.detect_format(Path("report.CSV")), "csv")
        self.assertEqual(OutputWriter.detect_format(Path("report.HTML")), "html")
        self.assertEqual(OutputWriter.detect_format(Path("report.HTM")), "html")


@pytest.mark.unit
class TestOutputWriterContentGeneration(unittest.TestCase):
    """Test content generation (pure function with dependencies)."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_formatter = Mock()
        self.mock_html_gen = Mock()
        self.writer = OutputWriter(
            output_formatter=self.mock_formatter, html_generator=self.mock_html_gen
        )
        self.test_results = {
            "extensions": [
                {"id": "test.ext1", "name": "ext1", "security": {"score": 85}}
            ],
            "scan_summary": {"total": 1, "vulnerabilities": 0},
        }

    def test_generate_csv_content(self):
        """Test CSV content generation."""
        self.mock_formatter.format_csv.return_value = "id,name,score\ntest.ext1,ext1,85"

        result = self.writer.generate_content("csv", self.test_results)

        self.assertEqual(result, "id,name,score\ntest.ext1,ext1,85")
        self.mock_formatter.format_csv.assert_called_once_with(
            self.test_results["extensions"]
        )

    def test_generate_html_content(self):
        """Test HTML content generation."""
        self.mock_html_gen.generate_report.return_value = "<html>...</html>"

        result = self.writer.generate_content("html", self.test_results)

        self.assertEqual(result, "<html>...</html>")
        self.mock_html_gen.generate_report.assert_called_once_with(self.test_results)

    def test_generate_json_content(self):
        """Test JSON content generation."""
        result = self.writer.generate_content("json", self.test_results)

        # Parse back to verify it's valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed, self.test_results)

        # Verify indentation
        self.assertIn("  ", result)  # Should have 2-space indentation

    def test_generate_content_invalid_format(self):
        """Test content generation with invalid format raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.writer.generate_content("invalid", self.test_results)

        self.assertIn("Invalid format type: invalid", str(ctx.exception))

    def test_generate_csv_with_empty_extensions(self):
        """Test CSV generation with empty extensions list."""
        self.mock_formatter.format_csv.return_value = "id,name,score\n"

        result = self.writer.generate_content(
            "csv", {"extensions": [], "scan_summary": {}}
        )

        self.assertEqual(result, "id,name,score\n")
        self.mock_formatter.format_csv.assert_called_once_with([])

    def test_generate_csv_with_missing_extensions_key(self):
        """Test CSV generation when 'extensions' key is missing."""
        self.mock_formatter.format_csv.return_value = "id,name,score\n"

        result = self.writer.generate_content("csv", {"scan_summary": {}})

        self.assertEqual(result, "id,name,score\n")
        self.mock_formatter.format_csv.assert_called_once_with([])


@pytest.mark.unit
class TestOutputWriterFileWriting(unittest.TestCase):
    """Test file writing (I/O operations)."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_csv_file(self):
        """Test writing CSV file with correct newline handling."""
        output_path = Path(self.test_dir) / "test.csv"
        content = "id,name,score\ntest.ext1,ext1,85\n"

        OutputWriter.write_to_file(output_path, content, "csv")

        # Verify file exists
        self.assertTrue(output_path.exists())

        # Verify content
        with open(output_path, "r", encoding="utf-8", newline="") as f:
            read_content = f.read()
        self.assertEqual(read_content, content)

    def test_write_html_file(self):
        """Test writing HTML file."""
        output_path = Path(self.test_dir) / "test.html"
        content = "<html><body>Test Report</body></html>"

        OutputWriter.write_to_file(output_path, content, "html")

        # Verify file exists
        self.assertTrue(output_path.exists())

        # Verify content
        with open(output_path, "r", encoding="utf-8") as f:
            read_content = f.read()
        self.assertEqual(read_content, content)

    def test_write_json_file(self):
        """Test writing JSON file."""
        output_path = Path(self.test_dir) / "test.json"
        content = '{\n  "test": "data"\n}'

        OutputWriter.write_to_file(output_path, content, "json")

        # Verify file exists
        self.assertTrue(output_path.exists())

        # Verify content
        with open(output_path, "r", encoding="utf-8") as f:
            read_content = f.read()
        self.assertEqual(read_content, content)

    def test_write_creates_parent_directories(self):
        """Test that parent directories are created automatically."""
        output_path = Path(self.test_dir) / "subdir1" / "subdir2" / "test.json"
        content = '{"test": "data"}'

        OutputWriter.write_to_file(output_path, content, "json")

        # Verify file exists
        self.assertTrue(output_path.exists())

        # Verify parent directories were created
        self.assertTrue(output_path.parent.exists())
        self.assertTrue(output_path.parent.parent.exists())

    def test_write_overwrites_existing_file(self):
        """Test that existing files are overwritten."""
        output_path = Path(self.test_dir) / "test.json"

        # Write initial content
        OutputWriter.write_to_file(output_path, "old content", "json")

        # Overwrite with new content
        new_content = "new content"
        OutputWriter.write_to_file(output_path, new_content, "json")

        # Verify new content
        with open(output_path, "r", encoding="utf-8") as f:
            read_content = f.read()
        self.assertEqual(read_content, new_content)


@pytest.mark.unit
@pytest.mark.security
class TestOutputWriterSecurity(unittest.TestCase):
    """Test security validation in file writing."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_to_file_rejects_path_traversal(self):
        """Test that write_to_file rejects path traversal attempts."""
        malicious_paths = [
            "../../etc/passwd",
            "../../../etc/passwd",
            "subdir/../../etc/passwd",
        ]

        for malicious_path in malicious_paths:
            with self.subTest(path=malicious_path):
                with self.assertRaises(ValueError) as ctx:
                    OutputWriter.write_to_file(Path(malicious_path), "content", "json")
                # Verify error message mentions path traversal
                error_msg = str(ctx.exception)
                self.assertTrue(
                    ".." in error_msg or "traversal" in error_msg.lower(),
                    f"Expected path traversal error for {malicious_path}, got: {error_msg}",
                )

    def test_write_to_file_rejects_url_encoded_paths(self):
        """Test that write_to_file rejects URL-encoded malicious paths."""
        malicious_paths = [
            "%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # ../../etc/passwd
            "test%2e%2e%2fmalicious.json",  # test../malicious.json
        ]

        for malicious_path in malicious_paths:
            with self.subTest(path=malicious_path):
                with self.assertRaises(ValueError) as ctx:
                    OutputWriter.write_to_file(Path(malicious_path), "content", "json")
                # Verify error message mentions URL encoding
                error_msg = str(ctx.exception)
                self.assertTrue(
                    "URL" in error_msg
                    or "%" in error_msg
                    or "encoded" in error_msg.lower(),
                    f"Expected URL encoding error for {malicious_path}, got: {error_msg}",
                )

    def test_write_to_file_rejects_system_directories(self):
        """Test that write_to_file rejects system directory access."""
        system_paths = [
            "/etc/vscan/malicious.json",
            "/sys/kernel/test.json",
            "/proc/self/malicious.json",
        ]

        for system_path in system_paths:
            with self.subTest(path=system_path):
                with self.assertRaises(ValueError) as ctx:
                    OutputWriter.write_to_file(Path(system_path), "content", "json")
                # Verify error message mentions system directories
                error_msg = str(ctx.exception)
                self.assertTrue(
                    "system" in error_msg.lower(),
                    f"Expected system directory error for {system_path}, got: {error_msg}",
                )

    def test_write_to_file_accepts_valid_paths(self):
        """Test that write_to_file accepts valid, safe paths."""
        valid_paths = [
            Path(self.test_dir) / "report.json",
            Path(self.test_dir) / "subdir" / "report.html",
            Path(self.test_dir) / "data" / "output.csv",
        ]

        for valid_path in valid_paths:
            with self.subTest(path=str(valid_path)):
                # Should not raise
                OutputWriter.write_to_file(valid_path, '{"test": "data"}', "json")
                self.assertTrue(valid_path.exists())


@pytest.mark.unit
class TestOutputWriterHelperMethods(unittest.TestCase):
    """Test helper methods (message generation, logging)."""

    def setUp(self):
        """Set up test fixtures."""
        self.writer = OutputWriter()

    def test_get_format_message_csv_generating(self):
        """Test format message for CSV generation."""
        result = self.writer._get_format_message("csv", "generating")
        self.assertEqual(result, "Generating csv export...")

    def test_get_format_message_csv_written(self):
        """Test format message for CSV written."""
        result = self.writer._get_format_message("csv", "written")
        self.assertEqual(result, "CSV export written to")

    def test_get_format_message_html_generating(self):
        """Test format message for HTML generation."""
        result = self.writer._get_format_message("html", "generating")
        self.assertEqual(result, "Generating html report...")

    def test_get_format_message_html_written(self):
        """Test format message for HTML written."""
        result = self.writer._get_format_message("html", "written")
        self.assertEqual(result, "HTML report written to")

    def test_get_format_message_json_generating(self):
        """Test format message for JSON generation."""
        result = self.writer._get_format_message("json", "generating")
        self.assertEqual(result, "Generating results...")

    def test_get_format_message_json_written(self):
        """Test format message for JSON written."""
        result = self.writer._get_format_message("json", "written")
        self.assertEqual(result, "Results written to")

    @patch("vscode_scanner.output_writer.display_info")
    @patch("vscode_scanner.output_writer.log")
    def test_log_progress_generating_rich(self, mock_log, mock_display_info):
        """Test logging progress message with rich display (generating)."""
        self.writer._log_progress(
            "Generating CSV export...", "/path/to/output.csv", True, "generating"
        )

        mock_display_info.assert_called_once_with(
            "Generating CSV export...", use_rich=True
        )
        mock_log.assert_not_called()

    @patch("vscode_scanner.output_writer.display_info")
    @patch("vscode_scanner.output_writer.log")
    def test_log_progress_generating_plain(self, mock_log, mock_display_info):
        """Test logging progress message without rich display (generating)."""
        self.writer._log_progress(
            "Generating CSV export...", "/path/to/output.csv", False, "generating"
        )

        mock_log.assert_called_once_with("Generating CSV export...", "INFO")
        mock_display_info.assert_not_called()

    @patch("vscode_scanner.output_writer.display_success")
    @patch("vscode_scanner.output_writer.log")
    @patch("vscode_scanner.output_writer.sanitize_string")
    def test_log_progress_written_rich(
        self, mock_sanitize, mock_log, mock_display_success
    ):
        """Test logging success message with rich display (written)."""
        mock_sanitize.return_value = "/path/to/output.csv"

        self.writer._log_progress(
            "CSV export written to", "/path/to/output.csv", True, "written"
        )

        mock_sanitize.assert_called_once_with("/path/to/output.csv", max_length=100)
        mock_display_success.assert_called_once_with(
            "CSV export written to /path/to/output.csv", use_rich=True
        )
        mock_log.assert_not_called()

    @patch("vscode_scanner.output_writer.display_success")
    @patch("vscode_scanner.output_writer.log")
    @patch("vscode_scanner.output_writer.sanitize_string")
    def test_log_progress_written_plain(
        self, mock_sanitize, mock_log, mock_display_success
    ):
        """Test logging success message without rich display (written)."""
        mock_sanitize.return_value = "/path/to/output.csv"

        self.writer._log_progress(
            "CSV export written to", "/path/to/output.csv", False, "written"
        )

        mock_sanitize.assert_called_once_with("/path/to/output.csv", max_length=100)
        mock_log.assert_called_once_with(
            "CSV export written to /path/to/output.csv", "SUCCESS"
        )
        mock_display_success.assert_not_called()


@pytest.mark.unit
class TestOutputWriterOrchestration(unittest.TestCase):
    """Test output orchestration (integration of all components)."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.mock_formatter = Mock()
        self.mock_html_gen = Mock()
        self.writer = OutputWriter(
            output_formatter=self.mock_formatter, html_generator=self.mock_html_gen
        )
        self.test_results = {
            "extensions": [{"id": "test.ext1"}],
            "scan_summary": {"total": 1},
        }

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("vscode_scanner.output_writer.display_info")
    @patch("vscode_scanner.output_writer.display_success")
    @patch("vscode_scanner.output_writer.sanitize_string")
    def test_write_output_csv(self, mock_sanitize, mock_success, mock_info):
        """Test complete CSV output workflow."""
        output_path = str(Path(self.test_dir) / "report.csv")
        mock_sanitize.return_value = output_path
        self.mock_formatter.format_csv.return_value = "id,name\ntest.ext1,ext1"

        format_type = self.writer.write_output(output_path, self.test_results, True)

        # Verify format detection
        self.assertEqual(format_type, "csv")

        # Verify progress logging
        mock_info.assert_called_once_with("Generating csv export...", use_rich=True)
        mock_success.assert_called_once()

        # Verify file was written
        self.assertTrue(Path(output_path).exists())

    @patch("vscode_scanner.output_writer.display_info")
    @patch("vscode_scanner.output_writer.display_success")
    @patch("vscode_scanner.output_writer.sanitize_string")
    def test_write_output_html(self, mock_sanitize, mock_success, mock_info):
        """Test complete HTML output workflow."""
        output_path = str(Path(self.test_dir) / "report.html")
        mock_sanitize.return_value = output_path
        self.mock_html_gen.generate_report.return_value = "<html></html>"

        format_type = self.writer.write_output(output_path, self.test_results, True)

        # Verify format detection
        self.assertEqual(format_type, "html")

        # Verify progress logging
        mock_info.assert_called_once_with("Generating html report...", use_rich=True)
        mock_success.assert_called_once()

        # Verify file was written
        self.assertTrue(Path(output_path).exists())

    @patch("vscode_scanner.output_writer.log")
    def test_write_output_json_plain(self, mock_log):
        """Test complete JSON output workflow without rich display."""
        output_path = str(Path(self.test_dir) / "output.json")

        format_type = self.writer.write_output(output_path, self.test_results, False)

        # Verify format detection
        self.assertEqual(format_type, "json")

        # Verify logging calls
        self.assertEqual(mock_log.call_count, 2)  # INFO + SUCCESS
        info_call = mock_log.call_args_list[0]
        self.assertIn("Generating", info_call[0][0])
        self.assertEqual(info_call[0][1], "INFO")

        # Verify file was written
        self.assertTrue(Path(output_path).exists())

        # Verify JSON content
        with open(output_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, self.test_results)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOutputWriterFormatDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputWriterContentGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputWriterFileWriting))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputWriterSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputWriterHelperMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputWriterOrchestration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
