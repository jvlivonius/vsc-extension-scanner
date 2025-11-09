# Version Management

**Purpose:** Simplified version management with automated documentation updates
**Document Type:** Reference Guide
**Last Updated:** 2025-11-01

---

## Single Source of Truth

**File:** `vscode_scanner/_version.py`

Contains:
- `__version__` - Application version (e.g., "3.5.6")
- `SCHEMA_VERSION` - JSON schema version (e.g., "2.1")

**All** version numbers import from this single file.

---

## Updating Version

### Method 1: Auto-Update (Recommended) ⭐ NEW

```bash
# Bump version AND auto-update documentation
python3 scripts/bump_version.py X.Y.Z --auto-update

# This updates:
# - vscode_scanner/_version.py (source of truth)
# - README.md (version badge)
# - CLAUDE.md (current status)
# - docs/project/PRD.md (version field)
```

### Method 2: Manual Documentation Updates

```bash
# Bump version only (you update docs manually)
python3 scripts/bump_version.py X.Y.Z

# Check current version
python3 scripts/bump_version.py --show

# Validate consistency
python3 scripts/bump_version.py --check
```

### Method 3: Manual Edit

1. Edit `vscode_scanner/_version.py`
2. Update `__version__ = "X.Y.Z"`
3. Run validation: `python3 scripts/bump_version.py --check`

---

## Version Types

### Application Version (`__version__`)

**Format:** Semantic Versioning (X.Y.Z)

- **X (Major):** Breaking changes, major features
- **Y (Minor):** New features (backward compatible)
- **Z (Patch):** Bug fixes, small improvements

**Examples:**
- `3.5.3` → Current
- `3.6.0` → Next minor (new features)
- `4.0.0` → Next major (breaking changes)

### Schema Version (`SCHEMA_VERSION`)

**Format:** Major.Minor

**Purpose:** JSON output schema compatibility

**When to bump:**
- Add/remove top-level fields → major (2.0 → 3.0)
- Add/remove extension object fields → minor (2.0 → 2.1)
- Internal changes without schema impact → no change

---

## Benefits

✅ **One place to update** - Change `_version.py` only
✅ **Automated doc updates** - 3 files updated automatically with `--auto-update`
✅ **No sync issues** - All files import from single source
✅ **Build tools synchronized** - Auto-sync with pyproject.toml
✅ **Runtime consistency** - CLI `--version` matches package
✅ **Automated validation** - Script checks for hardcoded versions
✅ **Pre-commit protection** - Hook prevents version mismatches

---

## Files Using Centralized Version

### Package Files
- `vscode_scanner/__init__.py`
- `vscode_scanner/vscan.py`
- `vscode_scanner/output_formatter.py`
- `vscode_scanner/cache_manager.py`
- `vscode_scanner/html_report_generator.py`

### Root Files (standalone usage)
- `vscan.py`
- `output_formatter.py`
- `cache_manager.py`
- `html_report_generator.py`

### Build Configuration
- `pyproject.toml` - Uses `dynamic = ["version"]`

---

## Version Consistency Check

The `--check` command validates **both Python and documentation files:**

```bash
python3 scripts/bump_version.py --check
```

**What it validates:**

**Python Files:**
- All modules use `_version.py` import (no hardcoded versions)
- `pyproject.toml` uses dynamic versioning

**Documentation Files (Simplified):**
- README.md version badge (`**Version:** X.Y.Z`)
- CLAUDE.md current status (`**Version:** X.Y.Z`)
- docs/project/PRD.md version field (`**Version:** X.Y.Z`)

**Standardized Pattern:** All docs use `**Version:** X.Y.Z` (no `v` prefix variations)

**Example output:**
```
Current version: 3.5.6
Schema version: 2.1

Python Files:
  ✓ vscode_scanner/__init__.py: Uses centralized version
  ✓ vscode_scanner/vscan.py: Uses centralized version
  ...

Documentation Files:
  ✓ README.md: Version 3.5.6 matches
  ✓ CLAUDE.md: Version 3.5.6 matches
  ✓ docs/project/PRD.md: Version 3.5.6 matches

✓ All files use consistent versioning!
```

**Pre-Commit Hook:**
The version consistency check runs automatically via pre-commit hook when you modify version-related files.

**Manual verification:**
```bash
python3 vscan.py --version
python3 -c "from vscode_scanner import __version__; print(__version__)"
```

---

## Documentation Updates

### Automated (with `--auto-update` flag)

These files are **automatically updated** by the script:
1. ✅ README.md - Version badge
2. ✅ CLAUDE.md - Current Status version
3. ✅ PRD.md - Version field

### Manual Updates Required

These files still require manual editing:
1. ⚠️ CHANGELOG.md - Add release section ([Keep a Changelog](https://keepachangelog.com/) format)
2. ⚠️ docs/archive/summaries/vX.Y.Z-release-notes.md - Create comprehensive release notes

**Why manual?**
- CHANGELOG.md requires human curation of changes (industry best practice)
- Release notes need comprehensive human-written summaries for GitHub releases

**Complete update checklist:** [RELEASE_PROCESS.md § Documentation Updates](RELEASE_PROCESS.md#step-2-documentation-updates)

---

## Release Workflow (Simplified)

**For complete release process, see [RELEASE_PROCESS.md](RELEASE_PROCESS.md)**

Quick reference (NEW simplified workflow):

```bash
# 1. Bump version with auto-update
python3 scripts/bump_version.py X.Y.Z --auto-update
# This automatically updates: _version.py, README.md, CLAUDE.md, PRD.md

# 2. Manual documentation updates (only 2 files now!)
# - Edit CHANGELOG.md (add release section)
# - Create docs/archive/summaries/vX.Y.Z-release-notes.md

# 3. Test and build
pytest tests/
python3 -m build

# 4. Commit and tag
git commit -m "chore(release): bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main vX.Y.Z
```

**Time Savings:** 50% reduction in manual steps (3 auto-updated, 2 manual vs 8 manual)

---

## Troubleshooting

### Version Mismatch

**Problem:** `--check` reports mismatches

**Solution:**
```bash
# Identify mismatched files
python3 scripts/bump_version.py --check

# Look for hardcoded versions
grep -r "VERSION.*=.*\"[0-9]" --include="*.py" .
```

### Build Fails

**Problem:** Build can't find version

**Solution:**
```bash
# Verify _version.py exists
ls -la vscode_scanner/_version.py

# Test import
python3 -c "from vscode_scanner._version import __version__; print(__version__)"
```

### Import Error

**Problem:** Module can't import version

**Solution:**
- Ensure `_version.py` is in package
- Check `MANIFEST.in` includes `_version.py`
- Verify `__init__.py` imports correctly

---

## Version History

See [CHANGELOG.md](../../CHANGELOG.md) for complete release history.

**Recent versions:**
- **3.5.3** - Testing Excellence complete
- **3.5.0** - Parallel processing (3 workers default)
- **3.3.0** - Duplicate detection, verified filters
- **3.1.0** - Configuration management, CSV export
- **2.2.0** - HTML reports, retry mechanism

---

## Related Documents

- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Complete release workflow using version management
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Printable release checklist with version bump steps
- [DOCUMENTATION_CONVENTIONS.md](DOCUMENTATION_CONVENTIONS.md) - Documentation update patterns
- [CHANGELOG.md](../../CHANGELOG.md) - Complete release history
- [scripts/bump_version.py](../../scripts/bump_version.py) - Version management automation script
- [vscode_scanner/_version.py](../../vscode_scanner/_version.py) - Single source of truth
