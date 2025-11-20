# GitHub Projects Filters and Bulk Operations

**Purpose**: Advanced filtering patterns and batch operation recipes for GitHub Projects V2

**Audience**: Power users, automation workflows, bulk issue management

---

## Quick Reference: Common Filters

**Important**: Multi-word values must be quoted in filter syntax.

| Filter | Usage | Example |
|--------|-------|---------|
| `status:VALUE` | Filter by Status field | `status:Backlog` or `status:"In Progress"` |
| `priority:VALUE` | Filter by Priority field | `priority:Critical,High` |
| `milestone:VALUE` | Filter by milestone | `milestone:"v3.8.0"` |
| `assignee:@me` | Your assigned items | `assignee:@me status:"In Progress"` |
| `label:VALUE` | Filter by repository label | `label:bug label:P1-high` |
| `no:assignee` | Unassigned items | `no:assignee priority:High` |
| `is:open` | Open issues only | `is:open milestone:"v3.8.0"` |
| `-status:VALUE` | Exclude status | `-status:Done` |

---

## Filter Patterns

### Daily Workflow Filters

#### Your Active Work
```
assignee:@me status:"In Progress"
```
Shows: Items you're currently working on

#### Ready to Start
```
status:Backlog,Todo priority:Critical,High -assignee:@me
```
Shows: High-priority unassigned backlog items

#### Blocked Items Needing Attention
```
status:Blocked assignee:@me
```
Shows: Your items that are blocked by dependencies

#### Needs Review
```
status:"In Review" assignee:@me
```
Shows: Your PRs awaiting review

### Planning & Prioritization Filters

#### Critical Issues Requiring Immediate Action
```
priority:Critical -status:Done
```
Shows: All open critical priority items

#### Current Milestone Progress
```
milestone:"v3.8.0" -status:Done
```
Shows: Open items for specific release

#### High-Priority Backlog
```
status:Backlog priority:Critical,High
```
Shows: Important items not yet started

#### Unestimated Work
```
-complexity:* -status:Done
```
Shows: Issues without complexity estimates

### Quality & Process Filters

#### Agent-Ready Issues
```
label:agent-ready status:Todo
```
Shows: Issues validated and ready for `/gh:implement-issue`

#### Missing Required Fields
```
-priority:* -status:Done
```
Shows: Issues without priority labels (needs triage)

#### Implemented But Not Merged
```
label:agent-implemented -status:Done
```
Shows: PRs awaiting review/merge

#### Issues With Dependencies
```
label:blocked-by
```
Shows: Issues with blocking dependencies (custom label)

### Team Collaboration Filters

#### Unassigned High-Priority Work
```
no:assignee priority:High,Critical -status:Done
```
Shows: Critical work needing assignment

#### Team Member's Full Workload
```
assignee:username -status:Done
```
Shows: All open items assigned to specific user

#### Recently Updated
```
is:open sort:updated-desc
```
Shows: Most recently modified open issues

---

## Advanced Filter Combinations

### Sprint Planning View
```
milestone:"v3.8.0" priority:Critical,High -status:Done -assignee:@me
```
Result: High-priority release work available for assignment

### Blockers Report
```
status:Blocked -status:Done
```
Result: All blocked items across project

### Quality Gate View
```
status:"In Review" -label:tests-passing
```
Result: PRs in review without passing tests (if using custom labels)

### Technical Debt Backlog
```
label:tech-debt status:Backlog priority:Medium,Low
```
Result: Non-urgent refactoring work

---

## Bulk Operations

### Batch Issue Creation

#### Create Feature with Multiple Tasks

```bash
#!/usr/bin/env bash
# Create parent feature
PARENT=$(./scripts/github-projects/create-issue.sh \
  --type feature \
  --title "Add CSV export functionality" \
  --milestone v3.8.0 \
  --priority High \
  --complexity L | grep -oP '#\K[0-9]+')

echo "Created parent: #$PARENT"

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
./scripts/github-projects/manage-issue-relationships.sh \
  set-parent $PARENT $CHILD1 $CHILD2 $CHILD3

echo "Feature #$PARENT created with 3 tasks: #$CHILD1, #$CHILD2, #$CHILD3"
```

### Batch Relationship Management

#### Set Multiple Parent-Child Relationships

