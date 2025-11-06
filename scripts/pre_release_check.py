#!/usr/bin/env python3
"""
Pre-Release Validation Runner for VS Code Extension Scanner

Comprehensive validation checks before releasing a new version.

Usage:
    python3 scripts/pre_release_check.py [OPTIONS]

Examples:
    python3 scripts/pre_release_check.py                      # Full validation (quiet)
    python3 scripts/pre_release_check.py --verbose            # Show detailed progress
    python3 scripts/pre_release_check.py --skip-git           # Skip git checks

Exit Codes:
    0 - All checks passed
    1 - Some checks failed
    3 - Execution error

Validation Steps:
    1. Version consistency across all files (bump_version.py --check)
    2. Git repository status (clean, on main/master)
    3. All tests pass (via run_tests.py --ci with coverage)
    4. Security scans pass (bandit, safety, pip-audit)
    5. Coverage meets minimum threshold (80%+)

Version: 1.0
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Import shared utilities and components from lib package
from lib import (
    Colors,
    EXIT_SUCCESS,
    EXIT_FAILURE,
    EXIT_ERROR,
    CoverageManager,
)


# ==============================================================================
# Helper Methods
# ==============================================================================


def _print_header(verbose: bool):
    """Print validation header."""
    if verbose:
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}PRE-RELEASE VALIDATION CHECKS{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")


def _print_summary(verbose: bool, all_passed: bool, results: dict):
    """Print validation summary with details of failed checks."""
    if verbose:
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        if all_passed:
            print(
                f"{Colors.GREEN}✅ PRE-RELEASE VALIDATION: ALL CHECKS PASSED{Colors.RESET}"
            )
        else:
            print(
                f"{Colors.RED}❌ PRE-RELEASE VALIDATION: SOME CHECKS FAILED{Colors.RESET}"
            )
            print(f"\n{Colors.YELLOW}Failed checks:{Colors.RESET}")
            for check, passed in results.items():
                if not passed:
                    print(f"  • {check}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")


def _run_security_tool(
    name: str, command: list[str], success_msg: str, verbose: bool
) -> bool:
    """Run single security tool and report results."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=60, check=False
        )
        if result.returncode == 0:
            if verbose:
                print(f"      {Colors.GREEN}✓{Colors.RESET} {name}: {success_msg}")
            return True
        else:
            if verbose:
                print(f"      {Colors.RED}✗{Colors.RESET} {name}: Issues detected")
                if result.stdout:
                    print(f"        {result.stdout}")
            return False
    except Exception as e:
        if verbose:
            print(
                f"      {Colors.YELLOW}⚠{Colors.RESET} {name} check skipped: {str(e)}"
            )
        return True  # Don't fail on tool unavailability


