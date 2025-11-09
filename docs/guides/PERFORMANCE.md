# Performance Guide

**Purpose:** How to benchmark, optimize, profile, and troubleshoot performance
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** Developers, Performance Engineers

---

## Table of Contents

- [Overview](#overview)
- [Performance Testing](#performance-testing)
  - [Running Performance Tests](#running-performance-tests)
  - [Writing Performance Tests](#writing-performance-tests)
  - [Test Assertions](#test-assertions)
- [Benchmarking](#benchmarking)
  - [Benchmarking Methodology](#benchmarking-methodology)
  - [Comparing Performance](#comparing-performance)
  - [Platform Considerations](#platform-considerations)
- [Profiling](#profiling)
  - [CPU Profiling](#cpu-profiling)
  - [Memory Profiling](#memory-profiling)
  - [Interpreting Results](#interpreting-results)
- [Optimization Strategies](#optimization-strategies)
  - [Caching Strategy](#caching-strategy)
  - [Parallel Processing](#parallel-processing)
  - [Database Optimization](#database-optimization)
  - [API Optimization](#api-optimization)
- [Troubleshooting](#troubleshooting)
  - [Slow Scans](#slow-scans)
  - [High Memory Usage](#high-memory-usage)
  - [Cache Issues](#cache-issues)
- [Resource Monitoring](#resource-monitoring)
- [References](#references)

---

## Overview

This guide explains how to measure, optimize, and troubleshoot performance in the VS Code Extension Security Scanner. Focus is on techniques and methodologies, not historical benchmarks.

**Performance Principles:**
- **Measure First:** Base optimization on measurements, not assumptions
- **Optimize Bottlenecks:** Focus on highest-impact areas identified through profiling
- **Test Changes:** Validate improvements with performance tests
- **Monitor Resources:** Track memory, disk, network usage patterns

**Benchmark Dating:**
- **Test Assertions (50x, 2x, etc.):** These are performance *requirements*, not historical measurements. They define minimum acceptable performance thresholds that must be maintained across all versions.
- **Historical Benchmarks:** For actual performance measurements from specific releases (e.g., "4.88x speedup measured on 2025-10-26 with 66 extensions"), see [STATUS.md](../project/STATUS.md) version history.
- **Current Metrics:** See [STATUS.md](../project/STATUS.md) § Current Metrics for latest measured performance

---

## Performance Testing

### Running Performance Tests

**Execute performance test suite:**
```bash
# Run all performance tests
python3 tests/test_performance.py
pytest tests/test_performance.py -v

# Run specific test
pytest tests/test_performance.py::test_cache_provides_50x_speedup -v
```

**Real-world performance measurement:**
```bash
# Time a full scan
time vscan scan --quiet

# Compare parallel vs sequential
time vscan scan --workers 1 --quiet  # Sequential baseline
time vscan scan --workers 3 --quiet  # Parallel (default)
time vscan scan --workers 5 --quiet  # Maximum workers

# Test with cold cache
rm ~/.vscan/cache.db
time vscan scan --quiet
```

### Writing Performance Tests

**Cache performance test pattern:**
```python
def test_cache_provides_50x_speedup():
    """Cached results at least 50x faster than fresh scans."""
    import time

    # First scan (fresh, no cache)
    start = time.time()
    scan_extension("ms-python.python")
    fresh_duration = time.time() - start

    # Second scan (cached)
    start = time.time()
    scan_extension("ms-python.python")
    cached_duration = time.time() - start

    speedup = fresh_duration / cached_duration
    assert speedup >= 50, f"Cache speedup {speedup}x below 50x threshold"
```

**Parallel processing test pattern:**
```python
def test_parallel_speedup():
    """3 workers provide 2x+ speedup over sequential."""
    import time

    extensions = ["ext1", "ext2", "ext3", "ext4", "ext5"]

    # Sequential (1 worker)
    start = time.time()
    scan_extensions(extensions, workers=1)
    seq_duration = time.time() - start

    # Parallel (3 workers)
    start = time.time()
    scan_extensions(extensions, workers=3)
    par_duration = time.time() - start

    speedup = seq_duration / par_duration
    assert speedup >= 2.0, f"Parallel speedup {speedup}x below 2x threshold"
```

**Memory usage test pattern:**
```python
def test_cache_migration_memory():
    """Cache migration doesn't load all data into memory."""
    import tracemalloc

    tracemalloc.start()
    cache._migrate_cache_to_v2()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Peak memory < 10MB
    max_mb = 10
    peak_mb = peak / (1024 * 1024)
    assert peak_mb < max_mb, f"Peak memory {peak_mb}MB exceeds {max_mb}MB limit"
```

### Test Assertions

**Performance test patterns:**
- **Speedup Tests:** Assert minimum speedup ratio (e.g., `speedup >= 2.0`)
- **Absolute Time:** Assert maximum duration (e.g., `duration < 1.0` seconds)
- **Resource Limits:** Assert maximum memory/disk usage
- **Scaling Tests:** Assert linear/sublinear scaling with input size

**Test File:** `tests/test_performance.py`

---

## Benchmarking

### Benchmarking Methodology

**Controlled benchmark environment:**
```bash
# 1. Clear cache for cold-start test
rm -rf ~/.vscan/cache.db

# 2. Ensure stable system (close unnecessary apps)
# 3. Run warmup scan (JIT compilation, etc.)
vscan scan --quiet

# 4. Run timed benchmark
time vscan scan --quiet

# 5. Repeat 3-5 times, calculate median
```

**Benchmark scenarios:**
```bash
# Cold cache (first run)
rm -rf ~/.vscan/cache.db
time vscan scan --quiet

# Warm cache (second run)
time vscan scan --quiet

# Parallel vs Sequential
time vscan scan --workers 1 --quiet  # Sequential baseline
time vscan scan --workers 3 --quiet  # Parallel default
time vscan scan --workers 5 --quiet  # Maximum workers

# Network conditions
vscan scan --delay 0.5  # Fast network (minimum API delay)
vscan scan --delay 5.0  # Slow/restricted network
```

### Comparing Performance

**Before/after comparison:**
```bash
# Baseline (before optimization)
git checkout baseline-branch
time vscan scan --quiet > baseline.txt

# Optimized (after changes)
git checkout optimization-branch
time vscan scan --quiet > optimized.txt

# Compare results
# Calculate: improvement = (baseline_time - optimized_time) / baseline_time * 100%
```

**Metrics to collect:**
- **Total scan time** (wall clock)
- **Per-extension scan time** (average)
- **Cache hit/miss rates**
- **Memory usage** (peak and average)
- **Network transfer volume**
- **API call count and latency**

### Platform Considerations

**Platform-specific factors:**
- macOS: APFS filesystem, different SQLite performance
- Linux: ext4/btrfs filesystem characteristics
- Windows: NTFS, different file permission handling
- Python version: 3.8 vs 3.11 performance differences

**How to account for platform differences:**
1. Always note platform in benchmark results
2. Focus on **relative improvements** (e.g., "2x faster") not absolute times
3. Re-run benchmarks when platform changes
4. Use platform-appropriate tools (see Profiling section)

---

## Profiling

### CPU Profiling

**Python cProfile:**
```bash
# Profile full scan
python -m cProfile -o profile.stats -m vscode_scanner.vscan scan

# Analyze results
python -m pstats profile.stats
(pstats) sort cumtime
(pstats) stats 20  # Show top 20 time consumers
```

**py-spy (sampling profiler):**
```bash
# Install
pip install py-spy

# Profile running scan
py-spy record -o profile.svg -- python -m vscode_scanner.vscan scan

# View flamegraph (profile.svg)
```

**Interpreting CPU profiles:**
- **cumtime:** Total time in function + callees (find bottlenecks)
- **tottime:** Time in function only (find hot loops)
- **ncalls:** Number of calls (find excessive calls)

**Optimization targets:**
- Functions with high cumtime (bottlenecks)
- Functions with high tottime (hot spots)
- Functions called many times (optimization multiplier)

### Memory Profiling

**tracemalloc (built-in):**
```bash
# Profile with tracemalloc
python -X tracemalloc=5 -m vscode_scanner.vscan scan
```

**memory_profiler:**
```bash
# Install
pip install memory_profiler

# Profile specific function
python -m memory_profiler vscode_scanner/vscan.py scan
```

**Monitoring during scan:**
```bash
# macOS
/usr/bin/time -l vscan scan

# Linux
/usr/bin/time -v vscan scan
```

**Memory leak detection:**
```python
import tracemalloc

tracemalloc.start()
# Run operation
snapshot1 = tracemalloc.take_snapshot()
# Run operation again
snapshot2 = tracemalloc.take_snapshot()

# Compare
top_stats = snapshot2.compare_to(snapshot1, 'lineno')
for stat in top_stats[:10]:
    print(stat)
```

### Interpreting Results

**What to look for:**
- **High memory:** Large data structures, unnecessary copies, lack of streaming
- **Memory growth:** Memory leaks, accumulating caches
- **CPU hotspots:** Inefficient algorithms, excessive object creation
- **I/O bottlenecks:** Disk thrashing, network latency

**Optimization priority:**
1. Fix memory leaks (unbounded growth)
2. Optimize CPU hotspots (>10% cumtime)
3. Reduce I/O operations (database, network)
4. Eliminate unnecessary work (redundant calls)

---

## Optimization Strategies

### Caching Strategy

**Multi-level caching:**
1. **In-Memory Cache:** API client connection pooling
2. **SQLite Cache:** Extension results with HMAC integrity
3. **Version-Based Invalidation:** Automatic refresh on updates

**Cache implementation:**
```python
# Check cache first
cached = cache_manager.get(extension_id)
if cached and not is_expired(cached):
    return cached

# Fetch from API
result = api_client.fetch(extension_id)

# Store in cache
cache_manager.set(extension_id, result)
return result
```

**Cache tuning:**
```bash
# Adjust TTL (time-to-live)
vscan config set cache.max_age 7   # Days (default: 7, range: 1-90)

# Clear stale cache
vscan cache clear

# Monitor cache performance
vscan cache stats
```

**Cache optimization techniques:**
- Store complete API responses (avoid partial cache)
- Use HMAC signatures (prevent tampering, see SECURITY.md)
- Implement batch commits (reduce SQLite transaction overhead)
- Run VACUUM after bulk deletes (reclaim disk space)

### Parallel Processing

**ThreadPoolExecutor configuration:**
```python
from concurrent.futures import ThreadPoolExecutor

# Optimal worker count selection
def calculate_workers(extension_count):
    if extension_count < 10:
        return 1  # Sequential for small scans
    elif extension_count < 30:
        return 2  # Moderate parallelism
    else:
        return 3  # Default optimal (best balance)

# Execute with isolation
with ThreadPoolExecutor(max_workers=workers) as executor:
    # Each worker gets dedicated API client
    futures = [executor.submit(scan_one, ext) for ext in extensions]
    results = [f.result() for f in futures]
```

**Thread safety:**
```python
# Thread-safe statistics collection
from threading import Lock

class ThreadSafeStats:
    def __init__(self):
        self._lock = Lock()
        self._data = {}

    def increment(self, key, value):
        with self._lock:
            self._data[key] = self._data.get(key, 0) + value
```

**Rate limit protection:**
- Distribute delays across workers
- Implement per-worker exponential backoff
- Track global rate limit
- Auto-throttle on API errors

**Worker count tuning:**
```bash
# Test different worker counts
for w in 1 2 3 5; do
    echo "Workers: $w"
    time vscan scan --workers $w --quiet
done
```

### Database Optimization

**SQLite tuning:**
```sql
-- Performance pragmas (applied automatically)
PRAGMA journal_mode = WAL;      -- Write-Ahead Logging
PRAGMA synchronous = NORMAL;    -- Balance safety/speed
PRAGMA cache_size = -2000;      -- 2MB cache
PRAGMA temp_store = MEMORY;     -- Memory for temp tables
```

**Batch operations:**
```python
# BAD: Individual commits
for result in results:
    db.execute("INSERT ...", result)
    db.commit()  # Slow!

# GOOD: Batch commit
db.execute("BEGIN")
for result in results:
    db.execute("INSERT ...", result)
db.commit()  # Single transaction
```

**Index optimization:**
```sql
-- Create indexes for common queries
CREATE INDEX idx_extension_id ON extensions(extension_id);
CREATE INDEX idx_timestamp ON extensions(timestamp);

-- Partial indexes for frequent filters
CREATE INDEX idx_recent ON extensions(timestamp)
  WHERE timestamp > datetime('now', '-7 days');
```

**Query optimization:**
- Use prepared statements (security + performance)
- Avoid `SELECT *` (fetch only needed columns)
- Use `LIMIT` for large result sets
- Run `EXPLAIN QUERY PLAN` for slow queries

### API Optimization

**Request optimization:**
```python
# Connection pooling (reuse HTTPS connections)
import urllib.request

opener = urllib.request.build_opener()
# Connection stays alive across requests

# Request configuration
request = urllib.request.Request(
    url,
    headers={'Connection': 'keep-alive'}
)
```

**Retry with exponential backoff:**
```python
def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError:
            delay = min(2 ** attempt * random.uniform(0.8, 1.2), 30)
            time.sleep(delay)
    raise MaxRetriesExceeded()
```

**Response handling:**
```python
# Streaming for large responses
response = urllib.request.urlopen(url)
data = response.read(MAX_RESPONSE_SIZE)  # 10MB limit

# Incremental JSON parsing
import json
result = json.loads(data)  # Parse once, cache result
```

---

## Troubleshooting

### Slow Scans

**Symptoms:**
- Scans take >2 minutes per extension
- Frequent timeout errors
- High CPU usage without progress

**Diagnosis:**
```bash
# 1. Check network latency
time curl -I https://vscan.dev

# 2. Check API delay setting
vscan config get scan.delay

# 3. Check worker count
vscan config get scan.workers

# 4. Profile execution
python -m cProfile -m vscode_scanner.vscan scan --quiet
```

**Solutions:**
```bash
# Increase delay if rate limited
vscan config set scan.delay 2.5

# Reduce workers if network unstable
vscan config set scan.workers 2

# Check cache is working
vscan cache stats  # Should show high hit rate on re-scans

# Verify internet connectivity
ping vscan.dev
```

### High Memory Usage

**Symptoms:**
- Memory usage >200MB
- System swap activity
- Out of memory errors

**Diagnosis:**
```bash
# Monitor memory during scan
/usr/bin/time -l vscan scan  # macOS
/usr/bin/time -v vscan scan  # Linux

# Check cache size
vscan cache stats

# Profile memory
python -X tracemalloc=5 -m vscode_scanner.vscan scan
```

**Solutions:**
```bash
# Clear cache
vscan cache clear --force

# Reduce workers (less concurrent API clients)
vscan config set scan.workers 2

# Check for memory leaks (if persistent)
# Run tracemalloc comparison (see Profiling section)
```

### Cache Issues

**Symptoms:**
- Cache not accelerating repeated scans
- Database corruption errors
- Excessive disk usage

**Diagnosis:**
```bash
# Check cache statistics
vscan cache stats

# Verify database integrity
sqlite3 ~/.vscan/cache.db "PRAGMA integrity_check;"

# Check cache size
du -h ~/.vscan/cache.db
```

**Solutions:**
```bash
# Clear and rebuild cache
vscan cache clear --force

# Adjust cache TTL
vscan config set cache.max_age 7

# Run VACUUM (automatic on clear)
vscan cache clear

# Verify disk space
df -h ~/.vscan
```

---

## Resource Monitoring

**Memory monitoring:**
```bash
# During scan execution
watch -n 1 'ps aux | grep vscan'

# With detailed metrics
/usr/bin/time -v python -m vscode_scanner.vscan scan
```

**Disk usage monitoring:**
```bash
# Cache database size
du -h ~/.vscan/cache.db

# Report file sizes
ls -lh *.html *.json *.csv
```

**Network monitoring:**
```bash
# Network activity (macOS)
nettop -p python

# Network activity (Linux)
iftop -f "host vscan.dev"
```

**Resource limits:**
- **Memory:** Should stay <100MB for typical scans (<200 extensions)
- **Disk:** Cache typically 2-5MB (50KB per extension)
- **Network:** ~8KB per extension (first scan), 0KB (cached)

---

## References

### Related Documentation

- **[TESTING.md](TESTING.md)** - General testing patterns (includes performance test section)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, threading model
- **[API_REFERENCE.md](API_REFERENCE.md)** - vscan.dev API performance characteristics

### Performance Tools

- **[Python cProfile](https://docs.python.org/3/library/profile.html)** - CPU profiling
- **[memory_profiler](https://pypi.org/project/memory-profiler/)** - Line-by-line memory profiling
- **[py-spy](https://github.com/benfred/py-spy)** - Sampling profiler (no code changes)
- **[SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)** - Query optimization analysis

### External Resources

- **[Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)** - General Python optimization
- **[SQLite Performance Tuning](https://www.sqlite.org/speed.html)** - Database optimization

---

**Document Version:** 2.0.0 (Refocused as actionable guide)
**Last Updated:** 2025-11-09
**Status:** Complete ✅
