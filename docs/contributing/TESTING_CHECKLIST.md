# Testing Checklist

**Document Type:** Timeless Reference
**Last Updated:** 2025-10-31

Comprehensive testing checklist for functional, performance, security, and compatibility validation.

**Version-Specific Details:** See [CHANGELOG.md](../../CHANGELOG.md) for version history and [docs/archive/summaries/](../archive/summaries/) for version-specific release notes.

**Current Test Suite:** Run `pytest --collect-only -q tests/` to see current test modules and counts.

---

## Core Functionality

### CLI Commands

- [ ] `vscan scan` (default 3 workers)
- [ ] `vscan scan --plain` (text-only, CI/CD friendly)
- [ ] `vscan scan --quiet` (single-line summary)
- [ ] `vscan --version`
- [ ] `vscan --help`
- [ ] `vscan cache stats`
- [ ] `vscan cache stats --cache-max-age 14`
- [ ] `vscan cache clear` (with confirmation)
- [ ] `vscan cache clear --force`
- [ ] `vscan config init`
- [ ] `vscan config show`
- [ ] `vscan config set scan.workers 3`
- [ ] `vscan config get scan.workers`
- [ ] `vscan config reset`
- [ ] `vscan report report.html`
- [ ] `vscan report results.json`
- [ ] `vscan report results.csv`

### Output Formats

**Terminal (Rich)**
- [ ] Formatted tables with colors
- [ ] Progress bars show worker count
- [ ] Cache indicators (⚡)
- [ ] Risk level colors (red/yellow/green)
- [ ] Verified publisher checkmarks

**JSON**
- [ ] `vscan scan --output results.json`
- [ ] Valid JSON structure
- [ ] Schema version present
- [ ] All required fields
- [ ] Proper character escaping

**HTML Reports**
- [ ] `vscan scan --output report.html`
- [ ] Self-contained (no external deps)
- [ ] Sortable tables work
- [ ] Risk filters functional
- [ ] Search works
- [ ] Charts render (pie, gauge, bar)
- [ ] Print-optimized

**CSV Export**
- [ ] `vscan scan --output results.csv`
- [ ] 15-column format
- [ ] CSV escaping correct
- [ ] UTF-8 encoding
- [ ] Opens in Excel/Sheets

### Filtering Options

- [ ] `--publisher microsoft` (exact, case-insensitive)
- [ ] `--publisher nonexistent` (no results, helpful message)
- [ ] `--min-risk-level low` (all)
- [ ] `--min-risk-level medium` (medium/high/critical)
- [ ] `--min-risk-level high` (high/critical)
- [ ] `--min-risk-level critical` (critical only)
- [ ] `--include-ids "id1,id2"` (comma-separated)
- [ ] `--exclude-ids "id1"` (exclude specific)
- [ ] `--verified-only` (verified publishers)
- [ ] `--unverified-only` (unverified publishers)
- [ ] `--with-vulnerabilities` (only vulns)
- [ ] `--without-vulnerabilities` (only clean)

---

## Parallel Processing

### Worker Configuration

- [ ] `--workers 1` (sequential, one at a time)
- [ ] Default (3 workers, ~4.88x speedup)
- [ ] `--workers 5` (maximum, ~4.27x speedup, 96.7%+ success rate)

### Thread Safety

- [ ] Main-thread-only cache writes (no SQLite locks)
- [ ] Stats collection correct (no race conditions)
- [ ] Progress display clean (no garbled output)
- [ ] Worker count displayed correctly
- [ ] Completion percentage accurate

### Performance Targets

**Small (10 extensions)**
- [ ] Sequential: ~15s baseline
- [ ] 3 workers: ~4x speedup
- [ ] 5 workers: ~4-5x speedup

**Medium (30 extensions)**
- [ ] Sequential: ~45s baseline
- [ ] 3 workers: ~4.5x speedup

**Large (66 extensions)**
- [ ] Sequential: ~6 min baseline
- [ ] 3 workers: ~4.8x speedup (1.2 min)
- [ ] 5 workers: ~4.3x speedup (1.4 min)

**Memory**
- [ ] Peak < 100MB regardless of workers
- [ ] No memory leaks
- [ ] Monitor with `ps aux` or Activity Monitor

---

## Caching System

### Basic Operations

- [ ] First scan creates `~/.vscan/cache.db`
- [ ] Second scan uses cache (⚡ indicator)
- [ ] Cache hits ~50x faster than fresh
- [ ] Default 7-day max age
- [ ] `--cache-max-age 14` custom expiry
- [ ] Expired entries refresh automatically
- [ ] `--refresh-cache` forces fresh scans
- [ ] `--no-cache` disables caching

### Statistics

- [ ] `vscan cache stats` shows totals
- [ ] From cache vs fresh counts
- [ ] Cache hit rate percentage
- [ ] Total cached extensions
- [ ] Stale entries detection
- [ ] `vscan cache clear` with confirmation
- [ ] `--force` skips confirmation
- [ ] Database file deleted after clear

