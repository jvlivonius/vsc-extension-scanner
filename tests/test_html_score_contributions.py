"""
Tests for ScoreContributionsComponent - Score Breakdown Chart.

Covers chart data preparation, color coding, Chart.js integration, and edge cases.
Target: 100% coverage of score_contributions.py
"""

import unittest
import pytest
import json

from vscode_scanner.html_report.components.score_contributions import (
    ScoreContributionsComponent,
    MODULE_ORDER,
)


@pytest.mark.unit
class TestScoreContributionsComponent(unittest.TestCase):
    """Test suite for ScoreContributionsComponent."""

    def setUp(self):
        """Set up test fixtures."""
        self.component = ScoreContributionsComponent()

        # Extension with full score contributions data
        self.extension_with_scores = {
            "id": "test.extension",
            "security": {
                "score_contributions": {
                    "base": 100,
                    "metadata": 0,
                    "dependencies": -5,
                    "socket": -15,
                    "virus_total": 0,
                    "permissions": -3,
                    "ossf_scorecard": 0,
                    "network_endpoints": -10,
                    "sensitive_info": 0,
                    "obfuscation": -2,
                    "consolidated_ast": 0,
                    "open_grep": 0,
                }
            },
        }

        # Extension with sparse score contributions
        self.extension_sparse_scores = {
            "id": "test.sparse",
            "security": {
                "score_contributions": {
                    "base": 100,
                    "socket": -8,
                    "permissions": -2,
                }
            },
        }

        # Extension without score contributions
        self.extension_no_scores = {"id": "test.no-scores", "security": {}}

    # === Chart Rendering Tests ===

    def test_render_with_valid_data(self):
        """Test chart rendering with complete score contributions."""
        extensions = [self.extension_with_scores]
        result = self.component.render(extensions)

        # Verify section structure
        self.assertIn('<section class="score-contributions">', result)
        self.assertIn("<h2>📊 Portfolio Security Analysis</h2>", result)

        # Verify portfolio summary
        self.assertIn('<div class="portfolio-summary">', result)
        self.assertIn("Overall Portfolio Score:", result)

        # Verify description
        self.assertIn(
            "This chart shows the average contribution of each security module",
            result,
        )

        # Verify canvas element
        self.assertIn('<canvas id="scoreContributionsChart"', result)
        self.assertIn('aria-label="Portfolio security contributions chart"', result)

        # Verify Chart.js configuration
        self.assertIn("new Chart(ctx, config)", result)
        self.assertIn("type: 'bar'", result)
        self.assertIn("indexAxis: 'y'", result)  # Horizontal bars

    def test_render_with_empty_extensions(self):
        """Test rendering with no extensions returns empty string."""
        result = self.component.render([])
        self.assertEqual(result, "")

    def test_render_without_score_contributions(self):
        """Test rendering when extension lacks score_contributions field."""
        extensions = [self.extension_no_scores]
        result = self.component.render(extensions)
        self.assertEqual(result, "")

    # === Chart Data Preparation Tests ===

    def test_chart_data_preparation_full(self):
        """Test chart data preparation with all modules having contributions."""
        extensions = [self.extension_with_scores]
        chart_data = self.component._prepare_chart_data(extensions)

        # Verify data structure
        self.assertIn("labels", chart_data)
        self.assertIn("values", chart_data)
        self.assertIn("colors", chart_data)

        # Verify base score is excluded (always 100, not useful)
        self.assertNotIn("Base Score", chart_data["labels"])
        self.assertNotIn(100, chart_data["values"])

        # Verify non-zero contributions are included
        self.assertIn("Socket (Supply Chain)", chart_data["labels"])
        self.assertIn(-15, chart_data["values"])
        self.assertIn("Dependencies", chart_data["labels"])
        self.assertIn(-5, chart_data["values"])

        # Verify zero contributions are excluded
        # Count: dependencies (-5) + socket (-15) + permissions (-3) +
        #        network_endpoints (-10) + obfuscation (-2) = 5 total
        self.assertEqual(len(chart_data["labels"]), 5)
        self.assertEqual(len(chart_data["values"]), 5)
        self.assertEqual(len(chart_data["colors"]), 5)

    def test_chart_data_preparation_sparse(self):
        """Test chart data preparation with sparse score contributions."""
        extensions = [self.extension_sparse_scores]
        chart_data = self.component._prepare_chart_data(extensions)

        # Verify only non-zero contributions included (base excluded)
        expected_labels = ["Socket (Supply Chain)", "Permissions"]
        self.assertEqual(chart_data["labels"], expected_labels)

        expected_values = [-8, -2]
        self.assertEqual(chart_data["values"], expected_values)

        # Verify correct color count
        self.assertEqual(len(chart_data["colors"]), len(chart_data["labels"]))

    def test_chart_data_preparation_missing(self):
        """Test chart data preparation when score_contributions is missing."""
        extensions = [self.extension_no_scores]
        chart_data = self.component._prepare_chart_data(extensions)

        # Verify empty data structure
        self.assertEqual(chart_data["labels"], [])
        self.assertEqual(chart_data["values"], [])
        self.assertEqual(chart_data["colors"], [])

    def test_chart_data_empty_extensions_list(self):
        """Test chart data preparation with empty extensions list."""
        chart_data = self.component._prepare_chart_data([])

        # Verify empty data structure
        self.assertEqual(chart_data["labels"], [])
        self.assertEqual(chart_data["values"], [])
        self.assertEqual(chart_data["colors"], [])

    # === Color Coding Tests ===

    def test_chart_color_coding_positive(self):
        """Test color coding for positive score contributions."""
        color = self.component._get_color_for_value(10)
        self.assertEqual(color, "#28a745")  # Green

        color = self.component._get_color_for_value(100)
        self.assertEqual(color, "#28a745")  # Green

    def test_chart_color_coding_minor_negative(self):
        """Test color coding for minor negative contributions (-5 to 0)."""
        color = self.component._get_color_for_value(-5)
        self.assertEqual(color, "#ffc107")  # Yellow

        color = self.component._get_color_for_value(-3)
        self.assertEqual(color, "#ffc107")  # Yellow

        color = self.component._get_color_for_value(-1)
        self.assertEqual(color, "#ffc107")  # Yellow

    def test_chart_color_coding_significant_negative(self):
        """Test color coding for significant negative contributions (< -5)."""
        color = self.component._get_color_for_value(-6)
        self.assertEqual(color, "#dc3545")  # Red

        color = self.component._get_color_for_value(-15)
        self.assertEqual(color, "#dc3545")  # Red

        color = self.component._get_color_for_value(-100)
        self.assertEqual(color, "#dc3545")  # Red

    def test_color_coding_in_chart_data(self):
        """Test that colors are correctly applied in chart data preparation."""
        extensions = [self.extension_with_scores]
        chart_data = self.component._prepare_chart_data(extensions)

        # Find indices of specific contributions
        socket_idx = chart_data["labels"].index("Socket (Supply Chain)")
        permissions_idx = chart_data["labels"].index("Permissions")

        # Verify color assignments
        self.assertEqual(
            chart_data["colors"][socket_idx], "#dc3545"
        )  # -15 = Red (significant)
        self.assertEqual(
            chart_data["colors"][permissions_idx], "#ffc107"
        )  # -3 = Yellow (minor)

    # === Chart.js Integration Tests ===

    def test_chartjs_inclusion(self):
        """Test that Chart.js configuration is properly included in output."""
        extensions = [self.extension_with_scores]
        result = self.component.render(extensions)

        # Verify Chart.js initialization
        self.assertIn("new Chart(ctx, config)", result)

        # Verify chart configuration
        self.assertIn("type: 'bar'", result)
        self.assertIn("indexAxis: 'y'", result)  # Horizontal
        self.assertIn("responsive: true", result)
        self.assertIn("maintainAspectRatio: false", result)

        # Verify title reflects aggregation
        self.assertIn("Average Security Contributions Across 1 Extension", result)

        # Verify legend is hidden (using bar colors instead)
        self.assertIn("legend: {", result)
        self.assertIn("display: false", result)

        # Verify axes configuration
        self.assertIn("scales: {", result)
        self.assertIn("x: {", result)
        self.assertIn("y: {", result)

    def test_json_data_embedding(self):
        """Test that Python data is correctly converted to JSON for JavaScript."""
        extensions = [self.extension_sparse_scores]
        result = self.component.render(extensions)

        # Verify labels are JSON-encoded (base excluded)
        self.assertIn("labels: [", result)
        self.assertNotIn('"Base Score"', result)
        self.assertIn('"Socket (Supply Chain)"', result)

        # Verify values are JSON-encoded (base excluded from chart data)
        self.assertIn("data: [", result)
        self.assertIn("-8", result)

        # Note: "100" appears in portfolio score display (e.g., "0/100")
        # but not in chart data values

        # Verify colors are JSON-encoded
        self.assertIn("backgroundColor: [", result)
        self.assertIn('"#dc3545"', result)  # Red for -8
        self.assertIn('"#ffc107"', result)  # Yellow for -2

    def test_to_json_string_list(self):
        """Test _to_json method with string list."""
        labels = ["Base Score", "Dependencies", "Socket (Supply Chain)"]
        result = self.component._to_json(labels)

        # Parse back to verify correctness
        parsed = json.loads(result)
        self.assertEqual(parsed, labels)

    def test_to_json_number_list(self):
        """Test _to_json method with number list."""
        values = [100, -5, -15, -3]
        result = self.component._to_json(values)

        # Parse back to verify correctness
        parsed = json.loads(result)
        self.assertEqual(parsed, values)

    def test_to_json_empty_list(self):
        """Test _to_json method with empty list."""
        result = self.component._to_json([])
        self.assertEqual(result, "[]")

    # === Module Order Tests ===

    def test_module_order_matches_breakdown(self):
        """Test that MODULE_ORDER matches module_breakdown.py order."""
        # Verify base score is first
        self.assertEqual(MODULE_ORDER[0][0], "base")
        self.assertEqual(MODULE_ORDER[0][1], "Base Score")

        # Verify all 12 modules are present (base + 11 security modules)
        self.assertEqual(len(MODULE_ORDER), 12)

        # Verify socket module is present
        socket_modules = [m for m in MODULE_ORDER if m[0] == "socket"]
        self.assertEqual(len(socket_modules), 1)
        self.assertEqual(socket_modules[0][1], "Socket (Supply Chain)")

    # === Graceful Degradation Tests ===

    def test_graceful_degradation_no_security_field(self):
        """Test graceful handling when security field is missing."""
        extensions = [{"id": "test.missing-security"}]
        result = self.component.render(extensions)
        self.assertEqual(result, "")

    def test_graceful_degradation_empty_score_contributions(self):
        """Test graceful handling when score_contributions is empty dict."""
        extensions = [{"id": "test.empty", "security": {"score_contributions": {}}}]
        result = self.component.render(extensions)
        self.assertEqual(result, "")

    def test_aggregate_multiple_extensions(self):
        """Test aggregation across multiple extensions calculates averages correctly."""
        # Extension 1: socket=-15, permissions=-3
        # Extension 2: socket=-8, permissions=-2
        # Expected averages: socket=-11.5, permissions=-2.5
        extensions = [
            self.extension_with_scores,
            self.extension_sparse_scores,
        ]
        chart_data = self.component._prepare_chart_data(extensions)

        # Verify aggregation occurred
        self.assertIn("Socket (Supply Chain)", chart_data["labels"])
        self.assertIn("Permissions", chart_data["labels"])

        # Verify averaged values (rounded to 1 decimal)
        socket_idx = chart_data["labels"].index("Socket (Supply Chain)")
        permissions_idx = chart_data["labels"].index("Permissions")

        # socket: (-15 + -8) / 2 = -11.5
        self.assertEqual(chart_data["values"][socket_idx], -11.5)

        # permissions: (-3 + -2) / 2 = -2.5
        self.assertEqual(chart_data["values"][permissions_idx], -2.5)

    def test_aggregate_single_extension(self):
        """Test aggregation with single extension (backward compatibility)."""
        extensions = [self.extension_with_scores]
        chart_data = self.component._prepare_chart_data(extensions)

        # Should work identically to before
        self.assertIn("Dependencies", chart_data["labels"])
        deps_idx = chart_data["labels"].index("Dependencies")
        self.assertEqual(chart_data["values"][deps_idx], -5.0)

        # Verify metadata
        self.assertEqual(chart_data["metadata"]["extension_count"], 1)

    def test_aggregate_includes_zeros(self):
        """Test that aggregation includes zero values in average calculation."""
        # Extension 1: socket=-10, dependencies=-5
        # Extension 2: socket=0, dependencies=0 (implicit)
        # Expected: socket=-5.0, dependencies=-2.5
        ext1 = {
            "id": "ext1",
            "security": {
                "score": 90,
                "score_contributions": {
                    "socket": -10,
                    "dependencies": -5,
                },
            },
        }
        ext2 = {
            "id": "ext2",
            "security": {
                "score": 100,
                "score_contributions": {
                    # No socket or dependencies - implicit zeros
                },
            },
        }

        extensions = [ext1, ext2]
        chart_data = self.component._prepare_chart_data(extensions)

        # Verify socket includes ext2's implicit zero
        self.assertIn("Socket (Supply Chain)", chart_data["labels"])
        socket_idx = chart_data["labels"].index("Socket (Supply Chain)")
        self.assertEqual(chart_data["values"][socket_idx], -5.0)  # (-10 + 0) / 2 = -5.0

        # Verify dependencies includes ext2's implicit zero
        self.assertIn("Dependencies", chart_data["labels"])
        deps_idx = chart_data["labels"].index("Dependencies")
        self.assertEqual(chart_data["values"][deps_idx], -2.5)  # (-5 + 0) / 2 = -2.5

    def test_portfolio_score_calculation(self):
        """Test portfolio score calculation across multiple extensions."""
        # Create extensions with known scores
        ext1 = {
            "id": "ext1",
            "security": {
                "score": 72,
                "score_contributions": {"socket": -10},
            },
        }
        ext2 = {
            "id": "ext2",
            "security": {
                "score": 88,
                "score_contributions": {"permissions": -5},
            },
        }
        ext3 = {
            "id": "ext3",
            "security": {
                "score": 85,
                "score_contributions": {"obfuscation": -3},
            },
        }

        chart_data = self.component._prepare_chart_data([ext1, ext2, ext3])

        # Verify portfolio score: (72 + 88 + 85) / 3 = 81.67 → 81.7
        self.assertEqual(chart_data["metadata"]["portfolio_score"], 81.7)
        self.assertEqual(chart_data["metadata"]["extension_count"], 3)

    def test_portfolio_risk_levels(self):
        """Test risk level determination from portfolio scores."""
        # Test low risk (90-100)
        self.assertEqual(self.component._get_risk_level(95), "low")
        self.assertEqual(self.component._get_risk_level(90), "low")

        # Test medium risk (70-89)
        self.assertEqual(self.component._get_risk_level(85), "medium")
        self.assertEqual(self.component._get_risk_level(70), "medium")

        # Test high risk (50-69)
        self.assertEqual(self.component._get_risk_level(65), "high")
        self.assertEqual(self.component._get_risk_level(50), "high")

        # Test critical risk (0-49)
        self.assertEqual(self.component._get_risk_level(45), "critical")
        self.assertEqual(self.component._get_risk_level(0), "critical")


if __name__ == "__main__":
    unittest.main()
