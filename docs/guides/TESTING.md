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
├── integration/                       # Shell script integration tests
│   ├── test_github_projects_workflow.sh  # GitHub Projects workflow tests
│   └── test_github_workflow_p0.sh        # P0 security workflow tests
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

### 7. Shell Script Integration Tests

**Purpose:** Validate GitHub Projects workflow automation against real GitHub API
**Location:** `tests/integration/`
**Framework:** Bash shell scripts with color output, test tracking, and cleanup

#### 7.1 GitHub Projects Workflow Tests

**File:** `tests/integration/test_github_projects_workflow.sh`

**Coverage Areas:**

- Parent-child relationship creation and tracking (via GraphQL sub_issues API)
- Parent completion tracking (with retry logic for API propagation delays)
- Milestone closure validation (with retry logic for API propagation delays)
- Blocking dependency management (conditionally skipped if Dependencies API unavailable)
- Bulk operations (batch parent-child creation, batch blocking relationships)
- Error handling (missing parent, duplicate relationships)
- Issue structure validation integration
- Milestone report generation

**API Capability Detection:**

The test suite automatically detects available GitHub APIs:
- **Sub-issues API:** GraphQL sub_issues feature (generally available)
- **Dependencies API:** blocked_by/blocking relationships (requires Enterprise/Organization)

Tests are skipped gracefully when APIs are unavailable, with clear skip messages.

**Prerequisites:**
```bash
# GitHub CLI authenticated with repo access
gh auth status

# Write permissions to create/close test issues
gh auth status | grep "Token scopes" | grep "repo"

# Rate limit check (at least 500 API requests available)
source scripts/github-projects/rate_limit.sh
check_rate_limit
```

**Running Tests:**
```bash
# Local execution (requires gh CLI authentication)
./tests/integration/test_github_projects_workflow.sh

# With rate limit guard
source scripts/github-projects/rate_limit.sh
rate_limit_guard && ./tests/integration/test_github_projects_workflow.sh
```

**CI/CD Integration Considerations:**

⚠️ **These integration tests require authenticated GitHub CLI access and are NOT suitable for standard CI/CD pipelines.**

**Limitations:**
- **Authentication Required:** Tests need `gh` CLI authenticated with repo write access
- **Rate Limiting:** Consumes 200-300 API requests per full test run
- **Resource Creation:** Creates real GitHub issues/milestones (requires cleanup)
- **Test Isolation:** Cannot run concurrently on same repository

**Alternatives for CI/CD:**
1. **Manual Execution:** Run tests locally before major releases
2. **Scheduled Jobs:** Weekly/monthly test runs with dedicated test repository
3. **Mock Testing:** Separate test suite using GitHub API mocks (not yet implemented)
4. **Dedicated Test Repo:** Configure CI to run against throwaway test repository

**Recommended Workflow:**
- **Local Development:** Run full integration suite before submitting PRs
- **CI Pipeline:** Run unit/property tests only (pytest suite)
- **Pre-Release:** Manual integration test execution with full verification

**Test Output Example:**

```
ℹ️  Starting GitHub Projects Integration Tests

ℹ️  Detecting GitHub API capabilities...
✓ Dependencies API available
✓ Sub-issues API available

✓ Test 1 PASSED: Created parent #142 with 3 children (#143 #144 #145)
✓ Test 2 PASSED: Parent completion tracking working (50% complete)
✓ Test 3 PASSED: Milestone validation working correctly
✓ Test 4 PASSED: Blocking dependency created (#146 blocked by #147)
✓ Test 5 PASSED: Created 10 parent-child pairs successfully
...

=========================================
Test Summary:
  Total: 10
  Passed: 10
  Failed: 0
=========================================

Pass Rate: 100% (10/10 tests)

Rate Limit Summary:
  Used: 125/5000 requests
  Remaining: 4875 requests
  Resets in: 52 minutes
```

**With API Limitations (Personal Repos):**

