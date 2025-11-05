"""
Error Handling Tests for VscanAPIClient - v3.8.1 Coverage Improvements.

Tests error paths, exception handling, and edge cases to reach 80% coverage
for vscan_api.py module.

Focus areas:
- HTTP error handling (timeouts, connection errors, network failures)
- Response validation (malformed JSON, missing fields, invalid data)
- Status code edge cases (3xx, 4xx, 5xx variations)
- Timing statistics with edge cases
- Workflow retry exhaustion scenarios
"""

import sys
import os
import unittest
import urllib.error
import json
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner.vscan_api import VscanAPIClient


@pytest.mark.unit
class TestHTTPErrorHandling(unittest.TestCase):
    """Test HTTP-level error handling in _make_request()."""

    def test_make_request_handles_timeout_error(self):
        """Test handling of urllib.error.URLError with TimeoutError."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Create URLError with TimeoutError as reason
            timeout_error = TimeoutError("timed out")
            url_error = urllib.error.URLError(timeout_error)
            mock_urlopen.side_effect = url_error

            # Should handle TimeoutError gracefully
            with self.assertRaises(Exception) as context:
                client._make_request("https://example.com/test", method="GET")

            self.assertIn("timed out", str(context.exception).lower())

    def test_make_request_handles_connection_refused(self):
        """Test handling of connection refused errors."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Create URLError with ConnectionRefusedError
            conn_error = ConnectionRefusedError("[Errno 61] Connection refused")
            url_error = urllib.error.URLError(conn_error)
            mock_urlopen.side_effect = url_error

            with self.assertRaises(Exception) as context:
                client._make_request("https://example.com/test", method="GET")

            error_msg = str(context.exception).lower()
            self.assertTrue(
                "network error" in error_msg or "connection" in error_msg,
                f"Expected network/connection error, got: {error_msg}",
            )

    def test_make_request_handles_malformed_json(self):
        """Test handling of malformed JSON responses."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Mock response with invalid JSON (finite stream)
            mock_response = MagicMock()
            mock_response.getcode.return_value = 200
            # Use side_effect to simulate chunked reading with finite data
            mock_response.read.side_effect = [b"<html>Not JSON</html>", b""]
            mock_response.__enter__ = Mock(return_value=mock_response)
            mock_response.__exit__ = Mock(return_value=False)
            mock_urlopen.return_value = mock_response

            # Malformed JSON returns empty dict {}, not an exception
            status_code, json_data = client._make_request(
                "https://example.com/test", method="GET"
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(json_data, {})

    def test_make_request_handles_404_not_found(self):
        """Test handling of 404 Not Found errors."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Create HTTPError with 404 status
            http_error = urllib.error.HTTPError(
                "https://example.com/test",
                404,
                "Not Found",
                {},
                None,
            )
            http_error.read = Mock(return_value=b'{"error": "Extension not found"}')
            mock_urlopen.side_effect = http_error

            with self.assertRaises(Exception) as context:
                client._make_request("https://example.com/test", method="GET")

            error_msg = str(context.exception)
            # 404 returns "Extension not found on vscan.dev"
            self.assertIn("not found", error_msg.lower())

    def test_make_request_handles_500_server_error(self):
        """Test handling of 500 Internal Server Error."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Create HTTPError with 500 status
            http_error = urllib.error.HTTPError(
                "https://example.com/test",
                500,
                "Internal Server Error",
                {},
                None,
            )
            http_error.read = Mock(return_value=b'{"error": "Server error"}')
            mock_urlopen.side_effect = http_error

            with self.assertRaises(Exception) as context:
                client._make_request("https://example.com/test", method="GET")

            error_msg = str(context.exception)
            self.assertIn("500", error_msg)

    def test_make_request_handles_502_bad_gateway(self):
        """Test handling of 502 Bad Gateway (retryable)."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            http_error = urllib.error.HTTPError(
                "https://example.com/test",
                502,
                "Bad Gateway",
                {},
                None,
            )
            http_error.read = Mock(return_value=b'{"error": "Bad Gateway"}')
            mock_urlopen.side_effect = http_error

            with self.assertRaises(Exception) as context:
                client._make_request("https://example.com/test", method="GET")

            self.assertIn("502", str(context.exception))

    def test_make_request_handles_503_service_unavailable(self):
        """Test handling of 503 Service Unavailable (retryable)."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            http_error = urllib.error.HTTPError(
                "https://example.com/test",
                503,
                "Service Unavailable",
                {},
                None,
            )
            http_error.read = Mock(return_value=b'{"error": "Service Unavailable"}')
            mock_urlopen.side_effect = http_error

            with self.assertRaises(Exception) as context:
                client._make_request("https://example.com/test", method="GET")

            self.assertIn("503", str(context.exception))

    def test_make_request_handles_504_gateway_timeout(self):
        """Test handling of 504 Gateway Timeout (retryable)."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            http_error = urllib.error.HTTPError(
                "https://example.com/test",
                504,
                "Gateway Timeout",
                {},
                None,
            )
            http_error.read = Mock(return_value=b'{"error": "Gateway Timeout"}')
            mock_urlopen.side_effect = http_error

            with self.assertRaises(Exception) as context:
                client._make_request("https://example.com/test", method="GET")

            self.assertIn("504", str(context.exception))

    def test_make_request_handles_empty_response_body(self):
        """Test handling of empty response body (204 No Content)."""
        client = VscanAPIClient()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.getcode.return_value = 204
            mock_response.read.return_value = b""
            mock_response.__enter__ = Mock(return_value=mock_response)
            mock_response.__exit__ = Mock(return_value=False)
            mock_urlopen.return_value = mock_response

            # Empty response returns empty dict {}, not an exception
            status_code, json_data = client._make_request(
                "https://example.com/test", method="GET"
            )

            self.assertEqual(status_code, 204)
            self.assertEqual(json_data, {})


