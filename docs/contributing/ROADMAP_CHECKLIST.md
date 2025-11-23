# Roadmap Validation Checklist

**Purpose**: Validate roadmap files before running `/gh:issues-create` command

**Template**: [docs/templates/roadmap-template.md](../templates/roadmap-template.md)

**Standards**: [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md) § 11 Roadmap Documentation

---

## Pre-Creation Validation

### ✅ Step 1: Structure Compliance

**Required Sections** (must be present):
- [ ] Header block with metadata (Status, Version, Effort, Impact, Type, Breaking Changes)
- [ ] Executive Summary with Current State, Problem, Goals
- [ ] Task Breakdown with proper heading hierarchy
- [ ] Testing Strategy
- [ ] Success Criteria
- [ ] Implementation Order (for multi-task roadmaps)
- [ ] Documentation Updates
- [ ] Release Checklist

**Optional Sections** (include if applicable):
- [ ] Context & Background (recommended for complex features)
- [ ] Risks & Mitigations (recommended for high-risk changes)
- [ ] Appendix with examples/benchmarks

### ✅ Step 2: Heading Hierarchy

**Phase Headings** (creates FEATURE issues):
```markdown
## Phase 1: Phase Name
## Phase 2: Another Phase
```
- [ ] Phases use level 2 headings (`##`)
- [ ] Phase numbers are sequential (1, 2, 3, not 1, 3, 5)
- [ ] Phase names are descriptive and unique

**Task Headings** (creates TASK issues):
```markdown
### Task 1.1: Task Name (effort estimate)
### Task 1.2: Another Task (effort estimate)
### Task 2.1: Task in Phase 2 (effort estimate)
```
- [ ] Tasks use level 3 headings (`###`)
- [ ] Task numbers follow pattern `N.M` (phase.task)
- [ ] Task numbers are sequential within each phase
- [ ] All tasks have effort estimates in parentheses

**Dependency Headings**:
```markdown
#### Blocked By
#123
#124, #125
```
- [ ] Dependencies use level 4 headings (`####`)
- [ ] Issue numbers formatted with `#` prefix
- [ ] Supports both line-separated and comma-separated formats

### ✅ Step 3: Metadata Completeness

**Frontmatter** (top of document):
- [ ] **Status**: One of (📋 Planning | ✅ Complete | 🔄 In Progress)
- [ ] **Target Version**: Format `vX.Y.Z`
- [ ] **Estimated Effort**: Includes both time range and total (e.g., "1-2 days (6-8 hours)")
- [ ] **Impact**: One-sentence benefit statement
- [ ] **Type**: One of (Major Feature | Enhancement | Bugfix | Refactoring | Documentation)
- [ ] **Breaking Changes**: YES or NO

**Effort Estimates** (in task headings):
- [ ] All tasks have effort estimates
- [ ] Format: `(X-Y hours)` or `(X days)` or `⏱️ XYmin`
- [ ] Estimates map to complexity:
  - XS: <2 hours
  - S: 2-4 hours
  - M: 4-8 hours (0.5-1 day)
  - L: 1-2 days
  - XL: >2 days

**Milestone**:
- [ ] Milestone exists (verify with: `gh api repos/:owner/:repo/milestones --jq '.[] | .title'`)
- [ ] Milestone format matches frontmatter `vX.Y.Z`

### ✅ Step 4: Task Content Quality

**Each Task Must Have**:
- [ ] **Goal**: One-sentence objective
- [ ] **Priority**: CRITICAL | HIGH | MEDIUM | LOW
- [ ] **Complexity**: XS | S | M | L | XL
- [ ] **Changes Required**: Files to create/modify/test
- [ ] **Implementation Details**: Enough guidance for implementation
- [ ] **Testing Requirements**: Unit/integration/manual tests specified
- [ ] **Acceptance Criteria**: Testable, measurable requirements
- [ ] **Files Modified**: List of affected files
- [ ] **Tests Affected**: List of test files

