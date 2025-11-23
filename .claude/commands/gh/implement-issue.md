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
- Handle parent-child issue relationships for feature coordination
- Update status of all parent AND child issues during workflow execution:
  - Backlog → Todo (after successful readiness verification)
  - Todo → In Progress (before spawning subagent)
  - In Progress → In Review (after PR creation)
  - In Review → Done (after PR merge, manual or automated)

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

### Single-Task Implementation
1. **Validate**: Run `validate-agent-ready.sh` → verify prerequisites → fail fast if not ready
2. **Fetch**: Use gh CLI to get issue metadata → extract requirements and context
3. **Update Status**: Set issue to "In Progress" → verify transition
4. **Orchestrate**: Spawn Task subprocess → provide full issue context → wait for JSON result
5. **Validate Response**: Check JSON format with `validate-task-response.sh` → fail if invalid
6. **Update Acceptance Criteria**: Parse issue body → check completed AC boxes (if applicable)
7. **Create PR**: Generate pull request from results → link to issue
8. **Update Status**: Set issue to "In Review" → verify transition

### Feature Implementation (Parent with Sub-Tasks)
1. **Validate**: Run `validate-agent-ready.sh --feature-mode` → verify all sub-tasks ready
2. **Fetch**: Get parent metadata + query all sub-task relationships
3. **Update Status (Parent)**: Set parent to "In Progress" → verify transition
4. **For Each Sub-Task** (in dependency order):
   a. **Update Status**: Set sub-task to "In Progress" → verify transition
   b. **Orchestrate**: Spawn Task subprocess → provide sub-task context → wait for JSON result
   c. **Validate Response**: Check JSON format → fail if invalid
   d. **Update Acceptance Criteria**: Check completed AC boxes in sub-task issue body
   e. **Update Status**: Set sub-task to "In Review" → verify transition
5. **Create PR**: Single PR closing all sub-tasks and parent → verify "Closes #N" syntax
6. **Update Parent Acceptance Criteria**: Check parent's AC boxes based on sub-task completion
7. **Update Parent Definition of Done**: Check DoD boxes based on overall feature completion
8. **Update Status (Parent)**: Set parent to "In Review" → verify transition

## Configuration

Workflow scripts (see scripts/github-projects/README.md):
- **validate-agent-ready.sh**: Issue readiness verification (supports --feature-mode)
- **update-status.sh**: GitHub Projects status transitions (GraphQL mutations)
- **manage-issue-relationships.sh**: Parent-child relationship management
- **validate-task-response.sh**: Task subprocess JSON response validation
- **update-acceptance-criteria.sh**: Check AC boxes in issue body (idempotent)

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
- **Return ONLY pure JSON** (no prose, no markdown code blocks, no explanations)

**JSON Result Schema:**
```json
{
  "status": "success|failed",
  "branch": "feature/branch-name",
  "commit_sha": "abc123...",
  "files_changed": ["file1.py", "file2.py"],
  "tests_passed": true,
  "coverage": 87.5,
  "error_message": null,
  "issue_number": 1234
}
```

