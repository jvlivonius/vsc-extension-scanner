#!/usr/bin/env bash
#
# create_issue.sh - GitHub Issue Creation Helper
#
# Standardized CLI wrapper around `gh issue create` with project-aware defaults
# and smart label synchronization for GitHub Projects V2 integration.
#
# Usage:
#   ./scripts/create_issue.sh --type TYPE --title TITLE --body BODY [OPTIONS]
#
# Required Arguments:
#   --type TYPE              Issue type: feature, task, bugfix, hotfix, release
#   --title TITLE            Issue title (will be prefixed with [TYPE])
#   --body BODY              Issue body/description
#
# Optional Arguments:
#   --milestone MILESTONE    Target milestone (optional, must exist if provided)
#   --assignee USER          Assignee (default: @me)
#   --priority PRIORITY      Priority: Critical, High, Medium, Low (maps to P0-P3 labels)
#   --complexity SIZE        Complexity: XS, S, M, L, XL (maps to complexity/* labels)
#   --labels LABELS          Comma-separated additional labels
#   --project PROJECT        Project title (default: "VS Code Extension Scanner Development")
#   --template FILE          Path to template file (optional)
#   --help                   Show this help message
#
# Examples:
#   # Create feature with all options
#   ./scripts/create_issue.sh \
#     --type feature \
#     --title "Add CSV export" \
#     --body "Export scan results as CSV format" \
#     --milestone v5.0.3 \
#     --priority High \
#     --complexity M \
#     --template .github/ISSUE_TEMPLATE/feature.yml
#
#   # Create bugfix with minimal options
#   ./scripts/create_issue.sh \
#     --type bugfix \
#     --title "Fix cache corruption" \
#     --body "Cache gets corrupted on network errors" \
#     --priority Critical
#
#   # Create task without milestone
#   ./scripts/create_issue.sh \
#     --type task \
#     --title "Implement CSV formatter class" \
#     --body "Create CSVExporter class" \
#     --complexity S \
#     --labels "good first issue,documentation"
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ASSIGNEE="@me"
PROJECT_TITLE="VS Code Extension Scanner Development"
PRIORITY=""
COMPLEXITY=""
ADDITIONAL_LABELS=""
TEMPLATE=""

# Required arguments (will be validated)
ISSUE_TYPE=""
TITLE=""
BODY=""
MILESTONE=""

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
GitHub Issue Creation Helper

Usage:
  $(basename "$0") --type TYPE --title TITLE --body BODY [OPTIONS]

Required Arguments:
  --type TYPE              Issue type: feature, task, bugfix, hotfix, release
  --title TITLE            Issue title (will be prefixed with [TYPE])
  --body BODY              Issue body/description

