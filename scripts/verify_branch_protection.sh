#!/bin/bash
# Branch Protection Verification Script
# Compares live GitHub branch protection settings with local configuration file
#
# Usage: ./scripts/verify_branch_protection.sh
# Requires: gh CLI tool authenticated

set -e

REPO="jvlivonius/vsc-extension-scanner"
CONFIG_FILE=".github/branch-protection-config.json"
BRANCH="main"

echo "🔍 Branch Protection Verification"
echo "=================================="
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: gh CLI not found"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "📋 Fetching live GitHub configuration..."
LIVE_CONFIG=$(gh api "repos/$REPO/branches/$BRANCH/protection" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ Error fetching live configuration:"
    echo "$LIVE_CONFIG"
    exit 1
fi

echo "✅ Live configuration fetched"
echo ""

# Extract status checks from live config
echo "🔍 Comparing status check configurations..."
echo ""

LIVE_CHECKS=$(echo "$LIVE_CONFIG" | jq -r '.required_status_checks.contexts[]' | sort)
LOCAL_CHECKS=$(jq -r '.required_status_checks.contexts[]' "$CONFIG_FILE" | sort)

echo "Live GitHub Status Checks:"
echo "$LIVE_CHECKS" | sed 's/^/  - /'
echo ""

echo "Local Config File Status Checks:"
echo "$LOCAL_CHECKS" | sed 's/^/  - /'
echo ""

# Compare checks
if [ "$LIVE_CHECKS" = "$LOCAL_CHECKS" ]; then
    echo "✅ Status checks match!"
else
    echo "❌ Status checks DO NOT match!"
    echo ""
    echo "Differences:"
    diff <(echo "$LIVE_CHECKS") <(echo "$LOCAL_CHECKS") || true
    echo ""
fi

# Compare other key settings
echo ""
echo "🔍 Comparing other protection settings..."
echo ""

LIVE_STRICT=$(echo "$LIVE_CONFIG" | jq -r '.required_status_checks.strict')
LOCAL_STRICT=$(jq -r '.required_status_checks.strict' "$CONFIG_FILE")

LIVE_ENFORCE=$(echo "$LIVE_CONFIG" | jq -r '.enforce_admins.enabled')
LOCAL_ENFORCE=$(jq -r '.enforce_admins' "$CONFIG_FILE")

LIVE_APPROVALS=$(echo "$LIVE_CONFIG" | jq -r '.required_pull_request_reviews.required_approving_review_count')
LOCAL_APPROVALS=$(jq -r '.required_pull_request_reviews.required_approving_review_count' "$CONFIG_FILE")

LIVE_FORCE_PUSH=$(echo "$LIVE_CONFIG" | jq -r '.allow_force_pushes.enabled')
LOCAL_FORCE_PUSH=$(jq -r '.allow_force_pushes' "$CONFIG_FILE")

LIVE_DELETIONS=$(echo "$LIVE_CONFIG" | jq -r '.allow_deletions.enabled')
LOCAL_DELETIONS=$(jq -r '.allow_deletions' "$CONFIG_FILE")

ALL_MATCH=true

# Check strict status checks
if [ "$LIVE_STRICT" = "$LOCAL_STRICT" ]; then
    echo "✅ Strict status checks: $LIVE_STRICT"
else
    echo "❌ Strict status checks: Live=$LIVE_STRICT, Local=$LOCAL_STRICT"
    ALL_MATCH=false
fi

# Check enforce admins
if [ "$LIVE_ENFORCE" = "$LOCAL_ENFORCE" ]; then
    echo "✅ Enforce admins: $LIVE_ENFORCE"
else
    echo "❌ Enforce admins: Live=$LIVE_ENFORCE, Local=$LOCAL_ENFORCE"
    ALL_MATCH=false
fi

# Check required approvals
if [ "$LIVE_APPROVALS" = "$LOCAL_APPROVALS" ]; then
    echo "✅ Required approvals: $LIVE_APPROVALS"
else
    echo "❌ Required approvals: Live=$LIVE_APPROVALS, Local=$LOCAL_APPROVALS"
    ALL_MATCH=false
fi

# Check force pushes
if [ "$LIVE_FORCE_PUSH" = "$LOCAL_FORCE_PUSH" ]; then
    echo "✅ Allow force pushes: $LIVE_FORCE_PUSH"
else
    echo "❌ Allow force pushes: Live=$LIVE_FORCE_PUSH, Local=$LOCAL_FORCE_PUSH"
    ALL_MATCH=false
fi

# Check deletions
if [ "$LIVE_DELETIONS" = "$LOCAL_DELETIONS" ]; then
    echo "✅ Allow deletions: $LIVE_DELETIONS"
else
    echo "❌ Allow deletions: Live=$LIVE_DELETIONS, Local=$LOCAL_DELETIONS"
    ALL_MATCH=false
fi

echo ""
echo "=================================="

if [ "$LIVE_CHECKS" = "$LOCAL_CHECKS" ] && [ "$ALL_MATCH" = true ]; then
    echo "✅ All configurations match!"
    exit 0
else
    echo "❌ Configuration drift detected!"
    echo ""
    echo "To fix:"
    echo "  1. Update $CONFIG_FILE to match live settings, or"
    echo "  2. Apply config file to GitHub:"
    echo "     gh api repos/$REPO/branches/$BRANCH/protection \\"
    echo "       --method PUT \\"
    echo "       --input $CONFIG_FILE"
    exit 1
fi
