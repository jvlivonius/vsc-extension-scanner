# Command Framework Migration Guide

**Purpose:** Adapt the .claude/ command framework for other project types (JavaScript, Go, Rust, etc.)

**Current State:** Optimized for Python CLI projects
**Target:** 95% reusable across any technology stack

---

## Quick Start: Adapt for Your Project

### 1. Copy Framework Files

Copy these files to your new project:

```bash
# Core framework (technology-agnostic)
.claude/CLAUDE.md
.claude/RULES_CORE.md
.claude/PRINCIPLES.md
.claude/FLAGS.md
.claude/MODE_LOADER.md
.claude/MCP_LOADER.md
.claude/COMMAND_TEMPLATE.md

# Agent personas (technology-agnostic)
.claude/agents/deep-research-agent.md
.claude/agents/performance-engineer.md
.claude/agents/quality-engineer.md
.claude/agents/root-cause-analyst.md
.claude/agents/security-engineer.md

# Modes (technology-agnostic)
.claude/modes/Brainstorming.md
.claude/modes/Introspection.md
.claude/modes/Orchestration.md
.claude/modes/Task_Management.md
.claude/modes/Token_Efficiency.md

# MCP guidelines (technology-agnostic)
.claude/mcp/Context7.md
.claude/mcp/MCP_Playwright.md
.claude/mcp/Sequential.md
.claude/mcp/Serena.md

# Commands (technology-agnostic after refactoring)
.claude/commands/sc/*.md
.claude/commands/gh/*.md
```

### 2. Create Your PROJECT_CONFIG.yaml

**This is the ONLY file you need to customize for your tech stack.**

---

## JavaScript/TypeScript Project Example

### PROJECT_CONFIG.yaml

```yaml
# Project Metadata
project:
  name: my-typescript-app
  type: node-cli
  language: typescript
  version: "18+"
  description: "TypeScript CLI Application"

# Framework Mappings
frameworks:
  cli: commander
  testing: jest
  property_testing: fast-check
  formatting: chalk
  http: axios
  database: prisma
  build_system: tsc

# Tool Commands
tools:
  # Testing
  test_runner: "jest"
  test_coverage: "jest --coverage"
  test_watch: "jest --watch"
  test_property: "jest --testMatch='**/*.property.test.ts'"

  # Building
  build: "npm run build"
  build_clean: "rm -rf dist/"

  # Quality
  lint: "eslint . --ext .ts,.tsx"
  type_check: "tsc --noEmit"
  format: "prettier --write ."

  # Analysis
  security_scan: "npm audit"
  dependency_check: "npm outdated"
  complexity_check: "plato -r -d reports src"

  # Development
  dev_server: "npm run dev"
  install_dev: "npm install"
  install_deps: "npm ci"

# MCP Server Preferences
mcp_preferences:
  code_docs: context7
  analysis: sequential
  symbols: serena
  browser_testing: playwright

# Agent Persona Preferences
agent_preferences:
  implementation: [typescript-expert, security-engineer]
  testing: [quality-engineer]
  performance: [performance-engineer]
  debugging: [root-cause-analyst]
  refactoring: [typescript-expert, quality-engineer]

# Documentation Requirements
required_docs:
  architecture: "docs/architecture.md"
  security: "docs/security.md"
  testing: "docs/testing.md"
  requirements: "docs/requirements.md"

# Project-Specific Paths
paths:
  source: "src"
  tests: "tests"
  docs: "docs"
  scripts: "scripts"
  build_output: "dist"

# Quality Gates
quality_gates:
  min_coverage: 80
  min_security_coverage: 90
  max_complexity: 15
  architecture_violations: 0
  security_vulnerabilities: 0

# Testing Configuration
testing:
  parallel_workers: 4
  timeout: 30000
  property_test_examples: 100

# Build Configuration
build:
  package_name: my-app
  entry_point: index.js
  target: ES2020
```

### Agent Persona Adjustment (Optional)

If you need TypeScript-specific expertise, create:

