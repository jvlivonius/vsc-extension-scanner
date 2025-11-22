# SC Commands Reference

**Purpose**: Shared patterns for all `/sc:*` commands. Eliminate redundancy, maintain consistency.

**Format**: Lookup table optimized for AI consumption. Read this ONCE, reference throughout commands.

---

## Command Namespace Overview

`/sc:*` = SuperClaude commands for software development workflow

| Command | Purpose | Complexity |
|---------|---------|------------|
| `/sc:implement` | Feature implementation | standard |
| `/sc:test` | Testing and quality | standard |
| `/sc:task` | Complex task coordination | advanced |
| `/sc:analyze` | Code analysis | basic |
| `/sc:build` | Build and package | basic |
| `/sc:design` | Design and architecture | standard |
| `/sc:cleanup` | Code cleanup | basic |
| `/sc:improve` | Quality improvements | standard |
| `/sc:load` | Session loading | basic |
| `/sc:save` | Session persistence | basic |

---

## MCP Server Usage Patterns

### When to Use Which MCP

| Task Type | Primary MCP | Secondary MCP | Rationale |
|-----------|-------------|---------------|-----------|
| Feature implementation | context7 | sequential | Official patterns + planning |
| Symbol operations | serena | - | Rename, extract, refactor |
| Complex analysis | sequential | context7 | Structured reasoning + docs |
| HTML report testing | playwright | - | Browser automation |
| Session persistence | serena | - | Project memory |

### MCP Configuration Variables

Commands reference PROJECT_CONFIG.yaml for MCP preferences:

```yaml
# From PROJECT_CONFIG.yaml
mcp_preferences:
  code_docs: context7
  analysis: sequential
  symbols: serena
  browser_testing: playwright
```

**Usage in commands:**
- `{CODE_DOCS_TOOL}` → context7
- `{ANALYSIS_TOOL}` → sequential
- `{SYMBOL_TOOL}` → serena
- `{BROWSER_TEST_TOOL}` → playwright

---

## Agent Persona Patterns

### Agent Selection Matrix

| Task Type | Primary Agent | Supporting Agents |
|-----------|---------------|-------------------|
| Implementation | python-expert | security-engineer |
| Testing | quality-engineer | - |
| Performance | performance-engineer | - |
| Debugging | root-cause-analyst | python-expert |
| Refactoring | python-expert | quality-engineer |
| Security review | security-engineer | - |

### Agent Configuration Variables

Commands reference PROJECT_CONFIG.yaml for agent preferences:

```yaml
# From PROJECT_CONFIG.yaml
agent_preferences:
  implementation: [python-expert, security-engineer]
  testing: [quality-engineer]
  performance: [performance-engineer]
  debugging: [root-cause-analyst]
  refactoring: [python-expert, quality-engineer]
  security_review: [security-engineer]
```

**Usage pattern:** Commands activate agents based on task type, config provides specific personas.

---

## Tool Command Patterns

### Standard Tool References

All /sc commands use PROJECT_CONFIG.yaml for tool commands:

```yaml
# From PROJECT_CONFIG.yaml
tools:
  test_runner: "pytest tests/"
  test_coverage: "pytest --cov=vscode_scanner tests/"
  build: "python -m build"
  lint: "pre-commit run --all-files"
  type_check: "mypy vscode_scanner"
```

### Common Tool Variables

| Variable | Config Key | Example Value |
|----------|------------|---------------|
| {TEST_RUNNER} | tools.test_runner | "pytest tests/" |
| {TEST_COVERAGE} | tools.test_coverage | "pytest --cov..." |
| {BUILD_TOOL} | tools.build | "python -m build" |
| {LINT_TOOL} | tools.lint | "pre-commit run" |
| {TYPE_CHECK} | tools.type_check | "mypy vscode_scanner" |

---

## Quality Gates

### Standard Quality Checks

Commands reference PROJECT_CONFIG.yaml for thresholds:

```yaml
# From PROJECT_CONFIG.yaml
quality_gates:
  min_coverage: 87
  min_security_coverage: 95
  max_complexity: 10
  architecture_violations: 0
  security_vulnerabilities: 0
```

### Quality Gate Validation Pattern

```markdown
[REQUIRED]
- Verify coverage meets {MIN_COVERAGE}% threshold
- Ensure zero security vulnerabilities
- Validate architecture boundaries
```

---

## Common Workflow Patterns

### Implementation Workflow (3 Steps)

Standard pattern for /sc:implement, /sc:improve, /sc:cleanup:

1. **Analyze**: Parse requirements → detect context from PROJECT_CONFIG
2. **Execute**: Generate/modify code → apply patterns → validate
3. **Finalize**: Run tests → verify quality gates → update docs

### Testing Workflow (3 Steps)

Standard pattern for /sc:test, /sc:analyze:

1. **Discover**: Categorize targets → determine tools from PROJECT_CONFIG
2. **Execute**: Run tools → monitor progress → collect results
3. **Report**: Generate metrics → validate quality gates → provide recommendations

### Task Workflow (3 Steps)

Standard pattern for /sc:task, /sc:design:

