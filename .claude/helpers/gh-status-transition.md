# GitHub Projects Status Transition Helper

**Purpose**: Enforce status transitions with verification and audit trail to prevent skipped workflow steps.

## Critical Requirement

**Status transitions are FIRST-CLASS operations that MUST be explicitly performed and verified.**

This helper ensures:
1. Status transitions are attempted
2. Transitions are verified via query
3. Failures are detected and reported loudly
4. All transitions are logged to Serena memory for audit trail

## Usage

```bash
# Update status with verification
update_github_projects_status <issue_number> <new_status> [<project_id>] [<field_id>]

# Examples:
update_github_projects_status 142 "Todo"
update_github_projects_status 142 "In Progress"
update_github_projects_status 142 "In Review"
```

## Status Values

- `Backlog` - Issue created, not yet ready
- `Todo` - Ready to start work (MANUAL transition)
- `In Progress` - Implementation started (MANUAL transition)
- `In Review` - PR created (AUTOMATIC transition)
- `Done` - PR merged (AUTOMATIC transition)
- `Blocked` - Has open dependencies (AUTOMATIC/MANUAL)

## Implementation

### Step 1: Get Project Item ID

```bash
function get_project_item_id() {
    local issue_number="$1"
    local project_title="VS Code Extension Scanner Development"

    # Query project items for this issue
    gh issue view "$issue_number" --json projectItems --jq \
        ".projectItems[] | select(.project.title == \"$project_title\") | .id"
}
```

### Step 2: Get Status Field ID

```bash
function get_status_field_id() {
    local project_id="$1"  # Can be retrieved or hardcoded

    # For now, use gh API to get field ID
    # In future, can hardcode once project structure is stable
    gh api graphql -f query='
    query {
      node(id: "$project_id") {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
              }
            }
          }
        }
      }
    }' --jq '.data.node.fields.nodes[] | select(.name == "Status") | .id'
}
```

### Step 3: Update Status with Verification

```bash
function update_github_projects_status() {
    local issue_number="$1"
    local new_status="$2"
    local project_id="${3:-PVT_kwDOQHRxEM4Ap7xz}"  # Default project ID

    echo "📊 Updating issue #$issue_number status: → $new_status"

    # Get project item ID
    local item_id=$(get_project_item_id "$issue_number")
    if [ -z "$item_id" ]; then
        echo "❌ ERROR: Issue #$issue_number not found in GitHub Projects"
        return 1
    fi

    # Update status using gh project item-edit
    gh project item-edit \
        --project-id "$project_id" \
        --id "$item_id" \
        --field-id "Status" \
        --text "$new_status"

    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to update status for issue #$issue_number"
        return 1
    fi

    # Wait for GitHub API to settle (2 seconds)
    sleep 2

    # VERIFY transition completed
    local actual_status=$(verify_status "$issue_number")

    if [ "$actual_status" != "$new_status" ]; then
        echo "❌ VERIFICATION FAILED:"
        echo "   Expected: $new_status"
        echo "   Actual:   $actual_status"
        echo ""
        echo "🚨 CRITICAL: Status transition did not complete as expected!"
        echo "   Manual intervention required."
        return 1
    fi

    echo "✅ Status transition verified: #$issue_number → $new_status"

    # Store transition in Serena memory for audit trail
    store_status_transition_audit "$issue_number" "$new_status"

    return 0
}
```

### Step 4: Verify Status

```bash
function verify_status() {
    local issue_number="$1"
    local project_title="VS Code Extension Scanner Development"

    # Query current status from GitHub Projects
    gh issue view "$issue_number" --json projectItems --jq \
        ".projectItems[] | select(.project.title == \"$project_title\") | .fieldValues.nodes[] | select(.field.name == \"Status\") | .name"
}
```

### Step 5: Store Audit Trail in Serena Memory

```bash
function store_status_transition_audit() {
    local issue_number="$1"
    local new_status="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Create or update audit memory
    mcp__serena__write_memory "status_transitions_issue_${issue_number}" \
        "$(cat <<EOF
# Status Transition Audit: Issue #${issue_number}

## Latest Transition
- **Status**: ${new_status}
- **Timestamp**: ${timestamp}
- **Agent**: Claude Code (Orchestrator)

## Transition History
$(mcp__serena__read_memory "status_transitions_issue_${issue_number}" 2>/dev/null | grep "^-" || echo "- Initial: Backlog")
- ${timestamp}: → ${new_status}
EOF
)"

    echo "📝 Audit trail updated in Serena memory"
}
```

