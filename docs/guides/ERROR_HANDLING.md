# Error Handling Strategy

**Version:** 3.1.0
**Last Updated:** 2025-10-24
**Status:** Current Implementation + Planned Enhancements

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Error Handling Architecture](#error-handling-architecture)
3. [ERROR_HELP System](#error_help-system)
4. [Error Display Flow](#error-display-flow)
5. [Error Types](#error-types)
6. [Implementation Guide](#implementation-guide)
7. [Planned Enhancements](#planned-enhancements)
8. [Testing Strategy](#testing-strategy)

---

## Philosophy

### Core Principles

**1. Fail Fast with Helpful Guidance**
- Detect errors early in the workflow
- Provide clear, actionable error messages
- Include suggestions for remediation
- Exit with meaningful codes (0, 1, 2)

**2. Comprehensive In-App Help**
- Don't make users search documentation for common errors
- Provide contextual help directly in error messages
- Include examples of correct usage
- Link to detailed docs for complex issues

**3. Centralized Error Routing**
- All user-facing errors go through `display.py`
- Consistent formatting across the application
- Single source of truth for error display
- No scattered `print(..., file=sys.stderr)` calls

**4. Security-Aware Error Messages**
- Sanitize error messages to prevent information disclosure
- Don't expose file paths, API keys, or internal details
- Provide enough info for debugging without security risks

---

## Error Handling Architecture

### Current Architecture (v3.1.0)

```
Exception Occurs
   │
   ├─> Caught in module (vscan_api, scanner, cli)
   │      │
   │      ├─> utils.sanitize_error_message()
   │      │      └─> Remove sensitive info
   │      │
   │      └─> utils.get_error_help(error_type)
   │             └─> Retrieve suggestions from ERROR_HELP
   │
   └─> display.display_error(message, suggestions)
          │
          ├─> Rich formatting (default)
          │      └─> Panel with color-coded severity
          │
          └─> Plain formatting (--plain or no Rich)
                 └─> Text with bullets
```

### Planned Architecture (Future Enhancement)

```
Exception Occurs
   │
   └─> errors.ErrorHandler.handle_error(exception, context)
          │
          ├─> Classify error type
          ├─> Sanitize error message
          ├─> Get contextual suggestions
          └─> Return ErrorContext
                 │
                 └─> display.display_error(context)
                        │
                        ├─> Rich Panel (default)
                        └─> Plain text (fallback)
```

---

## ERROR_HELP System

### Overview

The `ERROR_HELP` dictionary (in `utils.py`) provides comprehensive, actionable guidance for common error scenarios.

**Location:** `vscode_scanner/utils.py:342-451`

**Size:** ~109 lines covering 7 error types

### Structure

```python
ERROR_HELP = {
    "error_type": [
        "Suggestion 1",
        "Suggestion 2",
        "Suggestion 3 (optional command example)",
    ],
    # ...
}
```

### Complete Error Types

#### 1. Rate Limiting (429)

**Triggers:**
- HTTP 429 response
- "rate limit" in error message
- vscan.dev throttling

**Suggestions:**
```python
"rate_limit": [
    "The vscan.dev API has rate limits to prevent abuse",
    "Wait a few minutes before scanning again",
    "Use --delay to increase time between requests: vscan scan --delay 3.0",
    "Use --max-retries to try more times: vscan scan --max-retries 5",
    "Enable caching to reduce API calls: vscan scan (caching is on by default)",
]
```

**Why This Helps:**
- Explains what rate limiting is
- Provides multiple solutions (wait, adjust delays, use cache)
- Includes exact command examples
- Educates user about caching

#### 2. Network Timeout

**Triggers:**
- `TimeoutError` exception
- "timeout" in error message
- Slow network conditions

**Suggestions:**
```python
"timeout": [
    "The request to vscan.dev timed out (default: 30 seconds)",
    "This can happen with slow connections or vscan.dev server issues",
    "Try increasing retries: vscan scan --max-retries 5",
    "Check your internet connection",
    "Try again later if vscan.dev is experiencing issues",
]
```

**Why This Helps:**
- Explains the timeout value
- Distinguishes between local and remote issues
- Provides actionable steps
- Sets reasonable expectations

#### 3. Extension Not Found (404)

**Triggers:**
- HTTP 404 response
- "not found" in error message
- Extension not in vscan.dev database

**Suggestions:**
```python
"not_found": [
    "Extension not found in vscan.dev database",
    "This is normal for newly published or unpopular extensions",
    "vscan.dev may not have scanned this extension yet",
    "You can still view your local extension files, but no security report is available",
    "Try again later - vscan.dev continuously adds new extensions",
]
```

**Why This Helps:**
- Explains why this happens (normal for new extensions)
- Sets expectations (not a bug)
- Provides reassurance (try later)
- Educates about vscan.dev coverage

#### 4. Server Errors (500, 502, 503)

**Triggers:**
- HTTP 500, 502, 503 responses
- "server error", "bad gateway", "service unavailable"

**Suggestions:**
```python
"server_error": [
    "vscan.dev is experiencing server issues (HTTP 5xx)",
    "This is temporary and usually resolves quickly",
    "The tool will automatically retry failed requests",
    "You can increase retry attempts: vscan scan --max-retries 5",
    "Check vscan.dev status: https://vscan.dev",
]
```

**Why This Helps:**
- Explains it's not user's fault
- Indicates automatic retry behavior
- Provides status check URL
- Sets expectations for resolution

#### 5. Network Connection Errors

**Triggers:**
- `ConnectionError`, `URLError`
- "connection refused", "no internet"
- DNS resolution failures

**Suggestions:**
```python
"connection_error": [
    "Could not connect to vscan.dev",
    "Check your internet connection",
    "Verify you can access https://vscan.dev in your browser",
    "Check if you're behind a proxy or firewall",
    "If using VPN, try disconnecting temporarily",
]
```

**Why This Helps:**
- Clear diagnosis (connection problem)
- Step-by-step troubleshooting
- Addresses common scenarios (proxy, VPN)
- Provides verification method (browser test)

#### 6. Invalid JSON Response

**Triggers:**
- `JSONDecodeError`
- Malformed API responses
- Partial responses

**Suggestions:**
```python
"invalid_json": [
    "Received invalid JSON response from vscan.dev",
    "This may indicate a server-side issue or network problem",
    "Try the scan again - this is often temporary",
    "If problem persists, vscan.dev may be experiencing issues",
]
```

**Why This Helps:**
- Explains what happened
- Indicates likely cause (server-side)
- Simple fix (try again)
- Escalation path (if persists)

#### 7. Generic Errors

**Triggers:**
- Any unclassified error
- Unexpected exceptions

**Suggestions:**
```python
"generic": [
    "An unexpected error occurred",
    "Try running the command again",
    "Use --verbose for more details: vscan scan --verbose",
    "If problem persists, report at: https://github.com/username/vsc-extension-scanner/issues",
]
```

**Why This Helps:**
- Acknowledges the error
- Provides simple first step (retry)
- Debugging option (verbose mode)
- Escalation path (issue tracker)

---

## Error Display Flow

### Step 1: Exception Occurs

```python
# Example in vscan_api.py
try:
    response = urllib.request.urlopen(request, timeout=30)
except urllib.error.HTTPError as e:
    if e.code == 429:
        # Rate limit hit
        raise
    elif e.code >= 500:
        # Server error
        raise
    # ...
```

### Step 2: Error Classification

```python
# In utils.py
def classify_error(error: Exception) -> str:
    """Classify error for help lookup."""
    error_str = str(error).lower()

    if 'rate limit' in error_str or '429' in error_str:
        return 'rate_limit'
    elif 'timeout' in error_str:
        return 'timeout'
    elif '404' in error_str:
        return 'not_found'
    elif '500' in error_str or '502' in error_str or '503' in error_str:
        return 'server_error'
    elif 'connection' in error_str:
        return 'connection_error'
    elif 'json' in error_str:
        return 'invalid_json'
    else:
        return 'generic'
```

### Step 3: Error Sanitization

```python
# In utils.py
def sanitize_error_message(message: str, context: str = "") -> str:
    """
    Remove sensitive information from error messages.

    - Remove file paths
    - Remove API keys
    - Remove internal details
    - Keep useful debugging info
    """
    # Remove absolute paths
    sanitized = re.sub(r'/[\w/]+/', '<path>/', message)

    # Remove Windows paths
    sanitized = re.sub(r'[A-Z]:\\[\w\\]+', '<path>', sanitized)

    # Remove potential API keys
    sanitized = re.sub(r'key=[\w-]+', 'key=<redacted>', sanitized)

    return sanitized
```

### Step 4: Get Contextual Help

```python
# In utils.py
def get_error_help(error_type: str) -> List[str]:
    """Get helpful suggestions for error type."""
    return ERROR_HELP.get(error_type, ERROR_HELP['generic'])
```

### Step 5: Display Error

```python
# In display.py
def display_error(
    message: str,
    use_rich: bool = True,
    suggestions: Optional[List[str]] = None
):
    """Display error with optional suggestions."""
    if use_rich and RICH_AVAILABLE:
        from rich.console import Console
        from rich.panel import Panel

        console = Console(stderr=True)

        content = f"[red]✗ Error:[/red] {message}"
        if suggestions:
            content += "\n\n[yellow]Suggestions:[/yellow]"
            for suggestion in suggestions:
                content += f"\n  • {suggestion}"

        console.print(Panel(content, border_style="red"))
    else:
        # Plain text fallback
        print(f"✗ Error: {message}", file=sys.stderr)
        if suggestions:
            print("\nSuggestions:", file=sys.stderr)
            for suggestion in suggestions:
                print(f"  • {suggestion}", file=sys.stderr)
```

---

## Error Types

### By HTTP Status Code

| Code | Error Type | Severity | Retry? |
|------|-----------|----------|--------|
| 400 | Bad Request | Medium | No |
| 404 | Not Found | Low | No |
| 429 | Rate Limit | Medium | Yes (with backoff) |
| 500 | Server Error | High | Yes |
| 502 | Bad Gateway | High | Yes |
| 503 | Service Unavailable | High | Yes |

### By Exception Type

| Exception | Error Type | Severity | Retry? |
|-----------|-----------|----------|--------|
| `TimeoutError` | Timeout | Medium | Yes |
| `ConnectionError` | Connection | High | Yes |
| `JSONDecodeError` | Invalid JSON | Medium | Yes |
| `HTTPError` | (varies by code) | Varies | Varies |

### Exit Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 0 | Success, no vulnerabilities | Scan completed, all extensions clean |
| 1 | Success, vulnerabilities found | Scan completed, issues detected |
| 2 | Failure | Scan failed due to errors |

---

## Implementation Guide

### For New Error Scenarios

**1. Add to ERROR_HELP:**
```python
# In utils.py
ERROR_HELP = {
    # ... existing entries
    "new_error_type": [
        "Brief explanation of what happened",
        "Why this error occurred",
        "How to fix it: command example",
        "Alternative solution if first doesn't work",
    ],
}
```

**2. Add Classification Logic:**
```python
# In utils.py, update classify_error()
def classify_error(error: Exception) -> str:
    error_str = str(error).lower()

    # ... existing checks

    if 'new pattern' in error_str:
        return 'new_error_type'

    return 'generic'
```

**3. Raise and Catch:**
```python
# In your module
try:
    # Operation that might fail
    risky_operation()
except SpecificException as e:
    error_type = classify_error(e)
    suggestions = get_error_help(error_type)
    sanitized = sanitize_error_message(str(e))

    display_error(sanitized, suggestions=suggestions)
    raise typer.Exit(2)
```

### For Module-Specific Errors

**Example: Cache Errors**
```python
# In cache_manager.py
try:
    cursor.execute("SELECT * FROM scan_cache")
except sqlite3.DatabaseError as e:
    error_type = "database_error"  # Custom type
    suggestions = [
        "Database file may be corrupted",
        "Try clearing cache: vscan cache clear --force",
        "Check disk space and permissions",
    ]
    display_error(str(e), suggestions=suggestions)
    raise
```

### For User Input Validation

**Example: Invalid Configuration**
```python
# In config_manager.py
def set_value(self, key: str, value: str):
    if not self.validate_value(key, value):
        suggestions = [
            f"Invalid value '{value}' for {key}",
            "Check valid range with: vscan config show",
            "Example: vscan config set scan.delay 2.0",
        ]
        display_error(f"Configuration error", suggestions=suggestions)
        raise typer.Exit(2)
```

---

## Planned Enhancements

### Future: ErrorHandler Class

**Proposed Implementation:**

```python
# New file: vscode_scanner/errors.py

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ErrorContext:
    """Complete error context for display."""
    error_type: str
    message: str
    suggestions: List[str]
    severity: str  # 'error', 'warning', 'info'
    exit_code: int  # 0, 1, or 2

class ErrorHandler:
    """
    Centralized error handling with contextual help.

    Benefits:
    - Single source of truth for error logic
    - Testable error classification
    - Consistent error UX
    - Easy to extend with new error types
    """

    def __init__(self, error_help: Dict[str, List[str]]):
        self.error_help = error_help

    def handle_error(
        self,
        error: Exception,
        context: str = ""
    ) -> ErrorContext:
        """Convert exception to error context with suggestions."""
        error_type = self._classify_error(error)
        sanitized_message = self._sanitize_message(str(error))
        suggestions = self.error_help.get(error_type, self.error_help['generic'])
        severity = self._get_severity(error_type)
        exit_code = self._get_exit_code(error_type)

        return ErrorContext(
            error_type=error_type,
            message=sanitized_message,
            suggestions=suggestions,
            severity=severity,
            exit_code=exit_code
        )

    def _classify_error(self, error: Exception) -> str:
        """Classify error type for help lookup."""
        # Classification logic from utils.classify_error()
        # ...

    def _sanitize_message(self, message: str) -> str:
        """Remove sensitive information."""
        # Sanitization logic from utils.sanitize_error_message()
        # ...

    def _get_severity(self, error_type: str) -> str:
        """Map error type to severity."""
        severity_map = {
            'rate_limit': 'warning',
            'timeout': 'warning',
            'not_found': 'info',
            'server_error': 'error',
            'connection_error': 'error',
            'invalid_json': 'error',
            'generic': 'error',
        }
        return severity_map.get(error_type, 'error')

    def _get_exit_code(self, error_type: str) -> int:
        """Determine appropriate exit code."""
        # 'not_found' might be 1 (found issue)
        # Others are 2 (scan failed)
        return 1 if error_type == 'not_found' else 2
```

**Usage:**
```python
# In any module
from vscode_scanner.errors import ErrorHandler, ErrorContext
from vscode_scanner.display import display_error
from vscode_scanner.utils import ERROR_HELP

error_handler = ErrorHandler(ERROR_HELP)

try:
    # Risky operation
    scan_extension()
except Exception as e:
    ctx = error_handler.handle_error(e, context="scan")
    display_error(ctx.message, suggestions=ctx.suggestions)
    raise typer.Exit(ctx.exit_code)
```

**Benefits:**
- Centralized error logic (testable!)
- Automatic severity classification
- Consistent exit codes
- Easy to mock for testing

---

## Testing Strategy

### Unit Tests

**Test ERROR_HELP Coverage:**
```python
def test_error_help_completeness():
    """Verify all error types have helpful suggestions."""
    required_types = [
        'rate_limit',
        'timeout',
        'not_found',
        'server_error',
        'connection_error',
        'invalid_json',
        'generic',
    ]

    for error_type in required_types:
        assert error_type in ERROR_HELP
        assert len(ERROR_HELP[error_type]) >= 2  # At least 2 suggestions
```

**Test Error Classification:**
```python
def test_classify_error():
    """Verify errors are classified correctly."""
    from vscode_scanner.utils import classify_error

    # Rate limit
    error = Exception("HTTP Error 429: Rate limit exceeded")
    assert classify_error(error) == 'rate_limit'

    # Timeout
    error = TimeoutError("Request timed out after 30s")
    assert classify_error(error) == 'timeout'

    # Generic
    error = Exception("Something weird happened")
    assert classify_error(error) == 'generic'
```

**Test Error Sanitization:**
```python
def test_sanitize_error_message():
    """Verify sensitive info is removed from errors."""
    from vscode_scanner.utils import sanitize_error_message

    # File paths removed
    error = "File not found: /Users/john/secret/api_keys.txt"
    sanitized = sanitize_error_message(error)
    assert "/Users/john" not in sanitized
    assert "api_keys.txt" not in sanitized

    # API keys redacted
    error = "Auth failed: key=sk_live_abc123def456"
    sanitized = sanitize_error_message(error)
    assert "sk_live_abc123def456" not in sanitized
    assert "<redacted>" in sanitized
```

### Integration Tests

**Test Error Display:**
```python
def test_error_display_consistency():
    """All modules use display_error() for user-facing errors."""
    # Static analysis test - check for:
    # - No print(..., file=sys.stderr) for user messages
    # - All errors route through display.display_error()
    # - No direct console.print() for errors in non-display modules
```

**Test Exit Codes:**
```python
def test_error_exit_codes():
    """Verify correct exit codes for error scenarios."""
    # Success, no vulns → 0
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0

    # Success, vulns found → 1
    # (mock scan with vulnerabilities)
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 1

    # Failure (e.g., network error) → 2
    # (mock network failure)
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 2
```

### Manual Testing

**Error Scenario Checklist:**
- [ ] Trigger rate limit (run many scans quickly)
- [ ] Disconnect network (test connection errors)
- [ ] Use invalid extension ID (test not found)
- [ ] Mock vscan.dev 500 error (test server errors)
- [ ] Test with empty cache (test cache errors)
- [ ] Test with invalid config file (test config errors)
- [ ] Verify error messages are helpful
- [ ] Verify suggestions are actionable
- [ ] Verify no sensitive info in errors

---

## Best Practices

### DO ✅

- **Always sanitize error messages** before displaying to user
- **Provide actionable suggestions** in ERROR_HELP
- **Include command examples** in suggestions when possible
- **Route all user-facing errors** through `display.display_error()`
- **Test error scenarios** with unit and integration tests
- **Use appropriate exit codes** (0, 1, 2)
- **Log full errors** in verbose mode for debugging

### DON'T ❌

- **Don't expose file paths** in error messages
- **Don't show raw exceptions** to end users
- **Don't use scattered print() calls** for errors
- **Don't make users search docs** for common errors
- **Don't use generic messages** like "Something went wrong"
- **Don't ignore errors** - fail fast with clear messages
- **Don't exit with random codes** - stick to 0, 1, 2

---

## References

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Overall architecture
- **[TESTING.md](TESTING.md)** - Testing guidelines
- **[project/ROADMAP.md](../project/ROADMAP.md)** - Error handling improvements
- **[../CLAUDE.md](../CLAUDE.md)** - Development guidance

---

**Document Version:** 1.0
**Status:** Current (v3.1.0) + Planned Enhancements
**Next Review:** When ErrorHandler class is implemented (Phase 2)
