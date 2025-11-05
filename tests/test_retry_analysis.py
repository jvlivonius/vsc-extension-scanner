#!/usr/bin/env python3
"""
Analysis of retry mechanism behavior.

This test analyzes the retry mechanism to understand why some extensions
are not being scanned after cache refresh.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import urllib.error

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.vscan_api import VscanAPIClient


@pytest.mark.integration
class TestRetryMechanismAnalysis(unittest.TestCase):
    """Analyze retry mechanism behavior."""

    def test_retry_mechanism_flow(self):
        """Test the basic retry mechanism flow."""
        client = VscanAPIClient(max_retries=3, retry_base_delay=0.1)

        # Verify initial stats
        self.assertEqual(client.retry_stats["total_retries"], 0)
        self.assertEqual(client.retry_stats["successful_retries"], 0)
        self.assertEqual(client.retry_stats["failed_after_retries"], 0)

    def test_retryable_error_classification(self):
        """Test which errors are classified as retryable."""
        client = VscanAPIClient()

        # Test retryable status codes
        http_429 = urllib.error.HTTPError("", 429, "Too Many Requests", {}, None)
        self.assertTrue(client._is_retryable_error(http_429, 429))

        http_502 = urllib.error.HTTPError("", 502, "Bad Gateway", {}, None)
        self.assertTrue(client._is_retryable_error(http_502, 502))

        http_503 = urllib.error.HTTPError("", 503, "Service Unavailable", {}, None)
        self.assertTrue(client._is_retryable_error(http_503, 503))

        http_504 = urllib.error.HTTPError("", 504, "Gateway Timeout", {}, None)
        self.assertTrue(client._is_retryable_error(http_504, 504))

        # Test non-retryable status codes
        http_400 = urllib.error.HTTPError("", 400, "Bad Request", {}, None)
        self.assertFalse(client._is_retryable_error(http_400, 400))

        http_404 = urllib.error.HTTPError("", 404, "Not Found", {}, None)
        self.assertFalse(client._is_retryable_error(http_404, 404))

        http_500 = urllib.error.HTTPError("", 500, "Internal Server Error", {}, None)
        self.assertFalse(client._is_retryable_error(http_500, 500))

    def test_scan_extension_error_handling(self):
        """Test how scan_extension handles errors (NO RETRY!)."""
        client = VscanAPIClient(max_retries=3)

        # Mock the internal methods
        with patch.object(client, "submit_analysis") as mock_submit:
            with patch.object(client, "poll_until_complete") as mock_poll:
                with patch.object(client, "get_results") as mock_get:
                    # Simulate a retryable error (503)
                    mock_submit.side_effect = Exception(
                        "vscan.dev server error (HTTP 503)"
                    )

                    # Call scan_extension
                    result = client.scan_extension("test-publisher", "test-extension")

                    # CRITICAL: scan_extension catches ALL exceptions and returns error result
                    # It does NOT propagate the exception, so retries in _make_request_with_retry
                    # won't help here!
                    self.assertEqual(result["scan_status"], "error")
                    self.assertIn("503", result["error"])

                    # Verify the error was caught at scan_extension level
                    mock_submit.assert_called_once()

    def test_make_request_with_retry_behavior(self):
        """Test _make_request_with_retry behavior."""
        client = VscanAPIClient(max_retries=2, retry_base_delay=0.1)

        with patch.object(client, "_make_request") as mock_make_request:
            # Simulate 2 failures then success
            mock_make_request.side_effect = [
                Exception("vscan.dev server error (HTTP 503)"),  # Attempt 1
                Exception("vscan.dev server error (HTTP 503)"),  # Attempt 2
                (200, {"analysisId": "test-id"}),  # Attempt 3 (success)
            ]

            # This should succeed after retries
            status, response = client._make_request_with_retry("https://test.com")

            self.assertEqual(status, 200)
            self.assertEqual(mock_make_request.call_count, 3)
            self.assertEqual(client.retry_stats["total_retries"], 2)

    @pytest.mark.slow
    def test_retry_stats_increment(self):
        """Test that retry stats are properly incremented."""
        client = VscanAPIClient(max_retries=3, retry_base_delay=0.1)

        with patch.object(client, "_make_request") as mock_make_request:
            # All attempts fail with retryable error
            mock_make_request.side_effect = Exception(
                "vscan.dev server error (HTTP 503)"
            )

            try:
                client._make_request_with_retry("https://test.com")
            except Exception:
                pass

            # Should have made 4 attempts (initial + 3 retries)
            self.assertEqual(mock_make_request.call_count, 4)
            self.assertEqual(client.retry_stats["total_retries"], 3)
            self.assertEqual(client.retry_stats["failed_after_retries"], 1)

    def test_critical_issue_scan_extension_no_retry(self):
        """
        CRITICAL ISSUE: scan_extension() catches all exceptions internally!

        The retry mechanism in _make_request_with_retry() works correctly,
        BUT scan_extension() wraps everything in a try-except that catches
        ALL exceptions and returns an error result instead of propagating them.

        This means:
        1. submit_analysis() can retry successfully ✓
        2. check_status() can retry successfully ✓
        3. get_results() can retry successfully ✓
        4. BUT if any step fails after all retries, scan_extension()
           catches it and returns {'scan_status': 'error'} ✗

        The problem is in vscan_api.py lines 744-802:
        - Line 799-802: catch Exception and set scan_status='error'
        - This prevents the scanner from knowing if the error was retryable
        """
        client = VscanAPIClient(max_retries=0)  # No retries for this test

        with patch.object(client, "submit_analysis") as mock_submit:
            # Simulate a transient error that SHOULD be retried
            mock_submit.side_effect = Exception(
                "Rate limit exceeded. Please try again later."
            )

            result = client.scan_extension("test", "ext")

            # The error is caught and returned as error status
            self.assertEqual(result["scan_status"], "error")
            self.assertIn("Rate limit", result["error"])

            # BUT: scan_extension doesn't retry the entire workflow!
            # Only individual API calls (submit_analysis, check_status, get_results) retry
            # If submit_analysis fails after all retries, scan_extension just returns error


if __name__ == "__main__":
    print("=" * 70)
    print("RETRY MECHANISM ANALYSIS")
    print("=" * 70)
    print()
    print("This test analyzes the retry mechanism to identify why some")
    print("extensions are not scanned after cache refresh.")
    print()
    print("=" * 70)
    print()

    # Run tests with verbose output
    unittest.main(verbosity=2)