@pytest.mark.unit
class TestRetryLogicEdgeCases(unittest.TestCase):
    """Test retry logic edge cases and boundary conditions."""

    def test_is_retryable_error_with_timeout_error(self):
        """Test _is_retryable_error() identifies TimeoutError correctly."""
        client = VscanAPIClient()

        # Create URLError with TimeoutError
        timeout_error = TimeoutError("Connection timed out")
        url_error = urllib.error.URLError(timeout_error)

        result = client._is_retryable_error(url_error, status_code=0)
        self.assertTrue(result, "TimeoutError should be retryable")

    def test_is_retryable_error_with_502_status(self):
        """Test _is_retryable_error() identifies 502 as retryable."""
        client = VscanAPIClient()

        error = Exception("Bad Gateway")
        result = client._is_retryable_error(error, status_code=502)
        self.assertTrue(result, "502 Bad Gateway should be retryable")

    def test_is_retryable_error_with_503_status(self):
        """Test _is_retryable_error() identifies 503 as retryable."""
        client = VscanAPIClient()

        error = Exception("Service Unavailable")
        result = client._is_retryable_error(error, status_code=503)
        self.assertTrue(result, "503 Service Unavailable should be retryable")

    def test_is_retryable_error_with_504_status(self):
        """Test _is_retryable_error() identifies 504 as retryable."""
        client = VscanAPIClient()

        error = Exception("Gateway Timeout")
        result = client._is_retryable_error(error, status_code=504)
        self.assertTrue(result, "504 Gateway Timeout should be retryable")

    def test_is_retryable_error_with_400_status(self):
        """Test _is_retryable_error() identifies 400 as non-retryable."""
        client = VscanAPIClient()

        error = Exception("Bad Request")
        result = client._is_retryable_error(error, status_code=400)
        self.assertFalse(result, "400 Bad Request should not be retryable")

    def test_is_retryable_error_with_401_status(self):
        """Test _is_retryable_error() identifies 401 as non-retryable."""
        client = VscanAPIClient()

        error = Exception("Unauthorized")
        result = client._is_retryable_error(error, status_code=401)
        self.assertFalse(result, "401 Unauthorized should not be retryable")

    def test_is_retryable_error_with_403_status(self):
        """Test _is_retryable_error() identifies 403 as non-retryable."""
        client = VscanAPIClient()

        error = Exception("Forbidden")
        result = client._is_retryable_error(error, status_code=403)
        self.assertFalse(result, "403 Forbidden should not be retryable")

    def test_is_retryable_error_with_500_status(self):
        """Test _is_retryable_error() identifies 500 as non-retryable (explicit)."""
        client = VscanAPIClient()

        error = Exception("Internal Server Error")
        result = client._is_retryable_error(error, status_code=500)
        self.assertFalse(result, "500 Internal Server Error should not be retryable")

    def test_is_retryable_error_with_connection_reset_pattern(self):
        """Test _is_retryable_error() identifies connection reset pattern."""
        client = VscanAPIClient()

        error = Exception("Connection reset by peer")
        result = client._is_retryable_error(error, status_code=0)
        self.assertTrue(result, "Connection reset should be retryable")

    def test_is_retryable_error_with_timeout_pattern(self):
        """Test _is_retryable_error() identifies timeout pattern in error message."""
        client = VscanAPIClient()

        error = Exception("Request timed out after 30 seconds")
        result = client._is_retryable_error(error, status_code=0)
        self.assertTrue(result, "Timeout pattern should be retryable")

    def test_max_retries_boundary_zero(self):
        """Test retry logic with max_retries=0 (no retries)."""
        client = VscanAPIClient(max_retries=0)

        self.assertEqual(client.max_retries, 0)

        with patch("urllib.request.urlopen") as mock_urlopen:
            http_error = urllib.error.HTTPError(
                "https://example.com/test",
                503,
                "Service Unavailable",
                {},
                None,
            )
            http_error.read = Mock(return_value=b'{"error": "Service unavailable"}')
            mock_urlopen.side_effect = http_error

            with self.assertRaises(Exception):
                client._make_request("https://example.com/test", method="GET")

            # Should fail immediately without retries
            self.assertEqual(mock_urlopen.call_count, 1)

    def test_max_retries_boundary_one(self):
        """Test retry logic with max_retries=1 (one retry attempt)."""
        client = VscanAPIClient(max_retries=1)

        self.assertEqual(client.max_retries, 1)

        with patch("urllib.request.urlopen") as mock_urlopen:
            with patch("time.sleep"):  # Skip sleep delays in tests
                http_error = urllib.error.HTTPError(
                    "https://example.com/test",
                    503,
                    "Service Unavailable",
                    {},
                    None,
                )
                http_error.read = Mock(return_value=b'{"error": "Service unavailable"}')
                mock_urlopen.side_effect = http_error

                with self.assertRaises(Exception):
                    client._make_request_with_retry(
                        "https://example.com/test", method="GET"
                    )

                # Initial attempt + 1 retry = 2 calls
                self.assertEqual(mock_urlopen.call_count, 2)


