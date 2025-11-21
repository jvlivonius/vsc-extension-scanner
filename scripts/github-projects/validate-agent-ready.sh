#!/usr/bin/env bash
#
# validate-agent-ready.sh - Comprehensive validation before agent implementation
#
# Validates that an issue is ready for /gh:implement-issue by checking:
# - Issue structure (via validate-issue-structure.sh)
# - All dependencies are closed
# - Parent-child relationships exist in GitHub API (if applicable)
# - GitHub native dependencies match issue body text
# - Acceptance criteria are present
# - Required labels are set (priority, complexity)
#
# Usage:
#   ./scripts/github-projects/validate-agent-ready.sh ISSUE_NUMBER [OPTIONS]
#
# Options:
#   --skip-structure    Skip basic structure validation
#   --skip-deps         Skip dependency validation
#   --skip-labels       Skip label validation
#   -h, --help          Show this help message
#
# Exit codes:
#   0 - Issue is ready for agent implementation
#   1 - Issue is not ready (validation errors found)
#
# Examples:
#   # Full validation
#   ./scripts/github-projects/validate-agent-ready.sh 142
#
#   # Skip structure check (if already validated)
#   ./scripts/github-projects/validate-agent-ready.sh 142 --skip-structure

set -euo pipefail

# Script directory for sourcing libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
readonly COLOR_RED='\033[0;31m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_NC='\033[0m' # No Color

# Validation settings
SKIP_STRUCTURE=false
SKIP_DEPS=false
SKIP_LABELS=false
FEATURE_MODE=false  # Set to true when validating a feature (epic with sub-tasks)

# Logging functions
log_info() {
    echo -e "${COLOR_BLUE}ℹ${COLOR_NC} $*"
}

log_success() {
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $*"
}

log_warning() {
    echo -e "${COLOR_YELLOW}⚠${COLOR_NC} $*"
}

log_error() {
    echo -e "${COLOR_RED}✗${COLOR_NC} $*"
}

# Usage information
usage() {
    cat <<EOF
Validate Issue Agent-Ready Status

Usage:
  $(basename "$0") ISSUE_NUMBER [OPTIONS]

Arguments:
  ISSUE_NUMBER             Issue number to validate

Options:
  --skip-structure         Skip basic structure validation
  --skip-deps              Skip dependency validation
  --skip-labels            Skip label validation
  --feature-mode           Validate as feature (epic with sub-tasks)
  -h, --help               Show this help message

Examples:
  # Full validation (single task)
  $(basename "$0") 142

  # Validate feature (epic with sub-tasks)
  $(basename "$0") 1004 --feature-mode

  # Skip structure check
  $(basename "$0") 142 --skip-structure

EOF
    exit 0
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
ISSUE_NUMBER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        --skip-structure)
            SKIP_STRUCTURE=true
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --skip-labels)
            SKIP_LABELS=true
            shift
            ;;
        --feature-mode)
            FEATURE_MODE=true
            shift
            ;;
        *)
            if [[ -z "$ISSUE_NUMBER" ]]; then
                ISSUE_NUMBER="$1"
                shift
            else
                log_error "Unknown argument: $1"
                usage
            fi
            ;;
    esac
done

# Validate arguments
if [[ -z "$ISSUE_NUMBER" ]]; then
    log_error "Issue number is required"
    usage
fi

# Validation results
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

log_info "Validating issue #$ISSUE_NUMBER for agent implementation..."
echo ""

# 1. Validate issue structure (if not skipped)
if [[ "$SKIP_STRUCTURE" == "false" ]]; then
    log_info "[1/6] Checking issue structure..."

    if [[ -x "$SCRIPT_DIR/validate-issue-structure.sh" ]]; then
        # Capture output to variable to avoid pipefail issues with grep -q
        STRUCTURE_OUTPUT=$("$SCRIPT_DIR/validate-issue-structure.sh" "$ISSUE_NUMBER" --require-milestone --require-priority --require-complexity 2>&1)
        if echo "$STRUCTURE_OUTPUT" | grep -q "VALID"; then
            log_success "Issue structure validation passed"
        else
            log_error "Issue structure validation failed"
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
    else
        log_warning "validate-issue-structure.sh not found, skipping structure check"
        VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
    fi
else
    log_info "[1/6] Skipping structure validation (--skip-structure)"
fi
echo ""

