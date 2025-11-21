"""
Integration tests for --verbose flag behavior with functional validation.

Tests functional behavior: does --verbose show operational details?
Uses parameter propagation and structural validation patterns.

Pattern: Test behavior (parameter passing), not formatting (emoji/string matching).
Reference: PR #1013 (test_cli_detailed_flag.py) for functional validation approach.

Target: Functional validation, parameter propagation, display logic behavior
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest

try:
    from typer.testing import CliRunner
    from vscode_scanner import cli

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestVerboseFlagParameter(unittest.TestCase):
    """Test --verbose flag parameter propagation through CLI."""

    def setUp(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("vscode_scanner.cli.run_scan")
    def test_verbose_flag_passes_parameter_true(self, mock_run_scan):
        """Test --verbose flag causes verbose=True to be passed to run_scan."""
        # ARRANGE
        mock_run_scan.return_value = 0

        # ACT
        result = self.runner.invoke(
            cli.app, ["scan", "--verbose"], catch_exceptions=False
        )

        # ASSERT
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_run_scan.call_args[1]
        self.assertTrue(call_kwargs.get("verbose", False))

    @patch("vscode_scanner.cli.run_scan")
    def test_without_verbose_flag_passes_parameter_false(self, mock_run_scan):
        """Test without --verbose, verbose=False is passed to run_scan (default)."""
        # ARRANGE
        mock_run_scan.return_value = 0

        # ACT
        result = self.runner.invoke(cli.app, ["scan"], catch_exceptions=False)

        # ASSERT
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_run_scan.call_args[1]
        self.assertFalse(call_kwargs.get("verbose", False))

    @patch("vscode_scanner.cli.run_scan")
    def test_verbose_with_quiet_flag_both_passed(self, mock_run_scan):
        """Test --verbose and --quiet can coexist (both passed to run_scan)."""
        # ARRANGE
        mock_run_scan.return_value = 0

        # ACT
        result = self.runner.invoke(
            cli.app, ["scan", "--verbose", "--quiet"], catch_exceptions=False
        )

        # ASSERT
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_run_scan.call_args[1]
        self.assertTrue(call_kwargs.get("verbose", False))
        self.assertTrue(call_kwargs.get("quiet", False))

    @patch("vscode_scanner.cli.run_scan")
    def test_verbose_with_output_flag_both_passed(self, mock_run_scan):
        """Test --verbose works with --output flag."""
        # ARRANGE
        mock_run_scan.return_value = 0
        import tempfile
        import os

        # ACT
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_verbose.json")
            result = self.runner.invoke(
                cli.app,
                ["scan", "--verbose", "--output", output_path],
                catch_exceptions=False,
            )

            # ASSERT
            self.assertIn(result.exit_code, [0, 1])
            call_kwargs = mock_run_scan.call_args[1]
            self.assertTrue(call_kwargs.get("verbose", False))


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestVerboseDisplayBehavior(unittest.TestCase):
    """Test verbose mode display function behavior."""

    def test_should_show_cache_stats_when_verbose_true(self):
        """Test SummaryFormatter.should_show_cache_stats returns True when verbose=True."""
        # ARRANGE
        from vscode_scanner.summary_formatter import SummaryFormatter

        results = {
            "summary": {
                "total_extensions_scanned": 5,
                "vulnerabilities_found": 0,
                "cache_statistics": {
                    "from_cache": 3,
                    "fresh_scans": 2,
                    "cache_hit_rate": 60.0,
                },
            }
        }

        # ACT
        should_show = SummaryFormatter.should_show_cache_stats(results, verbose=True)

        # ASSERT
        self.assertTrue(should_show)

    def test_should_show_cache_stats_when_verbose_false(self):
        """Test SummaryFormatter.should_show_cache_stats returns False when verbose=False."""
        # ARRANGE
        from vscode_scanner.summary_formatter import SummaryFormatter

        results = {
            "summary": {
                "total_extensions_scanned": 5,
                "vulnerabilities_found": 0,
            }
        }

        # ACT
        should_show = SummaryFormatter.should_show_cache_stats(results, verbose=False)

        # ASSERT
        self.assertFalse(should_show)

    def test_should_show_retry_stats_when_verbose_true(self):
        """Test SummaryFormatter.should_show_retry_stats returns True when verbose=True."""
        # ARRANGE
        from vscode_scanner.summary_formatter import SummaryFormatter

        retry_stats = {
            "total_retries": 3,
            "successful_retries": 3,
            "failed_after_retries": 0,
            "total_workflow_retries": 0,
            "successful_workflow_retries": 0,
            "failed_after_workflow_retries": 0,
        }

        # ACT
        should_show = SummaryFormatter.should_show_retry_stats(
            retry_stats, verbose=True
        )

        # ASSERT
        self.assertTrue(should_show)

    def test_should_show_retry_stats_when_verbose_false(self):
        """Test SummaryFormatter.should_show_retry_stats returns False when verbose=False."""
        # ARRANGE
        from vscode_scanner.summary_formatter import SummaryFormatter

        retry_stats = {
            "total_retries": 3,
            "successful_retries": 3,
            "failed_after_retries": 0,
        }

        # ACT
        should_show = SummaryFormatter.should_show_retry_stats(
            retry_stats, verbose=False
        )

        # ASSERT
        self.assertFalse(should_show)


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.integration
class TestVerboseQuietInteraction(unittest.TestCase):
    """Test verbose and quiet flag interaction behavior."""

    def test_quiet_mode_minimal_output_single_line(self):
        """Test quiet mode shows minimal single-line summary."""
        # ARRANGE
        from vscode_scanner.scanner import _print_summary

        extensions = [
            {"id": "test1.ext", "name": "Test1"},
            {"id": "test2.ext", "name": "Test2"},
        ]
        stats = {"vulnerabilities_found": 1}
        results = {}

        # ACT & ASSERT
        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            _print_summary(
                extensions,
                stats,
                10.0,
                use_rich=False,
                results=results,
                quiet=True,
                verbose=False,
            )

            output = captured_output.getvalue()

            # Verify single line output
            self.assertEqual(output.count("\n"), 1)

            # Verify minimal content (no cache/retry/timing)
            self.assertIn("Scanned 2 extensions", output)
            self.assertIn("Found 1 vulnerabilities", output)
            self.assertNotIn("Cache", output)
            self.assertNotIn("Retry", output)
            self.assertNotIn("Duration", output)
        finally:
            sys.stdout = sys.__stdout__

    def test_verbose_stats_shown_in_display_summary(self):
        """Test that display_summary shows retry/timing info inline when verbose=True."""
        # ARRANGE
        from vscode_scanner.display import display_summary

        results = {
            "summary": {"total_extensions_scanned": 5, "vulnerabilities_found": 0}
        }

        retry_stats = {
            "total_retries": 3,
            "successful_retries": 3,
            "failed_after_retries": 0,
            "total_workflow_retries": 0,
            "successful_workflow_retries": 0,
            "failed_after_workflow_retries": 0,
        }

        # ACT & ASSERT
        with patch("vscode_scanner.display.Panel") as mock_panel:
            with patch("vscode_scanner.display.Console"):
                display_summary(
                    results, 65.3, retry_stats=retry_stats, use_rich=True, verbose=True
                )

                # Verify Panel was called (summary panel created)
                mock_panel.assert_called_once()

                # Get the content passed to Panel
                call_args = mock_panel.call_args
                content_text = str(call_args[0][0])

                # Should contain retry and timing information
                self.assertIn("Retries", content_text)
                self.assertIn("Duration", content_text)


if __name__ == "__main__":
    unittest.main()
