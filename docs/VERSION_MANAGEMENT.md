# Version Management Guide

## Overview

The VS Code Extension Scanner uses a **centralized version management system** with a single source of truth for all version numbers.

## Single Source of Truth

**File:** [vscode_scanner/_version.py](../vscode_scanner/_version.py)

This file contains:
- `__version__` - Application version (e.g., "2.2.1")
- `SCHEMA_VERSION` - JSON schema version (e.g., "2.0")

## Files That Import From _version.py

All version numbers are imported from `_version.py`:

### Package Files
- [vscode_scanner/__init__.py](../vscode_scanner/__init__.py)
- [vscode_scanner/vscan.py](../vscode_scanner/vscan.py)
- [vscode_scanner/output_formatter.py](../vscode_scanner/output_formatter.py)
- [vscode_scanner/cache_manager.py](../vscode_scanner/cache_manager.py)
- [vscode_scanner/html_report_generator.py](../vscode_scanner/html_report_generator.py)

### Root Files (for standalone usage)
- [vscan.py](../vscan.py)
- [output_formatter.py](../output_formatter.py)
- [cache_manager.py](../cache_manager.py)
- [html_report_generator.py](../html_report_generator.py)

### Build Configuration
- [setup.py](../setup.py) - Reads version dynamically via Python import
- [pyproject.toml](../pyproject.toml) - Uses `dynamic = ["version"]` with setuptools

## Updating the Version

### Method 1: Use the Helper Script (Recommended)

```bash
# Bump to a new version
python3 scripts/bump_version.py 2.3.0

# Check current version
python3 scripts/bump_version.py --show

# Validate consistency
python3 scripts/bump_version.py --check
```

### Method 2: Manual Edit

1. Edit [vscode_scanner/_version.py](../vscode_scanner/_version.py)
2. Update `__version__ = "X.Y.Z"`
3. Run validation: `python3 scripts/bump_version.py --check`

## Version Types

### Application Version (`__version__`)

**Format:** Semantic Versioning (X.Y.Z)

- **X (Major):** Breaking changes, major new features
- **Y (Minor):** New features, enhancements (backward compatible)
- **Z (Patch):** Bug fixes, small improvements

**Examples:**
- `2.2.1` → Current version
- `2.3.0` → Next minor version (new features)
- `3.0.0` → Next major version (breaking changes)

### Schema Version (`SCHEMA_VERSION`)

**Format:** Major.Minor

**Purpose:** Tracks JSON output schema compatibility

- Only changed when JSON schema structure changes
- Current: `"2.0"` (introduced in Phase 4)
- Previous: `"1.0"` (Phase 1-3)

**When to bump:**
- Add/remove top-level fields → bump major (2.0 → 3.0)
- Add/remove fields in extensions object → bump minor (2.0 → 2.1)
- Internal changes without schema impact → no change

## Benefits of Centralized Versioning

✅ **One place to update** - Change version in `_version.py` only
✅ **No sync issues** - All files import from single source
✅ **Build tools synchronized** - setup.py and pyproject.toml auto-sync
✅ **Runtime consistency** - CLI `--version` always matches package
✅ **Automated validation** - Script checks for hardcoded versions

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 2.2.1 | 2025-10-24 | HTML report feature + documentation updates |
| 2.2.0 | 2025-10-23 | Retry mechanism + HTML reports |
| 2.1.0 | 2025-10-23 | Code quality improvements + security fixes |
| 2.0.0 | 2025-10-22 | Phase 4: Enhanced data integration |
| 1.0.0 | 2025-10-20 | Initial release (Phases 1-3) |

## Common Tasks

### Release a New Version

```bash
# 1. Update version
python3 scripts/bump_version.py 2.3.0

# 2. Verify consistency
python3 scripts/bump_version.py --check

# 3. Test the build
python3 -m build

# 4. Verify version in package
python3 -c "from vscode_scanner import __version__; print(__version__)"

# 5. Commit changes
git add vscode_scanner/_version.py
git commit -m "Bump version to 2.3.0"
```

### Check Version Consistency

```bash
# Quick check
python3 scripts/bump_version.py --check

# Manual verification
python3 vscan.py --version
python3 -c "from vscode_scanner import __version__; print(__version__)"
```

### Troubleshooting

**Problem:** Version mismatch in different files

**Solution:**
```bash
# Check for issues
python3 scripts/bump_version.py --check

# Look for hardcoded versions
grep -r "VERSION.*=.*\"[0-9]" --include="*.py" .
```

**Problem:** Build fails with version error

**Solution:**
```bash
# Ensure _version.py exists
ls -la vscode_scanner/_version.py

# Verify imports work
python3 -c "from vscode_scanner._version import __version__; print(__version__)"
```

## Documentation Updates

When bumping versions, also update:

1. ✅ [CLAUDE.md](../CLAUDE.md) - Current Status section
2. ✅ [README.md](../README.md) - Version badge
3. ⚠️ [CHANGELOG.md](../CHANGELOG.md) - Add release notes (if created)

## See Also

- [scripts/bump_version.py](../scripts/bump_version.py) - Version management script
- [vscode_scanner/_version.py](../vscode_scanner/_version.py) - Single source of truth
- [setup.py](../setup.py) - Package setup with dynamic versioning
- [pyproject.toml](../pyproject.toml) - Modern Python packaging config
