#!/usr/bin/env python3
"""
Coverage integration for test execution using pytest-cov.

This module manages coverage measurement via pytest-cov plugin,
report generation, and threshold validation.

pytest-cov integrates seamlessly with pytest-xdist for parallel execution.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from .test_utils import Colors

# Optional coverage.py support (for report generation)
try:
    import coverage

    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False


class CoverageManager:
    """Manages coverage measurement and reporting."""

    def __init__(
        self,
        enabled: bool,
        formats: str = "term",
        threshold: Optional[float] = None,
    ):
        """
        Initialize coverage manager.

        Args:
            enabled: Whether coverage is enabled
            formats: Comma-separated list of report formats (term, html, xml, json)
            threshold: Minimum coverage percentage required (or None)
        """
        self.enabled = enabled
        self.formats = formats.split(",") if formats else ["term"]
        self.threshold = threshold
        self.coverage_used = False

        # Validate pytest-cov is available if enabled
        if self.enabled and not self._validate_pytest_cov():
            print(
                f"{Colors.YELLOW}Warning: pytest-cov not found. "
                f"Install with: pip install pytest-cov{Colors.RESET}",
                file=sys.stderr,
            )
            self.enabled = False

    def _validate_pytest_cov(self) -> bool:
        """
        Validate that pytest-cov plugin is available.

        Returns:
            True if pytest-cov is available, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--co", "--cov"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            # pytest-cov is available if command doesn't error about unknown option
            return "unrecognized arguments: --cov" not in result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_coverage_args(self, append: bool = False) -> List[str]:
        """
        Get pytest-cov arguments for coverage measurement.

        Args:
            append: Whether to append coverage data (True) or overwrite (False)

        Returns:
            List of pytest-cov arguments to add to pytest command
        """
        if not self.enabled:
            return []

        self.coverage_used = True

        # Build pytest-cov arguments
        args = [
            "--cov=vscode_scanner",  # Package to measure coverage for
            "--cov-branch",  # Include branch coverage
        ]

        # Add --cov-append for subsequent test groups (combines coverage data)
        if append:
            args.append("--cov-append")

        # Add report format arguments
        for fmt in self.formats:
            fmt = fmt.strip()
            if fmt == "term":
                args.append("--cov-report=term")
            elif fmt == "html":
                args.append("--cov-report=html")
            elif fmt == "xml":
                args.append("--cov-report=xml")
            elif fmt == "json":
                args.append("--cov-report=json")

        return args

    def generate_reports(self, show_output: bool = True):
        """
        Display coverage report locations (pytest-cov generates reports during execution).

        Args:
            show_output: Whether to print report information messages
        """
        if not self.enabled or not self.coverage_used:
            return

        if show_output:
            print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
            print(f"{Colors.BOLD}COVERAGE REPORTS{Colors.RESET}")
            print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

            # Show report locations
            for fmt in self.formats:
                fmt = fmt.strip()

                if fmt == "html":
                    html_dir = Path("htmlcov")
                    print(
                        f"{Colors.GREEN}✓{Colors.RESET} HTML coverage report: {html_dir}/index.html"
                    )
                elif fmt == "xml":
                    xml_file = Path("coverage.xml")
                    print(
                        f"{Colors.GREEN}✓{Colors.RESET} XML coverage report: {xml_file}"
                    )
                elif fmt == "json":
                    json_file = Path("coverage.json")
                    print(
                        f"{Colors.GREEN}✓{Colors.RESET} JSON coverage report: {json_file}"
                    )

        # Validate threshold if specified
        if self.threshold is not None:
            self._validate_threshold_from_file(show_output)

    def _validate_threshold_from_file(self, show_output: bool) -> bool:
        """
        Validate coverage meets threshold requirement by loading from .coverage file.

        Args:
            show_output: Whether to print validation results

        Returns:
            True if coverage meets threshold, False otherwise
        """
        if not COVERAGE_AVAILABLE:
            if show_output:
                print(
                    f"{Colors.YELLOW}Warning: coverage module not available for threshold validation{Colors.RESET}",
                    file=sys.stderr,
                )
            return True

        try:
            # Load coverage data from file (created by pytest-cov)
            cov = coverage.Coverage()
            cov.load()

            # Get total coverage percentage
            total_coverage = cov.report(file=None, show_missing=False)

            if show_output:
                print(f"\n{Colors.BOLD}Coverage Threshold Validation:{Colors.RESET}")
                print(f"  Required: {self.threshold}%")
                print(f"  Actual:   {total_coverage:.2f}%")

            if total_coverage < self.threshold:
                if show_output:
                    print(
                        f"  Status:   {Colors.RED}✗ FAILED{Colors.RESET} "
                        f"(below threshold by {self.threshold - total_coverage:.2f}%)"
                    )
                return False
            else:
                if show_output:
                    print(
                        f"  Status:   {Colors.GREEN}✓ PASSED{Colors.RESET} "
                        f"(exceeds threshold by {total_coverage - self.threshold:.2f}%)"
                    )
                return True

        except Exception as e:
            if show_output:
                print(
                    f"{Colors.YELLOW}Warning: Failed to validate threshold: {e}{Colors.RESET}",
                    file=sys.stderr,
                )
            return True

    def get_coverage_percentage(self) -> Optional[float]:
        """
        Get current coverage percentage from existing coverage data.

        Returns:
            Coverage percentage or None if not available
        """
        if not self.enabled or not COVERAGE_AVAILABLE:
            return None

        try:
            cov = coverage.Coverage()
            cov.load()
            return cov.report(file=None, show_missing=False)
        except Exception:
            return None
