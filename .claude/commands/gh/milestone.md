---
name: milestone
description: "Comprehensive milestone management and progress tracking"
category: workflow
complexity: standard
mcp-servers: []
personas: [python-expert]
---

# /gh:milestone - Milestone Management

## Triggers
- Milestone creation and planning needs
- Progress tracking and reporting requirements
- Release coordination and closure workflows
- Milestone synchronization with project boards

## Usage

```bash
/gh:milestone create vX.Y.Z --due YYYY-MM-DD [--description "..."]
/gh:milestone report vX.Y.Z [--format markdown|json] [--output FILE]
/gh:milestone sync vX.Y.Z [--project-number N]
/gh:milestone close vX.Y.Z [--generate-notes]
/gh:milestone list [--state open|closed|all]
```

**Parameters:**
- `vX.Y.Z`: Milestone version (e.g., v3.8.0)
- `--due YYYY-MM-DD`: Due date for milestone
- `--format`: Output format (markdown or json)
- `--output FILE`: Save output to file
- `--project-number N`: GitHub project number
- `--generate-notes`: Auto-generate release notes on close
- `--state`: Filter milestones by state

## Behavioral Flow

1. **Parse**: Extract milestone identifier and subcommand
2. **Validate**: Verify milestone exists (except for create), check permissions
3. **Execute**: Perform requested operation with appropriate GitHub API calls
4. **Report**: Provide summary with actionable next steps

Key behaviors:
- Create milestones with due dates and descriptions
- Generate comprehensive progress reports
- Sync milestone issues to project board
- Close milestones with automatic release note generation
- Validate all operations before execution

## Tool Coordination

- **gh CLI**: Milestone/issue/project management (`gh api`, `gh issue`, `gh project`)
- **Bash**: Script execution for reporting and validation
- **Read**: Template reading, report formatting
- **Write**: Release notes generation

## Key Patterns

### Pattern 1: Milestone Creation

```bash
/gh:milestone create v3.8.0 --due 2025-01-15 --description "CSV export feature release"
```

**Implementation:**
1. Validate version format (vX.Y.Z)
2. Parse due date (YYYY-MM-DD format)
3. Create milestone via GitHub API:
   ```bash
   gh api repos/:owner/:repo/milestones \
     -f title="v3.8.0" \
     -f description="CSV export feature release" \
     -f due_on="2025-01-15T23:59:59Z"
   ```
4. Report milestone number and URL
5. Suggest next steps (create issues, link to project)

### Pattern 2: Progress Report Generation

```bash
/gh:milestone report v3.8.0 --format markdown --output milestone-report.md
```

**Implementation:**
1. Execute milestone report script:
   ```bash
   ./scripts/github-projects/generate-milestone-report.sh v3.8.0 \
     --format markdown \
     --output milestone-report.md
   ```
2. Script generates:
   - Progress statistics (completion %, open/closed counts)
   - Issue breakdown by type and priority
   - Open issues list with priorities
   - Recently closed issues with dates
   - Blocked issues summary
   - Actionable next steps

**Report Structure:**
```markdown
# Milestone Report: v3.8.0

## Progress Summary
- Completion: 67% (8/12 issues)
- Open: 4 issues
- Closed: 8 issues

## Issue Breakdown
### By Type
- Features: 5
- Bugs: 3
- Tasks: 4

### By Priority
- P0 (Critical): 1
- P1 (High): 6
- P2 (Medium): 3
- P3 (Low): 2

## Open Issues
- #142: Add CSV export (#P1-high)
- #143: Implement formatter class (#P1-high)
...
```

### Pattern 3: Milestone Synchronization

```bash
/gh:milestone sync v3.8.0 --project-number 3
```

**Implementation:**
1. Fetch all milestone issues:
   ```bash
   gh issue list --milestone v3.8.0 --state all --limit 1000
   ```