## Error Handling

### Status Transition Failed

```bash
if ! update_github_projects_status "$issue_number" "In Progress"; then
    echo "🚨 CRITICAL ERROR: Status transition failed"
    echo "   Issue #$issue_number could not be moved to 'In Progress'"
    echo "   Aborting workflow to prevent inconsistent state"
    exit 1
fi
```

**Behavior**: Fail loudly and halt workflow. Do NOT proceed with implementation if status transition fails.

### Verification Mismatch

```bash
# Automatic detection in update_github_projects_status function
# If verification fails, function returns 1 and prints error message
# Caller must handle failure (usually by aborting)
```

## Integration with Orchestrator

### Before Spawning Sub-Agent

```bash
# CRITICAL: Update status BEFORE delegation
if ! update_github_projects_status "$issue_number" "In Progress"; then
    echo "❌ Cannot proceed: Status transition to 'In Progress' failed"
    exit 1
fi

# ONLY after status verified, spawn sub-agent
result=$(invoke_sub_agent_implementer "$issue_number" "$payload")
```

### After PR Creation

```bash
# Create PR first
pr_number=$(gh pr create --title "..." --body "Closes #$issue_number")

if [ $? -eq 0 ]; then
    # CRITICAL: Update status AFTER PR creation
    if ! update_github_projects_status "$issue_number" "In Review"; then
        echo "⚠️ WARNING: PR created but status transition failed"
        echo "   PR #$pr_number: https://github.com/owner/repo/pull/$pr_number"
        echo "   Manually update issue #$issue_number to 'In Review' status"
    fi
else
    echo "❌ PR creation failed - keeping status as 'In Progress'"
fi
```

## Audit Trail Queries

### Check Status History for Issue

```bash
# Read status transition history from Serena memory
mcp__serena__read_memory "status_transitions_issue_142"
```

**Example Output**:
```
# Status Transition Audit: Issue #142

## Latest Transition
- **Status**: In Review
- **Timestamp**: 2025-11-21T22:45:30Z
- **Agent**: Claude Code (Orchestrator)

## Transition History
- 2025-11-21T22:30:15Z: → Todo
- 2025-11-21T22:35:42Z: → In Progress
- 2025-11-21T22:45:30Z: → In Review
```

### List All Status Audits

```bash
# List all status transition memories
mcp__serena__list_memories | grep "status_transitions_issue_"
```

## Testing

### Manual Test

```bash
# Test status transition for issue #142
update_github_projects_status 142 "Todo"

# Verify audit trail was created
mcp__serena__read_memory "status_transitions_issue_142"
```

### Rollback Test

```bash
# Test verification failure (use invalid status)
update_github_projects_status 142 "InvalidStatus"

# Should fail with verification error and return 1
```

## Key Guarantees

1. **Atomic Verification**: Status update + verification happen together
2. **Fail Loudly**: Verification failures halt workflow immediately
3. **Audit Trail**: Every transition logged to Serena memory with timestamp
4. **No Silent Failures**: All errors reported with clear messages
5. **Idempotent**: Can retry transitions safely (same status → no change)

## Boundaries

**Responsibilities**:
- ✅ Update GitHub Projects status field
- ✅ Verify transition completed correctly
- ✅ Store audit trail in Serena memory
- ✅ Fail loudly on verification mismatch

**Not Responsible For**:
- ❌ Deciding WHEN to transition (orchestrator's logic)
- ❌ Validating if transition is allowed (GitHub Projects handles this)
- ❌ Fetching issue metadata (caller provides issue number)
- ❌ Creating issues or PRs (separate responsibilities)

## Future Enhancements

1. **Hardcode Project/Field IDs**: Once stable, hardcode IDs to reduce API calls
2. **Retry Logic**: Add automatic retry with exponential backoff for transient failures
3. **Batch Transitions**: Support updating multiple issues in one call
4. **Transition Validation**: Check if transition is valid before attempting (e.g., can't go Backlog → Done)
5. **Rollback Support**: Revert to previous status if subsequent operation fails
