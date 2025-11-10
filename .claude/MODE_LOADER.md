# MODE Activation System

MODEs load conditionally based on context detection for token efficiency.

## Auto-Activation Triggers

**Brainstorming Mode** (`modes/Brainstorming.md`):
- Keywords: "explore", "not sure", "thinking about", "maybe", "could we"
- Vague project requests or uncertainty indicators
- Manual: `--brainstorm` or `--bs` flag
- @modes/Brainstorming.md

**Introspection Mode** (`modes/Introspection.md`):
- Error recovery situations or unexpected results
- Keywords: "analyze reasoning", "reflect on", "why did"
- Manual: `--introspect` flag
- @modes/Introspection.md

**Token Efficiency Mode** (`modes/Token_Efficiency.md`):
- Context usage >75%
- Manual: `--uc` or `--ultracompressed` flag
- @modes/Token_Efficiency.md

**Orchestration Mode** (`modes/Orchestration.md`):
- Multi-tool operations (>3 files)
- Performance constraints (>75% resource usage)
- Parallel execution opportunities
- @modes/Orchestration.md

**Task Management Mode** (`modes/Task_Management.md`):
- Operations with >3 steps
- Multiple file/directory scope (>2 directories OR >3 files)
- Manual: `--task-manage` or `--delegate` flag
- @modes/Task_Management.md
