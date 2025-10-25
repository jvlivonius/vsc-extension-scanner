#!/usr/bin/env python3
"""
Utilities Module

Shared utilities for logging and common functions.
"""

import sys
import platform
import tempfile
from pathlib import Path as PathLib
from typing import Optional


# Global verbosity flag
_VERBOSE = False


def setup_logging(verbose: bool = False):
    """
    Setup logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    global _VERBOSE
    _VERBOSE = verbose


def log(message: str, level: str = "INFO", newline: bool = True, force: bool = False):
    """
    Log message to stderr with simplified logic.

    Args:
        message: Message to log
        level: Log level (INFO, SUCCESS, WARNING, ERROR)
        newline: Whether to print newline after message
        force: Force printing even if not verbose (for important messages)
    """
    # Determine if message should be printed
    should_print = (level in ("ERROR", "WARNING")) or force or _VERBOSE

    if not should_print:
        return

    # Map log levels to prefixes
    prefixes = {
        "ERROR": "[ERROR]",
        "WARNING": "[WARNING]",
        "SUCCESS": "[✓]",
        "INFO": ""
    }

    prefix = prefixes.get(level, f"[{level}]")

    # Format and print message
    output = f"{prefix} {message}".strip() if prefix else message
    end = '\n' if newline else ''
    print(output, file=sys.stderr, end=end, flush=True)


def get_restricted_paths():
    """
    Get list of restricted system paths based on platform.

    Enhanced in v3.5.1 with additional critical system paths.

    Returns:
        List of restricted path prefixes for the current platform
    """
    system = platform.system()

    if system == "Windows":
        # Windows system directories
        return [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\ProgramData",
            "C:\\System32",
            "C:\\$",  # System volume information
        ]
    elif system == "Darwin":  # macOS
        # macOS system directories
        return [
            "/etc", "/sys", "/boot", "/dev", "/proc", "/var", "/root",
            "/System", "/Library/System"
        ]
    else:  # Linux and other Unix-like
        # Unix/Linux system directories
        return ["/etc", "/sys", "/boot", "/dev", "/proc", "/var", "/root"]


def is_temp_directory(path_str: str) -> bool:
    """
    Check if path is within a legitimate temporary directory.

    Args:
        path_str: Path to check

    Returns:
        True if path is within system temp directory, False otherwise
    """
    try:
        path = PathLib(path_str).resolve()
        temp_dir = PathLib(tempfile.gettempdir()).resolve()
        path.relative_to(temp_dir)
        return True
    except (ValueError, OSError):
        return False


def is_restricted_path(path_str: str) -> bool:
    """
    Check if path is in a restricted system directory (cross-platform).

    Args:
        path_str: Path to check

    Returns:
        True if path is restricted, False otherwise
    """
    try:
        path = PathLib(path_str).resolve()
        restricted = get_restricted_paths()

        # Check if path starts with any restricted path
        for restricted_path in restricted:
            try:
                restricted_resolved = PathLib(restricted_path).resolve()
                path.relative_to(restricted_resolved)
                # Path is under restricted directory
                return True
            except ValueError:
                # Not under this restricted path, continue checking
                continue

        return False
    except (ValueError, OSError):
        # If we can't resolve the path, consider it restricted for safety
        return True


def validate_path(path: str, allow_absolute: bool = True, path_type: str = "path") -> bool:
    """
    Validate that a path doesn't contain dangerous patterns.

    Enhanced in v3.5.1 with:
    - URL encoding detection (prevents %2e%2e%2f traversal)
    - Shell variable expansion (~/, $HOME/, etc.)
    - Critical system path blocking
    - Helpful error messages via ValueError

    Args:
        path: Path to validate (supports shell expansion like ~/, $HOME/)
        allow_absolute: Whether to allow absolute paths (default: True)
        path_type: Type of path for error messages (e.g., "output", "cache")

    Raises:
        ValueError: If path contains dangerous patterns or resolves to restricted location

    Returns:
        True if path is valid (for backward compatibility with existing code)

    Examples:
        >>> validate_path("~/Documents/results.json")  # OK: expands to home
        True
        >>> validate_path("/etc/passwd")  # Raises: system directory
        ValueError: Access to system directories not allowed
        >>> validate_path("%2e%2e%2f")  # Raises: URL encoding
        ValueError: URL-encoded paths are not allowed
    """
    import os

    if not path:
        raise ValueError(f"{path_type.capitalize()} path cannot be empty")

    # Block URL-encoded paths (security: prevent encoded traversal like %2e%2e%2f)
    if '%' in path:
        raise ValueError(
            f"URL-encoded paths are not allowed. "
            f"Found '%' character in {path_type} path: {path}"
        )

    # Block dangerous characters that enable command injection
    dangerous_chars = ['\0', '|', ';', '`', '\n', '\r']
    for char in dangerous_chars:
        if char in path:
            raise ValueError(
                f"{path_type.capitalize()} path contains dangerous character: {repr(char)}. "
                f"Characters like null bytes, pipes, and backticks are not allowed."
            )

    # Block parent directory traversal attempts
    if '..' in path:
        raise ValueError(
            f"Parent directory traversal (..) not allowed in {path_type} path: {path}"
        )

    # Expand shell variables and user home directory for validation
    # This ensures we check the actual target path, not the unexpanded form
    # Examples: ~/docs -> /home/user/docs, $HOME/data -> /home/user/data
    try:
        expanded_path = os.path.expandvars(os.path.expanduser(path))
    except Exception as e:
        raise ValueError(f"Failed to expand {path_type} path '{path}': {str(e)}")

    # Validate it's a valid path format
    try:
        p = PathLib(expanded_path)

        # Check if expanded path resolves to a critical system directory
        if is_restricted_path(str(p)):
            # Allow temp directories (legitimate use case for output files)
            if not is_temp_directory(str(p)):
                raise ValueError(
                    f"Access to system directories not allowed. "
                    f"{path_type.capitalize()} path resolves to restricted location: {p}"
                )

        # For absolute paths, warn user but allow (per approved plan)
        if allow_absolute and p.is_absolute():
            log(f"Using absolute path for {path_type}: {p}", "WARNING")

        return True

    except ValueError:
        # Re-raise our own ValueError messages unchanged
        raise
    except (OSError, Exception) as e:
        raise ValueError(f"Invalid {path_type} path format '{path}': {str(e)}")


def sanitize_string(text: Optional[str], max_length: int = 500) -> str:
    """
    Sanitize a string for safe inclusion in CLI output.

    Enhanced in v3.5.1 to prevent terminal injection and control character attacks.
    Removes ANSI escape codes, control characters, and other potentially dangerous sequences.

    Args:
        text: Text to sanitize
        max_length: Maximum length (default: 500)

    Returns:
        Sanitized string safe for terminal output

    Examples:
        >>> sanitize_string("normal text")
        'normal text'
        >>> sanitize_string("\\x1b[31mred text\\x1b[0m")  # ANSI color codes stripped
        'red text'
        >>> sanitize_string("text\\x00with\\x07nulls")  # Control chars removed
        'textwithnulls'
    """
    if text is None:
        return ""

    # Convert to string if not already
    text = str(text)

    # Remove ANSI escape sequences (terminal injection prevention)
    # Pattern: ESC[ followed by any characters and a letter (CSI sequences)
    # Also removes other ESC sequences (OSC, etc.)
    import re
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)  # CSI sequences (colors, cursor movement)
    text = re.sub(r'\x1b\][^\x07]*\x07', '', text)  # OSC sequences (window title, etc.)
    text = re.sub(r'\x1b[^[]', '', text)  # Other ESC sequences

    # Remove dangerous control characters
    # Keep: \n (newline), \t (tab), \r (carriage return) - these are safe for display
    # Remove: \x00 (null), \x07 (bell), \x08 (backspace), \x7f (delete), etc.
    dangerous_control_chars = [
        '\x00',  # Null byte
        '\x07',  # Bell (can be annoying/used for timing attacks)
        '\x08',  # Backspace (terminal manipulation)
        '\x0b',  # Vertical tab
        '\x0c',  # Form feed
        '\x1b',  # Escape (if any remain after regex)
        '\x7f',  # Delete
    ]

    for char in dangerous_control_chars:
        text = text.replace(char, '')

    # Remove any remaining control characters except \n, \t, \r
    # Control characters are 0x00-0x1F and 0x7F
    text = ''.join(char for char in text if ord(char) >= 0x20 or char in '\n\t\r')

    # Truncate if too long (prevents DoS via extremely long strings)
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text


def sanitize_error_message(error_msg: str, context: str = "error") -> str:
    """
    Sanitize error messages from external sources (API, exceptions) to prevent
    information disclosure.

    Args:
        error_msg: Raw error message from external source
        context: Context for generic fallback message

    Returns:
        Sanitized, user-friendly error message
    """
    if not error_msg:
        return f"An {context} occurred"

    # Convert to string and limit length
    error_str = str(error_msg)

    # Remove potentially sensitive patterns
    # - File paths (anything with / or \ followed by multiple segments)
    # - Stack traces (lines starting with "  File " or "Traceback")
    # - Internal implementation details
    sanitized = error_str

    # Truncate to reasonable length
    max_length = 150
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    # Remove null bytes and control characters
    sanitized = ''.join(char for char in sanitized if char == '\n' or char >= ' ')
    sanitized = sanitized.replace('\x00', '')

    # If message is too generic or empty after sanitization, use context
    if not sanitized.strip() or sanitized.strip() in ['Unknown error', 'Error', 'Failed']:
        return f"An {context} occurred"

    return sanitized.strip()


def validate_extension_id(ext_id: str) -> bool:
    """
    Validate extension ID format for SQL safety.

    Valid format: publisher.name
    - Both parts contain only alphanumeric, dots, hyphens, underscores
    - Must have exactly one dot separator
    - Both parts must be non-empty

    Args:
        ext_id: Extension ID to validate

    Returns:
        bool: True if valid format, False otherwise

    Examples:
        >>> validate_extension_id("ms-python.python")
        True
        >>> validate_extension_id("GitHub.copilot")
        True
        >>> validate_extension_id("'; DROP TABLE")
        False
        >>> validate_extension_id("../../../etc/passwd")
        False
    """
    import re

    if not ext_id or not isinstance(ext_id, str):
        return False

    # Pattern: publisher.name where both parts are alphanumeric + dots/hyphens/underscores
    pattern = r'^[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$'

    if not re.match(pattern, ext_id):
        return False

    # Ensure exactly one dot (publisher.name format)
    parts = ext_id.split('.')
    if len(parts) != 2:
        return False

    # Both parts must be non-empty
    if not parts[0] or not parts[1]:
        return False

    return True


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def truncate_text(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def _safe_chmod(path: PathLib, mode: int):
    """
    Set file permissions (Unix-like systems only).

    Internal helper function used by safe_mkdir, safe_touch, and safe_chmod.
    On Windows, this is a no-op (Windows uses ACLs).

    Args:
        path: Path object to modify
        mode: Unix permission mode
    """
    if platform.system() != "Windows":
        try:
            path.chmod(mode)
        except (OSError, NotImplementedError):
            # Permissions not supported, graceful fallback
            pass


def safe_mkdir(path: PathLib, mode: int = 0o755):
    """
    Create directory with permissions (cross-platform).

    On Unix-like systems, sets the specified mode.
    On Windows, mode parameter is ignored (Windows uses ACLs).

    Args:
        path: Path object to create
        mode: Unix permission mode (default: 0o755)
    """
    path.mkdir(parents=True, exist_ok=True)
    _safe_chmod(path, mode)


def safe_touch(path: PathLib, mode: int = 0o600):
    """
    Create file with permissions (cross-platform).

    On Unix-like systems, sets the specified mode.
    On Windows, mode parameter is ignored (Windows uses ACLs).

    Args:
        path: Path object to create
        mode: Unix permission mode (default: 0o600)
    """
    path.touch(exist_ok=True)
    _safe_chmod(path, mode)


def safe_chmod(path: PathLib, mode: int):
    """
    Change file/directory permissions (cross-platform).

    On Unix-like systems, sets the specified mode.
    On Windows, this is a no-op (Windows uses ACLs).

    Args:
        path: Path object to modify
        mode: Unix permission mode
    """
    _safe_chmod(path, mode)


# Error help messages with recovery suggestions
ERROR_HELP = {
    "rate_limit": {
        "message": "vscan.dev rate limit reached.",
        "suggestions": [
            "Wait a few minutes before trying again",
            "Use --delay to slow down requests (e.g., --delay 3.0)",
            "The service may be experiencing high traffic"
        ]
    },
    "timeout": {
        "message": "Request timed out.",
        "suggestions": [
            "Try --max-retries 5 for more retry attempts",
            "Use --retry-delay 3.0 for longer backoff delays",
            "The extension may be large and take longer to analyze",
            "Check your internet connection"
        ]
    },
    "not_found": {
        "message": "Extension not found on vscan.dev.",
        "suggestions": [
            "The extension may be too new or not yet indexed",
            "Verify the extension ID is correct",
            "Try scanning again later"
        ]
    },
    "network": {
        "message": "Network error occurred.",
        "suggestions": [
            "Check your internet connection",
            "Verify firewall settings allow HTTPS to vscan.dev",
            "Try again in a few moments"
        ]
    },
    "permission": {
        "message": "Permission denied.",
        "suggestions": [
            "Check file/directory permissions",
            "Ensure you have write access to the output location",
            "Try running with appropriate permissions"
        ]
    },
    "invalid_json": {
        "message": "Invalid JSON in extension file.",
        "suggestions": [
            "The extension may be corrupted",
            "Try reinstalling the extension",
            "The package.json file may be malformed"
        ]
    },
    "no_extensions": {
        "message": "VS Code extensions directory not found.",
        "suggestions": [
            "Ensure VS Code is installed",
            "Use --extensions-dir to specify custom location",
            "Check that VS Code extensions are installed"
        ]
    }
}


def show_error_help(error_type: str):
    """
    Display helpful error message with recovery suggestions.

    Args:
        error_type: Type of error (rate_limit, timeout, network, etc.)
    """
    if error_type not in ERROR_HELP:
        return

    help_info = ERROR_HELP[error_type]
    log("", "INFO", force=True)
    log(f"💡 {help_info['message']}", "INFO", force=True)

    # Show all suggestions
    log("", "INFO", force=True)
    log("Suggestions:", "INFO", force=True)
    for suggestion in help_info['suggestions']:
        log(f"  • {suggestion}", "INFO", force=True)


def get_error_type(error_message: str) -> str:
    """
    Determine error type from error message.

    Args:
        error_message: Error message string

    Returns:
        Error type string for ERROR_HELP lookup
    """
    error_lower = error_message.lower()

    if "rate limit" in error_lower or "429" in error_message:
        return "rate_limit"
    elif "timed out" in error_lower or "timeout" in error_lower:
        return "timeout"
    elif "not found" in error_lower or "404" in error_message:
        return "not_found"
    elif "network" in error_lower or "connection" in error_lower:
        return "network"
    elif "permission" in error_lower or "denied" in error_lower:
        return "permission"
    elif "json" in error_lower:
        return "invalid_json"
    elif "directory not found" in error_lower:
        return "no_extensions"
    else:
        return "unknown"


def main():
    """Test the utils module."""
    setup_logging(verbose=True)

    log("Testing INFO level", "INFO")
    log("Testing SUCCESS level", "SUCCESS")
    log("Testing WARNING level", "WARNING")
    log("Testing ERROR level", "ERROR")

    print(f"\nDuration formatting:")
    print(f"  45.5s -> {format_duration(45.5)}")
    print(f"  95.0s -> {format_duration(95.0)}")
    print(f"  3665.0s -> {format_duration(3665.0)}")

    print(f"\nPath validation:")
    try:
        result = validate_path('/home/user/.vscode')
        print(f"  /home/user/.vscode -> {result}")
    except ValueError as e:
        print(f"  /home/user/.vscode -> ERROR: {e}")

    try:
        result = validate_path('../../../etc/passwd')
        print(f"  ../../../etc/passwd -> {result}")
    except ValueError as e:
        print(f"  ../../../etc/passwd -> ERROR: {e}")

    print(f"\nText truncation:")
    long_text = "This is a very long text that should be truncated to a reasonable length for display purposes"
    print(f"  Original: {long_text}")
    print(f"  Truncated: {truncate_text(long_text, 50)}")


if __name__ == "__main__":
    main()
