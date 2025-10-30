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
