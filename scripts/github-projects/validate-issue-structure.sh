#!/usr/bin/env bash
# Validate issue structure and required fields
# Usage: ./validate-issue-structure.sh ISSUE_NUMBER [OPTIONS]

set -euo pipefail

# Script directory for sourcing libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Rate limit library in same directory

# Source rate limit library if available
if [[ -f "$SCRIPT_DIR/rate_limit.sh" ]]; then
    # shellcheck source=./rate_limit.sh
    source "$SCRIPT_DIR/rate_limit.sh"
fi

# Colors (if not already defined by rate_limit.sh)
if [[ -z "${COLOR_RED:-}" ]]; then
    readonly COLOR_RED='\033[0;31m'
    readonly COLOR_YELLOW='\033[1;33m'
    readonly COLOR_GREEN='\033[0;32m'
    readonly COLOR_BLUE='\033[0;34m'
    readonly COLOR_NC='\033[0m' # No Color
else
    # Color constants from rate_limit.sh, add BLUE
    readonly COLOR_BLUE='\033[0;34m'
fi

# Validation settings
REQUIRE_DOCUMENTATION=true
REQUIRE_ACCEPTANCE_CRITERIA=true
REQUIRE_MILESTONE=false
REQUIRE_PRIORITY=false
REQUIRE_COMPLEXITY=false
STRICT_MODE=false

# Usage information
usage() {
    cat <<EOF
Validate Issue Structure

Usage:
  $(basename "$0") ISSUE_NUMBER [OPTIONS]

Arguments:
  ISSUE_NUMBER             Issue number to validate

Options:
  --require-milestone      Require milestone assignment
  --require-priority       Require priority label (P0-P3)
  --require-complexity     Require complexity label
  --no-docs                Don't require documentation field
  --no-criteria            Don't require acceptance criteria
  --strict                 Enable all requirements (fail on any missing field)
  -h, --help               Show this help message

Examples:
  # Basic validation
  $(basename "$0") 142

  # Strict validation (all fields required)
  $(basename "$0") 142 --strict

  # Custom validation
  $(basename "$0") 142 --require-milestone --require-priority
EOF
    exit 0
}

# Logging functions
log_info() {
    echo -e "${COLOR_BLUE}ℹ${COLOR_NC} $*" >&2
}

log_success() {
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $*" >&2
}

log_warning() {
    echo -e "${COLOR_YELLOW}⚠${COLOR_NC} $*" >&2
}

log_error() {
    echo -e "${COLOR_RED}✗${COLOR_NC} $*" >&2
}

# Parse arguments
ISSUE_NUMBER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        --require-milestone)
            REQUIRE_MILESTONE=true
            shift
            ;;
        --require-priority)
            REQUIRE_PRIORITY=true
            shift
            ;;
        --require-complexity)
            REQUIRE_COMPLEXITY=true
            shift
            ;;
        --no-docs)
            REQUIRE_DOCUMENTATION=false
            shift
            ;;
        --no-criteria)
            REQUIRE_ACCEPTANCE_CRITERIA=false
            shift
            ;;
        --strict)
            STRICT_MODE=true
            REQUIRE_MILESTONE=true
            REQUIRE_PRIORITY=true
            REQUIRE_COMPLEXITY=true
            REQUIRE_DOCUMENTATION=true
            REQUIRE_ACCEPTANCE_CRITERIA=true
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

# Check rate limit if function available
if declare -f rate_limit_guard >/dev/null 2>&1; then
    rate_limit_guard || exit 1
fi

# Auto-detect repository
OWNER_REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null)
if [[ -z "$OWNER_REPO" ]]; then
    log_error "Could not detect repository. Run from repository directory."
    exit 1
fi

log_info "Validating issue #$ISSUE_NUMBER in $OWNER_REPO"

# Fetch issue details
ISSUE_JSON=$(gh issue view "$ISSUE_NUMBER" \
    --json number,title,body,state,labels,milestone,assignees \
    2>/dev/null)

if [[ -z "$ISSUE_JSON" ]]; then
    log_error "Could not fetch issue #$ISSUE_NUMBER"
    exit 1
fi

# Extract fields
TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
BODY=$(echo "$ISSUE_JSON" | jq -r '.body // ""')
STATE=$(echo "$ISSUE_JSON" | jq -r '.state')
MILESTONE=$(echo "$ISSUE_JSON" | jq -r '.milestone.title // ""')
LABELS=$(echo "$ISSUE_JSON" | jq -r '.labels[].name' | tr '\n' ',' | sed 's/,$//')

log_info "Issue: #$ISSUE_NUMBER - $TITLE"
log_info "State: $STATE"

# Validation results
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

# Validate title
if [[ -z "$TITLE" ]]; then
    log_error "FAIL: Title is empty"
    ((VALIDATION_ERRORS++))
