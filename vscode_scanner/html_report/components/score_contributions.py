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
        Render score contributions chart section.

        Args:
            extensions: List of extension data dictionaries
            *args: Additional positional arguments (ignored, for compatibility)
            **kwargs: Additional keyword arguments (ignored, for compatibility)

        Returns:
            HTML string for score contributions chart section
        """
        # Extract score contributions from first extension (or aggregate)
        chart_data = self._prepare_chart_data(extensions)

        if not chart_data["labels"]:
            # No score contribution data available
            return ""

        # Generate JavaScript data structures
        labels_json = self._to_json(chart_data["labels"])
        values_json = self._to_json(chart_data["values"])
        colors_json = self._to_json(chart_data["colors"])

        return f"""
        <section class="score-contributions">
            <h2>📊 Score Breakdown Visualization</h2>
            <p class="score-contributions-description">
                This chart shows how each security module affects the overall security score.
                Positive values (green) improve the score, while negative values (red/yellow) reduce it.
            </p>
            <div class="score-chart-container">
                <canvas id="scoreContributionsChart" aria-label="Score contributions horizontal bar chart"></canvas>
            </div>
        </section>

        <script>
        (function() {{
            const ctx = document.getElementById('scoreContributionsChart');
            if (!ctx) return;

            const chartData = {{
                labels: {labels_json},
                datasets: [{{
                    label: 'Score Impact',
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
                            text: 'Security Score Contributions by Module',
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
                                    return 'Impact: ' + sign + value;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'Score Impact'
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
        Prepare chart data from extension scan results.

        Uses first extension's score_contributions for display.
        In multi-extension reports, could aggregate across all extensions.

        Args:
            extensions: List of extension data

        Returns:
            Dict with labels, values, and colors lists
        """
        if not extensions:
            return {"labels": [], "values": [], "colors": []}

        # Get score contributions from first extension
        # (In future: could aggregate across all extensions)
        first_ext = extensions[0]
        security = first_ext.get("security", {})
        score_contributions = security.get("score_contributions", {})

        if not score_contributions:
            return {"labels": [], "values": [], "colors": []}

        labels = []
        values = []
        colors = []

        # Process modules in defined order
        for module_key, module_name in MODULE_ORDER:
            value = score_contributions.get(module_key, 0)

            # Show all non-zero contributions plus base score
            if value != 0 or module_key == "base":
                labels.append(module_name)
                values.append(value)
                colors.append(self._get_color_for_value(value))

        return {"labels": labels, "values": values, "colors": colors}

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
