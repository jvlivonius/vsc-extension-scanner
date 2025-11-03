"""
Deterministic Retry Logic Tests - Phase 4.

Tests retry logic with injectable jitter function for deterministic testing.
Improves vscan_api.py coverage without relying on random behavior.
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner.vscan_api import VscanAPIClient


class TestDeterministicRetry(unittest.TestCase):
    """Test retry logic with deterministic jitter functions."""

    def test_backoff_with_zero_jitter(self):
        """Test backoff calculation with zero jitter function."""
        client = VscanAPIClient()

        # Zero jitter function (deterministic, no randomness)
        def zero_jitter(min_val: float, max_val: float) -> float:
            return 0.0

        # Test attempts with zero jitter (pure exponential backoff)
        # Base delay is 2s, exponential: attempt 0 = 2s, attempt 1 = 4s, attempt 2 = 8s
        delay_0 = client._calculate_backoff_delay(0, jitter_fn=zero_jitter)
        self.assertEqual(delay_0, 2.0)  # 2 * (2^0) + 0 = 2.0

        delay_1 = client._calculate_backoff_delay(1, jitter_fn=zero_jitter)
        self.assertEqual(delay_1, 4.0)  # 2 * (2^1) + 0 = 4.0

        delay_2 = client._calculate_backoff_delay(2, jitter_fn=zero_jitter)
        self.assertEqual(delay_2, 8.0)  # 2 * (2^2) + 0 = 8.0

        delay_3 = client._calculate_backoff_delay(3, jitter_fn=zero_jitter)
        self.assertEqual(delay_3, 16.0)  # 2 * (2^3) + 0 = 16.0

    def test_backoff_with_max_positive_jitter(self):
        """Test backoff calculation with maximum positive jitter (+20%)."""
        client = VscanAPIClient()

        # Maximum positive jitter function (always +20%)
        def max_positive_jitter(min_val: float, max_val: float) -> float:
            return max_val  # Return maximum (positive jitter)

        # Test with max positive jitter
        delay_0 = client._calculate_backoff_delay(0, jitter_fn=max_positive_jitter)
        self.assertEqual(delay_0, 2.4)  # 2.0 + (0.2 * 2.0) = 2.4

        delay_1 = client._calculate_backoff_delay(1, jitter_fn=max_positive_jitter)
        self.assertEqual(delay_1, 4.8)  # 4.0 + (0.2 * 4.0) = 4.8

        delay_2 = client._calculate_backoff_delay(2, jitter_fn=max_positive_jitter)
        self.assertEqual(delay_2, 9.6)  # 8.0 + (0.2 * 8.0) = 9.6

    def test_backoff_with_max_negative_jitter(self):
        """Test backoff calculation with maximum negative jitter (-20%)."""
        client = VscanAPIClient()

        # Maximum negative jitter function (always -20%)
        def max_negative_jitter(min_val: float, max_val: float) -> float:
            return min_val  # Return minimum (negative jitter)

        # Test with max negative jitter
        delay_0 = client._calculate_backoff_delay(0, jitter_fn=max_negative_jitter)
        self.assertEqual(delay_0, 1.6)  # 2.0 - (0.2 * 2.0) = 1.6

        delay_1 = client._calculate_backoff_delay(1, jitter_fn=max_negative_jitter)
        self.assertEqual(delay_1, 3.2)  # 4.0 - (0.2 * 4.0) = 3.2

        delay_2 = client._calculate_backoff_delay(2, jitter_fn=max_negative_jitter)
        self.assertEqual(delay_2, 6.4)  # 8.0 - (0.2 * 8.0) = 6.4

    def test_backoff_respects_ceiling_with_jitter(self):
        """Test that ceiling (30s) is respected even with jitter."""
        client = VscanAPIClient()

        # Zero jitter to make ceiling test deterministic
        def zero_jitter(min_val: float, max_val: float) -> float:
            return 0.0

        # Attempt 4: 2 * (2^4) = 32s, capped at 30s
        delay_4 = client._calculate_backoff_delay(4, jitter_fn=zero_jitter)
        self.assertEqual(delay_4, 30.0)  # Capped at MAX_BACKOFF_DELAY

        # Attempt 10: 2 * (2^10) = 2048s, capped at 30s
        delay_10 = client._calculate_backoff_delay(10, jitter_fn=zero_jitter)
        self.assertEqual(delay_10, 30.0)  # Capped at MAX_BACKOFF_DELAY

    def test_backoff_respects_minimum_with_negative_jitter(self):
        """Test that minimum (0.5s) is respected with negative jitter."""
        client = VscanAPIClient(retry_base_delay=0.5)

        # Large negative jitter to test minimum boundary
        def large_negative_jitter(min_val: float, max_val: float) -> float:
            return min_val * 10  # Very large negative jitter

        # Even with large negative jitter, delay should be >= 0.5s
        delay_0 = client._calculate_backoff_delay(0, jitter_fn=large_negative_jitter)
        self.assertGreaterEqual(delay_0, 0.5)  # Minimum 0.5s

    def test_backoff_with_retry_after_header(self):
        """Test that Retry-After header takes precedence over jitter."""
        client = VscanAPIClient()

        # Jitter function that should be ignored when Retry-After is present
        def unused_jitter(min_val: float, max_val: float) -> float:
            return 999.0  # Should be ignored

        # When Retry-After is present, jitter should be ignored
        delay = client._calculate_backoff_delay(
            attempt=5, retry_after=10, jitter_fn=unused_jitter
        )
        self.assertEqual(delay, 10.0)  # Uses Retry-After, not backoff/jitter

    def test_backoff_with_retry_after_capped(self):
        """Test that Retry-After is capped at MAX_BACKOFF_DELAY."""
        client = VscanAPIClient()

        def unused_jitter(min_val: float, max_val: float) -> float:
            return 0.0

        # Large Retry-After value should be capped at 30s
        delay = client._calculate_backoff_delay(
            attempt=0, retry_after=999, jitter_fn=unused_jitter
        )
        self.assertEqual(delay, 30.0)  # Capped at MAX_BACKOFF_DELAY

    def test_backoff_without_jitter_fn_uses_random(self):
        """Test that without jitter_fn, random.uniform is used (non-deterministic)."""
        client = VscanAPIClient()

        # Call multiple times without jitter_fn
        delays = [client._calculate_backoff_delay(1) for _ in range(10)]

        # With random jitter, delays should vary (not all identical)
        unique_delays = set(delays)
        self.assertGreater(
            len(unique_delays), 1, "Random jitter should produce varying delays"
        )

        # All delays should be in valid range (base=4s, jitter=±20%)
        for delay in delays:
            self.assertGreaterEqual(delay, 3.2)  # 4.0 - 0.8 = 3.2
            self.assertLessEqual(delay, 4.8)  # 4.0 + 0.8 = 4.8

    def test_backoff_jitter_range_validation(self):
        """Test that jitter function receives correct min/max values."""
        client = VscanAPIClient()

        received_ranges = []

        def capture_jitter_range(min_val: float, max_val: float) -> float:
            received_ranges.append((min_val, max_val))
            return 0.0

        # Attempt 0: backoff = 2s, jitter range = ±20% = ±0.4s
        client._calculate_backoff_delay(0, jitter_fn=capture_jitter_range)
        self.assertEqual(len(received_ranges), 1)
        min_val, max_val = received_ranges[0]
        self.assertAlmostEqual(min_val, -0.4, places=5)  # -20% of 2s
        self.assertAlmostEqual(max_val, 0.4, places=5)  # +20% of 2s

        # Attempt 2: backoff = 8s, jitter range = ±20% = ±1.6s
        received_ranges.clear()
        client._calculate_backoff_delay(2, jitter_fn=capture_jitter_range)
        self.assertEqual(len(received_ranges), 1)
        min_val, max_val = received_ranges[0]
        self.assertAlmostEqual(min_val, -1.6, places=5)  # -20% of 8s
        self.assertAlmostEqual(max_val, 1.6, places=5)  # +20% of 8s


if __name__ == "__main__":
    unittest.main()
