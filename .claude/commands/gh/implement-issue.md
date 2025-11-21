---
name: issues-implement
description: "Implement GitHub issue with automated doc reading, testing, and PR creation"
category: workflow
complexity: advanced
mcp-servers: []  # Orchestrator uses NO MCP servers (subagent gets them)
personas: []     # Orchestrator has NO personas (subagent gets them)
---

# /gh:implement-issue - GitHub Issue Orchestration

Agent-driven issue implementation with Task-based subprocess orchestration for guaranteed status transitions.

## Overview

**Orchestrator Role** (this command): GitHub Projects workflow management
- Fetch issue metadata and validate prerequisites
- **Update status transitions** (Backlog → Todo → In Progress → In Review)
- Spawn implementation subagent via Task tool
- Create pull request from subagent results
- Handle failures gracefully

**Subagent Role** (Task tool subprocess): Pure implementation
- Read required documentation
- Create feature branch
- Implement changes per acceptance criteria
- Run tests and quality gates
- Commit and push changes
- Return structured result

## Usage

```bash
/gh:implement-issue <issue-number>
```

**Example:**
```bash
/gh:implement-issue 71
```

## Workflow Steps

### Step 0: Validate Issue Prerequisites

Before starting implementation, validate the issue is agent-ready:

```bash
ISSUE_NUMBER="$1"

# Validate using automated script
if ! ./scripts/github-projects/validate-agent-ready.sh "$ISSUE_NUMBER"; then
    echo "❌ Issue #$ISSUE_NUMBER is not agent-ready"
    echo "Run validation to see specific failures"
    exit 1
fi

echo "✅ Issue #$ISSUE_NUMBER validated as agent-ready"
```

**Validation checks:**
- Issue structure complete (title, body, acceptance criteria)
- All blocking dependencies closed
- Required documentation exists
- Labels complete (type, priority, complexity)
- No `blocked-by` or `needs-human-help` labels

---

### Step 1: Fetch Issue Metadata

Fetch complete issue data from GitHub:

```bash
# Fetch issue JSON with all metadata
ISSUE_JSON=$(gh issue view "$ISSUE_NUMBER" --json \
  title,body,labels,milestone,state,number,projectItems)

# Extract core metadata
ISSUE_TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
ISSUE_BODY=$(echo "$ISSUE_JSON" | jq -r '.body')
LABELS_RAW=$(echo "$ISSUE_JSON" | jq -r '.labels[].name')
LABELS=$(echo "$LABELS_RAW" | tr '\n' ',' | sed 's/,$//')
MILESTONE=$(echo "$ISSUE_JSON" | jq -r '.milestone.title // "none"')

# Determine issue type from labels
if echo "$LABELS" | grep -q "feature"; then
    ISSUE_TYPE="feature"
elif echo "$LABELS" | grep -q "bugfix"; then
    ISSUE_TYPE="bugfix"
elif echo "$LABELS" | grep -q "hotfix"; then
    ISSUE_TYPE="hotfix"
else
    ISSUE_TYPE="task"
fi

echo "Issue #$ISSUE_NUMBER: $ISSUE_TITLE"
echo "Type: $ISSUE_TYPE"
echo "Labels: $LABELS"
echo "Milestone: $MILESTONE"
```

---

### Step 2: Parse Acceptance Criteria and Required Docs

Extract structured data from issue body:

