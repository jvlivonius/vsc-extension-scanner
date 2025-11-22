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

## 🚨 CRITICAL: YOU ARE AN ORCHESTRATOR, NOT AN IMPLEMENTER 🚨

```
╔════════════════════════════════════════════════════════════════╗
║                     YOUR ROLE IN THIS WORKFLOW                  ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║ ✅ ORCHESTRATOR (you) → GitHub workflow + Task tool spawning   ║
║ ✅ SUBAGENT (Task tool) → Pure implementation subprocess       ║
║                                                                 ║
║ ⛔ DO NOT: Implement code, read impl files, edit/write files   ║
║ ⛔ DO NOT: Use MCP tools (serena, sequential-thinking)         ║
║                                                                 ║
║ ✅ DO: Use Bash (gh CLI, git, scripts)                         ║
║ ✅ DO: Use Task tool to spawn implementation subagent          ║
║ ✅ DO: Create PRs from subagent results                        ║
║                                                                 ║
║ IF YOU IMPLEMENT CODE → YOU FAILED THE ASSIGNMENT              ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
```

**Quick Reference:**
- **Orchestrator** (this command): GitHub Projects status → Task tool → PR creation
- **Subagent** (Task subprocess): Documentation → branch → implementation → tests → commit → return JSON

**Usage:** `/gh:implement-issue <issue-number>`

---

## Workflow Steps

### Step -1: Environment Validation

Verify prerequisites before starting:

```bash
ISSUE_NUMBER="$1"

# Check gh CLI authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ gh CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Check required tools
for cmd in jq git; do
    if ! command -v $cmd &>/dev/null; then
        echo "❌ Required tool not found: $cmd"
        exit 1
    fi
done

# Check validation script exists
if [ ! -f "./scripts/github-projects/validate-agent-ready.sh" ]; then
    echo "❌ Validation script not found"
    exit 1
fi

echo "✅ Environment validated"
```

---

### Step 0: Validate Issue Prerequisites

```bash
if ! ./scripts/github-projects/validate-agent-ready.sh "$ISSUE_NUMBER"; then
    echo "❌ Issue #$ISSUE_NUMBER is not agent-ready"
    exit 1
fi

echo "✅ Issue #$ISSUE_NUMBER validated as agent-ready"
```

**Validation checks:** Issue structure, dependencies closed, required docs exist, labels complete, no blockers

---

### Step 1: Fetch Issue Metadata

```bash
# Fetch issue JSON
ISSUE_JSON=$(gh issue view "$ISSUE_NUMBER" --json title,body,labels,milestone,state,number,projectItems)

# Extract metadata
ISSUE_TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
ISSUE_BODY=$(echo "$ISSUE_JSON" | jq -r '.body')
LABELS_RAW=$(echo "$ISSUE_JSON" | jq -r '.labels[].name')
LABELS=$(echo "$LABELS_RAW" | tr '\n' ',' | sed 's/,$//')
MILESTONE=$(echo "$ISSUE_JSON" | jq -r '.milestone.title // "none"')

# Determine issue type
if echo "$LABELS" | grep -q "feature"; then ISSUE_TYPE="feature"
elif echo "$LABELS" | grep -q "bugfix"; then ISSUE_TYPE="bugfix"
elif echo "$LABELS" | grep -q "hotfix"; then ISSUE_TYPE="hotfix"
else ISSUE_TYPE="task"; fi

echo "Issue #$ISSUE_NUMBER: $ISSUE_TITLE | Type: $ISSUE_TYPE | Milestone: $MILESTONE"
```

---

### Step 2: Parse Acceptance Criteria and Required Docs

```bash
# Parse acceptance criteria
ACCEPTANCE_CRITERIA=$(echo "$ISSUE_BODY" | \
  awk '/## Acceptance Criteria/,/^##/ {print}' | \
  grep '^- \[ \]' | sed 's/^- \[ \] //' | \
  jq -R -s -c 'split("\n") | map(select(length > 0))')

# Parse required documentation
REQUIRED_DOCS_LINE=$(echo "$ISSUE_BODY" | \
  awk '/## Required Documentation/,/^##/ {print}' | \
  grep -v '^##' | head -1 | tr -d '\n' | xargs)
REQUIRED_DOCS=$(echo "$REQUIRED_DOCS_LINE" | \
  jq -R -s -c 'split(",") | map(ltrimstr(" ") | rtrimstr(" ")) | map(select(length > 0))')

echo "Acceptance Criteria: $(echo "$ACCEPTANCE_CRITERIA" | jq -r '. | length') items"
echo "Required Docs: $(echo "$REQUIRED_DOCS" | jq -r '. | length') files"
```

