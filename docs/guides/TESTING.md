# Testing Guide

**Version:** 3.1.0
**Last Updated:** 2025-10-24
**Target Audience:** Contributors, Developers, QA Engineers

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
├── test_architecture.py      # Architecture validation tests
├── test_display.py            # Display module tests (24 tests)
├── test_scanner.py            # Scanner module tests (15 tests)
├── test_cli.py                # CLI module tests (18 tests)
├── test_api.py                # API validation tests
├── test_cache.py              # Cache manager tests
├── test_config.py             # Configuration manager tests
├── test_security.py           # Security vulnerability tests
├── test_performance.py        # Performance benchmark tests
├── test_integration.py        # End-to-end integration tests (7 suites)
├── test_retry.py              # Retry mechanism tests
├── test_db_integrity.py       # Database integrity tests
├── fixtures/                  # Test data and fixtures
│   ├── sample_extensions/
│   ├── mock_responses/
│   └── test_configs/
└── conftest.py                # Pytest configuration and shared fixtures
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

### Run All Tests

```bash
# Using pytest
pytest tests/

# With coverage
pytest tests/ --cov=vscode_scanner --cov-report=html

# Verbose output
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_cache.py tests/test_api.py

# Integration tests
pytest tests/test_integration.py

# Architecture tests
pytest tests/test_architecture.py

# Security tests
pytest tests/test_security.py

# Performance tests
pytest tests/test_performance.py
```

### Run Individual Test Files

```bash
# Display module tests
python3 tests/test_display.py

# Scanner module tests
python3 tests/test_scanner.py

# CLI module tests
python3 tests/test_cli.py
```

### Run by Test Name Pattern

```bash
# All tests with "cache" in name
pytest -k cache

# All tests with "error" in name
pytest -k error

# Exclude slow tests
pytest -m "not slow"
```

### Watch Mode (Development)

```bash
# Rerun tests on file changes
pytest-watch tests/
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

### Input Validation

```python
def test_extension_id_validation_blocks_injection():
    """Extension IDs are validated before use in database queries."""
    from vscode_scanner.utils import validate_extension_id

    malicious_inputs = [
        "'; DROP TABLE scan_cache; --",
        "' OR '1'='1",
        "1' UNION SELECT * FROM users--",
    ]

    for malicious in malicious_inputs:
        assert not validate_extension_id(malicious), \
            f"Should reject malicious input: {malicious}"
```

### Path Traversal

```python
def test_path_traversal_blocked():
    """Path traversal attempts are blocked."""
    from vscode_scanner.utils import is_safe_path

    dangerous_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\Windows\\System32",
        "/etc/passwd",
        "C:\\Windows\\System32",
    ]

    for dangerous in dangerous_paths:
        assert not is_safe_path(dangerous), \
            f"Should block dangerous path: {dangerous}"
```

### Error Message Sanitization

```python
def test_error_messages_dont_leak_paths():
    """Error messages don't expose file paths."""
    from vscode_scanner.utils import sanitize_error_message

    error_with_path = "File not found: /Users/john/secret/keys.json"
    sanitized = sanitize_error_message(error_with_path)

    assert "/Users/john" not in sanitized
    assert "keys.json" not in sanitized
    assert "<path>" in sanitized
```

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

---

## Test Coverage

### Coverage Goals

- **Unit Tests:** 80%+ coverage
- **Integration Tests:** Cover major workflows
- **Security Tests:** 100% of security functions

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