@pytest.mark.unit
class TestTimingStatistics(unittest.TestCase):
    """Test timing statistics collection and reporting."""

    def test_get_timing_stats_with_empty_lists(self):
        """Test get_timing_stats() handles empty timing lists."""
        client = VscanAPIClient()

        # Timing stats should be empty initially
        stats = client.get_timing_stats()

        # Should return stats with zero averages
        self.assertEqual(stats["avg_submit_time"], 0.0)
        self.assertEqual(stats["avg_poll_time"], 0.0)
        self.assertEqual(stats["avg_results_time"], 0.0)
        self.assertEqual(stats["avg_total_time"], 0.0)

    def test_get_timing_stats_with_single_values(self):
        """Test get_timing_stats() with single timing values."""
        client = VscanAPIClient()

        # Manually add single timing values
        client.timing_stats["submit_times"] = [1.5]
        client.timing_stats["poll_times"] = [2.0]
        client.timing_stats["results_times"] = [0.5]
        client.timing_stats["total_scan_times"] = [4.0]

        stats = client.get_timing_stats()

        self.assertEqual(stats["avg_submit_time"], 1.5)
        self.assertEqual(stats["avg_poll_time"], 2.0)
        self.assertEqual(stats["avg_results_time"], 0.5)
        self.assertEqual(stats["avg_total_time"], 4.0)

    def test_get_timing_stats_with_multiple_values(self):
        """Test get_timing_stats() calculates averages correctly."""
        client = VscanAPIClient()

        # Add multiple timing values
        client.timing_stats["submit_times"] = [1.0, 2.0, 3.0]
        client.timing_stats["poll_times"] = [5.0, 10.0]
        client.timing_stats["results_times"] = [0.5, 1.5, 2.5]
        client.timing_stats["total_scan_times"] = [10.0, 20.0, 30.0]

        stats = client.get_timing_stats()

        self.assertEqual(stats["avg_submit_time"], 2.0)  # (1+2+3)/3
        self.assertEqual(stats["avg_poll_time"], 7.5)  # (5+10)/2
        self.assertEqual(stats["avg_results_time"], 1.5)  # (0.5+1.5+2.5)/3
        self.assertEqual(stats["avg_total_time"], 20.0)  # (10+20+30)/3

    def test_get_timing_stats_mixed_empty_and_populated(self):
        """Test get_timing_stats() with some empty and some populated lists."""
        client = VscanAPIClient()

        # Mix of empty and populated timing lists
        client.timing_stats["submit_times"] = [2.5, 3.5]
        client.timing_stats["poll_times"] = []  # Empty
        client.timing_stats["results_times"] = [1.0]
        client.timing_stats["total_scan_times"] = []  # Empty

        stats = client.get_timing_stats()

        self.assertEqual(stats["avg_submit_time"], 3.0)  # (2.5+3.5)/2
        self.assertEqual(stats["avg_poll_time"], 0.0)  # Empty list
        self.assertEqual(stats["avg_results_time"], 1.0)  # Single value
        self.assertEqual(stats["avg_total_time"], 0.0)  # Empty list


