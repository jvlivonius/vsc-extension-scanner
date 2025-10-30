"""
HTML Report Generation Package.

This package contains components for generating self-contained HTML security reports
from VS Code extension scan data.

Public API:
    HTMLReportGenerator: Main class for generating HTML reports
"""

from .generator import HTMLReportGenerator

__all__ = ["HTMLReportGenerator"]