---

### Step 3: Generate Branch Name (with Collision Handling)

```bash
# Generate base branch name
BRANCH_TITLE=$(echo "$ISSUE_TITLE" | \
  sed 's/\[.*\] //' | tr '[:upper:]' '[:lower:]' | \
  tr ' ' '-' | sed 's/[^a-z0-9-]//g' | cut -c1-50)
BRANCH_NAME="${ISSUE_TYPE}/${BRANCH_TITLE}"

# Handle collisions
SUFFIX=1
while git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; do
    BRANCH_NAME="${ISSUE_TYPE}/${BRANCH_TITLE}-${SUFFIX}"
    SUFFIX=$((SUFFIX + 1))
done

echo "Branch name: $BRANCH_NAME (verified unique)"
```

---

### Step 4: Update Status → "In Progress"

**⚠️ CRITICAL**: Status transition BEFORE spawning subagent (fail-fast if transition fails).

```bash
if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Progress"; then
    echo "❌ CRITICAL: Status transition failed. Cannot proceed."
    exit 1
fi

echo "✅ Status: In Progress"
```

**Guarantees:** GraphQL mutation → 2s settle time → verification query → exit 1 if mismatch

---

### Step 5: Select Subagent Type

```bash
select_subagent_type() {
    local labels="$1" ac="$2" docs="$3"

    # Priority 1: Security
    echo "$labels" | grep -q "security" && { echo "security-engineer"; return; }
    echo "$docs" | jq -r '.[]' | grep -q "SECURITY.md" && { echo "security-engineer"; return; }

    # Priority 2: Quality/Testing
    echo "$labels" | grep -qE "test|quality" && { echo "quality-engineer"; return; }
    echo "$ac" | jq -r '.[]' | grep -qiE "coverage|≥[0-9]+%|unit test|property test" && { echo "quality-engineer"; return; }

    # Priority 3: Python development
    echo "$labels" | grep -qE "feature|enhancement" && { echo "python-expert"; return; }

    # Default
    echo "general-purpose"
}

SUBAGENT_TYPE=$(select_subagent_type "$LABELS" "$ACCEPTANCE_CRITERIA" "$REQUIRED_DOCS")
echo "Subagent: $SUBAGENT_TYPE"
```

**Decision Tree:** security > quality > python-expert > general-purpose

---

### Step 6: Build Implementation Payload

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
  '{issue_number: $issue_number, issue_title: $issue_title, issue_type: $issue_type,
    labels: ($labels | split(",")), acceptance_criteria: $acceptance_criteria,
    required_docs: $required_docs, branch_name: $branch_name, milestone: $milestone}')

echo "✅ Payload prepared"
```

---

### Step 7: 🛑 EXECUTE TASK TOOL TO SPAWN SUBAGENT 🛑

**⚠️ CRITICAL INSTRUCTION**: You MUST now **execute the Task tool** (not just show parameters).

**Execute this tool call NOW:**

```
Task tool parameters:
- subagent_type: "$SUBAGENT_TYPE"
- description: "Implement issue #$ISSUE_NUMBER"
- prompt: "You are implementing GitHub issue #$ISSUE_NUMBER in a clean subprocess.

**Your Role**: Pure implementation (NO GitHub Projects management)

**Issue Payload**:
$PAYLOAD

**Your Tasks**:
1. Read required docs from payload.required_docs
2. Create branch: payload.branch_name
3. Implement per payload.acceptance_criteria
4. Apply ARCHITECTURE.md + SECURITY.md patterns
5. Run tests + quality gates (security, architecture, pre-commit)
6. Commit with format: <type>(<scope>): <subject>
7. Push branch

**RETURN THIS JSON STRUCTURE**:
{
  \"status\": \"success\" | \"failed\",
  \"commit_sha\": \"<sha>\",
  \"files_changed\": [\"file1.py\", \"file2.md\"],
  \"tests_run\": true,
  \"test_results\": {\"total\": 245, \"passed\": 245, \"failed\": 0, \"coverage\": \"87.2%\"},
  \"quality_gates\": {\"security_tests\": \"passed\", \"architecture_tests\": \"passed\", \"pre_commit\": \"passed\"},
  \"error_message\": null
}

**Context**:
- MCP servers available: serena, sequential-thinking, context7, playwright
- Persona active: $SUBAGENT_TYPE
- NEVER update GitHub Projects status (orchestrator handles it)
- Return JSON when complete or failed

