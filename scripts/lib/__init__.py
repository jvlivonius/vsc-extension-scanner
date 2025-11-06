#!/usr/bin/env python3
"""
Testing infrastructure package for VS Code Extension Scanner.

This package contains reusable components for test execution, coverage,
test discovery, and output formatting.
"""

# Core utilities
from .test_utils import (
    Colors,
    EXIT_SUCCESS,
    EXIT_FAILURE,
    EXIT_NOT_FOUND,
    EXIT_ERROR,
)

# Test execution components
from .pytest_executor import PytestExecutor
from .pytest_output_parser import (
    PytestOutputParser,
    OutputMode,
    TestResult,
)
from .coverage_manager import CoverageManager
from .output_formatter import OutputFormatter

# Test discovery components
from .test_discovery import (
    TestFile,
    discover_test_files,
    get_test_registry,
)

# Test group and filter components
from .marker_config import (
    create_test_group_enum,
    parse_filter_expression,
)

__all__ = [
    # Utilities
    "Colors",
    "EXIT_SUCCESS",
    "EXIT_FAILURE",
    "EXIT_NOT_FOUND",
    "EXIT_ERROR",
    # Components
    "PytestExecutor",
    "PytestOutputParser",
    "OutputMode",
    "TestResult",
    "CoverageManager",
    "OutputFormatter",
    # Test Discovery
    "TestFile",
    "discover_test_files",
    "get_test_registry",
    # Test Groups and Filters
    "create_test_group_enum",
    "parse_filter_expression",
]

__version__ = "1.0.0"
