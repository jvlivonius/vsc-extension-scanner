# Security Guide

## Overview

This document establishes security standards, requirements, and best practices for the VS Code Extension Security Scanner. As a security tool, this project must maintain the highest security standards to protect users and maintain trust.

**Security Philosophy:** Defense in depth with fail-fast validation and minimal attack surface.

---

## Current Security Status

**Overall Risk Level:** LOW

The codebase has undergone comprehensive security review and remediation:

- ✅ **Path Traversal:** All 3 critical vulnerabilities fixed
- ✅ **Resource Exhaustion:** All 2 high-severity vulnerabilities fixed
- ✅ **Input Validation:** Comprehensive validation implemented
- ✅ **File Permissions:** Restrictive permissions enforced
- ⚠️ **Cache Integrity:** No HMAC validation (medium priority)

**Security Test Coverage:** 8/10 critical tests passing (80%)

See [archive/reviews/security-analysis.md](../archive/reviews/security-analysis.md) for historical vulnerability details.

---

## Security Architecture

### Defense Layers

```
┌─────────────────────────────────────────────────────┐
│  Input Validation Layer                             │
│  - Path validation (validate_path)                  │
│  - String sanitization (sanitize_string)            │
│  - Size limits (API responses, files)               │
├─────────────────────────────────────────────────────┤
│  Access Control Layer                               │
│  - Directory restrictions (no system paths)         │
│  - Home directory boundaries                        │
│  - File permission enforcement (0o600/0o700)        │
├─────────────────────────────────────────────────────┤
│  Network Security Layer                             │
│  - HTTPS enforcement                                │
│  - Response size limits (10MB)                      │
│  - Request throttling                               │
├─────────────────────────────────────────────────────┤
│  Data Protection Layer                              │
│  - Error message sanitization                       │
│  - Secure cache storage (user-only access)          │
│  - No sensitive data logging                        │
└─────────────────────────────────────────────────────┘
```

### Security Principles

1. **Fail Fast:** Validate inputs immediately, reject invalid data early
2. **Least Privilege:** Minimal file permissions, restricted directory access
3. **Defense in Depth:** Multiple validation layers, no single point of failure
4. **Secure by Default:** Restrictive defaults, explicit opt-in for permissive settings
5. **Information Hiding:** Sanitized error messages, no stack traces to users

---

## Security Requirements

### 1. Path Validation (CRITICAL)

**Requirement:** All user-provided paths must be validated before use.

**Implementation:**
```python
from utils import validate_path

# ALWAYS validate before using paths
if not validate_path(user_path):
    log("Error: Invalid path", "ERROR")
    return 2
```

**Protected Paths:**
- `--output` - Output file path
- `--extensions-dir` - Extensions directory path
- `--cache-dir` - Cache directory path

**Validation Rules:**
- ✅ No parent directory traversal (`..`)
- ✅ No absolute paths (`/`, `C:\`)
- ✅ No home expansion (`~`)
- ✅ No shell metacharacters (`$`, `;`, `|`, `&`)
- ✅ No URL encoding (`%2e`, `%2f`)
- ✅ Must resolve within current working directory (for output)
- ✅ Must resolve within user home (for extensions/cache)

**Restricted Paths:**
- Unix/Linux: `/etc`, `/var`, `/sys`, `/proc`, `/root`, `/usr`
- macOS: Same as Unix/Linux plus `/System`, `/Library`
- Windows: `C:\Windows`, `C:\Program Files`, system32

**Reference:** `utils.py:validate_path()` | `guides/ARCHITECTURE.md:Security`

---

### 2. Input Validation (HIGH)

**Requirement:** All external input must be validated for size and structure.

#### API Response Limits

```python
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB

# Read with size checking
total_read = 0
while chunk := response.read(8192):
    total_read += len(chunk)
    if total_read > MAX_RESPONSE_SIZE:
        raise Exception("Response too large")
```

**Implementation:** `vscan_api.py:_make_request()`

#### File Size Limits

```python
MAX_PACKAGE_JSON_SIZE = 1 * 1024 * 1024  # 1MB

# Check size before reading
file_size = path.stat().st_size
if file_size > MAX_PACKAGE_JSON_SIZE:
    raise Exception("File too large")
```

**Implementation:** `extension_discovery.py:_read_package_json()`

#### JSON Structure Validation

```python
# Validate JSON is expected type
if not isinstance(package_data, dict):
    raise Exception("Invalid JSON structure")

# Validate required fields exist
required_fields = ["name", "publisher", "version"]
for field in required_fields:
    if field not in package_data:
        raise Exception(f"Missing required field: {field}")
```

---

### 3. Access Control (CRITICAL)

**Requirement:** Enforce minimum necessary file permissions.

#### Cache Directory Permissions

```python
# Create with user-only access
cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)  # drwx------

