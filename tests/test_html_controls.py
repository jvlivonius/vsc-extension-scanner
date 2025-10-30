"""
Tests for ControlsComponent in HTML Report Generator.

Covers filter controls, search, column visibility, and static HTML generation.
Target: 10 tests, 70% coverage
"""

import unittest
import pytest

from vscode_scanner.html_report.components.controls import ControlsComponent


@pytest.mark.unit
class TestControlsComponent(unittest.TestCase):
    """Test suite for ControlsComponent with comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.controls = ControlsComponent()

    def test_render_basic_structure(self):
        """Test basic rendering of controls section."""
        result = self.controls.render()

        # Verify structure
        self.assertIn('<section class="controls">', result)
        self.assertIn('<div class="search-filter">', result)

    def test_search_box_present(self):
        """Test search input field is rendered."""
        result = self.controls.render()

        # Verify search box
        self.assertIn('id="search-box"', result)
        self.assertIn('placeholder="Search extensions..."', result)
        self.assertIn('onkeyup="searchExtensions()"', result)
        self.assertIn('type="text"', result)

    def test_risk_filter_dropdown(self):
        """Test risk level filter dropdown with all options."""
        result = self.controls.render()

        # Verify risk filter dropdown
        self.assertIn('id="risk-filter"', result)
        self.assertIn('onchange="filterByRisk()"', result)

        # Verify all risk level options
        self.assertIn('<option value="all">All Risk Levels</option>', result)
        self.assertIn('<option value="critical">Critical Risk Only</option>', result)
        self.assertIn('<option value="high">High Risk Only</option>', result)
        self.assertIn('<option value="medium">Medium Risk Only</option>', result)
        self.assertIn('<option value="low">Low Risk Only</option>', result)

    def test_verified_filter_dropdown(self):
        """Test publisher verification filter dropdown."""
        result = self.controls.render()

        # Verify verified filter dropdown
        self.assertIn('id="verified-filter"', result)
        self.assertIn('onchange="filterByVerified()"', result)

        # Verify options
        self.assertIn('<option value="all">All Publishers</option>', result)
        self.assertIn('<option value="verified">Verified Only</option>', result)
        self.assertIn('<option value="unverified">Unverified Only</option>', result)

    def test_clear_filters_button(self):
        """Test clear filters button."""
        result = self.controls.render()

        # Verify clear button
        self.assertIn('onclick="clearFilters()"', result)
        self.assertIn('class="btn-secondary"', result)
        self.assertIn("Clear Filters", result)

    def test_column_toggle_button(self):
        """Test column visibility toggle button with SVG icon."""
        result = self.controls.render()

        # Verify toggle button
        self.assertIn('onclick="toggleColumnDropdown()"', result)
        self.assertIn('class="btn-icon"', result)
        self.assertIn('title="Show/Hide Columns"', result)

        # Verify SVG icon present
        self.assertIn("<svg", result)
        self.assertIn('viewBox="0 0 16 16"', result)
        self.assertIn('fill="currentColor"', result)

    def test_column_dropdown_structure(self):
        """Test column visibility dropdown structure."""
        result = self.controls.render()

        # Verify dropdown container
        self.assertIn('id="column-dropdown"', result)
        self.assertIn('class="column-dropdown"', result)
        self.assertIn('style="display: none;"', result)  # Hidden by default

    def test_all_column_checkboxes_present(self):
        """Test that all 13 column checkboxes are rendered."""
        result = self.controls.render()

        # Expected columns
        columns = [
            "name",
            "version",
            "publisher",
            "verified",
            "risk",
            "score",
            "vulnerabilities",
            "installs",
            "rating",
            "dependencies",
            "last-updated",
            "installed",
            "last-scanned",
        ]

        for col in columns:
            # Verify checkbox
            self.assertIn(f'id="col-{col}"', result)
            self.assertIn(f"onchange=\"toggleColumn('{col}')\"", result)
            self.assertIn(f'<label for="col-{col}">', result)

        # Count dropdown items
        dropdown_item_count = result.count('<div class="column-dropdown-item">')
        self.assertEqual(dropdown_item_count, 13)

    def test_default_checked_columns(self):
        """Test that first 5 columns are checked by default."""
        result = self.controls.render()

        # These should be checked
        default_checked = ["name", "version", "publisher", "verified", "risk"]
        for col in default_checked:
            # Find the checkbox line for this column
            checkbox_pattern = f'id="col-{col}" checked'
            self.assertIn(checkbox_pattern, result)

        # These should NOT be checked (no 'checked' attribute)
        optional_columns = [
            "score",
            "vulnerabilities",
            "installs",
            "rating",
            "dependencies",
            "last-updated",
            "installed",
            "last-scanned",
        ]
        for col in optional_columns:
            # Verify checkbox exists but without 'checked'
            self.assertIn(f'id="col-{col}"', result)
            # Make sure there's no 'checked' before the onchange
            checkbox_line = f'id="col-{col}" checked'
            self.assertNotIn(checkbox_line, result)

    def test_svg_icon_complete_structure(self):
        """Test SVG icon has both path elements."""
        result = self.controls.render()

        # Verify SVG structure
        self.assertIn('<svg width="16" height="16"', result)

        # Count path elements (should have 2)
        path_count = result.count('<path d="')
        self.assertGreaterEqual(path_count, 2)


if __name__ == "__main__":
    unittest.main()