Start implementation now."
```

**STOP AND EXECUTE THE TASK TOOL ABOVE BEFORE PROCEEDING TO STEP 8**

**Subprocess Guarantees**:
- ✅ Clean context (no orchestrator variables/state)
- ✅ Full MCP access (serena, sequential-thinking, context7, playwright)
- ✅ Auto-activated persona ($SUBAGENT_TYPE)
- ✅ One-way communication: orchestrator → subagent (prompt), subagent → orchestrator (JSON return)

---

### Step 8: Process Subagent Result

**IMPORTANT**: This step runs AFTER Task tool completes and returns result.

```bash
# Validate JSON structure
if ! echo "$SUBAGENT_RESULT" | jq empty 2>/dev/null; then
    echo "❌ Subagent returned invalid JSON"
    gh issue edit "$ISSUE_NUMBER" --add-label "needs-human-help"
    gh issue comment "$ISSUE_NUMBER" --body "⚠️ Subagent returned malformed result. Manual investigation required."
    exit 1
fi

# Parse with defaults
RESULT_STATUS=$(echo "$SUBAGENT_RESULT" | jq -r '.status // "unknown"')
COMMIT_SHA=$(echo "$SUBAGENT_RESULT" | jq -r '.commit_sha // "none"')
FILES_CHANGED=$(echo "$SUBAGENT_RESULT" | jq -r '.files_changed | join(", ") // "none"')
TESTS_RUN=$(echo "$SUBAGENT_RESULT" | jq -r '.tests_run // false')
ERROR_MESSAGE=$(echo "$SUBAGENT_RESULT" | jq -r '.error_message // "none"')

# Handle success/failure
if [ "$RESULT_STATUS" = "success" ]; then
    echo "✅ Implementation successful"
    echo "   Commit: $COMMIT_SHA | Files: $FILES_CHANGED | Tests: $TESTS_RUN"
else
    echo "❌ Implementation failed: $ERROR_MESSAGE"
    gh issue edit "$ISSUE_NUMBER" --add-label "needs-human-help"
    gh issue comment "$ISSUE_NUMBER" --body "⚠️ Agent implementation failed

**Error**: $ERROR_MESSAGE
**Status**: Remains 'In Progress' for manual intervention
**Branch**: $BRANCH_NAME (preserved for debugging)"
    exit 1
fi
```

---

### Step 9: Create Pull Request (with Retry)

```bash
# Generate PR title
PR_TITLE_PREFIX=$(echo "$ISSUE_TYPE" | sed 's/task/feat/')
PR_TITLE="${PR_TITLE_PREFIX}(${ISSUE_TYPE:0:10}): $(echo "$ISSUE_TITLE" | sed 's/\[.*\] //')"

# Extract test results
TEST_TOTAL=$(echo "$SUBAGENT_RESULT" | jq -r '.test_results.total // 0')
TEST_PASSED=$(echo "$SUBAGENT_RESULT" | jq -r '.test_results.passed // 0')
TEST_COVERAGE=$(echo "$SUBAGENT_RESULT" | jq -r '.test_results.coverage // "N/A"')
QUALITY_SEC=$(echo "$SUBAGENT_RESULT" | jq -r '.quality_gates.security_tests // "N/A"')
QUALITY_ARCH=$(echo "$SUBAGENT_RESULT" | jq -r '.quality_gates.architecture_tests // "N/A"')
QUALITY_PRE=$(echo "$SUBAGENT_RESULT" | jq -r '.quality_gates.pre_commit // "N/A"')

# Build PR body
PR_BODY="Closes #$ISSUE_NUMBER

## Summary
$ISSUE_TITLE

## Changes
$FILES_CHANGED

## Testing
- Tests: $TEST_PASSED / $TEST_TOTAL passed | Coverage: $TEST_COVERAGE
- Security: $QUALITY_SEC | Architecture: $QUALITY_ARCH | Pre-commit: $QUALITY_PRE

## Checklist
- [x] Implements acceptance criteria
- [x] Security validation (validate_path, sanitize_string)
- [x] Tests + quality gates passed

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

# Create PR with retry logic
MAX_RETRIES=3
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if gh pr create --title "$PR_TITLE" --body "$PR_BODY" --head "$BRANCH_NAME" --base main --milestone "$MILESTONE" 2>/dev/null; then
        PR_NUMBER=$(gh pr view --json number --jq '.number')
        echo "✅ Created PR #$PR_NUMBER"
        break
    else
        RETRY=$((RETRY + 1))
        if [ $RETRY -lt $MAX_RETRIES ]; then
            echo "⚠️ PR creation failed, retrying ($RETRY/$MAX_RETRIES)..."
            sleep 2
        else
            echo "❌ PR creation failed after $MAX_RETRIES attempts"
            ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Progress"
            gh issue edit "$ISSUE_NUMBER" --add-label "needs-human-help"
            gh issue comment "$ISSUE_NUMBER" --body "⚠️ PR creation failed after $MAX_RETRIES attempts. Branch: $BRANCH_NAME"
            exit 1
        fi
    fi
