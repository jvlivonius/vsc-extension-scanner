# VS Code Extension Scanner - Testing Checklist

**Document Type:** Timeless Reference
**Last Updated:** 2025-10-30

This comprehensive checklist covers functional, performance, security, and compatibility testing for the VS Code Extension Scanner.

**Note:** For version-specific testing scenarios, breaking changes, and regression tests, see:
- [CHANGELOG.md](../../CHANGELOG.md) - Version history and changes
- [docs/archive/summaries/](../archive/summaries/) - Version-specific release notes
- [docs/project/STATUS.md](../project/STATUS.md) - Current project state

---

## Core Functionality Testing

### CLI Commands

- [ ] **Main scan command**
  - `vscan scan` - Standard scan with default 3 workers
  - `vscan scan --plain` - Plain output without Rich
  - `vscan scan --quiet` - Minimal single-line output
  - `vscan --version` - Version information
  - `vscan --help` - Main help message

- [ ] **Cache commands**
  - `vscan cache stats` - Display cache statistics
  - `vscan cache stats --cache-max-age 14` - Show stale entries
  - `vscan cache clear` - Clear cache with confirmation
  - `vscan cache clear --force` - Clear without confirmation

- [ ] **Config commands** (v3.1.0+)
  - `vscan config init` - Create default config file
  - `vscan config show` - Display current configuration
  - `vscan config set scan.workers 3` - Set config value
  - `vscan config get scan.workers` - Get specific value
  - `vscan config reset` - Delete config file with confirmation

- [ ] **Report commands**
  - `vscan report report.html` - Generate HTML from cache
  - `vscan report results.json` - Generate JSON from cache
  - `vscan report results.csv` - Generate CSV from cache

### Output Formats

- [ ] **Terminal output (default)**
  - Rich formatted tables with colors
  - Progress bars with worker count displayed
  - Cache hit indicators (⚡)
  - Risk level color coding (red/yellow/green)
  - Verified publisher checkmarks

- [ ] **JSON output**
  - `vscan scan --output results.json`
  - Schema version 2.1
  - Valid JSON structure
  - All required fields present
  - Proper escaping of special characters

- [ ] **HTML reports** (v2.2.0+)
  - `vscan scan --output report.html`
  - Self-contained (no external dependencies)
  - Sortable tables work
  - Risk filters functional
  - Search functionality works
  - Charts render correctly (pie, gauge, bar)
  - Print-optimized layout

- [ ] **CSV export** (v3.1.0+)
  - `vscan scan --output results.csv`
  - 15-column format
  - Proper CSV escaping (commas, quotes, newlines)
  - UTF-8 encoding
  - Opens correctly in Excel, Google Sheets

### Filtering Options

- [ ] **Publisher filter**
  - `--publisher microsoft` (exact match, case-insensitive)
  - `--publisher nonexistent` (no results, helpful message)

- [ ] **Risk level filter**
  - `--min-risk-level low` (all extensions)
  - `--min-risk-level medium` (medium/high/critical)
  - `--min-risk-level high` (high/critical only)
  - `--min-risk-level critical` (critical only)

- [ ] **Extension ID filters**
  - `--include-ids "ms-python.python,GitHub.copilot"` (comma-separated)
  - `--exclude-ids "local.test-extension"` (exclude specific)
  - Combined with other filters

- [ ] **Verification filters** (v3.3.0+)
  - `--verified-only` (only verified publishers)
  - `--unverified-only` (only unverified publishers)

- [ ] **Vulnerability filters** (v3.3.0+)
  - `--with-vulnerabilities` (only extensions with vulns)
  - `--without-vulnerabilities` (only clean extensions)

---

## Parallel Processing & Performance

### Worker Configuration

- [ ] **Sequential mode (1 worker)**
  - `vscan scan --workers 1`
  - Verify sequential execution (one at a time)
  - Compare timing with parallel modes

- [ ] **Default mode (3 workers)**
  - `vscan scan` (no flags)
  - Verify 3 workers in progress display
  - ~4.88x faster than sequential
  - Measure actual speedup

- [ ] **Maximum performance (5 workers)**
  - `vscan scan --workers 5`
  - ~4.27x faster than sequential
  - No rate limiting errors
  - 96.7%+ success rate

### Thread Safety

