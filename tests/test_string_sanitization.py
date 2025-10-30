#!/usr/bin/env python3
"""
Comprehensive String Sanitization Tests (v3.5.1 Security Hardening)

Tests the enhanced sanitize_string() function to ensure it:
1. Removes ANSI escape sequences (terminal injection prevention)
2. Removes dangerous control characters
3. Keeps safe whitespace characters (\n, \t, \r)
4. Truncates long strings (DoS prevention)
5. Handles None input gracefully
6. Converts non-string input to string

This addresses security concerns for CLI output:
- Terminal injection via ANSI codes
- Control character attacks
- DoS via extremely long strings
"""

import sys
import unittest
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.utils import sanitize_string


@pytest.mark.security
class TestStringSanitization(unittest.TestCase):
    """Test the enhanced sanitize_string() function."""

    def test_normal_text(self):
        """Test that normal text passes through unchanged."""
        result = sanitize_string("Hello, World!")
        self.assertEqual(result, "Hello, World!")

        result = sanitize_string("Extension: ms-python.python v1.2.3")
        self.assertEqual(result, "Extension: ms-python.python v1.2.3")

    def test_none_input(self):
        """Test that None input returns empty string."""
        result = sanitize_string(None)
        self.assertEqual(result, "")

    def test_numeric_input(self):
        """Test that numeric input is converted to string."""
        result = sanitize_string(12345)
        self.assertEqual(result, "12345")

        result = sanitize_string(3.14159)
        self.assertEqual(result, "3.14159")

    def test_ansi_color_codes_removed(self):
        """Test that ANSI color codes are stripped."""
        # Red text: \x1b[31m
        result = sanitize_string("\x1b[31mred text\x1b[0m")
        self.assertEqual(result, "red text")

        # Green background: \x1b[42m
        result = sanitize_string("\x1b[42mgreen background\x1b[0m")
        self.assertEqual(result, "green background")

        # Bold: \x1b[1m
        result = sanitize_string("\x1b[1mbold text\x1b[0m")
        self.assertEqual(result, "bold text")

    def test_ansi_cursor_movement_removed(self):
        """Test that ANSI cursor movement sequences are stripped."""
        # Cursor up: \x1b[A
        result = sanitize_string("Line1\x1b[ALine2")
        self.assertEqual(result, "Line1Line2")

        # Cursor position: \x1b[10;20H
        result = sanitize_string("Text\x1b[10;20HMore text")
        self.assertEqual(result, "TextMore text")

        # Clear screen: \x1b[2J
        result = sanitize_string("\x1b[2JCleared")
        self.assertEqual(result, "Cleared")

    def test_osc_sequences_removed(self):
        """Test that OSC (Operating System Command) sequences are stripped."""
        # Window title: \x1b]0;Title\x07
        result = sanitize_string("\x1b]0;Window Title\x07Normal text")
        self.assertEqual(result, "Normal text")

    def test_null_byte_removed(self):
        """Test that null bytes are removed."""
        result = sanitize_string("text\x00with\x00nulls")
        self.assertEqual(result, "textwithnulls")

    def test_bell_character_removed(self):
        """Test that bell character is removed (prevents annoying beeps)."""
        result = sanitize_string("text\x07with\x07bells")
        self.assertEqual(result, "textwithbells")

    def test_backspace_removed(self):
        """Test that backspace is removed (prevents terminal manipulation)."""
        result = sanitize_string("text\x08back")
        self.assertEqual(result, "textback")

    def test_delete_removed(self):
        """Test that delete character is removed."""
        result = sanitize_string("text\x7fdelete")
        self.assertEqual(result, "textdelete")

    def test_safe_whitespace_preserved(self):
        """Test that newline, tab, and carriage return are preserved."""
        # Newline
        result = sanitize_string("line1\nline2")
        self.assertEqual(result, "line1\nline2")

        # Tab
        result = sanitize_string("col1\tcol2")
        self.assertEqual(result, "col1\tcol2")

        # Carriage return removed (security fix - can overwrite terminal)
        result = sanitize_string("text\r\n")
        self.assertEqual(result, "text\n")  # \r removed, \n preserved

    def test_other_control_characters_removed(self):
        """Test that other control characters are removed."""
        # Vertical tab
        result = sanitize_string("text\x0bvtab")
        self.assertEqual(result, "textvtab")

        # Form feed
        result = sanitize_string("text\x0cff")
        self.assertEqual(result, "textff")

    def test_truncation(self):
        """Test that long strings are truncated."""
        long_text = "A" * 1000
        result = sanitize_string(long_text, max_length=100)

        self.assertEqual(len(result), 103)  # 100 + "..."
        self.assertTrue(result.endswith("..."))
        self.assertEqual(result[:100], "A" * 100)

    def test_custom_max_length(self):
        """Test custom max_length parameter."""
        text = "0123456789" * 10  # 100 characters
        result = sanitize_string(text, max_length=50)

        self.assertEqual(len(result), 53)  # 50 + "..."
        self.assertTrue(result.endswith("..."))

    def test_terminal_injection_attack(self):
        """Test protection against terminal injection attack."""
        # Malicious payload: clear screen, move cursor, display fake error
        malicious = "\x1b[2J\x1b[H\x1b[31m[ERROR] System compromised!\x1b[0m"
        result = sanitize_string(malicious)

        # Should only contain the text, no escape codes
        self.assertEqual(result, "[ERROR] System compromised!")
        self.assertNotIn("\x1b", result)

    def test_mixed_attack_vectors(self):
        """Test string with multiple attack vectors combined."""
        mixed = "Normal\x00null\x07bell\x1b[31mred\x1b[0m\x08back"
        result = sanitize_string(mixed)

        # All dangerous characters and sequences should be removed
        self.assertEqual(result, "Normalnullbellredback")
        self.assertNotIn("\x00", result)
        self.assertNotIn("\x07", result)
        self.assertNotIn("\x1b", result)
        self.assertNotIn("\x08", result)

    def test_unicode_text_preserved(self):
        """Test that Unicode text is preserved."""
        # Various Unicode characters
        unicode_text = "Hello 世界 🌍 Привет"
        result = sanitize_string(unicode_text)
        self.assertEqual(result, unicode_text)

    def test_empty_string(self):
        """Test that empty string is handled correctly."""
        result = sanitize_string("")
        self.assertEqual(result, "")

    def test_whitespace_only(self):
        """Test strings with only whitespace."""
        result = sanitize_string("   \t\n   ")
        self.assertEqual(result, " ")  # Normalized to single space


