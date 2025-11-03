# SuperClaude Framework Archive

This directory contains SuperClaude framework components that are **not applicable** to the vscode_scanner project but may be useful for future projects or reference.

## Why These Components Are Archived

**vscode_scanner is:**
- Python CLI tool for security scanning
- Backend-only (no web UI, no browser automation)
- Single API source (vscan.dev with documented endpoints)
- Technical tool (not business strategy consulting)

**Therefore, these components are unnecessary:**
- Business analysis tools (strategic consulting)
- Frontend/UI generation tools (web development)
- Browser automation tools (E2E testing for web apps)
- Multi-source research tools (offline scanning tool)

## Archive Organization

### business/
Business Panel Analysis Mode - Multi-expert business strategy analysis
- **Files:** BUSINESS_PANEL_EXAMPLES.md, BUSINESS_SYMBOLS.md, MODE_Business_Panel.md
- **Why archived:** CLI security tool, not business strategy consulting
- **When useful:** Strategic planning, market analysis, organizational decisions

### frontend/
Frontend Development MCP Servers
- **Files:** MCP_Magic.md (UI components), MCP_Playwright.md (browser automation)
- **Why archived:** Backend Python CLI with Rich terminal output, not web UI
- **When useful:** React/Vue/Angular projects, E2E browser testing

### research/
Deep Research Mode with Multi-Source Investigation
- **Files:** MODE_DeepResearch.md, MCP_Tavily.md
- **Why archived:** Single documented API source, no web scraping needed
- **When useful:** Multi-source research, academic investigations, competitive analysis

### mcp/
Additional MCP Servers Not Needed for Python CLI
- **Files:** MCP_Morphllm.md (bulk pattern edits), infrastructure sections
- **Why archived:** Serena handles symbol operations better for this project
- **When useful:** Large-scale pattern-based refactoring, infrastructure automation

## Retrieving Archived Content

To reactivate archived components:
1. Move file from `archive/[category]/` back to `.claude/`
2. Update `.claude/CLAUDE.md` imports to include the file
3. Restart Claude Code to reload context

## Token Savings

- **Before:** ~40,000 tokens (SuperClaude framework)
- **After:** ~10,000 tokens (project-relevant components only)
- **Savings:** ~30,000 tokens (75% reduction)
- **Result:** +31,000 tokens available workspace (+21% capacity)
