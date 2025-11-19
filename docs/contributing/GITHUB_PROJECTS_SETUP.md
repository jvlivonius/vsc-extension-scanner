# GitHub Projects Setup Guide

**One-time initial configuration for GitHub Projects V2 integration.**

---

## Prerequisites

✅ GitHub CLI authenticated with project permissions
✅ Token scopes: `project`, `read:project`, `repo`, `workflow`

```bash
# Verify authentication
gh auth status
```

---

## 1. Create Project Board

### Via GitHub CLI (Recommended)

```bash
gh project create \
  --owner jvlivonius \
  --title "VS Code Extension Scanner Development" \
  --format json
```

**Result:** Project #3 at https://github.com/users/jvlivonius/projects/3

### Via Web UI

1. Navigate to: https://github.com/jvlivonius/projects
2. Click "New project" → Select "Table" view
3. Title: "VS Code Extension Scanner Development"

---

## 2. Create Custom Fields

Navigate to project → Table view → Click **"+"** in rightmost field header

### Required Fields

| Field Name | Type | Options |
|-----------|------|---------|
| **Status** | Single select | Backlog, Todo, In Progress, In Review, Done, Blocked |
| **Priority** | Single select | Critical, High, Medium, Low |
| **Complexity** | Single select | XS, S, M, L, XL |

**Important:** Set "Status" default to "Backlog", "Priority" default to "Medium"

### Optional Fields

| Field Name | Type | Purpose |
|-----------|------|---------|
| **Theme** | Single select | Feature area grouping (Scanning, API, Cache, CLI, Security, Testing) |
| **Estimate** | Number | Hours or story points |
| **Sprint** | Iteration | 2-week cycles (if using sprints) |
| **Planned Start** | Date | For roadmap view |
| **Target Completion** | Date | For roadmap view |

**Note:** Use built-in features instead of custom fields for:
- **Milestone** field for version tracking (v3.8.0, v3.9.0) - don't create custom "Release" field
- **Issue Dependencies** (Blocked by/Blocking) for dependencies - don't create custom "Dependencies" field
- **Text input fields** in YAML issue templates for documentation requirements - don't create custom "Required Docs" field

---

## 3. Configure Views

### View 1: Kanban Board (Primary)

1. Click **"+"** → "New view" → Name: "Kanban Board"
2. View menu (▼) → Layout → **Board**
3. View menu → Column field → **Status**
4. View menu → Group by → **Priority** (swimlanes)
5. View menu → Field sum → **Estimate**
6. View menu → Fields → Toggle ON: Assignees, Labels, Milestone, Priority, Complexity

### View 2: Detailed Table

1. Click **"+"** → "New view" → Name: "Detailed View"
2. View menu → Group by → **Status**
3. View menu → Sort → **Priority** (descending)
4. View menu → Field sum → **Estimate**
5. View menu → Fields → Toggle ON all fields

### View 3: Release Roadmap (Optional)

Requires "Planned Start" and "Target Completion" date fields.

1. Click **"+"** → "New view" → Name: "Release Roadmap"
2. View menu → Layout → **Roadmap**
3. View menu → Roadmap settings → Start: Planned Start, Target: Target Completion
4. View menu → Group by → **Milestone**

---

## 4. Setup Automation Rules

### Built-In Workflows (Auto-Enabled)

Navigate to Project menu (...) → Workflows

✅ **Item closed** → Set status to "Done" (pre-enabled)
✅ **Pull request merged** → Set status to "Done" (pre-enabled)
✅ **Item reopened** → Restore previous status (pre-enabled)

### Configure Auto-Add Workflow

1. Find "Auto-add to project" workflow → Edit
2. Repository: `jvlivonius/vsc-extension-scanner`
3. Filter: `is:issue,pr is:open -label:duplicate`
4. Toggle **ON** → Save

### Configure Auto-Status on Add

1. Find "Item added to project" workflow → Edit
2. When: Item added to project
3. Set: Status → **Backlog**
4. Toggle **ON** → Save

---

## 5. Create Repository Labels

```bash
# Type labels
gh label create "feature" --description "New feature" --color "0e8a16"
gh label create "bugfix" --description "Bug fix" --color "d73a4a"
gh label create "hotfix" --description "Critical security/data fix" --color "b60205"
gh label create "task" --description "Implementation task" --color "fbca04"
gh label create "release" --description "Release tracking" --color "5319e7"

# Priority labels
gh label create "P0-critical" --description "Critical priority" --color "b60205"
gh label create "P1-high" --description "High priority" --color "d93f0b"
gh label create "P2-medium" --description "Medium priority" --color "fbca04"
gh label create "P3-low" --description "Low priority" --color "0e8a16"

# Status labels
gh label create "agent-ready" --description "Ready for agent implementation" --color "7057ff"
gh label create "agent-implemented" --description "Implemented by Claude Code agent" --color "5319e7"
gh label create "blocked" --description "Blocked by dependencies" --color "d4c5f9"
gh label create "needs-review" --description "Needs human review" --color "fef2c0"

# Complexity labels
gh label create "complexity/XS" --description "< 2 hours" --color "c2e0c6"
gh label create "complexity/S" --description "2-4 hours" --color "bfdadc"
gh label create "complexity/M" --description "4-8 hours" --color "fef2c0"
gh label create "complexity/L" --description "1-2 days" --color "fad8c7"
gh label create "complexity/XL" --description "> 2 days" --color "f9d0c4"
```

