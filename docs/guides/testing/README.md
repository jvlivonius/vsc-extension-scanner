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

- **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - Coverage strategy (52% → 70%)
  - Module-by-module coverage goals and gap analysis
  - HTML coverage reports and measurement techniques

---

## Specialized Testing Areas

Domain-specific testing guides:

- **[TESTING_MOCKING.md](TESTING_MOCKING.md)** - Mocking guidelines
  - Canonical mock objects for vscan.dev API
  - Mock validation and drift prevention patterns

- **[TESTING_CLI.md](TESTING_CLI.md)** - CLI testing
  - Command validation and argument parsing tests
  - CliRunner patterns for Typer framework

- **[TESTING_HTML_REPORTS.md](TESTING_HTML_REPORTS.md)** - HTML report testing
  - Self-contained HTML structure validation
  - Embedded CSS/JavaScript and chart generation tests

- **[TESTING_RETRY.md](TESTING_RETRY.md)** - Retry mechanism testing
  - Exponential backoff validation with jitter
  - Retry-After header handling and error classification

- **[TESTING_PARALLEL.md](TESTING_PARALLEL.md)** - Parallel scanning tests
  - Thread-safe statistics validation (ThreadSafeStats)
  - Worker isolation and race condition prevention

- **[PERFORMANCE.md](../PERFORMANCE.md)** § 2 - Performance testing (formerly TESTING_PERFORMANCE.md)
  - Cache speedup validation (50x+ improvement)
  - Memory usage and parallel performance benchmarks

---

## Templates

- **[TEST_FILE_TEMPLATE.md](TEST_FILE_TEMPLATE.md)** - Test file template
  - Complete test file structure with AAA pattern
  - Fixtures, mocking examples, and best practices

---

## Related Documentation

- **Parent Guide:** [../TESTING.md](../TESTING.md) - Main testing overview
- **Contributing:** [../../contributing/TESTING_CHECKLIST.md](../../contributing/TESTING_CHECKLIST.md) - Pre-release checklist
- **Roadmap:** [../../project/v3.5.3-roadmap.md](../../project/v3.5.3-roadmap.md) - Testing Excellence plan

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Total Test Suite:** 604 tests, 100% passing, 52.37% coverage
