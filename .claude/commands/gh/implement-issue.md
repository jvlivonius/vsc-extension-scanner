---
name: issues-implement
description: "Implement GitHub issue with automated doc reading, testing, and PR creation"
category: workflow
complexity: advanced
mcp-servers: [serena, sequential-thinking]
personas: [python-expert, security-engineer, quality-engineer]
---

# /gh:issues-implement - Agent-Driven Issue Implementation

## Triggers
- GitHub issue marked as `agent-ready` and ready for implementation
- Manual trigger for automated issue implementation workflow
- Need for systematic issue resolution with full context

## Usage

```bash
/gh:issues-implement <issue-number> [--branch <name>] [--no-pr] [--dry-run]
```

**Parameters:**
- `<issue-number>`: GitHub issue number to implement (e.g., 142)
- `--branch <name>`: Custom branch name (default: auto-generated from issue)
- `--no-pr`: Implement without creating PR (manual PR creation later)
- `--dry-run`: Validate prerequisites without implementing

## Behavioral Flow

1. **Fetch**: Retrieve issue details, metadata, acceptance criteria
2. **Validate**: Check dependencies resolved, required docs linked, prerequisites met
3. **Prepare**: Read required documentation, create feature branch, analyze scope
4. **Implement**: Code changes following acceptance criteria and project standards
5. **Verify**: Run tests, security scans, create PR with issue linkage

Key behaviors:
- Read all required documentation before implementation
- Validate all dependencies are closed before starting
- Follow acceptance criteria systematically
- Apply security patterns (`validate_path()`, `sanitize_string()`)
- Run full test suite and quality gates
- Create PR with comprehensive description and issue linkage
- Update issue with implementation status label

## Tool Coordination

- **gh CLI**: Issue fetching, PR creation (`gh issue view`, `gh pr create`)
- **Read**: Documentation reading, code analysis
- **Bash**: Git operations, test execution, quality gates
- **Edit/Write**: Code implementation, test creation
- **Serena MCP**: Symbol operations, refactoring, dependency tracking
- **sequential-thinking MCP**: Complex implementation strategy, architecture analysis

## Key Patterns

### Pattern 1: Issue Metadata Extraction

```bash
# Fetch issue details
gh issue view <number> --json title,body,labels,milestone,state

# Extract metadata:
- Title → branch name generation
- Body → parse dependencies, required docs, acceptance criteria
- Labels → determine type (feature, bugfix, hotfix)
- Milestone → link PR to same milestone
```

### Pattern 2: Dependency Validation

```
Dependencies in issue body:
  "Blocked By: #140, #141"

Validation:
  gh issue view 140 --json state  # Must be "closed"
  gh issue view 141 --json state  # Must be "closed"

If any open → Error: "Dependencies not resolved: #140 (open)"
```

