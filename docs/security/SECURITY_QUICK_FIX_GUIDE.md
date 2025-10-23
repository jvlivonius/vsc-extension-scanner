# Security Quick Fix Guide
**Critical Vulnerabilities - Immediate Action Required**

This guide provides copy-paste fixes for the most critical security vulnerabilities identified in the VS Code Extension Scanner codebase.

---

## ⚠️ CRITICAL: Path Traversal Vulnerabilities

### Fix #1: Secure Output File Writing (vscan.py)

**Location:** `vscan.py:361-372`

**Replace this code:**
```python
# Output results
if args.output:
    try:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        log(f"Results written to {args.output}", "SUCCESS")
    except Exception as e:
        log(f"Error writing output file: {e}", "ERROR")
        return 2
```

**With this secure version:**
```python
# Output results
if args.output:
    try:
        # Validate and restrict output path
        output_path = Path(args.output).resolve()
        cwd = Path.cwd().resolve()

        # Ensure output is within current directory
        try:
            output_path.relative_to(cwd)
        except ValueError:
            log("Error: Output path must be within current directory", "ERROR")
            log(f"  Attempted: {output_path}", "ERROR")
            log(f"  Current directory: {cwd}", "ERROR")
            return 2

        # Check for traversal patterns
        if ".." in str(args.output) or args.output.startswith("/"):
            log("Error: Invalid characters in output path", "ERROR")
            return 2

        # Create parent directories with restricted permissions
        output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)

        # Write with exclusive create to prevent race conditions
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        log(f"Results written to {args.output}", "SUCCESS")
    except Exception as e:
        log(f"Error writing output file: {type(e).__name__}", "ERROR")
        if verbose:
            log(f"Details: {e}", "ERROR")
        return 2
```

---

### Fix #2: Secure Extensions Directory (extension_discovery.py)

**Location:** `extension_discovery.py:36-43`

**Replace this code:**
```python
if self.custom_dir:
    custom_path = Path(self.custom_dir).expanduser().resolve()
    if not custom_path.exists():
        raise FileNotFoundError(f"Custom extensions directory not found: {custom_path}")
    if not custom_path.is_dir():
        raise FileNotFoundError(f"Custom extensions path is not a directory: {custom_path}")
    return custom_path
```

**With this secure version:**
```python
if self.custom_dir:
    # Validate path doesn't contain dangerous patterns
    if ".." in self.custom_dir or self.custom_dir.startswith("/etc") or self.custom_dir.startswith("/var") or self.custom_dir.startswith("/sys"):
        raise FileNotFoundError(f"Invalid or restricted path: {self.custom_dir}")

    custom_path = Path(self.custom_dir).expanduser().resolve()

    # Ensure path is within user's home directory
    home = Path.home().resolve()
    try:
        custom_path.relative_to(home)
    except ValueError:
        raise FileNotFoundError(f"Custom extensions directory must be within home directory: {custom_path}")

    if not custom_path.exists():
        raise FileNotFoundError(f"Custom extensions directory not found: {custom_path}")
    if not custom_path.is_dir():
        raise FileNotFoundError(f"Custom extensions path is not a directory: {custom_path}")

    return custom_path
```

---

### Fix #3: Secure Cache Directory (cache_manager.py)

**Location:** `cache_manager.py:21-29`

**Replace this code:**
```python
def __init__(self, cache_dir: Optional[str] = None):
    """
    Initialize cache manager.

    Args:
        cache_dir: Directory to store cache database. Defaults to ~/.vscan/
    """
    self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".vscan"
    self.cache_db = self.cache_dir / "cache.db"
```

