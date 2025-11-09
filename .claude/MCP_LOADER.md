# MCP Server Reference

Quick reference for MCP server availability and usage patterns.

## How MCP Loading Actually Works

**IMPORTANT**: MCP servers are configured at the system level and **automatically load at Claude Code startup**. Once configured, all MCP servers and their tools are **always present** in every conversation.

### Configuration (System Level)

MCP servers are managed via CLI commands:
- `claude mcp add <name>` - Add/configure a server (persists across sessions)
- `claude mcp remove <name>` - Remove a server configuration
- `claude mcp list` - View configured servers
- `/mcp` (in chat) - Check server connection status

Servers can be configured at three scopes:
- **Local**: Project-specific user settings (default)
- **Project**: Shared via `.mcp.json` (version controlled)
- **User**: Cross-project personal configurations

### Loading Behavior

- **Always Loaded**: All configured MCP servers load automatically at startup
- **Always Available**: All tools from configured servers are present in every conversation
- **Token Cost**: Each MCP server adds tools to the context (~20k tokens for 3 servers)
- **No Conditional Loading**: There is no dynamic loading based on keywords, flags, or context

### Managing Token Usage

To reduce context usage:
- **Remove unused servers**: `claude mcp remove <name>` for servers you don't need
- **Project-specific configs**: Use project scope to load different servers per project
- **Minimal configuration**: Only configure MCP servers you regularly use

## Available Servers (If Configured)

**serena** - Semantic code understanding, symbol operations, project memory
**context7** - Official library documentation (pytest, typer, hypothesis, rich)
**sequential-thinking** - Multi-step reasoning, complex analysis, systematic problem-solving

## Usage Guidelines

The `.claude/mcp/` directory contains **usage guidelines** (not configuration files) that help Claude decide WHEN to use each MCP server's tools:

- `mcp/Serena.md` - When to use Serena tools (symbol operations, large projects)
- `mcp/Context7.md` - When to use Context7 (library docs, official patterns)
- `mcp/Sequential.md` - When to use sequential-thinking (complex analysis, debugging)

These files contain:
- **Triggers**: Scenarios where the MCP's tools are most useful
- **Choose When**: Decision guidelines for tool selection
- **Examples**: Common use cases and patterns

**Note**: These are semantic hints for Claude's decision-making, not technical loading conditions.

## User Flags (Optional Semantic Hints)

You can include these flags in your requests as hints for Claude's tool selection:

- `--serena` - Hint: prefer Serena tools for this task
- `--c7` or `--context7` - Hint: prefer Context7 for library documentation
- `--seq` or `--sequential` - Hint: prefer sequential-thinking for analysis

**Important**: These flags do NOT control MCP loading. They are semantic hints that may influence Claude's tool selection if you've implemented custom logic in slash commands or if Claude interprets them as usage preferences.