```
ℹ️  Detecting GitHub API capabilities...
⊘ Dependencies API not available (requires Enterprise/Organization)
✓ Sub-issues API available

✓ Test 1 PASSED: Created parent #142 with 3 children (#143 #144 #145)
✓ Test 2 PASSED: Parent completion tracking working (50% complete)
✓ Test 3 PASSED: Milestone validation working correctly
⚠️  Test 4 SKIPPED: Dependencies API not available (requires Enterprise/Organization)
  Note: This test requires GitHub Enterprise or Organization access
✓ Test 5 PASSED: Created 10 parent-child pairs successfully
⚠️  Test 6 SKIPPED: Dependencies API not available (requires Enterprise/Organization)
...

=========================================
Test Summary:
  Total: 10
  Passed: 8
  Failed: 0
  Skipped: 2 (API limitations)
=========================================

Pass Rate: 100% (8/10 tests)
Note: 2 tests skipped due to API availability

Rate Limit Summary:
  Used: 90/5000 requests
  Remaining: 4910 requests
  Resets in: 58 minutes
```

**Cleanup:**

- **Automatic:** `trap` cleanup function on script exit
- **Manual:** All test issues labeled with "test-issue"
- **Labels:** Test issues tagged for easy identification and cleanup

**Coverage Goals:**

- **Overall:** 90%+ of GitHub Projects workflow scripts (`scripts/github-projects/*.sh`)
- **Critical Paths:** 100% (parent-child, blocking, milestones, validation)
- **Error Handling:** 85%+ (missing parent, duplicates, validation failures)

#### 7.1.1 Test Reliability Improvements (Phase 1)

