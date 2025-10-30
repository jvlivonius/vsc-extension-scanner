"""
Overview Table Component for HTML Report.

Generates the main extensions overview table with sortable columns
and expandable detail rows.
"""

from typing import List, Dict, Any
from ..base_component import BaseComponent


class OverviewTableComponent(BaseComponent):
    """Component for generating the main extensions overview table."""

    def __init__(self):
        """Initialize with chart and detail view components."""
        super().__init__()
        from .charts import ChartComponents
        from .detail_view import DetailViewComponent

        self.charts = ChartComponents()
        self.detail_view = DetailViewComponent()

    def render(self, extensions: List[Dict[str, Any]]) -> str:
        """
        Generate main overview table with sortable columns.

        Args:
            extensions: List of extension data dictionaries

        Returns:
            HTML string for overview table section
        """
        table_rows = []

        for ext in extensions:
            row_html = self._generate_table_row(ext)
            table_rows.append(row_html)

        return f"""
        <section class="overview-table">
            <table id="extensions-table">
                <thead>
                    <tr>
                        <th class="col-name sortable" onclick="sortTable('name')">
                            Extension <span class="sort-indicator"></span>
                        </th>
                        <th class="col-version sortable" onclick="sortTable('version')">
                            Version <span class="sort-indicator"></span>
                        </th>
                        <th class="col-publisher sortable" onclick="sortTable('publisher')">
                            Publisher <span class="sort-indicator"></span>
                        </th>
                        <th class="col-verified sortable" onclick="sortTable('verified')">
                            Verified <span class="sort-indicator"></span>
                        </th>
                        <th class="col-risk sortable" onclick="sortTable('risk')">
                            Risk Level <span class="sort-indicator"></span>
                        </th>
                        <th class="col-score sortable" onclick="sortTable('score')" style="display: none;">
                            Security Score <span class="sort-indicator"></span>
                        </th>
                        <th class="col-vulnerabilities sortable" onclick="sortTable('vulnerabilities')" style="display: none;">
                            Vulnerabilities <span class="sort-indicator"></span>
                        </th>
                        <th class="col-installs sortable" onclick="sortTable('installs')" style="display: none;">
                            Installs <span class="sort-indicator"></span>
                        </th>
                        <th class="col-rating sortable" onclick="sortTable('rating')" style="display: none;">
                            Rating <span class="sort-indicator"></span>
                        </th>
                        <th class="col-dependencies sortable" onclick="sortTable('dependencies')" style="display: none;">
                            Dependencies <span class="sort-indicator"></span>
                        </th>
                        <th class="col-last-updated sortable" onclick="sortTable('last-updated')" style="display: none;">
                            Last Updated <span class="sort-indicator"></span>
                        </th>
                        <th class="col-installed sortable" onclick="sortTable('installed')" style="display: none;">
                            Installed <span class="sort-indicator"></span>
                        </th>
                        <th class="col-last-scanned sortable" onclick="sortTable('last-scanned')" style="display: none;">
                            Last Scanned <span class="sort-indicator"></span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </section>
        """

    def _generate_table_row(self, ext: Dict[str, Any]) -> str:
        """Generate a single table row with detail row."""
        ext_id = ext.get("id", "unknown")
        name = ext.get("name", "Unknown")
        display_name = ext.get("display_name", name)
        version = ext.get("version", "unknown")

        # Publisher info
        publisher = ext.get("publisher", {})
        pub_id = publisher.get("id", "Unknown")
        pub_name = publisher.get("name") or pub_id
        pub_verified = publisher.get("verified", False)

        # Security info
        security = ext.get("security", {})
        risk_level = security.get("risk_level", "unknown")
        score = security.get("score")
        score_display = f"{score}" if score is not None else "N/A"

        # Statistics
        stats = ext.get("statistics", {})
        installs = stats.get("installs")
        installs_display = self._format_number(installs) if installs else "N/A"
        rating = stats.get("rating")
        rating_count = stats.get("rating_count")
        rating_display = f"{rating:.1f} ({rating_count})" if rating else "N/A"

        deps_count = security.get("dependencies_count", 0)

        # Calculate total vulnerabilities
        vulnerabilities = security.get("vulnerabilities", {})
        vuln_count = (
            vulnerabilities.get("critical", 0)
            + vulnerabilities.get("high", 0)
            + vulnerabilities.get("moderate", 0)
            + vulnerabilities.get("low", 0)
        )

        # Dates
        last_updated = ext.get("last_updated", "N/A")
        installed_at = ext.get("installed_at", "N/A")
        last_scanned_at = ext.get("last_scanned_at", "N/A")

        scan_status = ext.get("scan_status", "unknown")

        # Generate detail view
        detail_view = self.detail_view.render(ext)

        # Risk badge
        risk_badge = (
            f'<span class="risk-badge risk-{risk_level}">{risk_level.upper()}</span>'
        )

        # Security gauge
        gauge = (
            self.charts.render_security_gauge(score, risk_level)
            if score is not None
            else "N/A"
        )

        # Publisher display
        pub_display = self._safe_escape(pub_name)

        # Vulnerability indicator
        vuln_indicator = (
            f' <span class="vuln-indicator" title="{vuln_count} vulnerabilities">⚠</span>'
            if vuln_count > 0
            else ""
        )

        row_class = (
            "extension-row" if scan_status == "success" else "extension-row scan-failed"
        )

        return f"""
            <tr class="{row_class}" data-risk="{risk_level}" data-name="{self._safe_escape(display_name.lower())}" data-publisher-name="{self._safe_escape(pub_name.lower())}" data-publisher-id="{self._safe_escape(pub_id.lower())}" data-verified="{str(pub_verified).lower()}" onclick="toggleDetails('{self._safe_escape(ext_id, quote=True)}', this)" style="cursor: pointer;">
                <td class="col-name">
                    <div class="name-container">
                        <div class="arrow-container">
                            <button class="expand-btn">▶</button>
                        </div>
                        <div class="text-container">
                            <strong>{self._safe_escape(display_name)}</strong>{vuln_indicator}
                        </div>
                    </div>
                </td>
                <td class="col-version">{self._safe_escape(version)}</td>
                <td class="col-publisher">{pub_display}</td>
                <td class="col-verified">{'✓' if pub_verified else '✗'}</td>
                <td class="col-risk">{risk_badge}</td>
                <td class="col-score" style="display: none;">{gauge}</td>
                <td class="col-vulnerabilities" style="display: none;">{vuln_count}</td>
                <td class="col-installs" style="display: none;">{installs_display}</td>
                <td class="col-rating" style="display: none;">{rating_display}</td>
                <td class="col-dependencies" style="display: none;">{deps_count}</td>
                <td class="col-last-updated" style="display: none;"><span class="date-value" data-iso-date="{self._safe_escape(last_updated)}">{self._safe_escape(last_updated)}</span></td>
                <td class="col-installed" style="display: none;"><span class="date-value" data-iso-date="{self._safe_escape(installed_at)}">{self._safe_escape(installed_at)}</span></td>
                <td class="col-last-scanned" style="display: none;"><span class="date-value" data-iso-date="{self._safe_escape(last_scanned_at)}">{self._safe_escape(last_scanned_at)}</span></td>
            </tr>
            <tr class="detail-row" id="detail-{self._safe_escape(ext_id, quote=True)}" style="display: none;">
                <td colspan="13">
                    {detail_view}
                </td>
            </tr>
            """
