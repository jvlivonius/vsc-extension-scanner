---
name: projects-sync
description: "Milestone synchronization and release notes generation"
category: workflow
complexity: standard
mcp-servers: []
personas: [python-expert]
---

# /gh:projects-sync - Project Board Synchronization

## Triggers
- Release coordination with milestone tracking
- Project board synchronization needs
- Release notes generation from milestone issues
- PR linkage to issues and milestones

## Usage

```bash
/gh:projects-sync milestone vX.Y.Z [--project-number N]
/gh:projects-sync release-notes vX.Y.Z [--draft] [--output FILE]
/gh:projects-sync link-pr <pr-number> --issue <issue-number> --milestone vX.Y.Z
```

**Parameters:**
- `vX.Y.Z`: Milestone version
- `--project-number N`: GitHub project number (optional, uses default if not specified)
- `--draft`: Generate draft release notes without creating GitHub issue
- `--output FILE`: Save release notes to file
- `<pr-number>`: Pull request number to link
- `--issue <issue-number>`: Issue number for PR linkage

## Behavioral Flow

1. **Fetch**: Retrieve milestone issues and current project board state
2. **Analyze**: Group by state, labels, and PR status
3. **Sync**: Update project board items via GitHub API
4. **Generate**: Create release notes from closed milestone issues (if applicable)
5. **Report**: Provide summary with counts and next steps

Key behaviors:
- Sync milestone issues to project board automatically
- Move items to appropriate columns based on PR status
- Generate release notes from closed milestone issues
- Link PRs to issues and milestones
- Maintain proper project board field values

## Tool Coordination

- **gh CLI**: Milestone/issue/project/PR management (`gh api`, `gh pr`, `gh project`)
- **Bash**: Script execution for reporting and validation
- **Write**: Release notes generation (draft format)

## Key Patterns

### Pattern 1: Milestone Synchronization

```bash
# Sync all milestone issues to project board
/gh:projects-sync milestone v3.8.0

# Workflow:
# 1. Fetch all issues for milestone
# 2. Group by state (open, closed)
# 3. Update project board items
# 4. Move items to columns based on PR status
# 5. Report summary with counts
```

**Implementation:**
1. Fetch all issues: `gh api repos/:owner/:repo/milestones/NUMBER`
2. Group by state (open, closed)
3. Update project board items via GitHub API
4. Move items to appropriate columns
5. Report: "Synced 12 issues: 5 Done, 3 In Progress, 4 Backlog"

### Pattern 2: Release Notes Generation

```bash
# Generate release notes from closed milestone issues
/gh:projects-sync release-notes v3.8.0 --draft

# Workflow:
# 1. Fetch milestone issues with state=closed
# 2. Group by labels (feature, bugfix, security, docs)
# 3. Extract titles and issue numbers
# 4. Format as markdown with proper sections
# 5. Save to docs/archive/summaries/vX.Y.Z-release-notes.md
```

**Output Structure:**
```markdown
# Release Notes: v3.8.0

## Summary
Brief overview of the release.

## Breaking Changes
- Changes that break backward compatibility

## New Features
- #142: Add CSV export functionality
- #145: Implement parallel processing

## Improvements
- #146: Optimize cache performance

## Bug Fixes
- #147: Fix memory leak in scanner

## Security
- #148: Validate file paths against traversal
```

### Pattern 3: PR Linkage

```bash
# Link PR to issue and milestone
/gh:projects-sync link-pr 156 --issue 142 --milestone v3.8.0

# Workflow:
# 1. Update PR description with "Closes #142"
# 2. Link PR to project board
# 3. Add milestone to PR
# 4. Report: "Linked PR #156 to issue #142 (milestone v3.8.0)"
```

## Examples

### Sync Milestone to Project Board

```bash
/gh:projects-sync milestone v3.8.0

# Fetches all v3.8.0 milestone issues
# Updates project board status based on issue/PR state:
#   - Closed issues → "Done"
#   - Open PRs → "In Review"
#   - Open issues → Keep current status
# Reports: "Synced 12 issues: 5 Done, 3 In Review, 4 In Progress"
```

### Generate Draft Release Notes

```bash
/gh:projects-sync release-notes v3.8.0 --draft

# Fetches closed milestone issues
# Groups by label:
#   - feature → New Features
#   - bugfix → Bug Fixes
#   - hotfix → Security (if critical)
#   - docs → Documentation
# Generates markdown with sections
# Saves to: docs/archive/summaries/v3.8.0-release-notes.md
# Reports: "Generated draft release notes with 8 items"
```

### Generate and Create Release Issue

```bash
/gh:projects-sync release-notes v3.8.0

# Same as --draft but also creates GitHub issue:
# Title: "Release v3.8.0"
# Body: Release notes content
# Labels: release, milestone-v3.8.0
# Reports: "Created release tracking issue #160"
```

