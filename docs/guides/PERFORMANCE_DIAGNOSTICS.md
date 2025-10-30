# Performance Diagnostics Guide

## Overview

The performance diagnostic tool helps identify the root cause of scanning slowdowns by measuring:
- API response times (submit, poll, results)
- Rate limiting detection (429 errors)
- Timeout occurrences
- Retry statistics
- Sequential vs parallel performance comparison
- Cache effectiveness

## Quick Start

Run the diagnostic with default settings (tests 5 extensions):

```bash
python3 scripts/diagnose_performance.py
```

## Usage Options

```bash
# Test with more extensions for better accuracy
python3 scripts/diagnose_performance.py --extensions-count 10

# Test different worker configurations
python3 scripts/diagnose_performance.py --workers 2
python3 scripts/diagnose_performance.py --workers 5

# Test different delay settings
python3 scripts/diagnose_performance.py --delay 3.0

# Save diagnostic report
python3 scripts/diagnose_performance.py --output diagnostic_report.txt
```

## Interpreting Results

### Step 1: Extension Discovery

Shows which extensions will be scanned:
```
Extensions directory: /Users/username/.vscode/extensions
Total extensions found: 66
Sample size: 5

  1. publisher.extension1 v1.0.0
  2. publisher.extension2 v2.1.0
  ...
```

### Step 2: Sequential Scan Test

Tests sequential scanning (--workers 1):
```
Scanning 5 extensions sequentially...
Request delay: 1.5s

  [1/5] Scanning extension1... ⚡ (cached) - 12.3ms
  [2/5] Scanning extension2... 🔍 (fresh) - 45.2s
  ...

✓ Sequential scan completed in 3m 45.2s
  Average per extension: 45.0s
```

**Key metrics:**
- `⚡ (cached)`: Extension retrieved from cache (instant)
- `🔍 (fresh)`: Extension scanned via API (slow)
- Average time tells you baseline per-extension cost

### Step 3: Parallel Scan Test

Tests parallel scanning with configured workers:
```
Scanning 5 extensions with 3 workers...
Request delay: 1.5s per worker

  [1/5] extension1 ⚡
  [2/5] extension2 🔍
  ...

✓ Parallel scan completed in 1m 15.3s
  Average per extension: 15.1s
```

**Speedup calculation:**
- Speedup = Sequential time ÷ Parallel time
- Expected: 3x-5x with 3 workers
- Actual < 2x indicates problems

### Step 4: API Performance Analysis

Identifies specific issues:

#### ✅ Healthy API (No Issues)
```
📊 Timing Breakdown:
  Average submit time:  1.2s
  Average poll time:    35.4s
  Average results time: 0.8s
  Average total time:   37.4s

⚠️  Issues Detected:
  ✓ No rate limiting detected
  ✓ No timeout issues detected
  ✓ Retry rate is normal
  ✓ API performance is healthy
```

#### 🚨 Rate Limiting Detected
```
📊 Timing Breakdown:
  Average submit time:  2.8s
  Average poll time:    35.4s
  Average results time: 1.1s
  Average total time:   39.3s

⚠️  Issues Detected:
  🚨 Rate limiting: 15 occurrences
     → Recommendation: Increase --delay from 1.5s to 3.0s
     → Recommendation: Reduce --workers from 3 to 2
```

**Diagnosis:** vscan.dev API is rate-limiting your requests.

**Solution:**
```bash
vscan scan --workers 2 --delay 3.0
```

Or in `~/.vscanrc`:
```ini
[scan]
workers = 2
delay = 3.0
```

#### 🐢 Slow API Performance
```
📊 Timing Breakdown:
  Average submit time:  1.5s
  Average poll time:    120.8s  ← Very slow!
  Average results time: 0.9s
  Average total time:   123.2s

⚠️  Issues Detected:
  🐢 Slow analysis: Average 2m 0.8s per extension
     → Issue: vscan.dev API analysis is slow
     → Not a configuration issue - API performance degraded
```

**Diagnosis:** The vscan.dev API is taking ~2 minutes per extension (vs ~35s normal).

**This is NOT your implementation's fault** - the vscan.dev API performance has degraded.

**Solutions:**
1. **Use cache aggressively**: Don't clear cache, scan less frequently
2. **Sequential mode**: More reliable when API is unstable
3. **Wait**: Check if API performance improves later

Conservative configuration:
```bash
vscan scan --workers 1 --delay 2.0
```

