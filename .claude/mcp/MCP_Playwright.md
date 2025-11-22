# Playwright MCP Server

Browser automation for HTML report testing and accessibility validation

## Triggers

- HTML report testing and visual regression validation
- Interactive HTML feature testing (collapsible sections, filtering, sorting)
- Accessibility testing with automated WCAG compliance for generated reports
- Cross-browser HTML rendering validation (Chrome, Firefox, Safari)
- Screenshot comparison for HTML template changes
- E2E testing scenarios requiring real browser interaction

## Choose When

- **For HTML report validation**: When you need to test generated HTML reports in real browsers
- **Over pytest**: For browser-based testing, visual validation (use pytest for Python unit/integration tests)
- **For accessibility testing**: Automated WCAG compliance validation of HTML output
- **For visual regression**: Screenshot comparisons when HTML report templates change
- **For interactive features**: Testing collapsible sections, JavaScript interactions in HTML reports
- **Not for Python code**: Use pytest for Python unit/integration tests, not Playwright

## Works Best With

- **sequential-thinking**: Sequential plans test strategy → Playwright executes browser automation
- **Context7**: Context7 provides pytest patterns → Playwright handles browser-specific testing
- **quality-engineer agent**: Quality engineer defines testing strategy → Playwright validates HTML reports

## Examples

```text
"test HTML report rendering" → Playwright (browser validation)
"validate report accessibility" → Playwright (automated WCAG testing)
"screenshot HTML output changes" → Playwright (visual regression)
"test collapsible sections in report" → Playwright (interactive feature testing)
"visual regression test for HTML templates" → Playwright (screenshot comparison)
"test Python scanner logic" → pytest (Python unit testing, NOT Playwright)
"run integration tests" → pytest (Python integration testing, NOT Playwright)
```