@pytest.mark.unit
class TestResponseValidation(unittest.TestCase):
    """Test response validation and missing field handling."""

    def test_submit_analysis_missing_analysis_id(self):
        """Test submit_analysis() handles missing analysisId field."""
        client = VscanAPIClient()

        with patch.object(client, "_make_request_with_retry") as mock_request:
            # Response missing 'analysisId' field with 200 status code
            mock_request.return_value = (200, {"status": "submitted"})

            with self.assertRaises(Exception) as context:
                client.submit_analysis("test-publisher", "test-extension")

            error_msg = str(context.exception).lower()
            self.assertTrue("failed to submit" in error_msg or "analysis" in error_msg)

    def test_check_status_missing_status_field(self):
        """Test check_status() handles missing status field."""
        client = VscanAPIClient()

        with patch.object(client, "_make_request_with_retry") as mock_request:
            # Response missing 'status' field with 200 status code
            mock_request.return_value = (200, {"id": "abc123"})

            with self.assertRaises(Exception) as context:
                client.check_status("abc123")

            error_msg = str(context.exception).lower()
            self.assertTrue(
                "failed to check status" in error_msg or "status" in error_msg
            )

    def test_get_results_non_200_status(self):
        """Test get_results() handles non-200 status codes."""
        client = VscanAPIClient()

        with patch.object(client, "_make_request_with_retry") as mock_request:
            # Non-200 status code
            mock_request.return_value = (404, {"error": "Not found"})

            with self.assertRaises(Exception) as context:
                client.get_results("abc123")

            error_msg = str(context.exception).lower()
            self.assertTrue(
                "failed to retrieve results" in error_msg or "results" in error_msg
            )


if __name__ == "__main__":
    unittest.main()
