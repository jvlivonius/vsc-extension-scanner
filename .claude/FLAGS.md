# SuperClaude Framework Flags

Behavioral flags for Claude Code to enable specific execution modes and tool selection patterns.

## Mode Activation Flags

**--brainstorm**: Vague requests, exploration keywords → Collaborative discovery
**--introspect**: Error recovery, self-analysis → Transparent reasoning
**--task-manage**: >3 steps, >2 directories → Systematic organization
**--orchestrate**: Multi-tool ops, parallel opportunities → Tool optimization
**--token-efficient / --uc**: Context >75% → Symbol communication

*Full MODE docs: `.claude/modes/` directory*

## MCP Server Usage Hints

**IMPORTANT**: MCP servers configured via `claude mcp add` are **always loaded**. These flags are **semantic hints** for Claude's tool selection, not loading controls.

**Usage Preference Hints**:
- **--c7 / --context7**: Prefer Context7 for library docs (pytest, typer, rich, hypothesis)
- **--seq / --sequential**: Prefer sequential-thinking for complex analysis, architecture, debugging
- **--serena**: Prefer Serena tools for symbol operations, project memory, session persistence

**Note**: These flags may influence Claude's tool selection if you've implemented custom logic in slash commands. They do NOT enable/disable MCP servers.

*See MCP_LOADER.md for how MCP loading actually works*

## Analysis Depth Flags

**--think**: Standard analysis (~4K tokens), prefer sequential-thinking
**--think-hard**: Deep analysis (~10K tokens), prefer sequential-thinking + Context7
**--ultrathink**: Maximum depth (~32K tokens), prefer all MCP tools + deep-research-agent

**Note**: These flags indicate analysis depth preference. MCP servers remain loaded regardless of flags.

## Execution Control Flags

**--delegate [auto|files|folders]**: >7 dirs OR >50 files → Sub-agent processing
**--concurrency [n]**: Control max concurrent ops (1-15)
**--loop**: Iterative improvement cycles
**--iterations [n]**: Set cycle count (1-10)
**--validate**: Pre-execution risk assessment
**--safe-mode**: Maximum validation, conservative execution

## Output Optimization Flags

**--uc / --ultracompressed**: Symbol communication, 30-50% token reduction
**--scope [file|module|project|system]**: Define operational scope
**--focus [performance|security|quality|architecture|testing]**: Target specific domain

## Flag Priority Rules

**Safety First**: --safe-mode > --validate > optimization flags
**Explicit Override**: User flags > auto-detection
**Depth Hierarchy**: --ultrathink > --think-hard > --think
**Scope Precedence**: system > project > module > file

**Note**: Flag priority applies to semantic hints and preferences. Actual MCP loading is controlled via `claude mcp add/remove` CLI commands.
