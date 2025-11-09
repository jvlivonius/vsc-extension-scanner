# Error Handling Guide

**Purpose:** How to handle errors, display messages, and implement error patterns
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** Developers

---


## Table of Contents

1. [Philosophy](#philosophy)
2. [Error Handling Architecture](#error-handling-architecture)
3. [ERROR_HELP System](#error_help-system)
4. [Error Display Flow](#error-display-flow)
5. [Display Function Selection Guide](#display-function-selection-guide) **← NEW**
6. [Error Types](#error-types)
7. [Implementation Guide](#implementation-guide)
8. [Planned Enhancements](#planned-enhancements)
9. [Testing Strategy](#testing-strategy)

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

### Architecture Overview

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
    "error_type": {
        "message": "Brief description of what happened",
        "suggestions": [
            "Suggestion 1",
            "Suggestion 2",
            "Suggestion 3 (optional command example)",
        ]
    },
    # ...
}
```

### Complete Error Types

#### 1. Rate Limiting (429)

**Triggers:**
- HTTP 429 response
- "rate limit" in error message
- vscan.dev throttling

**Structure:**
```python
"rate_limit": {
    "message": "vscan.dev rate limit reached.",
    "suggestions": [
        "Wait a few minutes before trying again",
        "Use --delay to slow down requests (e.g., --delay 3.0)",
        "The service may be experiencing high traffic"
    ]
}
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
    "The request to vscan.dev timed out",
    f"(Current timeout: {constants.API_TIMEOUT_SECONDS} seconds)",
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
    "If problem persists, report at: https://github.com/jvlivonius/vsc-extension-scanner/issues",
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
# Timeout value: see constants.API_TIMEOUT_SECONDS
try:
    response = urllib.request.urlopen(request, timeout=API_TIMEOUT_SECONDS)
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

## Retry Mechanism

### Overview

The retry mechanism (v2.2+) handles transient API failures gracefully through intelligent retry with exponential backoff. The system distinguishes between retryable transient errors and permanent failures to avoid unnecessary API calls.

**Design Goals:**
- Automatically recover from transient failures (network timeouts, rate limits, temporary server errors)
- Fail fast on permanent errors (authentication failures, invalid requests, not found)
- Respect server rate limit signals (Retry-After headers)
- Prevent DoS through backoff ceiling and jitter
- Maintain observability through retry statistics

### Error Classification

Not all errors should trigger retries. The system classifies errors into **retryable** (transient) and **non-retryable** (permanent) categories.

**Retryable Errors** (Transient - safe to retry):

| HTTP Code | Error Type | Reason | Max Retries |
|-----------|------------|--------|-------------|
| 408 | Request Timeout | Network/server timeout, may succeed on retry | 3 |
| 429 | Too Many Requests | Rate limit hit, server explicitly allows retry | 3 |
| 502 | Bad Gateway | Temporary proxy/gateway failure | 3 |
| 503 | Service Unavailable | Server temporarily overloaded | 3 |
| 504 | Gateway Timeout | Upstream timeout, may resolve | 3 |
| - | ConnectionError | Network unavailable, may reconnect | 3 |
| - | TimeoutError | Request timed out before completion | 3 |

**Non-Retryable Errors** (Permanent - fail immediately):

| HTTP Code | Error Type | Reason | Action |
|-----------|------------|--------|--------|
| 400 | Bad Request | Invalid request format, won't change | Fail fast |
| 401 | Unauthorized | Authentication failed | Fail fast |
| 403 | Forbidden | Access denied | Fail fast |
| 404 | Not Found | Resource doesn't exist | Fail fast |
| 422 | Unprocessable Entity | Validation failed | Fail fast |
| 500 | Internal Server Error | Server-side bug, unlikely to resolve | Fail fast |

**Implementation:**
```python
def _is_retryable_error(http_code: int, error_type: str) -> bool:
    """Classify errors as retryable or permanent."""
    retryable_codes = {408, 429, 502, 503, 504}
    retryable_exceptions = {'ConnectionError', 'TimeoutError'}

    return http_code in retryable_codes or error_type in retryable_exceptions
```

### Exponential Backoff with Jitter

**Algorithm:** The retry mechanism uses exponential backoff with jitter to avoid thundering herd problems and reduce server load.

**Formula:**
```
delay = min(base_delay * (2 ^ retry_count) * (0.8 + random(0, 0.4)), MAX_BACKOFF_DELAY)
```

Where:
- **base_delay** = Configurable base delay (see `constants.DEFAULT_RETRY_BASE_DELAY`)
- **retry_count** = Number of retries attempted (0-indexed)
- **jitter** = Random factor between 0.8 and 1.2 (±20%)
- **MAX_BACKOFF_DELAY** = Maximum delay ceiling (see `constants.MAX_BACKOFF_DELAY`, prevents DoS)

**Example Backoff Progression:**

| Retry | Base Calculation | With Jitter Range | Actual Range |
|-------|------------------|-------------------|--------------|
| 0 | 2.0 × 2^0 = 2.0s | 2.0 × [0.8, 1.2] | 1.6s - 2.4s |
| 1 | 2.0 × 2^1 = 4.0s | 4.0 × [0.8, 1.2] | 3.2s - 4.8s |
| 2 | 2.0 × 2^2 = 8.0s | 8.0 × [0.8, 1.2] | 6.4s - 9.6s |
| 3 | 2.0 × 2^3 = 16.0s | min(16.0 × [0.8, 1.2], 30) | 12.8s - 19.2s |
| 4 | 2.0 × 2^4 = 32.0s | min(32.0 × [0.8, 1.2], 30) | 24.0s - 30.0s |
| 5+ | Capped at 30.0s | min(*, 30) | 24.0s - 30.0s |

**Implementation:**
```python
import random

def _calculate_backoff_delay(retry_count: int, base_delay: float = 2.0) -> float:
    """Calculate exponential backoff delay with jitter."""
    delay = base_delay * (2 ** retry_count)
    jitter = random.uniform(0.8, 1.2)  # ±20% randomization

    return min(delay * jitter, MAX_BACKOFF_DELAY)  # Cap at 30s
```

**Why Jitter?**
- Prevents synchronized retry storms (thundering herd)
- Distributes load across time
- Reduces server spike when multiple clients retry simultaneously

**Why 30s Ceiling?**
- Prevents excessive wait times for users
- Mitigates DoS risk from malicious Retry-After headers
- Balances recovery time vs user experience

### Retry-After Header Handling

**Server-Specified Delays:** When servers return a `Retry-After` header (typically with 429 or 503 responses), the system honors the server's requested delay while applying the same 30-second ceiling for security.

**Priority:**
1. **Retry-After header present** → Use server-specified delay (with 30s max)
2. **No Retry-After header** → Use exponential backoff algorithm

**Implementation:**
```python
def _get_retry_delay(response, retry_count: int, base_delay: float = 2.0) -> float:
    """Get retry delay honoring Retry-After or using backoff."""
    retry_after = response.getheader('Retry-After')

    if retry_after:
        try:
            # Honor server's requested delay (capped at 30s for security)
            delay = float(retry_after)
            return min(delay, MAX_BACKOFF_DELAY)
        except ValueError:
            pass  # Invalid header, fall back to backoff

    # Use exponential backoff
    return _calculate_backoff_delay(retry_count, base_delay)
```

**Security Note:** Malicious servers could send `Retry-After: 9999` to cause denial of service. The 30-second ceiling prevents this attack vector.

### Retry Statistics Tracking

**Observability:** The system tracks detailed retry statistics for debugging and monitoring. Statistics are displayed in verbose mode and always included in JSON output.

**Tracked Metrics:**

| Metric | Description | Usage |
|--------|-------------|-------|
| `total_retries` | Total retry attempts across all requests | Measure retry frequency |
| `successful_retries` | Retries that eventually succeeded | Success rate calculation |
| `failed_after_retry` | Requests that failed despite retries | Identify persistent issues |
| `rate_limit_hits` | Times 429 status encountered | Monitor rate limiting |
| `server_error_retries` | Times 502/503/504 encountered | Server health indicator |
| `timeout_retries` | Times request timed out | Network quality indicator |
| `retry_delays_total` | Sum of all retry wait times | User impact measurement |

**Implementation:**
```python
class RetryStats:
    """Thread-safe retry statistics collection."""

    def __init__(self):
        self._lock = threading.Lock()
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_after_retry = 0
        self.rate_limit_hits = 0
        self.server_error_retries = 0
        self.timeout_retries = 0
        self.retry_delays_total = 0.0

    def record_retry(self, error_type: str, delay: float, success: bool):
        """Thread-safe retry recording."""
        with self._lock:
            self.total_retries += 1
            self.retry_delays_total += delay

            if success:
                self.successful_retries += 1
            else:
                self.failed_after_retry += 1

            if error_type == '429':
                self.rate_limit_hits += 1
            elif error_type in {'502', '503', '504'}:
                self.server_error_retries += 1
            elif error_type == 'timeout':
                self.timeout_retries += 1
```

**Display:**
```bash
# Default mode - hidden (clean output)
$ vscan scan
Scanned 66 extensions - 5 vulnerabilities found
Cache hit rate: 71.4%

# Verbose mode - shows retry statistics
$ vscan scan --verbose
Scanned 66 extensions - 5 vulnerabilities found
Cache hit rate: 71.4%

Retry Statistics:
  Total retries: 5
  Successful: 4 (80.0%)
  Failed after retry: 1 (20.0%)
  Rate limit hits: 2
  Server errors: 3
  Total retry delay: 18.4s
```

### Configuration Best Practices

**Configurable Parameters:**

| Parameter | Default | Range | Configuration Path | Purpose |
|-----------|---------|-------|-------------------|---------|
| `max_retries` | 3 | 0-5 | `scan.max_retries` | Balance reliability vs speed |
| `retry_delay` | 2.0s | 0.5-10.0s | `scan.retry_delay` | Base backoff delay |
| `request_timeout` | 30s | 10-60s | `scan.timeout` | When to give up on single request |

**Configuration File (`~/.vscanrc`):**
```ini
[scan]
max_retries = 3        # 0 disables retry, 5 maximum
retry_delay = 2.0      # Base delay in seconds
timeout = 30           # Request timeout in seconds
```

**CLI Override:**
```bash
# Disable retries (fail fast mode)
vscan scan --max-retries 0

# Aggressive retry (high reliability mode)
vscan scan --max-retries 5 --retry-delay 3.0

# Quick scan (minimal retry)
vscan scan --max-retries 1 --retry-delay 1.0
```

**Recommendations:**

**Default (3 retries):** Recommended for most users
- ✅ Handles transient failures gracefully
- ✅ Balances reliability and speed
- ✅ Validated in production

**Aggressive (5 retries):** For critical scans or poor network conditions
- ✅ Maximum reliability
- ⚠️ Slower on failures
- Use when: Unstable network, CI/CD pipelines

**Minimal (1 retry):** For fast scans or excellent network conditions
- ✅ Faster on failures
- ⚠️ May miss transient errors
- Use when: Exploring, local network, time-sensitive

**None (0 retries):** For debugging only
- ✅ Immediate failure visibility
- ❌ No transient error recovery
- Use when: Testing error handling, debugging

### Integration with Scan Workflow

**Retry Flow in Scanner:**

```
Extension Scan Request
   │
   ├─> API Client: scan_extension_with_retry()
   │      │
   │      ├─> Attempt 1: POST /api/extensions/analyze
   │      │      ├─> Success → Return result
   │      │      └─> Failure → Check if retryable
   │      │             ├─> Non-retryable → Fail fast
   │      │             └─> Retryable → Continue
   │      │
   │      ├─> Wait: Calculate backoff delay (or use Retry-After)
   │      │
   │      ├─> Attempt 2: Retry request
   │      │      ├─> Success → Update stats (successful_retry)
   │      │      └─> Failure → Check if retryable
   │      │
   │      ├─> Wait: Exponential backoff (doubled)
   │      │
   │      ├─> Attempt 3: Final retry
   │      │      ├─> Success → Update stats (successful_retry)
   │      │      └─> Failure → Give up
   │      │
   │      └─> Update stats (failed_after_retry)
   │      └─> Return error result
   │
   └─> Scanner: Log failure, continue to next extension
```

**Key Behaviors:**
- ✅ Individual extension failures don't stop entire scan
- ✅ Retry statistics aggregated across all extensions
- ✅ Cache writes happen after successful retry
- ✅ Failed extensions reported in scan summary

---

## Display Function Selection Guide

### When to Use display_error()

**Purpose:** Fatal errors that prevent the operation from completing

**Use when:**
- Operation cannot continue (exit code 2)
- User action is blocked
- Data corruption or invalid state detected
- Configuration errors that prevent execution
- Invalid user input that stops the command

**Examples from codebase:**
```python
# Cache clearing failure
display_error(f"Error clearing cache: {e}", use_rich=True)
raise typer.Exit(2)

# Invalid output path
display_error("Invalid output path", use_rich=True)
raise ValueError("Invalid output path")

# Cache database corruption
display_error(f"Failed to handle corrupted database: {sanitized_error}")
display_info("Cache functionality may be impaired")
```

**Characteristics:**
- Always followed by program termination or exception
- Requires user intervention to fix
- Blocks the requested operation
- Exit code: 2 (failure)

### When to Use display_warning()

**Purpose:** Non-fatal issues that allow operation to continue

**Use when:**
- Operation can proceed with degraded functionality
- Optional features are unavailable
- Data quality issues that don't block execution
- Missing optional configuration
- Informational issues that user should know about

**Examples from codebase:**
```python
# Config file not found (can use defaults)
display_warning(f"No configuration file found at {config_path}", use_rich=True)
display_info("Run 'vscan config init' to create one", use_rich=True)
# Continue execution with defaults...

# Invalid extension IDs filtered out
display_warning(f"Filtered out {filtered_count} invalid extension IDs")
# Continue scanning remaining valid extensions...

# No extensions match filters
display_warning("No extensions match the specified filters:", use_rich=True)
# Still return success (exit 0), just nothing to report
```

**Characteristics:**
- Program continues execution after warning
- User awareness is helpful but not critical
- Graceful degradation or fallback behavior
- Exit code: 0 or 1 (depending on scan results)

### When to Use log()

**Purpose:** Internal logging for debugging and verbose output

**Use when:**
- Verbose mode is enabled (`--verbose`)
- Debugging information needed for troubleshooting
- Progress updates for long operations
- Internal state changes
- Performance metrics

**Examples from codebase:**
```python
# Verbose logging in utils.py
log(message, level="INFO")  # Only prints if _VERBOSE is True

# Error logging with sanitization
error_msg = sanitize_string(str(e), max_length=200)
log(f"Error discovering extensions: {error_msg}", "ERROR")
```

**Characteristics:**
- Respects global verbosity flag
- Not visible in normal operation
- Technical details for developers/debugging
- Can be safely ignored by end users
- Controlled by `setup_logging(verbose=True/False)`

### Decision Tree

```
Is this a fatal error that stops execution?
├─ Yes → display_error() + raise/exit
└─ No → Is this an issue user should be aware of?
    ├─ Yes → display_warning() + continue
    └─ No → Is verbose mode enabled?
        ├─ Yes → log() at appropriate level
        └─ No → (silent, no output)
```

### Best Practices

**DO ✅**
- Use display_error() for all blocking errors
- Use display_warning() for recoverable issues
- Use log() for verbose/debug information
- Sanitize all error messages before display
- Provide actionable suggestions with errors
- Route all display through display.py functions

**DON'T ❌**
- Don't use log() for user-facing errors
- Don't use display_error() for warnings
- Don't mix print() with display functions
- Don't show stack traces in display_error()
- Don't display sensitive info in any function
- Don't skip sanitization of external data

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

**Exit Code Convention:** vscan uses three exit codes following Unix conventions

| Code | Meaning | When to Use | Examples |
|------|---------|-------------|----------|
| 0 | Success, no issues | Operation completed successfully, no vulnerabilities found | All scans succeeded, no vulnerabilities detected |
| 1 | Success with findings | Operation completed successfully, vulnerabilities found | Scan completed, found high-risk extensions |
| 2 | Failure | Operation failed due to errors | Network error, invalid config, permission denied |

#### Detailed Exit Code Rules

**Exit Code 0 (Success, Clean):**
```python
# Scan completed, no vulnerabilities found
if vulnerabilities_found == 0 and scan_completed:
    raise typer.Exit(0)

# Cache stats displayed successfully
# Config shown successfully
# Report generated without issues
```

**Exit Code 1 (Success, Issues Found):**
```python
# Scan completed, found vulnerabilities
if vulnerabilities_found > 0 and scan_completed:
    raise typer.Exit(1)

# Useful for CI/CD pipelines to detect issues
# Operation succeeded, but user should take action
```

**Exit Code 2 (Failure):**
```python
# Fatal error - scan could not complete
display_error("Network error: Could not connect to vscan.dev")
raise typer.Exit(2)

# Invalid user input
display_error("Invalid output path")
raise typer.Exit(2)

# Missing required resources
display_error("Cache is empty. Run 'vscan scan' first")
raise typer.Exit(2)

# Configuration error
display_error(f"Invalid configuration: {error}")
raise typer.Exit(2)
```

#### CI/CD Integration Examples

**GitHub Actions:**
```yaml
- name: Scan extensions
  run: vscan scan
  # Exit 0: Pass (no vulnerabilities)
  # Exit 1: Fail (vulnerabilities found) ← Fails the build
  # Exit 2: Error (scan failed) ← Fails the build
```

**Shell Scripts:**
```bash
vscan scan
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ No vulnerabilities found"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "⚠ Vulnerabilities detected!"
    exit 1  # Fail the build
elif [ $EXIT_CODE -eq 2 ]; then
    echo "✗ Scan failed"
    exit 2  # Fail the build
fi
```

#### Exit Code Best Practices

**DO ✅**
- Use exit code 0 for successful scans with no findings
- Use exit code 1 for successful scans with findings
- Use exit code 2 for all operational failures
- Always exit with one of these three codes
- Document exit codes in command help text

**DON'T ❌**
- Don't use exit codes outside 0-2 range
- Don't exit 0 when scan failed (misleading success)
- Don't exit 2 for successful scans with findings
- Don't use random or undocumented exit codes
- Don't exit without displaying error context

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

**Concept:** Centralize error handling with `ErrorHandler` class and `ErrorContext` dataclass for better testability and consistency.

**Key Benefits:**
- Single source of truth for error logic
- Automatic error classification and severity mapping
- Consistent exit codes and error UX
- Easy to mock for testing

**Status:** See project roadmap for implementation timeline

---

## Testing Strategy

**Test Files:**
- `tests/test_error_handling.py` - Error classification, sanitization, EXIT codes
- `tests/test_display.py` - Error display consistency
- `tests/test_security.py` - Error message sanitization (CWE-209)

**Key Test Areas:**
1. **ERROR_HELP Coverage** - All error types have 2+ helpful suggestions
2. **Error Classification** - Correct mapping of exceptions to error types (rate_limit, timeout, server_error, etc.)
3. **Error Sanitization** - File paths and API keys removed from messages (see SECURITY.md)
4. **Exit Codes** - Correct codes for success (0), vulnerabilities found (1), failure (2)
5. **Display Consistency** - All errors route through `display_error()`, no direct print() calls

**Manual Testing Checklist:**
- Trigger transient errors (rate limit, network disconnect, server 500)
- Test permanent errors (invalid extension ID, auth failure)
- Verify error messages helpful and suggestions actionable
- Confirm no sensitive info in error output

See [TESTING.md](TESTING.md) and [TESTING_SECURITY.md](testing/TESTING_SECURITY.md) for complete testing patterns

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

**Document Type:** Timeless Reference
**Last Updated:** 2025-11-09
**See Also:** [ERROR_CODES.md](ERROR_CODES.md) - Complete error code reference
