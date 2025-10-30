"""
Tests for BaseComponent - HTML Report Base Utilities.

Covers HTML escaping, number formatting, CSS class generation, and utility methods.
Target: 8 tests for 95%+ coverage of base_component.py
"""

import unittest
import pytest

from vscode_scanner.html_report.base_component import BaseComponent


# Concrete implementation for testing abstract base class
class ConcreteComponent(BaseComponent):
    """Concrete implementation of BaseComponent for testing."""

    def render(self, *args, **kwargs) -> str:
        """Test implementation of render method."""
        return "<div>Test Component</div>"


@pytest.mark.unit
class TestBaseComponent(unittest.TestCase):
    """Test suite for BaseComponent utility methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.component = ConcreteComponent()

    # === Initialization Tests ===

    def test_component_initialization_with_version(self):
        """Test that component initializes with version from _version.py."""
        # Verify version is set
        self.assertIsNotNone(self.component.version)
        self.assertIsInstance(self.component.version, str)

        # Version should match format (e.g., "3.5.4")
        version_parts = self.component.version.split(".")
        self.assertGreaterEqual(len(version_parts), 2)

    # === HTML Escaping Tests ===

    def test_safe_escape_with_valid_string(self):
        """Test HTML escaping with valid string."""
        result = self.component._safe_escape("Hello World")
        self.assertEqual(result, "Hello World")

    def test_safe_escape_with_html_characters(self):
        """Test XSS prevention through HTML character escaping."""
        malicious = '<script>alert("xss")</script>'
        result = self.component._safe_escape(malicious)

        # Should escape angle brackets
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertIn("&quot;", result)

    def test_safe_escape_with_none_value(self):
        """Test that None values use default."""
        result = self.component._safe_escape(None)
        self.assertEqual(result, "N/A")

        # Test custom default
        result_custom = self.component._safe_escape(None, default="Unknown")
        self.assertEqual(result_custom, "Unknown")

    def test_safe_escape_with_non_string_types(self):
        """Test escaping with numbers and other types."""
        # Integer
        self.assertEqual(self.component._safe_escape(42), "42")

        # Float
        self.assertEqual(self.component._safe_escape(3.14), "3.14")

        # Boolean
        self.assertEqual(self.component._safe_escape(True), "True")

    def test_safe_escape_quote_parameter(self):
        """Test quote parameter affects attribute quoting."""
        text_with_quotes = 'He said "Hello"'

        # With quoting (default)
        result_quoted = self.component._safe_escape(text_with_quotes, quote=True)
        self.assertIn("&quot;", result_quoted)

        # Without quoting
        result_unquoted = self.component._safe_escape(text_with_quotes, quote=False)
        self.assertIn('"', result_unquoted)
        self.assertNotIn("&quot;", result_unquoted)

    # === Gauge Color Class Tests ===

    def test_get_gauge_color_class_ranges(self):
        """Test gauge color class selection based on score ranges."""
        # Success range (75+)
        self.assertEqual(self.component._get_gauge_color_class(100), "gauge-success")
        self.assertEqual(self.component._get_gauge_color_class(75), "gauge-success")

        # Warning range (50-74)
        self.assertEqual(self.component._get_gauge_color_class(74), "gauge-warning")
        self.assertEqual(self.component._get_gauge_color_class(50), "gauge-warning")

        # Danger range (<50)
        self.assertEqual(self.component._get_gauge_color_class(49), "gauge-danger")
        self.assertEqual(self.component._get_gauge_color_class(0), "gauge-danger")

    # === Risk Level Class Tests ===

    def test_get_risk_level_class_valid_levels(self):
        """Test risk level CSS class generation."""
        self.assertEqual(
            self.component._get_risk_level_class("critical"), "risk-badge risk-critical"
        )
        self.assertEqual(
            self.component._get_risk_level_class("high"), "risk-badge risk-high"
        )
        self.assertEqual(
            self.component._get_risk_level_class("medium"), "risk-badge risk-medium"
        )
        self.assertEqual(
            self.component._get_risk_level_class("low"), "risk-badge risk-low"
        )

    def test_get_risk_level_class_case_insensitive(self):
        """Test that risk level class handles different cases."""
        # Uppercase
        self.assertEqual(
            self.component._get_risk_level_class("CRITICAL"), "risk-badge risk-critical"
        )

        # Mixed case
        self.assertEqual(
            self.component._get_risk_level_class("HiGh"), "risk-badge risk-high"
        )

    def test_get_risk_level_class_none_or_empty(self):
        """Test risk level class with None or empty string."""
        # None
        self.assertEqual(
            self.component._get_risk_level_class(None), "risk-badge risk-unknown"
        )

        # Empty string
        self.assertEqual(
            self.component._get_risk_level_class(""), "risk-badge risk-unknown"
        )

    # === Number Formatting Tests ===

    def test_format_number_billions(self):
        """Test number formatting for billions."""
        self.assertEqual(self.component._format_number(1_000_000_000), "1.0B")
        self.assertEqual(self.component._format_number(2_500_000_000), "2.5B")
        self.assertEqual(self.component._format_number(187_936_883_000), "187.9B")

    def test_format_number_millions(self):
        """Test number formatting for millions."""
        self.assertEqual(self.component._format_number(1_000_000), "1.0M")
        self.assertEqual(self.component._format_number(1_500_000), "1.5M")
        self.assertEqual(self.component._format_number(187_936_883), "187.9M")

    def test_format_number_thousands(self):
        """Test number formatting for thousands."""
        self.assertEqual(self.component._format_number(1_000), "1.0K")
        self.assertEqual(self.component._format_number(1_500), "1.5K")
        self.assertEqual(self.component._format_number(42_000), "42.0K")

    def test_format_number_small_values(self):
        """Test number formatting for values under 1000."""
        self.assertEqual(self.component._format_number(0), "0")
        self.assertEqual(self.component._format_number(42), "42")
        self.assertEqual(self.component._format_number(999), "999")

    def test_format_number_edge_cases(self):
        """Test number formatting at boundary values."""
        # Just below thousands
        self.assertEqual(self.component._format_number(999), "999")

        # Exactly thousands
        self.assertEqual(self.component._format_number(1_000), "1.0K")

        # Just below millions
        self.assertEqual(self.component._format_number(999_999), "1000.0K")

        # Exactly millions
        self.assertEqual(self.component._format_number(1_000_000), "1.0M")

        # Just below billions
        self.assertEqual(self.component._format_number(999_999_999), "1000.0M")

        # Exactly billions
        self.assertEqual(self.component._format_number(1_000_000_000), "1.0B")

    # === Abstract Method Test ===

    def test_render_method_implemented(self):
        """Test that concrete implementation provides render method."""
        result = self.component.render()
        self.assertIsInstance(result, str)
        self.assertIn("Test Component", result)


if __name__ == "__main__":
    unittest.main()
