#!/usr/bin/env python3
"""
Test Suite: Output Formatter Tests
Purpose: Test output formatting for JSON and CSV generation
Coverage: vscode_scanner.output_formatter (format_output, format_csv)

This test suite validates output formatting including:
- JSON output structure and schema versioning
- Summary statistics calculation (scans, vulnerabilities, risk levels)
- Cache statistics integration
- Extension metadata formatting
- Security section completeness
- Dependencies information
- CSV export generation
- Error state handling
- Edge cases (empty results, missing fields)

Mocking Strategy:
- No mocking needed - pure data transformation testing
- Use realistic test data matching API response structure
- Test both success and error states
"""

import unittest
from datetime import datetime
from vscode_scanner.output_formatter import OutputFormatter


# ============================================================
# Basic Output Formatting Tests
# ============================================================


class TestOutputFormatterBasic(unittest.TestCase):
    """Test suite for basic output formatting operations.

    **Purpose:** Ensure basic JSON output structure is correct
    with proper schema versioning.

    **Scope:**
    - Output structure (schema_version, output_mode, summary, extensions)
    - Schema version inclusion
    - Empty results handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter()
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def test_basic_output_structure(self):
        """Test that output has required structure."""
        # Arrange
        scan_results = []

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)

        # Assert
        self.assertIn("schema_version", output)
        self.assertIn("output_mode", output)
        self.assertIn("summary", output)
        self.assertIn("extensions", output)

    def test_schema_version_included(self):
        """Test that schema version is included."""
        # Arrange
        scan_results = []

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)

        # Assert
        self.assertIsNotNone(output["schema_version"])
        self.assertEqual(output["output_mode"], "detailed")

    def test_empty_results_handled(self):
        """Test that empty scan results are handled gracefully."""
        # Arrange
        scan_results = []

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 0.5)

        # Assert
        self.assertEqual(output["summary"]["total_extensions_scanned"], 0)
        self.assertEqual(len(output["extensions"]), 0)
        self.assertEqual(output["summary"]["vulnerabilities_found"], 0)


# ============================================================
# Summary Formatting Tests
# ============================================================


class TestSummaryFormatting(unittest.TestCase):
    """Test suite for summary section formatting.

    **Purpose:** Ensure summary statistics are calculated correctly
    from scan results.

    **Scope:**
    - Total, successful, failed scan counts
    - Vulnerability counting
    - Risk level distribution
    - Cache statistics
    - Failed extensions list
    """

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter()
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def test_summary_counts_extensions_correctly(self):
        """Test that summary counts total extensions correctly."""
        # Arrange
        scan_results = [
            {"scan_status": "success", "vulnerabilities": {"count": 0}},
            {"scan_status": "success", "vulnerabilities": {"count": 5}},
            {"scan_status": "error", "error": "Failed to scan"},
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 2.5)
        summary = output["summary"]

        # Assert
        self.assertEqual(summary["total_extensions_scanned"], 3)
        self.assertEqual(summary["successful_scans"], 2)
        self.assertEqual(summary["failed_scans"], 1)

    def test_summary_counts_vulnerabilities(self):
        """Test that summary counts vulnerabilities correctly."""
        # Arrange
        scan_results = [
            {"scan_status": "success", "vulnerabilities": {"count": 3}},
            {"scan_status": "success", "vulnerabilities": {"count": 7}},
            {"scan_status": "error"},
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        summary = output["summary"]

        # Assert
        self.assertEqual(summary["vulnerabilities_found"], 10)

    def test_summary_counts_risk_levels(self):
        """Test that summary counts risk levels correctly."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "risk_level": "high",
                "vulnerabilities": {"count": 0},
            },
            {
                "scan_status": "success",
                "risk_level": "medium",
                "vulnerabilities": {"count": 0},
            },
            {
                "scan_status": "success",
                "risk_level": "low",
                "vulnerabilities": {"count": 0},
            },
            {
                "scan_status": "success",
                "risk_level": "high",
                "vulnerabilities": {"count": 0},
            },
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        summary = output["summary"]

        # Assert
        self.assertEqual(summary["high_risk_extensions"], 2)
        self.assertEqual(summary["medium_risk_extensions"], 1)
        self.assertEqual(summary["low_risk_extensions"], 1)

    def test_summary_includes_cache_statistics(self):
        """Test that cache statistics are included when provided."""
        # Arrange
        scan_results = [{"scan_status": "success", "vulnerabilities": {"count": 0}}]
        cache_stats = {"from_cache": 5, "fresh_scans": 3}

        # Act
        output = self.formatter.format_output(
            scan_results, self.timestamp, 1.0, cache_stats=cache_stats
        )
        summary = output["summary"]

        # Assert
        self.assertIn("cache_statistics", summary)
        self.assertEqual(summary["cache_statistics"]["from_cache"], 5)
        self.assertEqual(summary["cache_statistics"]["fresh_scans"], 3)
        self.assertEqual(summary["cache_statistics"]["cache_hit_rate"], 62.5)

    def test_summary_calculates_cache_hit_rate(self):
        """Test that cache hit rate is calculated correctly."""
        # Arrange
        scan_results = []
        cache_stats = {"from_cache": 7, "fresh_scans": 3}

        # Act
        output = self.formatter.format_output(
            scan_results, self.timestamp, 1.0, cache_stats=cache_stats
        )
        cache_stats_output = output["summary"]["cache_statistics"]

        # Assert
        self.assertEqual(cache_stats_output["cache_hit_rate"], 70.0)

    def test_summary_includes_failed_extensions(self):
        """Test that failed extensions are included when provided."""
        # Arrange
        scan_results = []
        failed_extensions = [
            {"id": "test.failed1", "error": "Network timeout"},
            {"id": "test.failed2", "error": "Invalid response"},
        ]

        # Act
        output = self.formatter.format_output(
            scan_results, self.timestamp, 1.0, failed_extensions=failed_extensions
        )
        summary = output["summary"]

        # Assert
        self.assertIn("failed_extensions", summary)
        self.assertEqual(len(summary["failed_extensions"]), 2)
        self.assertEqual(summary["failed_extensions"][0]["id"], "test.failed1")

    def test_summary_includes_timestamp_and_duration(self):
        """Test that summary includes scan timestamp and duration."""
        # Arrange
        scan_results = []
        duration = 12.345

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, duration)
        summary = output["summary"]

        # Assert
        self.assertEqual(summary["scan_timestamp"], self.timestamp)
        self.assertEqual(summary["scan_duration_seconds"], 12.35)


