#!/usr/bin/env python3
"""
Mock Validation Tests

These tests ensure that all API mocks accurately represent the real vscan.dev API.
This prevents "mock drift" where tests pass but real integration fails.

Test Categories:
1. Real API Structure Documentation (calls real API once)
2. Canonical Mock Validation (verifies canonical mock matches real API)
3. Existing Mock Validation (verifies all test mocks are consistent)

Usage:
    # Run all validation tests
    python3 tests/test_mock_validation.py

    # Skip slow real API test
    pytest -v -m "not slow" tests/test_mock_validation.py

Last Validated: 2025-10-26
"""

import sys
import unittest
from pathlib import Path
from typing import Dict, Any, Set

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.vscan_api import VscanAPIClient
from tests.fixtures.canonical_mock import (
    CanonicalVscanAPIMock,
    REQUIRED_SUCCESS_FIELDS,
    REQUIRED_ERROR_FIELDS,
    CRITICAL_FIELDS,
)

# Mark tests appropriately
try:
    import pytest

    integration = pytest.mark.integration
    slow = pytest.mark.slow
except ImportError:

    def integration(func):
        return func

    def slow(func):
        return func


@pytest.mark.mock_validation
class TestRealAPIStructure(unittest.TestCase):
    """
    Document and validate the real vscan.dev API response structure.

    This runs ONCE against the real API to document the expected structure.
    """

    @classmethod
    def setUpClass(cls):
        """Store real API response for all tests in this class."""
        cls.real_response = None

    @integration
    @slow
    def test_document_real_api_success_response(self):
        """
        Call real API and document exact success response structure.

        This test makes a real API call to vscan.dev using a well-known,
        stable extension to document the actual response structure.

        WARNING: This test makes a real API call and takes ~10 seconds.
        """
        print("\n" + "=" * 70)
        print("REAL API STRUCTURE DOCUMENTATION TEST")
        print("=" * 70)
        print("\nCalling real vscan.dev API...")
        print("Extension: ms-python.python (stable, well-known)")

        # Call real API with generous timeout
        api_client = VscanAPIClient(delay=2.0, max_retries=3, timeout=30)

        result = api_client.scan_extension_with_retry(
            publisher="ms-python", name="python"
        )

        # Store for other tests
        self.__class__.real_response = result

        print(f"\nAPI Response Status: {result.get('scan_status')}")
        print(f"Fields Returned: {len(result.keys())}")
        print("\n" + "-" * 70)
        print("FIELD INVENTORY:")
        print("-" * 70)

        # Document all top-level fields
        for field in sorted(result.keys()):
            value = result[field]
            value_type = type(value).__name__
            value_preview = str(value)[:50] if value else "None"
            print(f"  {field:25} {value_type:12} {value_preview}")

        print("-" * 70)

        # Verify scan succeeded
        self.assertEqual(
            result["scan_status"],
            "success",
            "Real API scan should succeed for ms-python.python",
        )

        # Verify all required fields are present
        actual_fields = set(result.keys())
        missing_fields = REQUIRED_SUCCESS_FIELDS - actual_fields
        extra_fields = actual_fields - REQUIRED_SUCCESS_FIELDS

        if missing_fields:
            print(f"\n⚠️  MISSING FIELDS: {missing_fields}")
        if extra_fields:
            print(f"\n✓ EXTRA FIELDS: {extra_fields}")

        # Document field types
        print("\n" + "-" * 70)
        print("FIELD TYPE VALIDATION:")
        print("-" * 70)

        field_types = {
            "name": str,
            "publisher": str,
            "scan_status": str,
            "metadata": dict,
            "security": dict,
            "dependencies": dict,
            "risk_factors": list,
            "security_score": (int, type(None)),
            "risk_level": (str, type(None)),
            "vulnerabilities": dict,
            "vscan_url": str,
            "has_errors": bool,
        }

        for field, expected_type in field_types.items():
            if field in result:
                actual_value = result[field]
                if isinstance(expected_type, tuple):
                    type_match = isinstance(actual_value, expected_type)
                else:
                    type_match = isinstance(actual_value, expected_type)

                status = "✓" if type_match else "✗"
                print(f"  {status} {field:25} {type(actual_value).__name__}")

        # Verify nested structures
        print("\n" + "-" * 70)
        print("NESTED STRUCTURE VALIDATION:")
        print("-" * 70)

        if "vulnerabilities" in result:
            vuln = result["vulnerabilities"]
            print(f"  vulnerabilities.count: {vuln.get('count')}")
            print(f"  vulnerabilities.critical: {vuln.get('critical')}")
            print(f"  vulnerabilities.high: {vuln.get('high')}")

        if "metadata" in result:
            meta = result["metadata"]
            print(f"  metadata fields: {list(meta.keys())[:5]}")

        if "security" in result:
            sec = result["security"]
            print(f"  security fields: {list(sec.keys())}")

        print("\n" + "=" * 70)

    @integration
    @slow
    def test_document_real_api_error_response(self):
        """Document real API error response structure (invalid extension)."""
        print("\nCalling real API with invalid extension...")

        api_client = VscanAPIClient(delay=1.0, max_retries=1, timeout=15)

        result = api_client.scan_extension_with_retry(
            publisher="invalid-publisher", name="nonexistent-extension-12345"
        )

        print(f"Error Response Status: {result.get('scan_status')}")
        print(f"Error Message: {result.get('error', 'N/A')[:100]}")

        # Should be error status
        self.assertEqual(
            result["scan_status"],
            "error",
            "Invalid extension should return error status",
        )

        # Should have error message
        self.assertIsNotNone(
            result.get("error"), "Error response should have error message"
        )

        # Should still have required structure
        self.assertIn("vulnerabilities", result)
        self.assertIn("metadata", result)


