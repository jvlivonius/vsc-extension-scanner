# HTML Report Testing

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Feature:** v2.2+ (Self-contained interactive HTML reports)

---

## Overview

Tests HTML report generation with embedded CSS/JavaScript, charts, and interactivity.

---

## Key Tests

### HTML Structure
```python
def test_html_structure():
    """Generated HTML has required structure."""
    html = generate_html_report(sample_data)

    assert '<!DOCTYPE html>' in html
    assert '<style>' in html  # Embedded CSS
    assert '<script>' in html  # Embedded JavaScript
    assert 'sortTable' in html  # Interactivity
```

### Charts
```python
def test_pie_chart_svg():
    """Pie chart SVG generated correctly."""
    svg = generate_pie_chart(high=10, medium=20, low=30)

    assert '<svg' in svg
    assert '<path' in svg  # Chart segments
```

### Browser Compatibility
- Chrome ✅
- Firefox ✅
- Safari ✅
- Edge ✅

---

## See Full Guide

**Location:** Original [TESTING.md](../TESTING.md) section "HTML Report Testing (v2.2+)" (lines 2208-2406)

---

**Document Version:** 1.0 (Summary)
**Last Updated:** 2025-10-30
