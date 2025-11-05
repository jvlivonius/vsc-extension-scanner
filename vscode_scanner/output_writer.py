#!/usr/bin/env python3
"""
Output Writer Module

Responsibilities:
- Format detection (pure function)
- Content generation (pure function)
- File writing (I/O operation)
- Output orchestration

Layer: Application
Dependencies: Infrastructure (OutputFormatter, HTMLReportGenerator, utils)
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from .output_formatter import OutputFormatter
from .html_report_generator import HTMLReportGenerator
from .utils import safe_mkdir, sanitize_string, validate_path, log
from .display import display_info, display_success


class OutputWriter:
    """
    Orchestrates output generation and file writing.

    Separates pure logic (format detection, content generation) from
    side effects (file I/O, logging).
    """

    def __init__(
        self,
        output_formatter: Optional[OutputFormatter] = None,
        html_generator: Optional[HTMLReportGenerator] = None,
    ):
        """
        Initialize OutputWriter with optional dependencies.

        Args:
            output_formatter: CSV formatter (injected for testing)
            html_generator: HTML report generator (injected for testing)
        """
        self.output_formatter = output_formatter or OutputFormatter()
        self.html_generator = html_generator or HTMLReportGenerator()

    @staticmethod
    def detect_format(output_path: Path) -> str:
        """
        Detect output format from file extension (pure function).

        Args:
            output_path: Path to output file

        Returns:
            Format string: "csv", "html", or "json"

        Examples:
            >>> OutputWriter.detect_format(Path("report.csv"))
            'csv'
            >>> OutputWriter.detect_format(Path("report.html"))
            'html'
            >>> OutputWriter.detect_format(Path("output.json"))
            'json'
        """
        suffix = output_path.suffix.lower()

        if suffix == ".csv":
            return "csv"
        elif suffix in (".html", ".htm"):
            return "html"
        else:
            return "json"

    def generate_content(self, format_type: str, results: Dict) -> str:
        """
        Generate output content based on format (pure function).

        Args:
            format_type: Output format ("csv", "html", or "json")
            results: Scan results dictionary

        Returns:
            Generated content as string

        Raises:
            ValueError: If format_type is invalid
        """
        if format_type == "csv":
            return self.output_formatter.format_csv(results.get("extensions", []))
        elif format_type == "html":
            return self.html_generator.generate_report(results)
        elif format_type == "json":
            return json.dumps(results, indent=2)
        else:
            raise ValueError(f"Invalid format type: {format_type}")

    @staticmethod
    def write_to_file(output_path: Path, content: str, format_type: str) -> None:
        """
        Write content to file (I/O operation).

        Args:
            output_path: Path to output file
            content: Content to write
            format_type: Format type for encoding selection

        Note:
            CSV files use newline="" for proper line ending handling

        Raises:
            ValueError: If output_path fails security validation
        """
        # Validate path before use (security requirement)
        validate_path(str(output_path), path_type="output")

        # Create parent directories with restricted permissions
        safe_mkdir(output_path.parent, mode=0o755)

        # Use appropriate encoding and newline settings
        encoding = "utf-8"
        newline = "" if format_type == "csv" else None

        with open(output_path, "w", encoding=encoding, newline=newline) as f:
            f.write(content)

    def _get_format_message(self, format_type: str, action: str) -> str:
        """
        Get format-specific message (pure function).

        Args:
            format_type: Output format
            action: Action being performed ("generating" or "written")

        Returns:
            Format-specific message
        """
        format_names = {
            "csv": "CSV export",
            "html": "HTML report",
            "json": "Results",
        }

        format_name = format_names.get(format_type, "Results")

        if action == "generating":
            return f"Generating {format_name.lower()}..."
        else:  # "written"
            return f"{format_name} written to"

    def _log_progress(
        self, message: str, output_path_str: str, use_rich: bool, action: str
    ) -> None:
        """
        Log progress message (side effect).

        Args:
            message: Base message
            output_path_str: Output path for success messages
            use_rich: Whether to use rich display
            action: Action type ("generating" or "written")
        """
        if action == "generating":
            if use_rich:
                display_info(message, use_rich=True)
            else:
                log(message, "INFO")
        else:  # "written"
            sanitized_path = sanitize_string(output_path_str, max_length=100)
            full_message = f"{message} {sanitized_path}"

            if use_rich:
                display_success(full_message, use_rich=True)
            else:
                log(full_message, "SUCCESS")

    def write_output(
        self, output_path_str: str, results: Dict, use_rich: bool = True
    ) -> str:
        """
        Orchestrate output generation and writing.

        Args:
            output_path_str: Path to output file (absolute)
            results: Scan results dictionary
            use_rich: Whether to use rich display

        Returns:
            Format type that was written ("csv", "html", or "json")

        Example:
            >>> writer = OutputWriter()
            >>> format_type = writer.write_output(
            ...     "/path/to/report.html",
            ...     {"extensions": [...], "scan_summary": {...}},
            ...     use_rich=True
            ... )
            >>> print(format_type)
            'html'
        """
        output_path = Path(output_path_str)

        # Pure: Detect format
        format_type = self.detect_format(output_path)

        # Side effect: Log progress
        generating_msg = self._get_format_message(format_type, "generating")
        self._log_progress(generating_msg, output_path_str, use_rich, "generating")

        # Pure: Generate content
        content = self.generate_content(format_type, results)

        # Side effect: Write file
        self.write_to_file(output_path, content, format_type)

        # Side effect: Log success
        written_msg = self._get_format_message(format_type, "written")
        self._log_progress(written_msg, output_path_str, use_rich, "written")

        return format_type
