#!/usr/bin/env python3
"""
VS Code Extension Scanner - Test Suite Runner

Simplified test execution with auto-discovery, dynamic marker loading,
and flexible group selection.

For complete usage information including available test groups and markers:
    python3 scripts/run_tests.py --help
"""

import sys
import subprocess
import time
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Optional coverage.py support
try:
    import coverage

    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False

# Optional pytest support
try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import shared utilities and components from lib package
from lib import (
    Colors,
    EXIT_SUCCESS,
    EXIT_FAILURE,
    EXIT_NOT_FOUND,
    EXIT_ERROR,
    PytestExecutor,
    PytestOutputParser,
    OutputMode,
    TestResult,
    CoverageManager,
    OutputFormatter,
    TestFile,
    discover_test_files,
    get_test_registry,
    create_test_group_enum,
    parse_filter_expression,
)

# ==============================================================================
# Test Group Definitions
# ==============================================================================

# Create TestGroup enum with dynamic markers from pyproject.toml
# Note: create_test_group_enum, parse_filter_expression now imported from lib.marker_config
# Note: TestFile, discover_test_files, get_test_registry now imported from lib.test_discovery
TestGroup = create_test_group_enum()


# ==============================================================================
# Test Orchestrator
# ==============================================================================


class TestOrchestrator:
    """Orchestrates test execution workflow using composition pattern."""

    def __init__(self, args):
        """
        Initialize orchestrator with components.

        Args:
            args: Parsed command-line arguments
        """
        # Initialize components
        self.executor = PytestExecutor()
        self.parser = PytestOutputParser()

        # Configure coverage
        self.coverage = CoverageManager(
            enabled=args.coverage,
            formats=args.coverage_format,
            threshold=args.coverage_threshold,
        )

        # Configure output formatter
        output_mode = (
            OutputMode.QUIET
            if args.quiet
            else (OutputMode.VERBOSE if args.verbose else OutputMode.NORMAL)
        )
        self.formatter = OutputFormatter(output_mode)

        # Store configuration
        self.fast = args.fast
        self.args = args
        self.results = []
        self.start_time = time.time()
        self._coverage_append = False  # Track coverage append state

    def discover_tests(
        self, groups: List[TestGroup]
    ) -> Dict[TestGroup, List[TestFile]]:
        """
        Discover test files for specified groups.

        Args:
            groups: List of test groups

        Returns:
            Dictionary mapping group to test files
        """
        discovered = {}

        for group in groups:
            # Get test files from registry
            all_test_files = get_test_registry(TestGroup).get(group, [])

            # Filter based on fast flag (skip slow tests)
            if self.fast:
                test_files = [tf for tf in all_test_files if not tf.slow]
            else:
                test_files = all_test_files

            if test_files:
                discovered[group] = test_files

        return discovered

    def _prepare_groups(self, groups: List[TestGroup]) -> tuple[List[TestGroup], bool]:
        """
        Expand ALL group and separate UNMARKED.

        Args:
            groups: List of test groups to run

        Returns:
            Tuple of (filtered_groups, has_unmarked)
        """
        # Expand ALL to all groups (including UNMARKED)
        if TestGroup.ALL in groups:
            groups = [g for g in TestGroup if g != TestGroup.ALL]

        # Separate UNMARKED group to run it last
        has_unmarked = TestGroup.UNMARKED in groups
        if has_unmarked:
            groups = [g for g in groups if g != TestGroup.UNMARKED]

        return groups, has_unmarked

    def _discover_and_validate(
        self, groups: List[TestGroup], has_unmarked: bool
    ) -> Dict[TestGroup, List[TestFile]]:
        """
        Discover tests and print header.

        Args:
            groups: List of test groups to discover
            has_unmarked: Whether UNMARKED group should be included

        Returns:
            Dictionary mapping TestGroup to discovered test files
        """
        # Build group list for header
        group_names = [g.value for g in groups]
        if has_unmarked:
            group_names.append(TestGroup.UNMARKED.value)

        # Print header
        self.formatter.print_header(group_names, self.fast)

        # Discover tests
        all_groups_to_discover = groups + ([TestGroup.UNMARKED] if has_unmarked else [])
        return self.discover_tests(all_groups_to_discover)

    def _execute_test_groups(
        self, groups: List[TestGroup], discovered: Dict[TestGroup, List[TestFile]]
    ) -> None:
        """
        Execute regular test groups.

        Args:
            groups: List of test groups to execute
            discovered: Dictionary of discovered test files per group
        """
        for group in groups:
            test_files = discovered.get(group, [])
            if test_files:
                self._execute_single_group(group, test_files, is_unmarked=False)

    def _execute_unmarked_tests(
        self, discovered: Dict[TestGroup, List[TestFile]]
    ) -> None:
        """
        Execute UNMARKED tests with warning message.

        Args:
            discovered: Dictionary of discovered test files per group
        """
        if TestGroup.UNMARKED not in discovered:
            return

        unmarked_files = discovered[TestGroup.UNMARKED]
        self._print_unmarked_warning(unmarked_files)
        self._execute_single_group(TestGroup.UNMARKED, unmarked_files, is_unmarked=True)

    def _execute_single_group(
        self, group: TestGroup, test_files: List[TestFile], is_unmarked: bool = False
    ) -> None:
        """
        Execute tests for a single group - ELIMINATES DUPLICATION.

        Args:
            group: Test group to execute
            test_files: List of test files in the group
            is_unmarked: Whether this is the UNMARKED group
        """
        # Calculate skipped count
        skipped_count = self._calculate_skipped_count(group, test_files)

        # Print header
        self.formatter.print_group_header(group.value, len(test_files), skipped_count)

        # Build and execute pytest command
        command = self._build_pytest_command(group, test_files, is_unmarked)
        command = self._wrap_with_coverage(command)

        # Execute and parse results
        result = self._execute_and_parse(command, group, test_files)

        # Store and print
        self.results.append(result)
        self.formatter.print_result(result)
        self.formatter.print_group_summary([result])

    def _build_pytest_command(
        self, group: TestGroup, test_files: List[TestFile], is_unmarked: bool
    ) -> List[str]:
        """
        Build pytest command for group.

        Args:
            group: Test group to build command for
            test_files: List of test files in the group
            is_unmarked: Whether this is the UNMARKED group

        Returns:
            Pytest command as list of strings
        """
        test_paths = [tf.path for tf in test_files]
        verbosity = "verbose" if self.args.verbose else "normal"

        if is_unmarked:
            # No marker filtering for unmarked tests
            markers = []
            extra_args = self._build_extra_args()
            if self.fast:
                extra_args.extend(["-m", "not slow"])
        else:
            # Normal marker-based filtering
            markers = self._build_markers_list(group)
            extra_args = self._build_extra_args()

        return self.executor.build_command(
            test_paths=test_paths,
            markers=markers,
            verbosity=verbosity,
            extra_args=extra_args,
        )

    def _build_markers_list(self, group: TestGroup) -> List[str]:
        """
        Build marker expressions for pytest.

        Args:
            group: Test group to build markers for

        Returns:
            List of pytest marker expressions
        """
        markers = [group.value.replace("-", "_")]  # Group marker

        # Apply --filter if specified (OR logic for multiple filters)
        if hasattr(self.args, "filter") and self.args.filter:
            try:
                filter_expressions = parse_filter_expression(self.args.filter)
                if filter_expressions:
                    # Combine with OR: (group) and (filter1 or filter2 or ...)
                    filter_clause = " or ".join(filter_expressions)
                    markers.append(f"({filter_clause})")
            except ValueError as e:
                print(f"{Colors.RED}{e}{Colors.RESET}")
                sys.exit(EXIT_ERROR)

        # Legacy: --fast flag (should be mapped to --filter earlier, but handle here too)
        if self.fast:
            markers.append("not slow")

        return markers

    def _build_extra_args(self) -> List[str]:
        """
        Build extra arguments for pytest.

        Returns:
            List of extra pytest arguments
        """
        extra_args = []
        if self.args.verbose:
            extra_args.append("-vv")
        return extra_args

    def _wrap_with_coverage(self, command: List[str]) -> List[str]:
        """
        Wrap command with coverage if enabled.

        Args:
            command: Pytest command to wrap

        Returns:
            Wrapped command with coverage or original command
        """
        if not self.coverage.enabled:
            return command

        wrapped = self.coverage.wrap_command(command, append=self._coverage_append)
        self._coverage_append = True
        return wrapped

    def _execute_and_parse(
        self, command: List[str], group: TestGroup, test_files: List[TestFile]
    ) -> TestResult:
        """
        Execute command and parse results.

        Args:
            command: Pytest command to execute
            group: Test group being executed
            test_files: List of test files in the group

        Returns:
            Parsed test result
        """
        start_time = time.time()
        process = self.executor.run(command, capture_output=True)
        end_time = time.time()

        return self.parser.parse_results(
            output=process.stdout,
            stderr=process.stderr,
            returncode=process.returncode,
            file_name=f"{group.value} ({len(test_files)} files)",
            start_time=start_time,
            end_time=end_time,
        )

    def _calculate_skipped_count(
        self, group: TestGroup, test_files: List[TestFile]
    ) -> int:
        """
        Calculate number of skipped tests in fast mode.

        Args:
            group: Test group
            test_files: List of test files to execute

        Returns:
            Number of skipped test files
        """
        if not self.fast:
            return 0

        all_test_files = get_test_registry(TestGroup).get(group, [])
        return len(all_test_files) - len(test_files)

    def _print_unmarked_warning(self, unmarked_files: List[TestFile]) -> None:
        """
        Print warning about unmarked test files.

        Args:
            unmarked_files: List of unmarked test files
        """
        print()
        print(
            f"{Colors.YELLOW}⚠️  WARNING: Found {len(unmarked_files)} test file(s) without required pytest markers{Colors.RESET}"
        )
        print(
            f"{Colors.YELLOW}    These tests should be marked with @pytest.mark.unit (or other markers){Colors.RESET}"
        )
        print(
            f"{Colors.YELLOW}    Files: {', '.join(str(tf.path.name) for tf in unmarked_files[:3])}{' ...' if len(unmarked_files) > 3 else ''}{Colors.RESET}"
        )
        print(
            f"{Colors.YELLOW}    See docs/guides/TESTING.md for marker requirements{Colors.RESET}"
        )
        print()

    def _generate_reports(self) -> None:
        """Generate coverage and summary reports."""
        end_time = time.time()
        self.formatter.print_overall_summary(self.results, self.start_time, end_time)

        if self.coverage.enabled:
            self.coverage.generate_reports(show_output=True)

    def _export_outputs(self) -> None:
        """Export JSON/JUnit outputs if requested."""
        if not (hasattr(self.args, "output") and hasattr(self.args, "output_file")):
            return

        end_time = time.time()

        if self.args.output == "json" and self.args.output_file:
            self.formatter.export_json(
                self.results,
                Path(self.args.output_file),
                self.start_time,
                end_time,
            )
        elif self.args.output == "junit" and self.args.output_file:
            self.formatter.export_junit(
                self.results,
                Path(self.args.output_file),
                self.start_time,
                end_time,
            )

    def run_groups(self, groups: List[TestGroup]) -> int:
        """
        Run test groups and return exit code.

        Args:
            groups: List of test groups to run

        Returns:
            Exit code (0=success, 1=failures, 2=no tests, 3=error)
        """
        # Prepare groups and separate UNMARKED
        groups, has_unmarked = self._prepare_groups(groups)

        # Discover tests and validate
        discovered = self._discover_and_validate(groups, has_unmarked)

        if not discovered:
            print(f"{Colors.RED}Error: No test files discovered{Colors.RESET}")
            return EXIT_NOT_FOUND

        # Execute test groups
        self._execute_test_groups(groups, discovered)

        # Execute UNMARKED separately with warning
        if has_unmarked:
            self._execute_unmarked_tests(discovered)

        # Reporting and export
        self._generate_reports()
        self._export_outputs()

        return self._calculate_exit_code()

    def _calculate_exit_code(self) -> int:
        """
        Calculate exit code based on test results.

        Returns:
            Exit code (0=success, 1=failures, 2=no tests, 3=error)
        """
        if not self.results:
            return EXIT_NOT_FOUND

        if any(r.status == "ERROR" for r in self.results):
            return EXIT_ERROR

        if any(r.status == "FAIL" for r in self.results):
            return EXIT_FAILURE

        return EXIT_SUCCESS


