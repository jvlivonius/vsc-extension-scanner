"""
HTML Report Generator - Backward Compatibility Wrapper.

This module maintains backward compatibility with existing imports.
The implementation has been moved to vscode_scanner.html_report package.

For new code, use:
    from vscode_scanner.html_report import HTMLReportGenerator

This wrapper ensures existing code continues to work:
    from vscode_scanner.html_report_generator import HTMLReportGenerator
"""

# Import from new location
from vscode_scanner.html_report import HTMLReportGenerator

# Re-export for backward compatibility
__all__ = ["HTMLReportGenerator"]