```markdown
# .claude/agents/typescript-expert.md
---
name: typescript-expert
description: "Production-ready TypeScript code with type safety"
category: specialized
---

# TypeScript Expert

## Triggers
TypeScript/JavaScript development

## Directives
- Write production-quality TypeScript with strict type checking
- Apply SOLID principles and clean architecture
- Use type guards and discriminated unions
- Implement comprehensive error handling
- Create type-safe interfaces and generics

[Rest follows python-expert.md pattern...]
```

**Then update PROJECT_CONFIG.yaml:**
```yaml
agent_preferences:
  implementation: [typescript-expert, security-engineer]  # Changed from python-expert
```

---

## Go Project Example

### PROJECT_CONFIG.yaml

```yaml
# Project Metadata
project:
  name: my-go-app
  type: go-cli
  language: go
  version: "1.21+"
  description: "Go CLI Application"

# Framework Mappings
frameworks:
  cli: cobra
  testing: testing
  http: net/http
  database: sqlx
  build_system: go

# Tool Commands
tools:
  # Testing
  test_runner: "go test ./..."
  test_coverage: "go test -cover -coverprofile=coverage.out ./..."
  test_watch: "gow test ./..."

  # Building
  build: "go build -o bin/app ./cmd/app"
  build_clean: "rm -rf bin/"

  # Quality
  lint: "golangci-lint run"
  type_check: "go vet ./..."
  format: "gofmt -w ."

  # Analysis
  security_scan: "gosec ./..."
  dependency_check: "go list -m -u all"
  complexity_check: "gocyclo -over 15 ."

  # Development
  dev_server: "go run ./cmd/app"
  install_dev: "go install"
  install_deps: "go mod download"

# MCP Server Preferences
mcp_preferences:
  code_docs: context7
  analysis: sequential
  symbols: serena
  browser_testing: playwright

# Agent Preferences
agent_preferences:
  implementation: [go-expert, security-engineer]
  testing: [quality-engineer]
  performance: [performance-engineer]

# Quality Gates
quality_gates:
  min_coverage: 70
  max_complexity: 10
  architecture_violations: 0

# Testing Configuration
testing:
  parallel_workers: auto
  timeout: 300
```

---

## Rust Project Example

### PROJECT_CONFIG.yaml

```yaml
# Project Metadata
project:
  name: my-rust-app
  type: rust-cli
  language: rust
  version: "1.70+"
  description: "Rust CLI Application"

# Framework Mappings
frameworks:
  cli: clap
  testing: cargo-test
  http: reqwest
  database: diesel
  build_system: cargo

# Tool Commands
tools:
  # Testing
  test_runner: "cargo test"
  test_coverage: "cargo tarpaulin --out Html"
  test_watch: "cargo watch -x test"

  # Building
  build: "cargo build --release"
  build_clean: "cargo clean"

  # Quality
  lint: "cargo clippy -- -D warnings"
  type_check: "cargo check"
  format: "cargo fmt"

  # Analysis
  security_scan: "cargo audit"
  dependency_check: "cargo outdated"

  # Development
  dev_server: "cargo run"
  install_dev: "cargo install --path ."
  install_deps: "cargo fetch"

# MCP Server Preferences
mcp_preferences:
  code_docs: context7
  analysis: sequential
  symbols: serena

# Agent Preferences
agent_preferences:
  implementation: [rust-expert, security-engineer]
  testing: [quality-engineer]
  performance: [performance-engineer]

# Quality Gates
quality_gates:
  min_coverage: 85
  max_complexity: 10
  architecture_violations: 0
  security_vulnerabilities: 0

# Testing Configuration
testing:
  parallel_workers: auto
  timeout: 600
```

---

## What Stays the Same (No Changes Needed)

### Commands
All `/sc:*` and `/gh:*` commands work without modification because they reference PROJECT_CONFIG variables:

```markdown
# Command uses placeholder
Execute {TEST_RUNNER} with coverage analysis

# PROJECT_CONFIG provides actual command
tools:
  test_runner: "pytest tests/"  # Python
  test_runner: "jest"           # JavaScript
  test_runner: "go test ./..."  # Go
  test_runner: "cargo test"     # Rust
```

### Agents
All agent personas are technology-agnostic except the language expert:

**Keep as-is:**
- security-engineer (OWASP applies to all languages)
- quality-engineer (testing principles universal)
- performance-engineer (profiling concepts universal)
- root-cause-analyst (debugging systematic)

