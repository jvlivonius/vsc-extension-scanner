# Release Process

**Purpose:** Reproducible release workflow for VS Code Extension Security Scanner

**Version:** 2.0
**Last Updated:** 2025-10-31

---

## Overview

### Three-Phase Workflow

**Phase 1: Pre-Release Preparation** (20-30 min)
- Version management with automated documentation updates (3 files auto-updated)
- Manual documentation updates (2 files: CHANGELOG.md, release notes)
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
- Dynamic versioning in `pyproject.toml`

**Expected output:** All files report version consistency with ✓ marks.

**Troubleshooting:** If mismatches detected, manually fix reported files and re-run `--check`.

---

### Step 2: Documentation Updates

#### Automated Updates (3 files - handled by bump_version.py)

The following files are **automatically updated** when using the `--auto-update` flag:

**2.1 README.md (Root)** ✅ Automated
- Version badge updated automatically
- **Manual (if needed):** Update installation examples if changed
- **Manual (if needed):** Update feature list if new features added

**2.2 CLAUDE.md (Root)** ✅ Automated
- `## Current Status` section version updated automatically
- **Manual (if needed):** Move in-progress work to previous updates section
- **Manual (if needed):** Update latest features/roadmap references

**2.3 docs/project/PRD.md** ✅ Automated
- Version field updated automatically
- **Manual (if needed):** Update requirements, constraints, or success criteria if changed

#### Manual Updates Required (2 files)

**2.4 CHANGELOG.md (Root)** ⚠️ Manual Required

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

**2.5 Release Notes (Required for Automated Releases)** ⚠️ Manual Required

Create `docs/archive/summaries/vX.Y.Z-release-notes.md` using template:
- Summary and key features
- Bug fixes and improvements
- Breaking changes with migration guide
- Installation/upgrade instructions
- Known issues

**Pattern:** Follow [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) for archive naming.

**For Automated Releases:**
- The GitHub Actions workflow will use this file for the GitHub release description
- If this file doesn't exist, it will fall back to extracting from CHANGELOG.md
- Release notes provide comprehensive user-facing information vs brief CHANGELOG bullets
- File must be created and committed **before** pushing the version tag

**2.6 Consolidate Release Documentation (Multi-Phase Releases)** ⚠️ Manual or Automated

For releases with multiple phases (roadmap + handoff docs + phase summaries):

**Sources to consolidate:**
- Roadmap objectives → Key Features section
- Handoff documents → Implementation Details
- Phase completion summaries → Key Achievements section
- Test metrics and coverage reports → Testing section

**Consolidation approaches:**

1. **Manual:** Extract key information from source documents
2. **Future:** Use AI assistant to consolidate multiple documents

The release notes supersede intermediate documents but preserve essential details for archival.

