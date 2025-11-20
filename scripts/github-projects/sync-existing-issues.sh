#!/usr/bin/env bash
#
# sync_existing_issues.sh - Sync Priority/Complexity for Existing Issues
#
# Syncs Priority and Complexity labels to project custom fields for all
# existing issues in the project.
#
# Usage:
#   ./scripts/sync_existing_issues.sh [OPTIONS]
#
# Options:
#   --project-number NUM    Project number (default: 3)
#   --dry-run              Show what would be synced without making changes
#   --help                 Show this help message
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - PROJECT_TOKEN secret configured (not GITHUB_TOKEN)
#   - Issues must already be in the project
#
# Examples:
#   # Sync all issues in project #3
#   ./scripts/sync_existing_issues.sh
#
#   # Preview what would be synced
#   ./scripts/sync_existing_issues.sh --dry-run
#
#   # Sync issues in different project
#   ./scripts/sync_existing_issues.sh --project-number 5

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_NUMBER="3"
DRY_RUN=false

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Function to show usage
usage() {
    cat << EOF
Sync Priority/Complexity for Existing Issues

Usage:
  $(basename "$0") [OPTIONS]

Options:
  --project-number NUM    Project number (default: 3)
  --dry-run              Show what would be synced without making changes
  --help                 Show this help message

Prerequisites:
  - gh CLI installed and authenticated
  - PROJECT_TOKEN configured (not GITHUB_TOKEN)
  - Issues must already be in the project

Examples:
  # Sync all issues in project #3
  $(basename "$0")

  # Preview what would be synced
  $(basename "$0") --dry-run

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-number)
            PROJECT_NUMBER="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Function to extract priority from labels
get_priority_from_labels() {
    local labels="$1"

    if [[ "$labels" == *"P0-critical"* ]]; then
        echo "Critical"
    elif [[ "$labels" == *"P1-high"* ]]; then
        echo "High"
    elif [[ "$labels" == *"P2-medium"* ]]; then
        echo "Medium"
    elif [[ "$labels" == *"P3-low"* ]]; then
        echo "Low"
    else
        echo ""
    fi
}

# Function to extract complexity from labels
get_complexity_from_labels() {
    local labels="$1"

    if [[ "$labels" == *"complexity/XS"* ]]; then
        echo "XS"
    elif [[ "$labels" == *"complexity/S"* ]]; then
        echo "S"
    elif [[ "$labels" == *"complexity/M"* ]]; then
        echo "M"
    elif [[ "$labels" == *"complexity/L"* ]]; then
        echo "L"
    elif [[ "$labels" == *"complexity/XL"* ]]; then
        echo "XL"
    else
        echo ""
    fi
}

