#!/usr/bin/env bash
#
# Documentation Freshness Checker
#
# Detects common documentation anti-patterns that lead to staleness:
# - Hard-coded version numbers in timeless docs
# - Duplicated constants from constants.py
# - Hard-coded test counts
# - Duplicated exit code definitions
#
# Exit codes:
#   0 = No issues found
#   1 = Potential staleness detected (warnings)
#   2 = Script error

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Counters
WARNINGS=0
ERRORS=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Documentation Freshness Checker"
echo "=================================="
echo

# Check 1: Version numbers in timeless docs
echo "📋 Check 1: Version numbers in timeless documentation"
TIMELESS_DOCS=(
    "docs/guides/ARCHITECTURE.md"
    "docs/guides/TESTING.md"
    "docs/guides/ERROR_HANDLING.md"
    "docs/guides/SECURITY.md"
)

for doc in "${TIMELESS_DOCS[@]}"; do
    if [ -f "$PROJECT_ROOT/$doc" ]; then
        # Check for version patterns like "Version: 3.5.1" or "v3.5.1"
        if grep -E '(Version:|^v[0-9]+\.[0-9]+\.[0-9]+)' "$PROJECT_ROOT/$doc" > /dev/null 2>&1; then
            # Exclude lines with "Document Type", "Applies To", "Document Version" which are allowed
            if grep -E '(Version:|^v[0-9]+\.[0-9]+\.[0-9]+)' "$PROJECT_ROOT/$doc" | grep -v "Document Type" | grep -v "Applies To" | grep -v "Document Version" | grep -v "Schema Version" | grep -v "Current Version" > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠ WARNING:${NC} Found version number in $doc"
                grep -n -E '(Version:|^v[0-9]+\.[0-9]+\.[0-9]+)' "$PROJECT_ROOT/$doc" | grep -v "Document Type" | grep -v "Applies To" | grep -v "Document Version" | grep -v "Schema Version" | grep -v "Current Version" | head -3
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    fi
done
echo

# Check 2: Duplicated constants from constants.py
echo "📋 Check 2: Duplicated constants (should reference constants.py)"
CONSTANT_PATTERNS=(
    "MAX_RESPONSE_SIZE.*=.*10.*1024.*1024"
    "MAX_PACKAGE_JSON_SIZE.*=.*1.*1024.*1024"
    "DEFAULT_MAX_RETRIES.*=.*3"
    "DEFAULT_RETRY_BASE_DELAY.*=.*2\.0"
    "MAX_BACKOFF_DELAY.*=.*30"
    "API_TIMEOUT_SECONDS.*=.*30"
)

DOC_FILES=$(find "$PROJECT_ROOT/docs" -name "*.md" -type f | grep -v "/archive/")

for pattern in "${CONSTANT_PATTERNS[@]}"; do
    for doc in $DOC_FILES; do
        if grep -E "$pattern" "$doc" > /dev/null 2>&1; then
            # Exclude _CANONICAL_REFERENCES.md which documents the pattern
            if [[ ! "$doc" =~ _CANONICAL_REFERENCES\.md ]]; then
                echo -e "${YELLOW}⚠ WARNING:${NC} Found hard-coded constant in $doc"
                grep -n -E "$pattern" "$doc" | head -1
                echo "   → Should reference constants.py instead"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    done
done
echo

# Check 3: Hard-coded test counts
echo "📋 Check 3: Hard-coded test counts (should be dynamic)"
if grep -E '\([0-9]+ tests?\)' "$PROJECT_ROOT/docs/guides/TESTING.md" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ WARNING:${NC} Found hard-coded test count in TESTING.md"
    grep -n -E '\([0-9]+ tests?\)' "$PROJECT_ROOT/docs/guides/TESTING.md" | head -3
    echo "   → Use 'pytest --collect-only' reference instead"
    WARNINGS=$((WARNINGS + 1))
fi
echo

# Check 4: Exit code duplication (should reference ERROR_HANDLING.md)
echo "📋 Check 4: Exit code duplication (should reference ERROR_HANDLING.md)"
EXIT_CODE_PATTERN='(0=clean|1=vulns|2=error)'
DOCS_TO_CHECK=$(find "$PROJECT_ROOT/docs" -name "*.md" -type f | grep -v ERROR_HANDLING.md | grep -v _CANONICAL_REFERENCES.md | grep -v "/archive/")

