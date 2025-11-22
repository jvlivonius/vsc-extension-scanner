---
name: implement
description: "Feature implementation with intelligent coordination"
category: workflow
complexity: standard
requires-config: true
---

# /sc:implement

## Purpose
Implement features with appropriate agent coordination and framework best practices.

## Triggers
- Feature development requests (components, APIs, services)
- Implementation requiring multi-domain expertise
- Code generation with testing and validation
- Framework-specific implementation needs

## Directives

[REQUIRED]
- Analyze requirements and detect technology context from PROJECT_CONFIG
- Activate relevant agents based on feature type (see agent_preferences in config)
- Generate implementation following {FRAMEWORK} best practices
- Apply security validation throughout development
- Create or update tests using {TEST_FRAMEWORK}
- Update documentation for significant changes

[OPTIONAL]
- Use {CODE_DOCS_TOOL} for framework-specific patterns and official documentation
- Use {ANALYSIS_TOOL} for complex multi-step planning and systematic reasoning
- Use {SYMBOL_TOOL} for symbol-based refactoring operations
- Generate comprehensive test coverage including edge cases

[FORBIDDEN]
- Skip security validation or quality gates
- Generate incomplete implementations (no TODOs, stubs, or placeholders)
- Make architectural decisions without consulting appropriate agents
- Implement features conflicting with security policies or architecture constraints
- Override user-specified safety constraints

## Workflow
1. Analyze: Parse requirements → detect context from PROJECT_CONFIG → activate agents
2. Implement: Generate code → apply framework patterns → validate security → create tests
3. Finalize: Run {TEST_RUNNER} → verify quality gates → update documentation

## Configuration

Required from PROJECT_CONFIG.yaml:
- frameworks.*: Framework to use based on feature type
- tools.test_runner: Testing tool for validation
- agent_preferences.implementation: Agents to activate
- mcp_preferences.code_docs: Documentation source
- required_docs.architecture: Architecture patterns reference

## Examples

PATTERN: /sc:implement user authentication --type api
RESULT: API endpoint with auth logic, security validation, tests

PATTERN: /sc:implement scan command --type cli
RESULT: CLI command using {CLI_FRAMEWORK}, input validation, help text

PATTERN: /sc:implement dashboard widget --with-tests
RESULT: Component with comprehensive test coverage

PATTERN: /sc:implement payment processing --safe
RESULT: Implementation with enhanced security validation

## Reference
See .claude/commands/sc/_sc-reference.md for:
- MCP server usage patterns
- Agent selection matrix
- Quality gate validation
- Common workflow patterns
