# Performance Testing Guide

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Test File:** `tests/test_performance.py`
**Target Audience:** Developers, Performance Engineers

---

## Overview

Performance tests verify timing characteristics, memory usage, and scalability.

**Run Performance Tests:**
```bash
python3 tests/test_performance.py
pytest tests/test_performance.py -v
```

---

## Key Performance Tests

### Cache Performance
```python
def test_cache_provides_50x_speedup():
    """Cached results at least 50x faster than fresh scans."""
    # First scan (fresh)
    start = time.time()
    scan_extension("ms-python.python")
    fresh_duration = time.time() - start

    # Second scan (cached)
    start = time.time()
    scan_extension("ms-python.python")
    cached_duration = time.time() - start

    speedup = fresh_duration / cached_duration
    assert speedup >= 50
```

### Memory Usage
```python
def test_cache_migration_memory():
    """Cache migration doesn't load all data into memory."""
    import tracemalloc

    tracemalloc.start()
    cache._migrate_cache_to_v2()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Peak memory < 10MB
    assert peak < 10 * 1024 * 1024
```

### Parallel Performance (v3.5.0+)
```python
def test_parallel_speedup():
    """3 workers provide 2x+ speedup."""
    # Sequential (1 worker)
    start = time.time()
    scan_extensions(extensions, workers=1)
    seq_duration = time.time() - start

    # Parallel (3 workers)
    start = time.time()
    scan_extensions(extensions, workers=3)
    par_duration = time.time() - start

    speedup = seq_duration / par_duration
    assert speedup >= 2.0  # At least 2x faster
```

---

## See Full Guide

**Location:** Original [TESTING.md](../TESTING.md) section "Performance Tests" (lines 1842-1897)

---

**Document Version:** 1.0 (Summary)
**Full Documentation:** See TESTING.md § Performance Tests
**Last Updated:** 2025-10-30
