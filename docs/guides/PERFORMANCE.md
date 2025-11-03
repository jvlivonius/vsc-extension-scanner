# Performance Documentation

**Document Type:** Living Benchmark Reference
**Applies To:** All 3.x versions
**Benchmark Date:** Latest measurements from 2025-10-26 (v3.5.0 parallel processing), 2025-10-22 (v3.1.0 caching)
**Platform:** macOS (Darwin 25.0.0), Python 3.11
**Note:** Specific timing numbers are platform/hardware-specific. Focus on relative improvements rather than absolute values.

## Benchmark Validity

**Important:** Benchmarks in this document are platform-specific and age over time.

**Current Measurements Valid For:**
- Platform: macOS (Darwin 25.0.0), Python 3.11
- Measurement Date: 2025-10-26 (parallel), 2025-10-22 (caching)
- Version: v3.5.0

**Refresh Required When:**
- Platform or OS changes significantly
- 6+ months have elapsed since measurement
- Major performance optimizations are implemented
- Python version is upgraded

**How to Re-Run Benchmarks:**
```bash
# Performance benchmarks
python3 tests/test_performance.py

# Real-world scan timing
time vscan scan --quiet

# Parallel vs sequential comparison
time vscan scan --workers 1 --quiet  # Sequential
time vscan scan --workers 3 --quiet  # Parallel (default)
```

## Overview

This document provides detailed performance benchmarks, optimization strategies, and resource usage metrics for the VS Code Extension Security Scanner.

---

## 1. Performance Benchmarks

### 1.1 Caching Performance (v3.1.0)

**Test Environment:**
- Platform: macOS
- Python: 3.11
- Extensions: 66 installed extensions
- Network: Stable broadband connection

**Results:**

| Metric | Without Cache | With Cache | Improvement |
|--------|---------------|------------|-------------|
| **66 extensions** | 6m 45s (405s) | 14.2s | **28.6x faster** |
| **3 extensions** | 26.3s | 0.2s | **131x faster** |
| **Average per ext** | 6.1s | 0.21s | **29x faster** |
| **Cache hit rate** | 0% | 97% | - |

**Key Insights:**
- First scan requires full API calls for all extensions (~6 seconds per extension)
- Cached scans leverage SQLite database for near-instant results
- Cache hit rate typically 97%+ on repeated scans within 7-day expiry window
- Cold cache misses occur only for: new extensions, version updates, or expired entries

### 1.2 Parallel Processing Performance (v3.5.0)

**Test Environment:**
- Platform: macOS, Windows, Linux
- Python: 3.11
- Extensions: 66 installed extensions
- Workers: 3 (default)

**Sequential vs Parallel Comparison:**

| Configuration | Scan Time | Extensions/sec | Speedup |
|---------------|-----------|----------------|---------|
| **Sequential (1 worker)** | 6m 6s (366s) | 0.18 | Baseline |
| **Parallel (2 workers)** | 3m 32s (212s) | 0.31 | **1.73x** |
| **Parallel (3 workers)** | 1m 15s (75s) | 0.88 | **4.88x** |
| **Parallel (5 workers)** | 1m 10s (70s) | 0.94 | **5.23x** |

**Optimal Configuration:**
- **Default:** 3 workers (best balance of speed and API respect)
- **Maximum:** 5 workers (diminishing returns beyond this)
- **Minimum:** 1 worker (sequential mode for debugging)

**Scaling Efficiency:**
| Workers | Ideal Speedup | Actual Speedup | Efficiency |
|---------|---------------|----------------|------------|
| 1 | 1.0x | 1.0x | 100% |
| 2 | 2.0x | 1.73x | 87% |
| 3 | 3.0x | 4.88x | 163%* |
| 5 | 5.0x | 5.23x | 105% |

*Note: 3 workers exceed linear scaling due to reduced wait times and better network utilization

### 1.3 Database Performance (v3.1.0)

**Optimization: Batch Commit**

| Operation | Before Optimization | After Optimization | Improvement |
|-----------|---------------------|-------------------|-------------|
| **Insert 66 records** | 45.2s | 5.6s | **87.6% faster** |
| **Commits per scan** | 66 individual | 1 batch | 98.5% reduction |

**Optimization: VACUUM After Bulk Delete**

| Metric | Before VACUUM | After VACUUM | Space Reclaimed |
|--------|---------------|--------------|-----------------|
| **Database Size** | 15.3 MB | 4.0 MB | **73.9%** |
| **Fragmentation** | High | Low | Optimized |

**Key Techniques:**
- Single transaction for batch inserts
- VACUUM operation after cache clear
- WAL mode for concurrent reads
- Prepared statements for security and performance

---

## 2. Performance Testing

**Test File:** `tests/test_performance.py`

### 2.1 Running Performance Tests

```bash
# Run all performance tests
python3 tests/test_performance.py
pytest tests/test_performance.py -v

# Run specific test
pytest tests/test_performance.py::test_cache_provides_50x_speedup -v
```

### 2.2 Key Performance Tests

#### Cache Performance Test
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