**CRITICAL Output Format Rules:**
- Response MUST be valid JSON parseable by `jq`
- NO prose wrapper (e.g., "Here is the result:", "Perfect!")
- NO markdown code blocks (e.g., \`\`\`json)
- NO explanatory text before or after JSON
- ONLY the raw JSON object
- Validated via: `echo "$response" | jq .`

## Status Transition Patterns

### Single-Task Status Updates

```bash
# BEFORE spawning subagent
if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Progress"; then
    echo "[FAILED] Status transition failed"
    exit 1
fi

# AFTER spawning subagent (wait for JSON response)
task_response=$(Task tool result)

# Validate JSON response format
if ! ./scripts/github-projects/validate-task-response.sh "$task_response"; then
    echo "[FAILED] Invalid JSON response from subagent"
    exit 1
fi

# AFTER PR creation
if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Review"; then
    echo "[WARNING] Manual status update needed"
    # Non-blocking - PR already created
fi
```

### Feature Implementation Status Updates

```bash
# Update parent to "In Progress"
if ! ./scripts/github-projects/update-status.sh "$PARENT_NUMBER" "In Progress"; then
    echo "[FAILED] Parent status transition failed"
    exit 1
fi

# Get all sub-task numbers
subtask_numbers=$(./scripts/github-projects/manage-issue-relationships.sh view "$PARENT_NUMBER" | grep -oP '#\K\d+')

# For each sub-task
for subtask in $subtask_numbers; do
    echo "[INFO] Implementing sub-task #$subtask"

    # Update sub-task to "In Progress"
    if ! ./scripts/github-projects/update-status.sh "$subtask" "In Progress"; then
        echo "[FAILED] Sub-task #$subtask status transition failed"
        exit 1
    fi

    # Spawn Task subprocess for sub-task implementation
    task_response=$(Task tool with sub-task context)

    # Validate JSON response
    if ! ./scripts/github-projects/validate-task-response.sh "$task_response"; then
        echo "[FAILED] Invalid JSON response for sub-task #$subtask"
        # Mark sub-task as needing human help
        gh issue edit "$subtask" --add-label "needs-human-help"
        exit 1
    fi

    # Update sub-task to "In Review"
    if ! ./scripts/github-projects/update-status.sh "$subtask" "In Review"; then
        echo "[WARNING] Sub-task #$subtask status update failed (non-blocking)"
    fi
done

# Create single PR closing all sub-tasks and parent
gh pr create --title "..." --body "Closes #$subtask1\nCloses #$subtask2\nCloses #$PARENT_NUMBER"

# Update parent to "In Review"
if ! ./scripts/github-projects/update-status.sh "$PARENT_NUMBER" "In Review"; then
    echo "[WARNING] Parent status update failed (non-blocking)"
fi
```

**Guarantees:**
- 2-second API settle time after mutations
- Verification query confirms field update
- Exit code 1 on failure (before subagent spawn)
- Warning only for post-PR failures (non-blocking)
- All parent AND child issues updated through each transition

## Acceptance Criteria Updates

**After Implementation Completion:**

Use `update-acceptance-criteria.sh` to check completed AC boxes:

```bash
# Single task example
./scripts/github-projects/update-acceptance-criteria.sh 1034 "Security notes visible in HTML reports"
./scripts/github-projects/update-acceptance-criteria.sh 1034 "All 1,224+ existing tests passing"
./scripts/github-projects/update-acceptance-criteria.sh 1034 "New code has 95%+ test coverage"

# Feature parent example (after all sub-tasks complete)
./scripts/github-projects/update-acceptance-criteria.sh 1033 "All sub-tasks completed"
./scripts/github-projects/update-acceptance-criteria.sh 1033 "All acceptance criteria met"
./scripts/github-projects/update-acceptance-criteria.sh 1033 "Documentation updated"
```

**When to Update:**
- After validating Task subprocess JSON response (tests_passed=true, coverage>=target)
- Before updating issue status to "In Review"
- For features: Update sub-task AC after each implementation, parent AC after all sub-tasks complete

**Script Features:**
- Handles special characters automatically (escaping)
- Idempotent (safe to run multiple times)
- Validates criterion exists before updating
- Warns if criterion not found (manual modification detected)

## Subprocess Contract Enforcement

**When spawning Task tool subagents, include this in the prompt:**

```markdown
## CRITICAL: Output Format Contract

You MUST return ONLY the raw JSON object specified below. Do NOT include:
- ❌ Prose explanations ("Here is the result:", "Perfect!", "Let me generate...")
- ❌ Markdown code blocks (\`\`\`json ... \`\`\`)
- ❌ Summary sections or implementation notes
- ❌ Any text before or after the JSON

✅ Return EXACTLY this format:
{"status":"success","branch":"feature/...","commit_sha":"...","files_changed":[...],"tests_passed":true,"coverage":87.5,"error_message":null,"issue_number":1234}

Your response will be validated with: echo "$response" | jq .
If validation fails, the workflow will terminate with an error.
```

**Validation After Task Tool Response:**

```bash
# Capture Task tool response
task_response=$(Task tool execution)

# Validate format
if ! ./scripts/github-projects/validate-task-response.sh "$task_response"; then
    echo "[FAILED] Subagent returned invalid JSON format"
    echo "[FAILED] Response must be pure JSON with no prose wrapper"
    exit 1
fi

# Extract fields
status=$(echo "$task_response" | jq -r '.status')
commit_sha=$(echo "$task_response" | jq -r '.commit_sha')
branch=$(echo "$task_response" | jq -r '.branch')
# ... extract other fields
```

## Error Handling

| Error | Response | Recovery |
|-------|----------|----------|
| Validation fails | Halt workflow, exit 1 | Fix issue prerequisites |
| JSON response invalid | Halt workflow, exit 1 | Fix subagent prompt/contract |
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