# Function to trigger label sync by re-adding label
sync_issue_fields() {
    local issue_number="$1"
    local priority_label="$2"
    local complexity_label="$3"

    if [[ -n "$priority_label" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            log_info "  [DRY RUN] Would sync Priority: $priority_label"
        else
            log_info "  Syncing Priority: $priority_label"
            # Remove and re-add label to trigger workflow
            gh issue edit "$issue_number" --remove-label "$priority_label" 2>/dev/null || true
            sleep 0.5
            gh issue edit "$issue_number" --add-label "$priority_label"
            sleep 0.5
        fi
    fi

    if [[ -n "$complexity_label" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            log_info "  [DRY RUN] Would sync Complexity: $complexity_label"
        else
            log_info "  Syncing Complexity: $complexity_label"
            # Remove and re-add label to trigger workflow
            gh issue edit "$issue_number" --remove-label "$complexity_label" 2>/dev/null || true
            sleep 0.5
            gh issue edit "$issue_number" --add-label "$complexity_label"
            sleep 0.5
        fi
    fi
}

log_info "Starting sync for issues in Project #$PROJECT_NUMBER"

if [[ "$DRY_RUN" == true ]]; then
    log_warning "DRY RUN MODE - No changes will be made"
fi

# Get all issues in the project with their labels and current field values
log_info "Fetching issues from project..."

# Fetch issues as JSON array
ISSUES_JSON=$(gh issue list --limit 100 --json number,title,labels,projectItems --jq '[.[] | select(.projectItems | length > 0)]')

if [[ "$ISSUES_JSON" == "[]" ]]; then
    log_warning "No issues found in project"
    exit 0
fi

# Count issues
TOTAL_ISSUES=$(echo "$ISSUES_JSON" | jq 'length')
log_info "Found $TOTAL_ISSUES issues in project"
echo

# Get project field values for all issues
log_info "Fetching current project field values..."

# GraphQL query to get project items with field values
QUERY=$(cat <<'EOF'
query($projectNumber: Int!, $owner: String!) {
  user(login: $owner) {
    projectV2(number: $projectNumber) {
      items(first: 100) {
        nodes {
          content {
            ... on Issue {
              number
            }
          }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
EOF
)

OWNER=$(gh repo view --json owner -q '.owner.login')
PROJECT_FIELDS=$(gh api graphql -f query="$QUERY" -F projectNumber="$PROJECT_NUMBER" -f owner="$OWNER")

# Track statistics
SYNCED_COUNT=0
SKIPPED_COUNT=0
ALREADY_SYNCED=0

# Process each issue
for i in $(seq 0 $((TOTAL_ISSUES - 1))); do
    issue_json=$(echo "$ISSUES_JSON" | jq ".[$i]")

    ISSUE_NUMBER=$(echo "$issue_json" | jq -r '.number')
    ISSUE_TITLE=$(echo "$issue_json" | jq -r '.title')
    LABELS=$(echo "$issue_json" | jq -r '[.labels[].name] | join(",")')

    log_info "Issue #$ISSUE_NUMBER: $ISSUE_TITLE"

    # Extract priority and complexity
    PRIORITY=$(get_priority_from_labels "$LABELS")
    COMPLEXITY=$(get_complexity_from_labels "$LABELS")

    # Determine priority label
    PRIORITY_LABEL=""
    case "$PRIORITY" in
        Critical) PRIORITY_LABEL="P0-critical" ;;
        High)     PRIORITY_LABEL="P1-high" ;;
        Medium)   PRIORITY_LABEL="P2-medium" ;;
        Low)      PRIORITY_LABEL="P3-low" ;;
    esac

    # Determine complexity label
    COMPLEXITY_LABEL=""
    if [[ -n "$COMPLEXITY" ]]; then
        COMPLEXITY_LABEL="complexity/$COMPLEXITY"
    fi

    # Check if there's anything to sync
    if [[ -z "$PRIORITY_LABEL" ]] && [[ -z "$COMPLEXITY_LABEL" ]]; then
        log_warning "  No Priority or Complexity labels - skipping"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    else
        # Get current field values for this issue
        CURRENT_PRIORITY=$(echo "$PROJECT_FIELDS" | jq -r \
            --arg issue "$ISSUE_NUMBER" \
            '.data.user.projectV2.items.nodes[] |
             select(.content.number == ($issue | tonumber)) |
             .fieldValues.nodes[] |
             select(.field.name == "Priority") |
             .name // ""' || echo "")

        CURRENT_COMPLEXITY=$(echo "$PROJECT_FIELDS" | jq -r \
            --arg issue "$ISSUE_NUMBER" \
            '.data.user.projectV2.items.nodes[] |
             select(.content.number == ($issue | tonumber)) |
             .fieldValues.nodes[] |
             select(.field.name == "Complexity") |
             .name // ""' || echo "")

        # Check if sync is needed
        NEEDS_PRIORITY_SYNC=false
        NEEDS_COMPLEXITY_SYNC=false

        if [[ -n "$PRIORITY" ]] && [[ "$CURRENT_PRIORITY" != "$PRIORITY" ]]; then
            NEEDS_PRIORITY_SYNC=true
            log_info "  Priority: $CURRENT_PRIORITY → $PRIORITY (needs sync)"
        elif [[ -n "$PRIORITY" ]] && [[ "$CURRENT_PRIORITY" == "$PRIORITY" ]]; then
            log_info "  Priority: $PRIORITY (already synced)"
        fi

        if [[ -n "$COMPLEXITY" ]] && [[ "$CURRENT_COMPLEXITY" != "$COMPLEXITY" ]]; then
            NEEDS_COMPLEXITY_SYNC=true
            log_info "  Complexity: $CURRENT_COMPLEXITY → $COMPLEXITY (needs sync)"
        elif [[ -n "$COMPLEXITY" ]] && [[ "$CURRENT_COMPLEXITY" == "$COMPLEXITY" ]]; then
            log_info "  Complexity: $COMPLEXITY (already synced)"
        fi

        # Only sync if needed
        if [[ "$NEEDS_PRIORITY_SYNC" == true ]] || [[ "$NEEDS_COMPLEXITY_SYNC" == true ]]; then
            # Determine which labels to sync
            SYNC_PRIORITY_LABEL=""
            SYNC_COMPLEXITY_LABEL=""

            if [[ "$NEEDS_PRIORITY_SYNC" == true ]]; then
                SYNC_PRIORITY_LABEL="$PRIORITY_LABEL"
            fi

            if [[ "$NEEDS_COMPLEXITY_SYNC" == true ]]; then
                SYNC_COMPLEXITY_LABEL="$COMPLEXITY_LABEL"
            fi

            sync_issue_fields "$ISSUE_NUMBER" "$SYNC_PRIORITY_LABEL" "$SYNC_COMPLEXITY_LABEL"
            SYNCED_COUNT=$((SYNCED_COUNT + 1))

            if [[ "$DRY_RUN" == false ]]; then
                # Wait a bit between issues to avoid rate limiting
                sleep 2
            fi
        else
            log_success "  Already synced - skipping"
            ALREADY_SYNCED=$((ALREADY_SYNCED + 1))
        fi
    fi

    echo
done

# Summary
echo "================================"
log_success "Sync complete!"
log_info "  Total issues: $TOTAL_ISSUES"
log_info "  Synced: $SYNCED_COUNT"
log_info "  Already synced: $ALREADY_SYNCED"
log_info "  Skipped (no labels): $SKIPPED_COUNT"

if [[ "$DRY_RUN" == false ]]; then
    log_info ""
    log_info "Note: GitHub Actions workflows are running to update project fields"
    log_info "      Field updates should complete within 10-15 seconds per issue"
    log_info "      Check GitHub Actions tab to monitor progress"
fi
