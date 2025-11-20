# GitHub Commands Reference

**Purpose**: Shared reference for all `/gh:*` commands. Eliminate redundancy, maintain consistency.

**Format**: Lookup table optimized for AI consumption. Read this ONCE, reference throughout commands.

---

## Rate Limiting Essentials

### Quick Facts
- **Limit**: 5,000 requests/hour (authenticated)
- **Library**: `scripts/github-projects/rate_limit.sh` (auto-sourced by all scripts)
- **Default Delay**: 0.5s between API calls
- **Guard Threshold**: Block if <20 requests remaining

### API Call Estimates

| Operation | Issues | API Calls |
|-----------|--------|-----------|
| Create from plan | 10 | ~35 |
| Create from plan | 30 | ~105 |
| Implement issue | 1 | ~8-15 |
| Triage (single) | 1 | ~3-5 |
| Triage (batch) | 50 | ~170-250 |
| Milestone sync | 50 | ~60 |
| Milestone report | 50 | ~60 |

### Critical Functions (from rate_limit.sh)

```bash
# 1. Guard at script start (REQUIRED)
rate_limit_guard || exit 1

# 2. Delay in loops (REQUIRED)
for item in $items; do
    gh api "endpoint/$item"
    rate_limit_delay  # 0.5s default
done

# 3. Retry on failures
retry_with_backoff gh api "endpoint"

# 4. Summary at end
rate_limit_summary
```

### Check Before Large Operations

```bash
# Check remaining quota
gh api rate_limit --jq '.rate | "Remaining: \(.remaining)/\(.limit)"'

# If <100 remaining, wait for reset
gh api rate_limit --jq '.rate.reset' | xargs -I {} date -r {}
```

### Batch Size Guidelines

| Remaining | Max Batch Size |
|-----------|----------------|
| >4000 | 100 issues |
| 1000-4000 | 50 issues |
| 500-1000 | 20 issues |
| <500 | Single issue only |

**Reference**: Full guide at [docs/guides/GITHUB_API_RATE_LIMITS.md](../../docs/guides/GITHUB_API_RATE_LIMITS.md)

---

## Label Sync Timing

### How It Works

GitHub Actions workflow syncs Priority/Complexity labels to project fields **asynchronously**.

**Trigger**: `labeled` or `unlabeled` event
**Delay**: 1-5 minutes
**Workflow**: `.github/workflows/sync-project-fields.yml`

### Critical Rule

**Add labels AFTER issue creation** to trigger sync workflow.

```bash
# ✅ CORRECT: Labels added after creation
gh issue create --title "..." --body "..."
gh issue edit <number> --add-label "P1-high,complexity/M"

# ❌ WRONG: Labels during creation (workflow doesn't trigger)
gh issue create --title "..." --body "..." --label "P1-high"
```

### Verification Commands

```bash
# Wait 2-3 minutes after label change, then verify
gh project item-list 3 --format json | jq '.items[] | select(.content.number==<N>)'

# Check workflow runs if sync doesn't occur within 5 minutes
gh run list --workflow=sync-project-fields.yml --limit 5

# Manual sync (if automated sync fails)
./scripts/github-projects/sync-existing-issues.sh
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Sync not occurring | Check GitHub Actions runs for errors |
| Partial sync | Verify labels match format (P0-P3, complexity/XS-XL) |
| Delayed sync (>10 min) | Check workflow status, consider manual sync |

**Reference**: [docs/contributing/GITHUB_PROJECTS.md#automatic-field-sync](../../docs/contributing/GITHUB_PROJECTS.md#automatic-field-sync)

---

## Parent-Child Relationships

### Critical Information

Parent-child relationships **must** use GitHub GraphQL API `addSubIssue` mutation.
**Cannot** be done via REST API or Projects API.

### Correct Approach

```bash
# 1. Get node IDs
PARENT_NODE_ID=$(gh api repos/:owner/:repo/issues/PARENT_NUM --jq '.node_id')
CHILD_NODE_ID=$(gh api repos/:owner/:repo/issues/CHILD_NUM --jq '.node_id')

# 2. Create relationship via GraphQL
gh api graphql -f query='mutation {
  addSubIssue(input: {issueId: "PARENT_NODE_ID", subIssueId: "CHILD_NODE_ID"}) {
    issue { number }
  }
}'
```

### Automated Script (RECOMMENDED)

```bash
./scripts/github-projects/manage-issue-relationships.sh set-parent PARENT_NUM CHILD1 CHILD2 CHILD3
```

### Verification

```bash
# Check parent has sub-issues
gh api repos/:owner/:repo/issues/PARENT_NUM --jq '.sub_issues_summary.total'