```bash
# Parse acceptance criteria (checkboxes)
ACCEPTANCE_CRITERIA=$(echo "$ISSUE_BODY" | \
  awk '/## Acceptance Criteria/,/^##/ {print}' | \
  grep '^- \[ \]' | \
  sed 's/^- \[ \] //' | \
  jq -R -s -c 'split("\n") | map(select(length > 0))')

# Parse required documentation
REQUIRED_DOCS_LINE=$(echo "$ISSUE_BODY" | \
  awk '/## Required Documentation/,/^##/ {print}' | \
  grep -v '^##' | head -1 | tr -d '\n' | xargs)

# Split comma-separated docs into array
REQUIRED_DOCS=$(echo "$REQUIRED_DOCS_LINE" | \
  jq -R -s -c 'split(",") | map(ltrimstr(" ") | rtrimstr(" ")) | map(select(length > 0))')

echo "Acceptance Criteria:"
echo "$ACCEPTANCE_CRITERIA" | jq -r '.[]' | sed 's/^/  - /'

echo "Required Documentation:"
echo "$REQUIRED_DOCS" | jq -r '.[]' | sed 's/^/  - /'
```

---

### Step 3: Generate Branch Name

Create semantic branch name from issue type and title:

```bash
# Remove task/feature markers, convert to lowercase, replace spaces with dashes
BRANCH_TITLE=$(echo "$ISSUE_TITLE" | \
  sed 's/\[.*\] //' | \
  tr '[:upper:]' '[:lower:]' | \
  tr ' ' '-' | \
  sed 's/[^a-z0-9-]//g' | \
  cut -c1-50)

BRANCH_NAME="${ISSUE_TYPE}/${BRANCH_TITLE}"

echo "Branch name: $BRANCH_NAME"
```

---

### Step 4: Update Status → "In Progress"

**⚠️ CRITICAL**: Enforce status transition BEFORE spawning subagent.

```bash
echo "Transitioning status to 'In Progress'..."

if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Progress"; then
    echo "❌ CRITICAL: Status transition to 'In Progress' failed"
    echo "Cannot proceed with implementation"
    exit 1
fi

echo "✅ Status transition verified: In Progress"
```

**Status script guarantees:**
- GraphQL mutation executed
- 2-second API settle time
- Status queried and verified
- Exit code 1 if verification fails

---

### Step 5: Select Subagent Type

Automatically select appropriate subagent based on issue characteristics:

```bash
select_subagent_type() {
    local labels="$1"
    local acceptance_criteria="$2"
    local required_docs="$3"

    # Priority 1: Security tasks
    if echo "$labels" | grep -q "security" || \
       echo "$required_docs" | jq -r '.[]' | grep -q "SECURITY.md"; then
        echo "security-engineer"
        return
    fi

    # Priority 2: Quality/Testing tasks
    if echo "$labels" | grep -qE "test|quality" || \
       echo "$acceptance_criteria" | jq -r '.[]' | grep -qiE "test coverage|≥[0-9]+%|unit test|property test"; then
        echo "quality-engineer"
        return
    fi

    # Priority 3: Python development (features/enhancements)
    if echo "$labels" | grep -qE "feature|enhancement"; then
        echo "python-expert"
        return
    fi

    # Default: General-purpose (no specialized persona)
    echo "general-purpose"
}

SUBAGENT_TYPE=$(select_subagent_type "$LABELS" "$ACCEPTANCE_CRITERIA" "$REQUIRED_DOCS")

echo "Selected subagent type: $SUBAGENT_TYPE"
```

**Subagent type mapping:**
- `security-engineer` → OWASP, validate_path(), sanitize_string()
- `quality-engineer` → pytest, hypothesis, coverage analysis
- `python-expert` → SOLID, clean architecture, TDD
- `general-purpose` → Basic implementation (no specialized persona)

---

### Step 6: Build Implementation Payload

Create structured JSON payload for subagent:

```bash
PAYLOAD=$(jq -n \
  --arg issue_number "$ISSUE_NUMBER" \
  --arg issue_title "$ISSUE_TITLE" \
  --arg issue_type "$ISSUE_TYPE" \
  --arg labels "$LABELS" \
  --argjson acceptance_criteria "$ACCEPTANCE_CRITERIA" \
  --argjson required_docs "$REQUIRED_DOCS" \
  --arg branch_name "$BRANCH_NAME" \
  --arg milestone "$MILESTONE" \
  '{
    issue_number: $issue_number,
    issue_title: $issue_title,
    issue_type: $issue_type,
    labels: ($labels | split(",")),
    acceptance_criteria: $acceptance_criteria,
    required_docs: $required_docs,
    branch_name: $branch_name,
    milestone: $milestone
  }')

echo "Implementation payload prepared"
```

