#!/usr/bin/env bash
#
# manage_issue_relationships.sh - GitHub Issue Relationship Manager
#
# Comprehensive tool for managing GitHub issue relationships including parent-child
# and blocking/blocked-by dependencies. Supports batch operations and automatic
# repository detection.
#
# Usage:
#   ./scripts/manage_issue_relationships.sh <subcommand> <args...> [OPTIONS]
#
# Subcommands:
#   set-parent       Set issues as children of parent (batch, overwrites existing parent)
#   remove-parent    Remove parent relationship from issue(s) (batch)
#   remove-child     Remove all child relationships from parent(s) (batch)
#   set-blocker      Set blocker for multiple issues (batch)
#   remove-blocker   Remove blocker from multiple issues (batch)
#   view             Display all relationships for issue(s) (batch)
#
# Options:
#   --owner OWNER    Repository owner (auto-detected if not provided)
#   --repo REPO      Repository name (auto-detected if not provided)
#   --help           Show this help message
#
# Examples:
#   # Set parent-child relationships (issue 67 is parent of 68, 69, 70)
#   ./scripts/manage_issue_relationships.sh set-parent 67 68 69 70
#
#   # Set parent (overwrites existing parent if any)
#   ./scripts/manage_issue_relationships.sh set-parent 99 68
#
#   # Remove parent from issue 68
#   ./scripts/manage_issue_relationships.sh remove-parent 68
#
#   # Remove parent from multiple issues
#   ./scripts/manage_issue_relationships.sh remove-parent 68 69 70
#
#   # Remove all children from parent issue 67
#   ./scripts/manage_issue_relationships.sh remove-child 67
#
#   # Remove all children from multiple parent issues
#   ./scripts/manage_issue_relationships.sh remove-child 67 99
#
#   # Set blocker (issue 67 blocks 68, 69, 70)
#   ./scripts/manage_issue_relationships.sh set-blocker 67 68 69 70
#
#   # Remove blocker (issue 67 no longer blocks 68, 69, 70)
#   ./scripts/manage_issue_relationships.sh remove-blocker 67 68 69 70
#
#   # Display all relationships for issue 67
#   ./scripts/manage_issue_relationships.sh view 67
#
#   # Display all relationships for multiple issues
#   ./scripts/manage_issue_relationships.sh view 67 68 69
#
#   # With explicit repository override
#   ./scripts/manage_issue_relationships.sh view 67 --owner jvlivonius --repo vsc-extension-scanner
#
# Prerequisites:
#   - gh CLI must be installed and authenticated
#   - Write access required for create/update/delete operations
#   - Read access sufficient for view operation
#
# Notes:
#   - Parent-child relationships use GitHub GraphQL API (sub_issues feature)
#   - Blocking dependencies use GitHub REST API
#   - Repository is auto-detected from current directory if not specified
#   - Use :owner/:repo placeholders for auto-detection (like gh issue create)
#
# Limitations:
#   - Pagination implemented: Supports >100 relationships automatically
#   - Rate limiting managed via rate_limit.sh library integration
#   - See docs/guides/GITHUB_API_RATE_LIMITS.md for API usage patterns
#
# Documentation:
#   - Workflow Guide: docs/contributing/GITHUB_PROJECTS.md#parent-child-relationships
#   - Rate Limiting: docs/guides/GITHUB_API_RATE_LIMITS.md
#   - Command Reference: .claude/commands/gh/projects.md
#

set -euo pipefail

# Script directory for sourcing libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source rate limit library if available
if [[ -f "$SCRIPT_DIR/rate_limit.sh" ]]; then
    source "$SCRIPT_DIR/rate_limit.sh"
else
    log_warning() {
        echo "[WARNING] $*" >&2
    }
    log_warning "rate_limit.sh not found - rate limiting disabled"
    log_warning "For better API management, ensure rate_limit.sh exists in $SCRIPT_DIR"

    # Define stub functions if rate limiting not available
    rate_limit_guard() { return 0; }
    rate_limit_delay() { return 0; }
    rate_limit_summary() { return 0; }
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables for repository override
OWNER=""
REPO=""
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
    cat << 'EOF'
GitHub Issue Relationship Manager

Usage:
  manage_issue_relationships.sh <subcommand> <args...> [OPTIONS]

Subcommands:
  set-parent <parent> <child1> [child2...]
      Set multiple issues as children of parent issue
      Overwrites existing parent if child already has one
      Example: ./manage_issue_relationships.sh set-parent 67 68 69 70

  remove-parent <issue1> [issue2...]
      Remove parent relationship from one or more issues
      Example: ./manage_issue_relationships.sh remove-parent 68
      Example: ./manage_issue_relationships.sh remove-parent 68 69 70

  remove-child <parent1> [parent2...]
      Remove all child relationships from one or more parent issues
      Example: ./manage_issue_relationships.sh remove-child 67
      Example: ./manage_issue_relationships.sh remove-child 67 99

  set-blocker <blocker> <blocked1> [blocked2...]
      Set blocker for multiple issues (blocker blocks all specified issues)
      Example: ./manage_issue_relationships.sh set-blocker 67 68 69 70

  remove-blocker <blocker> <blocked1> [blocked2...]
      Remove blocker from multiple issues
      Example: ./manage_issue_relationships.sh remove-blocker 67 68 69 70

  view <issue1> [issue2...]
      Display all relationships for one or more issues
      Example: ./manage_issue_relationships.sh view 67
      Example: ./manage_issue_relationships.sh view 67 68 69

