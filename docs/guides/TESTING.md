# Testing Guide

**Purpose:** Testing philosophy, patterns, and how to write/run tests
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** Developers, QA Engineers, Contributors

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
- Full suite runs in < 30 seconds (parallel execution enabled by default)
- **Performance:** 2.9x speedup via pytest-xdist parallel execution

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

# With automated tools
pre-commit run --all-files  # Runs bandit, security tests
bandit -r vscode_scanner/ -ll
safety check
pip-audit
```

### Run Coverage Analysis

```bash
# Using run_tests.py with pytest-cov (recommended - includes parallel execution)
python3 scripts/run_tests.py --coverage --coverage-format html
open htmlcov/index.html  # macOS (use 'xdg-open' on Linux, 'start' on Windows)

# Terminal coverage report
python3 scripts/run_tests.py --coverage --coverage-format term

# Multiple formats (comma-separated)
python3 scripts/run_tests.py --coverage --coverage-format "html,xml,term"

# Using pytest directly with pytest-cov
pytest tests/ --cov=vscode_scanner --cov-branch --cov-report=html -n auto
pytest tests/ --cov=vscode_scanner --cov-branch --cov-report=term -n auto

# Legacy: coverage.py (for compatibility)
coverage run -m pytest tests/
coverage report --show-missing
coverage html
```

### Parallel Test Execution

**Default Behavior:** Parallel execution is enabled by default via pytest-xdist.

```bash
# Automatic parallel execution (default)
python3 scripts/run_tests.py --include unit  # Uses all available CPU cores

# Direct pytest with parallel execution
pytest tests/ -n auto  # Auto-detect CPU cores
pytest tests/ -n 4     # Use 4 workers explicitly

# Performance comparison
pytest tests/test_utils.py           # Serial: ~0.10s
pytest tests/test_utils.py -n auto   # Parallel: ~0.95s (overhead for small suites)

# Full suite benefits
pytest tests/ -m unit         # Serial: ~31s (estimated)
pytest tests/ -m unit -n auto # Parallel: ~10.69s (2.9x speedup)
```

**Worker Isolation:**
- Each worker gets isolated cache directories (e.g., `~/.vscan_test_integrity_gw0`)
- Worker ID available via `request.config.workerinput["workerid"]`
- Prevents SQLite and HMAC conflicts in parallel execution

**Example Worker-Isolated Fixture:**
```python
@pytest.fixture(autouse=True)
def setup_teardown(self, request):
    """Worker-specific isolation for pytest-xdist."""
    worker_id = getattr(request.config, "workerinput", {}).get("workerid", "master")
    self.test_dir = os.path.join(
        os.path.expanduser("~"),
        f".vscan_test_cache_{worker_id}"
    )
    os.makedirs(self.test_dir, exist_ok=True)
    yield
    if os.path.exists(self.test_dir):
        shutil.rmtree(self.test_dir)
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

**Current Test Metrics:**
- **Total Tests:** Run `pytest --collect-only -q tests/` for current count
- **Overall Coverage:** See [STATUS.md](../project/STATUS.md) for current metrics
- **Security Coverage:** 95%+ maintained (utils.py, cache_manager.py)
- **Property Tests:** Hypothesis generates 1,000+ test scenarios per property test

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
**See:** [TESTING_INTEGRATION.md](testing/TESTING_INTEGRATION.md)

### 3. Architecture Tests
**Purpose:** Verify 3-layer architecture boundaries
**Speed:** Fast (< 0.5s total)
**Coverage:** Enforce layering rules, prevent architecture erosion

### 4. Security Tests
**Purpose:** Verify security controls and prevent vulnerabilities
**Coverage:** 95%+ of security modules
**See:** [TESTING_SECURITY.md](testing/TESTING_SECURITY.md) for comprehensive security testing guide

### 5. Property-Based Tests
**Purpose:** Generate 100-1000+ test scenarios automatically
**Framework:** Hypothesis
**Coverage:** 20 tests generating 1,250+ scenarios
**See:** [TESTING_PROPERTY_BASED.md](testing/TESTING_PROPERTY_BASED.md) for complete guide

### 6. Performance Tests
**Purpose:** Verify performance characteristics
**Focus:** Timing, memory, scalability
**See:** [PERFORMANCE.md](PERFORMANCE.md) § 2 (Performance Testing)

---

## Dynamic Marker System

**Single source of truth:** All pytest markers loaded from `pyproject.toml` at runtime. No hardcoded definitions, automatic validation via `test_marker_categories.py`.

### Marker Categories

| Category | Tag | Usage | Required | Examples |
|----------|-----|-------|----------|----------|
| **Test Group** | `[GROUP]` | `--include`/`--exclude` | Yes (one per test) | unit, security, architecture, parallel, integration, real_api, mock_validation |
| **Behavioral** | `[BEHAVIORAL]` | `--filter` | Optional | slow, property_based |
| **Meta** | Runtime-only | Auto-generated | N/A | unmarked, all |

### Adding New Markers

1. Update `pyproject.toml`: `"marker_name: [GROUP|BEHAVIORAL] Description"`
2. Apply to tests: `@pytest.mark.marker_name`
3. Use: `python3 scripts/run_tests.py --include marker_name`

