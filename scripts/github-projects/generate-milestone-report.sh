#!/usr/bin/env bash
# Generate comprehensive milestone progress report
# Usage: ./generate-milestone-report.sh MILESTONE [OPTIONS]

set -euo pipefail

# Script directory for sourcing libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$(dirname "$SCRIPT_DIR")/lib"

# Source rate limit library if available
if [[ -f "$LIB_DIR/rate_limit.sh" ]]; then
    # shellcheck source=../lib/rate_limit.sh
    source "$LIB_DIR/rate_limit.sh"
fi

# Colors
readonly COLOR_RED='\033[0;31m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_NC='\033[0m' # No Color

# Output format
OUTPUT_FORMAT="markdown"  # markdown or json
SHOW_BLOCKERS=true
SHOW_DEPENDENCIES=true
SHOW_PROGRESS=true

# Usage information
usage() {
    cat <<EOF
Generate Milestone Progress Report

Usage:
  $(basename "$0") MILESTONE [OPTIONS]

Arguments:
  MILESTONE                Milestone name (e.g., v3.8.0)

Options:
  --format FORMAT          Output format: markdown (default), json
  --no-blockers            Don't include blocked issues section
  --no-dependencies        Don't include dependency chain analysis
  --no-progress            Don't include progress statistics
  --output FILE            Save report to file (default: stdout)
  -h, --help               Show this help message

Examples:
  # Basic report
  $(basename "$0") v3.8.0

  # JSON output to file
  $(basename "$0") v3.8.0 --format json --output milestone-report.json

  # Minimal report (only issue counts)
  $(basename "$0") v3.8.0 --no-blockers --no-dependencies
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
MILESTONE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --no-blockers)
            SHOW_BLOCKERS=false
            shift
            ;;
        --no-dependencies)
            SHOW_DEPENDENCIES=false
            shift
            ;;
        --no-progress)
            SHOW_PROGRESS=false
            shift
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            if [[ -z "$MILESTONE" ]]; then
                MILESTONE="$1"
                shift
            else
                log_error "Unknown argument: $1"
                usage
            fi
            ;;
    esac
done

# Validate arguments
if [[ -z "$MILESTONE" ]]; then
    log_error "Milestone name is required"
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

log_info "Generating report for milestone '$MILESTONE' in $OWNER_REPO"

# Fetch all issues for milestone
log_info "Fetching milestone issues..."
ISSUES_JSON=$(gh issue list \
    --milestone "$MILESTONE" \
    --state all \
    --limit 1000 \
    --json number,title,state,labels,assignees,createdAt,closedAt,url \
    2>/dev/null)

if [[ -z "$ISSUES_JSON" ]] || [[ "$ISSUES_JSON" == "[]" ]]; then
    log_warning "No issues found for milestone '$MILESTONE'"
    exit 0
fi

# Calculate statistics
TOTAL_ISSUES=$(echo "$ISSUES_JSON" | jq 'length')
OPEN_ISSUES=$(echo "$ISSUES_JSON" | jq '[.[] | select(.state == "OPEN")] | length')
CLOSED_ISSUES=$(echo "$ISSUES_JSON" | jq '[.[] | select(.state == "CLOSED")] | length')
COMPLETION_PCT=$((CLOSED_ISSUES * 100 / TOTAL_ISSUES))

# Count by type
FEATURES=$(echo "$ISSUES_JSON" | jq '[.[] | select(.labels[].name == "feature")] | length')
BUGS=$(echo "$ISSUES_JSON" | jq '[.[] | select(.labels[].name == "bug" or .labels[].name == "bugfix")] | length')
TASKS=$(echo "$ISSUES_JSON" | jq '[.[] | select(.labels[].name == "task")] | length')

# Count by priority
P0=$(echo "$ISSUES_JSON" | jq '[.[] | select(.labels[].name == "P0-critical")] | length')
P1=$(echo "$ISSUES_JSON" | jq '[.[] | select(.labels[].name == "P1-high")] | length')
P2=$(echo "$ISSUES_JSON" | jq '[.[] | select(.labels[].name == "P2-medium")] | length')
P3=$(echo "$ISSUES_JSON" | jq '[.[] | select(.labels[].name == "P3-low")] | length')

log_success "Found $TOTAL_ISSUES issues ($CLOSED_ISSUES closed, $OPEN_ISSUES open)"

