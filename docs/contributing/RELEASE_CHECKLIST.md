# Release Checklist

**Purpose:** Comprehensive release checklist
**Document Type:** Checklist

---

## Prerequisites: Git Workflow Verification

**CRITICAL: Verify clean main branch before starting:**

```bash
git status && git branch
# Expected: On branch main, working directory clean
```

- [ ] On `main` branch
- [ ] Working directory clean
- [ ] Up to date with remote (`git pull origin main`)
- [ ] All feature branches merged

→ **See:** [GIT_WORKFLOW.md § Release Workflow](GIT_WORKFLOW.md#release-workflow) and [RELEASE_PROCESS.md § Prerequisites](RELEASE_PROCESS.md#prerequisites)

---

## Phase 1: Pre-Release Preparation

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

#### Step 2a: Release Documentation Consolidation (Multi-Phase Releases Only)

**For releases with multiple phases (roadmap + handoffs + summaries):**

- [ ] Consolidate into comprehensive release notes:
  - [ ] Roadmap objectives → Key Features section
  - [ ] Handoff documents → Implementation Details
  - [ ] Phase summaries → Key Achievements section
  - [ ] Test metrics → Testing section
- [ ] Verify all breaking changes documented with migration guides
- [ ] Verify release notes file created in correct location

**Tools:**
- Manual: Extract key information from source documents
- Automated (future): Use `scripts/archive_release_docs.py vX.Y.Z` (documentation archival only)

**Reference:** [DOCUMENTATION_CONVENTIONS.md § Release Documentation Archival Pattern](DOCUMENTATION_CONVENTIONS.md#release-documentation-archival-pattern)

**Note:** Single-phase releases can skip this step.

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

## Phase 2: Build & Package

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

## Phase 2.5: Release Documentation Archival (Multi-Phase Only)

**For releases with intermediate documents (handoffs, phase summaries):**

### Archive Release Documentation

**Option 1: Automated (Recommended)**

- [ ] `python3 scripts/archive_release_docs.py vX.Y.Z --dry-run` (preview)
- [ ] Review dry-run output (verify documents detected correctly)
- [ ] `python3 scripts/archive_release_docs.py vX.Y.Z` (execute)
- [ ] `git status` (verify changes)

**Option 2: Manual**

- [ ] `git mv docs/project/vX.Y-roadmap.md docs/archive/plans/vX.Y-roadmap.md`
- [ ] `git rm docs/project/vX.Y-phase*-handoff.md` (remove handoffs)
- [ ] `git rm docs/project/vX.Y-phase*-summary.md` (remove phase summaries)
- [ ] `git rm docs/archive/summaries/vX.Y-phase*-completion-summary.md` (remove summaries)
- [ ] Edit `docs/archive/README.md` (add version entry)
- [ ] Edit `docs/project/STATUS.md` (change to "Released")
- [ ] `git add docs/archive/README.md docs/project/STATUS.md`

### Commit Documentation Changes

- [ ] `git status` (verify all changes staged)
- [ ] `git commit -m "docs(vX.Y): Archive release documentation"`
- [ ] `git push origin feature/vX.Y-docs` (or appropriate branch)
- [ ] Create PR: "docs(vX.Y): Finalize release documentation"
- [ ] Get approval and merge PR
- [ ] `git checkout main && git pull` (switch back to main)

**Reference:** [DOCUMENTATION_CONVENTIONS.md § Release Documentation Archival Pattern](DOCUMENTATION_CONVENTIONS.md#release-documentation-archival-pattern)

**Note:** Single-phase releases without intermediate documents can skip this phase entirely.

---

## Phase 3: Version Control

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

### GitHub Release (Automated via Workflow)

**Primary: GitHub Actions (Automatic)**

- [ ] Tag push triggers GitHub Actions workflow automatically
- [ ] `gh run watch` (monitor workflow execution)
- [ ] `gh run list --workflow=release.yml` (check status)
- [ ] Verify workflow completes successfully
- [ ] Verify GitHub release created with artifacts

**If Workflow Fails: Manual Creation (Fallback)**

- [ ] **CLI:** `gh release create vX.Y.Z dist/*.whl dist/SHA256SUMS.txt --title "vX.Y.Z" --notes-file docs/archive/summaries/vX.Y.Z-release-notes.md`
- [ ] **Web:** Repository → Releases → Draft → Select tag → Upload → Publish

### Correcting Releases (If Needed)

**If release notes need updates after tag push:**

- [ ] `git checkout main && git pull origin main`
- [ ] `gh release delete vX.Y.Z --yes`
- [ ] `git tag -d vX.Y.Z`
- [ ] `git push origin --delete vX.Y.Z`
- [ ] Update `docs/archive/summaries/vX.Y.Z-release-notes.md`
- [ ] `git add docs/archive/summaries/vX.Y.Z-release-notes.md`
- [ ] `git commit -m "docs: Update vX.Y.Z release notes"`
- [ ] `git push origin main`
- [ ] `git tag -a vX.Y.Z -F docs/archive/summaries/vX.Y.Z-release-notes.md`
- [ ] `git push origin vX.Y.Z`
- [ ] `gh run watch` (monitor automated release creation)

---

## Verification

- [ ] GitHub release visible and downloadable
- [ ] CHANGELOG.md updated
- [ ] README.md shows X.Y.Z
- [ ] STATUS.md reflects release
- [ ] `git tag -l vX.Y.Z` exists

---

## Related Documents

- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Complete release process guide
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version bump procedures
- [GIT_WORKFLOW.md](GIT_WORKFLOW.md) - Git prerequisites and release workflow
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Pre-release testing validation
- [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) - Release documentation archival

---

**Next Steps:** Distribution ([DISTRIBUTION.md](../../DISTRIBUTION.md)), post-release communication, roadmap planning
