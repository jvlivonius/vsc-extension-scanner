# Security Guide

## Overview

This document establishes security standards, requirements, and best practices for the VS Code Extension Security Scanner. As a security tool, this project must maintain the highest security standards to protect users and maintain trust.

**Security Philosophy:** Defense in depth with fail-fast validation and minimal attack surface.

---

## Current Security Status

**Overall Risk Level:** LOW

The codebase has undergone comprehensive security review and remediation (v3.5.1 complete):

- ✅ **Path Traversal:** All 3 critical vulnerabilities fixed
- ✅ **Resource Exhaustion:** All 2 high-severity vulnerabilities fixed
- ✅ **Input Validation:** Comprehensive validation implemented
- ✅ **File Permissions:** Restrictive permissions enforced
- ✅ **Cache Integrity:** HMAC-SHA256 signatures implemented (v3.5.1)

**Security Test Coverage:** Comprehensive suite with 161+ tests passing, including dedicated security regression tests

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
│  Cache Integrity Layer (v3.5.1)                     │
│  - HMAC-SHA256 signatures on all cached entries     │
│  - Cryptographic secret key (32-byte)               │
│  - Timing-safe signature comparison                 │
│  - Tamper detection and automatic rejection         │
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
- ✅ Case-insensitive system path blocking (v3.5.5+)

**Restricted Paths:**
- Unix/Linux: `/etc`, `/var`, `/sys`, `/proc`, `/root`, `/usr`
- macOS: Same as Unix/Linux plus `/System`, `/Library`
- Windows: `C:\Windows`, `C:\Program Files`, system32

**Case-Insensitive Blocking (v3.5.5):**
On case-insensitive filesystems (macOS APFS/HFS+, Windows NTFS), all case variations of system paths are blocked to prevent security bypasses. Examples: `/Sys`, `/SYS`, `/Etc`, `/ETC`, `/Proc`, `/SYSTEM`, `/Library/SYSTEM`.

**Reference:** `utils.py:validate_path()` | `utils.py:is_restricted_path()` | `guides/ARCHITECTURE.md:Security`

---

### 2. Input Validation (HIGH)

**Requirement:** All external input must be validated for size and structure.

#### API Response Limits

See `constants.py:MAX_RESPONSE_SIZE_BYTES` for the current API response size limit.

```python
# Read with size checking
total_read = 0
while chunk := response.read(8192):
    total_read += len(chunk)
    if total_read > MAX_RESPONSE_SIZE_BYTES:
        raise Exception("Response too large")
```

**Implementation:** `vscan_api.py:_make_request()`

#### File Size Limits

See `constants.py:MAX_PACKAGE_JSON_SIZE` for the current package.json size limit.

```python
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

#### Cache Integrity Checking (v3.5.1)

**Requirement:** All cached data must be cryptographically signed to prevent tampering.

```python
import hmac
import hashlib
import secrets

# Secret key management (32-byte cryptographic key)
secret_key_path = cache_dir / ".cache_secret"
if not secret_key_path.exists():
    secret_key = secrets.token_bytes(32)
    secret_key_path.write_bytes(secret_key)
    secret_key_path.chmod(0o600)  # User-only access

