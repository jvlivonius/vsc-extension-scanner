"""
Header Component for HTML Report.

Generates the report header with summary statistics and risk distribution charts.
"""

from typing import Dict, Any
from ..base_component import BaseComponent


class HeaderComponent(BaseComponent):
    """Component for generating report header with summary and charts."""

    def render(self, summary: Dict[str, Any], pie_chart_html: str) -> str:
        """
        Render report header with summary statistics and charts.

        Args:
            summary: Summary statistics dictionary
            pie_chart_html: Pre-generated pie chart HTML (from ChartComponent)

        Returns:
            HTML string for header section
        """
        # Extract summary statistics
        timestamp = summary.get("scan_timestamp", "Unknown")
        total = summary.get("total_extensions_scanned", 0)
        duration = summary.get("scan_duration_seconds", 0)
        vuln_found = summary.get("vulnerabilities_found", 0)

        # Extract risk counts
        critical_risk = summary.get("critical_risk_extensions", 0)
        high_risk = summary.get("high_risk_extensions", 0)
        medium_risk = summary.get("medium_risk_extensions", 0)
        low_risk = summary.get("low_risk_extensions", 0)

        # Extract cache statistics
        cache_stats = summary.get("cache_statistics", {})
        cache_hit_rate = cache_stats.get("cache_hit_rate", 0)

        return f"""
        <header class="report-header">
            <h1>VS Code Extension Security Report</h1>
            <div class="metadata">
                <div class="metadata-item">
                    <span class="label">Generated:</span>
                    <span class="value date-value" data-iso-date="{self._safe_escape(timestamp)}">{self._safe_escape(timestamp)}</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Total Extensions:</span>
                    <span class="value">{total}</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Scan Duration:</span>
                    <span class="value">{duration:.1f}s</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Cache Hit Rate:</span>
                    <span class="value">{cache_hit_rate:.1f}%</span>
                </div>
            </div>

            <div class="summary-charts">
                <div class="chart-container">
                    <h3>Risk Distribution</h3>
                    {pie_chart_html}
                    <div class="chart-legend">
                        <div class="legend-item">
                            <span class="legend-color risk-critical-bg"></span>
                            <span>Critical Risk: {critical_risk}</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-color risk-high-bg"></span>
                            <span>High Risk: {high_risk}</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-color risk-medium-bg"></span>
                            <span>Medium Risk: {medium_risk}</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-color risk-low-bg"></span>
                            <span>Low Risk: {low_risk}</span>
                        </div>
                    </div>
                </div>

                <div class="chart-container vulnerabilities-kpi">
                    <h3>Vulnerabilities Found</h3>
                    <div class="vuln-kpi-display">
                        <div class="vuln-kpi-number">{vuln_found}</div>
                        <div class="vuln-kpi-label">Total Vulnerabilities</div>
                    </div>
                </div>
            </div>
        </header>
        """
