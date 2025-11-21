# Feature Implementation Guide

**Purpose**: Complete reference for implementing features (epics) with sub-tasks using orchestrated workflow

**Audience**: Developers implementing multi-task features, maintainers managing complex work

**Last Updated**: 2025-11-21

---

## Table of Contents

1. [Overview](#overview)
2. [When to Use Feature Implementation](#when-to-use-feature-implementation)
3. [Complete Workflow](#complete-workflow)
4. [Error Recovery](#error-recovery)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Examples](#examples)

---

## Overview

### What is Feature Implementation?

**Feature Implementation** is an orchestrated workflow for implementing GitHub issues that have sub-tasks (parent-child relationships). Instead of implementing each sub-task separately, the system:

1. **Detects** the feature automatically (via parent-child API)
2. **Validates** all sub-tasks upfront (fail fast)
3. **Builds** dependency graph (topological sort)
4. **Implements** sub-tasks in dependency order
5. **Recovers** intelligently from failures
6. **Creates** single PR closing all completed sub-tasks

### Key Benefits

- **Atomic PRs**: One PR per feature (not per sub-task)
- **Dependency Respect**: Implements in correct order automatically
- **Intelligent Recovery**: Continues with independent tasks when one fails
- **Clean History**: One commit per sub-task, clear feature lineage
- **Integration Testing**: Feature-level tests before closure

### Single Task vs Feature

| Aspect | Single Task | Feature (with sub-tasks) |
|--------|-------------|--------------------------|
| Detection | No sub-issues | Has sub-issues (parent-child) |
| Validation | Single issue | All sub-tasks upfront |
| Branch | feature/task-name | feature/feature-name |
| Commits | 1 commit | N commits (one per sub-task) |
| PR | Closes 1 issue | Closes N issues |
| Recovery | N/A | Skips failed, continues independent |
| Integration Tests | Task-level | Feature-level |

---

## When to Use Feature Implementation

### Use Feature Implementation When:

✅ **Issue has 3+ sub-tasks** that should be implemented together
✅ **Sub-tasks have dependencies** (A must complete before B)
✅ **Feature needs integration testing** after all parts complete
✅ **Atomic merge desired** (all changes together or nothing)
✅ **Clear parent-child hierarchy** exists

### Use Single Task Implementation When:

❌ Issue has no sub-tasks (standalone work)
❌ Sub-tasks are completely independent (separate PRs preferred)
❌ Sub-tasks span multiple milestones or releases
❌ Different developers own different sub-tasks
❌ Incremental delivery required (deploy parts separately)

### Examples

**Feature Implementation** (Epic #1004):
```
[Epic] GitHub Workflow Automation Improvements
├─ #1005: Fix validation script bug
├─ #1006: Implement status transitions
├─ #1007: Implement dependency blocking
├─ #1008: Implement feature completion
└─ #1009: Document automation workflows

Dependencies: 1005→1006, 1006→1007, 1006→1008, 1007→1009, 1008→1009

Use: Feature implementation (related tasks, dependencies, integration needed)
```

**Single Task Implementation** (#142):
```
[Task] Add CSV export functionality

No sub-tasks, standalone feature

Use: Single task implementation
```

---

## Complete Workflow

### Step -1: Automatic Detection

Command automatically detects feature vs single task by querying parent-child relationships via `manage-issue-relationships.sh view`. If sub-issues exist, the feature workflow activates; otherwise, the standard single-task workflow runs.

**See**: [/gh:implement-issue Step -1](../../.claude/commands/gh/implement-issue.md#step--1-issue-type-detection-feature-vs-single-task) for complete detection logic.

### Phase 1: Discovery and Validation

#### 1.1 Fetch All Sub-Tasks

```bash
# Query parent-child relationships (CORRECT method)
# DEPENDENCY: Requires manage-issue-relationships.sh output format with "Sub-Issues" section
# If script output format changes, update grep pattern below
SUB_TASKS=$(./scripts/github-projects/manage-issue-relationships.sh view 1004 |
            grep -A 100 "Sub-Issues" |
            grep -oE "#[0-9]+" |
            grep -oE "[0-9]+")

echo "Found sub-tasks: $SUB_TASKS"
# Output: 1005 1006 1007 1008 1009
```

**IMPORTANT**: Always use `manage-issue-relationships.sh view` to get sub-tasks. Never:
- ❌ Search for "#1004" in issue bodies
- ❌ Assume sequential numbering (1005-1009 after 1004)
- ❌ Grep issue lists for keywords

#### 1.2 Validate All Sub-Tasks Upfront

```bash
echo "Validating all sub-tasks before implementation..."

for task in $SUB_TASKS; do
    echo "Validating #$task..."

    if ! ./scripts/github-projects/validate-agent-ready.sh "$task"; then
        echo "❌ Error: Sub-task #$task failed validation"
        echo ""
        echo "Fix validation issues:"
        echo "  - Ensure issue structure complete"
        echo "  - Check all dependencies closed"
        echo "  - Verify required docs linked"
        echo "  - Confirm labels set correctly"
        exit 1
    fi

    echo "✅ Sub-task #$task validated"
done

echo ""
echo "✅ All sub-tasks validated successfully"
```

**Validation Checks** (per sub-task):
- Issue structure (title, body, required docs, acceptance criteria)
- All blocking dependencies closed
- Required documentation files exist
- Labels set (priority, complexity, type)

**If ANY sub-task fails validation → STOP immediately**

### Phase 2: Dependency Analysis

#### 2.1 Build Dependency Graph

```bash
# Build graph and perform topological sort
echo "Building dependency graph..."

SORTED_TASKS=$(./scripts/github-projects/build-task-dependency-graph.sh $SUB_TASKS)

if [[ $? -ne 0 ]]; then
    echo "❌ Error: Cycle detected in dependencies"
    echo ""
    echo "Action required:"
    echo "  1. Review blocking relationships"
    echo "  2. Identify incorrect blocker"
    echo "  3. Remove blocker:"
    echo "     ./scripts/github-projects/manage-issue-relationships.sh remove-blocker <blocker> <blocked>"
    echo "  4. Re-run feature implementation"
    exit 1
fi

echo "Implementation order: $SORTED_TASKS"
```

**Algorithm**: Kahn's topological sort
1. Query `blocked_by` for each sub-task
2. Build adjacency list: task → [tasks it blocks]
3. Calculate in-degree (dependency count) per task
4. Process tasks with in-degree 0 (no dependencies)
5. Remove edges, add newly freed tasks to queue
6. Detect cycles (if not all tasks processed)

#### 2.2 Review Feature Scope

```bash
echo ""
echo "=== Feature Scope Review ==="
gh issue view 1004 --json title,body | jq -r '.title,.body'

echo ""
echo "=== Sub-Tasks Coverage ==="
for task in $SORTED_TASKS; do
    gh issue view "$task" --json title | jq -r '"  - #\(.number): \(.title)"'
done
```

### Phase 3: Branch Creation

```bash
# Generate branch name from feature title
FEATURE_TITLE=$(gh issue view 1004 --json title | jq -r '.title')
BRANCH_NAME="feature/$(echo "$FEATURE_TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/\[.*\] //' | tr ' ' '-')"

echo "Creating feature branch: $BRANCH_NAME"

# Create branch from updated main
git checkout main && git pull
git checkout -b "$BRANCH_NAME"

echo "✅ Created feature branch: $BRANCH_NAME"
```

### Phase 4: Sequential Implementation

#### 4.1 Initialize Tracking

```bash
declare -a completed_tasks=()
declare -a failed_tasks=()
declare -a skipped_tasks=()
```

#### 4.2 Implementation Loop

```bash
for task in $SORTED_TASKS; do
    echo ""
    echo "=========================================="
    echo "Implementing sub-task #$task..."
    echo "=========================================="

    # Check if blocked by failed task
    if is_blocked_by_failed_tasks "$task" "${failed_tasks[@]}"; then
        echo "⚠️  Skipping #$task (blocked by failed task)"
        skipped_tasks+=("$task")
        continue
    fi

    # Implement single task (standard Steps 0-5)
    echo "Step 0: Validating #$task..."
    echo "Step 1: Fetching and parsing issue..."
    echo "Step 2: Validating dependencies..."
    echo "Step 3: Reading required documentation..."
    echo "Step 4: Creating branch (already on feature branch)..."
    echo "Step 5: Implementing changes..."

    if implement_single_task_logic "$task"; then
        # Commit changes
        git add .
        git commit -m "$(generate_task_commit_message "$task")"

        completed_tasks+=("$task")
        echo "✅ Sub-task #$task completed and committed"
    else
        echo "❌ Sub-task #$task failed"
        failed_tasks+=("$task")

        # Mark as needs human help
        echo "Marking #$task as needs-human-help"
        gh issue edit "$task" --add-label "needs-human-help"

        # Continue with independent tasks (user requirement)
        echo "Continuing with independent tasks..."
    fi
done
```

#### 4.3 Helper: Check if Blocked by Failed Task

```bash
is_blocked_by_failed_tasks() {
    local task="$1"
    shift
    local failed_tasks=("$@")

    if [[ ${#failed_tasks[@]} -eq 0 ]]; then
        return 1  # No failed tasks, not blocked
    fi

    # Query task's blocking dependencies
    local blockers=$(gh api repos/:owner/:repo/issues/$task/dependencies/blocked_by --jq '.[].number' 2>/dev/null)

    # Check if any blocker is in failed_tasks
    for blocker in $blockers; do
        for failed in "${failed_tasks[@]}"; do
            if [[ "$blocker" == "$failed" ]]; then
                echo "  #$task blocked by failed task #$blocker"
                return 0  # Task is blocked
            fi
        done
    done

    return 1  # Task is not blocked
}
```

#### 4.4 Helper: Generate Task Commit Message

```bash
generate_task_commit_message() {
    local task="$1"
    local task_title=$(gh issue view "$task" --json title | jq -r '.title')

    # Extract type from labels
    local labels=$(gh issue view "$task" --json labels | jq -r '.labels[].name')
    local type="feat"

    if echo "$labels" | grep -q "bugfix"; then
        type="fix"
    elif echo "$labels" | grep -q "hotfix"; then
        type="hotfix"
    fi

    # Generate commit message
    echo "${type}(task): $(echo "$task_title" | sed 's/\[.*\] //') (#$task)

Implements sub-task #$task as part of feature implementation.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
}
```

### Phase 5: PR Creation

```bash
# Check if any tasks completed
if [[ ${#completed_tasks[@]} -eq 0 ]]; then
    echo "❌ No tasks completed successfully"
    echo "Cannot create PR with zero changes"
    exit 1
fi

# Generate PR body
CLOSES_LIST=$(printf ", #%s" "${completed_tasks[@]}")
CLOSES_LIST=${CLOSES_LIST:2}

PR_BODY="Closes $CLOSES_LIST

Part of #1004

## Implemented Sub-Tasks
$(for task in "${completed_tasks[@]}"; do
    gh issue view "$task" --json title | jq -r '"- [x] #'$task': \(.title)"'
done)

$(if [[ ${#failed_tasks[@]} -gt 0 ]]; then
    echo ""
    echo "## Failed Sub-Tasks (Needs Human Help)"
    for task in "${failed_tasks[@]}"; do
        gh issue view "$task" --json title | jq -r '"- [ ] #'$task': \(.title) ⚠️"'
    done
fi)

$(if [[ ${#skipped_tasks[@]} -gt 0 ]]; then
    echo ""
    echo "## Skipped Sub-Tasks (Blocked by Failed)"
    for task in "${skipped_tasks[@]}"; do
        gh issue view "$task" --json title | jq -r '"- [ ] #'$task': \(.title) 🚫"'
    done
fi)

## Integration Tests
- [ ] All sub-task tests pass
- [ ] Feature-level integration tests pass
- [ ] Documentation updated

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Create PR
gh pr create \
  --title "feat(epic): $(echo "$FEATURE_TITLE" | sed 's/\[.*\] //')" \
  --body "$PR_BODY" \
  --milestone "$(gh issue view 1004 --json milestone | jq -r '.milestone.title')"

echo "✅ PR created successfully"
```

### Phase 6: Results Reporting

```bash
echo ""
echo "============================================"
echo "Feature Implementation Complete"
echo "============================================"
echo "Feature: #1004"
echo "Branch: $BRANCH_NAME"
echo ""
echo "Results:"
echo "  ✅ Completed: ${#completed_tasks[@]} tasks (${completed_tasks[*]})"
echo "  ❌ Failed: ${#failed_tasks[@]} tasks (${failed_tasks[*]})"
echo "  ⚠️  Skipped: ${#skipped_tasks[@]} tasks (${skipped_tasks[*]})"
echo ""

if [[ ${#failed_tasks[@]} -gt 0 ]]; then
    echo "⚠️  Action Required:"
    echo "  1. Fix failed tasks manually"
    echo "  2. Remove needs-human-help label after fix"
    echo "  3. Implement skipped tasks in follow-up PR"
    echo ""
fi

echo "Next Steps:"
echo "  1. Review PR and request human review"
echo "  2. After PR merge, run integration tests"
echo "  3. If integration tests pass, close feature #1004"
```

### Phase 7: Integration Testing (Post-Merge)

After PR merges, run feature-level integration tests:

```bash
# CRITICAL: Integration tests MUST run AFTER PR merge to main branch
# Running before merge tests against outdated main branch and produces invalid results
echo "Waiting for PR merge confirmation..."
gh pr view "$PR_NUMBER" --json mergedAt | jq -e '.mergedAt' || {
    echo "❌ Error: PR not yet merged. Integration tests require merged code."
    exit 1
}

echo "✅ PR merged, running feature-level integration tests..."

python3 -m pytest tests/integration/test_feature_1004.py -v

if [[ $? -eq 0 ]]; then
    echo "✅ Integration tests passed"
    echo "Closing feature #1004"
    gh issue close 1004 --comment "Feature implementation complete. All sub-tasks implemented and integration tests passed."
else
    echo "❌ Integration tests failed"
    echo "Reopening feature #1004"
    gh issue reopen 1004
    gh issue comment 1004 --body "⚠️ Integration tests failed after PR merge. Investigation required."
fi
```

---

## Error Recovery

### Scenario 1: One Sub-Task Fails, Others Independent

**Setup**:
```
Feature #1004 with tasks:
  #1005 → #1006 → #1007
  #1008 (independent)
  #1009 (independent)

Dependencies:
  1005 blocks 1006
  1006 blocks 1007
  1008 and 1009 have no dependencies
```

**Execution**:
```
✅ #1005 completed
❌ #1006 failed (tests didn't pass)
⚠️  #1007 skipped (depends on #1006)
✅ #1008 completed (independent)
✅ #1009 completed (independent)
```

**Result**:
- PR created with: #1005, #1008, #1009
- Failed task: #1006 (marked needs-human-help)
- Blocked task: #1007 (skipped until #1006 fixed)

**Recovery Steps**:
1. Human debugs and fixes #1006 manually
2. Remove `needs-human-help` label from #1006
3. Create follow-up PR for #1006 and #1007
4. Original feature PR remains open until all complete

### Scenario 2: Circular Dependency Detected

**Setup**:
```
Tasks: #1005 → #1006 → #1007 → #1005 (cycle!)
```

**Detection**:
```bash
$ ./scripts/github-projects/build-task-dependency-graph.sh 1005 1006 1007

❌ Cycle detected in dependencies
Error: #1005 → #1006 → #1007 → #1005

Tasks not processed (involved in cycle):
  #1005 (has 1 unresolved dependencies)
  #1006 (has 1 unresolved dependencies)
  #1007 (has 1 unresolved dependencies)
```

**Recovery Steps**:
1. Review blocking relationships:
   ```bash
   ./scripts/github-projects/manage-issue-relationships.sh view 1005
   ./scripts/github-projects/manage-issue-relationships.sh view 1006
   ./scripts/github-projects/manage-issue-relationships.sh view 1007
   ```

2. Identify incorrect blocker (e.g., #1007 shouldn't block #1005)

3. Remove incorrect blocker:
   ```bash
   ./scripts/github-projects/manage-issue-relationships.sh remove-blocker 1005 1007
   ```

4. Re-run feature implementation:
   ```bash
   /gh:implement-issue 1004
   ```

### Scenario 3: Validation Failure During Upfront Check

**Setup**:
```
Feature #1004 with tasks:
  #1005 (valid)
  #1006 (missing required documentation)
  #1007 (valid)
  #1008 (valid)
  #1009 (valid)
```

**Execution**:
```bash
Validating all sub-tasks before implementation...
Validating #1005...
✅ Sub-task #1005 validated

Validating #1006...
❌ Error: Sub-task #1006 failed validation
  - Missing required documentation field

Fix validation issues:
  - Ensure issue structure complete
  - Check all dependencies closed
  - Verify required docs linked
  - Confirm labels set correctly
```

**Recovery Steps**:
1. Update #1006 with required documentation:
   ```markdown
   ## Required Documentation
   ARCHITECTURE.md, SECURITY.md, PRD.md
   ```

2. Re-run feature implementation:
   ```bash
   /gh:implement-issue 1004
   ```

---

## Acceptance Criteria Tracking (CRITICAL)

**During implementation, you MUST update acceptance criteria checkboxes as work completes.**

### Why This Matters

- ✅ **Visibility**: Real-time progress tracking on issue page
- ✅ **Automation**: Workflows validate AC completion before status transitions
- ✅ **Prevents Blocking**: Unchecked ACs block "Done" status transition
- ✅ **Audit Trail**: Clear record of implementation progress

### How to Update

After completing each acceptance criterion:

```bash
# Update checkbox in issue body
./scripts/github-projects/update-acceptance-criteria.sh <issue-number> "<criterion-text>"

# Example during implementation:
./scripts/github-projects/update-acceptance-criteria.sh 75 "Module display renders correctly"
./scripts/github-projects/update-acceptance-criteria.sh 75 "Unit tests achieve ≥90% coverage"
./scripts/github-projects/update-acceptance-criteria.sh 75 "Security validation passes"
```

### Common Workflow Pattern

```bash
# 1. Implement feature code
<write code>
./scripts/github-projects/update-acceptance-criteria.sh $ISSUE "Code implements feature as specified"

# 2. Write tests
<write tests>
./scripts/github-projects/update-acceptance-criteria.sh $ISSUE "Tests written with ≥80% coverage"

# 3. Apply security patterns
<apply patterns>
./scripts/github-projects/update-acceptance-criteria.sh $ISSUE "Security validation applied"

# 4. Run quality gates
<run checks>
./scripts/github-projects/update-acceptance-criteria.sh $ISSUE "Pre-commit hooks pass"
./scripts/github-projects/update-acceptance-criteria.sh $ISSUE "Architecture tests pass"
```

### Current Limitations

**What's Automated:**

- ✅ Validation: Workflows check if ACs are complete
- ✅ Blocking: Prevents status transitions if ACs unchecked
- ✅ Comments: Status transition comments explain requirements

**What's Manual:**

- ⚠️ **Checking boxes**: Must use `update-acceptance-criteria.sh` script
- ⚠️ **Status field updates**: Currently comment-only (GraphQL requires additional permissions)

**Why Manual:**

- No automated mapping from code changes to specific criteria
- Requires human judgment to confirm criterion completion
- Ensures quality verification before marking complete

### Troubleshooting

**Issue stuck in "In Review" despite merged PR:**
```bash
# Check which ACs are unchecked
gh issue view $ISSUE_NUMBER

# Update any unchecked criteria
./scripts/github-projects/update-acceptance-criteria.sh $ISSUE_NUMBER "<unchecked criterion>"
```

**Script reports "Criterion not found":**

- Check exact text matches (including special characters)
- Verify criterion exists in issue body
- Text may have been manually edited - update via web UI

**See Also:**

- [/gh:implement-issue Pattern 5](../../.claude/commands/gh/implement-issue.md#pattern-5-acceptance-criteria-tracking-important) - AC tracking workflow
- [GITHUB_WORKFLOWS.md Status Limitations](../../docs/contributing/GITHUB_WORKFLOWS.md#status-transitions-limitations) - Current automation limitations

---

## Best Practices

### 1. Feature Scope Planning

**Before Creating Feature**:
- ✅ Break down into 3-10 sub-tasks (manageable)
- ✅ Define clear acceptance criteria per sub-task
- ✅ Identify blocking dependencies
- ✅ Document required docs for each sub-task

**Example**:
```markdown
[Epic] Add CSV Export Feature

Sub-tasks:
1. Implement CSV formatter class (no deps)
2. Add export command to CLI (depends on #1)
3. Add CSV export tests (depends on #1, #2)
4. Document CSV export (no deps)

Dependencies: minimal (only 3 blocking relationships)
```

### 2. Sub-Task Independence

**Design for Parallelization**:
- ✅ Minimize blocking dependencies
- ✅ Make sub-tasks as independent as possible
- ✅ Use blocking only for true technical dependencies
- ❌ Avoid cascade dependencies (A→B→C→D→E)

**Good Structure**:
```
Feature: Database Refactoring
├─ #1: Design new schema (no deps) ← Can start immediately
├─ #2: Create migration scripts (depends on #1)
├─ #3: Update data access layer (depends on #2)
├─ #4: Add integration tests (depends on #3)
└─ #5: Update documentation (depends on #1) ← Can start after #1

Parallel work possible: #1 can start, then #2+#5 can run in parallel
```

**Bad Structure**:
```
Feature: Database Refactoring
├─ #1: Task 1 → blocks #2
├─ #2: Task 2 → blocks #3
├─ #3: Task 3 → blocks #4
├─ #4: Task 4 → blocks #5
└─ #5: Task 5

All sequential, no parallel work possible
```

### 3. Clear Sub-Task Titles

**Use Descriptive Titles**:
```bash
# ✅ CORRECT
[TASK] Implement CSV formatter class
[TASK] Add export command to CLI
[TASK] Add CSV export tests
[TASK] Document CSV export feature

# ❌ WRONG
Implement CSV stuff
Add export
Do the tests
Update docs
```

### 4. Feature Completion Criteria

**Parent Feature Acceptance Criteria**:
```markdown
## Acceptance Criteria
- [ ] All sub-tasks completed (#1005-#1009)
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] No regression in existing functionality
- [ ] Performance benchmarks within acceptable range
```

### 5. Monitoring Progress

```bash
# View feature progress anytime
./scripts/github-projects/manage-issue-relationships.sh view 1004

# Output shows:
# - Total sub-issues: 5
# - Completed: 2 (✓)
# - In Progress: 1
# - Blocked: 1
# - To Do: 1
```

---

## Troubleshooting

### Issue: Feature Not Detected

**Symptom**: `/gh:implement-issue 1004` treats it as single task

**Cause**: No parent-child relationships set

**Solution**:
```bash
# Verify relationships exist
./scripts/github-projects/manage-issue-relationships.sh view 1004

# If no sub-issues shown, create relationships
./scripts/github-projects/manage-issue-relationships.sh set-parent 1004 1005 1006 1007 1008 1009
```

### Issue: Dependency Graph Fails

**Symptom**: Error during dependency graph building

**Causes & Solutions**:
1. **Circular dependency**: See [Scenario 2](#scenario-2-circular-dependency-detected)
2. **API rate limit**: Wait 1 hour or use personal access token with higher limits
3. **Missing blocker**: Sub-task references blocker that doesn't exist in sub-task set

### Issue: All Sub-Tasks Skip

**Symptom**: First task fails, all others skip

**Cause**: Cascading dependencies (A→B→C→D→E)

**Solution**: Redesign dependencies to allow parallel work

### Issue: PR Body Too Large

**Symptom**: `gh pr create` fails with "body too large" error

**Cause**: Too many sub-tasks or verbose descriptions

**Solution**: Simplify PR body, reference sub-tasks by number only

---

## Examples

### Example 1: Simple Feature (No Dependencies)

```bash
# Feature: Add Export Formats (#200)
# Sub-tasks: #201 (CSV), #202 (JSON), #203 (HTML), #204 (Tests)
# Dependencies: None (all independent)

/gh:implement-issue 200

# Execution:
✅ Detected: FEATURE with 4 sub-tasks
✅ All sub-tasks validated
✅ Implementation order: 201 202 203 204 (any order)
✅ All tasks completed
✅ PR created: Closes #201, #202, #203, #204
```

### Example 2: Feature with Sequential Dependencies

```bash
# Feature: Database Migration (#300)
# Sub-tasks: #301 (schema), #302 (scripts), #303 (DAL), #304 (tests)
# Dependencies: 301→302, 302→303, 303→304

/gh:implement-issue 300

# Execution:
✅ Detected: FEATURE with 4 sub-tasks
✅ All sub-tasks validated
✅ Implementation order: 301 302 303 304 (respecting dependencies)
✅ All tasks completed
✅ PR created: Closes #301, #302, #303, #304
```

### Example 3: Feature with Partial Failure

```bash
# Feature: API Refactoring (#400)
# Sub-tasks: #401, #402, #403, #404, #405
# Dependencies: 401→402, 402→403, 404 and 405 independent

/gh:implement-issue 400

# Execution:
✅ #401 completed
❌ #402 failed (tests didn't pass)
⚠️  #403 skipped (depends on #402)
✅ #404 completed (independent)
✅ #405 completed (independent)

Result:
- PR created: Closes #401, #404, #405
- Needs fixing: #402 (marked needs-human-help)
- Blocked: #403 (will implement after #402 fixed)
```

---

## References

- [GITHUB_RELATIONSHIPS.md](../contributing/GITHUB_RELATIONSHIPS.md) - Parent-child and blocking relationships
- [/gh:implement-issue command](../../.claude/commands/gh/implement-issue.md) - Command reference
- [build-task-dependency-graph.sh](../../scripts/github-projects/build-task-dependency-graph.sh) - Dependency graph builder
- [manage-issue-relationships.sh](../../scripts/github-projects/manage-issue-relationships.sh) - Relationship management

---

**Status**: Active
**Maintainer**: Keep in sync with workflow changes and user feedback