```bash
# Single parent with many children
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

#### Set Sequential Blocking Chain

```bash
# Sequential pipeline: 151 → 152 → 153 → 154
./scripts/github-projects/manage-issue-relationships.sh set-blocker 152 151
./scripts/github-projects/manage-issue-relationships.sh set-blocker 153 152
./scripts/github-projects/manage-issue-relationships.sh set-blocker 154 153

# Creates: 151 blocks 152 blocks 153 blocks 154
```

#### Set Multiple Blockers for One Issue

```bash
# Both 158 and 159 must complete before 160 can start
./scripts/github-projects/manage-issue-relationships.sh set-blocker 160 158 159
```

### Batch Label Updates

#### Upgrade Priority for Multiple Issues

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
  sleep 0.5  # Rate limiting
done
```

#### Add Label to All Milestone Issues

```bash
# Add "needs-review" label to all open issues
gh issue list \
  --milestone v3.8.0 \
  --state open \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "needs-review"
```

#### Remove Obsolete Labels

```bash
# Remove "blocked" label from all issues
gh issue list \
  --label "blocked" \
  --state open \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue edit {} --remove-label "blocked"
```

### Batch Field Sync

#### Sync All Issues to Project Board

```bash
# Sync all repository issues to project board
./scripts/github-projects/sync-existing-issues.sh

# (Future enhancement: milestone-specific sync)
# ./scripts/github-projects/sync-existing-issues.sh --milestone v3.8.0
```

#### Update Complexity for All Features

```bash
# Find all features without complexity estimate
gh issue list \
  --label "feature" \
  --json number,title | \
  jq -r '.[] | "#\(.number): \(.title)"'

# Manually review and update each
gh issue edit 142 --add-label "complexity/L"
gh issue edit 143 --add-label "complexity/M"
```

### Batch Querying

#### List All Issues with Blocking Dependencies

```bash
# Check every milestone issue for blockers
for issue in $(gh issue list --milestone v3.8.0 --json number --jq '.[].number'); do
  BLOCKERS=$(gh api repos/:owner/:repo/issues/$issue/dependencies/blocked_by --jq '.[].number' 2>/dev/null)

  if [[ -n "$BLOCKERS" ]]; then
    echo "Issue #$issue blocked by: $BLOCKERS"
  fi
done
```

#### Find Issues Ready for Implementation

```bash
# Issues with high priority, no blockers, all fields filled
gh issue list \
  --milestone v3.8.0 \
  --state open \
  --json number,title,labels \
  --jq '.[] | select(
    (.labels[].name | contains("P0-critical") or contains("P1-high")) and
    (.labels[].name | test("complexity/"))
  ) | "#\(.number): \(.title)"'
```

#### Generate Milestone Progress Report

```bash
# Count issues by status
TOTAL=$(gh issue list --milestone v3.8.0 --json number --jq '. | length')
CLOSED=$(gh issue list --milestone v3.8.0 --state closed --json number --jq '. | length')
OPEN=$(gh issue list --milestone v3.8.0 --state open --json number --jq '. | length')

echo "Milestone v3.8.0 Progress:"
echo "  Total: $TOTAL"
echo "  Closed: $CLOSED"
echo "  Open: $OPEN"
echo "  Completion: $(($CLOSED * 100 / $TOTAL))%"
```

### Batch Closure

#### Close All Implemented Issues

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
MILESTONE_NUM=$(gh api repos/:owner/:repo/milestones \
  --jq '.[] | select(.title=="v3.8.0") | .number')

# Close all open issues
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

#### Parallel Label Updates (with Rate Limiting)

```bash
# Process up to 3 issues concurrently (stay within rate limits)
gh issue list --milestone v3.8.0 --json number --jq '.[].number' | \
  xargs -P 3 -I {} bash -c 'gh issue edit {} --add-label "reviewed" && sleep 0.5'
```

**Warning**: Parallel operations can consume API rate limit quickly. Use conservatively.

#### Batch with Rate Limit Checking

```bash
#!/usr/bin/env bash
source scripts/github-projects/rate_limit.sh

rate_limit_guard || exit 1

ISSUES=$(gh issue list --milestone v3.8.0 --json number --jq '.[].number')

for issue in $ISSUES; do
  gh issue edit $issue --add-label "processed"
  rate_limit_delay  # Built-in 0.5s delay
done

rate_limit_summary
```

