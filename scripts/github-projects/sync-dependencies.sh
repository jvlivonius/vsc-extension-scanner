#!/usr/bin/env bash
#
# sync-dependencies.sh - Ensure issue body dependencies match GitHub API state
#
# This script validates that "Blocked By: #N" documented in issue bodies
# match the actual GitHub native dependency relationships set via API.
# Can check for discrepancies or automatically create missing relationships.
#
# Usage:
#   ./scripts/github-projects/sync-dependencies.sh ISSUE_NUMBER [ACTION]
#
# Arguments:
#   ISSUE_NUMBER    Issue number to check/sync
#   ACTION          check (default) or fix
#                   - check: Report discrepancies only
#                   - fix: Create missing GitHub dependencies
#
# Examples:
#   # Check for discrepancies
#   ./scripts/github-projects/sync-dependencies.sh 142
#
#   # Fix discrepancies by creating missing dependencies
#   ./scripts/github-projects/sync-dependencies.sh 142 fix

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
readonly COLOR_RED='\033[0;31m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${COLOR_BLUE}[INFO]${COLOR_NC} $*"
}

log_success() {
    echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_NC} $*"
}

log_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_NC} $*"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_NC} $*" >&2
}

# Function to safely parse blocked-by dependencies from issue body
parse_blocked_by() {
    local body="$1"

    # Extract dependency section using awk
    local deps_section=$(echo "$body" | awk '/### Dependencies/,/^###/ {print}' | grep "Blocked By:" || echo "")

    # Extract issue numbers with validation
    local issue_nums=$(echo "$deps_section" | grep -oE '#[0-9]+' | grep -oE '[0-9]+' || echo "")

    # Validate each is actually a number
    local validated_nums=""
    for num in $issue_nums; do
        if [[ "$num" =~ ^[0-9]+$ ]] && [[ "$num" != "0" ]]; then
            validated_nums="$validated_nums $num"
        fi
    done

    echo "$validated_nums"
}

# Parse arguments
ISSUE_NUMBER="${1:-}"
ACTION="${2:-check}"

if [[ -z "$ISSUE_NUMBER" ]]; then
    echo "Usage: $(basename "$0") ISSUE_NUMBER [check|fix]"
    exit 1
fi

if [[ "$ACTION" != "check" && "$ACTION" != "fix" ]]; then
    log_error "Invalid action: $ACTION (must be 'check' or 'fix')"
    exit 1
fi

log_info "Analyzing dependency synchronization for issue #$ISSUE_NUMBER..."
echo ""

# Get issue body
BODY=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body' 2>/dev/null)

if [[ -z "$BODY" ]]; then
    log_error "Could not fetch issue #$ISSUE_NUMBER"
    exit 1
fi

# Parse documented dependencies from issue body
BLOCKED_BY_TEXT=$(parse_blocked_by "$BODY")

# Get GitHub API dependencies
BLOCKED_BY_API=$(gh api "repos/:owner/:repo/issues/$ISSUE_NUMBER/dependencies/blocked_by" 2>/dev/null | jq -r '.[].number' | tr '\n' ' ' || echo "")

log_info "Documented in issue body: ${BLOCKED_BY_TEXT:-None}"
log_info "Set in GitHub API: ${BLOCKED_BY_API:-None}"
echo ""

# Find discrepancies
MISSING_IN_API=""
EXTRA_IN_API=""

# Check for dependencies documented but not in API
for dep in $BLOCKED_BY_TEXT; do
    if ! echo "$BLOCKED_BY_API" | grep -qw "$dep"; then
        MISSING_IN_API="$MISSING_IN_API $dep"
    fi
done

# Check for dependencies in API but not documented
for dep in $BLOCKED_BY_API; do
    if ! echo "$BLOCKED_BY_TEXT" | grep -qw "$dep"; then
        EXTRA_IN_API="$EXTRA_IN_API $dep"
    fi
done

# Report findings
SYNC_ISSUES=0

if [[ -n "$MISSING_IN_API" ]]; then
    log_warning "Dependencies documented but NOT set in GitHub API:$MISSING_IN_API"
    ((SYNC_ISSUES++))
fi

if [[ -n "$EXTRA_IN_API" ]]; then
    log_warning "Dependencies in GitHub API but NOT documented in issue body:$EXTRA_IN_API"
    ((SYNC_ISSUES++))
fi

if [[ $SYNC_ISSUES -eq 0 ]]; then
    log_success "✓ Dependencies are synchronized"
    exit 0
fi

echo ""

# Take action based on mode
if [[ "$ACTION" == "fix" ]]; then
    log_info "Fixing discrepancies..."
    echo ""

    SUCCESS_COUNT=0
    FAIL_COUNT=0

    # Create missing GitHub dependencies
    if [[ -n "$MISSING_IN_API" ]]; then
        log_info "Creating missing GitHub dependencies..."

        for dep in $MISSING_IN_API; do
            log_info "  Setting #$dep as blocker for #$ISSUE_NUMBER..."

            if "$SCRIPT_DIR/manage-issue-relationships.sh" set-blocker "$dep" "$ISSUE_NUMBER" &>/dev/null; then
                log_success "  ✓ Dependency #$dep created"
                ((SUCCESS_COUNT++))
            else
                log_error "  ✗ Failed to create dependency #$dep"
                ((FAIL_COUNT++))
            fi
        done
    fi

    # Report on extra dependencies in API
    if [[ -n "$EXTRA_IN_API" ]]; then
        log_warning "Note: The following dependencies exist in GitHub API but not in issue body:"
        for dep in $EXTRA_IN_API; do
            log_warning "  - #$dep (consider adding to issue body or removing from API)"
        done
    fi

    echo ""
    echo "=== FIX SUMMARY ==="
    echo "Created: $SUCCESS_COUNT"
    echo "Failed: $FAIL_COUNT"

    if [[ $FAIL_COUNT -eq 0 ]]; then
        log_success "✓ Dependencies synchronized successfully"
        exit 0
    else
        log_error "✗ Some dependencies failed to sync"
        exit 1
    fi
else
    # Check mode - just report
    echo "=== RECOMMENDATIONS ==="

    if [[ -n "$MISSING_IN_API" ]]; then
        echo "To create missing GitHub dependencies, run:"
        echo "  $0 $ISSUE_NUMBER fix"
        echo ""
        echo "Or manually:"
        for dep in $MISSING_IN_API; do
            echo "  ./scripts/github-projects/manage-issue-relationships.sh set-blocker $dep $ISSUE_NUMBER"
        done
    fi

    if [[ -n "$EXTRA_IN_API" ]]; then
        echo ""
        echo "To remove extra GitHub dependencies, run:"
        for dep in $EXTRA_IN_API; do
            echo "  ./scripts/github-projects/manage-issue-relationships.sh remove-blocker $dep $ISSUE_NUMBER"
        done
    fi

    exit 1
fi
