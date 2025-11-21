---
name: __implement-code-internal
description: "INTERNAL: Sub-agent for code implementation (called by orchestrator only)"
category: internal
complexity: advanced
mcp-servers: [serena, sequential-thinking]
personas: [python-expert, security-engineer, quality-engineer]
internal: true
---

# /gh:__implement-code - Implementation Sub-Agent (INTERNAL)

**⚠️ INTERNAL COMMAND**: This command is called ONLY by `/gh:implement-issue` orchestrator. **Not user-facing**.

## Purpose

Pure implementation context separated from orchestration responsibilities. Focuses exclusively on:
- Reading documentation
- Writing code
- Running tests
- Committing changes

**Never touches**: GitHub Projects status, issue metadata fetching, PR creation, dependency validation

## Usage

```bash
/gh:__implement-code --issue <number> --payload '<json>'
```

**Parameters:**
- `--issue <number>`: Issue number being implemented
- `--payload '<json>'`: JSON payload from orchestrator containing all context

## Payload Schema

```json
{
  "issue_number": 142,
  "issue_title": "Add CSV export functionality",
  "issue_type": "feature",
  "branch_name": "feature/add-csv-export",
  "required_docs": ["ARCHITECTURE.md", "SECURITY.md", "PRD.md"],
  "acceptance_criteria": [
    "Code implements feature as specified",
    "Security validation applied (validate_path, sanitize_string)",
    "Tests written with ≥80% coverage",
    "Architecture tests pass (0 violations)",
    "Pre-commit hooks pass"
  ],
  "milestone": "v3.8.0",
  "parent_feature": null
}
```

## Behavioral Flow

### 1. Parse Payload

```bash
# Extract payload from --payload argument
PAYLOAD_JSON="$1"
ISSUE_NUMBER=$(echo "$PAYLOAD_JSON" | jq -r '.issue_number')
BRANCH_NAME=$(echo "$PAYLOAD_JSON" | jq -r '.branch_name')
REQUIRED_DOCS=$(echo "$PAYLOAD_JSON" | jq -r '.required_docs[]')
ACCEPTANCE_CRITERIA=$(echo "$PAYLOAD_JSON" | jq -r '.acceptance_criteria[]')
```

**Validation**:
- Payload must be valid JSON
- Required fields must exist
- Branch name must match pattern: `^(feature|bugfix|hotfix)/.*`

### 2. Read Required Documentation

```bash
# Read each required doc to understand patterns and constraints
for doc in $REQUIRED_DOCS; do
    # Resolve doc path
    if [ -f "docs/guides/$doc" ]; then
        DOC_PATH="docs/guides/$doc"
    elif [ -f "docs/project/$doc" ]; then
        DOC_PATH="docs/project/$doc"
    elif [ -f "$doc" ]; then
        DOC_PATH="$doc"
    else
        return_error "documentation_not_found" "Required doc not found: $doc"
    fi

    # Read and extract key patterns
    # (Use Read tool to load into context)
    echo "Reading $DOC_PATH for implementation guidance..."
done
```

**Pattern Extraction**:
- ARCHITECTURE.md → 3-layer rules, import restrictions
- SECURITY.md → `validate_path()`, `sanitize_string()` usage
- PRD.md → Feature scope, requirements, constraints

### 3. Checkout/Create Branch

```bash
# Check if branch exists (may be created by orchestrator for features)
if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
    # Branch exists (feature implementation) - just checkout
    git checkout "$BRANCH_NAME"
else
    # New branch - create from main
    git checkout main && git pull
    git checkout -b "$BRANCH_NAME"
fi
```

### 4. Implement Code Changes

**Agent Personas Active**:
- `python-expert`: Production-quality code, SOLID principles, clean architecture
- `security-engineer`: `validate_path()`, `sanitize_string()`, OWASP compliance
- `quality-engineer`: Test strategy, edge case coverage, AAA pattern

