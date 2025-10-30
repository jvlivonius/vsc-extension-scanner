# Release Checklist

**Version:** ___________
**Release Date:** ___________
**Release Manager:** ___________

---

## Pre-Release Preparation

### Version Management

- [ ] **Update version**
  ```bash
  python3 scripts/bump_version.py X.Y.Z
  ```

- [ ] **Verify version consistency**
  ```bash
  python3 scripts/bump_version.py --check
  ```
  - [ ] All Python files use centralized version
  - [ ] README.md version matches
  - [ ] CLAUDE.md version matches
  - [ ] docs/project/STATUS.md version matches
  - [ ] docs/project/PRD.md version matches
  - [ ] DISTRIBUTION.md version examples match

### Documentation Updates

- [ ] **CHANGELOG.md** (Root)
  - [ ] Added new `## [X.Y.Z] - YYYY-MM-DD` section
  - [ ] Documented under: Added, Changed, Fixed, Deprecated, Removed, Security
  - [ ] Included migration notes (if breaking changes)
  - [ ] Updated comparison links at bottom

- [ ] **README.md** (Root)
  - [ ] Updated version number (line 7)
  - [ ] Updated installation examples (if changed)
  - [ ] Updated feature list (if new features)

- [ ] **CLAUDE.md** (Root)
  - [ ] Updated "Current Status" section (~line 21)
  - [ ] Moved in-progress work to "Previous Updates"
  - [ ] Added new release to "Latest Updates"
  - [ ] Verified all version references match

- [ ] **DISTRIBUTION.md** (Root)
  - [ ] Updated version references
  - [ ] Updated wheel filename examples
  - [ ] Updated troubleshooting (if new issues)

- [ ] **docs/project/STATUS.md**
  - [ ] Updated current version (line 5)
  - [ ] Updated schema version if changed (line 6)
  - [ ] Added new release section
  - [ ] Updated "Next Release" section

- [ ] **docs/project/PRD.md**
  - [ ] Updated version (if requirements changed)
  - [ ] Updated feature scope (if applicable)
  - [ ] Updated constraints (if applicable)

- [ ] **docs/README.md**
  - [ ] Verified navigation table is current
  - [ ] Verified all links work
  - [ ] Updated if new docs added

- [ ] **Release Notes** (Recommended)
  - [ ] Created `docs/archive/summaries/vX.Y.Z-release-notes.md`
  - [ ] Used template from `docs/templates/release-notes-template.md`
  - [ ] Included: summary, features, fixes, breaking changes, upgrade notes

### Archive Cleanup (if applicable)

- [ ] **Archived completed roadmap** (if completing a versioned roadmap)
  - [ ] Moved `docs/project/vX.Y-ROADMAP.md` to `docs/archive/plans/`
  - [ ] Updated `docs/archive/README.md` navigation
  - [ ] Followed DOCUMENTATION_CONVENTIONS.md naming

### Pre-Release Testing

#### Automated Tests

- [ ] **Run all test suites:**
  ```bash
  # Recommended: Run all with pytest
  pytest tests/

  # Alternative: Run individually
  for test in tests/test_*.py; do python3 "$test"; done
  ```

- [ ] **All tests passed** (no failures)
- [ ] **Test coverage:** See `tests/` directory for current test modules

#### Manual Verification

- [ ] `vscan --version` shows correct version (X.Y.Z)
- [ ] `vscan --help` displays correctly
- [ ] `vscan scan` works with real extensions
- [ ] `vscan scan --output report.html` generates valid HTML
- [ ] `vscan scan --output results.json` generates valid JSON
- [ ] `vscan scan --output data.csv` generates valid CSV
- [ ] `vscan cache stats` displays correctly
- [ ] `vscan config show` displays correctly

#### Platform Testing

- [ ] Tested on macOS (primary platform)
- [ ] Tested on Windows (if available)
- [ ] Tested on Linux (if available)

#### Version Consistency Check

- [ ] **Verified version appears consistently:**
  ```bash
  python3 scripts/bump_version.py --show
  python3 -c "from vscode_scanner import __version__; print(__version__)"
  vscan --version
  # All should show: X.Y.Z
  ```

---

## Build & Package

### Clean Build Environment

- [ ] **Removed old build artifacts:**
  ```bash
  rm -rf build/
  rm -rf dist/
  rm -rf *.egg-info
  rm -rf vscode_scanner.egg-info
  ```

- [ ] **Verified cleanup completed**
  ```bash
  ls -la build/ dist/ *.egg-info 2>&1 | grep "No such file"
  ```

### Build Distribution Package

- [ ] **Ensured build tools installed:**
  ```bash
  python3 -m pip install --upgrade build
  ```

- [ ] **Built distribution package:**
  ```bash
  python3 -m build
  ```