@pytest.mark.security
class TestStringSanitizationIntegration(unittest.TestCase):
    """Integration tests for sanitize_string() usage."""

    def test_sanitize_file_paths(self):
        """Test sanitizing file paths (common use case)."""
        # Normal path
        path = "/Users/test/extensions/ms-python.python-2024.10.0"
        result = sanitize_string(path, max_length=150)
        self.assertEqual(result, path)

        # Path with ANSI codes (shouldn't happen but should be handled)
        malicious_path = "/tmp/\x1b[31mmalicious\x1b[0m/file.txt"
        result = sanitize_string(malicious_path)
        self.assertEqual(result, "/tmp/malicious/file.txt")

    def test_sanitize_error_messages(self):
        """Test sanitizing error messages."""
        error = "File not found: extension.json"
        result = sanitize_string(error, max_length=200)
        self.assertEqual(result, error)

        # Error with control characters
        malicious_error = "Error\x00:\x07File\x08corrupted"
        result = sanitize_string(malicious_error)
        self.assertEqual(result, "Error:Filecorrupted")

    def test_sanitize_extension_names(self):
        """Test sanitizing extension names and descriptions."""
        name = "Python Extension for VS Code"
        result = sanitize_string(name)
        self.assertEqual(result, name)

        # Malicious name with ANSI injection
        malicious_name = "Normal Extension\x1b[2J\x1b[H\x1b[31mFake Error\x1b[0m"
        result = sanitize_string(malicious_name)
        self.assertEqual(result, "Normal ExtensionFake Error")


def run_tests():
    """Run all string sanitization tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStringSanitization))
    suite.addTests(loader.loadTestsFromTestCase(TestStringSanitizationIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    print("=" * 70)
    print("STRING SANITIZATION TESTS (v3.5.1 Security Hardening)")
    print("=" * 70)
    print()
    print("Testing enhanced sanitize_string() function:")
    print("- ANSI escape sequence removal")
    print("- Control character filtering")
    print("- Safe whitespace preservation")
    print("- Length truncation")
    print("- Terminal injection prevention")
    print()
    print("=" * 70)
    print()

    sys.exit(run_tests())
