#!/usr/bin/env bash
#
# update-status.sh - Update GitHub Projects status field with verification
#
# Usage: ./update-status.sh <issue-number> <status>
#
# Example:
#   ./update-status.sh 71 "In Progress"
#
# Valid statuses: "Backlog", "Todo", "In Progress", "In Review", "Done"

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source rate limit library if available
if [[ -f "$SCRIPT_DIR/rate_limit.sh" ]]; then
    source "$SCRIPT_DIR/rate_limit.sh"
else
    rate_limit_guard() { return 0; }
    rate_limit_delay() { return 0; }
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${NC}[INFO] $*" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

usage() {
    cat << 'EOF'
Update GitHub Projects Status Field

Usage:
  update-status.sh <issue-number> <status>

Arguments:
  issue-number    GitHub issue number (e.g., 71)
  status          Target status (Backlog|Todo|In Progress|In Review|Done)

Examples:
  # Transition to In Progress
  ./update-status.sh 71 "In Progress"

  # Mark as Done
  ./update-status.sh 75 "Done"

Notes:
  - Status field name must match exactly (case-sensitive)
  - Requires gh CLI authentication with project scope
  - Rate limit: 1 API call per update + 1 verification call

EOF
}

# Validate arguments
if [ $# -ne 2 ]; then
    log_error "Invalid number of arguments"
    usage
    exit 1
fi

ISSUE_NUMBER="$1"
TARGET_STATUS="$2"

# Validate issue number
if ! [[ "$ISSUE_NUMBER" =~ ^[0-9]+$ ]]; then
    log_error "Invalid issue number: $ISSUE_NUMBER"
    exit 1
fi

# Validate status value
VALID_STATUSES=("Backlog" "Todo" "In Progress" "In Review" "Done")
if [[ ! " ${VALID_STATUSES[@]} " =~ " ${TARGET_STATUS} " ]]; then
    log_error "Invalid status: $TARGET_STATUS"
    log_error "Valid statuses: ${VALID_STATUSES[*]}"
    exit 1
fi

log_info "Updating issue #$ISSUE_NUMBER status to '$TARGET_STATUS'"

# Check rate limit
rate_limit_guard || exit 1

# Get issue node ID for GraphQL query
ISSUE_NODE_ID=$(gh issue view "$ISSUE_NUMBER" --json id --jq '.id')

if [ -z "$ISSUE_NODE_ID" ]; then
    log_error "Could not get issue node ID for #$ISSUE_NUMBER"
    exit 1
fi

# Query project items via GraphQL to get project item ID and project ID
PROJECT_QUERY_RESULT=$(gh api graphql -f query='
  query($issueId: ID!) {
    node(id: $issueId) {
      ... on Issue {
        projectItems(first: 1) {
          nodes {
            id
            project {
              id
            }
          }
        }
      }
    }
  }
' -f issueId="$ISSUE_NODE_ID")

PROJECT_ITEM_ID=$(echo "$PROJECT_QUERY_RESULT" | jq -r '.data.node.projectItems.nodes[0].id // empty')
PROJECT_ID=$(echo "$PROJECT_QUERY_RESULT" | jq -r '.data.node.projectItems.nodes[0].project.id // empty')

if [ -z "$PROJECT_ITEM_ID" ] || [ -z "$PROJECT_ID" ]; then
    log_error "Issue #$ISSUE_NUMBER is not in any project"
    exit 1
fi

# Get Status field ID
STATUS_FIELD_ID=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" --jq '.data.node.fields.nodes[] | select(.name=="Status") | .id')

if [ -z "$STATUS_FIELD_ID" ]; then
    log_error "Could not find Status field in project"
    exit 1
fi

# Get target status option ID
STATUS_OPTION_ID=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              name
              options {
                id
                name
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" --jq ".data.node.fields.nodes[] | select(.name==\"Status\") | .options[] | select(.name==\"$TARGET_STATUS\") | .id")

if [ -z "$STATUS_OPTION_ID" ]; then
    log_error "Could not find status option '$TARGET_STATUS' in project"
    exit 1
fi

# Update status field via GraphQL mutation
log_info "Executing status transition..."

MUTATION_RESULT=$(gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
    updateProjectV2ItemFieldValue(
      input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: {
          singleSelectOptionId: $value
        }
      }
    ) {
      projectV2Item {
        id
      }
    }
  }
' -f projectId="$PROJECT_ID" \
  -f itemId="$PROJECT_ITEM_ID" \
  -f fieldId="$STATUS_FIELD_ID" \
  -f value="$STATUS_OPTION_ID")

if [ -z "$MUTATION_RESULT" ]; then
    log_error "Status update mutation failed"
    exit 1
fi

rate_limit_delay

# Verify status update (allow 2 seconds for API to settle)
sleep 2
log_info "Verifying status transition..."

CURRENT_STATUS=$(gh issue view "$ISSUE_NUMBER" --json projectItems \
  --jq '.projectItems[0].status.name // empty')

if [ "$CURRENT_STATUS" = "$TARGET_STATUS" ]; then
    log_success "Status updated successfully: #$ISSUE_NUMBER → '$TARGET_STATUS'"
    exit 0
else
    log_error "Status verification failed"
    log_error "Expected: '$TARGET_STATUS', Got: '$CURRENT_STATUS'"
    exit 1
fi
