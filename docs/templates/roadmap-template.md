# {Version} {Feature Name} Roadmap

<!--
ROADMAP TEMPLATE v1.0
Purpose: Create structured roadmaps optimized for /gh:issues-create command
Documentation: docs/contributing/DOCUMENTATION_STANDARDS.md § 11 Roadmap Documentation
Checklist: docs/contributing/ROADMAP_CHECKLIST.md

USAGE:
1. Copy this template to docs/project/ or docs/archive/plans/
2. Replace all {placeholders} with actual values
3. Remove sections marked (Optional) if not needed
4. Validate with ROADMAP_CHECKLIST.md before creating issues
5. Run: /gh:issues-create create-from-plan <roadmap-file> --milestone vX.Y.Z
-->

**Status**: 📋 Planning | ✅ Complete | 🔄 In Progress
**Target Version**: vX.Y.Z
**Estimated Effort**: {total time estimate} ({breakdown: e.g., "1-2 days (6-8 hours)"})
**Impact**: {brief impact statement - what changes and why it matters}
**Type**: Major Feature | Enhancement | Bugfix | Refactoring | Documentation
**Breaking Changes**: YES | NO

<!--
FRONTMATTER NOTES:
- Status icons: 📋 Planning, 🔄 In Progress, ✅ Complete, ⏳ Pending
- Effort format: "X-Y days (A-B hours)" for clarity
- Impact: One sentence explaining user/system benefit
- Breaking Changes: YES requires major version bump
-->

---

## Executive Summary

<!--
PURPOSE: 3-5 sentence overview answering:
- What are we building/fixing?
- Why is this important?
- What's the scope?
- What's the expected outcome?

EXAMPLE:
"Complete Phase 1 (Data Visualization) from v5.x enhancement opportunities by implementing three presentation layer features: security notes display, score chart visualization, and enhanced metadata display. This work unlocks rich security data already stored in database (v4.0.0) by making it visible in CLI and HTML outputs. Expected outcome: Users gain actionable security insights without additional API calls or database changes."
-->

{3-5 sentence executive summary}

### Current State

<!--
DESCRIBE: What exists today
- Features/metrics/capabilities
- Known limitations
- User pain points
-->

**What Works**:
- {Current capability 1}
- {Current capability 2}

**What's Missing/Limited**:
- {Limitation 1}
- {Limitation 2}

### Problem Statement

<!--
WHY: Why does this need to change?
- User impact
- Technical debt
- Opportunity cost
-->

{Clear problem description}

### Goals

<!--
MEASURABLE: What specific outcomes define success?
- Use metrics where possible
- Make goals testable
-->

1. {Specific measurable goal 1}
2. {Specific measurable goal 2}
3. {Specific measurable goal 3}

### Outcomes (Optional - for completed roadmaps)

<!--
RESULTS: What was actually achieved (use past tense)
- Compare to original goals
- Unexpected benefits
- Lessons learned
-->

**Achieved**:
- ✅ {Actual outcome 1}
- ✅ {Actual outcome 2}

**Not Achieved** (with reasons):
- ❌ {Goal not met} - {why}

---

## Context & Background

<!--
TECHNICAL CONTEXT: Information needed before implementation
- Prerequisites
- Research findings
- Data availability
- Architectural constraints

KEEP CONCISE: Link to detailed docs rather than repeating
-->

### Data Availability (if applicable)

<!--
FOR DATA-DRIVEN FEATURES: What data exists, where, and in what format
-->

**Data Source**: {Database/API/File location}

**Data Format**:
```{language}
{
    "field1": "value",
    "field2": 123
}
```

**Access Pattern**: {How to retrieve this data}

### Current State Analysis (if applicable)

<!--
FOR IMPROVEMENTS: What's the current implementation
-->

| Aspect | Current State | Target State |
|--------|--------------|-------------|
| {Aspect 1} | {Current} | {Target} |
| {Aspect 2} | {Current} | {Target} |

### Architecture Notes

<!--
DESIGN CONTEXT: Architectural considerations
- Which layers affected (Presentation/Application/Infrastructure)
- Design patterns to follow
- Anti-patterns to avoid
-->

**Affected Layers**:
- {Layer}: {Why/how}

**Design Patterns**:
- {Pattern}: {Application}

**No Database Changes**: True | False
- {Explanation if applicable}

