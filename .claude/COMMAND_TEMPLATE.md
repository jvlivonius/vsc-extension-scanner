# Command Template Reference

**Purpose:** Canonical template for all slash commands. Ensures consistency, reliability, and agent-first optimization.

**Usage:** Copy this template when creating new commands. Follow structure exactly.

---

## Template Structure

```markdown
---
name: {command-name}
description: "{one-line purpose - what this command does}"
category: {workflow|utility|special}
complexity: {basic|standard|advanced}
requires-config: {true|false}
---

# /{namespace}:{command-name}

## Purpose
{One clear sentence defining what this command accomplishes}

## Triggers
- {Context pattern that should activate this command}
- {User request pattern that matches this command}
- {Scenario when this command is appropriate}

## Directives

[REQUIRED]
- {Action that MUST be performed}
- {Action that MUST be performed}
- {Action that MUST be performed}

[OPTIONAL]
- {Enhancement or optimization that CAN be performed}
- {Enhancement or optimization that CAN be performed}

[FORBIDDEN]
- {Action that MUST NOT be performed}
- {Constraint that MUST be respected}

## Workflow
1. {Essential step 1}
2. {Essential step 2}
3. {Essential step 3}

## Configuration
{Only include if requires-config: true}

Required from PROJECT_CONFIG.yaml:
- {CONFIG_VAR}: {description and possible values}
- {CONFIG_VAR}: {description and possible values}

## Examples

PATTERN: /{namespace}:{command} {template-args}
RESULT: {Expected outcome}

PATTERN: /{namespace}:{command} {variant-args} --flag
RESULT: {Expected outcome with flag}

## Reference
{Optional: Link to _reference.md for shared patterns}
See .claude/commands/{namespace}/_reference.md for:
- {Shared pattern 1}
- {Shared pattern 2}
```

---

## Section Guidelines

### YAML Frontmatter

**Required fields:**
- `name`: Command name (no slashes, lowercase, hyphens)
- `description`: One-line summary in quotes
- `category`: One of workflow|utility|special
- `complexity`: One of basic|standard|advanced
- `requires-config`: true if uses PROJECT_CONFIG variables

**Examples:**
```yaml
---
name: implement
description: "Feature implementation with intelligent coordination"
category: workflow
complexity: standard
requires-config: true
---
```

### Purpose Section

**Format:** One clear sentence

**Good:**
- "Execute tests with coverage analysis and quality reporting"
- "Orchestrate GitHub issue implementation via Task subprocess"
- "Analyze code quality, security, performance, and architecture"

**Bad:**
- "This command helps you run tests..." (too conversational)
- "Testing and validation" (too vague)
- Multiple sentences or paragraphs (too verbose)

### Triggers Section

**Format:** Bullet list of patterns

**Good:**
- "Feature development requests (components, APIs, services)"
- "Test execution needs (unit, integration, property-based)"
- "Code quality assessment for projects or components"

**Bad:**
- Natural language narratives
- Examples instead of patterns
- Technology-specific details

### Directives Section

**Must have three subsections:**
- `[REQUIRED]`: Actions that MUST happen
- `[OPTIONAL]`: Enhancements that CAN happen
- `[FORBIDDEN]`: Constraints that MUST NOT be violated

**Format:** Imperative bullet points

**Good:**
```markdown
[REQUIRED]
- Analyze requirements and detect context from PROJECT_CONFIG
- Generate implementation following {FRAMEWORK} patterns
- Apply security validation throughout development

[OPTIONAL]
- Use {ANALYSIS_TOOL} for complex planning
- Generate comprehensive test coverage

[FORBIDDEN]
- Skip security validation
- Generate incomplete implementations
```

**Bad:**
- "You should analyze..." (too conversational)
- "The system will..." (not directive)
- Emoji (🚨, ✅, ❌) instead of bracket notation

### Workflow Section

**Format:** 3-5 numbered steps (prefer 3)

**Good:**
```markdown
1. Analyze: Parse requirements → detect context
2. Implement: Generate code → validate → test
3. Finalize: Update docs → verify quality gates
```

**Bad:**
- 7+ steps (violates KISS)
- Verbose explanations per step
- Nested sub-steps

### Configuration Section

**Only include if `requires-config: true`**

**Format:** List variables from PROJECT_CONFIG.yaml

**Good:**
```markdown
## Configuration

Required from PROJECT_CONFIG.yaml:
- TEST_FRAMEWORK: Testing tool (tools.test_runner)
- BUILD_TOOL: Build command (tools.build)
```

**Bad:**
- Inline configuration instead of referencing PROJECT_CONFIG
- Hardcoded technology names
- Configuration embedded in other sections

### Examples Section

**Format:** PATTERN → RESULT pairs

**Good:**
```markdown
PATTERN: /sc:test --coverage
RESULT: Full test suite with coverage report

PATTERN: /sc:test src/auth --type unit
RESULT: Unit tests for auth module only
```

