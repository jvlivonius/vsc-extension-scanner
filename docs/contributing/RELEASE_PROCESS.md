# Release Process

**Purpose:** Reproducible 3-phase release workflow with automation tools
**Document Type:** Process Guide
**Last Updated:** 2025-11-01
**Version:** 2.1

---

## Overview

### Three-Phase Workflow

**Phase 1: Pre-Release Preparation**
- Version management with automated documentation updates (3 files auto-updated)
- Manual documentation updates (2 files: CHANGELOG.md, release notes)
- Comprehensive testing (automated + manual)

**Phase 2: Build & Package**
- Clean build environment
- Distribution package creation
- Installation verification in isolated environment

**Phase 3: Version Control**
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

**CRITICAL:** Releases MUST be created from a clean `main` branch. Verify:

```bash
git status && git branch
# Expected: On branch main, working directory clean
```

**Requirements:**
- ✅ On `main` branch (releases only from main)
- ✅ Working directory clean (no uncommitted changes)
- ✅ All feature branches merged
- ✅ Up to date with remote: `git pull origin main`

→ **See:** [GIT_WORKFLOW.md § Release Workflow](GIT_WORKFLOW.md#release-workflow) for complete prerequisites and branch workflow

---

## Automated Pre-Release Validation

**Time savings:** 50-60% reduction (55-80 min → 30-40 min) via 3 automation tools

### Pre-Release Check (Before Phase 1)

**Run:** `python3 scripts/pre_release_check.py --verbose` (options: `--quiet`, `--skip-git`)

| Step | Validates | Exit 0 = Pass |
|------|-----------|---------------|
| 1. Version | `_version.py` ↔ README/CLAUDE/PRD consistency | ✓ |
| 2. Git | Clean directory, main/master branch | ✓ |
| 3. Tests | Full suite with coverage (CI mode, excludes real_api) | ✓ |
| 4. Security | bandit + safety + pip-audit (skips if N/A) | ✓ |
| 5. Coverage | ≥80% threshold gate | ✓ |

### Smoke Testing (Phase 2, Step 6)

**Run:** `python3 scripts/smoke_test.py dist/vscan-X.Y.Z.whl --verbose` (options: `--config FILE`)

| Step | Validates | Note |
|------|-----------|------|
| 1. Wheel | File exists, .whl format | |
| 2. Venv | Temp isolated virtualenv | Platform-specific |
| 3. Install | Wheel installation in venv | |
| 4. CLI | `vscan --version/--help` | Commands: scan, cache, config, report |
| 5. Scan | Real API calls via config JSON | Exit 1 (vulns found) = expected |
| 6. Outputs | JSON/HTML/CSV generation + validation | |
| 7. Cache | `cache stats` + `cache clear --force` | |

**Config:** `scripts/smoke_test_extensions.json` (see template in docs)

**Exit codes:** 0=pass, 1=failed, 2=wheel not found, 3=error

### Release Notes Validation (Phase 1, Step 1)

**Integrated with version bump:** `python3 scripts/bump_version.py X.Y.Z --validate-notes`

- Blocks bump if `docs/archive/summaries/vX.Y.Z-release-notes.md` missing/empty (<100 chars)
- Prevents generic GitHub release message
- Standalone check: `--check-notes X.Y.Z`

**Fix if fails:** `cp docs/templates/release-notes-template.md docs/archive/summaries/vX.Y.Z-release-notes.md` → fill → commit → rerun

---

## Phase 1: Pre-Release Preparation

### Step 1: Version Management

**⚠️ ALWAYS use `--validate-notes` flag** (prevents generic GitHub release message)

```bash
python3 scripts/bump_version.py X.Y.Z --validate-notes  # RECOMMENDED
python3 scripts/bump_version.py --check                 # Verify consistency
python3 scripts/bump_version.py --check-notes X.Y.Z     # Standalone notes check
```

**What `--validate-notes` does:**
- Updates `_version.py` + blocks if release notes missing
- Requires: `docs/archive/summaries/vX.Y.Z-release-notes.md` (>100 chars)
- Prevents: Generic GitHub Actions release message

**If validation fails:** Copy template → fill → commit → rerun (see [Release Notes Validation](#release-notes-validation-phase-1-step-1))
- File is ready for GitHub Actions release workflow

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

**2.5 Release Notes (Required for Automated Releases)** 🔴 CRITICAL - Manual Required

Create `docs/archive/summaries/vX.Y.Z-release-notes.md` using template:
- Summary and key features
- Bug fixes and improvements
- Breaking changes with migration guide
- Installation/upgrade instructions
- Known issues

**Template:** `docs/templates/release-notes-template.md`

**Pattern:** Follow [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) for archive naming.

**🔴 CRITICAL: This file MUST exist BEFORE pushing the version tag!**

**Why this matters:**
- The GitHub Actions workflow uses this file for the GitHub release description
- If missing, the release will have only a generic message instead of comprehensive notes
- This file provides comprehensive user-facing information vs brief CHANGELOG bullets
- **Validation prevents this mistake:** Use `--validate-notes` flag when bumping version

**Validation workflow:**

```bash
# Option 1: Validate during version bump (RECOMMENDED)
python3 scripts/bump_version.py X.Y.Z --validate-notes

# Option 2: Validate separately before tagging
python3 scripts/bump_version.py --check-notes X.Y.Z
```

**If validation fails:**
1. Copy template: `docs/templates/release-notes-template.md`
2. Create: `docs/archive/summaries/vX.Y.Z-release-notes.md`
3. Fill in all sections with version-specific information
4. Commit the file
5. Re-run validation to confirm

**Expected validation output:**
```
✓ Release notes file exists: docs/archive/summaries/vX.Y.Z-release-notes.md
✓ Release notes file has content (XXXX chars)
```

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

### Step 3: Pre-Release Validation

**⚠️ RECOMMENDED: Use automated pre-release check**

The automated pre-release check performs comprehensive validation in a single command, replacing most manual testing steps.

**Automated Validation (Recommended):**

```bash
python3 scripts/pre_release_check.py --verbose
```

This automated script performs **5 comprehensive validation steps**:

1. **Version Consistency** - Validates all files match `_version.py`
2. **Git Status** - Ensures clean working directory on main/master
3. **Test Suite** - Runs full test suite with coverage (CI mode)
4. **Security Scans** - Runs bandit, safety, pip-audit
5. **Coverage Threshold** - Validates ≥80% coverage

**Expected Output:**

```
======================================================================
PRE-RELEASE VALIDATION CHECKS
======================================================================

[1/5] Validating version consistency...
      ✓ Version consistency validated

[2/5] Validating git working directory...
      ✓ Git status clean (branch: main)

[3/5] Running test suite with coverage...
      ✓ All tests passed (40 tests in 12.3s)

[4/5] Running security scans...
      ✓ bandit: No high severity issues
      ✓ safety: No known vulnerabilities
      ✓ pip-audit: No vulnerabilities

[5/5] Validating test coverage...
      ✓ Coverage: 89.4% (target: 80%+)

======================================================================
✅ PRE-RELEASE VALIDATION: ALL CHECKS PASSED
======================================================================
```

**Options:**

```bash
# Quiet mode (summary only)
python3 scripts/pre_release_check.py

# Skip git checks (for testing)
python3 scripts/pre_release_check.py --skip-git
```

**Exit Codes:**
- `0` - All checks passed → Proceed to Phase 2
- `1` - Some checks failed → Fix issues before continuing
- `3` - Execution error → Check environment

→ **See:** [Pre-Release Check](#pre-release-check-recommended-before-phase-1) section above for complete documentation.

**Manual Verification (Optional - Only if Automated Check Fails):**

If you need to debug specific failures from the automated check, you can run components individually:

**Version Consistency:**
```bash
# Verify version consistency
python3 scripts/bump_version.py --check

# Verify version displays correctly
python3 -c "from vscode_scanner import __version__; print(__version__)"
./vscan --version  # Should show X.Y.Z
```

**Test Suite:**
```bash
# Run complete test suite (CI mode)
python3 scripts/run_tests.py --ci --coverage

# Alternative: Direct pytest
pytest tests/
```

**Security Scans:**
```bash
bandit -r vscode_scanner/ -lll
safety check
pip-audit
```

**Coverage Check:**
```bash
coverage report
# Should show ≥80% overall coverage
```

**Manual Functional Testing (Only if needed for debugging):**
- `vscan --version` shows correct version X.Y.Z
- `vscan --help` displays correctly
- `vscan scan <extension-id>` works with real extensions
- Output formats work: HTML, JSON, CSV
- Cache and config commands work

**Phase 1 Gate:** The automated pre-release check must pass (exit code 0) before proceeding to Phase 2. If it fails, fix the reported issues and re-run until all checks pass.

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

**⚠️ RECOMMENDED: Use automated smoke testing**

The automated smoke test validates package installation and core functionality in an isolated environment.

**Automated Smoke Testing (Recommended):**

```bash
python3 scripts/smoke_test.py dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl --verbose

# With custom extension config
python3 scripts/smoke_test.py dist/vscan-X.Y.Z.whl --config scripts/smoke_test_extensions.json

# Quiet mode
python3 scripts/smoke_test.py dist/vscan-X.Y.Z.whl
```

This automated script performs **7 comprehensive validation steps** in an isolated virtualenv:

1. **Wheel Validation** - Verifies wheel file exists and format
2. **Virtualenv Creation** - Creates temporary isolated environment
3. **Package Installation** - Installs wheel and validates success
4. **CLI Accessibility** - Tests `vscan --version` and `vscan --help`
5. **Core Scan Workflow** - Real API calls with configured extensions
6. **Output Formats** - Validates JSON, HTML, CSV generation
7. **Cache Operations** - Tests cache stats and clear commands

**Expected Output:**

```
======================================================================
SMOKE TESTS: vscode_extension_scanner-3.7.1-py3-none-any.whl
======================================================================

[1/7] Wheel file: vscode_extension_scanner-3.7.1-py3-none-any.whl ✓
       Loaded 3 extensions from smoke_test_extensions.json

[2/7] Creating test virtualenv at /tmp/vscan_smoke_xxx/venv...
      ✓ Virtualenv created successfully

[3/7] Installing wheel in virtualenv...
      ✓ Package installed successfully

[4/7] Testing CLI command accessibility...
      ✓ CLI accessible: vscan 3.7.1
      ✓ Help command works

[5/7] Testing core scan workflow (real API calls)...
      Scanning 3 extensions: ms-python.python, GitHub.copilot, esbenp.prettier-vscode
      ⚠ Scan completed with vulnerabilities found (exit code 1 - expected)

[6/7] Testing output format generation...
      ✓ JSON output generated and validated
      ✓ HTML output generated and validated
      ✓ CSV output generated and validated

[7/7] Testing cache operations...
      ✓ Cache stats command works
      ✓ Cache clear command works

======================================================================
✅ SMOKE TESTS: ALL CHECKS PASSED
======================================================================
```

**Configuration:**

Ensure `scripts/smoke_test_extensions.json` exists with test extensions:

```json
{
  "extensions": [
    {
      "id": "ms-python.python",
      "publisher": "Microsoft",
      "name": "Python"
    },
    {
      "id": "GitHub.copilot",
      "publisher": "GitHub",
      "name": "GitHub Copilot"
    }
  ]
}
```

**Exit Codes:**
- `0` - All smoke tests passed → Package ready for release
- `1` - Some smoke tests failed → Fix package issues
- `2` - Wheel file not found/invalid → Check build step
- `3` - Execution error → Check environment

→ **See:** [Smoke Testing](#smoke-testing-phase-2-step-6) section above for complete documentation.

**Manual Verification (Fallback - Only if Automated Smoke Test Fails):**

If you need to debug specific smoke test failures, you can verify the package manually:

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

# Test scan with real extension
vscan scan ms-python.python

# Test output formats
vscan scan ms-python.python --output scan-test.json
vscan scan ms-python.python --output scan-test.html
vscan scan ms-python.python --output scan-test.csv

# Verify Python import
python3 -c "import vscode_scanner; print(vscode_scanner.__version__)"

# Cleanup
deactivate
rm -rf test-release-env
```

**Phase 2 Gate:** Automated smoke tests must pass (exit code 0) before proceeding to Phase 3. If they fail, fix the reported issues and re-run until all checks pass.

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

**For releases with intermediate documents (handoffs, phase summaries, roadmaps):**

Use automated archival to consolidate, archive, and remove intermediate documents:

```bash
# Preview changes
python3 scripts/archive_release_docs.py vX.Y.Z --dry-run

# Execute archival
python3 scripts/archive_release_docs.py vX.Y.Z
```

→ **See:** [DOCUMENTATION_CONVENTIONS.md § Release Documentation Archival Pattern](DOCUMENTATION_CONVENTIONS.md#release-documentation-archival-pattern) for complete workflow, naming conventions, and manual steps

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

## Future Automation Opportunities

Potential enhancements: Interactive release wizard, pre-release checklist validation, rollback mechanism, PyPI auto-publishing

---

## Time Estimates

**Current Process (v3.7.1+):**
- Phase 1 (Preparation): 15-20 min (80% automated via `bump_version.py --auto-update`)
- Phase 2 (Build & Package): ~5 min (automated: `smoke_test.py` validation)
- Phase 3 (Version Control): ~5 min (git tag, push, GitHub Actions release)
- **Total: 30-40 minutes**

**Automation Tools:**
- `pre_release_check.py` - Git, version, tests, security, coverage validation
- `bump_version.py --auto-update` - Version bump + 3-file doc updates
- `smoke_test.py` - Package installation and CLI verification

**Efficiency Gains vs. Manual Process (pre-v3.7.1):**

| Component | Manual | Automated | Reduction |
|-----------|--------|-----------|-----------|
| Version management | 15-20 min | 1 min | 93% |
| Pre-release testing | 15-20 min | 5 min | 67% |
| Package verification | 10-15 min | 3 min | 70% |
| **Total** | **55-80 min** | **30-40 min** | **50-60%** |

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