**With this secure version:**
```python
def __init__(self, cache_dir: Optional[str] = None):
    """
    Initialize cache manager.

    Args:
        cache_dir: Directory to store cache database. Defaults to ~/.vscan/
    """
    if cache_dir:
        # Validate cache directory path
        if ".." in cache_dir or cache_dir.startswith("/etc") or cache_dir.startswith("/var"):
            raise ValueError(f"Invalid cache directory path: {cache_dir}")

        cache_path = Path(cache_dir).expanduser().resolve()

        # Ensure within user's home directory
        home = Path.home().resolve()
        try:
            cache_path.relative_to(home)
        except ValueError:
            raise ValueError(f"Cache directory must be within home directory: {cache_path}")

        self.cache_dir = cache_path
    else:
        self.cache_dir = Path.home() / ".vscan"

    self.cache_db = self.cache_dir / "cache.db"
```

---

## ⚠️ HIGH: Resource Exhaustion

### Fix #4: API Response Size Limits (vscan_api.py)

**Location:** `vscan_api.py:43-92`

**Add this constant at the top of the file (after line 15):**
```python
# Maximum response size (10MB)
MAX_RESPONSE_SIZE = 10 * 1024 * 1024
```

**Replace this code (lines 82-92):**
```python
try:
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status_code = response.getcode()
        raw_response = response.read().decode('utf-8')

        try:
            json_data = json.loads(raw_response)
        except json.JSONDecodeError:
            json_data = {}

        return status_code, json_data
```

**With this secure version:**
```python
try:
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status_code = response.getcode()

        # Read response with size limit
        raw_response = b''
        chunk_size = 8192
        total_read = 0

        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break

            total_read += len(chunk)
            if total_read > MAX_RESPONSE_SIZE:
                raise Exception(f"Response exceeds maximum size ({MAX_RESPONSE_SIZE} bytes)")

            raw_response += chunk

        raw_response = raw_response.decode('utf-8')

        try:
            json_data = json.loads(raw_response)
        except json.JSONDecodeError:
            json_data = {}

        return status_code, json_data
```

---

## ⚠️ HIGH: Package.json Size Limits

### Fix #5: Validate package.json Size (extension_discovery.py)

**Location:** `extension_discovery.py:118-131`

**Add this constant at the top (after imports):**
```python
# Maximum package.json size (1MB)
MAX_PACKAGE_JSON_SIZE = 1024 * 1024
```

**Replace this code:**
```python
try:
    with open(package_json_path, 'r', encoding='utf-8') as f:
        package_data = json.load(f)

except json.JSONDecodeError as e:
    raise Exception(f"Invalid JSON in package.json: {e}")
except Exception as e:
    raise Exception(f"Error reading package.json: {e}")
```

**With this secure version:**
```python
try:
    # Check file size first
    file_size = package_json_path.stat().st_size
    if file_size > MAX_PACKAGE_JSON_SIZE:
        raise Exception(f"package.json too large: {file_size} bytes (max: {MAX_PACKAGE_JSON_SIZE})")

    # Read with size limit
    with open(package_json_path, 'r', encoding='utf-8') as f:
        content = f.read(MAX_PACKAGE_JSON_SIZE + 1)

        if len(content) > MAX_PACKAGE_JSON_SIZE:
            raise Exception(f"package.json exceeds size limit ({MAX_PACKAGE_JSON_SIZE} bytes)")

        package_data = json.loads(content)

        # Validate it's a dictionary
        if not isinstance(package_data, dict):
            raise Exception("package.json must be a JSON object")

except json.JSONDecodeError as e:
    raise Exception(f"Invalid JSON in package.json: {e}")
except Exception as e:
    raise Exception(f"Error reading package.json: {e}")
```

---

## ⚠️ MEDIUM: Improved Path Validation

### Fix #6: Better validate_path() Implementation (utils.py)

**Location:** `utils.py:70-88`

**Replace this code:**
```python
def validate_path(path: str) -> bool:
    """
    Validate that a path doesn't contain dangerous patterns.

    Args:
        path: Path to validate

    Returns:
        True if path is safe, False otherwise
    """
    # Check for path traversal attempts
    dangerous_patterns = ['../', '..\\', '../', '..\\\\']
    path_lower = path.lower()

    for pattern in dangerous_patterns:
        if pattern in path_lower:
            return False

    return True
```

