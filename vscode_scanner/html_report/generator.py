#!/usr/bin/env python3
"""
HTML Report Generator Module - Component-Based Architecture

Generates self-contained HTML reports from scan results with interactive
features, data visualizations, and print optimization.

This is a refactored version using component composition for improved
maintainability and testability.
"""

from typing import Dict, Any
from pathlib import Path

from .components import (
    HeaderComponent,
    ControlsComponent,
    FooterComponent,
    OverviewTableComponent,
    ChartComponents,
)


class HTMLReportGenerator:
    """
    Generates comprehensive HTML security reports using component composition.

    This class acts as an orchestrator, delegating rendering to specialized
    components for maintainability and separation of concerns.
    """

    def __init__(self):
        """Initialize report generator with all components."""
        self.header = HeaderComponent()
        self.controls = ControlsComponent()
        self.footer = FooterComponent()
        self.table = OverviewTableComponent()
        self.charts = ChartComponents()

    def generate_report(self, data: Dict[str, Any]) -> str:
        """
        Generate complete HTML report from scan data.

        Args:
            data: Output from OutputFormatter.format_output() with detailed=True
                 Must include 'summary' and 'extensions' keys

        Returns:
            Complete HTML document as string
        """
        summary = data.get("summary", {})
        extensions = data.get("extensions", [])

        # Generate risk distribution chart for header
        critical_risk = summary.get("critical_risk_extensions", 0)
        high_risk = summary.get("high_risk_extensions", 0)
        medium_risk = summary.get("medium_risk_extensions", 0)
        low_risk = summary.get("low_risk_extensions", 0)

        pie_chart_html = self.charts.render_risk_distribution_bar(
            critical_risk, high_risk, medium_risk, low_risk
        )

        # Build HTML document using components
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VS Code Extension Security Report</title>
    {self._load_styles()}
</head>
<body>
    <div class="container">
        {self.header.render(summary, pie_chart_html)}
        {self.controls.render()}
        {self.table.render(extensions)}
        {self.footer.render(summary)}
    </div>
    {self._load_scripts()}
</body>
</html>"""

        return html_doc

    def _load_styles(self) -> str:
        """Load and embed CSS styles from assets."""
        css_path = Path(__file__).parent / "assets" / "report_styles.css"
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        return f"<style>\n{css_content}\n</style>"

    def _load_scripts(self) -> str:
        """Load and embed JavaScript from assets."""
        js_path = Path(__file__).parent / "assets" / "report_scripts.js"
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        return f"<script>\n{js_content}\n</script>"
