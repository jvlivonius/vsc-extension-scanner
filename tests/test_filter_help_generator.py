#!/usr/bin/env python3
"""
Unit Tests for FilterHelpGenerator Module

Tests the pure functions for filter help message generation.
"""

import sys
import unittest
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.filter_help_generator import FilterHelpGenerator


class MockArgs:
    """Mock args object for testing."""

    def __init__(
        self,
        publisher=None,
        include_ids=None,
        exclude_ids=None,
        min_risk_level=None,
    ):
        self.publisher = publisher
        self.include_ids = include_ids
        self.exclude_ids = exclude_ids
        self.min_risk_level = min_risk_level


@pytest.mark.unit
class TestFilterHelpGeneratorExtractFilters(unittest.TestCase):
    """Test active filter extraction."""

    def test_extract_publisher_filter(self):
        """Test extracting publisher filter."""
        args = MockArgs(publisher="microsoft")
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(result, ["  --publisher: microsoft"])

    def test_extract_include_ids_filter(self):
        """Test extracting include_ids filter."""
        args = MockArgs(include_ids="ext1,ext2")
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(result, ["  --include-ids: ext1,ext2"])

    def test_extract_exclude_ids_filter(self):
        """Test extracting exclude_ids filter."""
        args = MockArgs(exclude_ids="ext3,ext4")
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(result, ["  --exclude-ids: ext3,ext4"])

    def test_extract_min_risk_level_filter(self):
        """Test extracting min_risk_level filter."""
        args = MockArgs(min_risk_level="high")
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(result, ["  --min-risk-level: high"])

    def test_extract_multiple_filters(self):
        """Test extracting multiple filters."""
        args = MockArgs(
            publisher="microsoft",
            include_ids="ext1,ext2",
            min_risk_level="medium",
        )
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(
            result,
            [
                "  --publisher: microsoft",
                "  --include-ids: ext1,ext2",
                "  --min-risk-level: medium",
            ],
        )

    def test_extract_no_filters(self):
        """Test extracting when no filters are active."""
        args = MockArgs()
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(result, [])

    def test_extract_filters_with_none_values(self):
        """Test extracting filters when values are explicitly None."""
        args = MockArgs(
            publisher=None, include_ids=None, exclude_ids=None, min_risk_level=None
        )
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(result, [])

    def test_extract_filters_with_empty_strings(self):
        """Test extracting filters when values are empty strings."""
        args = MockArgs(publisher="", include_ids="", exclude_ids="")
        result = FilterHelpGenerator.extract_active_filters(args)
        self.assertEqual(result, [])


@pytest.mark.unit
class TestFilterHelpGeneratorPublisherCheck(unittest.TestCase):
    """Test publisher filter detection."""

    def test_has_publisher_filter_true(self):
        """Test detecting active publisher filter."""
        args = MockArgs(publisher="microsoft")
        result = FilterHelpGenerator.has_publisher_filter(args)
        self.assertTrue(result)

    def test_has_publisher_filter_false_none(self):
        """Test detecting no publisher filter when None."""
        args = MockArgs(publisher=None)
        result = FilterHelpGenerator.has_publisher_filter(args)
        self.assertFalse(result)

    def test_has_publisher_filter_false_empty(self):
        """Test detecting no publisher filter when empty string."""
        args = MockArgs(publisher="")
        result = FilterHelpGenerator.has_publisher_filter(args)
        self.assertFalse(result)

    def test_has_publisher_filter_no_attribute(self):
        """Test detecting no publisher filter when attribute missing."""
        args = object()  # No publisher attribute
        result = FilterHelpGenerator.has_publisher_filter(args)
        self.assertFalse(result)


@pytest.mark.unit
class TestFilterHelpGeneratorSuggestions(unittest.TestCase):
    """Test suggestion message generation."""

    def test_generate_suggestions_with_filtered_out(self):
        """Test generating suggestions when extensions were filtered out."""
        result = FilterHelpGenerator.generate_suggestion_messages(10, False)
        self.assertEqual(
            result, ["Tip: 10 extensions were found, but all were filtered out."]
        )

    def test_generate_suggestions_with_publisher_filter(self):
        """Test generating suggestions with publisher filter active."""
        result = FilterHelpGenerator.generate_suggestion_messages(5, True)
        expected = [
            "Tip: 5 extensions were found, but all were filtered out.",
            "Tip: Publisher names are case-insensitive but must match exactly.",
            "     Run without filters to see available publishers.",
        ]
        self.assertEqual(result, expected)

    def test_generate_suggestions_no_original_extensions(self):
        """Test generating suggestions when no extensions were found originally."""
        result = FilterHelpGenerator.generate_suggestion_messages(0, False)
        self.assertEqual(result, [])

    def test_generate_suggestions_publisher_only_no_filtered_out(self):
        """Test generating suggestions with publisher filter but no filtered extensions."""
        result = FilterHelpGenerator.generate_suggestion_messages(0, True)
        expected = [
            "Tip: Publisher names are case-insensitive but must match exactly.",
            "     Run without filters to see available publishers.",
        ]
        self.assertEqual(result, expected)

    def test_generate_suggestions_single_extension_filtered(self):
        """Test generating suggestions with single extension filtered."""
        result = FilterHelpGenerator.generate_suggestion_messages(1, False)
        self.assertEqual(
            result, ["Tip: 1 extensions were found, but all were filtered out."]
        )

    def test_generate_suggestions_many_extensions_filtered(self):
        """Test generating suggestions with many extensions filtered."""
        result = FilterHelpGenerator.generate_suggestion_messages(100, True)
        self.assertEqual(len(result), 3)
        self.assertIn("100 extensions", result[0])


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFilterHelpGeneratorExtractFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterHelpGeneratorPublisherCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterHelpGeneratorSuggestions))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
