"""
Tests for ChartComponents in HTML Report Generator.

Covers all chart rendering methods: risk bar, security gauge, pie chart,
vulnerability grid, and mini gauge.
Target: 15 tests, 75% coverage
"""

import unittest
import pytest

from vscode_scanner.html_report.components.charts import ChartComponents


@pytest.mark.unit
class TestChartComponents(unittest.TestCase):
    """Test suite for ChartComponents with comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.charts = ChartComponents()

    # === render_risk_distribution_bar tests ===

    def test_risk_bar_normal_rendering(self):
        """Test risk distribution bar with normal counts."""
        result = self.charts.render_risk_distribution_bar(
            critical=2, high=5, medium=15, low=20
        )

        # Verify structure
        self.assertIn('class="simple-chart"', result)
        self.assertIn('class="chart-bar"', result)

        # Verify all risk levels present
        self.assertIn("bar-segment risk-critical-bg", result)
        self.assertIn("bar-segment risk-high-bg", result)
        self.assertIn("bar-segment risk-medium-bg", result)
        self.assertIn("bar-segment risk-low-bg", result)

        # Verify percentages calculated (total=42)
        # Critical: 2/42 ≈ 4.8%, High: 5/42 ≈ 11.9%, etc.
        self.assertIn("%", result)

    def test_risk_bar_all_zeros(self):
        """Test risk distribution bar with all zero counts."""
        result = self.charts.render_risk_distribution_bar(
            critical=0, high=0, medium=0, low=0
        )

        # Should handle zero total gracefully (shows "No data")
        self.assertIn("no-data", result)

    def test_risk_bar_percentage_calculation(self):
        """Test that percentages are calculated correctly."""
        # Simple percentages: 25 each = 100 total
        result = self.charts.render_risk_distribution_bar(
            critical=25, high=25, medium=25, low=25
        )

        # Each should be 25%
        # Count style attributes with 25.0%
        width_count = result.count("25.0%")
        self.assertGreaterEqual(width_count, 4)

    # === render_security_gauge tests ===

    def test_security_gauge_normal_score(self):
        """Test security gauge with normal score and risk level."""
        result = self.charts.render_security_gauge(score=75, risk_level="low")

        # Verify structure
        self.assertIn('class="security-gauge"', result)

        # Verify score displayed
        self.assertIn("75", result)

        # Verify gauge bar present
        self.assertIn('class="gauge-bar', result)

    def test_security_gauge_edge_scores(self):
        """Test security gauge with edge case scores (0 and 100)."""
        result_zero = self.charts.render_security_gauge(score=0, risk_level="critical")
        result_hundred = self.charts.render_security_gauge(score=100, risk_level="low")

        # Both should render without errors
        self.assertIn('class="security-gauge"', result_zero)
        self.assertIn('class="security-gauge"', result_hundred)

        # Verify scores
        self.assertIn("0", result_zero)
        self.assertIn("100", result_hundred)

    def test_security_gauge_risk_level_classes(self):
        """Test that risk level determines CSS class."""
        # Risk-level-based CSS classes
        result_critical = self.charts.render_security_gauge(
            score=50, risk_level="critical"
        )
        result_high = self.charts.render_security_gauge(score=50, risk_level="high")
        result_medium = self.charts.render_security_gauge(score=50, risk_level="medium")
        result_low = self.charts.render_security_gauge(score=50, risk_level="low")

        # Verify risk-level-based classes
        self.assertIn("gauge-critical", result_critical)
        self.assertIn("gauge-danger", result_high)
        self.assertIn("gauge-warning", result_medium)
        self.assertIn("gauge-success", result_low)

    # === render_score_pie_chart tests ===

    def test_score_pie_chart_normal_rendering(self):
        """Test score pie chart with normal score."""
        result = self.charts.render_score_pie_chart(score=75, risk_level="low")

        # Verify structure
        self.assertIn('class="score-pie-container"', result)
        self.assertIn('class="score-pie"', result)

        # Verify score text
        self.assertIn("75", result)

    def test_score_pie_chart_svg_structure(self):
        """Test that pie chart contains SVG elements."""
        result = self.charts.render_score_pie_chart(score=60, risk_level="medium")

        # Verify SVG present
        self.assertIn("<svg", result)

        # Verify circle elements
        self.assertIn("<circle", result)

        # Should have viewBox
        self.assertIn("viewBox", result)

    def test_score_pie_chart_risk_colors(self):
        """Test that risk level affects chart colors via SVG stroke."""
        # Colors are embedded in SVG stroke attribute
        result_low = self.charts.render_score_pie_chart(score=50, risk_level="low")
        result_critical = self.charts.render_score_pie_chart(
            score=50, risk_level="critical"
        )

        # Both should have SVG circles with stroke colors
        self.assertIn("stroke=", result_low)
        self.assertIn("stroke=", result_critical)

        # Different risk levels should have different colors
        self.assertNotEqual(result_low, result_critical)

    # === render_vulnerability_grid tests ===

    def test_vulnerability_grid_normal_counts(self):
        """Test vulnerability grid with normal counts."""
        vulns = {"critical": 3, "high": 5, "moderate": 8, "low": 12}
        result = self.charts.render_vulnerability_grid(vulns)

        # Verify structure
        self.assertIn('class="vuln-grid"', result)

        # Verify all severity levels
        self.assertIn("critical", result)
        self.assertIn("high", result)
        self.assertIn("moderate", result)
        self.assertIn("low", result)

        # Verify counts
        self.assertIn("3", result)
        self.assertIn("5", result)
        self.assertIn("8", result)
        self.assertIn("12", result)

    def test_vulnerability_grid_all_zeros(self):
        """Test vulnerability grid with all zero counts."""
        vulns = {"critical": 0, "high": 0, "moderate": 0, "low": 0}
        result = self.charts.render_vulnerability_grid(vulns)

        # Should render zeros
        self.assertIn('class="vuln-grid"', result)
        self.assertIn("0", result)

    def test_vulnerability_grid_structure(self):
        """Test vulnerability grid has correct structure."""
        vulns = {"critical": 1, "high": 2, "moderate": 3, "low": 4}
        result = self.charts.render_vulnerability_grid(vulns)

        # Should have grid with severity boxes
        self.assertIn('class="vuln-grid"', result)

        # Should display all severity levels
        self.assertIn("Critical", result)
        self.assertIn("High", result)
        self.assertIn("Moderate", result)
        self.assertIn("Low", result)

    # === render_mini_gauge tests ===

    def test_mini_gauge_normal_score(self):
        """Test mini gauge with normal score."""
        result = self.charts.render_mini_gauge(score=85)

        # Verify compact structure
        self.assertIn('class="mini-gauge"', result)

        # Verify score
        self.assertIn("85", result)

    def test_mini_gauge_compact_structure(self):
        """Test that mini gauge is compact (for table cells)."""
        result = self.charts.render_mini_gauge(score=50)

        # Should be smaller than regular gauge
        # Verify it doesn't have full gauge structure
        self.assertNotIn('class="security-gauge"', result)

        # Verify mini-specific class
        self.assertIn("mini-gauge", result)

    # === render dispatcher test ===

    def test_render_dispatcher_routes_correctly(self):
        """Test that render() dispatcher routes to correct methods."""
        # Test each chart type
        risk_bar = self.charts.render("risk_bar", critical=1, high=2, medium=3, low=4)
        self.assertIn("chart-bar", risk_bar)

        gauge = self.charts.render("security_gauge", score=75, risk_level="low")
        self.assertIn("security-gauge", gauge)

        pie = self.charts.render("score_pie", score=60, risk_level="medium")
        self.assertIn("score-pie", pie)

        grid = self.charts.render("vuln_grid", vulnerabilities={"critical": 1})
        self.assertIn("vuln-grid", grid)

        mini = self.charts.render("mini_gauge", score=80)
        self.assertIn("mini-gauge", mini)

        # Test unknown chart type
        unknown = self.charts.render("invalid_type")
        self.assertIn("Unknown chart type", unknown)


if __name__ == "__main__":
    unittest.main()