- [ ] **Cache writes**
  - Verify main-thread-only cache writes
  - No SQLite "database is locked" errors
  - Batch writes after parallel completion
  - No cross-thread connection errors

- [ ] **Statistics collection**
  - Verify stats are collected correctly
  - No race conditions in counters
  - Final totals match actual results

- [ ] **Progress display**
  - Progress updates work correctly
  - No garbled output from concurrent threads
  - Worker count displayed correctly
  - Completion percentage accurate

### Performance Benchmarks

- [ ] **Small set (10 extensions)**
  - Sequential: ~15 seconds
  - 3 workers: ~3-4 seconds
  - Speedup: ~4x

- [ ] **Medium set (30 extensions)**
  - Sequential: ~45 seconds
  - 3 workers: ~10 seconds
  - Speedup: ~4.5x

- [ ] **Large set (66 extensions)**
  - Sequential: ~6 minutes
  - 3 workers: ~1.2 minutes
  - Speedup: ~4.8x

- [ ] **Memory usage**
  - < 100MB RAM regardless of worker count
  - No memory leaks
  - Monitor with `ps aux` or Activity Monitor

---

## Caching System

### Basic Cache Operations

- [ ] **Cache creation**
  - First scan creates `~/.vscan/cache.db`
  - SQLite database format
  - Schema version 2.1

- [ ] **Cache hits**
  - Second scan uses cached results (⚡ indicator)
  - Instant results for cached extensions
  - ~50x faster than fresh scans

- [ ] **Cache expiration**
  - Default 7 days max age
  - `--cache-max-age 14` custom expiry
  - Expired entries refreshed automatically

- [ ] **Cache refresh**
  - `--refresh-cache` forces fresh scans
  - `--no-cache` disables caching entirely
  - Refresh only scanned extensions (not all)

### Cache Statistics

- [ ] **Stats display**
  - `vscan cache stats` shows totals
  - From cache vs fresh scans count
  - Cache hit rate percentage
  - Total cached extensions
  - Stale entries detection

- [ ] **Cache clearing**
  - `vscan cache clear` with confirmation
  - `vscan cache clear --force` without confirmation
  - Verify database file is deleted

### Cache Integrity

- [ ] **Schema version**
  - Current schema: 2.1
  - Automatic migration from 2.0 → 2.1
  - Handles corrupted databases gracefully

- [ ] **Data consistency**
  - Extension ID + version as key
  - Version changes invalidate cache
  - Failed scans not cached

---

## Extension Discovery

### Platform-Specific Paths

- [ ] **macOS**
  - Default: `~/.vscode/extensions/`
  - VS Code Insiders: `~/.vscode-insiders/extensions/`
  - Custom: `--extensions-dir /custom/path`