# Ensure database is user-only
if not cache_db.exists():
    cache_db.touch(mode=0o600)  # -rw-------
else:
    cache_db.chmod(0o600)
```

**Implementation:** `cache_manager.py:_init_database()`

#### Directory Restrictions

```python
# Ensure custom paths stay within home directory
home = Path.home().resolve()
try:
    custom_path.relative_to(home)
except ValueError:
    raise FileNotFoundError("Path must be within home directory")
```

**Platform-Specific:**
- Unix/macOS: Use `os.chmod()` with octal permissions
- Windows: Graceful fallback (permissions not enforced)

---

### 4. Error Handling (HIGH)

**Requirement:** Error messages must not disclose sensitive information.

#### Error Message Sanitization

```python
from utils import sanitize_string

try:
    # ... operation ...
except Exception as e:
    # NEVER show raw exception to user
    log("Error: Operation failed", "ERROR")

    # Sanitize any user-facing details
    safe_message = sanitize_string(str(e), max_length=200)
    if verbose:
        log(f"Details: {safe_message}", "ERROR")
```

**What NOT to Include:**
- ❌ Full file paths (reveals directory structure)
- ❌ Stack traces (reveals implementation details)
- ❌ Database errors (reveals schema)
- ❌ Environment variables
- ❌ User names or home directories

**What to Include:**
- ✅ Error type (generic: "File error", "Network error")
- ✅ Actionable suggestions (see ERROR_HANDLING.md)
- ✅ Sanitized error context (first 200 chars, no paths)

**Reference:** `guides/ERROR_HANDLING.md`

---

### 5. Network Security (MEDIUM)

**Requirement:** All network communication must use secure protocols.

#### HTTPS Enforcement

```python
# ALWAYS use HTTPS for vscan.dev API
API_BASE_URL = "https://vscan.dev/api"  # Never http://

# Verify in code
if not url.startswith("https://"):
    raise ValueError("Only HTTPS URLs are allowed")
```

#### TLS Configuration

```python
import ssl

# Strict TLS validation
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

# Use in requests
with urllib.request.urlopen(req, context=ssl_context) as response:
    # ...
```

**Note:** Currently uses Python's default SSL context (secure by default).

---

### 6. Data Protection

**Requirement:** Protect user data and maintain privacy.

#### Cache Data Protection

```python
# User-only access to cache (see Access Control above)
cache_dir permissions: 0o700
cache_db permissions: 0o600
```

#### No Sensitive Data Collection

The tool MUST NOT:
- ❌ Collect or transmit user credentials
- ❌ Track user behavior
- ❌ Log personally identifiable information
- ❌ Store API keys or tokens
- ❌ Access files outside extension directories

#### Information Disclosure Prevention

```python
# Sanitize all output
output_message = sanitize_string(message)

