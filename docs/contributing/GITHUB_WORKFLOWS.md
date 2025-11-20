# GitHub Projects Daily Workflows

**Practical day-to-day development workflows for GitHub Projects V2**

**Prerequisites**: [GITHUB_PROJECTS_QUICKSTART.md](GITHUB_PROJECTS_QUICKSTART.md) for 5-minute introduction

---

## Table of Contents

1. [Issue Creation Workflows](#issue-creation-workflows)
2. [Issue Triage Workflows](#issue-triage-workflows)
3. [Implementation Workflows](#implementation-workflows)
4. [Project Board Management](#project-board-management)
5. [Milestone Management](#milestone-management)
6. [Release Workflows](#release-workflows)

---

## Issue Creation Workflows

### Method 1: Web UI with Templates (Recommended)

**When to use**: Creating individual issues with structured format

1. Navigate to: https://github.com/jvlivonius/vsc-extension-scanner/issues/new/choose
2. Select template (`feature.yml`, `task.yml`, or `release.yml`)
3. Fill in all fields:
   - Title: Clear, actionable description
   - Required Documentation: Comma-separated (e.g., "ARCHITECTURE.md, SECURITY.md")
   - Dependencies: "Blocked By: #N" if applicable
   - Acceptance Criteria: Specific, testable conditions
4. Submit → Issue auto-added to Project #3 in "Backlog"

**Result**: Structured issue with all metadata, ready for triage

### Method 2: CLI for Single Issues

**When to use**: Quick issue creation, automation scripts

```bash
gh issue create \
  --title "[FEATURE] Add CSV export" \
  --body "$(cat <<'EOF'
## Summary
Export scan results as CSV format for analysis in Excel/spreadsheet tools

## Required Documentation
ARCHITECTURE.md, SECURITY.md, PRD.md

## Dependencies
Blocked By: None
Blocks: None

## Acceptance Criteria
- [ ] CSV formatter handles special characters (commas, quotes)
- [ ] --output-csv CLI flag implemented
- [ ] Tests cover edge cases
- [ ] Documentation updated
EOF
)" \
  --label "feature,P1-high,complexity/M" \
  --milestone "v3.8.0"
```

**Note**: Add labels AFTER creation to trigger auto-sync workflow

### Method 3: Bulk Creation from Plan

**When to use**: Feature planning, creating multiple related issues

```bash
/gh:issues-create create-from-plan docs/archive/plans/v3.8-csv-export.md --milestone v3.8.0
```

**Plan format**:
```markdown
## Phase 1: CSV Formatter
### 1.1 Implement CSV formatter class
#### Required Documentation
ARCHITECTURE.md, SECURITY.md
#### Changes Required
...

### 1.2 Add export command to CLI
#### Required Documentation
ARCHITECTURE.md
#### Changes Required
...
```

**Result**:
- Parent feature issue created
- Child task issues created
- Parent-child relationships set automatically
- All linked to milestone and project board

**See**: [issues-create.md](../../.claude/commands/gh/issues-create.md) for full details

---

## Issue Triage Workflows

### Single Issue Triage

**When to use**: New issues needing classification

```bash
/gh:triage 160
```

**Process**:
1. AI analyzes issue content using sequential-thinking
2. Suggests:
   - Type (feature/bug/task/hotfix)
   - Priority (P0-P3)
   - Complexity (XS-XL)
   - Required documentation
3. Presents recommendations with confidence scores
4. Applies labels if confirmed

**Example output**:
```
Issue #160: Add CSV export functionality

Type: Feature ✓ (confidence: 95%)
Priority: P1-high ⚠️ (confidence: 85%)
Complexity: M (confidence: 80%)

Required Documentation:
- ARCHITECTURE.md, SECURITY.md, PRD.md

Apply suggestions? (y/n)
```

### Batch Triage

**When to use**: Weekly triage sessions, milestone planning

```bash
/gh:triage --batch --milestone v3.8.0 --limit 20
```

**Process**:
1. Fetches untriaged issues
2. Analyzes each with sequential-thinking
3. Groups by confidence:
   - High confidence (>90%): Auto-suggest
   - Low confidence (<70%): Manual review
4. Batch applies high-confidence suggestions

**Best practices**:
- Limit to 20-30 issues per batch (rate limiting)
- Review low-confidence issues manually
- Run weekly for consistent triage

**See**: [triage.md](../../.claude/commands/gh/triage.md) for full details

---

## Implementation Workflows

### Agent-Driven Implementation

**Prerequisites**:
1. Issue validated: `./scripts/github-projects/validate-agent-ready.sh <number>`
2. All dependencies closed
3. Required documentation specified

**Workflow**:
```bash
/gh:issues-implement 142
```

**Process**:
1. **Fetch**: Retrieve issue details, metadata
2. **Validate**: Check dependencies, docs, prerequisites
3. **Prepare**: Read required docs, create feature branch
4. **Implement**: Code changes following acceptance criteria
5. **Verify**: Run tests, security scans
6. **PR**: Create PR with issue linkage

**Branch naming**: Auto-generated from issue type and title
- Feature: `feature/add-csv-export`
- Bugfix: `bugfix/fix-memory-leak`
- Hotfix: `hotfix/security-cve-2024-12345`

**PR linkage**: Automatically adds "Closes #142" to PR description

**See**: [implement-issue.md](../../.claude/commands/gh/implement-issue.md) for full details

### Manual Implementation

**When agent implementation not suitable**:

1. **Create branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Read required docs**:
   - Check issue "Required Documentation" field
   - Read each doc before starting

3. **Implement with quality gates**:
   ```bash
   # Make changes...
   python3 -m pytest tests/
   python3 tests/test_security.py
   python3 tests/test_architecture.py
   pre-commit run --all-files
   ```

4. **Create PR**:
   ```bash
   git push -u origin feature/my-feature
   gh pr create --title "feat(module): description" --body "Closes #142"
   ```

---

## Project Board Management

### Moving Issues Through Workflow

**Kanban Board**: https://github.com/users/jvlivonius/projects/3/views/1

**Status transitions**:
1. **Backlog → Todo**: Drag when ready to work
2. **Todo → In Progress**: Drag when you start
3. **In Progress → In Review**: Auto-transitions when PR opens
4. **In Review → Done**: Auto-transitions when PR merges

**Manual status update** (if needed):
```bash
# Via project board: Click Status cell → Select value
# Via CLI: Update labels if using custom status labels
gh issue edit 142 --add-label "status:in-progress"
```

### Common Filters for Daily Work

**Your Active Work**:
```
assignee:@me status:"In Progress"
```

**Ready to Start**:
```
status:Backlog,Todo priority:Critical,High -assignee:@me
```

**Needs Review**:
```
status:"In Review" assignee:@me
```

**Blocked Items**:
```
status:Blocked -status:Done
```

**Current Milestone**:
```
milestone:"v3.8.0" -status:Done
```

**See**: [GITHUB_FILTERS.md](../guides/GITHUB_FILTERS.md) for advanced filtering patterns

### Setting Relationships

**Parent-Child** (feature breakdown):
```bash
# Feature #142 has tasks #143, #144, #145
./scripts/github-projects/manage-issue-relationships.sh set-parent 142 143 144 145

# Verify
./scripts/github-projects/manage-issue-relationships.sh view 142
```

**Blocking** (dependencies):
```bash
# Issue #146 blocks issue #147
./scripts/github-projects/manage-issue-relationships.sh set-blocker 147 146

# Verify
./scripts/github-projects/manage-issue-relationships.sh view 147
```

**See**: [GITHUB_RELATIONSHIPS.md](GITHUB_RELATIONSHIPS.md) for comprehensive guide

---

## Milestone Management

### Creating Milestones

**For new releases**:
```bash
/gh:milestone create v3.8.0 --due 2025-01-15 --description "CSV export and performance improvements"
```

**Result**: Milestone created, ready to link issues

### Tracking Progress

**Weekly progress report**:
```bash
/gh:milestone report v3.8.0 --format markdown
```

**Output**:
```markdown
# Milestone Report: v3.8.0

## Progress Summary
- Completion: 67% (8/12 issues)
- Open: 4 issues
- Closed: 8 issues

## Open Issues
- #142: Add CSV export (P1-high)
- #143: Implement formatter (P1-high)

## Blocked Issues
- #145: Blocked by #142
```

### Syncing to Project Board

**After bulk label changes or weekly sync**:
```bash
/gh:projects-sync milestone v3.8.0
```

**Process**:
- Fetches all milestone issues
- Updates project board status
- Moves closed issues to "Done"
- Syncs Priority/Complexity fields from labels

**See**: [milestone.md](../../.claude/commands/gh/milestone.md) for full details

---

## Release Workflows

### Pre-Release Phase

**1. Create milestone**:
```bash
/gh:milestone create v3.8.0 --due 2025-01-15
```

**2. Create issues from plan**:
```bash
/gh:issues-create create-from-plan docs/plans/v3.8.md --milestone v3.8.0
```

**3. Weekly tracking**:
```bash
/gh:milestone report v3.8.0
```

### Development Phase

**4. Implement issues**:
```bash
# For each ready issue:
./scripts/github-projects/validate-agent-ready.sh 142
/gh:issues-implement 142
```

**5. Sync board weekly**:
```bash
/gh:projects-sync milestone v3.8.0
```

### Release Phase

**6. Generate release notes**:
```bash
/gh:projects-sync release-notes v3.8.0 --draft
```

**7. Close milestone**:
```bash
/gh:milestone close v3.8.0 --generate-notes
```

**8. Tag and publish**:
```bash
git tag -a v3.8.0 -m "Release v3.8.0"
git push origin v3.8.0
python3 -m build && twine upload dist/*
```

**See**: [RELEASE_PROCESS.md](RELEASE_PROCESS.md) for complete release workflow

---

## Automation Patterns

### Label Sync Automation

**Automatic**: GitHub Actions workflow syncs labels to project fields

**Trigger**: `labeled` or `unlabeled` event on issues

**Delay**: 1-5 minutes for sync to complete

**Verification**:
```bash
# Check workflow runs
gh run list --workflow=sync-project-fields.yml --limit 5

# Manual sync if needed
./scripts/github-projects/sync-existing-issues.sh
```

**See**: [_gh-reference.md](../../.claude/commands/gh/_gh-reference.md#label-sync-timing) for details

### Issue Auto-Linking

**Automatic**: PRs with "Closes #N" auto-link to issues

**Trigger**: PR description contains GitHub keywords

**Keywords**: `Closes`, `Fixes`, `Resolves` followed by `#N`

**Result**: Issue auto-closes when PR merges, status moves to "Done"

### Dependency Tracking

**Automatic**: Agent checks blocked-by dependencies before implementation

**Workflow**:
1. Issue body contains "Blocked By: #140"
2. `/gh:issues-implement` validates #140 is CLOSED
3. Errors if blocker still OPEN

**Manual check**:
```bash
./scripts/github-projects/validate-agent-ready.sh <issue-number>
```

---

## Common Scenarios

### Scenario 1: Feature Development

```bash
# 1. Plan: Create feature with tasks
/gh:issues-create create-from-plan docs/plans/csv-export.md --milestone v3.8.0

# 2. Triage: Set priorities
/gh:triage 142  # Parent feature
/gh:triage 143  # Task 1
/gh:triage 144  # Task 2

# 3. Implement: Start with first task
/gh:issues-implement 143

# 4. Track: Monitor progress
/gh:milestone report v3.8.0

# 5. Release: Close when complete
/gh:milestone close v3.8.0 --generate-notes
```

### Scenario 2: Bug Fix

```bash
# 1. Create: Report bug
gh issue create --title "[BUG] Memory leak in scanner" --label "bug,P0-critical"

# 2. Triage: Analyze priority
/gh:triage 150

# 3. Implement: Fix immediately
/gh:issues-implement 150

# 4. Verify: Ensure fix works
# (Tests run automatically during implementation)
```

### Scenario 3: Weekly Planning

```bash
# 1. Review: Check milestone progress
/gh:milestone report v3.8.0

# 2. Triage: Process new issues
/gh:triage --batch --milestone v3.8.0 --limit 20

# 3. Prioritize: Update priorities
# (Use project board filters and drag-drop)

# 4. Sync: Update board
/gh:projects-sync milestone v3.8.0
```

---

## Troubleshooting

**Issue not showing on project board**:
- Wait 1-2 minutes for auto-sync
- Manual add: Project board → "+" button → Select issue

**Labels not syncing to fields**:
- Wait 1-5 minutes for GitHub Actions
- Check: `gh run list --workflow=sync-project-fields.yml`
- Manual sync: `./scripts/github-projects/sync-existing-issues.sh`

**Parent-child not working**:
- Use script: `./scripts/github-projects/manage-issue-relationships.sh`
- Must use GraphQL API (REST API doesn't support)

**Rate limit errors**:
- Check: `gh api rate_limit`
- Wait for reset or switch token: `gh auth switch`

**Implementation blocked**:
- Run: `./scripts/github-projects/validate-agent-ready.sh <number>`
- Fix validation errors before `/gh:issues-implement`

---

## Best Practices

**Issue Creation**:
- Use templates for consistency
- Always specify "Required Documentation"
- Add clear acceptance criteria
- Set milestone immediately

**Triage**:
- Triage within 24 hours of creation
- Use AI suggestions but verify
- Batch triage weekly for efficiency

**Implementation**:
- Validate dependencies first
- Read required docs before coding
- Run all quality gates before PR
- Link PRs to issues with "Closes #N"

**Project Board**:
- Drag cards daily as status changes
- Use filters for focused views
- Keep "In Progress" limit to 3-5 items
- Archive "Done" items monthly

**Milestones**:
- Weekly progress reports
- Sync board after batch changes
- Close only when all critical issues resolved

---

## References

- [GITHUB_PROJECTS_QUICKSTART.md](GITHUB_PROJECTS_QUICKSTART.md) - 5-minute introduction
- [GITHUB_RELATIONSHIPS.md](GITHUB_RELATIONSHIPS.md) - Parent-child and blocking
- [GITHUB_FILTERS.md](../guides/GITHUB_FILTERS.md) - Advanced filtering
- [_gh-reference.md](../../.claude/commands/gh/_gh-reference.md) - Command reference
- [issues-create.md](../../.claude/commands/gh/issues-create.md) - Issue creation
- [triage.md](../../.claude/commands/gh/triage.md) - Issue triage
- [implement-issue.md](../../.claude/commands/gh/implement-issue.md) - Implementation
- [milestone.md](../../.claude/commands/gh/milestone.md) - Milestone management
- [projects-sync.md](../../.claude/commands/gh/projects-sync.md) - Project sync

---

**Last Updated**: 2025-11-20
**Status**: Active
**Maintainer**: Update workflows as team practices evolve