---

### Step 7: Spawn Implementation Subagent

**⚠️ CRITICAL**: Use Task tool to spawn subagent with clean context.

Now I'll use the **Task tool** to spawn the implementation subagent:

```
Task Parameters:
- subagent_type: "$SUBAGENT_TYPE" (selected in Step 5)
- description: "Implement issue #$ISSUE_NUMBER"
- prompt: "You are implementing GitHub issue #$ISSUE_NUMBER in a clean implementation context.

**Your Role**: Pure implementation (NO GitHub Projects management)

**Issue Metadata**:
```json
$PAYLOAD
```

**Your Responsibilities**:
1. Read all required documentation from issue payload
2. Create feature branch: $BRANCH_NAME
3. Implement changes following acceptance criteria exactly
4. Apply project standards (ARCHITECTURE.md, SECURITY.md patterns)
5. Run tests and quality gates (security, architecture, pre-commit)
6. Commit changes with proper commit message format
7. Push branch to remote

**Return Format** (JSON):
```json
{
  "status": "success" | "failed",
  "commit_sha": "<sha>",
  "files_changed": ["file1.py", "file2.md"],
  "tests_run": true,
  "test_results": {
    "total": 245,
    "passed": 245,
    "failed": 0,
    "coverage": "87.2%"
  },
  "quality_gates": {
    "security_tests": "passed",
    "architecture_tests": "passed",
    "pre_commit": "passed"
  },
  "error_message": null | "<error details>"
}
```

**IMPORTANT**:
- You have access to MCP servers: serena, sequential-thinking
- You are running with persona: $SUBAGENT_TYPE
- Never update GitHub Projects status (orchestrator handles that)
- Return structured JSON result when complete
- If you encounter errors, set status='failed' and provide error_message

Start implementation now."
```

**Subagent execution happens in separate subprocess with:**
- Clean context (no orchestration noise)
- Full MCP server access (serena + sequential-thinking)
- Appropriate agent persona activated
- Isolated from GitHub Projects workflow

---

### Step 8: Process Subagent Result

When subagent completes, parse and validate the result:

```bash
# Subagent returns JSON result
SUBAGENT_RESULT="<returned by Task tool>"

# Parse result fields
RESULT_STATUS=$(echo "$SUBAGENT_RESULT" | jq -r '.status')
COMMIT_SHA=$(echo "$SUBAGENT_RESULT" | jq -r '.commit_sha // "none"')
FILES_CHANGED=$(echo "$SUBAGENT_RESULT" | jq -r '.files_changed | join(", ")')
TESTS_RUN=$(echo "$SUBAGENT_RESULT" | jq -r '.tests_run')
ERROR_MESSAGE=$(echo "$SUBAGENT_RESULT" | jq -r '.error_message // "none"')

if [ "$RESULT_STATUS" = "success" ]; then
    echo "✅ Implementation successful"
    echo "   Commit: $COMMIT_SHA"
    echo "   Files changed: $FILES_CHANGED"
    echo "   Tests run: $TESTS_RUN"
else
    echo "❌ Implementation failed"
    echo "   Error: $ERROR_MESSAGE"

    # Keep status "In Progress", add needs-human-help label
    gh issue edit "$ISSUE_NUMBER" --add-label "needs-human-help"

    # Add failure comment
    gh issue comment "$ISSUE_NUMBER" --body "⚠️ Agent implementation failed

**Error Details**: $ERROR_MESSAGE

**Status**: Remains 'In Progress' for manual intervention
**Branch**: $BRANCH_NAME (preserved for debugging)

Manual investigation and fixes required."

    exit 1
fi
```

