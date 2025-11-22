---
name: issues-implement
description: "GitHub issue implementation orchestration via Task subprocess"
category: workflow
complexity: advanced
requires-config: false
---

# /gh:implement-issue

## Purpose
Orchestrate GitHub issue implementation using Task tool subprocess isolation with guaranteed status transitions.

## Triggers
- GitHub issue implementation requests
- Issues labeled as "agent-ready"
- Workflow requiring GitHub Projects status transitions
- Parent feature issues with sub-task coordination

## Directives

[CRITICAL]: You are an ORCHESTRATOR, not an IMPLEMENTER

[REQUIRED]
- Validate issue prerequisites using validation script before starting
- Use Task tool to spawn implementation subagent (subprocess isolation)
- Use Bash exclusively for gh CLI, git operations, validation scripts
- Manage GitHub Projects status transitions via bash checkpoints
- Create pull request from subagent implementation results
- Update issue status to "In Review" after PR creation
- Handle parent-child issue relationships for feature coordination

[OPTIONAL]
- Add implementation notes to issue comments
- Request review from specific team members
- Apply additional labels based on implementation type
- Create follow-up issues for discovered improvements

[FORBIDDEN]
- Implement code yourself (use Task tool subprocess for all implementation)
- Read implementation files directly (orchestrator role only)
- Use Edit/Write tools for code changes (subagent responsibility)
- Use MCP tools like serena, sequential-thinking (subagent gets full MCP access)
- Skip validation or status transition checkpoints
- Proceed if validation fails

## Workflow
1. Validate: Run `validate-agent-ready.sh` → verify prerequisites → fail fast if not ready
2. Fetch: Use gh CLI to get issue metadata → extract requirements and context
3. Orchestrate: Spawn Task subprocess → provide full issue context → wait for JSON result
4. Finalize: Create PR from results → update status via `update-status.sh` → verify transition

## Configuration

Validation scripts (see scripts/github-projects/README.md):
- validate-agent-ready.sh: Issue readiness verification
- update-status.sh: GitHub Projects status transitions
- manage-issue-relationships.sh: Parent-child relationship management

Status transitions enforced:
- Todo → In Progress (before spawning subagent)
- In Progress → In Review (after PR creation)
- In Review → Done (after PR merge, manual or automated)

## Examples

PATTERN: /gh:implement-issue 142
RESULT: Validation → Status "In Progress" → Task spawn → Implementation → PR → Status "In Review"

PATTERN: /gh:implement-issue 142 --dry-run
RESULT: Validation and planning only, no actual implementation

## Task Subprocess Pattern

**Orchestrator Responsibilities:**
- GitHub API interactions (gh CLI)
- Status field transitions (GraphQL mutations)
- PR creation and metadata management
- Validation checkpoint enforcement

**Subagent Responsibilities (via Task tool):**
- Documentation reading
- Branch creation and git operations
- Code implementation with full MCP access
- Test execution and validation
- Commit creation
- Return structured JSON result

**JSON Result Schema:**
```json
{
  "status": "success|failed",
  "branch": "feature/branch-name",
  "commit_sha": "abc123...",
  "files_changed": ["file1.py", "file2.py"],
  "tests_passed": true,
  "coverage": 87.5,
  "error_message": null
}
```

## Status Transition Script

**Critical Pattern:**
```bash
# BEFORE spawning subagent
if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Progress"; then
    echo "[FAILED] Status transition failed"
    exit 1
fi

# AFTER PR creation
if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Review"; then
    echo "[WARNING] Manual status update needed"
    # Non-blocking - PR already created
fi
```

**Guarantees:**
- 2-second API settle time after mutations
- Verification query confirms field update
- Exit code 1 on failure (before subagent spawn)
- Warning only for post-PR failures (non-blocking)

## Error Handling

| Error | Response | Recovery |
|-------|----------|----------|
| Validation fails | Halt workflow, exit 1 | Fix issue prerequisites |
| Status transition fails (before) | Halt workflow, exit 1 | Check GitHub Projects config |
| Subagent implementation fails | Keep "In Progress" | Add "needs-human-help" label |
| Status transition fails (after PR) | Log warning, continue | Manual status update needed |
| PR creation fails | Keep "In Progress" | Debug gh CLI, retry |

## Feature Implementation Pattern

**Parent Issue Detection:**
- Query: `gh issue view <N> --json parent`
- If parent exists → Feature issue
- If has sub-issues → Feature issue

**Feature Workflow:**
1. Validate: All sub-tasks exist and dependencies resolved
2. Build dependency graph: Topological ordering of sub-tasks
3. Single branch strategy: One feature branch for all sub-tasks
4. Sequential implementation: Implement sub-tasks in dependency order
5. One commit per sub-task: Clear atomic changes
6. Single PR: Closes all sub-tasks and parent feature
7. Integration tests: Feature-level validation after PR merge

**Reference:** See docs/guides/FEATURE_IMPLEMENTATION.md

## Reference
See .claude/commands/gh/_gh-reference.md for:
- Rate limiting patterns
- Label sync timing
- Parent-child relationships
- Common error patterns
- GraphQL query templates
- Validation checklist