**Implementation Guidelines**:
```python
# Follow patterns from documentation
# - Use validate_path() for all file operations
# - Use sanitize_string() for all user input
# - Follow 3-layer architecture (P → A → I)
# - Write tests alongside code (TDD approach)
# - Apply AAA pattern (Arrange-Act-Assert)
# - Use property-based tests for edge cases
```

**Acceptance Criteria Tracking**:
```bash
# As each criterion is met, update checkbox in issue
gh issue edit $ISSUE_NUMBER --body "$(update_checkbox_in_body "$criterion")"
```

### 5. Run Quality Gates

**Test Execution**:
```bash
# All tests must pass
python3 -m pytest tests/ -v

if [ $? -ne 0 ]; then
    return_failure "test_failure" "Tests failed - see output above"
fi
```

**Security Scan**:
```bash
# 0 vulnerabilities required
python3 tests/test_security.py

if [ $? -ne 0 ]; then
    return_failure "security_violation" "Security tests failed"
fi
```

**Architecture Validation**:
```bash
# 0 violations required
python3 tests/test_architecture.py

if [ $? -ne 0 ]; then
    return_failure "architecture_violation" "Architecture rules violated"
fi
```

**Pre-commit Hooks**:
```bash
# All hooks must pass
pre-commit run --all-files

if [ $? -ne 0 ]; then
    return_failure "precommit_failure" "Pre-commit hooks failed"
fi
```

**Coverage Analysis**:
```bash
# Coverage should be ≥80% (critical paths ≥95%)
coverage run -m pytest tests/
coverage report

COVERAGE_PERCENT=$(coverage report | tail -1 | awk '{print $4}' | sed 's/%//')
if [ "$COVERAGE_PERCENT" -lt 80 ]; then
    return_warning "low_coverage" "Coverage ${COVERAGE_PERCENT}% below 80% threshold"
fi
```

### 6. Commit Changes

```bash
# Generate commit message following conventional commits
COMMIT_MSG=$(cat <<EOF
$(generate_commit_type $ISSUE_TYPE)($(extract_scope $ISSUE_TITLE)): $(format_subject $ISSUE_TITLE)

$(generate_commit_body $ISSUE_NUMBER $ACCEPTANCE_CRITERIA)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)

# Commit all changes
git add .
git commit -m "$COMMIT_MSG"
```

**Commit Types**:
- `feature` → `feat`
- `bugfix` → `fix`
- `hotfix` → `hotfix`

### 7. Push Branch

```bash
# Push to remote (may already exist for features)
if git ls-remote --heads origin "$BRANCH_NAME" | grep -q "$BRANCH_NAME"; then
    # Branch exists remotely - just push
    git push origin "$BRANCH_NAME"
else
    # New branch - push with upstream
    git push -u origin "$BRANCH_NAME"
fi
```

### 8. Return Result to Orchestrator

**Success Report** (JSON):
```json
{
  "status": "success",
  "issue_number": 142,
  "branch_name": "feature/add-csv-export",
  "commit_sha": "abc123def456",
  "tests_passed": true,
  "coverage_percent": 87.5,
  "security_vulnerabilities": 0,
  "architecture_violations": 0,
  "acceptance_criteria_completed": [
    "Code implements feature as specified",
    "Security validation applied",
    "Tests written with ≥80% coverage",
    "Architecture tests pass",
    "Pre-commit hooks pass"
  ],
  "files_changed": [
    "vscode_scanner/csv_exporter.py",
    "tests/test_csv_exporter.py"
  ],
  "implementation_notes": "CSV exporter handles special characters with proper escaping via sanitize_string()"
}
```

**Failure Report** (JSON):
```json
{
  "status": "failed",
  "issue_number": 142,
  "error_type": "test_failure",
  "error_message": "2 tests failed in test_csv_exporter.py::test_special_characters",
  "partial_completion": {
    "branch_created": true,
    "code_written": true,
    "tests_written": true,
    "tests_passed": false,
    "coverage_percent": 45.2
  },
  "needs_human_help": true,
  "blocking_issue": "CSV escaping logic incorrect for nested quotes",
  "files_changed": [
    "vscode_scanner/csv_exporter.py",
    "tests/test_csv_exporter.py"
  ]
}
```