See [DOCUMENTATION_CONVENTIONS.md § Release Documentation Archival Pattern](DOCUMENTATION_CONVENTIONS.md#release-documentation-archival-pattern) for naming conventions and decision framework.

#### Time Savings

**Old workflow:** 8 files requiring manual updates (~20-30 min)
**New workflow:** 2 files requiring manual updates + 3 auto-updated (~8-12 min)
**Time reduction:** ~60% faster documentation phase

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

**Automated Smoke Test (Recommended):**

```bash
# Run comprehensive smoke tests (creates temp virtualenv automatically)
python3 scripts/run_tests.py --smoke dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl
```

**Expected output:** All 5 validation steps pass with ✓ marks:
1. Wheel file validation
2. Virtualenv creation
3. Package installation
4. CLI accessibility test (`vscan --version`)
5. Help command test (`vscan --help`)

**Manual Verification (Alternative):**

If you need to manually verify the package:

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
# Stage all updated files (automated + manual)
git add vscode_scanner/_version.py README.md CLAUDE.md docs/project/PRD.md
git add CHANGELOG.md docs/archive/summaries/vX.Y.Z-release-notes.md

# Note: 6 files total (3 auto-updated + 2 manual + release notes)

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

### Step 9b: Archive Release Documentation (Multi-Phase Releases)

**For releases with intermediate documents (handoffs, phase summaries):**

After creating comprehensive release notes, organize documentation following the archival workflow.

**Option 1: Automated (Recommended)**

```bash
# Preview changes
python3 scripts/archive_release_docs.py vX.Y.Z --dry-run

# Execute archival
python3 scripts/archive_release_docs.py vX.Y.Z

# Verify changes
git status
```

**Option 2: Manual**

```bash
# 1. Archive roadmap
git mv docs/project/vX.Y-roadmap.md docs/archive/plans/vX.Y-roadmap.md

# 2. Remove intermediate documents
git rm docs/project/vX.Y-phase*-handoff.md
git rm docs/project/vX.Y-phase*-summary.md
git rm docs/archive/summaries/vX.Y-phase*-completion-summary.md

# 3. Update indexes
# Edit docs/archive/README.md (add version entry)
# Edit docs/project/STATUS.md (change to "Released")

# 4. Stage changes
git add docs/archive/README.md docs/project/STATUS.md

# 5. Commit
git commit -m "docs(vX.Y): Archive release documentation

Archived:
- Roadmap to docs/archive/plans/

Removed (superseded by release notes):
- X handoff documents
- Y phase summaries

Updated:
- docs/archive/README.md (version entry)
- docs/project/STATUS.md (released status)"
```

**Document Naming Conventions:**
- Handoffs: `vX.Y-phaseN-handoff.md` → REMOVE
- Phase summaries: `vX.Y-phaseN-*-summary.md` → REMOVE
- Roadmaps: `vX.Y-*-roadmap.md` → ARCHIVE to `docs/archive/plans/`
- Release notes: `vX.Y.Z-release-notes.md` → KEEP

See [DOCUMENTATION_CONVENTIONS.md § Release Documentation Archival Pattern](DOCUMENTATION_CONVENTIONS.md#release-documentation-archival-pattern) for complete details.

**Note:** Single-phase releases without intermediate documents can skip this step.

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

### Step 11: GitHub Release (Automated)

**Primary Method: GitHub Actions (Automatic)**

When you push the version tag in Step 10, the GitHub Actions workflow automatically:
1. Builds distribution packages
2. Generates checksums
3. Verifies package installation
4. Extracts release notes from `docs/archive/summaries/vX.Y.Z-release-notes.md`
5. Creates GitHub release with artifacts

**Monitor workflow:**

```bash
# Watch latest workflow run
gh run watch

# View recent release workflows
gh run list --workflow=release.yml

# Check workflow status
gh run list --limit 1
```

**Phase 3 Gate:** Verify GitHub release created with downloadable artifacts.

---

#### Correcting Releases After Creation

**If release notes need updates after tag push:**

```bash
# 1. Checkout main and pull latest changes
git checkout main && git pull origin main

# 2. Delete existing GitHub release
gh release delete vX.Y.Z --yes

# 3. Delete local and remote tags
git tag -d vX.Y.Z
git push origin --delete vX.Y.Z

# 4. Update release notes
# Edit: docs/archive/summaries/vX.Y.Z-release-notes.md
git add docs/archive/summaries/vX.Y.Z-release-notes.md
git commit -m "docs: Update vX.Y.Z release notes"
git push origin main

# 5. Recreate tag from updated release notes
git tag -a vX.Y.Z -F docs/archive/summaries/vX.Y.Z-release-notes.md

# 6. Push tag to trigger automated workflow
git push origin vX.Y.Z

# 7. Monitor workflow completion
gh run watch
```

**Note:** Only use manual release creation if GitHub Actions workflow fails.

**Manual Release Creation (Fallback Only):**

Using GitHub CLI:
```bash
gh release create vX.Y.Z \
  dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl \
  dist/SHA256SUMS.txt \
  --title "vX.Y.Z" \
  --notes-file docs/archive/summaries/vX.Y.Z-release-notes.md
```

Using Web Interface:
1. Navigate to repository → Releases → Draft new release
2. Select tag vX.Y.Z
3. Set title: vX.Y.Z
4. Copy release notes from archive
5. Upload wheel and SHA256SUMS.txt
6. Publish release

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
5. Extract release notes from `docs/archive/summaries/vX.Y.Z-release-notes.md` (or fallback to CHANGELOG.md)
6. Create GitHub release with artifacts and comprehensive release notes

#### Manual Steps Required

You still need to complete Phase 1 and initial Phase 3 steps manually:

**Phase 1 - Pre-Release Preparation:**
```bash
# 1. Version management with auto-update
python3 scripts/bump_version.py X.Y.Z --auto-update
# This automatically updates: README.md, CLAUDE.md, docs/project/PRD.md

# 2. Manual documentation updates (2 files)
# - CHANGELOG.md (add release section)
# - IMPORTANT: Create docs/archive/summaries/vX.Y.Z-release-notes.md

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

**With Automated Workflow + Version Management:**
- Phase 1 (Preparation): 20-30 minutes (60% automated)
  - Version bump with auto-update: ~1 minute
  - Manual doc updates (2 files): ~8-12 minutes
  - Testing: ~12-18 minutes
- Phase 2 (Build & Package): ~5 minutes (fully automated)
- Phase 3 (Version Control): ~5 minutes (mostly automated)
- **Total:** 30-40 minutes (50-60% time reduction from original 55-80 min)

**Breakdown of improvements:**
- Version automation: 50% reduction in doc update time (8 files → 2 files manual)
- Build automation: 38% reduction in build/package time
- **Combined:** ~50% overall time reduction

**Legacy Manual Process:**
- Phase 1 (Preparation): 30-45 minutes (all manual doc updates)
- Phase 2 (Build & Package): 15-20 minutes (manual build)
- Phase 3 (Version Control): 10-15 minutes (manual steps)
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