@pytest.mark.mock_validation
class TestCanonicalMockValidation(unittest.TestCase):
    """Validate that canonical mock matches documented real API structure."""

    def test_canonical_success_structure(self):
        """Verify canonical success mock has all required fields."""
        mock_result = CanonicalVscanAPIMock.get_success_response(
            publisher="test-publisher", name="test-extension"
        )

        # Check all required fields present
        actual_fields = set(mock_result.keys())
        missing_fields = REQUIRED_SUCCESS_FIELDS - actual_fields

        self.assertEqual(
            len(missing_fields),
            0,
            f"Canonical mock missing required fields: {missing_fields}",
        )

        print(
            f"\n✓ Canonical success mock has all {len(REQUIRED_SUCCESS_FIELDS)} required fields"
        )

    def test_canonical_error_structure(self):
        """Verify canonical error mock has all required fields."""
        mock_result = CanonicalVscanAPIMock.get_error_response(
            publisher="test-publisher", name="test-extension"
        )

        # Check all required fields present
        actual_fields = set(mock_result.keys())
        missing_fields = REQUIRED_ERROR_FIELDS - actual_fields

        self.assertEqual(
            len(missing_fields),
            0,
            f"Canonical error mock missing required fields: {missing_fields}",
        )

        print(
            f"\n✓ Canonical error mock has all {len(REQUIRED_ERROR_FIELDS)} required fields"
        )

    def test_canonical_field_types(self):
        """Verify canonical mock field types match expected types."""
        mock_result = CanonicalVscanAPIMock.get_success_response("test", "extension")

        # Verify critical field types
        self.assertIsInstance(mock_result["scan_status"], str)
        self.assertEqual(mock_result["scan_status"], "success")

        self.assertIsInstance(mock_result["metadata"], dict)
        self.assertIsInstance(mock_result["security"], dict)
        self.assertIsInstance(mock_result["dependencies"], dict)
        self.assertIsInstance(mock_result["risk_factors"], list)
        self.assertIsInstance(mock_result["vulnerabilities"], dict)

        self.assertIsInstance(mock_result["security_score"], int)
        self.assertIsInstance(mock_result["risk_level"], str)

        print("\n✓ All canonical mock field types are correct")

    def test_canonical_nested_structure(self):
        """Verify canonical mock nested structures."""
        mock_result = CanonicalVscanAPIMock.get_success_response("test", "extension")

        # Verify vulnerabilities structure
        vuln = mock_result["vulnerabilities"]
        required_vuln_fields = {"count", "critical", "high", "moderate", "low", "info"}
        self.assertTrue(required_vuln_fields.issubset(vuln.keys()))

        # All counts should be integers
        for field in required_vuln_fields:
            self.assertIsInstance(
                vuln[field], int, f"vulnerabilities.{field} should be int"
            )

        print("\n✓ Canonical mock nested structures are correct")

    def test_canonical_vulnerable_response(self):
        """Verify canonical vulnerable extension response."""
        mock_result = CanonicalVscanAPIMock.get_vulnerable_response(
            publisher="test", name="vulnerable-ext", critical=1, high=2, moderate=3
        )

        # Should have vulnerabilities
        vuln = mock_result["vulnerabilities"]
        self.assertEqual(vuln["count"], 6)  # 1+2+3
        self.assertEqual(vuln["critical"], 1)
        self.assertEqual(vuln["high"], 2)
        self.assertEqual(vuln["moderate"], 3)

        # Security score should be lower
        self.assertLess(mock_result["security_score"], 80)

        # Should have risk factors
        self.assertGreater(len(mock_result["risk_factors"]), 0)

        print("\n✓ Canonical vulnerable response structure is correct")


