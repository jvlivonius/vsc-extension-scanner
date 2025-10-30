# Coverage Strategy

**Document Type:** Timeless Reference
**Applies To:** All 3.x versions
**Major Revision Trigger:** Major coverage target changes or testing philosophy shifts
**Target Audience:** Contributors, Developers, QA Engineers, Technical Leads
**Purpose:** Define coverage targets, measurement strategies, and quality gates

---

## Table of Contents

1. [Overview](#overview)
2. [Coverage Targets](#coverage-targets)
3. [Priority-Based Testing](#priority-based-testing)
4. [Coverage Measurement](#coverage-measurement)
5. [Quality Gates](#quality-gates)
6. [Test Type Selection](#test-type-selection)
7. [Module-Specific Strategies](#module-specific-strategies)
8. [Continuous Improvement](#continuous-improvement)

---

## Overview

### Philosophy

**Coverage is a diagnostic tool, not a goal.** High coverage indicates thoroughness but doesn't guarantee quality. Our strategy balances:

- **Thoroughness**: Critical paths must be tested
- **Efficiency**: Focus on high-impact areas first
- **Maintainability**: Tests should be clear and stable
- **Security**: Security modules get extra scrutiny

### Current Status vs Baseline

**How to Measure Current Coverage:**
```bash
# Generate current coverage report
pytest tests/ --cov=vscode_scanner --cov-report=term

# Detailed HTML report
pytest tests/ --cov=vscode_scanner --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest tests/ --cov=vscode_scanner --cov-report=term-missing
```

**Baseline (v3.5.2):**
```
Overall Coverage: 52.37%
Target: 70%+
Gap: 17.63 percentage points

Security Modules: 95%+ ✅ EXCELLENT
Core Business Logic: 60% 🟡 GOOD but improvable
Presentation Layer: 80%+ ✅ EXCELLENT
Infrastructure: 60-65% 🟡 MEDIUM
```

**See:** [claudedocs/coverage-baseline-v3.5.2.md](../../claudedocs/coverage-baseline-v3.5.2.md) for detailed baseline analysis.

---

## Coverage Targets

### Overall Targets

| Milestone | Overall Coverage | Branch Coverage | Security Coverage | Status |
|-----------|-----------------|-----------------|-------------------|--------|
| **Baseline** (v3.5.2) | 52.37% | 83.40% | 95%+ | ✅ Achieved |
| **Milestone 1** (v3.5.3) | 70%+ | 85%+ | 95%+ | 🎯 Target |
| **Aspirational** (v4.0) | 85%+ | 90%+ | 98%+ | 🌟 Future |

### Module-Specific Targets

Coverage targets vary by module criticality and type:

#### 🔴 CRITICAL Priority (95%+ coverage required)

**Security Modules:**
- `utils.py` (security functions): 95%+ ✅ **Baseline achieved: 95%+**
- `cache_manager.py` (HMAC integrity): 95%+ (baseline: 60.54%)

**Why 95%+:** Security vulnerabilities can have catastrophic impact. Near-complete coverage required.

**Current Status:**
- Path validation: 95%+ ✅
- String sanitization: 90%+ ✅
- HMAC integrity: Needs improvement to 95%

#### 🟡 HIGH Priority (85%+ coverage required)

**Core Business Logic:**
- `scanner.py`: 85%+ (baseline: 60.29%)
- `vscan_api.py`: 85%+ ✅ **Baseline: 77.99%**
- `extension_discovery.py`: 85%+ (baseline: 63.98%)

**Why 85%+:** Core business logic directly impacts user experience and reliability.

**Focus Areas:**
- Error handling paths
- Edge case scenarios
- Integration points
- Data validation

#### 🟢 MEDIUM Priority (70%+ coverage required)

**Infrastructure & Support:**
- `cli.py`: 70%+ (baseline: 17.55%) 🔴 **CRITICAL GAP**
- `config_manager.py`: 70%+ (baseline: 57.48%)
- `output_formatter.py`: 70%+ (baseline: 62.30%)
- `html_report_generator.py`: 70%+ (baseline: 0.00%) 🔴 **CRITICAL GAP**

**Why 70%+:** Supporting infrastructure needs good coverage but can tolerate some gaps in less-critical paths.

#### 🔵 LOW Priority (60%+ coverage acceptable)

**Presentation Layer:**
- `display.py`: 60%+ ✅ **Baseline: 80.58%**
- UI rendering and formatting code

**Why 60%+:** Presentation code is less critical and often harder to test meaningfully.

### Branch Coverage

**Target: 85%+ branch coverage**

Branch coverage ensures we test both success and failure paths:

```python
# Example: Both branches must be tested
if validate_path(path):  # True branch
    process_file(path)
else:  # False branch - Must also be tested!
    log_error("Invalid path")
```

**Current Branch Coverage: 83.40%** (close to target)

**Focus Areas:**
- Error handling branches
- Conditional logic
- Exception paths

---

## Priority-Based Testing

### Phase-Based Approach

**Phase 1: Foundation** (v3.5.2 → v3.5.3)
- Fix existing test failures
- Document testing patterns
- Establish coverage baseline
- **Status:** In progress ⏳

**Phase 2: CLI Testing Expansion**
- Test all CLI commands: config, cache, report
- Test input validation
- Test error handling
- **Impact:** +15.63% coverage

**Phase 3: Core Module Tests**
- Create missing test files
- Expand error path coverage
- Test edge cases
- **Impact:** +15.86% coverage

**Phase 4: Polish & Validation**
- Test non-security utilities
- Expand integration tests
- Validate coverage targets
- **Impact:** +3.09% coverage

### High-Impact Opportunities

Focus on these modules for maximum coverage improvement:

| Module | Current | Target | Impact | Priority |
|--------|---------|--------|--------|----------|
| `html_report_generator.py` | 0% | 70% | +8.16% | 🔴 CRITICAL |
| `cli.py` | 17.55% | 70% | +9.34% | 🔴 CRITICAL |
| `scanner.py` | 60.29% | 85% | +6.27% | 🟡 HIGH |
| `cache_manager.py` | 60.54% | 95% | +6.12% | 🟡 HIGH |
| `config_manager.py` | 57.48% | 70% | +3.43% | 🟢 MEDIUM |

**Strategy:** Target critical gaps first for maximum coverage improvement per test hour invested.

---

## Coverage Measurement

### Tools

**Primary:** `coverage.py` with branch coverage enabled

```bash
# Run tests with coverage
coverage run -m pytest tests/ -v

# Generate terminal report
coverage report

# Generate HTML report
coverage html

# Generate XML for CI/CD
coverage xml
```

**Configuration:** `.coveragerc`
```ini
[run]
branch = True
source = vscode_scanner/

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod

[html]
directory = htmlcov
```

### Metrics Tracked

1. **Statement Coverage**: % of code lines executed
2. **Branch Coverage**: % of conditional branches tested
3. **Missing Lines**: Specific untested lines
4. **Partial Coverage**: Branches with only one path tested

### Baseline Reports

- **HTML Report**: `htmlcov/index.html` - Interactive module-by-module coverage
- **XML Report**: `coverage.xml` - Machine-readable for CI/CD
- **Gap Analysis**: `claudedocs/coverage-baseline-v3.5.2.md` - Strategic roadmap

---

## Quality Gates

### Pre-Commit Gates

**Before committing code:**
1. ✅ All tests pass (0 failures)
2. ✅ Security tests pass (0 vulnerabilities)
3. ✅ Coverage doesn't decrease from baseline
4. ✅ New code has 70%+ coverage

```bash
# Run quality gate checks
./scripts/pre_commit_checks.sh  # If available
# OR
pytest tests/ && coverage report --fail-under=52
```

### Pull Request Gates

**Before merging PRs:**
1. ✅ All CI/CD tests pass
2. ✅ Coverage baseline maintained (52.37%+)
3. ✅ No new security warnings
4. ✅ Branch coverage maintained (83%+)
5. ✅ New modules have 70%+ coverage

### Release Gates

**Before releasing versions:**
1. ✅ Coverage targets met for milestone
2. ✅ Security modules at 95%+
3. ✅ All property tests pass (1,250+ scenarios)
4. ✅ Integration tests pass
5. ✅ Performance benchmarks met

---

## Test Type Selection

### When to Use Each Test Type

#### Unit Tests (Primary)

**Use When:**
- Testing individual functions/methods
- Testing business logic in isolation
- Fast feedback needed (< 0.1s per test)

**Coverage Goal:** 70-95% depending on module criticality

**Example:**
```python
def test_sanitize_string_removes_ansi_codes(self):
    """Unit test for ANSI code removal."""
    input_str = "\x1b[31mRed\x1b[0m"
    result = sanitize_string(input_str)
    self.assertEqual(result, "Red")
```

#### Property-Based Tests (Hypothesis)

**Use When:**
- Testing security-critical functions
- Validating invariants across input space
- Finding edge cases automatically

**Coverage Goal:** Critical security properties

**Example:**
```python
@given(st.text())
@settings(max_examples=1000)
def test_validate_path_never_crashes(self, path):
    """Property: validate_path handles ANY input."""
    try:
        validate_path(path)
    except (ValueError, OSError):
        pass  # Expected for invalid paths
```

**Benefits:**
- Generates 100-1000+ test cases automatically
- Finds edge cases humans miss
- Provides high confidence in security properties

**Cost:** Slower execution (1-2 seconds per property)

#### Integration Tests

**Use When:**
- Testing component interactions
- Validating end-to-end workflows
- Testing with real implementations (not mocks)

**Coverage Goal:** Key integration points

**Example:**
```python
def test_scan_cache_integration(self):
    """Test scanner → cache integration."""
    scanner = Scanner(cache_enabled=True)
    result = scanner.scan("test.ext")

    # Verify cached correctly
    cached = cache_manager.get("test.ext")
    self.assertEqual(result, cached)
```

#### Security Tests

**Use When:**
- Testing attack resistance
- Validating security boundaries
- Testing defense-in-depth layers

**Coverage Goal:** 95%+ for security modules

**Example:**
```python
def test_blocks_sql_injection(self):
    """Security test: SQL injection prevention."""
    malicious = "'; DROP TABLE scan_cache; --"

    with self.assertRaises(ValueError):
        validate_extension_id(malicious)
```

### Test Type Distribution

**Recommended Mix:**
- 70% Unit tests (fast, focused)
- 15% Integration tests (realistic scenarios)
- 10% Property-based tests (security critical)
- 5% Security regression tests (attack scenarios)

---

## Module-Specific Strategies

### Security Modules (utils.py security functions)

**Target:** 95%+ coverage
**Test Types:** Unit + Property-based + Security regression
**Focus:** Attack resistance, edge cases, error handling

**Strategy:**
```
1. Unit tests for each security function
2. Property-based tests for fuzzing (1000+ cases)
3. Security regression tests for known attacks
4. Error message validation (no info leakage)
```

**Example Coverage Map:**
- Path validation: 95%+ ✅
- String sanitization: 90%+ ✅
- Extension ID validation: 85%+ ✅

### Core Business Logic (scanner.py, vscan_api.py)

**Target:** 85%+ coverage
**Test Types:** Unit + Integration
**Focus:** Happy paths, error handling, edge cases

**Strategy:**
```
1. Unit tests for business logic
2. Integration tests for workflows
3. Error path testing (API failures, timeouts)
4. Edge case coverage (empty results, malformed data)
```

**Missing Coverage:**
- Error recovery paths (scanner.py)
- API retry logic edge cases
- Timeout handling

### Infrastructure (cache_manager.py, config_manager.py)

**Target:** 70-95% (95% for security-critical cache HMAC)
**Test Types:** Unit + Integration + Property-based (cache)
**Focus:** Data integrity, error recovery, edge cases

**Strategy:**
```
1. Cache: HMAC integrity tests (property-based)
2. Config: Validation tests for all config values
3. Error recovery: Corruption handling, missing files
4. Edge cases: Empty cache, invalid config values
```

### CLI (cli.py)

**Target:** 70%+ coverage
**Current:** 17.55% 🔴 **CRITICAL GAP**
**Test Types:** Integration + Unit
**Focus:** Command execution, argument parsing, error handling

**Strategy:**
```
1. Test each command: scan, config, cache, report
2. Test argument combinations
3. Test error messages and help text
4. Test output formatting
```

**Priority Commands:**
1. Config commands (init, show, set, get, reset)
2. Cache commands (stats, clear)
3. Report commands (HTML, JSON, CSV)
4. Error handling (KeyboardInterrupt, permissions)

### HTML Report Generator (html_report_generator.py)

**Target:** 70%+ coverage
**Current:** 0% 🔴 **CRITICAL GAP - NO TESTS EXIST**
**Test Types:** Unit + Integration
**Focus:** Template rendering, data formatting, file generation

**Strategy:**
```
1. Create tests/test_html_report.py (missing)
2. Test HTML generation for various result sets
3. Test error handling (write permissions, invalid data)
4. Validate HTML structure and content
```

**Impact:** +8.16% overall coverage improvement

### Presentation Layer (display.py)

**Target:** 60%+ coverage
**Current:** 80.58% ✅ **EXCEEDS TARGET**
**Test Types:** Unit
**Focus:** Formatting, Rich integration, fallback modes

**Strategy:** Maintain current excellent coverage, add edge cases as found.

---

## Continuous Improvement

### Monitoring

**Weekly:**
- Run coverage reports
- Track coverage trends
- Identify new gaps

**Per PR:**
- Check coverage diff
- Require tests for new code
- Review coverage reports

**Per Release:**
- Validate milestone targets
- Update baseline documentation
- Plan next coverage phase

### Coverage Trend Analysis

**Track Over Time:**
```
v3.5.0: 45% baseline
v3.5.1: 50% (security hardening)
v3.5.2: 52.37% (property tests added)
v3.5.3: 70%+ target (CLI + core modules)
v4.0: 85%+ aspirational (comprehensive coverage)
```

### Addressing Coverage Gaps

**When Coverage Falls:**
1. **Investigate**: Why did coverage decrease?
2. **Assess Impact**: Is the gap in critical code?
3. **Prioritize**: Use priority matrix (security > core > infrastructure)
4. **Plan**: Add to roadmap with impact estimate
5. **Implement**: Write tests to close gap
6. **Verify**: Confirm coverage improvement

### Anti-Patterns to Avoid

❌ **Don't:**
- Write tests just to hit coverage numbers
- Test private implementation details
- Create brittle tests that break easily
- Mock everything (lose integration testing value)
- Ignore hard-to-test code (it's often most important!)

✅ **Do:**
- Focus on behavior, not implementation
- Test critical paths thoroughly
- Write clear, maintainable tests
- Balance unit and integration tests
- Make hard-to-test code testable

---

## Roadmap to 70%+ Coverage

Based on [claudedocs/coverage-baseline-v3.5.2.md](../../claudedocs/coverage-baseline-v3.5.2.md):

### Phase 2: CLI Testing Expansion (+15.63%)

**Tasks:**
1. Test input validators (bounded_int, bounded_float)
2. Test config commands (init, show, set, get, reset)
3. Test cache commands (stats, clear)
4. Test report commands (HTML, JSON, CSV)
5. Test error handling (KeyboardInterrupt, PermissionError)

**Impact:** cli.py: 17.55% → 70% (+9.34% overall)

### Phase 3: Core Module Tests (+15.86%)

**Tasks:**
1. Create tests/test_output_formatter.py (+2.43%)
2. Create tests/test_config_manager.py (+1.00%)
3. Expand tests/test_cache_integrity.py (+6.12%)
4. Create tests/test_extension_discovery.py (+2.04%)
5. Expand tests/test_scanner.py (+6.27%)

**Focus:** Error paths, edge cases, integration points

### Phase 4: Polish & Validation (+3.09%)

**Tasks:**
1. Create tests/test_utils.py (non-security utilities)
2. Polish tests/test_api.py and tests/test_display.py
3. Expand tests/test_integration.py
4. Generate validation reports
5. Update documentation

**Final Coverage Projection:** 86.93% (exceeds 70% target)

---

## Success Criteria

### v3.5.3 Milestone Success

**Must Achieve:**
- ✅ Overall coverage: 70%+
- ✅ Branch coverage: 85%+
- ✅ Security coverage: 95%+
- ✅ All tests passing (306+ tests)
- ✅ Property tests: 1,250+ scenarios passing

**Quality Indicators:**
- Clear, maintainable tests
- Fast execution (< 3 minutes full suite)
- Good documentation of test patterns
- Reproducible results

### Long-Term Success (v4.0)

**Aspirational Targets:**
- Overall coverage: 85%+
- Branch coverage: 90%+
- Security coverage: 98%+
- Property test scenarios: 2,000+
- Integration test coverage: Comprehensive

---

## References

- [TESTING.md](TESTING.md) - Complete testing guide and patterns
- [TEST_FILE_TEMPLATE.md](TEST_FILE_TEMPLATE.md) - Standard test file structure
- [claudedocs/coverage-baseline-v3.5.2.md](../../claudedocs/coverage-baseline-v3.5.2.md) - Detailed gap analysis
- [SECURITY.md](SECURITY.md) - Security requirements and validation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and module responsibilities

---

## Quick Reference

### Coverage Commands

```bash
# Run tests with coverage
coverage run -m pytest tests/ -v

# View terminal report
coverage report

# Check against threshold
coverage report --fail-under=52

# Generate HTML report
coverage html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Generate XML for CI
coverage xml
```

### Priority Matrix

```
Coverage Priority = (Criticality × Impact) / Effort

Where:
- Criticality: Security=10, Core=7, Infrastructure=5, UI=3
- Impact: % coverage improvement potential
- Effort: Hours to implement tests
```

**Example Calculation:**
```
html_report_generator.py:
  Criticality: 5 (Infrastructure)
  Impact: 8.16% coverage gain
  Effort: 4 hours
  Priority: (5 × 8.16) / 4 = 10.2 (HIGH)
```

### Coverage Targets Summary

| Module Type | Target | Current Status |
|-------------|--------|----------------|
| Security | 95%+ | ✅ Achieved |
| Core Logic | 85%+ | 🟡 60-78% (improving) |
| Infrastructure | 70%+ | 🟡 57-65% (improving) |
| Presentation | 60%+ | ✅ 80%+ (exceeds) |
| **Overall** | **70%+** | **52.37% → 70%+ (target)** |
