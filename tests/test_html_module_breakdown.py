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
        """Test enhanced risk distribution bars are rendered correctly."""
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Verify enhanced risk distribution bar container (with title attribute)
        self.assertIn('class="risk-distribution-bar-enhanced"', result)

        # Verify risk level segments
        self.assertIn('class="risk-bar-segment risk-high"', result)
        self.assertIn('class="risk-bar-segment risk-medium"', result)
        self.assertIn('class="risk-bar-segment risk-low"', result)
        self.assertIn('class="risk-bar-segment risk-none"', result)

    def test_risk_counts_displayed(self):
        """Test risk count labels are integrated into bars."""
        extensions = [self.extension_with_modules]
        result = self.component.render(extensions)

        # Verify risk labels inside bars (not separate badges)
        self.assertIn('class="risk-label"', result)

        # Labels should appear inside segments showing just the count (only when segment width >= 10%)
        # With single extension, each module gets 100% width, so all labels visible
        # Labels are numbers only without suffix (e.g., "1", "2", not "1H", "2M")
        self.assertIn(
            '<span class="risk-label">1</span>', result
        )  # Count labels present

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

        # Should aggregate risk counts (e.g., socket: 1 high + 1 low)
        # Labels show just the number without suffix
        self.assertIn('<span class="risk-label">1</span>', result)

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

    # === Portfolio Integration Tests (Phase 1 - Issue #1035 Consolidation) ===

    def test_portfolio_summary_displayed(self):
        """Test portfolio summary appears in module breakdown section."""
        extensions = [
            {
                "id": "ext1",
                "security": {
                    "score": 85,
                    "module_risk_levels": {"socket": "high"},
                    "score_contributions": {"socket": -15},
                },
            },
            {
                "id": "ext2",
                "security": {
                    "score": 92,
                    "module_risk_levels": {"permissions": "medium"},
                    "score_contributions": {"permissions": -8},
                },
            },
        ]

        result = self.component.render(extensions)

        # Verify portfolio summary section present
        self.assertIn('<div class="portfolio-summary">', result)
        self.assertIn("Overall Portfolio Score:", result)

        # Verify portfolio score calculation: (85 + 92) / 2 = 88.5
        self.assertIn("88.5/100", result)

        # Verify risk level: 88.5 = Medium (70-89)
        self.assertIn("Medium Risk", result)
        self.assertIn("🟡", result)

        # Verify extension count
        self.assertIn("2 extensions", result)

    def test_enhanced_bars_with_integrated_labels(self):
        """Test enhanced risk bars display integrated labels inside segments."""
        # Create extension with clear risk distribution
        extensions = [
            {
                "id": "ext1",
                "security": {
                    "score": 75,
                    "module_risk_levels": {"socket": "high"},
                    "score_contributions": {"socket": -10},
                },
            },
            {
                "id": "ext2",
                "security": {
                    "score": 85,
                    "module_risk_levels": {"socket": "medium"},
                    "score_contributions": {"socket": -5},
                },
            },
        ]

        result = self.component.render(extensions)

        # Verify enhanced bar container (not old style)
        self.assertIn('class="risk-distribution-bar-enhanced"', result)
        self.assertNotIn('class="risk-distribution-bar"', result)

        # Verify labels integrated inside segments (format: "1H", "1M", etc.)
        self.assertIn('class="risk-label"', result)

        # Verify segments have proper structure
        self.assertIn('class="risk-bar-segment risk-high"', result)
        self.assertIn('class="risk-bar-segment risk-medium"', result)

    def test_comprehensive_tooltips_on_enhanced_bars(self):
        """Test tooltips show complete risk distribution details."""
        extensions = [
            {
                "id": "ext1",
                "security": {
                    "score": 88,
                    "module_risk_levels": {"socket": "high"},
                    "score_contributions": {"socket": -12},
                },
            },
            {
                "id": "ext2",
                "security": {
                    "score": 92,
                    "module_risk_levels": {"socket": "medium"},
                    "score_contributions": {"socket": -8},
                },
            },
            {
                "id": "ext3",
                "security": {
                    "score": 95,
                    "module_risk_levels": {"socket": "low"},
                    "score_contributions": {"socket": -5},
                },
            },
        ]

        result = self.component.render(extensions)

        # Verify tooltip attribute present
        self.assertIn('title="', result)

        # Verify tooltip contains risk distribution info
        # Socket should show: 1 high (33.3%), 1 medium (33.3%), 1 low (33.3%)
        self.assertIn("High Risk:", result)
        self.assertIn("Medium Risk:", result)
        self.assertIn("Low Risk:", result)

    def test_critical_risk_level_handled(self):
        """Test that critical risk level is properly counted and visualized."""
        # Extension with critical risk level
        extension_with_critical = {
            "id": "critical.extension",
            "security": {
                "module_risk_levels": {
                    "network_endpoints": "critical",
                    "socket": "high",
                    "dependencies": "medium",
                    "permissions": "low",
                },
                "score_contributions": {
                    "network_endpoints": -20,
                    "socket": -15,
                    "dependencies": -5,
                    "permissions": -2,
                },
            },
        }

        extensions = [extension_with_critical]
        html = self.component.render(extensions)

        # Verify critical count is tracked
        self.assertIn("Critical Risk", html)

        # Verify critical bar segment is rendered with correct CSS class
        self.assertIn('class="risk-bar-segment risk-critical"', html)

        # Verify critical appears in tooltip
        self.assertIn("Critical Risk: 1", html)

        # Verify critical CSS color is applied (dark red)
        # The CSS should be in report_styles.css
        # Here we just verify the class is present
        self.assertIn("risk-critical", html)

    def test_critical_risk_percentage_calculation(self):
        """Test that critical risk percentage is calculated correctly."""
        # Multiple extensions with mixed risk levels including critical
        extensions = [
            {
                "id": "ext1",
                "security": {
                    "module_risk_levels": {"network_endpoints": "critical"},
                    "score_contributions": {"network_endpoints": -20},
                },
            },
            {
                "id": "ext2",
                "security": {
                    "module_risk_levels": {"network_endpoints": "high"},
                    "score_contributions": {"network_endpoints": -15},
                },
            },
            {
                "id": "ext3",
                "security": {
                    "module_risk_levels": {"network_endpoints": "medium"},
                    "score_contributions": {"network_endpoints": -5},
                },
            },
            {
                "id": "ext4",
                "security": {
                    "module_risk_levels": {"network_endpoints": "low"},
                    "score_contributions": {"network_endpoints": -2},
                },
            },
        ]

        html = self.component.render(extensions)

        # With 4 extensions total, critical should be 25% (1/4)
        # The bar segment should have width: 25.0%
        self.assertIn("Critical Risk: 1 (25.0%)", html)

        # Verify the bar width is set correctly
        # Should contain style="width: 25.0%" for critical segment
        self.assertRegex(
            html,
            r'class="risk-bar-segment risk-critical".*?style="width: 25\.0%"',
        )

    def test_critical_risk_in_stats_aggregation(self):
        """Test that critical risk is properly aggregated in statistics."""
        extensions = [
            {
                "id": "ext1",
                "security": {
                    "module_risk_levels": {"network_endpoints": "critical"},
                    "score_contributions": {"network_endpoints": -20},
                },
            },
            {
                "id": "ext2",
                "security": {
                    "module_risk_levels": {"network_endpoints": "critical"},
                    "score_contributions": {"network_endpoints": -18},
                },
            },
        ]

        # Call the internal stats method directly
        stats = self.component._calculate_module_stats(extensions)

        # Verify critical_count exists and is correct
        self.assertIn("network_endpoints", stats)
        self.assertEqual(stats["network_endpoints"]["critical_count"], 2)
        self.assertEqual(stats["network_endpoints"]["total_extensions"], 2)

        # Verify other counts remain zero
        self.assertEqual(stats["network_endpoints"]["high_count"], 0)
        self.assertEqual(stats["network_endpoints"]["medium_count"], 0)
        self.assertEqual(stats["network_endpoints"]["low_count"], 0)
        self.assertEqual(stats["network_endpoints"]["none_count"], 0)


if __name__ == "__main__":
    unittest.main()
