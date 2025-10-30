"""
Chart Components for HTML Report.

Generates various chart visualizations for security data.
"""

from typing import Dict
from ..base_component import BaseComponent


class ChartComponents(BaseComponent):
    """Component for generating charts and data visualizations."""

    def render_risk_distribution_bar(
        self, critical: int, high: int, medium: int, low: int
    ) -> str:
        """
        Generate bar chart for risk distribution.

        Args:
            critical: Count of critical risk extensions
            high: Count of high risk extensions
            medium: Count of medium risk extensions
            low: Count of low risk extensions

        Returns:
            HTML string for bar chart visualization
        """
        total = critical + high + medium + low
        if total == 0:
            return '<div class="no-data">No data</div>'

        # Calculate percentages
        critical_pct = (critical / total) * 100
        high_pct = (high / total) * 100
        medium_pct = (medium / total) * 100
        low_pct = (low / total) * 100

        return f"""
        <div class="simple-chart">
            <div class="chart-bar">
                <div class="bar-segment risk-critical-bg" style="width: {critical_pct:.1f}%" title="Critical Risk: {critical} ({critical_pct:.1f}%)"></div>
                <div class="bar-segment risk-high-bg" style="width: {high_pct:.1f}%" title="High Risk: {high} ({high_pct:.1f}%)"></div>
                <div class="bar-segment risk-medium-bg" style="width: {medium_pct:.1f}%" title="Medium Risk: {medium} ({medium_pct:.1f}%)"></div>
                <div class="bar-segment risk-low-bg" style="width: {low_pct:.1f}%" title="Low Risk: {low} ({low_pct:.1f}%)"></div>
            </div>
        </div>
        """

    def render_security_gauge(self, score: int, risk_level: str = "unknown") -> str:
        """
        Generate security score gauge (progress bar) using risk level colors.

        Args:
            score: Security score (0-100)
            risk_level: Risk level string (critical/high/medium/low/unknown)

        Returns:
            HTML string for security gauge
        """
        if score is None:
            return "N/A"

        # Determine color based on RISK LEVEL (not score)
        risk_color_map = {
            "critical": "gauge-critical",
            "high": "gauge-danger",
            "medium": "gauge-warning",
            "low": "gauge-success",
            "unknown": "gauge-unknown",
        }
        color_class = risk_color_map.get(risk_level, "gauge-unknown")

        return f"""
        <div class="security-gauge">
            <div class="gauge-bar">
                <div class="gauge-fill {color_class}" style="width: {score}%"></div>
            </div>
            <span class="gauge-label">{score}</span>
        </div>
        """

    def render_score_pie_chart(self, score: int, risk_level: str) -> str:
        """
        Generate circular pie chart for security score.

        Args:
            score: Security score (0-100)
            risk_level: Risk level string (critical/high/medium/low/unknown)

        Returns:
            HTML string for circular pie chart
        """
        if score is None:
            return '<div class="no-data">N/A</div>'

        # Determine color based on RISK LEVEL (not score)
        risk_colors = {
            "critical": "#8b0000",  # dark red
            "high": "#dc3545",  # red
            "medium": "#fd7e14",  # orange
            "low": "#28a745",  # green
            "unknown": "#6c757d",  # gray
        }
        color = risk_colors.get(risk_level, "#6c757d")

        # Calculate the circumference and stroke-dasharray for the circle
        # For a circle with radius 42, circumference = 2 * π * r ≈ 263.9
        radius = 42
        stroke_width = 9
        circumference = 2 * 3.14159 * radius
        filled = (score / 100) * circumference

        # For clockwise rotation from 12 o'clock:
        # - Use transform="rotate(-90 50 50)" to start at 12 o'clock
        # - Use dashoffset = circumference - filled for clockwise direction
        dashoffset = circumference - filled

        return f"""
        <div class="score-pie-container">
            <svg class="score-pie" viewBox="0 0 100 100">
                <!-- Inner background for depth -->
                <circle cx="50" cy="50" r="{radius - stroke_width/2 - 1}" fill="#f8f9fa" opacity="0.5"/>
                <!-- Track circle (background) -->
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="#e9ecef" stroke-width="{stroke_width}"/>
                <!-- Progress arc (clockwise from 12 o'clock) -->
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke_width}"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{dashoffset}"
                        transform="rotate(-90 50 50)"
                        stroke-linecap="round"/>
                <!-- Score text (centered) -->
                <text x="50" y="50" text-anchor="middle" dominant-baseline="middle" class="score-text">{score}</text>
            </svg>
        </div>
        """

    def render_vulnerability_grid(self, vulnerabilities: Dict[str, int]) -> str:
        """
        Generate colored grid visualization for vulnerabilities.

        Args:
            vulnerabilities: Dictionary with vulnerability counts by severity

        Returns:
            HTML string for vulnerability grid
        """
        critical = vulnerabilities.get("critical", 0)
        high = vulnerabilities.get("high", 0)
        moderate = vulnerabilities.get("moderate", 0)
        low = vulnerabilities.get("low", 0)

        return f"""
        <div class="vuln-grid">
            <div class="vuln-box vuln-critical">
                <div class="vuln-label">Critical</div>
                <div class="vuln-count">{critical}</div>
            </div>
            <div class="vuln-box vuln-high">
                <div class="vuln-label">High</div>
                <div class="vuln-count">{high}</div>
            </div>
            <div class="vuln-box vuln-moderate">
                <div class="vuln-label">Moderate</div>
                <div class="vuln-count">{moderate}</div>
            </div>
            <div class="vuln-box vuln-low">
                <div class="vuln-label">Low</div>
                <div class="vuln-count">{low}</div>
            </div>
        </div>
        """

    def render_mini_gauge(self, score: int) -> str:
        """
        Generate mini security score gauge.

        Args:
            score: Security score (0-100)

        Returns:
            HTML string for mini gauge
        """
        if score is None:
            return "N/A"

        color_class = self._get_gauge_color_class(score)

        return f"""
        <span class="mini-gauge">
            <span class="mini-gauge-bar">
                <span class="mini-gauge-fill {color_class}" style="width: {score}%"></span>
            </span>
            <span class="mini-gauge-label">{score}</span>
        </span>
        """

    def render(self, chart_type: str, **kwargs) -> str:
        """
        Render a chart based on type.

        Args:
            chart_type: Type of chart to render
            **kwargs: Chart-specific parameters

        Returns:
            HTML string for the requested chart
        """
        chart_methods = {
            "risk_bar": self.render_risk_distribution_bar,
            "security_gauge": self.render_security_gauge,
            "score_pie": self.render_score_pie_chart,
            "vuln_grid": self.render_vulnerability_grid,
            "mini_gauge": self.render_mini_gauge,
        }

        method = chart_methods.get(chart_type)
        if method:
            return method(**kwargs)
        return f'<div class="error">Unknown chart type: {chart_type}</div>'