---

## Export & Reporting

### Export Issues to CSV

```bash
# Export milestone issues with key fields
gh issue list \
  --milestone v3.8.0 \
  --state all \
  --limit 1000 \
  --json number,title,state,labels,assignees \
  --jq -r '
    ["Number","Title","State","Priority","Complexity","Assignee"],
    (.[] | [
      .number,
      .title,
      .state,
      (.labels[] | select(.name | startswith("P")) | .name),
      (.labels[] | select(.name | startswith("complexity/")) | .name),
      (.assignees[0].login // "unassigned")
    ]) | @csv
  ' > milestone-v3.8.0.csv
```

### Generate Markdown Report

```bash
# Create formatted milestone report
cat > milestone-report.md <<'EOF'
# Milestone v3.8.0 Report

## Summary
EOF

gh issue list --milestone v3.8.0 --json number,title,state --jq -r '
  "Total Issues: \(. | length)",
  "Open: \([.[] | select(.state=="OPEN")] | length)",
  "Closed: \([.[] | select(.state=="CLOSED")] | length)",
  "",
  "## Open Issues",
  (.[] | select(.state=="OPEN") | "- #\(.number): \(.title)"),
  "",
  "## Closed Issues",
  (.[] | select(.state=="CLOSED") | "- #\(.number): \(.title)")
' >> milestone-report.md
```

---

## Safety Guidelines

### Before Bulk Operations

1. **Test with small sample first**
   ```bash
   # Test with 3 issues before full batch
   gh issue list --milestone v3.8.0 --json number --jq '.[0:3] | .[].number'
   ```

2. **Check rate limit**
   ```bash
   gh api rate_limit --jq '.rate | "Remaining: \(.remaining)/\(.limit)"'
   ```

3. **Dry-run when possible**
   ```bash
   # Preview changes without executing
   for issue in $ISSUES; do
     echo "Would update: #$issue"
   done
   ```

### During Bulk Operations

1. **Add delays between API calls**
   ```bash
   for issue in $ISSUES; do
     gh issue edit $issue ...
     sleep 0.5  # 500ms delay
   done
   ```

2. **Monitor rate limit**
   ```bash
   # Check every 10 operations
   if (( count % 10 == 0 )); then
     check_rate_limit
   fi
   ```

3. **Log operations**
   ```bash
   for issue in $ISSUES; do
     gh issue edit $issue --add-label "processed" 2>&1 | tee -a bulk-update.log
   done
   ```

### After Bulk Operations

1. **Verify changes**
   ```bash
   gh issue list --milestone v3.8.0 --label "processed" | wc -l
   ```

2. **Check for errors**
   ```bash
   grep -i error bulk-update.log
   ```

3. **Show rate limit usage**
   ```bash
   rate_limit_summary
   ```

---

## Common Pitfalls

### ❌ Forgetting Multi-Word Quotes

```bash
# WRONG - breaks on spaces
status:In Progress

# CORRECT
status:"In Progress"
```

### ❌ No Rate Limiting in Loops

```bash
# WRONG - hits rate limit
for issue in $ISSUES; do
  gh issue edit $issue --add-label "tag"
done

# CORRECT
for issue in $ISSUES; do
  gh issue edit $issue --add-label "tag"
  sleep 0.5  # Rate limiting
done
```

### ❌ Parallel Processing Without Limits

```bash
# WRONG - exhausts API quota
xargs -P 20 -I {} gh api ...

# CORRECT - limit to 3-5 concurrent
xargs -P 3 -I {} gh api ...
```

### ❌ Missing Error Handling

```bash
# WRONG - continues on errors
gh issue close $issue

# CORRECT - check exit code
if ! gh issue close $issue; then
  echo "Failed to close #$issue" >&2
fi
```

---

## References

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub Projects V2 Filters](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/filtering-projects)
- [Rate Limiting Best Practices](GITHUB_API_RATE_LIMITS.md)
- [Bulk Operation Scripts](../../scripts/github-projects/)
- [GitHub Relationships Guide](../contributing/GITHUB_RELATIONSHIPS.md)

---

**Last Updated**: 2025-11-20
**Status**: Active
**Maintainer**: Add new filter patterns and bulk operation recipes as workflows evolve
