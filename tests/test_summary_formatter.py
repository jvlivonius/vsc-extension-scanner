#!/usr/bin/env python3
"""
Unit Tests for SummaryFormatter Module

Tests the pure functions for scan summary formatting logic.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.summary_formatter import SummaryFormatter


@pytest.mark.unit
class TestSummaryFormatterQuietMode(unittest.TestCase):
    """Test quiet mode summary formatting."""

    def test_format_no_vulnerabilities(self):
        """Test quiet summary with no vulnerabilities."""
        result = SummaryFormatter.format_quiet_summary(10, 0)
        self.assertEqual(result, "Scanned 10 extensions - No vulnerabilities found ✓")

    def test_format_with_vulnerabilities(self):
        """Test quiet summary with vulnerabilities."""
        result = SummaryFormatter.format_quiet_summary(5, 3)
        self.assertEqual(result, "Scanned 5 extensions - Found 3 vulnerabilities")

    def test_format_single_extension_no_vulns(self):
        """Test quiet summary with single extension, no vulnerabilities."""
        result = SummaryFormatter.format_quiet_summary(1, 0)
        self.assertEqual(result, "Scanned 1 extensions - No vulnerabilities found ✓")

    def test_format_single_vulnerability(self):
        """Test quiet summary with single vulnerability."""
        result = SummaryFormatter.format_quiet_summary(1, 1)
        self.assertEqual(result, "Scanned 1 extensions - Found 1 vulnerabilities")

    def test_format_zero_extensions(self):
        """Test quiet summary with zero extensions."""
        result = SummaryFormatter.format_quiet_summary(0, 0)
        self.assertEqual(result, "Scanned 0 extensions - No vulnerabilities found ✓")

    def test_format_many_vulnerabilities(self):
        """Test quiet summary with many vulnerabilities."""
        result = SummaryFormatter.format_quiet_summary(100, 50)
        self.assertEqual(result, "Scanned 100 extensions - Found 50 vulnerabilities")


@pytest.mark.unit
class TestSummaryFormatterRetryStats(unittest.TestCase):
    """Test retry stats extraction."""

    def test_extract_retry_stats_present(self):
        """Test extracting retry stats when api_client is present."""
        mock_client = Mock()
        mock_client.get_retry_stats.return_value = {"total_retries": 5}

        stats = {"api_client": mock_client}
        result = SummaryFormatter.extract_retry_stats(stats)

        self.assertEqual(result, {"total_retries": 5})
        mock_client.get_retry_stats.assert_called_once()

    def test_extract_retry_stats_no_client(self):
        """Test extracting retry stats when api_client is missing."""
        stats = {}
        result = SummaryFormatter.extract_retry_stats(stats)
        self.assertIsNone(result)

    def test_extract_retry_stats_none_client(self):
        """Test extracting retry stats when api_client is None."""
        stats = {"api_client": None}
        result = SummaryFormatter.extract_retry_stats(stats)
        self.assertIsNone(result)

    def test_extract_retry_stats_no_method(self):
        """Test extracting retry stats when api_client has no get_retry_stats method."""
        mock_client = Mock(spec=[])  # No methods
        stats = {"api_client": mock_client}

        result = SummaryFormatter.extract_retry_stats(stats)
        self.assertIsNone(result)

    def test_extract_retry_stats_method_raises(self):
        """Test extracting retry stats when get_retry_stats raises exception."""
        mock_client = Mock()
        mock_client.get_retry_stats.side_effect = RuntimeError("API error")

        stats = {"api_client": mock_client}
        result = SummaryFormatter.extract_retry_stats(stats)
        self.assertIsNone(result)


@pytest.mark.unit
class TestSummaryFormatterCacheStats(unittest.TestCase):
    """Test cache stats conditional logic."""

    def test_should_show_cache_stats_verbose_with_stats(self):
        """Test showing cache stats in verbose mode with stats present."""
        results = {"summary": {"cache_statistics": {"hits": 10, "misses": 5}}}
        result = SummaryFormatter.should_show_cache_stats(results, verbose=True)
        self.assertTrue(result)

    def test_should_not_show_cache_stats_not_verbose(self):
        """Test not showing cache stats when not in verbose mode."""
        results = {"summary": {"cache_statistics": {"hits": 10, "misses": 5}}}
        result = SummaryFormatter.should_show_cache_stats(results, verbose=False)
        self.assertFalse(result)

    def test_should_not_show_cache_stats_no_stats(self):
        """Test not showing cache stats when stats are missing."""
        results = {"summary": {}}
        result = SummaryFormatter.should_show_cache_stats(results, verbose=True)
        self.assertFalse(result)

    def test_should_not_show_cache_stats_empty_stats(self):
        """Test not showing cache stats when stats are empty dict."""
        results = {"summary": {"cache_statistics": {}}}
        result = SummaryFormatter.should_show_cache_stats(results, verbose=True)
        self.assertFalse(result)

    def test_should_not_show_cache_stats_no_summary(self):
        """Test not showing cache stats when summary is missing."""
        results = {}
        result = SummaryFormatter.should_show_cache_stats(results, verbose=True)
        self.assertFalse(result)

    def test_get_cache_stats_present(self):
        """Test getting cache stats when present."""
        cache_data = {"hits": 10, "misses": 5}
        results = {"summary": {"cache_statistics": cache_data}}

        result = SummaryFormatter.get_cache_stats(results)
        self.assertEqual(result, cache_data)

    def test_get_cache_stats_missing(self):
        """Test getting cache stats when missing."""
        results = {"summary": {}}
        result = SummaryFormatter.get_cache_stats(results)
        self.assertIsNone(result)


@pytest.mark.unit
class TestSummaryFormatterRetryStatsConditional(unittest.TestCase):
    """Test retry stats conditional logic."""

    def test_should_show_retry_stats_verbose_with_stats(self):
        """Test showing retry stats in verbose mode with stats present."""
        retry_stats = {"total": 5}
        result = SummaryFormatter.should_show_retry_stats(retry_stats, verbose=True)
        self.assertTrue(result)

    def test_should_not_show_retry_stats_not_verbose(self):
        """Test not showing retry stats when not in verbose mode."""
        retry_stats = {"total": 5}
        result = SummaryFormatter.should_show_retry_stats(retry_stats, verbose=False)
        self.assertFalse(result)

    def test_should_not_show_retry_stats_no_stats(self):
        """Test not showing retry stats when stats are None."""
        result = SummaryFormatter.should_show_retry_stats(None, verbose=True)
        self.assertFalse(result)

    def test_should_not_show_retry_stats_not_verbose_no_stats(self):
        """Test not showing retry stats when not verbose and no stats."""
        result = SummaryFormatter.should_show_retry_stats(None, verbose=False)
        self.assertFalse(result)


@pytest.mark.unit
class TestSummaryFormatterScanResults(unittest.TestCase):
    """Test scan results extraction and checking."""

    def test_has_scan_results_with_results(self):
        """Test checking for scan results when present."""
        results = {"extensions": [{"id": "ext1"}]}
        result = SummaryFormatter.has_scan_results(results)
        self.assertTrue(result)

    def test_has_no_scan_results_empty_list(self):
        """Test checking for scan results when list is empty."""
        results = {"extensions": []}
        result = SummaryFormatter.has_scan_results(results)
        self.assertFalse(result)

    def test_has_no_scan_results_missing_key(self):
        """Test checking for scan results when extensions key is missing."""
        results = {}
        result = SummaryFormatter.has_scan_results(results)
        self.assertFalse(result)

    def test_get_scan_results_present(self):
        """Test getting scan results when present."""
        extensions = [{"id": "ext1"}, {"id": "ext2"}]
        results = {"extensions": extensions}

        result = SummaryFormatter.get_scan_results(results)
        self.assertEqual(result, extensions)

    def test_get_scan_results_empty(self):
        """Test getting scan results when empty."""
        results = {"extensions": []}
        result = SummaryFormatter.get_scan_results(results)
        self.assertEqual(result, [])

    def test_get_scan_results_missing(self):
        """Test getting scan results when extensions key is missing."""
        results = {}
        result = SummaryFormatter.get_scan_results(results)
        self.assertEqual(result, [])

    def test_get_scan_results_multiple_extensions(self):
        """Test getting scan results with multiple extensions."""
        extensions = [
            {"id": "ext1", "security": {"score": 85}},
            {"id": "ext2", "security": {"score": 70}},
            {"id": "ext3", "security": {"score": 90}},
        ]
        results = {"extensions": extensions}

        result = SummaryFormatter.get_scan_results(results)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, extensions)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSummaryFormatterQuietMode))
    suite.addTests(loader.loadTestsFromTestCase(TestSummaryFormatterRetryStats))
    suite.addTests(loader.loadTestsFromTestCase(TestSummaryFormatterCacheStats))
    suite.addTests(
        loader.loadTestsFromTestCase(TestSummaryFormatterRetryStatsConditional)
    )
    suite.addTests(loader.loadTestsFromTestCase(TestSummaryFormatterScanResults))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
