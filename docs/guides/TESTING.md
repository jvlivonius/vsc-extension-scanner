# Testing Guide

**Document Type:** Timeless Reference
**Applies To:** All 3.x versions
**Major Revision Trigger:** Test framework changes, testing philosophy shifts, or major tool updates
**Target Audience:** Contributors, Developers, QA Engineers
**See:** [CHANGELOG.md](../../CHANGELOG.md) for version-specific test additions

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Quick Start](#quick-start)
3. [Test Organization](#test-organization)
4. [Test Categories](#test-categories)
5. [Running Tests](#running-tests)
6. [Writing Tests](#writing-tests)
7. [Specialized Testing Documentation](#specialized-testing-documentation)

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

## Quick Start

### Run All Tests

```bash
# Unified test runner (recommended)
python3 scripts/run_tests.py --all

# Specific test groups
python3 scripts/run_tests.py --unit --security
python3 scripts/run_tests.py --all --fast

# Individual test files
python3 tests/test_scanner.py
python3 tests/test_security.py

# Using pytest (if installed)
pytest tests/ -v
```

### Run Security Tests (CRITICAL)

```bash
# Security test suite - MUST pass before commits
python3 tests/test_security.py
python3 tests/test_security_regression.py
python3 tests/test_sqlite_security.py

# With automated tools (Phase 1)
pre-commit run --all-files  # Runs bandit, security tests
bandit -r vscode_scanner/ -ll
safety check
pip-audit
```

### Run Coverage Analysis

```bash
# Generate coverage report (HTML format - recommended)
coverage run -m pytest tests/
coverage html
open htmlcov/index.html  # macOS (use 'xdg-open' on Linux, 'start' on Windows)

# Terminal coverage report with missing lines
coverage run -m pytest tests/
coverage report --show-missing

# Generate all report formats
coverage run -m pytest tests/ && coverage report && coverage html && coverage xml
```

---

## Test Organization

### Directory Structure

```
tests/
├── test_architecture.py               # Layer compliance (3-layer validation)
├── test_security*.py                  # Security test suite (5 files)
├── test_property_*.py                 # Property-based tests (Hypothesis)
├── test_scanner.py                    # Core scanning workflow
├── test_display.py                    # Terminal formatting
├── test_cli.py                        # CLI interface
├── test_integration.py                # End-to-end workflows
├── test_parallel_scanning.py          # Multi-threaded execution
├── test_retry*.py                     # Retry mechanism (3 files)
├── test_performance.py                # Performance benchmarks
└── fixtures/                          # Test data and fixtures
    └── canonical_mock.py              # Canonical mock implementation
```

**Current Test Metrics (v3.5.3):**
- **Total Tests:** 604 tests across 35 test files
- **Overall Coverage:** 52.37% (target: 70%)
- **Security Coverage:** 95%+ (utils.py, cache_manager.py)
- **Property Tests:** 20 tests generating 1,250+ scenarios

### Test File Naming

- `test_<module>.py` - Tests for specific module
- `test_<feature>.py` - Tests for specific feature
- Test functions: `test_<what>_<expected_behavior>()`

---

## Test Categories

### 1. Unit Tests
**Purpose:** Test individual functions/methods in isolation
**Speed:** Fast (< 0.1s each)
**Mocking:** Mock all I/O and external dependencies

### 2. Integration Tests
**Purpose:** Test multiple components working together
**Speed:** Moderate (1-5s each)
**Mocking:** Real module interactions, mock external services
**See:** [TESTING_INTEGRATION.md](TESTING_INTEGRATION.md)

### 3. Architecture Tests
**Purpose:** Verify 3-layer architecture boundaries
**Speed:** Fast (< 0.5s total)
**Coverage:** Enforce layering rules, prevent architecture erosion

### 4. Security Tests
**Purpose:** Verify security controls and prevent vulnerabilities
**Coverage:** 95%+ of security modules
**See:** [TESTING_SECURITY.md](TESTING_SECURITY.md) for comprehensive security testing guide

### 5. Property-Based Tests
**Purpose:** Generate 100-1000+ test scenarios automatically
**Framework:** Hypothesis
**Coverage:** 20 tests generating 1,250+ scenarios
**See:** [TESTING_PROPERTY_BASED.md](TESTING_PROPERTY_BASED.md) for complete guide

### 6. Performance Tests
**Purpose:** Verify performance characteristics
**Focus:** Timing, memory, scalability
**See:** [TESTING_PERFORMANCE.md](TESTING_PERFORMANCE.md)

---

## Running Tests

### Test Suite Runner (Recommended)

The unified test runner (`scripts/run_tests.py`) provides standardized execution with clear output.

**Quick Start:**
```bash
# Run all tests
python3 scripts/run_tests.py --all

# Run specific groups
python3 scripts/run_tests.py --unit --security
python3 scripts/run_tests.py --all --fast
```

**Available Test Groups:**

| Flag | Duration | Description |
|------|----------|-------------|
| `--unit` | ~2s | Core functionality (scanner, display, CLI, edge cases) |
| `--security` | ~0.5s | Security validation, sanitization, integrity |
| `--architecture` | ~0.2s | Layer compliance, zero violations |
| `--parallel` | ~0.15s | Threading, parallel scanning |
| `--integration` | ~1s | Integration tests + DB integrity |
| `--real-api` | ~30s | Real vscan.dev API calls (slow) |
| `--all` | ~40s | All test groups combined |

**Output Formats:**
```bash
# JSON output for automation
python3 scripts/run_tests.py --all --output json --output-file results.json

# JUnit XML for CI/CD
python3 scripts/run_tests.py --all --output junit --output-file results.xml

# Quiet mode (summary only)
python3 scripts/run_tests.py --all --quiet
```

### Alternative: pytest

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scanner.py

# Run tests by pattern
pytest -k "cache" -v

# Skip slow tests
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

### Test File Template

**See:** [TEST_FILE_TEMPLATE.md](TEST_FILE_TEMPLATE.md) for complete template with examples

**Key Elements:**
- Descriptive docstring with coverage details
- Organized test classes by feature
- Section headers (Happy Path, Edge Cases, Error Handling)
- AAA pattern for all tests
- setUp/tearDown for resource management
- `run_tests()` function for standalone execution

### Test Fixtures

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
        mock_scan.return_value = {"score": 85, "risk_level": "low"}
        yield mock_scan
```

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("extension_id,expected_valid", [
    ("ms-python.python", True),
    ("GitHub.copilot", True),
    ("invalid", False),
    ("'; DROP TABLE", False),
])
def test_extension_id_validation(extension_id, expected_valid):
    """Test various extension ID formats."""
    assert validate_extension_id(extension_id) == expected_valid
```

---

## Specialized Testing Documentation

The following specialized guides provide comprehensive coverage of specific testing domains:

**Navigation:** See [testing/README.md](testing/README.md) for quick access to all testing documentation

### Core Testing Guides

- **[TESTING_SECURITY.md](testing/TESTING_SECURITY.md)** - Security testing (path validation, string sanitization, cache integrity, HMAC validation, automated tools)
- **[TESTING_PROPERTY_BASED.md](testing/TESTING_PROPERTY_BASED.md)** - Property-based testing with Hypothesis (20 tests, 1,250+ scenarios)
- **[TESTING_INTEGRATION.md](testing/TESTING_INTEGRATION.md)** - Integration testing patterns (end-to-end workflows, full scan, report generation)
- **[TESTING_COVERAGE.md](testing/TESTING_COVERAGE.md)** - Coverage strategy (85% overall, 95% security, measurement tools)

### Specialized Testing Areas

- **[TESTING_MOCKING.md](testing/TESTING_MOCKING.md)** - Mocking guidelines (when to mock, mock validation, canonical mocks)
- **[TESTING_CLI.md](testing/TESTING_CLI.md)** - CLI testing (Typer framework, terminal compatibility, help text)
- **[TESTING_HTML_REPORTS.md](testing/TESTING_HTML_REPORTS.md)** - HTML report testing (structure, charts, interactivity, browser compatibility)
- **[TESTING_RETRY.md](testing/TESTING_RETRY.md)** - Retry mechanism testing (exponential backoff, error detection, Retry-After headers)
- **[TESTING_PARALLEL.md](testing/TESTING_PARALLEL.md)** - Parallel scanning tests (thread safety, performance, worker isolation)
- **[TESTING_PERFORMANCE.md](testing/TESTING_PERFORMANCE.md)** - Performance tests (cache speedup, memory usage, scalability)

### Supporting Documentation

- **[TEST_FILE_TEMPLATE.md](testing/TEST_FILE_TEMPLATE.md)** - Test file template with examples
- **[../contributing/TESTING_CHECKLIST.md](../contributing/TESTING_CHECKLIST.md)** - Pre-release testing checklist

---

## Best Practices

### DO ✅

- Write tests first (TDD) for new features
- Test edge cases and error conditions
- Use descriptive test names following `test_<feature>_<condition>_<result>`
- Keep tests independent and isolated
- Clean up after tests (use fixtures)
- Mock external dependencies only
- Test one thing per test
- Use AAA pattern consistently
- Run all tests before committing
- Maintain high coverage (85% overall, 95% security)

### DON'T ❌

- Test implementation details (test behavior instead)
- Write slow unit tests (use mocking)
- Share state between tests (use fixtures for isolation)
- Skip cleanup (fixtures handle it automatically)
- Mock everything (test real module interactions)
- Write brittle tests (avoid tight coupling)
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

Common causes:
- Timing dependencies
- Missing fixture cleanup
- Hardcoded paths
- Non-deterministic behavior

**Solution:** Check for race conditions, use mocking for time-dependent tests, ensure cleanup

### Flaky Tests

Solutions:
- Add retry logic for network tests
- Use mocking for time-dependent tests
- Increase timeouts for slow operations
- Check for race conditions in parallel tests

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
- name: Run test suite
  run: |
    python3 scripts/run_tests.py --all --skip-real-api \
      --output junit --output-file test-results.xml

- name: Publish test results
  uses: EnricoMi/publish-unit-test-result-action@v2
  with:
    files: test-results.xml
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/ -x
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

**Phase 1 Security Tools (Automated):**
```bash
# Install pre-commit hooks (includes security tools)
pip install -e .[dev]
pre-commit install

# Test pre-commit hooks
pre-commit run --all-files

# Manual security scans
bandit -r vscode_scanner/ -ll
safety check
pip-audit
```

---

## Coverage Goals

- **Overall Coverage:** 85%+ across all modules
- **Security Modules:** 95%+ (utils.py, cache_manager.py)
- **Security Functions:** 100% (validate_path, sanitize_string, HMAC)
- **Integration Tests:** Cover major workflows
- **Property Tests:** Security-critical functions

**See:** [TESTING_COVERAGE.md](TESTING_COVERAGE.md) for detailed coverage strategy

---

## References

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture (3-layer model)
- **[SECURITY.md](SECURITY.md)** - Security requirements and threat model
- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling patterns
- **[../project/v3.5.3-roadmap.md](../project/v3.5.3-roadmap.md)** - Testing Excellence roadmap (52% → 70% coverage)
- **[../contributing/TESTING_CHECKLIST.md](../contributing/TESTING_CHECKLIST.md)** - Manual testing checklist

---

**Document Version:** 2.0
**Status:** Current
**Last Updated:** 2025-10-30 (v3.5.3 Testing Excellence - Phase 4)
**Maintained By:** Development Team
