# Retry Mechanism Testing

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Test Files:** `test_retry.py`, `test_retry_analysis.py`, `test_workflow_retry.py`
**Feature:** v2.2+ (Exponential backoff with jitter)

---

## Overview

Tests retry mechanism with exponential backoff for transient API failures.

**Run Retry Tests:**
```bash
python3 tests/test_retry.py
python3 tests/test_retry_analysis.py
python3 tests/test_workflow_retry.py
```

---

## Key Tests

### Exponential Backoff
```python
def test_exponential_backoff():
    """Verify exponential backoff timing."""
    delay_0 = calculate_backoff(0, base=2.0)  # ~2s
    delay_1 = calculate_backoff(1, base=2.0)  # ~4s
    delay_2 = calculate_backoff(2, base=2.0)  # ~8s

    assert 1.6 <= delay_0 <= 2.4  # Jitter ±20%
    assert 3.2 <= delay_1 <= 4.8
    assert 6.4 <= delay_2 <= 9.6
```

### Retryable Error Detection
```python
def test_non_retryable_errors():
    """Permanent errors don't trigger retries."""
    assert not is_retryable(400)  # Bad Request
    assert not is_retryable(404)  # Not Found
    assert is_retryable(429)      # Rate Limit - OK to retry
    assert is_retryable(503)      # Service Unavailable - OK to retry
```

### Retry-After Header
```python
def test_retry_after_header():
    """Respect Retry-After with ceiling."""
    response = Mock()
    response.getheader.return_value = "5"

    delay = get_retry_delay(response)
    assert 4.5 <= delay <= 5.5  # Use server's delay

    # Test ceiling (malicious header)
    response.getheader.return_value = "9999"
    delay = get_retry_delay(response)
    assert delay <= 30  # Capped at 30s max
```

---

## See Full Guide

**Location:** Original [TESTING.md](../TESTING.md) section "Retry Mechanism Tests" (lines 2407-2518)

---

**Document Version:** 1.0 (Summary)
**Last Updated:** 2025-10-30
