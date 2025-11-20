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
2. Parse due date (YYYY-MM-DD)
3. Create via GitHub API
4. Report milestone number and URL
5. Suggest next steps

### Pattern 2: Progress Report Generation

```bash
/gh:milestone report v3.8.0 --format markdown --output milestone-report.md
```

**Report Structure:**
```markdown
# Milestone Report: v3.8.0

## Progress Summary
- Completion: 67% (8/12 issues)
- Open: 4 issues
- Closed: 8 issues

## Issue Breakdown
### By Type
- Features: 5, Bugs: 3, Tasks: 4

### By Priority
- P0 (Critical): 1, P1 (High): 6, P2 (Medium): 3, P3 (Low): 2

## Open Issues
- #142: Add CSV export (P1-high)
- #143: Implement formatter class (P1-high)
```

**Script**: Uses `./scripts/github-projects/generate-milestone-report.sh`

### Pattern 3: Milestone Synchronization

```bash
/gh:milestone sync v3.8.0 --project-number 3
```

**Implementation:**
1. Fetch all milestone issues
2. Group by state (open/closed) and PR status
3. Update project board:
   - Closed issues → "Done"
   - Issues with open PRs → "In Review"
   - Open issues → Keep current status
4. Sync Priority/Complexity from labels
5. Report: "Synced 12 issues: 8 Done, 4 In Progress"

**Label Sync**: If labels were recently changed, allow 1-5 minutes for GitHub Actions sync before milestone sync.

**See**: [_gh-reference.md](_gh-reference.md#label-sync-timing) for sync automation

### Pattern 4: Milestone Closure

```bash
/gh:milestone close v3.8.0 --generate-notes
```

**Implementation:**

1. **Validate closure readiness** (runs `validate-milestone-closure.sh`):
   - All P0 (critical) issues closed
   - All parent issues 100% complete (sub_issues_summary)
   - No open blocking dependencies
   - All PRs merged or deferred
2. Generate release notes (if --generate-notes)
3. Close milestone via API
4. Comment on all milestone issues: "Released in v3.8.0"
5. Report completion and next steps

**Validation Script:**

```bash
./scripts/github-projects/validate-milestone-closure.sh v3.8.0

# Exit codes:
# 0 = Ready for closure
# 1 = Validation failed (blocking issues)
# 2 = Critical error (script failure)
```

**Auto-validation:** The `/gh:milestone close` command automatically runs validation before closure.

**See**: [_gh-reference.md](_gh-reference.md#issue-validation-checklist) for shared validation patterns

**See**: `/gh:projects-sync release-notes` for release notes details

### Pattern 5: Milestone Listing

```bash
/gh:milestone list --state open
```

**Output:**
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

# Reports: "Created milestone v3.8.0 (#15) due 2025-01-15"
# Suggests: "Add issues with: gh issue edit <N> --milestone v3.8.0"
```

### Generate Weekly Progress Report

```bash
/gh:milestone report v3.8.0 --format markdown

# Shows: 67% complete (8/12 issues)
# Lists: 4 open issues (2 high priority)
# Reports: 8 closed this week
# Identifies: Blocked issues and next actions
```

### Sync Milestone with Project Board

```bash
/gh:milestone sync v3.8.0

# Fetches all v3.8.0 issues
# Updates project board status
# Moves 3 closed issues to "Done"
# Reports: "Synced 12 issues, 3 status updates"
```

### Close Milestone

```bash
/gh:milestone close v3.8.0 --generate-notes

# Validates: Checks for open issues
# Prompts: "4 issues remain open. Proceed? (y/n)"
# Generates: Release notes from closed issues
# Closes: Milestone
# Comments: On all issues
# Reports: Next steps (tagging, publishing)
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
2. Calculate statistics (total/open/closed counts, completion %)
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
- [ ] All parent issues have 100% child completion
- [ ] No open issues blocked by other open issues
- [ ] Validation script passes: `./scripts/github-projects/validate-milestone-closure.sh vX.Y.Z`
- [ ] All PRs merged or explicitly deferred
- [ ] Release notes generated and reviewed
- [ ] Milestone issues commented
- [ ] Project board items archived (optional)

## Error Handling

**Milestone Not Found:**
```
Error: Milestone 'v3.8.0' not found
Action: Create milestone first:
  /gh:milestone create v3.8.0 --due YYYY-MM-DD
```

**Validation Failures:**

The validation script performs comprehensive checks. Run `validate-milestone-closure.sh --dry-run vX.Y.Z` to preview.

```
Error: Milestone validation failed
Details:
  ✗ P0 issues still open: 2 (#142, #145)
  ✗ Parent #142 only 67% complete (2/3 children)
  ✗ Issue #145 blocked by 1 open issues (#148)

Action: Fix validation errors before closure:
  1. Close/defer P0 issues: #142, #145
  2. Complete parent-child work
  3. Resolve blocking dependencies
  4. Re-run: ./scripts/github-projects/validate-milestone-closure.sh v3.8.0

Use --force to bypass validation (NOT RECOMMENDED)
```

**See**: [_gh-reference.md](_gh-reference.md#common-error-patterns) for error handling patterns

**Permission Denied:**
```
Error: Insufficient permissions to close milestone
Action: Requires 'repo' scope:
  gh auth refresh -s repo
```

**Duplicate Milestone:**
```
Error: Milestone 'v3.8.0' already exists (#15)
Action: Use existing milestone or choose different version
```

**See**: [_gh-reference.md](_gh-reference.md#common-error-patterns) for full error reference

## Rate Limiting

**API Call Breakdown:**

| Operation | Milestone Size | API Calls |
|-----------|----------------|-----------|
| Create milestone | N/A | 1 |
| Report (with details) | 20 issues | ~25 |
| Report (with details) | 50 issues | ~60 |
| Sync to project | 30 issues | ~40 |
| Close milestone | 20 issues | ~25 |

**Best Practices:**
1. Check before large operations: `gh api rate_limit`
2. Break large milestones (>50 issues) into batches
3. Use `--dry-run` mode to estimate API usage

**See**: [_gh-reference.md](_gh-reference.md#rate-limiting-essentials) for rate limit management

## Integration with Release Process

### Pre-Release (Planning Phase)

```bash
# 1. Create milestone
/gh:milestone create v3.8.0 --due 2025-01-15

# 2. Create and link issues
/gh:issues-create create-from-plan docs/plans/v3.8.md --milestone v3.8.0

# 3. Weekly progress checks
/gh:milestone report v3.8.0
```

### Release (Execution Phase)

```bash
# 4. Implement and track (Issues implemented via /gh:issues-implement)

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

**See**: [RELEASE_PROCESS.md](../../docs/contributing/RELEASE_PROCESS.md) for complete workflow

## Configuration

### ~/.vscanrc Extension

```ini
[github_milestones]
default_format = markdown
auto_generate_notes = true
report_include_blocked = true
```

## References

- [_gh-reference.md](_gh-reference.md) - Shared GitHub command reference
- [GITHUB_PROJECTS.md](../../docs/contributing/GITHUB_PROJECTS.md) - Milestone management
- [RELEASE_PROCESS.md](../../docs/contributing/RELEASE_PROCESS.md) - Release workflow
- [/gh:projects-sync](./projects-sync.md) - Release notes generation
- [GitHub Milestones API](https://docs.github.com/en/rest/issues/milestones)