else
    log_success "PASS: Title present"
fi

# Validate body
if [[ -z "$BODY" ]]; then
    log_warning "WARN: Issue body is empty"
    ((VALIDATION_WARNINGS++))
else
    log_success "PASS: Body present"
fi

# Validate Required Documentation field
if [[ "$REQUIRE_DOCUMENTATION" == "true" ]]; then
    if echo "$BODY" | grep -qi "^## Required Documentation"; then
        # Extract content AFTER "## Required Documentation" header (not the header itself)
        # Match exact section header, then get first non-empty line
        DOCS=$(echo "$BODY" | awk '/^## Required Documentation$/{getline; while(NF==0) getline; print; exit}' | xargs)

        # Check if documentation is explicitly marked as "None" (valid for bug fixes, etc.)
        if [[ -n "$DOCS" ]] && echo "$DOCS" | grep -qiE '^(None|N/A)(\s|\(|$)'; then
            log_success "PASS: Required Documentation explicitly marked as None (acceptable for bug fixes)"
        elif [[ -n "$DOCS" ]]; then
            # Extract documentation file names (both .md files and capitalized words without extension)
            # This handles: "ARCHITECTURE.md, SECURITY.md" and "GITHUB_WORKFLOWS.md, PRD.md"
            DOC_FILES_RAW=$(echo "$DOCS" | grep -oE '[A-Z][A-Za-z_0-9]*\.md|[A-Z][A-Z_]+')

            if [[ -n "$DOC_FILES_RAW" ]]; then
                log_success "PASS: Required Documentation field present and valid"

                # Convert newlines to spaces and clean up
                DOC_FILES=$(echo "$DOC_FILES_RAW" | tr '\n' ' ' | xargs)

                # Validate file existence
                MISSING_FILES=""
                FILES_CHECKED=0
                FILES_FOUND=0

                for doc in $DOC_FILES; do
                    FILES_CHECKED=$((FILES_CHECKED + 1))
                    FOUND=false

                    # Try common documentation locations
                    for base_path in "docs/guides" "docs/project" "docs/contributing" "docs"; do
                        # Try exact match first
                        if [[ -f "$base_path/$doc" ]]; then
                            log_success "  ✓ Found: $base_path/$doc"
                            FILES_FOUND=$((FILES_FOUND + 1))
                            FOUND=true
                            break
                        fi

                        # If doc doesn't end in .md, try adding .md extension
                        if [[ ! "$doc" =~ \.md$ ]] && [[ -f "$base_path/$doc.md" ]]; then
                            log_success "  ✓ Found: $base_path/$doc.md"
                            FILES_FOUND=$((FILES_FOUND + 1))
                            FOUND=true
                            break
                        fi
                    done

                    if [[ "$FOUND" == "false" ]]; then
                        MISSING_FILES="$MISSING_FILES $doc"
                        log_error "  ✗ Not found: $doc (checked docs/guides, docs/project, docs/contributing, docs)"
                        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
                    fi
                done

                # Summary of file validation
                if [[ $FILES_CHECKED -gt 0 ]]; then
                    if [[ -n "$MISSING_FILES" ]]; then
                        log_error "FAIL: $FILES_CHECKED file(s) checked, $FILES_FOUND found, missing:$MISSING_FILES"
                    else
                        log_success "PASS: All $FILES_CHECKED required documentation files exist"
                    fi
                fi
            else
                log_warning "WARN: Required Documentation field found but no valid docs listed (expected: ARCHITECTURE.md, SECURITY.md, etc.)"
                VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
            fi
        else
            log_warning "WARN: Required Documentation field found but no documentation listed on following line"
            VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
        fi
    else
        log_error "FAIL: Required Documentation field missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
fi

# Validate Acceptance Criteria
if [[ "$REQUIRE_ACCEPTANCE_CRITERIA" == "true" ]]; then
    if echo "$BODY" | grep -qi "Acceptance Criteria"; then
        # Check if criteria has actual content (not just the heading)
        CRITERIA=$(echo "$BODY" | sed -n '/Acceptance Criteria/,/^##/p' | tail -n +2)
        if [[ -n "$CRITERIA" ]] && [[ "$CRITERIA" != *"None"* ]]; then
            log_success "PASS: Acceptance Criteria present"
        else
            log_warning "WARN: Acceptance Criteria section exists but is empty"
            ((VALIDATION_WARNINGS++))
        fi
    else
        log_error "FAIL: Acceptance Criteria section missing"
        ((VALIDATION_ERRORS++))
    fi
fi

# Validate Milestone
if [[ "$REQUIRE_MILESTONE" == "true" ]]; then
    if [[ -n "$MILESTONE" ]]; then
        log_success "PASS: Milestone assigned ($MILESTONE)"
    else
        log_error "FAIL: Milestone not assigned"
        ((VALIDATION_ERRORS++))
    fi