#### Memory Usage Test
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

#### Parallel Performance Test (v3.5.0+)
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

**See:** Complete test suite in `tests/test_performance.py` for all performance validation tests.

---

## 3. Resource Usage

### 3.1 Memory Footprint

| Operation | Memory Usage | Peak Memory | Notes |
|-----------|--------------|-------------|-------|
| **Idle (CLI loaded)** | 15 MB | 18 MB | Typer + Rich loaded |
| **Scanning (sequential)** | 35 MB | 42 MB | Single API client |
| **Scanning (3 workers)** | 48 MB | 55 MB | 3 API clients + thread overhead |
| **Scanning (5 workers)** | 52 MB | 62 MB | 5 API clients + thread overhead |
| **Cache operations** | +2-5 MB | - | SQLite connection |
| **HTML generation** | +8-12 MB | - | Template rendering |

**Memory Management:**
- No memory leaks detected in 24-hour stress tests
- Automatic garbage collection of large responses
- 10 MB API response size limit prevents memory exhaustion
- Thread-local storage prevents shared state issues

### 3.2 Disk Usage

| Component | Size | Growth Rate | Notes |
|-----------|------|-------------|-------|
| **Package Installation** | 8-10 MB | Static | Python package + dependencies |
| **Cache Database** | 2-5 MB | ~50 KB per extension | SQLite with compression |
| **Configuration File** | <1 KB | Static | ~/.vscanrc INI file |
| **HTML Reports** | 200-500 KB | Per report | Self-contained with embedded assets |
| **JSON Reports** | 50-150 KB | Per report | Compact schema v2.0 |
| **CSV Reports** | 10-30 KB | Per report | Minimal column set |

**Disk Space Recommendations:**
- Minimum: 20 MB (installation + small cache)
- Recommended: 50 MB (includes room for reports)
- Large deployments: 100 MB (extensive cache + report history)

### 3.3 Network Usage

| Operation | Data Transfer | API Calls | Rate Limit Impact |
|-----------|---------------|-----------|-------------------|
| **Initial scan (66 ext)** | ~500 KB | 66 | 1.5s delay between calls |
| **Cached scan** | 0 KB | 0 | No network activity |
| **Cache refresh** | ~300 KB | ~40 | Only outdated entries |
| **Single extension** | ~8 KB | 1 | Per extension |

**Network Optimization:**
- HTTPS connection reuse across requests
- Exponential backoff on transient failures (2s, 4s, 8s)
- Configurable rate limiting (default 1.5s, range 0.5-10s)
- Graceful handling of network failures

---

## 4. Performance Optimization Strategies

### 4.1 Caching Strategy

**Multi-Level Caching:**
1. **In-Memory Cache:** API client connection pooling
2. **SQLite Cache:** Extension results with HMAC integrity
3. **Version-Based Invalidation:** Automatic refresh on updates

**Cache Hit Optimization:**
- Store complete vscan.dev response
- Include timestamp and version metadata
- HMAC-SHA256 signatures prevent tampering
- Configurable TTL (default 7 days, range 1-90 days)

**Cache Management Best Practices:**
```bash
# Regular maintenance (monthly)
vscan cache stats --cache-max-age 30  # Check for stale entries
vscan cache clear                      # Clear if database grows >50MB

# Performance tuning
vscan config set cache.max_age 14      # Extend TTL for slower-changing extensions
vscan config set cache.max_age 3       # Reduce TTL for active development
```

### 4.2 Parallel Processing Strategy

**Threading Architecture:**
- **ThreadPoolExecutor:** Python standard library, no external deps
- **Worker Isolation:** Each worker has dedicated API client
- **Thread-Safe Stats:** Lock-protected shared statistics collection
- **Main Thread DB:** All SQLite writes occur in main thread (SQLite limitation)

**Optimal Worker Count Selection:**
```python
# Automatic selection based on extension count
extensions_count < 10:  workers = 1  # Sequential for small scans
extensions_count < 30:  workers = 2  # Moderate parallelism
extensions_count >= 30: workers = 3  # Default optimal
```

**Rate Limit Protection:**
- Distributed delays across workers
- Per-worker exponential backoff
- Global rate limit tracking
- Automatic worker throttling on API errors

### 4.3 API Optimization

**Request Optimization:**
- Connection pooling for HTTPS requests
- Request timeouts (30s connect, 60s read)
- Automatic retry with exponential backoff
- Jitter to prevent thundering herd

**Response Handling:**
- Streaming for large responses
- 10 MB size limit prevents memory exhaustion
- Incremental parsing of JSON responses
- Error response caching (5-minute TTL)

### 4.4 Database Optimization

**SQLite Tuning:**
```sql
-- Performance pragmas
PRAGMA journal_mode = WAL;           -- Write-Ahead Logging for concurrency
PRAGMA synchronous = NORMAL;         -- Balance safety and speed
PRAGMA cache_size = -2000;           -- 2MB cache
PRAGMA temp_store = MEMORY;          -- Use memory for temp storage
```

