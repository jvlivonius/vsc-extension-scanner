# Release Process

**Purpose:** Reproducible release workflow for VS Code Extension Security Scanner

**Version:** 2.0
**Last Updated:** 2025-10-31

---

## Overview

### Three-Phase Workflow

**Phase 1: Pre-Release Preparation** (30-45 min)
- Version management and consistency validation
- Documentation updates across 8 files
- Comprehensive testing (automated + manual)

**Phase 2: Build & Package** (15-20 min)
- Clean build environment
- Distribution package creation
- Installation verification in isolated environment

**Phase 3: Version Control** (10-15 min)
- Atomic release commit
- Annotated version tag
- GitHub release with artifacts

### Core Principles

- **Single Source of Truth:** All versions derive from `_version.py`
- **Fail-Fast Validation:** Each phase has gates - don't proceed with failures
- **Reproducible Builds:** Clean environment, documented steps, verified outputs
- **Atomic Releases:** Commit + tag + artifacts published together

### Out of Scope

- **Distribution:** Follow [DISTRIBUTION.md](../../DISTRIBUTION.md) after release
- **Communication:** Post-release announcements handled separately
- **Roadmap Planning:** Next version planning is separate workflow

### Related Documents

- **Execution:** [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Printable checklist
- **Versioning:** [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version management details
- **Testing:** [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Testing guidelines
- **Git Workflow:** [GIT_WORKFLOW.md](GIT_WORKFLOW.md) - Branching strategy and PR guidelines
- **Templates:** [release-notes-template.md](../templates/release-notes-template.md)

---

## Prerequisites

### Git Workflow Verification

**BEFORE starting the release process, verify git state:**

```bash
# Check current branch and working directory
git status
git branch

# Expected:
# - On branch: main
# - Working directory: clean (no uncommitted changes)
# - All feature branches merged

# If not on main:
git checkout main
git pull origin main

# If uncommitted changes exist:
git add .
git commit -m "..."
# OR
git stash
```

**Branch Requirements:**
- ✅ Must be on `main` branch (releases only from main)
- ✅ Working directory must be clean (no uncommitted changes)
- ✅ All feature branches for this release must be merged
- ✅ Main branch must be up to date with remote (`git pull origin main`)

**If working on a feature branch:**
1. Complete current feature work
2. Create PR and get approval
3. Merge PR to main
4. Switch to main: `git checkout main && git pull origin main`
5. Then start release process

→ **See:** [GIT_WORKFLOW.md](GIT_WORKFLOW.md) for complete branch workflow details

---

## Phase 1: Pre-Release Preparation

### Step 1: Version Management

**Update version in single source:**

```bash
python3 scripts/bump_version.py X.Y.Z
```

**Verify consistency across all files:**

```bash
python3 scripts/bump_version.py --check
```

The `--check` command validates:
- Python files import from `_version.py` (no hardcoded versions)
- Documentation version references match
- Dynamic versioning in `setup.py` and `pyproject.toml`

**Expected output:** All files report version consistency with ✓ marks.

**Troubleshooting:** If mismatches detected, manually fix reported files and re-run `--check`.

---

### Step 2: Documentation Updates

Update **8 core documentation files** in this recommended order:

#### 2.1 CHANGELOG.md (Root)
Add new release section using [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Fixed
- Bug fixes

### Security
- Security vulnerability fixes
```

- Place after `[Unreleased]` section
- Include migration notes for breaking changes
- Update comparison links at bottom

#### 2.2 README.md (Root)
- Update version badge in header section
- Update installation examples if changed
- Update feature list if new features added

#### 2.3 CLAUDE.md (Root)
- Update `## Current Status` section with new version
- Move in-progress work to previous updates
- Verify all version references match `_version.py`

#### 2.4 DISTRIBUTION.md (Root)
- Update version references in installation examples
- Update wheel filename examples throughout
- Update troubleshooting section if new issues discovered

#### 2.5 docs/project/STATUS.md
- Update `**Current Version:**` field
- Update `**Schema Version:**` field if changed
- Add new release section at top
- Update "Next Release" section

#### 2.6 docs/project/PRD.md
- Update version number if requirements changed
- Update feature scope, constraints, success criteria if applicable

#### 2.7 docs/README.md
- Verify navigation table is current
- Verify all links work
- Update if new documentation added

#### 2.8 Release Notes (Recommended)
Create `docs/archive/summaries/vX.Y.Z-release-notes.md` using template:
- Summary and key features
- Bug fixes and improvements
- Breaking changes with migration guide
- Installation/upgrade instructions
- Known issues

**Pattern:** Follow [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) for archive naming.

---

### Step 3: Pre-Release Testing

**Automated Tests (Required):**

```bash
# Run complete test suite
pytest tests/

# Alternative: Individual test files
for test in tests/test_*.py; do python3 "$test"; done
```

**All tests must pass before proceeding to Phase 2.**

**Manual Verification (Required):**
- `vscan --version` shows correct version
- `vscan --help` displays correctly
- `vscan scan` works with real extensions
- Output formats work: HTML, JSON, CSV
- Cache and config commands work
- Cross-platform testing (macOS, Windows, Linux if available)

**Version Consistency Check:**

```bash
# All should show X.Y.Z
python3 scripts/bump_version.py --show
python3 -c "from vscode_scanner import __version__; print(__version__)"
vscan --version
```

**Phase 1 Gate:** Only proceed if all tests pass and version is consistent.

---

## Phase 2: Build & Package

### Step 4: Clean Build Environment

Remove old build artifacts:

```bash
rm -rf build/ dist/ *.egg-info
```

**Verify cleanup:** Should see "No such file or directory" for these paths.

---

### Step 5: Build Distribution Package

```bash
# Ensure build tools current
python3 -m pip install --upgrade build

# Build wheel and source distribution
python3 -m build

# Verify outputs
ls -lh dist/
```

**Expected outputs:**
- `vscode_extension_scanner-X.Y.Z-py3-none-any.whl`
- `vscode_extension_scanner-X.Y.Z.tar.gz`

---

### Step 6: Verify Package Installation

Test in isolated environment:

```bash
# Create test environment
python3 -m venv test-release-env
source test-release-env/bin/activate  # Windows: test-release-env\Scripts\activate

# Install from wheel
pip install dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl

# Verify installation
vscan --version           # Must show X.Y.Z
vscan --help              # Must display correctly
vscan cache stats         # Must work without errors

# Verify Python import
python3 -c "import vscode_scanner; print(vscode_scanner.__version__)"

# Cleanup
deactivate
rm -rf test-release-env
```

**Phase 2 Gate:** Installation verification must succeed before proceeding.

---

### Step 7: Generate Package Metadata

```bash
# Generate SHA256 checksums
cd dist/
shasum -a 256 *.whl *.tar.gz > SHA256SUMS.txt
cat SHA256SUMS.txt  # Verify
cd ..
```

**Optional GPG Signature:**

```bash
gpg --armor --detach-sign dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl
```

---

## Phase 3: Version Control

### Step 8: Commit Release Changes

```bash
# Stage all updated files
git add vscode_scanner/_version.py CHANGELOG.md README.md CLAUDE.md DISTRIBUTION.md
git add docs/project/STATUS.md docs/project/PRD.md docs/README.md
git add docs/archive/summaries/vX.Y.Z-release-notes.md

# Verify staged files
git status

# Commit with descriptive message
git commit -m "Release vX.Y.Z: {Brief description}

- Bumped version to X.Y.Z
- Updated all documentation
- Created release notes
- {Other notable changes}

See CHANGELOG.md for full details"
```

**Commit Message Format:**
- First line: `Release vX.Y.Z: {Brief description}` (< 72 chars)
- Bullet points for key changes
- Reference to CHANGELOG.md

---

### Step 9: Create Version Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release vX.Y.Z

{Brief description}

Key changes:
- Feature/improvement 1
- Feature/improvement 2
- Bug fix 1

See CHANGELOG.md for complete details"

# Verify tag
git tag -l -n9 vX.Y.Z
git log --oneline -1 vX.Y.Z
```

---

### Step 10: Push to Remote

```bash
# Push release commit to main
git push origin main

# Push version tag (tags are permanent!)
git push origin vX.Y.Z

# Verify both commit and tag pushed successfully
git ls-remote --heads origin main
git ls-remote --tags origin | grep vX.Y.Z
```

**Important:**
- Always push from `main` branch (releases never from feature branches)
- Tags are permanent once pushed - verify version is correct before pushing
- Both commit and tag must be pushed together for complete release

---

### Step 11: Create GitHub Release

**Using GitHub CLI:**

```bash
gh release create vX.Y.Z \
  dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl \
  dist/SHA256SUMS.txt \
  --title "vX.Y.Z" \
  --notes-file docs/archive/summaries/vX.Y.Z-release-notes.md
```

**Fallback - Web Interface:**
1. Navigate to repository → Releases → Draft new release
2. Select tag vX.Y.Z
3. Set title: vX.Y.Z
4. Copy release notes from archive
5. Upload wheel and SHA256SUMS.txt
6. Publish release

**Phase 3 Gate:** Verify GitHub release created with downloadable artifacts.

---

## Troubleshooting

### Version Consistency Issues

**Problem:** `bump_version.py --check` reports mismatches

**Solution:**
1. Note which files have wrong version
2. Manually update reported files
3. Re-run `--check` until all pass
4. Check for hardcoded versions vs imports

### Test Failures After Version Bump

**Problem:** Tests fail referencing old version

**Solution:**
1. Search tests for version references: `grep -r "3\.3\." tests/`
2. Update test fixtures and expectations
3. Verify no hardcoded version assertions

### Build Fails with "version not found"

**Problem:** Build can't find version information

**Solution:**
1. Verify `_version.py` exists: `cat vscode_scanner/_version.py`
2. Test import: `python3 -c "from vscode_scanner._version import __version__; print(__version__)"`
3. Check `MANIFEST.in` includes `_version.py`

### Installation Verification Fails

**Problem:** Installed package shows wrong version or imports fail

**Solution:**
1. Ensure clean virtual environment (no cached packages)
2. Check wheel was installed: `pip list | grep vscode`
3. Verify PATH: `which vscan`
4. Check for conflicting installations

### GitHub Release Upload Fails

**Problem:** `gh release create` fails with authentication or upload errors

**Solution:**
1. Verify GitHub CLI authenticated: `gh auth status`
2. Check repository permissions
3. Verify files exist in dist/
4. Use web interface as fallback

---

## Automated Release Workflow

### GitHub Actions Release Automation

**Workflow:** `.github/workflows/release.yml`

The release workflow **automatically triggers** when you push a version tag to the main branch, handling Phase 2 (Build & Package) and most of Phase 3 (GitHub Release creation).

#### What Gets Automated

✅ **Automatic when tag is pushed:**
1. Clean build environment
2. Build wheel and source distribution
3. Generate SHA256 checksums
4. Install and verify package in isolated environment
5. Extract release notes from CHANGELOG.md
6. Create GitHub release with artifacts

#### Manual Steps Required

You still need to complete Phase 1 and initial Phase 3 steps manually:

**Phase 1 - Pre-Release Preparation:**
```bash
# 1. Version management
python3 scripts/bump_version.py X.Y.Z
python3 scripts/bump_version.py --check

# 2. Documentation updates (8 files)
# - CHANGELOG.md, README.md, CLAUDE.md, etc.

# 3. Testing
pytest tests/
```

**Phase 3 - Commit & Tag (triggers automation):**
```bash
# Commit release changes
git add .
git commit -m "Release vX.Y.Z: description"

# Create and push tag (THIS TRIGGERS THE WORKFLOW)
git tag -a vX.Y.Z -m "Release message"
git push origin main
git push origin vX.Y.Z  # Workflow starts automatically
```

#### Workflow Validation

The automated workflow includes these verification steps:
- ✅ Version in package matches git tag
- ✅ Package installs successfully
- ✅ `vscan --version` and `vscan --help` work
- ✅ Python import successful
- ✅ All artifacts generated and checksummed

#### Monitoring Workflow Execution

**View workflow status:**
```bash
# Using GitHub CLI
gh run list --workflow=release.yml

# View specific run
gh run view <run-id>

# Watch latest run in real-time
gh run watch
```

**Via GitHub Web Interface:**
1. Navigate to repository → Actions tab
2. Select "Build & Release" workflow
3. View running/completed workflow runs

#### Workflow Artifacts

The workflow automatically uploads to GitHub Release:
- `vscode_extension_scanner-X.Y.Z-py3-none-any.whl` (wheel)
- `vscode_extension_scanner-X.Y.Z.tar.gz` (source)
- `SHA256SUMS.txt` (checksums)

#### Troubleshooting Automated Workflow

**Problem:** Workflow fails with version mismatch

**Solution:**
1. Check that `_version.py` was updated correctly
2. Verify tag format matches `vX.Y.Z` pattern
3. Re-run `bump_version.py --check`

**Problem:** Package verification fails

**Solution:**
1. Check workflow logs in GitHub Actions
2. Verify `pyproject.toml` and `MANIFEST.in` are correct
3. Test build locally: `python3 -m build`

**Problem:** Release notes missing or incorrect

**Solution:**
1. Ensure CHANGELOG.md has section for version: `## [X.Y.Z] - YYYY-MM-DD`
2. Workflow extracts text between version headers
3. If extraction fails, edit release notes manually on GitHub

---

## Manual Release Process (Legacy)

**Note:** Steps 4-7 and 11 are now automated. This section remains for reference or manual releases if needed.

### Phase 2: Build & Package (Automated)

Steps 4-7 are now handled by the automated workflow, but can be performed manually if needed:

### Step 4: Clean Build Environment (Automated)

Remove old build artifacts:

```bash
rm -rf build/ dist/ *.egg-info
```

**Verify cleanup:** Should see "No such file or directory" for these paths.

---

### Step 5: Build Distribution Package (Automated)

```bash
# Ensure build tools current
python3 -m pip install --upgrade build

# Build wheel and source distribution
python3 -m build

# Verify outputs
ls -lh dist/
```

**Expected outputs:**
- `vscode_extension_scanner-X.Y.Z-py3-none-any.whl`
- `vscode_extension_scanner-X.Y.Z.tar.gz`

---

### Step 6: Verify Package Installation (Automated)

Test in isolated environment:

```bash
# Create test environment
python3 -m venv test-release-env
source test-release-env/bin/activate  # Windows: test-release-env\Scripts\activate

# Install from wheel
pip install dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl

# Verify installation
vscan --version           # Must show X.Y.Z
vscan --help              # Must display correctly
vscan cache stats         # Must work without errors

# Verify Python import
python3 -c "import vscode_scanner; print(vscode_scanner.__version__)"

# Cleanup
deactivate
rm -rf test-release-env
```

**Phase 2 Gate:** Installation verification must succeed before proceeding.

---

### Step 7: Generate Package Metadata (Automated)

```bash
# Generate SHA256 checksums
cd dist/
shasum -a 256 *.whl *.tar.gz > SHA256SUMS.txt
cat SHA256SUMS.txt  # Verify
cd ..
```

**Optional GPG Signature:**

```bash
gpg --armor --detach-sign dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl
```

---

## Remaining Automation Opportunities

### Current Manual Steps That Could Be Scripted

1. **Documentation Updates**
   - Script to update version badges across files
   - Template-based CHANGELOG entry generation
   - Automated link verification in docs

2. **Testing Workflow**
   - Single command to run all pre-release tests
   - Automated version consistency checks in CI/CD
   - Cross-platform test orchestration

3. **Pre-commit Validation**
   - Pre-commit hooks for version validation
   - Automated CHANGELOG format checking

### Enhancement Proposals

- **Interactive release script:** Step-by-step wizard with validation for Phase 1
- **Pre-release checklist validation:** Automated checks before allowing tag creation
- **Rollback mechanism:** Quick rollback for failed releases
- **Release metrics:** Track time, issues, improvements across releases
- **PyPI publishing:** Automatic PyPI upload after successful GitHub release

---

## Time Estimates

**With Automated Workflow:**
- Phase 1 (Preparation): 30-45 minutes (manual)
- Phase 2 (Build & Package): ~5 minutes (automated)
- Phase 3 (Version Control): ~5 minutes (mostly automated)
- **Total:** 40-55 minutes (38% time reduction)

**Legacy Manual Process:**
- Phase 1 (Preparation): 30-45 minutes
- Phase 2 (Build & Package): 15-20 minutes
- Phase 3 (Version Control): 10-15 minutes
- **Total:** 55-80 minutes for complete release

**First-time release:** Add 15-30 minutes for familiarization.

---

## See Also

- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Printable execution checklist
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version management guide
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Testing guidelines
- [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) - Documentation standards
- [release-notes-template.md](../templates/release-notes-template.md) - Release notes template
- [CHANGELOG.md](../../CHANGELOG.md) - Release history
- [DISTRIBUTION.md](../../DISTRIBUTION.md) - Distribution process

---

**Process Version:** 2.1
**Last Updated:** 2025-11-01
**Changes:** Added automated GitHub Actions workflow for build and release (v2.0 → v2.1)