---

## Task Breakdown

<!--
CRITICAL FOR /gh:issues-create PARSING:

PHASE FORMAT (creates FEATURE issues):
  ## Phase N: Phase Name

TASK FORMAT (creates TASK issues):
  ### Task N.M: Task Name (effort estimate)

NUMBERED TASKS (alternative):
  ### N.M Task Name

EFFORT ESTIMATES (maps to complexity labels):
  - XS: <2 hours
  - S: 2-4 hours
  - M: 4-8 hours (0.5-1 day)
  - L: 1-2 days
  - XL: >2 days

EXAMPLE:
  ## Phase 1: Data Visualization

  ### Task 1.1: Display Security Notes (1-2 hours)

  Goal: Add security expert commentary to HTML reports

  #### Blocked By
  #140

  #### Changes Required
  ...
-->

## Phase 1: {Phase Name}

<!--
PHASE DESCRIPTION: High-level overview of this phase
- What's the theme?
- How does it fit in the larger roadmap?
- Dependencies on other phases?
-->

**Goal**: {Phase objective}

**Effort**: {Phase total time}

### Task 1.1: {Task Name} ({effort estimate})

<!--
TASK STRUCTURE: Each task becomes a GitHub issue

REQUIRED SECTIONS:
- Goal: One-sentence objective
- Implementation Details: What to build
- Testing Requirements: How to validate
- Acceptance Criteria: When is it done
- Files Modified: What changes

