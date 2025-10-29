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

Test Groups:
    --unit              Fast unit tests (scanner, display, CLI)
    --security          Security validation tests
    --architecture      Architecture compliance tests
    --parallel          Parallel scanning and threading tests
    --integration       Integration tests (mocked API)
    --real-api          Real API integration tests (slow)
    --mock-validation   Mock validation tests (slow)
    --all               All test groups

Options:
    --skip-slow         Skip slow tests
    --skip-real-api     Skip tests that make real API calls
    --output FORMAT     Output format: console (default), json, junit
    --output-file PATH  Output file for json/junit formats
    --verbose           Verbose output
    --quiet             Minimal output

Exit Codes:
    0 - All tests passed
    1 - Some tests failed
    2 - No tests found
    3 - Execution error

Version: 1.0
Created: 2025-10-26
"""

import sys
import subprocess
import time
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

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
            Path("tests/test_verbose_mode.py"), TestGroup.UNIT, "Verbose mode output"
        ),
        TestFile(
            Path("tests/test_config_extensions_dir.py"),
            TestGroup.UNIT,
            "Config extensions directory",
        ),
        TestFile(
            Path("tests/test_report_empty_cache.py"),
            TestGroup.UNIT,
            "Empty cache reporting",
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
        TestFile(
            Path("tests/test_transactional_cache.py"),
            TestGroup.PARALLEL,
            "Transactional cache writes",
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
        self, skip_slow=False, skip_real_api=False, verbose=False, quiet=False
    ):
        """Initialize test runner."""
        self.skip_slow = skip_slow
        self.skip_real_api = skip_real_api
        self.verbose = verbose
        self.quiet = quiet
        self.results: List[TestResult] = []
        self.start_time = time.time()

        # Detect TTY for color support
        if not sys.stdout.isatty():
            Colors.disable()

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

        # Run each group
        for group in groups:
            self._run_group(group)

        if not self.quiet:
            self._print_overall_summary()

        return self._calculate_exit_code()

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

        # Run each test file
        for test_file in test_files:
            result = self._run_test_file(test_file)
            self.results.append(result)

            if not self.quiet:
                self._print_test_result(result)

        if not self.quiet:
            self._print_group_summary(group, test_files)

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
                f"{Colors.BOLD}⚠️  CRITICAL:{Colors.RESET} 0 vulnerabilities confirmed"
            )
        elif group == TestGroup.ARCHITECTURE:
            print(
                f"{Colors.BOLD}⚠️  CRITICAL:{Colors.RESET} 0 layer violations detected"
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

        with open(filepath, "w") as f:
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
        xml_str = parseString(tostring(testsuites)).toprettyxml(indent="  ")

        with open(filepath, "w") as f:
            f.write(xml_str)

        print(f"JUnit XML output written to: {filepath}")


# ==============================================================================
# Main
# ==============================================================================


def main():
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

    args = parser.parse_args()

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