# ==============================================================================
# Main Entry Point
# ==============================================================================


def generate_dynamic_help_text() -> str:
    """
    Generate dynamic help text with current markers from pyproject.toml.

    Returns:
        Formatted help text string with marker lists and usage examples
    """
    from lib.marker_config import (
        get_test_group_markers,
        get_behavioral_markers_set,
        get_marker_description,
        META_MARKERS,
    )

    # Load markers dynamically from pyproject.toml
    try:
        test_groups = sorted(get_test_group_markers())
        behavioral = sorted(get_behavioral_markers_set())
    except Exception as e:
        # Fallback if marker loading fails
        return f"""
Error loading markers from pyproject.toml: {e}

Please run: python3 scripts/run_tests.py --help
"""

    # Build help text sections
    help_text = """
Test Suite Runner for VS Code Extension Scanner

Simplified test execution with auto-discovery, dynamic marker loading, and flexible group selection.

Quick Start - Preset Aliases:
    python3 scripts/run_tests.py --fast          # Fast: all tests except slow (>1s)
    python3 scripts/run_tests.py --ci            # CI: all tests except real-api
    python3 scripts/run_tests.py --report        # Report: all tests with HTML coverage
    python3 scripts/run_tests.py --security-only # Security tests only

Group Selection (Dynamic):
    python3 scripts/run_tests.py                             # All test groups (default)
    python3 scripts/run_tests.py --include unit,security     # Specific groups only
    python3 scripts/run_tests.py --exclude slow,real-api     # All except specified
    python3 scripts/run_tests.py --include unit --exclude slow  # Combine filters

Available Groups (loaded from pyproject.toml):
"""

    # Add test group markers dynamically
    for marker in test_groups:
        desc = get_marker_description(marker) or "No description"
        # Remove [GROUP] tag from description if present
        if desc.startswith("[GROUP]"):
            desc = desc[7:].strip()
        help_text += f"    - {marker}: {desc}\n"

    # Add behavioral markers section
    help_text += "\nBehavioral Markers (execution modifiers):\n"
    for marker in behavioral:
        desc = get_marker_description(marker) or "No description"
        # Remove [BEHAVIORAL] tag from description if present
        if desc.startswith("[BEHAVIORAL]"):
            desc = desc[12:].strip()
        help_text += f"    - {marker}: {desc}\n"

    # Add meta markers section
    help_text += "\nMeta Markers (runtime-only, not in pyproject.toml):\n"
    help_text += "    - unmarked: Tests without required pytest markers\n"
    help_text += "    - all: Run all test groups\n"

    # Add advanced usage section
    help_text += """
Advanced Usage:
    python3 scripts/run_tests.py --include unit,security --fast
    python3 scripts/run_tests.py --output json --output-file results.json
    python3 scripts/run_tests.py --coverage --coverage-format html
    python3 scripts/run_tests.py --exclude unmarked,slow

Exit Codes:
    0 - All tests passed
    1 - Some tests failed
    2 - No tests found
    3 - Execution error

Version: 3.0
Updated: 2025-11-06
"""

    return help_text


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="VS Code Extension Scanner Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=generate_dynamic_help_text(),
    )

    # Test group selection (comma-separated)
    parser.add_argument(
        "--include",
        type=str,
        metavar="GROUPS",
        help="Comma-separated list of test groups to include (e.g., unit,security). "
        "Available groups loaded from pyproject.toml. Default: all groups if not specified. "
        "Use --filter for behavioral markers.",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        metavar="GROUPS",
        help="Comma-separated list of test groups to exclude (e.g., real_api). "
        "Takes precedence over --include. Use --filter for behavioral markers.",
    )

    # Behavioral marker filtering
    parser.add_argument(
        "--filter",
        type=str,
        metavar="FILTERS",
        help="Comma-separated behavioral marker filters with optional 'not' prefix. "
        "Multiple filters use OR logic (any match). "
        "Examples: 'slow', 'not slow', 'slow,not property_based'. "
        "Only behavioral markers allowed (use --include/--exclude for groups).",
    )

    # Preset aliases for common workflows
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests (alias for --filter 'not slow'). Equivalent to --filter 'not slow'.",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI preset: all tests except real_api (network-dependent)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Report preset: all tests with coverage and HTML report",
    )

    # Security-only mode
    parser.add_argument(
        "--security-only",
        action="store_true",
        help="Run security tests only (fast security validation)",
    )

    # Options
    parser.add_argument(
        "--output",
        choices=["console", "json", "junit"],
        default="console",
        help="Output format (default: console)",
    )
    parser.add_argument("--output-file", help="Output file for json/junit formats")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")

    # Coverage options
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Enable coverage measurement (requires: pip install coverage)",
    )
    parser.add_argument(
        "--coverage-format",
        default="term",
        help="Coverage report format: term,html,xml,json (comma-separated, default: term)",
    )
    parser.add_argument(
        "--coverage-threshold",
        type=float,
        metavar="PCT",
        help="Minimum required coverage percentage (e.g., 85.0)",
    )

    return parser