OPTIONAL SECTIONS:
- Blocked By: Dependencies (#### Blocked By heading with #N)
- Code Examples: Implementation guidance
- Notes: Special considerations
-->

**Goal**: {One-sentence task objective}

**Priority**: CRITICAL | HIGH | MEDIUM | LOW

**Complexity**: XS | S | M | L | XL

#### Blocked By

<!--
DEPENDENCY NOTATION (parsed by /gh:issues-create):
- Use "#### Blocked By" heading (level 4)
- List issue numbers on following lines
- Format: #N or comma-separated #N, #M
- Leave "None" if no dependencies
-->

None

#### Changes Required

**Files to Create**:
- `{file_path}` - {description}

**Files to Modify**:
- `{file_path}` - {what changes}
- `{file_path}` - {what changes}

**Tests to Add**:
- `{test_file}` - {test description}
- `{test_file}` - {test description}

**Configuration Changes** (if applicable):
- `{config_file}` - {what to update}

#### Implementation Details

<!--
GUIDANCE: Enough detail for implementation without being prescriptive
- Recommended approach
- Code examples (keep minimal but complete)
- Patterns to follow
- Anti-patterns to avoid
-->

{Implementation description}

**Code Example**:
```{language}
# Example implementation
{code snippet}
```

**Pattern to Follow**:
- {Existing pattern reference}

#### Testing Requirements

**Unit Tests** (`{test_file}`):
- [ ] `test_{feature}_with_{condition}()` - {what it tests}
- [ ] `test_{feature}_without_{condition}()` - {what it tests}
- [ ] `test_{feature}_edge_case()` - {what it tests}

**Integration Tests** (if applicable):
- [ ] {Integration scenario description}

**Manual Testing**:
1. {Step-by-step verification}
2. {Expected outcome}

#### Acceptance Criteria

<!--
TESTABLE: Each criterion should be verifiable
- Use checkboxes for GitHub issues
- Be specific and measurable
- Include both functional and non-functional requirements
-->

**Functional**:
- [ ] {Specific behavior works as designed}
- [ ] {Edge case handled correctly}

**Quality**:
- [ ] All new tests passing
- [ ] Code coverage maintained at {X}%+
- [ ] Pre-commit hooks passing
- [ ] 0 architecture violations

**User Experience**:
- [ ] {UX requirement met}

#### Files Modified

<!--
SUMMARY: Quick reference of file changes
- Helps with merge conflict prediction
- Enables parallelization analysis
-->

- `{file_path}`
- `{file_path}`

#### Tests Affected

<!--
IMPACT: Which test files need updates
-->

- `{test_file}` - {what needs updating}

#### Notes (Optional)

<!--
SPECIAL CONSIDERATIONS:
- Performance implications
- Security concerns
- Backward compatibility
- Migration requirements
-->

{Any special notes}

---

### Task 1.2: {Task Name} ({effort estimate})

<!--
REPEAT TASK STRUCTURE:
Copy the structure from Task 1.1 above
Adjust content for this specific task
-->

{Follow Task 1.1 structure}

---

## Phase 2: {Phase Name} (Optional)

<!--
MULTI-PHASE ROADMAPS:
Repeat Phase 1 structure for additional phases
Consider breaking very large roadmaps into separate files
-->

{Follow Phase 1 structure}

---

## Testing Strategy

<!--
COMPREHENSIVE TESTING PLAN:
- Overall test coverage goals
- Testing types and their purposes
- Test data requirements
- Performance benchmarks (if applicable)
-->

### Unit Tests (Target: {coverage %}+)

**Scope**: {What to unit test}

**Coverage Requirements**:
- New code: {X}%+ coverage
- Critical paths: {Y}%+ coverage
- Security functions: 95%+ coverage

**Test Data**:
- {Test data source or generation strategy}

### Integration Tests

**Scenarios**:
1. {Integration scenario 1}
2. {Integration scenario 2}

**Environment**:
- {Testing environment requirements}

### Manual Testing

**Test Cases**:

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| T1 | {Scenario} | {Steps} | {Expected} |
| T2 | {Scenario} | {Steps} | {Expected} |

**Visual Verification** (for UI changes):
- [ ] {Visual check 1}
- [ ] {Visual check 2}

### Performance Testing (Optional)

**Benchmarks**:
| Metric | Baseline | Target | Acceptable Range |
|--------|----------|--------|------------------|
| {Metric} | {Current} | {Goal} | {Min-Max} |

---

## Success Criteria

<!--
DEFINITION OF DONE:
When is this roadmap complete?
Organize by category (Functional/Quality/Performance/UX)
-->

### Functional Requirements

**Core Features**:
- [ ] {Feature 1 working as specified}
- [ ] {Feature 2 working as specified}

**Edge Cases**:
- [ ] {Edge case 1 handled}
- [ ] {Edge case 2 handled}

### Quality Requirements

**Code Quality**:
- [ ] All {N}+ existing tests passing
- [ ] New code has {X}%+ test coverage
- [ ] 0 security vulnerabilities (Semgrep, Bandit, pip-audit)
- [ ] 0 architecture violations
- [ ] Pre-commit hooks passing (Black, Pylint, Mypy)

**Standards Compliance**:
- [ ] Follows ARCHITECTURE.md patterns
- [ ] Meets SECURITY.md requirements
- [ ] Adheres to TESTING.md guidelines

### Performance Requirements (Optional)

**Speed**:
- [ ] {Operation} completes in <{time}
- [ ] No performance regression (±5% acceptable)

**Resource Usage**:
- [ ] Memory usage <{threshold}
- [ ] Disk space <{threshold}

### User Experience Requirements (Optional)

**Usability**:
- [ ] {UX criterion 1}
- [ ] {UX criterion 2}

**Accessibility**:
- [ ] Screen reader compatible
- [ ] Keyboard navigation works
- [ ] WCAG AA compliance

---

## Implementation Order

<!--
EXECUTION PLAN:
- Recommended sequence (consider dependencies)
- Parallelization opportunities
- Risk mitigation through ordering
-->

### Recommended Sequence

**Day/Phase 1** ({total time}):
1. Task 1.1 ({time}) - {rationale for order}
2. Task 1.2 ({time}) - {rationale for order}
3. Write tests for 1.1 and 1.2 ({time})

**Day/Phase 2** ({total time}):
4. Task 2.1 ({time})
5. Integration testing ({time})

### Parallelization Opportunities

**Independent Streams**:
- **Track 1**: Tasks {list} (no dependencies)
- **Track 2**: Tasks {list} (no dependencies)

**Merge Points**:
- After Track 1 + Track 2: {Integration point}

### Critical Path

**Blocking Chain**:
{Task A} → {Task B} → {Task C}

**Why**: {Dependency explanation}

---

## Risks & Mitigations

<!--
RISK MANAGEMENT:
Identify potential issues before they occur
Each risk should have severity, probability, and mitigation

SEVERITY: LOW | MEDIUM | HIGH | CRITICAL
PROBABILITY: LOW (<25%) | MEDIUM (25-75%) | HIGH (>75%)
-->

### Risk 1: {Risk Name}

**Severity**: LOW | MEDIUM | HIGH | CRITICAL

**Probability**: LOW | MEDIUM | HIGH

**Impact**: {What happens if this risk materializes}

**Mitigation**:
1. {Prevention strategy}
2. {Contingency plan}
3. {Rollback procedure if needed}

**Owner**: {Who is responsible for monitoring this risk}

### Risk 2: {Risk Name}

{Follow Risk 1 structure}

---

## Documentation Updates

<!--
DOCUMENTATION CHANGES:
All docs that need updating when this roadmap completes
-->

### Files to Update

**Required**:
- `STATUS.md` - Add v{X.Y.Z} release section with metrics
- `CHANGELOG.md` - Add v{X.Y.Z} entry with changes
- `CLAUDE.md` - Update {section} with {changes}

**Conditional** (if applicable):
- `PRD.md` - Update scope/features section
- `ARCHITECTURE.md` - Document new patterns
- `SECURITY.md` - Update security requirements

### New Documentation (Optional)

**Create**:
- `docs/{category}/{file}.md` - {purpose}

**Archive** (after completion):
- Move this roadmap to `docs/archive/plans/v{X.Y.Z}-{name}-roadmap.md`

---

## Release Checklist

<!--
RELEASE PROCESS:
Steps to execute when roadmap is complete
Separate pre-release, release, and post-release actions
-->

### Pre-Release Validation

- [ ] All tasks completed (verify in GitHub project)
- [ ] All sub-issues closed
- [ ] All tests passing (1,{N}+ tests)
- [ ] Test coverage ≥{X}% (current: {Y}%)
- [ ] 0 security vulnerabilities (run: `pip-audit`, `bandit`, `semgrep`)
- [ ] 0 architecture violations (run: `python tests/test_architecture.py`)
- [ ] Pre-commit hooks passing
- [ ] Manual testing complete (checklist above)
- [ ] Documentation updated (see Documentation Updates section)
- [ ] CHANGELOG.md drafted

### Release Process

**Version Bump**:
```bash
python3 scripts/bump_version.py {X.Y.Z}
```

**Git Operations**:
```bash
git add .
git commit -m "{type}({scope}): {description} (v{X.Y.Z})"
git tag -a v{X.Y.Z} -m "Release v{X.Y.Z}: {brief description}"
git push origin {branch-name}
git push origin --tags
```

**Build & Verify**:
```bash
python3 -m build
pip install dist/vscode_scanner-{X.Y.Z}-py3-none-any.whl
vscan --version  # Verify version number
```

**Create Pull Request**:
```bash
gh pr create \
  --title "Release v{X.Y.Z}: {Feature Name}" \
  --body "$(cat docs/archive/summaries/v{X.Y.Z}-release-notes.md)" \
  --milestone v{X.Y.Z}
```

### Post-Release Actions

- [ ] PR merged to main
- [ ] GitHub release created with tag v{X.Y.Z}
- [ ] Release notes published
- [ ] Archive roadmap: Move to `docs/archive/plans/`
- [ ] Create summary: `docs/archive/summaries/v{X.Y.Z}-release-notes.md`
- [ ] Update STATUS.md with "Released: {date}"
- [ ] Close milestone v{X.Y.Z}
- [ ] Announce release (if applicable)

---

## Appendix (Optional)

<!--
SUPPLEMENTARY INFORMATION:
Material that supports the roadmap but isn't essential for implementation
- Examples
- Benchmarks
- Research data
- Screenshots/mockups
-->

### Example Outputs

**Before** (current state):
```
{Current output example}
```

**After** (target state):
```
{Expected output example}
```

### Benchmarks (Optional)

**Performance Comparison**:

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| {Operation} | {Time} | {Time} | {%} |

### References

**Related Documents**:
- [Document Name](path/to/doc.md) - {Why relevant}

**External Resources**:
- [Resource Name](url) - {Why referenced}

**Related Issues**:
- #{N} - {Relationship}

---

## Document Metadata

**Template Version**: 1.0
**Created**: {YYYY-MM-DD}
**Last Updated**: {YYYY-MM-DD}
**Author**: {Name or "Claude Code"}
**Status**: {Planning | In Progress | Complete | Archived}

<!--
CHANGE LOG (for template updates):
- v1.0 (YYYY-MM-DD): Initial template creation
-->
