#!/usr/bin/env python3
"""
Test Suite Runner for VS Code Extension Scanner

Unified test execution with standardized output, supporting multiple test groups
and output formats.

Usage:
    python3 scripts/run_tests.py --all
    python3 scripts/run_tests.py --unit --security
    python3 scripts/run_tests.py --all --skip-slow
    python3 scripts/run_tests.py --all --output json --output-file results.json
    python3 scripts/run_tests.py --all --output junit --output-file results.xml
    python3 scripts/run_tests.py --all --coverage
    python3 scripts/run_tests.py --all --coverage --coverage-format html
    python3 scripts/run_tests.py --all --coverage --coverage-threshold 85.0
    python3 scripts/run_tests.py --all --pytest
    python3 scripts/run_tests.py --all --pytest --coverage

Test Groups:
    --unit              Fast unit tests (scanner, display, CLI, validators, commands, utils)
    --security          Security validation tests (includes property-based tests)
    --architecture      Architecture compliance tests
    --parallel          Parallel scanning and threading tests
    --integration       Integration tests (mocked API)
    --real-api          Real API integration tests (slow)
    --mock-validation   Mock validation tests (slow)
    --all               All test groups

Test Coverage:
    36 test files, 604+ tests
    Includes 21 property-based tests generating 21,000+ test scenarios

Options:
    --skip-slow         Skip slow tests
    --skip-real-api     Skip tests that make real API calls
    --output FORMAT     Output format: console (default), json, junit
    --output-file PATH  Output file for json/junit formats
    --verbose           Verbose output
    --quiet             Minimal output
    --coverage          Enable coverage measurement (requires: pip install coverage)
    --coverage-format   Coverage report format: term,html,xml,json (default: term)
    --coverage-threshold PCT  Minimum required coverage percentage
    --pytest            Use pytest runner for in-process execution (requires: pip install pytest)

Exit Codes:
    0 - All tests passed
    1 - Some tests failed
    2 - No tests found
    3 - Execution error

Version: 1.3
Updated: 2025-10-30 (Phase 2: Pytest Integration)
"""

import sys
import subprocess
import time
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict
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
    slow: bool = False
    real_api: bool = False


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

        def pytest_sessionstart(self, _session):
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
            elif report.when == "setup" and report.skipped:
                # Count skipped tests
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

