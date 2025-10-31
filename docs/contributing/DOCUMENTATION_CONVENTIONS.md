# Documentation Conventions

**Purpose:** Consistent naming, organization, and maintenance of project documentation

**Version:** 2.0
**Last Updated:** 2025-10-31

---

## Core Principles

### Single Source of Truth
- Each concept documented in **ONE** canonical location
- Other documents link to canonical source, never duplicate
- See `docs/guides/_CANONICAL_REFERENCES.md` for complete index

### Timeless vs. Versioned
- **guides/**, **contributing/** - Timeless, updated in place
- **project/** - Active, archived when complete
- **archive/** - Historical, version-prefixed, immutable

### Dynamic References
- Prefer code references over hard-coded values
- Link to canonical docs, don't duplicate tables/constants
- Use pattern descriptions, not line numbers

---

## Directory Structure

```
docs/
├── guides/         # Timeless technical reference (NEVER archive)
├── project/        # Active project management (archive when complete)
├── contributing/   # Contributor guides (NEVER archive)
├── templates/      # Document templates
└── archive/        # Historical documentation (version-based)
    ├── plans/      # Roadmaps, requirements, specs
    ├── summaries/  # Release notes, completion reports
    └── reviews/    # Analysis, research, retrospectives
```

**Directory Rules:**

| Directory | Archive? | Naming Pattern | Purpose |
|-----------|----------|----------------|---------|
| **guides/** | NEVER | lowercase-hyphenated | Timeless technical docs |
| **project/** | When complete | lowercase-hyphenated | Current status/plans |
| **contributing/** | NEVER | SCREAMING_SNAKE_CASE | Process guides |
| **templates/** | NEVER | lowercase-hyphenated | Document templates |
| **archive/*** | Created here | vX.Y-description | Historical snapshots |

---

## Naming Conventions

### Active Documentation

**guides/** and **project/**
- Format: `lowercase-hyphenated-name.md`
- Example: `error-handling.md`, `security.md`
- No version numbers (living documents)

**contributing/**
- Format: `SCREAMING_SNAKE_CASE.md`
- Example: `TESTING_CHECKLIST.md`, `VERSION_MANAGEMENT.md`
- Stands out as important process documents

### Archived Documentation

**All archives MUST start with version prefix:**

| Type | Format | Example |
|------|--------|---------|
| **Roadmap** | `vX.Y-roadmap.md` | `v3.1-roadmap.md` |
| **Feature Spec** | `vX.Y-{feature}-spec.md` | `v2.2-html-reports-spec.md` |
| **Release Notes** | `vX.Y-release-notes.md` | `v3.1-release-notes.md` |
| **Analysis** | `vX.Y-{topic}-analysis.md` | `v2.2-retry-analysis.md` |
| **Multi-version** | `vX.Y-vZ.W-{description}.md` | `v1.0-v2.0-phase1-research.md` |

**Version Format:**
- Always lowercase 'v': `v3.1` not `V3.1`
- No spaces: `v3.1-roadmap.md` not `v3.1 - roadmap.md`
- Major.Minor (no patch): `v3.1` not `v3.1.2`

---

## Document Lifecycle

### Creating Active Documents

1. Create in appropriate directory (guides/, project/, contributing/)
2. Use correct naming convention
3. Add to `docs/README.md` index
4. Reference in `CLAUDE.md` if developer-facing

### Archiving Documents

**When to Archive:**

| Document Type | Trigger | Destination |
|---------------|---------|-------------|
| Roadmaps | Version releases | `archive/plans/` |
| Feature Specs | Implementation complete | `archive/plans/` |
| Release Notes | Created in archive | `archive/summaries/` |
| Analysis/Research | After completion | `archive/reviews/` |

**How to Archive:**

```bash
# Step 1: Move with version prefix
git mv docs/project/ROADMAP.md docs/archive/plans/v3.2-roadmap.md

# Step 2: Update cross-references
grep -r "ROADMAP.md" docs/ --include="*.md"
# Update found references in CLAUDE.md, docs/README.md, etc.

# Step 3: Update archive index
# Add entry to docs/archive/README.md

# Step 4: Commit
git add -A
git commit -m "Archive: Move v3.2 roadmap after completion"
```

**Never Archive:**
- `guides/*` - Timeless design principles
- `contributing/*` - Active processes
- These are living documents defining current practices

---

## Maintainability Patterns

### Reference Pattern (Good)

```markdown
✅ Exit codes: See [ERROR_HANDLING.md § Exit Codes](../guides/ERROR_HANDLING.md#exit-codes)
✅ Version bump: Update `## Current Status` section in CLAUDE.md
✅ Constants: See `constants.py:MAX_RESPONSE_SIZE_BYTES`
✅ Git workflow: See [GIT_WORKFLOW.md](GIT_WORKFLOW.md) - Canonical branching strategy
✅ Branch protection: See [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) - GitHub settings
```

### Duplication Anti-Pattern (Bad)

```markdown
❌ Duplicating exit code table in 3 different files
❌ Hard-coding: "The API response limit is 10MB"
❌ Line references: "Update line 7 in README.md"
```

### Timeless vs. Brittle

| ❌ Brittle (Line Numbers) | ✅ Timeless (Patterns) |
|--------------------------|------------------------|
| "Update line 7" | "Update version badge in header section" |
| "CLAUDE.md line 21" | "Update `## Current Status` section in CLAUDE.md" |
| "Lines 5-6" | "Update `**Current Version:**` field" |

### Dynamic vs. Hard-Coded

| ❌ Hard-Coded | ✅ Dynamic |
|--------------|-----------|
| `test_scanner.py (25 tests)` | `Run pytest --collect-only -q tests/` |
| `timeout=30 seconds` | `See constants.py:API_TIMEOUT_SECONDS` |
| `Version: 3.5.1` | `Document Type: Timeless Reference` |

---

## Cross-Reference Management

**Always update cross-references when moving/renaming files.**

### Find References

```bash
# Find all references to a file
grep -r "old-filename.md" docs/ --include="*.md"
```

### Priority Files to Check

**Always check:**
- `CLAUDE.md` - Project instructions
- `docs/README.md` - Documentation index
- `docs/archive/README.md` - Archive index (if archiving)

**Check if relevant:**
- `docs/project/STATUS.md`
- `docs/project/PRD.md`
- All markdown files via grep

---

## Git Best Practices

### Use git mv (Preserves History)

```bash
# ✅ Correct
git mv docs/old-name.md docs/new-name.md

# ❌ Wrong - breaks history
rm docs/old-name.md && touch docs/new-name.md
```

### Commit Message Format

```
<Type>: <Short Description>

<Details if needed>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `Docs:`, `Rename:`, `Archive:`, `Fix:`, `Refactor:`

**Examples:**
```bash
git commit -m "Docs: Add DOCUMENTATION_CONVENTIONS.md"
git commit -m "Rename: phase4-summary.md → v2.0-phase4-release-notes.md"
git commit -m "Archive: Move v3.1 roadmap after release"
```

---

## Anti-Patterns to Avoid

### Naming Anti-Patterns

```
❌ phase4-summary.md              → Which Phase 4? What version?
✅ v2.0-phase4-release-notes.md   → Clear version association

❌ TESTING.md (in guides/)        → Should be lowercase
✅ testing.md                     → Correct for guides/

❌ docs/guides/v3.2-roadmap.md    → Guides are timeless
✅ docs/archive/plans/v3.2-roadmap.md → Correct location
```

### Duplication Anti-Pattern

```markdown
❌ Same exit code table in 3 files

✅ In ERROR_HANDLING.md (canonical):
[Complete exit code table]

✅ In other docs:
See [ERROR_HANDLING.md § Exit Codes](../guides/ERROR_HANDLING.md#exit-codes)
```

### Line Number Anti-Pattern

```markdown
❌ "Update line 7 in README.md"
✅ "Update version badge in README.md header section"

❌ "CLAUDE.md line ~21"
✅ "Update `## Current Status` section in CLAUDE.md"
```

---

## Quick Reference

### Common Operations

**Rename Active Document:**
```bash
git mv docs/guides/old.md docs/guides/new.md
grep -r "old.md" docs/ --include="*.md"
# Update references
git commit -m "Rename: old.md → new.md"
```

**Archive Completed Work:**
```bash
git mv docs/project/ROADMAP.md docs/archive/plans/v3.2-roadmap.md
# Update cross-references
# Add to docs/archive/README.md
git commit -m "Archive: Move v3.2 roadmap"
```

**Create Archived Document:**
```bash
touch docs/archive/summaries/v3.3-release-notes.md
# Edit file
# Add to docs/archive/README.md
git commit -m "Docs: Add v3.3 release notes"
```

### Decision Tree

**Where should this document go?**

```
Timeless technical docs? → docs/guides/ (lowercase-hyphenated)
Active project management? → docs/project/ (lowercase-hyphenated)
Process/contributor guide? → docs/contributing/ (SCREAMING_SNAKE_CASE)
Document template? → docs/templates/ (lowercase-hyphenated)
Historical roadmap/plan? → docs/archive/plans/ (vX.Y-name)
Release notes/summary? → docs/archive/summaries/ (vX.Y-name)
Analysis/research/review? → docs/archive/reviews/ (vX.Y-topic-type)
```

### Validation Commands

```bash
# Find references to a file
grep -r "filename.md" docs/ --include="*.md"

# Find archived docs for version
find docs/archive -name "v3.1-*"

# Check for line number references
grep -r "line [0-9]" docs/ --include="*.md"

# Check naming convention violations
find docs/guides docs/project -name "v[0-9]*"
find docs/archive/plans docs/archive/summaries -name "*.md" ! -name "v[0-9]*" ! -name "README.md"

# Run documentation freshness check
./scripts/check_doc_freshness.sh
```

---

## Validation Checklist

**Before committing documentation changes:**

- [ ] File naming follows conventions (lowercase-hyphenated OR SCREAMING_SNAKE_CASE OR vX.Y-prefix)
- [ ] File location appropriate (guides/, project/, contributing/, archive/)
- [ ] Used `git mv` for renames/moves (not rm + touch)
- [ ] Cross-references updated (grep search completed)
- [ ] Updated CLAUDE.md (if referenced)
- [ ] Updated docs/README.md (if structural change)
- [ ] Updated docs/archive/README.md (if archiving)
- [ ] No line number references (use pattern descriptions)
- [ ] Links to canonical sources instead of duplicating content
- [ ] All markdown links work (no 404s)

---

## Freshness Maintenance

### Automated Checking

```bash
# Run freshness validation
./scripts/check_doc_freshness.sh
```

**Checks for:**
- Version numbers in timeless docs
- Duplicated constants from code
- Hard-coded test counts
- Exit code duplication
- Line number references

### Integration

- ✅ Run before releases
- ✅ Monthly documentation review
- ✅ After major refactors

### Manual Maintenance

- When updating constants, search docs for hard-coded values
- When changing APIs, update canonical documentation only
- After bug fixes, check if docs need updates
- Regular audits using freshness checker

---

## Related Documentation

- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Code versioning (separate from docs)
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Testing process
- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Release workflow
- [../archive/README.md](../archive/README.md) - Archive navigation
- [../README.md](../README.md) - Complete documentation index
- [../../CLAUDE.md](../../CLAUDE.md) - Project instructions

---

## Version History

**v2.0 (2025-10-31)**
- Restructured for maintainability and compactness (888 → 282 lines)
- Removed line number references throughout
- Consolidated naming conventions into single tables
- Simplified anti-patterns and examples
- Enhanced timeless reference patterns

**v1.0 (2025-10-25)**
- Initial release after archive reorganization
- Established version-based naming for archives
- Defined directory structure and purposes
- Codified git best practices

---

_These conventions prioritize clarity and consistency. When in doubt, use pattern-based descriptions and canonical references._

**Maintained By:** Project Contributors
