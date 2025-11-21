# MCP Server Reference

Quick reference for MCP server availability and usage patterns.

## Available Servers (If Configured)

**serena** - Semantic code understanding, symbol operations, project memory
**context7** - Official library documentation (pytest, typer, hypothesis, rich)
**sequential-thinking** - Multi-step reasoning, complex analysis, systematic problem-solving
**playwright** - Browser automation for HTML report testing and accessibility validation

## Usage Guidelines

The `.claude/mcp/` directory contains **usage guidelines** (not configuration files) that help Claude decide WHEN to use each MCP server's tools:

- @mcp/Serena.md - When to use Serena tools (symbol operations, large projects)
- @mcp/Context7.md - When to use Context7 (library docs, official patterns)
- @mcp/Sequential.md - When to use sequential-thinking (complex analysis, debugging)
- @mcp/MCP_Playwright.md - When to use Playwright (HTML report testing, accessibility)

These files contain:
- **Triggers**: Scenarios where the MCP's tools are most useful
- **Choose When**: Decision guidelines for tool selection
- **Examples**: Common use cases and patterns

## User Flags (Optional Semantic Hints)

You can include these flags in your requests as hints for Claude's tool selection:

- `--serena` - Hint: prefer Serena tools for this task
- `--c7` or `--context7` - Hint: prefer Context7 for library documentation
- `--seq` or `--sequential` - Hint: prefer sequential-thinking for analysis
- `--playwright` or `--pw` - Hint: prefer Playwright for HTML report testing
