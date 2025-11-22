---
name: analyze
description: "Code analysis across quality, security, performance, and architecture"
category: utility
complexity: basic
requires-config: true
---

# /sc:analyze

## Purpose
Perform comprehensive code analysis across quality, security, performance, and architecture domains.

## Triggers
- Code quality assessment requests
- Security vulnerability scanning and compliance validation
- Performance bottleneck identification
- Architecture review and technical debt assessment

## Directives

[REQUIRED]
- Discover and categorize source files using language detection
- Apply domain-specific analysis techniques based on focus area
- Generate prioritized findings with severity ratings
- Create actionable recommendations with implementation guidance
- Validate against {QUALITY_GATES} thresholds

[OPTIONAL]
- Use {ANALYSIS_TOOL} for complex multi-domain analysis
- Generate HTML reports for detailed visualization
- Provide trend analysis if historical data available
- Include technical debt quantification
- Run external analysis tools via {SECURITY_SCAN}, {COMPLEXITY_CHECK}

[FORBIDDEN]
- Execute dynamic analysis requiring code compilation or runtime
- Modify source code or apply fixes without explicit user consent
- Analyze external dependencies beyond import and usage patterns
- Skip security or architecture validation

## Workflow
1. Discover: Categorize files → determine analysis scope and techniques
2. Analyze: Run domain-specific tools → collect findings → assess severity
3. Report: Generate metrics → validate quality gates → provide recommendations

## Configuration

Required from PROJECT_CONFIG.yaml:
- tools.security_scan: Security analysis tool command
- tools.complexity_check: Complexity analysis tool
- tools.lint: Code quality tool
- quality_gates.*: Analysis thresholds

Analysis domains:
- Quality: Code smells, maintainability, complexity
- Security: Vulnerabilities, OWASP compliance, secret scanning
- Performance: Bottlenecks, inefficiencies, resource usage
- Architecture: Layer violations, dependency issues, pattern compliance

## Examples

PATTERN: /sc:analyze
RESULT: Multi-domain analysis of entire project with comprehensive report

PATTERN: /sc:analyze src/auth --focus security --depth deep
RESULT: Deep security analysis with vulnerability assessment and remediation

PATTERN: /sc:analyze --focus performance --format report
RESULT: HTML report with performance bottleneck identification

PATTERN: /sc:analyze src/components --focus quality --depth quick
RESULT: Rapid quality assessment with code smell detection

## Reference
See .claude/commands/sc/_sc-reference.md for:
- Quality gate patterns
- Domain analysis techniques
- Error handling patterns