done
```

---

### Step 10: Update Status → "In Review"

```bash
if ! ./scripts/github-projects/update-status.sh "$ISSUE_NUMBER" "In Review"; then
    echo "⚠️ WARNING: Status transition to 'In Review' failed (non-blocking)"
    echo "PR #$PR_NUMBER created successfully. Manual status update needed."
fi

echo "✅ Status: In Review"
```

**Note:** Failure is non-blocking (PR already created).

---

### Step 11: Final Summary

```bash
echo ""
echo "╔════════════════════════════════════════╗"
echo "║  ✅ Implementation Complete            ║"
echo "╠════════════════════════════════════════╣"
echo "║ Issue:  #$ISSUE_NUMBER                 "
echo "║ PR:     #$PR_NUMBER                    "
echo "║ Branch: $BRANCH_NAME                   "
echo "║ Commit: $COMMIT_SHA                    "
echo "║ Status: In Review                      "
echo "║ Files:  $FILES_CHANGED                 "
echo "╠════════════════════════════════════════╣"
echo "║ Next: PR review → CI checks → Merge    ║"
echo "╚════════════════════════════════════════╝"
```

---

## Error Handling Reference

| Error Type | Status | Label | Exit | Notes |
|------------|--------|-------|------|-------|
| Environment validation failed | N/A | - | 1 | Pre-workflow check |
| Issue not agent-ready | N/A | - | 1 | Validation failed |
| Status → "In Progress" failed | - | - | 1 | Cannot track work |
| Subagent implementation failed | In Progress | needs-human-help | 1 | Preserve branch |
| Subagent JSON invalid | In Progress | needs-human-help | 1 | Malformed response |
| PR creation failed (all retries) | In Progress | needs-human-help | 1 | Rollback status |
| Status → "In Review" failed | - | - | 0 | Non-blocking warning |

---

## Subagent Type Decision Tree

```
Issue Analysis
     ↓
security label OR SECURITY.md → security-engineer
     ↓ No
test/quality label OR "coverage" in AC → quality-engineer
     ↓ No
feature/enhancement label → python-expert
     ↓ No
general-purpose
```

---

## Architecture Benefits

**Orchestrator** (this command):
- ✅ Lightweight: NO MCP servers, NO personas
- ✅ Bash-enforced status transitions (cannot be bypassed)
- ✅ Verification after each mutation

**Subagent** (Task subprocess):
- ✅ Clean context: No orchestration noise
- ✅ Full MCP access: serena, sequential-thinking, context7, playwright
- ✅ Auto-activated persona: security-engineer, quality-engineer, python-expert, general-purpose
- ✅ Structured JSON return format

**Key Guarantees:**
- ✅ Status transitions CANNOT be skipped (bash exit codes)
- ✅ True subprocess isolation (Task tool)
- ✅ Automatic persona selection (no manual config)
- ✅ Graceful failure handling (preserve "In Progress" state)

---

## Example Execution

```
$ /gh:implement-issue 71

✅ Environment validated
✅ Issue #71 validated as agent-ready
Issue #71: [TASK] Add CLI Examples | Type: task | Milestone: v5.0.3
Acceptance Criteria: 3 items | Required Docs: 1 files
Branch name: task/add-cli-examples (verified unique)
✅ Status: In Progress
Subagent: general-purpose
✅ Payload prepared

[Task tool spawned with subagent_type=general-purpose]
[Subagent executes: docs → branch → implementation → tests → commit]
[Subagent returns JSON result]

✅ Implementation successful
   Commit: abc123def | Files: CLAUDE.md, README.md | Tests: true
✅ Created PR #1027
✅ Status: In Review

╔════════════════════════════════════════╗
║  ✅ Implementation Complete            ║
╠════════════════════════════════════════╣
║ Issue:  #71
║ PR:     #1027
║ Branch: task/add-cli-examples
║ Commit: abc123def
║ Status: In Review
║ Files:  CLAUDE.md, README.md
╠════════════════════════════════════════╣
║ Next: PR review → CI checks → Merge    ║
╚════════════════════════════════════════╝
```

---

## References

- **Status Script**: `scripts/github-projects/update-status.sh` (GraphQL mutations + verification)
- **Validation Script**: `scripts/github-projects/validate-agent-ready.sh` (issue prerequisites)
- **Orchestration Pattern**: `.claude/RULES_CORE.md` (Task-based subprocess architecture)