for doc in $DOCS_TO_CHECK; do
    if grep -E "$EXIT_CODE_PATTERN" "$doc" > /dev/null 2>&1; then
        # Check if it also has a reference to ERROR_HANDLING.md
        if ! grep -E "ERROR_HANDLING\.md.*Exit Codes" "$doc" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠ WARNING:${NC} Found exit code definition without reference in $doc"
            grep -n -E "$EXIT_CODE_PATTERN" "$doc" | head -1
            echo "   → Should reference ERROR_HANDLING.md § Exit Codes"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
done
echo

# Check 5: Canonical references index is up to date
echo "📋 Check 5: Canonical references index exists"
if [ ! -f "$PROJECT_ROOT/docs/guides/_CANONICAL_REFERENCES.md" ]; then
    echo -e "${RED}✗ ERROR:${NC} _CANONICAL_REFERENCES.md not found"
    echo "   → This file should establish single source of truth"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} _CANONICAL_REFERENCES.md exists"
fi
echo

# Check 6: Performance.md has benchmark dates
echo "📋 Check 6: PERFORMANCE.md benchmark dating"
if [ -f "$PROJECT_ROOT/docs/guides/PERFORMANCE.md" ]; then
    if ! grep -E "(Benchmark Date|as of)" "$PROJECT_ROOT/docs/guides/PERFORMANCE.md" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ WARNING:${NC} PERFORMANCE.md missing benchmark date context"
        echo "   → Benchmarks should be clearly dated"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✓${NC} PERFORMANCE.md has benchmark dating"
    fi
fi
echo