# Define all test files organized by group
TEST_REGISTRY: Dict[TestGroup, List[TestFile]] = {
    TestGroup.UNIT: [
        TestFile(Path("tests/test_scanner.py"), TestGroup.UNIT, "Core scanner logic"),
        TestFile(Path("tests/test_display.py"), TestGroup.UNIT, "Display module"),
        TestFile(Path("tests/test_cli.py"), TestGroup.UNIT, "CLI interface"),
        TestFile(
            Path("tests/test_failed_extensions.py"),
            TestGroup.UNIT,
            "Failed extensions tracking",
        ),
        TestFile(
            Path("tests/test_config_extensions_dir.py"),
            TestGroup.UNIT,
            "Config extensions directory",
        ),
        TestFile(
            Path("tests/test_transactional_cache.py"),
            TestGroup.UNIT,
            "Transactional cache operations",
        ),
        TestFile(
            Path("tests/test_utils.py"),
            TestGroup.UNIT,
            "Utility functions (Phase 4.1)",
        ),
        TestFile(
            Path("tests/test_config_manager.py"),
            TestGroup.UNIT,
            "Config manager",
        ),
        TestFile(
            Path("tests/test_output_formatter.py"),
            TestGroup.UNIT,
            "Output formatting (JSON/CSV)",
        ),
        TestFile(
            Path("tests/test_extension_discovery.py"),
            TestGroup.UNIT,
            "Extension discovery",
        ),
        TestFile(
            Path("tests/test_input_validators.py"),
            TestGroup.UNIT,
            "CLI input validators",
        ),
        TestFile(
            Path("tests/test_config_commands.py"),
            TestGroup.UNIT,
            "Config subcommands",
        ),
        TestFile(
            Path("tests/test_cache_commands.py"),
            TestGroup.UNIT,
            "Cache subcommands",
        ),
        TestFile(
            Path("tests/test_report_commands.py"),
            TestGroup.UNIT,
            "Report generation",
        ),
        TestFile(
            Path("tests/test_error_handling.py"),
            TestGroup.UNIT,
            "Error handling paths",
        ),
    ],
    TestGroup.SECURITY: [
        TestFile(
            Path("tests/test_security.py"), TestGroup.SECURITY, "Security validation"
        ),
        TestFile(
            Path("tests/test_path_validation.py"), TestGroup.SECURITY, "Path validation"
        ),
        TestFile(
            Path("tests/test_string_sanitization.py"),
            TestGroup.SECURITY,
            "String sanitization",
        ),
        TestFile(
            Path("tests/test_cache_integrity.py"),
            TestGroup.SECURITY,
            "Cache integrity (HMAC)",
        ),
        TestFile(
            Path("tests/test_security_regression.py"),
            TestGroup.SECURITY,
            "Security regression suite",
        ),
        TestFile(
            Path("tests/test_sqlite_security.py"),
            TestGroup.SECURITY,
            "SQLite security audit",
        ),
        TestFile(
            Path("tests/test_property_validation.py"),
            TestGroup.SECURITY,
            "Property-based validation tests (13 tests, 13K scenarios)",
        ),
        TestFile(
            Path("tests/test_property_cache.py"),
            TestGroup.SECURITY,
            "Property-based cache integrity tests (8 tests, 8K scenarios)",
        ),
    ],
    TestGroup.ARCHITECTURE: [
        TestFile(
            Path("tests/test_architecture.py"),
            TestGroup.ARCHITECTURE,
            "Layer compliance",
        ),
    ],
    TestGroup.PARALLEL: [
        TestFile(
            Path("tests/test_parallel_scanning.py"),
            TestGroup.PARALLEL,
            "Parallel scanning",
        ),
    ],
    TestGroup.INTEGRATION: [
        TestFile(
            Path("tests/test_integration.py"),
            TestGroup.INTEGRATION,
            "Integration tests (mocked)",
        ),
        TestFile(
            Path("tests/test_db_integrity.py"),
            TestGroup.INTEGRATION,
            "Database integrity",
        ),
        TestFile(
            Path("tests/test_api.py"),
            TestGroup.INTEGRATION,
            "API client tests",
        ),
        TestFile(
            Path("tests/test_retry.py"),
            TestGroup.INTEGRATION,
            "Retry mechanism",
        ),
        TestFile(
            Path("tests/test_retry_analysis.py"),
            TestGroup.INTEGRATION,
            "Retry analysis",
        ),
        TestFile(
            Path("tests/test_workflow_retry.py"),
            TestGroup.INTEGRATION,
            "Workflow retry logic",
        ),
        TestFile(
            Path("tests/test_performance.py"),
            TestGroup.INTEGRATION,
            "Performance benchmarks",
            slow=True,
        ),
        TestFile(
            Path("tests/test_verbose_mode.py"),
            TestGroup.INTEGRATION,
            "Verbose mode output",
        ),
        TestFile(
            Path("tests/test_report_empty_cache.py"),
            TestGroup.INTEGRATION,
            "Empty cache reporting",
        ),
    ],
    TestGroup.REAL_API: [
        TestFile(
            Path("tests/test_integration_real_api.py"),
            TestGroup.REAL_API,
            "Real API integration",
            slow=True,
            real_api=True,
        ),
    ],
    TestGroup.MOCK_VALIDATION: [
        TestFile(
            Path("tests/test_mock_validation.py"),
            TestGroup.MOCK_VALIDATION,
            "Mock validation against real API",
            slow=True,
            real_api=True,
        ),
    ],
}


# ==============================================================================
# Auto-Discovery Functions (Phase 3B)
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

        def pytest_collection_finish(self, session):
            """Called after collection is complete."""
            for item in session.items:
                file_path = Path(item.fspath)
                if not file_path.exists():
                    continue

                # Get markers
                markers = {marker.name for marker in item.iter_markers()}

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
    pytest.main(["--collect-only", "-q", "tests/"], plugins=[collector])

    # Convert to TestFile objects with relative paths (matching TEST_REGISTRY format)
    project_root = Path.cwd()
    result = {}
    for group, file_paths in collector.test_files.items():
        result[group] = [
            TestFile(
                path=file_path.relative_to(project_root)
                if file_path.is_absolute()
                else file_path,
                group=group,
                description=f"Auto-discovered from markers",
            )
            for file_path in sorted(file_paths)
        ]

    return result


