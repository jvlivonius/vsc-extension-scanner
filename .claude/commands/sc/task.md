---
name: task
description: "Execute complex tasks with intelligent workflow management"
category: special
complexity: advanced
requires-config: true
---

# /sc:task

## Purpose
Execute complex tasks with multi-agent coordination, hierarchical breakdown, and cross-session persistence.

## Triggers
- Complex tasks requiring multi-agent coordination
- Projects needing structured workflow management
- Operations requiring intelligent MCP server routing
- Tasks benefiting from systematic execution and progressive enhancement
- Cross-session task persistence needs

## Directives

[REQUIRED]
- Parse task requirements and determine optimal execution strategy
- Route to appropriate MCP servers based on task type
- Activate relevant agents from PROJECT_CONFIG agent_preferences
- Execute tasks with intelligent workflow management
- Apply quality gates and comprehensive task completion verification
- Persist task state using {SYMBOL_TOOL} memory operations

[OPTIONAL]
- Use {ANALYSIS_TOOL} for complex multi-step task analysis
- Use {CODE_DOCS_TOOL} for framework-specific patterns
- Enable parallel execution for independent sub-tasks
- Generate comprehensive task completion reports
- Create hierarchical task breakdown (Epic → Story → Task → Subtask)

[FORBIDDEN]
- Execute simple tasks that don't require advanced orchestration
- Compromise quality standards for speed
- Operate without proper validation and quality gates
- Skip task persistence for complex multi-session operations

## Workflow
1. Plan: Break down task → identify dependencies → allocate resources
2. Coordinate: Activate agents → route to MCPs → execute in parallel where possible
3. Integrate: Collect results → validate completion → persist state via {SYMBOL_TOOL}

## Configuration

Required from PROJECT_CONFIG.yaml:
- mcp_preferences.*: MCP server routing preferences
- agent_preferences.*: Agent activation based on task type
- quality_gates.*: Quality thresholds for validation
- tools.*: Tool commands for execution

Task hierarchy levels:
- Epic: Large multi-session objectives
- Story: Coordinated feature work
- Task: Individual deliverables
- Subtask: Atomic operations

## Examples

PATTERN: /sc:task create "authentication system" --strategy systematic
RESULT: Comprehensive task breakdown with multi-domain coordination

PATTERN: /sc:task execute "feature backlog" --strategy agile --delegate
RESULT: Iterative task execution with cross-session persistence

PATTERN: /sc:task execute "platform migration" --parallel
RESULT: Parallel execution across multiple technical domains

## Reference
See .claude/commands/sc/_sc-reference.md for:
- Task workflow patterns
- Agent selection matrix
- MCP server usage patterns
- Session persistence patterns
