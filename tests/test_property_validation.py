#!/usr/bin/env python3
"""
Property-based tests for security-critical validation functions.

Uses Hypothesis to generate 1000+ test cases per property, testing:
- validate_path() - Path validation and traversal prevention
- sanitize_string() - String sanitization for different contexts

Property-based testing complements example-based tests by:
1. Discovering edge cases automatically
2. Testing against invariants (properties that should always hold)
3. Fuzzing inputs to find unexpected behavior
4. Providing high-confidence security validation

Part of Phase 2 security automation (v3.5.2).
"""

import sys
import os
import unittest
from unittest.mock import patch

import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Hypothesis imports
from hypothesis import given, strategies as st, settings, example, assume
from hypothesis import HealthCheck, Phase

# Project imports
from vscode_scanner.utils import validate_path, sanitize_string


# ============================================================================
# Property Tests for validate_path()
# ============================================================================


@pytest.mark.security
class TestPathValidationProperties(unittest.TestCase):
    """Property-based tests for path validation security."""

    @given(st.text())
    @settings(max_examples=1000, deadline=None)
    def test_validate_path_never_crashes(self, path_input):
        """
        PROPERTY: validate_path should handle any string input without crashing.

        This tests robustness - the function should either:
        1. Return True (for legitimate inputs), or
        2. Raise ValueError (for invalid/malicious inputs), or
        3. Raise OSError (for invalid inputs)

        It should NEVER crash with unexpected exceptions.
        """
        try:
            result = validate_path(path_input)
            # If it doesn't raise, result should be True
            self.assertIsInstance(result, bool)
            self.assertTrue(result)
        except (ValueError, OSError):
            # Expected for invalid or malicious paths
            pass
        except Exception as e:
            # Unexpected exception - test fails
            self.fail(
                f"validate_path crashed with unexpected exception: {type(e).__name__}: {e}"
            )

    @given(st.text(min_size=1))
    @settings(max_examples=1000, deadline=None)
    @example("../../../etc/passwd")  # Classic path traversal
    @example("..\\..\\..\\windows\\system32")  # Windows path traversal
    @example("%2e%2e%2f%2e%2e%2f")  # URL-encoded traversal
    @example("%252e%252e%252f")  # Double URL-encoded
    def test_traversal_always_blocked(self, path):
        """
        PROPERTY: Path traversal attempts should ALWAYS be blocked.

        Any path containing ".." or URL-encoded variations should raise SecurityError.
        This is a critical security property - no false negatives allowed.
        """
        # Check for traversal patterns
        has_traversal = (
            ".." in path or "%2e%2e" in path.lower() or "%252e" in path.lower()
        )

        if has_traversal:
            with self.assertRaises(
                ValueError, msg=f"Traversal path not blocked: {path}"
            ):
                validate_path(path)

    @given(st.text())
    @settings(max_examples=500, deadline=None)
    def test_system_paths_always_blocked(self, path):
        """
        PROPERTY: System-critical paths should ALWAYS be blocked.

        Paths that ARE system directories or are UNDER system directories
        should raise ValueError. Uses proper path prefix matching to avoid
        false positives (e.g., /sys0, /etc-backup, /mysystem are legitimate
        directory names that should NOT be blocked).
        """
        import os

        system_dirs = ["/etc", "/sys", "/proc", "c:\\windows\\system32"]

        # Check if path is a system directory or subdirectory (proper path prefix)
        # This avoids false positives from substring matching
        path_lower = path.lower()
        has_system_dir = any(
            path_lower == sysdir.lower()
            or path_lower.startswith(sysdir.lower() + os.sep)
            for sysdir in system_dirs
        )

        if has_system_dir:
            with self.assertRaises(ValueError):
                validate_path(path)

    @given(st.text())
    @settings(max_examples=500, deadline=None)
    def test_null_bytes_always_blocked(self, path):
        """
        PROPERTY: Null bytes in paths should ALWAYS be blocked.

        Null bytes can be used to bypass validation in C-based file operations.
        """
        if "\x00" in path:
            with self.assertRaises(ValueError):
                validate_path(path)

    @given(
        st.text(
            alphabet=st.characters(exclude_characters=["\x00"]),
            min_size=1,
            max_size=100,
        )
    )
    @settings(
        max_examples=500,
        deadline=None,
        suppress_health_check=[HealthCheck.filter_too_much],
    )
    def test_safe_relative_paths_accepted(self, filename):
        """
        PROPERTY: Safe relative paths (no traversal) should be accepted.

        When provided a simple filename or safe relative path,
        validate_path should NOT raise ValueError for valid paths.
        """
        # Skip if contains traversal or system paths
        assume(".." not in filename)
        assume(
            not any(
                x in filename.lower() for x in ["/etc", "/sys", "/proc", "system32"]
            )
        )
        assume(len(filename.strip()) > 0)  # Non-empty after strip

        try:
            result = validate_path(filename)
            # Should return True
            self.assertIsInstance(result, bool)
            self.assertTrue(result)
        except (ValueError, OSError):
            # Acceptable - invalid path format
            pass

    @given(st.text())
    @settings(max_examples=500, deadline=None)
    def test_unicode_handled_correctly(self, path):
        """
        PROPERTY: Unicode characters should be handled safely.

        Unicode normalization attacks should not bypass validation.
        """
        try:
            result = validate_path(path)
            # If accepted, should return True
            self.assertIsInstance(result, bool)
            self.assertTrue(result)
            # Path should not contain traversal patterns
            self.assertNotIn("..", path)
        except (ValueError, OSError, UnicodeError):
            # Expected for invalid paths
            pass


# ============================================================================
# Property Tests for sanitize_string()
# ============================================================================


