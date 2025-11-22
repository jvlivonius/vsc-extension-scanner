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
- Test execution requests (unit, integration, property-based, E2E)
- Coverage analysis and quality gate validation
- Test failure analysis and debugging
- Continuous testing during development

## Directives

[REQUIRED]
- Discover tests using {TEST_FRAMEWORK} conventions
- Execute tests with monitoring and progress tracking
- Generate coverage reports with quality metrics
- Validate against {MIN_COVERAGE}% threshold
- Report failures with actionable diagnostics
- Verify zero security vulnerabilities

[OPTIONAL]
- Use {BROWSER_TEST_TOOL} for HTML report E2E testing and accessibility validation
- Enable watch mode for continuous testing on file changes
- Run property-based tests for systematic edge case discovery
- Generate HTML coverage reports for detailed analysis
- Execute parallel test runs for faster feedback

[FORBIDDEN]
- Execute tests without proper environment setup
- Ignore test failures or quality gate violations
- Modify test framework configuration without permission
- Skip security or architecture tests
- Proceed with failing quality gates

## Workflow
1. Discover: Categorize tests → determine runner from PROJECT_CONFIG
2. Execute: Run {TEST_RUNNER} → monitor progress → collect results
3. Report: Generate coverage → validate quality gates → provide recommendations

## Configuration

Required from PROJECT_CONFIG.yaml:
- tools.test_runner: Testing tool command
- tools.test_coverage: Coverage analysis command
- quality_gates.min_coverage: Minimum coverage threshold
- mcp_preferences.browser_testing: E2E testing tool for HTML reports
- testing.parallel_workers: Parallel execution setting

## Examples

PATTERN: /sc:test
RESULT: Full test suite with coverage report, quality gate validation

PATTERN: /sc:test --coverage
RESULT: Tests with detailed coverage metrics and threshold validation

PATTERN: /sc:test src/auth --type unit
RESULT: Unit tests for auth module only

PATTERN: /sc:test --watch
RESULT: Continuous testing on file changes, real-time feedback

PATTERN: /sc:test --type html
RESULT: Browser-based HTML report testing (rendering, accessibility, interactions)

PATTERN: /sc:test --type property
RESULT: Property-based tests with {PROPERTY_TEST_EXAMPLES} scenarios

## Reference
See .claude/commands/sc/_sc-reference.md for:
- Testing workflow patterns
- Quality gate validation
- MCP tool selection (pytest vs playwright)
- Parallel execution patterns