def apply_preset_aliases(args: argparse.Namespace) -> None:
    """
    Apply preset flags to args (--ci, --report, --security-only, --fast).

    Modifies args in-place to expand preset aliases into their equivalent
    --include/--exclude/--filter/--coverage combinations.

    Args:
        args: Parsed command-line arguments to modify
    """
    # Handle preset aliases (map to --include/--exclude)
    if args.security_only:
        # Security-only mode
        args.include = "security"
        print(
            f"{Colors.CYAN}Running security tests only (fast validation){Colors.RESET}\n"
        )

    if args.ci:
        # CI preset: all tests except real-api (unreliable in CI)
        args.exclude = "real-api" + ("," + args.exclude if args.exclude else "")
        print(
            f"{Colors.CYAN}Using --ci preset: all tests except real-api{Colors.RESET}\n"
        )

    if args.report:
        # Report preset: all tests with coverage HTML
        args.coverage = True
        if not args.coverage_format:
            args.coverage_format = "html"
        print(
            f"{Colors.CYAN}Using --report preset: all tests with coverage HTML report{Colors.RESET}\n"
        )

    # Handle --fast flag (map to --filter)
    if args.fast:
        if args.filter:
            # Combine: --fast + --filter
            args.filter = f"not slow,{args.filter}"
        else:
            args.filter = "not slow"


