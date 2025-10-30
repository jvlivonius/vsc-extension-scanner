"""
Tests for OverviewTableComponent in HTML Report Generator.

Covers table generation, row creation, data handling, and integration.
Target: 20 tests, 75% coverage
"""

import unittest
import pytest

from vscode_scanner.html_report.components.overview_table import OverviewTableComponent


@pytest.mark.unit
class TestOverviewTableComponent(unittest.TestCase):
    """Test suite for OverviewTableComponent with comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.table = OverviewTableComponent()
        self.minimal_ext = {
            "id": "test.extension",
            "name": "Test Extension",
            "display_name": "Test Extension",
            "version": "1.0.0",
            "publisher": {"id": "testpub", "name": "Test Publisher", "verified": False},
            "security": {
                "risk_level": "low",
                "score": 85,
                "vulnerabilities": {},
                "dependencies_count": 0,
            },
            "statistics": {},
        }

        self.full_ext = {
            "id": "full.extension",
            "name": "Full Extension",
            "display_name": "Full Test Extension",
            "version": "2.5.3",
            "publisher": {"id": "verified", "name": "Verified Pub", "verified": True},
            "security": {
                "risk_level": "high",
                "score": 45,
                "vulnerabilities": {"critical": 2, "high": 3, "moderate": 1, "low": 0},
                "dependencies_count": 15,
            },
            "statistics": {"installs": 1500000, "rating": 4.5, "rating_count": 1200},
            "last_updated": "2024-01-15T10:00:00",
            "installed_at": "2024-01-01T12:00:00",
            "last_scanned_at": "2024-01-20T08:30:00",
        }

    def test_render_empty_extensions_list(self):
        """Test rendering with empty extensions list."""
        result = self.table.render([])

        # Should still generate table structure
        self.assertIn('<section class="overview-table">', result)
        self.assertIn('<table id="extensions-table">', result)
        self.assertIn("<thead>", result)
        self.assertIn("<tbody>", result)

        # tbody should be empty
        self.assertIn("<tbody>\n                    \n                </tbody>", result)

    def test_render_single_extension(self):
        """Test rendering with single extension."""
        result = self.table.render([self.minimal_ext])

        # Verify table structure
        self.assertIn('<table id="extensions-table">', result)

        # Verify extension data
        self.assertIn("Test Extension", result)
        self.assertIn("1.0.0", result)
        self.assertIn("Test Publisher", result)

    def test_render_multiple_extensions(self):
        """Test rendering with multiple extensions."""
        result = self.table.render([self.minimal_ext, self.full_ext])

        # Should have 4 rows (2 main rows + 2 detail rows)
        row_count = result.count("<tr")
        self.assertGreaterEqual(row_count, 4)

    def test_table_header_columns(self):
        """Test that all 13 column headers are present."""
        result = self.table.render([])

        # Verify all column headers
        expected_headers = [
            "Extension",
            "Version",
            "Publisher",
            "Verified",
            "Risk Level",
            "Security Score",
            "Vulnerabilities",
            "Installs",
            "Rating",
            "Dependencies",
            "Last Updated",
            "Installed",
            "Last Scanned",
        ]

        for header in expected_headers:
            self.assertIn(header, result)

    def test_sortable_columns(self):
        """Test that columns have sortable onclick handlers."""
        result = self.table.render([])

        # Verify sortable columns
        self.assertIn("onclick=\"sortTable('name')\"", result)
        self.assertIn("onclick=\"sortTable('version')\"", result)
        self.assertIn("onclick=\"sortTable('risk')\"", result)

    def test_hidden_columns_by_default(self):
        """Test that optional columns are hidden by default."""
        result = self.table.render([])

        # These columns should have style="display: none;"
        hidden_patterns = [
            "col-score",
            "col-vulnerabilities",
            "col-installs",
            "col-rating",
            "col-dependencies",
            "col-last-updated",
            "col-installed",
            "col-last-scanned",
        ]

        for pattern in hidden_patterns:
            # Check that column exists and has display: none
            self.assertIn(pattern, result)

        # Verify display: none is present for hidden columns
        display_none_count = result.count('style="display: none;"')
        self.assertGreaterEqual(display_none_count, 8)  # At least 8 hidden columns

    def test_extension_row_data_attributes(self):
        """Test that extension rows have correct data attributes."""
        result = self.table.render([self.minimal_ext])

        # Verify data attributes for filtering/sorting
        self.assertIn('data-risk="low"', result)
        self.assertIn('data-name="test extension"', result)  # lowercase
        self.assertIn('data-publisher-name="test publisher"', result)  # lowercase
        self.assertIn('data-verified="false"', result)

    def test_verified_publisher_indicator(self):
        """Test verified publisher checkmark."""
        result = self.table.render([self.full_ext])

        # Verified publisher should have checkmark
        self.assertIn("✓", result)

    def test_unverified_publisher_indicator(self):
        """Test unverified publisher cross."""
        result = self.table.render([self.minimal_ext])

        # Unverified should have cross
        self.assertIn("✗", result)

    def test_risk_badge_rendering(self):
        """Test risk level badge with correct CSS class."""
        result = self.table.render([self.full_ext])

        # Should have risk badge
        self.assertIn("risk-badge risk-high", result)
        self.assertIn("HIGH", result)  # uppercase

    def test_vulnerability_indicator(self):
        """Test vulnerability warning indicator."""
        result = self.table.render([self.full_ext])

        # Should have warning indicator (6 total vulnerabilities)
        self.assertIn("vuln-indicator", result)
        self.assertIn("⚠", result)

    def test_no_vulnerability_indicator(self):
        """Test that clean extensions have no vulnerability indicator."""
        result = self.table.render([self.minimal_ext])

        # Should NOT have warning indicator
        self.assertNotIn("vuln-indicator", result)

    def test_detail_row_structure(self):
        """Test that detail rows are generated with correct ID."""
        result = self.table.render([self.minimal_ext])

        # Should have detail row with correct ID
        self.assertIn('class="detail-row"', result)
        self.assertIn('id="detail-test.extension"', result)
        self.assertIn('style="display: none;"', result)  # Hidden by default

    def test_expand_button_present(self):
        """Test that expand/collapse button is present."""
        result = self.table.render([self.minimal_ext])

        # Should have expand button
        self.assertIn('class="expand-btn"', result)
        self.assertIn("▶", result)  # Arrow character

    def test_clickable_rows(self):
        """Test that rows are clickable to toggle details."""
        result = self.table.render([self.minimal_ext])

        # Should have onclick with toggleDetails
        self.assertIn('onclick="toggleDetails', result)
        self.assertIn('style="cursor: pointer;"', result)

    def test_number_formatting(self):
        """Test that large numbers are formatted with suffixes."""
        result = self.table.render([self.full_ext])

        # 1,500,000 installs should be formatted as 1.5M
        self.assertIn("1.5M", result)

    def test_rating_display(self):
        """Test that rating is displayed with count."""
        result = self.table.render([self.full_ext])

        # Should show rating with count
        self.assertIn("4.5", result)
        self.assertIn("1200", result)  # formatted count

    def test_date_iso_attributes(self):
        """Test that dates have data-iso-date attributes."""
        result = self.table.render([self.full_ext])

        # Should have ISO date attributes
        self.assertIn('data-iso-date="2024-01-15T10:00:00"', result)
        self.assertIn('data-iso-date="2024-01-01T12:00:00"', result)
        self.assertIn('data-iso-date="2024-01-20T08:30:00"', result)

    def test_scan_failed_status(self):
        """Test that failed scans have special CSS class."""
        failed_ext = self.minimal_ext.copy()
        failed_ext["scan_status"] = "failed"

        result = self.table.render([failed_ext])

        # Should have scan-failed class
        self.assertIn("scan-failed", result)

    def test_html_escaping(self):
        """Test XSS prevention through HTML escaping."""
        malicious_ext = self.minimal_ext.copy()
        malicious_ext["display_name"] = '<script>alert("xss")</script>'

        result = self.table.render([malicious_ext])

        # Should escape HTML
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)


if __name__ == "__main__":
    unittest.main()