**See**: [_gh-reference.md](_gh-reference.md#blocking-dependencies) for dependency verification

### Pattern 3: Documentation Reading

```
Required Docs in issue (text field):
  "ARCHITECTURE.md, SECURITY.md, PRD.md"

Parse workflow:
  1. Extract from issue body
  2. Split by commas, trim whitespace
  3. Resolve paths: "docs/guides/${doc}" or "docs/project/${doc}"
  4. Validate paths (no directory traversal)
  5. Read each doc with Read tool
  6. Extract relevant patterns and constraints
  7. Apply patterns during implementation
```

### Pattern 4: Acceptance Criteria Verification

```
Before creating PR, verify all checkboxes:
  - [ ] Code implements feature as specified → validate
  - [ ] Security validation applied → check validate_path() usage
  - [ ] Tests written with ≥80% coverage → run coverage report
  - [ ] Architecture tests pass → run test_architecture.py
  - [ ] Pre-commit hooks pass → run pre-commit
```

## Examples

### Basic Implementation

```bash
/gh:issues-implement 142

# Workflow:
1. Validate dependencies (runs validate-agent-ready.sh automatically)
2. Read required docs: ARCHITECTURE.md, SECURITY.md
3. Create branch: feature/add-csv-export (from issue title)
4. Implement changes following acceptance criteria
5. Run tests and quality gates
6. Create PR: "feat(export): add CSV export functionality"
7. Link PR to issue: "Closes #142"
8. Update issue label: agent-implemented
9. Report: "Implemented #142, created PR #156"
```

### Dry Run Validation

```bash
/gh:issues-implement 144 --dry-run

# Validates:
- Issue exists and is open
- Dependencies resolved
- Required docs are linked
- Acceptance criteria clear
- No blockers detected

# Reports: "Issue #144 ready for implementation" or lists blockers
```

### Implementation Without PR

```bash
/gh:issues-implement 145 --no-pr

# Implements changes and commits to branch
# Does not create PR (manual PR creation later)
# Useful for multi-issue PRs or when combining work
```

## Boundaries

**Will:**
- Read all required documentation and apply patterns systematically
- Validate dependencies and prerequisites before implementation
- Implement code following acceptance criteria and project standards
- Run comprehensive tests and quality gates
- Create PR with proper linkage to issue and milestone

**Will Not:**
- Implement issues with unresolved dependencies (must error)
- Skip required documentation reading
- Bypass security validation or quality gates
- Auto-merge PRs (human review always required)
- Close issues without PR merge (manual closure after review)

## Implementation Workflow

### Step 0: Validate Agent-Ready Status (AUTOMATED)

**IMPORTANT**: This validation is **automatically executed** at the start of the implementation workflow.

```bash
# AUTOMATED: Runs automatically when /gh:issues-implement is invoked
./scripts/github-projects/validate-agent-ready.sh <issue-number>

if [ $? -ne 0 ]; then
    echo "Error: Issue not ready for agent implementation"
    exit 1
fi
```

**What this validates:**
- Issue structure (title, body, docs, acceptance criteria)
- All dependencies are closed
- Required labels are set (priority, complexity, type)
- Required documentation files exist

**See**: [_gh-reference.md](_gh-reference.md#issue-validation-checklist) for validation details

### Step 1: Fetch and Parse Issue

```bash
# Fetch issue JSON
ISSUE_JSON=$(gh issue view <number> --json title,body,labels,milestone,state)

# Extract metadata
TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
BODY=$(echo "$ISSUE_JSON" | jq -r '.body')
LABELS=$(echo "$ISSUE_JSON" | jq -r '.labels[].name')
MILESTONE=$(echo "$ISSUE_JSON" | jq -r '.milestone.title')
```

### Step 2: Validate Dependencies

```bash
# Parse dependencies from body using safe extraction
parse_blocked_by() {
    local body="$1"
    local deps_section=$(echo "$body" | awk '/### Dependencies/,/^###/ {print}' | grep "Blocked By:")
    local issue_nums=$(echo "$deps_section" | grep -oE '#[0-9]+' | grep -oE '[0-9]+')
    echo "$issue_nums"
}

BLOCKED_BY=$(parse_blocked_by "$BODY")

# Validate each dependency is closed
for dep in $BLOCKED_BY; do
    DEP_STATE=$(gh issue view "$dep" --json state | jq -r '.state')
    if [ "$DEP_STATE" != "CLOSED" ]; then
        echo "Error: Dependency #$dep is $DEP_STATE (must be CLOSED)"
        exit 1
    fi
done
```

**See**: [_gh-reference.md](_gh-reference.md#blocking-dependencies) for dependency patterns

### Step 3: Read Required Documentation

```bash
# Validate and resolve documentation paths
validate_doc_path() {
    local doc_name="$1"
    doc_name=$(echo "$doc_name" | xargs)  # Trim whitespace

    # Resolve standard doc names
    case "$doc_name" in
        ARCHITECTURE.md) echo "docs/guides/ARCHITECTURE.md" ;;
        SECURITY.md) echo "docs/guides/SECURITY.md" ;;
        PRD.md) echo "docs/project/PRD.md" ;;
        TESTING.md) echo "docs/guides/TESTING.md" ;;
        *) echo "docs/guides/$doc_name" ;;
    esac
}

# Extract required docs from issue body
REQUIRED_DOCS_RAW=$(echo "$BODY" | awk '/### Required Documentation/,/^###/ {print}' | grep -v "^###" | head -1)

# Read each document with validation
IFS=',' read -ra DOC_ARRAY <<< "$REQUIRED_DOCS_RAW"
for doc_name in "${DOC_ARRAY[@]}"; do
  doc_path=$(validate_doc_path "$doc_name")
  echo "Reading: $doc_path"
  # Use Read tool to load documentation
done
```

### Step 4: Create Branch and Implement

```bash
# Generate branch name from issue
ISSUE_TYPE=$(echo "$LABELS" | grep -oE 'feature|bugfix|hotfix' | head -1)
BRANCH_NAME="${ISSUE_TYPE}/$(echo $TITLE | sed 's/\[.*\] //' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

# Create branch
git checkout main && git pull
git checkout -b "$BRANCH_NAME"

# Implement changes:
# - Follow acceptance criteria from issue body
# - Apply security patterns (validate_path, sanitize_string)
# - Follow 3-layer architecture rules
# - Write tests alongside implementation
```

### Step 5: Verify and Create PR

```bash
# Run quality gates
python3 -m pytest tests/  # All tests must pass
python3 tests/test_security.py  # 0 vulnerabilities
python3 tests/test_architecture.py  # 0 violations
pre-commit run --all-files  # Linting, formatting

# Create PR with issue linkage
gh pr create \
  --title "$(format_pr_title "$TITLE")" \
  --body "Closes #<issue-number>\n\n[Generated PR description]" \
  --milestone "$MILESTONE"

# Update issue label
gh issue edit <number> --add-label "agent-implemented"
```

**Label Sync**: After adding `agent-implemented` label, GitHub Actions will sync to project fields within 1-5 minutes.

**See**: [_gh-reference.md](_gh-reference.md#label-sync-timing) for sync automation details

## Error Handling

### Dependency Not Resolved

```
Error: Issue #142 has unresolved dependencies
  - #140: OPEN (must be CLOSED)

Action: Wait for dependencies to be resolved, or remove dependency if incorrect
```

### Missing Required Documentation

```
Error: Issue #142 missing required documentation field
  Expected: "Required Documentation" field with comma-separated doc names

Action: Update issue with required documentation
  Example: "ARCHITECTURE.md, SECURITY.md, PRD.md"
```

### Test Failures

```
Error: Quality gates failed
  - pytest: 2 tests failed
  - coverage: 78% (below 80% threshold)

Action: Fix failing tests and improve coverage before creating PR
Human escalation required for debugging
```

### Architecture Violations

```
Error: Architecture validation failed
  - Infrastructure layer importing Presentation (scanner.py:15)

Action: Refactor to respect 3-layer boundaries (P → A → I)
Review: docs/guides/ARCHITECTURE.md
```

**See**: [_gh-reference.md](_gh-reference.md#common-error-patterns) for full error reference

## Rate Limiting

**API Call Breakdown (per issue):**
- Fetch issue details: 1 call
- Fetch dependencies: 1-3 calls
- Validation: 3-5 calls
- Create PR: 1 call
- Update labels: 1 call
- **Total: ~8-15 API calls per issue**

**Best Practices:**
1. Check before batch operations: `gh api rate_limit`
2. Implement one issue at a time (not batch processing)
3. Monitor for rate limit warnings in output

**See**: [_gh-reference.md](_gh-reference.md#rate-limiting-essentials) for rate limit management

## Integration with Project Workflow

### Feature Branch Workflow

```
1. User creates issue: /gh:issues-create create-from-plan
2. Issue created with metadata and acceptance criteria
3. User triggers implementation: /gh:issues-implement #142
4. Agent implements, creates PR
5. Human reviews PR, requests changes if needed
6. Agent updates PR based on feedback
7. Human approves and merges PR
8. GitHub automation closes issue and updates project board
```

### Quality Gates Checklist

```
Before PR creation, verify:
✓ All dependencies resolved (blocked-by issues closed)
✓ Required documentation read and patterns applied
✓ Code implements all acceptance criteria
✓ Security patterns applied (validate_path, sanitize_string)
✓ Tests written with ≥80% coverage overall, ≥95% security
✓ Architecture tests pass (0 violations)
✓ Security tests pass (0 vulnerabilities)
✓ Pre-commit hooks pass (linting, formatting)
✓ Manual testing completed
```

## Configuration

### ~/.vscanrc Extension

```ini
[github_issues]
auto_branch_prefix = true
default_reviewer = jvlivonius
auto_run_tests = true
auto_add_labels = agent-implemented
require_passing_tests = true
```

## Agent Personas

This command activates specialized agent expertise:

**python-expert:** Production-quality Python code, SOLID principles, clean architecture
**security-engineer:** Security pattern validation, OWASP compliance verification
**quality-engineer:** Test strategy, edge case detection, coverage analysis

## References

- [_gh-reference.md](_gh-reference.md) - Shared GitHub command reference
- [GITHUB_RELATIONSHIPS.md](../../docs/contributing/GITHUB_RELATIONSHIPS.md) - Dependency management
- [GITHUB_PROJECTS.md](../../docs/contributing/GITHUB_PROJECTS.md) - Project workflow
- [ARCHITECTURE.md](../../docs/guides/ARCHITECTURE.md) - 3-layer architecture
- [SECURITY.md](../../docs/guides/SECURITY.md) - Security patterns
- [TESTING.md](../../docs/guides/TESTING.md) - Testing standards
