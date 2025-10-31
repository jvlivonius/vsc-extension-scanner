# Pull Request

## Title Format
<!-- Use format: <type>(<scope>): <subject> -->
<!-- Examples:
  - feat(scanner): add parallel processing support
  - fix(cache): prevent corruption on interrupt
  - docs(api): update vscan.dev integration guide
  - hotfix(security): fix path traversal vulnerability
-->

## Changes
<!-- Describe what was changed and why -->
<!-- Be specific about the problem solved and the approach taken -->

**Summary:**
-

**Motivation:**
-

**Approach:**
-

## Testing
<!-- How were these changes tested? -->

**Test Coverage:**
- [ ] All existing tests pass (628 tests)
- [ ] New tests added (if applicable)
- [ ] Coverage maintained/improved (target: 70%+)
- [ ] Security tests pass (0 vulnerabilities)

**Manual Testing:**
-

**Test Commands:**
```bash
# Commands used for testing
python3 -m pytest tests/
python3 tests/test_security_regression.py
```

## Checklist
<!-- Verify all items before requesting review -->

**Code Quality:**
- [ ] Code follows project conventions and patterns
- [ ] No new warnings or errors
- [ ] No hardcoded values or magic numbers (use constants)
- [ ] Proper error handling implemented

**Testing:**
- [ ] All 628 tests passing
- [ ] New tests added for new functionality
- [ ] Edge cases covered
- [ ] Security tests pass (0 vulnerabilities)

**Documentation:**
- [ ] Code comments added for complex logic
- [ ] Docstrings updated/added for public functions
- [ ] README.md updated (if user-facing changes)
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Relevant docs in `docs/` updated

**Version & Release:**
- [ ] Version bumped (if applicable): `python3 scripts/bump_version.py X.Y.Z`
- [ ] Version consistency verified: `python3 scripts/bump_version.py --check`
- [ ] CHANGELOG.md entry added for version bump

**Architecture:**
- [ ] No layer violations (run `python3 tests/test_architecture.py`)
- [ ] Follows 3-layer architecture (Presentation → Application → Infrastructure)
- [ ] Uses proper validation (`validate_path()`, `sanitize_string()`)

**Git Workflow:**
- [ ] Branch is up to date with main
- [ ] Branch follows naming convention (feature/*, bugfix/*, hotfix/*)
- [ ] Commit messages follow standards (type(scope): subject)
- [ ] No merge conflicts

## Breaking Changes
<!-- List any breaking changes or migrations required -->
<!-- Remove this section if no breaking changes -->

**Breaking:**
-

**Migration Guide:**
-

## Related Issues
<!-- Link to related issues using GitHub keywords -->
<!-- Examples: Closes #42, Fixes #128, Refs #256 -->

Closes #

## Screenshots / Outputs
<!-- If applicable, add screenshots or command outputs -->
<!-- Especially useful for CLI changes or HTML report updates -->

```
# Paste relevant command output or screenshots here
```

## Additional Notes
<!-- Any additional context, concerns, or discussion points -->

---

## Reviewer Notes
<!-- For reviewers: focus areas, known limitations, questions -->

**Focus Areas:**
-

**Questions:**
-

---

**PR Type:** <!-- Select one -->
- [ ] Feature (new functionality)
- [ ] Bugfix (non-critical fix)
- [ ] Hotfix (critical security/data fix)
- [ ] Documentation
- [ ] Refactoring
- [ ] Performance
- [ ] Testing
- [ ] Chore (dependencies, build, etc.)
