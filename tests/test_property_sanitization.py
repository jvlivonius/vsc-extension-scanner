#!/usr/bin/env python3
"""
Property-Based Tests for String Sanitization

Uses Hypothesis to generate thousands of test cases automatically to find edge cases
in the sanitize_string function that traditional unit tests might miss.

**Purpose:**
- Validate sanitize_string behavior across a wide range of inputs
- Find edge cases with automatically generated test data
- Ensure no crashes or unexpected behavior with malformed inputs

**Coverage:**
- Control character removal
- ANSI escape sequence removal
- Length truncation
- None handling
- Unicode handling
"""

import sys
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.utils import sanitize_string


@pytest.mark.property_based
@pytest.mark.security
class TestSanitizeStringProperties:
    """Property-based tests for sanitize_string using Hypothesis."""

    @given(st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_always_returns_string(self, text):
        """Property: sanitize_string always returns a string."""
        result = sanitize_string(text)
        assert isinstance(result, str)

    @given(st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_result_length_respects_max_length(self, text):
        """Property: result never exceeds max_length."""
        max_len = 100
        result = sanitize_string(text, max_length=max_len)
        assert len(result) <= max_len

    @given(st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_removes_ansi_escape_codes(self, text):
        """Property: ANSI escape sequences are removed."""
        # Add ANSI codes to input
        ansi_text = f"\x1b[31m{text}\x1b[0m"
        result = sanitize_string(ansi_text)
        # Result should not contain ANSI escape sequences
        assert "\x1b[" not in result
        assert "\x1b" not in result

    @given(st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_removes_control_characters(self, text):
        """Property: control characters (except newline/tab) are removed."""
        # Add control characters
        control_chars = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"
        contaminated = f"{text}{control_chars}"
        result = sanitize_string(contaminated)

        # Should not contain these control characters
        for char in control_chars:
            if char not in ["\n", "\t", "\r"]:
                assert char not in result

    @given(st.text(min_size=1))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_preserves_safe_characters(self, text):
        """Property: safe characters are preserved."""
        # Filter to only safe characters
        safe_text = "".join(c for c in text if c.isprintable() or c in ["\n", "\t"])
        result = sanitize_string(safe_text, max_length=10000)

        # Should preserve safe characters (accounting for possible truncation)
        if len(safe_text) <= 10000:
            assert len(result) == len(safe_text) or result == safe_text.strip()

    @given(st.none() | st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_handles_none_values(self, text):
        """Property: None values are handled without crashing."""
        result = sanitize_string(text)
        assert isinstance(result, str)
        if text is None:
            assert result == ""

    @given(st.integers(min_value=10, max_value=1000))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_respects_any_max_length(self, max_len):
        """Property: any valid max_length is respected exactly."""
        long_text = "x" * 2000
        result = sanitize_string(long_text, max_length=max_len)
        # Result should be exactly max_len (includes "..." suffix within that length)
        assert len(result) == max_len

    @given(st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_idempotent_sanitization(self, text):
        """Property: sanitizing twice gives same result as sanitizing once."""
        first = sanitize_string(text)
        second = sanitize_string(first)
        assert first == second

    @given(st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126)))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_ascii_printable_unchanged(self, text):
        """Property: ASCII printable characters pass through unchanged."""
        # ASCII printable characters (32-126) should not be removed
        result = sanitize_string(text, max_length=10000)
        # Should preserve the text (possibly with whitespace normalization)
        assert all(c in text or c.isspace() for c in result)

    @given(st.text(min_size=0, max_size=1000))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_crashes_on_any_input(self, text):
        """Property: sanitize_string never crashes on any text input."""
        try:
            result = sanitize_string(text)
            assert result is not None
        except Exception as e:
            pytest.fail(f"sanitize_string crashed on input: {repr(text)}, error: {e}")


@pytest.mark.property_based
@pytest.mark.security
class TestSanitizeStringRegressions:
    """Regression tests for known edge cases found by property testing."""

    def test_multiple_ansi_codes(self):
        """Regression: multiple ANSI codes in sequence."""
        text = "\x1b[31m\x1b[1m\x1b[4mRed Bold Underline\x1b[0m"
        result = sanitize_string(text)
        assert "\x1b" not in result
        assert "Red Bold Underline" in result

    def test_nested_ansi_codes(self):
        """Regression: nested ANSI codes."""
        text = "\x1b[31mRed \x1b[32mGreen\x1b[0m Red\x1b[0m"
        result = sanitize_string(text)
        assert "\x1b" not in result

    def test_control_character_soup(self):
        """Regression: mix of control characters."""
        text = "Test\x00\x01\x02\x03\x04\x05\x06\x07String"
        result = sanitize_string(text)
        assert result == "TestString"

    def test_unicode_with_ansi(self):
        """Regression: Unicode characters with ANSI codes."""
        text = "\x1b[31m日本語テキスト\x1b[0m"
        result = sanitize_string(text)
        assert "\x1b" not in result
        assert "日本語テキスト" in result

    def test_empty_string(self):
        """Regression: empty string handling."""
        assert sanitize_string("") == ""
        assert sanitize_string(None) == ""

    def test_max_length_boundary(self):
        """Regression: exact max_length boundary."""
        text = "x" * 500
        result = sanitize_string(text, max_length=500)
        assert len(result) == 500

        text = "x" * 501
        result = sanitize_string(text, max_length=500)
        # Should be truncated to exactly max_length (includes "..." within limit)
        assert len(result) == 500
        assert result.endswith("...")


if __name__ == "__main__":
    # Run with Hypothesis statistics
    sys.exit(pytest.main([__file__, "-v", "--hypothesis-show-statistics"]))