# Remove paths from error messages
error_msg = error_msg.replace(str(Path.home()), "~")
error_msg = error_msg.replace(str(Path.cwd()), ".")
```

---

## Threat Model

### Attack Vectors

| Vector | Threat | Mitigation |
|--------|--------|------------|
| **Malicious Input Paths** | Path traversal to write/read arbitrary files | `validate_path()` with strict rules |
| **Malicious Extensions** | Crafted package.json causes DoS or code execution | Size limits, JSON validation, sandboxed parsing |
| **Compromised vscan.dev** | Malicious API responses cause resource exhaustion | Response size limits, timeout enforcement |
| **Cache Tampering** | Modified cache.db injects false data | File permissions (0o600), integrity checks (future) |
| **MITM Attack** | Intercept/modify API requests | HTTPS enforcement, TLS validation |
| **Local Attacker** | Read sensitive data from cache | Restrictive file permissions (0o700/0o600) |

### Trust Boundaries

```
┌─────────────────────────────────────────────────┐
│  UNTRUSTED: User Input                          │
│  - CLI arguments (paths, filters)               │
│  - Extension directory contents (package.json)  │
├─────────────────────────────────────────────────┤
│  SEMI-TRUSTED: vscan.dev API                    │
│  - API responses (validated, size-limited)      │
├─────────────────────────────────────────────────┤
│  TRUSTED: Application Code                      │
│  - Security utilities (validate_path)           │
│  - Constants (MAX_RESPONSE_SIZE)                │
└─────────────────────────────────────────────────┘
```

### Out of Scope Threats

The following are **not** defended against:
- ❌ Root/admin privilege abuse (don't run as root!)
- ❌ Kernel-level attacks
- ❌ Hardware attacks
- ❌ Social engineering
- ❌ Compromised Python interpreter

---

## Security Testing

### Test Categories

#### 1. Path Traversal Tests

```bash
# Should FAIL (blocked)
vscan scan --output /etc/test.json
vscan scan --output ../../../tmp/escape.json
vscan scan --extensions-dir /etc
vscan scan --cache-dir /tmp/evil

# Should SUCCEED
vscan scan --output ./results.json
vscan scan --output results/data.json
vscan scan --cache-dir ~/.vscan-custom
```

#### 2. Input Validation Tests

```bash
# Test large file handling
dd if=/dev/zero of=huge.json bs=1M count=20  # 20MB
# Tool should reject files > 10MB

# Test malformed JSON
echo "{ invalid json" > bad.json
# Tool should handle gracefully
```

#### 3. Permission Tests

```bash
# Check cache permissions
ls -la ~/.vscan/
# Should show: drwx------ (700) for directory
# Should show: -rw------- (600) for cache.db
```

#### 4. Network Security Tests

```bash
# Verify HTTPS enforcement
# Inspect code: grep -r "http://" vscode_scanner/
# Should only find in comments/docs, not in API URLs
```

### Running Security Tests

```bash
# Full security test suite
python3 tests/test_security.py

