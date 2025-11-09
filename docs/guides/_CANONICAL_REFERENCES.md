# Canonical References Index

**Purpose:** This document establishes the **single source of truth** for concepts documented in multiple places across the documentation.

**Maintainability Principle:** Each concept should be documented in detail in ONE canonical location. Other documents should **link** to the canonical source, not duplicate the content.

---

## How to Use This Index

1. **When writing documentation:** Check this index to see if a concept already has a canonical source
2. **When updating documentation:** Update the canonical source, not the references
3. **When adding new concepts:** Choose a canonical location and add it to this index

---

## Canonical Sources by Topic

### Exit Codes

**Canonical:** [ERROR_HANDLING.md § Exit Codes](ERROR_HANDLING.md#exit-codes)

**What's Documented:** Complete exit code system (0, 1, 2), usage guidelines, examples

**References (link only, don't duplicate):**
- TESTING_CHECKLIST.md → Exit code test scenarios
- PRD.md → Exit code requirements
- CLI implementation → `cli.py`

**Update Trigger:** Changes to exit code meanings or additions of new exit codes

---

### Security Functions

**Canonical:** [SECURITY.md § Security Requirements](SECURITY.md#security-requirements)

**What's Documented:**
- `validate_path()` - Path traversal protection
- `sanitize_string()` - String sanitization for all contexts
- HMAC cache integrity - `_compute_integrity_signature()`, `_verify_integrity_signature()`

**References (link only, don't duplicate):**
- ARCHITECTURE.md § Security Architecture → Links to SECURITY.md
- ERROR_HANDLING.md § Error Sanitization → Links to SECURITY.md
- Implementation → `utils.py`, `cache_manager.py`

**Update Trigger:** New security functions added or existing function signatures change

---

### Performance Benchmarks

**Canonical:** [PERFORMANCE.md § Performance Benchmarks](PERFORMANCE.md#performance-benchmarks)

**What's Documented:**
- Caching performance metrics
- Parallel scanning performance
- Memory usage benchmarks
- Platform-specific measurements

**References (link only, don't duplicate):**
- ARCHITECTURE.md § Parallel Scanning Architecture → Links to PERFORMANCE.md for metrics
- README.md → May reference "X times faster" claims

**Update Trigger:** New benchmarks run, major performance optimizations, or platform changes

**Note:** Benchmarks are living documents - clearly date measurements and specify platform

---

### Testing Philosophy

**Canonical:** [TESTING.md § Testing Philosophy](TESTING.md#testing-philosophy)

**What's Documented:**
- Test behavior, not implementation
- Fast feedback loop
- Isolated tests
- Clear failure messages
- AAA pattern (Arrange-Act-Assert)

**References (link only, don't duplicate):**
- TESTING_CHECKLIST.md → Pre-release testing checklist
- CONTRIBUTING.md → Testing requirements for contributors

**Update Trigger:** Testing methodology changes or new testing patterns adopted

---

### Architecture Layers

**Canonical:** [ARCHITECTURE.md § Layered Architecture](ARCHITECTURE.md#layered-architecture)

**What's Documented:**
- 3-layer architecture (Presentation → Application → Infrastructure)
- Layer responsibilities
- Dependency rules (one-way dependencies)
- Anti-patterns and violations

**References (link only, don't duplicate):**
- CONTRIBUTING.md → Quick reference to layer rules
- test_architecture.py → Automated layer compliance tests

**Update Trigger:** Layer count changes, responsibility shifts, or architectural refactoring

---

### Error Handling Patterns

**Canonical:** [ERROR_HANDLING.md](ERROR_HANDLING.md)

**What's Documented:**
- Display function selection guide (`display_error()`, `display_warning()`, `log()`)
- ERROR_HELP system
- Exit code system
- Error message sanitization
- Fail-fast vs continue-on-failure decisions

**References (link only, don't duplicate):**
- ARCHITECTURE.md § Error Handling Strategy → Links to ERROR_HANDLING.md
- SECURITY.md § Error Message Sanitization → Links to ERROR_HANDLING.md

**Update Trigger:** New error handling patterns, ERROR_HELP system changes, or display function changes

---

### Configuration System

**Canonical:** [ARCHITECTURE.md § Configuration Management](ARCHITECTURE.md#configuration-management)

**What's Documented:**
- Configuration file format (INI)
- Configuration file location (`~/.vscanrc`)
- Configuration hierarchy (CLI args > config file > defaults)
- Configuration schema

**References (link only, don't duplicate):**
- README.md § Configuration → Quick usage examples
- config_manager.py → Implementation

**Update Trigger:** New configuration options, format changes, or hierarchy changes

---

### Constants and Default Values

**Canonical:** `vscode_scanner/constants.py` (CODE, not docs)

**What's Documented:**
- `DEFAULT_REQUEST_DELAY`
- `DEFAULT_MAX_RETRIES`
- `MAX_RESPONSE_SIZE_BYTES`
- `MAX_PACKAGE_JSON_SIZE_BYTES`
- All other constants

**References (link only, don't duplicate):**
- SECURITY.md → References constants.py for size limits
- ERROR_HANDLING.md → References constants.py for delays
- Any documentation → Use `See constants.py:CONSTANT_NAME` pattern

**Update Trigger:** Constants changed in code

**Documentation Pattern:**
```markdown
# ❌ BAD - Duplicating value
The maximum response size is 10MB (10 * 1024 * 1024 bytes).

# ✅ GOOD - Referencing code
See `constants.py:MAX_RESPONSE_SIZE_BYTES` for the current response size limit.
```

---

### Test Directory Structure

**Canonical:** `tests/` directory (CODE, not docs)

**What's Documented:**
- Test file names
- Test file purposes
- Test organization

**References (link only, don't duplicate):**
- TESTING.md § Directory Structure → High-level overview with link to tests/ directory
- Do NOT list all test files with counts in documentation

**Update Trigger:** Test files added, renamed, or removed

**Documentation Pattern:**
```markdown
# ❌ BAD - Hard-coded test list with counts
tests/
├── test_scanner.py  (25 tests)
├── test_display.py  (23 tests)
...

# ✅ GOOD - High-level overview with dynamic reference
Tests are organized by module in the tests/ directory.
Run `pytest --collect-only -q tests/` to see current test list and counts.
```

---

### Module Responsibilities

**Canonical:** [ARCHITECTURE.md § Module Responsibilities](ARCHITECTURE.md#module-responsibilities)

**What's Documented:**
- Each module's purpose
- Layer assignment
- Key functions/classes
- Dependencies

**References (link only, don't duplicate):**
- README.md § Project Structure → High-level overview
- CONTRIBUTING.md → Module guidelines

**Update Trigger:** New modules added, modules refactored, or responsibilities change

---

## Documentation Anti-Patterns

### ❌ Anti-Pattern: Duplicating Exit Codes

**Problem:** Exit codes documented in 3 places (ERROR_HANDLING.md, TESTING_CHECKLIST.md, PRD.md)

**Solution:**
```markdown
# In ERROR_HANDLING.md (canonical)
## Exit Codes {#exit-codes}
[Full detailed table]

# In TESTING_CHECKLIST.md (reference)
Test exit codes defined in [ERROR_HANDLING.md#exit-codes](../guides/ERROR_HANDLING.md#exit-codes)

# In PRD.md (reference)
Exit codes follow [ERROR_HANDLING.md](../guides/ERROR_HANDLING.md#exit-codes)
```

---

### ❌ Anti-Pattern: Hard-Coding Constants

**Problem:** Constants duplicated from code into documentation

**Solution:**
```markdown
# ❌ BAD
The retry delay is 2.0 seconds with a maximum of 30 seconds.

# ✅ GOOD
See `constants.py:DEFAULT_RETRY_BASE_DELAY` and `constants.py:MAX_BACKOFF_DELAY`
```

---

### ❌ Anti-Pattern: Hard-Coding Test Counts

**Problem:** Test counts become stale immediately

**Solution:**
```markdown
# ❌ BAD
test_scanner.py has 25 tests

# ✅ GOOD
test_scanner.py tests core scanning workflow
Run `pytest --collect-only -q tests/test_scanner.py` to see current test count
```

---

## Maintaining This Index

### When to Update This Index

1. **New concept needs documentation** → Choose canonical location, add to index
2. **Duplication detected** → Consolidate to one location, update index
3. **Canonical location changes** → Update index with new location

### Review Frequency

- Monthly: Check for new duplication patterns
- Before releases: Verify all canonical references are current
- After major refactors: Update affected canonical sources

---

## Related Documentation

- [DOCUMENTATION_CONVENTIONS.md](../contributing/DOCUMENTATION_CONVENTIONS.md) - Documentation standards and naming conventions
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design principles
- [SECURITY.md](SECURITY.md) - Security standards and requirements
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error handling patterns and exit codes
- [TESTING.md](TESTING.md) - Testing philosophy and patterns
- [PERFORMANCE.md](PERFORMANCE.md) - Performance benchmarks and optimization strategies

---
