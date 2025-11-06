"""
Tests for marker categorization and synchronization.

Ensures that marker categories in scripts/lib/marker_categories.py are properly
synchronized with markers defined in pyproject.toml.
"""

import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.marker_config import (
    get_marker_names,
    get_markers,
    parse_marker_category,
    TEST_GROUP_MARKERS,
    BEHAVIORAL_MARKERS,
    META_MARKERS,
    is_test_group_marker,
    is_behavioral_marker,
    is_meta_marker,
)


@pytest.mark.unit
class TestMarkerCategorization:
    """Test marker categorization system."""

    def test_all_markers_are_categorized(self):
        """Ensure all pyproject.toml markers are in categories module."""
        toml_markers = get_marker_names()
        categorized = TEST_GROUP_MARKERS() | BEHAVIORAL_MARKERS()

        # All TOML markers should be categorized
        uncategorized = toml_markers - categorized
        assert not uncategorized, (
            f"Found uncategorized markers: {sorted(uncategorized)}. "
            f"Please add [GROUP] or [BEHAVIORAL] tag to marker description "
            f"in pyproject.toml"
        )

    def test_no_missing_markers_in_toml(self):
        """Ensure categories don't reference non-existent markers."""
        toml_markers = get_marker_names()
        categorized = TEST_GROUP_MARKERS() | BEHAVIORAL_MARKERS()

        # All categorized markers should exist in TOML
        missing = categorized - toml_markers
        assert not missing, (
            f"Markers in categories but missing from pyproject.toml: {sorted(missing)}. "
            f"Please add them to [tool.pytest.ini_options].markers "
            f"or remove [TAG] from marker description"
        )

    def test_all_markers_have_category_tags(self):
        """Ensure all markers in pyproject.toml have [TAG] in description."""
        markers = get_markers()
        untagged = []

        for name, desc in markers.items():
            category = parse_marker_category(desc)
            if category is None:
                untagged.append(name)

        assert not untagged, (
            f"Markers missing [GROUP] or [BEHAVIORAL] tag: {sorted(untagged)}. "
            f"All markers must have a category tag in their description."
        )

    def test_parse_marker_category_with_valid_tags(self):
        """Test parsing of valid category tags."""
        assert parse_marker_category("[GROUP] Unit tests") == "GROUP"
        assert parse_marker_category("[BEHAVIORAL] Slow tests") == "BEHAVIORAL"
        assert parse_marker_category("  [GROUP]  Some description  ") == "GROUP"

    def test_parse_marker_category_without_tags(self):
        """Test parsing returns None for descriptions without tags."""
        assert parse_marker_category("No tag here") is None
        assert parse_marker_category("") is None
        assert parse_marker_category("GROUP without brackets") is None
        assert parse_marker_category("[") is None
        assert parse_marker_category("[]") is None

    def test_no_overlap_between_categories(self):
        """Ensure marker categories don't overlap."""
        group_and_behavioral = TEST_GROUP_MARKERS() & BEHAVIORAL_MARKERS()
        group_and_meta = TEST_GROUP_MARKERS() & META_MARKERS
        behavioral_and_meta = BEHAVIORAL_MARKERS() & META_MARKERS

        assert (
            not group_and_behavioral
        ), f"Markers in both TEST_GROUP and BEHAVIORAL: {group_and_behavioral}"
        assert (
            not group_and_meta
        ), f"Markers in both TEST_GROUP and META: {group_and_meta}"
        assert (
            not behavioral_and_meta
        ), f"Markers in both BEHAVIORAL and META: {behavioral_and_meta}"

    def test_expected_test_group_markers_present(self):
        """Verify expected test group markers are defined."""
        expected = {
            "unit",
            "security",
            "architecture",
            "parallel",
            "integration",
            "real_api",
            "mock_validation",
        }

        assert expected.issubset(
            TEST_GROUP_MARKERS()
        ), f"Missing expected test group markers: {expected - TEST_GROUP_MARKERS()}"

    def test_expected_behavioral_markers_present(self):
        """Verify expected behavioral markers are defined."""
        expected = {"slow", "property_based"}

        assert expected.issubset(
            BEHAVIORAL_MARKERS()
        ), f"Missing expected behavioral markers: {expected - BEHAVIORAL_MARKERS()}"

    def test_expected_meta_markers_present(self):
        """Verify expected meta markers are defined."""
        expected = {"unmarked", "all"}

        assert expected.issubset(
            META_MARKERS
        ), f"Missing expected meta markers: {expected - META_MARKERS}"

    def test_is_test_group_marker_helper(self):
        """Test is_test_group_marker helper function."""
        assert is_test_group_marker("unit")
        assert is_test_group_marker("security")
        assert not is_test_group_marker("slow")
        assert not is_test_group_marker("unmarked")
        assert not is_test_group_marker("fake-marker")

    def test_is_behavioral_marker_helper(self):
        """Test is_behavioral_marker helper function."""
        assert is_behavioral_marker("slow")
        assert is_behavioral_marker("property_based")
        assert not is_behavioral_marker("unit")
        assert not is_behavioral_marker("unmarked")
        assert not is_behavioral_marker("fake-marker")

    def test_is_meta_marker_helper(self):
        """Test is_meta_marker helper function."""
        assert is_meta_marker("unmarked")
        assert is_meta_marker("all")
        assert not is_meta_marker("unit")
        assert not is_meta_marker("slow")
        assert not is_meta_marker("fake-marker")

    def test_meta_markers_not_in_pyproject_toml(self):
        """Ensure meta markers are not defined in pyproject.toml."""
        toml_markers = get_marker_names()

        # Meta markers should NOT be in pyproject.toml
        meta_in_toml = META_MARKERS & toml_markers
        assert not meta_in_toml, (
            f"Meta markers should not be in pyproject.toml: {meta_in_toml}. "
            f"Meta markers are runtime-only and created by the test runner."
        )