fi

# Validate Priority label
if [[ "$REQUIRE_PRIORITY" == "true" ]]; then
    if echo "$LABELS" | grep -qE 'P[0-3]-(critical|high|medium|low)'; then
        PRIORITY=$(echo "$LABELS" | grep -oE 'P[0-3]-(critical|high|medium|low)')
        log_success "PASS: Priority label present ($PRIORITY)"
    else
        log_error "FAIL: Priority label (P0-P3) missing"
        ((VALIDATION_ERRORS++))
    fi
fi

# Validate Complexity label
if [[ "$REQUIRE_COMPLEXITY" == "true" ]]; then
    if echo "$LABELS" | grep -qE 'complexity/(XS|S|M|L|XL)'; then
        COMPLEXITY=$(echo "$LABELS" | grep -oE 'complexity/(XS|S|M|L|XL)')
        log_success "PASS: Complexity label present ($COMPLEXITY)"
    else
        log_error "FAIL: Complexity label missing"
        ((VALIDATION_ERRORS++))
    fi
fi

# Check for blockers (informational)
if echo "$BODY" | grep -qi "Blocked By:"; then
    BLOCKERS=$(echo "$BODY" | grep -i "Blocked By:" | sed 's/.*Blocked By:\s*//' | tr -d '\r')
    if [[ "$BLOCKERS" != *"None"* ]] && [[ -n "$BLOCKERS" ]]; then
        log_info "INFO: Issue has blockers: $BLOCKERS"
    fi
fi

# Validate dependencies if they exist
if echo "$BODY" | grep -qiE '#[0-9]+'; then
    REFERENCED_ISSUES=$(echo "$BODY" | grep -oE '#[0-9]+' | sort -u)
    log_info "INFO: References other issues: $(echo $REFERENCED_ISSUES | tr '\n' ' ')"
fi

# Summary
echo ""
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo "Issue: #$ISSUE_NUMBER"
echo "Errors: $VALIDATION_ERRORS"
echo "Warnings: $VALIDATION_WARNINGS"

if [[ $VALIDATION_ERRORS -eq 0 ]]; then
    if [[ $VALIDATION_WARNINGS -eq 0 ]]; then
        log_success "✓ Issue structure is VALID (no errors or warnings)"
        EXIT_CODE=0
    else
        log_warning "⚠ Issue structure is VALID with $VALIDATION_WARNINGS warning(s)"
        EXIT_CODE=0
    fi
else
    log_error "✗ Issue structure is INVALID ($VALIDATION_ERRORS error(s))"
    EXIT_CODE=1
fi

echo ""
echo "Recommendations:"
if [[ $VALIDATION_ERRORS -gt 0 ]] || [[ $VALIDATION_WARNINGS -gt 0 ]]; then
    echo "  - Edit issue via web UI: https://github.com/$OWNER_REPO/issues/$ISSUE_NUMBER"
    echo "  - Or use: gh issue edit $ISSUE_NUMBER"
    if [[ "$REQUIRE_DOCUMENTATION" == "true" ]] && echo "$BODY" | grep -qvi "Required Documentation"; then
        echo "  - Add 'Required Documentation: ARCHITECTURE.md, SECURITY.md' to issue body"
    fi
    if [[ "$REQUIRE_ACCEPTANCE_CRITERIA" == "true" ]] && echo "$BODY" | grep -qvi "Acceptance Criteria"; then
        echo "  - Add 'Acceptance Criteria' section with checkboxes"
    fi
    echo ""
    echo "Documentation:"
    echo "  - Issue Structure Guide: docs/contributing/GITHUB_PROJECTS.md#issue-structure"
    echo "  - Workflow Overview: docs/contributing/GITHUB_PROJECTS.md#workflow-overview"
    echo "  - Rate Limits: docs/guides/GITHUB_API_RATE_LIMITS.md"
    if [[ "$REQUIRE_MILESTONE" == "true" ]] && [[ -z "$MILESTONE" ]]; then
        echo "  - Assign milestone: gh issue edit $ISSUE_NUMBER --milestone vX.Y.Z"
    fi
    if [[ "$REQUIRE_PRIORITY" == "true" ]] && ! echo "$LABELS" | grep -qE 'P[0-3]-'; then
        echo "  - Add priority: gh issue edit $ISSUE_NUMBER --add-label P1-high"
    fi
    if [[ "$REQUIRE_COMPLEXITY" == "true" ]] && ! echo "$LABELS" | grep -qE 'complexity/'; then
        echo "  - Add complexity: gh issue edit $ISSUE_NUMBER --add-label complexity/M"
    fi
fi

# Show rate limit summary if function available
if declare -f rate_limit_summary >/dev/null 2>&1; then
    rate_limit_summary >&2
fi

exit $EXIT_CODE
