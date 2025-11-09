# sequential-thinking MCP Server - Usage Guidelines

> **IMPORTANT**: This document describes WHEN to use sequential-thinking, not how to load the server. MCP servers configured via `claude mcp add` are always loaded at startup. See `MCP_LOADER.md` for configuration details.

**Purpose**: Multi-step reasoning engine for complex analysis and systematic problem solving

## Triggers
- Complex debugging scenarios with multiple layers
- Architectural analysis and system design questions
- `--think`, `--think-hard`, `--ultrathink` flags
- Problems requiring hypothesis testing and validation
- Multi-component failure investigation
- Performance bottleneck identification requiring methodical approach

## Choose When
- **Over native reasoning**: When problems have 3+ interconnected components
- **For systematic analysis**: Root cause analysis, architecture review, security assessment
- **When structure matters**: Problems benefit from decomposition and evidence gathering
- **For cross-domain issues**: Problems spanning CLI, API, cache, architecture layers
- **Not for simple tasks**: Basic explanations, single-file changes, straightforward fixes

## Works Best With
- **Context7**: sequential-thinking coordinates analysis → Context7 provides official patterns
- **Serena**: sequential-thinking analyzes architecture → Serena performs symbol refactoring
- **pytest**: sequential-thinking identifies testing strategy → pytest executes validation

## Examples
```
"why is this API slow?" → sequential-thinking (systematic performance analysis)
"analyze 3-layer architecture" → sequential-thinking (structured system design)
"debug cache corruption" → sequential-thinking (multi-component investigation)
"analyze security vulnerabilities" → sequential-thinking (comprehensive threat modeling)
"explain this function" → Native Claude (simple explanation)
"fix this typo" → Native Claude (straightforward change)
```
