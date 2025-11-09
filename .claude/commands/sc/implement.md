---
name: implement
description: "Code implementation with intelligent persona activation (Python CLI optimized)"
category: workflow
complexity: standard
# PYTHON CLI OPTIMIZATION: Removed magic, playwright (frontend/browser tools)
mcp-servers: [context7, sequential, serena]
personas: [architect, backend, security, qa-specialist]
---

# /sc:implement - Feature Implementation

> **Context Framework Note**: This behavioral instruction activates when Claude Code users type `/sc:implement` patterns. It guides Claude to coordinate specialist personas and MCP tools for comprehensive implementation.

## Triggers
- Feature development requests for components, APIs, or complete functionality
- Code implementation needs with framework-specific requirements
- Multi-domain development requiring coordinated expertise
- Implementation projects requiring testing and validation integration

## Context Trigger Pattern
```
/sc:implement [feature-description] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]
```
**Usage**: Type this in Claude Code conversation to activate implementation behavioral mode with coordinated expertise and systematic development approach.

## Behavioral Flow
1. **Analyze**: Examine implementation requirements and detect technology context
2. **Plan**: Choose approach and activate relevant personas for domain expertise
3. **Generate**: Create implementation code with framework-specific best practices
4. **Validate**: Apply security and quality validation throughout development
5. **Integrate**: Update documentation and provide testing recommendations

Key behaviors:
- Context-based agent activation (python-expert, security-engineer, quality-engineer, performance-engineer)
- Framework-specific implementation via Context7 integration
- Systematic multi-component coordination via sequential-thinking
- Comprehensive testing integration with pytest for validation

## MCP Integration (Python CLI Optimized)
- **Context7**: Python patterns, pytest/hypothesis/typer/rich official docs ✅
- **sequential-thinking**: Complex multi-step analysis and implementation planning ✅
- **Serena**: Symbol operations, refactoring, session persistence ✅

<!-- ARCHIVED MCP INTEGRATION (Frontend/Browser):
- Magic MCP: UI generation (archived - use Rich for terminal UI)
- Playwright MCP: Browser testing (archived - use pytest for Python testing)
-->

## Tool Coordination
- **Write/Edit**: Code generation and modification for implementation (use multiple parallel Edits for multi-file)
- **Read/Grep/Glob**: Project analysis and pattern detection for consistency
- **Task Tracking**: Progress tracking for complex multi-file implementations
- **Delegation**: For large-scale feature development requiring systematic coordination

## Key Patterns
- **Context Detection**: Tech stack → appropriate agent and MCP activation
- **Implementation Flow**: Requirements → code generation → validation → integration
- **Multi-Agent Coordination**: python-expert + security-engineer + quality-engineer → comprehensive solutions
- **Quality Integration**: Implementation → testing → documentation → validation

## Examples

### CLI Command Implementation
```
/sc:implement scan command --type cli --framework typer
# python-expert generates CLI command with typer best practices
# security-engineer ensures input validation and safe execution
```

### API Service Implementation
```
/sc:implement user authentication API --type api --safe --with-tests
# Backend persona handles server-side logic and data processing
# Security persona ensures authentication best practices
```

### Full-Stack Feature
```
/sc:implement payment processing system --type feature --with-tests
# Multi-agent coordination: python-expert, security-engineer, quality-engineer
# sequential-thinking breaks down complex implementation steps
```

### Framework-Specific Implementation
```
/sc:implement dashboard widget --framework vue
# Context7 MCP provides Vue-specific patterns and documentation
# Framework-appropriate implementation with official best practices
```

## Boundaries

**Will:**
- Implement features with intelligent persona activation and MCP coordination
- Apply framework-specific best practices and security validation
- Provide comprehensive implementation with testing and documentation integration

**Will Not:**
- Make architectural decisions without appropriate persona consultation
- Implement features conflicting with security policies or architectural constraints
- Override user-specified safety constraints or bypass quality gates