### Integrity

- [ ] Current schema version validated
- [ ] Automatic migration from older schemas
- [ ] Corrupted databases handled gracefully
- [ ] Extension ID + version as key
- [ ] Version changes invalidate cache
- [ ] Failed scans not cached

---

## Extension Discovery

### Platform Paths

**macOS**
- [ ] Default: `~/.vscode/extensions/`
- [ ] Insiders: `~/.vscode-insiders/extensions/`
- [ ] Custom: `--extensions-dir /path`

**Windows**
- [ ] Default: `%USERPROFILE%\.vscode\extensions\`
- [ ] Handles spaces in paths
- [ ] Backslash separators

**Linux**
- [ ] Default: `~/.vscode/extensions/`
- [ ] Snap installations
- [ ] Flatpak installations

### Edge Cases

- [ ] No VS Code: clear error, suggest `--extensions-dir`, exit 2
- [ ] Empty directory: "0 scanned", exit 0
- [ ] Missing package.json: warn and skip
- [ ] Invalid JSON: warn and skip
- [ ] Missing required fields: warn and skip
- [ ] Corrupted extensions continue scan
- [ ] Duplicates: only current version scanned
- [ ] Installation dates from extensions.json
- [ ] Last scanned timestamp in cache
- [ ] Date sorting in HTML reports

---

## API Integration

### Basic Workflow

- [ ] Analyze endpoint (POST, returns analysisId)
- [ ] Popular extensions cached (instant)
- [ ] Status endpoint (GET, polls until complete)
- [ ] Progress field updates
- [ ] Results endpoint (GET, complete analysis)

### Retry Mechanism

- [ ] Exponential backoff (2s, 4s, 8s)
- [ ] Respect Retry-After header
- [ ] Default 3 attempts
- [ ] `--max-retries` configurable
- [ ] `--max-retries 0` disables
- [ ] `--retry-delay` custom delay

### Error Handling

**Network Errors**
- [ ] Connection timeout (30s)
- [ ] DNS failure handled
- [ ] Clear error messages
- [ ] Retry logic activated

**HTTP Errors**
- [ ] 404: extension doesn't exist
- [ ] 429: rate limited, retry with backoff
- [ ] 500: internal error, retry
- [ ] 503: service unavailable, retry

**Invalid Responses**
- [ ] Malformed JSON handled
- [ ] Missing fields handled
- [ ] Unexpected statuses handled
- [ ] Graceful degradation

---

## Configuration Management

### File Operations

- [ ] Init: creates `~/.vscanrc` with defaults
- [ ] Won't overwrite existing (error)
- [ ] Proper permissions (600)
- [ ] Show: displays all settings
- [ ] Config vs default values shown
- [ ] Set: `vscan config set scan.delay 2.0`
- [ ] Type validation (int, float, bool, choice, path)
- [ ] Range validation (min/max)
- [ ] Get: returns single value
- [ ] Shows default if not set
- [ ] Reset: deletes config file
- [ ] Confirmation prompt
- [ ] `--force` skips confirmation

### Validation

**Type Checking**
- [ ] Integers: workers, max_retries, cache_max_age
- [ ] Floats: delay, retry_delay
- [ ] Booleans: quiet, plain, no_cache
- [ ] Strings: publisher, exclude_ids
- [ ] Paths: extensions_dir, cache_dir

**Range Validation**
- [ ] workers: 1-5
- [ ] delay: 0.0-10.0
- [ ] max_retries: 0-10
- [ ] cache_max_age: 1-365 days

**Choice Validation**
- [ ] min_risk_level: low|medium|high|critical
- [ ] Invalid choices rejected

**Priority**
- [ ] CLI args override config
- [ ] Config overrides defaults
- [ ] All combinations tested

---

## Security

### Path Validation

- [ ] Reject `../../../etc/passwd`
- [ ] Reject system paths (/etc, /sys, /var)
- [ ] Reject Windows system paths (C:\Windows)
- [ ] Allow temp directories
- [ ] Block SQL injection patterns
- [ ] Block path traversal in IDs
- [ ] Block boolean injection
- [ ] Proper sanitization

### Network Security

- [ ] All requests HTTPS
- [ ] Certificate validation enabled
- [ ] No insecure fallbacks
- [ ] No credentials in output
- [ ] No user paths in JSON
- [ ] Error messages sanitized
- [ ] No information disclosure

### Input Sanitization

- [ ] Publisher names escaped
- [ ] Extension IDs validated
- [ ] Paths normalized
- [ ] No code injection

---

## Error Handling

### Error Messages

- [ ] Clear and actionable
- [ ] Describe problem
- [ ] Suggest fix
- [ ] Reference docs
- [ ] No stack traces (unless verbose)
- [ ] Error codes (E001-E099: config, E100-E199: discovery, E200-E299: API, E300-E399: cache)

### Exit Codes

**See [ERROR_HANDLING.md § Exit Codes](../guides/ERROR_HANDLING.md#exit-codes) for complete documentation.**

- [ ] 0: Success, no vulnerabilities
- [ ] 1: Success, vulnerabilities found
- [ ] 2: Scan failed (network/config/system errors)

### Progress Indicators

**Rich Mode (default)**
- [ ] Live progress bar
- [ ] Extension name shown
- [ ] Worker count displayed
- [ ] Cache indicators (⚡, 🔍)
- [ ] Status symbols (✓, ⚠, ✗)

**Plain Mode (`--plain`)**
- [ ] Text-only progress
- [ ] Per-extension status
- [ ] No special characters
- [ ] CI/CD friendly

**Quiet Mode (`--quiet`)**
- [ ] Single-line summary
- [ ] "Scanned X - Found Y"
- [ ] Exit code for automation

---

## Cross-Platform Compatibility

### Operating Systems

- [ ] macOS 13+ (Ventura, Sonoma, Sequoia)
- [ ] Windows 10/11
- [ ] Ubuntu 22.04 / 24.04 LTS
- [ ] Fedora (latest)
- [ ] Debian (stable)

### Python Versions

- [ ] Python 3.8
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12

### Dependencies

- [ ] Rich ≥13.0.0 installs
- [ ] Typer ≥0.9.0 installs
- [ ] All features work with required deps
- [ ] `--plain` provides fallback

---

## Performance Benchmarks

### Resource Usage

**Memory**
- [ ] Peak < 100MB
- [ ] No leaks
- [ ] GC works

**CPU**
- [ ] Appropriate for worker count
- [ ] No busy loops
- [ ] Efficient threading

**Network**
- [ ] Respects rate limits
- [ ] No excessive requests
- [ ] Parallel handling

**Cache**
- [ ] Hits < 0.1s per extension
- [ ] 50x faster than fresh
- [ ] 70-90% hit rate typical

---

## Integration & Real-World Scenarios

### Use Cases

- [ ] Developer machine (30-50 extensions)
- [ ] CI/CD pipeline (automated, exit codes)
- [ ] Team audit (HTML reports)

### Workflows

**Initial Setup**
- [ ] Install vscan
- [ ] Create config
- [ ] First scan

**Regular Usage**
- [ ] Daily/weekly rescans
- [ ] Cache utilization
- [ ] Report generation

---

## Documentation

### Accuracy

- [ ] README.md examples work
- [ ] CLAUDE.md instructions current
- [ ] CHANGELOG.md complete
- [ ] docs/guides/ accurate

### Completeness

- [ ] All features documented
- [ ] Migration guides clear
- [ ] Error messages reference docs
- [ ] Examples cover common cases

---

## Test Execution

### Automated Testing

**Quick Test Modes:**
```bash
# Security-only (fast validation, ~1 min)
python3 scripts/run_tests.py --security-only

