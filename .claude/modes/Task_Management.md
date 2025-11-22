# Task Management Mode

## Triggers
Operations with >3 steps, multiple file/directory scope (>2 directories OR >3 files), complex dependencies, --task-manage or --delegate flag

## Task Hierarchy with Memory

[PLAN] **Plan** → write_memory("plan", goal_statement)
→ [PHASE] **Phase** → write_memory("phase_X", milestone)
  → [TASK] **Task** → write_memory("task_X.Y", deliverable)
    → [TODO] **Todo** → Track tasks + write_memory("todo_X.Y.Z", status)

## Memory Operations

**Session Start**:
1. list_memories() → Show existing task state
2. read_memory("current_plan") → Resume context
3. think_about_collected_information() → Understand where we left off

**During Execution**:
1. write_memory("task_2.1", "completed: auth middleware")
2. think_about_task_adherence() → Verify on track
3. Update task status in parallel
4. write_memory("checkpoint", current_state) every 30min

**Session End**:
1. think_about_whether_you_are_done() → Assess completion
2. write_memory("session_summary", outcomes)
3. delete_memory() for completed temporary items

## Execution Pattern

1. **Load**: list_memories() → read_memory() → Resume state
2. **Plan**: Create hierarchy → write_memory() for each level
3. **Track**: Task tracking + memory updates in parallel
4. **Execute**: Update memories as tasks complete
5. **Checkpoint**: Periodic write_memory() for state preservation
6. **Complete**: Final memory update with outcomes

## Tool Selection

| Task Type | Primary Tool | Memory Key |
|-----------|-------------|------------|
| Analysis | sequential-thinking | "analysis_results" |
| Symbol Operations | Serena MCP | "refactoring_state" |
| Testing | Project test framework | "test_results" |
| Documentation | Context7 MCP | "doc_patterns" |

## Memory Schema

**State** (current progress):
- `state_plan`: Overall goal
- `state_phase_N`: Current phase (1-5)
- `state_task_N.M`: Task status

**Checkpoints** (recovery points):
- `checkpoint_[timestamp]`: State snapshots

**Metadata** (context):
- `meta_blockers`: Active impediments
- `meta_decisions`: Key choices
