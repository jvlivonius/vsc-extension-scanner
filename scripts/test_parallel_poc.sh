#!/bin/bash
# PoC script to validate pytest-xdist parallel test execution
# Tests different test groups to identify which can run in parallel vs serial

# Note: Don't use 'set -e' because we want to continue testing even if some groups fail

echo "=========================================="
echo "pytest-xdist Parallel Execution PoC"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
RESULTS_FILE=$(mktemp)
TOTAL_TESTS=0
PASSED_GROUPS=0
FAILED_GROUPS=0

# Function to log results
log_result() {
    local group=$1
    local status=$2
    local duration=$3
    echo "${group}|${status}|${duration}" >> "$RESULTS_FILE"
}

# Function to run test group
run_test_group() {
    local group_name=$1
    local test_pattern=$2
    local workers=$3
    local description=$4

    echo -e "${BLUE}Testing: ${group_name}${NC}"
    echo "Pattern: ${test_pattern}"
    echo "Workers: ${workers}"
    echo "Description: ${description}"
    echo "---"

    local start_time=$(date +%s)

    if [ "$workers" = "serial" ]; then
        # Run serially (no xdist)
        if pytest "$test_pattern" -v --tb=short -m "not real_api" 2>&1 | tee /tmp/pytest_output_${group_name}.log; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo -e "${GREEN}✓ PASSED${NC} (${duration}s)\n"
            log_result "$group_name" "PASSED" "${duration}s"
            PASSED_GROUPS=$((PASSED_GROUPS + 1))
            return 0
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo -e "${RED}✗ FAILED${NC} (${duration}s)\n"
            log_result "$group_name" "FAILED" "${duration}s"
            FAILED_GROUPS=$((FAILED_GROUPS + 1))
            return 1
        fi
    else
        # Run with xdist
        if pytest "$test_pattern" -v --tb=short -m "not real_api" -n "$workers" 2>&1 | tee /tmp/pytest_output_${group_name}.log; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo -e "${GREEN}✓ PASSED${NC} (${duration}s, ${workers} workers)\n"
            log_result "$group_name" "PASSED_PARALLEL" "${duration}s"
            PASSED_GROUPS=$((PASSED_GROUPS + 1))
            return 0
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo -e "${RED}✗ FAILED${NC} (${duration}s, ${workers} workers)\n"
            log_result "$group_name" "FAILED_PARALLEL" "${duration}s"
            FAILED_GROUPS=$((FAILED_GROUPS + 1))
            return 1
        fi
    fi
}

# Install package dependencies first
echo "Installing package dependencies..."
pip install -e .[test] > /dev/null 2>&1
echo -e "${GREEN}✓ Package dependencies installed${NC}\n"

# Check if pytest-xdist is available
echo "Checking for pytest-xdist..."
if python3 -c "import xdist" 2>/dev/null; then
    echo -e "${GREEN}✓ pytest-xdist is installed${NC}\n"
else
    echo -e "${YELLOW}pytest-xdist not found. Installing for PoC...${NC}"
    pip install pytest-xdist
    echo -e "${GREEN}✓ pytest-xdist installed${NC}\n"
fi

echo "=========================================="
echo "Phase 1: Baseline Serial Execution"
echo "=========================================="
echo ""

# Baseline: Run a small subset serially to establish baseline
run_test_group "baseline_serial" "tests/test_utils.py" "serial" "Baseline serial execution of utils tests"

echo "=========================================="
echo "Phase 2: Safe Unit Tests (Likely Parallel-Safe)"
echo "=========================================="
echo ""

# Test pure unit tests (no I/O, no cache, no DB)
UNIT_TEST_GROUPS=(
    "tests/test_utils.py|Pure utility functions (no state)"
    "tests/test_constants.py|Constants and enums (read-only)"
    "tests/test_types.py|Type definitions and dataclasses"
    "tests/test_string_sanitization.py|String sanitization (pure functions)"
)

for test_group in "${UNIT_TEST_GROUPS[@]}"; do
    IFS='|' read -r pattern description <<< "$test_group"
    if [ -f "$pattern" ]; then
        run_test_group "unit_$(basename $pattern .py)" "$pattern" "auto" "$description"
    else
        echo -e "${YELLOW}⚠ Skipping $pattern (file not found)${NC}\n"
    fi
done

echo "=========================================="
echo "Phase 3: Cache-Related Tests (Potential Conflicts)"
echo "=========================================="
echo ""

# Test cache-related tests (may have file conflicts)
CACHE_TEST_GROUPS=(
    "tests/test_cache*.py|Cache operations (potential file conflicts)"
    "tests/test_sqlite*.py|SQLite operations (DB locking concerns)"
)

