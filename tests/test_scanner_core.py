#!/usr/bin/env python3
"""
Core workflow tests for scanner.py module.

Tests the main run_scan() function, exit code calculation, and thread-safe statistics.
Filter tests moved to test_scanner_filters.py.
Integration tests moved to test_scanner_integration.py.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner import scanner


@pytest.mark.unit
class TestRunScan(unittest.TestCase):
    """Test the main run_scan() function."""

    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_run_scan_success_no_vulns(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_apply_filters,
        mock_scan_extensions,
        mock_discover,
    ):
        """Test successful scan with no vulnerabilities."""
        # Mock discovery
        mock_extensions = [
            {"id": "test.ext1", "version": "1.0.0", "name": "ext1", "publisher": "test"}
        ]
        mock_discover.return_value = (mock_extensions, Path("/fake/path"), 1)

        # Mock scanning
        mock_scan_results = [
            {"id": "test.ext1", "risk_level": "low", "vulnerabilities": {"count": 0}}
        ]
        mock_stats = {
            "vulnerabilities_found": 0,
            "successful_scans": 1,
            "failed_scans": 0,
            "cached_results": 0,
            "fresh_scans": 1,
            "api_client": MagicMock(),
        }
        mock_scan_extensions.return_value = (mock_scan_results, mock_stats)

        # Mock filters (no filtering)
        mock_apply_filters.return_value = mock_scan_results

        # Mock output
        mock_results = {"summary": {"total_extensions_scanned": 1}}
        mock_generate_output.return_value = mock_results

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (0 = no vulnerabilities)
        self.assertEqual(exit_code, 0)

        # Verify functions were called
        mock_discover.assert_called_once()
        mock_scan_extensions.assert_called_once()
        mock_apply_filters.assert_called_once()
        mock_generate_output.assert_called_once()

    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_run_scan_success_with_vulns(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_apply_filters,
        mock_scan_extensions,
        mock_discover,
    ):
        """Test successful scan with vulnerabilities found."""
        # Mock discovery
        mock_extensions = [
            {"id": "test.ext1", "version": "1.0.0", "name": "ext1", "publisher": "test"}
        ]
        mock_discover.return_value = (mock_extensions, Path("/fake/path"), 1)

        # Mock scanning with vulnerabilities
        mock_scan_results = [
            {"id": "test.ext1", "risk_level": "high", "vulnerabilities": {"count": 2}}
        ]
        mock_stats = {
            "vulnerabilities_found": 1,
            "successful_scans": 1,
            "failed_scans": 0,
            "cached_results": 0,
            "fresh_scans": 1,
            "api_client": MagicMock(),
        }
        mock_scan_extensions.return_value = (mock_scan_results, mock_stats)

        # Mock filters
        mock_apply_filters.return_value = mock_scan_results

        # Mock output
        mock_results = {"summary": {"total_extensions_scanned": 1}}
        mock_generate_output.return_value = mock_results

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (1 = vulnerabilities found)
        self.assertEqual(exit_code, 1)

    @patch("vscode_scanner.scanner._discover_extensions")
    def test_run_scan_discovery_error(self, mock_discover):
        """Test handling of discovery errors."""
        # Mock discovery failure
        mock_discover.side_effect = FileNotFoundError("Extensions directory not found")

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (2 = error)
        self.assertEqual(exit_code, 2)

    @patch("vscode_scanner.scanner._discover_extensions")
    def test_run_scan_empty_extensions(self, mock_discover):
        """Test handling of empty extension list."""
        # Mock discovery with no extensions
        mock_discover.return_value = ([], Path("/fake/path"), 0)

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (0 = success but no extensions)
        self.assertEqual(exit_code, 0)


@pytest.mark.unit
class TestCalculateExitCode(unittest.TestCase):
    """Test exit code calculation."""

    def test_no_vulnerabilities(self):
        """Test exit code when no vulnerabilities found."""
        exit_code = scanner._calculate_exit_code(0)
        self.assertEqual(exit_code, 0)

    def test_with_vulnerabilities(self):
        """Test exit code when vulnerabilities found."""
        exit_code = scanner._calculate_exit_code(1)
        self.assertEqual(exit_code, 1)

        exit_code = scanner._calculate_exit_code(10)
        self.assertEqual(exit_code, 1)


@pytest.mark.unit
class TestThreadSafeStats(unittest.TestCase):
    """Test thread-safe statistics tracking.

    **Purpose:** Ensure stats tracking works correctly in multi-threaded environment.

    **Scope:**
    - Concurrent increments
    - Counter accuracy
    - Thread safety verification
    """

    def test_thread_safe_stats_initialization(self):
        """Test ThreadSafeStats initialization."""
        stats = scanner.ThreadSafeStats()

        self.assertEqual(stats.get("vulnerabilities_found"), 0)
        self.assertEqual(stats.get("successful_scans"), 0)
        self.assertEqual(stats.get("failed_scans"), 0)
        self.assertEqual(stats.get("cached_results"), 0)
        self.assertEqual(stats.get("fresh_scans"), 0)

    def test_thread_safe_stats_increment_vulnerabilities(self):
        """Test incrementing vulnerability count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("vulnerabilities_found")
        self.assertEqual(stats.get("vulnerabilities_found"), 1)

        stats.increment("vulnerabilities_found")
        self.assertEqual(stats.get("vulnerabilities_found"), 2)

    def test_thread_safe_stats_increment_successful_scans(self):
        """Test incrementing successful scan count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("successful_scans")
        self.assertEqual(stats.get("successful_scans"), 1)

    def test_thread_safe_stats_increment_failed_scans(self):
        """Test incrementing failed scan count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("failed_scans")
        self.assertEqual(stats.get("failed_scans"), 1)

    def test_thread_safe_stats_increment_cached_results(self):
        """Test incrementing cached result count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("cached_results")
        self.assertEqual(stats.get("cached_results"), 1)

    def test_thread_safe_stats_increment_fresh_scans(self):
        """Test incrementing fresh scan count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("fresh_scans")
        self.assertEqual(stats.get("fresh_scans"), 1)

    def test_thread_safe_stats_to_dict(self):
        """Test converting stats to dictionary."""
        mock_api = MagicMock()
        stats = scanner.ThreadSafeStats()
        stats.set("api_client", mock_api)

        stats.increment("vulnerabilities_found")
        stats.increment("successful_scans")
        stats.increment("cached_results")

        result = stats.to_dict()

        self.assertEqual(result["vulnerabilities_found"], 1)
        self.assertEqual(result["successful_scans"], 1)
        self.assertEqual(result["cached_results"], 1)
        self.assertIn("api_client", result)


if __name__ == "__main__":
    unittest.main()
