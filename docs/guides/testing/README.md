# Testing Documentation

Comprehensive testing guides for VS Code Extension Security Scanner.

---

## Quick Navigation

**Start Here:** [../TESTING.md](../TESTING.md) - Main testing guide (overview, quick start, test patterns)

---

## Core Testing Guides

Essential testing documentation for comprehensive coverage:

- **[TESTING_SECURITY.md](TESTING_SECURITY.md)** - Security testing (21K, 95%+ coverage, 102 tests)
  - Path validation (CWE-22), HMAC integrity (CWE-345), error disclosure (CWE-209)
  - Three-layer defense: pre-commit hooks, Bandit scanner, safety/pip-audit

- **[TESTING_PROPERTY_BASED.md](TESTING_PROPERTY_BASED.md)** - Hypothesis property-based testing
  - 20 property tests generating 1,250+ scenarios automatically
  - Fuzzing for path validation, string sanitization, cache integrity

- **[TESTING_INTEGRATION.md](TESTING_INTEGRATION.md)** - Integration testing patterns
  - End-to-end workflows: discovery → scanning → caching → output
  - 7 integration tests covering major user journeys

- **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - How to measure and improve test coverage
  - Module-by-module coverage goals (85%+ overall, 95%+ security)
  - Coverage measurement, analysis, and improvement workflows

---

## Specialized Testing Areas

Domain-specific testing guides:

- **[TESTING_MOCKING.md](TESTING_MOCKING.md)** - Mocking guidelines
  - Canonical mock objects for vscan.dev API
  - Mock validation and drift prevention patterns

- **[PERFORMANCE.md](../PERFORMANCE.md)** § 2 - Performance testing
  - Cache speedup validation and benchmarking methodology
  - Memory usage profiling and parallel performance testing

---

## Templates

- **[TEST_FILE_TEMPLATE.md](TEST_FILE_TEMPLATE.md)** - Test file template
  - Complete test file structure with AAA pattern
  - Fixtures, mocking examples, and best practices

---

## Related Documentation

- **Parent Guide:** [../TESTING.md](../TESTING.md) - Main testing overview
- **Contributing:** [../../contributing/TESTING_CHECKLIST.md](../../contributing/TESTING_CHECKLIST.md) - Pre-release checklist
- **Status:** [../../project/STATUS.md](../../project/STATUS.md) - Current test metrics and coverage

---

**Total Test Suite:** Run `pytest --collect-only -q tests/` for count. See [STATUS.md](../../project/STATUS.md) for coverage.