**With this secure version:**
```python
def validate_path(path: str) -> bool:
    """
    Validate that a path doesn't contain dangerous patterns.

    Args:
        path: Path to validate

    Returns:
        True if path is safe, False otherwise
    """
    if not path:
        return False

    # Block absolute paths
    if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
        return False

    # Block dangerous patterns
    dangerous_patterns = [
        '..',      # Parent directory
        '~',       # Home expansion
        '$',       # Variable expansion
        '%',       # URL encoding
        '\\x',     # Hex encoding
        '\0',      # Null byte
        '|',       # Pipe
        ';',       # Command separator
        '&',       # Background
        '`',       # Command substitution
        '\n',      # Newline
        '\r'       # Carriage return
    ]

    for pattern in dangerous_patterns:
        if pattern in path:
            return False

    # Ensure path stays within current directory
    try:
        resolved = Path(path).resolve()
        cwd = Path.cwd().resolve()
        resolved.relative_to(cwd)
    except (ValueError, RuntimeError, OSError):
        return False

    return True
```

---

## ⚠️ MEDIUM: Secure Cache Permissions

### Fix #7: Restrict Cache Directory Permissions (cache_manager.py)

**Location:** `cache_manager.py:39-42`

**Replace this code:**
```python
def _init_database(self):
    """Initialize SQLite database with schema v2.0."""
    # Create cache directory if it doesn't exist
    self.cache_dir.mkdir(parents=True, exist_ok=True)
```

**With this secure version:**
```python
def _init_database(self):
    """Initialize SQLite database with schema v2.0."""
    # Create cache directory with restricted permissions (user-only)
    self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Ensure database file has restrictive permissions
    if not self.cache_db.exists():
        self.cache_db.touch(mode=0o600)
    else:
        # Update permissions on existing database
        self.cache_db.chmod(0o600)
```

---

## Testing Your Fixes

After applying these fixes, run the security test suite:

```bash
python3 test_security_vulnerabilities.py
```

Expected output after fixes:
```
Tests Passed: 10
Tests Failed: 0
Vulnerabilities Confirmed: 0
✅ No vulnerabilities confirmed
```

---

## Priority Order

Apply fixes in this order:

1. **Fix #1** - Output path validation (CRITICAL)
2. **Fix #2** - Extensions directory validation (CRITICAL)
3. **Fix #3** - Cache directory validation (CRITICAL)
4. **Fix #6** - Improve validate_path() (CRITICAL - enables other fixes)
5. **Fix #4** - API response limits (HIGH)
6. **Fix #5** - Package.json limits (HIGH)
7. **Fix #7** - Cache permissions (MEDIUM)

---

## Verification Checklist

After applying all fixes:

- [ ] Run `python3 test_security_vulnerabilities.py` - all tests pass
- [ ] Test normal operation: `python vscan.py --verbose`
- [ ] Test path validation:
  - [ ] `python vscan.py --output /etc/test.json` → Should fail
  - [ ] `python vscan.py --extensions-dir /etc` → Should fail
  - [ ] `python vscan.py --cache-dir /tmp/test` → Should fail
- [ ] Test with legitimate paths:
  - [ ] `python vscan.py --output ./results.json` → Should work
  - [ ] `python vscan.py --cache-dir ~/.vscan-custom` → Should work
- [ ] Review error messages don't leak sensitive info
- [ ] Check cache file permissions: `ls -la ~/.vscan/` → Should show `drwx------`

---

## Additional Security Hardening

### Optional: Add TLS Certificate Validation

In `vscan_api.py`, add before line 83:

```python
import ssl

# Create secure SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

# Use in urlopen call:
with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
```

### Optional: Add Cache Integrity Checks

See `SECURITY_ANALYSIS.md` section on "Cache Poisoning" for HMAC implementation details.

---

**End of Quick Fix Guide**

For complete analysis and additional recommendations, see `SECURITY_ANALYSIS.md`.
