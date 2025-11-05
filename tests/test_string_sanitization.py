#!/usr/bin/env python3
"""
Comprehensive String Sanitization Tests (v3.7.0 Phase 3 - Parameterized)

Tests the enhanced sanitize_string() function to ensure it:
1. Removes ANSI escape sequences (terminal injection prevention)
2. Removes dangerous control characters
3. Keeps safe whitespace characters (\n, \t, \r)
4. Truncates long strings (DoS prevention)
5. Handles None input gracefully
6. Converts non-string input to string

Phase 3.1 Refactoring: Consolidated repetitive tests using @pytest.mark.parametrize
for better maintainability and clearer test output. Converted from unittest to pure pytest style.
"""

import sys
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.utils import sanitize_string


@pytest.mark.security
class TestStringSanitization:
    """Test the enhanced sanitize_string() function."""

    def test_normal_text(self):
        """Test that normal text passes through unchanged."""
        result = sanitize_string("Hello, World!")
        assert result == "Hello, World!"

        result = sanitize_string("Extension: ms-python.python v1.2.3")
        assert result == "Extension: ms-python.python v1.2.3"

    def test_none_input(self):
        """Test that None input returns empty string."""
        result = sanitize_string(None)
        assert result == ""

    @pytest.mark.parametrize(
        "numeric_input,expected",
        [
            (12345, "12345"),
            (3.14159, "3.14159"),
        ],
        ids=["integer", "float"],
    )
    def test_numeric_input(self, numeric_input, expected):
        """Test that numeric input is converted to string."""
        result = sanitize_string(numeric_input)
        assert result == expected

    @pytest.mark.parametrize(
        "ansi_input,expected_output,description",
        [
            # Red text: \x1b[31m
            ("\x1b[31mred text\x1b[0m", "red text", "red_color"),
            # Green background: \x1b[42m
            ("\x1b[42mgreen background\x1b[0m", "green background", "green_background"),
            # Bold: \x1b[1m
            ("\x1b[1mbold text\x1b[0m", "bold text", "bold"),
        ],
        ids=lambda x: x[2] if isinstance(x, tuple) and len(x) > 2 else str(x),
    )
    def test_ansi_color_codes_removed(self, ansi_input, expected_output, description):
        """
        Test that ANSI color codes are stripped.

        Parameterized to test different ANSI color and formatting codes.
        """
        result = sanitize_string(ansi_input)
        assert result == expected_output

    @pytest.mark.parametrize(
        "ansi_sequence,expected_output,description",
        [
            # Cursor up: \x1b[A
            ("Line1\x1b[ALine2", "Line1Line2", "cursor_up"),
            # Cursor position: \x1b[10;20H
            ("Text\x1b[10;20HMore text", "TextMore text", "cursor_position"),
            # Clear screen: \x1b[2J
            ("\x1b[2JCleared", "Cleared", "clear_screen"),
        ],
        ids=lambda x: x[2] if isinstance(x, tuple) and len(x) > 2 else str(x),
    )
    def test_ansi_cursor_movement_removed(
        self, ansi_sequence, expected_output, description
    ):
        """
        Test that ANSI cursor movement sequences are stripped.

        Parameterized to test different cursor control sequences.
        """
        result = sanitize_string(ansi_sequence)
        assert result == expected_output

    def test_osc_sequences_removed(self):
        """Test that OSC (Operating System Command) sequences are stripped."""
        # Window title: \x1b]0;Title\x07
        result = sanitize_string("\x1b]0;Window Title\x07Normal text")
        assert result == "Normal text"

    @pytest.mark.parametrize(
        "control_char_input,expected_output,description",
        [
            # Null byte
            ("text\x00with\x00nulls", "textwithnulls", "null_byte"),
            # Bell character
            ("text\x07with\x07bells", "textwithbells", "bell"),
            # Backspace
            ("text\x08back", "textback", "backspace"),
            # Delete
            ("text\x7fdelete", "textdelete", "delete"),
        ],
        ids=lambda x: x[2] if isinstance(x, tuple) and len(x) > 2 else str(x),
    )
    def test_dangerous_control_characters_removed(
        self, control_char_input, expected_output, description
    ):
        """
        Test that dangerous control characters are removed.

        Parameterized to test removal of null bytes, bell, backspace, and delete characters.
        Prevents terminal manipulation and annoying beeps.
        """
        result = sanitize_string(control_char_input)
        assert result == expected_output

    @pytest.mark.parametrize(
        "whitespace_input,expected_output,description",
        [
            # Newline preserved
            ("line1\nline2", "line1\nline2", "newline"),
            # Tab preserved
            ("col1\tcol2", "col1\tcol2", "tab"),
            # Carriage return removed (security fix - can overwrite terminal)
            ("text\r\n", "text\n", "carriage_return_removed"),
        ],
        ids=lambda x: x[2] if isinstance(x, tuple) and len(x) > 2 else str(x),
    )
    def test_safe_whitespace_preserved(
        self, whitespace_input, expected_output, description
    ):
        """
        Test that newline and tab are preserved, but carriage return is removed.

        Carriage return removal is a security fix - it can overwrite terminal content.
        """
        result = sanitize_string(whitespace_input)
        assert result == expected_output

    @pytest.mark.parametrize(
        "control_input,expected_output,description",
        [
            # Vertical tab
            ("text\x0bvtab", "textvtab", "vertical_tab"),
            # Form feed
            ("text\x0cff", "textff", "form_feed"),
        ],
        ids=lambda x: x[2] if isinstance(x, tuple) and len(x) > 2 else str(x),
    )
    def test_other_control_characters_removed(
        self, control_input, expected_output, description
    ):
        """
        Test that other control characters (vertical tab, form feed) are removed.

        Parameterized to test removal of various control characters.
        """
        result = sanitize_string(control_input)
        assert result == expected_output

    def test_truncation(self):
        """Test that long strings are truncated."""
        long_text = "A" * 1000
        result = sanitize_string(long_text, max_length=100)

        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")
        assert result[:100] == "A" * 100

    def test_custom_max_length(self):
        """Test custom max_length parameter."""
        text = "0123456789" * 10  # 100 characters
        result = sanitize_string(text, max_length=50)

        assert len(result) == 53  # 50 + "..."
        assert result.endswith("...")

    def test_terminal_injection_attack(self):
        """Test protection against terminal injection attack."""
        # Malicious payload: clear screen, move cursor, display fake error
        malicious = "\x1b[2J\x1b[H\x1b[31m[ERROR] System compromised!\x1b[0m"
        result = sanitize_string(malicious)

        # Should only contain the text, no escape codes
        assert result == "[ERROR] System compromised!"
        assert "\x1b" not in result

    def test_mixed_attack_vectors(self):
        """Test string with multiple attack vectors combined."""
        mixed = "Normal\x00null\x07bell\x1b[31mred\x1b[0m\x08back"
        result = sanitize_string(mixed)

        # All dangerous characters and sequences should be removed
        assert result == "Normalnullbellredback"
        assert "\x00" not in result
        assert "\x07" not in result
        assert "\x1b" not in result
        assert "\x08" not in result

    def test_unicode_text_preserved(self):
        """Test that Unicode text is preserved."""
        # Various Unicode characters
        unicode_text = "Hello 世界 🌍 Привет"
        result = sanitize_string(unicode_text)
        assert result == unicode_text

    def test_empty_string(self):
        """Test that empty string is handled correctly."""
        result = sanitize_string("")
        assert result == ""

    def test_whitespace_only(self):
        """Test strings with only whitespace."""
        result = sanitize_string("   \t\n   ")
        assert result == " "  # Normalized to single space