**Failure handling:**
- Status stays "In Progress" (NOT reverted to Todo)
- `needs-human-help` label added
- Branch and commits preserved for debugging
- Detailed error comment posted

---

### Step 9: Create Pull Request

Generate comprehensive PR from subagent results:

```bash
# Generate PR title (conventional commit format)
PR_TITLE_PREFIX=$(echo "$ISSUE_TYPE" | sed 's/task/feat/')
PR_TITLE="${PR_TITLE_PREFIX}($(echo "$ISSUE_TYPE" | cut -c1-10)): $(echo "$ISSUE_TITLE" | sed 's/\[.*\] //')"

# Extract test results for PR body
TEST_TOTAL=$(echo "$SUBAGENT_RESULT" | jq -r '.test_results.total // 0')
TEST_PASSED=$(echo "$SUBAGENT_RESULT" | jq -r '.test_results.passed // 0')
TEST_COVERAGE=$(echo "$SUBAGENT_RESULT" | jq -r '.test_results.coverage // "N/A"')

QUALITY_SECURITY=$(echo "$SUBAGENT_RESULT" | jq -r '.quality_gates.security_tests // "N/A"')
QUALITY_ARCH=$(echo "$SUBAGENT_RESULT" | jq -r '.quality_gates.architecture_tests // "N/A"')
QUALITY_PRECOMMIT=$(echo "$SUBAGENT_RESULT" | jq -r '.quality_gates.pre_commit // "N/A"')

# Build PR body
PR_BODY="Closes #$ISSUE_NUMBER

## Summary
Implements issue #$ISSUE_NUMBER: $ISSUE_TITLE

## Changes
$FILES_CHANGED

## Testing
- Tests: $TEST_PASSED / $TEST_TOTAL passed
- Coverage: $TEST_COVERAGE
- Security tests: $QUALITY_SECURITY
- Architecture tests: $QUALITY_ARCH
- Pre-commit hooks: $QUALITY_PRECOMMIT

## Checklist
- [x] Code implements feature as specified
- [x] All acceptance criteria verified
- [x] Security validation applied (validate_path, sanitize_string)
- [x] Tests written with required coverage
- [x] Quality gates passed

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Create PR
gh pr create \
  --title "$PR_TITLE" \
  --body "$PR_BODY" \
  --head "$BRANCH_NAME" \
  --base main \
  --milestone "$MILESTONE"

PR_NUMBER=$(gh pr view --json number --jq '.number')
echo "✅ Created PR #$PR_NUMBER"
```

---

### Step 10: Update Status → "In Review"

**⚠️ CRITICAL**: Enforce status transition AFTER PR creation.

```bash
echo "Transitioning status to 'In Review'..."

if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Review"; then
    echo "⚠️ WARNING: Status transition to 'In Review' failed"
    echo "PR created successfully, but manual status update needed"
    echo "Run: gh project item-edit --id <item-id> --field Status --text 'In Review'"
fi

echo "✅ Status transition verified: In Review"
```

**Note**: Status transition failure is non-blocking (PR already created).

---

### Step 11: Final Summary

```bash
echo ""
echo "======================================"
echo "✅ Implementation Complete"
echo "======================================"
echo "Issue: #$ISSUE_NUMBER"
echo "PR: #$PR_NUMBER"
echo "Branch: $BRANCH_NAME"
echo "Commit: $COMMIT_SHA"
echo "Status: In Review"
echo "Files Changed: $FILES_CHANGED"
echo ""
echo "Next Steps:"
echo "1. PR awaits review and approval"
echo "2. CI/CD checks will run automatically"
echo "3. Merge after approval to close issue"
echo "======================================"
```

---

## Error Handling

### Subagent Implementation Failure
- **Action**: Keep status "In Progress"
- **Label**: Add "needs-human-help"
- **Comment**: Post error details
- **Preserve**: Branch and commits for debugging
- **Exit**: Code 1 (failed)

