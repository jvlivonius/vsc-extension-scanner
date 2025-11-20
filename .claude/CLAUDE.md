# SuperClaude Entry Point - Python CLI Optimized

Tiered context system with selective agent auto-activation and MCP tool usage guidelines.

---

## Project: VS Code Extension Security Scanner

**Purpose**: Python CLI tool for manual security audits of VS Code extensions via vscan.dev API

**Tech Stack**:
- **Language**: Python 3.8+
- **Testing**: pytest, hypothesis (property-based)
- **CLI**: typer, rich
- **Data**: SQLite3 with HMAC-SHA256 integrity
- **HTTP**: urllib.request (stdlib only)

**Architecture**: 3-layer (Presentation → Application → Infrastructure), strict one-way dependencies

**Critical Docs Before Code Changes**:
- `CLAUDE.md` (root) - Project overview, commands, structure, workflows
- `docs/guides/ARCHITECTURE.md` - 3-layer rules, design principles, anti-patterns
- `docs/guides/SECURITY.md` - validate_path(), sanitize_string() patterns
- `docs/project/PRD.md` - Feature scope, requirements, constraints

**Current Status**: `docs/project/STATUS.md` - Version, test metrics, active roadmap

---

## Quick Task Router

Recommended agents and tools for common development tasks:

| Development Task | Recommended Approach | Read First |
|-----------------|----------|------------|
| Add new feature | python-expert + security-engineer agents | PRD.md, ARCHITECTURE.md |
| Fix security bug | security-engineer agent (auto-active) | SECURITY.md |
| Refactor/cleanup | python-expert + quality-engineer agents | ARCHITECTURE.md |
| Debug complex issue | root-cause-analyst agent + sequential-thinking MCP | Error logs, STATUS.md |
| Write/improve tests | quality-engineer agent | TESTING.md |
| Performance issue | performance-engineer agent | PERFORMANCE.md |
| Multi-file changes | Serena MCP tools (symbol operations) | mcp/Serena.md |
| Library questions | Context7 MCP tools (official docs) | mcp/Context7.md |

**Note**: MCP servers (if configured) are always loaded. See MCP_LOADER.md for details.

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

**python-expert**
- @agents/python-expert.md
- Production-quality Python, SOLID principles, TDD approach
- Clean architecture, dependency injection, separation of concerns

**security-engineer**
- @agents/security-engineer.md
- OWASP compliance, vulnerability assessment
- Critical patterns: validate_path(), sanitize_string()

**quality-engineer**
- @agents/quality-engineer.md
- pytest + hypothesis (property-based testing)
- Test strategy, edge case detection, coverage analysis

**performance-engineer**
- @agents/performance-engineer.md
- ThreadPoolExecutor optimization (3 workers, configurable 1-5)
- Profiling-based optimization, memory efficiency

**root-cause-analyst**
- @agents/root-cause-analyst.md
- Systematic debugging, evidence-based analysis
- Hypothesis testing, pattern recognition

### Project-Specific Agent Triggers

**Security Changes** (security-engineer):
- MUST read SECURITY.md first
- Use validate_path() for all file operations
- Use sanitize_string() for all user input
- Verify: `python tests/test_security.py` (0 vulnerabilities required)

**Architecture Changes** (python-expert):
- Follow 3-layer rules: P → A → I (one-way only)
- NO Infrastructure imports of Presentation
- Verify: `python tests/test_architecture.py` (0 violations required)

**Testing Requirements** (quality-engineer):
- pytest + hypothesis patterns
- Maintain 87%+ overall, 80%+ critical, 95%+ security coverage
- AAA pattern (Arrange-Act-Assert)

---

# Tier 2: Context-Triggered Modes & Agents

## MODEs
These activate dynamically via keyword detection or manual flags:

**modes/Brainstorming.md (--brainstorm)**
- Vague requests, exploration, uncertainty
- Example: "explore better caching strategies", "thinking about API retry logic"

**modes/Introspection.md (--introspect)**
- Error recovery, meta-analysis, unexpected results
- Example: test failures, CI breaks, "why did this fail?"

**modes/Token_Efficiency.md (--uc)**
- Context >75%, efficiency mode
- Example: large refactoring, multi-file operations

**modes/Orchestration.md (--orchestrate)**
- Multi-tool coordination, parallel opportunities
- Example: batch file operations, complex workflows

**modes/Task_Management.md (--task-manage)**
- >3 steps, complex scope, multiple directories
- Example: security enhancement, feature implementation, major refactoring

## Workflow Rules
Loaded for implementation tasks:
- **RULES_WORKFLOW.md**: Implementation patterns, professional standards

## Specialized Agents
- **agents/deep-research-agent.md (--think-hard, --ultrathink)**: Complex analysis

---

## Available Slash Commands

**Session Management**:
- `/sc:load` - Resume session context from Serena memory
- `/sc:save` - Save session context to Serena memory

**Development Workflows**:
- `/sc:implement` - Code implementation with intelligent persona activation
- `/sc:test` - Execute tests with coverage analysis (pytest/hypothesis)
- `/sc:build` - Build, compile, and package projects
- `/sc:analyze` - Comprehensive code analysis (quality, security, performance, architecture)
- `/sc:improve` - Apply systematic improvements to code quality, performance, maintainability

**Specialized Tasks**:
- `/sc:design` - Design system architecture, APIs, component interfaces
- `/sc:cleanup` - Systematically clean up code, remove dead code, optimize structure
- `/sc:task` - Execute complex tasks with intelligent workflow management

**GitHub Integration** (`/gh:` commands):

- `/gh:projects` - GitHub Projects workflow automation with issue/PR linking
- `/gh:implement-issue` - Agent-driven issue implementation with automated testing and PR creation
- `/gh:milestone` - Comprehensive milestone management (create, report, sync, close)
- `/gh:triage` - AI-assisted issue triage with intelligent label and priority suggestions
- `/gh:git` - Git operations with intelligent commit messages and workflow optimization

**Usage**: Type command name (e.g., `/sc:test` or `/gh:triage`) to see full prompt expansion

---

# Tier 3: Usage Guidelines & Reference

## MCP Server Usage Guidelines (in mcp/ directory)

**IMPORTANT**: These are **usage guidelines**, not configuration files. MCP servers configured via `claude mcp add` are **always loaded** at startup. These docs help Claude decide WHEN to use each server's tools.

- **mcp/Serena.md**: When to use Serena tools (symbol operations, project memory, session persistence)
- **mcp/Context7.md**: When to use Context7 tools (library docs: pytest, typer, rich, hypothesis)
- **mcp/Sequential.md**: When to use sequential-thinking (complex analysis, multi-step reasoning)

See **MCP_LOADER.md** for how MCP loading actually works.

## Quick Reference (in root directory)
- **RULES_REFERENCE.md**: Decision trees, quick actions, examples
