#!/usr/bin/env bash
#
# validate-task-response.sh - Validate Task subprocess JSON response format
#
# Validates that Task tool subagent responses conform to the expected JSON schema:
# - Response must be valid JSON (parseable by jq)
# - Required fields must be present
# - No prose wrapper or markdown formatting
#
# Usage:
#   ./scripts/github-projects/validate-task-response.sh "$response"
#
# Exit codes:
#   0 - Response is valid
#   1 - Response is invalid (missing fields, bad format, etc.)
#
# Examples:
#   # Valid response
#   response='{"status":"success","branch":"feature/foo","commit_sha":"abc123",...}'
#   ./scripts/github-projects/validate-task-response.sh "$response"
#
#   # Invalid response (prose wrapper)
#   response='Perfect! Here is the JSON: {"status":"success",...}'
#   ./scripts/github-projects/validate-task-response.sh "$response"  # Exit 1

set -euo pipefail

# Colors
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${COLOR_BLUE}ℹ${COLOR_NC} $*"
}

log_success() {
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $*"
}

log_error() {
    echo -e "${COLOR_RED}✗${COLOR_NC} $*"
}

# Usage information
usage() {
    cat <<EOF
Validate Task Subprocess JSON Response

Usage:
  $(basename "$0") RESPONSE_STRING

Arguments:
  RESPONSE_STRING          JSON response from Task tool subprocess

Examples:
  # Valid response
  $(basename "$0") '{"status":"success","branch":"feature/foo",...}'

  # Invalid response (will fail)
  $(basename "$0") 'Here is the result: {...}'

EOF
    exit 0
}

# Parse arguments
if [[ $# -eq 0 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    usage
fi

response="$1"

log_info "Validating Task subprocess response format..."

# Check if response is valid JSON
if ! echo "$response" | jq . >/dev/null 2>&1; then
    log_error "Response is not valid JSON"
    log_error "Response must be pure JSON with no prose wrapper or markdown code blocks"
    log_error "Expected: {\"status\":\"success\",...}"
    log_error "Got: ${response:0:100}..."
    exit 1
fi

log_success "Response is valid JSON"

# Define required fields
required_fields=(
    "status"
    "branch"
    "commit_sha"
    "files_changed"
    "tests_passed"
    "error_message"
)

# Validate required fields exist (including null values)
missing_fields=()
for field in "${required_fields[@]}"; do
    if ! echo "$response" | jq -e "has(\"$field\")" >/dev/null 2>&1; then
        missing_fields+=("$field")
    fi
done

if [[ ${#missing_fields[@]} -gt 0 ]]; then
    log_error "Missing required fields: ${missing_fields[*]}"
    log_error "Required fields: ${required_fields[*]}"
    exit 1
fi

log_success "All required fields present"

# Validate status field value
status=$(echo "$response" | jq -r '.status')
if [[ "$status" != "success" ]] && [[ "$status" != "failed" ]]; then
    log_error "Invalid status value: '$status'"
    log_error "Status must be 'success' or 'failed'"
    exit 1
fi

log_success "Status field valid: '$status'"

# Validate files_changed is an array
if ! echo "$response" | jq -e '.files_changed | type == "array"' >/dev/null 2>&1; then
    log_error "Field 'files_changed' must be an array"
    exit 1
fi

log_success "Field 'files_changed' is valid array"

# Validate tests_passed is boolean
if ! echo "$response" | jq -e '.tests_passed | type == "boolean"' >/dev/null 2>&1; then
    log_error "Field 'tests_passed' must be a boolean"
    exit 1
fi

log_success "Field 'tests_passed' is valid boolean"

log_success "Task subprocess response format is valid"
exit 0
