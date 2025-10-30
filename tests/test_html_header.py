"""
Tests for HeaderComponent in HTML Report Generator.

Covers HTML generation, data handling, escaping, and edge cases.
Target: 15 tests, 80% coverage
"""

import unittest
import pytest

from vscode_scanner.html_report.components.header import HeaderComponent


@pytest.mark.unit
class TestHeaderComponent(unittest.TestCase):
    """Test suite for HeaderComponent with comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.header = HeaderComponent()
        self.valid_summary = {
            "scan_timestamp": "2024-01-15T10:30:00",
            "total_extensions_scanned": 42,
            "scan_duration_seconds": 15.7,
            "vulnerabilities_found": 8,
            "critical_risk_extensions": 2,
            "high_risk_extensions": 5,
            "medium_risk_extensions": 15,
            "low_risk_extensions": 20,
            "cache_statistics": {"cache_hit_rate": 75.5},
        }
        self.valid_pie_chart = '<div class="pie-chart">chart</div>'

    def test_render_with_valid_data(self):
        """Test basic rendering with all valid data."""
        result = self.header.render(self.valid_summary, self.valid_pie_chart)

        # Verify structure
        self.assertIn('<header class="report-header">', result)
        self.assertIn("<h1>VS Code Extension Security Report</h1>", result)

        # Verify metadata
        self.assertIn("2024-01-15T10:30:00", result)
        self.assertIn("42", result)  # Total extensions
        self.assertIn("15.7s", result)  # Duration
        self.assertIn("75.5%", result)  # Cache hit rate

        # Verify risk distribution
        self.assertIn("Critical Risk: 2", result)
        self.assertIn("High Risk: 5", result)
        self.assertIn("Medium Risk: 15", result)
        self.assertIn("Low Risk: 20", result)

        # Verify vulnerabilities KPI
        self.assertIn("8", result)
        self.assertIn("Total Vulnerabilities", result)

        # Verify pie chart embedded
        self.assertIn(self.valid_pie_chart, result)

    def test_render_with_empty_summary(self):
        """Test rendering with empty summary dict (defaults to 0/N/A)."""
        result = self.header.render({}, "")

        # Should not crash, use defaults
        self.assertIn('<header class="report-header">', result)
        self.assertIn("Unknown", result)  # Default timestamp
        self.assertIn("0", result)  # Default counts

    def test_render_with_missing_fields(self):
        """Test rendering with partial summary data."""
        partial = {"total_extensions_scanned": 10, "scan_duration_seconds": 5.0}
        result = self.header.render(partial, "")

        # Should handle missing fields gracefully
        self.assertIn("10", result)
        self.assertIn("5.0s", result)
        self.assertIn("Unknown", result)  # Missing timestamp
        self.assertIn("0.0%", result)  # Missing cache stats

    def test_html_escaping_in_timestamp(self):
        """Test XSS prevention through HTML escaping."""
        malicious = self.valid_summary.copy()
        malicious["scan_timestamp"] = '<script>alert("xss")</script>'

        result = self.header.render(malicious, self.valid_pie_chart)

        # Should escape HTML
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)

    def test_zero_values_handling(self):
        """Test rendering with all zero risk counts."""
        zero_summary = self.valid_summary.copy()
        zero_summary.update(
            {
                "critical_risk_extensions": 0,
                "high_risk_extensions": 0,
                "medium_risk_extensions": 0,
                "low_risk_extensions": 0,
                "vulnerabilities_found": 0,
            }
        )

        result = self.header.render(zero_summary, self.valid_pie_chart)

        # Should display zeros correctly
        self.assertIn("Critical Risk: 0", result)
        self.assertIn("High Risk: 0", result)
        self.assertIn("Medium Risk: 0", result)
        self.assertIn("Low Risk: 0", result)
        self.assertIn('<div class="vuln-kpi-number">0</div>', result)

    def test_large_numbers(self):
        """Test rendering with large extension counts."""
        large_summary = self.valid_summary.copy()
        large_summary["total_extensions_scanned"] = 9999
        large_summary["vulnerabilities_found"] = 1234

        result = self.header.render(large_summary, self.valid_pie_chart)

        self.assertIn("9999", result)
        self.assertIn("1234", result)

    def test_float_precision_duration(self):
        """Test scan duration float formatting (1 decimal place)."""
        float_summary = self.valid_summary.copy()
        float_summary["scan_duration_seconds"] = 123.456789

        result = self.header.render(float_summary, self.valid_pie_chart)

        # Should round to 1 decimal place
        self.assertIn("123.5s", result)

    def test_float_precision_cache_rate(self):
        """Test cache hit rate float formatting (1 decimal place)."""
        cache_summary = self.valid_summary.copy()
        cache_summary["cache_statistics"]["cache_hit_rate"] = 88.888888

        result = self.header.render(cache_summary, self.valid_pie_chart)

        # Should round to 1 decimal place
        self.assertIn("88.9%", result)

    def test_pie_chart_html_injection(self):
        """Test that pie chart HTML is embedded as-is (trusted input)."""
        custom_chart = '<svg class="custom-chart"><circle/></svg>'
        result = self.header.render(self.valid_summary, custom_chart)

        # Should embed chart HTML directly
        self.assertIn(custom_chart, result)

    def test_missing_cache_statistics(self):
        """Test handling when cache_statistics dict is missing."""
        no_cache = self.valid_summary.copy()
        del no_cache["cache_statistics"]

        result = self.header.render(no_cache, self.valid_pie_chart)

        # Should default to 0.0%
        self.assertIn("0.0%", result)

    def test_metadata_items_structure(self):
        """Test that all 4 metadata items are present."""
        result = self.header.render(self.valid_summary, self.valid_pie_chart)

        # Count metadata items
        metadata_count = result.count('<div class="metadata-item">')
        self.assertEqual(metadata_count, 4)

        # Verify labels
        self.assertIn("Generated:", result)
        self.assertIn("Total Extensions:", result)
        self.assertIn("Scan Duration:", result)
        self.assertIn("Cache Hit Rate:", result)

    def test_risk_legend_structure(self):
        """Test risk distribution legend has all 4 risk levels."""
        result = self.header.render(self.valid_summary, self.valid_pie_chart)

        # Count legend items
        legend_count = result.count('<div class="legend-item">')
        self.assertEqual(legend_count, 4)

        # Verify CSS classes for colors
        self.assertIn("risk-critical-bg", result)
        self.assertIn("risk-high-bg", result)
        self.assertIn("risk-medium-bg", result)
        self.assertIn("risk-low-bg", result)

    def test_vulnerabilities_kpi_structure(self):
        """Test vulnerabilities KPI display structure."""
        result = self.header.render(self.valid_summary, self.valid_pie_chart)

        # Verify KPI structure
        self.assertIn('<div class="chart-container vulnerabilities-kpi">', result)
        self.assertIn('<div class="vuln-kpi-display">', result)
        self.assertIn('<div class="vuln-kpi-number">8</div>', result)
        self.assertIn('<div class="vuln-kpi-label">Total Vulnerabilities</div>', result)

    def test_date_value_iso_attribute(self):
        """Test that timestamp has data-iso-date attribute for JS formatting."""
        result = self.header.render(self.valid_summary, self.valid_pie_chart)

        # Verify ISO date attribute
        self.assertIn('data-iso-date="2024-01-15T10:30:00"', result)
        self.assertIn('class="value date-value"', result)

    def test_header_closing_tag(self):
        """Test that header tag is properly closed."""
        result = self.header.render(self.valid_summary, self.valid_pie_chart)

        # Verify proper HTML structure
        self.assertTrue(result.strip().startswith('<header class="report-header">'))
        self.assertTrue(result.strip().endswith("</header>"))


if __name__ == "__main__":
    unittest.main()