2. Group by state (open/closed)
3. Update project board items:
   - Move closed issues to "Done" column
   - Update Priority/Complexity fields from labels
   - Verify all issues present on board
4. Report synchronization summary:
   ```
   Synced 12 issues:
   - 8 moved to Done
   - 4 remain In Progress/Backlog
   - 0 missing from project board
   ```

### Pattern 4: Milestone Closure

```bash
/gh:milestone close v3.8.0 --generate-notes
```

**Implementation:**
1. **Validate closure readiness:**
   - Check all issues closed or explicitly accepted as open
   - Warn about open critical (P0) issues
   - Confirm with user before proceeding

2. **Generate release notes:**
   ```bash
   /sc:gh-projects generate-release-notes v3.8.0
   ```
   - Group closed issues by type (features, bugs, security)
   - Format as markdown with issue links
   - Save to `docs/archive/summaries/vX.Y.Z-release-notes.md`

3. **Close milestone:**
   ```bash
   MILESTONE_NUM=$(gh api repos/:owner/:repo/milestones \
     --jq '.[] | select(.title=="v3.8.0") | .number')

   gh api repos/:owner/:repo/milestones/$MILESTONE_NUM \
     -X PATCH \
     -f state="closed"
   ```

4. **Post-closure actions:**
   - Comment on all milestone issues: "Released in v3.8.0"
   - Archive project board items (optional)
   - Generate PR for release notes (optional)

5. **Report completion:**
   ```
   ✓ Milestone v3.8.0 closed
   ✓ Release notes generated: docs/archive/summaries/v3.8.0-release-notes.md
   ✓ Commented on 12 issues

   Next steps:
   - Review release notes
   - Create git tag: git tag -a v3.8.0 -m "Release v3.8.0"
   - Build and publish: python3 -m build && twine upload dist/*
   ```

### Pattern 5: Milestone Listing

```bash
/gh:milestone list --state open
```

**Implementation:**
1. Fetch milestones:
   ```bash
   gh api repos/:owner/:repo/milestones \
     --jq '.[] | select(.state=="open") | {title, due_on, open_issues, closed_issues}'
   ```
2. Format as table:
   ```
   Open Milestones:

   Milestone    Due Date      Open  Closed  Progress
   v3.8.0       2025-01-15    4     8       67%
   v3.9.0       2025-02-15    12    0       0%
   v4.0.0       2025-03-15    0     0       0%
   ```

## Examples

### Create Milestone for Next Release

```bash
/gh:milestone create v3.8.0 --due 2025-01-15 --description "CSV export and performance improvements"

# Agent actions:
# 1. Validates version format
# 2. Creates milestone via GitHub API
# 3. Reports: "Created milestone v3.8.0 (#15) due 2025-01-15"
# 4. Suggests: "Add issues with: gh issue edit <N> --milestone v3.8.0"
```

### Generate Weekly Progress Report

```bash
/gh:milestone report v3.8.0 --format markdown

# Agent generates comprehensive report showing:
# - 67% complete (8/12 issues)
# - 4 issues open (2 high priority)
# - 8 issues closed this week
# - Blocked issues: #145 (waiting on #142)
# - Next actions: Review PR #156, close #142
```

### Sync Milestone with Project Board

```bash
/gh:milestone sync v3.8.0

# Agent actions:
# 1. Fetches all v3.8.0 issues
# 2. Updates project board status
# 3. Moves 3 closed issues to "Done"
# 4. Reports: "Synced 12 issues, 3 status updates"
```

### Close Milestone and Generate Release Notes

```bash
/gh:milestone close v3.8.0 --generate-notes

# Agent workflow:
# 1. Checks: 4 issues still open
# 2. Prompts: "4 issues remain open. Proceed with closure? (y/n)"
# 3. User confirms: y
# 4. Generates release notes from closed issues
# 5. Closes milestone
# 6. Comments on all issues
# 7. Reports next steps (tagging, publishing)
```

### List All Milestones