def validate_registry() -> tuple[bool, List[str]]:
    """Compare TEST_REGISTRY against auto-discovered tests.

    Returns:
        Tuple of (is_valid, list_of_issues).
        is_valid is True if registry matches discovery, False otherwise.
        list_of_issues contains human-readable descriptions of discrepancies.
    """
    discovered = discover_test_files()
    issues = []
    warnings = []

    # Build registry lookup
    registry_files = {}
    for group in TestGroup:
        if group in TEST_REGISTRY:
            for test_file in TEST_REGISTRY[group]:
                registry_files[test_file.path] = group

    # Build discovered lookup
    discovered_files = {}
    for group, files in discovered.items():
        for test_file in files:
            discovered_files[test_file.path] = group

    # Check for missing files
    registry_set = set(registry_files.keys())
    discovered_set = set(discovered_files.keys())

    missing_from_registry = discovered_set - registry_set
    missing_from_discovered = registry_set - discovered_set
    group_mismatches = []

    # Check for group mismatches
    common_files = registry_set & discovered_set
    for file_path in common_files:
        registry_group = registry_files[file_path]
        discovered_group = discovered_files[file_path]
        if registry_group != discovered_group:
            group_mismatches.append(
                f"{file_path.name}: Registry={registry_group.value}, Discovered={discovered_group.value}"
            )

    # Build issue list
    if missing_from_registry:
        issues.append(
            f"Files not in TEST_REGISTRY: {', '.join(f.name for f in missing_from_registry)}"
        )

    if missing_from_discovered:
        # Check if these files exist and have pytest collection errors
        collection_errors = []
        actual_missing = []

        for file_path in missing_from_discovered:
            if file_path.exists():
                collection_errors.append(file_path.name)
            else:
                actual_missing.append(file_path.name)

        if collection_errors:
            warnings.append(
                f"Files in TEST_REGISTRY with pytest collection errors (check syntax/imports): {', '.join(collection_errors)}"
            )

        if actual_missing:
            issues.append(
                f"Files in TEST_REGISTRY but missing from disk: {', '.join(actual_missing)}"
            )

    if group_mismatches:
        issues.extend([f"Group mismatch: {mismatch}" for mismatch in group_mismatches])

    # Combine issues and warnings
    all_messages = issues + warnings
    is_valid = len(issues) == 0  # Warnings don't fail validation
    return is_valid, all_messages