for test_group in "${CACHE_TEST_GROUPS[@]}"; do
    IFS='|' read -r pattern description <<< "$test_group"
    matching_files=$(ls $pattern 2>/dev/null || echo "")
    if [ -n "$matching_files" ]; then
        run_test_group "cache_$(echo $pattern | tr '/*' '_')" "$pattern" "auto" "$description"
    else
        echo -e "${YELLOW}⚠ Skipping $pattern (no matching files)${NC}\n"
    fi
done

echo "=========================================="
echo "Phase 4: Integration Tests (High Risk)"
echo "=========================================="
echo ""

# Test integration tests (shared state, API calls)
if [ -f "tests/test_integration.py" ]; then
    run_test_group "integration_parallel" "tests/test_integration.py" "auto" "Integration tests with parallel execution"
else
    echo -e "${YELLOW}⚠ Skipping integration tests (file not found)${NC}\n"
fi

echo "=========================================="
echo "Phase 5: Full Suite Comparison"
echo "=========================================="
echo ""

# Run full suite serially for baseline
echo -e "${BLUE}Running full suite serially (baseline)...${NC}"
run_test_group "full_suite_serial" "tests/" "serial" "Complete test suite (serial)"

# Run full suite with parallel execution
echo -e "${BLUE}Running full suite with parallel execution...${NC}"
run_test_group "full_suite_parallel" "tests/" "auto" "Complete test suite (parallel)"

echo "=========================================="
echo "PoC Results Summary"
echo "=========================================="
echo ""

# Display results
echo "Results by Test Group:"
echo "---"
printf "%-30s %-20s %-10s\n" "Test Group" "Status" "Duration"
printf "%-30s %-20s %-10s\n" "----------" "------" "--------"

while IFS='|' read -r group status duration; do
    if [[ "$status" == "PASSED"* ]]; then
        printf "%-30s ${GREEN}%-20s${NC} %-10s\n" "$group" "$status" "$duration"
    else
        printf "%-30s ${RED}%-20s${NC} %-10s\n" "$group" "$status" "$duration"
    fi
done < "$RESULTS_FILE"

echo ""
echo "Summary:"
echo "  Passed groups: ${PASSED_GROUPS}"
echo "  Failed groups: ${FAILED_GROUPS}"
echo ""

# Analyze results and provide recommendations
echo "=========================================="
echo "Recommendations"
echo "=========================================="
echo ""

if [ $FAILED_GROUPS -eq 0 ]; then
    echo -e "${GREEN}✓ All test groups passed with parallel execution!${NC}"
    echo ""
    echo "Next Steps:"
    echo "  1. Add pytest-xdist to pyproject.toml test dependencies"
    echo "  2. Update test.yml to use: pytest -n auto tests/"
    echo "  3. Expected speedup: 30-50% for full test suite"
    echo ""
elif grep -q "full_suite_parallel|PASSED" "$RESULTS_FILE"; then
    echo -e "${YELLOW}⚠ Some test groups failed, but full suite passed${NC}"
    echo ""
    echo "Analysis:"
    echo "  - Individual test group failures may be due to test isolation"
    echo "  - Full suite success suggests parallel execution is viable"
    echo ""
    echo "Next Steps:"
    echo "  1. Review failed test groups in logs: /tmp/pytest_output_*.log"
    echo "  2. Consider pytest-xdist for full suite only"
    echo "  3. Monitor for flaky tests in CI"
    echo ""
else
    echo -e "${RED}✗ Parallel execution failed for critical test groups${NC}"
    echo ""
    echo "Issues Detected:"
    grep "FAILED" "$RESULTS_FILE" | while IFS='|' read -r group status duration; do
        echo "  - $group: Check /tmp/pytest_output_${group}.log"
    done
    echo ""
    echo "Common Causes:"
    echo "  - SQLite database locking (shared cache.db)"
    echo "  - Shared cache file conflicts (HMAC integrity)"
    echo "  - Temporary file collisions"
    echo ""
    echo "Recommendations:"
    echo "  1. Review test logs for specific errors"
    echo "  2. Consider test fixtures for worker isolation"
    echo "  3. May need to mark tests with pytest.mark.serial"
    echo "  4. Skip parallel optimization for now"
    echo ""
fi

# Cleanup
rm -f "$RESULTS_FILE"

# Exit with success if all passed, failure otherwise
if [ $FAILED_GROUPS -eq 0 ]; then
    exit 0
else
    exit 1
fi