```bash
/gh:milestone list --state all

# Shows:
# All Milestones:
#
# v3.8.0 (open)     | Due: 2025-01-15 | Progress: 67% (8/12)
# v3.7.0 (closed)   | Due: 2024-12-15 | Completed: 2024-12-14
# v3.6.0 (closed)   | Due: 2024-11-15 | Completed: 2024-11-12
```

## Boundaries

**Will:**
- Create and manage milestones with validation
- Generate comprehensive progress reports
- Sync milestone issues with project boards
- Close milestones with automatic release note generation
- Track and report blocked issues
- Provide actionable next steps

**Will Not:**
- Delete milestones (use gh CLI directly with confirmation)
- Modify milestone dates without explicit user request
- Force-close milestones with open critical issues without confirmation
- Auto-merge PRs or bypass review requirements
- Automatically publish releases (requires explicit user action)

## Implementation Details

### Milestone Creation Validation
- Version format: `vX.Y.Z` (semantic versioning)
- Due date format: `YYYY-MM-DD` (ISO 8601)
- Description: Optional, max 500 characters
- Check for duplicate milestones before creation

### Report Generation Logic
1. Fetch all milestone issues with metadata
2. Calculate statistics:
   - Total/open/closed counts
   - Completion percentage
   - Type distribution (features/bugs/tasks)
   - Priority distribution (P0-P3)
3. Identify blocked issues via dependencies API
4. Format based on --format flag (markdown/json)
5. Output to file or stdout

### Synchronization Strategy
1. Query all milestone issues
2. For each issue:
   - Check project board membership
   - Update status based on PR state
   - Sync Priority/Complexity from labels
3. Report items needing manual intervention

### Closure Checklist
- [ ] All critical (P0) issues closed
- [ ] All PRs merged or explicitly deferred
- [ ] Release notes generated and reviewed
- [ ] Milestone issues commented
- [ ] Project board items archived (optional)

## Error Handling

**Milestone Not Found:**
```
Error: Milestone 'v3.8.0' not found
Action: Create milestone first with:
  /gh:milestone create v3.8.0 --due YYYY-MM-DD
```

**Open Critical Issues:**
```
Warning: 2 critical (P0) issues remain open: #142, #145
Action: Close critical issues before milestone closure, or
  use --force to proceed (creates tracking issue for open items)
```

**Permission Denied:**
```
Error: Insufficient permissions to close milestone
Action: Requires 'repo' scope. Run:
  gh auth refresh -s repo
```

**Duplicate Milestone:**
```
Error: Milestone 'v3.8.0' already exists (#15)
Action: Use existing milestone or choose different version
```

## Integration with Release Process

### Pre-Release (Planning Phase)
```bash
# 1. Create milestone
/gh:milestone create v3.8.0 --due 2025-01-15

# 2. Create and link issues
/sc:gh-projects create-from-plan docs/plans/v3.8.md --milestone v3.8.0

# 3. Weekly progress checks
/gh:milestone report v3.8.0
```

### Release (Execution Phase)
```bash
# 4. Implement and track
# (Issues implemented via /sc:implement-issue)

# 5. Sync board status
/gh:milestone sync v3.8.0

# 6. Pre-release validation
./scripts/github-projects/validate-issue-structure.sh <issue-numbers>
```

### Post-Release (Closure Phase)
```bash
# 7. Close milestone with notes
/gh:milestone close v3.8.0 --generate-notes

# 8. Tag and publish
git tag -a v3.8.0 -m "Release v3.8.0"
git push origin v3.8.0
python3 -m build && twine upload dist/*
```

## References

- [Milestone Management Guide](../../docs/contributing/GITHUB_PROJECTS.md)
- [Release Process](../../docs/contributing/RELEASE_PROCESS.md)
- [Issue Templates](.github/ISSUE_TEMPLATE/)
- [GitHub Milestones API](https://docs.github.com/en/rest/issues/milestones)
