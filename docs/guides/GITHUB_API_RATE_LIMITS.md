# GitHub API Rate Limiting Best Practices

**Purpose**: Prevent rate limit exhaustion when using GitHub Projects and Issue workflow automation

**Rate Limit**: 5,000 requests/hour for authenticated users (primary rate limit)

---

## Overview

GitHub API has strict rate limiting to prevent abuse. When automating issue workflows, especially batch operations, you can easily exceed these limits without proper management.

**Common Scenarios That Hit Rate Limits:**
- Creating 50+ issues from a plan
- Validating all issues in a milestone
- Setting parent-child relationships for multiple issues
- Syncing dependencies across many issues
- Generating comprehensive milestone reports

---

## rate_limit.sh Library

**Location**: `scripts/github-projects/rate_limit.sh`

**Purpose**: Centralized rate limit monitoring, backoff strategies, and guard functions

### Available Functions

#### 1. `check_rate_limit()`

**Purpose**: Check current GitHub API rate limit status

**Returns:**
- `0` = OK (>100 requests remaining)
- `1` = WARNING (<100 requests remaining)
- `2` = CRITICAL (<20 requests remaining)

**Output:**
```
✓ Rate limit OK: 4523/5000 requests remaining
⚠️  WARNING: 85/5000 API requests remaining
   Rate limit resets in 42 minutes
🚨 CRITICAL: Only 15/5000 API requests remaining!
   Rate limit resets in 12 minutes
   Consider waiting or using a different token
```

**Usage:**
```bash
check_rate_limit
status=$?

if [[ $status -eq 2 ]]; then
    echo "Critical rate limit - aborting"
    exit 1
fi
```

---

#### 2. `rate_limit_guard()`

**Purpose**: Block script execution if rate limit is critical

**Arguments:**
- `$1` = force flag (`true` to override, default: `false`)

**Returns:**
- `0` = Safe to continue
- `1` = Critical rate limit, abort

**Behavior:**
- **WARNING (<100)**: Displays warning, allows execution
- **CRITICAL (<20)**: Blocks execution unless `--force` specified

**Usage:**
```bash
# At start of script - abort if critical
rate_limit_guard || exit 1

# With force override
rate_limit_guard true  # Proceeds even if critical
```

---

#### 3. `rate_limit_delay()`

**Purpose**: Add configurable delay between API calls

**Arguments:**
- `$1` = delay in seconds (default: `0.5`)

**Environment Variables:**
- `RATE_LIMIT_DELAY=false` to disable delays globally

**Usage:**
```bash
for issue in $issues; do
    gh api "repos/:owner/:repo/issues/$issue"
    rate_limit_delay  # 0.5s delay
done

# Custom delay
for dep in $dependencies; do
    gh api "repos/:owner/:repo/issues/$dep/dependencies"
    rate_limit_delay 1.0  # 1 second delay
done
```

**Why This Helps:**
- Spreads API calls over time
- Reduces burst traffic
- Allows rate limit counter to reset gradually
- Default 0.5s = max 120 requests/minute (well below 5000/hour)

---

#### 4. `exponential_backoff()`

**Purpose**: Wait with exponentially increasing delays between retry attempts

**Arguments:**
- `$1` = attempt number (1-based)
- `$2` = max attempts (default: `5`)
- `$3` = base delay in seconds (default: `1`)

**Backoff Schedule:**
- Attempt 1: 1s delay
- Attempt 2: 2s delay
- Attempt 3: 4s delay
- Attempt 4: 8s delay
- Attempt 5: 16s delay

**Usage:**
```bash
for attempt in $(seq 1 5); do
    if gh api "some/endpoint"; then
        break
    fi
    exponential_backoff "$attempt" 5 1 || exit 1
done
```

---

#### 5. `retry_with_backoff()`

**Purpose**: Execute command with automatic retry and exponential backoff

**Arguments:**
- `$@` = command to execute

**Environment Variables:**
- `RETRY_MAX_ATTEMPTS=5` (default: 5)
- `RETRY_BASE_DELAY=1` (default: 1 second)

**Behavior:**
- Retries only on rate limit errors (HTTP 403)
- Non-rate-limit errors fail immediately
- Returns original command exit code on success

**Usage:**
```bash
# Simple retry
retry_with_backoff gh api "repos/:owner/:repo/issues"

# Custom retry settings
RETRY_MAX_ATTEMPTS=3 RETRY_BASE_DELAY=2 \
    retry_with_backoff gh api "repos/:owner/:repo/issues/$issue"
```

---

#### 6. `rate_limit_summary()`

**Purpose**: Display final rate limit usage statistics

