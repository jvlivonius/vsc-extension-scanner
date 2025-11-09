# MODE Activation System

MODEs load conditionally based on context detection for token efficiency.

## Auto-Activation Triggers

**Brainstorming Mode** (`modes/Brainstorming.md`):
- Keywords: "explore", "not sure", "thinking about", "maybe", "could we"
- Vague project requests or uncertainty indicators
- Manual: `--brainstorm` or `--bs` flag

**Introspection Mode** (`modes/Introspection.md`):
- Error recovery situations or unexpected results
- Keywords: "analyze reasoning", "reflect on", "why did"
- Manual: `--introspect` flag

**Token Efficiency Mode** (`modes/Token_Efficiency.md`):
- Context usage >75%
- Manual: `--uc` or `--ultracompressed` flag

**Orchestration Mode** (`modes/Orchestration.md`):
- Multi-tool operations (>3 files)
- Performance constraints (>75% resource usage)
- Parallel execution opportunities

**Task Management Mode** (`modes/Task_Management.md`):
- Operations with >3 steps
- Multiple file/directory scope (>2 directories OR >3 files)
- Manual: `--task-manage` or `--delegate` flag

## Usage

MODEs are **not auto-loaded** - they activate dynamically when triggers are detected or flags are used.

**Full MODE documentation:** See `.claude/modes/` directory
