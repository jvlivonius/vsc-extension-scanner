# Testing Guide

**Document Type:** Timeless Reference
**Applies To:** All 3.x versions
**Major Revision Trigger:** Test framework changes, testing philosophy shifts, or major tool updates
**Target Audience:** Contributors, Developers, QA Engineers
**See:** [CHANGELOG.md](../../CHANGELOG.md) for version-specific test additions

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Organization](#test-organization)
3. [Test Categories](#test-categories)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [Architecture Tests](#architecture-tests)
7. [Security Tests](#security-tests)
8. [Performance Tests](#performance-tests)
9. [Integration Tests](#integration-tests)
10. [Mocking Guidelines](#mocking-guidelines)
11. [Test Coverage](#test-coverage)
12. [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

### Core Principles

**1. Test Behavior, Not Implementation**
```python
# ✅ GOOD - Tests behavior
def test_scan_caches_results():
    """Scan results should be cached for subsequent runs."""
    scanner.scan("ms-python.python")
    first_duration = scanner.duration

    scanner.scan("ms-python.python")
    second_duration = scanner.duration

    assert second_duration < first_duration  # Cached is faster

# ❌ BAD - Tests implementation details
def test_scan_calls_cache_save():
    """Scan should call cache.save_result()."""
    with mock.patch('cache_manager.save_result') as mock_save:
        scanner.scan("ms-python.python")
        assert mock_save.called  # Fragile!
```

**2. Fast Feedback Loop**
- Unit tests run in < 1 second
- Integration tests run in < 10 seconds
- Full suite runs in < 30 seconds

**3. Isolated Tests**
- Tests don't depend on each other
- Tests can run in any order
- Each test cleans up after itself

**4. Clear Failure Messages**
```python
# ✅ GOOD - Clear message
assert result['vulnerabilities'] == 0, \
    f"Expected no vulnerabilities, found {result['vulnerabilities']}"

# ❌ BAD - Vague message
assert result['vulnerabilities'] == 0
```

---

## Test Organization

### Directory Structure

```
tests/
├── test_architecture.py               # Layer compliance and dependency validation
├── test_display.py                    # Terminal formatting and Rich integration
├── test_scanner.py                    # Core scanning workflow and filtering
├── test_cli.py                        # Command-line interface and argument parsing
├── test_api.py                        # API client validation
├── test_security.py                   # Security vulnerability detection
├── test_security_regression.py        # Security regression suite
├── test_path_validation.py            # Path traversal protection
├── test_string_sanitization.py        # String sanitization coverage
├── test_cache_integrity.py            # HMAC cache integrity
├── test_parallel_scanning.py          # Multi-threaded execution
├── test_transactional_cache.py        # Thread-safe cache operations
├── test_performance.py                # Performance benchmarks and profiling
├── test_integration.py                # End-to-end workflow integration
├── test_integration_real_api.py       # Live API integration scenarios
├── test_db_integrity.py               # Database consistency validation
├── test_retry.py                      # Retry mechanism with exponential backoff
├── test_retry_analysis.py             # Retry timing and behavior analysis
├── test_workflow_retry.py             # Workflow-specific retry patterns
├── test_mock_validation.py            # Mock-to-real-API conformance
├── test_failed_extensions.py          # Failed extension tracking and reporting
├── test_verbose_mode.py               # Verbose output mode testing
├── test_config_extensions_dir.py      # Custom extensions directory handling
├── test_report_empty_cache.py         # Empty cache edge case handling
├── fixtures/                          # Test data and fixtures
│   ├── __init__.py
│   └── canonical_mock.py              # Canonical mock implementation
└── conftest.py                        # Pytest configuration and shared fixtures
```

**To see current test counts:** Run `pytest --collect-only -q tests/` or use the test suite runner:
```bash
python3 scripts/run_tests.py --all
```

### Test File Naming

- `test_<module>.py` - Tests for specific module
- `test_<feature>.py` - Tests for specific feature
- Test functions: `test_<what>_<expected_behavior>()`

**Examples:**
```python
# Module tests
test_cache.py: test_cache_hit_returns_cached_result()
test_api.py: test_api_handles_rate_limit_with_retry()

# Feature tests
test_retry.py: test_retry_respects_retry_after_header()
test_security.py: test_path_traversal_blocked()
```

---

## Test Categories

### 1. Unit Tests

**Purpose:** Test individual functions/methods in isolation.

**Characteristics:**
- Fast (< 0.1s each)
- No external dependencies
- Mock all I/O
- High coverage of edge cases

**Example:**
```python
def test_validate_extension_id():
    """Extension ID validation accepts valid IDs and rejects invalid."""
    # Valid IDs
    assert validate_extension_id("ms-python.python") == True
    assert validate_extension_id("GitHub.copilot") == True

    # Invalid IDs
    assert validate_extension_id("invalid") == False
    assert validate_extension_id("'; DROP TABLE") == False
    assert validate_extension_id("../../../etc/passwd") == False
```

### 2. Integration Tests

**Purpose:** Test multiple components working together.

**Characteristics:**
- Moderate speed (1-5s each)
- Real interactions between modules
- Mock only external services (API, filesystem)
- Test workflows

**Example:**
```python
def test_full_scan_workflow():
    """Complete scan workflow from discovery to output."""
    with mock_vscan_api(), temp_cache():
        result = perform_scan(
            extensions_dir="./tests/fixtures/sample_extensions",
            output="results.json"
        )

        # Verify workflow
        assert result['extensions_scanned'] == 3
        assert os.path.exists("results.json")
        assert cache_has_entries() == True
```

### 3. Architecture Tests

**Purpose:** Verify architectural boundaries and dependencies.

**Characteristics:**
- Fast (< 0.5s total)
- Static analysis of imports
- Enforce layering rules
- Prevent architecture erosion

**Example:**
```python
def test_infrastructure_layer_isolation():
    """Infrastructure modules don't import from application/presentation."""
    infrastructure = ['vscan_api', 'cache_manager', 'extension_discovery']
    forbidden = ['scanner', 'cli', 'display']

    for module in infrastructure:
        imports = get_module_imports(f'vscode_scanner.{module}')
        for forbidden_module in forbidden:
            assert forbidden_module not in imports, \
                f"{module} should not import {forbidden_module}"
```

### 4. Security Tests

**Purpose:** Verify security controls and prevent vulnerabilities.

**Characteristics:**
- Test malicious inputs
- Verify sanitization
- Check path traversal protection
- Validate SQL injection prevention

**Example:**
```python
def test_sql_injection_prevention():
    """Extension IDs are validated before database operations."""
    cache = CacheManager()

    malicious_ids = [
        "'; DROP TABLE scan_cache; --",
        "' OR '1'='1",
        "../../etc/passwd",
    ]

    for malicious_id in malicious_ids:
        # Should not crash or execute malicious SQL
        with pytest.raises(ValidationError):
            cache.save_result(malicious_id, "1.0", {})
```

### 5. Performance Tests

**Purpose:** Verify performance characteristics and prevent regressions.

**Characteristics:**
- Measure timing and memory
- Compare against baselines
- Test scalability (10, 100, 1000 items)
- Identify bottlenecks

**Example:**
```python
def test_cache_provides_50x_speedup():
    """Cached results are at least 50x faster than fresh scans."""
    with mock_vscan_api(delay=1.0):
        # First scan (fresh)
        start = time.time()
        scan_extension("ms-python.python")
        fresh_duration = time.time() - start

        # Second scan (cached)
        start = time.time()
        scan_extension("ms-python.python")
        cached_duration = time.time() - start

        speedup = fresh_duration / cached_duration
        assert speedup >= 50, f"Expected 50x speedup, got {speedup}x"
```

### 6. End-to-End Tests

**Purpose:** Test complete user workflows.

**Characteristics:**
- Slow (10-30s each)
- Minimal mocking
- Real database and filesystem
- Test from CLI invocation to output

**Example:**
```python
def test_scan_and_report_workflow():
    """User can scan extensions and generate HTML report."""
    runner = CliRunner()

    # Run scan
    result = runner.invoke(app, ["scan", "--output", "scan.json"])
    assert result.exit_code == 0
    assert os.path.exists("scan.json")

    # Generate report
    result = runner.invoke(app, ["report", "report.html"])
    assert result.exit_code == 0
    assert os.path.exists("report.html")

    # Verify report content
    with open("report.html") as f:
        html = f.read()
        assert "<title>VS Code Extension Security Report</title>" in html
```

---

## Running Tests

### Test Suite Runner

The unified test runner provides standardized execution with clear output.

**Quick Start:**
```bash
# Run all tests
python3 scripts/run_tests.py --all

# Run specific groups
python3 scripts/run_tests.py --unit
python3 scripts/run_tests.py --security --architecture
python3 scripts/run_tests.py --unit --security --parallel

# Skip slow tests (faster CI)
python3 scripts/run_tests.py --all --skip-slow

# Skip real API tests
python3 scripts/run_tests.py --all --skip-real-api
```

**Available Test Groups:**

| Flag | Duration | Description |
|------|----------|-------------|
| `--unit` | ~2s | Core functionality (scanner, display, CLI, edge cases) |
| `--security` | ~0.5s | Security validation, path/string sanitization, cache integrity |
| `--architecture` | ~0.2s | Layer compliance, zero violations |
| `--parallel` | ~0.15s | Threading, parallel scanning, thread-safe cache |
| `--integration` | ~1s | Integration tests (mocked API + DB integrity) |
| `--real-api` | ~30s | Real vscan.dev API calls (slow) |
| `--mock-validation` | ~5s | Mock validation against real API |
| `--all` | ~40s | All test groups combined |

**Note:** Run `python3 scripts/run_tests.py --all` to see current test counts for each group.

**Output Formats:**

```bash
# Console (default) - colored, human-readable
python3 scripts/run_tests.py --unit

# JSON output for automation
python3 scripts/run_tests.py --all --output json --output-file results.json

# JUnit XML for CI/CD
python3 scripts/run_tests.py --all --output junit --output-file results.xml

# Quiet mode (summary only)
python3 scripts/run_tests.py --all --quiet

# Verbose mode (include test output)
python3 scripts/run_tests.py --unit --verbose
```

**Example Output:**

```
======================================================================
VS CODE EXTENSION SCANNER - TEST SUITE
======================================================================

Running Test Groups: unit, security
Skip Slow Tests: No
Skip Real API: No

----------------------------------------------------------------------
TEST GROUP: Unit (7 files)
----------------------------------------------------------------------
✓ test_scanner.py                           XX tests   0.018s   PASS
✓ test_display.py                           XX tests   0.003s   PASS
✓ test_cli.py                               XX tests   0.580s   PASS
...

Summary: Run `pytest tests/ -v --tb=no` to see current test counts

----------------------------------------------------------------------
TEST GROUP: Security (5 files)
----------------------------------------------------------------------
✓ test_security.py                          11 tests   0.012s   PASS
...

Summary: XX tests, XX passed, 0 failed, 0 skipped (0.193s)
⚠️  CRITICAL: 0 vulnerabilities confirmed

======================================================================
OVERALL SUMMARY
======================================================================

Total Test Files: Run `pytest --collect-only -q tests/` to see file count
Total Tests Run:  Run `pytest tests/ -v` for current test counts
Total Passed:     Check pytest output for pass/fail breakdown
Total Failed:     0 ✗
Total Skipped:    0 ⊘
Total Duration:   Varies by system (typically <2s for full suite)

Exit Code: 0 (SUCCESS)
======================================================================
```

**CI/CD Integration:**

```yaml
# .github/workflows/tests.yml
- name: Run test suite
  run: |
    python3 scripts/run_tests.py --all --skip-real-api \
      --output junit --output-file test-results.xml

- name: Publish test results
  uses: EnricoMi/publish-unit-test-result-action@v2
  with:
    files: test-results.xml
```

**Exit Codes:**
- `0` - All tests passed (success)
- `1` - Some tests failed
- `2` - No tests found
- `3` - Execution error

---

### Alternative: Individual Test Files

```bash
# Run individual test files directly
python3 tests/test_scanner.py
python3 tests/test_display.py
python3 tests/test_security.py
```

### Alternative: pytest

```bash
# Using pytest (if installed)
pytest tests/ -v
pytest tests/test_scanner.py
pytest -k "cache" -v
pytest -m "not slow"
```

---

## Writing Tests

### Test Structure (AAA Pattern)

```python
def test_cache_hit_returns_cached_result():
    """When extension is in cache, return cached result without API call."""
    # ARRANGE - Set up test conditions
    cache = CacheManager(cache_dir="./test_cache")
    expected_result = {"score": 85, "risk_level": "low"}
    cache.save_result("test.extension", "1.0", expected_result)

    # ACT - Perform the action
    actual_result = cache.get_cached_result("test.extension", "1.0", max_age_days=7)

    # ASSERT - Verify the outcome
    assert actual_result is not None
    assert actual_result['score'] == expected_result['score']
    assert actual_result['risk_level'] == expected_result['risk_level']

    # CLEANUP
    cache.clear_cache()
```

### Test Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_cache_dir():
    """Provide temporary cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_vscan_api():
    """Mock vscan.dev API responses."""
    with mock.patch('vscode_scanner.vscan_api.scan_extension') as mock_scan:
        mock_scan.return_value = {
            "score": 85,
            "risk_level": "low",
            "vulnerabilities": {"total": 0}
        }
        yield mock_scan

@pytest.fixture
def sample_extensions_dir():
    """Provide directory with sample extensions."""
    return Path(__file__).parent / "fixtures" / "sample_extensions"
```

**Usage:**
```python
def test_with_fixtures(temp_cache_dir, mock_vscan_api):
    """Tests automatically get fixtures."""
    cache = CacheManager(cache_dir=temp_cache_dir)
    result = scan_extension("test.ext")
    # Cleanup automatic!
```

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("extension_id,expected_valid", [
    ("ms-python.python", True),
    ("GitHub.copilot", True),
    ("invalid", False),
    ("'; DROP TABLE", False),
    ("../../etc/passwd", False),
])
def test_extension_id_validation(extension_id, expected_valid):
    """Test various extension ID formats."""
    assert validate_extension_id(extension_id) == expected_valid
```

### Test Markers

```python
import pytest

@pytest.mark.slow
def test_scan_100_extensions():
    """Slow test - only run occasionally."""
    # ...

@pytest.mark.integration
def test_full_workflow():
    """Integration test."""
    # ...

@pytest.mark.security
def test_path_traversal_blocked():
    """Security test."""
    # ...
```

**Run marked tests:**
```bash
pytest -m slow        # Run only slow tests
pytest -m "not slow"  # Skip slow tests
pytest -m security    # Run only security tests
```

---

## Architecture Tests

### Purpose

Prevent architecture erosion by automatically verifying:
- Layer boundaries
- Dependency rules
- No circular imports
- Module organization

### Implementation

```python
# tests/test_architecture.py

import ast
import importlib
from pathlib import Path

def get_module_imports(module_name: str) -> set:
    """Extract all imports from a module."""
    module = importlib.import_module(module_name)
    module_file = Path(module.__file__)

    with open(module_file) as f:
        tree = ast.parse(f.read())

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    return imports

def test_infrastructure_layer_isolation():
    """Infrastructure doesn't import from application/presentation."""
    infrastructure_modules = [
        'vscode_scanner.vscan_api',
        'vscode_scanner.cache_manager',
        'vscode_scanner.extension_discovery',
    ]

    forbidden_imports = {
        'scanner', 'cli', 'display',
        'output_formatter', 'html_report_generator',
        'config_manager',
    }

    for module in infrastructure_modules:
        imports = get_module_imports(module)
        forbidden_found = imports & forbidden_imports

        assert not forbidden_found, \
            f"{module} imports forbidden modules: {forbidden_found}"

def test_no_circular_dependencies():
    """No circular import dependencies exist."""
    # Use tools like pydeps or implement cycle detection
    # This is a placeholder for actual implementation
    pass
```

---

## Security Tests

### Overview

Security testing is divided into multiple specialized test suites:
- **test_security.py** - Core security vulnerability tests
- **test_path_validation.py** - Comprehensive path validation coverage
- **test_string_sanitization.py** - String sanitization in all contexts
- **test_cache_integrity.py** - HMAC signature validation
- **test_security_regression.py** - Regression suite for all fixed vulnerabilities

**To see current test counts:** Run `pytest --collect-only -q tests/test_security*.py tests/test_path*.py tests/test_string*.py tests/test_cache*.py`

### Path Validation Tests

```python
def test_path_traversal_blocked():
    """validate_path() blocks all path traversal attempts."""
    from vscode_scanner.utils import validate_path

    dangerous_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\Windows\\System32",
        "/etc/passwd",
        "C:\\Windows\\System32",
        "%2e%2e%2f/etc/passwd",  # URL-encoded traversal
        "~/../.ssh/id_rsa",       # Shell expansion
    ]

    for dangerous in dangerous_paths:
        with pytest.raises(ValueError, match="Invalid path"):
            validate_path(dangerous, path_type="output")
```

### String Sanitization Tests

```python
def test_string_sanitization_prevents_injection():
    """sanitize_string() prevents terminal and log injection."""
    from vscode_scanner.utils import sanitize_string

    # Test ANSI escape sequences (terminal injection)
    ansi_input = "\x1b[31mRed Text\x1b[0m"
    result = sanitize_string(ansi_input, context="output")
    assert "\x1b" not in result

    # Test path disclosure in errors
    error_with_path = "File not found: /Users/john/secret/keys.json"
    sanitized = sanitize_string(error_with_path, context="error", max_length=100)
    assert "/Users/john" not in sanitized
    assert "keys.json" not in sanitized

    # Test control characters
    control_chars = "Normal\x00text\x01with\x1fcontrol"
    result = sanitize_string(control_chars, context="log")
    assert "\x00" not in result
    assert "\x01" not in result
```

### Cache Integrity Tests

```python
def test_cache_integrity_hmac_validation():
    """HMAC signatures prevent cache tampering."""
    from vscode_scanner.cache_manager import CacheManager

    cache = CacheManager()

    # Cache a result
    extension_id = "test.extension"
    version = "1.0.0"
    result = {"vulnerabilities": [], "risk_score": 0}
    cache.save_result(extension_id, version, result)

    # Tamper with database directly (bypass cache manager)
    import sqlite3
    conn = sqlite3.connect(cache.cache_db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE scan_cache SET vulnerability_data = ? WHERE extension_id = ?",
        ('{"vulnerabilities": ["FAKE"], "risk_score": 10}', extension_id)
    )
    conn.commit()
    conn.close()

    # Attempt to retrieve tampered entry
    cached = cache.get_cached_result(extension_id, version)

    # HMAC verification should detect tampering and reject entry
    assert cached is None, "Tampered cache entry should be rejected"
```

### Security Regression Tests

```python
def test_all_fixed_vulnerabilities_stay_fixed():
    """Regression suite ensures all fixed CVEs stay fixed."""
    # test_security_regression.py contains 24 tests covering:
    # - CWE-22: Path traversal (3 variants fixed)
    # - CWE-400: Resource exhaustion (2 variants fixed)
    # - CWE-345: Data authenticity (HMAC implementation)
    # - CWE-209: Information disclosure (error sanitization)

    # Example: URL-encoded path traversal
    from vscode_scanner.utils import validate_path

    url_encoded_traversal = "data/%2e%2e%2f/etc/passwd"
    with pytest.raises(ValueError):
        validate_path(url_encoded_traversal, path_type="output")
```

### SQLite Security Tests

**Purpose:** Custom security audit for SQLite database usage

**Test File:** `tests/test_sqlite_security.py`

**Coverage:**
- File permissions (0o600 for cache.db, 0o600 for .cache_secret, 0o700 for cache directory)
- SQL injection prevention (parameterized queries only)
- HMAC timing-safe comparison (hmac.compare_digest)
- Database schema integrity
- HMAC signature integrity validation

```python
def test_sqlite_file_permissions():
    """Verify cache database has user-only permissions (0o600)."""
    cache = CacheManager()
    file_stat = os.stat(cache.cache_db)
    file_mode = stat.S_IMODE(file_stat.st_mode)
    assert file_mode == 0o600, f"Cache DB permissions: {oct(file_mode)}"

def test_no_sql_injection_patterns():
    """Scan cache_manager.py for dangerous SQL patterns."""
    dangerous_patterns = ['f"SELECT', 'f"INSERT', '% "SELECT']
    # Verifies all queries use parameterized statements
```

**To run:** `python3 tests/test_sqlite_security.py`

### Automated Security Tools

**Three-Layer Security Automation:**

#### 1. Pre-commit Hooks (Local Prevention)

**Installation:**
```bash
pip install -e .               # Install security tools in [dev]
pre-commit install             # Enable pre-commit hooks
```

**What it runs automatically:**
- **Black** - Code formatting consistency
- **Bandit** - AST-based Python security scanner
- **Pylint Security** - Security-focused linting
- **Security Tests** - All test_security*.py and test_sqlite_security.py

**Manual execution:**
```bash
pre-commit run --all-files     # Test all hooks
pre-commit run bandit          # Run specific hook
```

**Configuration:** `.pre-commit-config.yaml`

#### 2. Bandit Security Scanner

**Purpose:** AST-based static security vulnerability detection for Python

**Installation:** `pip install bandit` (included in `[dev]` extras)

**Usage:**
```bash
# Terminal output
bandit -r vscode_scanner/ -ll

# JSON report (for CI/CD)
bandit -r vscode_scanner/ -ll -f json -o bandit-report.json
```

**What it detects:**
- SQL injection vulnerabilities (B608)
- Weak cryptography (B501-B507) - CRITICAL for HMAC validation
- Unsafe `urllib` usage (B310) - CRITICAL for HTTP client security
- Shell injection (B601-B611)
- Hardcoded credentials (B105-B107)

**Configuration:** `.bandit` file
- Severity: medium or higher
- Confidence: medium or higher
- Excludes: tests/, node_modules/, .git/

**Expected Result:** Zero critical vulnerabilities

#### 3. Safety & pip-audit (Dependency Security)

**Purpose:** Scan Python dependencies for known CVEs

**Installation:**
```bash
pip install safety pip-audit   # Included in [dev] extras
```

**Safety Usage:**
```bash
# Quick check
safety check

# Detailed report
pip freeze > requirements-scan.txt
safety check --file requirements-scan.txt --full-report
```

**pip-audit Usage:**
```bash
# Quick check
pip-audit

# Detailed report
pip-audit --desc --output json > pip-audit-report.json
```

**What they check:**
- **Safety:** 50,000+ known vulnerabilities from Safety DB
- **pip-audit:** OSV (Open Source Vulnerabilities) database
- Both check: Rich (≥13.0.0) and Typer (≥0.9.0) dependencies

**Expected Result:** No high/critical severity vulnerabilities

#### 4. CI/CD Security Workflow

**File:** `.github/workflows/security.yml`

**Triggers:**
- Every push to main/master/develop/claude/** branches
- Every pull request
- Weekly schedule (Monday 00:00 UTC)
- Manual dispatch

**What it runs:**
```yaml
jobs:
  security-scan:
    - Bandit security scan (AST analysis)
    - Safety dependency check (CVE database)
    - pip-audit package audit (OSV database)
    - Security regression tests (95% coverage)
    - Path validation tests
    - String sanitization tests
    - Cache integrity tests (HMAC)
    - SQLite security tests (Phase 1)
```

**Artifacts:** Stores security reports for 90 days

**Failure Conditions:**
- Any security test fails
- Bandit finds critical vulnerabilities
- Safety finds high/critical CVEs
- pip-audit finds high/critical vulnerabilities

### Security Testing Best Practices

**Before Every Commit:**
```bash
# Option 1: Pre-commit hooks (automatic)
pre-commit run --all-files

# Option 2: Manual execution
bandit -r vscode_scanner/ -ll
safety check
pip-audit
python3 tests/test_sqlite_security.py
python3 tests/test_security_regression.py
```

**Tool Priority:**
1. **Security Tests (test_security*.py)** - Highest authority, must pass
2. **Bandit** - AST security analysis, zero critical required
3. **Safety/pip-audit** - Dependency scanning, no high/critical CVEs
4. **Pre-commit** - Prevention layer, catches issues early

**Security Coverage Goals:**
- **Overall:** 85% code coverage
- **Security modules:** 95% coverage (utils.py, cache_manager.py)
- **Security tools:** Zero critical findings
- **Dependency CVEs:** Zero high/critical vulnerabilities

---

## Performance Tests

### Cache Performance

```python
def test_batch_operations_faster_than_individual():
    """Batch cache operations are significantly faster."""
    import time
    from vscode_scanner.cache_manager import CacheManager

    cache = CacheManager()
    test_data = [{"id": f"ext{i}", "score": 80} for i in range(100)]

    # Individual operations
    start = time.time()
    for data in test_data:
        cache.save_result(data["id"], "1.0", data)
    individual_duration = time.time() - start

    cache.clear_cache()

    # Batch operations
    cache.start_batch()
    start = time.time()
    for data in test_data:
        cache.save_result_batch(data["id"], "1.0", data)
    cache.commit_batch()
    batch_duration = time.time() - start

    speedup = individual_duration / batch_duration
    assert speedup >= 5, f"Expected 5x speedup, got {speedup}x"
```

### Memory Usage

```python
def test_cache_migration_memory_usage():
    """Cache migration doesn't load all data into memory."""
    import tracemalloc
    from vscode_scanner.cache_manager import CacheManager

    # Create large cache (simulate 100 entries)
    cache = CacheManager()
    for i in range(100):
        cache.save_result(f"ext{i}", "1.0", {"score": 80, "data": "x" * 1000})

    # Measure memory during migration
    tracemalloc.start()
    cache._migrate_cache_to_v2(cache._conn.cursor())
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Peak memory should be < 10MB (not loading all entries)
    assert peak < 10 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024}MB"
```

---

## Parallel Scanning Tests

### Overview

Parallel scanning introduces multi-threaded execution with 1-5 worker threads. Tests ensure thread safety, performance gains, and correct behavior under concurrent operations.

Test files:
- **test_parallel_scanning.py** - Parallel execution, performance, worker isolation
- **test_transactional_cache.py** - Thread-safe cache operations

### Thread Safety Tests

```python
def test_thread_safe_statistics_collection():
    """Statistics are correctly accumulated across worker threads."""
    from vscode_scanner.scanner import ThreadSafeStats
    import threading

    stats = ThreadSafeStats()
    num_threads = 5
    increments_per_thread = 100

    def worker():
        for _ in range(increments_per_thread):
            stats.increment('total_scanned', 1)
            stats.increment('vulnerabilities_found', 1)

    # Run concurrent increments
    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify correct totals (no race conditions)
    result = stats.to_dict()
    expected_total = num_threads * increments_per_thread
    assert result['total_scanned'] == expected_total
    assert result['vulnerabilities_found'] == expected_total
```

### Performance Tests

```python
def test_parallel_faster_than_sequential():
    """Parallel scanning is significantly faster than sequential."""
    from vscode_scanner.scanner import _scan_extensions
    import time

    # Create test extensions
    extensions = [f"test.ext{i}" for i in range(20)]

    # Sequential scan (1 worker)
    start = time.time()
    results_seq = _scan_extensions(extensions, workers=1)
    duration_seq = time.time() - start

    # Parallel scan (3 workers)
    start = time.time()
    results_par = _scan_extensions(extensions, workers=3)
    duration_par = time.time() - start

    # Verify same results
    assert len(results_seq) == len(results_par)

    # Verify speedup (should be >2x faster with 3 workers)
    speedup = duration_seq / duration_par
    assert speedup >= 2.0, f"Expected 2x+ speedup, got {speedup}x"
```

### Worker Isolation Tests

```python
def test_worker_isolation_no_shared_state():
    """Each worker has isolated API client and state."""
    from vscode_scanner.scanner import _scan_extensions

    extensions = [f"test.ext{i}" for i in range(10)]

    # Run parallel scan
    results = _scan_extensions(extensions, workers=3)

    # Verify all results are independent
    extension_ids = [r['extension_id'] for r in results]
    assert len(extension_ids) == len(set(extension_ids)), \
        "Workers should not interfere with each other"

    # Verify no race conditions in cache writes
    # (all writes happen in main thread after workers complete)
    for result in results:
        assert 'error' not in result or result['error'] is None
```

### Cache Thread Safety Tests

```python
def test_cache_writes_serialized():
    """Database writes are serialized in main thread (SQLite limitation)."""
    from vscode_scanner.cache_manager import CacheManager
    from vscode_scanner.scanner import _parallel_scan_extensions

    cache = CacheManager()
    extensions = [f"test.ext{i}" for i in range(20)]

    # Run parallel scan with caching enabled
    results = _parallel_scan_extensions(extensions, workers=3, use_cache=True)

    # Verify all results were cached correctly
    for result in results:
        cached = cache.get_cached_result(result['extension_id'], result['version'])
        assert cached is not None, "Result should be cached"
        assert cached['risk_score'] == result['risk_score']
```

---

## Integration Tests

### Full Scan Workflow

```python
def test_complete_scan_workflow():
    """End-to-end scan from discovery to output."""
    from vscode_scanner.scanner import perform_scan

    with mock_vscan_api(), temp_cache(), temp_output_dir():
        result = perform_scan(
            extensions_dir="./tests/fixtures/sample_extensions",
            output="results.json",
            use_cache=True,
        )

        # Verify scan completed
        assert result['summary']['total_extensions_scanned'] > 0

        # Verify output file created
        assert os.path.exists("results.json")

        # Verify cache populated
        cache = CacheManager()
        stats = cache.get_cache_stats()
        assert stats['total_entries'] > 0

        # Verify output format
        with open("results.json") as f:
            data = json.load(f)
            assert data['schema_version'] == "2.0"
            assert 'extensions' in data
```

### Report Generation Workflow

```python
def test_report_generation_from_cache():
    """Generate reports from cached data without API calls."""
    # Setup: Populate cache
    cache = CacheManager()
    cache.save_result("test.ext", "1.0", sample_result())

    # Act: Generate HTML report
    result = generate_report(
        output="report.html",
        cache_max_age=7,
    )

    # Assert: Report created, no API calls made
    assert result == 0  # Success
    assert os.path.exists("report.html")
    assert_no_api_calls_made()  # Verify cache-only
```

---

## CLI Testing (v3.0+)

### Overview

The CLI UX enhancement (v3.0) introduced Typer and Rich for modern terminal formatting. Tests ensure command structure, terminal compatibility, and output formatting work correctly across environments.

### Command Structure Tests

```python
def test_command_structure():
    """Verify Typer commands are correctly organized."""
    from vscode_scanner.cli import app

    # Verify main commands exist
    commands = [cmd.name for cmd in app.registered_commands]
    assert 'scan' in commands
    assert 'report' in commands
    assert 'cache' in commands
    assert 'config' in commands

def test_subcommand_organization():
    """Verify subcommands are properly nested."""
    from vscode_scanner.cli import app, cache_app, config_app

    # Cache subcommands
    cache_commands = [cmd.name for cmd in cache_app.registered_commands]
    assert 'stats' in cache_commands
    assert 'clear' in cache_commands

    # Config subcommands
    config_commands = [cmd.name for cmd in config_app.registered_commands]
    assert 'init' in config_commands
    assert 'show' in config_commands
    assert 'set' in config_commands
    assert 'get' in config_commands
```

### Terminal Compatibility Tests

```python
def test_rich_output_with_color_support():
    """Rich formatting works in terminals with color support."""
    runner = CliRunner(color=True)
    result = runner.invoke(app, ["scan"])

    # Verify Rich formatting (color codes present)
    assert '\x1b[' in result.output  # ANSI escape sequences

def test_plain_output_without_color():
    """Plain output works in terminals without color support."""
    runner = CliRunner(color=False)
    result = runner.invoke(app, ["scan", "--plain"])

    # Verify no ANSI codes (plain text only)
    assert '\x1b[' not in result.output

def test_output_redirection():
    """Output can be redirected to files and pipes."""
    import subprocess

    # Redirect stdout to file
    result = subprocess.run(
        ["vscan", "scan", "--output", "results.json"],
        capture_output=True,
        text=True
    )

    assert result.returncode in {0, 1}  # Success or vulnerabilities found
    assert os.path.exists("results.json")
```

### Terminal Compatibility Matrix

Test the CLI across different terminal environments:

| Terminal | Color Support | Rich Formatting | Plain Fallback | Status |
|----------|---------------|-----------------|----------------|--------|
| iTerm2 (macOS) | Yes | ✅ Full support | ✅ Works | Tested |
| Terminal.app | Yes | ✅ Full support | ✅ Works | Tested |
| GNOME Terminal | Yes | ✅ Full support | ✅ Works | Tested |
| Windows Terminal | Yes | ✅ Full support | ✅ Works | Tested |
| CMD.exe | Limited | ⚠️ Partial | ✅ Works | Tested |
| CI/CD (GitHub Actions) | No | ❌ Disabled | ✅ Works | Tested |
| SSH sessions | Varies | ✅ Auto-detect | ✅ Works | Tested |

### Help Text Tests

```python
def test_help_text_completeness():
    """All commands have comprehensive help text."""
    runner = CliRunner()

    # Main help
    result = runner.invoke(app, ["--help"])
    assert "VS Code Extension Security Scanner" in result.output
    assert "scan" in result.output
    assert "report" in result.output

    # Command-specific help
    result = runner.invoke(app, ["scan", "--help"])
    assert "--output" in result.output
    assert "--workers" in result.output
    assert "Examples:" in result.output
```

### Manual Testing Checklist

**CLI UX Testing:**
- [ ] All commands accessible and responsive
- [ ] Help text clear and comprehensive
- [ ] Progress bars display correctly
- [ ] Tables render properly in terminal
- [ ] Color-coding works (risk levels, status)
- [ ] Error messages formatted correctly
- [ ] Confirmation prompts work
- [ ] Auto-completion (if enabled) works

**Terminal Compatibility:**
- [ ] Test in iTerm2/Terminal.app (macOS)
- [ ] Test in GNOME Terminal (Linux)
- [ ] Test in Windows Terminal
- [ ] Test in CMD.exe
- [ ] Test with `--plain` flag
- [ ] Test output redirection (`> file.txt`)
- [ ] Test in CI/CD environment (GitHub Actions)

**Edge Cases:**
- [ ] Very narrow terminal width (<80 cols)
- [ ] Very wide terminal width (>200 cols)
- [ ] No color support (TERM=dumb)
- [ ] SSH session over slow connection

---

## HTML Report Testing (v2.2+)

### Overview

HTML reports (v2.2) generate self-contained interactive reports with embedded CSS/JavaScript. Tests ensure HTML structure, interactivity, and browser compatibility.

### HTML Structure Validation

```python
def test_html_report_structure():
    """Generated HTML has required structure."""
    from vscode_scanner.html_report_generator import HTMLReportGenerator

    generator = HTMLReportGenerator()
    html = generator.generate_report(sample_scan_data())

    # Verify basic HTML structure
    assert '<!DOCTYPE html>' in html
    assert '<html' in html and '</html>' in html
    assert '<head>' in html and '</head>' in html
    assert '<body>' in html and '</body>' in html

    # Verify sections
    assert '<header class="report-header">' in html
    assert '<section class="controls">' in html
    assert '<section class="overview-table">' in html
    assert '<footer class="report-footer">' in html

def test_html_has_embedded_styles():
    """CSS is embedded, not external."""
    html = generate_html_report(sample_scan_data())

    # Verify embedded CSS
    assert '<style>' in html and '</style>' in html
    assert 'href=' not in html  # No external stylesheets
    assert '.risk-high' in html  # CSS classes present

def test_html_has_embedded_scripts():
    """JavaScript is embedded, not external."""
    html = generate_html_report(sample_scan_data())

    # Verify embedded JavaScript
    assert '<script>' in html and '</script>' in html
    assert 'src=' not in html or 'data:' in html  # No external scripts (except data URIs for SVG)
    assert 'sortTable' in html  # JS functions present
    assert 'filterByRisk' in html
```

### Chart Generation Tests

```python
def test_pie_chart_svg_generation():
    """Pie chart SVG is generated correctly."""
    from vscode_scanner.html_report_generator import HTMLReportGenerator

    generator = HTMLReportGenerator()
    svg = generator._generate_pie_chart_svg(high=10, medium=20, low=30)

    # Verify SVG structure
    assert '<svg' in svg
    assert '<path' in svg  # Pie chart segments
    assert 'viewBox=' in svg
    assert '</svg>' in svg

def test_security_gauge_generation():
    """Security score gauges render correctly."""
    generator = HTMLReportGenerator()

    # Test various scores
    gauge_high = generator._generate_security_gauge(85)
    gauge_med = generator._generate_security_gauge(65)
    gauge_low = generator._generate_security_gauge(35)

    # Verify color coding
    assert 'green' in gauge_high or '#28a745' in gauge_high
    assert 'orange' in gauge_med or '#ffc107' in gauge_med
    assert 'red' in gauge_low or '#dc3545' in gauge_low
```

### Interactive Features Tests

```python
def test_table_sorting_javascript():
    """Table sorting JavaScript is present."""
    html = generate_html_report(sample_scan_data())

    # Verify sorting function exists
    assert 'function sortTable' in html
    assert 'onclick="sortTable(' in html

def test_filtering_javascript():
    """Filtering JavaScript is present."""
    html = generate_html_report(sample_scan_data())

    # Verify filter functions
    assert 'function filterByRisk' in html
    assert 'function searchExtensions' in html
    assert 'function toggleColumn' in html

def test_expandable_rows_javascript():
    """Row expansion JavaScript is present."""
    html = generate_html_report(sample_scan_data())

    # Verify expand/collapse functions
    assert 'function toggleDetails' in html
    assert 'onclick="toggleDetails(' in html
```

### Browser Compatibility Tests

**Manual Testing Checklist:**

| Browser | Version | HTML Rendering | JavaScript | CSS | Status |
|---------|---------|----------------|------------|-----|--------|
| Chrome | Latest | ✅ | ✅ | ✅ | Tested |
| Firefox | Latest | ✅ | ✅ | ✅ | Tested |
| Safari | Latest | ✅ | ✅ | ✅ | Tested |
| Edge | Latest | ✅ | ✅ | ✅ | Tested |
| Chrome | -2 versions | ✅ | ✅ | ✅ | Tested |
| Firefox | -2 versions | ✅ | ✅ | ✅ | Tested |

**Feature Testing:**
- [ ] Report loads in all browsers
- [ ] Tables render correctly
- [ ] Charts display properly
- [ ] Sorting works
- [ ] Filtering works
- [ ] Search works
- [ ] Row expansion works
- [ ] Column toggles work
- [ ] Print preview looks good
- [ ] Responsive design works

**Performance Testing:**
- [ ] 10 extensions: < 1s load time
- [ ] 50 extensions: < 2s load time
- [ ] 100 extensions: < 5s load time
- [ ] 500 extensions: < 10s load time

### Print Testing

```python
def test_print_media_queries():
    """Print CSS media queries are present."""
    html = generate_html_report(sample_scan_data())

    # Verify print styles
    assert '@media print' in html
    assert 'page-break-inside: avoid' in html
    assert '.controls { display: none' in html  # Hide controls when printing
```

**Manual Print Testing:**
- [ ] Print preview shows all extensions
- [ ] Details are expanded automatically
- [ ] Interactive controls hidden
- [ ] Page breaks appropriate
- [ ] Black & white mode works
- [ ] Headers/footers appropriate

### HTML Validation

**Automated Validation:**
```bash
# Use HTML5 validator (if available)
html5validator report.html

# Or use online validator
curl -F "uploaded_file=@report.html" \
  https://validator.w3.org/nu/?out=json
```

**Validation Checklist:**
- [ ] Valid HTML5 syntax
- [ ] No unclosed tags
- [ ] No duplicate IDs
- [ ] Proper nesting
- [ ] Valid CSS syntax
- [ ] Valid JavaScript syntax
- [ ] Accessibility attributes (ARIA labels)
- [ ] Semantic HTML elements

### Offline Testing

```python
def test_report_works_offline():
    """HTML report works without internet connection."""
    # Generate report
    generate_html_report(sample_scan_data(), "report.html")

    # Disconnect network
    # (manual test - open report.html with network disabled)

    # Verify:
    # - Report loads
    # - All features work
    # - No network errors in console
```

---

## Retry Mechanism Tests

### Overview

The retry mechanism (v2.2+) implements exponential backoff with jitter to handle transient API failures gracefully. Tests ensure correct retry behavior, proper backoff timing, and workflow-level retry separation.

Test files:
- **test_retry.py** - Basic retry mechanism tests
- **test_retry_analysis.py** - Retry timing and backoff analysis
- **test_workflow_retry.py** - Workflow-specific retry behavior

### Exponential Backoff Tests

```python
def test_exponential_backoff_timing():
    """Verify exponential backoff with jitter works correctly."""
    from vscode_scanner.vscan_api import _calculate_backoff_delay

    # Test exponential growth
    delay_0 = _calculate_backoff_delay(0, base_delay=2.0)  # ~2s
    delay_1 = _calculate_backoff_delay(1, base_delay=2.0)  # ~4s
    delay_2 = _calculate_backoff_delay(2, base_delay=2.0)  # ~8s

    # Verify exponential pattern (allowing for jitter ±20%)
    assert 1.6 <= delay_0 <= 2.4
    assert 3.2 <= delay_1 <= 4.8
    assert 6.4 <= delay_2 <= 9.6

    # Verify maximum ceiling (30s prevents DoS)
    delay_10 = _calculate_backoff_delay(10, base_delay=2.0)
    assert delay_10 <= 30.0
```

### Retryable Error Detection Tests

```python
def test_non_retryable_errors_fail_immediately():
    """Permanent errors don't trigger retries."""
    from vscode_scanner.vscan_api import _is_retryable_error

    # Client errors - don't retry
    assert not _is_retryable_error(400, "Bad Request")
    assert not _is_retryable_error(401, "Unauthorized")
    assert not _is_retryable_error(403, "Forbidden")
    assert not _is_retryable_error(404, "Not Found")
    assert not _is_retryable_error(500, "Internal Server Error")

    # Transient errors - safe to retry
    assert _is_retryable_error(408, "Request Timeout")
    assert _is_retryable_error(429, "Too Many Requests")
    assert _is_retryable_error(502, "Bad Gateway")
    assert _is_retryable_error(503, "Service Unavailable")
    assert _is_retryable_error(504, "Gateway Timeout")
```

### Workflow Retry Separation Tests

```python
def test_workflow_specific_retry_limits():
    """Different workflows have appropriate retry limits."""
    from vscode_scanner.vscan_api import VScanAPI

    api = VScanAPI()

    # Critical operations: 3 retries
    assert api.max_retries_scan == 3
    assert api.retry_base_delay_scan == 2.0

    # Non-critical operations: fewer retries
    assert api.max_retries_cache <= 1
    assert api.retry_base_delay_cache <= 1.0
```

### Retry-After Header Handling Tests

```python
def test_respects_retry_after_header():
    """API Retry-After header is honored (with ceiling)."""
    from vscode_scanner.vscan_api import VScanAPI
    from unittest import mock

    api = VScanAPI()

    # Mock response with Retry-After: 5
    mock_response = mock.Mock()
    mock_response.getheader.return_value = "5"

    delay = api._get_retry_delay(mock_response, retry_count=0)

    # Should use Retry-After value (5s)
    assert 4.5 <= delay <= 5.5  # Allow small jitter

def test_retry_after_ceiling_prevents_dos():
    """Malicious Retry-After headers are capped at MAX_BACKOFF_DELAY."""
    from vscode_scanner.vscan_api import VScanAPI, MAX_BACKOFF_DELAY
    from unittest import mock

    api = VScanAPI()

    # Mock malicious Retry-After: 9999
    mock_response = mock.Mock()
    mock_response.getheader.return_value = "9999"

    delay = api._get_retry_delay(mock_response, retry_count=0)

    # Should be capped at 30s maximum
    assert delay <= MAX_BACKOFF_DELAY
```

---

## Mocking Guidelines

### When to Mock

**DO Mock:**
- External API calls (vscan.dev)
- Filesystem operations in unit tests
- Time (for testing time-dependent logic)
- Network requests

**DON'T Mock:**
- Internal module interactions (test real integration)
- Simple data transformations
- Logic being tested

### Mocking Examples

**Mock API Calls:**
```python
from unittest import mock

@mock.patch('vscode_scanner.vscan_api.scan_extension')
def test_scanner_handles_api_error(mock_scan):
    """Scanner handles API errors gracefully."""
    mock_scan.side_effect = ConnectionError("Network unavailable")

    result = perform_scan(extensions_dir="./test_extensions")

    assert result['failed_scans'] > 0
    assert result['error_message'] is not None
```

**Mock Time:**
```python
@mock.patch('time.time')
def test_cache_expiration(mock_time):
    """Cached results expire after max_age."""
    # Cache entry created at t=0
    mock_time.return_value = 0
    cache.save_result("test.ext", "1.0", {"score": 80})

    # Check at t=8 days (should be expired with 7-day max age)
    mock_time.return_value = 8 * 24 * 60 * 60
    result = cache.get_cached_result("test.ext", "1.0", max_age_days=7)

    assert result is None  # Expired
```

### Mock Validation

**Problem:** Mocks can drift from real API behavior, causing tests to pass while real integration fails.

**Solution:** Validate mocks against real API structure using `test_mock_validation.py`.

**Canonical Mock Usage:**
```python
from tests.fixtures.canonical_mock import CanonicalVscanAPIMock

def test_scanner_with_valid_response():
    """Test scanner with realistic API response."""
    # Use canonical mock that matches real API structure
    mock_response = CanonicalVscanAPIMock.get_success_response(
        publisher="test-publisher",
        name="test-extension",
        security_score=85,
        vuln_count=0
    )

    # Mock will have all required fields that real API returns
    assert 'scan_status' in mock_response
    assert 'metadata' in mock_response
    assert 'security' in mock_response
    # ... all 16 required fields present
```

**Available Mock Methods:**
- `get_success_response()` - Clean extension (no vulnerabilities)
- `get_error_response()` - Failed scan
- `get_vulnerable_response()` - Extension with vulnerabilities

**Validation:**
```bash
# Run mock validation tests (includes 1 real API call)
python3 tests/test_mock_validation.py

# Output shows real API structure vs mock structure
# Tests fail if mocks drift from real API
```

**Required Fields (validated 2025-10-26):**
```python
REQUIRED_SUCCESS_FIELDS = {
    'name', 'publisher', 'scan_status', 'error',
    'metadata', 'security', 'dependencies', 'risk_factors',
    'security_score', 'risk_level', 'vulnerabilities',
    'vscan_url', 'analysis_timestamp', 'has_errors',
    'raw_response', 'analysis_id'
}
```

**Critical Fields (scanner depends on these):**
```python
CRITICAL_FIELDS = {
    'scan_status',      # 'success' or 'error'
    'security_score',   # int 0-100 or None
    'vulnerabilities'   # dict with 'count', 'critical', etc.
}
```

**When Creating New Mocks:**
1. Always use `CanonicalVscanAPIMock` as base
2. Run `test_mock_validation.py` to verify
3. Update canonical mock if real API changes
4. Re-run validation after updates

**Validation Frequency:**
- Run before each release
- Run when vscan.dev API updates
- Run if mock-based tests fail in production

---

## Test Coverage

### Coverage Goals

- **Overall Coverage:** 85%+ across all modules
- **Security Modules:** 95%+ coverage (utils.py, cache_manager.py)
- **Integration Tests:** Cover major workflows
- **Security Tests:** 100% of security functions (validate_path, sanitize_string, HMAC validation)

### Measure Coverage

```bash
# Run with coverage
pytest tests/ --cov=vscode_scanner --cov-report=html

# View HTML report
open htmlcov/index.html

# Show missing lines
pytest tests/ --cov=vscode_scanner --cov-report=term-missing
```

### Coverage Reports

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
vscode_scanner/cache_manager    450     45    90%   123-145, 234-267
vscode_scanner/scanner          380     20    95%   45-52, 123-134
vscode_scanner/vscan_api        320     30    91%   89-102, 234-245
vscode_scanner/cli              450    100    78%   (many branches)
-----------------------------------------------------------
TOTAL                          2100    250    88%
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest tests/ --cov=vscode_scanner --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run tests before commit
pytest tests/ -x

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## Best Practices

### DO ✅

- Write tests first (TDD) for new features
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests independent
- Clean up after tests (fixtures, temp files)
- Mock external dependencies
- Test one thing per test
- Use AAA pattern (Arrange, Act, Assert)

### DON'T ❌

- Test implementation details
- Write slow unit tests
- Share state between tests
- Skip cleanup (fixtures handle it)
- Mock everything (test real interactions)
- Write brittle tests (tight coupling)
- Ignore failing tests
- Commit untested code

---

## Troubleshooting Tests

### Test Fails Locally

```bash
# Run with verbose output
pytest tests/test_failing.py -v

# Show full error traceback
pytest tests/test_failing.py --tb=long

# Drop into debugger on failure
pytest tests/test_failing.py --pdb
```

### Test Passes Locally, Fails in CI

- Check for timing dependencies
- Verify fixture cleanup
- Check for hardcoded paths
- Ensure deterministic behavior

### Flaky Tests

- Add retry logic for network tests
- Use mocking for time-dependent tests
- Increase timeouts for slow operations
- Check for race conditions

---

## References

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling patterns
- **[project/ROADMAP.md](../project/ROADMAP.md)** - Code quality guidelines
- **[contributing/TESTING_CHECKLIST.md](../contributing/TESTING_CHECKLIST.md)** - Manual testing checklist

---

**Document Version:** 1.0
**Status:** Current
**Maintained By:** Development Team