**Bad:**
- Story-based walkthroughs
- Verbose natural language explanations
- Technology-specific examples without config variables

### Reference Section

**Optional:** Link to shared patterns

**Good:**
```markdown
## Reference
See .claude/commands/gh/_gh-reference.md for:
- Rate limiting patterns
- Label sync timing
- Parent-child relationships
```

**Bad:**
- Inline documentation of shared patterns
- Duplicating content from reference files

---

## Token Efficiency Rules

### Do This (Agent-First)
- Use bracket notation: `[REQUIRED]`, `[OPTIONAL]`, `[FORBIDDEN]`
- Use imperative commands: "Execute tests", "Validate results"
- Use PATTERN→RESULT format for examples
- Use bullet lists for directives
- Reference external docs instead of duplicating

### Don't Do This (Human-Readable Bloat)
- ❌ Emoji: 🚨, ✅, ❌, ⛔
- ❌ "Context Framework Note" preambles
- ❌ "Behavioral Flow" narrative sections
- ❌ "Key Patterns", "Tool Coordination", "MCP Integration" sections
- ❌ "Boundaries" sections (use [FORBIDDEN] instead)
- ❌ Story-based examples
- ❌ Conversational tone ("This command helps you...")

---

## Consistency Checklist

Before finalizing a command, verify:

- [ ] YAML frontmatter has all required fields
- [ ] No emojis anywhere (use bracket notation)
- [ ] Purpose is one sentence
- [ ] Triggers are bullet list of patterns
- [ ] Directives have [REQUIRED]/[OPTIONAL]/[FORBIDDEN] sections
- [ ] Workflow is 3-5 steps maximum
- [ ] Examples use PATTERN→RESULT format
- [ ] No technology hardcoding (use {CONFIG_VAR} references)
- [ ] No archived/commented sections (DELETE, don't comment)
- [ ] No "Context Framework Note" or similar preambles
- [ ] Total length < 150 lines (target: 60-80 lines)

---

## Migration from Old Format

**Remove these sections entirely:**
- "Context Framework Note"
- "Behavioral Flow" (replace with Workflow)
- "MCP Integration" (mention in Configuration if needed)
- "Tool Coordination" (agents know tools)
- "Key Patterns" (redundant with Directives)
- "Boundaries" (replace with [FORBIDDEN])

**Transform these sections:**
- "Will/Will Not" → `[REQUIRED]` and `[FORBIDDEN]`
- Emoji markers → Bracket notation
- Story examples → PATTERN→RESULT
- 5+ steps → 3 essential steps

**Extract these to PROJECT_CONFIG:**
- Technology names (pytest, typer, etc.)
- Tool commands (how to run tests, build, etc.)
- Framework preferences
- Agent persona mappings

---

## Example: Complete Command

```markdown
---
name: test
description: "Execute tests with coverage analysis and quality reporting"
category: utility
complexity: standard
requires-config: true
---

# /sc:test

## Purpose
Execute tests with coverage analysis, quality gates, and actionable reporting.

## Triggers
- Test execution requests (unit, integration, property-based)
- Coverage analysis and quality gate validation
- Test failure analysis and debugging
- Continuous testing during development

## Directives

[REQUIRED]
- Discover tests using {TEST_FRAMEWORK} conventions
- Execute tests with monitoring and progress tracking
- Generate coverage reports with quality metrics
- Report failures with actionable diagnostics

[OPTIONAL]
- Use {BROWSER_TEST_TOOL} for HTML report validation
- Enable watch mode for continuous testing
- Run property-based tests for edge case discovery

[FORBIDDEN]
- Execute tests without proper environment setup
- Ignore test failures or quality gate violations
- Modify test framework configuration without permission

## Workflow
1. Discover: Categorize tests → determine runner from PROJECT_CONFIG
2. Execute: Run {TEST_FRAMEWORK} → monitor progress → collect results
3. Report: Generate coverage → validate quality gates → provide recommendations

## Configuration

Required from PROJECT_CONFIG.yaml:
- TEST_FRAMEWORK: Testing tool (tools.test_runner)
- TEST_COVERAGE: Coverage command (tools.test_coverage)
- MIN_COVERAGE: Minimum coverage threshold (quality_gates.min_coverage)

## Examples

PATTERN: /sc:test
RESULT: Full test suite with coverage report

PATTERN: /sc:test --coverage
RESULT: Tests with detailed coverage metrics

PATTERN: /sc:test src/auth --type unit
RESULT: Unit tests for auth module only

PATTERN: /sc:test --watch
RESULT: Continuous testing on file changes
```

**Line count:** 68 lines
**Token count:** ~550 tokens
**Comparison:** Old format would be ~110 lines, ~900 tokens (38% savings)

---

**Last Updated:** 2025-11-22
**Maintainer:** Keep synchronized with PROJECT_CONFIG.yaml schema
**Usage:** All new commands must follow this template exactly
