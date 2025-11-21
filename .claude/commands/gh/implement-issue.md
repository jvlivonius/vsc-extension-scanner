---
name: issues-implement
description: "Implement GitHub issue with automated doc reading, testing, and PR creation"
category: workflow
complexity: advanced
mcp-servers: [serena, sequential-thinking]
personas: [python-expert, security-engineer, quality-engineer]
---

# /gh:issues-implement - Agent-Driven Issue Implementation

## Triggers
- GitHub issue marked as `agent-ready` and ready for implementation
- Manual trigger for automated issue implementation workflow
- Need for systematic issue resolution with full context

## Usage

```bash
/gh:issues-implement <issue-number> [--branch <name>] [--no-pr] [--dry-run]
```

**Parameters:**
- `<issue-number>`: GitHub issue number to implement (e.g., 142)
- `--branch <name>`: Custom branch name (default: auto-generated from issue)
- `--no-pr`: Implement without creating PR (manual PR creation later)
- `--dry-run`: Validate prerequisites without implementing

## Behavioral Flow

1. **Fetch**: Retrieve issue details, metadata, acceptance criteria
2. **Validate**: Check dependencies resolved, required docs linked, prerequisites met
3. **Prepare**: Read required documentation, create feature branch, analyze scope
4. **Implement**: Code changes following acceptance criteria and project standards
5. **Verify**: Run tests, security scans, create PR with issue linkage

Key behaviors:
- Read all required documentation before implementation
- Validate all dependencies are closed before starting
- Follow acceptance criteria systematically
- Apply security patterns (`validate_path()`, `sanitize_string()`)
- Run full test suite and quality gates
- Create PR with comprehensive description and issue linkage
- Update issue with implementation status label

## Tool Coordination

- **gh CLI**: Issue fetching, PR creation (`gh issue view`, `gh pr create`)
- **Read**: Documentation reading, code analysis
- **Bash**: Git operations, test execution, quality gates
- **Edit/Write**: Code implementation, test creation
- **Serena MCP**: Symbol operations, refactoring, dependency tracking
- **sequential-thinking MCP**: Complex implementation strategy, architecture analysis

## Key Patterns

### Pattern 1: Issue Metadata Extraction

```bash
# Fetch issue details
gh issue view <number> --json title,body,labels,milestone,state

# Extract metadata:
- Title → branch name generation
- Body → parse dependencies, required docs, acceptance criteria
- Labels → determine type (feature, bugfix, hotfix)
- Milestone → link PR to same milestone
```

### Pattern 2: Dependency Validation

```
Dependencies in issue body:
  "Blocked By: #140, #141"

Validation:
  gh issue view 140 --json state  # Must be "closed"
  gh issue view 141 --json state  # Must be "closed"

If any open → Error: "Dependencies not resolved: #140 (open)"
```

