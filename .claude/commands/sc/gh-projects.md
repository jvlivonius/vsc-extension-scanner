---
name: gh-projects
description: "GitHub Projects workflow integration with automated issue/PR linking"
category: workflow
complexity: standard
mcp-servers: []
personas: [python-expert]
---

# /sc:gh-projects - GitHub Projects Integration

## Triggers
- Feature planning requiring breakdown into GitHub issues
- Release coordination with milestone tracking
- Project board synchronization needs
- Release notes generation from milestone issues
- Multi-issue feature development workflows

## Usage
```
/sc:gh-projects create-from-plan <plan-file> --milestone vX.Y.Z [--project-number N]
/sc:gh-projects sync-milestone vX.Y.Z [--project-number N]
/sc:gh-projects generate-release-notes vX.Y.Z [--draft]
/sc:gh-projects link-pr <pr-number> --issue <issue-number> --milestone vX.Y.Z
```

**Parameters:**
- `<plan-file>`: Path to feature plan markdown (e.g., `docs/archive/plans/v3.8-feature.md`)
- `--milestone vX.Y.Z`: Target milestone version
- `--project-number N`: GitHub project number (optional, uses default if not specified)
- `--draft`: Generate draft release notes without creating GitHub issue

## Behavioral Flow
1. **Parse**: Analyze feature plan or milestone structure
2. **Validate**: Verify milestone exists, check project access, validate issue template
3. **Generate**: Create issues with proper metadata, dependencies, acceptance criteria
4. **Link**: Connect issues to milestone and project board
5. **Report**: Provide summary with issue numbers and next steps

Key behaviors:
- Parse feature plans into structured issue hierarchy (Feature → Tasks)
- Generate issues with required documentation links and acceptance criteria
- Link issues to milestones and project board automatically
- Generate release notes from closed milestone issues
- Maintain proper dependency chain in issue metadata

## Tool Coordination
- **gh CLI**: Issue/milestone/project management (`gh issue create`, `gh project`, `gh api`)
- **Read**: Feature plan parsing, issue template reading
- **Bash**: Git status verification, milestone validation
- **Write**: Release notes generation (draft format)

## Key Patterns

### Pattern 1: Feature Plan → Issues
```
Feature Plan Structure:
## Phase N: Phase Name
### N.1 Specific Task
#### Changes Required
...

Generated Issues:
- [FEATURE] Phase Name (#parent)
  - [TASK] N.1 Specific Task (blocked-by: #parent)
  - [TASK] N.2 Next Task (blocked-by: #previous)
```

### Pattern 2: Issue Metadata
```yaml
Milestone: vX.Y.Z
Labels: feature, P2-medium, complexity/M
Dependencies: blocked-by #N, blocks #M
Required Docs: ARCHITECTURE.md, SECURITY.md
Acceptance Criteria: [checklist from template]
```

### Pattern 3: Release Notes Generation
```
Input: Milestone vX.Y.Z with closed issues
Output: Release notes draft with:
- Summary
- Breaking Changes
- New Features (#issue)
- Improvements (#issue)
- Bug Fixes (#issue)
- Security (#issue)
```

## Examples

### Create Issues from Feature Plan
```bash
/sc:gh-projects create-from-plan docs/archive/plans/v3.8-feature.md --milestone v3.8.0

# Analyzes plan structure
# Creates parent feature issue: #142
# Creates task issues: #143, #144, #145
# Links to milestone and project board
# Reports: "Created 4 issues for v3.8.0: #142 (parent), #143-145 (tasks)"
```

### Sync Milestone with Project Board
```bash
/sc:gh-projects sync-milestone v3.8.0

# Fetches all milestone issues
# Updates project board status
# Moves closed issues to "Done"
# Reports: "Synced 12 issues: 5 Done, 3 In Progress, 4 Backlog"
```

### Generate Release Notes
```bash
/sc:gh-projects generate-release-notes v3.8.0 --draft

# Fetches closed milestone issues
# Groups by label (feature, bugfix, docs, etc.)
# Generates release notes markdown
# Saves to: docs/archive/summaries/v3.8.0-release-notes.md
# Reports: "Generated draft release notes with 8 items"
```