# ============================================================
# Extension Formatting Tests
# ============================================================


class TestExtensionFormatting(unittest.TestCase):
    """Test suite for individual extension formatting.

    **Purpose:** Ensure individual extension data is formatted
    correctly with all metadata and security information.

    **Scope:**
    - Basic extension metadata (id, name, version)
    - Publisher information (name, verified status)
    - Description and repository URL
    - Statistics (installs, rating)
    - Security section (score, risk level, vulnerabilities)
    - Dependencies information
    - Error state handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter()
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def test_extension_basic_metadata(self):
        """Test that extension basic metadata is formatted correctly."""
        # Arrange
        scan_results = [
            {
                "id": "publisher.extension",
                "name": "extension",
                "publisher": "publisher",
                "scan_status": "success",
                "vulnerabilities": {"count": 0},
                "metadata": {
                    "display_name": "My Extension",
                    "version": "1.0.0",
                    "description": "Test extension",
                    "publisher": {"id": "publisher", "name": "Publisher Name"},
                },
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        extension = output["extensions"][0]

        # Assert
        self.assertEqual(extension["id"], "publisher.extension")
        self.assertEqual(extension["name"], "extension")
        self.assertEqual(extension["display_name"], "My Extension")
        self.assertEqual(extension["version"], "1.0.0")
        self.assertEqual(extension["description"], "Test extension")

    def test_extension_publisher_information(self):
        """Test that publisher information is formatted correctly."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "vulnerabilities": {"count": 0},
                "metadata": {
                    "publisher": {
                        "id": "microsoft",
                        "name": "Microsoft",
                        "verified": True,
                        "domain": "https://microsoft.com",
                    }
                },
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        publisher = output["extensions"][0]["publisher"]

        # Assert
        self.assertEqual(publisher["id"], "microsoft")
        self.assertEqual(publisher["name"], "Microsoft")
        self.assertTrue(publisher["verified"])
        self.assertEqual(publisher["domain"], "https://microsoft.com")

    def test_extension_statistics(self):
        """Test that extension statistics are included."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "vulnerabilities": {"count": 0},
                "metadata": {
                    "statistics": {
                        "installs": 1000000,
                        "rating": 4.5,
                        "rating_count": 250,
                    }
                },
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        stats = output["extensions"][0]["statistics"]

        # Assert
        self.assertEqual(stats["installs"], 1000000)
        self.assertEqual(stats["rating"], 4.5)
        self.assertEqual(stats["rating_count"], 250)

    def test_extension_security_section(self):
        """Test that security section is comprehensive for successful scans."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "security_score": 85,
                "risk_level": "medium",
                "vulnerabilities": {
                    "total": 3,
                    "critical": 0,
                    "high": 1,
                    "moderate": 2,
                    "low": 0,
                },
                "risk_factors": [{"type": "outdated-dependency", "severity": "medium"}],
                "dependencies": {"total_count": 10, "with_vulnerabilities": 2},
                "metadata": {},
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        security = output["extensions"][0]["security"]

        # Assert
        self.assertEqual(security["score"], 85)
        self.assertEqual(security["risk_level"], "medium")
        self.assertEqual(security["vulnerabilities"]["total"], 3)
        self.assertEqual(security["vulnerabilities"]["high"], 1)
        self.assertEqual(security["risk_factors_count"], 1)
        self.assertEqual(security["dependencies_count"], 10)
        self.assertEqual(security["dependencies_with_vulnerabilities"], 2)

    def test_extension_error_state_formatting(self):
        """Test that extensions with errors are formatted correctly."""
        # Arrange
        scan_results = [
            {
                "id": "test.failed",
                "name": "failed",
                "scan_status": "error",
                "error": "Network timeout",
                "metadata": {},
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        extension = output["extensions"][0]

        # Assert
        self.assertEqual(extension["scan_status"], "error")
        self.assertEqual(extension["error"], "Network timeout")
        self.assertIsNone(extension["security"]["score"])
        self.assertIsNone(extension["security"]["risk_level"])
        self.assertEqual(extension["security"]["vulnerabilities"]["total"], 0)


# ============================================================
# CSV Formatting Tests
# ============================================================


class TestCSVFormatting(unittest.TestCase):
    """Test suite for CSV export formatting.

    **Purpose:** Ensure CSV output is correctly formatted
    for spreadsheet analysis.

    **Scope:**
    - CSV header row
    - Data row formatting
    - Field extraction and fallbacks
    - Empty results handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter()

    def test_csv_header_row(self):
        """Test that CSV has correct header row."""
        # Arrange
        scan_results = []

        # Act
        csv_output = self.formatter.format_csv(scan_results)
        lines = csv_output.strip().split("\n")
        header = lines[0]

        # Assert
        self.assertIn("Extension ID", header)
        self.assertIn("Name", header)
        self.assertIn("Version", header)
        self.assertIn("Publisher", header)
        self.assertIn("Risk Level", header)
        self.assertIn("Security Score", header)
        self.assertIn("Vulnerabilities", header)

    def test_csv_data_rows(self):
        """Test that CSV data rows are formatted correctly."""
        # Arrange
        scan_results = [
            {
                "id": "publisher.extension",
                "name": "extension",
                "display_name": "My Extension",
                "version": "1.0.0",
                "publisher": {
                    "id": "publisher",
                    "name": "Publisher Name",
                    "verified": True,
                },
                "security": {
                    "risk_level": "low",
                    "score": 90,
                    "vulnerabilities": {
                        "total": 0,
                        "critical": 0,
                        "high": 0,
                        "moderate": 0,
                        "low": 0,
                    },
                    "dependencies": {"total_count": 5},
                },
                "metadata": {"last_updated": "2025-01-15"},
                "vscan_url": "https://vscan.dev/extension/publisher.extension",
                "installed_at": "2025-01-01",
                "last_scanned_at": "2025-01-20",
            }
        ]

        # Act
        csv_output = self.formatter.format_csv(scan_results)
        lines = csv_output.strip().split("\n")

        # Assert
        self.assertEqual(len(lines), 2)  # header + 1 data row
        data_row = lines[1]
        self.assertIn("publisher.extension", data_row)
        self.assertIn("My Extension", data_row)
        self.assertIn("1.0.0", data_row)
        self.assertIn("Yes", data_row)  # verified publisher
        self.assertIn("low", data_row)

    def test_csv_handles_empty_results(self):
        """Test that CSV handles empty results gracefully."""
        # Arrange
        scan_results = []

        # Act
        csv_output = self.formatter.format_csv(scan_results)
        lines = csv_output.strip().split("\n")

        # Assert
        self.assertEqual(len(lines), 1)  # only header row

    def test_csv_handles_missing_fields(self):
        """Test that CSV handles missing fields with fallbacks."""
        # Arrange
        scan_results = [
            {
                "id": "test.minimal",
                "name": "minimal"
                # Most fields missing
            }
        ]

        # Act
        csv_output = self.formatter.format_csv(scan_results)
        lines = csv_output.strip().split("\n")

        # Assert
        self.assertEqual(len(lines), 2)  # header + 1 data row
        # Should not crash, should use empty strings for missing fields


# ============================================================
# Edge Cases and Error Handling Tests
# ============================================================


class TestEdgeCases(unittest.TestCase):
    """Test suite for edge cases and error handling.

    **Purpose:** Ensure robust handling of edge cases,
    missing fields, and unusual input.

    **Scope:**
    - Missing or None fields
    - Empty nested structures
    - Zero division scenarios
    - Unknown risk levels
    - Missing vulnerability counts
    """

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter()
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def test_handles_missing_metadata(self):
        """Test that missing metadata fields are handled gracefully."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                # metadata missing entirely
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        extension = output["extensions"][0]

        # Assert
        self.assertIsNotNone(extension)
        self.assertEqual(extension["scan_status"], "success")

    def test_handles_missing_vulnerability_counts(self):
        """Test that missing vulnerability counts default to zero."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                # vulnerabilities missing
                "metadata": {},
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        summary = output["summary"]

        # Assert
        self.assertEqual(summary["vulnerabilities_found"], 0)

    def test_handles_zero_cache_entries(self):
        """Test that zero cache entries don't cause division by zero."""
        # Arrange
        scan_results = []
        cache_stats = {"from_cache": 0, "fresh_scans": 0}

        # Act
        output = self.formatter.format_output(
            scan_results, self.timestamp, 1.0, cache_stats=cache_stats
        )
        cache_stats_output = output["summary"]["cache_statistics"]

        # Assert
        self.assertEqual(cache_stats_output["cache_hit_rate"], 0.0)

    def test_handles_unknown_risk_levels(self):
        """Test that unknown risk levels are counted correctly."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "risk_level": "mysterious",
                "vulnerabilities": {"count": 0},
            },
            {
                "scan_status": "success",
                "vulnerabilities": {"count": 0},
            },  # no risk_level
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        summary = output["summary"]

        # Assert
        # Should not crash, mysterious risk level is not counted in known categories
        self.assertEqual(summary["high_risk_extensions"], 0)

    def test_handles_none_publisher(self):
        """Test that None publisher values are handled gracefully."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "vulnerabilities": {"count": 0},
                "metadata": {
                    "publisher": {
                        "id": "test",
                        "name": None,  # None value
                        "verified": False,
                    }
                },
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        publisher = output["extensions"][0]["publisher"]

        # Assert
        self.assertEqual(publisher["id"], "test")
        self.assertIsNone(publisher["name"])
        self.assertFalse(publisher["verified"])


# ============================================================
# Test Runner
# ============================================================


def run_tests():
    """Run the test suite and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormatterBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestSummaryFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestExtensionFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestCSVFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Output Formatter Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_tests())
