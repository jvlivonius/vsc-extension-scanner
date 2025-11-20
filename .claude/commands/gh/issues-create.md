---
name: issues-create
description: "Create GitHub issues from feature plans with automated relationship setup"
category: workflow
complexity: standard
mcp-servers: []
personas: [python-expert]
---

# /gh:issues-create - Issue Creation from Plans

## Triggers
- Feature planning requiring breakdown into GitHub issues
- Multi-issue feature development workflows
- Need to create structured issue hierarchy from documentation

## Usage

```bash
/gh:issues-create create-from-plan <plan-file> --milestone vX.Y.Z [--auto-link] [--project-number N]
/gh:issues-create single --type <type> --title "..." --milestone vX.Y.Z [options]
```

**Parameters:**
- `<plan-file>`: Path to feature plan markdown (e.g., `docs/archive/plans/v3.8-feature.md`)
- `--milestone vX.Y.Z`: Target milestone version
- `--auto-link`: Automatically create parent-child and blocking relationships (default: true)
- `--no-auto-link`: Skip automatic relationship setup (manual setup required)
- `--project-number N`: GitHub project number (optional, uses default if not specified)
- `--type`: Issue type (feature, task, bug, hotfix)
- `--title`: Issue title

## Behavioral Flow

1. **Parse**: Analyze feature plan or structure
2. **Validate**: Verify milestone exists, check project access
3. **Generate**: Create issues with proper metadata, dependencies, acceptance criteria
4. **Link**: Connect issues to milestone and project board (auto-sync)
5. **Relationships**: Set parent-child and blocking dependencies (if --auto-link)
6. **Report**: Provide summary with issue numbers and next steps

Key behaviors:
- Parse feature plans into structured issue hierarchy (Feature → Tasks)
- Generate issues with required documentation links and acceptance criteria
- Automatically set parent-child relationships via GraphQL
- Automatically create blocking dependencies via REST API
- Link issues to milestones and project board automatically

## Tool Coordination

- **gh CLI**: Issue creation, milestone management (`gh issue create`, `gh api`)
- **Read**: Feature plan parsing, issue template reading
- **Bash**: Git status verification, milestone validation, relationship script execution

## Key Patterns

### Pattern 1: Feature Plan → Issues with Auto-Linking

```
Feature Plan Structure:
## Phase N: Phase Name
### N.1 Specific Task
#### Blocked By
#140
#### Changes Required
...

Generated Issues:
- [FEATURE] Phase Name (#142, parent)
  - [TASK] N.1 Specific Task (#143, child, blocked by #140)
  - [TASK] N.2 Next Task (#144, child)
```

**Workflow:**
1. Parse plan markdown structure
2. Create feature issue for each phase
3. Create task issues for each sub-task
4. Apply labels based on keywords (feature, task)
5. Set complexity from effort estimates
6. Link required documentation
7. **Automatically set parent-child relationships**
8. **Automatically create blocked-by dependencies**
9. Verify all relationships via GitHub API