**Note:** Documentation requirements are handled via text input fields in YAML issue templates (`.github/ISSUE_TEMPLATE/*.yml`), not labels. See templates for "Required Documentation" field with comma-separated format: "ARCHITECTURE.md, SECURITY.md, PRD.md"

---

## 6. Setup Automatic Field Sync

**Automatically sync Priority and Complexity labels to project fields.**

### Prerequisites

✅ Workflow files exist:
- `.github/workflows/sync-project-fields.yml`
- `.github/actions/sync-project-field/action.yml`

### Fetch Project IDs

```bash
cd /Users/joerg.von.livonius/Development/vsc-extension-scanner
./scripts/github-projects/get-project-ids.sh
```

**Output:** Commands to set repository variables with Project, Field, and Option IDs.

### Set Repository Variables

Copy and run all commands from script output:

```bash
# Project ID
gh variable set PROJECT_ID --body "PVT_..."

# Priority field
gh variable set PRIORITY_FIELD_ID --body "PVTSSF_..."
gh variable set PRIORITY_CRITICAL_OPTION_ID --body "..."
gh variable set PRIORITY_HIGH_OPTION_ID --body "..."
gh variable set PRIORITY_MEDIUM_OPTION_ID --body "..."
gh variable set PRIORITY_LOW_OPTION_ID --body "..."

# Complexity field
gh variable set COMPLEXITY_FIELD_ID --body "PVTSSF_..."
gh variable set COMPLEXITY_XS_OPTION_ID --body "..."
gh variable set COMPLEXITY_S_OPTION_ID --body "..."
gh variable set COMPLEXITY_M_OPTION_ID --body "..."
gh variable set COMPLEXITY_L_OPTION_ID --body "..."
gh variable set COMPLEXITY_XL_OPTION_ID --body "..."
```

### Test Automation

```bash
# Create test issue
gh issue create --title "Test automatic field sync" --body "Testing" --label "P1-high,complexity/M"

# Verify workflow ran
gh run list --workflow=sync-project-fields.yml

# Check project board - Priority should be "High", Complexity should be "M"
```

---

## 7. Enable Built-in Milestone Field

### Create Repository Milestones

```bash
# Via CLI
gh api repos/jvlivonius/vsc-extension-scanner/milestones \
  -F title="v3.8.0" \
  -F description="Release 3.8.0" \
  -F due_on="2025-12-15T00:00:00Z"
```

Or via web UI: https://github.com/jvlivonius/vsc-extension-scanner/milestones

### Enable in Project Views

1. Navigate to project → Table view
2. View menu (▼) → Fields
3. Toggle **ON**: Milestone
4. Result: Milestone column appears, auto-synced from repository

---

## 8. Built-in Issue Dependencies

GitHub Projects V2 supports native dependency tracking via "Blocked by/Blocking" relationships.

**How to set dependencies:**

Via Web UI:
1. Open issue → Sidebar → "Relationships" section
2. Click "Mark as blocked by" or "Mark as blocking"
3. Select up to 50 issues per relationship type
4. Blocked issues show "Blocked" icon on project boards

Via Issue Creation:
- Dependencies can be set programmatically during issue creation via API
- Claude Code `/sc:gh-projects create-from-plan` automatically sets "blocked-by" relationships based on task hierarchy

**Features:**
- ✅ Bidirectional linking (automatically updates both issues)
- ✅ Visual "Blocked" indicator on project boards and issue lists
- ✅ Up to 50 relationships per type
- ✅ API support for automation (GraphQL and REST)
- ✅ Filterable in project views

**Use this instead of a custom "Dependencies" field.**

---

## 9. Verification

```bash
# List projects
gh project list --owner jvlivonius

# List labels
gh label list

# List repository variables
gh variable list

# Should show:
# - PROJECT_ID
# - PRIORITY_FIELD_ID + option IDs (4)
# - COMPLEXITY_FIELD_ID + option IDs (5)
```

**Web UI Checklist:**
- ✅ Project #3 exists and loads
- ✅ Custom fields visible in Table view
- ✅ Kanban Board view shows Status columns
- ✅ Auto-add workflow enabled
- ✅ Test issue appears in project with correct fields

---

## Troubleshooting

### Issue Not Auto-Added to Project

**Symptom**: Created issue doesn't appear in Project #3

**Common Causes:**
1. **Auto-add workflow not configured properly**
2. **Repository not selected in filter**
3. **Issue matches exclusion filter**

