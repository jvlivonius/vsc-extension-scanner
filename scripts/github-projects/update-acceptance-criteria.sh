#!/usr/bin/env bash
# Update Acceptance Criteria checkbox in GitHub issue
#
# Usage: ./update-acceptance-criteria.sh <issue-number> <criterion-text>
#
# Example:
#   ./update-acceptance-criteria.sh 75 "Unit tests achieve ≥90% coverage"

set -euo pipefail

# Validate arguments
if [ $# -lt 2 ]; then
  echo "Error: Missing required arguments"
  echo "Usage: $0 <issue-number> <criterion-text>"
  echo ""
  echo "Example:"
  echo "  $0 75 'Unit tests achieve ≥90% coverage'"
  exit 1
fi

ISSUE_NUMBER="$1"
shift
CRITERION_TEXT="$*"

# Validate issue number
if ! [[ "$ISSUE_NUMBER" =~ ^[0-9]+$ ]]; then
  echo "Error: Invalid issue number: $ISSUE_NUMBER"
  exit 1
fi

echo "Updating acceptance criteria for issue #$ISSUE_NUMBER"
echo "Criterion: $CRITERION_TEXT"

# Get current issue body
CURRENT_BODY=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body')

if [ -z "$CURRENT_BODY" ]; then
  echo "Error: Could not fetch issue body"
  exit 1
fi

# Check if criterion exists (either checked or unchecked)
if ! echo "$CURRENT_BODY" | grep -qF "$CRITERION_TEXT"; then
  echo "Warning: Criterion not found in issue body"
  echo "Skipping update (criterion may have been manually modified)"
  exit 0
fi

# Check if already checked
if echo "$CURRENT_BODY" | grep -qF "- [x] $CRITERION_TEXT"; then
  echo "✓ Criterion already checked"
  exit 0
fi

# Replace unchecked with checked
# Using sed with proper escaping for special characters
ESCAPED_TEXT=$(echo "$CRITERION_TEXT" | sed 's/[\/&]/\\&/g')
UPDATED_BODY=$(echo "$CURRENT_BODY" | sed "s/- \[ \] $ESCAPED_TEXT/- [x] $ESCAPED_TEXT/")

# Verify change was made
if [ "$CURRENT_BODY" = "$UPDATED_BODY" ]; then
  echo "Error: Failed to update criterion (no change detected)"
  echo "This may indicate special characters need additional escaping"
  exit 1
fi

# Save updated body to temp file (gh issue edit requires file or string)
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT
echo "$UPDATED_BODY" > "$TEMP_FILE"

# Update issue
if gh issue edit "$ISSUE_NUMBER" --body-file "$TEMP_FILE"; then
  echo "✓ Successfully checked criterion in issue #$ISSUE_NUMBER"
else
  echo "Error: Failed to update issue"
  exit 1
fi