**Output:**
```
Rate Limit Summary:
  Used: 234/5000 requests
  Remaining: 4766 requests
  Resets in: 38 minutes
```

**Usage:**
```bash
# At end of script
echo ""
echo "=== Operation Complete ==="
rate_limit_summary
```

---

## Standard Integration Pattern

All scripts that make GitHub API calls should follow this pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Source rate limit library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/rate_limit.sh" ]]; then
    source "$SCRIPT_DIR/rate_limit.sh"
else
    echo "ERROR: rate_limit.sh not found" >&2
    exit 1
fi

# 2. Check rate limit at script start
rate_limit_guard || exit 1

# 3. Add delays in loops
for item in $items; do
    # Make API call
    gh api "some/endpoint/$item"

    # Add delay
    rate_limit_delay
done

# 4. Show summary at end
rate_limit_summary
```

---

## Integration Examples

### Example 1: Simple Script with Rate Limiting

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/rate_limit.sh"

# Guard at start
rate_limit_guard || exit 1

# Process issues with delays
ISSUES="142 143 144 145"
for issue in $ISSUES; do
    echo "Processing issue #$issue..."
    gh issue view "$issue" --json title,state
    rate_limit_delay  # 0.5s between calls
done

# Summary
rate_limit_summary
```

---

### Example 2: Batch Operations with Retry

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/rate_limit.sh"

# Guard with custom thresholds
rate_limit_guard || exit 1

# Batch operations with retry
ISSUES=$(gh issue list --limit 100 --json number --jq '.[].number')

for issue in $ISSUES; do
    echo "Validating issue #$issue..."

    # Retry on rate limit errors
    if ! retry_with_backoff gh api "repos/:owner/:repo/issues/$issue"; then
        echo "Failed to fetch issue #$issue after retries"
        continue
    fi

    rate_limit_delay
done

rate_limit_summary
```

---

### Example 3: Critical Operations with Force Override

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/rate_limit.sh"

FORCE=${1:-false}

# Allow force override for critical operations
if [[ "$FORCE" == "--force" ]]; then
    rate_limit_guard true  # Proceeds even if critical
else
    rate_limit_guard || exit 1
fi

# Critical operation
gh api graphql -f query='...'

rate_limit_summary
```

---

## Rate Limit Calculation Examples

### Creating Issues from Plan

**Scenario**: Create 30 issues with parent-child relationships

**API Calls:**
- Create 30 issues: 30 requests
- Get node IDs for parent: 1 request
- Set 29 children via GraphQL: 29 requests
- **Total: 60 requests**

**Time with delays:**
- 60 requests × 0.5s delay = 30 seconds
- Well below rate limit

---

### Milestone Report Generation

**Scenario**: Generate report for milestone with 50 issues

**API Calls:**
- List issues in milestone: 1 request
- Fetch details for 50 issues: 50 requests
- Check dependencies for 20 issues: 20 requests
- Check parent-child for 10 issues: 10 requests
- **Total: 81 requests**

**Time with delays:**
- 81 requests × 0.5s delay = 40.5 seconds
- Remaining: 5000 - 81 = 4919 requests

---

### Dependency Synchronization

**Scenario**: Sync dependencies for 100 issues

**API Calls:**
- Fetch issue bodies: 100 requests
- Check GitHub API dependencies: 100 requests
- Create missing dependencies: ~20 requests
- **Total: 220 requests**

**Time with delays:**
- 220 requests × 0.5s delay = 110 seconds (~2 minutes)
- Remaining: 5000 - 220 = 4780 requests

---

## Troubleshooting

### Error: "API rate limit exceeded"

**Symptoms:**
```
gh: API rate limit exceeded for user
```

**Solutions:**

1. **Check remaining quota:**
   ```bash
   gh api rate_limit
   ```

2. **Wait for reset:**
   ```bash
   # Check reset time
   gh api rate_limit --jq '.rate.reset' | xargs -I {} date -r {}

   # Wait until reset
   sleep $(($(gh api rate_limit --jq '.rate.reset') - $(date +%s)))
   ```

3. **Use different authentication:**
   ```bash
   # Switch to different token
   gh auth switch

   # Or use token with higher limits
   gh auth login --with-token < token.txt
   ```

---

### Warning: "Only X requests remaining"

**Symptoms:**
```
⚠️  WARNING: 85/5000 API requests remaining
   Rate limit resets in 42 minutes
```

**Recommendations:**

1. **Defer non-critical operations:**
   - Wait until rate limit resets
   - Reduce batch sizes
   - Increase delays between calls