**Schema Optimization:**
```sql
-- Indexes for fast lookups
CREATE INDEX idx_extension_id ON extensions(extension_id);
CREATE INDEX idx_timestamp ON extensions(timestamp);

-- Partial indexes for common queries
CREATE INDEX idx_recent ON extensions(timestamp)
  WHERE timestamp > datetime('now', '-7 days');
```

**Query Optimization:**
- Prepared statements for all queries
- Batch inserts in single transaction
- Lazy connection initialization
- Automatic VACUUM on cache clear

---

## 5. Benchmarking & Profiling

### 5.1 Benchmarking Methodology

**Test Scenarios:**
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
vscan scan --delay 0.5  # Fast network
vscan scan --delay 5.0  # Slow/restricted network
```

**Metrics Collection:**
- Total scan time (wall clock)
- Per-extension scan time
- Cache hit/miss rates
- Memory usage (peak and average)
- Network transfer volume
- API call count and latency

### 5.2 Load Testing

**Stress Test Scenarios:**
```bash
# Large extension count
vscan scan --extensions-dir /path/to/200-extensions

# Concurrent scans (multi-process)
for i in {1..5}; do vscan scan & done

# Cache pressure
vscan config set cache.max_age 1  # Force frequent invalidation
for i in {1..100}; do vscan scan; sleep 86400; done
```

**Performance Targets:**
- ✅ Handle 200+ extensions without memory issues
- ✅ Support 5 concurrent scan processes
- ✅ Maintain <100MB total memory usage
- ✅ Cache database stays <20MB for 200 extensions

### 5.3 Profiling

**CPU Profiling:**
```bash
# Python cProfile
python -m cProfile -o profile.stats -m vscode_scanner.vscan scan
python -m pstats profile.stats

# Hotspot analysis
(pstats) sort cumtime
(pstats) stats 20
```

**Memory Profiling:**
```bash
# memory_profiler
pip install memory_profiler
python -m memory_profiler vscode_scanner/vscan.py scan

# tracemalloc (built-in)
python -X tracemalloc=5 -m vscode_scanner.vscan scan
```

---

## 6. Performance Troubleshooting

### 6.1 Slow Scans

**Symptoms:**
- Scans take >2 minutes per extension
- Frequent timeout errors
- High CPU usage

**Diagnosis:**
```bash
# Check network latency
time curl -I https://vscan.dev

# Check API delays
vscan config get scan.delay

# Check worker count
vscan config get scan.workers

# Profile execution
python -m cProfile -m vscode_scanner.vscan scan --quiet
```

**Solutions:**
- Increase `scan.delay` if rate limited: `vscan config set scan.delay 2.5`
- Reduce `scan.workers` if network unstable: `vscan config set scan.workers 2`
- Check firewall/proxy settings
- Verify internet connectivity

### 6.2 High Memory Usage

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

# Check for memory leaks
python -X tracemalloc=5 -m vscode_scanner.vscan scan
```

**Solutions:**
- Clear cache: `vscan cache clear --force`
- Reduce workers: `vscan config set scan.workers 2`
- Update to latest version (memory leak fixes)
- Report issue if persistent

### 6.3 Cache Issues

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
- Clear and rebuild: `vscan cache clear --force`
- Adjust max age: `vscan config set cache.max_age 7`
- Run VACUUM: `vscan cache clear` (automatic)
- Check disk space availability

---

## 7. Performance Roadmap

### 7.1 Completed Optimizations

- ✅ **v3.1.0:** SQLite caching (28x speedup)
- ✅ **v3.1.0:** Batch database commits (87% faster inserts)
- ✅ **v3.4.0:** Parallel processing (4.88x speedup with 3 workers)
- ✅ **v3.5.0:** Thread-safe statistics collection
- ✅ **v3.5.1:** Connection pooling and retry optimization

### 7.2 Future Optimizations (v3.6+)

**Planned:**
- 🔄 HTTP/2 multiplexing for concurrent API requests
- 🔄 Differential scanning (only check changed extensions)
- 🔄 Predictive cache pre-warming
- 🔄 Async I/O for database operations
- 🔄 Compressed cache storage

**Under Consideration:**
- Binary protocol for faster API communication
- Local vulnerability database mirror
- Distributed caching across team members
- GPU acceleration for report generation

---

## 8. References

### 8.1 Related Documentation

- **Test Suite:** `tests/test_performance.py` - Complete performance test validation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and threading model
- **[TESTING.md](testing/TESTING.md)** - General testing patterns and methodology
- **[API_REFERENCE.md](API_REFERENCE.md)** - vscan.dev API performance characteristics

### 8.2 Performance Tools

- **[Python cProfile](https://docs.python.org/3/library/profile.html)** - CPU profiling
- **[memory_profiler](https://pypi.org/project/memory-profiler/)** - Memory profiling
- **[SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)** - Query optimization
- **[py-spy](https://github.com/benfred/py-spy)** - Sampling profiler

---

**Document Version:** 2.0.0 (Consolidated)
**Status:** Complete ✅
**Last Updated:** 2025-11-03 (Merged TESTING_PERFORMANCE.md for maintainability)
