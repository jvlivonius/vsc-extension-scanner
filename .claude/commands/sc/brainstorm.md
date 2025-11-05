---
name: brainstorm
description: "Interactive requirements discovery through Socratic dialogue (Python CLI optimized)"
category: orchestration
complexity: advanced
# PYTHON CLI OPTIMIZATION: Removed magic, playwright, morphllm (frontend/browser tools)
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, backend, security, devops]
---

# /sc:brainstorm - Interactive Requirements Discovery

> **Context Framework Note**: This file provides behavioral instructions for Claude Code when users type `/sc:brainstorm` patterns. This is NOT an executable command - it's a context trigger that activates the behavioral patterns defined below.

## Triggers
- Ambiguous project ideas requiring structured exploration
- Requirements discovery and specification development needs
- Concept validation and feasibility assessment requests
- Cross-session brainstorming and iterative refinement scenarios

## Context Trigger Pattern
```
/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```
**Usage**: Type this pattern in your Claude Code conversation to activate brainstorming behavioral mode with systematic exploration and multi-persona coordination.

## Behavioral Flow
1. **Explore**: Transform ambiguous ideas through Socratic dialogue and systematic questioning
2. **Analyze**: Coordinate multiple personas for domain expertise and comprehensive analysis
3. **Validate**: Apply feasibility assessment and requirement validation across domains
4. **Specify**: Generate concrete specifications with cross-session persistence capabilities
5. **Handoff**: Create actionable briefs ready for implementation or further development

Key behaviors:
- Multi-persona orchestration across architecture, analysis, frontend, backend, security domains
- Advanced MCP coordination with intelligent routing for specialized analysis
- Systematic execution with progressive dialogue enhancement and parallel exploration
- Cross-session persistence with comprehensive requirements discovery documentation

## MCP Integration (Python CLI Optimized)
- **Sequential MCP**: Complex multi-step reasoning for systematic exploration and validation ✅
- **Context7 MCP**: Python library patterns, pytest/hypothesis best practices ✅
- **Serena MCP**: Cross-session persistence, memory management, project context ✅

<!-- ARCHIVED MCPs (Frontend/Browser Tools - Python CLI Optimization):
- Magic MCP: UI/UX feasibility (archived - frontend tool, not applicable to CLI)
- Playwright MCP: Browser testing (archived - E2E web tool, use pytest instead)
- Morphllm MCP: Pattern transformation (archived - use Serena for symbol operations)
-->

## Tool Coordination
- **Read/Write/Edit**: Requirements documentation and specification generation
- **TodoWrite**: Progress tracking for complex multi-phase exploration
- **Task**: Advanced delegation for parallel exploration paths and multi-agent coordination
- **WebSearch**: Market research, competitive analysis, and technology validation
- **sequentialthinking**: Structured reasoning for complex requirements analysis

## Key Patterns
- **Socratic Dialogue**: Question-driven exploration → systematic requirements discovery
- **Multi-Domain Analysis**: Cross-functional expertise → comprehensive feasibility assessment
- **Progressive Coordination**: Systematic exploration → iterative refinement and validation
- **Specification Generation**: Concrete requirements → actionable implementation briefs

## Examples

### Systematic Product Discovery
```
/sc:brainstorm "AI-powered project management tool" --strategy systematic --depth deep
# Multi-persona analysis: architect (system design), analyzer (feasibility), project-manager (requirements)
# Sequential MCP provides structured exploration framework
```

### Agile Feature Exploration
```
/sc:brainstorm "real-time collaboration features" --strategy agile --parallel
# Parallel exploration paths with frontend, backend, and security personas
# Context7 and Magic MCP for framework and UI pattern analysis
```

### Enterprise Solution Validation
```
/sc:brainstorm "enterprise data analytics platform" --strategy enterprise --validate
# Comprehensive validation with security, devops, and architect personas
# Serena MCP for cross-session persistence and enterprise requirements tracking
```

### Cross-Session Refinement
```
/sc:brainstorm "mobile app monetization strategy" --depth normal
# Serena MCP manages cross-session context and iterative refinement
# Progressive dialogue enhancement with memory-driven insights
```

## Boundaries

**Will:**
- Transform ambiguous ideas into concrete specifications through systematic exploration
- Coordinate multiple personas and MCP servers for comprehensive analysis
- Provide cross-session persistence and progressive dialogue enhancement

**Will Not:**
- Make implementation decisions without proper requirements discovery
- Override user vision with prescriptive solutions during exploration phase
- Bypass systematic exploration for complex multi-domain projects