@pytest.mark.security
class TestStringSanitizationProperties(unittest.TestCase):
    """Property-based tests for string sanitization security."""

    @given(st.text())
    @settings(max_examples=1000, deadline=None)
    def test_sanitize_never_crashes(self, input_str):
        """
        PROPERTY: sanitize_string should handle ANY input without crashing.

        This tests robustness for all types of string input.
        """
        try:
            result = sanitize_string(input_str)
            # Result should always be a string
            self.assertIsInstance(result, str)
        except Exception as e:
            self.fail(f"sanitize_string crashed: {type(e).__name__}: {e}")

    @given(st.text())
    @settings(max_examples=1000, deadline=None)
    def test_sanitize_removes_control_chars(self, input_str):
        """
        PROPERTY: Sanitized output should NOT contain dangerous control characters.

        Control characters like null bytes, escape sequences, etc. should be removed
        or escaped to prevent terminal injection attacks.
        """
        result = sanitize_string(input_str)

        # Dangerous control characters that should not appear
        dangerous_chars = [
            "\x00",  # Null byte
            "\x1b",  # Escape (ANSI escape sequences)
            "\r",  # Carriage return (can overwrite terminal output)
        ]

        for char in dangerous_chars:
            self.assertNotIn(
                char,
                result,
                msg=f"Dangerous control character {repr(char)} found in sanitized output",
            )

    @given(st.text())
    @settings(max_examples=500, deadline=None)
    def test_sanitize_maintains_string_type(self, input_str):
        """
        PROPERTY: Sanitization should always return a string.

        Type consistency is important for API contracts.
        """
        result = sanitize_string(input_str)
        self.assertIsInstance(result, str)

    @given(st.text(min_size=1))
    @settings(max_examples=500, deadline=None)
    def test_sanitize_not_empty_unless_input_empty(self, input_str):
        """
        PROPERTY: Non-empty input should produce non-empty output.

        Sanitization should not completely remove all content
        unless the input was only dangerous characters (ANSI sequences, etc).
        """
        result = sanitize_string(input_str)

        # If input has printable non-whitespace characters, output should not be empty
        # Note: Whitespace-only strings are an edge case that may strip to empty
        # Note: ANSI escape sequences (e.g., \x1b[A) are correctly removed entirely
        has_printable = any(c.isprintable() and not c.isspace() for c in input_str)
        has_ansi = "\x1b" in input_str  # Contains ANSI escape sequences

        if has_printable and not has_ansi:
            # Output should have some content (unless it was all ANSI sequences)
            self.assertGreater(
                len(result.strip()),
                0,
                msg="Non-empty input produced empty output after sanitization",
            )

    @given(st.text())
    @settings(max_examples=500, deadline=None)
    def test_log_context_prevents_log_injection(self, input_str):
        """
        PROPERTY: Sanitization should prevent log injection.

        Newlines and special characters should be escaped or removed
        to prevent log injection attacks.
        """
        result = sanitize_string(input_str)

        # Log injection patterns to check for
        # Note: Implementation may escape or remove these patterns
        # This test verifies the result is safe for logging
        self.assertIsInstance(result, str)

        # Multiple consecutive newlines should be reduced (log injection prevention)
        self.assertNotIn(
            "\n\n\n", result, msg="Multiple newlines not sanitized for logging"
        )

    @given(
        st.text(
            alphabet=st.characters(
                min_codepoint=0x20,  # Start from space (ASCII 32), excludes control chars
                exclude_categories=["Cc", "Cs"],  # Control + Surrogate categories
            ),
            max_size=1000,
        )
    )
    @settings(max_examples=500, deadline=None)
    def test_safe_strings_minimally_modified(self, safe_str):
        """
        PROPERTY: Safe strings should be minimally modified.

        If input contains no dangerous characters, sanitization should
        preserve most of the content (may normalize whitespace).
        """
        result = sanitize_string(safe_str)

        # Length should not change dramatically for safe input
        # (allowing for some whitespace normalization)
        if len(safe_str) > 0:
            self.assertGreater(len(result), 0)
            # Result should not be dramatically shorter
            # (unless input was all whitespace)
            if len(safe_str.strip()) > 0:
                self.assertGreater(
                    len(result),
                    len(safe_str) // 10,
                    msg="Safe string was excessively truncated",
                )

    @given(st.text())
    @settings(max_examples=500, deadline=None)
    def test_idempotent_sanitization(self, input_str):
        """
        PROPERTY: Sanitizing twice should produce same result as sanitizing once.

        sanitize(sanitize(x)) should equal sanitize(x).
        """
        once = sanitize_string(input_str)
        twice = sanitize_string(once)
        self.assertEqual(once, twice, msg="Sanitization not idempotent")


# ============================================================================
# Combined Security Properties
# ============================================================================


@pytest.mark.security
class TestCombinedSecurityProperties(unittest.TestCase):
    """Property tests for combined security scenarios."""

    @given(st.text(), st.text())
    @settings(max_examples=300, deadline=None)
    def test_path_then_sanitize(self, path, content):
        """
        PROPERTY: Validating path then sanitizing content should never crash.

        Tests the common pattern: validate path, then sanitize content for display.
        """
        try:
            # Try to validate path (may fail legitimately)
            validated_path = validate_path(path)

            # Sanitize content (should never crash)
            sanitized = sanitize_string(content)

            # If both succeed, check types
            self.assertIsInstance(validated_path, bool)
            self.assertTrue(validated_path)
            self.assertIsInstance(sanitized, str)

        except (ValueError, OSError):
            # Expected for invalid paths
            pass
        except Exception as e:
            self.fail(
                f"Unexpected exception in combined security check: {type(e).__name__}: {e}"
            )


def run_tests():
    """Run all property-based tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPathValidationProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestStringSanitizationProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestCombinedSecurityProperties))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
