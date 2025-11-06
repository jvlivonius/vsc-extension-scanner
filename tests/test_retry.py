#!/usr/bin/env python3
"""
Retry Mechanism Test Suite

Tests the intelligent retry mechanism for handling transient API errors.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

import pytest
import time
import urllib.error

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner.vscan_api import VscanAPIClient


@pytest.mark.integration
class TestRetryMechanism(unittest.TestCase):
    """Test suite for retry mechanism."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = VscanAPIClient(
            delay=0.1,  # Short delay for testing
            verbose=False,
            max_retries=3,
            retry_base_delay=0.1,  # Short delay for testing
        )

    def test_successful_request_no_retries(self):
        """Test 1: Successful request should not trigger any retries."""
        with patch.object(self.client, "_make_request") as mock_request:
            mock_request.return_value = (200, {"analysisId": "test-123"})

            result = self.client._make_request_with_retry(
                "https://test.com/api", method="POST", data={"test": "data"}
            )

            # Should only be called once (no retries)
            self.assertEqual(mock_request.call_count, 1)
            self.assertEqual(result[0], 200)
            self.assertEqual(result[1]["analysisId"], "test-123")

            # Verify retry stats
            stats = self.client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 0)
            self.assertEqual(stats["successful_retries"], 0)
            self.assertEqual(stats["failed_after_retries"], 0)

    def test_single_retry_success(self):
        """Test 2: Single retry should succeed after one failure."""
        with patch.object(self.client, "_make_request") as mock_request:
            # First call fails with 503, second succeeds
            mock_request.side_effect = [
                Exception("vscan.dev server error (HTTP 503)"),
                (200, {"analysisId": "test-456"}),
            ]

            result = self.client._make_request_with_retry(
                "https://test.com/api", method="GET"
            )

            # Should be called twice (1 original + 1 retry)
            self.assertEqual(mock_request.call_count, 2)
            self.assertEqual(result[0], 200)

            # Verify retry stats
            stats = self.client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 1)

    @pytest.mark.slow
    def test_multiple_retries_success(self):
        """Test 3: Multiple retries should eventually succeed."""
        with patch.object(self.client, "_make_request") as mock_request:
            # First 3 calls fail, 4th succeeds
            mock_request.side_effect = [
                Exception("vscan.dev server error (HTTP 502)"),
                Exception("vscan.dev server error (HTTP 503)"),
                Exception("vscan.dev server error (HTTP 504)"),
                (200, {"status": "completed"}),
            ]

            result = self.client._make_request_with_retry(
                "https://test.com/api", method="GET"
            )

            # Should be called 4 times (1 original + 3 retries)
            self.assertEqual(mock_request.call_count, 4)
            self.assertEqual(result[0], 200)

            # Verify retry stats
            stats = self.client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 3)

    @pytest.mark.slow
    def test_max_retries_exceeded(self):
        """Test 4: Should fail after max retries exceeded."""
        with patch.object(self.client, "_make_request") as mock_request:
            # All calls fail
            mock_request.side_effect = Exception("vscan.dev server error (HTTP 503)")

            with self.assertRaises(Exception) as context:
                self.client._make_request_with_retry(
                    "https://test.com/api", method="GET"
                )

            self.assertIn("503", str(context.exception))

            # Should be called 4 times (1 original + 3 retries)
            self.assertEqual(mock_request.call_count, 4)

            # Verify retry stats
            stats = self.client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 3)
            self.assertEqual(stats["failed_after_retries"], 1)

    def test_non_retryable_error(self):
        """Test 5: Non-retryable errors should fail immediately."""
        with patch.object(self.client, "_make_request") as mock_request:
            # 404 is not retryable
            mock_request.side_effect = Exception("Extension not found on vscan.dev")

            with self.assertRaises(Exception) as context:
                self.client._make_request_with_retry(
                    "https://test.com/api", method="GET"
                )

            self.assertIn("not found", str(context.exception))

            # Should only be called once (no retries for 404)
            self.assertEqual(mock_request.call_count, 1)

            # Verify no retries attempted
            stats = self.client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 0)

    def test_rate_limiting_retry(self):
        """Test 6: Rate limiting (HTTP 429) should trigger retry."""
        with patch.object(self.client, "_make_request") as mock_request:
            # First call hits rate limit, second succeeds
            mock_request.side_effect = [
                Exception("Rate limit exceeded. Please try again later."),
                (200, {"analysisId": "test-789"}),
            ]

            result = self.client._make_request_with_retry(
                "https://test.com/api", method="POST", data={"test": "data"}
            )

            # Should be called twice (1 original + 1 retry)
            self.assertEqual(mock_request.call_count, 2)
            self.assertEqual(result[0], 200)

            # Verify retry stats
            stats = self.client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 1)

    @pytest.mark.slow
    def test_server_errors_retry(self):
        """Test 7: Server errors (502, 503, 504) should trigger retries."""
        test_cases = [
            ("vscan.dev server error (HTTP 502)", True),
            ("vscan.dev server error (HTTP 503)", True),
            ("vscan.dev server error (HTTP 504)", True),
            ("vscan.dev server error (HTTP 500)", False),  # 500 is not retryable
        ]

        for error_msg, should_retry in test_cases:
            with self.subTest(error=error_msg):
                client = VscanAPIClient(max_retries=2, retry_base_delay=0.05)

                with patch.object(client, "_make_request") as mock_request:
                    if should_retry:
                        # Should retry and eventually succeed
                        mock_request.side_effect = [
                            Exception(error_msg),
                            (200, {"result": "ok"}),
                        ]
                        result = client._make_request_with_retry("https://test.com/api")
                        self.assertEqual(result[0], 200)
                        self.assertEqual(mock_request.call_count, 2)
                    else:
                        # Should fail immediately
                        mock_request.side_effect = Exception(error_msg)
                        with self.assertRaises(Exception):
                            client._make_request_with_retry("https://test.com/api")
                        self.assertEqual(mock_request.call_count, 1)

    def test_timeout_errors_retry(self):
        """Test 8: Timeout errors should trigger retries."""
        with patch.object(self.client, "_make_request") as mock_request:
            # Simulate timeout then success
            timeout_error = Exception(
                "Request timed out after 30s. The extension may take longer to analyze."
            )
            mock_request.side_effect = [timeout_error, (200, {"status": "completed"})]

            result = self.client._make_request_with_retry(
                "https://test.com/api", method="GET"
            )

            # Should be called twice (1 original + 1 retry)
            self.assertEqual(mock_request.call_count, 2)
            self.assertEqual(result[0], 200)

            # Verify retry stats
            stats = self.client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 1)

    def test_retry_after_header_respect(self):
        """Test 9: Retry-After header should be respected."""
        with patch.object(self.client, "_make_request") as mock_request:
            # Create HTTPError with Retry-After header
            http_error = urllib.error.HTTPError(
                url="https://test.com/api",
                code=429,
                msg="Too Many Requests",
                hdrs={"Retry-After": "5"},
                fp=None,
            )
            http_error.read = lambda: b'{"error": "rate limited"}'
            http_error.headers = {"Retry-After": "5"}

            mock_request.side_effect = [http_error, (200, {"result": "success"})]

            # Mock time.sleep to avoid actual delay
            with patch("time.sleep") as mock_sleep:
                result = self.client._make_request_with_retry(
                    "https://test.com/api", method="GET"
                )

                # Verify retry occurred
                self.assertEqual(mock_request.call_count, 2)
                self.assertEqual(result[0], 200)

                # Verify sleep was called with Retry-After value
                # Note: actual delay includes jitter, but base should be from header
                self.assertTrue(mock_sleep.called)
                # Sleep should be called with ~5 seconds (Retry-After value)
                sleep_call_args = mock_sleep.call_args[0][0]
                self.assertGreaterEqual(sleep_call_args, 5.0)
                self.assertLess(sleep_call_args, 6.0)  # 5s + max jitter (1s)

    def test_is_retryable_error(self):
        """Test error classification logic."""
        # Retryable errors
        retryable_cases = [
            (Exception("Rate limit exceeded"), None, True),
            (Exception("vscan.dev server error (HTTP 502)"), 502, True),
            (Exception("vscan.dev server error (HTTP 503)"), 503, True),
            (Exception("vscan.dev server error (HTTP 504)"), 504, True),
            (Exception("Request timed out"), None, True),
            (Exception("Connection refused"), None, True),
        ]

        for error, status_code, expected in retryable_cases:
            with self.subTest(error=str(error)):
                result = self.client._is_retryable_error(error, status_code)
                self.assertEqual(result, expected, f"Expected {expected} for {error}")

        # Non-retryable errors
        non_retryable_cases = [
            (Exception("Extension not found"), 404, False),
            (Exception("vscan.dev server error (HTTP 500)"), 500, False),
            (Exception("Bad request"), 400, False),
            (Exception("Unauthorized"), 401, False),
        ]

        for error, status_code, expected in non_retryable_cases:
            with self.subTest(error=str(error)):
                result = self.client._is_retryable_error(error, status_code)
                self.assertEqual(result, expected, f"Expected {expected} for {error}")

    def test_calculate_backoff_delay(self):
        """Test exponential backoff calculation."""
        # Test exponential growth
        delay_0 = self.client._calculate_backoff_delay(0)
        delay_1 = self.client._calculate_backoff_delay(1)
        delay_2 = self.client._calculate_backoff_delay(2)

        # Base delay * 2^attempt + jitter (0-1s)
        # attempt 0: 0.1 * 2^0 = 0.1 + jitter -> 0.1-1.1
        # attempt 1: 0.1 * 2^1 = 0.2 + jitter -> 0.2-1.2
        # attempt 2: 0.1 * 2^2 = 0.4 + jitter -> 0.4-1.4

        self.assertGreaterEqual(delay_0, 0.1)
        self.assertLess(delay_0, 1.2)

        self.assertGreaterEqual(delay_1, 0.2)
        self.assertLess(delay_1, 1.3)

        self.assertGreaterEqual(delay_2, 0.4)
        self.assertLess(delay_2, 1.5)

        # Test Retry-After header override
        retry_after_delay = self.client._calculate_backoff_delay(0, retry_after=10)
        self.assertEqual(retry_after_delay, 10.0)

    @pytest.mark.slow
    def test_retry_stats_tracking(self):
        """Test retry statistics are tracked correctly."""
        client = VscanAPIClient(max_retries=2, retry_base_delay=0.05)

        # Scenario 1: Successful retry
        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = [
                Exception("vscan.dev server error (HTTP 503)"),
                (200, {"result": "ok"}),
            ]
            client._make_request_with_retry("https://test.com/api")

        stats = client.get_retry_stats()
        self.assertEqual(stats["total_retries"], 1)

        # Scenario 2: Failed after retries
        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = Exception("vscan.dev server error (HTTP 503)")
            try:
                client._make_request_with_retry("https://test.com/api")
            except Exception:
                pass

        stats = client.get_retry_stats()
        self.assertEqual(stats["total_retries"], 3)  # 1 + 2 more
        self.assertEqual(stats["failed_after_retries"], 1)

    def test_retry_with_zero_max_retries(self):
        """Test that retries are disabled when max_retries=0."""
        client = VscanAPIClient(max_retries=0)

        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = Exception("vscan.dev server error (HTTP 503)")

            with self.assertRaises(Exception):
                client._make_request_with_retry("https://test.com/api")

            # Should only be called once (no retries)
            self.assertEqual(mock_request.call_count, 1)

            # No retries should be tracked
            stats = client.get_retry_stats()
            self.assertEqual(stats["total_retries"], 0)


