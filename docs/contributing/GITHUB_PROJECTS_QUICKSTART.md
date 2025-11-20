# GitHub Projects Quickstart

**Get started with GitHub Projects V2 in 5 minutes**

**Project**: [VS Code Extension Scanner Development (Project #3)](https://github.com/users/jvlivonius/projects/3)

---

## 1. Access the Project Board (30 seconds)

**URL**: https://github.com/users/jvlivonius/projects/3

**Views**:
- **Kanban Board** - Daily work (drag cards between columns)
- **Detailed Table** - All fields with sorting/filtering
- **Release Roadmap** - Timeline view by milestone

---

## 2. Create Your First Issue (2 minutes)

### Via Web UI (Recommended)

Navigate to: https://github.com/jvlivonius/vsc-extension-scanner/issues/new/choose

Choose template:
- `feature.yml` - New functionality
- `task.yml` - Implementation task
- `release.yml` - Release tracking

**Auto-sync**: Issue automatically added to Project #3 in "Backlog" status

### Via CLI

```bash
gh issue create \
  --title "[FEATURE] Add CSV export" \
  --body "Export scan results as CSV format" \
  --label "feature,P1-high,complexity/M" \
  --milestone "v3.8.0"

# Result:
# - Issue created
# - Auto-added to project board
# - Labels sync to Priority/Complexity fields (1-5 min delay)
```

---

## 3. Essential Slash Commands (2 minutes)

**Create issues from plan**:
```bash
/gh:issues-create create-from-plan docs/plans/feature.md --milestone v3.8.0
```

**Triage new issues**:
```bash
/gh:triage 160  # AI-assisted label suggestions
```

**Implement issue**:
```bash
/gh:issues-implement 142  # Automated implementation with docs reading
```

**Track milestone progress**:
```bash
/gh:milestone report v3.8.0
```

**Sync project board**:
```bash
/gh:projects-sync milestone v3.8.0
```

---

## 4. Common Workflows (1 minute)

### Move Issues Through Pipeline

1. **Backlog → Todo**: Drag card when ready to work
2. **Todo → In Progress**: Drag when you start implementation
3. **Create PR** with `Closes #142` in description
4. **Auto-moves to In Review** when PR opens
5. **Auto-moves to Done** when PR merges

### Set Relationships

**Parent-child** (feature → tasks):
```bash
./scripts/github-projects/manage-issue-relationships.sh set-parent 142 143 144 145
```

**Blocking** (dependencies):
```bash
./scripts/github-projects/manage-issue-relationships.sh set-blocker 147 146
# 146 blocks 147
```

### Quick Filters

| What You Want | Filter |
|---------------|--------|
| Your active work | `assignee:@me status:"In Progress"` |
| Ready to start | `status:Backlog,Todo priority:High` |
| Needs review | `status:"In Review"` |
| Current milestone | `milestone:"v3.8.0" -status:Done` |
| Blocked items | `status:Blocked` |

**Tip**: Multi-word values need quotes: `status:"In Progress"`

---

## 5. Key Concepts (30 seconds)

### Labels vs Fields

**Repository Labels** (on issue page):
- `P0-critical`, `P1-high`, `P2-medium`, `P3-low`
- `complexity/XS`, `complexity/S`, `complexity/M`, `complexity/L`, `complexity/XL`

**Project Fields** (in project views):
- **Status** - Backlog, Todo, In Progress, In Review, Done, Blocked
- **Priority** - Auto-synced from P0-P3 labels
- **Complexity** - Auto-synced from complexity/* labels

**Auto-Sync**: Labels → Fields sync happens via GitHub Actions within 1-5 minutes

### Relationship Types

| Type | Use Case | Example |
|------|----------|---------|
| **Parent-Child** | Feature breakdown | Feature #142 has tasks #143, #144, #145 |
| **Blocking** | Dependencies | Issue #146 blocks issue #147 |

---

## Next Steps

**Setup**: First-time configuration → [GITHUB_PROJECTS_SETUP.md](GITHUB_PROJECTS_SETUP.md)

**Daily Workflows**: Issue creation, triage, implementation → [GITHUB_WORKFLOWS.md](GITHUB_WORKFLOWS.md)

**Relationships**: Parent-child and blocking patterns → [GITHUB_RELATIONSHIPS.md](GITHUB_RELATIONSHIPS.md)

**Filters & Bulk Ops**: Advanced filtering, batch operations → [GITHUB_FILTERS.md](../guides/GITHUB_FILTERS.md)

**Command Reference**: Shared patterns, rate limits, errors → [_gh-reference.md](../../.claude/commands/gh/_gh-reference.md)

---

## Common Issues

**"Labels not syncing to project fields"**:
- Wait 1-5 minutes for GitHub Actions workflow
- Check: `gh run list --workflow=sync-project-fields.yml`
- Manual sync: `./scripts/github-projects/sync-existing-issues.sh`

**"Parent-child relationship not showing"**:
- Must use GraphQL `addSubIssue` mutation (not REST API)
- Use script: `./scripts/github-projects/manage-issue-relationships.sh`

**"Rate limit exceeded"**:
- Check: `gh api rate_limit`
- Wait for reset or use different token: `gh auth switch`

**"Issue not agent-ready"**:
- Run: `./scripts/github-projects/validate-agent-ready.sh <issue-number>`
- Fix validation errors before `/gh:issues-implement`

---

## Quick Reference Card

| Need | Command |
|------|---------|
| Create issues | `/gh:issues-create create-from-plan <file> --milestone vX.Y.Z` |
| Triage issue | `/gh:triage <number>` |
| Implement issue | `/gh:issues-implement <number>` |
| Set parent-child | `manage-issue-relationships.sh set-parent PARENT CHILD1 CHILD2` |
| Set blocker | `manage-issue-relationships.sh set-blocker BLOCKED BLOCKER` |
| Milestone report | `/gh:milestone report vX.Y.Z` |
| Sync board | `/gh:projects-sync milestone vX.Y.Z` |
| Check rate limit | `gh api rate_limit` |

---

**Last Updated**: 2025-11-20
**Quick Start Time**: ~5 minutes
**Next**: [GITHUB_WORKFLOWS.md](GITHUB_WORKFLOWS.md) for daily development patterns