# 2. Fetch issue details
log_info "[2/6] Fetching issue details..."
ISSUE_JSON=$(gh issue view "$ISSUE_NUMBER" --json body,state,labels,milestone 2>/dev/null)

if [[ -z "$ISSUE_JSON" ]]; then
    log_error "Could not fetch issue #$ISSUE_NUMBER"
    exit 1
fi

BODY=$(echo "$ISSUE_JSON" | jq -r '.body // ""')
STATE=$(echo "$ISSUE_JSON" | jq -r '.state')
LABELS=$(echo "$ISSUE_JSON" | jq -r '.labels[].name' | tr '\n' ',' | sed 's/,$//')
MILESTONE=$(echo "$ISSUE_JSON" | jq -r '.milestone.title // ""')

log_success "Issue fetched successfully (state: $STATE)"
echo ""

# 2.5. Feature mode: Fetch and validate sub-tasks
if [[ "$FEATURE_MODE" == "true" ]]; then
    log_info "[2.5/6] Validating feature with sub-tasks..."

    # Query parent-child relationships
    if [[ -x "$SCRIPT_DIR/manage-issue-relationships.sh" ]]; then
        RELATIONSHIP_DATA=$("$SCRIPT_DIR/manage-issue-relationships.sh" view "$ISSUE_NUMBER" 2>&1)

        # Extract sub-issue count
        SUB_ISSUES_COUNT=$(echo "$RELATIONSHIP_DATA" | grep -A1 "Sub-Issues" | grep "total" | grep -oE "[0-9]+" | head -1 || echo "0")

        if [[ "$SUB_ISSUES_COUNT" -eq 0 ]]; then
            log_error "Feature mode enabled but issue #$ISSUE_NUMBER has no sub-tasks"
            log_info "Either this is not a feature, or sub-tasks haven't been created yet"
            ((VALIDATION_ERRORS++))
        else
            log_success "Feature has $SUB_ISSUES_COUNT sub-task(s)"

            # Extract sub-issue numbers
            SUB_ISSUES=$(echo "$RELATIONSHIP_DATA" | grep -A100 "Sub-Issues" | grep -oE "#[0-9]+" | grep -oE "[0-9]+" || echo "")

            if [[ -n "$SUB_ISSUES" ]]; then
                log_info "Sub-tasks: $(echo $SUB_ISSUES | tr ' ' ',')"
            fi
        fi
    else
        log_error "manage-issue-relationships.sh not found, cannot validate feature relationships"
        ((VALIDATION_ERRORS++))
    fi
    echo ""
fi

# 3. Validate all dependencies are closed (if not skipped)
if [[ "$SKIP_DEPS" == "false" ]]; then
    log_info "[3/6] Checking dependencies..."

    BLOCKED_BY=$(parse_blocked_by "$BODY")

    if [[ -n "$BLOCKED_BY" ]]; then
        deps_ok=true
        for dep in $BLOCKED_BY; do
            if DEP_STATE=$(gh issue view "$dep" --json state 2>/dev/null | jq -r '.state'); then
                if [[ "$DEP_STATE" != "CLOSED" ]]; then
                    log_error "Dependency #$dep is $DEP_STATE (must be CLOSED)"
                    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
                    deps_ok=false
                fi
            else
                log_error "Dependency issue #$dep does not exist"
                VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
                deps_ok=false
            fi
        done

        if [[ "$deps_ok" == "true" ]]; then
            log_success "All ${BLOCKED_BY//[[:space:]]/} dependencies are closed"
        fi
    else
        log_success "No blocking dependencies"
    fi
else
    log_info "[3/6] Skipping dependency validation (--skip-deps)"
fi
echo ""

# 4. Validate GitHub native dependencies match issue body
log_info "[4/6] Checking GitHub dependency API consistency..."

if [[ -n "$BLOCKED_BY" ]]; then
    # Get dependencies from GitHub API
    BLOCKED_BY_API=$(gh api "repos/:owner/:repo/issues/$ISSUE_NUMBER/dependencies/blocked_by" 2>/dev/null | jq -r '.[].number' | tr '\n' ' ' || echo "")

    missing_in_api=""
    for dep in $BLOCKED_BY; do
        if ! echo "$BLOCKED_BY_API" | grep -qw "$dep"; then
            missing_in_api="$missing_in_api #$dep"
        fi
    done

    if [[ -n "$missing_in_api" ]]; then
        log_warning "Dependencies documented but not set in GitHub API:$missing_in_api"
        log_info "To fix, run: ./scripts/github-projects/manage-issue-relationships.sh set-blocker <blocker> $ISSUE_NUMBER"
        VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
    else
        log_success "GitHub dependency API matches issue body"
    fi
