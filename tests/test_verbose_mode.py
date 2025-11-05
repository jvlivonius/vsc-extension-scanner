#!/usr/bin/env python3
"""
Test suite for enhanced verbose mode (v3.3 Feature 2).

Tests:
- Standard mode hides operational details (cache stats, retry stats, timing)
- Verbose mode shows all operational details
- Quiet mode shows minimal summary (unchanged)
- Both Rich and Plain modes work correctly
"""

import unittest
import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.scanner import _print_summary
from vscode_scanner.display import display_summary


@pytest.mark.integration
class TestVerboseModeStandard(unittest.TestCase):
    """Test standard mode (security-focused, hides operational details)."""

    def test_standard_mode_hides_cache_stats_rich(self):
        """Test that standard mode hides cache statistics in Rich mode."""
        extensions = [{"id": "test.ext", "name": "Test"}]
        stats = {
            "successful_scans": 1,
            "failed_scans": 0,
            "vulnerabilities_found": 0,
            "cached_results": 1,
            "fresh_scans": 0,
            "api_client": None,
        }
        results = {
            "summary": {
                "total_extensions_scanned": 1,
                "vulnerabilities_found": 0,
                "cache_statistics": {
                    "from_cache": 1,
                    "fresh_scans": 0,
                    "cache_hit_rate": 100.0,
                },
            },
            "extensions": [
                {
                    "id": "test.ext",
                    "name": "Test",
                    "scan_status": "success",
                    "security": {"score": 85, "risk_level": "low"},
                }
            ],
        }

        # Capture output
        with patch("sys.stdout", new=io.StringIO()) as mock_stdout:
            with patch("vscode_scanner.scanner.display_summary") as mock_display:
                with patch("vscode_scanner.scanner.create_results_table"):
                    with patch(
                        "vscode_scanner.scanner.create_cache_stats_table"
                    ) as mock_cache_table:
                        # Standard mode (verbose=False)
                        _print_summary(
                            extensions,
                            stats,
                            10.0,
                            use_rich=True,
                            results=results,
                            quiet=False,
                            verbose=False,
                        )

                        # Cache stats table should NOT be called in standard mode
                        mock_cache_table.assert_not_called()


@pytest.mark.integration
class TestVerboseModeVerbose(unittest.TestCase):
    """Test verbose mode (shows all operational details)."""

    def test_verbose_mode_shows_cache_stats_rich(self):
        """Test that verbose mode shows cache statistics in Rich mode."""
        extensions = [{"id": "test.ext", "name": "Test"}]
        stats = {
            "successful_scans": 1,
            "failed_scans": 0,
            "vulnerabilities_found": 0,
            "cached_results": 1,
            "fresh_scans": 0,
        }
        results = {
            "summary": {
                "total_extensions_scanned": 1,
                "vulnerabilities_found": 0,
                "cache_statistics": {
                    "from_cache": 1,
                    "fresh_scans": 0,
                    "cache_hit_rate": 100.0,
                },
            },
            "extensions": [
                {
                    "id": "test.ext",
                    "name": "Test",
                    "scan_status": "success",
                    "security": {"score": 85, "risk_level": "low"},
                }
            ],
        }

        # Capture output
        with patch("sys.stdout", new=io.StringIO()):
            with patch("vscode_scanner.scanner.display_summary") as mock_display:
                with patch("vscode_scanner.scanner.create_results_table"):
                    with patch(
                        "vscode_scanner.scanner.create_cache_stats_table"
                    ) as mock_cache_table:
                        from rich.console import Console

                        with patch.object(Console, "print"):
                            # Configure mock to return something
                            mock_cache_table.return_value = MagicMock()

                            # Verbose mode (verbose=True)
                            _print_summary(
                                extensions,
                                stats,
                                10.0,
                                use_rich=True,
                                results=results,
                                quiet=False,
                                verbose=True,
                            )

                            # Cache stats table SHOULD be called in verbose mode
                            mock_cache_table.assert_called_once()


