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
# Claude Code /gh:implement-issue parses "Blocked By:" from issue body
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

### `/gh:projects` - Project Workflow Automation

**Create issues from feature plan:**
```bash
/gh:projects create-from-plan docs/archive/plans/v3.8-csv-export.md --milestone v3.8.0
```
Parses markdown plan → Creates parent feature + task issues → Links to milestone → Auto-adds to project

**Generate release notes:**
```bash
/gh:projects generate-release-notes v3.8.0 --draft
```
Fetches milestone issues → Groups by type → Formats as markdown → Saves to `docs/archive/summaries/`

**Sync milestone status:**
```bash
/gh:projects sync-milestone v3.8.0
```
Updates project board from milestone status → Reports summary

### `/gh:implement-issue` - Agent-Driven Implementation

**Basic implementation:**
```bash
/gh:implement-issue 142
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
/gh:implement-issue 143 --branch feature/custom-name  # Custom branch
/gh:implement-issue 144 --dry-run                     # Validate only
/gh:implement-issue 145 --no-pr                       # No PR creation
```

### `/gh:milestone` - Milestone Management

**Track milestone progress and manage release coordination:**
```bash
/gh:milestone create v3.8.0 --due 2025-01-15
/gh:milestone report v3.8.0 --format markdown
/gh:milestone sync v3.8.0
/gh:milestone close v3.8.0 --generate-notes
/gh:milestone list --state open
```

**What it does:**
1. **create**: Creates new milestone with due date and description
2. **report**: Generates comprehensive progress report using `generate-milestone-report.sh`
   - Shows completion percentage, issue breakdown by type/priority
   - Outputs markdown (default) or JSON format
3. **sync**: Synchronizes milestone issues with project board
4. **close**: Closes milestone and optionally generates release notes
   - Validates no open P0 issues before closing
   - Integrates with `/gh:projects generate-release-notes`
5. **list**: Lists milestones filtered by state

**Example workflow:**
```bash
# Create milestone
/gh:milestone create v3.8.0 --due 2025-01-15 --description "CSV export feature"

# Check progress during development
/gh:milestone report v3.8.0

# Close when complete
/gh:milestone close v3.8.0 --generate-notes
```

### `/gh:triage` - AI-Assisted Issue Triage

**Intelligently classify and prioritize issues:**
```bash
/gh:triage 160                                    # Single issue
/gh:triage --batch --milestone v3.8.0             # Batch processing
/gh:triage --review 160 --suggest-improvements    # Quality review
/gh:triage 161 --auto-apply                       # Auto-apply if confident
```

**What it does:**
1. **Fetch**: Retrieves issue details (title, body, labels, comments)
2. **Analyze**: Uses sequential-thinking MCP for:
   - Type classification (feature, bug, task, hotfix)
   - Priority assessment (P0-P3 based on impact/urgency)
   - Complexity estimation (XS, S, M, L, XL)
   - Required documentation identification
   - Similar issue detection (duplicate prevention)
3. **Suggest**: Generates recommendations with confidence scores
4. **Apply**: Optionally updates issue with labels (requires confirmation unless --auto-apply with >90% confidence)

**Confidence thresholds:**
- **>0.9**: Auto-apply safe (if --auto-apply flag)
- **0.7-0.9**: High confidence (suggest with approval)
- **0.5-0.7**: Medium confidence (manual review)
- **<0.5**: Low confidence (requires human judgment)

**Batch mode:**
```bash
# Triage all untriaged issues in milestone
/gh:triage --batch --milestone v3.8.0

# High confidence suggestions auto-applied
# Low confidence issues flagged for manual review
```

### Command Quick Reference

| Command | Purpose | Common Usage |
|---------|---------|--------------|
| `/gh:projects create-from-plan` | Create issues from feature plan | `/gh:projects create-from-plan docs/archive/plans/v3.8-feature.md --milestone v3.8.0` |
| `/gh:projects sync-milestone` | Sync milestone to project board | `/gh:projects sync-milestone v3.8.0` |
| `/gh:projects generate-release-notes` | Generate release notes from milestone | `/gh:projects generate-release-notes v3.8.0 --draft` |
| `/gh:implement-issue` | Agent-driven implementation | `/gh:implement-issue 142` |
| `/gh:milestone create` | Create new milestone | `/gh:milestone create v3.8.0 --due 2025-01-15` |
| `/gh:milestone report` | Generate progress report | `/gh:milestone report v3.8.0` |
| `/gh:milestone close` | Close milestone with notes | `/gh:milestone close v3.8.0 --generate-notes` |
| `/gh:triage` | AI-assisted issue triage | `/gh:triage 160` or `/gh:triage --batch --milestone v3.8.0` |

