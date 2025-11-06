#!/usr/bin/env python3
"""
Testing infrastructure package for VS Code Extension Scanner.

This package contains reusable components for test execution, coverage,
and output formatting.
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
]

__version__ = "1.0.0"