#### ⏱️ Timeout Issues
```
⚠️  Issues Detected:
  ⏱️  Timeouts: 8 occurrences
     → Recommendation: API may be slow, consider sequential mode
```

**Diagnosis:** Network timeouts or API instability.

**Solution:**
```bash
# Sequential is more reliable when API is unstable
vscan scan --workers 1
```

### Step 5: Recommendations

Based on all metrics, provides tailored advice:

#### Scenario 1: Rate Limiting
```
🎯 Recommended Configuration (Rate Limiting Detected):
   ~/.vscanrc:
   [scan]
   workers = 2
   delay = 3.0

   Command line:
   vscan scan --workers 2 --delay 3.0
```

#### Scenario 2: API Degradation
```
🎯 Root Cause: vscan.dev API Performance Degradation
   The vscan.dev API analysis is taking significantly longer.
   This is not a configuration issue with your scanner.

   Options:
   1. Use cache aggressively: Scan less frequently
   2. Use sequential mode: More reliable but slower
   3. Wait for API performance to improve

   Conservative configuration:
   ~/.vscanrc:
   [scan]
   workers = 1
   delay = 2.0
```

#### Scenario 3: Optimal Performance
```
🎯 Current Configuration is Optimal:
   Your parallel scanning is working well.

   Keep current settings:
   ~/.vscanrc:
   [scan]
   workers = 3
   delay = 1.5
```

## Common Patterns

### Pattern 1: 20x Slowdown (API Degradation)

**Symptoms:**
- Used to scan in 1 minute, now takes 20 minutes
- Average poll time > 60s (was ~35s)
- No rate limiting detected
- Retry rate is normal

**Diagnosis:** vscan.dev API performance degraded

**Solution:** Not a configuration issue. Use cache, scan less frequently, or wait for API to improve.

### Pattern 2: Rate Limiting

**Symptoms:**
- Rate limiting errors (429)
- High retry rate (>30% of requests)
- Parallel scan not much faster than sequential

**Diagnosis:** Hitting vscan.dev rate limits

**Solution:**
```bash
vscan scan --workers 2 --delay 3.0
```

### Pattern 3: Network Instability

**Symptoms:**
- Frequent timeouts
- High workflow retry rate
- Variable performance

**Diagnosis:** Network/API instability

**Solution:**
```bash
# Sequential is more reliable
vscan scan --workers 1 --delay 2.0
```

## Advanced Diagnostics

### Testing Different Configurations

Compare multiple configurations:

```bash
# Baseline (your current issue)
python3 scripts/diagnose_performance.py

# Conservative (slower but reliable)
python3 scripts/diagnose_performance.py --workers 1 --delay 2.0

# Aggressive (fast but may hit limits)
python3 scripts/diagnose_performance.py --workers 5 --delay 1.0

# Balanced
python3 scripts/diagnose_performance.py --workers 2 --delay 3.0
```

### Monitoring Over Time

Run diagnostics periodically to track API performance:

```bash
# Save timestamped reports
python3 scripts/diagnose_performance.py --output "diagnostic_$(date +%Y%m%d_%H%M%S).txt"
```

Compare reports to see if API performance is improving or degrading.

## Timing Statistics Explained

### Submit Time
- Time to submit extension analysis request
- Normal: 0.5s - 2s
- High (>3s): Rate limiting or network issues

### Poll Time
- Time waiting for analysis to complete
- Normal: 30s - 45s
- High (>60s): API analysis is slow
- Very high (>120s): API performance degraded

### Results Time
- Time to retrieve analysis results
- Normal: 0.5s - 1.5s
- High (>3s): Network or API issues

### Total Time
- End-to-end scan time per extension
- Normal: 35s - 50s
- High (>60s): Check poll time for root cause

## Recommendations Summary

| Issue | Workers | Delay | Notes |
|-------|---------|-------|-------|
| Rate limiting | 2 | 3.0s | Slower but respects limits |
| API degradation | 1 | 2.0s | Sequential more reliable |
| Timeouts | 1 | 2.0s | Reduce load on API |
| Optimal | 3 | 1.5s | Default configuration |

## See Also

- [PERFORMANCE.md](PERFORMANCE.md) - Performance benchmarks and optimization
- [ARCHITECTURE.md](ARCHITECTURE.md) - Parallel scanning architecture
- [API_REFERENCE.md](API_REFERENCE.md) - vscan.dev API documentation