2. **Optimize API usage:**
   ```bash
   # Instead of individual calls
   for issue in $issues; do
       gh issue view "$issue"
   done

   # Use batch query
   gh api graphql -f query='query {
       repository(owner: "...", name: "...") {
           issues(first: 100) {
               nodes { number title state }
           }
       }
   }'
   ```

3. **Enable verbose logging:**
   ```bash
   VERBOSE=true ./script.sh
   ```

---

### Critical: "Only X requests remaining"

**Symptoms:**
```
🚨 CRITICAL: Only 15/5000 API requests remaining!
   Rate limit resets in 12 minutes
   Consider waiting or using a different token
```

**Immediate Actions:**

1. **Stop all automated scripts**
2. **Wait for rate limit reset** (shown in message)
3. **Review API usage patterns**

**Prevention:**
- Always use `rate_limit_guard()` at script start
- Add `rate_limit_delay()` in all loops
- Monitor rate limit with `rate_limit_summary()`

---

## Best Practices

### 1. Always Guard at Start

```bash
# ✅ GOOD
rate_limit_guard || exit 1

# ❌ BAD
# No rate limit check
```

---

### 2. Add Delays in Loops

```bash
# ✅ GOOD
for issue in $issues; do
    gh api "issues/$issue"
    rate_limit_delay
done

# ❌ BAD
for issue in $issues; do
    gh api "issues/$issue"  # No delay - burst traffic
done
```

---

### 3. Use Batch APIs When Possible

```bash
# ✅ GOOD - Single GraphQL query
gh api graphql -f query='query {
    repository(...) {
        issues(first: 100) { nodes { number title } }
    }
}'

# ❌ BAD - 100 individual calls
for i in $(seq 1 100); do
    gh issue view "$i"
done
```

---

### 4. Implement Retry Logic

```bash
# ✅ GOOD
retry_with_backoff gh api "endpoint"

# ❌ BAD
gh api "endpoint"  # No retry on transient failures
```

---

### 5. Show Rate Limit Summary

```bash
# ✅ GOOD
rate_limit_summary  # User sees impact

# ❌ BAD
# No visibility into rate limit usage
```

---

## Advanced: Custom Rate Limit Strategies

### Strategy 1: Adaptive Delays

Increase delay as rate limit decreases:

```bash
adaptive_delay() {
    local remaining=$(gh api rate_limit --jq '.rate.remaining')

    if [[ $remaining -lt 50 ]]; then
        rate_limit_delay 2.0  # 2s delay when critical
    elif [[ $remaining -lt 200 ]]; then
        rate_limit_delay 1.0  # 1s delay when low
    else
        rate_limit_delay 0.5  # 0.5s delay when OK
    fi
}

for issue in $issues; do
    gh api "issues/$issue"
    adaptive_delay
done
```

---

### Strategy 2: Batch Processing with Checkpoints

```bash
BATCH_SIZE=20
CHECKPOINT_INTERVAL=5

process_batch() {
    local start=$1
    local end=$2

    for i in $(seq $start $end); do
        process_issue "$i"
        rate_limit_delay
    done

    # Checkpoint: check rate limit
    check_rate_limit
    if [[ $? -eq 2 ]]; then
        echo "Rate limit critical - pausing"
        return 1
    fi
}

# Process in batches
for batch in $(seq 0 $CHECKPOINT_INTERVAL $total); do
    process_batch $batch $((batch + BATCH_SIZE))

    # Show progress and rate limit
    rate_limit_summary
done
```

---

### Strategy 3: Parallel Processing with Rate Limiting

```bash
# Use GNU parallel with rate limiting
export -f rate_limit_delay

parallel --delay 0.5 --jobs 3 \
    'gh api "issues/{}" && rate_limit_delay' \
    ::: $(seq 1 100)
```

**Note**: Parallel processing increases complexity. Use with caution.

---

## References

- [GitHub REST API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [GitHub GraphQL API Rate Limits](https://docs.github.com/en/graphql/overview/resource-limitations)
- [rate_limit.sh Source](../../scripts/github-projects/rate_limit.sh)
- [GitHub Projects Workflow](../contributing/GITHUB_PROJECTS.md)

---

## Quick Reference Card

| Function | Purpose | When to Use |
|----------|---------|-------------|
| `rate_limit_guard()` | Block if critical | **Every script start** |
| `rate_limit_delay()` | Add delay | **Every loop iteration** |
| `retry_with_backoff()` | Retry on failure | **Critical API calls** |
| `check_rate_limit()` | Check status | **Before batch operations** |
| `rate_limit_summary()` | Show usage | **Every script end** |

---

**Last Updated**: 2025-11-20
**Status**: Active
**Maintenance**: Update when rate limit thresholds change
