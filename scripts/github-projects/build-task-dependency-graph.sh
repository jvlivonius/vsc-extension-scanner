#!/usr/bin/env bash
#
# build-task-dependency-graph.sh - Build dependency graph and topological sort
#
# Purpose: Given a list of issue numbers, query their blocking dependencies and
#          return a topologically sorted list respecting implementation order.
#
# Usage:
#   ./build-task-dependency-graph.sh <issue1> <issue2> <issue3> ...
#
# Example:
#   ./build-task-dependency-graph.sh 1005 1006 1007 1008 1009
#   Output: 1005 1006 1007 1008 1009 (in dependency order)
#
# Algorithm:
#   1. For each issue, query blocking dependencies (blocked_by)
#   2. Build adjacency list: task → [tasks it blocks]
#   3. Perform topological sort (Kahn's algorithm)
#   4. Detect cycles (error if found)
#   5. Return sorted list
#
# Exit Codes:
#   0 - Success, sorted list printed to stdout
#   1 - Cycle detected or other error
#

set -euo pipefail

# Script directory for sourcing libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source rate limit library if available
if [[ -f "$SCRIPT_DIR/rate_limit.sh" ]]; then
    source "$SCRIPT_DIR/rate_limit.sh"
else
    # Define stub functions if rate limiting not available
    rate_limit_guard() { return 0; }
    rate_limit_delay() { return 0; }
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
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
Build Task Dependency Graph

Usage:
  build-task-dependency-graph.sh <issue1> [issue2 issue3 ...]

Description:
  Builds a dependency graph from blocking relationships and returns
  topologically sorted list of issues respecting implementation order.

Examples:
  # Sort 5 tasks by dependencies
  ./build-task-dependency-graph.sh 1005 1006 1007 1008 1009

  # Sort with explicit repository
  ./build-task-dependency-graph.sh 142 143 144 --owner jvlivonius --repo vsc-extension-scanner

Options:
  --owner OWNER    Repository owner (auto-detected if not provided)
  --repo REPO      Repository name (auto-detected if not provided)
  --help           Show this help message

Algorithm:
  Uses Kahn's algorithm for topological sort:
  1. Build in-degree map (count of dependencies per task)
  2. Start with tasks having in-degree 0 (no dependencies)
  3. Process queue, removing edges and adding newly freed tasks
  4. If all tasks processed → success, otherwise → cycle detected

EOF
}

# Global variables for repository override
OWNER=""
REPO=""

# Function to build API path based on whether explicit repo is set
gh_api_call() {
    if [[ -n "$OWNER" && -n "$REPO" ]]; then
        gh api "repos/$OWNER/$REPO/$1" "${@:2}"
    else
        gh api "repos/:owner/:repo/$1" "${@:2}"
    fi
}

# Fetch all blocked_by dependencies for an issue
fetch_blocked_by() {
    local issue_number="$1"
    local page=1
    local per_page=100
    local all_blockers=""

    while true; do
        local page_data
        page_data=$(gh_api_call "issues/$issue_number/dependencies/blocked_by?page=$page&per_page=$per_page" 2>/dev/null) || true

        if [[ -z "$page_data" ]] || [[ "$page_data" == "[]" ]]; then
            break
        fi

        local page_blockers
        page_blockers=$(echo "$page_data" | jq -r '.[].number' 2>/dev/null || echo "")

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
        page_count=$(echo "$page_data" | jq '. | length' 2>/dev/null || echo "0")
        if [[ "$page_count" -lt "$per_page" ]]; then
            break
        fi

        page=$((page + 1))
        rate_limit_delay
    done

    echo "$all_blockers"
}

