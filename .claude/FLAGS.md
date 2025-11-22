# SuperClaude Framework Flags

Behavioral flags for execution modes and tool selection. See `.claude/modes/` and `MCP_LOADER.md` for details.

## Mode Flags

**--brainstorm**: Vague requests, exploration → Collaborative discovery
**--introspect**: Error recovery, self-analysis → Transparent reasoning
**--task-manage**: >3 steps, >2 directories → Systematic organization
**--orchestrate**: Multi-tool ops, parallel ops → Tool optimization
**--uc / --token-efficient**: Context >75% → Symbol communication

## MCP Tool Preference Hints

**IMPORTANT**: MCP servers (via `claude mcp add`) are always loaded. These flags are semantic hints only.

**--c7 / --context7**: Prefer Context7 for library documentation
**--seq / --sequential**: Prefer sequential-thinking for complex analysis
**--serena**: Prefer Serena for symbol operations
**--playwright / --pw**: Prefer Playwright for browser testing

## Analysis Depth

**--think**: Standard analysis (~4K tokens)
**--think-hard**: Deep analysis (~10K tokens)
**--ultrathink**: Maximum depth (~32K tokens) + deep-research-agent

## Execution Control

**--delegate [auto|files|folders]**: Sub-agent processing (>7 dirs OR >50 files)
**--concurrency [n]**: Max concurrent ops (1-15)
**--loop**: Iterative improvement cycles
**--iterations [n]**: Cycle count (1-10)
**--validate**: Pre-execution risk assessment
**--safe-mode**: Maximum validation

## Output Control

**--scope [file|module|project|system]**: Operational scope
**--focus [performance|security|quality|architecture|testing]**: Target domain

## Priority Rules

Safety: --safe-mode > --validate > optimization
Override: User flags > auto-detection
Depth: --ultrathink > --think-hard > --think
Scope: system > project > module > file
