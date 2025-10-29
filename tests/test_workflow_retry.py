#!/usr/bin/env python3
"""
Test suite for workflow-level retry functionality.

Tests the new workflow retry mechanism that retries entire scan workflows
when they fail due to transient errors.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.vscan_api import VscanAPIClient
from vscode_scanner.constants import (
    DEFAULT_WORKFLOW_MAX_RETRIES,
    DEFAULT_WORKFLOW_RETRY_DELAY,
    WORKFLOW_RETRYABLE_ERROR_PATTERNS,
)


class TestWorkflowRetry(unittest.TestCase):
    """Test workflow-level retry functionality."""

    def test_workflow_retry_initialization(self):
        """Test that workflow retry parameters are properly initialized."""
        client = VscanAPIClient(max_workflow_retries=3, workflow_retry_delay=2.0)

        self.assertEqual(client.max_workflow_retries, 3)
        self.assertEqual(client.workflow_retry_delay, 2.0)

        # Verify workflow retry stats are initialized
        self.assertEqual(client.retry_stats["total_workflow_retries"], 0)
        self.assertEqual(client.retry_stats["successful_workflow_retries"], 0)
        self.assertEqual(client.retry_stats["failed_after_workflow_retries"], 0)

    def test_workflow_retry_default_values(self):
        """Test default workflow retry configuration."""
        client = VscanAPIClient()

        self.assertEqual(client.max_workflow_retries, DEFAULT_WORKFLOW_MAX_RETRIES)
        self.assertEqual(client.workflow_retry_delay, DEFAULT_WORKFLOW_RETRY_DELAY)

    def test_is_workflow_retryable_error(self):
        """Test workflow retryable error classification."""
        client = VscanAPIClient()

        # Retryable errors
        self.assertTrue(
            client._is_workflow_retryable_error(
                "Rate limit exceeded. Please try again later."
            )
        )
        self.assertTrue(
            client._is_workflow_retryable_error("vscan.dev server error (HTTP 503)")
        )
        self.assertTrue(client._is_workflow_retryable_error("Gateway Timeout"))
        self.assertTrue(
            client._is_workflow_retryable_error("Request timeout after 30s")
        )
        self.assertTrue(
            client._is_workflow_retryable_error("Analysis timeout after 300s")
        )

        # Non-retryable errors
        self.assertFalse(
            client._is_workflow_retryable_error("Extension not found on vscan.dev")
        )
        self.assertFalse(client._is_workflow_retryable_error("HTTP error 400"))
        self.assertFalse(client._is_workflow_retryable_error("Invalid extension name"))
        self.assertFalse(client._is_workflow_retryable_error(""))
        self.assertFalse(client._is_workflow_retryable_error(None))

    def test_workflow_retry_success_on_first_attempt(self):
        """Test that no workflow retry occurs when first attempt succeeds."""
        client = VscanAPIClient(max_workflow_retries=2)

        # Mock scan_extension to return success immediately
        successful_result = {"scan_status": "success", "security_score": 85}

        with patch.object(
            client, "scan_extension", return_value=successful_result
        ) as mock_scan:
            result = client.scan_extension_with_retry("test", "ext")

            # Verify only called once (no retries)
            self.assertEqual(mock_scan.call_count, 1)
            self.assertEqual(result["scan_status"], "success")

            # Verify no workflow retries were counted
            stats = client.get_retry_stats()
            self.assertEqual(stats["total_workflow_retries"], 0)
            self.assertEqual(stats["successful_workflow_retries"], 0)

    def test_workflow_retry_succeeds_after_one_retry(self):
        """Test successful workflow retry after one failure."""
        client = VscanAPIClient(max_workflow_retries=2, workflow_retry_delay=0.1)

        # Mock scan_extension: fail once with retryable error, then succeed
        mock_scan_results = [
            {
                "scan_status": "error",
                "error": "Rate limit exceeded. Please try again later.",
            },
            {"scan_status": "success", "security_score": 85},
        ]

        with patch.object(
            client, "scan_extension", side_effect=mock_scan_results
        ) as mock_scan:
            start_time = time.time()
            result = client.scan_extension_with_retry("test", "ext")
            elapsed = time.time() - start_time

            # Verify called twice (1 attempt + 1 retry)
            self.assertEqual(mock_scan.call_count, 2)
            self.assertEqual(result["scan_status"], "success")

            # Verify delay occurred (should be at least 0.1s for one retry)
            self.assertGreaterEqual(elapsed, 0.1)

            # Verify workflow retry stats
            stats = client.get_retry_stats()
            self.assertEqual(stats["total_workflow_retries"], 1)
            self.assertEqual(stats["successful_workflow_retries"], 1)
            self.assertEqual(stats["failed_after_workflow_retries"], 0)

    def test_workflow_retry_fails_after_all_attempts(self):
        """Test that workflow retry fails after exhausting all attempts."""
        client = VscanAPIClient(max_workflow_retries=2, workflow_retry_delay=0.1)

        # Mock scan_extension to always fail with retryable error
        error_result = {
            "scan_status": "error",
            "error": "vscan.dev server error (HTTP 503)",
        }

        with patch.object(
            client, "scan_extension", return_value=error_result
        ) as mock_scan:
            result = client.scan_extension_with_retry("test", "ext")

            # Verify called 3 times (1 initial + 2 retries)
            self.assertEqual(mock_scan.call_count, 3)
            self.assertEqual(result["scan_status"], "error")

            # Verify workflow retry stats
            stats = client.get_retry_stats()
            self.assertEqual(stats["total_workflow_retries"], 2)
            self.assertEqual(stats["successful_workflow_retries"], 0)
            self.assertEqual(stats["failed_after_workflow_retries"], 1)

    def test_workflow_retry_non_retryable_error_no_retry(self):
        """Test that non-retryable errors don't trigger workflow retry."""
        client = VscanAPIClient(max_workflow_retries=2)

        # Mock scan_extension to return non-retryable error
        error_result = {
            "scan_status": "error",
            "error": "Extension not found on vscan.dev",
        }

        with patch.object(
            client, "scan_extension", return_value=error_result
        ) as mock_scan:
            result = client.scan_extension_with_retry("test", "ext")

            # Verify only called once (no retries for non-retryable error)
            self.assertEqual(mock_scan.call_count, 1)
            self.assertEqual(result["scan_status"], "error")

            # Verify no workflow retries occurred
            stats = client.get_retry_stats()
            self.assertEqual(stats["total_workflow_retries"], 0)
            self.assertEqual(stats["failed_after_workflow_retries"], 0)

    def test_workflow_retry_exponential_backoff(self):
        """Test that workflow retry uses exponential backoff."""
        client = VscanAPIClient(max_workflow_retries=2, workflow_retry_delay=1.0)

        error_result = {"scan_status": "error", "error": "Rate limit exceeded"}

        with patch.object(client, "scan_extension", return_value=error_result):
            with patch("time.sleep") as mock_sleep:
                client.scan_extension_with_retry("test", "ext")

                # Verify exponential backoff delays
                # First retry: 1.0 * (2^0) = 1.0s
                # Second retry: 1.0 * (2^1) = 2.0s
                calls = mock_sleep.call_args_list
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[0][0][0], 1.0)  # First retry delay
                self.assertEqual(calls[1][0][0], 2.0)  # Second retry delay

    def test_workflow_retry_stats_accumulate(self):
        """Test that workflow retry stats accumulate across multiple scans."""
        client = VscanAPIClient(max_workflow_retries=1, workflow_retry_delay=0.1)

        # First scan: fail then succeed
        with patch.object(
            client,
            "scan_extension",
            side_effect=[
                {"scan_status": "error", "error": "Rate limit exceeded"},
                {"scan_status": "success"},
            ],
        ):
            client.scan_extension_with_retry("test1", "ext1")

        # Second scan: succeed immediately
        with patch.object(
            client, "scan_extension", return_value={"scan_status": "success"}
        ):
            client.scan_extension_with_retry("test2", "ext2")

        # Third scan: fail all attempts
        with patch.object(
            client,
            "scan_extension",
            return_value={"scan_status": "error", "error": "Rate limit exceeded"},
        ):
            client.scan_extension_with_retry("test3", "ext3")

        # Verify accumulated stats
        stats = client.get_retry_stats()
        self.assertEqual(stats["total_workflow_retries"], 2)  # scan1: 1, scan3: 1
        self.assertEqual(stats["successful_workflow_retries"], 1)  # scan1 recovered
        self.assertEqual(stats["failed_after_workflow_retries"], 1)  # scan3 failed

    def test_workflow_retry_with_zero_max_retries(self):
        """Test that workflow retry can be disabled with max_retries=0."""
        client = VscanAPIClient(max_workflow_retries=0)

        error_result = {"scan_status": "error", "error": "Rate limit exceeded"}

        with patch.object(
            client, "scan_extension", return_value=error_result
        ) as mock_scan:
            result = client.scan_extension_with_retry("test", "ext")

            # Should only call once with no retries
            self.assertEqual(mock_scan.call_count, 1)
            self.assertEqual(result["scan_status"], "error")

            # No workflow retries should be counted
            stats = client.get_retry_stats()
            self.assertEqual(stats["total_workflow_retries"], 0)

    def test_get_retry_stats_includes_workflow_stats(self):
        """Test that get_retry_stats() includes workflow-level statistics."""
        client = VscanAPIClient()

        stats = client.get_retry_stats()

        # Verify all workflow stat keys are present
        self.assertIn("total_workflow_retries", stats)
        self.assertIn("successful_workflow_retries", stats)
        self.assertIn("failed_after_workflow_retries", stats)

        # Verify HTTP stat keys are still present
        self.assertIn("total_retries", stats)
        self.assertIn("successful_retries", stats)
        self.assertIn("failed_after_retries", stats)


if __name__ == "__main__":
    print("=" * 70)
    print("WORKFLOW RETRY TEST SUITE")
    print("=" * 70)
    print()
    print("Testing workflow-level retry functionality that retries entire")
    print("scan workflows when they fail due to transient errors.")
    print()
    print("=" * 70)
    print()

    # Run tests with verbose output
    unittest.main(verbosity=2)
