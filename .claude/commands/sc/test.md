---
name: test
description: "Execute tests with coverage analysis (Python CLI - pytest/hypothesis)"
category: utility
complexity: enhanced
# PYTHON CLI OPTIMIZATION: Removed playwright (browser tool, use pytest for Python testing)
mcp-servers: []
personas: [qa-specialist]
---

# /sc:test - Testing and Quality Assurance

## Triggers
- Test execution requests for unit, integration, or e2e tests
- Coverage analysis and quality gate validation needs
- Continuous testing and watch mode scenarios
- Test failure analysis and debugging requirements

## Usage
```
/sc:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]
```

## Behavioral Flow
1. **Discover**: Categorize available tests using runner patterns and conventions
2. **Configure**: Set up appropriate test environment and execution parameters
3. **Execute**: Run tests with monitoring and real-time progress tracking
4. **Analyze**: Generate coverage reports and failure diagnostics
5. **Report**: Provide actionable recommendations and quality metrics

Key behaviors:
- Auto-detect test framework and configuration (pytest, hypothesis)
- Generate comprehensive coverage reports with metrics
- Execute unit, integration, and property-based tests
- Provide intelligent test failure analysis
- Support continuous watch mode for development

## MCP Integration
- **Context7**: Auto-activated for test framework documentation (pytest, hypothesis patterns)
- **quality-engineer agent**: Activated for test analysis and quality assessment
- **Enhanced Capabilities**: Property-based testing, hypothesis strategies, coverage analysis

## Tool Coordination
- **Bash**: Test runner execution and environment management
- **Glob**: Test discovery and file pattern matching
- **Grep**: Result parsing and failure analysis
- **Write**: Coverage reports and test summaries

## Key Patterns
- **Test Discovery**: Pattern-based categorization → appropriate runner selection (pytest)
- **Coverage Analysis**: Execution metrics → comprehensive coverage reporting
- **Property Testing**: Hypothesis strategies → systematic edge case discovery
- **Watch Mode**: File monitoring → continuous test execution

## Examples

### Basic Test Execution
```
/sc:test
# Discovers and runs all tests with standard configuration
# Generates pass/fail summary and basic coverage
```

### Targeted Coverage Analysis
```
/sc:test src/components --type unit --coverage
# Unit tests for specific directory with detailed coverage metrics
```

### Property-Based Testing
```
/sc:test --type property
# Executes hypothesis property-based tests for edge case discovery
# Systematic testing with 1,000+ generated scenarios
```

### Development Watch Mode
```
/sc:test --watch --fix
# Continuous testing with automatic simple failure fixes
# Real-time feedback during development
```

## Boundaries

**Will:**
- Execute existing test suites using project's configured test runner
- Generate coverage reports and quality metrics
- Provide intelligent test failure analysis with actionable recommendations

**Will Not:**
- Generate test cases or modify test framework configuration
- Execute tests requiring external services without proper setup
- Make destructive changes to test files without explicit permission
