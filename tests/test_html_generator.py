"""
Tests for HTMLReportGenerator - Main HTML Report Orchestrator.

Covers component initialization, report generation, asset loading, and integration.
Target: 10 tests for 95%+ coverage of generator.py
"""

import unittest
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from vscode_scanner.html_report.generator import HTMLReportGenerator


@pytest.mark.unit
class TestHTMLReportGenerator(unittest.TestCase):
    """Test suite for HTMLReportGenerator orchestration."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = HTMLReportGenerator()

        self.minimal_data = {
            "summary": {
                "scan_timestamp": "2024-01-15T10:00:00",
                "total_extensions_scanned": 5,
                "critical_risk_extensions": 1,
                "high_risk_extensions": 1,
                "medium_risk_extensions": 2,
                "low_risk_extensions": 1,
            },
            "extensions": [
                {
                    "id": "test.ext",
                    "name": "TestExt",
                    "version": "1.0.0",
                    "publisher": {"id": "test", "verified": False},
                    "security": {"risk_level": "low", "score": 85},
                }
            ],
        }

        self.empty_data = {"summary": {}, "extensions": []}

    # === Component Initialization Tests ===

    def test_generator_initializes_all_components(self):
        """Test that generator initializes all required components."""
        # Verify all components are initialized
        self.assertIsNotNone(self.generator.header)
        self.assertIsNotNone(self.generator.controls)
        self.assertIsNotNone(self.generator.footer)
        self.assertIsNotNone(self.generator.table)
        self.assertIsNotNone(self.generator.charts)

        # Verify correct types
        from vscode_scanner.html_report.components import (
            HeaderComponent,
            ControlsComponent,
            FooterComponent,
            OverviewTableComponent,
            ChartComponents,
        )

        self.assertIsInstance(self.generator.header, HeaderComponent)
        self.assertIsInstance(self.generator.controls, ControlsComponent)
        self.assertIsInstance(self.generator.footer, FooterComponent)
        self.assertIsInstance(self.generator.table, OverviewTableComponent)
        self.assertIsInstance(self.generator.charts, ChartComponents)

    # === Report Generation Tests ===

    def test_generate_report_with_valid_data(self):
        """Test report generation with complete valid data."""
        result = self.generator.generate_report(self.minimal_data)

        # Verify HTML structure
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn('<html lang="en">', result)
        self.assertIn("<head>", result)
        self.assertIn("<body>", result)
        self.assertIn("</html>", result)

        # Verify title
        self.assertIn("<title>VS Code Extension Security Report</title>", result)

        # Verify meta tags
        self.assertIn('<meta charset="UTF-8">', result)
        self.assertIn('<meta name="viewport"', result)

        # Verify main container
        self.assertIn('<div class="container">', result)

        # Verify components rendered (by checking for their known patterns)
        self.assertIn("report-header", result)  # Header
        self.assertIn("controls", result)  # Controls
        self.assertIn("overview-table", result)  # Table
        self.assertIn("report-footer", result)  # Footer

    def test_generate_report_with_empty_data(self):
        """Test report generation with empty summary and extensions."""
        result = self.generator.generate_report(self.empty_data)

        # Should still generate valid HTML structure
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn('<html lang="en">', result)

        # Components should handle empty data gracefully
        self.assertIn("report-header", result)
        self.assertIn("overview-table", result)

    def test_generate_report_extracts_risk_counts(self):
        """Test that risk counts are correctly extracted from summary."""
        result = self.generator.generate_report(self.minimal_data)

        # Verify risk distribution data is in report
        # (Chart will have been generated with these values)
        self.assertIn("Critical Risk: 1", result)
        self.assertIn("High Risk: 1", result)
        self.assertIn("Medium Risk: 2", result)
        self.assertIn("Low Risk: 1", result)

    def test_generate_report_with_missing_summary(self):
        """Test report generation when summary key is missing."""
        data_no_summary = {"extensions": []}

        result = self.generator.generate_report(data_no_summary)

        # Should use defaults (0 for all risk counts)
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("report-header", result)

    def test_generate_report_with_missing_extensions(self):
        """Test report generation when extensions key is missing."""
        data_no_extensions = {"summary": self.minimal_data["summary"]}

        result = self.generator.generate_report(data_no_extensions)

        # Should generate report with empty table
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("overview-table", result)

    # === Asset Loading Tests ===

    def test_load_styles_reads_css_file(self):
        """Test that _load_styles reads and embeds CSS file."""
        result = self.generator._load_styles()

        # Verify style tag wrapping
        self.assertTrue(result.startswith("<style>\n"))
        self.assertTrue(result.endswith("\n</style>"))

        # Verify CSS content is present
        # (Should contain actual CSS from report_styles.css)
        self.assertIn(".container", result)
        self.assertIn(".report-header", result)

    def test_load_scripts_reads_js_file(self):
        """Test that _load_scripts reads and embeds JavaScript file."""
        result = self.generator._load_scripts()

        # Verify script tag wrapping
        self.assertTrue(result.startswith("<script>\n"))
        self.assertTrue(result.endswith("\n</script>"))

        # Verify JavaScript content is present
        # (Should contain actual JS from report_scripts.js)
        self.assertIn("function", result)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_styles_file_not_found(self, mock_file):
        """Test error handling when CSS file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            self.generator._load_styles()

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_scripts_file_not_found(self, mock_file):
        """Test error handling when JS file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            self.generator._load_scripts()

    # === Integration Test ===

    def test_full_report_integration(self):
        """Test complete report generation with all components working together."""
        # Use realistic data
        full_data = {
            "summary": {
                "scan_timestamp": "2024-01-15T10:30:00",
                "total_extensions_scanned": 10,
                "scan_duration_seconds": 25.5,
                "vulnerabilities_found": 12,
                "critical_risk_extensions": 2,
                "high_risk_extensions": 3,
                "medium_risk_extensions": 3,
                "low_risk_extensions": 2,
                "cache_statistics": {"cache_hit_rate": 75.0},
            },
            "extensions": [
                {
                    "id": "publisher.extension1",
                    "name": "Extension1",
                    "display_name": "Test Extension 1",
                    "version": "2.5.0",
                    "publisher": {
                        "id": "publisher",
                        "name": "Test Publisher",
                        "verified": True,
                    },
                    "security": {
                        "risk_level": "high",
                        "score": 45,
                        "vulnerabilities": {
                            "critical": 1,
                            "high": 2,
                            "moderate": 0,
                            "low": 0,
                        },
                    },
                    "statistics": {
                        "installs": 1500000,
                        "rating": 4.5,
                        "rating_count": 1200,
                    },
                },
                {
                    "id": "other.extension2",
                    "name": "Extension2",
                    "display_name": "Safe Extension",
                    "version": "1.0.0",
                    "publisher": {
                        "id": "other",
                        "name": "Other Publisher",
                        "verified": False,
                    },
                    "security": {
                        "risk_level": "low",
                        "score": 95,
                        "vulnerabilities": {},
                    },
                    "statistics": {},
                },
            ],
        }

        result = self.generator.generate_report(full_data)

        # Verify complete HTML document
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("</html>", result)

        # Verify all major sections present
        self.assertIn("VS Code Extension Security Report", result)
        self.assertIn("2024-01-15T10:30:00", result)  # Timestamp
        self.assertIn("10", result)  # Total extensions
        self.assertIn("Test Extension 1", result)  # Extension name
        self.assertIn("Safe Extension", result)  # Second extension
        self.assertIn("Test Publisher", result)  # Publisher
        self.assertIn("vscan", result)  # Footer

        # Verify risk distribution
        self.assertIn("Critical Risk: 2", result)
        self.assertIn("High Risk: 3", result)

        # Verify assets embedded
        self.assertIn("<style>", result)
        self.assertIn("<script>", result)


if __name__ == "__main__":
    unittest.main()
