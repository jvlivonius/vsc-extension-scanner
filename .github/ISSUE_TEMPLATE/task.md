---
name: Implementation Task
about: Specific implementation task (broken down from feature or epic)
title: '[TASK] '
labels: task, P2-medium, complexity/M, requires:architecture, requires:security
assignees: jvlivonius
---

## Task Description

**Summary:** Brief one-sentence description of this specific task.

**Parent Feature:** #<issue-number> or link to feature plan

**Milestone:** vX.Y.Z

**Estimated Effort:** (XS: <2h, S: 2-4h, M: 4-8h, L: 1-2d, XL: >2d)

## Required Documentation

Before implementing this task, read and understand:

- [ ] [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) _(if modifying code structure)_
- [ ] [SECURITY.md](docs/guides/SECURITY.md) _(if handling user input or file operations)_
- [ ] [TESTING.md](docs/guides/TESTING.md) _(for test patterns and standards)_
- [ ] Additional docs:
  - _List any task-specific documentation_

## Dependencies

**Blocked By:** (Must be completed first)
- None

**Blocks:** (This must be completed before these can start)
- None

## Scope

### What to Implement

Describe the specific changes needed in detail:

**Files to Modify:**
- `path/to/file.py` - (description of changes)

**Functions/Classes to Add/Modify:**
- `ClassName.method_name()` - (description)

**Tests to Add:**
- `tests/test_module.py::test_function_name()` - (what to test)

### What NOT to Include

List anything explicitly out of scope for this task:
- (e.g., "Do not implement X, that's for issue #Y")

## Acceptance Criteria

This task is complete when:

- [ ] Documented requirements followed
- [ ] Code changes implemented as described
- [ ] Tests added/updated with passing status
- [ ] Coverage maintained (≥80% overall, ≥95% security modules)
- [ ] Pre-commit hooks pass (security, linting, formatting)
- [ ] Manual verification completed

**Security Requirements** (if applicable):
- [ ] `validate_path()` used for all file operations
- [ ] `sanitize_string()` used for all user input
- [ ] No path disclosure in error messages

**Architecture Requirements** (if applicable):
- [ ] Respects layer boundaries (P → A → I, one-way only)
- [ ] Follows command-query separation
- [ ] No infrastructure imports in presentation layer

## Implementation Guidance

### Technical Details

**Approach:**
Describe the recommended implementation approach:

1. Step 1
2. Step 2
3. Step 3

**Key Patterns to Follow:**
- (e.g., "Use AAA pattern for tests")
- (e.g., "Follow existing error handling pattern in scanner.py")

**Edge Cases:**
- List specific edge cases to handle and test

### Example Code (if applicable)

```python
# Provide example implementation or pattern to follow
def example_function(param: str) -> Result:
    """Example of what the implementation should look like."""
    pass
```

## Agent Implementation

**Agent-Ready:**
- [ ] Dependencies resolved (all blocked-by issues closed)
- [ ] Required documentation linked
- [ ] Implementation guidance provided
- [ ] Acceptance criteria clear

**To trigger implementation:**
```bash
/sc:implement-issue #<issue-number>
```

## Verification Steps

After implementation, verify manually:

1. Test command: `./vscan <command> <args>`
2. Expected behavior: (describe)
3. Verify logs/output: (describe)

## Notes

Add any additional context, gotchas, or considerations:
- (e.g., "Be careful with thread safety in this module")
- (e.g., "This pattern is used elsewhere in scanner.py:450")