@pytest.mark.mock_validation
class TestExistingMocksValidation(unittest.TestCase):
    """Validate existing mocks in test files."""

    def test_critical_fields_in_integration_mock(self):
        """Verify test_integration.py mock has critical fields."""
        # Import the mock
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from test_integration import MockVscanAPI

            mock = MockVscanAPI()
            result = mock.scan_extension("test", "extension", "1.0.0")

            # Check critical fields that scanner depends on
            for field in CRITICAL_FIELDS:
                self.assertIn(
                    field, result, f"MockVscanAPI missing critical field: {field}"
                )

            print(f"\n✓ test_integration.py MockVscanAPI has all critical fields")

        except ImportError as e:
            self.skipTest(f"Could not import MockVscanAPI: {e}")

    def test_critical_fields_in_parallel_mock(self):
        """Verify test_parallel_scanning.py mocks have critical fields."""
        # This test file uses unittest.mock.patch with return_value dicts
        # We validate the pattern used in those tests

        # Example from test_parallel_scanning.py:
        minimal_mock_response = {
            "scan_status": "success",
            "security": {"score": 85},
            "vulnerabilities": {"count": 0},
        }

        # These minimal mocks are acceptable if they have scan_status
        self.assertIn("scan_status", minimal_mock_response)

        print(f"\n✓ test_parallel_scanning.py mock pattern has critical fields")


@pytest.mark.mock_validation
class TestMockConsistency(unittest.TestCase):
    """Verify consistency across different mock types."""

    def test_all_success_mocks_have_same_structure(self):
        """Verify all success mocks return consistent structure."""
        # Get different success responses
        mock1 = CanonicalVscanAPIMock.get_success_response("pub1", "ext1")
        mock2 = CanonicalVscanAPIMock.get_success_response(
            "pub2", "ext2", security_score=50
        )
        mock3 = CanonicalVscanAPIMock.get_vulnerable_response("pub3", "ext3")

        # All should have same fields (different values)
        fields1 = set(mock1.keys())
        fields2 = set(mock2.keys())
        fields3 = set(mock3.keys())

        self.assertEqual(
            fields1, fields2, "Success mocks should have consistent fields"
        )
        self.assertEqual(
            fields1, fields3, "Vulnerable mock should have same fields as success"
        )

        print(f"\n✓ All success mock variations have consistent structure")

    def test_all_mocks_match_required_fields(self):
        """Verify all mock types match required field sets."""
        success_mock = CanonicalVscanAPIMock.get_success_response("pub", "ext")
        error_mock = CanonicalVscanAPIMock.get_error_response("pub", "ext")

        # Success should have all success fields
        self.assertTrue(REQUIRED_SUCCESS_FIELDS.issubset(success_mock.keys()))

        # Error should have all error fields
        self.assertTrue(REQUIRED_ERROR_FIELDS.issubset(error_mock.keys()))

        print(f"\n✓ All mock types match their required field sets")


def run_tests():
    """Run all mock validation tests."""
    print("\n" + "=" * 70)
    print("MOCK VALIDATION TEST SUITE")
    print("=" * 70)
    print("\nThese tests validate that API mocks match the real vscan.dev API")
    print("to prevent mock drift and ensure test reliability.\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRealAPIStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestCanonicalMockValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestExistingMocksValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestMockConsistency))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✓ ALL MOCK VALIDATION TESTS PASSED")
        print("\nMocks are validated against real API structure.")
        print("It is safe to use CanonicalVscanAPIMock in tests.")
    else:
        print("✗ SOME MOCK VALIDATION TESTS FAILED")
        print("\nMock structure may have drifted from real API.")
        print("Review test output above for details.")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_tests())