Options:
  --owner OWNER    Repository owner (auto-detected if not provided)
  --repo REPO      Repository name (auto-detected if not provided)
  --dry-run        Preview changes without applying them
  --help           Show this help message

Repository Detection:
  If --owner and --repo are not provided, the script will attempt to detect
  the repository from the current directory (must be run from within a repo).
  This uses the same detection mechanism as gh CLI commands.

Permissions:
  - Write access required for: set-parent, remove-parent, remove-child,
    set-blocker, remove-blocker
  - Read access sufficient for: view

Examples:
  # Auto-detect repository
  ./manage_issue_relationships.sh set-parent 67 68 69 70
  ./manage_issue_relationships.sh view 67

  # Explicit repository
  ./manage_issue_relationships.sh view 67 --owner jvlivonius --repo vsc-extension-scanner

EOF
}

# Function to build API path based on whether explicit repo is set
gh_api_call() {
    if [[ -n "$OWNER" && -n "$REPO" ]]; then
        gh api "repos/$OWNER/$REPO/$1" "${@:2}"
    else
        gh api "repos/:owner/:repo/$1" "${@:2}"
    fi
}

# Dry-run wrapper for gh api graphql
gh_api_graphql_wrapped() {
    if [[ "$DRY_RUN" == "true" ]]; then
        # Return mock success response
        echo '{"data":{"node":{"number":1}}}'
        return 0
    else
        gh api graphql "$@"
    fi
}

# Dry-run wrapper for gh_api_call with POST
gh_api_call_post_wrapped() {
    local endpoint="$1"
    shift

    if [[ "$DRY_RUN" == "true" ]]; then
        # Return mock success response
        echo '{"number":1,"title":"Mock Issue"}'
        return 0
    else
        gh_api_call "$endpoint" -X POST "$@"
    fi
}

# Dry-run wrapper for gh_api_call with DELETE
gh_api_call_delete_wrapped() {
    local endpoint="$1"

    if [[ "$DRY_RUN" == "true" ]]; then
        # Return success (no output for DELETE)
        return 0
    else
        gh_api_call "$endpoint" -X DELETE
    fi
}

# Fetch all sub-issues for a parent with pagination support (GraphQL cursor-based)
fetch_all_sub_issues() {
    local issue_node="$1"
    local all_sub_issues=""
    local has_next_page="true"
    local cursor=""

    while [[ "$has_next_page" == "true" ]]; do
        local after_clause=""
        if [[ -n "$cursor" ]]; then
            after_clause=", after: \"$cursor\""
        fi

        local page_data
        page_data=$(gh api graphql -f query="query {
            node(id: \"$issue_node\") {
                ... on Issue {
                    subIssues(first: 100${after_clause}) {
                        nodes { number title state url }
                        pageInfo { hasNextPage endCursor }
                    }
                }
            }
        }" -H "GraphQL-Features: sub_issues" 2>/dev/null) || return 1

        # Extract sub-issues from this page
        local page_issues
        page_issues=$(echo "$page_data" | jq -r '.data.node.subIssues.nodes[] | "\(.number)|\(.title)|\(.state)|\(.url)"')

        if [[ -n "$page_issues" ]]; then
            if [[ -z "$all_sub_issues" ]]; then
                all_sub_issues="$page_issues"
            else
                all_sub_issues="${all_sub_issues}"$'\n'"${page_issues}"
            fi
        fi

        # Check pagination
        has_next_page=$(echo "$page_data" | jq -r '.data.node.subIssues.pageInfo.hasNextPage')
        cursor=$(echo "$page_data" | jq -r '.data.node.subIssues.pageInfo.endCursor')

        if [[ "$has_next_page" != "true" ]]; then
            break
        fi
    done

    echo "$all_sub_issues"
}

# Fetch all blocked_by dependencies with pagination support (REST page-based)
fetch_all_blocked_by() {
    local issue_number="$1"
    local all_blockers=""
    local page=1
    local per_page=100

    while true; do
        local page_data
        page_data=$(gh_api_call "issues/$issue_number/dependencies/blocked_by?page=$page&per_page=$per_page" 2>/dev/null)

        if [[ -z "$page_data" ]] || [[ "$page_data" == "[]" ]]; then
            break
        fi

        local page_blockers
        page_blockers=$(echo "$page_data" | jq -r '.[] | "\(.number)|\(.title)"')

        if [[ -z "$page_blockers" ]]; then
            break
        fi

        if [[ -z "$all_blockers" ]]; then
            all_blockers="$page_blockers"
        else
            all_blockers="${all_blockers}"$'\n'"${page_blockers}"
        fi

        # Check if we got less than per_page results (last page)
        local page_count
        page_count=$(echo "$page_data" | jq '. | length')
        if [[ "$page_count" -lt "$per_page" ]]; then
            break
        fi

        page=$((page + 1))
    done

    echo "$all_blockers"
}