**Customize:**
- python-expert → typescript-expert, go-expert, rust-expert, etc.

### Modes
All modes are technology-agnostic:
- Brainstorming (universal exploration patterns)
- Introspection (meta-analysis universal)
- Token_Efficiency (symbol compression universal)
- Orchestration (tool coordination universal)
- Task_Management (workflow universal)

### MCP Guidelines
All MCP usage guidelines are technology-agnostic:
- Context7 works for any language documentation
- Sequential works for any complex analysis
- Serena works for any language symbols
- Playwright works for any HTML output

---

## Adaptation Checklist

- [ ] Copy .claude/ framework files to new project
- [ ] Create PROJECT_CONFIG.yaml for your tech stack
- [ ] Update `project.name`, `project.type`, `project.language`
- [ ] Map `frameworks.*` to your technology choices
- [ ] Define `tools.*` commands for your toolchain
- [ ] Set `quality_gates.*` to your standards
- [ ] (Optional) Create language-specific expert agent
- [ ] (Optional) Update `agent_preferences.*` if custom agent created
- [ ] Test all /sc:* commands work with your config
- [ ] Verify {CONFIG_VAR} substitution works correctly

---

## Validation

### Test Command Adaptation

```bash
# Test that commands use your config
/sc:test
# Should execute: YOUR_tools.test_runner (not hardcoded pytest)

/sc:build
# Should execute: YOUR_tools.build (not hardcoded "python -m build")

/sc:implement --help
# Should show YOUR_frameworks references
```

### Verify Config Variables

Commands should reference:
- `{TEST_FRAMEWORK}` → your `tools.test_runner`
- `{BUILD_TOOL}` → your `tools.build`
- `{CLI_FRAMEWORK}` → your `frameworks.cli`
- `{MIN_COVERAGE}` → your `quality_gates.min_coverage`

If you see hardcoded values (pytest, typer, etc.), that command needs refactoring.

---

## Common Issues

### Issue: Command mentions pytest/typer/python

**Cause:** Command not yet refactored to use PROJECT_CONFIG
**Fix:** That command is in the "remaining to refactor" list (see REFACTORING_SUMMARY.md)

### Issue: {CONFIG_VAR} not substituted

**Cause:** Missing entry in PROJECT_CONFIG.yaml
**Fix:** Add the variable to appropriate section:
```yaml
tools:
  test_runner: "your-test-command"  # Add missing tool
```

### Issue: Agent mentions Python-specific patterns

**Cause:** Using python-expert instead of language-specific expert
**Fix:** Create language-expert.md and update agent_preferences

---

## Benefits of This Approach

### Single Config File
Change tech stack = Edit 1 YAML file (not 17 command files)

### Portable Framework
Same .claude/commands/ folder works for Python, JavaScript, Go, Rust

### Consistent Commands
/sc:implement, /sc:test, /sc:build work identically across projects

### Easy Maintenance
Update tool command in one place, affects all commands automatically

### Team Sharing
Share .claude/ framework across team, customize PROJECT_CONFIG per project

---

## Advanced: Multi-Language Projects

For projects using multiple languages (e.g., Python backend + TypeScript frontend):

```yaml
# PROJECT_CONFIG.yaml
project:
  type: full-stack
  languages: [python, typescript]

frameworks:
  # Python
  python_cli: typer
  python_testing: pytest

  # TypeScript
  ts_cli: commander
  ts_testing: jest

tools:
  # Python
  python_test: "pytest tests/"
  python_build: "python -m build"

  # TypeScript
  ts_test: "jest"
  ts_build: "npm run build"

# Commands can use context-specific variables
# /sc:test --lang python → uses python_test
# /sc:test --lang typescript → uses ts_test
```

---

## Support

**Questions?** See:
- COMMAND_TEMPLATE.md for command structure
- REFACTORING_SUMMARY.md for refactoring status
- PROJECT_CONFIG.yaml for example configuration

**Contributing:** If you adapt this framework for a new language, consider contributing your PROJECT_CONFIG.yaml example!

---

**Last Updated:** 2025-11-22
**Framework Version:** v1.0 (Post-Refactoring)
**Compatibility:** Requires refactored commands (see REFACTORING_SUMMARY.md for status)
