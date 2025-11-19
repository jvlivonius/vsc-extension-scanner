# GitHub Projects Workflow Guide

**Daily development workflows and usage patterns for GitHub Projects V2.**

**Project:** [VS Code Extension Scanner Development (Project #3)](https://github.com/users/jvlivonius/projects/3)
**Setup:** See [GITHUB_PROJECTS_SETUP.md](GITHUB_PROJECTS_SETUP.md) for initial configuration

---

## Quick Access

**Project URL:** https://github.com/users/jvlivonius/projects/3

**Views:**
- **Kanban Board** - Daily work, drag cards between columns
- **Detailed Table** - All fields, sorting, filtering
- **Release Roadmap** - Timeline view by milestone

---

## Core Concepts

### Labels vs Fields

**Repository Labels** (show on issue page):
- `feature`, `bugfix`, `hotfix`, `task`, `release`
- `P0-critical`, `P1-high`, `P2-medium`, `P3-low`
- `complexity/XS`, `complexity/S`, `complexity/M`, `complexity/L`, `complexity/XL`

**Project Custom Fields** (show in project views):
- **Status** - Backlog, Todo, In Progress, In Review, Done, Blocked
- **Priority** - Critical, High, Medium, Low (auto-synced from labels)
- **Complexity** - XS, S, M, L, XL (auto-synced from labels)

**Built-in Milestone Field** (auto-synced from repository milestones):
- Use for version tracking: v3.8.0, v3.9.0, v4.0.0
- Don't create custom "Release" field

**Built-in Issue Dependencies** (Blocked by/Blocking):
- Set via issue sidebar → Relationships section
- Creates bidirectional link with visual "Blocked" indicator
- Up to 50 issues per relationship type
- Don't create custom "Dependencies" field

**Documentation Requirements** (text field):
- YAML issue templates include "Required Documentation" text input field
- Comma-separated format: "ARCHITECTURE.md, SECURITY.md, PRD.md"
- Claude Code agents parse and read required docs before implementation

**Auto-Sync:** Priority and Complexity labels automatically sync to project fields via GitHub Actions.

---

## Daily Workflows

### Creating Issues

**Recommended: Use YAML issue templates via web UI**

Navigate to: https://github.com/jvlivonius/vsc-extension-scanner/issues/new/choose

**Available templates:**
- `feature.yml` - Feature implementation with structured documentation requirements
- `task.yml` - Implementation task with effort estimation
- `release.yml` - Release tracking with comprehensive checklist

**Via CLI (for programmatic workflows):**
```bash
# Create feature with labels
gh issue create \
  --title "[FEATURE] Add CSV export" \
  --body "$(cat <<'EOF'
## Summary
Export scan results as CSV format

## Required Documentation
ARCHITECTURE.md, SECURITY.md, PRD.md

## Dependencies
Blocked By: None
Blocks: None
EOF
)" \
  --label "feature,P1-high,complexity/M" \
  --milestone "v3.8.0"

# Result:
# 1. Issue created with labels
# 2. Auto-added to Project #3 (Status = "Backlog")
# 3. Priority field set to "High" (auto-synced from P1-high label)
# 4. Complexity field set to "M" (auto-synced from complexity/M label)
# 5. Milestone field shows "v3.8.0" (auto-synced)
# 6. Required docs field parsed by agents before implementation
```

**Setting dependencies:**
```bash
# Dependencies set via issue sidebar → Relationships section (web UI)
# Or programmatically during issue creation via API
# Claude Code /sc:implement-issue parses "Blocked By:" from issue body
```

### Moving Issues Through Workflow

**Kanban Board View:**
1. Filter high-priority backlog: `status:Backlog priority:High`
2. Drag issue from "Backlog" → "Todo" (ready to work)
3. Drag issue from "Todo" → "In Progress" (start work)
4. Create PR with `Closes #142` in description
5. Auto-workflow moves to "In Review"
6. Merge PR → Auto-workflow moves to "Done"

### Updating Fields Manually

**Web UI:**
- Table view → Click cell → Select value
- Board view → Drag card between columns (updates Status)

**CLI (requires GraphQL):**
```bash
# Assign to milestone
gh issue edit 142 --milestone "v3.8.0"

# Update labels (triggers auto-sync to Priority/Complexity fields)
gh issue edit 142 --add-label "P0-critical"
gh issue edit 142 --remove-label "P1-high"
```

---

## Common Filters

**Important:** Multi-word values must be quoted.

| Filter | Usage |
|--------|-------|
| `status:Backlog,Todo` | Items ready to work |
| `status:"In Progress"` | Currently being worked (multi-word needs quotes) |
| `priority:Critical,High` | High-priority items |
| `milestone:"v3.8.0"` | Specific release (quote versions with dots) |
| `-status:Done` | Exclude completed |
| `assignee:@me` | Your assigned items |
| `sprint:@current` | Current sprint (if using sprints) |
| `label:bug` | Items with bug label |
| `no:assignee` | Unassigned items |

**Combining filters:**
```
status:Backlog,Todo priority:Critical,High -assignee:@me
```
Result: High-priority backlog items not assigned to you

---

## Slash Commands

### `/sc:gh-projects` - Project Workflow Automation

**Create issues from feature plan:**
```bash
/sc:gh-projects create-from-plan docs/archive/plans/v3.8-csv-export.md --milestone v3.8.0
```
Parses markdown plan → Creates parent feature + task issues → Links to milestone → Auto-adds to project

**Generate release notes:**
```bash
/sc:gh-projects generate-release-notes v3.8.0 --draft
```
Fetches milestone issues → Groups by type → Formats as markdown → Saves to `docs/archive/summaries/`

**Sync milestone status:**
```bash
/sc:gh-projects sync-milestone v3.8.0
```
Updates project board from milestone status → Reports summary

### `/sc:implement-issue` - Agent-Driven Implementation

**Basic implementation:**
```bash
/sc:implement-issue 142
```

**What it does:**
1. Fetches issue #142 details (title, body, labels, milestone)
2. Validates prerequisites (dependencies resolved)
3. Parses "Required Documentation" field (comma-separated: "ARCHITECTURE.md, SECURITY.md")
4. Reads each required document before implementation
5. Creates feature branch
6. Implements code following acceptance criteria with tests
7. Runs quality gates (pytest, security, architecture)
8. Creates PR with `Closes #142`
9. Updates issue with `agent-implemented` label

**Options:**
```bash
/sc:implement-issue 143 --branch feature/custom-name  # Custom branch
/sc:implement-issue 144 --dry-run                     # Validate only
/sc:implement-issue 145 --no-pr                       # No PR creation
```

---

## Automatic Field Sync

**How it works:**
- Add/remove labels → GitHub Actions triggers → Project fields update
- Highest priority wins: P0 > P1 > P2 > P3
- Smallest complexity wins: XS > S > M > L > XL

**Examples:**
```bash
# Set priority
gh issue edit 142 --add-label "P1-high"
# → Priority field automatically set to "High"

# Change priority
gh issue edit 142 --remove-label "P1-high" --add-label "P0-critical"
# → Priority field automatically updated to "Critical"

# Clear priority
gh issue edit 142 --remove-label "P0-critical"
# → Priority field cleared (null)

# Set complexity
gh issue edit 142 --add-label "complexity/M"
# → Complexity field automatically set to "M"
```

**Troubleshooting:**
```bash
# Check workflow runs
gh run list --workflow=sync-project-fields.yml

# View specific run
gh run view <run-id> --log

# Re-fetch IDs if fields recreated
./scripts/github-projects/get-project-ids.sh
```

---

## Feature Implementation Workflow

### 1. Plan → Issues

**Input:** Feature plan markdown (e.g., `docs/archive/plans/v3.8-csv-export.md`)

```bash
/sc:gh-projects create-from-plan docs/archive/plans/v3.8-csv-export.md --milestone v3.8.0
```

**Output:**
- Parent feature issue: `[FEATURE] Add CSV export functionality`
- Task issues: `[TASK] Implement CSV formatter class`
- All linked to milestone v3.8.0
- All auto-added to Project #3

### 2. Select → Implement

**Kanban Board:**
1. Filter: `status:Backlog priority:High milestone:"v3.8.0"`
2. Select ready issue (dependencies closed)
3. Drag to "Todo"
4. Note issue number (e.g., #142)

**Trigger agent:**
```bash
/sc:implement-issue 142
```

**Result:**
- Branch created: `feature/add-csv-export`
- Code implemented with tests
- PR created with `Closes #142`
- Status auto-updated to "In Review"

### 3. Review → Merge

**Manual actions:**
1. Review PR on GitHub
2. Test changes locally
3. Request changes or approve
4. Merge PR

**Auto-workflow:**
- PR merged → Status = "Done"
- Issue closed (via `Closes #142`)

### 4. Release

**When all milestone issues closed:**
```bash
python3 scripts/bump_version.py 3.8.0 --auto-update --milestone --create-release-issue
```

**Creates:**
- Release tracking issue: `[RELEASE] v3.8.0`
- Repository milestone (if not exists)
- Auto-adds to project

**Generate release notes:**
```bash
/sc:gh-projects generate-release-notes v3.8.0
```

---

## Common Issues

### Labels Don't Show as Board Columns

**Problem:** Created labels but they don't appear as columns.

**Solution:** Repository labels ≠ Project fields. Create custom "Status" field with options, then set as column field in Board view.

### Items Not Auto-Adding

**Check:**
1. Auto-add workflow enabled: Project menu → Workflows → Auto-add → ON
2. Filter matches issue: `is:issue,pr is:open -label:duplicate`
3. Repository selected: `jvlivonius/vsc-extension-scanner`

### Can't Group by Labels

**Problem:** "Group by" doesn't show "Labels" option.

**Solution:** Create custom single-select field (e.g., "Priority") and group by that. Labels are multi-value, grouping requires single-value.

### Custom Fields Don't Show on Issue Page

**Expected behavior:** Custom fields are project-scoped, not repository-scoped. Use labels for issue page visibility.

### Milestone Field Missing

**Solution:** Milestone is a built-in field. Enable it: View menu → Fields → Toggle ON "Milestone". Don't create custom "Release" field.

### Field Sync Not Working

**Check:**
```bash
# Workflow runs
gh run list --workflow=sync-project-fields.yml

# Repository variables exist
gh variable list  # Should show PROJECT_ID, PRIORITY_FIELD_ID, etc.

# Issue in project
# Verify issue was auto-added to Project #3
```

**Fix:** Re-run ID script if fields were recreated:
```bash
./scripts/github-projects/get-project-ids.sh
# Copy and run all output commands
```

---

## UI Quick Reference

| Element | Location | Shortcut |
|---------|----------|----------|
| Project Menu | Top-right (...) | Settings, Workflows |
| View Menu | Next to view name (▼) | Layout, Fields, Group, Sort, Filter |
| Field Menu | Table header (▼) | Edit field, Hide |
| Add Field | Table rightmost (+) | Create field |
| Command Palette | - | Cmd/Ctrl + K |

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Command palette | Cmd/Ctrl + K |
| Edit item | E |
| Copy item URL | C |
| Save and close | Cmd/Ctrl + Enter |
| Navigate items | ↑ ↓ arrows |

---

## Best Practices

1. **Use labels for categorization** - Shows on issue page
2. **Use custom fields for workflow** - Shows in project views
3. **Use Milestone for version tracking** - Auto-synced from repository
4. **Let automation handle Status** - Auto-add, auto-close workflows
5. **Let Actions sync Priority/Complexity** - Add labels, fields update automatically
6. **Filter aggressively** - Focus on relevant items only
7. **Archive completed items** - Keep board clean (manual or auto after 30 days)

---

## References

- **Setup Guide:** [GITHUB_PROJECTS_SETUP.md](GITHUB_PROJECTS_SETUP.md)
- **Release Process:** [RELEASE_PROCESS.md](RELEASE_PROCESS.md)
- **Git Workflow:** [GIT_WORKFLOW.md](GIT_WORKFLOW.md)
- **GitHub Projects Docs:** https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **GitHub CLI Projects:** https://cli.github.com/manual/gh_project