else
    log_success "No dependencies to check"
fi
echo ""

# 5. Validate acceptance criteria are present
log_info "[5/6] Checking acceptance criteria..."

if echo "$BODY" | grep -qi "Acceptance Criteria"; then
    # Check if criteria has actual content (not just the heading)
    CRITERIA=$(echo "$BODY" | sed -n '/Acceptance Criteria/,/^##/p' | tail -n +2)
    if [[ -n "$CRITERIA" ]] && [[ "$CRITERIA" != *"None"* ]]; then
        log_success "Acceptance criteria present"
    else
        log_warning "Acceptance Criteria section exists but appears empty"
        VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
    fi
else
    log_error "Acceptance Criteria section missing"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi
echo ""

# 6. Validate required labels (if not skipped)
if [[ "$SKIP_LABELS" == "false" ]]; then
    log_info "[6/6] Checking required labels..."

    labels_ok=true

    # Check priority label
    if echo "$LABELS" | grep -qE 'P[0-3]-(critical|high|medium|low)'; then
        PRIORITY=$(echo "$LABELS" | grep -oE 'P[0-3]-(critical|high|medium|low)')
        log_success "Priority label present: $PRIORITY"
    else
        log_error "Priority label (P0-P3) missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        labels_ok=false
    fi

    # Check complexity label
    if echo "$LABELS" | grep -qE 'complexity/(XS|S|M|L|XL)'; then
        COMPLEXITY=$(echo "$LABELS" | grep -oE 'complexity/(XS|S|M|L|XL)')
        log_success "Complexity label present: $COMPLEXITY"
    else
        log_error "Complexity label missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        labels_ok=false
    fi

    # Check type label
    if echo "$LABELS" | grep -qE '(feature|task|bugfix|hotfix)'; then
        TYPE=$(echo "$LABELS" | grep -oE '(feature|task|bugfix|hotfix)' | head -1)
        log_success "Type label present: $TYPE"
    else
        log_error "Type label (feature/task/bugfix/hotfix) missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        labels_ok=false
    fi
else
    log_info "[6/6] Skipping label validation (--skip-labels)"
fi
echo ""

# Summary
echo "========================================="
echo "Agent-Ready Validation Summary"
echo "========================================="
echo "Issue: #$ISSUE_NUMBER"
if [[ "$FEATURE_MODE" == "true" ]] && [[ -n "$SUB_ISSUES_COUNT" ]] && [[ "$SUB_ISSUES_COUNT" -gt 0 ]]; then
    echo "Type: FEATURE (Epic with $SUB_ISSUES_COUNT sub-task(s))"
    if [[ -n "$SUB_ISSUES" ]]; then
        echo "Sub-tasks: $(echo $SUB_ISSUES | tr ' ' ',')"
    fi
else
    echo "Type: SINGLE TASK"
fi
echo "State: $STATE"
if [[ -n "$MILESTONE" ]]; then
    echo "Milestone: $MILESTONE"
fi
echo "Errors: $VALIDATION_ERRORS"
echo "Warnings: $VALIDATION_WARNINGS"
echo ""

if [[ $VALIDATION_ERRORS -eq 0 ]]; then
    if [[ $VALIDATION_WARNINGS -eq 0 ]]; then
        log_success "✓ Issue #$ISSUE_NUMBER is READY for agent implementation"
        echo ""
        echo "To implement:"
        echo "  /gh:implement-issue $ISSUE_NUMBER"
        EXIT_CODE=0
    else
        log_warning "⚠ Issue #$ISSUE_NUMBER is READY with $VALIDATION_WARNINGS warning(s)"
        echo ""
        echo "Consider addressing warnings before implementation:"
        echo "  /gh:implement-issue $ISSUE_NUMBER"
        EXIT_CODE=0
    fi
else
    log_error "✗ Issue #$ISSUE_NUMBER is NOT READY ($VALIDATION_ERRORS error(s))"
    echo ""
    echo "Fix errors before attempting implementation"
    EXIT_CODE=1
fi

exit $EXIT_CODE
