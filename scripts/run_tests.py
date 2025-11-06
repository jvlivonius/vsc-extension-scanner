#!/usr/bin/env python3
"""
Test Suite Runner for VS Code Extension Scanner

Simplified test execution with auto-discovery and preset aliases.

Quick Start - Preset Aliases:
    python3 scripts/run_tests.py --fast      # Fast: all tests except slow (>1s)
    python3 scripts/run_tests.py --ci        # CI: all tests except real_api
    python3 scripts/run_tests.py --report    # Report: all tests with HTML coverage

Quality Modes:
    python3 scripts/run_tests.py --security-only                  # Security tests only

Advanced Usage:
    python3 scripts/run_tests.py --all
    python3 scripts/run_tests.py --unit --security
    python3 scripts/run_tests.py --all --fast
    python3 scripts/run_tests.py --all --output json --output-file results.json
    python3 scripts/run_tests.py --all --coverage --coverage-format html

Exit Codes:
    0 - All tests passed
    1 - Some tests failed
    2 - No tests found
    3 - Execution error

Note: Pre-release validation and smoke tests have been moved to dedicated scripts:
    - scripts/pre_release_check.py    # Pre-release validation
    - scripts/smoke_test.py           # Smoke test wheel packages

Version: 2.2
Updated: 2025-11-06
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
)

# ==============================================================================
# Test Group Definitions
# ==============================================================================


class TestGroup(Enum):
    """Test group categories."""

    UNIT = "unit"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    PARALLEL = "parallel"
    INTEGRATION = "integration"
    REAL_API = "real-api"
    MOCK_VALIDATION = "mock-validation"
    UNMARKED = "unmarked"  # Tests without required pytest markers
    ALL = "all"


@dataclass
class TestFile:
    """Test file metadata."""

    path: Path
    group: TestGroup
    description: str
    slow: bool = False  # Slow test marker (>1s duration, excluded by --fast)
    real_api: bool = False  # Real API tests (network-dependent)
    integration: bool = False  # Integration tests (mocked but complex)
    property_based: bool = False  # Property-based tests (hypothesis)


# Note: TestResult is now imported from lib.pytest_output_parser

# ==============================================================================
# Test File Registry
# ==============================================================================


def discover_test_files() -> Dict[TestGroup, List[TestFile]]:
    """Auto-discover test files using pytest markers.

    Returns:
        Dictionary mapping TestGroup to list of discovered TestFile objects.
        Returns empty dict if pytest is not available.
    """
    if not PYTEST_AVAILABLE:
        print(
            f"{Colors.YELLOW}Warning: pytest not available for auto-discovery.{Colors.RESET}"
        )
        return {}

    from _pytest.config import Config
    from _pytest.main import Session

    # Collect all tests
    class TestCollector:
        def __init__(self):
            self.test_files = {}
            self.file_markers = {}  # Track markers per file
            self.all_test_files = set()  # Track ALL test files

        def pytest_collection_finish(self, session):
            """Called after collection is complete."""
            # Required markers for test discovery
            required_markers = {
                "unit",
                "security",
                "architecture",
                "parallel",
                "real_api",
                "real-api",
                "mock_validation",
                "mock-validation",
                "integration",
            }

            for item in session.items:
                file_path = Path(item.fspath)
                if not file_path.exists():
                    continue

                # Track all test files
                self.all_test_files.add(file_path)

                # Get markers
                markers = {marker.name for marker in item.iter_markers()}

                # Aggregate markers per file
                if file_path not in self.file_markers:
                    self.file_markers[file_path] = set()
                self.file_markers[file_path].update(markers)

                # Map markers to test groups (prioritize specific markers over general ones)
                test_group = None
                if "unit" in markers:
                    test_group = TestGroup.UNIT
                elif "security" in markers:
                    test_group = TestGroup.SECURITY
                elif "architecture" in markers:
                    test_group = TestGroup.ARCHITECTURE
                elif "parallel" in markers:
                    test_group = TestGroup.PARALLEL
                elif "real_api" in markers or "real-api" in markers:
                    test_group = TestGroup.REAL_API
                elif "mock_validation" in markers or "mock-validation" in markers:
                    test_group = TestGroup.MOCK_VALIDATION
                elif "integration" in markers:
                    test_group = TestGroup.INTEGRATION

                if test_group:
                    if test_group not in self.test_files:
                        self.test_files[test_group] = set()
                    self.test_files[test_group].add(file_path)

    collector = TestCollector()
    # Suppress pytest output during collection (capture stdout/stderr)
    import io

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        pytest.main(["--collect-only", "-qq", "tests/"], plugins=[collector])
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    # Convert to TestFile objects with relative paths (matching TEST_REGISTRY format)
    project_root = Path.cwd()
    result = {}
    for group, file_paths in collector.test_files.items():
        test_files = []
        for file_path in sorted(file_paths):
            relative_path = (
                file_path.relative_to(project_root)
                if file_path.is_absolute()
                else file_path
            )
            filename = file_path.name.lower()

            # Get markers for this file
            file_markers = collector.file_markers.get(file_path, set())

            # Detect test characteristics based on markers, filename, and group
            is_real_api = (
                "real_api" in filename
                or group == TestGroup.REAL_API
                or "real_api" in file_markers
            )
            is_integration = (
                "integration" in filename
                or group == TestGroup.INTEGRATION
                or "integration" in file_markers
            )
            is_property = (
                "property" in filename or "property_based" in file_markers
            )  # Property-based tests
            is_slow = "slow" in file_markers  # Slow tests (>5s duration)

            test_files.append(
                TestFile(
                    path=relative_path,
                    group=group,
                    description=f"Auto-discovered from markers",
                    slow=is_slow,
                    real_api=is_real_api,
                    integration=is_integration,
                    property_based=is_property,
                )
            )
        result[group] = test_files

    # Find unmarked tests (files not in any group)
    marked_files = set()
    for files in result.values():
        marked_files.update(
            f.path if isinstance(f, TestFile) else Path(f) for f in files
        )

    unmarked_files = []
    for file_path in sorted(collector.all_test_files):
        relative_path = (
            file_path.relative_to(project_root)
            if file_path.is_absolute()
            else file_path
        )

        # Check if this file is not in any marked group
        if not any(
            relative_path == (f.path if isinstance(f, TestFile) else Path(f))
            for f in marked_files
        ):
            # Get markers for this file
            file_markers = collector.file_markers.get(file_path, set())
            filename = file_path.name.lower()

            # Check if file truly has no required markers
            required_markers_check = {
                "unit",
                "security",
                "architecture",
                "parallel",
                "real_api",
                "real-api",
                "mock_validation",
                "mock-validation",
                "integration",
            }
            if not file_markers & required_markers_check:
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

    return result


# Auto-discover test files from pytest markers (replaces manual TEST_REGISTRY)
_test_registry_cache: Optional[Dict[TestGroup, List[TestFile]]] = None


def _load_or_discover_registry() -> Dict[TestGroup, List[TestFile]]:
    """
    Load test registry using auto-discovery.

    Results are cached to avoid repeated pytest collection overhead.
    Auto-validates on first load and warns about discrepancies.
    """
    global _test_registry_cache  # pylint: disable=global-statement

    if _test_registry_cache is not None:
        return _test_registry_cache

    # Discover tests using pytest markers
    discovered = discover_test_files()

    if not discovered:
        print(
            f"{Colors.YELLOW}Warning: No tests discovered via pytest markers.{Colors.RESET}"
        )
        return {}

    _test_registry_cache = discovered
    return discovered


# Load registry on module import (cached for performance)
# Skip discovery if just showing help to avoid unnecessary pytest collection
if "--help" not in sys.argv and "-h" not in sys.argv:
    TEST_REGISTRY = _load_or_discover_registry()
else:
    TEST_REGISTRY = {}  # Empty registry for help display


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
            all_test_files = TEST_REGISTRY.get(group, [])

            # Filter based on fast flag (skip slow tests)
            if self.fast:
                test_files = [tf for tf in all_test_files if not tf.slow]
            else:
                test_files = all_test_files

            if test_files:
                discovered[group] = test_files

        return discovered

    def run_groups(self, groups: List[TestGroup]) -> int:
        """
        Run test groups and return exit code.

        Args:
            groups: List of test groups to run

        Returns:
            Exit code (0=success, 1=failures, 2=no tests, 3=error)
        """
        # Expand ALL to all groups (including UNMARKED)
        if TestGroup.ALL in groups:
            groups = [g for g in TestGroup if g != TestGroup.ALL]

        # Separate UNMARKED group to run it last
        has_unmarked = TestGroup.UNMARKED in groups
        if has_unmarked:
            groups = [g for g in groups if g != TestGroup.UNMARKED]

        # Print header
        group_names = [g.value for g in groups]
        if has_unmarked:
            group_names.append(TestGroup.UNMARKED.value)
        self.formatter.print_header(group_names, self.fast)

        # Discover tests
        all_groups_to_discover = groups + ([TestGroup.UNMARKED] if has_unmarked else [])
        discovered = self.discover_tests(all_groups_to_discover)

        if not discovered:
            print(f"{Colors.RED}Error: No test files discovered{Colors.RESET}")
            return EXIT_NOT_FOUND

        # Run each group (UNMARKED will be added at the end)
        append_coverage = False
        for group in groups:
            test_files = discovered.get(group, [])
            if not test_files:
                continue

            # Calculate skipped count for fast mode
            if self.fast:
                all_test_files = TEST_REGISTRY.get(group, [])
                skipped_count = len(all_test_files) - len(test_files)
            else:
                skipped_count = 0

            # Print group header
            self.formatter.print_group_header(
                group.value, len(test_files), skipped_count
            )

            # Build pytest command - use test file paths
            test_paths = [tf.path for tf in test_files]

            # Build markers list
            markers = [group.value.replace("-", "_")]  # Convert group name to marker
            if self.fast:
                markers.append("not slow")

            verbosity = "verbose" if self.args.verbose else "normal"
            extra_args = []
            if self.args.verbose:
                extra_args.append("-vv")

            command = self.executor.build_command(
                test_paths=test_paths,
                markers=markers,
                verbosity=verbosity,
                extra_args=extra_args,
            )

            # Wrap with coverage if enabled
            if self.coverage.enabled:
                command = self.coverage.wrap_command(command, append=append_coverage)
                append_coverage = True

            # Execute tests
            start_time = time.time()
            process = self.executor.run(command, capture_output=True)
            end_time = time.time()

            # Parse results
            result = self.parser.parse_results(
                output=process.stdout,
                stderr=process.stderr,
                returncode=process.returncode,
                file_name=f"{group.value} ({len(test_files)} files)",
                start_time=start_time,
                end_time=end_time,
            )

            # Store and print result
            self.results.append(result)
            self.formatter.print_result(result)

            # Print group summary
            self.formatter.print_group_summary([result])

        # Run UNMARKED tests last (if present)
        if has_unmarked and TestGroup.UNMARKED in discovered:
            unmarked_files = discovered[TestGroup.UNMARKED]

            # Print warning about unmarked tests
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

            # Calculate skipped count for fast mode
            if self.fast:
                all_test_files = TEST_REGISTRY.get(TestGroup.UNMARKED, [])
                skipped_count = len(all_test_files) - len(unmarked_files)
            else:
                skipped_count = 0

            # Print group header
            self.formatter.print_group_header(
                TestGroup.UNMARKED.value, len(unmarked_files), skipped_count
            )

            # Build pytest command - use test file paths
            test_paths = [tf.path for tf in unmarked_files]

            # For unmarked tests, don't filter by marker - just run the files directly
            verbosity = "verbose" if self.args.verbose else "normal"
            extra_args = []
            if self.args.verbose:
                extra_args.append("-vv")
            if self.fast:
                extra_args.extend(["-m", "not slow"])

            command = self.executor.build_command(
                test_paths=test_paths,
                markers=[],  # No marker filtering for unmarked tests
                verbosity=verbosity,
                extra_args=extra_args,
            )

            # Wrap with coverage if enabled
            if self.coverage.enabled:
                command = self.coverage.wrap_command(command, append=append_coverage)
                append_coverage = True

            # Execute tests
            start_time = time.time()
            process = self.executor.run(command, capture_output=True)
            end_time = time.time()

            # Parse results
            result = self.parser.parse_results(
                output=process.stdout,
                stderr=process.stderr,
                returncode=process.returncode,
                file_name=f"{TestGroup.UNMARKED.value} ({len(unmarked_files)} files)",
                start_time=start_time,
                end_time=end_time,
            )

            # Store and print result
            self.results.append(result)
            self.formatter.print_result(result)

            # Print group summary
            self.formatter.print_group_summary([result])

        # Print overall summary
        end_time = time.time()
        self.formatter.print_overall_summary(self.results, self.start_time, end_time)

        # Generate coverage reports if enabled
        if self.coverage.enabled:
            self.coverage.generate_reports(show_output=True)

        # Export outputs if requested
        if hasattr(self.args, "output") and hasattr(self.args, "output_file"):
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

        # Calculate exit code
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
# Main
# ==============================================================================


def main():  # pylint: disable=too-many-return-statements
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="VS Code Extension Scanner Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Test groups
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument(
        "--architecture", action="store_true", help="Run architecture tests"
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Run parallel/threading tests"
    )
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    parser.add_argument(
        "--real-api", action="store_true", help="Run real API tests (slow)"
    )
    parser.add_argument(
        "--mock-validation",
        action="store_true",
        help="Run mock validation tests (slow)",
    )
    parser.add_argument(
        "--unmarked",
        action="store_true",
        help="Run tests without required pytest markers (included with --all)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Run all test groups (including unmarked)"
    )

    # Preset aliases for common workflows
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests (>1s duration)",
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

    args = parser.parse_args()

    # Handle special modes (security-only)
    if args.security_only:
        # Security-only mode
        args.security = True
        print(
            f"{Colors.CYAN}Running security tests only (fast validation){Colors.RESET}\n"
        )

    # Handle preset aliases
    if args.ci:
        args.unit = True
        args.security = True
        args.architecture = True
        args.parallel = True
        args.integration = True
        args.mock_validation = True
        # Note: real_api group is intentionally excluded (unreliable in CI)
        # Can be combined with --fast to also skip slow tests (>1s)
        print(
            f"{Colors.CYAN}Using --ci preset: all tests except real_api{Colors.RESET}\n"
        )

    if args.report:
        args.all = True
        args.coverage = True
        if not args.coverage_format:
            args.coverage_format = "html"
        print(
            f"{Colors.CYAN}Using --report preset: all tests with coverage HTML report{Colors.RESET}\n"
        )

    # Determine which groups to run
    groups = []
    if args.unit:
        groups.append(TestGroup.UNIT)
    if args.security:
        groups.append(TestGroup.SECURITY)
    if args.architecture:
        groups.append(TestGroup.ARCHITECTURE)
    if args.parallel:
        groups.append(TestGroup.PARALLEL)
    if args.integration:
        groups.append(TestGroup.INTEGRATION)
    if args.real_api:
        groups.append(TestGroup.REAL_API)
    if args.mock_validation:
        groups.append(TestGroup.MOCK_VALIDATION)
    if args.unmarked:
        groups.append(TestGroup.UNMARKED)
    if args.all:
        groups.append(TestGroup.ALL)

    # Default to all groups if no groups specified
    if not groups:
        groups.append(TestGroup.ALL)

    # Validate output arguments
    if args.output in ["json", "junit"] and not args.output_file:
        print(
            f"Error: --output-file required for {args.output} format", file=sys.stderr
        )
        return EXIT_ERROR

    # Create orchestrator and execute
    orchestrator = TestOrchestrator(args)
    exit_code = orchestrator.run_groups(groups)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
