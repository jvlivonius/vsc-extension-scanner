# Orchestration Mode

## Triggers
Multi-tool operations (>3 files), performance constraints (>75% resource usage), parallel execution opportunities, --orchestrate flag

## Directives
- Choose most powerful tool for each task type
- Adapt approach based on system resource constraints
- Identify independent operations for concurrent execution
- Optimize tool usage for speed and effectiveness

## Tool Selection Matrix

| Task Type | Best Tool | Alternative |
|-----------|-----------|-------------|
| Symbol operations | Serena MCP | Manual search + Edit |
| Deep analysis | sequential-thinking | Native reasoning |
| Multi-file edits | Multiple parallel Edits | Sequential Edits |
| Library docs | Context7 MCP | WebSearch |
| Testing | Project test framework | Manual test writing |
| Config files | Read + Edit | Bash commands |
| Browser testing | Playwright MCP | Manual testing |

## Resource Management

**[GREEN] Zone (0-75%)**
- Full capabilities available
- Use all tools and features
- Normal verbosity

**[YELLOW] Zone (75-85%)**
- Activate efficiency mode
- Reduce verbosity
- Defer non-critical operations

**[RED] Zone (85%+)**
- Essential operations only
- Minimal output
- Fail fast on complex requests

## Parallel Execution Triggers
- **3+ files**: Auto-suggest parallel processing
- **Independent operations**: Batch Read calls, parallel edits
- **Multi-directory scope**: Enable delegation mode
- **Performance requests**: Parallel-first approach