# Check child has parent
gh api repos/:owner/:repo/issues/CHILD_NUM --jq '.parent_issue_url'
```

### Common Mistakes

| ❌ WRONG | ✅ CORRECT |
|---------|----------|
| REST API PATCH with `parent_issue_id` | GraphQL `addSubIssue` mutation |
| Projects API "Parent issue" field | GraphQL mutation |
| Issue dependencies API (creates blocked-by) | GraphQL `addSubIssue` |

---

## Blocking Dependencies

### Setup

Use REST API for `blocked-by` relationships (NOT GraphQL).

```bash
# Create blocker relationship
./scripts/github-projects/manage-issue-relationships.sh set-blocker BLOCKER_NUM BLOCKED_NUM
```

### Verification

```bash
# Check blocked-by dependencies
gh api repos/:owner/:repo/issues/BLOCKED_NUM/dependencies/blocked_by --jq '.[].number'
```

**Difference**: Blocking ≠ Parent-Child
- **Blocking**: Issue A blocks issue B (workflow dependency)
- **Parent-Child**: Issue A contains sub-tasks B, C, D (hierarchical structure)

---

## Common Error Patterns

### Dependency Not Resolved

```
Error: Issue #142 has unresolved dependencies
  - #140: OPEN (must be CLOSED)

Action: Wait for dependencies, or remove if incorrect
```

### Missing Required Documentation

```
Error: Issue #142 missing required documentation field
  Expected: "Required Documentation" field with comma-separated doc names

Action: Edit issue → Fill "Required Documentation" field
  Example: "ARCHITECTURE.md, SECURITY.md, PRD.md"
```

### Test/Quality Gate Failures

```
Error: Quality gates failed
  - pytest: 2 tests failed
  - coverage: 78% (below 80% threshold)

Action: Fix tests and improve coverage before PR creation
```

### Architecture Violations

```
Error: Architecture validation failed
  - Infrastructure layer importing Presentation (file:line)

Action: Refactor to respect 3-layer boundaries (P → A → I)
  Review: docs/guides/ARCHITECTURE.md
```

### Milestone Not Found

```
Error: Milestone 'vX.Y.Z' not found

Action: Create milestone first:
  gh api repos/:owner/:repo/milestones -F title="vX.Y.Z" -F due_on="YYYY-MM-DD"
```

### Permission Denied

```
Error: Insufficient permissions to [operation]

Action: Requires 'repo' scope:
  gh auth refresh -s repo
```

### Rate Limit Exceeded

```
Error: API rate limit exceeded

Actions:
  1. Check reset time: gh api rate_limit --jq '.rate.reset' | xargs -I {} date -r {}
  2. Wait for reset, or
  3. Switch token: gh auth switch
```

---

## GraphQL Query Templates

### Fetch Issue Node ID

```graphql
query {
  repository(owner: "OWNER", name: "REPO") {
    issue(number: N) {
      id
      number
      title
    }
  }
}
```

### Create Parent-Child Relationship

```graphql
mutation {
  addSubIssue(input: {
    issueId: "PARENT_NODE_ID"
    subIssueId: "CHILD_NODE_ID"
  }) {
    issue {
      number
      title
    }
  }
}
```

### Batch Fetch Multiple Issues

```graphql
query {
  repository(owner: "OWNER", name: "REPO") {
    issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        number
        title
        state
        labels(first: 10) {
          nodes { name }
        }
      }
    }
  }
}
```

---

## Issue Validation Checklist

Use before `/gh:implement-issue`:

```bash
./scripts/github-projects/validate-agent-ready.sh <issue-number>
```

**Validates**:
- [ ] Issue exists and is OPEN
- [ ] All dependencies (blocked-by) are CLOSED
- [ ] Required labels set (priority, complexity, type)
- [ ] Required documentation field populated
- [ ] Acceptance criteria present
- [ ] Documentation files exist

**Exit Codes**:
- `0` = Ready for implementation
- `1` = Validation failed (see output)
- `2` = Critical error

---

## Standard Script Integration

All scripts calling GitHub API should follow this pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Source rate limit library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/rate_limit.sh"

# 2. Guard at start
rate_limit_guard || exit 1

# 3. Operations with delays
for item in $items; do
    gh api "endpoint/$item"
    rate_limit_delay
done

# 4. Summary at end
rate_limit_summary
```

---

## Configuration Paths

| Config | Location |
|--------|----------|
| User config | `~/.vscanrc` |
| Project settings | `.github/projects/` |
| Issue templates | `.github/ISSUE_TEMPLATE/` |
| Scripts | `scripts/github-projects/` |
| Workflows | `.github/workflows/` |

---

## Quick Command Reference

| Need | Command |
|------|---------|
| Check rate limit | `gh api rate_limit --jq '.rate'` |
| Create milestone | `gh api repos/:owner/:repo/milestones -F title="vX.Y.Z"` |
| List issues | `gh issue list --milestone vX.Y.Z --state all` |
| Set parent-child | `./scripts/github-projects/manage-issue-relationships.sh set-parent P C1 C2` |
| Set blocker | `./scripts/github-projects/manage-issue-relationships.sh set-blocker BLOCKER BLOCKED` |
| Validate issue | `./scripts/github-projects/validate-agent-ready.sh <N>` |
| Sync labels | `./scripts/github-projects/sync-existing-issues.sh` |

---

**Last Updated**: 2025-11-20
**Maintainer**: Keep in sync with rate_limit.sh and GitHub API changes
**Usage**: Import this reference in command descriptions instead of repeating content