**Solution:**
```bash
# 1. Check auto-add workflow configuration (Web UI Required)
# Navigate to: https://github.com/users/jvlivonius/projects/3
# → Click "..." menu → Workflows → "Auto-add to project"
# → Verify:
#   - Toggle: ON
#   - Repository: jvlivonius/vsc-extension-scanner (CHECKED)
#   - Filter: is:issue,pr is:open -label:duplicate
# → Save if changes needed

# 2. Manually add issue as workaround
gh project item-add 3 --owner jvlivonius --url https://github.com/jvlivonius/vsc-extension-scanner/issues/<number>

# 3. Test with new issue
gh issue create --title "[TEST] Auto-add test" --body "Testing" --label "feature"
# Wait 1-2 minutes, then check project board
```

### Field Sync Workflow Failing

**Symptom**: Workflow fails with exit code 1

**Common Causes:**
1. **Repository variables not set** (PROJECT_ID, field IDs, option IDs)
2. **Issue not in project** (sync can't update fields for non-project items)
3. **GraphQL query errors**

**Solution:**
```bash
# 1. Verify repository variables exist
gh variable list
# Should show: PROJECT_ID, PRIORITY_FIELD_ID, COMPLEXITY_FIELD_ID, and all option IDs

# 2. If variables missing, re-run ID script
./scripts/github-projects/get-project-ids.sh
# Copy and run all output commands

# 3. Check workflow logs
gh run list --workflow=sync-project-fields.yml
gh run view <run-id> --log

# 4. Manually add issue to project first
gh project item-add 3 --owner jvlivonius --url https://github.com/jvlivonius/vsc-extension-scanner/issues/<number>

# 5. Re-trigger sync by adding/removing label
gh issue edit <number> --remove-label "P2-medium" --add-label "P1-high"
```

### Custom Fields Not Showing

**Symptom**: Priority or Complexity fields missing from project views

**Solution:**
```bash
# 1. Enable fields in view (Web UI)
# Project #3 → Table view → View menu (▼) → Fields
# → Toggle ON: Priority, Complexity

# 2. Verify fields exist in project
# Project #3 → Settings (⚙️) → Fields
# → Should show: Priority (Critical, High, Medium, Low)
# →              Complexity (XS, S, M, L, XL)

# 3. If fields missing, create them manually:
# Project #3 → Settings → Fields → New field
# → Name: Priority, Type: Single select
# → Options: Critical, High, Medium, Low
# Repeat for Complexity with options: XS, S, M, L, XL

# 4. Re-run ID script to get new field IDs
./scripts/github-projects/get-project-ids.sh
```

### Milestone Field Not Visible

**Symptom**: Can't see milestone column in project views

**Solution:**
```bash
# Milestone is a BUILT-IN field, not custom

# 1. Enable in view (Web UI)
# Project #3 → Table view → View menu (▼) → Fields
# → Toggle ON: Milestone

# 2. Create milestones in repository
gh api repos/jvlivonius/vsc-extension-scanner/milestones \
  -F title="v3.8.0" \
  -F description="Release 3.8.0"

# 3. Assign milestone to issues
gh issue edit <number> --milestone "v3.8.0"
```

### Labels Not Syncing to Fields

**Symptom**: Adding priority/complexity labels doesn't update project fields

**Common Causes:**
1. **Workflow not triggered** (issue/PR not in watched events)
2. **Issue not in project** (can't update fields for non-project items)
3. **Variable mismatch** (label value doesn't match expected format)

**Solution:**
```bash
# 1. Verify workflow triggers
cat .github/workflows/sync-project-fields.yml | grep -A 5 "on:"
# Should include: issues.types [opened, labeled, unlabeled]

# 2. Check recent workflow runs
gh run list --workflow=sync-project-fields.yml --limit 10

# 3. Verify label format
gh label list | grep -E "P[0-3]|complexity"
# Should show: P0-critical, P1-high, P2-medium, P3-low
#              complexity/XS, complexity/S, complexity/M, complexity/L, complexity/XL

# 4. Test sync manually
gh issue edit <number> --add-label "P1-high"
# Wait 30 seconds, then check project board

# 5. If still failing, check workflow logs
gh run list --workflow=sync-project-fields.yml
gh run view <latest-run-id> --log
```

### Can't Filter by Documentation Requirements

**Note**: As of the latest version, documentation requirements use a text input field, not labels.

**To find issues by required docs:**
```bash
# Search issue bodies
gh issue list --json number,title,body --jq '.[] | select(.body | contains("ARCHITECTURE.md")) | "\(.number): \(.title)"'

# Or use project view filters with text search
# Project #3 → Filter: text:"ARCHITECTURE.md"
```

---

## Next Steps

Setup complete. See [GITHUB_PROJECTS.md](GITHUB_PROJECTS.md) for:
- Daily development workflows
- Using filters and views
- Slash command reference
- Common workflow patterns

---

## References

- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub CLI Projects](https://cli.github.com/manual/gh_project)
- [Project Automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project)