# Compute HMAC-SHA256 signature on write
def compute_signature(data: str, secret_key: bytes) -> str:
    return hmac.new(
        secret_key,
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

# Verify signature on read (timing-safe comparison)
def verify_signature(data: str, expected_sig: str, secret_key: bytes) -> bool:
    computed_sig = compute_signature(data, secret_key)
    # Use timing-safe comparison to prevent timing attacks
    return hmac.compare_digest(computed_sig, expected_sig)

# On cache read, verify integrity
signature = get_cached_signature(extension_id)
if not verify_signature(cached_data, signature, secret_key):
    # Tampered entry detected - treat as cache miss
    log("Cache integrity check failed", "WARNING")
    return None
```

**Security Features:**
- 32-byte cryptographic keys generated with `secrets.token_bytes()`
- HMAC-SHA256 algorithm for strong signature security
- Timing-safe comparison prevents timing attack vulnerabilities
- Tampered entries automatically rejected (treated as cache miss)
- Per-user secret keys (stored in `~/.vscan/.cache_secret` with 0o600 permissions)

**Implementation:** `cache_manager.py:_get_or_create_secret_key()`, `_compute_integrity_signature()`, `_verify_integrity_signature()`

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

### 7. Concurrency Security (v3.5.0+)

**Requirement:** All shared state must be thread-safe when using parallel scanning.

Parallel scanning (v3.5.0+) introduces concurrency with 1-5 worker threads. All shared state must be protected with proper synchronization primitives to prevent race conditions and data corruption.

#### Thread-Safe Statistics

```python
from threading import Lock

class ThreadSafeStats:
    """Thread-safe statistics collection for parallel scanning."""

    def __init__(self):
        self._lock = Lock()
        self._stats = {
            'total_scanned': 0,
            'vulnerabilities_found': 0,
            'cache_hits': 0,
            'api_calls': 0
        }

    def increment(self, key: str, amount: int = 1):
        """Thread-safe increment operation."""
        with self._lock:
            self._stats[key] = self._stats.get(key, 0) + amount

    def get_stats(self) -> dict:
        """Thread-safe read of all statistics."""
        with self._lock:
            return self._stats.copy()
```

**Implementation:** `scanner.py:ThreadSafeStats` (lines 33-117)

#### Worker Isolation

```python
# Each worker thread has isolated API client instance
def worker_function(extension_info, worker_id):
    # Create isolated API client per worker
    api_client = VScanAPI()  # No shared state

    # Scan extension with isolated client
    result = api_client.scan_extension(extension_info)

    # Thread-safe statistics update
    stats.increment('total_scanned', 1)
    if result.has_vulnerabilities:
        stats.increment('vulnerabilities_found', 1)

    return result
```

**Security Features:**
- **Lock-based synchronization:** All shared state protected by `threading.Lock`
- **Worker isolation:** Each worker has isolated API client (no shared network state)
- **Main thread serialization:** Database writes occur in main thread only (SQLite limitation)
- **No shared mutable state:** Workers only share immutable configuration and thread-safe statistics

**Concurrency Configuration:**

See `scanner.py` for current worker configuration values:
- `DEFAULT_WORKER_COUNT` - Default parallel workers (3)
- `MIN_WORKERS` - Sequential mode (1)
- `MAX_WORKERS` - Maximum parallelism (5)

**Thread Safety Rules:**
- ✅ Statistics updates: Always use `ThreadSafeStats` class with locks
- ✅ API clients: Create isolated instances per worker thread
- ✅ Database writes: Serialize in main thread after worker completion
- ❌ Never share mutable objects between workers without synchronization
- ❌ Never perform database writes from worker threads

**Reference:** `scanner.py:ThreadSafeStats`, `scanner.py:_parallel_scan_extensions()`

---

### 8. Retry Security

**Requirement:** Retry logic must prevent DoS attacks and resource exhaustion.

The API client implements exponential backoff with jitter to handle transient failures without creating additional security vulnerabilities.

#### Retry Configuration

See `constants.py` for current retry configuration values:
- `DEFAULT_MAX_RETRIES` - Maximum retry attempts for HTTP requests
- `DEFAULT_RETRY_BASE_DELAY` - Base delay for exponential backoff
- `MAX_BACKOFF_DELAY` - Maximum retry delay ceiling
- Jitter factor (±20% randomization) prevents thundering herd

#### Exponential Backoff with Jitter

```python
def _calculate_backoff_delay(retry_count: int, base_delay: float) -> float:
    """Calculate retry delay with exponential backoff and jitter."""
    # Exponential backoff: base_delay * 2^retry_count
    delay = base_delay * (2 ** retry_count)

    # Apply maximum ceiling (prevents DoS via Retry-After manipulation)
    delay = min(delay, MAX_BACKOFF_DELAY)

    # Add jitter: ±20% randomization (prevents thundering herd)
    jitter = delay * JITTER_FACTOR * (2 * random.random() - 1)
    delay = max(0, delay + jitter)

    return delay
```

**Implementation:** `vscan_api.py:_calculate_backoff_delay()` (lines 344-366)

#### Non-Retryable Error Detection

```python
def _is_retryable_error(status_code: int, error_type: str) -> bool:
    """Determine if error should trigger retry or fail immediately."""
    # Client errors (4xx) - don't retry (permanent failures)
    non_retryable_status = [400, 401, 403, 404]
    if status_code in non_retryable_status:
        return False

    # Server error 500 - don't retry (may indicate serious issue)
    if status_code == 500:
        return False

    # Transient errors - safe to retry
    retryable_status = [408, 429, 502, 503, 504]
    return status_code in retryable_status
```

**Implementation:** `vscan_api.py:_is_retryable_error()` (lines 368-393)

#### Security Features

- **Maximum delay ceiling (30s):** Prevents DoS via malicious `Retry-After` headers
- **Jitter randomization (±20%):** Prevents thundering herd attacks during recovery
- **Non-retryable error detection:** 400, 401, 403, 404, 500 fail immediately (no retry loops)
- **Workflow-level retry separation:** Different retry limits for critical vs. non-critical operations
- **Exponential backoff:** Reduces load on failing services during incidents

**Retry Strategy by Operation:**

See `constants.py:DEFAULT_MAX_RETRIES` and `constants.py:DEFAULT_RETRY_BASE_DELAY` for current retry settings. The tool uses different retry strategies for critical vs. non-critical operations:

- **Critical operations** (extension scanning): Full retry with exponential backoff
- **Non-critical operations** (cache updates): Minimal retry for performance

**Thread Safety:** Each worker thread has isolated retry state (no shared retry counters)

**Reference:** `vscan_api.py:_make_request()`, `vscan_api.py:_calculate_backoff_delay()`

---

## Threat Model

### Attack Vectors

| Vector | Threat | Mitigation |
|--------|--------|------------|
| **Malicious Input Paths** | Path traversal to write/read arbitrary files | `validate_path()` with strict rules |
| **Malicious Extensions** | Crafted package.json causes DoS or code execution | Size limits, JSON validation, sandboxed parsing |
| **Compromised vscan.dev** | Malicious API responses cause resource exhaustion | Response size limits, timeout enforcement |
| **Cache Tampering** | Modified cache.db injects false data | File permissions (0o600), HMAC-SHA256 signatures (v3.5.1) |
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
| CWE-345 | Data Authenticity | ✅ **FIXED** (HMAC-SHA256 signatures, v3.5.1) |
| CWE-732 | Incorrect Permissions | ✅ **FIXED** (0o600/0o700) |
| CWE-209 | Information Disclosure | ✅ **FIXED** (sanitized errors) |

### OWASP Top 10 (2021)

| Category | Coverage | Status |
|----------|----------|--------|
| A01:2021 - Broken Access Control | Path validation, directory restrictions | ✅ **FIXED** |
| A03:2021 - Injection | Parameterized SQL, input validation | ✅ **SAFE** |
| A04:2021 - Insecure Design | Defense in depth, fail fast | ✅ **FIXED** |
| A05:2021 - Security Misconfiguration | Restrictive defaults, permissions | ✅ **FIXED** |
| A08:2021 - Software and Data Integrity | HMAC-SHA256 cache integrity | ✅ **FIXED** (v3.5.1) |

---

## Known Security Limitations

### Resolved Limitations

#### 1. ✅ Cache Integrity (RESOLVED in v3.5.1)

**Previous Issue:** No cryptographic integrity validation (HMAC) on cached data.

**Resolution:** HMAC-SHA256 signatures implemented with timing-safe comparison. All cached entries are now cryptographically signed with per-user secret keys. Tampered entries are automatically detected and rejected.

**Implementation:** See Section 6: Data Protection - Cache Integrity Checking

**Reference:** [archive/reviews/security-analysis.md](../archive/reviews/security-analysis.md) #6

---

### Current Limitations

### 1. JSON Recursion Depth (Low Priority)

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
- `constants.py:MAX_RESPONSE_SIZE_BYTES` - API response limit
- `constants.py:MAX_PACKAGE_JSON_SIZE` - File size limit
- `constants.py:DEFAULT_MAX_RETRIES` - HTTP retry attempts
- `constants.py:DEFAULT_RETRY_BASE_DELAY` - Retry delay base
- `constants.py:MAX_BACKOFF_DELAY` - Maximum retry delay ceiling

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
| 2025-10-28 | HMAC cache integrity implemented (v3.5.1) | CWE-345 fixed, OWASP A08 resolved |
| 2025-10-28 | Path validation enhanced (v3.5.1) | URL encoding + shell expansion detection |
| 2025-10-28 | String sanitization hardening (v3.5.1) | ANSI escape removal, control char filtering |
| 2025-10-28 | Comprehensive security test suite (v3.5.1) | 161+ tests including regression tests |

**Current Status:** 93% vulnerability reduction (15 → 1 remaining), v3.5.1 security hardening complete

---

**For detailed historical security analysis, see [archive/reviews/](../archive/reviews/) directory.**
