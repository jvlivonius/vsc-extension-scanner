#!/usr/bin/env python3
"""
Test Suite: v4.0 Comprehensive Security Findings Tests
Purpose: Test comprehensive security findings (schema v4.0)
Coverage: vscode_scanner.vscan_api (comprehensive parsers), output_formatter

This test suite validates v4.0 comprehensive security findings including:
- VirusTotal details with filtering (exclude category="undetected") - CRITICAL
- Output formatter includes all comprehensive security fields - CRITICAL
- All 9 parser methods return valid data structures

Testing Strategy:
- Focus on VirusTotal filtering logic (critical requirement)
- Test output formatter integration
- Verify parsers don't crash on empty/missing data
"""

import unittest
import pytest
import json
import os
from datetime import datetime, timezone
from vscode_scanner.vscan_api import VscanAPIClient
from vscode_scanner.output_formatter import OutputFormatter


# ============================================================
# VirusTotal Parser Tests (CRITICAL - Filtering Logic)
# ============================================================


@pytest.mark.unit
class TestVirusTotalFiltering(unittest.TestCase):
    """Test suite for VirusTotal filtering logic.

    **Purpose:** Ensure engines with category="undetected" are excluded.
    This is the CRITICAL v4.1 requirement.

    **Scope:**
    - Filtering logic (exclude undetected engines)
    - Preserve all other categories
    - Handle empty results
    """

    def setUp(self):
        """Set up test fixtures."""
        self.api = VscanAPIClient()

    def test_virustotal_excludes_undetected_engines(self):
        """Test that engines with category='undetected' are excluded."""
        # Arrange
        api_response = {
            "analysisModules": {
                "virusTotal": {
                    "scannedFiles": 1,
                    "fileResults": [
                        {
                            "fileName": "test.js",
                            "hash": "abc123",
                            "results": {
                                "engines": {
                                    "Engine1": {
                                        "category": "malicious",
                                        "result": "Trojan",
                                    },
                                    "Engine2": {
                                        "category": "undetected",
                                        "result": None,
                                    },
                                    "Engine3": {
                                        "category": "suspicious",
                                        "result": "Adware",
                                    },
                                    "Engine4": {
                                        "category": "undetected",
                                        "result": None,
                                    },
                                }
                            },
                        }
                    ],
                }
            }
        }

        # Act
        result = self.api._parse_virustotal_details(api_response)

        # Assert
        file_result = result["file_results"][0]
        engines = file_result["engines"]

        # Only 2 engines should remain (Engine1 and Engine3)
        self.assertEqual(len(engines), 2)
        self.assertIn("Engine1", engines)
        self.assertIn("Engine3", engines)
        self.assertNotIn("Engine2", engines)
        self.assertNotIn("Engine4", engines)

    def test_virustotal_preserves_all_non_undetected_categories(self):
        """Test that all non-undetected categories are preserved."""
        # Arrange
        api_response = {
            "analysisModules": {
                "virusTotal": {
                    "fileResults": [
                        {
                            "results": {
                                "engines": {
                                    "E1": {"category": "malicious"},
                                    "E2": {"category": "suspicious"},
                                    "E3": {"category": "failure"},
                                    "E4": {"category": "type-unsupported"},
                                    "E5": {"category": "timeout"},
                                    "E6": {"category": "undetected"},
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Act
        result = self.api._parse_virustotal_details(api_response)

        # Assert
        engines = result["file_results"][0]["engines"]

        # All categories except "undetected" should be preserved
        self.assertEqual(len(engines), 5)
        self.assertNotIn("E6", engines)

    def test_virustotal_handles_empty_data(self):
        """Test handling when virusTotal is missing or empty."""
        # Arrange
        api_response = {}

        # Act
        result = self.api._parse_virustotal_details(api_response)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["file_results"], [])


# ============================================================
# Parser Robustness Tests
# ============================================================


@pytest.mark.unit
class TestParserRobustness(unittest.TestCase):
    """Test that all v4.1 parsers handle missing data gracefully.

    **Purpose:** Ensure parsers don't crash on empty/missing data.

    **Scope:**
    - All 9 parser methods
    - Empty API responses
    - Return valid data structures
    """

    def setUp(self):
        """Set up test fixtures."""
        self.api = VscanAPIClient()
        self.empty_response = {}

    def test_permissions_parser_handles_empty(self):
        """Test permissions parser with empty data."""
        result = self.api._parse_permissions_details(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIn("permissions", result)

    def test_ossf_parser_handles_empty(self):
        """Test OSSF scorecard parser with empty data."""
        result = self.api._parse_ossf_scorecard_details(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_ast_parser_handles_empty(self):
        """Test AST findings parser with empty data."""
        result = self.api._parse_ast_findings(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_socket_parser_handles_empty(self):
        """Test socket findings parser with empty data."""
        result = self.api._parse_socket_findings(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_network_parser_handles_empty(self):
        """Test network endpoints parser with empty data."""
        result = self.api._parse_network_endpoints(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_obfuscation_parser_handles_empty(self):
        """Test obfuscation findings parser with empty data."""
        result = self.api._parse_obfuscation_findings(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_sensitive_parser_handles_empty(self):
        """Test sensitive info findings parser with empty data."""
        result = self.api._parse_sensitive_info_findings(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_opengrep_parser_handles_empty(self):
        """Test opengrep findings parser with empty data."""
        result = self.api._parse_opengrep_findings(self.empty_response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)


# ============================================================
# Output Formatter v4.1 Tests (CRITICAL)
# ============================================================


@pytest.mark.unit
class TestOutputFormatterV41(unittest.TestCase):
    """Test suite for v4.1 output formatter enhancements.

    **Purpose:** Ensure all v4.1 comprehensive security findings
    are included in JSON output.

    **Scope:**
    - Schema version 4.1
    - vscode_engine field
    - All 9 comprehensive security findings in output
    """

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter()
        self.timestamp = datetime.now(timezone.utc).isoformat() + "Z"

    def test_schema_version_is_4_0(self):
        """Test that schema version is 4.0."""
        # Arrange
        scan_results = []

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)

        # Assert
        self.assertEqual(output["schema_version"], "4.0")

    def test_extension_includes_vscode_engine(self):
        """Test that vscode_engine field is included."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "metadata": {"vscode_engine": "^1.75.0"},
                "vulnerabilities": {"count": 0},
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        extension = output["extensions"][0]

        # Assert
        self.assertEqual(extension["vscode_engine"], "^1.75.0")

    def test_security_section_includes_all_v4_1_findings(self):
        """Test that security section includes all v4.1 comprehensive findings."""
        # Arrange
        scan_results = [
            {
                "scan_status": "success",
                "metadata": {},
                "vulnerabilities": {"count": 0},
                "virustotal_details": {"scanned_files": 10},
                "permissions_details": {"permissions": []},
                "ossf_checks": {"score": 8.5},
                "ast_findings": {"findings": []},
                "socket_findings": {"issues": []},
                "network_endpoints": {"endpoints": []},
                "obfuscation_findings": {"detected": False},
                "sensitive_findings": {"secrets": []},
                "opengrep_findings": {"findings": []},
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        security = output["extensions"][0]["security"]

        # Assert - All 9 v4.1 fields should be present
        self.assertIn("virustotal", security)
        self.assertIn("permissions_detailed", security)
        self.assertIn("ossf_scorecard", security)
        self.assertIn("ast_findings", security)
        self.assertIn("socket_findings", security)
        self.assertIn("network_endpoints", security)
        self.assertIn("obfuscation", security)
        self.assertIn("sensitive_info", security)
        self.assertIn("opengrep", security)

    def test_v4_1_findings_preserve_structure(self):
        """Test that v4.1 findings preserve their data structure."""
        # Arrange
        vt_data = {
            "scanned_files": 5,
            "file_results": [
                {"file_name": "test.js", "engines": {"E1": {"category": "malicious"}}}
            ],
        }
        scan_results = [
            {
                "scan_status": "success",
                "metadata": {},
                "vulnerabilities": {"count": 0},
                "virustotal_details": vt_data,
            }
        ]

        # Act
        output = self.formatter.format_output(scan_results, self.timestamp, 1.0)
        vt_output = output["extensions"][0]["security"]["virustotal"]

        # Assert - Data structure is preserved
        self.assertEqual(vt_output["scanned_files"], 5)
        self.assertEqual(len(vt_output["file_results"]), 1)


# ============================================================
# Test Runner
# ============================================================


def run_tests():
    """Run the test suite and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVirusTotalFiltering))
    suite.addTests(loader.loadTestsFromTestCase(TestParserRobustness))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormatterV41))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("v4.0 Comprehensive Security Findings Test Summary")
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
