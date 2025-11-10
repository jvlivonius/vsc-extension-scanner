---
name: implement-issue
description: "Implement GitHub issue with automated doc reading, testing, and PR creation"
category: workflow
complexity: advanced
mcp-servers: [serena, sequential-thinking]
personas: [python-expert, security-engineer, quality-engineer]
---

# /sc:implement-issue - Agent-Driven Issue Implementation

## Triggers
- GitHub issue marked as `agent-ready` and ready for implementation
- Manual trigger for automated issue implementation workflow
- Need for systematic issue resolution with full context

## Usage
```
/sc:implement-issue <issue-number> [--branch <name>] [--no-pr] [--dry-run]
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

### Pattern 3: Documentation Reading
```
Required Docs in issue (text field):
  "ARCHITECTURE.md, SECURITY.md, PRD.md"

Parse workflow:
  1. Extract from issue body: grep -oP '### Required Documentation.*?```.*?\n(.*?)\n```'
  2. Split by commas: split(',')
  3. Trim whitespace: map(trim)
  4. Resolve paths: map(doc => "docs/guides/${doc}")
  5. Read each doc in order
  6. Extract relevant patterns and constraints
  7. Apply patterns during implementation
  8. Verify compliance before PR creation

Example parsing:
  Input: "ARCHITECTURE.md, SECURITY.md, PRD.md"
  Output: ["docs/guides/ARCHITECTURE.md", "docs/guides/SECURITY.md", "docs/project/PRD.md"]
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
/sc:implement-issue 142

# Workflow:
1. Fetch issue #142 details
2. Validate dependencies (blocked-by issues are closed)
3. Read required docs: ARCHITECTURE.md, SECURITY.md
4. Create branch: feature/add-csv-export (from issue title)
5. Implement changes following acceptance criteria
6. Run tests and quality gates
7. Create PR: "feat(export): add CSV export functionality"
8. Link PR to issue: "Closes #142"
9. Update issue label: agent-implemented
10. Report: "Implemented #142, created PR #156"
```

### Custom Branch Name
```bash
/sc:implement-issue 143 --branch feature/custom-auth

# Uses custom branch name instead of auto-generated
# Rest of workflow identical
```

### Dry Run Validation
```bash
/sc:implement-issue 144 --dry-run

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
/sc:implement-issue 145 --no-pr

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

### Step 1: Fetch and Parse Issue
```bash
# Fetch issue JSON
ISSUE_JSON=$(gh issue view <number> --json title,body,labels,milestone,state)

# Extract metadata
TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
BODY=$(echo "$ISSUE_JSON" | jq -r '.body')
LABELS=$(echo "$ISSUE_JSON" | jq -r '.labels[].name')
MILESTONE=$(echo "$ISSUE_JSON" | jq -r '.milestone.title')
STATE=$(echo "$ISSUE_JSON" | jq -r '.state')

# Validate state
if [ "$STATE" != "OPEN" ]; then
  echo "Error: Issue #<number> is $STATE (must be OPEN)"
  exit 1
fi
```

### Step 2: Validate Dependencies
```bash
# Parse dependencies from body
BLOCKED_BY=$(echo "$BODY" | grep -oP 'Blocked By:.*#\K\d+' | tr '\n' ' ')

# Validate each dependency
for dep in $BLOCKED_BY; do
  DEP_STATE=$(gh issue view $dep --json state | jq -r '.state')
  if [ "$DEP_STATE" != "CLOSED" ]; then
    echo "Error: Dependency #$dep is $DEP_STATE (must be CLOSED)"
    exit 1
  fi
done
```