**See**: [_gh-reference.md](_gh-reference.md#parent-child-relationships) for parent-child implementation details

### Pattern 2: Issue Metadata Template

```yaml
Milestone: vX.Y.Z
Labels: feature, P2-medium, complexity/M
Dependencies: blocked-by #N, blocks #M
Required Docs: ARCHITECTURE.md, SECURITY.md
Acceptance Criteria: [checklist from template]
```

**Label Sync Timing**: Add labels AFTER issue creation to trigger GitHub Actions sync workflow.

**See**: [_gh-reference.md](_gh-reference.md#label-sync-timing) for sync automation details

## Examples

### Create Issues from Plan with Auto-Linking

```bash
/gh:issues-create create-from-plan docs/archive/plans/v3.8-feature.md --milestone v3.8.0

# Analyzes plan structure
# Creates parent feature issue: #142
# Creates task issues: #143, #144, #145
# Links to milestone v3.8.0 and project board
# Automatically sets parent-child relationships: #143-145 as children of #142
# Automatically creates blocked-by dependencies if specified in plan
# Verifies all relationships via GitHub API

# Reports:
# "Created 4 issues for v3.8.0: #142 (parent), #143-145 (tasks)"
# "Set parent-child relationships: 3 successful"
# "Set blocked-by dependencies: 2 successful"
```

### Create Issues Without Auto-Linking

```bash
/gh:issues-create create-from-plan docs/archive/plans/v3.8-feature.md --milestone v3.8.0 --no-auto-link

# Creates issues but skips automatic relationship setup
# Reports: "Created 4 issues for v3.8.0: #142 (parent), #143-145 (tasks)"
#          "Note: Use --auto-link or manually set relationships"

# Manual relationship setup:
./scripts/github-projects/manage-issue-relationships.sh set-parent 142 143 144 145
./scripts/github-projects/manage-issue-relationships.sh set-blocker 143 140
```

### Create Single Issue

```bash
/gh:issues-create single \
  --type feature \
  --title "Add CSV export functionality" \
  --milestone v3.8.0 \
  --priority High \
  --complexity L \
  --docs "ARCHITECTURE.md, SECURITY.md, PRD.md"

# Creates single issue with metadata
# Links to milestone and project board
# Reports: "Created issue #142"
```

## Boundaries

**Will:**
- Parse feature plans and create structured GitHub issues automatically
- Set parent-child relationships via GraphQL API
- Create blocking dependencies via REST API
- Link issues to milestones and project boards with proper metadata
- Verify all relationships were created successfully

**Will Not:**
- Create project boards (manual setup required, see GITHUB_PROJECTS_SETUP.md)
- Modify existing issues without explicit confirmation
- Auto-merge PRs or bypass review requirements
- Create more than 30 issues at once (rate limit safety)

## Implementation Details

### Issue Creation Logic

1. Read feature plan markdown using Read tool
2. Parse phases and tasks using heading structure (## Phase, ### Task)
3. For each phase → create feature issue with template
4. For each task → create task issue
5. Apply labels based on keywords (feature, task, bugfix)
6. Set complexity based on effort estimates
7. Link required documentation from project standards
8. Add acceptance criteria from templates
9. Link to milestone and project board
10. **If --auto-link (default):**
    - Set parent-child relationships via `manage-issue-relationships.sh`
    - Create blocked-by dependencies via `manage-issue-relationships.sh`
    - Verify all relationships were created successfully
11. Report summary with created issue numbers

### Parent-Child Auto-Linking (Step 10)

```bash
# After creating all issues from plan:
PARENT_ISSUE=$parent_issue_number
CHILD_ISSUES="$task_issue_1 $task_issue_2 $task_issue_3"

# Set relationships via script (uses GraphQL API)
./scripts/github-projects/manage-issue-relationships.sh \
    set-parent $PARENT_ISSUE $CHILD_ISSUES

# Verify relationships created
gh api repos/:owner/:repo/issues/$PARENT_ISSUE \
    --jq '.sub_issues_summary.total'
```

**See**: [GITHUB_RELATIONSHIPS.md](../../docs/contributing/GITHUB_RELATIONSHIPS.md) for comprehensive relationship guide

### Blocked-By Auto-Linking (Step 10)

```bash
# For each issue with "Blocked By: #N" in feature plan:
BLOCKER=$blocker_issue_number
BLOCKED=$blocked_issue_number

# Set dependency via script (uses REST API)
./scripts/github-projects/manage-issue-relationships.sh \
    set-blocker $BLOCKED $BLOCKER

# Verify dependency created
gh api repos/:owner/:repo/issues/$BLOCKED/dependencies/blocked_by \
    --jq '.[].number'
```

## Error Handling

**Missing Milestone:**
```
Error: Milestone v3.8.0 not found
Action: Create milestone first:
  gh api repos/:owner/:repo/milestones -F title="v3.8.0" -F due_on="YYYY-MM-DD"
```

**Invalid Feature Plan:**
```
Error: Feature plan missing required sections (Phases, Tasks)
Action: Ensure plan follows template in docs/archive/plans/
```

**Dependency Loop:**
```
Error: Circular dependency detected: #142 → #143 → #142
Action: Review and fix dependency chain in feature plan
```

**Rate Limit:**
```
Warning: Creating 30+ issues will consume significant API quota
Action: Break into smaller batches or wait for rate limit reset
```

**See**: [_gh-reference.md](_gh-reference.md#common-error-patterns) for full error reference

## Rate Limiting

**API Call Estimates:**

| Operation | Issues Created | Estimated API Calls |
|-----------|----------------|---------------------|
| Create from plan (10 issues) | 10 | ~35 (create + relationships + sync) |
| Create from plan (30 issues) | 30 | ~105 (create + relationships + sync) |
| Create single issue | 1 | ~3 (create + sync) |

**Best Practices:**
1. Check rate limit before large operations: `gh api rate_limit`
2. Scripts automatically add 0.5s delays between calls
3. For plans with >30 issues, break into smaller batches

**See**: [_gh-reference.md](_gh-reference.md#rate-limiting-essentials) for rate limit management

## Integration with Workflow

### After Issue Creation

```bash
# 1. Issues created and linked
/gh:issues-create create-from-plan plan.md --milestone v3.8.0

# 2. Triage new issues
/gh:triage <issue-number>

# 3. Validate before implementation
./scripts/github-projects/validate-agent-ready.sh <issue-number>

# 4. Implement
/gh:implement-issue <issue-number>
```

## Configuration

### ~/.vscanrc Extension

```ini
[github_projects]
default_project_number = 3
default_milestone_prefix = v
auto_link_prs = true
create_auto_link = true  # Default for --auto-link flag
```

## References

- [GitHub Relationships Guide](../../docs/contributing/GITHUB_RELATIONSHIPS.md)
- [_gh-reference.md](_gh-reference.md) - Shared command reference
- [Issue Templates](.github/ISSUE_TEMPLATE/)
- [manage-issue-relationships.sh](../../scripts/github-projects/manage-issue-relationships.sh)
- [GITHUB_PROJECTS_SETUP.md](../../docs/contributing/GITHUB_PROJECTS_SETUP.md)
