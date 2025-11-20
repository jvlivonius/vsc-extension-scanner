#!/usr/bin/env bash
# Rate limit monitoring and backoff helpers for GitHub API operations
# Source this file in scripts that make GitHub API calls

# Colors for output
readonly COLOR_RED='\033[0;31m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_NC='\033[0m' # No Color

# Rate limit thresholds
readonly RATE_LIMIT_WARNING_THRESHOLD=100
readonly RATE_LIMIT_CRITICAL_THRESHOLD=20

# Check GitHub API rate limit status
# Returns: 0 if OK, 1 if warning, 2 if critical
check_rate_limit() {
    local remaining
    local limit
    local reset_time
    local current_time
    local minutes_until_reset

    # Fetch rate limit info
    local rate_info
    rate_info=$(gh api rate_limit --jq '.rate' 2>/dev/null)

    if [[ $? -ne 0 ]]; then
        echo -e "${COLOR_YELLOW}⚠️  Could not fetch rate limit information${COLOR_NC}" >&2
        return 0  # Don't block operations if check fails
    fi

    remaining=$(echo "$rate_info" | jq -r '.remaining')
    limit=$(echo "$rate_info" | jq -r '.limit')
    reset_time=$(echo "$rate_info" | jq -r '.reset')
    current_time=$(date +%s)
    minutes_until_reset=$(( (reset_time - current_time) / 60 ))

    # Check thresholds
    if [[ $remaining -lt $RATE_LIMIT_CRITICAL_THRESHOLD ]]; then
        echo -e "${COLOR_RED}🚨 CRITICAL: Only $remaining/$limit API requests remaining!${COLOR_NC}" >&2
        echo -e "${COLOR_RED}   Rate limit resets in $minutes_until_reset minutes${COLOR_NC}" >&2
        echo -e "${COLOR_RED}   Consider waiting or using a different token${COLOR_NC}" >&2
        return 2
    elif [[ $remaining -lt $RATE_LIMIT_WARNING_THRESHOLD ]]; then
        echo -e "${COLOR_YELLOW}⚠️  WARNING: $remaining/$limit API requests remaining${COLOR_NC}" >&2
        echo -e "${COLOR_YELLOW}   Rate limit resets in $minutes_until_reset minutes${COLOR_NC}" >&2
        return 1
    else
        if [[ "${VERBOSE:-false}" == "true" ]]; then
            echo -e "${COLOR_GREEN}✓ Rate limit OK: $remaining/$limit requests remaining${COLOR_NC}" >&2
        fi
        return 0
    fi
}

# Wait with exponential backoff
# Args: $1 = attempt number (1-based)
exponential_backoff() {
    local attempt=$1
    local max_attempts=${2:-5}
    local base_delay=${3:-1}

    if [[ $attempt -gt $max_attempts ]]; then
        echo -e "${COLOR_RED}❌ Max retry attempts ($max_attempts) exceeded${COLOR_NC}" >&2
        return 1
    fi

    local delay=$((base_delay * (2 ** (attempt - 1))))
    echo -e "${COLOR_YELLOW}⏳ Retry $attempt/$max_attempts after ${delay}s delay${COLOR_NC}" >&2
    sleep "$delay"
    return 0
}

# Execute command with retry and exponential backoff
# Args: $1+ = command to execute
# Returns: command exit code or 1 if all retries exhausted
retry_with_backoff() {
    local max_retries=${RETRY_MAX_ATTEMPTS:-5}
    local base_delay=${RETRY_BASE_DELAY:-1}

    for attempt in $(seq 1 $max_retries); do
        if "$@"; then
            return 0
        fi

        local exit_code=$?

        # Check if error is rate limit related (403)
        if [[ $exit_code -eq 22 ]] || grep -q "rate limit" <<< "$@" 2>/dev/null; then
            echo -e "${COLOR_YELLOW}⚠️  Rate limit hit, applying backoff${COLOR_NC}" >&2
            exponential_backoff "$attempt" "$max_retries" "$base_delay" || return 1
        else
            # Non-rate-limit error, don't retry
            return $exit_code
        fi
    done

    echo -e "${COLOR_RED}❌ All retry attempts exhausted${COLOR_NC}" >&2
    return 1
}

# Wait if rate limit is critical
# Returns: 0 to continue, 1 to abort
rate_limit_guard() {
    local force=${1:-false}

    check_rate_limit
    local status=$?

    if [[ $status -eq 2 ]]; then
        # Critical threshold
        if [[ "$force" == "true" ]]; then
            echo -e "${COLOR_YELLOW}⚠️  Proceeding despite critical rate limit (--force specified)${COLOR_NC}" >&2
            return 0
        else
            echo -e "${COLOR_RED}❌ Aborting due to critical rate limit${COLOR_NC}" >&2
            echo -e "${COLOR_RED}   Use --force to override (not recommended)${COLOR_NC}" >&2
            return 1
        fi
    fi

    return 0
}

# Add delay between API calls for rate limiting
# Args: $1 = delay in seconds (default: 0.5)
rate_limit_delay() {
    local delay=${1:-0.5}
    if [[ "${RATE_LIMIT_DELAY:-true}" == "true" ]]; then
        sleep "$delay"
    fi
}

# Print rate limit usage summary
rate_limit_summary() {
    local rate_info
    rate_info=$(gh api rate_limit --jq '.rate' 2>/dev/null)

    if [[ $? -ne 0 ]]; then
        return 1
    fi

    local remaining=$(echo "$rate_info" | jq -r '.remaining')
    local limit=$(echo "$rate_info" | jq -r '.limit')
    local used=$((limit - remaining))
    local reset_time=$(echo "$rate_info" | jq -r '.reset')
    local current_time=$(date +%s)
    local minutes_until_reset=$(( (reset_time - current_time) / 60 ))

    echo ""
    echo "Rate Limit Summary:"
    echo "  Used: $used/$limit requests"
    echo "  Remaining: $remaining requests"
    echo "  Resets in: $minutes_until_reset minutes"
}

# Export functions for use in other scripts
export -f check_rate_limit
export -f exponential_backoff
export -f retry_with_backoff
export -f rate_limit_guard
export -f rate_limit_delay
export -f rate_limit_summary