- [ ] **Windows**
  - Default: `%USERPROFILE%\.vscode\extensions\`
  - Handles paths with spaces
  - Backslash path separators

- [ ] **Linux**
  - Default: `~/.vscode/extensions/`
  - Snap installations
  - Flatpak installations

### Edge Cases

- [ ] **No VS Code installed**
  - Clear error message
  - Exit code 2
  - Suggest using `--extensions-dir`

- [ ] **Empty extensions directory**
  - Complete with "0 extensions scanned"
  - Exit code 0
  - No errors

- [ ] **Corrupted extensions** (v3.3.3+)
  - Missing package.json - warn and skip
  - Invalid JSON - warn and skip
  - Missing required fields - warn and skip
  - Continue scanning remaining extensions

- [ ] **Duplicate extensions** (v3.3.3+)
  - Old versions on disk ignored
  - Only current version from extensions.json scanned
  - No duplicate entries in results

### Installation Date Tracking (v3.3.1+)

- [ ] **Date tracking**
  - Installation dates from extensions.json
  - Last scanned timestamp in cache
  - Dates display in HTML reports

- [ ] **Date sorting** (v3.3.2+)
  - HTML report date columns sortable
  - ISO date format for sorting
  - N/A dates sorted to end

---

## vscan.dev API Integration

### Basic API Workflow

- [ ] **Analyze endpoint**
  - POST with publisher + name
  - Returns analysisId
  - Popular extensions cached (instant)

- [ ] **Status endpoint**
  - GET with analysisId
  - Polls until "completed"
  - Progress field updates

- [ ] **Results endpoint**
  - GET with analysisId
  - Complete security analysis
  - All fields populated

### Retry Mechanism (v2.2.0+)

- [ ] **Exponential backoff**
  - First retry: 2 seconds
  - Second retry: 4 seconds
  - Third retry: 8 seconds
  - Configurable via `--retry-delay`

- [ ] **Retry-After header**
  - Respect server rate limits
  - Honor Retry-After header
  - Graceful handling

- [ ] **Max retries**
  - Default: 3 attempts
  - Configurable via `--max-retries`
  - `--max-retries 0` disables retries

### Error Handling

- [ ] **Network errors**
  - Connection timeout (30 seconds)
  - DNS failure
  - Clear error messages
  - Retry logic activated

- [ ] **HTTP errors**
  - 404 Not Found (extension doesn't exist)
  - 429 Rate Limited (retry with backoff)
  - 500 Internal Server Error (retry)
  - 503 Service Unavailable (retry)

- [ ] **Invalid responses**
  - Malformed JSON
  - Missing fields
  - Unexpected status values
  - Graceful degradation

---

## Configuration Management (v3.1.0+)

### Config File Operations

- [ ] **Init command**
  - Creates `~/.vscanrc` with defaults
  - Won't overwrite existing (error)
  - Proper permissions (600)

- [ ] **Show command**
  - Displays all settings
  - Shows config vs default values
  - Unified table format (scan.delay, cache.max_age)

- [ ] **Set command**
  - `vscan config set scan.delay 2.0`
  - Type validation (int, float, bool, choice, path)
  - Range validation (min/max values)

- [ ] **Get command**
  - Returns single value
  - Shows default if not set
  - Clear output

- [ ] **Reset command**
  - Deletes config file
  - Confirmation prompt
  - `--force` to skip confirmation

### Config Validation

- [ ] **Type checking**
  - Integers: workers, max_retries, cache_max_age
  - Floats: delay, retry_delay
  - Booleans: quiet, plain, no_cache
  - Strings: publisher, exclude_ids
  - Paths: extensions_dir, cache_dir

- [ ] **Range validation**
  - workers: 1-5
  - delay: 0.0-10.0
  - max_retries: 0-10
  - cache_max_age: 1-365 days

- [ ] **Choice validation**
  - min_risk_level: low|medium|high|critical
  - Invalid choices rejected

### Config Priority

- [ ] **Hierarchy**
  - CLI arguments override config
  - Config overrides defaults
  - Test all combinations

---

## Security Testing

### Path Validation

- [ ] **Path traversal protection**
  - Reject `--extensions-dir ../../../etc/passwd`
  - Reject system paths (/etc, /sys, /var)
  - Reject Windows system paths (C:\Windows)
  - Allow temp directories

- [ ] **Extension ID validation**
  - Block SQL injection patterns
  - Block path traversal in IDs
  - Block boolean injection
  - Proper sanitization

### Network Security

- [ ] **HTTPS enforcement**
  - All requests use HTTPS
  - Certificate validation enabled
  - No insecure fallbacks

- [ ] **Data privacy**
  - No credentials in output
  - No user paths in JSON
  - Error messages sanitized
  - No information disclosure

### Input Sanitization

- [ ] **String inputs**
  - Publisher names escaped
  - Extension IDs validated
  - Paths normalized
  - No code injection

---

## Error Handling & UX

### Error Messages

- [ ] **Clear and actionable**
  - Describe what went wrong
  - Suggest how to fix
  - Reference documentation
  - No stack traces (unless verbose)

- [ ] **Error codes** (v3.2.0+)
  - E001-E099: Configuration errors
  - E100-E199: Discovery errors
  - E200-E299: API errors
  - E300-E399: Cache errors

### Exit Codes

**For complete exit code documentation, see [ERROR_HANDLING.md § Exit Codes](../guides/ERROR_HANDLING.md#exit-codes)**

Test scenarios:
- [ ] **0** - Success, no vulnerabilities
- [ ] **1** - Success, vulnerabilities found
- [ ] **2** - Scan failed (network, config, or system errors)

### Progress Indicators

- [ ] **Rich mode** (default)
  - Live progress bar
  - Extension name shown
  - Worker count displayed
  - Cache indicators (⚡, 🔍)
  - Status symbols (✓, ⚠, ✗)

- [ ] **Plain mode** (`--plain`)
  - Text-only progress
  - Per-extension status
  - No special characters
  - CI/CD friendly

- [ ] **Quiet mode** (`--quiet`)
  - Single-line summary only
  - "Scanned X extensions - Found Y vulnerabilities"
  - Exit code for automation

---

## Cross-Platform Compatibility

### Operating Systems

- [ ] macOS 13+ (Ventura, Sonoma, Sequoia)
- [ ] Windows 10/11
- [ ] Ubuntu 22.04 LTS / 24.04 LTS
- [ ] Fedora (latest)
- [ ] Debian (latest stable)

### Python Versions

- [ ] Python 3.8
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12

### Dependencies

- [ ] **Required**
  - Rich ≥13.0.0
  - Typer ≥0.9.0
  - All dependencies install correctly

- [ ] **Optional** (no longer needed)
  - All features work without optional deps
  - `--plain` provides fallback behavior

---

## Performance Testing

### Timing Benchmarks

- [ ] **10 extensions**
  - Sequential (1 worker): ~15s
  - Default (3 workers): ~3-4s
  - Maximum (5 workers): ~3s

- [ ] **30 extensions**
  - Sequential: ~45s
  - Default: ~10s
  - Maximum: ~9s

- [ ] **66 extensions** (real-world)
  - Sequential: ~6 minutes
  - Default: ~1.2 minutes (4.88x speedup)
  - Maximum: ~1.4 minutes (4.27x speedup)

### Resource Usage

- [ ] **Memory**
  - Peak RAM < 100MB
  - No memory leaks
  - Garbage collection works

- [ ] **CPU**
  - Appropriate CPU usage for worker count
  - No busy loops
  - Efficient threading

- [ ] **Network**
  - Respects API rate limits
  - No excessive requests
  - Parallel requests handled

### Cache Performance

- [ ] **Cache hits**
  - Instant results (< 0.1s per extension)
  - 50x faster than fresh scans
  - 70-90% hit rate typical

---

## Integration Testing

### Real-World Scenarios

- [ ] **Developer machine**
  - 30-50 extensions
  - Mix of popular and custom
  - Regular rescans

- [ ] **CI/CD pipeline**
  - Automated daily scans
  - Exit code checks
  - JSON/CSV output processing

- [ ] **Team security audit**
  - Generate HTML reports
  - Share with stakeholders
  - Track over time

### End-to-End Workflows

- [ ] **Initial setup**
  - Install vscan
  - Create config file
  - First scan

- [ ] **Regular usage**
  - Daily/weekly rescans
  - Cache utilization
  - Report generation

---

## Documentation Testing

### Accuracy

- [ ] README.md examples work
- [ ] CLAUDE.md instructions current
- [ ] CHANGELOG.md complete
- [ ] docs/guides/ content accurate

### Completeness

- [ ] All features documented
- [ ] Migration guides clear
- [ ] Error messages reference docs
- [ ] Examples cover common use cases

---

## Test Execution Strategy

### Automated Testing

```bash
# Run all tests (recommended)
pytest tests/

# Or run individually (see tests/ directory for current list)
for test in tests/test_*.py; do
    python3 "$test"
done
```

**Current test modules:** See `tests/` directory for complete list and test counts.

### Manual Testing

1. **Pre-release testing**
   - Build package
   - Install in clean virtualenv
   - Run through this checklist

2. **Platform testing**
   - Test on macOS, Windows, Linux
   - Test multiple Python versions
   - Verify all features work

3. **Performance testing**
   - Benchmark timing
   - Monitor resource usage
   - Verify speedups

### Tools

- `pytest` - Unit and integration tests
- `time` - Execution timing
- `memory_profiler` - Memory usage
- `tox` - Multi-version testing
- Virtual machines - Cross-platform

---

## Pre-Release Checklist

Before releasing a new version:

- [ ] All automated tests pass
- [ ] Manual testing on primary platform complete
- [ ] Cross-platform testing done
- [ ] Performance benchmarks meet targets
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Migration guide created (if breaking changes)
- [ ] Build and install tested
- [ ] Smoke test passed

---

**Maintained By:** Project contributors
**Questions:** See [CHANGELOG.md](../../CHANGELOG.md) for version-specific changes