# Expected output:
# Tests Passed: 8
# Tests Failed: 0 (or 2 for cache integrity)
```

### Continuous Testing

Security tests SHOULD be run:
- ✅ Before every commit (pre-commit hook)
- ✅ On every PR (CI/CD pipeline)
- ✅ Before every release
- ✅ After dependency updates

---

## Security Compliance

### CWE Coverage

| CWE | Name | Status |
|-----|------|--------|
| CWE-22 | Path Traversal | ✅ **FIXED** (3 instances) |
| CWE-89 | SQL Injection | ✅ **SAFE** (parameterized queries) |
| CWE-400 | Resource Exhaustion | ✅ **FIXED** (size limits) |
| CWE-345 | Data Authenticity | ⚠️ **PARTIAL** (no HMAC yet) |
| CWE-732 | Incorrect Permissions | ✅ **FIXED** (0o600/0o700) |
| CWE-209 | Information Disclosure | ✅ **FIXED** (sanitized errors) |

### OWASP Top 10 (2021)

| Category | Coverage | Status |
|----------|----------|--------|
| A01:2021 - Broken Access Control | Path validation, directory restrictions | ✅ **FIXED** |
| A03:2021 - Injection | Parameterized SQL, input validation | ✅ **SAFE** |
| A04:2021 - Insecure Design | Defense in depth, fail fast | ✅ **FIXED** |
| A05:2021 - Security Misconfiguration | Restrictive defaults, permissions | ✅ **FIXED** |
| A08:2021 - Software and Data Integrity | ⚠️ Cache integrity (no HMAC) | ⚠️ **PARTIAL** |

---

## Known Security Limitations

### 1. Cache Integrity (Medium Priority)

**Issue:** No cryptographic integrity validation (HMAC) on cached data.

**Impact:** Attacker with filesystem access could modify cache.db to inject false security scores.

**Mitigation:** File permissions (0o600) prevent other users from modifying cache.

**Future Enhancement:** Implement HMAC signatures for cache entries.

**Reference:** [archive/reviews/security-analysis.md](../archive/reviews/security-analysis.md) #6

### 2. JSON Recursion Depth (Low Priority)

**Issue:** Python's json module has default recursion limits but deeply nested JSON could cause performance issues.

**Impact:** Malicious package.json with extreme nesting could cause temporary slowdown.

**Mitigation:** Size limits (1MB) make this attack impractical.

**Future Enhancement:** Explicit recursion depth checking.

---

## Security Development Workflow

### Adding New Features

When adding features that involve:

1. **User Input** → Use `validate_path()` and `sanitize_string()`
2. **File Operations** → Check permissions, validate sizes
3. **Network Requests** → Enforce HTTPS, add size limits
4. **Error Handling** → Sanitize messages, no stack traces
5. **Cache/Database** → Parameterized queries, integrity checks

### Code Review Checklist

Security reviewers MUST verify:

- [ ] All user paths validated with `validate_path()`
- [ ] Error messages sanitized with `sanitize_string()`
- [ ] File sizes checked before reading
- [ ] File permissions set restrictively (0o600/0o700)
- [ ] No absolute paths or system directories accessed
- [ ] SQL queries use parameterized statements
- [ ] Network requests use HTTPS only
- [ ] No sensitive data in logs or error messages
- [ ] Security tests added for new functionality

---

## Security Resources

### Internal Documentation

- **[guides/ARCHITECTURE.md](ARCHITECTURE.md)** - Security design principles
- **[guides/ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error sanitization patterns
- **[guides/TESTING.md](TESTING.md)** - Security testing strategies
- **[archive/reviews/security-analysis.md](../archive/reviews/security-analysis.md)** - Historical security audit
- **[archive/reviews/security-fixes.md](../archive/reviews/security-fixes.md)** - Applied security fixes

### External Standards

- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)
- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security.html)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/projects/ssdf)

### Security Utilities

**Core Security Functions:**
- `utils.py:validate_path(path: str) -> bool` - Path validation
- `utils.py:sanitize_string(text: str, max_length: int) -> str` - String sanitization

**Constants:**
- `constants.py:MAX_RESPONSE_SIZE` - API response limit (10MB)
- `constants.py:MAX_PACKAGE_JSON_SIZE` - File size limit (1MB)

---

## Reporting Security Issues

**DO NOT** file public GitHub issues for security vulnerabilities.

Instead:
1. Contact the maintainer privately
2. Provide detailed reproduction steps
3. Allow 90 days for remediation before public disclosure

**For security questions about using the tool:**
- File a GitHub issue with `[SECURITY]` prefix
- Ask in discussions

---

## Security Changelog

| Date | Change | Impact |
|------|--------|--------|
| 2025-10-22 | Initial security audit completed | 15 vulnerabilities identified |
| 2025-10-22 | Path traversal fixes applied | 3 CRITICAL issues fixed |
| 2025-10-22 | Resource exhaustion fixes applied | 2 HIGH issues fixed |
| 2025-10-23 | Error sanitization refactoring | 1 HIGH issue fixed |
| 2025-10-24 | Cross-platform path security | Windows compatibility added |

**Current Status:** 82% vulnerability reduction (15 → 2 remaining)

---

**For detailed historical security analysis, see [archive/reviews/](../archive/reviews/) directory.**
