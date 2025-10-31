# Version Management

**Purpose:** Centralized version management with single source of truth

**Last Updated:** 2025-10-31

---

## Single Source of Truth

**File:** `vscode_scanner/_version.py`

Contains:
- `__version__` - Application version (e.g., "3.5.3")
- `SCHEMA_VERSION` - JSON schema version (e.g., "2.1")

**All** version numbers import from this single file.

---

## Updating Version

### Method 1: Helper Script (Recommended)

```bash
# Bump to new version
python3 scripts/bump_version.py X.Y.Z

# Check current version
python3 scripts/bump_version.py --show

# Validate consistency
python3 scripts/bump_version.py --check
```

### Method 2: Manual Edit

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
✅ **No sync issues** - All files import from single source
✅ **Build tools synchronized** - Auto-sync with setup.py/pyproject.toml
✅ **Runtime consistency** - CLI `--version` matches package
✅ **Automated validation** - Script checks for hardcoded versions

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
- `setup.py` - Dynamic via Python import
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
- `setup.py` and `pyproject.toml` use dynamic versioning

**Documentation Files:**
- README.md version badge
- CLAUDE.md `## Current Status` section
- docs/project/STATUS.md `**Current Version:**` field
- docs/project/PRD.md version field
- DISTRIBUTION.md version examples

**Example output:**
```
Current version: 3.5.3
Schema version: 2.1

Python Files:
  ✓ vscode_scanner/__init__.py: Uses centralized version
  ✓ vscode_scanner/vscan.py: Uses centralized version
  ...

Documentation Files:
  ✓ README.md: Version 3.5.3 matches
  ✓ CLAUDE.md: Version 3.5.3 matches
  ✓ docs/project/STATUS.md: Version 3.5.3 matches
  ✓ docs/project/PRD.md: Version 3.5.3 matches
  ✓ DISTRIBUTION.md: All examples use 3.5.3

✓ All files use consistent versioning!
```

**Manual verification:**
```bash
python3 vscan.py --version
python3 -c "from vscode_scanner import __version__; print(__version__)"
```

---

## Documentation Updates

When bumping versions, update these files (validated by `bump_version.py --check`):

1. ✅ CHANGELOG.md - Add release section ([Keep a Changelog](https://keepachangelog.com/) format)
2. ✅ README.md - Version badge in header section
3. ✅ CLAUDE.md - `## Current Status` section
4. ✅ DISTRIBUTION.md - Version examples throughout
5. ✅ docs/project/STATUS.md - `**Current Version:**` field
6. ✅ docs/project/PRD.md - Version field (if requirements changed)
7. ✅ docs/README.md - Navigation and links
8. ✅ docs/archive/summaries/vX.Y.Z-release-notes.md - Create new

**Complete update checklist:** [RELEASE_PROCESS.md § Documentation Updates](RELEASE_PROCESS.md#step-2-documentation-updates)

---

## Release Workflow

**For complete release process, see [RELEASE_PROCESS.md](RELEASE_PROCESS.md)**

Quick reference:

```bash
# 1. Bump version
python3 scripts/bump_version.py X.Y.Z
python3 scripts/bump_version.py --check

# 2. Update 8 documentation files (see RELEASE_PROCESS.md)

# 3. Test and build
pytest tests/
python3 -m build

# 4. Commit and tag
git commit -m "Release vX.Y.Z: ..."
git tag -a vX.Y.Z -m "..."
git push origin main vX.Y.Z
```

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

## Related Documentation

- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Complete 11-step release workflow
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Printable release checklist
- [CHANGELOG.md](../../CHANGELOG.md) - Complete release history
- [scripts/bump_version.py](../../scripts/bump_version.py) - Version management script
- [vscode_scanner/_version.py](../../vscode_scanner/_version.py) - Single source of truth

---

**Maintained By:** Project contributors
