# HTML Reports Guide

**Purpose:** Architecture and usage of self-contained interactive HTML reports
**Document Type:** Timeless Reference
**Feature:** v2.2+
**Module:** `html_report_generator.py`

---

## Overview

The HTML report generator creates self-contained, interactive security reports that work offline without external dependencies. Each report is a single HTML file containing embedded CSS, JavaScript, and data visualizations.

**Key Features:**
- Self-contained (no CDN dependencies)
- Interactive (sortable tables, expandable details, search)
- Offline-capable (works in air-gapped environments)
- Print-optimized (compliance documentation)
- Lightweight (vanilla JS, no frameworks)

---

## Usage

### Generate HTML Report

```bash
# Scan and generate HTML report
vscan scan --output report.html

# From cached results (no API calls)
vscan report --cache --output report.html

# With filtering
vscan scan --min-risk-level high --output high-risk.html
```

### Report Structure

**Sections:**
1. **Summary Header** - Total extensions, risk distribution pie chart
2. **Overview Table** - Sortable, filterable extension list with key metrics
3. **Detail Views** - Expandable rows with full security findings
4. **Footer** - Scan metadata, vscan.dev attribution

**Interactive Features:**
- **Sort** - Click column headers to sort by name, publisher, risk level, etc.
- **Search** - Filter extensions by name or publisher
- **Expand** - Click rows to view detailed security findings
- **Print** - Auto-expands all details for complete report

---

## Architecture

### Self-Contained Design

**Zero External Dependencies:**
- All CSS embedded in `<style>` tags (~300 lines)
- All JavaScript embedded in `<script>` tags (~200 lines)
- No CDN dependencies (Chart.js, Bootstrap, jQuery)
- Works offline and in any environment
- Single HTML file contains complete report

**Security Benefits:**
- No CDN compromise risk
- No external network requests
- Safe for air-gapped environments
- Compliant with strict security policies

### Embedded Assets

**CSS Strategy:**
```python
def _generate_styles(self) -> str:
    """Generate embedded CSS (no external stylesheets)."""
    # Includes: Layout, tables, charts, print media queries
    # Works in all modern browsers (Chrome, Firefox, Safari, Edge)
```

**JavaScript Strategy:**
```python
def _generate_scripts(self) -> str:
    """Generate embedded JavaScript (no external libraries)."""
    # Functions: Table sorting, filtering, row expansion, search
    # Pure vanilla JavaScript, no jQuery or frameworks
```

### Data Visualizations

**Pie Charts** - SVG `<path>` elements (no Chart.js):
- Risk distribution (high/medium/low)
- Pure SVG with calculated path data
- Lightweight and fast

**Bar Charts** - CSS-styled `<div>` elements:
- Colored bars with width percentages
- No external charting library

**Security Gauges** - Horizontal progress bars:
- Color gradients (red→yellow→green)
- CSS-based, no images

---

## Performance Optimizations

### 1. Collapsible Dependency Lists
```python
# Show first 10 dependencies by default
# "Show X more..." button to expand
# Reduces initial DOM size for large reports (100+ extensions)
```

### 2. Lazy Rendering
```python
# Detail sections use display: none when collapsed
# Only visible when user expands row
# Minimizes initial rendering time
```

### 3. Efficient DOM
```python
# Minimize DOM nodes
# Simple CSS selectors (no complex queries)
# Reuse elements where possible
```

**Performance Target:** <1 second rendering for 100+ extension reports

---

## Print Optimization

**Print-Friendly CSS:**
```css
@media print {
  /* Auto-expand all rows for complete report */
  .extension-details { display: block !important; }

  /* Remove interactive controls */
  .controls, .expand-button { display: none; }

  /* Prevent page breaks in extension details */
  .extension-row { page-break-inside: avoid; }

  /* Black & white friendly colors */
  .risk-high { border: 2px solid #000; }
}
```

**Use Cases:**
- Compliance documentation
- Audit trail records
- Offline review and sharing
- Long-term archival

---

## Browser Compatibility

**Supported Browsers:**
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Features Used:**
- CSS Grid (layout)
- CSS Flexbox (alignment)
- SVG (charts)
- Vanilla JavaScript ES6+ (interactivity)

**Fallbacks:**
- Graceful degradation for older browsers
- Core content readable without JavaScript
- Print works even if JS disabled

---

## Design Decisions

**Why Self-Contained?**
- Easy sharing (single file attachment)
- Works in restricted environments (no internet access)
- Reduces security risks (no CDN compromise)
- Simplifies archival (complete snapshot in one file)

**Why No Frameworks?**
- Reduces file size (no large library downloads)
- Faster rendering (no framework overhead)
- Simpler maintenance (less dependency updates)
- Better offline support (no external dependencies)

**Why Embedded Assets?**
- Offline functionality (works without network)
- Security (no external requests to track)
- Portability (single file contains everything)
- Reliability (no CDN outages or changes)

---

## Implementation Reference

**Module:** `vscode_scanner/html_report_generator.py`
**Lines of Code:** Run `wc -l vscode_scanner/html_report_generator.py` for current count (baseline: ~2,300)

**Key Functions:**
- `generate_report()` - Main HTML generation entry point
- `_generate_header()` - Summary section with charts
- `_generate_overview_table()` - Sortable extension table
- `_generate_detail_view()` - Expandable security findings
- `_generate_pie_chart_svg()` - SVG risk distribution chart
- `_generate_styles()` - Embedded CSS
- `_generate_scripts()` - Embedded JavaScript

---

## Testing

**Test Coverage:**
- HTML structure validation (DOCTYPE, required tags)
- Embedded CSS presence (no external stylesheets)
- Embedded JavaScript presence (no external scripts)
- Chart SVG generation (valid path data)
- Table sorting functionality
- Browser compatibility (manual testing)

**Test Files:**
- Core tests covered in `tests/test_output_formatter.py`
- See [TESTING.md](TESTING.md) for complete testing patterns

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Overall system architecture (3-layer design)
- **[output_formatter.py](ARCHITECTURE.md#output_formatterpy-infrastructure)** - JSON/CSV output formats
- **[API_REFERENCE.md](API_REFERENCE.md)** - vscan.dev API data structure

---