1. **Plan**: Break down task → identify dependencies → allocate resources
2. **Coordinate**: Activate agents → route to MCPs → execute in parallel
3. **Integrate**: Collect results → validate completion → persist state

---

## Documentation Requirements

### Required Documentation Pattern

Commands reference PROJECT_CONFIG.yaml for docs:

```yaml
# From PROJECT_CONFIG.yaml
required_docs:
  architecture: "docs/guides/ARCHITECTURE.md"
  security: "docs/guides/SECURITY.md"
  testing: "docs/guides/TESTING.md"
  requirements: "docs/project/PRD.md"
```

### Documentation Reading Pattern

```markdown
[REQUIRED]
- Read {ARCHITECTURE_DOC} before structural changes
- Read {SECURITY_DOC} before security-related work
- Read {TESTING_DOC} for test strategy
- Read {REQUIREMENTS_DOC} for scope validation
```

---

## Error Handling Patterns

### Common Error Scenarios

| Error | Detection | Recovery |
|-------|-----------|----------|
| Tests failing | Run {TEST_RUNNER} | Fix failures before proceeding |
| Coverage below threshold | Compare to {MIN_COVERAGE} | Add tests or adjust threshold |
| Quality gate failure | Validate against quality_gates | Fix issues, don't skip gates |
| Missing documentation | Check required_docs existence | Read docs or fail fast |

### Error Handling Directive

Standard pattern for all commands:

```markdown
[FORBIDDEN]
- Skip quality gates or test failures
- Proceed with errors unresolved
- Generate incomplete implementations
```

---

## Session Persistence Patterns

### Load/Save Workflow

Used by /sc:load, /sc:save, /sc:task:

**Save Pattern:**
```markdown
1. Use {SYMBOL_TOOL} write_memory() for state
2. Persist task hierarchy and progress
3. Store context for resume
```

**Load Pattern:**
```markdown
1. Use {SYMBOL_TOOL} list_memories()
2. Read relevant memory files
3. Resume from checkpoints
```

---

## Parallel Execution Patterns

### When to Parallelize

| Scenario | Pattern | Benefit |
|----------|---------|---------|
| Multiple independent tests | Parallel test execution | Faster feedback |
| Multiple file edits | Multiple Edit tool calls | Atomic changes |
| Multi-domain analysis | Concurrent analysis runs | Comprehensive results |

### Parallel Execution Directive

```markdown
[REQUIRED]
- Execute independent operations in parallel
- Use multiple tool calls in single message
- Only sequential when dependencies exist
```

---

## Configuration Override Patterns

### Command-Line Overrides

Commands may accept flags that override PROJECT_CONFIG:

| Flag | Overrides | Example |
|------|-----------|---------|
| `--framework X` | frameworks.* | --framework jest |
| `--test-tool X` | tools.test_runner | --test-tool vitest |
| `--coverage-min X` | quality_gates.min_coverage | --coverage-min 90 |

### Override Pattern

```markdown
PATTERN: /sc:test --framework jest
RESULT: Uses jest instead of PROJECT_CONFIG default
```

---

## Common Constraints

### Universal Constraints

All /sc commands share these [FORBIDDEN] directives:

- Generate incomplete implementations (no TODOs, no stubs)
- Skip security validation or quality gates
- Make destructive changes without validation
- Proceed with unresolved errors
- Ignore architecture or security documentation

---

## Cross-Command References

### Commands That Work Together

| Primary | Complementary | Integration |
|---------|---------------|-------------|
| /sc:implement | /sc:test | Implementation → Testing |
| /sc:design | /sc:implement | Design → Implementation |
| /sc:analyze | /sc:improve | Analysis → Improvements |
| /sc:load | /sc:save | Session lifecycle |
| /sc:task | All | Orchestration layer |

---

## Framework Migration

### Adapting for Other Languages

To use SC commands for JavaScript/TypeScript projects:

```yaml
# JavaScript PROJECT_CONFIG.yaml
frameworks:
  cli: commander
  testing: jest
  formatting: chalk
  http: axios

tools:
  test_runner: "jest"
  test_coverage: "jest --coverage"
  build: "npm run build"
  lint: "eslint ."
  type_check: "tsc --noEmit"
```

**Result:** Same /sc commands work with different tech stack.

---

## Quick Reference Table

| Need | Config Variable | Example Value |
|------|----------------|---------------|
| Test framework | {TEST_FRAMEWORK} | pytest |
| Build tool | {BUILD_TOOL} | python -m build |
| Code docs MCP | {CODE_DOCS_TOOL} | context7 |
| Analysis MCP | {ANALYSIS_TOOL} | sequential |
| Symbol operations MCP | {SYMBOL_TOOL} | serena |
| Min coverage | {MIN_COVERAGE} | 87 |
| Architecture doc | {ARCHITECTURE_DOC} | docs/guides/ARCHITECTURE.md |
| Security doc | {SECURITY_DOC} | docs/guides/SECURITY.md |

---

**Last Updated**: 2025-11-22
**Maintainer**: Keep in sync with PROJECT_CONFIG.yaml and COMMAND_TEMPLATE.md
**Usage**: Import this reference in command descriptions instead of repeating content