**Auto-benefits:** Dynamic TestGroup enum, generated help text, validation included in `--include architecture`

---

## Running Tests

### Test Suite Runner (Recommended)

**Groups** (dynamic from `pyproject.toml`):
```bash
python3 scripts/run_tests.py                          # All groups (default)
python3 scripts/run_tests.py --include unit,security  # Specific groups
python3 scripts/run_tests.py --exclude real-api       # All except specified
python3 scripts/run_tests.py --list-groups            # Show all available groups
```

**Note:** Test groups are loaded dynamically from `pyproject.toml` § [tool.pytest.ini_options].markers. Use `--list-groups` to see current groups.

| Group | Time | Description |
|-------|------|-------------|
| unit, security, architecture, parallel, integration, mock-validation | <5s | Fast tests |
| real-api | ~30s | Real API calls (network-dependent) |
| unmarked | varies | Tests without markers (meta-group) |

**Filters & Presets:**
```bash
python3 scripts/run_tests.py --filter 'not slow'    # Behavioral filtering
python3 scripts/run_tests.py --fast                 # Exclude slow (preset)
python3 scripts/run_tests.py --ci                   # Exclude real-api (preset)
python3 scripts/run_tests.py --report               # HTML coverage (preset)
python3 scripts/run_tests.py --security-only        # Security only (preset)
```

**Output & Coverage:**
```bash
python3 scripts/run_tests.py --coverage --coverage-format html|xml
python3 scripts/run_tests.py --output json|junit --output-file FILE
python3 scripts/run_tests.py --quiet --help --list-groups
```

### Alternative: Direct pytest

For simple scenarios or when you need pytest-specific features:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scanner.py

# Run tests by pattern
pytest -k "cache" -v

# Skip slow tests (behavioral marker)
pytest -m "not slow"

# Run specific test group (requires marker)
pytest -m "unit" tests/
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

### Required Pytest Markers

**CRITICAL:** All tests **must** have at least one test group marker for proper test discovery by `run_tests.py`.

**Single Source of Truth:** All markers are defined in `pyproject.toml` under `[tool.pytest.ini_options].markers`. See the [Dynamic Marker System](#dynamic-marker-system) section for details on marker categories and adding new markers.

**Required Test Group Markers** (choose exactly one per test):
- `@pytest.mark.unit` - Unit tests for individual components (most common)
- `@pytest.mark.integration` - Integration tests with mocked dependencies
- `@pytest.mark.security` - Security vulnerability tests
- `@pytest.mark.architecture` - Architecture compliance tests
- `@pytest.mark.parallel` - Parallel execution and threading tests
- `@pytest.mark.real_api` - Tests that make real API calls (slow, network-dependent)
- `@pytest.mark.mock_validation` - Mock validation against real API responses

**Optional Behavioral Markers** (can combine with any group):
- `@pytest.mark.slow` - Tests taking >5 seconds (excluded by `--fast` preset)
- `@pytest.mark.property_based` - Property-based tests using Hypothesis framework

**Example Combining Markers:**
```python
import pytest

# Unit test that is slow and property-based
@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.property_based
def test_scanner_with_many_extensions(extension_list):
    """Property test with large extension lists."""
    ...
```

**Module-Level Marking (Recommended):**
```python
import pytest

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit

class TestMyFeature:
    def test_something(self):
        ...
```

**Class-Level Marking:**
```python
@pytest.mark.unit
class TestMyFeature:
    def test_something(self):
        ...
```

**Verification:**
```bash
# Verify all tests have markers
python3 -m pytest tests/ --collect-only -q | grep "tests collected"

# Check specific file has markers
python3 -m pytest tests/test_myfile.py -m unit --collect-only -q
```

#### The UNMARKED Meta-Group

**Purpose:** Safety net preventing tests from being silently excluded (v3.7.1+). Tests without markers → auto-collected into `UNMARKED` → run last with yellow warning.

**Behavior:**
- Included by default with `--all` (warns which files need markers)
- Excluded from specific groups: `--include unit` skips unmarked tests
- Strict mode: `--exclude unmarked` for CI enforcement

**Fix unmarked tests (module-level recommended):**
```python
import pytest
pytestmark = pytest.mark.unit  # or security, integration, etc.

def test_my_function():
    ...
```

**Verify:** `python3 scripts/run_tests.py --include unmarked` should show no tests after fixing.

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
- **[PERFORMANCE.md](PERFORMANCE.md)** § 2 - Performance tests (cache speedup, memory usage, scalability)

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

**Automated Security Tools:**
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

**See:** [TESTING_COVERAGE.md](testing/TESTING_COVERAGE.md) for detailed coverage strategy

---

## References

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture (3-layer model)
- **[SECURITY.md](SECURITY.md)** - Security requirements and threat model
- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling patterns
- **[../project/STATUS.md](../project/STATUS.md)** - Current test metrics and coverage goals
- **[../contributing/TESTING_CHECKLIST.md](../contributing/TESTING_CHECKLIST.md)** - Manual testing checklist

---
