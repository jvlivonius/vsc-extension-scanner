# Rules Quick Reference

**Decision trees, quick actions, and examples for rapid decision-making.**

## Critical Decision Flows

**🔴 Before Any File Operations**
```
File operation needed?
├─ Writing/Editing? → Read existing first → Understand patterns → Edit
├─ Creating new? → Check existing structure → Place appropriately
└─ Safety check → Absolute paths only → No auto-commit
```

**🟡 Starting New Feature**
```
New feature request?
├─ Scope clear? → No → Brainstorm mode first
├─ >3 steps? → Yes → Track tasks systematically
├─ Patterns exist? → Yes → Follow exactly
├─ Tests available? → Yes → Run before starting
└─ Framework deps? → Check package.json first
```

**🟢 Tool Selection Matrix (Python CLI)**
```
Task type → Best tool:
├─ Multi-file edits → Multiple parallel Edits
├─ Symbol operations → Serena MCP > manual search
├─ Complex analysis → sequential-thinking MCP > native reasoning
├─ Code search → Grep > bash grep
├─ Library docs → Context7 MCP > web search
└─ Testing → pytest + hypothesis > manual tests
```

## Priority-Based Quick Actions

### 🔴 CRITICAL (Never Compromise)
- `git status && git branch` before starting
- Read before Write/Edit operations
- Feature branches only, never main/master
- Root cause analysis, never skip validation
- Absolute paths, no auto-commit

### 🟡 IMPORTANT (Strong Preference)
- Track tasks for >3 step operations
- Complete all started implementations
- Build only what's asked (MVP first)
- Professional language (no marketing superlatives)
- Clean workspace (remove temp files)

### 🟢 RECOMMENDED (Apply When Practical)
- Parallel operations over sequential
- Descriptive naming conventions
- MCP tools over basic alternatives
- Batch operations when possible
