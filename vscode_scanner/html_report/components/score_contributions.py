"""
Score Contributions Chart Component for HTML Report.

Generates interactive horizontal bar chart showing how each security module
contributes to the overall security score using Chart.js library.
"""

from typing import Dict, Any, List, Tuple
from ..base_component import BaseComponent


# Module display order (matches module_breakdown.py)
MODULE_ORDER = [
    ("base", "Base Score"),
    ("metadata", "Metadata"),
    ("dependencies", "Dependencies"),
    ("socket", "Socket (Supply Chain)"),
    ("virus_total", "VirusTotal"),
    ("permissions", "Permissions"),
    ("ossf_scorecard", "OSSF Scorecard"),
    ("network_endpoints", "Network Endpoints"),
    ("sensitive_info", "Sensitive Info"),
    ("obfuscation", "Obfuscation"),
    ("consolidated_ast", "AST Analysis"),
    ("open_grep", "Pattern Scanning"),
]


class ScoreContributionsComponent(BaseComponent):
    """Component for generating score contributions visualization with Chart.js."""

    def render(  # pylint: disable=arguments-differ
        self, extensions: List[Dict[str, Any]], *args, **kwargs
    ) -> str:
        """
        Render aggregated score contributions chart section.

        Args:
            extensions: List of extension data dictionaries
            *args: Additional positional arguments (ignored, for compatibility)
            **kwargs: Additional keyword arguments (ignored, for compatibility)

        Returns:
            HTML string for score contributions chart section with portfolio summary
        """
        # Extract aggregated score contributions
        chart_data = self._prepare_chart_data(extensions)

        if not chart_data["labels"]:
            # No score contribution data available
            return ""

        # Extract metadata
        metadata = chart_data.get("metadata", {})
        ext_count = metadata.get("extension_count", 0)
        portfolio_score = metadata.get("portfolio_score", 0)
        portfolio_risk = metadata.get("portfolio_risk", "unknown")

        # Risk emoji mapping
        risk_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🔴",
            "critical": "🔴🔴",
        }

        # Generate JavaScript data structures
        labels_json = self._to_json(chart_data["labels"])
        values_json = self._to_json(chart_data["values"])
        colors_json = self._to_json(chart_data["colors"])

        # Pluralize extension(s)
        ext_plural = "s" if ext_count != 1 else ""

        return f"""
        <section class="score-contributions">
            <h2>📊 Portfolio Security Analysis</h2>
            <div class="portfolio-summary">
                <div class="portfolio-score">
                    <strong>Overall Portfolio Score:</strong> {portfolio_score}/100
                    ({portfolio_risk.title()} Risk {risk_emoji.get(portfolio_risk, "")})
                </div>
                <div class="portfolio-info">
                    Average contributions across {ext_count} extension{ext_plural}
                </div>
            </div>
            <p class="score-contributions-description">
                This chart shows the average contribution of each security module across all
                scanned extensions. Positive values (green) improve scores, while negative
                values (red/yellow) indicate security concerns that affect multiple extensions.
            </p>
            <div class="score-chart-container">
                <canvas id="scoreContributionsChart" aria-label="Portfolio security contributions chart"></canvas>
            </div>
        </section>

        <script>
        (function() {{
            const ctx = document.getElementById('scoreContributionsChart');
            if (!ctx) return;

            const chartData = {{
                labels: {labels_json},
                datasets: [{{
                    label: 'Average Score Impact',
                    data: {values_json},
                    backgroundColor: {colors_json},
                    borderColor: '#333',
                    borderWidth: 1
                }}]
            }};

            const config = {{
                type: 'bar',
                data: chartData,
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Average Security Contributions Across {ext_count} Extension{ext_plural}',
                            font: {{ size: 16 }}
                        }},
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed.x;
                                    const sign = value >= 0 ? '+' : '';
                                    return 'Average Impact: ' + sign + value;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'Average Score Impact'
                            }},
                            grid: {{
                                display: true
                            }}
                        }},
                        y: {{
                            grid: {{
                                display: false
                            }}
                        }}
                    }}
                }}
            }};

            new Chart(ctx, config);
        }})();
        </script>
        """

    def _prepare_chart_data(
        self, extensions: List[Dict[str, Any]]
    ) -> Dict[str, List[Any]]:
        """
        Prepare aggregated chart data from all extension scan results.

        Calculates average contributions across all extensions to show
        portfolio-wide security posture.

        Args:
            extensions: List of extension data

        Returns:
            Dict with labels, values (averages), colors, and metadata
        """
        if not extensions:
            return {"labels": [], "values": [], "colors": [], "metadata": {}}

        # Aggregate contributions across all extensions
        module_sums = {}  # {module_key: sum_of_contributions}
        module_counts = {}  # {module_key: count_of_non_zero_values}
        extension_scores = []  # [72, 87, 82, ...]

        for ext in extensions:
            security = ext.get("security", {})
            score_contributions = security.get("score_contributions", {})

            # Collect extension score
            if "score" in security:
                extension_scores.append(security["score"])

            # Aggregate module contributions
            for module_key, _ in MODULE_ORDER:
                if module_key == "base":
                    continue  # Skip base score

                value = score_contributions.get(module_key, 0)
                if value != 0:
                    module_sums[module_key] = module_sums.get(module_key, 0) + value
                    module_counts[module_key] = module_counts.get(module_key, 0) + 1

        # Calculate averages
        labels = []
        values = []
        colors = []

        for module_key, module_name in MODULE_ORDER:
            if module_key == "base":
                continue

            if module_key in module_sums:
                # Average contribution for this module
                avg_value = module_sums[module_key] / module_counts[module_key]
                labels.append(module_name)
                values.append(round(avg_value, 1))  # Round to 1 decimal
                colors.append(self._get_color_for_value(avg_value))

        # Calculate portfolio metrics
        portfolio_score = (
            round(sum(extension_scores) / len(extension_scores), 1)
            if extension_scores
            else 0
        )

        return {
            "labels": labels,
            "values": values,
            "colors": colors,
            "metadata": {
                "extension_count": len(extensions),
                "portfolio_score": portfolio_score,
                "portfolio_risk": self._get_risk_level(portfolio_score),
            },
        }

    def _get_risk_level(self, score: float) -> str:
        """
        Determine risk level from portfolio score.

        Args:
            score: Portfolio security score (0-100)

        Returns:
            Risk level string: 'low', 'medium', 'high', or 'critical'
        """
        if score >= 90:
            return "low"
        if score >= 70:
            return "medium"
        if score >= 50:
            return "high"
        return "critical"

    def _get_color_for_value(self, value: float) -> str:
        """
        Determine bar color based on score contribution value.

        Args:
            value: Score contribution value

        Returns:
            Hex color code
        """
        if value > 0:
            return "#28a745"  # Green for positive contributions
        if value >= -5:
            return "#ffc107"  # Yellow for minor negative
        return "#dc3545"  # Red for significant negative

    def _to_json(self, data: List[Any]) -> str:
        """
        Convert Python list to JSON string for JavaScript.

        Args:
            data: List of values (strings or numbers)

        Returns:
            JSON string representation
        """
        import json

        return json.dumps(data)
