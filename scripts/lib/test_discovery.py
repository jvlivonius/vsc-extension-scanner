#!/usr/bin/env python3
"""
Test Discovery Module for VS Code Extension Scanner Test Suite.

This module provides functionality for auto-discovering test files using pytest markers,
organizing them into test groups, and managing the test registry cache.

Key Components:
- TestFile: Dataclass representing test file metadata
- _TestCollector: Pytest plugin for collecting test files and markers
- discover_test_files(): Main discovery function using pytest collection
- get_test_registry(): Lazy-loading registry with caching

Usage:
    from lib.test_discovery import TestFile, discover_test_files, get_test_registry

    # Discover all test files
    test_files = discover_test_files()

    # Get cached registry
    registry = get_test_registry()
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Conditional pytest imports
try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

# Import from sibling modules
from .test_utils import Colors
from .marker_config import get_required_markers, normalize_marker_name

# TestGroup will be imported from marker_config after Phase 2
# For now, we need to handle the circular dependency
# by importing it at runtime in functions that need it


@dataclass
class TestFile:
    """Test file metadata."""

    path: Path
    group: "TestGroup"  # Forward reference, will be resolved at runtime
    description: str
    slow: bool = False  # Slow test marker (>1s duration, excluded by --fast)
    real_api: bool = False  # Real API tests (network-dependent)
    integration: bool = False  # Integration tests (mocked but complex)
    property_based: bool = False  # Property-based tests (hypothesis)


class _TestCollector:
    """Pytest plugin for collecting test files and markers."""

    def __init__(self, test_group_type):
        """
        Initialize the test collector.

        Args:
            test_group_type: TestGroup enum class (passed to avoid circular import)
        """
        self.test_files: Dict = {}
        self.file_markers: Dict[Path, set] = {}
        self.all_test_files: set = set()
        self.TestGroup = (
            test_group_type  # Store TestGroup enum  # pylint: disable=invalid-name
        )

        # Store required markers for later use (standardized to underscores)
        required_markers = get_required_markers()
        self.required_markers_with_variants = required_markers.copy()
        self.required_markers = required_markers

    def pytest_collection_finish(self, session):
        """Called after pytest collection is complete."""
        for item in session.items:
            file_path = Path(item.fspath)
            if not file_path.exists():
                continue

            self.all_test_files.add(file_path)
            self._collect_file_markers(file_path, item)
            self._map_to_test_group(file_path, item)

    def _collect_file_markers(self, file_path: Path, item) -> None:
        """Aggregate markers per file."""
        markers = {marker.name for marker in item.iter_markers()}

        if file_path not in self.file_markers:
            self.file_markers[file_path] = set()
        self.file_markers[file_path].update(markers)

    def _map_to_test_group(self, file_path: Path, item) -> None:
        """Map file to test group based on markers."""
        markers = {marker.name for marker in item.iter_markers()}

        for marker_name in markers:
            # Normalize marker name (handle both hyphen and underscore variants)
            normalized_marker = normalize_marker_name(marker_name)

            # Check if this is a required marker
            if normalized_marker in self.required_markers:
                # Find corresponding TestGroup
                test_group = self.TestGroup.from_string(normalized_marker)
                if test_group:
                    if test_group not in self.test_files:
                        self.test_files[test_group] = set()
                    self.test_files[test_group].add(file_path)
                    break  # Use first matching marker


def _run_pytest_collection(test_group_type) -> _TestCollector:
    """
    Run pytest collection and return collector.

    Args:
        test_group_type: TestGroup enum class

    Returns:
        TestCollector instance with collected test files and markers
    """
    collector = _TestCollector(test_group_type)

    # Suppress pytest output during collection
    import io

    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        pytest.main(["--collect-only", "-qq", "tests/"], plugins=[collector])
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return collector


def _convert_to_test_files(
    collector: _TestCollector,
) -> Dict:
    """
    Convert collected file paths to TestFile objects.

    Args:
        collector: TestCollector instance with collected files

    Returns:
        Dictionary mapping TestGroup to list of TestFile objects
    """
    project_root = Path.cwd()
    result = {}

    for group, file_paths in collector.test_files.items():
        test_files = [
            _create_test_file(file_path, group, collector, project_root)
            for file_path in sorted(file_paths)
        ]
        result[group] = test_files

    return result


def _create_test_file(
    file_path: Path, group, collector: _TestCollector, project_root: Path
) -> TestFile:
    """
    Create TestFile object from file path and metadata.

    Args:
        file_path: Path to test file
        group: Test group the file belongs to
        collector: TestCollector instance with marker information
        project_root: Project root directory

    Returns:
        TestFile object with metadata
    """
    relative_path = (
        file_path.relative_to(project_root) if file_path.is_absolute() else file_path
    )

    filename = file_path.name.lower()
    file_markers = collector.file_markers.get(file_path, set())

    # Access TestGroup enum through collector to avoid circular import
    TestGroup = collector.TestGroup  # pylint: disable=invalid-name

    return TestFile(
        path=relative_path,
        group=group,
        description="Auto-discovered from markers",
        slow="slow" in file_markers,
        real_api=(
            "real_api" in filename
            or group == TestGroup.REAL_API
            or "real_api" in file_markers
        ),
        integration=(
            "integration" in filename
            or group == TestGroup.INTEGRATION
            or "integration" in file_markers
        ),
        property_based=("property" in filename or "property_based" in file_markers),
    )


def _add_unmarked_tests(result: Dict, collector: _TestCollector) -> None:
    """
    Add unmarked test files to result.

    Args:
        result: Dictionary to add unmarked tests to (modified in-place)
        collector: TestCollector instance with file information
    """
    # Collect all marked files
    marked_files = {
        f.path if isinstance(f, TestFile) else Path(f)
        for files in result.values()
        for f in files
    }

    project_root = Path.cwd()
    unmarked_files = []

    # Access TestGroup enum through collector
    TestGroup = collector.TestGroup  # pylint: disable=invalid-name

    for file_path in sorted(collector.all_test_files):
        relative_path = (
            file_path.relative_to(project_root)
            if file_path.is_absolute()
            else file_path
        )

        # Check if this file is not in any marked group
        if relative_path not in marked_files:
            file_markers = collector.file_markers.get(file_path, set())

            # Check if file truly has no required markers
            if not file_markers & collector.required_markers_with_variants:
                unmarked_files.append(
                    TestFile(
                        path=relative_path,
                        group=TestGroup.UNMARKED,
                        description="Tests without required pytest markers",
                        slow="slow" in file_markers,
                        real_api=False,
                        integration=False,
                        property_based="property_based" in file_markers,
                    )
                )

    if unmarked_files:
        result[TestGroup.UNMARKED] = unmarked_files


def discover_test_files(test_group_type) -> Dict:
    """
    Auto-discover test files using pytest markers.

    Args:
        test_group_type: TestGroup enum class (to avoid circular import)

    Returns:
        Dictionary mapping TestGroup to list of discovered TestFile objects.
        Returns empty dict if pytest is not available.
    """
    if not PYTEST_AVAILABLE:
        print(
            f"{Colors.YELLOW}Warning: pytest not available for auto-discovery.{Colors.RESET}"
        )
        return {}

    # Import pytest modules (needed for type hints in TestCollector)
    from _pytest.config import Config
    from _pytest.main import Session

    # Run pytest collection
    collector = _run_pytest_collection(test_group_type)

    # Convert to TestFile objects
    result = _convert_to_test_files(collector)

    # Add unmarked tests
    _add_unmarked_tests(result, collector)

    return result


# Auto-discover test files from pytest markers (replaces manual TEST_REGISTRY)
_test_registry_cache: Optional[Dict] = None


def get_test_registry(test_group_type) -> Dict:
    """
    Get test registry with lazy loading.

    Results are cached to avoid repeated pytest collection overhead.
    Auto-validates on first load and warns about discrepancies.

    Args:
        test_group_type: TestGroup enum class (to avoid circular import)

    Returns:
        Dictionary mapping TestGroup to list of discovered TestFile objects
    """
    global _test_registry_cache  # pylint: disable=global-statement

    if _test_registry_cache is not None:
        return _test_registry_cache

    # Discover tests using pytest markers
    discovered = discover_test_files(test_group_type)

    if not discovered:
        print(
            f"{Colors.YELLOW}Warning: No tests discovered via pytest markers.{Colors.RESET}"
        )
        return {}

    _test_registry_cache = discovered
    return discovered