## Error Handling

### Documentation Not Found

```json
{
  "status": "failed",
  "error_type": "documentation_not_found",
  "error_message": "Required documentation not found: SECURITY.md",
  "partial_completion": {
    "branch_created": false,
    "code_written": false
  },
  "needs_human_help": true
}
```

### Branch Conflict

```json
{
  "status": "failed",
  "error_type": "git_conflict",
  "error_message": "Branch feature/add-csv-export has uncommitted changes",
  "partial_completion": {
    "branch_created": true,
    "code_written": false
  },
  "needs_human_help": true
}
```

### Test Failure

```json
{
  "status": "failed",
  "error_type": "test_failure",
  "error_message": "3 tests failed:\n- test_csv_export_unicode\n- test_csv_export_empty\n- test_csv_export_large_dataset",
  "partial_completion": {
    "branch_created": true,
    "code_written": true,
    "tests_written": true,
    "tests_passed": false
  },
  "needs_human_help": true,
  "blocking_issue": "Unicode handling in CSV export needs review"
}
```

## Tool Coordination

- **Read**: Documentation reading (`ARCHITECTURE.md`, `SECURITY.md`, `PRD.md`)
- **Edit/Write**: Code implementation following patterns from docs
- **Bash**: Git operations, test execution, quality gates
- **Serena MCP**: Symbol operations for refactoring (if needed)
- **sequential-thinking MCP**: Complex implementation strategy (if needed)

**Never Uses**:
- ❌ `gh project` commands (status management is orchestrator's job)
- ❌ `gh issue view` (metadata provided via payload)
- ❌ `gh pr create` (PR creation is orchestrator's job)

## Key Constraints

1. **Pure Implementation Context**: Sub-agent NEVER touches GitHub Projects or issue metadata
2. **Stateless Execution**: All context provided via payload, no state persistence in sub-agent
3. **Atomic Operations**: Either full success OR clean failure with diagnostic info
4. **Quality Gatekeeping**: All quality gates must pass before returning success
5. **Human Escalation**: Complex failures marked with `needs_human_help: true`

## Result Storage (Orchestrator Responsibility)

Sub-agent returns result JSON. Orchestrator is responsible for:
- Storing result in Serena memory (`orchestration_issue_<number>`)
- Creating PR from successful implementation
- Adding labels (`needs-human-help` for failures)
- Updating GitHub Projects status

**Sub-agent ONLY implements code, orchestrator handles everything else.**

## Boundaries

**Will**:
- Read required documentation and extract implementation patterns
- Create/checkout branch as specified by orchestrator
- Implement code following acceptance criteria and project standards
- Run comprehensive quality gates (tests, security, architecture, coverage)
- Commit changes with proper conventional commit messages
- Push branch to remote
- Return structured JSON result with implementation details

**Will Not**:
- Fetch issue metadata (provided via payload)
- Validate dependencies (orchestrator's job)
- Update GitHub Projects status (orchestrator's job)
- Create pull requests (orchestrator's job)
- Add issue labels (orchestrator's job)
- Make architectural decisions beyond documented patterns

## Testing This Command

**DO NOT invoke this command directly**. It is called ONLY by `/gh:implement-issue` orchestrator.

For testing purposes, you can invoke manually:
```bash
/gh:__implement-code --issue 142 --payload '{
  "issue_number": 142,
  "issue_title": "Add CSV export",
  "issue_type": "feature",
  "branch_name": "feature/add-csv-export",
  "required_docs": ["ARCHITECTURE.md", "SECURITY.md"],
  "acceptance_criteria": ["Tests pass", "Security validated"],
  "milestone": "v3.8.0",
  "parent_feature": null
}'
```