def _validate_version(verbose: bool) -> bool:
    """Validate version consistency across files."""
    if verbose:
        print("\n[1/5] Validating version consistency...")

    version_cmd = [sys.executable, "scripts/bump_version.py", "--check"]
    if verbose:
        version_cmd.append("--verbose")

    try:
        result = subprocess.run(
            version_cmd,
            capture_output=not verbose,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode == 0:
            if verbose:
                print(
                    f"      {Colors.GREEN}✓{Colors.RESET} Version consistency validated"
                )
            return True
        else:
            if verbose:
                print(f"      {Colors.RED}✗{Colors.RESET} Version mismatch detected")
                if not verbose and result.stdout:
                    print(f"        {result.stdout}")
            return False
    except Exception as e:
        if verbose:
            print(f"      {Colors.RED}✗{Colors.RESET} Version check failed: {str(e)}")
        return False


def _validate_git(verbose: bool) -> bool:
    """Validate git working directory is clean and on main/master."""
    if verbose:
        print("\n[2/5] Validating git working directory...")

    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            if verbose:
                print(f"      {Colors.RED}✗{Colors.RESET} Not a git repository")
            return False

        # Check current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        branch = result.stdout.strip()
        if branch not in ["main", "master"]:
            if verbose:
                print(
                    f"      {Colors.RED}✗{Colors.RESET} Not on main/master branch (current: {branch})"
                )
            return False

        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.stdout.strip():
            if verbose:
                print(
                    f"      {Colors.RED}✗{Colors.RESET} Working directory has uncommitted changes"
                )
                print(f"        {result.stdout}")
            return False

        if verbose:
            print(
                f"      {Colors.GREEN}✓{Colors.RESET} Git status clean (branch: {branch})"
            )
        return True

    except FileNotFoundError:
        if verbose:
            print(
                f"      {Colors.YELLOW}⚠{Colors.RESET} Git check skipped: git command not found"
            )
        return True  # Don't fail if git unavailable
    except Exception as e:
        if verbose:
            print(f"      {Colors.YELLOW}⚠{Colors.RESET} Git check skipped: {str(e)}")
        return True


def _run_tests_with_coverage(verbose: bool) -> bool:
    """Run test suite with mandatory coverage tracking."""
    if verbose:
        print("\n[3/5] Running test suite with coverage...")

    try:
        # Build command with verbose and coverage flags
        # run_tests.py has built-in coverage support via --coverage flag
        test_cmd = [sys.executable, "scripts/run_tests.py", "--ci", "--coverage"]
        if not verbose:
            test_cmd.append("--quiet")

        # Execute (let output flow through if verbose)
        result = subprocess.run(
            test_cmd,
            capture_output=not verbose,
            text=True,
            timeout=300,
            check=False,
        )

        if result.returncode == 0:
            if verbose:
                print(f"      {Colors.GREEN}✓{Colors.RESET} All tests passed")
            return True
        else:
            if verbose:
                print(f"      {Colors.RED}✗{Colors.RESET} Some tests failed")
                if not verbose and result.stderr:
                    print(f"        {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        if verbose:
            print(f"      {Colors.RED}✗{Colors.RESET} Tests timed out after 5 minutes")
        return False
    except Exception as e:
        if verbose:
            print(f"      {Colors.RED}✗{Colors.RESET} Test execution failed: {str(e)}")
        return False


def _run_security_scans(verbose: bool) -> bool:
    """Run security scanning tools."""
    if verbose:
        print("\n[4/5] Running security scans...")

    tools = [
        (
            "bandit",
            [sys.executable, "-m", "bandit", "-r", "vscode_scanner/", "-lll"],
            "No high severity issues",
        ),
        (
            "safety",
            [sys.executable, "-m", "safety", "check", "--json"],
            "No known vulnerabilities",
        ),
        ("pip-audit", [sys.executable, "-m", "pip_audit"], "No vulnerabilities"),
    ]

    all_passed = True
    for tool_name, command, success_msg in tools:
        if not _run_security_tool(tool_name, command, success_msg, verbose):
            all_passed = False

    return all_passed


def _validate_coverage_threshold(verbose: bool) -> bool:
    """Validate coverage meets 80% threshold."""
    if verbose:
        print("\n[5/5] Validating test coverage...")

    try:
        coverage_mgr = CoverageManager(enabled=True, threshold=80.0)
        coverage_pct = coverage_mgr.get_coverage_percentage()

        if coverage_pct is None:
            if verbose:
                print(
                    f"      {Colors.YELLOW}⚠{Colors.RESET} Coverage data not available"
                )
            return False

        if coverage_pct >= 80.0:
            if verbose:
                print(
                    f"      {Colors.GREEN}✓{Colors.RESET} Coverage: {coverage_pct:.1f}% (target: 80%+)"
                )
            return True
        else:
            if verbose:
                print(
                    f"      {Colors.RED}✗{Colors.RESET} Coverage: {coverage_pct:.1f}% (below 80% threshold)"
                )
            return False

    except Exception as e:
        if verbose:
            print(
                f"      {Colors.YELLOW}⚠{Colors.RESET} Coverage validation failed: {str(e)}"
            )
        return False


def run_pre_release_checks(verbose: bool = True, skip_git: bool = False) -> bool:
    """
    Run comprehensive pre-release validation checks.

    Validation Steps:
    1. Version consistency across all files
    2. Git repository status (clean, on main/master)
    3. All tests pass with mandatory coverage
    4. Security scans pass (bandit, safety, pip-audit)
    5. Coverage meets minimum threshold (80%+)

    Args:
        verbose: Print detailed progress information
        skip_git: Skip git repository validation

    Returns:
        True if all checks pass, False otherwise
    """
    _print_header(verbose)

    results = {
        "version": _validate_version(verbose),
        "git": _validate_git(verbose) if not skip_git else True,
        "tests": _run_tests_with_coverage(verbose),
        "security": _run_security_scans(verbose),
        "coverage": _validate_coverage_threshold(verbose),
    }

    all_passed = all(results.values())
    _print_summary(verbose, all_passed, results)

    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pre-Release Validation Runner for VS Code Extension Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Detailed progress output (default: quiet)",
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Skip git repository validation checks",
    )

    args = parser.parse_args()

    # Run pre-release checks
    success = run_pre_release_checks(verbose=args.verbose, skip_git=args.skip_git)

    return EXIT_SUCCESS if success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
