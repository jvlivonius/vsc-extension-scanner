# Security Testing Guide

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Applies To:** All 3.x versions
**Target Audience:** Security Engineers, Developers, QA Engineers

---

## Table of Contents

1. [Overview](#overview)
2. [Security Test Coverage](#security-test-coverage)
3. [Path Validation Tests](#path-validation-tests)
4. [String Sanitization Tests](#string-sanitization-tests)
5. [Cache Integrity Tests](#cache-integrity-tests)
6. [SQLite Security Tests](#sqlite-security-tests)
7. [Security Regression Tests](#security-regression-tests)
8. [Automated Security Tools](#automated-security-tools)
9. [Best Practices](#best-practices)

---

## Overview

Security testing is divided into multiple specialized test suites providing comprehensive coverage of security controls:

**Test Files:**
- **test_security.py** - Core security vulnerability tests (11 tests)
- **test_path_validation.py** - Comprehensive path validation coverage (24 tests)
- **test_string_sanitization.py** - String sanitization in all contexts (22 tests)
- **test_cache_integrity.py** - HMAC signature validation (21 tests)
- **test_sqlite_security.py** - SQLite-specific security audit (custom, Phase 1)
- **test_security_regression.py** - Regression suite for all fixed vulnerabilities (24 tests)

**Coverage Goals:**
- **Security Modules:** 95%+ coverage (utils.py, cache_manager.py)
- **Security Functions:** 100% coverage (validate_path, sanitize_string, HMAC validation)
- **Security Tools:** Zero critical findings (Bandit, Safety, pip-audit)

**Run Security Tests:**
```bash
# Complete security test suite (MUST pass before commits)
python3 tests/test_security.py
python3 tests/test_security_regression.py
python3 tests/test_path_validation.py
python3 tests/test_string_sanitization.py
python3 tests/test_cache_integrity.py
python3 tests/test_sqlite_security.py

# Or via test runner
python3 scripts/run_tests.py --security

# With automated tools (Phase 1)
pre-commit run --all-files
bandit -r vscode_scanner/ -ll
safety check
pip-audit
```

---

## Security Test Coverage

### Coverage by File

**Current Counts:** Run `pytest --collect-only -q tests/test_security*.py` for exact test counts.

| Test File | Primary Focus | CVE Coverage |
|-----------|---------------|--------------|
| test_security.py | Core vulnerabilities | CWE-22, CWE-89, CWE-400 |
| test_path_validation.py | Path traversal protection | CWE-22 variants |
| test_string_sanitization.py | Injection prevention | CWE-79, CWE-93, CWE-209 |
| test_cache_integrity.py | HMAC validation | CWE-345 |
| test_sqlite_security.py | SQLite audit | CWE-89, permissions |
| test_security_regression.py | Regression prevention | All fixed CVEs |

**Total Security Tests:** See → [STATUS.md](../../project/STATUS.md) for current security test coverage

---

## Path Validation Tests

### Purpose

Prevent **CWE-22: Path Traversal** attacks by validating all file paths before use.

**Function Under Test:** `vscode_scanner.utils.validate_path(path, path_type)`

**Test File:** `tests/test_path_validation.py` (24 tests)

**Requirements:** See [SECURITY.md - Path Validation](../SECURITY.md#1-path-validation-critical) for complete validation rules, protected paths, and restricted directories

### Test Examples

#### Test 1: Basic Path Traversal Detection

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

#### Test 2: URL-Encoded Traversal Detection (Critical)

```python
def test_url_encoded_traversal_blocked():
    """Detect URL-encoded path traversal attempts.

    CRITICAL: CWE-22 variant that bypasses basic ".." checks.
    """
    from vscode_scanner.utils import validate_path

    url_encoded_attacks = [
        "data/%2e%2e%2f/etc/passwd",          # Single encoding
        "data/%252e%252e%252f/etc/passwd",    # Double encoding
        "data/%2E%2e%2F/etc/passwd",          # Mixed case
    ]

    for attack in url_encoded_attacks:
        with pytest.raises(ValueError):
            validate_path(attack, path_type="output")
```

#### Test 3: System Directory Protection

```python
def test_system_directories_blocked():
    """Block access to system-critical directories."""
    from vscode_scanner.utils import validate_path

    system_dirs = [
        "/etc/passwd",
        "/sys/kernel/config",
        "/proc/self/mem",
        "C:\\Windows\\System32\\config",
    ]

    for sysdir in system_dirs:
        with pytest.raises(ValueError):
            validate_path(sysdir, path_type="output")
```

### Test Coverage

**Attack Vectors:** Tests cover all validation rules from [SECURITY.md](../SECURITY.md#1-path-validation-critical) including path traversal (classic, URL-encoded, double-encoded), shell expansion, system directory access, and null byte injection.

**Coverage Result:** 95%+ of `validate_path()` function (24 tests)

---

## String Sanitization Tests

### Purpose

Prevent **injection attacks** (CWE-79, CWE-93, CWE-209) by sanitizing all user-facing strings.

**Function Under Test:** `vscode_scanner.utils.sanitize_string(s, context, max_length)`

**Test File:** `tests/test_string_sanitization.py` (22 tests)

**Requirements:** See [SECURITY.md - Error Handling](../SECURITY.md#4-error-handling-high) for sanitization requirements and implementation patterns

### Test Examples

#### Test 1: ANSI Escape Sequence Removal (Terminal Injection)

```python
def test_string_sanitization_prevents_terminal_injection():
    """sanitize_string() removes ANSI escape sequences."""
    from vscode_scanner.utils import sanitize_string

    # Test ANSI escape sequences (terminal injection)
    ansi_input = "\x1b[31mRed Text\x1b[0m"
    result = sanitize_string(ansi_input, context="output")
    assert "\x1b" not in result
    assert "Red Text" in result

    # Test terminal control sequences
    clear_screen = "\x1b[2J\x1b[H"
    result = sanitize_string(clear_screen, context="output")
    assert "\x1b" not in result
```

#### Test 2: Path Disclosure in Error Messages (CWE-209)

```python
def test_error_context_sanitizes_paths():
    """Error context sanitizes sensitive path information.

    CRITICAL: CWE-209 - Information Disclosure through Error Messages.
    """
    from vscode_scanner.utils import sanitize_string

    # Test path disclosure in errors
    error_with_path = "File not found: /Users/john/secret/keys.json"
    sanitized = sanitize_string(error_with_path, context="error", max_length=100)

    assert "/Users/john" not in sanitized
    assert "keys.json" not in sanitized
    assert "File not found" in sanitized  # Generic message preserved
```

#### Test 3: Control Character Removal

```python
def test_control_characters_removed():
    """Control characters are removed to prevent attacks."""
    from vscode_scanner.utils import sanitize_string

    # Test various control characters
    control_chars = "Normal\x00text\x01with\x1fcontrol"
    result = sanitize_string(control_chars, context="log")

    assert "\x00" not in result  # Null byte
    assert "\x01" not in result  # Start of heading
    assert "\x1f" not in result  # Unit separator
    assert "Normaltext" in result or "Normal text" in result
```

### Test Coverage

**Attack Vectors:** Tests cover ANSI escape sequences, terminal control characters, log injection, path disclosure in error messages, and null byte attacks across all contexts (output, log, error).

**Coverage Result:** 90%+ of `sanitize_string()` function (22 tests)

---

## Cache Integrity Tests

### Purpose

Prevent **CWE-345: Data Authenticity** attacks by validating HMAC signatures on cached security scores.

**Module Under Test:** `vscode_scanner.cache_manager.CacheManager`

**Test File:** `tests/test_cache_integrity.py` (21 tests)

### Test Examples

#### Test 1: HMAC Tampering Detection (CRITICAL)

```python
def test_cache_integrity_hmac_validation():
    """HMAC signatures prevent cache tampering.

    CRITICAL: If cache entries can be tampered with, security scores
    could be manipulated to hide vulnerabilities.
    """
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

#### Test 2: HMAC Timing-Safe Comparison

```python
def test_hmac_uses_timing_safe_comparison():
    """HMAC validation uses constant-time comparison.

    Prevents timing attacks against HMAC signature validation.
    """
    from vscode_scanner.cache_manager import CacheManager
    import hmac

    # Verify code uses hmac.compare_digest (timing-safe)
    with open("vscode_scanner/cache_manager.py") as f:
        source = f.read()
        assert "hmac.compare_digest" in source, \
            "Must use timing-safe HMAC comparison"
```

#### Test 3: HMAC Secret Key Protection

```python
def test_hmac_secret_permissions():
    """HMAC secret key has user-only permissions (0o600).

    CRITICAL: If secret key is world-readable, attackers can forge signatures.
    """
    from vscode_scanner.cache_manager import CacheManager
    import os
    import stat

    cache = CacheManager()
    secret_file = os.path.join(cache.cache_dir, ".cache_secret")

    # Verify file permissions (Unix systems)
    if os.name != 'nt':  # Skip on Windows
        file_stat = os.stat(secret_file)
        file_mode = stat.S_IMODE(file_stat.st_mode)
        assert file_mode == 0o600, \
            f"Secret key must have 0o600 permissions, got {oct(file_mode)}"
```

### Cache Integrity Coverage

**Attack Vectors Tested:**
- Direct database modification (tampering)
- HMAC signature forgery attempts
- Secret key permission vulnerabilities
- Timing attacks (constant-time comparison)
- Cache poisoning (fake security scores)

**Coverage Result:** 95%+ of HMAC validation code

---

## SQLite Security Tests

### Purpose

Custom security audit for SQLite database usage to prevent SQL injection and ensure secure configuration.

**Test File:** `tests/test_sqlite_security.py` (Custom, Phase 1)

### Test Examples

#### Test 1: SQL Injection Prevention

```python
def test_no_sql_injection_patterns():
    """Scan cache_manager.py for dangerous SQL patterns.

    Verifies all queries use parameterized statements, not string formatting.
    """
    with open("vscode_scanner/cache_manager.py") as f:
        source = f.read()

    # Dangerous patterns (SQL injection vulnerabilities)
    dangerous_patterns = [
        'f"SELECT',
        'f"INSERT',
        'f"UPDATE',
        'f"DELETE',
        '% "SELECT',
        '% "INSERT',
        '.format("SELECT',
    ]

    for pattern in dangerous_patterns:
        assert pattern not in source, \
            f"SQL injection risk: Found {pattern} in cache_manager.py"

    # Verify parameterized queries are used
    assert "cursor.execute(" in source
    assert "?" in source  # Parameterized placeholders
```

#### Test 2: Database File Permissions

```python
def test_sqlite_file_permissions():
    """Verify cache database has user-only permissions (0o600).

    Prevents other users from reading security scan data.
    """
    from vscode_scanner.cache_manager import CacheManager
    import os
    import stat

    cache = CacheManager()

    # Verify cache.db permissions (Unix systems)
    if os.name != 'nt':
        file_stat = os.stat(cache.cache_db_path)
        file_mode = stat.S_IMODE(file_stat.st_mode)
        assert file_mode == 0o600, \
            f"Cache DB permissions: {oct(file_mode)}, expected 0o600"
```

#### Test 3: Database Schema Integrity

```python
def test_database_schema_integrity():
    """Verify database schema matches expected structure."""
    from vscode_scanner.cache_manager import CacheManager
    import sqlite3

    cache = CacheManager()
    conn = sqlite3.connect(cache.cache_db_path)
    cursor = conn.cursor()

    # Verify scan_cache table structure
    cursor.execute("PRAGMA table_info(scan_cache)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    required_columns = {
        'extension_id': 'TEXT',
        'version': 'TEXT',
        'scan_result': 'TEXT',
        'timestamp': 'INTEGER',
        'hmac_signature': 'TEXT',
    }

    for col, dtype in required_columns.items():
        assert col in columns, f"Missing column: {col}"
        assert columns[col] == dtype, \
            f"Column {col} type mismatch: {columns[col]} != {dtype}"

    conn.close()
```

### SQLite Security Coverage

**Checks Performed:**
- File permissions (0o600 for cache.db and .cache_secret)
- SQL injection prevention (parameterized queries only)
- HMAC timing-safe comparison (hmac.compare_digest)
- Database schema integrity
- Directory permissions (0o700 for cache directory)

---

## Security Regression Tests

### Purpose

Comprehensive regression suite ensuring all fixed vulnerabilities stay fixed.

**Test File:** `tests/test_security_regression.py` (24 tests)

### Test Examples

#### Test 1: CWE-22 Regression (Path Traversal Variants)

```python
def test_cwe_22_path_traversal_variants():
    """All CWE-22 path traversal variants remain fixed.

    Covers 3 variants fixed in v2.0:
    - Classic traversal (../)
    - URL-encoded (%2e%2e%2f)
    - Windows traversal (..\)
    """
    from vscode_scanner.utils import validate_path

    # Variant 1: Classic traversal
    with pytest.raises(ValueError):
        validate_path("../../etc/passwd")

    # Variant 2: URL-encoded traversal
    with pytest.raises(ValueError):
        validate_path("data/%2e%2e%2f/etc/passwd")

    # Variant 3: Windows traversal
    with pytest.raises(ValueError):
        validate_path("..\\..\\Windows\\System32")
```

#### Test 2: CWE-400 Regression (Resource Exhaustion)

```python
def test_cwe_400_resource_exhaustion_fixed():
    """Resource exhaustion vulnerabilities remain fixed.

    Fixed in v2.1:
    - No unbounded loops
    - Request timeouts enforced
    - Rate limiting respected
    """
    from vscode_scanner.vscan_api import VScanAPI
    from vscode_scanner.constants import MAX_RETRIES, REQUEST_TIMEOUT

    api = VScanAPI()

    # Verify retry limits (prevents infinite loops)
    assert hasattr(api, 'max_retries')
    assert api.max_retries <= MAX_RETRIES

    # Verify request timeouts (prevents hanging)
    assert hasattr(api, 'request_timeout')
    assert api.request_timeout <= REQUEST_TIMEOUT
```

### Security Regression Coverage

**CVEs/CWEs Covered:**
- **CWE-22:** Path traversal (3 variants)
- **CWE-400:** Resource exhaustion (2 variants)
- **CWE-345:** Data authenticity (HMAC implementation)
- **CWE-209:** Information disclosure (error sanitization)
- **CWE-89:** SQL injection prevention
- **CWE-79:** Cross-site scripting (terminal injection)

**Total Regression Tests:** 24 tests covering all fixed vulnerabilities

---

## Automated Security Tools

### Three-Layer Security Automation (Phase 1)

#### Layer 1: Pre-commit Hooks (Local Prevention)

**Installation:**
```bash
pip install -e .[dev]               # Install security tools
pre-commit install                  # Enable pre-commit hooks
```

**What runs automatically:**
- **Black** - Code formatting consistency
- **Bandit** - AST-based Python security scanner
- **Pylint Security** - Security-focused linting
- **Security Tests** - All test_security*.py files

**Manual execution:**
```bash
pre-commit run --all-files     # Test all hooks
pre-commit run bandit          # Run specific hook
```

**Configuration:** `.pre-commit-config.yaml`

#### Layer 2: Bandit Security Scanner

**Purpose:** AST-based static security vulnerability detection for Python

**Installation:** `pip install bandit` (included in `[dev]` extras)

**Usage:**
```bash
# Terminal output
bandit -r vscode_scanner/ -ll

# JSON report (for CI/CD)
bandit -r vscode_scanner/ -ll -f json -o bandit-report.json

# Find all suppressions in codebase
grep -r "# nosec" vscode_scanner/

# Find suppressions without rule codes (BAD)
grep -r "# nosec[^B]" vscode_scanner/

# Find suppressions without justification (BAD)
grep -r "# nosec B[0-9]\\+$" vscode_scanner/
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

#### Suppression Validation

**Current Project Suppressions:** 4 approved suppressions across 2 files

**Validating Suppressions:**
```bash
# Run Bandit with baseline to track changes
bandit -r vscode_scanner/ -ll -f json -o bandit-current.json

# Compare against baseline
diff bandit-baseline.json bandit-current.json

# Show only suppressed issues
bandit -r vscode_scanner/ -ll --confidence-level MEDIUM --severity-level MEDIUM
```

**Suppression Quality Standards:**
- ✅ Must include specific rule code (e.g., `B310`, `B608`)
- ✅ Must reference validation function (e.g., `validate_url()`)
- ✅ Must explain security control (e.g., "HTTPS enforcement")
- ✅ Must be approved by security review for critical paths
- ❌ Never suppress without justification
- ❌ Never use generic "safe" without explanation

**Test-Driven Suppressions:**

All suppressions should reference security tests that validate the protection:

```python
# This pattern is validated by tests/test_path_validation.py::test_path_traversal
# which confirms all ../ sequences are rejected
sanitized_path = validate_path(user_path)  # nosec B108 - validated by path tests
```

**Current Approved Suppressions:**

1. **urllib.request.urlopen** (vscan_api.py:311) - B310
   - Justification: URL validated by `validate_url()` for HTTPS-only
   - Security Controls: HTTPS enforcement, 10MB response limit, timeout, TLS validation
   - Status: ✅ Approved

2. **SQL Dynamic IN Clause** (cache_manager.py:1137, 1144) - B608
   - Justification: Parameterized query with programmatically generated placeholders
   - Security Controls: `validate_extension_id()`, parameterized tuple, no user data in f-string
   - Status: ✅ Approved

3. **XML Parsing** (scripts/run_tests.py:1671) - B318
   - Justification: XML generated internally, not from external input
   - Security Controls: Trusted data source, test report generation only
   - Status: ✅ Approved

**Suppression Anti-Patterns:**

❌ **Bad - No rule code:**
```python
result = subprocess.run(cmd, shell=True)  # nosec - needed for pipeline
```

❌ **Bad - Vague justification:**
```python
xml_data = minidom.parseString(user_input)  # nosec B318 - safe
```

✅ **Good - Complete justification:**
```python
# nosec B608: Safe SQL - placeholders programmatically generated ("?", "?", ...),
# actual extension IDs passed as parameterized tuple (validated_ids).
# All IDs validated by validate_extension_id() before reaching this code.
cursor.execute(f"DELETE FROM scan_cache WHERE extension_id NOT IN ({placeholders})", validated_ids)
```

**Reference:** See [SECURITY.md § Bandit Suppression Security](../SECURITY.md#9-bandit-suppression-security) for security policy and approval requirements.

#### Layer 3: Safety & pip-audit (Dependency Security)

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

#### Layer 4: CI/CD Security Workflow

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

---

## Best Practices

### Before Every Commit

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

### Tool Priority

1. **Security Tests (test_security*.py)** - Highest authority, must pass
2. **Bandit** - AST security analysis, zero critical required
3. **Safety/pip-audit** - Dependency scanning, no high/critical CVEs
4. **Pre-commit** - Prevention layer, catches issues early

### Security Coverage Goals

- **Overall:** 85% code coverage
- **Security modules:** 95% coverage (utils.py, cache_manager.py)
- **Security tools:** Zero critical findings
- **Dependency CVEs:** Zero high/critical vulnerabilities

### Writing Security Tests

**DO ✅:**
- Test all attack vectors comprehensively
- Use realistic attack payloads
- Document CVE/CWE numbers in docstrings
- Mark critical tests clearly
- Test both positive and negative cases
- Verify error messages don't leak information

**DON'T ❌:**
- Skip edge cases for security functions
- Assume security by obscurity
- Test only happy paths
- Ignore timing attack vulnerabilities
- Forget to test permission settings
- Use weak test data

### Example Security Test Template

```python
def test_security_function_blocks_attack():
    """Test that security function blocks specific attack.

    SECURITY TEST: CWE-XXX - Vulnerability Description

    This test ensures that [specific attack] is blocked by [function].
    If this test fails, [security impact description].

    Attack Vector: [description of attack]
    Expected Behavior: [what should happen]
    """
    # ARRANGE - Set up attack scenario
    malicious_input = "attack_payload"

    # ACT & ASSERT - Verify attack is blocked
    with pytest.raises(ValueError) as exc_info:
        vulnerable_function(malicious_input)

    # Verify error message doesn't leak information
    assert "sensitive_data" not in str(exc_info.value)
```

---

## References

- **[TESTING.md](../TESTING.md)** - Main testing guide
- **[SECURITY.md](SECURITY.md)** - Security requirements and threat model
- **[TESTING_PROPERTY_BASED.md](TESTING_PROPERTY_BASED.md)** - Property-based security testing
- **[../contributing/TESTING_CHECKLIST.md](../contributing/TESTING_CHECKLIST.md)** - Pre-release security checklist

---