# Pre-release validation (comprehensive, ~5 min)
python3 scripts/run_tests.py --pre-release

# Smoke test built package
python3 scripts/run_tests.py --smoke dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl
```

**Standard Test Modes:**
```bash
# Run all tests
pytest tests/

# Run with test runner
python3 scripts/run_tests.py --all

# Fast development tests
python3 scripts/run_tests.py --fast

# CI preset
python3 scripts/run_tests.py --ci
```

**Current modules:** Run `pytest --collect-only -q tests/` for complete list.

### Manual Testing

**Pre-Release (Automated)**
```bash
# Comprehensive pre-release validation
python3 scripts/run_tests.py --pre-release
```

Validates:
1. Version consistency across all files
2. Git repository status (clean working directory, on main/master)
3. Core test suite (unit + security + architecture)
4. Security scans (bandit, safety, pip-audit)
5. Test coverage threshold (52%+)

**Pre-Release (Manual Alternative)**
1. Build package
2. Install in clean virtualenv
3. Run through checklist

**Platform Testing**
1. Test on macOS, Windows, Linux
2. Test multiple Python versions
3. Verify all features

**Performance Testing**
1. Benchmark timing
2. Monitor resources
3. Verify speedups

### Tools

- `pytest` - Unit/integration tests
- `time` - Execution timing
- `memory_profiler` - Memory usage
- `tox` - Multi-version testing
- VMs - Cross-platform

---

## Pre-Release Checklist

Before release:

- [ ] All automated tests pass
- [ ] Manual testing complete (primary platform)
- [ ] Cross-platform tested
- [ ] Performance meets targets
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Migration guide (if breaking changes)
- [ ] Build and install tested
- [ ] Smoke test passed

---

**Maintained By:** Project contributors
**Questions:** See [CHANGELOG.md](../../CHANGELOG.md) for version changes