@pytest.mark.integration
class TestVerboseModeQuiet(unittest.TestCase):
    """Test quiet mode (unchanged behavior)."""

    def test_quiet_mode_minimal_output(self):
        """Test that quiet mode shows minimal single-line summary."""
        extensions = [
            {"id": "test1.ext", "name": "Test1"},
            {"id": "test2.ext", "name": "Test2"},
        ]
        stats = {"vulnerabilities_found": 1}
        results = {}

        # Capture output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            # Quiet mode (quiet=True, verbose doesn't matter)
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

            # Should be a single line
            self.assertEqual(output.count("\n"), 1)

            # Should contain minimal info
            self.assertIn("Scanned 2 extensions", output)
            self.assertIn("Found 1 vulnerabilities", output)

            # Should NOT contain detailed stats
            self.assertNotIn("Cache", output)
            self.assertNotIn("Retry", output)
            self.assertNotIn("Duration", output)
        finally:
            sys.stdout = sys.__stdout__


@pytest.mark.integration
class TestDisplaySummaryVerboseParameter(unittest.TestCase):
    """Test display_summary function verbose parameter."""

    def test_display_summary_hides_retry_stats_standard(self):
        """Test display_summary hides retry stats in standard mode."""
        results = {
            "summary": {"total_extensions_scanned": 5, "vulnerabilities_found": 0}
        }

        retry_stats = {
            "total_retries": 3,
            "successful_retries": 3,
            "failed_after_retries": 0,
            "total_workflow_retries": 0,
        }

        # Capture Rich output
        with patch("vscode_scanner.display.Console") as mock_console:
            with patch("vscode_scanner.display.Panel") as mock_panel:
                # Standard mode (verbose=False)
                display_summary(
                    results, 10.0, retry_stats=retry_stats, use_rich=True, verbose=False
                )

                # Get the content passed to Panel
                call_args = mock_panel.call_args
                content_text = str(call_args[0][0])

                # Should NOT contain retry information
                self.assertNotIn("Retries", content_text)
                self.assertNotIn("🔄", content_text)

    def test_display_summary_shows_retry_stats_verbose(self):
        """Test display_summary shows retry stats in verbose mode."""
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

        # Capture Rich output
        with patch("vscode_scanner.display.Console") as mock_console:
            with patch("vscode_scanner.display.Panel") as mock_panel:
                # Verbose mode (verbose=True)
                display_summary(
                    results, 10.0, retry_stats=retry_stats, use_rich=True, verbose=True
                )

                # Get the content passed to Panel
                call_args = mock_panel.call_args
                content_text = str(call_args[0][0])

                # Should contain retry information
                self.assertIn("Retries", content_text)

    def test_display_summary_hides_timing_standard(self):
        """Test display_summary hides timing in standard mode."""
        results = {
            "summary": {"total_extensions_scanned": 5, "vulnerabilities_found": 0}
        }

        # Capture Rich output
        with patch("vscode_scanner.display.Console") as mock_console:
            with patch("vscode_scanner.display.Panel") as mock_panel:
                # Standard mode (verbose=False)
                display_summary(
                    results, 65.3, retry_stats=None, use_rich=True, verbose=False
                )

                # Get the content passed to Panel
                call_args = mock_panel.call_args
                content_text = str(call_args[0][0])

                # Should NOT contain timing information
                self.assertNotIn("Duration", content_text)
                self.assertNotIn("⏱", content_text)

    def test_display_summary_shows_timing_verbose(self):
        """Test display_summary shows timing in verbose mode."""
        results = {
            "summary": {"total_extensions_scanned": 5, "vulnerabilities_found": 0}
        }

        # Capture Rich output
        with patch("vscode_scanner.display.Console") as mock_console:
            with patch("vscode_scanner.display.Panel") as mock_panel:
                # Verbose mode (verbose=True)
                display_summary(
                    results, 65.3, retry_stats=None, use_rich=True, verbose=True
                )

                # Get the content passed to Panel
                call_args = mock_panel.call_args
                content_text = str(call_args[0][0])

                # Should contain timing information
                self.assertIn("Duration", content_text)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
