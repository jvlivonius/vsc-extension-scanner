# Parallel Scanning Tests

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Test File:** `tests/test_parallel_scanning.py`
**Feature:** v3.5.0+ (1-5 worker threads)

---

## Overview

Tests multi-threaded execution with ThreadPoolExecutor (1-5 workers).

**Run Parallel Tests:**
```bash
python3 tests/test_parallel_scanning.py
python3 scripts/run_tests.py --parallel
```

---

## Key Tests

### Thread Safety
```python
def test_thread_safe_statistics():
    """Statistics correctly accumulated across threads."""
    stats = ThreadSafeStats()

    def worker():
        for _ in range(100):
            stats.increment('total', 1)

    threads = [Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()

    assert stats.to_dict()['total'] == 500  # No race conditions
```

### Worker Isolation
```python
def test_worker_isolation():
    """Each worker has isolated API client."""
    results = scan_extensions(extensions, workers=3)

    # No interference between workers
    assert len(results) == len(extensions)
    assert all('error' not in r for r in results)
```

---

## See Full Guide

**Location:** Original [TESTING.md](../TESTING.md) section "Parallel Scanning Tests" (lines 1900-2015)

---

**Document Version:** 1.0 (Summary)
**Last Updated:** 2025-10-30