**Optional Task Sections** (include if applicable):
- [ ] Blocked By: Dependencies on other issues (use `#### Blocked By`)
- [ ] Code Examples: Implementation guidance
- [ ] Notes: Special considerations

### ✅ Step 5: Acceptance Criteria Quality

**Requirements**:
- [ ] All criteria are testable (not subjective)
- [ ] Each criterion is a single, specific requirement
- [ ] Criteria use checkboxes (`- [ ]`)
- [ ] Organized by category (Functional/Quality/Performance/UX)
- [ ] Include both positive cases ("X works") and negative cases ("handles Y gracefully")

**Examples**:

✅ **Good**:
- `[ ] Security notes visible in HTML reports when data present`
- `[ ] Gracefully handles missing data (shows fallback message)`

❌ **Bad**:
- `[ ] Make reports better` (not specific)
- `[ ] Everything works correctly` (not testable)

### ✅ Step 6: Testing Strategy

**Required Elements**:
- [ ] Unit test coverage target specified (e.g., "95%+")
- [ ] Unit tests listed with test names and purposes
- [ ] Integration tests described (if applicable)
- [ ] Manual testing steps provided (if applicable)
- [ ] Test data requirements documented

**Quality Checks**:
- [ ] Test names follow pattern: `test_{feature}_{condition}()`
- [ ] Each test has clear purpose description
- [ ] Coverage targets realistic (don't set 100% if not achievable)

### ✅ Step 7: Documentation References

**Required Documentation Links**:
- [ ] Template indicates which docs are required reading
- [ ] Links use relative paths (not absolute URLs)
- [ ] All referenced files exist

**Common Required Docs**:
- [ ] ARCHITECTURE.md (for architectural decisions)
- [ ] SECURITY.md (for security-sensitive changes)
- [ ] PRD.md (for scope validation)
- [ ] TESTING.md (for test patterns)
- [ ] HTML_REPORTS.md (for HTML report changes)

### ✅ Step 8: Risk Assessment (Recommended)

**For High-Impact Changes**:
- [ ] Risks identified with severity (LOW/MEDIUM/HIGH/CRITICAL)
- [ ] Probability assessed (LOW/MEDIUM/HIGH)
- [ ] Impact described (what happens if risk materializes)
- [ ] Mitigation strategies documented
- [ ] Rollback procedures specified (if needed)

**Common Risk Categories**:
- API changes (breaking vs. backward compatible)
- Database schema changes (migration required)
- File size increases (e.g., Chart.js inline)
- Browser compatibility (fallback mechanisms)
- Performance regressions (benchmark targets)

### ✅ Step 9: Implementation Order

**For Multi-Task Roadmaps**:
- [ ] Recommended sequence provided
- [ ] Dependencies between tasks documented
- [ ] Parallelization opportunities identified
- [ ] Critical path highlighted

**Quality Checks**:
- [ ] Sequence makes logical sense (dependencies resolved first)
- [ ] Time estimates add up to total effort
- [ ] Parallel tracks clearly separated

### ✅ Step 10: Release Checklist

**Required Elements**:
- [ ] Pre-release validation steps
- [ ] Version bump command
- [ ] Git commit/tag format
- [ ] Build & verify commands
- [ ] PR creation command
- [ ] Post-release actions

**Quality Checks**:
- [ ] Commands are copy-paste ready
- [ ] Placeholders clearly marked (e.g., `{X.Y.Z}`)
- [ ] References actual scripts/tools in project

---

## Parsing Compatibility

### ✅ Automated Checks

**Run These Commands**:

**Check heading hierarchy**:
```bash
grep -E "^#{1,4} " <roadmap-file> | head -20
# Should show: ## Phase, ### Task N.M pattern
```

**Check effort estimates**:
```bash
grep -E "^### (Task )?[0-9]+\.[0-9]+" <roadmap-file>
# Each task should have (X hours) or (X days)
```

**Check dependencies**:
```bash
grep -A 5 "#### Blocked By" <roadmap-file>
# Should show issue numbers #N after heading
```

**Verify milestone exists**:
```bash
gh api repos/:owner/:repo/milestones --jq '.[] | select(.title == "vX.Y.Z")'
# Should return milestone object, or empty if missing
```

### ✅ Manual Review

**Read Through**:
- [ ] Roadmap makes sense to a human reader
- [ ] Enough context for someone unfamiliar with the feature
- [ ] Examples are clear and complete
- [ ] No broken markdown formatting
- [ ] No placeholder text left (search for `{`)

**Test Parsing** (recommended):
```bash
# Dry-run to see what issues would be created
# (This command doesn't exist yet, but validates structure manually)
# Look for: Phase count, Task count, Dependencies
grep -E "^## Phase" <roadmap-file> | wc -l   # Phase count
grep -E "^### (Task )?[0-9]+\.[0-9]+" <roadmap-file> | wc -l  # Task count
grep "#### Blocked By" <roadmap-file> | wc -l  # Dependency count
```

---

## Common Pitfalls

### ❌ Avoid These Mistakes

**Heading Hierarchy Issues**:
- ❌ Using `# Phase` (level 1) - should be `## Phase` (level 2)
- ❌ Using `#### Task` (level 4) - should be `### Task` (level 3)
- ❌ Skipping levels (## → ####) - maintain hierarchy

**Task Numbering Issues**:
- ❌ Non-sequential numbers (1.1, 1.3, 1.5) - use 1.1, 1.2, 1.3
- ❌ Missing phase number (Task 1, Task 2) - use Task 1.1, Task 1.2
- ❌ Inconsistent format (Task 1.1 vs 1.1 Task) - pick one pattern

**Effort Estimate Issues**:
- ❌ Missing estimates - all tasks must have effort
- ❌ Vague estimates ("a while", "soon") - use specific time
- ❌ Outside parentheses: `Task 1.1 1-2 hours:` - use `(1-2 hours)`

**Dependency Issues**:
- ❌ Wrong heading level (`### Blocked By`) - must be `####`
- ❌ Missing `#` prefix (`Blocked By: 123`) - use `#123`
- ❌ Dependencies don't exist - verify issue numbers

**Metadata Issues**:
- ❌ Missing frontmatter fields - all required fields must be present
- ❌ Invalid status value - use exact formats (📋 Planning, etc.)
- ❌ Milestone doesn't exist - create before running command

**Content Issues**:
- ❌ No acceptance criteria - required for each task
- ❌ No testing strategy - required for validation
- ❌ Vague implementation details - provide enough guidance
- ❌ Broken links - verify all referenced files exist

---

## Pre-Command Checklist

**Before running** `/gh:issues-create create-from-plan <roadmap> --milestone vX.Y.Z`:

### Setup Validation

- [ ] Git status clean or changes committed
- [ ] On correct branch (not main)
- [ ] Milestone `vX.Y.Z` exists in GitHub
- [ ] GitHub project board exists (if using `--project-number`)
- [ ] Rate limit sufficient (`gh api rate_limit` shows >100 remaining)

### Roadmap Validation

- [ ] All checklist items above marked ✅
- [ ] Template placeholders replaced (`{Version}`, `{Feature Name}`, etc.)
- [ ] Heading hierarchy correct (## Phase, ### Task)
- [ ] All tasks have effort estimates
- [ ] All blocked-by dependencies use existing issue numbers
- [ ] Acceptance criteria are testable
- [ ] Documentation links are valid

### Command Preparation

**Review command options**:
```bash
# Standard usage
/gh:issues-create create-from-plan docs/project/roadmap.md --milestone vX.Y.Z

# With auto-linking (default)
/gh:issues-create create-from-plan docs/project/roadmap.md --milestone vX.Y.Z --auto-link

# Without auto-linking (manual relationships)
/gh:issues-create create-from-plan docs/project/roadmap.md --milestone vX.Y.Z --no-auto-link

# With specific project
/gh:issues-create create-from-plan docs/project/roadmap.md --milestone vX.Y.Z --project-number 3
```

**Expected Results**:
- 1 FEATURE issue per Phase (## Phase N)
- 1 TASK issue per Task (### Task N.M)
- Parent-child relationships set (if --auto-link)
- Blocked-by dependencies created (if specified)
- All issues linked to milestone
- All issues added to project board

### Post-Creation Validation

**Verify issues created**:
```bash
# List issues in milestone
gh issue list --milestone vX.Y.Z

# Check parent-child relationships
gh api repos/:owner/:repo/issues/{parent_number} --jq '.sub_issues_summary'

# Check dependencies
gh api repos/:owner/:repo/issues/{issue_number}/dependencies/blocked_by --jq '.[].number'
```

**Manual Checks**:
- [ ] All expected issues created (count matches roadmap)
- [ ] Issue titles match task headings
- [ ] Parent-child relationships correct
- [ ] Dependencies set correctly
- [ ] Labels applied (feature, task, complexity, priority)
- [ ] Milestone assigned to all issues

---

## Troubleshooting

### Issues Not Created

**Possible Causes**:
1. Heading hierarchy incorrect (wrong ## vs ### levels)
2. Milestone doesn't exist
3. Rate limit exceeded
4. Permission issues

**Solutions**:
```bash
# Verify heading structure
grep -E "^#{1,4} " <roadmap-file>

# Create milestone if missing
gh api repos/:owner/:repo/milestones -F title="vX.Y.Z" -F state="open"

# Check rate limit
gh api rate_limit

# Test permissions
gh api repos/:owner/:repo/issues --method POST -F title="Test" -F body="Test" --dry-run
```

### Relationships Not Set

**Possible Causes**:
1. Used `--no-auto-link` flag
2. Parent/child issues not all created
3. GraphQL API error

**Solutions**:
```bash
# Manual relationship setup
./scripts/github-projects/manage-issue-relationships.sh set-parent {parent} {child1} {child2}

# Verify relationships
gh api repos/:owner/:repo/issues/{parent_number} --jq '.sub_issues_summary'
```

### Dependencies Not Created

**Possible Causes**:
1. Wrong heading format (not `#### Blocked By`)
2. Issue numbers don't exist
3. REST API error

**Solutions**:
```bash
# Manual dependency setup
./scripts/github-projects/manage-issue-relationships.sh set-blocker {blocked} {blocker}

# Verify dependencies
gh api repos/:owner/:repo/issues/{issue_number}/dependencies/blocked_by
```

---

## Example Validation

**Good Roadmap Structure**:
```markdown
# v5.0.4 Phase 1 Data Visualization Roadmap

**Status**: 📋 Planning
**Target Version**: v5.0.4
**Estimated Effort**: 1-1.5 days (6-8 hours)
**Impact**: Complete Phase 1 data visualization
**Type**: Enhancement
**Breaking Changes**: NO

---

## Phase 1: Data Visualization

### Task 1.1: Display Security Notes (1-2 hours)

**Goal**: Add security notes to HTML reports

**Priority**: HIGH
**Complexity**: S

#### Blocked By

None

#### Changes Required

**Files to Modify**:
- `vscode_scanner/html_report_generator.py` - Add notes section

**Tests to Add**:
- `tests/test_html_report_generator.py` - Add note tests

#### Acceptance Criteria

- [ ] Notes visible in HTML reports
- [ ] Handles missing notes gracefully

---

### Task 1.2: Add Score Chart (2-4 hours)

{Follow same structure}
```

✅ **Passes all checks**:
- Correct heading hierarchy (## Phase, ### Task)
- All metadata present
- Effort estimates in parentheses
- Blocked By uses #### heading
- Acceptance criteria testable
- Files and tests specified

---

## References

- [Roadmap Template](../templates/roadmap-template.md)
- [Documentation Standards](DOCUMENTATION_STANDARDS.md) § 11
- [GitHub Issues Create Command](.claude/commands/gh/issues-create.md)
- [GitHub Relationships Guide](GITHUB_RELATIONSHIPS.md)
- [Example Roadmap](../project/v5.0.4-phase1-completion-roadmap.md)
