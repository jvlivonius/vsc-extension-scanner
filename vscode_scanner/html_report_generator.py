#!/usr/bin/env python3
"""
HTML Report Generator Module

Generates self-contained HTML reports from scan results with interactive
features, data visualizations, and print optimization.
"""

import html
import json
from typing import Dict, Any, List
from datetime import datetime
from ._version import __version__


class HTMLReportGenerator:
    """Generates comprehensive HTML security reports."""

    def _safe_escape(self, value: Any, default: str = "N/A", quote: bool = True) -> str:
        """Safely escape HTML, handling None values."""
        if value is None:
            return default
        return html.escape(str(value), quote=quote)

    def _get_gauge_color_class(self, score: int) -> str:
        """Get CSS class for gauge color based on score."""
        if score >= 75:
            return "gauge-success"
        elif score >= 50:
            return "gauge-warning"
        else:
            return "gauge-danger"

    def generate_report(self, data: Dict[str, Any]) -> str:
        """
        Generate complete HTML report from scan data.

        Args:
            data: Output from OutputFormatter.format_output() with detailed=True

        Returns:
            Complete HTML document as string
        """
        summary = data.get("summary", {})
        extensions = data.get("extensions", [])

        # Build HTML document
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VS Code Extension Security Report</title>
    {self._generate_styles()}
</head>
<body>
    <div class="container">
        {self._generate_header(summary)}
        {self._generate_controls()}
        {self._generate_overview_table(extensions)}
        {self._generate_footer(summary)}
    </div>
    {self._generate_scripts()}