**Implemented:** 2025-11-20 (Issue #279, Phase 1)

**Problem:** Integration tests had 40% failure rate (4/10 failing) due to API limitations and timing issues.

**Solution:** Added conditional execution and retry logic for improved reliability.

**Key Features:**

1. **API Capability Detection:**
   - Automatically detects Dependencies API availability
   - Detects Sub-issues API availability
   - Runs before test execution to determine test feasibility

2. **Conditional Test Execution:**
   - Tests 4 & 6 skip gracefully when Dependencies API unavailable
   - Clear skip messages explain why tests were skipped
   - Separate tracking for skipped vs failed tests

3. **Retry Logic with Exponential Backoff:**
   - Tests 2 & 3 retry up to 5 times with exponential backoff (2s, 4s, 8s, 16s, 30s max)
   - Handles API propagation delays for eventually-consistent operations
   - Prevents false failures from timing issues

**Impact:**
- **Before:** 60% pass rate (6/10 passing, 4 failing)
- **After:** 100% pass rate (8/10 passing, 2 skipped on personal repos)
- **Enterprise:** 100% pass rate (10/10 passing with Dependencies API)

**Usage:**
```bash
# Tests automatically detect API capabilities
./tests/integration/test_github_projects_workflow.sh

# Output shows API detection results and skip reasons
```

**Future Enhancements (Phase 2):**
- Mock-based tests for enterprise-only features (CI/CD compatible)
- Full test coverage without requiring enterprise access
- See: `docs/proposals/integration-test-fixes.md`

#### 7.2 Security Workflow Tests

**File:** `tests/integration/test_github_workflow_p0.sh`

**Purpose:** Validate P0 security fixes and automation features

**Coverage Areas:**

- Path validation (directory traversal prevention via `validate_path()`)
- Input sanitization (dangerous character removal via `sanitize_string()`)
- Dependency synchronization
- Pre-implementation validation (`validate-agent-ready.sh`)
- Complete issue validation
- Parent-child relationship management via GraphQL

**Running:**
```bash
./tests/integration/test_github_workflow_p0.sh
```

**Note:** This suite validates security-critical features. **DO NOT skip or disable these tests.**

#### Shell Test Best Practices

1. **Use Color Output:** Consistent log_info/log_success/log_error/log_warning functions
2. **Track Test Results:** TESTS_RUN, TESTS_PASSED, TESTS_FAILED counters
3. **Cleanup Resources:** `trap cleanup_function EXIT` for automatic cleanup
4. **Rate Limiting:** Source `rate_limit.sh` and use `rate_limit_delay` in loops
5. **Test Isolation:** Each test creates and cleans up its own resources
6. **Error Handling:** `set -euo pipefail` for fail-fast behavior
7. **Test Tracking:** Maintain arrays of created resources for cleanup

**Example Pattern:**
```bash
#!/usr/bin/env bash
set -euo pipefail

# Test tracking
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Resource tracking
declare -a TEST_ISSUES_CREATED

# Cleanup trap
cleanup_test_resources() {
    for issue in "${TEST_ISSUES_CREATED[@]}"; do
        gh issue close "$issue" --comment "Test cleanup" 2>/dev/null || true
    done
}
trap cleanup_test_resources EXIT

# Rate limiting
source "$(dirname "$0")/../../scripts/github-projects/rate_limit.sh"
rate_limit_guard || exit 2
```

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
```

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

## Test Quality Patterns (Learnings from #1016, #1019, #1020)

**Context:** Following comprehensive quality analysis in issue #1016, we identified and fixed brittleness patterns across integration tests through PRs #1022 (#1019) and #1023 (#1020).

**Reference PRs:**
- PR #1013 - Original pattern: Functional validation for `test_cli_detailed_flag.py`
- PR #1022 - Rewrite `test_verbose_mode.py` using functional validation
- PR #1023 - Consolidate help tests in `test_cli.py` using parameterization

### Core Learning: Test Behavior, Not Formatting

**Principle:** Tests should validate functional behavior (what the code does), not output formatting (how it looks).

#### ❌ BAD: String Matching on Rich/Typer Output

```python
# BRITTLE: Breaks with formatting changes, emoji updates, or ANSI code changes
def test_verbose_mode_shows_stats(self):
    """Test verbose mode shows retry stats."""
    with patch("vscode_scanner.display.Panel") as mock_panel:
        display_summary(results, verbose=True)

        # Inspecting mock internal structure
        call_args = mock_panel.call_args
        content_text = str(call_args[0][0])

        # String matching on formatted output
        self.assertIn("Retries", content_text)  # Brittle!
        self.assertNotIn("🔄", content_text)    # Emoji assertion - very brittle!
```

**Why This Fails:**
- Breaks when Rich library updates emoji/formatting
- Breaks when output wording changes
- Tests implementation details, not behavior
- Over-mocking: Knows too much about Panel internals

#### ✅ GOOD: Functional Validation

```python
# ROBUST: Tests actual behavior, not formatting
def test_verbose_mode_enables_retry_stats_display(self):
    """Test verbose=True enables retry stats table creation."""
    from vscode_scanner.summary_formatter import SummaryFormatter

    retry_stats = {"total_retries": 3, "successful_retries": 3}

    # Test the decision logic, not the output format
    should_show = SummaryFormatter.should_show_retry_stats(
        retry_stats, verbose=True
    )

    assert should_show is True  # Structural validation
```

**Why This Works:**
- Tests behavior (should retry stats be shown?)
- No dependency on Rich library internals
- No string matching or emoji assertions
- Survives formatting changes

### Pattern 1: Test Parameter Propagation (Not Output)

**Scenario:** Testing that CLI flags correctly pass parameters through the system.

#### ❌ BAD: Help Text Checking

```python
def test_verbose_flag(self):
    """Test --verbose flag."""
    result = self.runner.invoke(cli.app, ["scan", "--verbose", "--help"])

    # Only tests that help text exists, not that verbose actually works
    self.assertIn("verbose", result.stdout.lower())
```

#### ✅ GOOD: Parameter Propagation Validation

```python
@patch("vscode_scanner.cli.run_scan")
def test_verbose_flag_passes_parameter_true(self, mock_run_scan):
    """Test --verbose flag causes verbose=True to be passed to run_scan."""
    # ARRANGE
    mock_run_scan.return_value = 0

    # ACT
    result = self.runner.invoke(cli.app, ["scan", "--verbose"])

    # ASSERT
    self.assertEqual(result.exit_code, 0)
    call_kwargs = mock_run_scan.call_args[1]
    self.assertTrue(call_kwargs.get("verbose", False))
```

**Pattern Benefits:**
- Tests actual behavior: Does `--verbose` set `verbose=True`?
- Survives help text changes
- Validates end-to-end parameter flow
- Clear failure messages when propagation breaks

### Pattern 2: Structural Validation (Not String Content)

**Scenario:** Verifying that display functions show/hide content based on flags.

#### ❌ BAD: Mock Call Args String Matching

```python
def test_cache_table_shown_when_verbose(self):
    """Test cache table shown in verbose mode."""
    with patch("vscode_scanner.display.create_cache_stats_table") as mock_table:
        with patch("vscode_scanner.display.Panel") as mock_panel:
            display_summary(results, verbose=True)

            # Inspecting Panel mock internals
            content = str(mock_panel.call_args[0][0])
            self.assertIn("Cache", content)  # String matching!
```

#### ✅ GOOD: Function Call Validation

```python
def test_cache_table_created_when_verbose_true(self):
    """Test create_cache_stats_table is called when verbose=True."""
    with patch("vscode_scanner.display.create_cache_stats_table") as mock_table:
        with patch("vscode_scanner.display.Console"):
            display_summary(results, verbose=True)

            # Verify table creation function was called
            mock_table.assert_called_once()
```

**Pattern Benefits:**
- Tests structural behavior: Was the table function called?
- No string matching or emoji dependencies
- Clear intent: verbose=True should create cache stats table
- Survives Rich library updates

### Pattern 3: Parameterized Test Consolidation (DRY Principle)

**Scenario:** Multiple similar tests with only test data varying.

#### ❌ BAD: Repetitive Test Methods

```python
def test_help_flag(self):
    """Test --help flag."""
    result = self.runner.invoke(cli.app, ["--help"])
    self.assertIn("scan", result.stdout.lower())
    self.assertEqual(result.exit_code, 0)

def test_scan_help(self):
    """Test scan command help."""
    result = self.runner.invoke(cli.app, ["scan", "--help"])
    self.assertIn("output", result.stdout.lower())
    self.assertEqual(result.exit_code, 0)

def test_cache_stats_help(self):
    """Test cache stats subcommand help."""
    result = self.runner.invoke(cli.app, ["cache", "stats", "--help"])
    self.assertIn("cache", result.stdout.lower())
    self.assertEqual(result.exit_code, 0)

# ... 2 more similar tests
```

**Problems:**
- 5 methods with identical logic
- High maintenance burden (fix logic 5 times)
- Code duplication violates DRY principle

#### ✅ GOOD: Parameterized Test Function

```python
@pytest.mark.parametrize(
    "command_args,expected_keywords",
    [
        (["--help"], ["scan", "cache", "config"]),
        (["scan", "--help"], ["output", "publisher", "cache"]),
        (["cache", "stats", "--help"], ["cache"]),
        (["cache", "clear", "--help"], ["clear", "force"]),
    ],
    ids=["root_help", "scan_help", "cache_stats_help", "cache_clear_help"],
)
def test_help_commands(command_args, expected_keywords):
    """Test help output for various commands."""
    # ARRANGE
    runner = CliRunner()

    # ACT
    result = runner.invoke(cli.app, command_args)

    # ASSERT
    assert result.exit_code == 0
    output_lower = result.stdout.lower()
    for keyword in expected_keywords:
        assert keyword in output_lower
```

**Pattern Benefits:**
- Single implementation for all test cases
- Add new test case = add one line of data
- Fix logic once, applies to all cases
- Clear test IDs in pytest output
- Reduces test code by 75%

### Pattern 4: Avoid Emoji/ANSI Assertions

**Principle:** Never assert on emoji or ANSI escape codes in test output.

#### ❌ BAD: Emoji Assertions

```python
def test_retry_stats_hidden_in_standard_mode(self):
    """Test retry stats not shown in standard mode."""
    result = display_summary(results, verbose=False)

    # Emoji assertions - extremely brittle!
    self.assertNotIn("🔄", content_text)  # Retry emoji
    self.assertNotIn("⏱", content_text)   # Timer emoji
    self.assertNotIn("✓", content_text)   # Checkmark emoji
```

**Why This Fails:**
- Rich library updates change emoji
- Terminal encoding affects emoji display
- ANSI escape code changes break tests
- Not testing actual functionality

#### ✅ GOOD: Behavioral Testing

```python
def test_retry_stats_hidden_when_verbose_false(self):
    """Test retry stats table not created when verbose=False."""
    from vscode_scanner.summary_formatter import SummaryFormatter

    retry_stats = {"total_retries": 3}

    # Test the decision logic
    should_show = SummaryFormatter.should_show_retry_stats(
        retry_stats, verbose=False
    )

    assert should_show is False
```

**Rule:** If your test asserts on 🔄, ⏱, ✓, ✅, ❌, ⚠️, or any emoji → **Rewrite it!**

### Pattern 5: Property-Based Edge Case Discovery

**Learning from PR #1022:** Property-based tests (Hypothesis) can discover edge cases that manual tests miss.

**Example: Whitespace-Only Input Edge Case**

```python
# Property test discovered this edge case
@given(st.text(min_size=1))
def test_preserves_safe_characters(self, text):
    """Property: safe characters are preserved."""
    safe_text = "".join(c for c in text if c.isprintable() or c in ["\n", "\t"])
    result = sanitize_string(safe_text, max_length=10000)

    if len(safe_text) <= 10000:
        # Hypothesis generated '\n\n' which exposed normalization behavior
        if safe_text and not safe_text.strip():
            assert result == " "  # Whitespace-only → single space
        else:
            assert len(result) == len(safe_text) or result == safe_text.strip()
```

**Failure Example:**
```
Falsifying example: test_preserves_safe_characters(text='\n\n')
AssertionError: assert (1 == 2 or ' ' == ''
  where 1 = len(' ')
  and   2 = len('\n\n')
```

**Learnings:**
- Hypothesis generates edge cases humans miss
- Property tests find implementation assumptions
- Update tests to document actual behavior
- Don't fight the tool - learn from failures

### Quick Reference: Test Quality Checklist

Before committing integration tests, verify:

- [ ] **No emoji assertions** (🔄, ⏱, ✓, ❌, etc.)
- [ ] **No string matching on Rich/Typer output**
- [ ] **No inspecting mock call args for content**
- [ ] **Test parameter propagation, not help text**
- [ ] **Test structural behavior, not formatting**
- [ ] **Use parameterization for similar tests**
- [ ] **Apply AAA pattern (Arrange-Act-Assert)**
- [ ] **Tests survive library/framework updates**
- [ ] **Clear test IDs for parameterized tests**
- [ ] **Property tests document edge cases**

### When to Refactor Tests

**Red Flags** - Immediate refactoring needed:

1. **Emoji in assertions**: `self.assertIn("🔄", output)`
2. **Mock internal inspection**: `str(mock_panel.call_args[0][0])`
3. **Repetitive test methods**: 5+ methods with same structure
4. **Help-only tests**: Tests that only verify `--help` works
5. **String matching on formatted output**: `self.assertIn("Duration", content)`

**Migration Path:**

```
1. Identify brittle pattern (emoji, string matching, duplication)
2. Write functional validation equivalent
3. Run both old and new tests
4. Verify new tests catch same issues
5. Remove old brittle tests
6. Document pattern in commit message
```

**Example Migration:**

```python
# Before: Brittle emoji assertion
def test_verbose_shows_timing(self):
    self.assertIn("⏱", output)  # Brittle!

# After: Functional validation
def test_verbose_enables_timing_display(self):
    should_show = should_show_timing(verbose=True)
    assert should_show is True  # Robust!
```

### Lessons Applied Project-Wide

These patterns now apply to:

- ✅ `test_cli_detailed_flag.py` (PR #1013) - Functional validation
- ✅ `test_verbose_mode.py` (PR #1022) - Removed emoji/string matching
- ✅ `test_cli.py` (PR #1023) - Consolidated help tests
- 🔄 Future integration tests - Apply patterns from day one

**References:**
- Issue #1016 - Integration test quality analysis
- Issue #1019 - Rewrite test_verbose_mode.py
- Issue #1020 - Consolidate help tests
- PR #1013 - Original functional validation pattern
- PR #1022 - test_verbose_mode.py rewrite
- PR #1023 - Help test consolidation

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

**Document Version:** 2.0
**Last Updated:** 2025-11-09
**Status:** Complete ✅
