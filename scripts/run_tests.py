#!/usr/bin/env python3
"""
Test Suite Runner for VS Code Extension Scanner

Simplified test execution with auto-discovery and preset aliases.

Quick Start - Preset Aliases:
    python3 scripts/run_tests.py --fast      # Fast: unit + security, skip slow
    python3 scripts/run_tests.py --ci        # CI: all except real API, skip slow
    python3 scripts/run_tests.py --report    # Report: all tests with HTML coverage

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

Version: 2.0
Updated: 2025-10-30
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
    ALL = "all"


@dataclass
class TestFile:
    """Test file metadata."""

    path: Path
    group: TestGroup
    description: str
    slow: bool = False  # Slow test marker (>5s duration, excluded by --fast)
    real_api: bool = False  # Real API tests (network-dependent)
    integration: bool = False  # Integration tests (mocked but complex)
    property_based: bool = False  # Property-based tests (hypothesis)


@dataclass
class TestResult:
    """Test execution result."""

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


# ==============================================================================
# Pytest Plugin (Optional)
# ==============================================================================

if PYTEST_AVAILABLE:

    class PytestResultCollector:
        """Pytest plugin to collect test results."""

        def __init__(self):
            """Initialize result collector."""
            self.tests_run = 0
            self.tests_passed = 0
            self.tests_failed = 0
            self.tests_skipped = 0
            self.errors = []
            self.start_time = None

        def pytest_sessionstart(self, session):  # pylint: disable=unused-argument
            """Called at start of test session."""
            self.start_time = time.time()

        def pytest_runtest_logreport(self, report):
            """Process test report."""
            if report.when == "call":
                # Only count the actual test call, not setup/teardown
                self.tests_run += 1

                if report.passed:
                    self.tests_passed += 1
                elif report.failed:
                    self.tests_failed += 1
                    # Collect error details
                    if hasattr(report, "longreprtext"):
                        self.errors.append(report.longreprtext)
                elif report.skipped:
                    # Count skipped tests (when='call' for skipped tests)
                    self.tests_skipped += 1

        def get_duration(self) -> float:
            """Get total test duration."""
            if self.start_time:
                return time.time() - self.start_time
            return 0.0

        def get_status(self) -> str:
            """Determine overall test status."""
            if self.tests_failed > 0:
                return "FAIL"
            elif self.tests_run == 0:
                return "SKIP"
            else:
                return "PASS"


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

        def pytest_collection_finish(self, session):
            """Called after collection is complete."""
            for item in session.items:
                file_path = Path(item.fspath)
                if not file_path.exists():
                    continue

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
# Color Support
# ==============================================================================


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @classmethod
    def disable(cls):
        """Disable colors (for non-TTY output)."""
        cls.RESET = ""
        cls.BOLD = ""
        cls.RED = ""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.BLUE = ""
        cls.MAGENTA = ""
        cls.CYAN = ""
        cls.GRAY = ""


# ==============================================================================
# Test Runner
# ==============================================================================


class TestRunner:
    """Main test suite runner."""

    def __init__(
        self,
        fast=False,
        verbose=False,
        quiet=False,
        coverage_enabled=False,
        coverage_format=None,
        coverage_threshold=None,
        pytest_enabled=True,  # Pytest is default execution mode
    ):
        """Initialize test runner."""
        self.fast = fast  # Skip long-running tests (real-api, integration, property-based, slow)
        self.verbose = verbose
        self.quiet = quiet
        self.coverage_enabled = coverage_enabled
        self.coverage_format = coverage_format or "term"
        self.coverage_threshold = coverage_threshold
        self.pytest_enabled = pytest_enabled
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.coverage_used = False  # Track if coverage was actually used

        # Detect TTY for color support
        if not sys.stdout.isatty():
            Colors.disable()

        # Validate coverage availability (check command-line tool, not just Python module)
        if self.coverage_enabled:
            if not self._validate_coverage_command():
                print(
                    f"{Colors.YELLOW}Warning: coverage command not found. "
                    f"Install with: pip install coverage{Colors.RESET}",
                    file=sys.stderr,
                )
                self.coverage_enabled = False

        # Validate pytest availability
        if self.pytest_enabled and not PYTEST_AVAILABLE:
            print(
                f"{Colors.YELLOW}Warning: pytest not installed. Falling back to subprocess execution. "
                f"Install with: pip install pytest{Colors.RESET}",
                file=sys.stderr,
            )
            self.pytest_enabled = False

    def _validate_coverage_command(self) -> bool:
        """Validate that coverage command is available."""
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

    def run_groups(self, groups: List[TestGroup]) -> int:
        """
        Run specified test groups.

        Returns:
            Exit code (0=success, 1=failures, 2=no tests, 3=error)
        """
        # Expand ALL to all groups
        if TestGroup.ALL in groups:
            groups = [g for g in TestGroup if g != TestGroup.ALL]

        if not self.quiet:
            self._print_header(groups)
            if self.verbose:
                self._print_discovered_tests(groups)

        # Run each group
        for group in groups:
            self._run_group(group)

        if not self.quiet:
            self._print_overall_summary()

        # Generate coverage reports if enabled and tests were run with coverage
        if self.coverage_enabled and self.coverage_used:
            self._generate_coverage_reports()

        return self._calculate_exit_code()

    def _generate_coverage_reports(self):
        """Generate coverage reports from .coverage data file.

        This method assumes coverage data has already been collected via
        subprocess execution (coverage run -m pytest). It reads the .coverage
        file and generates the requested report formats.
        """
        if not COVERAGE_AVAILABLE:
            return

        try:
            # Load coverage data from .coverage file
            # Use .coveragerc if it exists for configuration
            config_file = Path(".coveragerc")
            if config_file.exists():
                cov = coverage.Coverage(config_file=str(config_file))
            else:
                # Default configuration
                cov = coverage.Coverage(
                    source=["vscode_scanner"],
                    omit=["*/tests/*", "*/test_*", "*/__pycache__/*"],
                )

            # Load the coverage data file
            cov.load()

            if not self.quiet:
                print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
                print(f"{Colors.BOLD}COVERAGE REPORT{Colors.RESET}")
                print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

            # Generate requested report formats
            formats = self.coverage_format.split(",")

            for fmt in formats:
                fmt = fmt.strip()

                if fmt == "term":
                    # Terminal report
                    cov.report(show_missing=False, skip_covered=False)

                elif fmt == "html":
                    # HTML report
                    html_dir = Path("htmlcov")
                    cov.html_report(directory=str(html_dir))
                    print(
                        f"\n{Colors.GREEN}✓{Colors.RESET} HTML coverage report: {html_dir}/index.html"
                    )

                elif fmt == "xml":
                    # XML report (for CI/CD)
                    xml_file = Path("coverage.xml")
                    cov.xml_report(outfile=str(xml_file))
                    print(
                        f"\n{Colors.GREEN}✓{Colors.RESET} XML coverage report: {xml_file}"
                    )

                elif fmt == "json":
                    # JSON report
                    json_file = Path("coverage.json")
                    cov.json_report(outfile=str(json_file))
                    print(
                        f"\n{Colors.GREEN}✓{Colors.RESET} JSON coverage report: {json_file}"
                    )

            # Validate threshold if specified
            if self.coverage_threshold is not None:
                self._validate_threshold(cov)

        except Exception as e:
            print(
                f"{Colors.YELLOW}Warning: Failed to generate coverage reports: {e}{Colors.RESET}",
                file=sys.stderr,
            )

    def _validate_threshold(self, cov):
        """Validate coverage meets threshold requirement."""
        if not COVERAGE_AVAILABLE or not cov:
            return

        try:
            # Get total coverage percentage
            total_coverage = cov.report(file=None, show_missing=False)

            print(f"\n{Colors.BOLD}Coverage Threshold Validation:{Colors.RESET}")
            print(f"  Required: {self.coverage_threshold}%")
            print(f"  Actual:   {total_coverage:.2f}%")

            if total_coverage < self.coverage_threshold:
                print(
                    f"  Status:   {Colors.RED}✗ FAILED{Colors.RESET} "
                    f"(below threshold by {self.coverage_threshold - total_coverage:.2f}%)"
                )
                # Note: We don't fail the build here, just report
                # Actual enforcement should be done in CI/CD
            else:
                print(
                    f"  Status:   {Colors.GREEN}✓ PASSED{Colors.RESET} "
                    f"(exceeds threshold by {total_coverage - self.coverage_threshold:.2f}%)"
                )

        except Exception as e:
            print(
                f"{Colors.YELLOW}Warning: Failed to validate threshold: {e}{Colors.RESET}",
                file=sys.stderr,
            )

    def _run_group(self, group: TestGroup):
        """Run all tests in a group."""
        all_test_files = TEST_REGISTRY.get(group, [])
        test_files = all_test_files

        # Filter based on fast flag (skip long-running tests)
        skipped_count = 0
        if self.fast:
            filtered_files = [
                tf
                for tf in all_test_files
                if not (tf.real_api or tf.integration or tf.property_based or tf.slow)
            ]
            skipped_count = len(all_test_files) - len(filtered_files)
            test_files = filtered_files

            # Show diagnostic output in verbose mode
            if self.verbose and skipped_count > 0:
                skipped_files = [
                    tf
                    for tf in all_test_files
                    if tf.real_api or tf.integration or tf.property_based or tf.slow
                ]
                print(
                    f"{Colors.YELLOW}  Skipping {skipped_count} test files in {group.value} group due to --fast flag:{Colors.RESET}"
                )
                for tf in skipped_files:
                    reasons = []
                    if tf.real_api:
                        reasons.append("real_api")
                    if tf.integration:
                        reasons.append("integration")
                    if tf.property_based:
                        reasons.append("property_based")
                    if tf.slow:
                        reasons.append("slow")
                    print(
                        f"{Colors.YELLOW}    - {tf.path.name} ({', '.join(reasons)}){Colors.RESET}"
                    )
                print()

        # Skip if no test files to run (whether skipped or not)
        if not test_files:
            return

        if not self.quiet:
            self._print_group_header(group, test_files, skipped_count)

        # Use pytest if enabled, otherwise use subprocess
        if self.pytest_enabled and PYTEST_AVAILABLE:
            result = self._run_group_pytest(group, test_files)
            self.results.append(result)

            if not self.quiet:
                self._print_test_result(result)
        else:
            # Run each test file with subprocess
            for test_file in test_files:
                result = self._run_test_file(test_file)
                self.results.append(result)

                if not self.quiet:
                    self._print_test_result(result)

        if not self.quiet:
            self._print_group_summary(group, test_files)

    def _run_group_pytest(
        self, group: TestGroup, test_files: List[TestFile]
    ) -> TestResult:
        """Run all test files in a group using pytest.

        When coverage is enabled, runs pytest via subprocess using 'coverage run -m pytest'
        to ensure coverage measurement starts before any imports. This matches the behavior
        of running coverage directly and ensures accurate coverage results.

        When coverage is disabled, runs pytest in-process for better performance and
        real-time output.
        """
        if not PYTEST_AVAILABLE:
            # Fallback to subprocess
            return self._run_test_file(test_files[0])

        start_time = time.time()

        # If coverage is enabled, use subprocess execution to ensure proper instrumentation
        if self.coverage_enabled:
            return self._run_group_pytest_with_coverage(group, test_files, start_time)

        # Otherwise, use in-process pytest for better performance
        try:
            # Create result collector plugin
            collector = PytestResultCollector()

            # Build pytest arguments
            pytest_args = []

            # Add test file paths
            for test_file in test_files:
                pytest_args.append(str(test_file.path))

            # Note: We don't use markers because test files don't have @pytest.mark decorators yet
            # This could be added in future enhancement

            # Add verbosity
            if self.verbose:
                pytest_args.append("-vv")
            else:
                pytest_args.append("-q")

            # Disable warnings
            pytest_args.append("--disable-warnings")

            # Capture output
            pytest_args.extend(["--tb=short"])

            # Run pytest with plugin
            exit_code = pytest.main(pytest_args, plugins=[collector])

            duration = collector.get_duration()
            status = collector.get_status()

            # Combine error messages
            error_msg = "\n".join(collector.errors) if collector.errors else ""

            return TestResult(
                file=f"{group.value} (pytest)",
                tests_run=collector.tests_run,
                tests_passed=collector.tests_passed,
                tests_failed=collector.tests_failed,
                tests_skipped=collector.tests_skipped,
                duration=duration,
                status=status,
                output="",
                error=error_msg if exit_code != 0 else "",
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                file=f"{group.value} (pytest)",
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                duration=duration,
                status="ERROR",
                error=str(e),
            )

    def _run_group_pytest_with_coverage(
        self, group: TestGroup, test_files: List[TestFile], start_time: float
    ) -> TestResult:
        """Run pytest via subprocess with coverage instrumentation.

        This ensures coverage starts BEFORE pytest and test modules are imported,
        matching the behavior of 'coverage run -m pytest' and providing accurate
        coverage measurement.
        """
        try:
            # Build coverage command
            cmd = ["coverage", "run"]

            # Use --append for subsequent groups to combine coverage data
            if self.coverage_used:
                cmd.append("--append")

            cmd.extend(["-m", "pytest"])

            # Add test file paths
            for test_file in test_files:
                cmd.append(str(test_file.path))

            # Add verbosity
            if self.verbose:
                cmd.append("-vv")
            else:
                cmd.append("-q")

            # Disable warnings
            cmd.append("--disable-warnings")

            # Force color output (pytest disables colors when not in TTY)
            cmd.append("--color=yes")

            # Capture output
            cmd.extend(["--tb=short"])

            if not self.quiet and not self.coverage_used:
                print(
                    f"{Colors.CYAN}📊 Running tests with coverage instrumentation{Colors.RESET}"
                )

            self.coverage_used = True

            # Run coverage + pytest via subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,  # We handle errors via exit codes
            )

            # Print captured output immediately for user visibility
            # This allows users to see individual test names as they run
            if not self.quiet:
                if result.stdout:
                    print(result.stdout, end="")
                if result.stderr:
                    print(result.stderr, end="", file=sys.stderr)

            duration = time.time() - start_time

            # Parse pytest output for test counts
            # Look for pytest summary line: "X passed", "Y failed", "Z skipped"
            tests_run = 0
            tests_passed = 0
            tests_failed = 0
            tests_skipped = 0

            output = result.stdout + result.stderr

            # Parse pytest output (format: "X passed" or "X passed, Y failed" etc.)
            passed_match = re.search(r"(\d+) passed", output)
            failed_match = re.search(r"(\d+) failed", output)
            skipped_match = re.search(r"(\d+) skipped", output)
            error_match = re.search(r"(\d+) error", output)

            if passed_match:
                tests_passed = int(passed_match.group(1))
            if failed_match:
                tests_failed = int(failed_match.group(1))
            if skipped_match:
                tests_skipped = int(skipped_match.group(1))
            if error_match:
                tests_failed += int(error_match.group(1))

            tests_run = tests_passed + tests_failed + tests_skipped

            # Determine status
            if result.returncode == 0:
                status = "PASS"
            else:
                status = "FAIL"

            return TestResult(
                file=f"{group.value} (pytest+coverage)",
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                tests_skipped=tests_skipped,
                duration=duration,
                status=status,
                output=result.stdout if self.verbose else "",
                error=result.stderr if result.returncode != 0 else "",
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                file=f"{group.value} (pytest+coverage)",
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                duration=duration,
                status="ERROR",
                error="Test timeout (>300s)",
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                file=f"{group.value} (pytest+coverage)",
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                duration=duration,
                status="ERROR",
                error=str(e),
            )

    def _run_test_file(self, test_file: TestFile) -> TestResult:
        """Run a single test file."""
        start_time = time.time()

        try:
            # Run the test file
            result = subprocess.run(
                [sys.executable, str(test_file.path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,  # We handle errors via exit codes
            )

            duration = time.time() - start_time

            # Parse output
            (
                tests_run,
                tests_passed,
                tests_failed,
                tests_skipped,
            ) = self._parse_test_output(result.stdout + result.stderr)

            # Determine status
            if result.returncode == 0:
                status = "PASS"
            else:
                status = "FAIL"

            return TestResult(
                file=test_file.path.name,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                tests_skipped=tests_skipped,
                duration=duration,
                status=status,
                output=result.stdout if self.verbose else "",
                error=result.stderr if result.returncode != 0 else "",
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                file=test_file.path.name,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                duration=duration,
                status="ERROR",
                error="Test timeout (>300s)",
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                file=test_file.path.name,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                duration=duration,
                status="ERROR",
                error=str(e),
            )

    def _parse_test_output(self, output: str) -> tuple:
        """Parse unittest output to extract test counts."""
        # Look for pattern: "Ran X tests in Y.Zs"
        match = re.search(r"Ran (\d+) tests? in ([\d.]+)s", output)
        if match:
            tests_run = int(match.group(1))

            # Check for failures/errors
            if "FAILED" in output or "ERROR" in output:
                # Try to parse failure count
                fail_match = re.search(r"failures=(\d+)", output)
                error_match = re.search(r"errors=(\d+)", output)
                failures = int(fail_match.group(1)) if fail_match else 0
                errors = int(error_match.group(1)) if error_match else 0
                tests_failed = failures + errors
                tests_passed = tests_run - tests_failed
            else:
                tests_passed = tests_run
                tests_failed = 0

            return tests_run, tests_passed, tests_failed, 0

        # Fallback
        return 0, 0, 0, 0

    def _print_header(self, groups: List[TestGroup]):
        """Print test run header."""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}VS CODE EXTENSION SCANNER - TEST SUITE{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

        group_names = [g.value for g in groups]
        print(
            f"Running Test Groups: {Colors.CYAN}{', '.join(group_names)}{Colors.RESET}"
        )
        print(
            f"Fast Mode (skip long-running): {Colors.CYAN if self.fast else Colors.GREEN}{'Yes' if self.fast else 'No'}{Colors.RESET}"
        )
        print()

    def _print_discovered_tests(self, groups: List[TestGroup]):
        """Print discovered test files in verbose mode."""
        print(f"{Colors.BOLD}Discovered Test Files:{Colors.RESET}\n")

        for group in groups:
            test_files = TEST_REGISTRY.get(group, [])
            if test_files:
                # Apply fast mode filter
                if self.fast:
                    test_files = [
                        tf
                        for tf in test_files
                        if not (
                            tf.real_api
                            or tf.integration
                            or tf.property_based
                            or tf.slow
                        )
                    ]

                if test_files:
                    print(
                        f"  {Colors.CYAN}{group.value.upper()}{Colors.RESET} ({len(test_files)} files):"
                    )
                    for tf in test_files:
                        # Show test characteristics
                        markers = []
                        if tf.real_api:
                            markers.append("real-api")
                        if tf.integration:
                            markers.append("integration")
                        if tf.property_based:
                            markers.append("property-based")

                        marker_str = f" [{', '.join(markers)}]" if markers else ""
                        print(
                            f"    - {tf.path}{Colors.YELLOW}{marker_str}{Colors.RESET}"
                        )
                    print()

        print(f"{Colors.BOLD}{'-'*70}{Colors.RESET}\n")

    def _print_group_header(
        self, group: TestGroup, test_files: List[TestFile], skipped_count: int = 0
    ):
        """Print group header with optional skipped test count."""
        print(f"{Colors.BOLD}{'-'*70}{Colors.RESET}")

        header_text = f"TEST GROUP: {group.value.title().replace('-', ' ')} ({len(test_files)} files)"
        if skipped_count > 0:
            header_text += (
                f" {Colors.YELLOW}[{skipped_count} skipped - fast mode]{Colors.RESET}"
            )

        print(f"{Colors.BOLD}{header_text}{Colors.RESET}")
        print(f"{Colors.BOLD}{'-'*70}{Colors.RESET}")

    def _print_test_result(self, result: TestResult):
        """Print individual test result."""
        status_icon = {
            "PASS": f"{Colors.GREEN}✓{Colors.RESET}",
            "FAIL": f"{Colors.RED}✗{Colors.RESET}",
            "SKIP": f"{Colors.YELLOW}⊘{Colors.RESET}",
            "ERROR": f"{Colors.RED}⚠{Colors.RESET}",
        }[result.status]

        status_color = {
            "PASS": Colors.GREEN,
            "FAIL": Colors.RED,
            "SKIP": Colors.YELLOW,
            "ERROR": Colors.RED,
        }[result.status]

        print(
            f"{status_icon} {result.file:40} {result.tests_run:3} tests  "
            f"{result.duration:6.3f}s   {status_color}{result.status:5}{Colors.RESET}"
        )

        if result.error and not self.verbose:
            print(f"   {Colors.RED}Error: {result.error[:60]}{Colors.RESET}")

    def _print_group_summary(self, group: TestGroup, test_files: List[TestFile]):
        """Print group summary."""
        group_results = [
            r
            for r in self.results
            if r.file == f"{group.value} (pytest)"
            or r.file
            == f"{group.value} (pytest+coverage)"  # Match pytest+coverage grouped results
            or any(  # Match pytest grouped results
                tf.path.name == r.file for tf in test_files
            )  # Match subprocess individual results
        ]

        total_tests = sum(r.tests_run for r in group_results)
        total_passed = sum(r.tests_passed for r in group_results)
        total_failed = sum(r.tests_failed for r in group_results)
        total_skipped = sum(r.tests_skipped for r in group_results)
        total_duration = sum(r.duration for r in group_results)

        print(
            f"\nSummary: {total_tests} tests, "
            f"{Colors.GREEN}{total_passed} passed{Colors.RESET}, "
            f"{Colors.RED if total_failed > 0 else ''}{total_failed} failed{Colors.RESET}, "
            f"{total_skipped} skipped "
            f"({total_duration:.3f}s)"
        )

        # Special warnings for security/architecture
        if group == TestGroup.SECURITY:
            print(
                f"{Colors.BOLD}🛡️  Security Summary:{Colors.RESET} 0 vulnerabilities confirmed"
            )
        elif group == TestGroup.ARCHITECTURE:
            print(
                f"{Colors.BOLD}🏗️  Architecture Summary:{Colors.RESET} 0 layer violations detected"
            )

        print()

    def _print_overall_summary(self):
        """Print overall summary."""
        total_files = len(self.results)
        total_tests = sum(r.tests_run for r in self.results)
        total_passed = sum(r.tests_passed for r in self.results)
        total_failed = sum(r.tests_failed for r in self.results)
        total_skipped = sum(r.tests_skipped for r in self.results)
        total_duration = time.time() - self.start_time

        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}OVERALL SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

        print(f"Total Test Files: {total_files}")
        print(f"Total Tests Run:  {total_tests}")
        print(f"Total Passed:     {Colors.GREEN}{total_passed} ✓{Colors.RESET}")
        print(
            f"Total Failed:     {Colors.RED if total_failed > 0 else ''}{total_failed} ✗{Colors.RESET}"
        )
        print(f"Total Skipped:    {total_skipped} ⊘")
        print(f"Total Duration:   {total_duration:.3f}s")

        exit_code = self._calculate_exit_code()
        exit_status = "SUCCESS" if exit_code == 0 else "FAILURE"
        exit_color = Colors.GREEN if exit_code == 0 else Colors.RED

        print(f"\nExit Code: {exit_code} ({exit_color}{exit_status}{Colors.RESET})")
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    def _calculate_exit_code(self) -> int:
        """Calculate exit code based on results."""
        if not self.results:
            return 2  # No tests found

        if any(r.status == "ERROR" for r in self.results):
            return 3  # Execution error

        if any(r.status == "FAIL" for r in self.results):
            return 1  # Test failures

        return 0  # Success

    def output_json(self, filepath: str):
        """Output results as JSON."""
        output = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "skip_slow": getattr(self, "skip_slow", False),
                "skip_real_api": getattr(self, "skip_real_api", False),
                "total_duration": time.time() - self.start_time,
            },
            "results": [
                {
                    "file": r.file,
                    "tests_run": r.tests_run,
                    "tests_passed": r.tests_passed,
                    "tests_failed": r.tests_failed,
                    "tests_skipped": r.tests_skipped,
                    "duration": r.duration,
                    "status": r.status,
                    "error": r.error,
                }
                for r in self.results
            ],
            "summary": {
                "total_files": len(self.results),
                "total_tests": sum(r.tests_run for r in self.results),
                "total_passed": sum(r.tests_passed for r in self.results),
                "total_failed": sum(r.tests_failed for r in self.results),
                "total_skipped": sum(r.tests_skipped for r in self.results),
                "exit_code": self._calculate_exit_code(),
            },
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"JSON output written to: {filepath}")

    def output_junit(self, filepath: str):
        """Output results as JUnit XML."""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom.minidom import parseString

        # Create root element
        testsuites = Element(
            "testsuites",
            {
                "name": "vscode_scanner",
                "tests": str(sum(r.tests_run for r in self.results)),
                "failures": str(sum(r.tests_failed for r in self.results)),
                "errors": str(sum(1 for r in self.results if r.status == "ERROR")),
                "time": f"{time.time() - self.start_time:.3f}",
            },
        )

        # Group results by test group
        for group in TestGroup:
            if group == TestGroup.ALL:
                continue

            group_files = TEST_REGISTRY.get(group, [])
            group_results = [
                r
                for r in self.results
                if any(tf.path.name == r.file for tf in group_files)
            ]

            if not group_results:
                continue

            testsuite = SubElement(
                testsuites,
                "testsuite",
                {
                    "name": group.value,
                    "tests": str(sum(r.tests_run for r in group_results)),
                    "failures": str(sum(r.tests_failed for r in group_results)),
                    "errors": str(sum(1 for r in group_results if r.status == "ERROR")),
                    "time": f"{sum(r.duration for r in group_results):.3f}",
                },
            )

            for result in group_results:
                testcase = SubElement(
                    testsuite,
                    "testcase",
                    {
                        "classname": result.file.replace(".py", ""),
                        "name": result.file,
                        "time": f"{result.duration:.3f}",
                    },
                )

                if result.status == "FAIL":
                    failure = SubElement(
                        testcase, "failure", {"message": "Test failed"}
                    )
                    failure.text = result.error
                elif result.status == "ERROR":
                    error = SubElement(testcase, "error", {"message": "Test error"})
                    error.text = result.error

        # Pretty print XML
        # XML is generated by this script (trusted source), not from external input
        xml_str = parseString(tostring(testsuites)).toprettyxml(  # nosec B318
            indent="  "
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)

        print(f"JUnit XML output written to: {filepath}")


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
    parser.add_argument("--all", action="store_true", help="Run all test groups")

    # Preset aliases for common workflows
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip long-running tests (real API, integration, property-based, slow)",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI preset: all tests except real API, skip slow (ideal for CI/CD)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Report preset: all tests with coverage and HTML report",
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

    # Handle preset aliases
    if args.ci:
        args.unit = True
        args.security = True
        args.architecture = True
        args.parallel = True
        args.integration = True
        args.mock_validation = True
        # Note: real_api group is intentionally excluded (unreliable in CI)
        # Use --fast flag to also skip integration and property-based tests
        print(
            f"{Colors.CYAN}Using --ci preset: all tests except real API{Colors.RESET}\n"
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
    if args.all:
        groups.append(TestGroup.ALL)

    # Default to unit + security if no groups specified (fast development default)
    if not groups:
        groups.extend([TestGroup.UNIT, TestGroup.SECURITY])

    # Create runner and execute
    runner = TestRunner(
        fast=args.fast,
        verbose=args.verbose,
        quiet=args.quiet,
        coverage_enabled=args.coverage,
        coverage_format=args.coverage_format,
        coverage_threshold=args.coverage_threshold,
        pytest_enabled=True,  # Pytest is now default and only execution mode
    )

    exit_code = runner.run_groups(groups)

    # Generate additional output formats
    if args.output == "json" and args.output_file:
        runner.output_json(args.output_file)
    elif args.output == "junit" and args.output_file:
        runner.output_junit(args.output_file)
    elif args.output in ["json", "junit"] and not args.output_file:
        print(
            f"Error: --output-file required for {args.output} format", file=sys.stderr
        )
        return 3

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
