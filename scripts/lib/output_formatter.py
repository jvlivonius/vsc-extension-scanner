#!/usr/bin/env python3
"""
Output formatting and reporting.

This module handles all presentation concerns: console output,
JSON export, JUnit XML export.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

from .test_utils import Colors
from .pytest_output_parser import TestResult, OutputMode


class OutputFormatter:
    """Handles all output formatting and reporting."""

    def __init__(self, mode: OutputMode = OutputMode.NORMAL):
        """
        Initialize formatter with output mode.

        Args:
            mode: Output verbosity mode (QUIET, NORMAL, VERBOSE)
        """
        self.mode = mode

    def print_header(self, groups: List[str], fast: bool = False):
        """
        Print test run header.

        Args:
            groups: List of test group names
            fast: Whether fast mode is enabled (skip slow tests)
        """
        if self.mode == OutputMode.QUIET:
            return

        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}VS CODE EXTENSION SCANNER - TEST SUITE{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

        print(f"Running Test Groups: {Colors.CYAN}{', '.join(groups)}{Colors.RESET}")
        print(
            f"Fast Mode (skip slow tests): {Colors.CYAN if fast else Colors.GREEN}{'Yes' if fast else 'No'}{Colors.RESET}"
        )
        print()

    def print_group_header(self, group: str, file_count: int, skipped_count: int = 0):
        """
        Print group header with optional skipped test count.

        Args:
            group: Test group name
            file_count: Number of test files in group
            skipped_count: Number of skipped files (in fast mode)
        """
        if self.mode == OutputMode.QUIET:
            return

        print(f"{Colors.BOLD}{'-'*70}{Colors.RESET}")

        header_text = (
            f"TEST GROUP: {group.title().replace('-', ' ')} ({file_count} files)"
        )
        if skipped_count > 0:
            header_text += (
                f" {Colors.YELLOW}[{skipped_count} skipped - fast mode]{Colors.RESET}"
            )

        print(f"{Colors.BOLD}{header_text}{Colors.RESET}")
        print(f"{Colors.BOLD}{'-'*70}{Colors.RESET}")

    def print_result(self, result: TestResult):
        """
        Print individual test result (mode-aware).

        Args:
            result: Test result to print
        """
        # In quiet mode, only show failed or error tests
        if self.mode == OutputMode.QUIET and result.status == "PASS":
            return

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

        # Show error details in non-verbose mode
        if result.error and self.mode != OutputMode.VERBOSE:
            print(f"   {Colors.RED}Error: {result.error[:60]}{Colors.RESET}")

    def print_group_summary(self, results: List[TestResult]):
        """
        Print group summary.

        Args:
            results: List of test results for this group
        """
        if self.mode == OutputMode.QUIET or not results:
            return

        total_tests = sum(r.tests_run for r in results)
        total_passed = sum(r.tests_passed for r in results)
        total_failed = sum(r.tests_failed for r in results)
        total_skipped = sum(r.tests_skipped for r in results)
        total_duration = sum(r.duration for r in results)

        print(
            f"\nSummary: {total_tests} tests, "
            f"{Colors.GREEN}{total_passed} passed{Colors.RESET}, "
            f"{Colors.RED if total_failed > 0 else ''}{total_failed} failed{Colors.RESET}, "
            f"{total_skipped} skipped "
            f"({total_duration:.3f}s)"
        )
        print()

    def print_overall_summary(
        self, results: List[TestResult], start_time: float, end_time: float
    ):
        """
        Print overall summary.

        Args:
            results: All test results
            start_time: Start timestamp
            end_time: End timestamp
        """
        total_files = len(results)
        total_tests = sum(r.tests_run for r in results)
        total_passed = sum(r.tests_passed for r in results)
        total_failed = sum(r.tests_failed for r in results)
        total_skipped = sum(r.tests_skipped for r in results)
        total_duration = end_time - start_time

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

        exit_code = self._calculate_exit_code(results)
        exit_status = "SUCCESS" if exit_code == 0 else "FAILURE"
        exit_color = Colors.GREEN if exit_code == 0 else Colors.RED

        print(f"\nExit Code: {exit_code} ({exit_color}{exit_status}{Colors.RESET})")
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    def _calculate_exit_code(self, results: List[TestResult]) -> int:
        """
        Calculate exit code based on results.

        Args:
            results: All test results

        Returns:
            Exit code (0=success, 1=failures, 2=no tests, 3=error)
        """
        if not results:
            return 2  # No tests found

        if any(r.status == "ERROR" for r in results):
            return 3  # Execution error

        if any(r.status == "FAIL" for r in results):
            return 1  # Test failures

        return 0  # Success

    def export_json(
        self,
        results: List[TestResult],
        filepath: Path,
        start_time: float,
        end_time: float,
    ):
        """
        Export results as JSON.

        Args:
            results: Test results to export
            filepath: Output file path
            start_time: Start timestamp
            end_time: End timestamp
        """
        output = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": end_time - start_time,
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
                for r in results
            ],
            "summary": {
                "total_files": len(results),
                "total_tests": sum(r.tests_run for r in results),
                "total_passed": sum(r.tests_passed for r in results),
                "total_failed": sum(r.tests_failed for r in results),
                "total_skipped": sum(r.tests_skipped for r in results),
                "exit_code": self._calculate_exit_code(results),
            },
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"JSON output written to: {filepath}")

    def export_junit(
        self,
        results: List[TestResult],
        filepath: Path,
        start_time: float,
        end_time: float,
    ):
        """
        Export results as JUnit XML.

        Args:
            results: Test results to export
            filepath: Output file path
            start_time: Start timestamp
            end_time: End timestamp
        """
        # Create root element
        testsuites = Element(
            "testsuites",
            {
                "name": "vscode_scanner",
                "tests": str(sum(r.tests_run for r in results)),
                "failures": str(sum(r.tests_failed for r in results)),
                "errors": str(sum(1 for r in results if r.status == "ERROR")),
                "time": f"{end_time - start_time:.3f}",
            },
        )

        # Create testsuite for each result
        for result in results:
            testsuite = SubElement(
                testsuites,
                "testsuite",
                {
                    "name": result.file,
                    "tests": str(result.tests_run),
                    "failures": str(result.tests_failed),
                    "errors": str(1 if result.status == "ERROR" else 0),
                    "time": f"{result.duration:.3f}",
                },
            )

            # Add testcase
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
                failure = SubElement(testcase, "failure", {"message": "Test failed"})
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