# Build dependency graph
build_dependency_graph() {
    local issues=("$@")

    log_info "Building dependency graph for ${#issues[@]} issues..."

    # Declare associative arrays for graph structure
    declare -gA adj_list        # task -> space-separated list of tasks it blocks
    declare -gA in_degree       # task -> count of dependencies (blocked_by count)
    declare -gA issue_set       # Set of all issues for quick lookup

    # Initialize all issues in the set
    for issue in "${issues[@]}"; do
        issue_set[$issue]=1
        adj_list[$issue]=""
        in_degree[$issue]=0
    done

    # Query dependencies for each issue
    for issue in "${issues[@]}"; do
        log_info "  Querying dependencies for #$issue..."

        local blockers
        blockers=$(fetch_blocked_by "$issue")

        if [[ -n "$blockers" ]]; then
            # Count blockers that are in our issue set
            local blocker_count=0
            while IFS= read -r blocker; do
                if [[ -n "${issue_set[$blocker]:-}" ]]; then
                    # This blocker is in our set, so it blocks current issue
                    adj_list[$blocker]="${adj_list[$blocker]} $issue"
                    blocker_count=$((blocker_count + 1))
                    log_info "    #$blocker blocks #$issue"
                fi
            done <<< "$blockers"

            in_degree[$issue]=$blocker_count
        else
            log_info "    No dependencies (can start immediately)"
        fi

        rate_limit_delay
    done

    log_success "Dependency graph built successfully"
}

# Topological sort using Kahn's algorithm
topological_sort() {
    local issues=("$@")

    log_info "Performing topological sort..."

    # Queue of tasks with no dependencies (in-degree 0)
    local queue=()
    local sorted=()
    local processed_count=0

    # Initialize queue with tasks that have no dependencies
    for issue in "${issues[@]}"; do
        if [[ ${in_degree[$issue]} -eq 0 ]]; then
            queue+=("$issue")
            log_info "  Initial task (no dependencies): #$issue"
        fi
    done

    if [[ ${#queue[@]} -eq 0 ]]; then
        log_error "No tasks with zero dependencies - cycle detected!"
        return 1
    fi

    # Process queue
    while [[ ${#queue[@]} -gt 0 ]]; do
        # Pop first element from queue
        local current="${queue[0]}"
        queue=("${queue[@]:1}")

        sorted+=("$current")
        processed_count=$((processed_count + 1))

        log_info "  Processing #$current (${processed_count}/${#issues[@]})"

        # For each task that current blocks, decrease in-degree
        if [[ -n "${adj_list[$current]}" ]]; then
            for blocked in ${adj_list[$current]}; do
                in_degree[$blocked]=$((in_degree[$blocked] - 1))

                # If in-degree becomes 0, add to queue
                if [[ ${in_degree[$blocked]} -eq 0 ]]; then
                    queue+=("$blocked")
                    log_info "    #$blocked is now ready (dependencies satisfied)"
                fi
            done
        fi
    done

    # Check if all tasks were processed
    if [[ $processed_count -ne ${#issues[@]} ]]; then
        log_error "Cycle detected! Only processed $processed_count of ${#issues[@]} tasks"
        log_error ""
        log_error "Tasks not processed (involved in cycle):"
        for issue in "${issues[@]}"; do
            if [[ ${in_degree[$issue]} -gt 0 ]]; then
                log_error "  #$issue (has ${in_degree[$issue]} unresolved dependencies)"
            fi
        done
        return 1
    fi

    log_success "Topological sort complete"

    # Print sorted list to stdout
    echo "${sorted[@]}"
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

    # Parse arguments
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi

    local issues=()
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
            --help|-h)
                usage
                exit 0
                ;;
            *)
                issues+=("$1")
                shift
                ;;
        esac
    done

    if [[ ${#issues[@]} -eq 0 ]]; then
        log_error "No issue numbers provided"
        usage
        exit 1
    fi

    log_info "Input issues: ${issues[*]}"
    echo "" >&2

    # Build dependency graph
    build_dependency_graph "${issues[@]}"
    echo "" >&2

    # Perform topological sort
    topological_sort "${issues[@]}"
}

# Run main
main "$@"