</body>
</html>"""

        return html_doc

    def _generate_header(self, summary: Dict[str, Any]) -> str:
        """Generate report header with summary and charts."""
        timestamp = summary.get("scan_timestamp", "Unknown")
        total = summary.get("total_extensions_scanned", 0)
        duration = summary.get("scan_duration_seconds", 0)
        vuln_found = summary.get("vulnerabilities_found", 0)

        critical_risk = summary.get("critical_risk_extensions", 0)
        high_risk = summary.get("high_risk_extensions", 0)
        medium_risk = summary.get("medium_risk_extensions", 0)
        low_risk = summary.get("low_risk_extensions", 0)

        cache_stats = summary.get("cache_statistics", {})
        from_cache = cache_stats.get("from_cache", 0)
        fresh_scans = cache_stats.get("fresh_scans", 0)
        cache_hit_rate = cache_stats.get("cache_hit_rate", 0)

        # Generate charts
        pie_chart = self._generate_pie_chart_svg(
            critical_risk, high_risk, medium_risk, low_risk
        )

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
                    {pie_chart}
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

    def _generate_controls(self) -> str:
        """Generate filter controls and search box."""
        return """
        <section class="controls">
            <div class="search-filter">
                <input type="text" id="search-box" placeholder="Search extensions..."
                       onkeyup="searchExtensions()">

                <select id="risk-filter" onchange="filterByRisk()">
                    <option value="all">All Risk Levels</option>
                    <option value="critical">Critical Risk Only</option>
                    <option value="high">High Risk Only</option>
                    <option value="medium">Medium Risk Only</option>
                    <option value="low">Low Risk Only</option>
                </select>

                <select id="verified-filter" onchange="filterByVerified()">
                    <option value="all">All Publishers</option>
                    <option value="verified">Verified Only</option>
                    <option value="unverified">Unverified Only</option>
                </select>

                <button onclick="clearFilters()" class="btn-secondary">Clear Filters</button>

                <button onclick="toggleColumnDropdown()" class="btn-icon" title="Show/Hide Columns">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
                        <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"/>
                    </svg>
                </button>

                <div id="column-dropdown" class="column-dropdown" style="display: none;">
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-name" checked onchange="toggleColumn('name')">
                        <label for="col-name">Name</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-version" checked onchange="toggleColumn('version')">
                        <label for="col-version">Version</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-publisher" checked onchange="toggleColumn('publisher')">
                        <label for="col-publisher">Publisher</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-verified" checked onchange="toggleColumn('verified')">
                        <label for="col-verified">Verified</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-risk" checked onchange="toggleColumn('risk')">
                        <label for="col-risk">Risk</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-score" onchange="toggleColumn('score')">
                        <label for="col-score">Security Score</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-vulnerabilities" onchange="toggleColumn('vulnerabilities')">
                        <label for="col-vulnerabilities">Vulnerabilities</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-installs" onchange="toggleColumn('installs')">
                        <label for="col-installs">Installs</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-rating" onchange="toggleColumn('rating')">
                        <label for="col-rating">Rating</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-dependencies" onchange="toggleColumn('dependencies')">
                        <label for="col-dependencies">Dependencies</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-last-updated" onchange="toggleColumn('last-updated')">
                        <label for="col-last-updated">Last Updated</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-installed" onchange="toggleColumn('installed')">
                        <label for="col-installed">Installed</label>
                    </div>
                    <div class="column-dropdown-item">
                        <input type="checkbox" id="col-last-scanned" onchange="toggleColumn('last-scanned')">
                        <label for="col-last-scanned">Last Scanned</label>
                    </div>
                </div>
            </div>
        </section>
        """

    def _generate_overview_table(self, extensions: List[Dict[str, Any]]) -> str:
        """Generate main overview table with sortable columns."""
        table_rows = []

        for ext in extensions:
            ext_id = ext.get("id", "unknown")
            name = ext.get("name", "Unknown")
            display_name = ext.get("display_name", name)
            version = ext.get("version", "unknown")

            publisher = ext.get("publisher", {})
            pub_id = publisher.get("id", "Unknown")
            pub_name = publisher.get("name") or pub_id
            pub_verified = publisher.get("verified", False)

            security = ext.get("security", {})
            risk_level = security.get("risk_level", "unknown")
            score = security.get("score")
            score_display = f"{score}" if score is not None else "N/A"

            stats = ext.get("statistics", {})
            installs = stats.get("installs")
            installs_display = self._format_number(installs) if installs else "N/A"
            rating = stats.get("rating")
            rating_count = stats.get("rating_count")
            rating_display = f"{rating:.1f} ({rating_count})" if rating else "N/A"

            deps_count = security.get("dependencies_count", 0)

            # Calculate total vulnerabilities as sum of all severity levels
            vulnerabilities = security.get("vulnerabilities", {})
            vuln_count = (
                vulnerabilities.get("critical", 0)
                + vulnerabilities.get("high", 0)
                + vulnerabilities.get("moderate", 0)
                + vulnerabilities.get("low", 0)
            )

            last_updated = ext.get("last_updated", "N/A")
            installed_at = ext.get("installed_at", "N/A")
            last_scanned_at = ext.get("last_scanned_at", "N/A")

            scan_status = ext.get("scan_status", "unknown")

            # Generate detail view
            detail_view = self._generate_detail_view(ext)

            # Risk badge
            risk_badge = f'<span class="risk-badge risk-{risk_level}">{risk_level.upper()}</span>'

            # Security gauge (using risk level colors)
            gauge = (
                self._generate_security_gauge(score, risk_level)
                if score is not None
                else "N/A"
            )

            # Publisher (verification now in separate column)
            pub_display = self._safe_escape(pub_name)

            # Vulnerability indicator
            vuln_indicator = (
                f' <span class="vuln-indicator" title="{vuln_count} vulnerabilities">⚠</span>'
                if vuln_count > 0
                else ""
            )

            row_class = (
                "extension-row"
                if scan_status == "success"
                else "extension-row scan-failed"
            )

            table_rows.append(
                f"""
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
            )

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

    def _generate_detail_view(self, ext: Dict[str, Any]) -> str:
        """Generate detailed extension information."""
        ext_id = ext.get("id", "unknown")
        name = ext.get("display_name") or ext.get("name", "Unknown")
        version = ext.get("version", "unknown")
        description = ext.get("description") or "No description available"

        # Metadata section
        license_text = ext.get("license") or "N/A"
        repo_url = ext.get("repository_url") or ""
        homepage_url = ext.get("homepage_url") or ""
        keywords = ext.get("keywords") or []
        categories = ext.get("categories") or []
        last_updated = ext.get("last_updated") or "N/A"
        installed_at = ext.get("installed_at") or "N/A"
        last_scanned_at = ext.get("last_scanned_at") or "N/A"

        # Publisher section
        publisher = ext.get("publisher", {})
        pub_name = publisher.get("name") or "Unknown"
        pub_id = publisher.get("id") or "Unknown"
        pub_verified = publisher.get("verified", False)
        pub_domain = publisher.get("domain") or "N/A"

        # Security section
        security = ext.get("security", {})
        score = security.get("score")
        risk_level = security.get("risk_level", "unknown")
        score_contributions = security.get("score_contributions", {})
        risk_factors = security.get("risk_factors", [])
        security_notes = security.get("security_notes", [])
        vulnerabilities = security.get("vulnerabilities", {})

        # Dependencies
        dependencies_data = security.get("dependencies", {})
        total_deps = dependencies_data.get("total_count", 0)
        runtime_deps = dependencies_data.get("runtime_count", 0)
        dev_deps = dependencies_data.get("dev_count", 0)
        deps_with_vulns = dependencies_data.get("with_vulnerabilities", 0)
        dep_list = dependencies_data.get("list", [])

        # Build sections
        # Links data
        analysis_id = ext.get("raw_analysis_id") or ""
        vscan_url = (
            f"https://vscan.dev/?analysisId={analysis_id}" if analysis_id else ""
        )

        # Get stats for Metadata section
        stats = ext.get("statistics", {})
        installs = stats.get("installs")
        installs_display = self._format_number(installs) if installs else "N/A"
        rating = stats.get("rating")
        rating_count = stats.get("rating_count")
        rating_display = (
            f"{rating:.1f} ({self._format_number(rating_count)} reviews)"
            if rating
            else "N/A"
        )

        marketplace_url = (
            f"https://marketplace.visualstudio.com/items?itemName={ext_id}"
            if ext_id != "unknown"
            else ""
        )

        # Build publisher display with optional domain link
        publisher_display = self._safe_escape(pub_name)

        # Add (ID) if different from name
        if pub_id and pub_id != "Unknown" and pub_id != pub_name:
            publisher_display += f" ({self._safe_escape(pub_id)})"

        # Wrap in domain link if available
        if pub_domain and pub_domain != "N/A":
            domain_clean = pub_domain
            if not domain_clean.startswith("http://") and not domain_clean.startswith(
                "https://"
            ):
                domain_url = f"https://{domain_clean}"
            else:
                domain_url = domain_clean
            publisher_display = f'<a href="{self._safe_escape(domain_url)}" target="_blank">{publisher_display}</a>'

        # Add verified badge
        if pub_verified:
            publisher_display += ' <span class="verified-badge-green" title="Verified Publisher">✓</span>'

        metadata_html = f"""
        <div class="detail-section">
            <h3>📝 Metadata</h3>
            <div class="detail-content">
                <div class="detail-item">
                    <span class="detail-label">Publisher:</span>
                    <span class="detail-value">{publisher_display}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Description:</span>
                    <span class="detail-value">{self._safe_escape(description)}</span>
                </div>
                {f'<div class="detail-item"><span class="detail-label">Homepage:</span><span class="detail-value"><a href="{self._safe_escape(homepage_url)}" target="_blank" title="{self._safe_escape(homepage_url)}">{self._safe_escape(homepage_url)}</a></span></div>' if homepage_url else ''}
                {f'<div class="detail-item"><span class="detail-label">Keywords:</span><span class="detail-value">{", ".join(self._safe_escape(k) for k in keywords if k)}</span></div>' if keywords else ''}
                {f'<div class="detail-item"><span class="detail-label">Categories:</span><span class="detail-value">{", ".join(self._safe_escape(c) for c in categories if c)}</span></div>' if categories else ''}
                <div class="detail-item">
                    <span class="detail-label">Installs:</span>
                    <span class="detail-value">{installs_display}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Rating:</span>
                    <span class="detail-value">{rating_display}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Last Updated:</span>
                    <span class="detail-value date-value" data-iso-date="{self._safe_escape(last_updated)}">{self._safe_escape(last_updated)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Installed:</span>
                    <span class="detail-value date-value" data-iso-date="{self._safe_escape(installed_at)}">{self._safe_escape(installed_at)}</span>
                </div>
                {f'<div class="detail-item"><span class="detail-label">Repository:</span><span class="detail-value"><a href="{self._safe_escape(repo_url)}" target="_blank" title="{self._safe_escape(repo_url)}">{self._safe_escape(repo_url)}</a></span></div>' if repo_url else ''}
                {f'<div class="detail-item"><span class="detail-label">Marketplace:</span><span class="detail-value"><a href="{self._safe_escape(marketplace_url)}" target="_blank" title="{self._safe_escape(marketplace_url)}">{self._safe_escape(marketplace_url)}</a></span></div>' if marketplace_url else ''}
            </div>
        </div>
        """

        # Security section
        score_html = (
            self._generate_security_gauge(score) if score is not None else "N/A"
        )

        # Module risk levels display (replacing score breakdown)
        module_risk_levels = security.get("module_risk_levels", {})
        module_risk_html = ""
        if module_risk_levels:
            module_risk_html = '<div class="module-risk-levels">'
            for module, module_risk in module_risk_levels.items():
                # Format module name (convert camelCase/snake_case to Title Case)
                formatted_name = module.replace("_", " ").replace("-", " ").title()
                risk_class = (
                    module_risk
                    if module_risk in ["low", "medium", "high", "critical"]
                    else "unknown"
                )
                module_risk_html += f"""
                <div class="module-risk-item">
                    <span class="module-risk-label">{self._safe_escape(formatted_name)}</span>
                    <span class="risk-badge risk-{risk_class}">{module_risk.upper()}</span>
                </div>
                """
            module_risk_html += "</div>"

        risk_factors_html = ""
        if risk_factors:
            risk_factors_html = '<div class="risk-factors">'
            for rf in risk_factors:
                severity = rf.get("severity", "unknown")
                rf_type = rf.get("type", "Unknown")
                rf_desc = rf.get("description", "")
                risk_factors_html += f'<div class="risk-factor risk-factor-{severity}"><span class="rf-severity">[{severity.upper()}]</span> <strong>{self._safe_escape(rf_type)}</strong><br><span class="rf-desc">{self._safe_escape(rf_desc)}</span></div>'
            risk_factors_html += "</div>"

        security_notes_html = ""
        if security_notes:
            security_notes_html = '<div class="security-notes"><ul>'
            for note in security_notes:
                security_notes_html += f"<li>{self._safe_escape(note)}</li>"
            security_notes_html += "</ul></div>"

        # Generate visualizations for the new two-column layout
        score_pie_chart = self._generate_score_pie_chart(score, risk_level)
        vuln_grid = self._generate_vulnerability_grid(vulnerabilities)

        security_html = f"""
        <div class="detail-section">
            <h3>🔒 Security Analysis</h3>

            <!-- Two-column layout for score and vulnerabilities -->
            <div class="security-viz-grid">
                <div class="security-viz-col">
                    <div class="viz-title">Security Score</div>
                    {score_pie_chart}
                    <div class="risk-badge-center">
                        <span class="risk-badge risk-{risk_level}">{risk_level.upper()} RISK</span>
                    </div>
                </div>
                <div class="security-viz-col">
                    <div class="viz-title">Vulnerabilities</div>
                    {vuln_grid}
                </div>
            </div>

            <!-- Module Risks and other details below -->
            <div class="detail-content">
                {f'<div class="detail-item"><span class="detail-label">Module Risks:</span><div class="detail-value">{module_risk_html}</div></div>' if module_risk_html else ''}
                {f'<div class="detail-item"><span class="detail-label">Risk Factors ({len(risk_factors)}):</span>{risk_factors_html}</div>' if risk_factors_html else ''}
                <div class="detail-item">
                    <span class="detail-label">Last Scanned:</span>
                    <span class="detail-value date-value" data-iso-date="{self._safe_escape(last_scanned_at)}">{self._safe_escape(last_scanned_at)}</span>
                </div>
                {f'<div class="detail-item"><span class="detail-label">Security Notes:</span>{security_notes_html}</div>' if security_notes_html else ''}
                {f'<div class="detail-item"><span class="detail-label">View on vscan.dev:</span><span class="detail-value"><a href="{self._safe_escape(vscan_url)}" target="_blank" title="{self._safe_escape(vscan_url)}">{self._safe_escape(vscan_url)}</a></span></div>' if vscan_url else ''}
            </div>
        </div>
        """

        # Dependencies section
        deps_html = ""
        if total_deps > 0:
            runtime_list_html = ""
            dev_list_html = ""

            if runtime_deps > 0 and dep_list:
                runtime_list = [d for d in dep_list if d.get("type") == "runtime"]
                runtime_list_html = '<div class="dep-list-collapsible">'
                runtime_list_html += f'<div class="dep-list-header" onclick="toggleDependencies(\'runtime-{self._safe_escape(ext_id, quote=True)}\')">'
                runtime_list_html += '<button class="dep-toggle-btn">▶</button>'
                runtime_list_html += (
                    "<strong>Runtime Dependencies ("
                    + str(len(runtime_list))
                    + ")</strong>"
                )
                runtime_list_html += "</div>"
                runtime_list_html += f'<div class="dep-list-content" id="runtime-{self._safe_escape(ext_id, quote=True)}" style="display: none;">'
                for dep in runtime_list:
                    dep_name = dep.get("name") or "Unknown"
                    dep_version = dep.get("version") or ""
                    dep_risk = dep.get("risk", "unknown")
                    dep_has_vuln = dep.get("has_vulnerabilities", False)
                    vuln_icon = " ⚠" if dep_has_vuln else ""
                    runtime_list_html += f'<div class="dep-item">• {self._safe_escape(dep_name)} v{self._safe_escape(dep_version)} <span class="dep-risk risk-{dep_risk}">{dep_risk}</span>{vuln_icon}</div>'
                runtime_list_html += "</div>"
                runtime_list_html += "</div>"

            if dev_deps > 0 and dep_list:
                dev_list = [d for d in dep_list if d.get("type") == "dev"]
                if dev_list:
                    dev_list_html = (
                        '<div class="dep-list-collapsible" style="margin-top: 15px;">'
                    )
                    dev_list_html += f'<div class="dep-list-header" onclick="toggleDependencies(\'dev-{self._safe_escape(ext_id, quote=True)}\')">'
                    dev_list_html += '<button class="dep-toggle-btn">▶</button>'
                    dev_list_html += (
                        "<strong>Dev Dependencies (" + str(len(dev_list)) + ")</strong>"
                    )
                    dev_list_html += "</div>"
                    dev_list_html += f'<div class="dep-list-content" id="dev-{self._safe_escape(ext_id, quote=True)}" style="display: none;">'
                    for dep in dev_list:
                        dep_name = dep.get("name") or "Unknown"
                        dep_version = dep.get("version") or ""
                        dep_risk = dep.get("risk", "unknown")
                        dep_has_vuln = dep.get("has_vulnerabilities", False)
                        vuln_icon = " ⚠" if dep_has_vuln else ""
                        dev_list_html += f'<div class="dep-item">• {self._safe_escape(dep_name)} v{self._safe_escape(dep_version)} <span class="dep-risk risk-{dep_risk}">{dep_risk}</span>{vuln_icon}</div>'
                    dev_list_html += "</div>"
                    dev_list_html += "</div>"

            deps_html = f"""
        <div class="detail-section">
            <h3>📦 Dependencies</h3>
            <div class="detail-content">
                <div class="detail-item">
                    <span class="detail-label">Total Dependencies:</span>
                    <span class="detail-value">{total_deps} (Runtime: {runtime_deps}, Dev: {dev_deps})</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">With Vulnerabilities:</span>
                    <span class="detail-value">{deps_with_vulns}</span>
                </div>
            </div>
            {runtime_list_html if runtime_list_html else ''}
            {dev_list_html if dev_list_html else ''}
        </div>
            """

        return f"""
        <div class="extension-details">
            <div class="detail-header">
                <h2>{self._safe_escape(name)} <span class="version-badge">v{self._safe_escape(version)}</span></h2>
            </div>
            {security_html}
            {metadata_html}
            {deps_html}
        </div>
        """

    def _generate_footer(self, summary: Dict[str, Any]) -> str:
        """Generate report footer."""
        timestamp = summary.get("scan_timestamp", "Unknown")
        return f"""
        <footer class="report-footer">
            <p>Generated by <strong>vscan</strong> v{__version__} on {self._safe_escape(timestamp)}</p>
            <p>For more information, visit <a href="https://vscan.dev" target="_blank">vscan.dev</a></p>
        </footer>
        """

    def _generate_pie_chart_svg(
        self, critical: int, high: int, medium: int, low: int
    ) -> str:
        """Generate bar chart for risk distribution."""
        total = critical + high + medium + low
        if total == 0:
            return '<div class="no-data">No data</div>'

        # Calculate percentages
        critical_pct = (critical / total) * 100
        high_pct = (high / total) * 100
        medium_pct = (medium / total) * 100
        low_pct = (low / total) * 100

        # Return simple bar chart (more readable than pie charts for this use case)
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

    def _generate_security_gauge(self, score: int, risk_level: str = "unknown") -> str:
        """Generate security score gauge (progress bar) using risk level colors."""
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

    def _generate_score_pie_chart(self, score: int, risk_level: str) -> str:
        """Generate circular pie chart for security score."""
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

    def _generate_vulnerability_grid(self, vulnerabilities: Dict[str, int]) -> str:
        """Generate colored grid visualization for vulnerabilities."""
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

    def _generate_mini_gauge(self, score: int) -> str:
        """Generate mini security score gauge."""
        if score is None:
            return "N/A"

        if score >= 75:
            color_class = "gauge-success"
        elif score >= 50:
            color_class = "gauge-warning"
        else:
            color_class = "gauge-danger"

        return f"""
        <span class="mini-gauge">
            <span class="mini-gauge-bar">
                <span class="mini-gauge-fill {color_class}" style="width: {score}%"></span>
            </span>
            <span class="mini-gauge-label">{score}</span>
        </span>
        """

    def _format_number(self, num: int) -> str:
        """Format large numbers (e.g., 187936883 -> 187M)."""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)

    def _generate_styles(self) -> str:
        """Generate embedded CSS styles."""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #212529;
            background: #f8f9fa;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Header */
        .report-header {
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        .report-header h1 {
            font-size: 28px;
            margin-bottom: 15px;
            color: #212529;
        }

        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .metadata-item {
            display: flex;
            flex-direction: column;
        }

        .metadata-item .label {
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 4px;
        }

        .metadata-item .value {
            font-size: 18px;
            font-weight: 600;
            color: #212529;
        }

        .vulnerability-count {
            color: #dc3545;
        }

        /* Charts */
        .summary-charts {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .chart-container {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }

        .chart-container h3 {
            font-size: 16px;
            margin-bottom: 15px;
            color: #495057;
            text-align: left;
        }

        /* Vulnerabilities KPI Display */
        .vulnerabilities-kpi {
            text-align: left;
        }

        .vulnerabilities-kpi h3 {
            text-align: left;
        }

        .vuln-kpi-display {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 30px 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px;
            margin: 10px 0;
        }

        .vuln-kpi-number {
            font-size: 72px;
            font-weight: 700;
            line-height: 1;
            color: #dc3545;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }

        .vuln-kpi-label {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #6c757d;
        }

        .simple-chart {
            margin: 10px 0;
        }

        .chart-bar {
            display: flex;
            height: 40px;
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid #dee2e6;
        }

        .bar-segment {
            height: 100%;
            transition: opacity 0.2s;
        }

        .bar-segment:hover {
            opacity: 0.8;
        }

        .chart-legend {
            margin-top: 15px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }

        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 8px;
        }

        .cache-stats {
            padding: 10px 0;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }

        .stat-item:last-child {
            border-bottom: none;
        }

        .stat-label {
            color: #6c757d;
        }

        .stat-value {
            font-weight: 600;
        }

        /* Controls */
        .controls {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }

        .search-filter {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            position: relative;
        }

        #search-box {
            flex: 1;
            min-width: 200px;
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
        }

        #risk-filter, #verified-filter {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
            background: white;
        }

        .btn-secondary {
            padding: 8px 16px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .btn-secondary:hover {
            background: #5a6268;
        }

        /* Column Dropdown */
        .btn-icon {
            background: #fff;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        .btn-icon:hover {
            background: #f8f9fa;
            border-color: #adb5bd;
        }

        .btn-icon svg {
            display: block;
        }

        .column-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 5px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            min-width: 200px;
            max-height: 400px;
            overflow-y: auto;
        }

        .column-dropdown-item {
            padding: 8px 12px;
            display: flex;
            align-items: center;
            cursor: pointer;
            transition: background 0.2s;
        }

        .column-dropdown-item:hover {
            background: #f8f9fa;
        }

        .column-dropdown-item input[type="checkbox"] {
            margin-right: 8px;
            cursor: pointer;
        }

        .column-dropdown-item label {
            cursor: pointer;
            flex: 1;
            user-select: none;
        }

        /* Table */
        .overview-table {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }

        thead {
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        }

        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            white-space: nowrap;
        }

        th.sortable {
            cursor: pointer;
            user-select: none;
        }

        th.sortable:hover {
            background: #e9ecef;
        }

        .sort-indicator {
            margin-left: 5px;
            color: #6c757d;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }

        .extension-row {
            transition: background-color 0.2s;
            background: #ffffff;
        }

        .extension-row:nth-child(4n+1) {
            background: #f8f9fa;
        }

        .extension-row:hover {
            background: #e9ecef;
        }

        .detail-row {
            background: #ffffff !important;
        }

        /* Verified column */
        .col-verified {
            text-align: center;
        }

        td.col-verified {
            font-size: 16px;
        }

        /* Risk badges */
        .risk-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            color: white;
        }

        .risk-critical, .risk-critical-bg {
            background-color: #8b0000;
            font-weight: 700;
        }

        .risk-high, .risk-high-bg {
            background-color: #dc3545;
        }

        .risk-medium, .risk-medium-bg {
            background-color: #fd7e14;
        }

        .risk-low, .risk-low-bg {
            background-color: #28a745;
        }

        .risk-unknown {
            background-color: #6c757d;
        }

        /* Module risk levels */
        .module-risk-levels {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
            margin-top: 10px;
        }

        .module-risk-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #dee2e6;
            transition: all 0.2s;
        }

        .module-risk-item:hover {
            background: #e9ecef;
            transform: translateX(2px);
        }

        .module-risk-label {
            font-size: 13px;
            font-weight: 500;
            color: #495057;
            flex: 1;
        }

        /* Security gauge */
        .security-gauge {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .gauge-bar {
            flex: 1;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            min-width: 100px;
        }

        .gauge-fill {
            height: 100%;
            transition: width 0.3s;
        }

        .gauge-critical {
            background: linear-gradient(90deg, #8b0000, #a31515);
        }

        .gauge-danger {
            background: linear-gradient(90deg, #dc3545, #c82333);
        }

        .gauge-warning {
            background: linear-gradient(90deg, #ffc107, #fd7e14);
        }

        .gauge-success {
            background: linear-gradient(90deg, #28a745, #20c997);
        }

        .gauge-unknown {
            background: linear-gradient(90deg, #6c757d, #868e96);
        }

        .gauge-label {
            font-size: 12px;
            font-weight: 600;
            min-width: 50px;
        }

        .mini-gauge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .mini-gauge-bar {
            width: 60px;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            display: inline-block;
        }

        .mini-gauge-fill {
            height: 100%;
            display: block;
        }

        .mini-gauge-label {
            font-size: 11px;
            font-weight: 600;
        }

        /* Security Visualization Grid */
        .security-viz-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .security-viz-col {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }

        .viz-title {
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Score Pie Chart */
        .score-pie-container {
            width: 200px;
            height: 200px;
            position: relative;
        }

        .score-pie {
            width: 100%;
            height: 100%;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }

        .score-text {
            font-size: 36px;
            font-weight: 700;
            fill: #212529;
            dominant-baseline: middle;
        }

        .score-subtext {
            font-size: 14px;
            font-weight: 400;
            fill: #6c757d;
        }

        .score-subtext-small {
            font-size: 12px;
            font-weight: 500;
            fill: #868e96;
        }

        .risk-badge-center {
            text-align: center;
            margin-top: 10px;
        }

        /* Vulnerability Grid */
        .vuln-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            width: 100%;
            max-width: 280px;
        }

        .vuln-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px 10px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            min-height: 100px;
        }

        .vuln-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .vuln-critical {
            background: linear-gradient(135deg, #8b0000 0%, #a31515 100%);
            color: white;
        }

        .vuln-high {
            background: linear-gradient(135deg, #dc3545 0%, #e35d6a 100%);
            color: white;
        }

        .vuln-moderate {
            background: linear-gradient(135deg, #fd7e14 0%, #fd9843 100%);
            color: white;
        }

        .vuln-low {
            background: linear-gradient(135deg, #28a745 0%, #48d167 100%);
            color: white;
        }

        .vuln-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.9;
            margin-bottom: 8px;
        }

        .vuln-count {
            font-size: 32px;
            font-weight: 700;
            line-height: 1;
        }

        /* Badges */
        .verified-badge {
            color: #28a745;
            font-weight: bold;
        }

        .verified-badge-green {
            color: #28a745;
            font-weight: bold;
            font-size: 14px;
        }

        .vuln-indicator {
            color: #dc3545;
            cursor: help;
        }

        .version-badge {
            font-size: 14px;
            color: #6c757d;
            font-weight: normal;
        }

        /* Name column layout */
        .name-container {
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }

        .arrow-container {
            flex-shrink: 0;
        }

        .text-container {
            flex-grow: 1;
            min-width: 0;
        }

        /* Expand button */
        .expand-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 12px;
            padding: 2px 8px;
            color: #495057;
            pointer-events: none;
        }

        .extension-row.expanded {
            background-color: #e3f2fd !important;
        }

        /* Detail view */
        .extension-details {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
        }

        .detail-header h2 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #212529;
        }

        .detail-grid-container {
            display: grid;
            grid-template-columns: 3fr 2fr;
            gap: 15px;
            margin-bottom: 25px;
        }

        .detail-section {
            margin-bottom: 25px;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        }

        .detail-grid-container .detail-section {
            margin-bottom: 0;
        }

        .detail-section h3 {
            font-size: 16px;
            margin-bottom: 15px;
            color: #495057;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 8px;
        }

        .detail-content {
            padding: 10px 0;
            display: table;
            width: 100%;
            table-layout: fixed;
            border-spacing: 0 8px;
        }

        .detail-item {
            display: table-row;
        }

        .detail-label {
            font-weight: 600;
            color: #495057;
            display: table-cell;
            width: 150px;
            padding-right: 15px;
            padding-top: 6px;
            padding-bottom: 6px;
            vertical-align: top;
            white-space: nowrap;
            line-height: 1.5;
        }

        .detail-value {
            color: #212529;
            display: table-cell;
            vertical-align: top;
            word-break: break-word;
            padding-top: 6px;
            padding-bottom: 6px;
            line-height: 1.5;
        }

        .detail-value a {
            display: inline;
            color: #007bff;
            text-decoration: none;
            line-height: 1.5;
        }

        /* For long URLs, wrap in a span with ellipsis */
        .detail-value a[title] {
            display: inline-block;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            vertical-align: top;
        }

        .detail-value a:hover {
            text-decoration: underline;
        }

        /* Score breakdown */
        .score-breakdown {
            margin-top: 15px;
        }

        .score-breakdown-item {
            margin-bottom: 15px;
        }

        .score-breakdown-label {
            font-size: 13px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 6px;
        }

        .score-breakdown-value {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .score-breakdown-bar {
            flex: 1;
            height: 24px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }

        .score-breakdown-fill {
            height: 100%;
            transition: width 0.3s;
        }

        .score-breakdown-number {
            min-width: 55px;
            font-size: 13px;
            font-weight: 600;
            text-align: right;
            color: #495057;
        }

        /* Risk factors */
        .risk-factors {
            margin-top: 10px;
        }

        .risk-factor {
            padding: 10px;
            margin: 8px 0;
            border-radius: 4px;
            border-left: 4px solid;
        }

        .risk-factor-high, .risk-factor-critical {
            background: #f8d7da;
            border-color: #dc3545;
        }

        .risk-factor-medium, .risk-factor-moderate {
            background: #fff3cd;
            border-color: #ffc107;
        }

        .risk-factor-low, .risk-factor-info {
            background: #d1ecf1;
            border-color: #17a2b8;
        }

        .rf-severity {
            font-weight: 600;
            margin-right: 5px;
        }

        .rf-desc {
            color: #6c757d;
            font-size: 13px;
        }

        /* Security notes */
        .security-notes ul {
            margin-left: 20px;
            color: #495057;
        }

        .security-notes li {
            margin: 5px 0;
        }

        /* Dependencies */
        .dep-list {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }

        .dep-list-collapsible {
            margin-top: 10px;
        }

        .dep-list-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .dep-list-header:hover {
            background: #e9ecef;
        }

        .dep-toggle-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 12px;
            padding: 0;
            color: #495057;
            pointer-events: none;
            flex-shrink: 0;
        }

        .dep-list-content {
            padding: 10px;
            padding-left: 30px;
            background: #f8f9fa;
            border-radius: 0 0 4px 4px;
            margin-top: 2px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }

        .dep-item {
            padding: 4px 0;
        }

        .dep-risk {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            margin-left: 8px;
            color: white;
        }

        .show-more-btn {
            margin-top: 10px;
            padding: 6px 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }

        .show-more-btn:hover {
            background: #0056b3;
        }

        /* Footer */
        .report-footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #dee2e6;
            text-align: center;
            color: #6c757d;
        }

        .report-footer p {
            margin: 5px 0;
        }

        .report-footer a {
            color: #007bff;
            text-decoration: none;
        }

        .report-footer a:hover {
            text-decoration: underline;
        }

        /* Print styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }

            .container {
                box-shadow: none;
                max-width: 100%;
            }

            .controls {
                display: none;
            }

            .expand-btn {
                display: none;
            }

            .detail-row {
                display: table-row !important;
            }

            .extension-row {
                page-break-inside: avoid;
            }

            .detail-row {
                page-break-inside: avoid;
            }

            .risk-high {
                border: 2px solid #000;
                color: #000;
                background: #fff;
            }

            .risk-medium {
                border: 1px solid #000;
                color: #000;
                background: #fff;
            }

            .risk-low {
                border: 1px dashed #000;
                color: #000;
                background: #fff;
            }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            table {
                font-size: 12px;
            }

            th, td {
                padding: 8px;
            }
        }
    </style>
        """

    def _generate_scripts(self) -> str:
        """Generate embedded JavaScript for interactivity."""
        return """
    <script>
        let currentSort = { column: null, direction: 'asc' };

        // Toggle extension details
        function toggleDetails(extId, rowElement) {
            const detailRow = document.getElementById('detail-' + extId);
            if (!detailRow) {
                console.error('Detail row not found for:', extId);
                return;
            }

            const allDetailRows = document.querySelectorAll('.detail-row');
            const allExtensionRows = document.querySelectorAll('.extension-row');
            const allExpandBtns = document.querySelectorAll('.expand-btn');

            const isCurrentlyOpen = detailRow.style.display === 'table-row';

            // Close all detail rows and remove highlighting
            allDetailRows.forEach(row => {
                row.style.display = 'none';
            });

            allExtensionRows.forEach(row => {
                row.classList.remove('expanded');
            });

            // Reset all expand buttons
            allExpandBtns.forEach(btn => {
                btn.textContent = '▶';
            });

            // If it wasn't open, open it now
            if (!isCurrentlyOpen) {
                detailRow.style.display = 'table-row';
                if (rowElement) {
                    rowElement.classList.add('expanded');
                    const expandBtn = rowElement.querySelector('.expand-btn');
                    if (expandBtn) {
                        expandBtn.textContent = '▼';
                    }
                }
            }
        }

        // Toggle dependencies list
        function toggleDependencies(depId) {
            const depContent = document.getElementById(depId);
            if (!depContent) {
                console.error('Dependencies content not found for:', depId);
                return;
            }

            const header = depContent.previousElementSibling;
            const toggleBtn = header.querySelector('.dep-toggle-btn');

            if (depContent.style.display === 'none') {
                depContent.style.display = 'block';
                if (toggleBtn) {
                    toggleBtn.textContent = '▼';
                }
            } else {
                depContent.style.display = 'none';
                if (toggleBtn) {
                    toggleBtn.textContent = '▶';
                }
            }
        }

        // Search extensions (search in name, publisher name, and publisher ID)
        function searchExtensions() {
            const query = document.getElementById('search-box').value.toLowerCase();
            const rows = document.querySelectorAll('.extension-row');

            rows.forEach(row => {
                const name = (row.dataset.name || '').toLowerCase();
                const publisherName = (row.dataset.publisherName || '').toLowerCase();
                const publisherId = (row.dataset.publisherId || '').toLowerCase();

                if (name.includes(query) || publisherName.includes(query) || publisherId.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                    // Hide detail row too
                    const nextRow = row.nextElementSibling;
                    if (nextRow && nextRow.classList.contains('detail-row')) {
                        nextRow.style.display = 'none';
                    }
                }
            });
        }

        // Filter by risk level
        function filterByRisk() {
            const filter = document.getElementById('risk-filter').value;
            const rows = document.querySelectorAll('.extension-row');

            rows.forEach(row => {
                const risk = row.dataset.risk || '';
                if (filter === 'all' || risk === filter) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                    // Hide detail row too
                    const nextRow = row.nextElementSibling;
                    if (nextRow && nextRow.classList.contains('detail-row')) {
                        nextRow.style.display = 'none';
                    }
                }
            });
        }

        // Filter by verified status
        function filterByVerified() {
            const filter = document.getElementById('verified-filter').value;
            const rows = document.querySelectorAll('.extension-row');

            rows.forEach(row => {
                const verified = row.dataset.verified === 'true';
                if (filter === 'all' ||
                    (filter === 'verified' && verified) ||
                    (filter === 'unverified' && !verified)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                    // Hide detail row too
                    const nextRow = row.nextElementSibling;
                    if (nextRow && nextRow.classList.contains('detail-row')) {
                        nextRow.style.display = 'none';
                    }
                }
            });
        }

        // Toggle column dropdown
        function toggleColumnDropdown() {
            const dropdown = document.getElementById('column-dropdown');
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('column-dropdown');
            const button = event.target.closest('.btn-icon');
            if (!button && !dropdown.contains(event.target)) {
                dropdown.style.display = 'none';
            }
        });

        // Clear all filters
        function clearFilters() {
            document.getElementById('search-box').value = '';
            document.getElementById('risk-filter').value = 'all';
            document.getElementById('verified-filter').value = 'all';

            const rows = document.querySelectorAll('.extension-row');
            rows.forEach(row => {
                row.style.display = '';
            });
        }

        // Toggle column visibility
        function toggleColumn(column) {
            const header = document.querySelector('.col-' + column);
            const cells = document.querySelectorAll('.col-' + column);

            cells.forEach(cell => {
                if (cell.style.display === 'none') {
                    cell.style.display = '';
                } else {
                    cell.style.display = 'none';
                }
            });
        }

        // Sort table
        function sortTable(column) {
            const table = document.getElementById('extensions-table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('.extension-row'));

            // Build a map of extension rows to their detail rows BEFORE sorting
            const detailRowMap = new Map();
            rows.forEach(row => {
                const nextSibling = row.nextElementSibling;
                if (nextSibling && nextSibling.classList.contains('detail-row')) {
                    detailRowMap.set(row, nextSibling);
                }
            });

            // Determine sort direction
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'asc';
            }

            // Update sort indicators
            document.querySelectorAll('.sort-indicator').forEach(indicator => {
                indicator.textContent = '';
            });

            const currentHeader = document.querySelector('.col-' + column + ' .sort-indicator');
            if (currentHeader) {
                currentHeader.textContent = currentSort.direction === 'asc' ? '▲' : '▼';
            }

            // Sort rows
            rows.sort((a, b) => {
                let aVal, bVal;

                switch(column) {
                    case 'name':
                        aVal = a.dataset.name || '';
                        bVal = b.dataset.name || '';
                        break;
                    case 'risk':
                        const riskOrder = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'unknown': 0 };
                        aVal = riskOrder[a.dataset.risk] || 0;
                        bVal = riskOrder[b.dataset.risk] || 0;
                        break;
                    case 'score':
                        aVal = parseFloat(a.querySelector('.gauge-label')?.textContent) || 0;
                        bVal = parseFloat(b.querySelector('.gauge-label')?.textContent) || 0;
                        break;
                    case 'vulnerabilities':
                        aVal = parseInt(a.querySelector('.col-vulnerabilities')?.textContent) || 0;
                        bVal = parseInt(b.querySelector('.col-vulnerabilities')?.textContent) || 0;
                        break;
                    case 'version':
                        aVal = a.querySelector('.col-version')?.textContent || '';
                        bVal = b.querySelector('.col-version')?.textContent || '';
                        break;
                    case 'publisher':
                        aVal = a.querySelector('.col-publisher')?.textContent || '';
                        bVal = b.querySelector('.col-publisher')?.textContent || '';
                        break;
                    case 'verified':
                        aVal = a.querySelector('.col-verified')?.textContent || '';
                        bVal = b.querySelector('.col-verified')?.textContent || '';
                        // ✓ comes before ✗ in ascending order
                        aVal = aVal === '✓' ? 1 : 0;
                        bVal = bVal === '✓' ? 1 : 0;
                        break;
                    case 'installs':
                        aVal = a.querySelector('.col-installs')?.textContent || '0';
                        bVal = b.querySelector('.col-installs')?.textContent || '0';
                        // Convert formatted numbers back
                        aVal = parseFormattedNumber(aVal);
                        bVal = parseFormattedNumber(bVal);
                        break;
                    case 'rating':
                        aVal = parseFloat(a.querySelector('.col-rating')?.textContent) || 0;
                        bVal = parseFloat(b.querySelector('.col-rating')?.textContent) || 0;
                        break;
                    case 'dependencies':
                        aVal = parseInt(a.querySelector('.col-dependencies')?.textContent) || 0;
                        bVal = parseInt(b.querySelector('.col-dependencies')?.textContent) || 0;
                        break;
                    case 'last-updated':
                    case 'installed':
                    case 'last-scanned':
                        // Get ISO date from data attribute (not formatted text)
                        const aDateEl = a.querySelector(`.col-${column} .date-value`);
                        const bDateEl = b.querySelector(`.col-${column} .date-value`);
                        const aDate = aDateEl?.getAttribute('data-iso-date');
                        const bDate = bDateEl?.getAttribute('data-iso-date');

                        // Handle N/A or missing dates (sort to end)
                        if (!aDate || aDate === 'N/A') {
                            aVal = 0;
                        } else {
                            try {
                                aVal = new Date(aDate).getTime();
                            } catch {
                                aVal = 0;
                            }
                        }

                        if (!bDate || bDate === 'N/A') {
                            bVal = 0;
                        } else {
                            try {
                                bVal = new Date(bDate).getTime();
                            } catch {
                                bVal = 0;
                            }
                        }
                        break;
                    default:
                        return 0;
                }

                if (typeof aVal === 'string') {
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }

                if (currentSort.direction === 'asc') {
                    return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                } else {
                    return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
                }
            });

            // Re-append rows with their detail rows using the map
            rows.forEach(row => {
                tbody.appendChild(row);
                const detailRow = detailRowMap.get(row);
                if (detailRow) {
                    tbody.appendChild(detailRow);
                }
            });
        }

        // Helper function to parse formatted numbers
        function parseFormattedNumber(str) {
            if (str === 'N/A') return 0;
            str = str.trim();
            const multiplier = str.slice(-1);
            const num = parseFloat(str);

            switch(multiplier) {
                case 'B': return num * 1000000000;
                case 'M': return num * 1000000;
                case 'K': return num * 1000;
                default: return num || 0;
            }
        }

        // Show more dependencies
        function showMoreDeps(extId, type) {
            // This is a placeholder - in a real implementation, you'd load more data
            alert('Show more dependencies feature - would load additional ' + type + ' dependencies for ' + extId);
        }

        // Format all dates to locale-specific human-friendly format
        function formatDates() {
            const dateElements = document.querySelectorAll('.date-value');
            dateElements.forEach(element => {
                const isoDate = element.getAttribute('data-iso-date');
                if (isoDate && isoDate !== 'N/A' && isoDate !== 'Unknown') {
                    try {
                        const date = new Date(isoDate);
                        if (!isNaN(date.getTime())) {
                            // Format: "Jan 15, 2025, 3:30 PM" or similar based on locale
                            const formatted = date.toLocaleString(undefined, {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                            element.textContent = formatted;
                        }
                    } catch (e) {
                        // Keep original text if parsing fails
                    }
                }
            });
        }

        // Initial sort by risk level (high to low)
        window.addEventListener('DOMContentLoaded', function() {
            formatDates();
            sortTable('risk');
            sortTable('risk'); // Sort twice to get descending order
        });
    </script>
        """


def main():
    """Test the HTML report generator."""
    import json

    # Load test data
    test_data = {
        "version": "2.0",
        "mode": "detailed",
        "summary": {
            "total_extensions_scanned": 3,
            "successful_scans": 3,
            "failed_scans": 0,
            "vulnerabilities_found": 0,
            "high_risk_extensions": 1,
            "medium_risk_extensions": 2,
            "low_risk_extensions": 0,
            "scan_timestamp": "2025-10-23T14:30:00Z",
            "scan_duration_seconds": 45.2,
            "cache_statistics": {
                "from_cache": 2,
                "fresh_scans": 1,
                "cache_hit_rate": 66.7,
            },
        },
        "extensions": [
            {
                "id": "ms-python.python",
                "name": "python",
                "display_name": "Python",
                "version": "2025.16.0",
                "publisher": {
                    "id": "ms-python",
                    "name": "Microsoft",
                    "verified": True,
                    "domain": "microsoft.com",
                },
                "description": "Python language support with IntelliSense, debugging, linting, and more.",
                "repository_url": "https://github.com/Microsoft/vscode-python",
                "license": "MIT",
                "last_updated": "2025-10-15",
                "statistics": {
                    "installs": 187936883,
                    "rating": 4.19,
                    "rating_count": 618,
                },
                "scan_status": "success",
                "security": {
                    "score": 82,
                    "risk_level": "high",
                    "vulnerabilities": {
                        "total": 0,
                        "critical": 0,
                        "high": 0,
                        "moderate": 0,
                        "low": 0,
                        "info": 0,
                    },
                    "risk_factors_count": 2,
                    "dependencies_count": 45,
                    "dependencies_with_vulnerabilities": 0,
                    "score_contributions": {
                        "code_quality": 85,
                        "dependencies": 90,
                        "permissions": 75,
                        "network": 80,
                    },
                    "risk_factors": [
                        {
                            "type": "network-access",
                            "severity": "medium",
                            "description": "Extension makes network requests",
                        },
                        {
                            "type": "missing-privacy-policy",
                            "severity": "low",
                            "description": "No privacy policy link found",
                        },
                    ],
                    "dependencies": {
                        "total_count": 45,
                        "runtime_count": 21,
                        "dev_count": 24,
                        "with_vulnerabilities": 0,
                        "list": [
                            {
                                "name": "vscode-languageclient",
                                "version": "8.1.0",
                                "type": "runtime",
                                "risk_level": "low",
                                "has_vulnerabilities": False,
                            },
                            {
                                "name": "@types/node",
                                "version": "18.0.0",
                                "type": "runtime",
                                "risk_level": "low",
                                "has_vulnerabilities": False,
                            },
                        ],
                    },
                },
                "vscan_url": "https://vscan.dev/extension/ms-python.python",
                "keywords": ["python", "intellisense", "linting"],
            }
        ],
    }

    generator = HTMLReportGenerator()
    html_output = generator.generate_report(test_data)

    # Write to file
    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    print("HTML report generated: test_report.html")


if __name__ == "__main__":
    main()
