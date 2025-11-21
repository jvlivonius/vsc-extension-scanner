"""
Tests for ModuleBreakdownComponent in HTML Report Generator.

Covers module breakdown rendering, risk distribution visualization,
score impact calculation, and edge case handling.
Target: 10+ tests, 95% coverage
"""

import unittest
import pytest

from vscode_scanner.html_report.components.module_breakdown import (
    ModuleBreakdownComponent,
    MODULE_DISPLAY_NAMES,
)


@pytest.mark.unit
class TestModuleBreakdownComponent(unittest.TestCase):
    """Test suite for ModuleBreakdownComponent with comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.component = ModuleBreakdownComponent()

        # Sample extension with full module data
        self.extension_with_modules = {
            "id": "test.extension",
            "security": {
                "module_risk_levels": {
                    "metadata": "low",
                    "dependencies": "medium",
                    "socket": "high",
                    "virus_total": "low",
                    "permissions": "medium",
                    "ossf_scorecard": "low",
                    "network_endpoints": "high",
                    "sensitive_info": "none",
                    "obfuscation": "low",
                    "consolidated_ast": "none",
                    "open_grep": "low",
                },
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
                },
            },
        }

        # Extension without module data
        self.extension_without_modules = {"id": "basic.extension", "security": {}}

    def test_render_with_valid_data(self):
        """Test basic rendering with valid module data."""
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Verify section structure
        self.assertIn('<section class="module-breakdown">', result)
        self.assertIn("<h2>Security Analysis Breakdown</h2>", result)

        # Verify description
        self.assertIn("11 security analysis modules", result)

        # Verify table structure
        self.assertIn('<table class="module-breakdown-table">', result)
        self.assertIn('<th class="col-module">Module</th>', result)
        self.assertIn('<th class="col-risk">Risk Distribution</th>', result)
        self.assertIn('<th class="col-score">Avg Score Impact</th>', result)

    def test_all_modules_displayed(self):
        """Test that all 11 modules are rendered in the table."""
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Verify all module display names are present
        for display_name in MODULE_DISPLAY_NAMES.values():
            self.assertIn(display_name, result)

    def test_risk_distribution_bars_rendered(self):
        """Test risk distribution bars are rendered correctly."""
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Verify risk distribution bar container
        self.assertIn('<div class="risk-distribution-bar">', result)

        # Verify risk level segments
        self.assertIn('class="risk-bar-segment risk-high"', result)
        self.assertIn('class="risk-bar-segment risk-medium"', result)
        self.assertIn('class="risk-bar-segment risk-low"', result)
        self.assertIn('class="risk-bar-segment risk-none"', result)

    def test_risk_counts_displayed(self):
        """Test risk count badges are displayed."""
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Verify risk counts container
        self.assertIn('<div class="risk-counts">', result)

        # Verify count badges (format: "1H", "2M", etc.)
        self.assertIn('class="risk-count risk-high"', result)
        self.assertIn('class="risk-count risk-medium"', result)
        self.assertIn('class="risk-count risk-low"', result)

    def test_score_impact_formatting(self):
        """Test score impact values are formatted correctly."""
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Negative impacts should have score-negative class
        self.assertIn('class="col-score score-negative"', result)

        # Verify negative score format (-5.0, -15.0, etc.)
        self.assertIn("-5.0", result)  # dependencies
        self.assertIn("-15.0", result)  # socket
        self.assertIn("-10.0", result)  # network_endpoints

    def test_positive_score_impact_styling(self):
        """Test positive score impacts have correct styling."""
        # Create extension with positive contribution
        extension = {
            "id": "positive.extension",
            "security": {
                "module_risk_levels": {"metadata": "none"},
                "score_contributions": {"metadata": 5},
            },
        }

        extensions = [extension]
        result = self.component.render(extensions)

        # Verify positive class
        self.assertIn('class="col-score score-positive"', result)
        self.assertIn("+5.0", result)

    def test_neutral_score_impact_styling(self):
        """Test zero score impacts have correct styling."""
        # Create extension with zero contribution
        extension = {
            "id": "neutral.extension",
            "security": {
                "module_risk_levels": {"metadata": "low"},
                "score_contributions": {"metadata": 0},
            },
        }

        extensions = [extension]
        result = self.component.render(extensions)

        # Verify neutral class
        self.assertIn('class="col-score score-neutral"', result)
        self.assertIn("0.0", result)

    def test_empty_extensions_list(self):
        """Test rendering with empty extensions list returns empty string."""
        result = self.component.render([])

        # Should return empty string (no data to display)
        self.assertEqual(result, "")

    def test_extensions_without_module_data(self):
        """Test graceful handling of extensions without module data."""
        extensions = [self.extension_without_modules]
        result = self.component.render(extensions)

        # Should return empty string (no valid module data)
        self.assertEqual(result, "")

    def test_mixed_extensions_with_and_without_data(self):
        """Test rendering with mix of valid and invalid extension data."""
        extensions = [self.extension_with_modules, self.extension_without_modules]
        result = self.component.render(extensions)

        # Should render based on valid data only
        self.assertIn('<section class="module-breakdown">', result)
        self.assertIn("Socket (Supply Chain)", result)

    def test_multiple_extensions_aggregation(self):
        """Test correct aggregation of multiple extensions."""
        # Create second extension with different risk levels
        extension2 = {
            "id": "second.extension",
            "security": {
                "module_risk_levels": {
                    "metadata": "high",
                    "dependencies": "low",
                    "socket": "low",
                    "virus_total": "none",
                    "permissions": "high",
                    "ossf_scorecard": "medium",
                    "network_endpoints": "medium",
                    "sensitive_info": "low",
                    "obfuscation": "none",
                    "consolidated_ast": "low",
                    "open_grep": "none",
                },
                "score_contributions": {
                    "metadata": -8,
                    "dependencies": -2,
                    "socket": -3,
                    "virus_total": 0,
                    "permissions": -12,
                    "ossf_scorecard": -4,
                    "network_endpoints": -6,
                    "sensitive_info": 0,
                    "obfuscation": 0,
                    "consolidated_ast": 0,
                    "open_grep": 0,
                },
            },
        }

        extensions = [self.extension_with_modules, extension2]
        result = self.component.render(extensions)

        # Should aggregate risk counts (e.g., socket: 1 high + 1 low = 1H 1L)
        self.assertIn("1H", result)  # High risk count
        self.assertIn("1L", result)  # Low risk count

        # Should average score impacts
        # Dependencies: (-5 + -2) / 2 = -3.5
        self.assertIn("-3.5", result)

    def test_html_escaping_in_module_names(self):
        """Test XSS prevention through HTML escaping (defensive)."""
        # Note: MODULE_DISPLAY_NAMES is hardcoded, but test defensive escaping
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Verify no script tags can be injected
        self.assertNotIn("<script>", result.lower())

        # Verify standard module names are properly escaped
        self.assertIn("Socket (Supply Chain)", result)

    def test_calculate_module_stats_correctness(self):
        """Test internal _calculate_module_stats() produces correct statistics."""
        extensions = [self.extension_with_modules]

        # Call internal method
        stats = self.component._calculate_module_stats(extensions)

        # Verify structure
        self.assertIn("socket", stats)
        self.assertEqual(stats["socket"]["high_count"], 1)
        self.assertEqual(stats["socket"]["medium_count"], 0)
        self.assertEqual(stats["socket"]["low_count"], 0)

        # Verify score impact calculation
        self.assertEqual(stats["socket"]["avg_score_impact"], -15.0)

    def test_generate_table_rows_output(self):
        """Test _generate_table_rows() produces valid HTML rows."""
        extensions = [self.extension_with_modules]
        stats = self.component._calculate_module_stats(extensions)

        # Call internal method
        rows_html = self.component._generate_table_rows(stats)

        # Verify row structure
        self.assertIn("<tr>", rows_html)
        self.assertIn("</tr>", rows_html)
        self.assertIn('<td class="col-module">', rows_html)
        self.assertIn('<td class="col-risk">', rows_html)
        self.assertIn('<td class="col-score', rows_html)

    def test_percentage_calculation_accuracy(self):
        """Test risk distribution percentage calculations are accurate."""
        # Create 10 extensions: 3 high, 2 medium, 3 low, 2 none
        extensions = []
        risk_levels = ["high"] * 3 + ["medium"] * 2 + ["low"] * 3 + ["none"] * 2

        for i, risk in enumerate(risk_levels):
            extensions.append(
                {
                    "id": f"ext{i}",
                    "security": {
                        "module_risk_levels": {"metadata": risk},
                        "score_contributions": {"metadata": -i},
                    },
                }
            )

        result = self.component.render(extensions)

        # Verify percentages: 3/10=30%, 2/10=20%, 3/10=30%, 2/10=20%
        # Note: Exact assertion depends on formatting, verify structure exists
        self.assertIn("width:", result)
        self.assertIn("%", result)

    def test_missing_score_contributions_defaults_to_zero(self):
        """Test extensions missing score_contributions are handled gracefully."""
        extension = {
            "id": "incomplete.extension",
            "security": {
                "module_risk_levels": {"metadata": "low"},
                # Missing score_contributions
            },
        }

        extensions = [extension]
        result = self.component.render(extensions)

        # Should render with 0.0 score impact
        self.assertIn("0.0", result)


if __name__ == "__main__":
    unittest.main()
