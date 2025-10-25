# Release Notes: v{VERSION}

**Release Date:** {YYYY-MM-DD}
**Status:** Production Ready / Beta / Release Candidate

---

## Summary

{One paragraph overview of the release - what's the main theme or focus?}

Example: This release focuses on performance improvements and user experience enhancements, introducing parallel scanning capabilities and improved error reporting.

---

## Key Features

### Feature 1: {Feature Name}

{Brief description of the feature and why it's valuable}

**Usage:**
```bash
{Example command or code showing how to use it}
```

### Feature 2: {Feature Name}

{Brief description}

**Usage:**
```bash
{Example command}
```

---

## Improvements

- {Improvement 1 - be specific about what improved and the impact}
- {Improvement 2}
- {Improvement 3}

---

## Bug Fixes

- **Fixed:** {Bug description} - {Impact of the fix}
- **Fixed:** {Bug description} - {Impact of the fix}
- **Fixed:** {Bug description} - {Impact of the fix}

---

## Breaking Changes

{If there are NO breaking changes, write: "None - This release is fully backward compatible with v{PREVIOUS_VERSION}"}

{If there ARE breaking changes, list each one with migration instructions:}

### Breaking Change 1: {Description}

**What changed:**
{Explain what changed and why}

**Migration guide:**
```bash
# Old way (v{OLD_VERSION})
{old command or code}

# New way (v{NEW_VERSION})
{new command or code}
```

**Action required:**
{What users need to do to migrate}

---

## Installation

### New Installation

```bash
pip install vscode_extension_scanner-{VERSION}-py3-none-any.whl
```

### Upgrade from Previous Version

```bash
pip install --upgrade vscode_extension_scanner-{VERSION}-py3-none-any.whl
```

**Verify installation:**
```bash
vscan --version
# Should show: {VERSION}
```

---

## Upgrade Notes

### From v{PREVIOUS_MAJOR_VERSION}.x

{List any special considerations when upgrading from previous major version}

- {Note 1}
- {Note 2}

### From v{PREVIOUS_MINOR_VERSION}.x

{List any special considerations when upgrading from previous minor version}

- {Note 1}
- {Note 2}

### Database/Cache

{If cache schema changed:}
- Cache will be automatically migrated from v{OLD_SCHEMA} to v{NEW_SCHEMA}
- No action required - migration happens on first run

{If no schema change:}
- No cache migration required
- All cached data remains compatible

---

## Known Issues

{If there are NO known issues, write: "None - All known issues from v{PREVIOUS_VERSION} have been resolved."}

{If there ARE known issues, list them:}

### Issue 1: {Brief description}

**Symptoms:**
{What users will observe}

**Workaround:**
{Temporary solution or mitigation}

**Status:**
{Planned fix in v{FUTURE_VERSION} or investigating}

---

## Deprecation Notices

{If there are NO deprecations, write: "None"}

{If there ARE deprecations:}

### Deprecated: {Feature/Flag/Command}

- **Deprecated in:** v{VERSION}
- **Will be removed in:** v{FUTURE_VERSION}
- **Replacement:** {Alternative to use}
- **Migration guide:** {Link to migration docs or instructions}

---

## Documentation

- **Full Changelog:** [CHANGELOG.md](../../CHANGELOG.md)
- **Release Process:** [RELEASE_PROCESS.md](../contributing/RELEASE_PROCESS.md)
- **User Guide:** [README.md](../../README.md)
- **Developer Guide:** [CLAUDE.md](../../CLAUDE.md)

---

## Testing

This release has been tested on:

- ✅ macOS {version} (primary platform)
- ✅ Windows {version} (if tested)
- ✅ Linux {distribution} (if tested)

**Test coverage:**
- {X} test files
- {Y} total tests
- {Z}% code coverage

---

## Contributors

{If applicable, thank contributors:}

Special thanks to the following contributors:
- {Name} - {Contribution}
- {Name} - {Contribution}

{If solo project:}

This release was developed by {Your Name}.

---

## Feedback

Found a bug? Have a feature request?

- **Issues:** {GitHub issues URL or email}
- **Questions:** {Support channel or email}
- **Documentation:** {Docs URL or wiki}

---

## What's Next

Planned for v{NEXT_VERSION}:

- {Planned feature 1}
- {Planned feature 2}
- {Planned improvement 1}

See [v{NEXT_VERSION}-ROADMAP.md](../project/v{NEXT_VERSION}-ROADMAP.md) for details.

---

**Happy scanning! Stay secure.**