# Check 7: README.md version consistency with STATUS.md
echo "📋 Check 7: README.md version consistency"
if [ -f "$PROJECT_ROOT/README.md" ] && [ -f "$PROJECT_ROOT/docs/project/STATUS.md" ]; then
    # Extract current version from STATUS.md (format: "**Status:** v3.6.0 Released")
    CURRENT_VERSION=$(grep -E '^\*\*Status:\*\* v[0-9]+\.[0-9]+\.[0-9]+' "$PROJECT_ROOT/docs/project/STATUS.md" | head -1 | sed -E 's/.*v([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

    if [ -n "$CURRENT_VERSION" ]; then
        # Check if README mentions an older version in "Latest:" line
        if grep -E "^\*\*Latest:\*\* v[0-9]+\.[0-9]+\.[0-9]+" "$PROJECT_ROOT/README.md" > /dev/null 2>&1; then
            README_VERSION=$(grep -E "^\*\*Latest:\*\* v[0-9]+\.[0-9]+\.[0-9]+" "$PROJECT_ROOT/README.md" | head -1 | sed -E 's/.*v([0-9]+\.[0-9]+\.[0-9]+).*/\1/')
            if [ "$README_VERSION" != "$CURRENT_VERSION" ]; then
                echo -e "${YELLOW}⚠ WARNING:${NC} README.md version mismatch"
                echo "   README shows: v$README_VERSION"
                echo "   STATUS.md shows: v$CURRENT_VERSION"
                echo "   → Update README.md to match current version"
                WARNINGS=$((WARNINGS + 1))
            else
                echo -e "${GREEN}✓${NC} README.md version matches STATUS.md (v$CURRENT_VERSION)"
            fi
        fi

        # Check badges for outdated test counts
        if grep -E 'tests-[0-9]+%20passed' "$PROJECT_ROOT/README.md" > /dev/null 2>&1; then
            BADGE_TESTS=$(grep -oE 'tests-[0-9]+%20passed' "$PROJECT_ROOT/README.md" | head -1 | sed -E 's/tests-([0-9]+)%20passed/\1/')
            # Extract test count from STATUS.md (format: "**Total Tests:** 831")
            STATUS_TESTS=$(grep -E '^\*\*Total Tests:\*\* [0-9]+' "$PROJECT_ROOT/docs/project/STATUS.md" | head -1 | sed -E 's/.*\*\* ([0-9]+).*/\1/')
            if [ -n "$STATUS_TESTS" ] && [ "$BADGE_TESTS" != "$STATUS_TESTS" ]; then
                echo -e "${YELLOW}⚠ WARNING:${NC} README.md test badge mismatch"
                echo "   Badge shows: $BADGE_TESTS tests"
                echo "   STATUS.md shows: $STATUS_TESTS tests"
                echo "   → Update README.md badge"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi

        # Check badges for outdated coverage
        if grep -E 'coverage-[0-9.]+%25' "$PROJECT_ROOT/README.md" > /dev/null 2>&1; then
            BADGE_COV=$(grep -oE 'coverage-[0-9.]+%25' "$PROJECT_ROOT/README.md" | head -1 | sed 's/coverage-//;s/%25//')
            # Extract coverage from STATUS.md (format: "**Final Coverage:** 78.94%")
            STATUS_COV=$(grep -E '^\*\*Final Coverage:\*\* [0-9.]+%' "$PROJECT_ROOT/docs/project/STATUS.md" | head -1 | sed -E 's/.*\*\* ([0-9.]+)%.*/\1/')
            if [ -n "$STATUS_COV" ] && [ "$BADGE_COV" != "$STATUS_COV" ]; then
                echo -e "${YELLOW}⚠ WARNING:${NC} README.md coverage badge mismatch"
                echo "   Badge shows: $BADGE_COV%"
                echo "   STATUS.md shows: $STATUS_COV%"
                echo "   → Update README.md badge"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    fi
fi
echo

# Check 8: SECURITY.md version support table
echo "📋 Check 8: SECURITY.md version support table"
if [ -f "$PROJECT_ROOT/SECURITY.md" ] && [ -f "$PROJECT_ROOT/docs/project/STATUS.md" ]; then
    CURRENT_VERSION=$(grep -E '^\*\*Status:\*\* v[0-9]+\.[0-9]+\.[0-9]+' "$PROJECT_ROOT/docs/project/STATUS.md" | head -1 | sed -E 's/.*v([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

    if [ -n "$CURRENT_VERSION" ]; then
        # Check if SECURITY.md lists current version as "Latest stable"
        if ! grep -E "^\| $CURRENT_VERSION.*Latest stable" "$PROJECT_ROOT/SECURITY.md" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠ WARNING:${NC} SECURITY.md doesn't list v$CURRENT_VERSION as latest"
            echo "   → Update version support table in SECURITY.md"
            WARNINGS=$((WARNINGS + 1))
        else
            echo -e "${GREEN}✓${NC} SECURITY.md lists v$CURRENT_VERSION as latest"
        fi
    fi
fi
echo

# Check 9: CHANGELOG.md has entry for current version
echo "📋 Check 9: CHANGELOG.md current version entry"
if [ -f "$PROJECT_ROOT/CHANGELOG.md" ] && [ -f "$PROJECT_ROOT/docs/project/STATUS.md" ]; then
    CURRENT_VERSION=$(grep -E '^\*\*Status:\*\* v[0-9]+\.[0-9]+\.[0-9]+' "$PROJECT_ROOT/docs/project/STATUS.md" | head -1 | sed -E 's/.*v([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

    if [ -n "$CURRENT_VERSION" ]; then
        # Check if CHANGELOG has an entry for current version (format: "## [3.6.0]")
        if ! grep -E "^## \[$CURRENT_VERSION\]" "$PROJECT_ROOT/CHANGELOG.md" > /dev/null 2>&1; then
            echo -e "${RED}✗ ERROR:${NC} CHANGELOG.md missing entry for v$CURRENT_VERSION"
            echo "   → Add release notes for current version"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN}✓${NC} CHANGELOG.md has entry for v$CURRENT_VERSION"
        fi
    fi
fi
echo

# Summary
echo "=================================="
echo "📊 Summary"
echo "=================================="
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}✗ Errors: $ERRORS${NC}"
fi
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warnings: $WARNINGS${NC}"
fi
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
fi
echo

# Exit with appropriate code
if [ $ERRORS -gt 0 ]; then
    exit 2
elif [ $WARNINGS -gt 0 ]; then
    echo "Run this script regularly to catch documentation drift early."
    exit 1
else
    exit 0
fi
