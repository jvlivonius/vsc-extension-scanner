#!/usr/bin/env python3
"""
Utilities Module

Shared utilities for logging and common functions.
"""

import sys
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
    Log message to stderr.

    Args:
        message: Message to log
        level: Log level (INFO, SUCCESS, WARNING, ERROR)
        newline: Whether to print newline after message
        force: Force printing even if not verbose (for important messages)
    """
    # Always print ERROR, WARNING, and forced messages
    if level in ("ERROR", "WARNING") or force:
        end = '\n' if newline else ''
        if level in ("ERROR", "WARNING"):
            print(f"[{level}] {message}", file=sys.stderr, end=end, flush=True)
        else:
            # For forced INFO/SUCCESS messages, don't add level prefix for ERROR/WARNING
            if level == "SUCCESS":
                print(f"[✓] {message}", file=sys.stderr, end=end, flush=True)
            else:
                print(message, file=sys.stderr, end=end, flush=True)
        return

    # Only print INFO and SUCCESS if verbose is enabled
    if not _VERBOSE:
        return

    # Format based on level
    if level == "SUCCESS":
        prefix = "[✓]"
    elif level == "INFO":
        prefix = ""
    else:
        prefix = f"[{level}]"

    # Print to stderr (stdout is reserved for JSON output)
    end = '\n' if newline else ''
    if prefix:
        print(f"{prefix} {message}", file=sys.stderr, end=end, flush=True)
    else:
        print(message, file=sys.stderr, end=end, flush=True)


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


def sanitize_string(text: Optional[str], max_length: int = 500) -> str:
    """
    Sanitize a string for safe inclusion in output.

    Args:
        text: Text to sanitize
        max_length: Maximum length

    Returns:
        Sanitized string
    """
    if text is None:
        return ""

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."

    # Remove null bytes
    text = text.replace('\x00', '')

    return text


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
    print(f"  /home/user/.vscode -> {validate_path('/home/user/.vscode')}")
    print(f"  ../../../etc/passwd -> {validate_path('../../../etc/passwd')}")

    print(f"\nText truncation:")
    long_text = "This is a very long text that should be truncated to a reasonable length for display purposes"
    print(f"  Original: {long_text}")
    print(f"  Truncated: {truncate_text(long_text, 50)}")


if __name__ == "__main__":
    main()
