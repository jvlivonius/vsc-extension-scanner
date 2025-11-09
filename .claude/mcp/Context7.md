# Context7 MCP Server - Usage Guidelines

> **IMPORTANT**: This document describes WHEN to use Context7 tools, not how to load the server. MCP servers configured via `claude mcp add` are always loaded at startup. See `MCP_LOADER.md` for configuration details.

**Purpose**: Official library documentation lookup and framework pattern guidance

## Triggers
- Import statements: `import`, `from`
- Framework keywords: pytest, typer, hypothesis, rich, click, etc.
- Library-specific questions about APIs or best practices
- Need for official documentation patterns vs generic solutions
- Version-specific implementation requirements

## Choose When
- **Over WebSearch**: When you need curated, version-specific documentation
- **Over native knowledge**: When implementation must follow official patterns
- **For frameworks**: pytest fixtures, typer decorators, hypothesis strategies
- **For libraries**: Correct API usage, CLI patterns, testing approaches
- **For compliance**: When adherence to official standards is mandatory

## Works Best With
- **sequential-thinking**: Context7 provides docs → sequential-thinking analyzes implementation strategy
- **Serena**: Context7 supplies patterns → Serena performs symbol-aware refactoring

## Examples
```
"implement pytest fixtures" → Context7 (official pytest patterns)
"use typer CLI decorators" → Context7 (official typer documentation)
"hypothesis property testing" → Context7 (official hypothesis strategies)
"rich console formatting" → Context7 (official Rich library patterns)
"just explain this function" → Native Claude (no external docs needed)
```