def parse_test_groups(args: argparse.Namespace) -> List[TestGroup]:
    """
    Parse --include/--exclude to determine test groups.

    Args:
        args: Parsed command-line arguments

    Returns:
        List of TestGroup enums to execute

    Raises:
        SystemExit: If unknown group names are specified (via sys.exit)
    """
    groups = []

    # Parse included groups
    if args.include:
        include_names = [name.strip() for name in args.include.split(",")]
        for name in include_names:
            group = TestGroup.from_string(name)
            if group:
                groups.append(group)
            else:
                print(f"{Colors.RED}Error: Unknown test group '{name}'{Colors.RESET}")
                print(
                    f"Available groups: {', '.join(sorted(g.value for g in TestGroup))}"
                )
                sys.exit(EXIT_ERROR)
    else:
        # No --include specified: include ALL groups by default
        groups.append(TestGroup.ALL)

    # Parse and apply excluded groups
    if args.exclude:
        exclude_names = [name.strip() for name in args.exclude.split(",")]
        exclude_groups = []
        for name in exclude_names:
            group = TestGroup.from_string(name)
            if group:
                exclude_groups.append(group)
            else:
                print(f"{Colors.RED}Error: Unknown test group '{name}'{Colors.RESET}")
                print(
                    f"Available groups: {', '.join(sorted(g.value for g in TestGroup))}"
                )
                sys.exit(EXIT_ERROR)

        # Apply exclusions
        if TestGroup.ALL in groups:
            # Expand ALL and then exclude
            groups = [
                g
                for g in TestGroup
                if g not in (TestGroup.ALL,) and g not in exclude_groups
            ]
        else:
            # Remove excluded groups from explicit includes
            groups = [g for g in groups if g not in exclude_groups]

    return groups


def validate_output_arguments(args: argparse.Namespace) -> Optional[int]:
    """
    Validate output format arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Error code if validation fails, None if valid
    """
    if args.output in ["json", "junit"] and not args.output_file:
        print(
            f"Error: --output-file required for {args.output} format", file=sys.stderr
        )
        return EXIT_ERROR
    return None


def main():
    """Main entry point - orchestration only."""
    parser = create_argument_parser()
    args = parser.parse_args()

    apply_preset_aliases(args)
    groups = parse_test_groups(args)

    error_code = validate_output_arguments(args)
    if error_code:
        return error_code

    orchestrator = TestOrchestrator(args)
    return orchestrator.run_groups(groups)


if __name__ == "__main__":
    sys.exit(main())
