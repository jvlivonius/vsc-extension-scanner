# Core Behavioral Rules

**Critical safety patterns and workflows that must always be followed.**

## Rule Priority System

**🔴 CRITICAL**: Security, data safety, production breaks - Never compromise
**🟡 IMPORTANT**: Quality, maintainability, professionalism - Strong preference
**🟢 RECOMMENDED**: Optimization, style, best practices - Apply when practical

### Conflict Resolution Hierarchy
1. **Safety First**: Security/data rules always win
2. **Scope > Features**: Build only what's asked > complete everything
3. **Quality > Speed**: Except in genuine emergencies
4. **Context Matters**: Prototype vs Production requirements differ

## Agent Orchestration
**Priority**: 🔴 **Triggers**: Task execution and post-implementation

**Agent Usage** (Selected agents auto-loaded via @import):
- **Auto-Loaded Agents**: python-expert, security-engineer, quality-engineer, performance-engineer, root-cause-analyst
- **Conditional Agents**: deep-research-agent (with --think-hard, --ultrathink)
- **Agent Expertise**: Agents provide specialized instruction sets for their domains
- **Always Active**: Auto-loaded agents apply their expertise to all relevant tasks

**Orchestration Flow**:
1. **Task Execution**: User request → Relevant agent expertise applies → Implementation
2. **Validation**: Implementation complete → Verify quality and correctness
3. **Documentation**: Update relevant documentation as needed

✅ **Right**: User request → python-expert expertise applies → Validate → Document
✅ **Right**: Use --think-hard to load deep-research-agent for complex analysis
❌ **Wrong**: Skip validation after implementation
❌ **Wrong**: Continue implementing after errors detected

## Workflow Rules
**Priority**: 🟡 **Triggers**: All development tasks

- **Task Pattern**: Understand → Plan (with parallelization analysis) → Track tasks (3+ steps) → Execute → Validate
- **Batch Operations**: ALWAYS parallel tool calls by default, sequential ONLY for dependencies
- **Validation Gates**: Always validate before execution, verify after completion
- **Quality Checks**: Run lint/typecheck before marking tasks complete
- **Context Retention**: Maintain ≥90% understanding across operations
- **Evidence-Based**: All claims must be verifiable through testing or documentation
- **Discovery First**: Complete project-wide analysis before systematic changes
- **Session Lifecycle**: Initialize with /sc:load, checkpoint regularly, save before end
- **Session Pattern**: /sc:load → Work → Checkpoint (30min) → /sc:save
- **Checkpoint Triggers**: Task completion, 30-min intervals, risky operations

✅ **Right**: Plan → Track tasks → Execute → Validate
❌ **Wrong**: Jump directly to implementation without planning

## Planning Efficiency
**Priority**: 🔴 **Triggers**: All planning phases, task tracking, multi-step tasks

- **Parallelization Analysis**: During planning, explicitly identify operations that can run concurrently
- **Tool Optimization Planning**: Plan for optimal MCP server combinations and batch operations
- **Dependency Mapping**: Clearly separate sequential dependencies from parallelizable tasks
- **Resource Estimation**: Consider token usage and execution time during planning phase
- **Efficiency Metrics**: Plan should specify expected parallelization gains (e.g., "3 parallel ops = 60% time saving")

✅ **Right**: "Plan: 1) Parallel: [Read 5 files] 2) Sequential: analyze → 3) Parallel: [Edit all files]"
❌ **Wrong**: "Plan: Read file1 → Read file2 → Read file3 → analyze → edit file1 → edit file2"

## Failure Investigation
**Priority**: 🔴 **Triggers**: Errors, test failures, unexpected behavior, tool failures

- **Root Cause Analysis**: Always investigate WHY failures occur, not just that they failed
- **Never Skip Tests**: Never disable, comment out, or skip tests to achieve results
- **Never Skip Validation**: Never bypass quality checks or validation to make things work
- **Debug Systematically**: Step back, assess error messages, investigate tool failures thoroughly
- **Fix Don't Workaround**: Address underlying issues, not just symptoms
- **Tool Failure Investigation**: When MCP tools or scripts fail, debug before switching approaches
- **Quality Integrity**: Never compromise system integrity to achieve short-term results
- **Methodical Problem-Solving**: Understand → Diagnose → Fix → Verify, don't rush to solutions

✅ **Right**: Analyze stack trace → identify root cause → fix properly
❌ **Wrong**: Comment out failing test to make build pass
**Detection**: `grep -r "skip\|disable\|TODO" tests/`

## Git Workflow
**Priority**: 🔴 **Triggers**: Session start, before changes, risky operations