# Generate report based on format
generate_markdown_report() {
    cat <<EOF
# Milestone Report: $MILESTONE

**Repository:** $OWNER_REPO
**Generated:** $(date '+%Y-%m-%d %H:%M:%S')

---

## Progress Summary

- **Completion:** $COMPLETION_PCT% ($CLOSED_ISSUES/$TOTAL_ISSUES issues)
- **Open:** $OPEN_ISSUES issues
- **Closed:** $CLOSED_ISSUES issues

\`\`\`
[${'█' | head -c $((COMPLETION_PCT / 5))}${'░' | head -c $((20 - COMPLETION_PCT / 5))}] $COMPLETION_PCT%
\`\`\`

---

## Issue Breakdown

### By Type
- **Features:** $FEATURES
- **Bugs:** $BUGS
- **Tasks:** $TASKS
- **Other:** $((TOTAL_ISSUES - FEATURES - BUGS - TASKS))

### By Priority
- **P0 (Critical):** $P0
- **P1 (High):** $P1
- **P2 (Medium):** $P2
- **P3 (Low):** $P3
- **Unprioritized:** $((TOTAL_ISSUES - P0 - P1 - P2 - P3))

---

## Open Issues

EOF

    # List open issues grouped by priority
    echo "$ISSUES_JSON" | jq -r '
        [.[] | select(.state == "OPEN")] |
        sort_by(.labels[].name | select(startswith("P"))) |
        .[] | "- #\(.number): \(.title)"
    ' || echo "No open issues"

    if [[ "$SHOW_BLOCKERS" == "true" ]]; then
        cat <<EOF

---

## Blocked Issues

EOF
        # Find blocked issues (would need to query dependencies API for each issue)
        echo "_Note: Dependency checking requires individual API calls per issue._"
        echo "_Use GitHub web UI or scripts/manage_issue_relationships.sh to view blockers._"
    fi

    if [[ "$SHOW_DEPENDENCIES" == "true" ]]; then
        cat <<EOF

---

## Dependency Chain Analysis

EOF
        echo "_Note: Full dependency chain analysis requires graph traversal._"
        echo "_Use scripts/manage_issue_relationships.sh view <issue> for details._"
    fi

    cat <<EOF

---

## Recently Closed

EOF

    echo "$ISSUES_JSON" | jq -r '
        [.[] | select(.state == "CLOSED")] |
        sort_by(.closedAt) | reverse |
        limit(10; .[]) | "- #\(.number): \(.title) (closed \(.closedAt | fromdateiso8601 | strftime("%Y-%m-%d")))"
    ' || echo "No closed issues"

    cat <<EOF

---

## Report Actions

- View milestone: https://github.com/$OWNER_REPO/milestone/$(gh api repos/$OWNER_REPO/milestones --jq ".[] | select(.title==\"$MILESTONE\") | .number")
- List all issues: \`gh issue list --milestone "$MILESTONE" --state all\`
- View blockers: \`./scripts/manage_issue_relationships.sh view <issue-number>\`

EOF
}

generate_json_report() {
    jq -n \
        --arg milestone "$MILESTONE" \
        --arg repo "$OWNER_REPO" \
        --arg timestamp "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
        --argjson total "$TOTAL_ISSUES" \
        --argjson open "$OPEN_ISSUES" \
        --argjson closed "$CLOSED_ISSUES" \
        --argjson completion "$COMPLETION_PCT" \
        --argjson features "$FEATURES" \
        --argjson bugs "$BUGS" \
        --argjson tasks "$TASKS" \
        --argjson p0 "$P0" \
        --argjson p1 "$P1" \
        --argjson p2 "$P2" \
        --argjson p3 "$P3" \
        --argjson issues "$ISSUES_JSON" \
        '{
            milestone: $milestone,
            repository: $repo,
            generated_at: $timestamp,
            progress: {
                total: $total,
                open: $open,
                closed: $closed,
                completion_percentage: $completion
            },
            breakdown: {
                by_type: {
                    features: $features,
                    bugs: $bugs,
                    tasks: $tasks,
                    other: ($total - $features - $bugs - $tasks)
                },
                by_priority: {
                    critical: $p0,
                    high: $p1,
                    medium: $p2,
                    low: $p3,
                    unprioritized: ($total - $p0 - $p1 - $p2 - $p3)
                }
            },
            issues: $issues
        }'
}

# Generate and output report
if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    REPORT=$(generate_json_report)
else
    REPORT=$(generate_markdown_report)
fi

if [[ -n "$OUTPUT_FILE" ]]; then
    echo "$REPORT" > "$OUTPUT_FILE"
    log_success "Report saved to $OUTPUT_FILE"
else
    echo "$REPORT"
fi

# Show rate limit summary if function available
if declare -f rate_limit_summary >/dev/null 2>&1; then
    rate_limit_summary >&2
fi
