"""
Controls Component for HTML Report.

Generates filter controls, search box, and column visibility toggles.
"""

from ..base_component import BaseComponent


class ControlsComponent(BaseComponent):
    """Component for generating filter controls and search functionality."""

    def render(self) -> str:
        """
        Render filter controls, search box, and column visibility options.

        Returns:
            HTML string for controls section
        """
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
