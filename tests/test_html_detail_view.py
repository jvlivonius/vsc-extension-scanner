"""
Tests for DetailViewComponent in HTML Report Generator.

Covers detailed extension info, security analysis, metadata, dependencies.
Target: 25 tests, 70% coverage
"""

import unittest
import pytest

from vscode_scanner.html_report.components.detail_view import DetailViewComponent


@pytest.mark.unit
class TestDetailViewComponent(unittest.TestCase):
    """Test suite for DetailViewComponent with comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.detail_view = DetailViewComponent()

        self.minimal_ext = {
            "id": "test.ext",
            "name": "TestExt",
            "display_name": "Test Extension",
            "version": "1.0.0",
            "description": "Test description",
            "publisher": {"id": "test", "name": "Test", "verified": False},
            "security": {"risk_level": "low", "score": 85},
            "statistics": {},
        }

        self.full_ext = {
            "id": "full.ext",
            "name": "FullExt",
            "display_name": "Full Extension",
            "version": "2.0.0",
            "description": "Full test description",
            "license": "MIT",
            "repository_url": "https://github.com/test/repo",
            "homepage_url": "https://example.com",
            "keywords": ["test", "extension", "sample"],
            "categories": ["Programming Languages", "Themes"],
            "last_updated": "2024-01-15T10:00:00",
            "installed_at": "2024-01-01T12:00:00",
            "last_scanned_at": "2024-01-20T08:30:00",
            "publisher": {
                "id": "verified",
                "name": "Verified Publisher",
                "verified": True,
                "domain": "https://verified.example.com",
            },
            "security": {
                "risk_level": "high",
                "score": 45,
                "risk_factors": [
                    {
                        "severity": "high",
                        "type": "Network Access",
                        "description": "Makes network requests",
                    }
                ],
                "security_notes": ["Note 1", "Note 2"],
                "vulnerabilities": {"critical": 2, "high": 3, "moderate": 1, "low": 0},
                "module_risk_levels": {
                    "network_access": "high",
                    "file_system": "medium",
                },
                "dependencies": {
                    "total_count": 15,
                    "runtime_count": 10,
                    "dev_count": 5,
                    "with_vulnerabilities": 2,
                    "list": [
                        {
                            "name": "lodash",
                            "version": "4.17.21",
                            "type": "runtime",
                            "risk": "low",
                            "has_vulnerabilities": False,
                        },
                        {
                            "name": "axios",
                            "version": "0.21.0",
                            "type": "runtime",
                            "risk": "high",
                            "has_vulnerabilities": True,
                        },
                    ],
                },
            },
            "statistics": {"installs": 2500000, "rating": 4.7, "rating_count": 3500},
            "raw_analysis_id": "test-analysis-123",
        }

    # === Basic Rendering Tests ===

    def test_render_basic_structure(self):
        """Test basic structure of detail view."""
        result = self.detail_view.render(self.minimal_ext)

        # Verify main structure
        self.assertIn('class="extension-details"', result)
        self.assertIn('class="detail-header"', result)
        self.assertIn("<h2>Test Extension", result)

    def test_render_with_version_badge(self):
        """Test that version badge is displayed."""
        result = self.detail_view.render(self.minimal_ext)

        self.assertIn('class="version-badge"', result)
        self.assertIn("v1.0.0", result)

    def test_render_all_three_sections(self):
        """Test that all three main sections are rendered."""
        result = self.detail_view.render(self.full_ext)

        # Verify all sections present
        self.assertIn("🔒 Security Analysis", result)
        self.assertIn("📝 Metadata", result)
        self.assertIn("📦 Dependencies", result)

    # === Metadata Section Tests ===

    def test_metadata_publisher_display(self):
        """Test publisher name and ID display."""
        result = self.detail_view.render(self.minimal_ext)

        self.assertIn("Publisher:", result)
        self.assertIn("Test", result)

    def test_metadata_verified_badge(self):
        """Test verified publisher badge."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Verified Publisher", result)
        self.assertIn("verified-badge-green", result)
        self.assertIn("✓", result)

    def test_metadata_description(self):
        """Test description display."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Description:", result)
        self.assertIn("Full test description", result)

    def test_metadata_optional_fields(self):
        """Test optional metadata fields (homepage, keywords, categories)."""
        result = self.detail_view.render(self.full_ext)

        # Homepage
        self.assertIn("Homepage:", result)
        self.assertIn("https://example.com", result)

        # Keywords
        self.assertIn("Keywords:", result)
        self.assertIn("test, extension, sample", result)

        # Categories
        self.assertIn("Categories:", result)
        self.assertIn("Programming Languages, Themes", result)

    def test_metadata_statistics(self):
        """Test statistics display (installs, rating)."""
        result = self.detail_view.render(self.full_ext)

        # Installs (2,500,000 → 2.5M)
        self.assertIn("Installs:", result)
        self.assertIn("2.5M", result)

        # Rating
        self.assertIn("Rating:", result)
        self.assertIn("4.7", result)
        self.assertIn("3.5K reviews", result)  # 3500 → 3.5K

    def test_metadata_dates(self):
        """Test date fields display."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Last Updated:", result)
        self.assertIn("2024-01-15T10:00:00", result)
        self.assertIn("Installed:", result)
        self.assertIn("2024-01-01T12:00:00", result)

    def test_metadata_links(self):
        """Test repository and marketplace links."""
        result = self.detail_view.render(self.full_ext)

        # Repository link
        self.assertIn("Repository:", result)
        self.assertIn('href="https://github.com/test/repo"', result)

        # Marketplace link
        self.assertIn("Marketplace:", result)
        self.assertIn(
            "https://marketplace.visualstudio.com/items?itemName=full.ext", result
        )

    # === Security Section Tests ===

    def test_security_score_pie_chart(self):
        """Test security score pie chart integration."""
        result = self.detail_view.render(self.full_ext)

        # Should have pie chart (from ChartComponents)
        self.assertIn("score-pie", result)

    def test_security_vulnerability_grid(self):
        """Test vulnerability grid integration."""
        result = self.detail_view.render(self.full_ext)

        # Should have vulnerability grid (from ChartComponents)
        self.assertIn("vuln-grid", result)

    def test_security_risk_badge(self):
        """Test risk level badge in security section."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("risk-badge risk-high", result)
        self.assertIn("HIGH RISK", result)

    def test_security_module_risk_levels(self):
        """Test module risk levels display."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Module Risks:", result)
        self.assertIn("Network Access", result)
        self.assertIn("File System", result)
        self.assertIn("risk-badge risk-high", result)  # network_access → high
        self.assertIn("risk-badge risk-medium", result)  # file_system → medium

    def test_security_risk_factors(self):
        """Test risk factors display."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Risk Factors (1):", result)
        self.assertIn("[HIGH]", result)
        self.assertIn("Network Access", result)
        self.assertIn("Makes network requests", result)

    def test_security_notes(self):
        """Test security notes display."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Security Notes:", result)
        self.assertIn("Note 1", result)
        self.assertIn("Note 2", result)

    def test_security_vscan_link(self):
        """Test vscan.dev analysis link."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("View on vscan.dev:", result)
        self.assertIn("https://vscan.dev/?analysisId=test-analysis-123", result)

    # === Dependencies Section Tests ===

    def test_dependencies_not_shown_when_zero(self):
        """Test that dependencies section is hidden when none exist."""
        result = self.detail_view.render(self.minimal_ext)

        # Should NOT show dependencies section
        self.assertNotIn("📦 Dependencies", result)

    def test_dependencies_counts(self):
        """Test dependencies count display."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Total Dependencies:", result)
        self.assertIn("15 (Runtime: 10, Dev: 5)", result)
        self.assertIn("With Vulnerabilities:", result)
        self.assertIn("2", result)

    def test_dependencies_runtime_list(self):
        """Test runtime dependencies list."""
        result = self.detail_view.render(self.full_ext)

        self.assertIn("Runtime Dependencies (2)", result)
        self.assertIn("lodash", result)
        self.assertIn("v4.17.21", result)
        self.assertIn("axios", result)
        self.assertIn("v0.21.0", result)

    def test_dependencies_collapsible_structure(self):
        """Test that dependencies are collapsible."""
        result = self.detail_view.render(self.full_ext)

        # Should have collapsible structure
        self.assertIn("dep-list-collapsible", result)
        self.assertIn('onclick="toggleDependencies', result)
        self.assertIn('style="display: none;"', result)  # Hidden by default

    def test_dependencies_vulnerability_indicator(self):
        """Test vulnerability warning on dependencies."""
        result = self.detail_view.render(self.full_ext)

        # axios has vulnerabilities
        self.assertIn("⚠", result)

    # === Edge Cases and Security ===

    def test_html_escaping(self):
        """Test XSS prevention through HTML escaping."""
        malicious = self.minimal_ext.copy()
        malicious["description"] = '<script>alert("xss")</script>'

        result = self.detail_view.render(malicious)

        # Should escape HTML
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)

    def test_missing_optional_fields(self):
        """Test graceful handling of missing optional fields."""
        minimal = {"id": "test", "security": {}}
        result = self.detail_view.render(minimal)

        # Should not crash, use defaults
        self.assertIn("extension-details", result)

    def test_dependencies_dev_list(self):
        """Test dev dependencies list rendering."""
        # Create extension with dev dependencies
        ext_with_dev = self.full_ext.copy()
        ext_with_dev["security"]["dependencies"]["list"].append(
            {
                "name": "jest",
                "version": "27.0.0",
                "type": "dev",
                "risk": "low",
                "has_vulnerabilities": False,
            }
        )

        result = self.detail_view.render(ext_with_dev)

        # Should show dev dependencies section
        self.assertIn("Dev Dependencies", result)
        self.assertIn("jest", result)
        self.assertIn("v27.0.0", result)


if __name__ == "__main__":
    unittest.main()