**Helper Scripts:**

| Script | Purpose | Common Usage |
|--------|---------|--------------|
| `create-issue.sh` | Create GitHub issue with metadata | `./scripts/github-projects/create-issue.sh --type feature --title "..." --milestone v3.8.0` |
| `manage-issue-relationships.sh` | Manage parent-child & blocking | `./scripts/github-projects/manage-issue-relationships.sh set-parent 142 143 144` |
| `validate-issue-structure.sh` | Validate issue completeness | `./scripts/github-projects/validate-issue-structure.sh 142 --strict` |
| `generate-milestone-report.sh` | Generate milestone report | `./scripts/github-projects/generate-milestone-report.sh v3.8.0` |
| `sync-existing-issues.sh` | Sync labels to project fields | `./scripts/github-projects/sync-existing-issues.sh` |

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
/gh:projects create-from-plan docs/archive/plans/v3.8-csv-export.md --milestone v3.8.0
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
/gh:implement-issue 142
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
/gh:projects generate-release-notes v3.8.0
```

---

## Relationship Types Decision Tree

### When to Use Parent-Child Relationships

**Use Case:** Feature breakdown, hierarchical task organization, epic → story structure

**Characteristics:**

- **Visual hierarchy:** Parent issues show summary of child progress
- **One parent per child:** Each child can have only one parent
- **GraphQL API:** Requires `addSubIssue` mutation
- **Limit:** Up to 100 sub-issues per parent

**Example scenarios:**
```
[FEATURE] Add CSV Export (#142)
  ├─ [TASK] Implement CSV formatter class (#143)
  ├─ [TASK] Add export command to CLI (#144)
  └─ [TASK] Add CSV export tests (#145)
```

**When to use:**

- Feature split into multiple implementation tasks
- Epic requires multiple sub-features
- Release tracking with multiple component issues
- Large refactoring split into smaller PRs

**How to create:**
```bash
# Create all issues first
gh issue create --title "[FEATURE] Add CSV Export" ...
gh issue create --title "[TASK] Implement CSV formatter" ...

# Set parent-child relationships
./scripts/github-projects/manage-issue-relationships.sh set-parent 142 143 144 145

# Verify
./scripts/github-projects/manage-issue-relationships.sh view 142
```

### When to Use Blocking Relationships

**Use Case:** Technical dependencies, sequential implementation order, blocked work

**Characteristics:**

- **Bidirectional:** Issue A blocks Issue B, Issue B is blocked by Issue A
- **Visual indicator:** "Blocked" badge shows on issues
- **REST API:** Easy to set via issue dependencies endpoint
- **Limit:** Up to 50 blockers per issue

**Example scenarios:**
```
#146 [TASK] Add database migration (blocks #147, #148)
  ↓ blocks
#147 [TASK] Implement new API endpoint (blocked by #146)
  ↓ blocks
#148 [TASK] Update UI for new API (blocked by #147)
```

**When to use:**

- Issue B cannot start until Issue A completes
- Database migrations must run before code changes
- API endpoint must exist before UI integration
- Foundation work required before dependent features

**How to create:**
```bash
# Set blocker: 146 blocks 147
./scripts/github-projects/manage-issue-relationships.sh set-blocker 147 146

# Set multiple blockers: 146 and 147 both block 148
./scripts/github-projects/manage-issue-relationships.sh set-blocker 148 146 147

# Verify
./scripts/github-projects/manage-issue-relationships.sh view 148
```

### When to Use Both

**Use Case:** Complex features with hierarchical breakdown AND technical dependencies

**Example:**
```
[FEATURE] Database Refactoring (#150)
  ├─ [TASK] Design new schema (#151)
  ├─ [TASK] Create migration scripts (#152) [blocked by #151]
  ├─ [TASK] Update data access layer (#153) [blocked by #152]
  └─ [TASK] Add integration tests (#154) [blocked by #153]
```

**Relationships:**

- **Parent-child:** #150 is parent of #151-154 (shows feature breakdown)
- **Blocking:** #151 → #152 → #153 → #154 (enforces implementation order)

**When to use:**

- Large features with sequential task dependencies
- Release planning with cross-feature dependencies
- Refactoring projects with ordered migrations

**How to create:**
```bash
# Create issues
gh issue create --title "[FEATURE] Database Refactoring" ...
# ... create task issues ...

# Set parent-child (feature breakdown)
./scripts/github-projects/manage-issue-relationships.sh set-parent 150 151 152 153 154

# Set blocking (implementation order)
./scripts/github-projects/manage-issue-relationships.sh set-blocker 152 151
./scripts/github-projects/manage-issue-relationships.sh set-blocker 153 152
./scripts/github-projects/manage-issue-relationships.sh set-blocker 154 153

# Verify all relationships
./scripts/github-projects/manage-issue-relationships.sh view 150
```

### Decision Tree

```
Does this issue have sub-tasks?
├─ YES → Use parent-child relationships
│   │
│   └─ Do sub-tasks have technical dependencies?
│       ├─ YES → Also use blocking relationships
│       └─ NO → Only parent-child
│
└─ NO → Is this issue blocked by another issue?
    ├─ YES → Use blocking relationship
    └─ NO → No relationships needed
```

---

## Agent Implementation Workflow

**End-to-end workflow using `/gh:implement-issue` with GitHub Projects integration.**

### Prerequisites

- Issue created via web UI or `scripts/github-projects/create-issue.sh`
- Issue added to Project #3 (auto-workflow)
- Issue has required metadata:
  - `Required Documentation` field filled in
  - `Acceptance Criteria` defined
  - Dependencies resolved (if any)
  - Priority and complexity labels set

### Step-by-Step Flow

#### 1. Issue Creation

```bash
# Option A: Web UI (recommended)
# Navigate to: https://github.com/jvlivonius/vsc-extension-scanner/issues/new/choose
# Select "Feature" template → Fill in all fields → Create issue

# Option B: CLI with helper script
./scripts/github-projects/create-issue.sh \
  --type feature \
  --title "Add CSV export" \
  --body "Export scan results as CSV format" \
  --milestone v3.8.0 \
  --priority High \
  --complexity M
```

**Result:**

- Issue #160 created
- Auto-added to Project #3 with Status = "Backlog"
- Priority = "High", Complexity = "M" (auto-synced)

#### 2. Issue Preparation (Project Board)

```bash
# Check project board
gh project item-list 3 --format json | jq '.items[] | select(.content.number==160)'

# Verify dependencies are closed
./scripts/github-projects/manage-issue-relationships.sh view 160

# Move to "Todo" status (ready to implement)
# Via web UI: Drag issue from Backlog → Todo column
```

#### 3. Agent Implementation

```bash
# Trigger agent implementation
/gh:implement-issue 160
```

**Agent workflow:**

1. **Fetch issue details:**

   ```bash
   gh issue view 160 --json title,body,labels,milestone
   ```

2. **Validate dependencies:**

   - Parse "Blocked By:" from issue body
   - Check all blocker issues are closed
   - Exit if blockers are still open

3. **Read required documentation:**
   - Parse "Required Documentation: ARCHITECTURE.md, SECURITY.md" from issue body
   - Read each document before implementation
   - Understand context and constraints

4. **Create feature branch:**
   ```bash
   git checkout main
   git pull
   git checkout -b feature/add-csv-export
   ```

5. **Implement changes:**
   - Write code following acceptance criteria
   - Follow ARCHITECTURE.md layer rules
   - Apply SECURITY.md validation patterns
   - Write tests (pytest + hypothesis)

6. **Run quality gates:**
   ```bash
   python3 -m pytest tests/                    # All tests pass
   python3 tests/test_security.py              # 0 vulnerabilities
   python3 tests/test_architecture.py          # 0 violations
   ```

7. **Create PR:**
   ```bash
   git add . && git commit -m "feat(export): add CSV export functionality"
   git push origin feature/add-csv-export

   gh pr create \
     --title "feat(export): Add CSV export functionality" \
     --body "$(cat <<'EOF'
   ## Summary
   Implements CSV export for scan results.

   ## Changes
   - Added CSVFormatter class
   - Added --output-csv CLI flag
   - Added comprehensive tests

   ## Testing
   - Unit tests: test_csv_formatter.py
   - Integration tests: test_cli_csv_export.py
   - Property tests: hypothesis strategies

   Closes #160
   EOF
   )" \
     --milestone v3.8.0
   ```

8. **Update issue:**
   ```bash
   gh issue edit 160 --add-label "agent-implemented"
   ```

**Result:**
- PR #165 created with `Closes #160`
- Issue #160 Status auto-updated to "In Review" (via GitHub automation)
- PR linked to milestone v3.8.0
- Project board shows issue in "In Review" column

#### 4. Review & Merge
```bash
# Review PR
gh pr view 165

# Check CI status
gh pr checks 165

# Review code changes
gh pr diff 165

# Approve and merge
gh pr review 165 --approve
gh pr merge 165 --squash
```

**Result:**
- PR #165 merged
- Issue #160 automatically closed (via `Closes #160`)
- Issue #160 Status auto-updated to "Done"
- Branch `feature/add-csv-export` can be deleted

#### 5. Update Parent Issue (if applicable)
```bash
# If #160 was a child task, check parent
./scripts/github-projects/manage-issue-relationships.sh view 160

# Example output shows parent #158
# Check parent issue and its children status
gh issue view 158 --json number,title,state

# Verify all child tasks are closed before closing parent
# (GitHub doesn't support "parent:" search syntax - use relationship script or manual check)
./scripts/github-projects/manage-issue-relationships.sh view 158

# If all children complete, close parent
gh issue close 158 --comment "All sub-tasks completed"
```

### Advanced: Batch Implementation
```bash
# Get all ready issues for milestone
# Note: Filter by priority/complexity labels or custom status labels if used
gh issue list \
  --milestone v3.8.0 \
  --label "P1-high" \
  --state open \
  --json number,title \
  --jq '.[] | .number'

# Output: 160, 161, 162

# Implement sequentially
/gh:implement-issue 160  # Wait for completion
/gh:implement-issue 161  # Wait for completion
/gh:implement-issue 162  # Wait for completion
```

### Monitoring Progress
```bash
# Check milestone progress
gh issue list --milestone v3.8.0 --state all --json state | \
  jq 'group_by(.state) | map({state: .[0].state, count: length})'

# Example output:
# [
#   {"state": "CLOSED", "count": 8},
#   {"state": "OPEN", "count": 4}
# ]
# Progress: 67% (8/12 issues complete)

# Check project board status
gh project item-list 3 --owner @me --format json | \
  jq '.items[] | select(.content.milestone=="v3.8.0") | {number: .content.number, status: .status}'
```

### Error Recovery

**Dependency check fails:**
```
Error: Issue #160 is blocked by open issues: #158, #159
Action: Complete blocker issues first, then retry
```

**Quality gate fails:**
```
Error: Architecture violations detected
Action: Fix violations, commit changes, re-run /gh:implement-issue
```

**PR creation fails:**
```
Error: Branch already exists
Action: Delete old branch: git push origin --delete feature/add-csv-export
```

---

## Bulk Operations

**Efficiently manage multiple issues using helper scripts and parallel operations.**

### Batch Issue Creation

#### Create Multiple Related Issues
```bash
# Create parent feature
PARENT=$(./scripts/github-projects/create-issue.sh \
  --type feature \
  --title "Add CSV export functionality" \
  --milestone v3.8.0 \
  --priority High \
  --complexity L | grep -oP '#\K[0-9]+')

echo "Created parent issue: #$PARENT"

# Create child tasks
CHILD1=$(./scripts/github-projects/create-issue.sh \
  --type task \
  --title "Implement CSV formatter class" \
  --milestone v3.8.0 \
  --priority High \
  --complexity M | grep -oP '#\K[0-9]+')

CHILD2=$(./scripts/github-projects/create-issue.sh \
  --type task \
  --title "Add export command to CLI" \
  --milestone v3.8.0 \
  --priority High \
  --complexity S | grep -oP '#\K[0-9]+')

CHILD3=$(./scripts/github-projects/create-issue.sh \
  --type task \
  --title "Add CSV export tests" \
  --milestone v3.8.0 \
  --priority High \
  --complexity S | grep -oP '#\K[0-9]+')

# Set parent-child relationships
./scripts/github-projects/manage-issue-relationships.sh set-parent $PARENT $CHILD1 $CHILD2 $CHILD3

echo "Created feature with 3 tasks: #$PARENT (parent of #$CHILD1, #$CHILD2, #$CHILD3)"
```

### Batch Relationship Management

#### Set Multiple Parent-Child Relationships
```bash
# Pattern: Parent has many children
./scripts/github-projects/manage-issue-relationships.sh set-parent 150 151 152 153 154 155

# Output:
# Setting parent #150 for 5 issues...
# ✓ Set #150 as parent of #151
# ✓ Set #150 as parent of #152
# ✓ Set #150 as parent of #153
# ✓ Set #150 as parent of #154
# ✓ Set #150 as parent of #155
# Summary: 5 relationships created
```

#### Set Multiple Blocking Relationships
```bash
# Pattern: Sequential pipeline (A → B → C → D)
./scripts/github-projects/manage-issue-relationships.sh set-blocker 152 151  # 151 blocks 152
./scripts/github-projects/manage-issue-relationships.sh set-blocker 153 152  # 152 blocks 153
./scripts/github-projects/manage-issue-relationships.sh set-blocker 154 153  # 153 blocks 154

# Pattern: Multiple blockers (A, B both block C)
./scripts/github-projects/manage-issue-relationships.sh set-blocker 160 158 159
# 158 and 159 both block 160
```

### Batch Label Updates

#### Update Priority for Multiple Issues
```bash
# Get all P2 issues in milestone
ISSUES=$(gh issue list \
  --milestone v3.8.0 \
  --label "P2-medium" \
  --json number \
  --jq '.[].number')

# Upgrade to P1
for issue in $ISSUES; do
  gh issue edit $issue --remove-label "P2-medium" --add-label "P1-high"
  echo "✓ Upgraded #$issue to P1-high"
done
```

#### Add Label to All Issues in Milestone
```bash
# Add "needs-review" label to all open issues
gh issue list \
  --milestone v3.8.0 \
  --state open \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "needs-review"
```

### Batch Field Sync

#### Sync All Milestone Issues to Project Board
```bash
# Use existing sync script
./scripts/github-projects/sync-existing-issues.sh

# Or sync specific milestone only (when script supports --milestone flag)
# ./scripts/github-projects/sync-existing-issues.sh --milestone v3.8.0
```

#### Update Status for Multiple Issues
```bash
# Note: Status is managed via GitHub Projects custom field (Backlog, Todo, In Progress, etc.)
# This example shows using custom labels if your workflow uses them
# Replace with your actual label scheme

gh issue list \
  --milestone v3.8.0 \
  --label "needs-implementation" \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue edit {} \
    --remove-label "needs-implementation" \
    --add-label "in-development"
```

### Batch Querying

#### List All Issues with Dependencies
```bash
# Find issues with blockers using relationship script
for issue in $(gh issue list --milestone v3.8.0 --json number --jq '.[].number'); do
  echo "Checking issue #$issue for blockers..."
  ./scripts/github-projects/manage-issue-relationships.sh view $issue
done
```

#### Find Issues Ready for Implementation
```bash
# Issues with:
# - Status = Todo or Backlog
# - Priority = High or Critical
# - No open blockers
# - All required fields filled

gh issue list \
  --milestone v3.8.0 \
  --state open \
  --json number,title,labels \
  --jq '.[] | select(
    (.labels[].name | contains("P0-critical") or contains("P1-high")) and
    (.labels[].name | contains("status:todo") or contains("status:backlog"))
  ) | "#\(.number): \(.title)"'
```

### Batch Closure

#### Close All Completed Issues
```bash
# Close issues with merged PRs
gh issue list \
  --milestone v3.8.0 \
  --label "agent-implemented" \
  --state open \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue close {} --comment "Implemented and merged"
```

#### Close Milestone and All Issues
```bash
# Get milestone number
MILESTONE_NUM=$(gh api repos/:owner/:repo/milestones --jq '.[] | select(.title=="v3.8.0") | .number')

# Close all open issues in milestone
gh issue list \
  --milestone v3.8.0 \
  --state open \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue close {} --comment "Released in v3.8.0"

# Close milestone
gh api repos/:owner/:repo/milestones/$MILESTONE_NUM \
  -X PATCH \
  -f state="closed"
```

### Performance Optimization

#### Parallel Operations (with rate limiting)
```bash
# Process up to 5 issues concurrently
gh issue list --milestone v3.8.0 --json number --jq '.[].number' | \
  xargs -P 5 -I {} bash -c '
    gh issue edit {} --add-label "needs-triage"
    sleep 0.5  # Rate limit protection
  '
```

#### GraphQL Batching (future enhancement)
```bash
# Fetch multiple issues in single query (reduces API calls)
gh api graphql -f query='
  query {
    repo: repository(owner: "jvlivonius", name: "vsc-extension-scanner") {
      issue1: issue(number: 150) { title state }
      issue2: issue(number: 151) { title state }
      issue3: issue(number: 152) { title state }
    }
  }
'
```

### Bulk Operation Best Practices

1. **Always dry-run first:** Test logic on 1-2 issues before bulk execution
2. **Rate limit protection:** Add `sleep 0.5` between API calls in loops
3. **Error handling:** Check exit codes, handle partial failures gracefully
4. **Verification:** Validate results after bulk operations
5. **Logging:** Record operations for audit trail
6. **Parallelization:** Use `xargs -P N` for independent operations (limit N=5)
7. **Reversibility:** Plan rollback strategy before execution

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
