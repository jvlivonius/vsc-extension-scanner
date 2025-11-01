# Release Checklist

**Version:** ___________
**Date:** ___________
**Manager:** ___________

---

## Prerequisites: Git Workflow Verification

**BEFORE starting release process:**

- [ ] `git status` - Working directory is clean (no uncommitted changes)
- [ ] `git branch` - Currently on `main` branch
- [ ] `git pull origin main` - Main branch is up to date with remote
- [ ] All feature branches for this release have been merged to main
- [ ] All PRs for this release have been approved and merged

**If checks fail:**
- If on feature branch: Complete work → Create PR → Merge → Switch to main
- If uncommitted changes: Commit or stash changes first
- If not up to date: Pull latest changes from remote

→ **See:** [GIT_WORKFLOW.md](GIT_WORKFLOW.md) for complete workflow details

---

## Phase 1: Pre-Release Preparation (20-30 min)

### Version Management with Auto-Update

- [ ] `python3 scripts/bump_version.py X.Y.Z --auto-update` (updates 3 files automatically)
- [ ] `python3 scripts/bump_version.py --check` (all files ✓)

### Documentation Updates

#### Automated (3 files - handled by bump_version.py --auto-update)
- [ ] ✅ **README.md** - Version badge (auto-updated)
- [ ] ✅ **CLAUDE.md** - Current Status version (auto-updated)
- [ ] ✅ **docs/project/PRD.md** - Version field (auto-updated)

#### Manual Updates Required (2 files)
- [ ] **CHANGELOG.md** - Add `## [X.Y.Z] - YYYY-MM-DD` section
- [ ] **CHANGELOG.md** - Document: Added, Changed, Fixed, Security
- [ ] **CHANGELOG.md** - Update comparison links at bottom
- [ ] **docs/archive/summaries/vX.Y.Z-release-notes.md** - Create from template

#### Optional Review (as needed)
- [ ] **README.md** - Update installation examples (if changed)
- [ ] **README.md** - Update feature list (if new features added)
- [ ] **CLAUDE.md** - Move in-progress work to previous updates
- [ ] **CLAUDE.md** - Update latest features/roadmap references
- [ ] **docs/project/PRD.md** - Update requirements/constraints (if changed)

### Automated Testing

- [ ] `pytest tests/` (all pass)
- [ ] Alternative: `for test in tests/test_*.py; do python3 "$test"; done`

### Manual Verification

- [ ] `vscan --version` shows X.Y.Z
- [ ] `vscan --help` displays correctly
- [ ] `vscan scan` works with extensions
- [ ] `vscan scan --output report.html` valid HTML
- [ ] `vscan scan --output results.json` valid JSON
- [ ] `vscan scan --output data.csv` valid CSV
- [ ] `vscan cache stats` works
- [ ] `vscan config show` works

### Platform Testing

- [ ] Tested on macOS
- [ ] Tested on Windows (if available)
- [ ] Tested on Linux (if available)

### Version Consistency

- [ ] `python3 scripts/bump_version.py --show` → X.Y.Z
- [ ] `python3 -c "from vscode_scanner import __version__; print(__version__)"` → X.Y.Z
- [ ] `vscan --version` → X.Y.Z

---

## Phase 2: Build & Package (15-20 min)

### Clean Build

- [ ] `rm -rf build/ dist/ *.egg-info`
- [ ] Verify cleanup: `ls -la build/ dist/ *.egg-info 2>&1 | grep "No such file"`

### Build Distribution

- [ ] `python3 -m pip install --upgrade build`
- [ ] `python3 -m build`
- [ ] `ls -lh dist/` shows wheel + tar.gz

### Verify Installation

- [ ] `python3 -m venv test-release-env`
- [ ] `source test-release-env/bin/activate`
- [ ] `pip install dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl`
- [ ] `vscan --version` → X.Y.Z
- [ ] `vscan --help` displays
- [ ] `vscan cache stats` works
- [ ] `python3 -c "import vscode_scanner; print(vscode_scanner.__version__)"` → X.Y.Z
- [ ] `deactivate && rm -rf test-release-env`

### Package Metadata

- [ ] `cd dist/ && shasum -a 256 *.whl *.tar.gz > SHA256SUMS.txt && cd ..`
- [ ] Optional: `gpg --armor --detach-sign dist/vscode_extension_scanner-X.Y.Z-py3-none-any.whl`

---

## Phase 3: Version Control (10-15 min)

### Commit Release

- [ ] `git add vscode_scanner/_version.py README.md CLAUDE.md docs/project/PRD.md`
- [ ] `git add CHANGELOG.md docs/archive/summaries/vX.Y.Z-release-notes.md`
- [ ] Note: 6 files total (3 auto-updated + 2 manual + release notes)
- [ ] `git status` (verify staged files)
- [ ] `git commit -m "chore(release): bump version to X.Y.Z"`

### Create Tag

- [ ] `git tag -a vX.Y.Z -m "Release vX.Y.Z..."`
- [ ] `git tag -l -n9 vX.Y.Z` (verify)
- [ ] `git log --oneline -1 vX.Y.Z` (verify)

### Push to Remote

- [ ] `git push origin main` (push release commit)
- [ ] `git push origin vX.Y.Z` (push tag - permanent!)
- [ ] `git ls-remote --heads origin main` (verify commit pushed)
- [ ] `git ls-remote --tags origin | grep vX.Y.Z` (verify tag pushed)

### GitHub Release

- [ ] **CLI:** `gh release create vX.Y.Z dist/*.whl dist/SHA256SUMS.txt --title "vX.Y.Z" --notes-file docs/archive/summaries/vX.Y.Z-release-notes.md`
- [ ] **Web:** Repository → Releases → Draft → Select tag → Upload → Publish

---

## Verification

- [ ] GitHub release visible and downloadable
- [ ] CHANGELOG.md updated
- [ ] README.md shows X.Y.Z
- [ ] STATUS.md reflects release
- [ ] `git tag -l vX.Y.Z` exists

---

## Notes

**Time Tracking:**
- Phase 1: _______ min
- Phase 2: _______ min
- Phase 3: _______ min
- **Total:** _______ min

**Issues Encountered:**

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

**Improvements for Next Release:**

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

---

**Reference:** [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Full process documentation

**Next Steps:** Distribution ([DISTRIBUTION.md](../../DISTRIBUTION.md)), post-release communication, roadmap planning
