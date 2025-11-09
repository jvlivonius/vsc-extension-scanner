# Testing Coverage Strategy

**Purpose:** How to measure, analyze, and improve test coverage
**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Applies To:** All versions
**Target Audience:** Developers, QA Engineers

---

## Coverage Goals

### Overall Targets

- **Overall Coverage:** 85%+ across all modules
- **Security Modules:** 95%+ (utils.py, cache_manager.py)
- **Security Functions:** 100% (validate_path, sanitize_string, HMAC validation)
- **Integration Tests:** Cover major workflows
- **Property Tests:** Security-critical functions

### Module-Specific Goals

| Module | Priority | Target | Rationale |
|--------|----------|--------|-----------|
| utils.py | Critical | 95% | Path validation, string sanitization (security) |
| cache_manager.py | Critical | 95% | HMAC validation, cache integrity (security) |
| scanner.py | High | 85% | Core scanning workflow |
| vscan_api.py | High | 85% | API client, network operations |
| extension_discovery.py | High | 85% | Extension detection logic |
| config_manager.py | Medium | 70% | Configuration management |
| output_formatter.py | Medium | 70% | JSON/CSV export |
| display.py | Medium | 70% | Terminal formatting |
| types.py | Medium | 70% | Data structures |
| constants.py | Low | 70% | Configuration constants |
| cli.py | UI | 50% | CLI interface (complex UI) |
| html_report_generator.py | UI | 50% | HTML report generation (complex UI) |

**Current Metrics:** See [STATUS.md](../../project/STATUS.md) for current coverage by module

---

## Measuring Coverage

### Generate Coverage Reports

```bash
# HTML report (recommended)
pytest tests/ --cov=vscode_scanner --cov-report=html

# View HTML report
open htmlcov/index.html

# Terminal report with missing lines
pytest tests/ --cov=vscode_scanner --cov-report=term-missing

# XML report (for CI/CD)
pytest tests/ --cov=vscode_scanner --cov-report=xml

# Combined reports
pytest tests/ --cov=vscode_scanner --cov-report=html --cov-report=term-missing
```

### Coverage Reports

Example output:

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

## Coverage Strategy by Module Type

### Security-Critical Modules (95%+ Required)

**Modules:**
- `utils.py` - Path validation, string sanitization
- `cache_manager.py` - HMAC validation, cache integrity

**Strategy:**
- Test all code paths (happy path + error paths)
- Test all edge cases comprehensively
- Use property-based testing for fuzzing
- 100% coverage of security functions
- Regression tests for all fixed vulnerabilities

**Priority:** Error paths, edge cases, threading, HMAC validation

### Core Business Logic (85%+ Required)

**Modules:**
- `scanner.py` - Core scanning workflow
- `vscan_api.py` - API client
- `extension_discovery.py` - Extension detection

**Strategy:**
- Test main workflows thoroughly
- Test error handling paths
- Mock external dependencies
- Integration tests for workflows

### Supporting Modules (70%+ Required)

**Modules:**
- `config_manager.py` - Configuration
- `output_formatter.py` - JSON/CSV export
- `display.py` - Terminal formatting

**Strategy:**
- Test core functionality
- Test major edge cases
- Error handling for invalid inputs

### Complex UI Modules (50%+ Acceptable)

**Modules:**
- `cli.py` - CLI interface (Typer framework)
- `html_report_generator.py` - HTML report generation

**Rationale:** These modules have complex UI logic that's difficult to test comprehensively with unit tests. Manual testing and integration tests provide sufficient coverage.

---

## Improving Coverage

### Step 1: Identify Gaps

```bash
# Generate HTML coverage report
pytest tests/ --cov=vscode_scanner --cov-report=html

# Open report and identify missing lines
open htmlcov/index.html

# Click on modules with low coverage
# Red lines = not covered
# Green lines = covered
```

### Step 2: Analyze Missing Coverage

**Common Gap Types:**
1. **Error Paths** - Exception handling branches
2. **Edge Cases** - Boundary conditions, empty inputs
3. **Threading Logic** - Race conditions, locks
4. **Retry Logic** - Exponential backoff, max retries
5. **Cleanup Code** - Finally blocks, context managers

### Step 3: Write Targeted Tests

**Example: Covering Error Path**

```python
# Identified gap: cache_manager.py line 234 (exception handling)
def test_cache_handles_corrupted_database():
    """Test cache handles corrupted database gracefully."""
    from vscode_scanner.cache_manager import CacheManager
    import sqlite3

    cache = CacheManager()

    # Corrupt database
    with sqlite3.connect(cache.cache_db_path) as conn:
        conn.execute("DROP TABLE scan_cache")

    # Should handle corruption gracefully (line 234)
    result = cache.get_cached_result("test.ext", "1.0")
    assert result is None  # Graceful degradation
```

### Step 4: Verify Improvement

```bash
# Run tests with coverage
pytest tests/ --cov=vscode_scanner --cov-report=term-missing

# Check specific module
pytest tests/test_cache_manager.py --cov=vscode_scanner.cache_manager --cov-report=term-missing
```

---

## Coverage Best Practices

### DO ✅

- Focus on behavior, not line coverage
- Prioritize security-critical modules
- Test error paths and edge cases
- Use property-based testing for complex logic
- Write regression tests for bugs
- Measure coverage regularly (CI/CD)
- Set realistic targets by module type

### DON'T ❌

- Chase 100% coverage everywhere (diminishing returns)
- Test trivial code (getters, setters)
- Write tests just to increase coverage
- Ignore gaps in security modules
- Skip error path testing
- Focus only on happy paths
- Test implementation details

---

## CI/CD Integration

### GitHub Actions Coverage Workflow

```yaml
# .github/workflows/coverage.yml
- name: Run tests with coverage
  run: |
    pytest tests/ --cov=vscode_scanner --cov-report=xml --cov-report=term

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    fail_ci_if_error: true

- name: Check coverage thresholds
  run: |
    pytest tests/ --cov=vscode_scanner --cov-fail-under=85
```

### Coverage Badges

```markdown
# README.md
[![Coverage](https://codecov.io/gh/jvlivonius/vsc-extension-scanner/branch/main/graph/badge.svg)](https://codecov.io/gh/jvlivonius/vsc-extension-scanner)
```

---

## References

- **[TESTING.md](../TESTING.md)** - Main testing guide
- **[TESTING_SECURITY.md](TESTING_SECURITY.md)** - Security testing guide
- **[TESTING_PROPERTY_BASED.md](TESTING_PROPERTY_BASED.md)** - Property-based testing guide
- **[../../project/STATUS.md](../../project/STATUS.md)** - Current coverage metrics

---

**Document Version:** 2.0.0 (Streamlined as practical guide)
**Last Updated:** 2025-11-09
**Status:** Complete ✅