**See**: [_gh-reference.md](_gh-reference.md#blocking-dependencies) for dependency verification

### Pattern 3: Documentation Reading

```
Required Docs in issue (text field):
  "ARCHITECTURE.md, SECURITY.md, PRD.md"

Parse workflow:
  1. Extract from issue body
  2. Split by commas, trim whitespace
  3. Resolve paths: "docs/guides/${doc}" or "docs/project/${doc}"
  4. Validate paths (no directory traversal)
  5. Read each doc with Read tool
  6. Extract relevant patterns and constraints
  7. Apply patterns during implementation
```

### Pattern 4: Acceptance Criteria Verification

```
Before creating PR, verify all checkboxes:
  - [ ] Code implements feature as specified → validate
  - [ ] Security validation applied → check validate_path() usage
  - [ ] Tests written with ≥80% coverage → run coverage report
  - [ ] Architecture tests pass → run test_architecture.py
  - [ ] Pre-commit hooks pass → run pre-commit
```

## Examples

### Basic Implementation

```bash
/gh:issues-implement 142

# Workflow:
1. Validate dependencies (runs validate-agent-ready.sh automatically)
2. Read required docs: ARCHITECTURE.md, SECURITY.md
3. Create branch: feature/add-csv-export (from issue title)
4. Implement changes following acceptance criteria
5. Run tests and quality gates
6. Create PR: "feat(export): add CSV export functionality"
7. Link PR to issue: "Closes #142"
8. Update issue label: agent-implemented
9. Report: "Implemented #142, created PR #156"
```

### Dry Run Validation

```bash
/gh:issues-implement 144 --dry-run

# Validates:
- Issue exists and is open
- Dependencies resolved
- Required docs are linked
- Acceptance criteria clear
- No blockers detected

# Reports: "Issue #144 ready for implementation" or lists blockers
```

### Implementation Without PR

```bash
/gh:issues-implement 145 --no-pr

# Implements changes and commits to branch
# Does not create PR (manual PR creation later)
# Useful for multi-issue PRs or when combining work
```

## Boundaries

**Will:**
- Read all required documentation and apply patterns systematically
- Validate dependencies and prerequisites before implementation
- Implement code following acceptance criteria and project standards
- Run comprehensive tests and quality gates
- Create PR with proper linkage to issue and milestone

**Will Not:**
- Implement issues with unresolved dependencies (must error)
- Skip required documentation reading
- Bypass security validation or quality gates
- Auto-merge PRs (human review always required)
- Close issues without PR merge (manual closure after review)

## Implementation Workflow

### Step -1: Issue Type Detection (FEATURE vs SINGLE TASK)

**CRITICAL**: Before validation, detect if issue is a feature (has sub-tasks) or single task.

```bash
# Query parent-child relationships using manage-issue-relationships.sh
RELATIONSHIP_DATA=$(./scripts/github-projects/manage-issue-relationships.sh view <issue-number>)

# DEPENDENCY: Requires manage-issue-relationships.sh output format "Sub-Issues (N total)"
# If script output format changes, update this grep pattern
SUB_ISSUES_COUNT=$(echo "$RELATIONSHIP_DATA" | grep "Sub-Issues" | grep -oE "[0-9]+ total" | cut -d' ' -f1 || echo "0")

if [[ "$SUB_ISSUES_COUNT" -gt 0 ]]; then
    echo "Detected: FEATURE with $SUB_ISSUES_COUNT sub-tasks"
    implement_feature <issue-number>  # Feature orchestration flow
else
    echo "Detected: SINGLE TASK"
    implement_single_task <issue-number>  # Standard implementation flow
fi
```

**What this determines:**
- **Feature** (has sub-tasks): Orchestrate implementation of all sub-tasks in dependency order
- **Single Task** (no sub-tasks): Standard implementation workflow (Steps 0-5)

**Feature Implementation Flow** (when sub-tasks detected):
1. Fetch all sub-tasks using relationship API
2. Validate ALL sub-tasks are agent-ready (fail fast)
3. Build dependency graph and topological sort
4. Review feature scope against sub-task coverage
5. Create single feature branch
6. Implement each sub-task in dependency order (one commit per task)
7. Skip failed tasks, continue with independent tasks
8. Create single PR closing all completed sub-tasks
9. After PR merge, run integration tests
10. Close parent feature only if integration tests pass

**See**: [Feature Implementation Section](#feature-implementation-with-sub-tasks) below for complete workflow

### Step 0: Validate Agent-Ready Status (AUTOMATED)

**IMPORTANT**: This validation is **automatically executed** at the start of the implementation workflow.

```bash
# AUTOMATED: Runs automatically when /gh:issues-implement is invoked
./scripts/github-projects/validate-agent-ready.sh <issue-number>

if [ $? -ne 0 ]; then
    echo "Error: Issue not ready for agent implementation"
    exit 1
fi
```

**What this validates:**
- Issue structure (title, body, docs, acceptance criteria)
- All dependencies are closed
- Required labels are set (priority, complexity, type)
- Required documentation files exist

**See**: [_gh-reference.md](_gh-reference.md#issue-validation-checklist) for validation details

### Step 1: Fetch and Parse Issue

```bash
# Fetch issue JSON
ISSUE_JSON=$(gh issue view <number> --json title,body,labels,milestone,state)

# Extract metadata
TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
BODY=$(echo "$ISSUE_JSON" | jq -r '.body')
LABELS=$(echo "$ISSUE_JSON" | jq -r '.labels[].name')
MILESTONE=$(echo "$ISSUE_JSON" | jq -r '.milestone.title')
```

### Step 2: Validate Dependencies

```bash
# Parse dependencies from body using safe extraction
parse_blocked_by() {
    local body="$1"
    local deps_section=$(echo "$body" | awk '/### Dependencies/,/^###/ {print}' | grep "Blocked By:")
    local issue_nums=$(echo "$deps_section" | grep -oE '#[0-9]+' | grep -oE '[0-9]+')
    echo "$issue_nums"
}

BLOCKED_BY=$(parse_blocked_by "$BODY")

# Validate each dependency is closed
for dep in $BLOCKED_BY; do
    DEP_STATE=$(gh issue view "$dep" --json state | jq -r '.state')
    if [ "$DEP_STATE" != "CLOSED" ]; then
        echo "Error: Dependency #$dep is $DEP_STATE (must be CLOSED)"
        exit 1
    fi
done
```

**See**: [_gh-reference.md](_gh-reference.md#blocking-dependencies) for dependency patterns

### Step 3: Read Required Documentation

```bash
# Validate and resolve documentation paths
validate_doc_path() {
    local doc_name="$1"
    doc_name=$(echo "$doc_name" | xargs)  # Trim whitespace

    # Resolve standard doc names
    case "$doc_name" in
        ARCHITECTURE.md) echo "docs/guides/ARCHITECTURE.md" ;;
        SECURITY.md) echo "docs/guides/SECURITY.md" ;;
        PRD.md) echo "docs/project/PRD.md" ;;
        TESTING.md) echo "docs/guides/TESTING.md" ;;
        *) echo "docs/guides/$doc_name" ;;
    esac
}

# Extract required docs from issue body
REQUIRED_DOCS_RAW=$(echo "$BODY" | awk '/### Required Documentation/,/^###/ {print}' | grep -v "^###" | head -1)

# Read each document with validation
IFS=',' read -ra DOC_ARRAY <<< "$REQUIRED_DOCS_RAW"
for doc_name in "${DOC_ARRAY[@]}"; do
  doc_path=$(validate_doc_path "$doc_name")
  echo "Reading: $doc_path"
  # Use Read tool to load documentation
done
```

### Step 4: Create Branch and Implement

```bash
# Generate branch name from issue
ISSUE_TYPE=$(echo "$LABELS" | grep -oE 'feature|bugfix|hotfix' | head -1)
BRANCH_NAME="${ISSUE_TYPE}/$(echo $TITLE | sed 's/\[.*\] //' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

# Create branch
git checkout main && git pull
git checkout -b "$BRANCH_NAME"

# Implement changes:
# - Follow acceptance criteria from issue body
# - Apply security patterns (validate_path, sanitize_string)
# - Follow 3-layer architecture rules
# - Write tests alongside implementation
```

### Step 5: Verify and Create PR

```bash
# Run quality gates
python3 -m pytest tests/  # All tests must pass
python3 tests/test_security.py  # 0 vulnerabilities
python3 tests/test_architecture.py  # 0 violations
pre-commit run --all-files  # Linting, formatting

# Create PR with issue linkage
gh pr create \
  --title "$(format_pr_title "$TITLE")" \
  --body "Closes #<issue-number>\n\n[Generated PR description]" \
  --milestone "$MILESTONE"

# Update issue label
gh issue edit <number> --add-label "agent-implemented"
```

**Label Sync**: After adding `agent-implemented` label, GitHub Actions will sync to project fields within 1-5 minutes.

**See**: [_gh-reference.md](_gh-reference.md#label-sync-timing) for sync automation details

## Error Handling

### Dependency Not Resolved

```
Error: Issue #142 has unresolved dependencies
  - #140: OPEN (must be CLOSED)

Action: Wait for dependencies to be resolved, or remove dependency if incorrect
```

### Missing Required Documentation

```
Error: Issue #142 missing required documentation field
  Expected: "Required Documentation" field with comma-separated doc names

Action: Update issue with required documentation
  Example: "ARCHITECTURE.md, SECURITY.md, PRD.md"
```

### Test Failures

```
Error: Quality gates failed
  - pytest: 2 tests failed
  - coverage: 78% (below 80% threshold)

Action: Fix failing tests and improve coverage before creating PR
Human escalation required for debugging
```

### Architecture Violations

```
Error: Architecture validation failed
  - Infrastructure layer importing Presentation (scanner.py:15)

Action: Refactor to respect 3-layer boundaries (P → A → I)
Review: docs/guides/ARCHITECTURE.md
```

**See**: [_gh-reference.md](_gh-reference.md#common-error-patterns) for full error reference

## Rate Limiting

**API Call Breakdown (per issue):**
- Fetch issue details: 1 call
- Fetch dependencies: 1-3 calls
- Validation: 3-5 calls
- Create PR: 1 call
- Update labels: 1 call
- **Total: ~8-15 API calls per issue**

**Best Practices:**
1. Check before batch operations: `gh api rate_limit`
2. Implement one issue at a time (not batch processing)
3. Monitor for rate limit warnings in output

**See**: [_gh-reference.md](_gh-reference.md#rate-limiting-essentials) for rate limit management

## Integration with Project Workflow

### Feature Branch Workflow

```
1. User creates issue: /gh:issues-create create-from-plan
2. Issue created with metadata and acceptance criteria
3. User triggers implementation: /gh:issues-implement #142
4. Agent implements, creates PR
5. Human reviews PR, requests changes if needed
6. Agent updates PR based on feedback
7. Human approves and merges PR
8. GitHub automation closes issue and updates project board
```

### Quality Gates Checklist

```
Before PR creation, verify:
✓ All dependencies resolved (blocked-by issues closed)
✓ Required documentation read and patterns applied
✓ Code implements all acceptance criteria
✓ Security patterns applied (validate_path, sanitize_string)
✓ Tests written with ≥80% coverage overall, ≥95% security
✓ Architecture tests pass (0 violations)
✓ Security tests pass (0 vulnerabilities)
✓ Pre-commit hooks pass (linting, formatting)
✓ Manual testing completed
```

## Feature Implementation with Sub-Tasks

When `/gh:implement-issue` detects sub-tasks (via Step -1), it orchestrates implementation across all sub-tasks: validates upfront, builds dependency graph, implements in order, creates single PR, runs integration tests post-merge.

**For detailed workflow, error recovery, and examples**: See [FEATURE_IMPLEMENTATION.md](../../docs/guides/FEATURE_IMPLEMENTATION.md)

**Executable workflow steps below** (for command reference):

#### Phase 1: Discovery and Validation

```bash
# 1.1 Fetch all sub-tasks using relationship API
SUB_TASKS=$(./scripts/github-projects/manage-issue-relationships.sh view $FEATURE_NUMBER |
            grep -A 100 "Sub-Issues" |
            grep -oE "#[0-9]+" |
            grep -oE "[0-9]+")

echo "Found sub-tasks: $SUB_TASKS"

# 1.2 Validate ALL sub-tasks upfront (fail fast)
for task in $SUB_TASKS; do
    if ! ./scripts/github-projects/validate-agent-ready.sh "$task"; then
        echo "❌ Error: Sub-task #$task failed validation"
        echo "Fix validation issues before implementing feature"
        exit 1
    fi
    echo "✅ Sub-task #$task validated"
done

echo "✅ All sub-tasks validated successfully"
```

#### Phase 2: Dependency Analysis

```bash
# 2.1 Build dependency graph and get topologically sorted list
SORTED_TASKS=$(./scripts/github-projects/build-task-dependency-graph.sh $SUB_TASKS)

if [[ $? -ne 0 ]]; then
    echo "❌ Error: Cycle detected in dependencies"
    echo "Review blocking relationships and remove cycles"
    exit 1
fi

echo "Implementation order: $SORTED_TASKS"

# 2.2 Review feature scope
echo ""
echo "=== Feature Scope Review ==="
gh issue view $FEATURE_NUMBER --json title,body | jq -r '.title,.body'

echo ""
echo "=== Sub-Tasks Coverage ==="
for task in $SORTED_TASKS; do
    gh issue view "$task" --json title | jq -r '"  - #\(input.number): \(.title)"'
done
```

#### Phase 3: Branch Creation

```bash
# 3.1 Generate branch name from feature title
FEATURE_TITLE=$(gh issue view $FEATURE_NUMBER --json title | jq -r '.title')
BRANCH_NAME="feature/$(echo "$FEATURE_TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/\[.*\] //' | tr ' ' '-')"

# 3.2 Create feature branch
git checkout main && git pull
git checkout -b "$BRANCH_NAME"

echo "✅ Created feature branch: $BRANCH_NAME"
```

#### Phase 4: Sub-Task Implementation Loop

```bash
# 4.1 Initialize tracking arrays
declare -a completed_tasks=()
declare -a failed_tasks=()
declare -a skipped_tasks=()

# 4.2 Implement each sub-task in dependency order
for task in $SORTED_TASKS; do
    echo ""
    echo "=========================================="
    echo "Implementing sub-task #$task..."
    echo "=========================================="

    # 4.3 Check if blocked by failed task
    if is_blocked_by_failed_tasks "$task" "${failed_tasks[@]}"; then
        echo "⚠️  Skipping #$task (blocked by failed task)"
        skipped_tasks+=("$task")
        continue
    fi

    # 4.4 Implement single task (use standard Steps 0-5)
    echo "Reading required documentation for #$task..."
    # (Execute standard implementation workflow)

    if implement_single_task_logic "$task"; then
        # 4.5 Commit changes
        git add .
        git commit -m "$(generate_task_commit_message "$task")"

        completed_tasks+=("$task")
        echo "✅ Sub-task #$task completed and committed"
    else
        echo "❌ Sub-task #$task failed"
        failed_tasks+=("$task")
        echo "Marking #$task as needs-human-help"
        gh issue edit "$task" --add-label "needs-human-help"
        # Continue with independent tasks (user requirement)
    fi
done
```

#### Phase 5: PR Creation

```bash
# 5.1 Check if any tasks completed
if [[ ${#completed_tasks[@]} -eq 0 ]]; then
    echo "❌ No tasks completed successfully"
    echo "Cannot create PR with zero changes"
    exit 1
fi

# 5.2 Generate PR body
CLOSES_LIST=$(printf ", #%s" "${completed_tasks[@]}")
CLOSES_LIST=${CLOSES_LIST:2}  # Remove leading ", "

PR_BODY="Closes $CLOSES_LIST

Part of #$FEATURE_NUMBER

## Implemented Sub-Tasks
$(for task in "${completed_tasks[@]}"; do
    gh issue view "$task" --json title | jq -r '"- [x] #'$task': \(.title)"'
done)

$(if [[ ${#failed_tasks[@]} -gt 0 ]]; then
    echo ""
    echo "## Failed Sub-Tasks (Needs Human Help)"
    for task in "${failed_tasks[@]}"; do
        gh issue view "$task" --json title | jq -r '"- [ ] #'$task': \(.title) ⚠️ needs-human-help"'
    done
fi)

$(if [[ ${#skipped_tasks[@]} -gt 0 ]]; then
    echo ""
    echo "## Skipped Sub-Tasks (Blocked by Failed)"
    for task in "${skipped_tasks[@]}"; do
        gh issue view "$task" --json title | jq -r '"- [ ] #'$task': \(.title) 🚫 blocked"'
    done
fi)

## Integration Tests
- [ ] All sub-task tests pass
- [ ] Feature-level integration tests pass
- [ ] Documentation updated

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5.3 Create PR
gh pr create \
  --title "feat(epic): $(echo "$FEATURE_TITLE" | sed 's/\[.*\] //')" \
  --body "$PR_BODY" \
  --milestone "$(gh issue view "$FEATURE_NUMBER" --json milestone | jq -r '.milestone.title')"

echo "✅ PR created successfully"
```

#### Phase 6: Results Reporting

```bash
# 6.1 Generate implementation summary
echo ""
echo "============================================"
echo "Feature Implementation Complete"
echo "============================================"
echo "Feature: #$FEATURE_NUMBER"
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
echo "  3. If integration tests pass, close feature #$FEATURE_NUMBER"
```

### Helper Functions

> **Implementation Note**: The helper functions shown below should be implemented inline within the feature implementation workflow script, or extracted to a separate `scripts/github-projects/feature-implementation-helpers.sh` file and sourced at runtime. Choose inline for simplicity or extracted for reusability across multiple features.

#### Check if Task is Blocked by Failed Task

```bash
is_blocked_by_failed_tasks() {
    local task="$1"
    shift
    local failed_tasks=("$@")

    if [[ ${#failed_tasks[@]} -eq 0 ]]; then
        return 1  # No failed tasks, not blocked
    fi

    # Query task's blocking dependencies
    # NOTE: GitHub API endpoint - if GitHub changes /dependencies/blocked_by path, update here
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

#### Generate Task Commit Message

```bash
generate_task_commit_message() {
    # COMMIT MESSAGE FORMAT (update here if format changes project-wide):
    # Line 1: <type>(task): <title> (#<issue>)
    # Line 2: (blank)
    # Line 3-4: Implementation details
    # Line 5: (blank)
    # Line 6-8: Claude Code attribution

    local task="$1"
    local task_title=$(gh issue view "$task" --json title | jq -r '.title')

    # Extract type from labels
    local labels=$(gh issue view "$task" --json labels | jq -r '.labels[].name')
    local type="feat"  # Default

    if echo "$labels" | grep -q "bugfix"; then
        type="fix"
    elif echo "$labels" | grep -q "hotfix"; then
        type="hotfix"
    fi

    # Generate commit message following format above
    echo "${type}(task): $(echo "$task_title" | sed 's/\[.*\] //') (#$task)

Implements sub-task #$task as part of feature implementation.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
}
```

### Integration Testing (Post-Merge)

After PR merges, run feature-level integration tests:

```bash
# Run integration tests for feature
echo "Running feature-level integration tests..."

# Example: Test entire workflow end-to-end
python3 -m pytest tests/integration/test_feature_$FEATURE_NUMBER.py -v

if [[ $? -eq 0 ]]; then
    echo "✅ Integration tests passed"
    echo "Closing feature #$FEATURE_NUMBER"
    gh issue close "$FEATURE_NUMBER" --comment "Feature implementation complete and integration tests passed. All sub-tasks implemented successfully."
else
    echo "❌ Integration tests failed"
    echo "Reopening feature #$FEATURE_NUMBER for investigation"
    gh issue reopen "$FEATURE_NUMBER"
    gh issue comment "$FEATURE_NUMBER" --body "⚠️ Integration tests failed after PR merge. Requires investigation and fix."
fi
```

### Error Recovery Patterns

#### Scenario 1: One Sub-Task Fails, Others Independent

```
Tasks: #1005 → #1006 → #1007, #1008 (independent), #1009 (independent)

#1006 fails:
  ✅ #1005 completed
  ❌ #1006 failed → mark needs-human-help
  ⚠️  #1007 skipped (depends on #1006)
  ✅ #1008 completed (independent)
  ✅ #1009 completed (independent)

Result: PR with #1005, #1008, #1009
Action: Human fixes #1006, then implements #1007 in follow-up PR
```

#### Scenario 2: Cycle Detected

```
Tasks: #1005 → #1006 → #1007 → #1005 (cycle!)

Error during dependency graph building:
  ❌ Cycle detected: #1005 → #1006 → #1007 → #1005

Action:
  1. Review blocking relationships
  2. Remove incorrect blocker to break cycle
  3. Re-run feature implementation
```

#### Scenario 3: Validation Failure

```
Tasks: #1005, #1006 (missing required docs), #1007, #1008, #1009

Validation phase:
  ✅ #1005 validated
  ❌ #1006 validation failed (missing required documentation)

Error: Sub-task #1006 failed validation
Action: Update #1006 with required documentation, then re-run
```

## Configuration

### ~/.vscanrc Extension

```ini
[github_issues]
auto_branch_prefix = true
default_reviewer = jvlivonius
auto_run_tests = true
auto_add_labels = agent-implemented
require_passing_tests = true
```

## Agent Personas

This command activates specialized agent expertise:

**python-expert:** Production-quality Python code, SOLID principles, clean architecture
**security-engineer:** Security pattern validation, OWASP compliance verification
**quality-engineer:** Test strategy, edge case detection, coverage analysis

## References

- [_gh-reference.md](_gh-reference.md) - Shared GitHub command reference
- [GITHUB_RELATIONSHIPS.md](../../docs/contributing/GITHUB_RELATIONSHIPS.md) - Dependency management
- [GITHUB_PROJECTS.md](../../docs/contributing/GITHUB_PROJECTS.md) - Project workflow
- [ARCHITECTURE.md](../../docs/guides/ARCHITECTURE.md) - 3-layer architecture
- [SECURITY.md](../../docs/guides/SECURITY.md) - Security patterns
- [TESTING.md](../../docs/guides/TESTING.md) - Testing standards
