# Release Process

**Version:** 1.0
**Last Updated:** 2025-10-25
**Status:** Active Process

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Release Preparation](#phase-1-pre-release-preparation)
3. [Build & Package](#phase-2-build--package)
4. [Version Control](#phase-3-version-control)
5. [Post-Release](#what-happens-after-release)
6. [Quick Reference](#quick-reference)

---

## Overview

This document describes the complete, reproducible release process for the VS Code Extension Security Scanner. The process is divided into three main phases:

1. **Pre-Release Preparation** - Version updates, documentation, testing
2. **Build & Package** - Clean build, package verification
3. **Version Control** - Commit, tag, push

**Out of Scope:** Distribution and post-release communication are handled separately via [DISTRIBUTION.md](../../DISTRIBUTION.md).

**Key Documents:**
- [CHANGELOG.md](../../CHANGELOG.md) - Release history
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version management guide
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Printable checklist
- [release-notes-template.md](../templates/release-notes-template.md) - Template for release notes

---

## Phase 1: Pre-Release Preparation

### Step 1: Version Management

**Update version in single source of truth:**

```bash
# 1.1 Bump version
python3 scripts/bump_version.py X.Y.Z

# 1.2 Verify consistency across ALL files
python3 scripts/bump_version.py --check
```

**What `--check` verifies:**
- ✅ Python files import from `_version.py` (no hardcoded versions)
- ✅ `README.md` version badge/number matches
- ✅ `CLAUDE.md` "Current Status" section matches
- ✅ `docs/project/STATUS.md` current version matches
- ✅ `docs/project/PRD.md` version number matches
- ✅ `DISTRIBUTION.md` version examples match
- ✅ `setup.py` and `pyproject.toml` use dynamic versioning

**Expected output:**
```
Current version: X.Y.Z
Schema version: 2.1

Python Files:
✓ vscode_scanner/__init__.py: Uses centralized version
✓ vscode_scanner/vscan.py: Uses centralized version
...

Documentation Files:
✓ README.md: Version X.Y.Z matches
✓ CLAUDE.md: Version X.Y.Z matches
✓ docs/project/STATUS.md: Version X.Y.Z matches
✓ docs/project/PRD.md: Version X.Y.Z matches
✓ DISTRIBUTION.md: All examples use X.Y.Z

✓ All files use consistent versioning!
```

---

### Step 2: Documentation Updates

Update the following files **in this order:**

#### 2.1 CHANGELOG.md (Root)

Add new release section:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature descriptions

### Changed
- Changes in existing functionality

### Fixed
- Bug fixes

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Security
- Security vulnerabilities fixed
```

**Important:**
- Use [Keep a Changelog](https://keepachangelog.com/) format
- Add to top of file (after `[Unreleased]` section)
- Include migration notes for breaking changes
- Update comparison links at bottom

#### 2.2 README.md (Root)

- **Line 7:** Update version number/badge
- Update installation examples (if changed)
- Update feature list (if new features added)
- Verify "What's New" section (if exists)

#### 2.3 CLAUDE.md (Root)

- **Line ~21:** Update "Current Status" section
  ```markdown
  **Current Status:** vX.Y.Z - {Description}
  ```
- **Lines ~23-95:** Move in-progress work to "Previous Updates"
- Add new release to "Latest Updates" section
- Ensure all version references match `_version.py`

#### 2.4 DISTRIBUTION.md (Root)

- Update version references in installation examples
- Update wheel filename examples: `vscode_extension_scanner-X.Y.Z-py3-none-any.whl`
- Update troubleshooting section (if new issues discovered)

#### 2.5 docs/project/STATUS.md

- **Line 5:** Update current version: `**Current Version:** X.Y.Z`
- **Line 6:** Update schema version (if changed): `**Schema Version:** 2.1`
- Add new release section at top
- Update "Next Release" section

#### 2.6 docs/project/PRD.md

- Update version number (if requirements changed)
- Update feature scope (if applicable)
- Update constraints (if applicable)
- Update success criteria (if changed)

#### 2.7 docs/README.md

- Verify navigation table is current
- Verify all links work
- Update if new documentation added
- Check version references

#### 2.8 Release Notes (Recommended)

Create: `docs/archive/summaries/vX.Y.Z-release-notes.md`

Use template: [release-notes-template.md](../templates/release-notes-template.md)

Include:
- Summary and key features
- Bug fixes and improvements
- Breaking changes (with migration guide)
- Installation/upgrade instructions
- Known issues

#### 2.9 Archive Cleanup (if completing a roadmap)

If this release completes a versioned roadmap:

```bash
# Move roadmap to archive
mv docs/project/vX.Y-ROADMAP.md docs/archive/plans/

# Update archive index
# Edit docs/archive/README.md and add entry
```

Ensure archived documents follow [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) naming scheme.

---

### Step 3: Pre-Release Testing

#### 3.1 Automated Tests

Run all test suites:

```bash
python3 tests/test_display.py
python3 tests/test_scanner.py
python3 tests/test_cli.py
python3 tests/test_api.py
python3 tests/test_retry.py
python3 tests/test_security.py
python3 tests/test_db_integrity.py
python3 tests/test_integration.py
python3 tests/test_parallel_scanning.py  # If v3.4+

# Or run all at once
for test in tests/test_*.py; do python3 "$test"; done
```

**All tests must pass before proceeding.**

#### 3.2 Manual Verification Checklist

- [ ] `vscan --version` shows correct version (X.Y.Z)
- [ ] `vscan --help` displays correctly
- [ ] `vscan scan` works with real extensions
- [ ] `vscan scan --output report.html` generates valid HTML
- [ ] `vscan scan --output results.json` generates valid JSON
- [ ] `vscan scan --output data.csv` generates valid CSV
- [ ] `vscan cache stats` displays correctly
- [ ] `vscan config show` displays correctly
- [ ] Test on macOS (primary platform)
- [ ] Test on Windows (if available)
- [ ] Test on Linux (if available)

#### 3.3 Version Consistency Check

Verify version appears consistently:

```bash
# Should all show X.Y.Z
python3 scripts/bump_version.py --show
python3 -c "from vscode_scanner import __version__; print(__version__)"
vscan --version
```

---

## Phase 2: Build & Package

### Step 4: Clean Build Environment

Remove old build artifacts:

```bash
# Remove build directories
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf vscode_scanner.egg-info

# Verify cleanup
ls -la build/ dist/ *.egg-info 2>&1 | grep "No such file"
```

---

### Step 5: Build Distribution Package

```bash
# Ensure build tools installed
python3 -m pip install --upgrade build

# Build wheel and source distribution
python3 -m build

# Verify outputs created
ls -lh dist/
```

**Expected files:**
- `vscode_extension_scanner-X.Y.Z-py3-none-any.whl`
- `vscode_extension_scanner-X.Y.Z.tar.gz`

---

### Step 6: Verify Package Installation

Test installation in isolated environment:

```bash
# Create test virtual environment
python3 -m venv test-release-env
source test-release-env/bin/activate  # On Windows: test-release-env\Scripts\activate

# Install from built wheel
pip install dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl

# Verify installation
vscan --version           # Must show X.Y.Z
vscan --help              # Must display correctly
vscan cache stats         # Must work without errors

# Optional: Quick functional test
vscan scan --help

# Verify Python import
python3 -c "import vscode_scanner; print(vscode_scanner.__version__)"

# Cleanup test environment
deactivate
rm -rf test-release-env
```

**All verification steps must pass before proceeding.**

---

### Step 7: Generate Package Metadata

Create checksums for distribution integrity:

```bash
# Generate SHA256 checksums
cd dist/
shasum -a 256 *.whl *.tar.gz > SHA256SUMS.txt

# Verify checksum file created
cat SHA256SUMS.txt

cd ..
```

**Optional: GPG signature (if using)**

```bash
# Sign wheel package
gpg --armor --detach-sign dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl

# Verify signature created
ls -la dist/*.asc
```

---

## Phase 3: Version Control

### Step 8: Commit Release Changes

Stage all updated files:

```bash
# Core files
git add vscode_scanner/_version.py
git add CHANGELOG.md
git add README.md
git add CLAUDE.md
git add DISTRIBUTION.md

# Documentation files
git add docs/project/STATUS.md
git add docs/project/PRD.md
git add docs/README.md

# Release notes (if created)
git add docs/archive/summaries/vX.Y.Z-release-notes.md

# Archive updates (if archiving roadmap)
git add docs/archive/plans/vX.Y-ROADMAP.md
git add docs/archive/README.md

# Verify staged files
git status

# Commit with descriptive message
git commit -m "Release vX.Y.Z: {Brief description}

- Bumped version to X.Y.Z
- Updated all documentation (README, CLAUDE, STATUS, PRD, DISTRIBUTION)
- Created release notes
- {Other notable changes}

See CHANGELOG.md for full details"
```

**Commit message guidelines:**
- First line: `Release vX.Y.Z: {Brief description}` (< 72 chars)
- Blank line
- Bullet points for key changes
- Reference to CHANGELOG.md
- Keep focused on technical changes

---

### Step 9: Create Version Tag

Create annotated git tag:

```bash
# Create tag with detailed message
git tag -a vX.Y.Z -m "Release vX.Y.Z

{Brief description of release}

Key changes:
- Feature/improvement 1
- Feature/improvement 2
- Bug fix 1

See CHANGELOG.md for complete details"

# Verify tag created correctly
git tag -l -n9 vX.Y.Z

# Check tag points to correct commit
git log --oneline -1 vX.Y.Z
```

**Tag message guidelines:**
- First line: `Release vX.Y.Z`
- Blank line
- Brief description (1-2 sentences)
- Blank line
- Key changes (3-5 bullet points)
- Reference to CHANGELOG.md

---

### Step 10: Push to Remote

Push commits and tags to remote repository:

```bash
# Push commits to remote branch
git push origin [branch-name]

# Push version tag to remote
git push origin vX.Y.Z

# Alternative: Push all tags (use with caution)
# git push --tags

# Verify tag pushed successfully
git ls-remote --tags origin | grep vX.Y.Z
```

**Important:**
- Ensure you're on the correct branch before pushing
- Verify remote repository is correct
- Tags are permanent once pushed - double-check version

---

### Step 11: Create GitHub Release (Optional)

If using GitHub, create a formal release:

**Option A: Using GitHub CLI**

```bash
gh release create vX.Y.Z \
  dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl \
  dist/SHA256SUMS.txt \
  --title "vX.Y.Z" \
  --notes-file docs/archive/summaries/vX.Y.Z-release-notes.md

# If release notes file doesn't exist, use inline notes:
gh release create vX.Y.Z \
  dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl \
  dist/SHA256SUMS.txt \
  --title "vX.Y.Z" \
  --notes "See CHANGELOG.md for details"
```

**Option B: Via GitHub Web Interface**

1. Go to repository on GitHub
2. Click "Releases" → "Draft a new release"
3. Click "Choose a tag" → Select `vX.Y.Z`
4. Set release title: `vX.Y.Z`
5. Copy release notes from `docs/archive/summaries/vX.Y.Z-release-notes.md`
6. Upload files:
   - `vscode_extension_scanner-X.Y.Z-py3-none-any.whl`
   - `SHA256SUMS.txt`
7. Click "Publish release"

---

## What Happens After Release

**Release process ends here.** The following are separate workflows:

### Distribution (Separate Process)

Package distribution follows [DISTRIBUTION.md](../../DISTRIBUTION.md):
- Email distribution to team
- Upload to shared drive
- Post on internal wiki
- Update distribution channels

### Post-Release Communication (Separate Workflow)

- Send release announcement email
- Post in team channels (Slack, Teams, etc.)
- Update project status meetings
- Update documentation sites

### Roadmap Planning (Separate Workflow)

- Create `docs/project/v[NEXT]-ROADMAP.md` for next version
- Update `docs/project/STATUS.md` "Next Release" section
- Plan features for next release
- Update issue tracker/project board

---

## Quick Reference

### Complete Release Checklist

```bash
# Phase 1: Pre-Release Preparation
python3 scripts/bump_version.py X.Y.Z
python3 scripts/bump_version.py --check
# Update 8 documentation files (see Step 2)
python3 tests/test_*.py  # Run all tests
vscan --version  # Verify

# Phase 2: Build & Package
rm -rf build/ dist/ *.egg-info
python3 -m build
# Test installation (see Step 6)
cd dist/ && shasum -a 256 *.whl *.tar.gz > SHA256SUMS.txt && cd ..

# Phase 3: Version Control
git add [all updated files]
git commit -m "Release vX.Y.Z: ..."
git tag -a vX.Y.Z -m "..."
git push origin [branch] vX.Y.Z
gh release create vX.Y.Z dist/*.whl dist/SHA256SUMS.txt
```

### Documentation Files to Update (8 Total)

1. ✅ `CHANGELOG.md` - Add release section
2. ✅ `README.md` - Update version badge (line 7)
3. ✅ `CLAUDE.md` - Update Current Status (line ~21)
4. ✅ `DISTRIBUTION.md` - Update version examples
5. ✅ `docs/project/STATUS.md` - Update version (lines 5-6)
6. ✅ `docs/project/PRD.md` - Update if requirements changed
7. ✅ `docs/README.md` - Verify navigation and links
8. ✅ `docs/archive/summaries/vX.Y.Z-release-notes.md` - Create new

### Common Issues

**Issue:** `bump_version.py --check` reports version mismatches

**Solution:**
```bash
# Check which files have wrong version
python3 scripts/bump_version.py --check

# Manually fix reported files
# Re-run check until all pass
```

**Issue:** Tests fail after version bump

**Solution:**
```bash
# Check if tests reference version numbers
grep -r "3\\.3\\." tests/

# Update test fixtures/expectations if needed
```

**Issue:** Build fails with "version not found"

**Solution:**
```bash
# Verify _version.py exists and is readable
cat vscode_scanner/_version.py

# Verify imports work
python3 -c "from vscode_scanner._version import __version__; print(__version__)"
```

---

## See Also

- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version management guide
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Printable checklist
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Testing guidelines
- [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) - Doc conventions
- [release-notes-template.md](../templates/release-notes-template.md) - Release notes template
- [CHANGELOG.md](../../CHANGELOG.md) - Release history
- [DISTRIBUTION.md](../../DISTRIBUTION.md) - Distribution guide

---

**Last Updated:** 2025-10-25
**Process Version:** 1.0
