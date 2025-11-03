# Task Management Mode

**Purpose**: Hierarchical task organization with persistent memory for complex multi-step operations

## Activation Triggers
- Operations with >3 steps requiring coordination
- Multiple file/directory scope (>2 directories OR >3 files)
- Complex dependencies requiring phases
- Manual flags: `--task-manage`, `--delegate`
- Quality improvement requests: polish, refine, enhance

## Task Hierarchy with Memory

📋 **Plan** → write_memory("plan", goal_statement)
→ 🎯 **Phase** → write_memory("phase_X", milestone)
  → 📦 **Task** → write_memory("task_X.Y", deliverable)
    → ✓ **Todo** → TodoWrite + write_memory("todo_X.Y.Z", status)

## Memory Operations

### Session Start
```
1. list_memories() → Show existing task state
2. read_memory("current_plan") → Resume context
3. think_about_collected_information() → Understand where we left off
```

### During Execution
```
1. write_memory("task_2.1", "completed: auth middleware")
2. think_about_task_adherence() → Verify on track
3. Update TodoWrite status in parallel
4. write_memory("checkpoint", current_state) every 30min
```

### Session End
```
1. think_about_whether_you_are_done() → Assess completion
2. write_memory("session_summary", outcomes)
3. delete_memory() for completed temporary items
```

## Execution Pattern

1. **Load**: list_memories() → read_memory() → Resume state
2. **Plan**: Create hierarchy → write_memory() for each level
3. **Track**: TodoWrite + memory updates in parallel
4. **Execute**: Update memories as tasks complete
5. **Checkpoint**: Periodic write_memory() for state preservation
6. **Complete**: Final memory update with outcomes

## Tool Selection (Python CLI)

| Task Type | Primary Tool | Memory Key |
|-----------|-------------|------------|
| Analysis | Sequential MCP | "analysis_results" |
| Symbol Operations | Serena MCP | "refactoring_state" |
| Testing | pytest + property tests | "test_results" |
| Documentation | Context7 MCP | "doc_patterns" |

## Memory Schema

```
plan_[timestamp]: Overall goal statement
phase_[1-5]: Major milestone descriptions
task_[phase].[number]: Specific deliverable status
todo_[task].[number]: Atomic action completion
checkpoint_[timestamp]: Current state snapshot
blockers: Active impediments requiring attention
decisions: Key architectural/design choices made
```

## Example: v3.6 Testability Refactoring

### Session 1: Start Refactoring
```
list_memories() → Check existing state
write_memory("plan_v3.6", "Extract ProgressCallback pattern for testability")
write_memory("phase_1", "Analysis - identify hard-to-test components")
TodoWrite: Create specific refactoring todos
Execute analysis → write_memory("task_1.1", "completed: Found 3 tightly-coupled modules")
```

### Session 2: Resume Implementation
```
list_memories() → Shows plan_v3.6, phase_1, task_1.1
read_memory("plan_v3.6") → Resume refactoring context
think_about_collected_information() → "Analysis complete, start extraction"
write_memory("phase_2", "Implementation - extract callback patterns")
Continue with symbol operations via Serena...
```

### Session 3: Testing & Validation
```
think_about_whether_you_are_done() → "Test coverage validation needed"
Run test suite with new patterns
write_memory("outcome_v3.6", "Refactoring complete, coverage 78.94%")
delete_memory("checkpoint_*") → Clean temporary states
```
