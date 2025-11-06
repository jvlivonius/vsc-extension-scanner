#!/usr/bin/env python3
"""
Shared utilities for test scripts.

Provides common functionality for test runners, pre-release checks, and smoke tests.
"""

import sys


# ==============================================================================
# Exit Codes
# ==============================================================================

EXIT_SUCCESS = 0  # All tests/validations passed
EXIT_FAILURE = 1  # Some tests/validations failed
EXIT_NOT_FOUND = 2  # No tests found or file not found
EXIT_ERROR = 3  # Execution error


# ==============================================================================
# Color Support
# ==============================================================================


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @classmethod
    def disable(cls):
        """Disable colors (for non-TTY output)."""
        cls.RESET = ""
        cls.BOLD = ""
        cls.RED = ""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.BLUE = ""
        cls.MAGENTA = ""
        cls.CYAN = ""
        cls.GRAY = ""


# Auto-disable colors if not a TTY
if not sys.stdout.isatty():
    Colors.disable()