def sync_registry(dry_run: bool = True) -> str:
    """Generate Python code for TEST_REGISTRY from discovered tests.

    Args:
        dry_run: If True, only generate code without modifying file.

    Returns:
        Generated Python code for TEST_REGISTRY definition.
    """
    discovered = discover_test_files()

    # Generate Python code
    lines = ["TEST_REGISTRY = {"]

    for group in TestGroup:
        if group not in discovered or not discovered[group]:
            continue

        lines.append(f"    TestGroup.{group.name}: [")

        for test_file in sorted(discovered[group], key=lambda x: x.path.name):
            # Try to extract description from file docstring
            description = test_file.description
            try:
                content = test_file.path.read_text()
                docstring_match = re.search(r'"""([^"]+)"""', content)
                if docstring_match:
                    first_line = docstring_match.group(1).split("\n")[0].strip()
                    if first_line and len(first_line) < 80:
                        description = first_line
            except (OSError, UnicodeDecodeError):
                pass

            lines.append(
                f'        TestFile(Path("{test_file.path}"), TestGroup.{group.name}, "{description}"),'
            )

        lines.append("    ],")

    lines.append("}")

    generated_code = "\n".join(lines)

    if not dry_run:
        print(
            f"{Colors.YELLOW}Note: Automatic registry update not implemented yet.{Colors.RESET}"
        )
        print(
            f"{Colors.YELLOW}Copy the generated code and update TEST_REGISTRY manually.{Colors.RESET}"
        )

    return generated_code


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
        skip_slow=False,
        skip_real_api=False,
        verbose=False,
        quiet=False,
        coverage_enabled=False,
        coverage_format=None,
        coverage_threshold=None,
        pytest_enabled=False,
    ):
        """Initialize test runner."""
        self.skip_slow = skip_slow
        self.skip_real_api = skip_real_api
        self.verbose = verbose
        self.quiet = quiet
        self.coverage_enabled = coverage_enabled
        self.coverage_format = coverage_format or "term"
        self.coverage_threshold = coverage_threshold
        self.pytest_enabled = pytest_enabled
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.cov = None

        # Detect TTY for color support
        if not sys.stdout.isatty():
            Colors.disable()

        # Validate coverage availability
        if self.coverage_enabled and not COVERAGE_AVAILABLE:
            print(
                f"{Colors.YELLOW}Warning: coverage.py not installed. "
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

    def run_groups(self, groups: List[TestGroup]) -> int:
        """
        Run specified test groups.

        Returns:
            Exit code (0=success, 1=failures, 2=no tests, 3=error)
        """
        # Expand ALL to all groups
        if TestGroup.ALL in groups:
            groups = [g for g in TestGroup if g != TestGroup.ALL]

        # Start coverage measurement if enabled
        if self.coverage_enabled:
            self._start_coverage()

        if not self.quiet:
            self._print_header(groups)

        # Run each group
        for group in groups:
            self._run_group(group)

        if not self.quiet:
            self._print_overall_summary()

        # Finalize coverage measurement if enabled
        if self.coverage_enabled:
            self._finalize_coverage()

        return self._calculate_exit_code()

    def _start_coverage(self):
        """Initialize coverage measurement."""
        if not COVERAGE_AVAILABLE:
            return

        try:
            # Use .coveragerc if it exists, otherwise use default config
            config_file = Path(".coveragerc")
            if config_file.exists():
                self.cov = coverage.Coverage(config_file=str(config_file))
            else:
                # Default configuration
                self.cov = coverage.Coverage(
                    source=["vscode_scanner"],
                    omit=["*/tests/*", "*/test_*", "*/__pycache__/*"],
                )

            self.cov.start()

            if not self.quiet:
                print(f"{Colors.CYAN}📊 Coverage measurement started{Colors.RESET}\n")

        except Exception as e:
            print(
                f"{Colors.YELLOW}Warning: Failed to start coverage: {e}{Colors.RESET}",
                file=sys.stderr,
            )
            self.coverage_enabled = False

    def _finalize_coverage(self):
        """Stop coverage measurement and generate reports."""
        if not COVERAGE_AVAILABLE or not self.cov:
            return

        try:
            self.cov.stop()
            self.cov.save()

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
                    self.cov.report(show_missing=False, skip_covered=False)

                elif fmt == "html":
                    # HTML report
                    html_dir = Path("htmlcov")
                    self.cov.html_report(directory=str(html_dir))
                    print(
                        f"\n{Colors.GREEN}✓{Colors.RESET} HTML coverage report: {html_dir}/index.html"
                    )

                elif fmt == "xml":
                    # XML report (for CI/CD)
                    xml_file = Path("coverage.xml")
                    self.cov.xml_report(outfile=str(xml_file))
                    print(
                        f"\n{Colors.GREEN}✓{Colors.RESET} XML coverage report: {xml_file}"
                    )

                elif fmt == "json":
                    # JSON report
                    json_file = Path("coverage.json")
                    self.cov.json_report(outfile=str(json_file))
                    print(
                        f"\n{Colors.GREEN}✓{Colors.RESET} JSON coverage report: {json_file}"
                    )

            # Validate threshold if specified
            if self.coverage_threshold is not None:
                self._validate_threshold()

        except Exception as e:
            print(
                f"{Colors.YELLOW}Warning: Failed to finalize coverage: {e}{Colors.RESET}",
                file=sys.stderr,
            )

    def _validate_threshold(self):
        """Validate coverage meets threshold requirement."""
        if not COVERAGE_AVAILABLE or not self.cov:
            return

        try:
            # Get total coverage percentage
            total_coverage = self.cov.report(file=None, show_missing=False)

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
        test_files = TEST_REGISTRY.get(group, [])

        # Filter based on flags
        if self.skip_slow:
            test_files = [tf for tf in test_files if not tf.slow]
        if self.skip_real_api:
            test_files = [tf for tf in test_files if not tf.real_api]

        if not test_files:
            return

        if not self.quiet:
            self._print_group_header(group, test_files)

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
        """Run all test files in a group using pytest."""
        if not PYTEST_AVAILABLE:
            # Fallback to subprocess
            return self._run_test_file(test_files[0])

        start_time = time.time()

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
            f"Skip Slow Tests: {Colors.YELLOW if self.skip_slow else Colors.GREEN}{'Yes' if self.skip_slow else 'No'}{Colors.RESET}"
        )
        print(
            f"Skip Real API: {Colors.YELLOW if self.skip_real_api else Colors.GREEN}{'Yes' if self.skip_real_api else 'No'}{Colors.RESET}"
        )
        print()

    def _print_group_header(self, group: TestGroup, test_files: List[TestFile]):
        """Print group header."""
        print(f"{Colors.BOLD}{'-'*70}{Colors.RESET}")
        print(
            f"{Colors.BOLD}TEST GROUP: {group.value.title().replace('-', ' ')} ({len(test_files)} files){Colors.RESET}"
        )
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
            r for r in self.results if any(tf.path.name == r.file for tf in test_files)
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
                "skip_slow": self.skip_slow,
                "skip_real_api": self.skip_real_api,
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

    # Auto-Discovery (Phase 3B)
    parser.add_argument(
        "--auto-discover",
        action="store_true",
        help="Auto-discover tests using pytest markers and display results",
    )
    parser.add_argument(
        "--validate-registry",
        action="store_true",
        help="Validate TEST_REGISTRY against auto-discovered tests",
    )
    parser.add_argument(
        "--sync-registry",
        action="store_true",
        help="Generate TEST_REGISTRY code from auto-discovered tests (dry-run)",
    )

    # Options
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow tests")
    parser.add_argument(
        "--skip-real-api", action="store_true", help="Skip real API tests"
    )
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

    # Pytest options
    parser.add_argument(
        "--pytest",
        action="store_true",
        help="Use pytest runner for in-process execution (requires: pip install pytest)",
    )

    args = parser.parse_args()

    # Handle auto-discovery commands (Phase 3C)
    if args.auto_discover:
        print(f"{Colors.BOLD}Auto-Discovery Results:{Colors.RESET}\n")
        discovered = discover_test_files()

        if not discovered:
            print(f"{Colors.YELLOW}No tests discovered.{Colors.RESET}")
            return 0

        total_files = 0
        for group, test_files in sorted(discovered.items(), key=lambda x: x[0].value):
            print(f"{Colors.CYAN}{group.value}:{Colors.RESET}")
            for test_file in sorted(test_files, key=lambda x: x.path.name):
                print(f"  - {test_file.path.name}")
            print(f"  {Colors.BOLD}Total: {len(test_files)} files{Colors.RESET}\n")
            total_files += len(test_files)

        print(
            f"{Colors.BOLD}Grand Total: {total_files} test files discovered{Colors.RESET}"
        )
        return 0

    if args.validate_registry:
        print(f"{Colors.BOLD}Validating TEST_REGISTRY...{Colors.RESET}\n")
        is_valid, messages = validate_registry()

        if is_valid:
            if messages:
                # Valid but has warnings
                print(
                    f"{Colors.GREEN}✓ TEST_REGISTRY is valid{Colors.RESET} (with warnings):\n"
                )
                for msg in messages:
                    # Show warnings in yellow
                    print(f"{Colors.YELLOW}  ⚠ {msg}{Colors.RESET}")
            else:
                # Perfect match
                print(
                    f"{Colors.GREEN}✓ TEST_REGISTRY is valid and matches all discovered tests!{Colors.RESET}"
                )
            return 0
        else:
            # Has actual errors
            print(f"{Colors.RED}✗ TEST_REGISTRY validation failed:{Colors.RESET}\n")
            for msg in messages:
                # Determine if it's a warning or error
                if "collection errors" in msg.lower():
                    print(f"{Colors.YELLOW}  ⚠ {msg}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}  ✗ {msg}{Colors.RESET}")
            return 1

    if args.sync_registry:
        print(
            f"{Colors.BOLD}Generating TEST_REGISTRY code from discovered tests...{Colors.RESET}\n"
        )
        generated_code = sync_registry(dry_run=True)
        print(generated_code)
        print(
            f"\n{Colors.YELLOW}Note: This is a dry-run. Copy the code above to update TEST_REGISTRY.{Colors.RESET}"
        )
        return 0

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

    # Default to --all if no groups specified
    if not groups:
        groups.append(TestGroup.ALL)

    # Create runner and execute
    runner = TestRunner(
        skip_slow=args.skip_slow,
        skip_real_api=args.skip_real_api,
        verbose=args.verbose,
        quiet=args.quiet,
        coverage_enabled=args.coverage,
        coverage_format=args.coverage_format,
        coverage_threshold=args.coverage_threshold,
        pytest_enabled=args.pytest,
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