- **Always Check Status First**: Start every session with `git status` and `git branch`
- **Feature Branches Only**: Create feature branches for ALL work, never work on main/master
- **Branch Naming**: Use format `<type>/<short-descriptive-name>` (feature/*, bugfix/*, hotfix/*)
- **Branch from Main**: Always create new branches from updated main branch
- **Incremental Commits**: Commit frequently with meaningful messages, not giant commits
- **Commit Message Format**: Use `<type>(<scope>): <subject>` (e.g., `feat(scanner): add parallel processing`)
- **Verify Before Commit**: Always `git diff` to review changes before staging
- **Create Restore Points**: Commit before risky operations for easy rollback
- **Branch for Experiments**: Use branches to safely test different approaches
- **Pull Request Required**: All changes merge via PR with 1 approval and passing CI
- **Update Before PR**: Rebase or merge main into feature branch before creating PR
- **Clean History**: Use descriptive commit messages, avoid "fix", "update", "changes"
- **Non-Destructive Workflow**: Always preserve ability to rollback changes
- **Delete After Merge**: Remove feature branches after PR merge

**Branch Types:**
- `feature/*` - New features, enhancements (e.g., `feature/add-csv-export`)
- `bugfix/*` - Non-critical bug fixes (e.g., `bugfix/cache-corruption`)
- `hotfix/*` - Critical security/data issues (e.g., `hotfix/CVE-2024-12345`)
- `claude/*` - Claude Code automated work (auto-generated names)
- `dependabot/*` - Automated dependency updates

**Commit Types:**
- `feat` - New feature
- `fix` - Bug fix
- `hotfix` - Critical security/data fix
- `docs` - Documentation only
- `refactor` - Code restructuring
- `test` - Testing updates
- `chore` - Maintenance (deps, build)

✅ **Right**: `git checkout main && git pull && git checkout -b feature/auth` → work → commit → push → PR
❌ **Wrong**: Work directly on main/master branch
❌ **Wrong**: Branch names like `fix-bug`, `temp`, `john-work`
✅ **Right**: `git commit -m "feat(auth): add JWT token validation"`
❌ **Wrong**: `git commit -m "update code"`
**Detection**: `git branch` should show feature/*, bugfix/*, or hotfix/* branch

→ **Full workflow:** See [docs/contributing/GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md)

## Tool Optimization
**Priority**: 🟢 **Triggers**: Multi-step operations, performance needs, complex tasks

- **Best Tool Selection**: Always use the most powerful tool for each task (MCP > Native > Basic)
- **Parallel Everything**: Execute independent operations in parallel, never sequentially
- **Agent Expertise**: Auto-loaded agents provide specialized guidance for complex operations
- **MCP Server Usage**: Leverage specialized MCP servers for their strengths (serena for symbols, sequential-thinking for analysis, context7 for docs)
- **Batch Operations**: Use multiple parallel Edit calls, batch Read calls, group operations
- **Powerful Search**: Use Grep tool over bash grep, Glob over find, specialized search tools
- **Efficiency First**: Choose speed and power over familiarity - use the fastest method available
- **Tool Specialization**: Match tools to their designed purpose (e.g., serena for symbols, context7 for docs, sequential for complex reasoning)

✅ **Right**: Use multiple parallel Edit calls for 3+ file changes, parallel Read calls
❌ **Wrong**: Sequential Edit calls, bash grep instead of Grep tool

## Safety Rules
**Priority**: 🔴 **Triggers**: File operations, library usage, codebase changes

- **Framework Respect**: Check package.json/deps before using libraries
- **Pattern Adherence**: Follow existing project conventions and import styles
- **Transaction-Safe**: Prefer batch operations with rollback capability
- **Systematic Changes**: Plan → Execute → Verify for codebase modifications

✅ **Right**: Check dependencies → follow patterns → execute safely
❌ **Wrong**: Ignore existing conventions, make unplanned changes

## Temporal Awareness
**Priority**: 🔴 **Triggers**: Date/time references, version checks, deadline calculations, "latest" keywords

- **Always Verify Current Date**: Check <env> context for "Today's date" before ANY temporal assessment
- **Never Assume From Knowledge Cutoff**: Don't default to January 2025 or knowledge cutoff dates
- **Explicit Time References**: Always state the source of date/time information
- **Version Context**: When discussing "latest" versions, always verify against current date
- **Temporal Calculations**: Base all time math on verified current date, not assumptions

✅ **Right**: "Checking env: Today is 2025-08-15, so the Q3 deadline is..."
❌ **Wrong**: "Since it's January 2025..." (without checking)
**Detection**: Any date reference without prior env verification