### Status Transition Failure (Before Implementation)
- **Action**: Halt workflow immediately
- **Reason**: Cannot track work without status
- **Exit**: Code 1 (failed)
- **Fix**: Check gh auth scopes, project permissions

### Status Transition Failure (After PR Creation)
- **Action**: Log warning, continue (non-blocking)
- **Reason**: PR already created successfully
- **Manual**: User updates status via GitHub UI
- **Exit**: Code 0 (success with warning)

### PR Creation Failure
- **Action**: Rollback status to "In Progress"
- **Label**: Add "needs-human-help"
- **Preserve**: Branch and commits
- **Comment**: Post PR creation error
- **Exit**: Code 1 (failed)

---

## Subagent Type Decision Tree

```
Issue Analysis
     ↓
┌─────────────────────────────┐
│ Labels contain "security"?  │
│ OR SECURITY.md required?    │──Yes──→ security-engineer
└──────────┬──────────────────┘
           ↓ No
┌─────────────────────────────┐
│ Labels contain "test"       │
│ "quality"?                  │
│ OR AC mentions "coverage"?  │──Yes──→ quality-engineer
└──────────┬──────────────────┘
           ↓ No
┌─────────────────────────────┐
│ Labels contain "feature"    │
│ or "enhancement"?           │──Yes──→ python-expert
└──────────┬──────────────────┘
           ↓ No
     general-purpose
```

---

## Architecture Benefits

### Orchestrator (This Command)
✅ Clean focus: GitHub Projects workflow only
✅ NO MCP servers (lightweight context)
✅ NO agent personas (pure orchestration)
✅ Status transitions enforced via bash checkpoints
✅ Verification after each status change

### Subagent (Task Tool)
✅ Clean focus: Pure implementation only
✅ Full MCP access (serena + sequential-thinking)
✅ Appropriate persona activated automatically
✅ Isolated from GitHub Projects noise
✅ Structured return format (JSON)

### Key Guarantees
✅ Status transitions CANNOT be skipped (bash enforced)
✅ True subprocess isolation (Task tool)
✅ Automatic persona selection (no manual config)
✅ Graceful failure handling (preserve state)
✅ Comprehensive audit trail (logs + comments)

---

## Example Execution: Issue #71

```
$ /gh:implement-issue 71

✅ Issue #71 validated as agent-ready
Issue #71: [TASK] Add CLI Examples to Documentation
Type: task
Labels: documentation, enhancement, P2-medium, complexity/S
Milestone: v5.0.3

Acceptance Criteria:
  - CLI examples added to CLAUDE.md
  - Examples follow DOCUMENTATION_STANDARDS.md
  - Pre-commit hooks pass

Required Documentation:
  - DOCUMENTATION_STANDARDS.md

Branch name: task/add-cli-examples

Transitioning status to 'In Progress'...
✅ Status transition verified: In Progress

Selected subagent type: general-purpose

Implementation payload prepared

Spawning implementation subagent...
[Task tool creates subprocess]
[Subagent executes implementation]
[Subagent returns JSON result]

✅ Implementation successful
   Commit: abc123def
   Files changed: CLAUDE.md, README.md, docs/project/PRD.md
   Tests run: false

✅ Created PR #1027

Transitioning status to 'In Review'...
✅ Status transition verified: In Review

======================================
✅ Implementation Complete
======================================
Issue: #71
PR: #1027
Branch: task/add-cli-examples
Commit: abc123def
Status: In Review
Files Changed: CLAUDE.md, README.md, docs/project/PRD.md
======================================
```

---

## References

- **Status Script**: `scripts/github-projects/update-status.sh`
- **Validation Script**: `scripts/github-projects/validate-agent-ready.sh`
- **Task Tool Documentation**: See Claude Code docs for Task tool usage
- **Orchestration Pattern**: See `.claude/RULES_CORE.md` for full pattern documentation
