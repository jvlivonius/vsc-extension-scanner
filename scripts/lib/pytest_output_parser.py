#!/usr/bin/env python3
"""
Unified parsing of pytest output.

This module provides a single, consistent way to parse pytest output
regardless of verbosity level or execution mode.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class OutputMode(Enum):
    """Output verbosity modes."""

    QUIET = "quiet"
    NORMAL = "normal"
    VERBOSE = "verbose"


@dataclass
class TestResult:
    """Parsed test execution result."""

    file: str
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    duration: float
    status: str  # PASS, FAIL, SKIP, ERROR
    output: str = ""
    error: str = ""

    @property
    def success(self) -> bool:
        """Check if test file passed."""
        return self.status == "PASS"


class PytestOutputParser:
    """Parse pytest output consistently."""

    def __init__(self):
        """Initialize parser."""
        # Regex patterns for pytest output
        self.passed_pattern = re.compile(r"(\d+) passed")
        self.failed_pattern = re.compile(r"(\d+) failed")
        self.skipped_pattern = re.compile(r"(\d+) skipped")
        self.error_pattern = re.compile(r"(\d+) error")
        self.duration_pattern = re.compile(r"in ([\d.]+)s")

    def parse_results(
        self,
        output: str,
        stderr: str,
        returncode: int,
        file_name: str,
        start_time: float,
        end_time: float,
    ) -> TestResult:
        """
        Parse pytest output into TestResult.

        Args:
            output: stdout from pytest
            stderr: stderr from pytest
            returncode: exit code from pytest
            file_name: name of the test file/group
            start_time: start timestamp
            end_time: end timestamp

        Returns:
            Parsed TestResult object
        """
        combined_output = output + stderr

        # Parse test counts from pytest summary
        tests_passed = self._extract_count(self.passed_pattern, combined_output)
        tests_failed = self._extract_count(self.failed_pattern, combined_output)
        tests_skipped = self._extract_count(self.skipped_pattern, combined_output)
        errors = self._extract_count(self.error_pattern, combined_output)

        # Errors count as failures
        tests_failed += errors

        # Total tests run
        tests_run = tests_passed + tests_failed + tests_skipped

        # Calculate duration
        duration = end_time - start_time

        # Determine status
        if returncode == 0:
            status = "PASS"
        elif tests_run == 0:
            status = "SKIP"
        elif returncode == 2:
            status = "ERROR"
        else:
            status = "FAIL"

        return TestResult(
            file=file_name,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_skipped=tests_skipped,
            duration=duration,
            status=status,
            output=output if status != "PASS" else "",
            error=stderr if returncode != 0 else "",
        )

    def _extract_count(self, pattern: re.Pattern, text: str) -> int:
        """
        Extract count from pytest output using regex pattern.

        Args:
            pattern: Compiled regex pattern
            text: Text to search

        Returns:
            Extracted count or 0 if not found
        """
        match = pattern.search(text)
        if match:
            return int(match.group(1))
        return 0

    def extract_failures(self, output: str) -> List[str]:
        """
        Extract failed test names from pytest output.

        Args:
            output: pytest output text

        Returns:
            List of failed test names
        """
        failures = []
        lines = output.split("\n")

        for line in lines:
            if " FAILED" in line:
                # Extract test name (before FAILED)
                test_name = line.split(" FAILED")[0].strip()
                if test_name and "::" in test_name:
                    failures.append(test_name)

        return failures

    def extract_skips(self, output: str) -> List[str]:
        """
        Extract skipped test names from pytest output.

        Args:
            output: pytest output text

        Returns:
            List of skipped test names
        """
        skips = []
        lines = output.split("\n")

        for line in lines:
            if " SKIPPED" in line:
                # Extract test name (before SKIPPED)
                test_name = line.split(" SKIPPED")[0].strip()
                if test_name and "::" in test_name:
                    skips.append(test_name)

        return skips

    def should_show_output(self, result: TestResult, mode: OutputMode) -> bool:
        """
        Determine if output should be shown based on mode.

        Args:
            result: Test result to check
            mode: Output mode

        Returns:
            True if output should be displayed
        """
        if mode == OutputMode.VERBOSE:
            return True
        elif mode == OutputMode.QUIET:
            # Only show failures and errors in quiet mode
            return result.status in ["FAIL", "ERROR"]
        else:  # NORMAL
            return True
