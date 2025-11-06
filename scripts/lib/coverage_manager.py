#!/usr/bin/env python3
"""
Coverage integration for test execution.

This module manages coverage measurement, report generation,
and threshold validation.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from .test_utils import Colors

# Optional coverage.py support
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

        # Validate coverage command is available if enabled
        if self.enabled and not self._validate_coverage_command():
            print(
                f"{Colors.YELLOW}Warning: coverage command not found. "
                f"Install with: pip install coverage{Colors.RESET}",
                file=sys.stderr,
            )
            self.enabled = False

    def _validate_coverage_command(self) -> bool:
        """
        Validate that coverage command is available.

        Returns:
            True if coverage command works, False otherwise
        """
        try:
            result = subprocess.run(
                ["coverage", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def wrap_command(self, pytest_args: List[str], append: bool = False) -> List[str]:
        """
        Wrap pytest command with coverage if enabled.

        Args:
            pytest_args: pytest command arguments (e.g., ['pytest', 'tests/', '-v'])
            append: Whether to append coverage data (True) or overwrite (False)

        Returns:
            Command with coverage wrapper if enabled, otherwise original command
        """
        if not self.enabled:
            return pytest_args

        self.coverage_used = True

        # Build coverage command
        command = ["coverage", "run"]

        # Add --append for subsequent test groups
        if append:
            command.append("--append")

        # Add -m pytest
        command.extend(["-m"])

        # Add pytest arguments (skip 'python -m pytest' prefix if present)
        if pytest_args[0] == sys.executable and "-m" in pytest_args:
            # Skip 'python -m' prefix
            pytest_idx = pytest_args.index("pytest") if "pytest" in pytest_args else 2
            command.extend(pytest_args[pytest_idx:])
        else:
            command.extend(pytest_args)

        return command

    def generate_reports(self, show_output: bool = True):
        """
        Generate coverage reports in requested formats.

        Args:
            show_output: Whether to print report generation messages
        """
        if not self.enabled or not self.coverage_used:
            return

        if not COVERAGE_AVAILABLE:
            if show_output:
                print(
                    f"{Colors.YELLOW}Warning: coverage module not available{Colors.RESET}",
                    file=sys.stderr,
                )
            return

        try:
            # Load coverage data
            cov = coverage.Coverage()
            cov.load()

            if show_output:
                print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
                print(f"{Colors.BOLD}COVERAGE REPORT{Colors.RESET}")
                print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

            # Generate requested report formats
            for fmt in self.formats:
                fmt = fmt.strip()

                if fmt == "term":
                    # Terminal report
                    cov.report(show_missing=False, skip_covered=False)

                elif fmt == "html":
                    # HTML report
                    html_dir = Path("htmlcov")
                    cov.html_report(directory=str(html_dir))
                    if show_output:
                        print(
                            f"\n{Colors.GREEN}✓{Colors.RESET} HTML coverage report: {html_dir}/index.html"
                        )

                elif fmt == "xml":
                    # XML report (for CI/CD)
                    xml_file = Path("coverage.xml")
                    cov.xml_report(outfile=str(xml_file))
                    if show_output:
                        print(
                            f"\n{Colors.GREEN}✓{Colors.RESET} XML coverage report: {xml_file}"
                        )

                elif fmt == "json":
                    # JSON report
                    json_file = Path("coverage.json")
                    cov.json_report(outfile=str(json_file))
                    if show_output:
                        print(
                            f"\n{Colors.GREEN}✓{Colors.RESET} JSON coverage report: {json_file}"
                        )

            # Validate threshold if specified
            if self.threshold is not None:
                self._validate_threshold(cov, show_output)

        except Exception as e:
            if show_output:
                print(
                    f"{Colors.YELLOW}Warning: Failed to generate coverage reports: {e}{Colors.RESET}",
                    file=sys.stderr,
                )

    def _validate_threshold(self, cov, show_output: bool) -> bool:
        """
        Validate coverage meets threshold requirement.

        Args:
            cov: Coverage instance
            show_output: Whether to print validation results

        Returns:
            True if coverage meets threshold, False otherwise
        """
        if not COVERAGE_AVAILABLE or not cov:
            return True

        try:
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