- [ ] **Verified outputs created:**
  ```bash
  ls -lh dist/
  # Should show:
  #   vscode_extension_scanner-X.Y.Z-py3-none-any.whl
  #   vscode_extension_scanner-X.Y.Z.tar.gz
  ```

### Verify Package Installation

- [ ] **Created test virtual environment**
  ```bash
  python3 -m venv test-release-env
  source test-release-env/bin/activate
  ```

- [ ] **Installed from built wheel**
  ```bash
  pip install dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl
  ```

- [ ] **Verified installation:**
  - [ ] `vscan --version` shows X.Y.Z
  - [ ] `vscan --help` displays correctly
  - [ ] `vscan cache stats` works without errors
  - [ ] `python3 -c "import vscode_scanner; print(vscode_scanner.__version__)"` shows X.Y.Z

- [ ] **Cleaned up test environment**
  ```bash
  deactivate
  rm -rf test-release-env
  ```

### Generate Package Metadata

- [ ] **Generated SHA256 checksums:**
  ```bash
  cd dist/
  shasum -a 256 *.whl *.tar.gz > SHA256SUMS.txt
  cat SHA256SUMS.txt  # Verify
  cd ..
  ```

- [ ] **GPG signature** (Optional - if using)
  ```bash
  gpg --armor --detach-sign dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl
  ```

---

## Version Control

### Commit Release Changes

- [ ] **Staged all updated files:**
  ```bash
  git add vscode_scanner/_version.py
  git add CHANGELOG.md
  git add README.md
  git add CLAUDE.md
  git add DISTRIBUTION.md
  git add docs/project/STATUS.md
  git add docs/project/PRD.md
  git add docs/README.md
  git add docs/archive/summaries/vX.Y.Z-release-notes.md
  # If archiving:
  git add docs/archive/plans/vX.Y-ROADMAP.md
  git add docs/archive/README.md
  ```

- [ ] **Verified staged files:**
  ```bash
  git status
  ```

- [ ] **Committed with descriptive message:**
  ```bash
  git commit -m "Release vX.Y.Z: {Brief description}

  - Bumped version to X.Y.Z
  - Updated all documentation
  - Created release notes
  - {Other changes}

  See CHANGELOG.md for full details"
  ```

### Create Version Tag

- [ ] **Created annotated tag:**
  ```bash
  git tag -a vX.Y.Z -m "Release vX.Y.Z

  {Brief description}

  Key changes:
  - Feature 1
  - Feature 2
  - Bug fix 1

  See CHANGELOG.md for complete details"
  ```

- [ ] **Verified tag:**
  ```bash
  git tag -l -n9 vX.Y.Z
  git log --oneline -1 vX.Y.Z
  ```

### Push to Remote

- [ ] **Pushed commits to remote:**
  ```bash
  git push origin [branch-name]
  ```

- [ ] **Pushed version tag to remote:**
  ```bash
  git push origin vX.Y.Z
  ```

- [ ] **Verified tag pushed successfully:**
  ```bash
  git ls-remote --tags origin | grep vX.Y.Z
  ```

### Create GitHub Release

- [ ] **Created GitHub release:**

  **Using GitHub CLI:**
  ```bash
  gh release create vX.Y.Z \
    dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl \
    dist/SHA256SUMS.txt \
    --title "vX.Y.Z" \
    --notes-file docs/archive/summaries/vX.Y.Z-release-notes.md
  ```

  **Fallback: Via GitHub Web Interface:**
  - [ ] Navigated to repository → Releases → Draft new release
  - [ ] Selected tag vX.Y.Z
  - [ ] Set release title: vX.Y.Z
  - [ ] Copied release notes
  - [ ] Uploaded wheel and checksums
  - [ ] Published release

---

## Post-Release Verification

- [ ] **Verified release artifacts:**
  - [ ] GitHub release created
  - [ ] Wheel file downloadable
  - [ ] Checksums match

- [ ] **Verified documentation:**
  - [ ] CHANGELOG.md updated
  - [ ] README.md shows correct version
  - [ ] STATUS.md reflects release

- [ ] **Verified git history:**
  - [ ] Tag exists: `git tag -l vX.Y.Z`
  - [ ] Commit message clear and descriptive
  - [ ] All changes included

---

## Notes

**Issues Encountered:**

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

**Time Taken:**

- Pre-Release Preparation: _______ minutes
- Build & Package: _______ minutes
- Version Control: _______ minutes
- **Total:** _______ minutes

**Improvements for Next Release:**

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

---

## Reference

**Full Process Documentation:** [RELEASE_PROCESS.md](RELEASE_PROCESS.md)
**Version-Specific Changes:** [CHANGELOG.md](../../CHANGELOG.md)

**Release Complete!** ✅

Next steps (separate workflows):
- Distribution (follow DISTRIBUTION.md)
- Post-release communication
- Roadmap planning for next version