### Link PR to Issue

```bash
/gh:projects-sync link-pr 156 --issue 142 --milestone v3.8.0

# Updates PR #156:
#   - Description: Adds "Closes #142"
#   - Milestone: v3.8.0
#   - Project: Links to project board
# Reports: "Linked PR #156 to issue #142 (milestone v3.8.0)"
```

## Boundaries

**Will:**
- Sync milestone issues to project board automatically
- Generate release notes drafts from milestone issues
- Link PRs to issues and milestones
- Maintain project board field synchronization

**Will Not:**
- Create project boards (manual setup required, see GITHUB_PROJECTS_SETUP.md)
- Modify existing issues without explicit confirmation
- Close or delete milestones without user approval
- Auto-merge PRs or bypass review requirements

## Implementation Details

### Milestone Synchronization Logic

1. Fetch all issues for milestone:
   ```bash
   gh api repos/:owner/:repo/issues \
     --jq '.[] | select(.milestone.title=="v3.8.0")'
   ```

2. Group by state (open, closed) and PR status

3. Update project board items:
   - Closed issues → Move to "Done"
   - Issues with open PRs → Move to "In Review"
   - Open issues → Keep current status

4. Sync Priority/Complexity fields from labels:
   - Extract from repository labels
   - Update project custom fields
   - **Note**: GitHub Actions handles this automatically for label changes

**See**: [_gh-reference.md](_gh-reference.md#label-sync-timing) for label sync automation

5. Report summary with counts

### Release Notes Generation Logic

1. Fetch milestone issues:
   ```bash
   gh api repos/:owner/:repo/issues?milestone=N&state=closed
   ```

2. Group by labels:
   - `feature` → New Features section
   - `bugfix` → Bug Fixes section
   - `hotfix` → Security section
   - `docs` → Documentation section

3. Extract titles and issue numbers

4. Format as markdown:
   ```markdown
   ## New Features
   - #142: Add CSV export functionality
   - #143: Implement parallel processing
   ```

5. Save to `docs/archive/summaries/vX.Y.Z-release-notes.md`

6. Optional: Create release tracking issue with checklist

### Dependency Tracking

- Parse "blocked-by: #N" from issue body
- Update project board when dependencies resolve
- Move from "Blocked" to "Todo" when all blockers closed

## Error Handling

**Missing Milestone:**
```
Error: Milestone v3.8.0 not found
Action: Create milestone first:
  /gh:milestone create v3.8.0 --due YYYY-MM-DD
```

**Missing Project:**
```
Error: Project number not specified and no default configured
Action: Specify --project-number N or configure default in ~/.vscanrc
```

**No Closed Issues:**
```
Warning: Milestone v3.8.0 has no closed issues
Action: Release notes will be empty. Close issues first.
```

**See**: [_gh-reference.md](_gh-reference.md#common-error-patterns) for full error reference

## Rate Limiting

**API Call Estimates:**

| Operation | Issues in Milestone | API Calls |
|-----------|---------------------|-----------|
| Sync milestone (50 issues) | 50 | ~60 (fetch + update project fields) |
| Generate release notes | Any | ~25 (fetch milestone issues + metadata) |
| Link PR | 1 | ~5 (update PR + link to board) |

**Best Practices:**
1. Batch sync operations during off-hours
2. Scripts include automatic 0.5s delays
3. Monitor rate limit: `gh api rate_limit`

**See**: [_gh-reference.md](_gh-reference.md#rate-limiting-essentials) for rate limit management

## Integration with Release Process

### Phase 1.5: Issue Tracking (After Version Bump)

```bash
# After scripts/bump_version.py --milestone v3.8.0
/gh:projects-sync milestone v3.8.0

# Updates project board with release branch status
```

### Phase 3.5: Milestone Closure (After Tag Push)

```bash
# After git tag -a v3.8.0
/gh:projects-sync release-notes v3.8.0

# Creates release notes from milestone issues

# Close milestone issues
gh api repos/:owner/:repo/issues/<number>/comments \
  -F body="Released in v3.8.0"

# Close milestone
/gh:milestone close v3.8.0
```

**See**: [RELEASE_PROCESS.md](../../docs/contributing/RELEASE_PROCESS.md) for complete workflow

## Configuration

### ~/.vscanrc Extension

```ini
[github_projects]
default_project_number = 3
auto_sync_on_push = false
release_notes_dir = docs/archive/summaries
```

## References

- [GitHub Projects Workflow](../../docs/contributing/GITHUB_PROJECTS.md)
- [_gh-reference.md](_gh-reference.md) - Shared command reference
- [Release Process](../../docs/contributing/RELEASE_PROCESS.md)
- [Milestone Management](./milestone.md)
- [GITHUB_PROJECTS_SETUP.md](../../docs/contributing/GITHUB_PROJECTS_SETUP.md)
