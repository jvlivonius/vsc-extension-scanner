#!/usr/bin/env bash
# Get GitHub Projects V2 IDs for automation
#
# This script fetches the project ID, field IDs, and option IDs needed for
# the sync-project-fields workflow and outputs commands to set them as
# GitHub repository variables.
#
# Prerequisites:
# 1. GitHub CLI installed and authenticated
# 2. Token with 'project' and 'repo' scopes
# 3. Project #3 exists with Priority and Complexity fields
#
# Usage:
#   ./scripts/github-projects/get-project-ids.sh
#   # Copy and run the output commands to set repository variables

set -euo pipefail

# Configuration
PROJECT_NUMBER=3
OWNER="jvlivonius"  # User-level project owner

echo "===================================="
echo "GitHub Projects V2 ID Fetcher"
echo "===================================="
echo ""
echo "Fetching IDs for Project #${PROJECT_NUMBER}..."
echo ""

# Step 1: Get project ID
echo "Step 1: Fetching project ID..."

PROJECT_QUERY=$(cat <<'EOF'
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      id
      title
    }
  }
}
EOF
)

PROJECT_RESPONSE=$(gh api graphql \
  -f query="$PROJECT_QUERY" \
  -f owner="$OWNER" \
  -F number="$PROJECT_NUMBER")

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | jq -r '.data.user.projectV2.id')
PROJECT_TITLE=$(echo "$PROJECT_RESPONSE" | jq -r '.data.user.projectV2.title')

if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "null" ]]; then
  echo "❌ Error: Could not find Project #${PROJECT_NUMBER} for user ${OWNER}"
  echo "   Make sure the project exists and you have access."
  exit 1
fi

echo "✅ Found project: $PROJECT_TITLE"
echo "   ID: $PROJECT_ID"
echo ""

# Step 2: Get all fields with their options
echo "Step 2: Fetching custom fields..."

FIELDS_QUERY=$(cat <<'EOF'
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}
EOF
)

FIELDS_RESPONSE=$(gh api graphql \
  -f query="$FIELDS_QUERY" \
  -f owner="$OWNER" \
  -F number="$PROJECT_NUMBER")

# Extract Priority field
PRIORITY_FIELD_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
  '.data.user.projectV2.fields.nodes[] | select(.name == "Priority") | .id')

if [[ -z "$PRIORITY_FIELD_ID" || "$PRIORITY_FIELD_ID" == "null" ]]; then
  echo "⚠️  Warning: Priority field not found"
  echo "   Create it in the project settings first"
else
  echo "✅ Found Priority field"
  echo "   ID: $PRIORITY_FIELD_ID"

  # Get Priority options
  PRIORITY_CRITICAL_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Priority") | .options[] | select(.name == "Critical") | .id')
  PRIORITY_HIGH_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Priority") | .options[] | select(.name == "High") | .id')
  PRIORITY_MEDIUM_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Priority") | .options[] | select(.name == "Medium") | .id')
  PRIORITY_LOW_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Priority") | .options[] | select(.name == "Low") | .id')

  echo "   Options:"
  echo "     Critical: $PRIORITY_CRITICAL_ID"
  echo "     High: $PRIORITY_HIGH_ID"
  echo "     Medium: $PRIORITY_MEDIUM_ID"
  echo "     Low: $PRIORITY_LOW_ID"
fi

echo ""

# Extract Complexity field
COMPLEXITY_FIELD_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
  '.data.user.projectV2.fields.nodes[] | select(.name == "Complexity") | .id')

if [[ -z "$COMPLEXITY_FIELD_ID" || "$COMPLEXITY_FIELD_ID" == "null" ]]; then
  echo "⚠️  Warning: Complexity field not found"
  echo "   Create it in the project settings first"
else
  echo "✅ Found Complexity field"
  echo "   ID: $COMPLEXITY_FIELD_ID"

  # Get Complexity options
  COMPLEXITY_XS_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Complexity") | .options[] | select(.name == "XS") | .id')
  COMPLEXITY_S_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Complexity") | .options[] | select(.name == "S") | .id')
  COMPLEXITY_M_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Complexity") | .options[] | select(.name == "M") | .id')
  COMPLEXITY_L_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Complexity") | .options[] | select(.name == "L") | .id')
  COMPLEXITY_XL_ID=$(echo "$FIELDS_RESPONSE" | jq -r \
    '.data.user.projectV2.fields.nodes[] | select(.name == "Complexity") | .options[] | select(.name == "XL") | .id')

  echo "   Options:"
  echo "     XS: $COMPLEXITY_XS_ID"
  echo "     S: $COMPLEXITY_S_ID"
  echo "     M: $COMPLEXITY_M_ID"
  echo "     L: $COMPLEXITY_L_ID"
  echo "     XL: $COMPLEXITY_XL_ID"
fi

echo ""
echo "===================================="
echo "Repository Variable Setup Commands"
echo "===================================="
echo ""
echo "Copy and run these commands to set repository variables:"
echo ""

# Generate commands
cat <<EOF
# Project ID
gh variable set PROJECT_ID --body "$PROJECT_ID"

EOF

if [[ -n "$PRIORITY_FIELD_ID" && "$PRIORITY_FIELD_ID" != "null" ]]; then
  cat <<EOF
# Priority field
gh variable set PRIORITY_FIELD_ID --body "$PRIORITY_FIELD_ID"
gh variable set PRIORITY_CRITICAL_OPTION_ID --body "$PRIORITY_CRITICAL_ID"
gh variable set PRIORITY_HIGH_OPTION_ID --body "$PRIORITY_HIGH_ID"
gh variable set PRIORITY_MEDIUM_OPTION_ID --body "$PRIORITY_MEDIUM_ID"
gh variable set PRIORITY_LOW_OPTION_ID --body "$PRIORITY_LOW_ID"

EOF
fi

if [[ -n "$COMPLEXITY_FIELD_ID" && "$COMPLEXITY_FIELD_ID" != "null" ]]; then
  cat <<EOF
# Complexity field
gh variable set COMPLEXITY_FIELD_ID --body "$COMPLEXITY_FIELD_ID"
gh variable set COMPLEXITY_XS_OPTION_ID --body "$COMPLEXITY_XS_ID"
gh variable set COMPLEXITY_S_OPTION_ID --body "$COMPLEXITY_S_ID"
gh variable set COMPLEXITY_M_OPTION_ID --body "$COMPLEXITY_M_ID"
gh variable set COMPLEXITY_L_OPTION_ID --body "$COMPLEXITY_L_ID"
gh variable set COMPLEXITY_XL_OPTION_ID --body "$COMPLEXITY_XL_ID"

EOF
fi

echo ""
echo "===================================="
echo "Next Steps"
echo "===================================="
echo ""
echo "1. Copy the commands above"
echo "2. Run them in your repository directory"
echo "3. Verify with: gh variable list"
echo "4. Test by adding a priority or complexity label to an issue"
echo ""
echo "Note: These IDs are stable unless you delete and recreate the fields."
echo "      If you recreate fields, re-run this script and update the variables."
echo ""
