# MCP Server Reference

Quick reference for MCP server availability and usage patterns.

## Available Servers (If Configured)

**serena** - Semantic code understanding, symbol operations, project memory
**context7** - Official library documentation lookup
**sequential-thinking** - Multi-step reasoning, complex analysis, systematic problem-solving
**playwright** - Browser automation, visual validation, accessibility testing

## Usage Guidelines

**IMPORTANT**: The `.claude/mcp/` files describe WHEN to use each MCP server's tools, not how to load the servers. MCP servers configured via `claude mcp add` are always loaded at startup.

**Available Guidelines**:
- @mcp/Serena.md - Symbol operations, project memory, session persistence
- @mcp/Context7.md - Official library documentation lookup
- @mcp/Sequential.md - Complex analysis, multi-step reasoning
- @mcp/MCP_Playwright.md - Browser automation, visual validation, accessibility

**Each file contains**:
- **Triggers**: Scenarios where the MCP's tools are most useful
- **Choose When**: Decision guidelines for tool selection
- **Works Best With**: Tool combination recommendations

## User Flags (Optional Semantic Hints)

You can include these flags in your requests as hints for Claude's tool selection:

- `--serena` - Hint: prefer Serena tools for this task
- `--c7` or `--context7` - Hint: prefer Context7 for library documentation
- `--seq` or `--sequential` - Hint: prefer sequential-thinking for analysis
- `--playwright` or `--pw` - Hint: prefer Playwright for HTML report testing