@pytest.mark.security
class TestStringSanitizationIntegration:
    """Integration tests for sanitize_string() usage."""

    def test_sanitize_file_paths(self):
        """Test sanitizing file paths (common use case)."""
        # Normal path
        path = "/Users/test/extensions/ms-python.python-2024.10.0"
        result = sanitize_string(path, max_length=150)
        assert result == path

        # Path with ANSI codes (shouldn't happen but should be handled)
        malicious_path = "/tmp/\x1b[31mmalicious\x1b[0m/file.txt"
        result = sanitize_string(malicious_path)
        assert result == "/tmp/malicious/file.txt"

    def test_sanitize_error_messages(self):
        """Test sanitizing error messages."""
        error = "File not found: extension.json"
        result = sanitize_string(error, max_length=200)
        assert result == error

        # Error with control characters
        malicious_error = "Error\x00:\x07File\x08corrupted"
        result = sanitize_string(malicious_error)
        assert result == "Error:Filecorrupted"

    def test_sanitize_extension_names(self):
        """Test sanitizing extension names and descriptions."""
        name = "Python Extension for VS Code"
        result = sanitize_string(name)
        assert result == name

        # Malicious name with ANSI injection
        malicious_name = "Normal Extension\x1b[2J\x1b[H\x1b[31mFake Error\x1b[0m"
        result = sanitize_string(malicious_name)
        assert result == "Normal ExtensionFake Error"


if __name__ == "__main__":
    print("=" * 70)
    print("STRING SANITIZATION TESTS (v3.7.0 Phase 3 - Parameterized)")
    print("=" * 70)
    print()
    print("Testing enhanced sanitize_string() function:")
    print("- ANSI escape sequence removal (parametrized)")
    print("- Control character filtering (parametrized)")
    print("- Safe whitespace preservation (parametrized)")
    print("- Length truncation")
    print("- Terminal injection prevention")
    print()
    print("=" * 70)
    print()

    # Run with pytest
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