# Fetch all blocking dependencies with pagination support (REST page-based)
fetch_all_blocking() {
    local issue_number="$1"
    local all_blocking=""
    local page=1
    local per_page=100

    while true; do
        local page_data
        page_data=$(gh_api_call "issues/$issue_number/dependencies/blocking?page=$page&per_page=$per_page" 2>/dev/null)

        if [[ -z "$page_data" ]] || [[ "$page_data" == "[]" ]]; then
            break
        fi

        local page_blocking
        page_blocking=$(echo "$page_data" | jq -r '.[] | "\(.number)|\(.title)"')

        if [[ -z "$page_blocking" ]]; then
            break
        fi

        if [[ -z "$all_blocking" ]]; then
            all_blocking="$page_blocking"
        else
            all_blocking="${all_blocking}"$'\n'"${page_blocking}"
        fi

        # Check if we got less than per_page results (last page)
        local page_count
        page_count=$(echo "$page_data" | jq '. | length')
        if [[ "$page_count" -lt "$per_page" ]]; then
            break
        fi

        page=$((page + 1))
    done

    echo "$all_blocking"
}

# Function to get issue node_id (for GraphQL)
get_issue_node_id() {
    local issue_number="$1"
    gh_api_call "issues/$issue_number" --jq '.node_id' 2>/dev/null
}

# Function to get issue id (for REST API)
get_issue_id() {
    local issue_number="$1"
    gh_api_call "issues/$issue_number" --jq '.id' 2>/dev/null
}

# Function to get issue field
get_issue_field() {
    local issue_number="$1"
    local jq_filter="$2"
    gh_api_call "issues/$issue_number" --jq "$jq_filter" 2>/dev/null
}

# Function to validate issue exists
validate_issue_exists() {
    local issue_number="$1"
    local result

    result=$(gh_api_call "issues/$issue_number" 2>&1)

    if ! echo "$result" | grep -q '"number"'; then
        log_error "Issue #$issue_number does not exist or is not accessible"
        return 1
    fi
    return 0
}

# Function to check permissions
check_permissions() {
    log_info "Checking repository permissions..."

    # Try to get repo info to verify access
    local repo_info
    if [[ -n "$OWNER" && -n "$REPO" ]]; then
        repo_info=$(gh api "repos/$OWNER/$REPO" 2>&1)
    else
        repo_info=$(gh api "repos/:owner/:repo" 2>&1)
    fi

    if ! echo "$repo_info" | grep -q '"id"'; then
        log_error "Cannot access repository or insufficient permissions"
        log_error "Make sure you are in a git repository or provide --owner and --repo"
        return 1
    fi

    # Check if user has push access
    local has_push
    has_push=$(echo "$repo_info" | jq -r '.permissions.push // false')

    if [[ "$has_push" != "true" ]]; then
        log_error "Insufficient permissions: Write access required"
        log_error "Current permissions: $(echo "$repo_info" | jq -r '.permissions')"
        return 1
    fi

    log_success "Permission check passed"
    return 0
}

# Function to show summary
show_summary() {
    local success_count="$1"
    local fail_count="$2"
    local skip_count="${3:-0}"

    echo ""
    echo "=== SUMMARY ==="
    echo "Successfully processed: $success_count"

    if [[ $skip_count -gt 0 ]]; then
        echo "Skipped: $skip_count"
    fi

    if [[ $fail_count -gt 0 ]]; then
        echo "Failed: $fail_count"
        exit 1
    fi
}