### Link PR to Issue and Milestone
```bash
/sc:gh-projects link-pr 156 --issue 142 --milestone v3.8.0

# Updates PR description with "Closes #142"
# Links PR to project board
# Adds milestone to PR
# Reports: "Linked PR #156 to issue #142 (milestone v3.8.0)"
```

## Boundaries

**Will:**
- Parse feature plans and create structured GitHub issues automatically
- Link issues to milestones and project boards with proper metadata
- Generate release notes drafts from milestone issues
- Maintain dependency chains and acceptance criteria in issues

**Will Not:**
- Create project boards (manual setup required, see GITHUB_PROJECTS_SETUP.md)
- Modify existing issues without explicit confirmation
- Close or delete milestones without user approval
- Auto-merge PRs or bypass review requirements

## Implementation Details

### Issue Creation Logic
1. Read feature plan markdown
2. Parse phases and tasks using heading structure
3. For each phase → create feature issue with template
4. For each task → create task issue linked to parent
5. Apply labels based on keywords (feature, bugfix, etc.)
6. Set complexity based on effort estimates
7. Link required documentation from project standards
8. Add acceptance criteria from templates

### Milestone Synchronization
1. Fetch all issues for milestone: `gh api repos/OWNER/REPO/milestones/NUMBER`
2. Group by state (open, closed)
3. Update project board items via GitHub API
4. Move items to appropriate columns based on PR status
5. Report summary with counts

### Release Notes Generation
1. Fetch milestone issues: `gh api repos/OWNER/REPO/issues?milestone=N&state=closed`
2. Group by labels: feature, bugfix, hotfix, docs, security
3. Extract titles and issue numbers
4. Format as markdown with proper sections
5. Save to `docs/archive/summaries/vX.Y.Z-release-notes.md`
6. Optional: Create release tracking issue with checklist

### Dependency Tracking
- Parse "blocked-by: #N" from issue body
- Validate dependencies exist before creating dependent issues
- Check dependency status before marking issue as agent-ready
- Update project board when dependencies resolve

## Error Handling

**Missing Milestone:**
```
Error: Milestone v3.8.0 not found
Action: Create milestone first with:
  gh api repos/OWNER/REPO/milestones -F title="v3.8.0" -F due_on="YYYY-MM-DD"
```

**Missing Project:**
```
Error: Project number not specified and no default configured
Action: Specify --project-number N or configure default in ~/.vscanrc
```

**Invalid Feature Plan:**
```
Error: Feature plan missing required sections (Phases, Tasks)
Action: Ensure plan follows template in docs/archive/plans/
```

**Dependency Loop:**
```
Error: Circular dependency detected: #142 → #143 → #142
Action: Review and fix dependency chain in issue metadata
```

## Integration with Release Process

### Phase 1.5: Issue Tracking (After Version Bump)
```bash
# After bump_version.py --milestone v3.8.0
/sc:gh-projects sync-milestone v3.8.0
# Updates project board with release branch status
```

### Phase 3.5: Milestone Closure (After Tag Push)
```bash
# After git tag -a v3.8.0
/sc:gh-projects generate-release-notes v3.8.0
# Creates release notes from milestone issues

# Close milestone issues
gh api repos/OWNER/REPO/issues/<number>/comments \
  -F body="Released in v3.8.0"

# Close milestone
gh api repos/OWNER/REPO/milestones/<number> \
  -X PATCH -F state="closed"
```

## Configuration

### ~/.vscanrc Extension
```ini
[github_projects]
default_project_number = 1
default_milestone_prefix = v
auto_link_prs = true
auto_sync_on_push = false
```

## References

- [GitHub Projects Setup Guide](../../contributing/GITHUB_PROJECTS_SETUP.md)
- [Issue Templates](.github/ISSUE_TEMPLATE/)
- [Release Process](../../contributing/RELEASE_PROCESS.md)
- [Git Workflow](../../contributing/GIT_WORKFLOW.md)
