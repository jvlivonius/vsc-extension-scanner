"""
Detail View Component for HTML Report.

Generates detailed extension information including security analysis,
metadata, and dependencies.
"""

from typing import Dict, Any
from ..base_component import BaseComponent


class DetailViewComponent(BaseComponent):
    """Component for generating detailed extension information."""

    def __init__(self):
        """Initialize with chart components for visualizations."""
        super().__init__()
        # Import here to avoid circular dependency
        from .charts import ChartComponents

        self.charts = ChartComponents()

    def render(self, ext: Dict[str, Any]) -> str:
        """
        Generate detailed extension information panel.

        Args:
            ext: Extension data dictionary

        Returns:
            HTML string for detailed extension view
        """
        # Extract basic info
        ext_id = ext.get("id", "unknown")
        name = ext.get("display_name") or ext.get("name", "Unknown")
        version = ext.get("version", "unknown")
        description = ext.get("description") or "No description available"

        # Build all sections
        security_html = self._render_security_section(ext)
        metadata_html = self._render_metadata_section(ext)
        deps_html = self._render_dependencies_section(ext)

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

    def _render_metadata_section(self, ext: Dict[str, Any]) -> str:
        """Render metadata section."""
        ext_id = ext.get("id", "unknown")
        description = ext.get("description") or "No description available"
        license_text = ext.get("license") or "N/A"
        repo_url = ext.get("repository_url") or ""
        homepage_url = ext.get("homepage_url") or ""
        keywords = ext.get("keywords") or []
        categories = ext.get("categories") or []
        last_updated = ext.get("last_updated") or "N/A"
        installed_at = ext.get("installed_at") or "N/A"

        # Publisher info
        publisher = ext.get("publisher", {})
        pub_name = publisher.get("name") or "Unknown"
        pub_id = publisher.get("id") or "Unknown"
        pub_verified = publisher.get("verified", False)
        pub_domain = publisher.get("domain") or "N/A"

        # Stats
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

        # Build publisher display
        publisher_display = self._safe_escape(pub_name)
        if pub_id and pub_id != "Unknown" and pub_id != pub_name:
            publisher_display += f" ({self._safe_escape(pub_id)})"

        if pub_domain and pub_domain != "N/A":
            domain_clean = pub_domain
            if not domain_clean.startswith("http://") and not domain_clean.startswith(
                "https://"
            ):
                domain_url = f"https://{domain_clean}"
            else:
                domain_url = domain_clean
            publisher_display = f'<a href="{self._safe_escape(domain_url)}" target="_blank">{publisher_display}</a>'

        if pub_verified:
            publisher_display += ' <span class="verified-badge-green" title="Verified Publisher">✓</span>'

        return f"""
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

    def _render_security_section(self, ext: Dict[str, Any]) -> str:
        """Render security analysis section."""
        security = ext.get("security", {})
        score = security.get("score")
        risk_level = security.get("risk_level", "unknown")
        risk_factors = security.get("risk_factors", [])
        security_notes = security.get("security_notes", [])
        vulnerabilities = security.get("vulnerabilities", {})
        last_scanned_at = ext.get("last_scanned_at") or "N/A"

        # Links
        analysis_id = ext.get("raw_analysis_id") or ""
        vscan_url = (
            f"https://vscan.dev/?analysisId={analysis_id}" if analysis_id else ""
        )

        # Module risk levels
        module_risk_levels = security.get("module_risk_levels", {})
        module_risk_html = ""
        if module_risk_levels:
            module_risk_html = '<div class="module-risk-levels">'
            for module, module_risk in module_risk_levels.items():
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

        # Risk factors
        risk_factors_html = ""
        if risk_factors:
            risk_factors_html = '<div class="risk-factors">'
            for rf in risk_factors:
                severity = rf.get("severity", "unknown")
                rf_type = rf.get("type", "Unknown")
                rf_desc = rf.get("description", "")
                risk_factors_html += f'<div class="risk-factor risk-factor-{severity}"><span class="rf-severity">[{severity.upper()}]</span> <strong>{self._safe_escape(rf_type)}</strong><br><span class="rf-desc">{self._safe_escape(rf_desc)}</span></div>'
            risk_factors_html += "</div>"

        # Security notes
        security_notes_html = ""
        if security_notes:
            security_notes_html = '<div class="security-notes"><ul>'
            for note in security_notes:
                security_notes_html += f"<li>{self._safe_escape(note)}</li>"
            security_notes_html += "</ul></div>"

        # Generate visualizations
        score_pie_chart = self.charts.render_score_pie_chart(score, risk_level)
        vuln_grid = self.charts.render_vulnerability_grid(vulnerabilities)

        return f"""
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

    def _render_dependencies_section(self, ext: Dict[str, Any]) -> str:
        """Render dependencies section."""
        ext_id = ext.get("id", "unknown")
        security = ext.get("security", {})
        dependencies_data = security.get("dependencies", {})
        total_deps = dependencies_data.get("total_count", 0)
        runtime_deps = dependencies_data.get("runtime_count", 0)
        dev_deps = dependencies_data.get("dev_count", 0)
        deps_with_vulns = dependencies_data.get("with_vulnerabilities", 0)
        dep_list = dependencies_data.get("list", [])

        if total_deps == 0:
            return ""

        runtime_list_html = ""
        dev_list_html = ""

        if runtime_deps > 0 and dep_list:
            runtime_list = [d for d in dep_list if d.get("type") == "runtime"]
            runtime_list_html = '<div class="dep-list-collapsible">'
            runtime_list_html += f'<div class="dep-list-header" onclick="toggleDependencies(\'runtime-{self._safe_escape(ext_id, quote=True)}\')">'
            runtime_list_html += '<button class="dep-toggle-btn">▶</button>'
            runtime_list_html += (
                f"<strong>Runtime Dependencies ({len(runtime_list)})</strong>"
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
                dev_list_html += f"<strong>Dev Dependencies ({len(dev_list)})</strong>"
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

        return f"""
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