Optional Arguments:
  --milestone MILESTONE    Target milestone (optional, must exist if provided)
  --assignee USER          Assignee (default: @me)
  --priority PRIORITY      Priority: Critical, High, Medium, Low (maps to P0-P3 labels)
  --complexity SIZE        Complexity: XS, S, M, L, XL (maps to complexity/* labels)
  --labels LABELS          Comma-separated additional labels
  --project PROJECT        Project title (default: "VS Code Extension Scanner Development")
  --template FILE          Path to template file (optional)
  --help                   Show this help message

Examples:
  # Create feature with high priority
  $(basename "$0") \\
    --type feature \\
    --title "Add CSV export" \\
    --body "Export scan results as CSV format" \\
    --milestone v5.0.3 \\
    --priority High \\
    --complexity M

  # Create critical bugfix without milestone
  $(basename "$0") \\
    --type bugfix \\
    --title "Fix cache corruption" \\
    --body "Cache gets corrupted on network errors" \\
    --priority Critical

EOF
}

# Function to validate issue type
validate_type() {
    local type="$1"
    case "$type" in
        feature|task|bugfix|hotfix|release)
            return 0
            ;;
        *)
            log_error "Invalid issue type: $type"
            log_error "Valid types: feature, task, bugfix, hotfix, release"
            return 1
            ;;
    esac
}

# Function to normalize priority (convert to proper case)
normalize_priority() {
    local priority="$1"
    # Convert to lowercase for comparison
    local priority_lower=$(echo "$priority" | tr '[:upper:]' '[:lower:]')

    case "$priority_lower" in
        critical) echo "Critical" ;;
        high)     echo "High" ;;
        medium)   echo "Medium" ;;
        low)      echo "Low" ;;
        *)        echo "" ;;  # Invalid, return empty
    esac
}

# Function to validate priority
validate_priority() {
    local priority="$1"
    local normalized=$(normalize_priority "$priority")

    if [[ -z "$normalized" ]]; then
        log_error "Invalid priority: $priority"
        log_error "Valid priorities: Critical, High, Medium, Low (case-insensitive)"
        return 1
    fi

    return 0
}

# Function to normalize complexity (convert to uppercase)
normalize_complexity() {
    local complexity="$1"
    # Convert to uppercase
    local complexity_upper=$(echo "$complexity" | tr '[:lower:]' '[:upper:]')

    case "$complexity_upper" in
        XS|S|M|L|XL) echo "$complexity_upper" ;;
        *)           echo "" ;;  # Invalid, return empty
    esac
}

# Function to validate complexity
validate_complexity() {
    local complexity="$1"
    local normalized=$(normalize_complexity "$complexity")

    if [[ -z "$normalized" ]]; then
        log_error "Invalid complexity: $complexity"
        log_error "Valid complexities: XS, S, M, L, XL (case-insensitive)"
        return 1
    fi

    return 0
}

# Function to map priority to label
priority_to_label() {
    local priority="$1"
    local normalized=$(normalize_priority "$priority")

    case "$normalized" in
        Critical) echo "P0-critical" ;;
        High)     echo "P1-high" ;;
        Medium)   echo "P2-medium" ;;
        Low)      echo "P3-low" ;;
    esac
}

# Function to map complexity to label
complexity_to_label() {
    local complexity="$1"
    local normalized=$(normalize_complexity "$complexity")
    echo "complexity/$normalized"
}

# Function to validate milestone exists
validate_milestone() {
    local milestone="$1"

    # Skip validation if milestone is empty
    if [[ -z "$milestone" ]]; then
        return 0
    fi

    log_info "Validating milestone: $milestone"

    if ! gh api "repos/:owner/:repo/milestones" --jq ".[] | select(.title == \"$milestone\") | .title" | grep -q "$milestone"; then
        log_error "Milestone '$milestone' does not exist"
        log_error "Available milestones:"
        gh api "repos/:owner/:repo/milestones" --jq '.[] | "  - \(.title) (\(.state))"'
        return 1
    fi

    log_success "Milestone validated: $milestone"
    return 0
}

# Function to validate template file
validate_template() {
    local template="$1"

    if [[ -z "$template" ]]; then
        return 0  # No template specified, skip validation
    fi

    log_info "Validating template: $template"

    if [[ ! -f "$template" ]]; then
        log_error "Template file not found: $template"
        return 1
    fi

    log_success "Template validated: $template"
    return 0
}

# Function to get project ID by title
get_project_id() {
    local project_title="$1"

    log_info "Looking up project: $project_title" >&2

    local project_info
    project_info=$(gh project list --owner @me --format json 2>&1 | jq -r ".projects[] | select(.title == \"$project_title\") | .number")

    if [[ -z "$project_info" ]]; then
        log_warning "Project '$project_title' not found" >&2
        log_warning "Issue will be created without project assignment" >&2
        echo ""
        return 0
    fi

    log_success "Project found: #$project_info" >&2
    echo "$project_info"
    return 0
}

# Function to build title with prefix
build_title() {
    local type="$1"
    local title="$2"

    local type_upper
    type_upper=$(echo "$type" | tr '[:lower:]' '[:upper:]')

    echo "[$type_upper] $title"
}

# Function to build label list
build_labels() {
    local type="$1"
    local priority="$2"
    local complexity="$3"
    local additional="$4"

    local labels=()

    # Add type label
    labels+=("$type")

    # Add priority label (will be added in step 2)
    if [[ -n "$priority" ]]; then
        local priority_label
        priority_label=$(priority_to_label "$priority")
        labels+=("$priority_label")
    fi

    # Add complexity label (will be added in step 2)
    if [[ -n "$complexity" ]]; then
        local complexity_label
        complexity_label=$(complexity_to_label "$complexity")
        labels+=("$complexity_label")
    fi

    # Add additional labels
    if [[ -n "$additional" ]]; then
        IFS=',' read -ra ADDR <<< "$additional"
        for label in "${ADDR[@]}"; do
            # Trim whitespace
            label=$(echo "$label" | xargs)
            labels+=("$label")
        done
    fi

    # Join with commas
    local IFS=','
    echo "${labels[*]}"
}

# Function to separate type labels from priority/complexity labels
separate_labels() {
    local all_labels="$1"
    local label_type="$2"  # "type" or "sync"

    local labels=()
    IFS=',' read -ra ADDR <<< "$all_labels"

    for label in "${ADDR[@]}"; do
        label=$(echo "$label" | xargs)

        if [[ "$label_type" == "type" ]]; then
            # Type labels: issue type and additional labels (not P* or complexity/*)
            if [[ ! "$label" =~ ^P[0-3]- ]] && [[ ! "$label" =~ ^complexity/ ]]; then
                labels+=("$label")
            fi
        else
            # Sync labels: priority and complexity labels
            if [[ "$label" =~ ^P[0-3]- ]] || [[ "$label" =~ ^complexity/ ]]; then
                labels+=("$label")
            fi
        fi
    done

    # Join with commas
    local IFS=','
    echo "${labels[*]}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            ISSUE_TYPE="$2"
            shift 2
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --body)
            BODY="$2"
            shift 2
            ;;
        --milestone)
            MILESTONE="$2"
            shift 2
            ;;
        --assignee)
            ASSIGNEE="$2"
            shift 2
            ;;
        --priority)
            PRIORITY="$2"
            shift 2
            ;;
        --complexity)
            COMPLEXITY="$2"
            shift 2
            ;;
        --labels)
            ADDITIONAL_LABELS="$2"
            shift 2
            ;;
        --project)
            PROJECT_TITLE="$2"
            shift 2
            ;;
        --template)
            TEMPLATE="$2"
            shift 2
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

# Validate required arguments
if [[ -z "$ISSUE_TYPE" ]]; then
    log_error "Missing required argument: --type"
    usage
    exit 1
fi

if [[ -z "$TITLE" ]]; then
    log_error "Missing required argument: --title"
    usage
    exit 1
fi

if [[ -z "$BODY" ]]; then
    log_error "Missing required argument: --body"
    usage
    exit 1
fi

# Validate arguments
validate_type "$ISSUE_TYPE" || exit 1

if [[ -n "$PRIORITY" ]]; then
    validate_priority "$PRIORITY" || exit 1
fi

if [[ -n "$COMPLEXITY" ]]; then
    validate_complexity "$COMPLEXITY" || exit 1
fi

validate_milestone "$MILESTONE" || exit 1
validate_template "$TEMPLATE" || exit 1

# Build components
FULL_TITLE=$(build_title "$ISSUE_TYPE" "$TITLE")
ALL_LABELS=$(build_labels "$ISSUE_TYPE" "$PRIORITY" "$COMPLEXITY" "$ADDITIONAL_LABELS")
TYPE_LABELS=$(separate_labels "$ALL_LABELS" "type")
SYNC_LABELS=$(separate_labels "$ALL_LABELS" "sync")

# Get project ID (optional, may be empty)
PROJECT_ID=$(get_project_id "$PROJECT_TITLE")

log_info "Creating issue..."
log_info "  Type: $ISSUE_TYPE"
log_info "  Title: $FULL_TITLE"
if [[ -n "$MILESTONE" ]]; then
    log_info "  Milestone: $MILESTONE"
else
    log_info "  Milestone: (none)"
fi
log_info "  Assignee: $ASSIGNEE"
log_info "  Type Labels: $TYPE_LABELS"
if [[ -n "$SYNC_LABELS" ]]; then
    log_info "  Sync Labels (added after creation): $SYNC_LABELS"
fi
if [[ -n "$PROJECT_ID" ]]; then
    log_info "  Project: $PROJECT_TITLE (#$PROJECT_ID)"
fi

# Build gh issue create command
GH_CMD=(gh issue create)
GH_CMD+=(--title "$FULL_TITLE")
GH_CMD+=(--body "$BODY")
if [[ -n "$MILESTONE" ]]; then
    GH_CMD+=(--milestone "$MILESTONE")
fi
GH_CMD+=(--assignee "$ASSIGNEE")

if [[ -n "$TYPE_LABELS" ]]; then
    GH_CMD+=(--label "$TYPE_LABELS")
fi

if [[ -n "$TEMPLATE" ]]; then
    GH_CMD+=(--template "$TEMPLATE")
fi

# Add project by title if available
if [[ -n "$PROJECT_ID" ]]; then
    GH_CMD+=(--project "$PROJECT_TITLE")
fi

# Step 1: Create issue with type labels and project assignment
log_info "Step 1: Creating issue with type labels and project assignment..."
ISSUE_URL=$("${GH_CMD[@]}")

if [[ -z "$ISSUE_URL" ]]; then
    log_error "Failed to create issue"
    exit 1
fi

log_success "Issue created: $ISSUE_URL"

# Extract issue number from URL
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')

# Step 2: Add priority/complexity labels to trigger auto-sync
# Note: GitHub auto-add is instantaneous, no wait needed
if [[ -n "$SYNC_LABELS" ]]; then
    log_info "Step 2: Adding priority/complexity labels to trigger auto-sync..."

    IFS=',' read -ra LABEL_ARRAY <<< "$SYNC_LABELS"
    for label in "${LABEL_ARRAY[@]}"; do
        label=$(echo "$label" | xargs)
        log_info "  Adding label: $label"
        gh issue edit "$ISSUE_NUMBER" --add-label "$label"
    done

    log_success "Labels added. GitHub Actions will sync to project fields."
fi

log_success "✓ Issue created successfully!"
log_success "  URL: $ISSUE_URL"
log_success "  Number: #$ISSUE_NUMBER"
if [[ -n "$PROJECT_ID" ]]; then
    log_success "  Project: $PROJECT_TITLE (#$PROJECT_ID)"
fi

if [[ -n "$SYNC_LABELS" ]]; then
    log_info "Note: Label sync to project fields should complete within 5-10 seconds"
fi
