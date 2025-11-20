#!/usr/bin/env bash
# Validate milestone is ready for closure
#
# Usage: validate-milestone-closure.sh <milestone> [--force]
#
# Exit Codes:
#   0 = Milestone ready for closure
#   1 = Validation failed (blocking issues)
#   2 = Critical error (script failure, missing dependencies)
#
# Documentation:
#   - Milestone Management: .claude/commands/gh/milestone.md
#   - Issue Validation: .claude/commands/gh/_gh-reference.md#issue-validation-checklist
#   - Rate Limiting: docs/guides/GITHUB_API_RATE_LIMITS.md

set -euo pipefail

# Source rate limit library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/rate_limit.sh" ]]; then
    source "$SCRIPT_DIR/rate_limit.sh"
else
    echo "ERROR: rate_limit.sh not found" >&2
    exit 2
fi

# Colors for output
readonly COLOR_RED='\033[0;31m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_NC='\033[0m'

# Logging functions
log_info() { echo -e "${COLOR_BLUE}ℹ️  $*${COLOR_NC}"; }
log_success() { echo -e "${COLOR_GREEN}✓ $*${COLOR_NC}"; }
log_error() { echo -e "${COLOR_RED}✗ $*${COLOR_NC}" >&2; }
log_warning() { echo -e "${COLOR_YELLOW}⚠️  $*${COLOR_NC}" >&2; }

# Validation tracking
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

# Parse arguments
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <milestone> [--force|--dry-run]" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 v3.8.0" >&2
    echo "  $0 v3.8.0 --force" >&2
    echo "  $0 v3.8.0 --dry-run" >&2
    exit 2
fi

MILESTONE="${1:-}"
FORCE="${2:-}"
DRY_RUN=false

# Validate milestone parameter
if [[ -z "$MILESTONE" ]]; then
    log_error "Milestone parameter is required"
    echo "Usage: $0 <milestone> [--force|--dry-run]" >&2
    exit 2
fi

# Parse flags
if [[ "$FORCE" == "--dry-run" ]]; then
    DRY_RUN=true
    FORCE=""
fi

# Rate limit guard
rate_limit_guard || exit 2

echo ""
if [[ "$DRY_RUN" == true ]]; then
    log_info "DRY RUN: Validating milestone: $MILESTONE"
else
    log_info "Validating milestone: $MILESTONE"
fi
echo ""

# Verify milestone exists
MILESTONE_EXISTS=$(gh api "repos/:owner/:repo/milestones" --jq ".[] | select(.title == \"$MILESTONE\") | .title" 2>/dev/null || echo "")
if [[ -z "$MILESTONE_EXISTS" ]]; then
    log_error "Milestone '$MILESTONE' not found"
    echo ""
    echo "Action: Create milestone first:"
    echo "  /gh:milestone create $MILESTONE --due YYYY-MM-DD"
    exit 2
fi

# Check 1: P0 (critical) issues
log_info "Check 1: P0 Critical Issues"
P0_OPEN=$(gh issue list --milestone "$MILESTONE" --label "P0-critical" --state open --json number --jq '. | length' 2>/dev/null || echo "0")

if [[ $P0_OPEN -gt 0 ]]; then
    P0_ISSUES=$(gh issue list --milestone "$MILESTONE" --label "P0-critical" --state open --json number --jq '.[].number' | tr '\n' ' ')
    log_error "P0 critical issues still open: $P0_OPEN (#$P0_ISSUES)"
    ((VALIDATION_ERRORS++))
else
    log_success "All P0 critical issues closed"
fi
rate_limit_delay
echo ""

# Check 2: Parent issue completion
log_info "Check 2: Parent Issue Completion"
PARENTS=$(gh issue list --milestone "$MILESTONE" --json number,labels --jq '.[] | select(.labels[]?.name == "parent") | .number' 2>/dev/null || echo "")

if [[ -z "$PARENTS" ]]; then
    log_success "No parent issues in milestone"
else
    PARENT_COUNT=0
    INCOMPLETE_PARENTS=0

    for parent in $PARENTS; do
        ((PARENT_COUNT++))

        # Get node ID
        NODE_ID=$(gh api "repos/:owner/:repo/issues/$parent" --jq '.node_id' 2>/dev/null)

        # Query sub_issues_summary via GraphQL
        COMPLETION=$(gh api graphql -f query="query {
            node(id: \"$NODE_ID\") {
                ... on Issue {
                    subIssuesSummary {
                        percentCompleted
                        count
                        completedCount
                    }
                }
            }
        }" -H "GraphQL-Features: sub_issues" --jq '.data.node.subIssuesSummary.percentCompleted' 2>/dev/null || echo "0")

        if [[ "$COMPLETION" != "100" ]]; then
            CHILD_COUNT=$(gh api graphql -f query="query {
                node(id: \"$NODE_ID\") {
                    ... on Issue { subIssuesSummary { count completedCount } }
                }
            }" -H "GraphQL-Features: sub_issues" 2>/dev/null)

            TOTAL=$(echo "$CHILD_COUNT" | jq -r '.data.node.subIssuesSummary.count')
            COMPLETED=$(echo "$CHILD_COUNT" | jq -r '.data.node.subIssuesSummary.completedCount')

            log_error "Parent #$parent only $COMPLETION% complete ($COMPLETED/$TOTAL children)"
            ((VALIDATION_ERRORS++))
            ((INCOMPLETE_PARENTS++))
        fi

        rate_limit_delay
    done

    if [[ $INCOMPLETE_PARENTS -eq 0 ]]; then
        log_success "All $PARENT_COUNT parent issues 100% complete"
    fi
fi
echo ""

# Check 3: Blocking dependencies
log_info "Check 3: Blocking Dependencies"
MILESTONE_ISSUES=$(gh issue list --milestone "$MILESTONE" --state open --json number --jq '.[].number' 2>/dev/null || echo "")

if [[ -z "$MILESTONE_ISSUES" ]]; then
    log_success "No open issues in milestone"
else
    BLOCKED_COUNT=0

    for issue in $MILESTONE_ISSUES; do
        # Check blocked_by dependencies
        BLOCKERS=$(gh api "repos/:owner/:repo/issues/$issue/dependencies/blocked_by" --jq '. | length' 2>/dev/null || echo "0")

        if [[ $BLOCKERS -gt 0 ]]; then
            BLOCKER_NUMBERS=$(gh api "repos/:owner/:repo/issues/$issue/dependencies/blocked_by" --jq '.[].number' 2>/dev/null | tr '\n' ' ')
            log_error "Issue #$issue blocked by $BLOCKERS open issues (#$BLOCKER_NUMBERS)"
            ((VALIDATION_ERRORS++))
            ((BLOCKED_COUNT++))
        fi

        rate_limit_delay
    done

    if [[ $BLOCKED_COUNT -eq 0 ]]; then
        log_success "No blocking dependencies found"
    fi
fi
echo ""

# Check 4: Open PRs
log_info "Check 4: Open Pull Requests"
OPEN_PRS=$(gh pr list --search "milestone:\"$MILESTONE\"" --state open --json number --jq '. | length' 2>/dev/null || echo "0")

if [[ $OPEN_PRS -gt 0 ]]; then
    PR_NUMBERS=$(gh pr list --search "milestone:\"$MILESTONE\"" --state open --json number --jq '.[].number' | tr '\n' ' ')
    log_warning "Open PRs still exist: $OPEN_PRS (#$PR_NUMBERS)"
    ((VALIDATION_WARNINGS++))
    echo "  Note: PRs should be merged or explicitly deferred before closure"
else
    log_success "All PRs merged or no PRs in milestone"
fi
rate_limit_delay
echo ""

# Summary
echo "========================================="
echo "Validation Summary:"
echo "  Errors: $VALIDATION_ERRORS"
echo "  Warnings: $VALIDATION_WARNINGS"
echo "========================================="
echo ""

# Exit with status
if [[ $VALIDATION_ERRORS -gt 0 ]]; then
    if [[ "$FORCE" == "--force" ]]; then
        log_warning "Validation failed but --force specified, proceeding anyway"
        log_warning "This is NOT RECOMMENDED and may cause incomplete releases"
        exit 0
    elif [[ "$DRY_RUN" == true ]]; then
        log_error "DRY RUN: Validation failed: $VALIDATION_ERRORS blocking issues found"
        echo ""
        echo "Fix these issues before closing milestone."
        exit 1
    else
        log_error "Validation failed: $VALIDATION_ERRORS blocking issues found"
        echo ""
        echo "Recommendations:"
        echo "  - Close or defer P0 critical issues"
        echo "  - Complete all parent-child work (100% completion required)"
        echo "  - Resolve blocking dependencies"
        echo "  - Merge or defer open PRs"
        echo ""
        echo "Documentation:"
        echo "  - Milestone Closure: docs/contributing/GITHUB_PROJECTS.md#milestone-closure"
        echo "  - Issue Validation: .claude/commands/gh/_gh-reference.md#issue-validation-checklist"
        echo ""
        echo "Use --force to bypass validation (NOT RECOMMENDED)"
        exit 1
    fi
elif [[ $VALIDATION_WARNINGS -gt 0 ]]; then
    if [[ "$DRY_RUN" == true ]]; then
        log_warning "DRY RUN: Validation passed with $VALIDATION_WARNINGS warnings"
    else
        log_warning "Validation passed with $VALIDATION_WARNINGS warnings"
    fi
    log_success "Milestone ready for closure (address warnings if possible)"
    exit 0
else
    if [[ "$DRY_RUN" == true ]]; then
        log_success "DRY RUN: Validation passed: Milestone ready for closure"
    else
        log_success "Validation passed: Milestone ready for closure"
    fi
    exit 0
fi
