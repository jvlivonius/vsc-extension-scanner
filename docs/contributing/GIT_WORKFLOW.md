# Git Workflow Guide

Branching strategy and git workflow guidelines for VS Code Extension Scanner development.

---

## Table of Contents

- [Overview](#overview)
- [Branching Strategy](#branching-strategy)
- [Branch Types](#branch-types)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Feature Development Workflow](#feature-development-workflow)
- [Release Workflow](#release-workflow)
- [Hotfix Workflow](#hotfix-workflow)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Commit Message Standards](#commit-message-standards)
- [Branch Protection](#branch-protection)
- [Special Considerations](#special-considerations)
- [Migration Guide](#migration-guide)

---

## Overview

This project uses **Simplified GitHub Flow** as its branching strategy. This approach balances simplicity with safety through strong CI/CD and testing requirements.

**Core Principles:**
- **One main branch**: `main` is always production-ready and deployable
- **Short-lived feature branches**: Create focused branches for specific work
- **Pull request workflow**: All changes merge via reviewed PRs
- **Release via tags**: Stable versions marked with annotated git tags (`vX.Y.Z`)
- **Strong testing**: 628 tests must pass, 72%+ coverage, 0 security vulnerabilities

**Why GitHub Flow?**
- ✅ Simple for small teams (no `develop` or `release` branch overhead)
- ✅ Fast iteration (feature → PR → merge → release)
- ✅ Clear history (tags mark releases, branches for features)
- ✅ Strong safety net (comprehensive CI/CD and testing)
- ✅ Compatible with package distribution model (PyPI)

---

## Branching Strategy

```
main (protected, production-ready)
  ├── feature/add-csv-export
  ├── feature/improve-html-reports
  ├── bugfix/cache-corruption
  ├── hotfix/security-vulnerability
  ├── claude/automated-branch-name
  └── dependabot/pip/package-name
```

### Branch Flow

```
1. Create branch from main
        ↓
2. Develop with frequent commits
        ↓
3. Push and create PR
        ↓
4. CI runs (tests, security, coverage)
        ↓
5. Code review (1 approval required)
        ↓
6. Merge to main (squash or merge commit)
        ↓
7. Delete feature branch
        ↓
8. Release when ready (tag on main)
```

---

## Branch Types

### `main` Branch

**Purpose**: Production-ready code, always deployable to PyPI

**Characteristics:**
- Protected branch (requires PR, reviews, CI passing)
- All commits must come from merged PRs
- Direct pushes blocked
- Every commit should be releasable
- Tagged for releases (`vX.Y.Z`)

**Rules:**
- ❌ Never commit directly to main
- ❌ Never force push to main
- ✅ Merge only via approved PRs
- ✅ Ensure all CI checks pass before merge
- ✅ Tag for releases after merge

### `feature/*` Branches

**Purpose**: New features, enhancements, improvements

**Examples:**
- `feature/add-csv-export`
- `feature/improve-retry-logic`
- `feature/parallel-processing`

**Lifetime:** Days to 2 weeks maximum

**Merge Strategy:** Squash or merge commit (project preference)

### `bugfix/*` Branches

**Purpose**: Non-critical bug fixes

**Examples:**
- `bugfix/cache-corruption-on-interrupt`
- `bugfix/html-table-formatting`
- `bugfix/rate-limit-handling`

**Lifetime:** Hours to days

**Merge Strategy:** Merge commit (preserve bug fix history)

### `hotfix/*` Branches

**Purpose**: Critical security vulnerabilities or data-loss bugs

**Examples:**
- `hotfix/security-path-traversal`
- `hotfix/CVE-2024-12345`
- `hotfix/data-loss-on-crash`

**Lifetime:** Hours (expedited process)

**Merge Strategy:** Merge commit + immediate release

**Process:**
1. Branch from main
2. Fix with tests
3. Expedited PR review
4. Merge immediately
5. Release immediately

### `claude/*` Branches

**Purpose**: Claude Code automated work and AI-assisted development

**Examples:**
- `claude/create-vscan-prd-011CUNe8k7s3rGxcEUmMhyDF`
- `claude/code-optimization-review-011CUSHpEqua9cJXq4JsqaS5`

**Characteristics:**
- Auto-generated names by Claude Code
- Treated as feature branches
- Subject to same PR and review process

**Workflow:**
1. Claude Code creates branch automatically
2. Review changes carefully
3. Create PR with clear description
4. Merge after approval
5. Delete branch after merge

### `dependabot/*` Branches

**Purpose**: Automated dependency updates from Dependabot

**Examples:**
- `dependabot/pip/rich-gte-13.0.0-and-lt-15.0.0`
- `dependabot/pip/typer-0.13.1`

**Characteristics:**
- Auto-created by Dependabot
- Grouped updates (weekly)
- Auto-merged after CI passes (if configured)

**Workflow:**
1. Dependabot creates PR automatically
2. CI runs tests
3. Review changes (check CHANGELOG if available)
4. Merge promptly if CI passes
5. Branch auto-deleted

---

## Branch Naming Conventions

### Format Rules

```
<type>/<short-descriptive-name>

Where:
- type: feature | bugfix | hotfix | claude | dependabot
- name: lowercase, hyphen-separated, descriptive
```

### Examples

**✅ Good Names:**
- `feature/add-json-schema-validation`
- `bugfix/fix-unicode-handling`
- `hotfix/prevent-sql-injection`
- `feature/html-report-dark-mode`

**❌ Bad Names:**
- `fix-bug` (not descriptive enough)
- `feature/MyNewFeature` (use lowercase)
- `john-working-on-stuff` (not purpose-driven)
- `temp` (temporary branches should have clear purpose)

### Special Cases

**Research/Exploration:**
```
feature/explore-async-processing
feature/poc-graphql-api
```

**Documentation:**
```
feature/add-api-documentation
feature/improve-testing-guide
```

**Refactoring:**
```
feature/refactor-cache-manager
feature/extract-validation-utils
```

---

## Feature Development Workflow

### Step-by-Step Process

#### 1. Start from Updated Main

```bash
# Ensure you're on main and it's up to date
git checkout main
git pull origin main

# Verify you're starting clean
git status
git branch
```

#### 2. Create Feature Branch

```bash
# Create and checkout new feature branch
git checkout -b feature/your-feature-name

# Verify you're on the new branch
git branch
# * feature/your-feature-name
```

#### 3. Develop with Incremental Commits

```bash
# Make changes, test frequently
# Add changes selectively
git add -p  # Interactive staging

# Commit with meaningful message
git commit -m "feat(module): add capability X

- Implementation details
- Testing approach
- Performance considerations

Refs #42
"

# Continue development
# Commit frequently (5-10 commits per feature is normal)
```

#### 4. Keep Branch Updated

```bash
# Fetch latest main changes
git fetch origin main

# Rebase your feature branch (keeps history clean)
git rebase origin/main

# Or merge if rebase is problematic
git merge origin/main

# Resolve conflicts if any
# Test after updating
```

#### 5. Push and Create Pull Request

```bash
# Push feature branch to remote
git push -u origin feature/your-feature-name

# Create PR using GitHub CLI
gh pr create \
  --title "Add feature X" \
  --body "## Changes
- Added feature X
- Updated tests
- Updated documentation

## Testing
- All 628 tests pass
- Coverage: 73%+
- Security: 0 vulnerabilities

## Checklist
- [x] Tests added/updated
- [x] Documentation updated
- [x] CHANGELOG.md updated (if applicable)
- [x] Version bumped (if applicable)

Closes #42
"

# Or create via GitHub web interface
```

#### 6. Code Review and Iteration

```bash
# Address review feedback
# Make changes based on comments

# Commit review changes
git add .
git commit -m "review: address feedback on validation logic"

# Push updates
git push origin feature/your-feature-name

# PR automatically updates
```

#### 7. Merge and Cleanup

```bash
# After PR approval and CI passes
# Merge via GitHub web interface or CLI
gh pr merge --squash  # or --merge or --rebase

# Switch back to main locally
git checkout main
git pull origin main

# Delete local feature branch
git branch -d feature/your-feature-name

# Verify remote branch was auto-deleted
# Or delete manually if needed
git push origin --delete feature/your-feature-name
```

---

## Release Workflow

Releases are created from `main` branch using annotated git tags.

### Release Process

#### 1. Ensure Main is Ready

```bash
# Start on updated main
git checkout main
git pull origin main

# Verify branch is clean
git status

# Run full test suite
python3 -m pytest tests/
python3 tests/test_security_regression.py

# All 628 tests must pass
# Coverage must be 70%+
# Security tests must show 0 vulnerabilities
```

#### 2. Bump Version

```bash
# Update version across all files
python3 scripts/bump_version.py X.Y.Z

# Verify version consistency
python3 scripts/bump_version.py --check

# Expected: 3 auto-updated files + 2 manual files have matching version
```

#### 3. Update Documentation

With automated documentation updates:
- **Automated (3 files):** `README.md`, `CLAUDE.md`, `docs/project/PRD.md` - Updated by `--auto-update` flag
- **Manual (2 files):** `CHANGELOG.md` (add release section), `docs/archive/summaries/vX.Y.Z-release-notes.md` (create new)
- **Source:** `vscode_scanner/_version.py` - Auto-updated by bump_version.py

#### 4. Commit Release Changes

```bash
# Stage all release-related files (6 files total)
git add vscode_scanner/_version.py \
        README.md \
        CLAUDE.md \
        docs/project/PRD.md \
        CHANGELOG.md \
        docs/archive/summaries/vX.Y.Z-release-notes.md

# Create release commit
git commit -m "Release vX.Y.Z: Brief description

- Bumped version to X.Y.Z across all files
- Updated CHANGELOG.md with release notes
- Updated STATUS.md and README.md
- All 628 tests passing (coverage 72.60%)
- Security: 0 vulnerabilities

See CHANGELOG.md for full details
See docs/archive/summaries/vX.Y.Z-release-notes.md for comprehensive notes
"
```

#### 5. Create Annotated Tag

```bash
# Create annotated tag with release notes
git tag -a vX.Y.Z -m "Release vX.Y.Z

## Highlights
- Major feature or improvement
- Notable bug fix
- Performance enhancement

## Changes
### Added
- New feature descriptions

### Fixed
- Bug fix descriptions

### Changed
- Enhancement descriptions

See CHANGELOG.md for complete release notes
"

# Verify tag was created
git tag -l -n9 vX.Y.Z
```

#### 6. Push Commit and Tag

```bash
# Push release commit to main
git push origin main

# Push tag separately (important!)
git push origin vX.Y.Z

# Verify tag appears on GitHub
gh release view vX.Y.Z  # Should show error if not released yet
```

#### 7. Build and Create GitHub Release

```bash
# Clean build environment
rm -rf build/ dist/ *.egg-info

# Build distribution packages
python3 -m build

# Verify build artifacts
ls -lh dist/
# vscode_scanner-X.Y.Z-py3-none-any.whl
# vscode_scanner-X.Y.Z.tar.gz

# Create SHA256 checksums
cd dist/
sha256sum * > SHA256SUMS.txt
cd ..

# Create GitHub release
gh release create vX.Y.Z \
  dist/*.whl \
  dist/*.tar.gz \
  dist/SHA256SUMS.txt \
  --title "vX.Y.Z" \
  --notes-file docs/archive/summaries/vX.Y.Z-release-notes.md

# Or use web interface to create release from tag
```

#### 8. Verify Release

```bash
# Check GitHub release page
gh release view vX.Y.Z

# Test installation from PyPI (after upload)
python3 -m venv test_env
source test_env/bin/activate
pip install vscode-scanner==X.Y.Z
vscan --version
deactivate
rm -rf test_env
```

### Release Timing

**Semantic Versioning:**
- **Major (X.0.0)**: Breaking changes, incompatible API changes
- **Minor (0.X.0)**: New features, backward-compatible
- **Patch (0.0.X)**: Bug fixes, backward-compatible

**Release Frequency:**
- **Patch releases**: As needed (hotfixes, bug fixes)
- **Minor releases**: Every 1-4 weeks (new features)
- **Major releases**: Rare (breaking changes)

---

## Hotfix Workflow

Critical issues requiring immediate release outside normal cycle.

### When to Use Hotfix

**Valid Hotfix Scenarios:**
- 🔴 Security vulnerabilities (CVEs)
- 🔴 Data loss or corruption bugs
- 🔴 Critical functionality completely broken
- 🔴 Dependency security issues

**Not Hotfix (use regular bugfix):**
- 🟡 Minor bugs with workarounds
- 🟡 UI/UX issues
- 🟡 Performance degradation (unless severe)
- 🟡 Non-critical feature requests

### Hotfix Process

#### 1. Create Hotfix Branch from Main

```bash
# Always branch from main (production code)
git checkout main
git pull origin main

# Create hotfix branch with clear identifier
git checkout -b hotfix/security-CVE-2024-12345

# Or for data-loss bugs
git checkout -b hotfix/prevent-data-corruption
```

#### 2. Implement Fix with Tests

```bash
# Make minimal changes to fix issue
# Add regression test to prevent recurrence

# Example: Security fix
# 1. Fix the vulnerability in code
# 2. Add test to tests/test_security_regression.py
# 3. Verify security tests pass

python3 tests/test_security_regression.py
# Must show: 0 vulnerabilities

# Run full test suite
python3 -m pytest tests/
# All 628 tests must pass
```

#### 3. Bump Patch Version

```bash
# Hotfixes always bump patch version
# Current version: 3.5.4
# Hotfix version: 3.5.5

python3 scripts/bump_version.py 3.5.5
python3 scripts/bump_version.py --check
```

#### 4. Create Expedited PR

```bash
# Push hotfix branch
git push -u origin hotfix/security-CVE-2024-12345

# Create PR with security label
gh pr create \
  --title "SECURITY: Fix CVE-2024-12345 - Path Traversal" \
  --label "security" \
  --label "hotfix" \
  --body "## Security Issue
CVE-2024-12345: Path traversal vulnerability in file validation

## Fix
- Strengthened path validation in utils.py:validate_path()
- Added case-insensitive checks for encoded paths
- Added regression test to test_security_regression.py

## Verification
- All 628 tests pass
- Security tests: 0 vulnerabilities
- Added specific test for CVE-2024-12345

## Impact
- High severity
- Affects all versions < 3.5.5
- Requires immediate release

## Release Plan
1. Merge this PR immediately after approval
2. Release v3.5.5 within 24 hours
3. Notify users via GitHub Security Advisory
"
```

#### 5. Expedited Review and Merge

- **Fast-track review** (within hours, not days)
- **Single approver sufficient** for critical security fixes
- **Merge immediately** after CI passes
- **No squash** (preserve hotfix commit for audit trail)

```bash
# After approval, merge with merge commit
gh pr merge --merge
```

#### 6. Immediate Release

Follow release workflow immediately:
1. Verify main updated
2. Tag release (annotated with security notes)
3. Build packages
4. Create GitHub release
5. Upload to PyPI (if applicable)
6. Create GitHub Security Advisory (for vulnerabilities)

```bash
# Quick release commands
git checkout main
git pull origin main
git tag -a v3.5.5 -m "Hotfix v3.5.5: Security fix CVE-2024-12345"
git push origin v3.5.5
python3 -m build
gh release create v3.5.5 dist/* --notes "Security hotfix for CVE-2024-12345"
```

---

## Pull Request Guidelines

### PR Template

Use `.github/pull_request_template.md` for consistent PRs.

### PR Title Format

```
<type>(<scope>): <subject>

Examples:
- feat(scanner): add parallel processing support
- fix(cache): prevent corruption on interrupt
- docs(api): update vscan.dev integration guide
- hotfix(security): fix path traversal CVE-2024-12345
```

### PR Description Requirements

**Minimum sections:**
1. **Changes**: What was changed and why
2. **Testing**: How changes were tested
3. **Checklist**: Pre-merge verification items

**Example:**

```markdown
## Changes
- Added parallel processing using ThreadPoolExecutor
- Configurable worker count (1-5)
- Thread-safe statistics tracking

## Testing
- All 628 tests pass
- Added 12 new tests for parallel execution
- Tested with 1, 3, and 5 workers
- Coverage increased from 70% to 73%

## Checklist
- [x] Tests added/updated
- [x] All tests passing
- [x] Documentation updated
- [x] CHANGELOG.md updated
- [x] Version bumped (if needed)
- [x] Security tests pass (0 vulnerabilities)

Closes #42
```

### Review Requirements

**Before Requesting Review:**
- ✅ All CI checks passing (tests, security, coverage)
- ✅ Branch up to date with main
- ✅ Self-review completed (read your own diff)
- ✅ Documentation updated
- ✅ Tests added for new functionality

**During Review:**
- Respond to feedback promptly
- Push updates to same branch (PR updates automatically)
- Re-request review after changes
- Use "resolve conversation" when addressed

**Merge Criteria:**
- ✅ 1+ approvals (2 for major changes)
- ✅ All CI checks passing
- ✅ No unresolved conversations
- ✅ Branch up to date with main
- ✅ No merge conflicts

---

## Commit Message Standards

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: New feature
- `fix`: Bug fix
- `hotfix`: Critical security/data fix
- `docs`: Documentation only
- `style`: Formatting, whitespace, etc.
- `refactor`: Code restructuring (no behavior change)
- `perf`: Performance improvement
- `test`: Adding/updating tests
- `chore`: Maintenance (deps, build, etc.)

### Scope (Optional)

Module or component affected:
- `scanner`, `cache`, `api`, `cli`, `display`, `config`, `utils`, etc.

### Subject

- Imperative mood ("add" not "added" or "adds")
- Lowercase first letter
- No period at end
- Max 72 characters
- Descriptive and clear

### Body (Optional)

- Explain **what** and **why** (not how)
- Wrap at 72 characters
- Separate from subject with blank line
- Use bullet points for multiple changes

### Footer (Optional)

- Reference issues: `Refs #42`, `Closes #42`
- Breaking changes: `BREAKING CHANGE: description`
- Co-authors: `Co-authored-by: Name <email>`

### Examples

**Simple commit:**
```
feat(cli): add --workers flag for parallel processing
```

**Detailed commit:**
```
feat(scanner): implement parallel extension scanning

- Add ThreadPoolExecutor with configurable workers (1-5)
- Thread-safe statistics tracking with locks
- Default 3 workers (4.88x speedup measured)
- Update display to show parallel progress

Performance testing showed 4.88x faster scanning with 3 workers
compared to sequential processing (5 extensions: 16.79s → 3.44s).

Refs #42
```

**Bug fix:**
```
fix(cache): prevent corruption when process interrupted

- Add atomic write operations for cache updates
- Use temporary files with rename
- Add corruption detection on load
- Graceful fallback to empty cache

Fixes issue where SIGINT during cache write left database corrupted.

Closes #128
```

**Security hotfix:**
```
hotfix(utils): prevent case-insensitive path traversal

- Add lowercase normalization to validate_path()
- Block %2F and %5C encoded path separators
- Add regression test for CVE-2024-12345

SECURITY: CVE-2024-12345 - High severity path traversal
Users should upgrade to v3.5.5 immediately.

Fixes CVE-2024-12345
```

---

## Branch Protection

### Main Branch Protection Rules

Configure via **GitHub Settings → Branches → Branch protection rules**

#### Required Settings

**Require pull request reviews:**
- ✅ Require approvals: **1**
- ✅ Dismiss stale reviews when new commits pushed
- ✅ Require review from Code Owners (if CODEOWNERS file exists)

**Require status checks:**
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- **Required checks:**
  - `security-scan` (Bandit, Safety, pip-audit)
  - `coverage-test` (minimum 70% coverage)
  - `test` (all 628 tests must pass)
  - `semgrep` (static analysis)

**Require merge queue:** (optional, for higher traffic)
- ⬜ Enable merge queue (not needed for current team size)

**Require deployments:**
- ⬜ Not applicable (package distribution, not deployment)

**Rules applied to administrators:**
- ✅ Include administrators (no one bypasses)

**Restrict pushes:**
- ✅ Restrict who can push to matching branches
- ✅ Only allow pull requests (no direct pushes)

**Allow force pushes:**
- ❌ Do not allow force pushes

**Allow deletions:**
- ❌ Do not allow branch deletion

### GitHub CLI Configuration

```bash
# Install gh CLI if not already installed
# https://cli.github.com/

# Configure branch protection
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "security-scan",
      "coverage-test",
      "test",
      "semgrep"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismissal_restrictions": {},
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

### Verification

```bash
# View current protection rules
gh api repos/:owner/:repo/branches/main/protection

# Test protection (should fail)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test: should fail"
git push origin main
# Expected: remote rejected (protected branch)
```

---

## Special Considerations

### Claude Code Integration

**Branch Pattern:** `claude/*`

**Workflow:**
1. Claude Code creates branch automatically with generated name
2. Treat as feature branch (subject to same PR process)
3. Review changes carefully (AI-assisted code needs human verification)
4. Create PR with clear description of changes
5. Ensure all tests pass
6. Merge after approval
7. Delete branch after merge

**Best Practices:**
- Review all Claude Code changes before committing
- Add test coverage for Claude-generated code
- Verify documentation accuracy
- Check for over-engineering or scope creep
- Ensure code follows project patterns

### Dependabot Integration

**Branch Pattern:** `dependabot/*`

**Existing Configuration:** `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      minor-and-patch:
        update-types: ["minor", "patch"]
```

**Workflow:**
1. Dependabot creates PR automatically (weekly)
2. CI runs full test suite
3. Review CHANGELOG of updated package (if available)
4. Check for breaking changes
5. Merge if CI passes and no breaking changes
6. Branch auto-deleted after merge

**Handling Failures:**
- If CI fails, investigate compatibility issues
- Check for deprecated API usage
- Update code if needed
- Consider pinning version if major issues

### Release Branches (Not Used)

**Why we don't use release branches:**
- Small team (no parallel release development needed)
- Package distribution (users upgrade, no long-term support needed)
- Fast iteration (releases are frequent and low-risk)
- Strong CI/CD (comprehensive testing before every merge)

**If you need to support old versions:**
- Create `support/vX.Y` branch from release tag
- Cherry-pick critical fixes
- Release as patch version
- Minimal maintenance (security fixes only)

---

## Migration Guide

### From Current State to GitHub Flow

#### Step 1: Clean Up Current Work

```bash
# You may be on a claude/* or feature branch
git status

# Complete current work
git add .
git commit -m "..."

# Push branch
git push origin HEAD
```

#### Step 2: Ensure Main is Default

```bash
# Check current default branch
gh repo view --json defaultBranchRef

# If not main, set it
gh repo edit --default-branch main
```

#### Step 3: Enable Branch Protection

Follow instructions in [Branch Protection](#branch-protection) section.

#### Step 4: Start Using New Workflow

```bash
# All new work starts from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-new-feature

# Develop, commit, push, create PR
```

#### Step 5: Clean Up Old Branches

```bash
# List all local branches
git branch

# Delete merged local branches
git branch -d old-feature-branch

# List all remote branches
git branch -r

# Delete merged remote branches
git push origin --delete old-feature-branch
```

### Common Scenarios

**Scenario: I'm in the middle of a feature on a different branch**

```bash
# Option 1: Finish and merge current work first
git add .
git commit -m "Complete feature X"
git push origin feature/my-feature
gh pr create
# Merge PR, then start fresh

# Option 2: Continue on current branch, follow new workflow
# Use new workflow for next feature
```

**Scenario: I have multiple WIP branches**

```bash
# Prioritize and complete one at a time
# Create PRs for each
# Merge sequentially
# Clean up as you go
```

**Scenario: I need to fix a bug while working on a feature**

```bash
# Option 1: Complete feature first, then fix bug
# (if bug is not urgent)

# Option 2: Stash feature work, fix bug, resume feature
git stash
git checkout main
git pull
git checkout -b bugfix/urgent-issue
# Fix bug, commit, push, PR, merge
git checkout feature/my-feature
git merge main  # Get bug fix
git stash pop
# Continue feature work
```

---

## Quick Reference

### Common Commands

```bash
# Start new feature
git checkout main && git pull && git checkout -b feature/name

# Save work in progress
git add . && git commit -m "wip: description"

# Update feature branch with latest main
git fetch origin main && git rebase origin/main

# Create PR
gh pr create --title "Title" --body "Description"

# Check PR status
gh pr status

# Merge PR
gh pr merge --squash

# Clean up after merge
git checkout main && git pull && git branch -d feature/name

# Create release
python3 scripts/bump_version.py X.Y.Z && \
git add . && \
git commit -m "Release vX.Y.Z" && \
git tag -a vX.Y.Z -m "Release vX.Y.Z" && \
git push origin main && \
git push origin vX.Y.Z
```

### Troubleshooting

**Problem: Can't push to main**
```
Solution: This is correct! Create a feature branch instead.
git checkout -b feature/my-changes
git push -u origin feature/my-changes
```

**Problem: PR has conflicts with main**
```
Solution: Update your branch with latest main
git checkout feature/my-feature
git fetch origin main
git rebase origin/main
# Resolve conflicts
git push --force-with-lease origin feature/my-feature
```

**Problem: Made commits directly on main**
```
Solution: Move commits to feature branch
git branch feature/extracted-work
git reset --hard origin/main
git checkout feature/extracted-work
git push -u origin feature/extracted-work
```

**Problem: Need to undo last commit**
```
Solution: Use reset (if not pushed) or revert (if pushed)
# Not pushed yet
git reset HEAD~1

# Already pushed
git revert HEAD
```

---

## See Also

- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Complete 11-step release process
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Pre-release verification checklist
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version bumping with bump_version.py
- [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) - Documentation standards
- [../guides/TESTING.md](../guides/TESTING.md) - Testing requirements and patterns

---

**Last Updated:** 2025-01-31
**Version:** 1.0.0
