"""
Module Breakdown Component for HTML Report.

Generates security analysis breakdown showing all 11 security modules
with risk levels and score contributions.
"""

from typing import Dict, Any, List
from ..base_component import BaseComponent


# Module Display Names (matches CLI display.py)
MODULE_DISPLAY_NAMES = {
    "metadata": "Metadata",
    "dependencies": "Dependencies",
    "socket": "Socket (Supply Chain)",
    "virus_total": "VirusTotal",
    "permissions": "Permissions",
    "ossf_scorecard": "OSSF Scorecard",
    "network_endpoints": "Network Endpoints",
    "sensitive_info": "Sensitive Info",
    "obfuscation": "Obfuscation",
    "consolidated_ast": "AST Analysis",
    "open_grep": "Pattern Scanning",
}


class ModuleBreakdownComponent(BaseComponent):
    """Component for generating security module breakdown section."""

    def render(  # pylint: disable=arguments-differ
        self, extensions: List[Dict[str, Any]], *args, **kwargs
    ) -> str:
        """
        Render module breakdown section showing aggregate module analysis.

        Args:
            extensions: List of extension data dictionaries
            *args: Additional positional arguments (ignored, for compatibility)
            **kwargs: Additional keyword arguments (ignored, for compatibility)

        Returns:
            HTML string for module breakdown section
        """
        # Calculate aggregate module statistics
        module_stats = self._calculate_module_stats(extensions)

        if not module_stats:
            # No module data available - return empty section
            return ""

        # Generate table rows
        table_rows = self._generate_table_rows(module_stats)

        return f"""
        <section class="module-breakdown">
            <h2>Security Analysis Breakdown</h2>
            <p class="module-breakdown-description">
                This breakdown shows the 11 security analysis modules used to evaluate each extension.
                Risk levels and score impacts are aggregated across all scanned extensions.
            </p>
            <div class="module-breakdown-table-container">
                <table class="module-breakdown-table">
                    <thead>
                        <tr>
                            <th class="col-module">Module</th>
                            <th class="col-risk">Risk Distribution</th>
                            <th class="col-score">Avg Score Impact</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </section>
        """

    def _calculate_module_stats(
        self, extensions: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate aggregate statistics for each module across all extensions.

        Args:
            extensions: List of extension data

        Returns:
            Dict mapping module keys to statistics (risk counts, avg score impact)
        """
        stats = {}

        # Initialize stats for each module
        for module_key in MODULE_DISPLAY_NAMES:
            stats[module_key] = {
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "none_count": 0,
                "score_impacts": [],
                "total_extensions": 0,
            }

        # Aggregate data from all extensions
        for ext in extensions:
            security = ext.get("security", {})
            module_risks = security.get("module_risk_levels", {})
            score_contributions = security.get("score_contributions", {})

            if not module_risks:
                continue  # Skip extensions without module data

            for module_key in MODULE_DISPLAY_NAMES:
                risk_level = module_risks.get(module_key, "none")
                score_impact = score_contributions.get(module_key, 0)

                # Count risk levels
                risk_key = f"{risk_level}_count"
                if risk_key in stats[module_key]:
                    stats[module_key][risk_key] += 1

                # Collect score impacts
                stats[module_key]["score_impacts"].append(score_impact)
                stats[module_key]["total_extensions"] += 1

        # Calculate averages
        for module_key, module_data in stats.items():
            impacts = module_data["score_impacts"]
            if impacts:
                module_data["avg_score_impact"] = sum(impacts) / len(impacts)
            else:
                module_data["avg_score_impact"] = 0

        # Return empty if no valid data
        if all(s["total_extensions"] == 0 for s in stats.values()):
            return {}

        return stats

    def _generate_table_rows(self, module_stats: Dict[str, Dict[str, Any]]) -> str:
        """
        Generate table rows for module breakdown.

        Args:
            module_stats: Module statistics from _calculate_module_stats()

        Returns:
            HTML string of table rows
        """
        rows = []

        for module_key, display_name in MODULE_DISPLAY_NAMES.items():
            stats = module_stats.get(module_key, {})

            if stats.get("total_extensions", 0) == 0:
                continue  # Skip modules with no data

            # Risk distribution bars
            high = stats.get("high_count", 0)
            medium = stats.get("medium_count", 0)
            low = stats.get("low_count", 0)
            none = stats.get("none_count", 0)
            total = stats.get("total_extensions", 0)

            # Calculate percentages
            high_pct = (high / total * 100) if total > 0 else 0
            medium_pct = (medium / total * 100) if total > 0 else 0
            low_pct = (low / total * 100) if total > 0 else 0
            none_pct = (none / total * 100) if total > 0 else 0

            # Build risk distribution bar HTML
            risk_bar_html = f"""
            <div class="risk-distribution-bar">
                {f'<div class="risk-bar-segment risk-high" style="width: {high_pct:.1f}%" title="High: {high}"></div>' if high > 0 else ''}
                {f'<div class="risk-bar-segment risk-medium" style="width: {medium_pct:.1f}%" title="Medium: {medium}"></div>' if medium > 0 else ''}
                {f'<div class="risk-bar-segment risk-low" style="width: {low_pct:.1f}%" title="Low: {low}"></div>' if low > 0 else ''}
                {f'<div class="risk-bar-segment risk-none" style="width: {none_pct:.1f}%" title="None: {none}"></div>' if none > 0 else ''}
            </div>
            <div class="risk-counts">
                {f'<span class="risk-count risk-high">{high}H</span>' if high > 0 else ''}
                {f'<span class="risk-count risk-medium">{medium}M</span>' if medium > 0 else ''}
                {f'<span class="risk-count risk-low">{low}L</span>' if low > 0 else ''}
                {f'<span class="risk-count risk-none">{none}N</span>' if none > 0 else ''}
            </div>
            """

            # Score impact
            avg_impact = stats.get("avg_score_impact", 0)
            impact_class = (
                "score-positive"
                if avg_impact > 0
                else "score-negative"
                if avg_impact < 0
                else "score-neutral"
            )
            impact_text = f"{avg_impact:+.1f}" if avg_impact != 0 else "0.0"

            row_html = f"""
            <tr>
                <td class="col-module">
                    <strong>{self._safe_escape(display_name)}</strong>
                </td>
                <td class="col-risk">
                    {risk_bar_html}
                </td>
                <td class="col-score {impact_class}">
                    {impact_text}
                </td>
            </tr>
            """
            rows.append(row_html)

        return "\n".join(rows)
