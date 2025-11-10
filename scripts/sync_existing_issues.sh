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

    if echo "$labels" | grep -q "P0-critical"; then
        echo "Critical"
    elif echo "$labels" | grep -q "P1-high"; then
        echo "High"
    elif echo "$labels" | grep -q "P2-medium"; then
        echo "Medium"
    elif echo "$labels" | grep -q "P3-low"; then
        echo "Low"
    else
        echo ""
    fi
}

# Function to extract complexity from labels
get_complexity_from_labels() {
    local labels="$1"

    if echo "$labels" | grep -q "complexity/XS"; then
        echo "XS"
    elif echo "$labels" | grep -q "complexity/S"; then
        echo "S"
    elif echo "$labels" | grep -q "complexity/M"; then
        echo "M"
    elif echo "$labels" | grep -q "complexity/L"; then
        echo "L"
    elif echo "$labels" | grep -q "complexity/XL"; then
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

# Get all issues in the project with their labels
log_info "Fetching issues from project..."

ISSUES=$(gh issue list --limit 100 --json number,title,labels,projectItems --jq '.[] | select(.projectItems | length > 0) | {number, title, labels: [.labels[].name]}')

if [[ -z "$ISSUES" ]]; then
    log_warning "No issues found in project"
    exit 0
fi

# Count issues
TOTAL_ISSUES=$(echo "$ISSUES" | jq -s 'length')
log_info "Found $TOTAL_ISSUES issues in project"
echo

# Track statistics
SYNCED_COUNT=0
SKIPPED_COUNT=0

# Process each issue
while IFS= read -r issue_json; do
    ISSUE_NUMBER=$(echo "$issue_json" | jq -r '.number')
    ISSUE_TITLE=$(echo "$issue_json" | jq -r '.title')
    LABELS=$(echo "$issue_json" | jq -r '.labels | join(",")')

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
        ((SKIPPED_COUNT++))
    else
        sync_issue_fields "$ISSUE_NUMBER" "$PRIORITY_LABEL" "$COMPLEXITY_LABEL"
        ((SYNCED_COUNT++))

        if [[ "$DRY_RUN" == false ]]; then
            # Wait a bit between issues to avoid rate limiting
            sleep 2
        fi
    fi

    echo
done <<< "$ISSUES"

# Summary
echo "================================"
log_success "Sync complete!"
log_info "  Total issues: $TOTAL_ISSUES"
log_info "  Synced: $SYNCED_COUNT"
log_info "  Skipped: $SKIPPED_COUNT"

if [[ "$DRY_RUN" == false ]]; then
    log_info ""
    log_info "Note: GitHub Actions workflows are running to update project fields"
    log_info "      Field updates should complete within 10-15 seconds per issue"
    log_info "      Check GitHub Actions tab to monitor progress"
fi