### Step 3: Read Required Documentation
```bash
# Parse required docs from issue body (YAML form text field)
# Look for "### Required Documentation" section followed by value
REQUIRED_DOCS_RAW=$(echo "$BODY" | grep -A 2 "### Required Documentation" | tail -1)

# Split comma-separated list and trim whitespace
IFS=',' read -ra DOC_ARRAY <<< "$REQUIRED_DOCS_RAW"

# Read each document
for doc_name in "${DOC_ARRAY[@]}"; do
  # Trim whitespace
  doc_name=$(echo "$doc_name" | xargs)

  # Resolve path based on doc name
  case "$doc_name" in
    ARCHITECTURE.md) doc_path="docs/guides/ARCHITECTURE.md" ;;
    SECURITY.md) doc_path="docs/guides/SECURITY.md" ;;
    PRD.md) doc_path="docs/project/PRD.md" ;;
    TESTING.md) doc_path="docs/guides/TESTING.md" ;;
    PERFORMANCE.md) doc_path="docs/guides/PERFORMANCE.md" ;;
    *) doc_path="docs/guides/$doc_name" ;;  # Default to guides/
  esac

  echo "Reading: $doc_path"
  # Use Read tool to load documentation
  # Extract patterns and constraints
done
```

### Step 4: Create Branch and Implement
```bash
# Generate branch name from issue
ISSUE_TYPE=$(echo "$LABELS" | grep -oE 'feature|bugfix|hotfix' | head -1)
BRANCH_NAME="${ISSUE_TYPE}/$(echo $TITLE | sed 's/\[.*\] //' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

# Create branch
git checkout main
git pull
git checkout -b "$BRANCH_NAME"

# Implement changes
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

# Generate PR description
PR_TITLE=$(echo "$TITLE" | sed 's/\[FEATURE\]/feat/' | sed 's/\[TASK\]/feat/' | sed 's/\[BUG\]/fix/')
PR_BODY="## Summary
Implements #<issue-number>

## Changes
$(git log --oneline main..$BRANCH_NAME)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests verified
- [ ] Manual testing completed

## Acceptance Criteria
$(echo "$BODY" | sed -n '/## Acceptance Criteria/,/##/p' | tail -n +2 | head -n -1)

Closes #<issue-number>"

# Create PR
gh pr create \
  --title "$PR_TITLE" \
  --body "$PR_BODY" \
  --milestone "$MILESTONE" \
  --label "$(echo $LABELS | tr ' ' ',')"

# Update issue label
gh issue edit <number> --add-label "agent-implemented"
```

## Error Handling

### Dependency Not Resolved
```
Error: Issue #142 has unresolved dependencies
  - #140: OPEN (must be CLOSED)
  - #141: OPEN (must be CLOSED)

Action: Wait for dependencies to be resolved, or remove dependency if incorrect
```

### Missing Required Documentation
```
Error: Issue #142 missing required documentation field
  Expected: "Required Documentation" field with comma-separated doc names
  Found: Empty or missing field

Action: Update issue with required documentation:
  Edit issue → Fill in "Required Documentation" field
  Example: "ARCHITECTURE.md, SECURITY.md, PRD.md"
```

### Test Failures
```
Error: Quality gates failed
  - pytest: 2 tests failed (tests/test_scanner.py::test_parallel)
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

## Integration with Project Workflow

### Feature Branch Workflow
```
1. User creates issue from feature plan: /sc:gh-projects create-from-plan
2. Issue created with metadata and acceptance criteria
3. User triggers implementation: /sc:implement-issue #142
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

**python-expert:**
- Production-quality Python code
- SOLID principles, clean architecture
- Comprehensive testing (pytest + hypothesis)

**security-engineer:**
- Security pattern validation
- OWASP compliance verification
- Threat model awareness

**quality-engineer:**
- Test strategy and edge case detection
- Coverage analysis and quality metrics
- Systematic testing approach

## References

- [GitHub Projects Workflow](../../contributing/GITHUB_PROJECTS.md)
- [Issue Templates](.github/ISSUE_TEMPLATE/)
- [Architecture Guide](../../guides/ARCHITECTURE.md)
- [Security Patterns](../../guides/SECURITY.md)
- [Testing Standards](../../guides/TESTING.md)