@pytest.mark.integration
class TestRetryIntegration(unittest.TestCase):
    """Integration tests for retry mechanism with actual API methods."""

    def test_submit_analysis_with_retry(self):
        """Test submit_analysis uses retry wrapper."""
        client = VscanAPIClient(max_retries=2, retry_base_delay=0.05)

        with patch.object(client, "_make_request") as mock_request:
            # First call fails, second succeeds
            mock_request.side_effect = [
                Exception("vscan.dev server error (HTTP 503)"),
                (202, {"analysisId": "test-integration-123"}),
            ]

            result = client.submit_analysis("test-publisher", "test-extension")

            # Should retry and succeed
            self.assertEqual(result, "test-integration-123")
            self.assertEqual(mock_request.call_count, 2)

    def test_check_status_with_retry(self):
        """Test check_status uses retry wrapper."""
        client = VscanAPIClient(max_retries=2, retry_base_delay=0.05)

        with patch.object(client, "_make_request") as mock_request:
            # First call fails, second succeeds
            mock_request.side_effect = [
                Exception("Request timed out after 30s"),
                (200, {"status": "completed", "progress": 100}),
            ]

            result = client.check_status("test-analysis-id")

            # Should retry and succeed
            self.assertEqual(result["status"], "completed")
            self.assertEqual(mock_request.call_count, 2)

    def test_get_results_with_retry(self):
        """Test get_results uses retry wrapper."""
        client = VscanAPIClient(max_retries=2, retry_base_delay=0.05)

        with patch.object(client, "_make_request") as mock_request:
            # First call fails, second succeeds
            mock_request.side_effect = [
                Exception("vscan.dev server error (HTTP 502)"),
                (200, {"securityScore": {"score": 85}}),
            ]

            result = client.get_results("test-analysis-id")

            # Should retry and succeed
            self.assertEqual(result["securityScore"]["score"], 85)
            self.assertEqual(mock_request.call_count, 2)


def main():
    """Run test suite."""
    print("=" * 70)
    print("Retry Mechanism Test Suite")
    print("=" * 70)
    print()

    # Run tests with verbose output
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all tests
    suite.addTests(loader.loadTestsFromTestCase(TestRetryMechanism))
    suite.addTests(loader.loadTestsFromTestCase(TestRetryIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 70)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
