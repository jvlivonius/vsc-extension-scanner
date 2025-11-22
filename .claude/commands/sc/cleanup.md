---
name: cleanup
description: "Systematically clean up code and optimize project structure"
category: workflow
complexity: standard
requires-config: true
---

# /sc:cleanup

## Purpose
Systematically clean code, remove dead code, and optimize project structure with safety validation.

## Triggers
- Code maintenance and technical debt reduction
- Dead code removal and import optimization
- Project structure improvement and organization
- Codebase hygiene and quality improvement

## Directives

[REQUIRED]
- Analyze cleanup opportunities and safety considerations
- Activate appropriate agents based on cleanup type
- Apply systematic cleanup with dead code detection
- Validate no functionality loss through testing
- Generate cleanup summary with recommendations

[OPTIONAL]
- Use {ANALYSIS_TOOL} for complex multi-step cleanup analysis
- Use {CODE_DOCS_TOOL} for framework-specific cleanup patterns
- Enable interactive mode for complex decisions
- Create backup before aggressive cleanup
- Run {TEST_RUNNER} for validation after cleanup

[FORBIDDEN]
- Remove code without thorough safety analysis
- Override project-specific cleanup exclusions
- Apply cleanup that compromises functionality
- Skip testing validation after cleanup
- Remove code with external dependencies unchecked

## Workflow
1. Analyze: Assess cleanup opportunities → evaluate safety → plan approach
2. Execute: Apply cleanup with validation → use parallel Edits for multi-file
3. Validate: Run {TEST_RUNNER} → verify functionality → generate report

## Configuration

Required from PROJECT_CONFIG.yaml:
- tools.test_runner: Testing for validation
- tools.lint: Code quality tool
- agent_preferences.refactoring: Agents to activate
- mcp_preferences.analysis: Analysis tool

Cleanup types:
- code: Dead code removal
- imports: Unused import cleanup
- files: File organization and structure
- all: Comprehensive cleanup

## Examples

PATTERN: /sc:cleanup src/ --type code --safe
RESULT: Conservative cleanup with automatic safety validation

PATTERN: /sc:cleanup --type imports
RESULT: Unused import removal with framework awareness

PATTERN: /sc:cleanup --type all --interactive
RESULT: Multi-domain cleanup with user guidance for complex decisions

PATTERN: /sc:cleanup components/ --aggressive
RESULT: Thorough cleanup with comprehensive analysis

## Reference
See .claude/commands/sc/_sc-reference.md for:
- Agent selection matrix
- Safety validation patterns
- Testing workflow patterns
