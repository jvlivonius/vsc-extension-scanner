# SuperClaude Entry Point - Python CLI Optimized

Tiered context system with selective agent auto-activation and MCP tool usage guidelines.

---

## Project Context

**See root CLAUDE.md for**:
- Project purpose and tech stack
- Critical documentation requirements
- Current project status
- Development commands and workflows

---

## Agent Selection Guide

| Task Category | Recommended Agent(s) |
|---------------|---------------------|
| New features | python-expert + security-engineer |
| Security issues | security-engineer |
| Refactoring | python-expert + quality-engineer |
| Complex debugging | root-cause-analyst + sequential-thinking MCP |
| Testing | quality-engineer |
| Performance | performance-engineer |
| Symbol operations | Serena MCP |
| Library documentation | Context7 MCP |

**Note**: MCP servers are always loaded if configured. See MCP_LOADER.md for details.

---

# Tier 1: Always Loaded

## Core Framework
@RULES_CORE.md
@PRINCIPLES.md
@FLAGS.md
@MODE_LOADER.md
@MCP_LOADER.md

## Auto-Active Agents
These agents provide specialized expertise for all relevant tasks:

**python-expert** (@agents/python-expert.md)
- Production-quality code, SOLID principles, TDD approach
- Clean architecture, dependency injection

**security-engineer** (@agents/security-engineer.md)
- OWASP compliance, vulnerability assessment
- Security validation required before approval

**quality-engineer** (@agents/quality-engineer.md)
- Test strategy, edge case detection, coverage analysis
- Property-based testing patterns

**performance-engineer** (@agents/performance-engineer.md)
- Profiling-based optimization, memory efficiency
- Parallel execution strategies

**root-cause-analyst** (@agents/root-cause-analyst.md)
- Systematic debugging, evidence-based analysis
- Hypothesis testing, pattern recognition

---

# Tier 2: Context-Triggered Modes & Agents

## MODEs
These activate dynamically via keyword detection or manual flags:

**modes/Brainstorming.md (--brainstorm)**
- Vague requests, exploration, uncertainty

**modes/Introspection.md (--introspect)**
- Error recovery, meta-analysis, unexpected results

**modes/Token_Efficiency.md (--uc)**
- Context >75%, efficiency mode

**modes/Orchestration.md (--orchestrate)**
- Multi-tool coordination, parallel opportunities

**modes/Task_Management.md (--task-manage)**
- >3 steps, complex scope, multiple directories

## Workflow Rules
Loaded for implementation tasks:
- **RULES_WORKFLOW.md**: Implementation patterns, professional standards

## Specialized Agents
- **agents/deep-research-agent.md (--think-hard, --ultrathink)**: Complex analysis

---

## Available Slash Commands

**See root CLAUDE.md for**:
- Session management commands (/sc:load, /sc:save)
- Development workflow commands (/sc:implement, /sc:test, /sc:build)
- Specialized task commands (/sc:design, /sc:cleanup, /sc:task)
- GitHub integration commands (/gh:projects, /gh:implement-issue, /gh:milestone)

**Usage**: Type command name to see full prompt expansion

---

# Tier 3: Usage Guidelines & Reference

## MCP Server Usage Guidelines (in mcp/ directory)

**IMPORTANT**: These are **usage guidelines**, not configuration files. MCP servers configured via `claude mcp add` are **always loaded** at startup. These docs help Claude decide WHEN to use each server's tools.

- **mcp/Serena.md**: Symbol operations, project memory, session persistence
- **mcp/Context7.md**: Official library documentation lookup
- **mcp/Sequential.md**: Complex analysis, multi-step reasoning
- **mcp/MCP_Playwright.md**: Browser automation, visual validation, accessibility

See **MCP_LOADER.md** for how MCP loading actually works.

## Quick Reference (in root directory)
- **RULES_REFERENCE.md**: Decision trees, quick actions, examples