# Subcommand: set-parent
cmd_set_parent() {
    if [[ $# -lt 2 ]]; then
        log_error "set-parent requires at least 2 arguments: <parent> <child1> [child2...]"
        exit 1
    fi

    local parent_number="$1"
    shift
    local child_numbers=("$@")

    log_info "Setting parent-child relationships..."
    log_info "Parent Issue: #$parent_number"
    log_info "Child Issues: ${child_numbers[*]}"
    echo ""

    # Validate parent exists
    validate_issue_exists "$parent_number" || exit 1

    # Get parent node ID
    log_info "Getting parent node ID..."
    local parent_node
    parent_node=$(get_issue_node_id "$parent_number")

    if [[ -z "$parent_node" ]]; then
        log_error "Could not get node ID for parent issue #$parent_number"
        exit 1
    fi

    log_success "Parent #$parent_number node ID: $parent_node"
    echo ""

    # Process each child issue
    local success_count=0
    local fail_count=0
    local skip_count=0

    for child_number in "${child_numbers[@]}"; do
        log_info "Processing child issue #$child_number..."

        # Validate child exists
        if ! validate_issue_exists "$child_number"; then
            log_error "  ❌ Issue #$child_number does not exist"
            fail_count=$((fail_count + 1))
            continue
        fi

        # Get child node ID
        local child_node
        child_node=$(get_issue_node_id "$child_number")

        if [[ -z "$child_node" ]]; then
            log_error "  ❌ ERROR: Could not get node ID for issue #$child_number"
            fail_count=$((fail_count + 1))
            continue
        fi

        # Try to add sub-issue relationship using GraphQL
        local result
        result=$(gh_api_graphql_wrapped -f query="mutation {
            addSubIssue(input: {issueId: \"$parent_node\", subIssueId: \"$child_node\"}) {
                issue { number }
            }
        }" -H "GraphQL-Features: sub_issues" 2>&1) || true

        # Rate limit delay between API calls
        rate_limit_delay

        if echo "$result" | grep -q '"number"'; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_success "  ✅ [DRY-RUN] Would set #$child_number as sub-issue of #$parent_number"
            else
                log_success "  ✅ Successfully set #$child_number as sub-issue of #$parent_number"
            fi
            success_count=$((success_count + 1))
        elif echo "$result" | grep -q "duplicate sub-issues"; then
            log_warning "  ⚠️  Relationship already exists"
            skip_count=$((skip_count + 1))
        elif echo "$result" | grep -q "may only have one parent"; then
            # Child already has a parent - remove old parent and add new one
            log_info "  → Child #$child_number already has a parent, replacing..."

            # Get current parent
            local old_parent_url
            old_parent_url=$(get_issue_field "$child_number" '.parent_issue_url')

            if [[ -n "$old_parent_url" && "$old_parent_url" != "null" ]]; then
                local old_parent_number
                old_parent_number=$(echo "$old_parent_url" | grep -oE '[0-9]+$')
                log_info "  → Removing old parent #$old_parent_number..."

                local old_parent_node
                old_parent_node=$(get_issue_node_id "$old_parent_number")

                if [[ -n "$old_parent_node" ]]; then
                    # Remove old parent
                    local remove_result
                    remove_result=$(gh_api_graphql_wrapped -f query="mutation {
                        removeSubIssue(input: {issueId: \"$old_parent_node\", subIssueId: \"$child_node\"}) {
                            issue { number }
                        }
                    }" -H "GraphQL-Features: sub_issues" 2>&1) || true

                    if echo "$remove_result" | grep -q '"number"'; then
                        if [[ "$DRY_RUN" == "true" ]]; then
                            log_success "  → [DRY-RUN] Would remove old parent #$old_parent_number"
                        else
                            log_success "  → Removed old parent #$old_parent_number"
                        fi

                        # Now add the new parent
                        local add_result
                        add_result=$(gh_api_graphql_wrapped -f query="mutation {
                            addSubIssue(input: {issueId: \"$parent_node\", subIssueId: \"$child_node\"}) {
                                issue { number }
                            }
                        }" -H "GraphQL-Features: sub_issues" 2>&1) || true

                        if echo "$add_result" | grep -q '"number"'; then
                            if [[ "$DRY_RUN" == "true" ]]; then
                                log_success "  ✅ [DRY-RUN] Would set #$child_number as sub-issue of #$parent_number (replaced parent)"
                            else
                                log_success "  ✅ Successfully set #$child_number as sub-issue of #$parent_number (replaced parent)"
                            fi
                            success_count=$((success_count + 1))
                        else
                            log_error "  ❌ Failed to set new parent"
                            log_error "  Response: $add_result"
                            fail_count=$((fail_count + 1))
                        fi
                    else
                        log_error "  ❌ Failed to remove old parent"
                        log_error "  Response: $remove_result"
                        fail_count=$((fail_count + 1))
                    fi
                else
                    log_error "  ❌ Could not get node ID for old parent #$old_parent_number"
                    fail_count=$((fail_count + 1))
                fi
            else
                log_error "  ❌ Could not determine old parent"
                fail_count=$((fail_count + 1))
            fi
        else
            log_error "  ❌ ERROR: Failed to set relationship for #$child_number"
            log_error "  Response: $result"
            fail_count=$((fail_count + 1))
        fi
    done

    show_summary "$success_count" "$fail_count" "$skip_count"

    # Show rate limit usage
    rate_limit_summary

    echo ""
    echo "=== VERIFICATION ==="
    # Wait a moment for API to update (eventual consistency)
    sleep 2
    gh_api_call "issues/$parent_number" --jq '"Parent #" + (.number | tostring) + " now has " + (.sub_issues_summary.total | tostring) + " sub-issues"'
}

# Subcommand: remove-parent
cmd_remove_parent() {
    if [[ $# -lt 1 ]]; then
        log_error "remove-parent requires at least 1 argument: <issue> [<issue2> ...]"
        exit 1
    fi

    local issue_numbers=("$@")

    log_info "Removing parent relationships from ${#issue_numbers[@]} issue(s)..."
    echo ""

    local success_count=0
    local fail_count=0
    local skip_count=0

    for issue_number in "${issue_numbers[@]}"; do
        log_info "Processing issue #$issue_number..."

        # Validate issue exists
        if ! validate_issue_exists "$issue_number"; then
            log_warning "  ⚠️  Issue #$issue_number does not exist, skipping..."
            skip_count=$((skip_count + 1))
            continue
        fi

        # Get current parent
        local parent_url
        parent_url=$(get_issue_field "$issue_number" '.parent_issue_url')

        if [[ -z "$parent_url" || "$parent_url" == "null" ]]; then
            log_warning "  ⚠️  Issue #$issue_number has no parent relationship to remove"
            skip_count=$((skip_count + 1))
            continue
        fi

        # Extract parent number from URL
        local parent_number
        parent_number=$(echo "$parent_url" | grep -oE '[0-9]+$')

        log_info "  Current parent: #$parent_number"

        # Get node IDs
        local parent_node issue_node
        parent_node=$(get_issue_node_id "$parent_number")
        issue_node=$(get_issue_node_id "$issue_number")

        if [[ -z "$parent_node" || -z "$issue_node" ]]; then
            log_error "  ❌ Could not get node IDs for issues"
            fail_count=$((fail_count + 1))
            continue
        fi

        # Execute GraphQL mutation
        local result
        result=$(gh_api_graphql_wrapped -f query="mutation {
            removeSubIssue(input: {issueId: \"$parent_node\", subIssueId: \"$issue_node\"}) {
                issue { number }
            }
        }" -H "GraphQL-Features: sub_issues" 2>&1) || true

        # Rate limit delay between API calls
        rate_limit_delay

        if echo "$result" | grep -q '"number"'; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_success "  ✅ [DRY-RUN] Would remove parent #$parent_number from issue #$issue_number"
            else
                log_success "  ✅ Successfully removed parent #$parent_number from issue #$issue_number"
            fi
            success_count=$((success_count + 1))
        else
            log_error "  ❌ Failed to remove parent relationship"
            log_error "  Response: $result"
            fail_count=$((fail_count + 1))
        fi
    done

    show_summary "$success_count" "$fail_count" "$skip_count"

    # Show rate limit usage
    rate_limit_summary

    echo ""
    echo "=== VERIFICATION ==="
    # Wait a moment for API to update (eventual consistency)
    sleep 2
    echo "Checking that issues now have no parent..."
    for issue_number in "${issue_numbers[@]}"; do
        local new_parent
        new_parent=$(get_issue_field "$issue_number" '.parent_issue_url' 2>/dev/null || echo "")
        if [[ -z "$new_parent" || "$new_parent" == "null" ]]; then
            echo "  Issue #$issue_number: no parent"
        else
            echo "  Issue #$issue_number: still has parent"
        fi
    done
}

# Subcommand: remove-child
cmd_remove_child() {
    if [[ $# -lt 1 ]]; then
        log_error "remove-child requires at least 1 argument: <parent> [<parent2> ...]"
        exit 1
    fi

    local parent_numbers=("$@")

    log_info "Removing all child relationships from ${#parent_numbers[@]} parent issue(s)..."
    echo ""

    local total_success=0
    local total_fail=0
    local total_skip=0

    for parent_number in "${parent_numbers[@]}"; do
        log_info "Processing parent #$parent_number..."

        # Validate parent exists
        if ! validate_issue_exists "$parent_number"; then
            log_warning "  ⚠️  Issue #$parent_number does not exist, skipping..."
            total_skip=$((total_skip + 1))
            continue
        fi

        # Get parent node ID
        local parent_node
        parent_node=$(get_issue_node_id "$parent_number")

        if [[ -z "$parent_node" ]]; then
            log_error "  ❌ Could not get node ID for parent issue #$parent_number"
            total_fail=$((total_fail + 1))
            continue
        fi

        # Query all sub-issues using GraphQL
        local sub_issues
        sub_issues=$(gh api graphql -f query="query {
            node(id: \"$parent_node\") {
                ... on Issue {
                    subIssues(first: 100) {
                        nodes { number }
                    }
                }
            }
        }" -H "GraphQL-Features: sub_issues" --jq '.data.node.subIssues.nodes[].number' 2>&1) || true

        if [[ -z "$sub_issues" ]]; then
            log_warning "  ⚠️  Issue #$parent_number has no sub-issues to remove"
            total_skip=$((total_skip + 1))
            continue
        fi

        # Convert to array
        local child_numbers=()
        while IFS= read -r num; do
            child_numbers+=("$num")
        done <<< "$sub_issues"

        log_info "  Found ${#child_numbers[@]} sub-issues to remove"

        # Warn if pagination limit reached
        if [[ ${#child_numbers[@]} -eq 100 ]]; then
            log_warning "  ⚠️  Pagination limit reached (100 items). Parent may have more sub-issues not shown."
        fi

        # Remove each sub-issue
        for child_number in "${child_numbers[@]}"; do
            local child_node
            child_node=$(get_issue_node_id "$child_number")

            if [[ -z "$child_node" ]]; then
                log_error "    ❌ Could not get node ID for issue #$child_number"
                total_fail=$((total_fail + 1))
                continue
            fi

            local result
            result=$(gh_api_graphql_wrapped -f query="mutation {
                removeSubIssue(input: {issueId: \"$parent_node\", subIssueId: \"$child_node\"}) {
                    issue { number }
                }
            }" -H "GraphQL-Features: sub_issues" 2>&1) || true

            # Rate limit delay between API calls
            rate_limit_delay

            if echo "$result" | grep -q '"number"'; then
                if [[ "$DRY_RUN" == "true" ]]; then
                    log_success "    ✅ [DRY-RUN] Would remove sub-issue #$child_number"
                else
                    log_success "    ✅ Successfully removed sub-issue #$child_number"
                fi
                total_success=$((total_success + 1))
            else
                log_error "    ❌ Failed to remove sub-issue #$child_number"
                log_error "    Response: $result"
                total_fail=$((total_fail + 1))
            fi
        done

        echo ""
    done

    show_summary "$total_success" "$total_fail" "$total_skip"

    # Show rate limit usage
    rate_limit_summary

    echo ""
    echo "=== VERIFICATION ==="
    # Wait a moment for API to update (eventual consistency)
    sleep 2
    echo "Checking that parent issues now have no sub-issues..."
    for parent_number in "${parent_numbers[@]}"; do
        gh_api_call "issues/$parent_number" --jq '"  Parent #" + (.number | tostring) + ": " + (.sub_issues_summary.total | tostring) + " sub-issues"' 2>/dev/null || echo "  Parent #$parent_number: query failed"
    done
}

# Subcommand: set-blocker
cmd_set_blocker() {
    if [[ $# -lt 2 ]]; then
        log_error "set-blocker requires at least 2 arguments: <blocker> <blocked1> [blocked2...]"
        exit 1
    fi

    local blocker_number="$1"
    shift
    local blocked_numbers=("$@")

    log_info "Setting blocked-by relationships..."
    log_info "Blocker Issue: #$blocker_number"
    log_info "Blocked Issues: ${blocked_numbers[*]}"
    echo ""

    # Validate blocker exists
    validate_issue_exists "$blocker_number" || exit 1

    # Get blocker ID
    log_info "Getting blocker issue ID..."
    local blocker_id
    blocker_id=$(get_issue_id "$blocker_number")

    if [[ -z "$blocker_id" ]]; then
        log_error "Could not get ID for blocker issue #$blocker_number"
        exit 1
    fi

    log_success "Blocker #$blocker_number ID: $blocker_id"
    echo ""

    # Process each blocked issue
    local success_count=0
    local fail_count=0
    local skip_count=0

    for blocked_number in "${blocked_numbers[@]}"; do
        log_info "Processing blocked issue #$blocked_number..."

        # Validate blocked issue exists
        if ! validate_issue_exists "$blocked_number"; then
            log_error "  ❌ Issue #$blocked_number does not exist"
            fail_count=$((fail_count + 1))
            continue
        fi

        # Add blocked-by dependency
        local result
        result=$(gh_api_call_post_wrapped "issues/$blocked_number/dependencies/blocked_by" \
            -F issue_id="$blocker_id" 2>&1) || true

        # Rate limit delay between API calls
        rate_limit_delay

        if echo "$result" | grep -q '"number"'; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_success "  ✅ [DRY-RUN] Would set issue #$blocked_number blocked by #$blocker_number"
            else
                log_success "  ✅ Issue #$blocked_number now blocked by #$blocker_number"
            fi
            success_count=$((success_count + 1))
        elif echo "$result" | grep -qi "already exists\|duplicate\|already been taken"; then
            log_warning "  ⚠️  Relationship already exists: #$blocked_number is already blocked by #$blocker_number"
            skip_count=$((skip_count + 1))
        else
            log_error "  ❌ ERROR: Failed for issue #$blocked_number"
            log_error "  Response: $result"
            fail_count=$((fail_count + 1))
        fi
    done

    show_summary "$success_count" "$fail_count" "$skip_count"

    # Show rate limit usage
    rate_limit_summary

    echo ""
    echo "=== VERIFICATION ==="
    # Wait a moment for API to update (eventual consistency)
    sleep 2
    echo "Checking blocked issues..."
    for blocked_number in "${blocked_numbers[@]}"; do
        gh_api_call "issues/$blocked_number" --jq '"  Issue #\(.number): blocked_by=\(.issue_dependencies_summary.blocked_by)"' 2>/dev/null || true
    done
}

# Subcommand: remove-blocker
cmd_remove_blocker() {
    if [[ $# -lt 2 ]]; then
        log_error "remove-blocker requires at least 2 arguments: <blocker> <blocked1> [blocked2...]"
        exit 1
    fi

    local blocker_number="$1"
    shift
    local blocked_numbers=("$@")

    log_info "Removing blocked-by relationships..."
    log_info "Blocker Issue: #$blocker_number"
    log_info "Blocked Issues: ${blocked_numbers[*]}"
    echo ""

    # Validate blocker exists
    validate_issue_exists "$blocker_number" || exit 1

    # Get blocker ID
    log_info "Getting blocker issue ID..."
    local blocker_id
    blocker_id=$(get_issue_id "$blocker_number")

    if [[ -z "$blocker_id" ]]; then
        log_error "Could not get ID for blocker issue #$blocker_number"
        exit 1
    fi

    log_success "Blocker #$blocker_number ID: $blocker_id"
    echo ""

    # Process each blocked issue
    local success_count=0
    local fail_count=0
    local skip_count=0

    for blocked_number in "${blocked_numbers[@]}"; do
        log_info "Removing blocked-by relationship from issue #$blocked_number..."

        # First check if the relationship exists
        local existing_blockers
        existing_blockers=$(gh_api_call "issues/$blocked_number/dependencies/blocked_by?per_page=100" 2>/dev/null | jq -r '.[].id' 2>/dev/null || echo "")

        # Warn if pagination limit reached
        local blocker_count
        blocker_count=$(echo "$existing_blockers" | grep -c "^" || echo "0")
        if [[ "$blocker_count" -eq 100 ]]; then
            log_warning "  ⚠️  Pagination limit reached (100 items). Issue may have more blockers not checked."
        fi

        if ! echo "$existing_blockers" | grep -q "^${blocker_id}$"; then
            log_warning "  ⚠️  Relationship does not exist: #$blocked_number is not blocked by #$blocker_number"
            skip_count=$((skip_count + 1))
            continue
        fi

        # Remove the dependency using DELETE endpoint
        local result
        result=$(gh_api_call_delete_wrapped "issues/$blocked_number/dependencies/blocked_by/$blocker_id" 2>&1) || true

        # Rate limit delay between API calls
        rate_limit_delay

        # Check if successful (DELETE returns full issue object on success, or nothing in dry-run)
        if [[ "$DRY_RUN" == "true" ]] || echo "$result" | grep -q '"number"'; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_success "  ✅ [DRY-RUN] Would remove blocker #$blocker_number from issue #$blocked_number"
            else
                local blocked_count
                blocked_count=$(echo "$result" | jq -r '.issue_dependencies_summary.blocked_by // 0')
                log_success "  ✅ Successfully removed (now has $blocked_count blocked-by dependencies)"
            fi
            success_count=$((success_count + 1))
        else
            log_error "  ❌ ERROR: Failed to remove dependency from #$blocked_number"
            log_error "  Response: $result"
            fail_count=$((fail_count + 1))
        fi
    done

    show_summary "$success_count" "$fail_count" "$skip_count"

    # Show rate limit usage
    rate_limit_summary

    echo ""
    echo "=== VERIFICATION ==="
    # Wait a moment for API to update (eventual consistency)
    sleep 2
    echo "Checking that blocked issues are now clean..."
    for blocked_number in "${blocked_numbers[@]}"; do
        gh_api_call "issues/$blocked_number" --jq '"  Issue #\(.number): blocked_by=\(.issue_dependencies_summary.blocked_by)"' 2>/dev/null || true
    done
}

# Subcommand: view
cmd_view() {
    if [[ $# -lt 1 ]]; then
        log_error "view requires at least 1 argument: <issue> [<issue2> ...]"
        exit 1
    fi

    local issue_numbers=("$@")
    local is_first=true

    # Get repository name once
    local repo_name
    if [[ -n "$OWNER" && -n "$REPO" ]]; then
        repo_name="$OWNER/$REPO"
    else
        repo_name=$(gh api "repos/:owner/:repo" --jq '"\(.owner.login)/\(.name)"' 2>/dev/null)
    fi

    for issue_number in "${issue_numbers[@]}"; do
        # Add separator between issues (except for first issue)
        if [[ "$is_first" == "true" ]]; then
            is_first=false
        else
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
        fi

        # Validate issue exists
        if ! validate_issue_exists "$issue_number"; then
            log_warning "⚠️  Issue #$issue_number does not exist, skipping..."
            continue
        fi

        # Get issue node_id for GraphQL queries
        local issue_node
        issue_node=$(get_issue_node_id "$issue_number")

        if [[ -z "$issue_node" ]]; then
            log_warning "⚠️  Could not get node ID for issue #$issue_number, skipping..."
            continue
        fi

        echo "=== Issue #$issue_number Relationships ==="
        echo "Repository: $repo_name"
        echo ""

        # Query parent and sub-issues via GraphQL
        local parent_data
        parent_data=$(gh api graphql -f query="query {
            node(id: \"$issue_node\") {
                ... on Issue {
                    parent { number title url }
                    subIssuesSummary { total completed percentCompleted }
                    subIssues(first: 100) {
                        nodes { number title state url }
                    }
                }
            }
        }" -H "GraphQL-Features: sub_issues" 2>/dev/null) || true

        # Display parent
        local parent_number
        parent_number=$(echo "$parent_data" | jq -r '.data.node.parent.number // empty')

        if [[ -n "$parent_number" ]]; then
            local parent_title
            parent_title=$(echo "$parent_data" | jq -r '.data.node.parent.title')
            echo "Parent Issue:"
            echo "  #$parent_number - $parent_title"
            echo ""
        fi

        # Display sub-issues
        local total_subs
        total_subs=$(echo "$parent_data" | jq -r '.data.node.subIssuesSummary.total // 0')

        if [[ "$total_subs" -gt 0 ]]; then
            local completed_subs
            completed_subs=$(echo "$parent_data" | jq -r '.data.node.subIssuesSummary.completed')
            echo "Sub-Issues ($total_subs total, $completed_subs completed):"

            # Use pagination if total exceeds 100
            if [[ "$total_subs" -gt 100 ]]; then
                log_info "  ℹ️  Fetching all $total_subs sub-issues with pagination..."
                local all_subs
                all_subs=$(fetch_all_sub_issues "$issue_node")

                if [[ -n "$all_subs" ]]; then
                    echo "$all_subs" | while IFS='|' read -r num title state url; do
                        if [[ "$state" == "closed" ]]; then
                            echo "  #$num - $title ✓"
                        else
                            echo "  #$num - $title"
                        fi
                    done
                fi
            else
                # Use existing single-page query for ≤100 items
                echo "$parent_data" | jq -r '.data.node.subIssues.nodes[] |
                    "  #\(.number) - \(.title)" + (if .state == "closed" then " ✓" else "" end)'
            fi
            echo ""
        fi

        # Query blocked-by dependencies via REST API with pagination
        local blocked_by_raw
        blocked_by_raw=$(fetch_all_blocked_by "$issue_number")

        if [[ -n "$blocked_by_raw" ]]; then
            local blocked_count
            blocked_count=$(echo "$blocked_by_raw" | grep -c "^" || echo "0")
            echo "Blocked By ($blocked_count):"

            if [[ "$blocked_count" -gt 100 ]]; then
                log_info "  ℹ️  Fetched all $blocked_count dependencies with pagination"
            fi

            echo "$blocked_by_raw" | while IFS='|' read -r num title; do
                echo "  #$num - $title"
            done
            echo ""
        fi

        # Query blocking dependencies via REST API with pagination
        local blocking_raw
        blocking_raw=$(fetch_all_blocking "$issue_number")

        if [[ -n "$blocking_raw" ]]; then
            local blocking_count
            blocking_count=$(echo "$blocking_raw" | grep -c "^" || echo "0")
            echo "Blocking ($blocking_count):"

            if [[ "$blocking_count" -gt 100 ]]; then
                log_info "  ℹ️  Fetched all $blocking_count dependencies with pagination"
            fi

            echo "$blocking_raw" | while IFS='|' read -r num title; do
                echo "  #$num - $title"
            done
            echo ""
        fi

        # Show message if no relationships
        if [[ -z "$parent_number" && "$total_subs" -eq 0 && -z "$blocked_by_raw" && -z "$blocking_raw" ]]; then
            echo "No relationships found."
        fi
    done
}

# Main script logic
main() {
    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "gh CLI is not installed. Please install it first:"
        log_error "https://cli.github.com/"
        exit 1
    fi

    # Check if gh is authenticated
    if ! gh auth status &> /dev/null; then
        log_error "gh CLI is not authenticated. Please run 'gh auth login' first."
        exit 1
    fi

    # Check rate limit before executing operations
    rate_limit_guard || exit 1

    # Parse subcommand
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi

    local subcommand="$1"
    shift

    # Check for help flag
    if [[ "$subcommand" == "--help" || "$subcommand" == "-h" ]]; then
        usage
        exit 0
    fi

    # Collect positional arguments and flags
    local args=()
    while [[ $# -gt 0 ]]; do
        case $1 in
            --owner)
                OWNER="$2"
                shift 2
                ;;
            --repo)
                REPO="$2"
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
                args+=("$1")
                shift
                ;;
        esac
    done

    # Show dry-run mode notification
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "🔍 DRY-RUN MODE: No changes will be applied"
        echo ""
    fi

    # Check permissions for write operations
    case "$subcommand" in
        set-parent|remove-parent|remove-child|set-blocker|remove-blocker)
            check_permissions || exit 1
            echo ""
            ;;
    esac

    # Dispatch to subcommand
    case "$subcommand" in
        set-parent)
            cmd_set_parent "${args[@]}"
            ;;
        remove-parent)
            cmd_remove_parent "${args[@]}"
            ;;
        remove-child)
            cmd_remove_child "${args[@]}"
            ;;
        set-blocker)
            cmd_set_blocker "${args[@]}"
            ;;
        remove-blocker)
            cmd_remove_blocker "${args[@]}"
            ;;
        view)
            cmd_view "${args[@]}"
            ;;
        *)
            log_error "Unknown subcommand: $subcommand"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main
main "$@"
