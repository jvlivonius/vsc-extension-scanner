#!/usr/bin/env python3
# pylint: disable=duplicate-code  # Subprocess patterns shared with coverage_manager
"""
Pytest execution via subprocess.

This module provides a single, consistent way to execute pytest via subprocess.
Replaces multiple execution strategies with one unified approach.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class PytestExecutor:
    """Executes pytest via subprocess (single execution strategy)."""

    def __init__(self, timeout: int = 300):
        """
        Initialize pytest executor.

        Args:
            timeout: Maximum execution time in seconds (default: 300 = 5 minutes)
        """
        self.timeout = timeout

    def run(
        self, command: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run pytest command and return result.

        Args:
            command: Full command to execute (e.g., ['pytest', 'tests/', '-v'])
            capture_output: Whether to capture stdout/stderr (default: True)

        Returns:
            CompletedProcess with returncode, stdout, stderr

        Raises:
            subprocess.TimeoutExpired: If execution exceeds timeout
        """
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout,
                check=False,  # Don't raise on non-zero exit (we handle via returncode)
            )
            return result

        except subprocess.TimeoutExpired as e:
            # Re-raise with more context
            raise subprocess.TimeoutExpired(
                cmd=e.cmd, timeout=e.timeout, output=e.output, stderr=e.stderr
            ) from e

    def build_command(
        self,
        test_paths: List[Path],
        markers: Optional[List[str]] = None,
        verbosity: str = "normal",
        extra_args: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Build pytest command with common options.

        Args:
            test_paths: List of test file/directory paths
            markers: pytest markers to filter tests (e.g., ['not real_api', 'security'])
            verbosity: Output verbosity ('quiet', 'normal', 'verbose')
            extra_args: Additional pytest arguments

        Returns:
            Complete command as list of strings
        """
        command = [sys.executable, "-m", "pytest"]

        # Add test paths
        for path in test_paths:
            command.append(str(path))

        # Add markers
        if markers:
            marker_expr = " and ".join(markers)
            command.extend(["-m", marker_expr])

        # Add verbosity
        if verbosity == "quiet":
            command.append("-q")
        elif verbosity == "verbose":
            command.append("-vv")
        # 'normal' uses pytest default (no flag)

        # Add standard options
        command.extend(["--disable-warnings", "--tb=short"])

        # Add extra arguments
        if extra_args:
            command.extend(extra_args)

        return command

    def validate_pytest_available(self) -> bool:
        """
        Check if pytest is available.

        Returns:
            True if pytest can be imported, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
