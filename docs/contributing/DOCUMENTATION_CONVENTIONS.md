# Documentation Naming and Organization Conventions

**Version:** 1.0
**Last Updated:** 2025-10-25
**Status:** Active Convention

---

## Table of Contents

1. [Introduction](#introduction)
2. [Directory Structure](#directory-structure)
3. [Naming Conventions](#naming-conventions)
4. [Document Lifecycle](#document-lifecycle)
5. [Cross-Reference Management](#cross-reference-management)
6. [README Requirements](#readme-requirements)
7. [Git Best Practices](#git-best-practices)
8. [Examples & Anti-Patterns](#examples--anti-patterns)
9. [Validation Checklist](#validation-checklist)
10. [Quick Reference](#quick-reference)

---

## Introduction

### Purpose

These conventions ensure **consistency, discoverability, and maintainability** of project documentation. They were established after the 2025-10-25 archive reorganization that eliminated confusion from duplicate "Phase 4" terminology.

### Scope

These conventions apply to **all documentation** in the `docs/` directory:
- Technical guides
- Project management documents
- Feature specifications
- Contributor guides
- Archived documentation

### When to Apply

- ✅ Creating new documentation
- ✅ Renaming existing documents
- ✅ Moving documents between directories
- ✅ Archiving completed work
- ✅ Reorganizing documentation structure

---

## Directory Structure

### Top-Level Organization

```
docs/
├── guides/         # Timeless technical reference (NEVER archive)
│   ├── architecture.md
│   ├── security.md
│   ├── error-handling.md
│   ├── testing.md
│   └── api-reference.md
│
├── project/        # Active project management (archive when complete)
│   ├── STATUS.md
│   ├── PRD.md
│   └── ROADMAP.md
│
├── specs/          # Shipped feature specifications (archive after 2+ versions)
│   ├── html-reports.md
│   ├── retry-mechanism.md
│   └── cli-ux.md
│
├── contributing/   # Contributor guides (NEVER archive)
│   ├── TESTING_CHECKLIST.md
│   ├── VERSION_MANAGEMENT.md
│   └── DOCUMENTATION_CONVENTIONS.md  # This file
│
└── archive/        # Historical documentation (version-based organization)
    ├── README.md   # Navigation guide (REQUIRED)
    ├── plans/      # Roadmaps, requirements, specifications
    ├── summaries/  # Release notes, completion reports
    └── reviews/    # Analysis, research, retrospectives
```

### Directory Purposes

| Directory | Purpose | Archive? | Naming Style |
|-----------|---------|----------|--------------|
| **guides/** | Timeless technical documentation | **NEVER** | lowercase-hyphenated |
| **project/** | Current project status and plans | When complete | lowercase-hyphenated |
| **specs/** | Shipped feature specifications | After 2+ versions | lowercase-hyphenated |
| **contributing/** | Contributor guides and checklists | **NEVER** | SCREAMING_SNAKE_CASE |
| **archive/plans/** | Historical roadmaps and requirements | Created here | vX.Y-description |
| **archive/summaries/** | Historical release notes | Created here | vX.Y-release-notes |
| **archive/reviews/** | Historical analysis and research | Created here | vX.Y-topic-type |

---

## Naming Conventions

### Active Documentation (guides/, project/, specs/)

**Format:** `lowercase-hyphenated-name.md`

**Rules:**
- Use lowercase for all characters
- Separate words with hyphens (kebab-case)
- Be descriptive but concise (2-4 words ideal)
- No version numbers (these are living documents)

**Examples:**
- ✅ `architecture.md`
- ✅ `error-handling.md`
- ✅ `testing-checklist.md`
- ❌ `Architecture.md` (wrong casing)
- ❌ `error_handling.md` (underscores not hyphens)
- ❌ `v3.2-testing.md` (no versions in active docs)

### Contributing Documentation

**Format:** `SCREAMING_SNAKE_CASE.md`

**Rules:**
- Use UPPERCASE for all characters
- Separate words with underscores
- Traditionally used for contributing/process docs
- Stands out as "important process documents"

**Examples:**
- ✅ `TESTING_CHECKLIST.md`
- ✅ `VERSION_MANAGEMENT.md`
- ✅ `DOCUMENTATION_CONVENTIONS.md`
- ❌ `testing-checklist.md` (should be SCREAMING_SNAKE_CASE)

### Archived Documentation (archive/)

**All archived documents MUST start with version prefix.**

#### Plans (Roadmaps & Requirements)

| Document Type | Format | Example |
|---------------|--------|---------|
| **Roadmap** | `vX.Y-roadmap.md` | `v3.1-roadmap.md` |
| **Requirements (single version)** | `vX.Y-{topic}-requirements.md` | `v3.2-security-requirements.md` |
| **Requirements (multi-version)** | `vX.Y-vZ.W-phaseN-{topic}.md` | `v1.0-v2.0-phase1-research.md` |

#### Summaries (Release Notes & Completion Reports)

| Document Type | Format | Example |
|---------------|--------|---------|
| **Release Notes** | `vX.Y-release-notes.md` | `v3.1-release-notes.md` |
| **Phase Summary** | `vX.Y-phaseN-release-notes.md` | `v2.0-phase3-release-notes.md` |
| **Completion Report** | `vX.Y-{feature}-completion.md` | `v3.0-cli-ux-completion.md` |

#### Reviews (Analysis, Research, Retrospectives)

| Document Type | Format | Example |
|---------------|--------|---------|
| **Analysis** | `vX.Y-{topic}-analysis.md` | `v2.2-retry-mechanism-analysis.md` |
| **Review** | `vX.Y-{topic}-review.md` | `v3.0-macos-testing-review.md` |
| **Phase Review** | `vX.Y-phaseN-review.md` | `v3.2-phase1-review.md` |
| **Research** | `vX.Y-{topic}-research.md` | `v2.1-security-research.md` |

### Version Numbering Rules

**Single Version:** `vX.Y`
- Use when document is tied to one specific release
- Example: `v3.1-roadmap.md` (roadmap for v3.1)

**Version Range:** `vX.Y-vZ.W`
- Use when document spans multiple releases
- Commonly used for original implementation phases
- Example: `v1.0-v2.0-phase1-research.md`

**When Uncertain:**
- Use the version where work **started**
- Example: Analysis done during v2.2 development → `v2.2-analysis.md`

**Formatting:**
- Always lowercase 'v': `v3.1` not `V3.1`
- No spaces: `v3.1-roadmap.md` not `v3.1 - roadmap.md`
- Match semantic versioning: Major.Minor (no patch)

---

## Document Lifecycle

### Active Documents

**Creation:**
1. Create in appropriate directory (guides/, project/, specs/)
2. Use lowercase-hyphenated naming
3. Add to `docs/README.md` index
4. Reference in `CLAUDE.md` if developer-facing

**Updates:**
- Update in place (no versioning)
- Track changes via git history
- Update cross-references if needed

### Archiving Documents

**When to Archive:**

| Document Type | Archive Trigger | Destination |
|---------------|----------------|-------------|
| **Roadmaps** | Version releases | `archive/plans/` |
| **Requirements** | Implementation complete | `archive/plans/` |
| **Release Notes** | Created in archive | `archive/summaries/` |
| **Analysis/Research** | Immediately after completion | `archive/reviews/` |
| **Feature Specs** | After 2+ major versions | `archive/specs/` (consider) |

**How to Archive:**

**Step 1: Prepare the File**
```bash
# If in project/, add version prefix and move to archive
git mv docs/project/ROADMAP.md docs/archive/plans/v3.2-roadmap.md

# If already has version-based name
git mv docs/specs/retry-mechanism.md docs/archive/specs/v2.2-retry-mechanism.md
```

**Step 2: Update Cross-References**
- Search for all references: `grep -r "ROADMAP.md" docs/`
- Update each reference to new path
- Check `CLAUDE.md`, `docs/README.md`, `docs/project/STATUS.md`

**Step 3: Update Indexes**
- Add entry to `docs/archive/README.md`
- Update `docs/README.md` if doc was listed
- Update version timeline in archive README

**Step 4: Commit**
```bash
git add -A
git commit -m "Archive: Move v3.2 roadmap to archive

Archived v3.2 roadmap after version completion.
Updated all cross-references.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Never Archive

**These documents stay in active directories:**
- `guides/ARCHITECTURE.md` - Timeless design principles
- `guides/SECURITY.md` - Current security requirements
- `guides/TESTING.md` - Current testing guidelines
- `contributing/TESTING_CHECKLIST.md` - Active process
- `contributing/VERSION_MANAGEMENT.md` - Active process

**Rationale:** These are living documents that define current practices, not historical snapshots.

---

## Cross-Reference Management

### Critical Rule

**ALWAYS update cross-references when moving/renaming files.**

### Finding References

```bash
# Find all markdown files referencing a file
grep -r "old-filename.md" docs/ --include="*.md"

# Find references in CLAUDE.md
grep "old-filename.md" CLAUDE.md

# Find references in specific file
grep "old-filename" docs/README.md
```

### Files to Check

When moving/renaming ANY documentation file, check these files for references:

**Priority 1 (Always Check):**
- [ ] `CLAUDE.md` - Project instructions
- [ ] `docs/README.md` - Documentation index
- [ ] `docs/archive/README.md` - Archive index (if archiving)

**Priority 2 (Check if Relevant):**
- [ ] `docs/project/STATUS.md` - Project status
- [ ] `docs/project/PRD.md` - Product requirements
- [ ] `docs/project/ROADMAP.md` - Current roadmap

**Priority 3 (Scan All):**
- [ ] All markdown files in `docs/` via grep search

### Update Pattern

**Old Reference:**
```markdown
See [Phase 4 Requirements](../archive/phases/phase4-enhanced-data.md)
```

**New Reference:**
```markdown
See [v2.0 Phase 4 Requirements](../archive/plans/v1.0-v2.0-phase4-enhanced-data.md)
```

**Tips:**
- Update both the link text AND the URL
- Use relative paths (`../archive/plans/` not absolute)
- Verify links work after changes

---

## README Requirements

### docs/README.md

**Status:** REQUIRED

**Must Include:**
- Complete directory structure tree
- Quick navigation table
- Documentation by role (developers, PMs, contributors)
- Development history with links to archived phases
- Recent updates section
- Statistics (line counts, doc counts)

**Update When:**
- Adding new top-level documents
- Restructuring directories
- Archiving major documents
- Completing project phases

### docs/archive/README.md

**Status:** REQUIRED

**Must Include:**
- Version timeline with all releases
- Links to plans, summaries, and reviews for each version
- Document type explanations (what goes in plans/ vs summaries/)
- Quick reference commands (find all docs for a version)
- Migration notes (when restructuring happens)
- Naming conventions (short summary)

**Update When:**
- Archiving any document
- Completing a version release
- Restructuring archive organization

### docs/guides/README.md

**Status:** OPTIONAL (but recommended)

**Should Include:**
- Purpose of each guide
- Reading order for new developers
- Cross-references between guides

### docs/specs/README.md

**Status:** OPTIONAL (but recommended)

**Should Include:**
- List of all feature specs
- Version where each feature shipped
- Current status (active, archived, deprecated)

---

## Git Best Practices

### Rule #1: Always Use git mv

**✅ CORRECT:**
```bash
git mv docs/old-name.md docs/new-name.md
git mv docs/project/file.md docs/archive/plans/v3.2-file.md
```

**❌ WRONG:**
```bash
# This breaks git history!
rm docs/old-name.md
touch docs/new-name.md

# This also breaks history!
mv docs/old-name.md docs/new-name.md  # Without git
git add docs/new-name.md
```

**Why:** `git mv` preserves file history, blame annotations, and shows as a rename in diffs.

### Rule #2: Stage Moves Before New Content

```bash
# Good workflow
git mv docs/old.md docs/new.md          # Move first
git add docs/new.md                      # Stage move
# Now edit docs/new.md if needed
git add docs/new.md                      # Stage edits
git commit -m "Rename: old.md → new.md"  # Commit shows rename
```

### Rule #3: Commit Messages for Documentation

**Format:**
```
<Type>: <Short Description>

<Detailed explanation if needed>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `Docs:` - New documentation or major updates
- `Rename:` - Renaming files
- `Archive:` - Moving to archive
- `Fix:` - Fixing broken links or errors
- `Refactor:` - Restructuring without changing content

**Examples:**
```bash
# Good commit messages
git commit -m "Docs: Add DOCUMENTATION_CONVENTIONS.md guide"
git commit -m "Rename: phase4-summary.md → v2.0-phase4-release-notes.md"
git commit -m "Archive: Move v3.1 roadmap after release completion"

# Bad commit messages
git commit -m "update docs"
git commit -m "changes"
git commit -m "moved files"
```

---

## Examples & Anti-Patterns

### Good Examples

**✅ Active Documentation:**
```
docs/guides/architecture.md
docs/guides/error-handling.md
docs/project/STATUS.md
docs/specs/html-reports.md
docs/contributing/TESTING_CHECKLIST.md
```

**✅ Archived Plans:**
```
docs/archive/plans/v1.0-v2.0-phase1-research.md
docs/archive/plans/v3.1-roadmap.md
docs/archive/plans/v3.2-roadmap.md
```

**✅ Archived Summaries:**
```
docs/archive/summaries/v2.0-phase3-release-notes.md
docs/archive/summaries/v3.0-release-notes.md
docs/archive/summaries/v3.1-release-notes.md
```

**✅ Archived Reviews:**
```
docs/archive/reviews/v2.1-security-analysis.md
docs/archive/reviews/v2.2-retry-mechanism-analysis.md
docs/archive/reviews/v3.2-phase1-review.md
```

### Anti-Patterns to Avoid

**❌ Generic Phase Names:**
```
❌ phase4-summary.md              → Which Phase 4? What version?
✅ v2.0-phase4-release-notes.md   → Clear version association
```

**❌ Non-Descriptive Names:**
```
❌ improvement-plan.md            → Which version? What improvements?
✅ v3.2-roadmap.md               → Specific version roadmap
```

**❌ Inconsistent Casing:**
```
❌ TESTING.md (in guides/)       → Should be lowercase
✅ testing.md                    → Correct for guides/

❌ testing-checklist.md (in contributing/)  → Should be UPPERCASE
✅ TESTING_CHECKLIST.md                    → Correct for contributing/
```

**❌ Wrong Directory:**
```
❌ docs/guides/v3.2-roadmap.md   → Guides are timeless, not versioned
✅ docs/archive/plans/v3.2-roadmap.md → Correct location
```

**❌ Deleting and Recreating:**
```bash
# ❌ WRONG - Breaks git history
rm docs/old-name.md
touch docs/archive/new-name.md

# ✅ CORRECT - Preserves history
git mv docs/old-name.md docs/archive/new-name.md
```

**❌ Forgetting Cross-References:**
```bash
git mv docs/ROADMAP.md docs/archive/plans/v3.2-roadmap.md
git commit -m "moved file"
# ❌ WRONG: Didn't update links in CLAUDE.md, docs/README.md, etc.
```

---

## Validation Checklist

### Before Committing Documentation Changes

Use this checklist to ensure conventions are followed:

**File Naming:**
- [ ] Active docs use `lowercase-hyphenated-name.md`
- [ ] Contributing docs use `SCREAMING_SNAKE_CASE.md`
- [ ] Archived docs start with version prefix (`vX.Y-`)
- [ ] Version format is correct (`v3.1` not `V3.1` or `3.1`)

**File Location:**
- [ ] Timeless guides in `docs/guides/`
- [ ] Active project docs in `docs/project/`
- [ ] Shipped specs in `docs/specs/` (or archived if old)
- [ ] Contributor guides in `docs/contributing/`
- [ ] Historical docs in appropriate `docs/archive/` subdirectory

**Git Operations:**
- [ ] Used `git mv` for all renames/moves (not `rm` + `touch`)
- [ ] Moves staged before additional edits
- [ ] Commit message follows format (`Docs:`, `Rename:`, `Archive:`)

**Cross-References:**
- [ ] Searched for references: `grep -r "filename.md" docs/`
- [ ] Updated links in `CLAUDE.md` (if referenced)
- [ ] Updated links in `docs/README.md` (if referenced)
- [ ] Updated links in `docs/project/STATUS.md` (if referenced)
- [ ] Updated `docs/archive/README.md` (if archiving)

**README Files:**
- [ ] Updated `docs/archive/README.md` if archiving
- [ ] Updated `docs/README.md` if structural change
- [ ] Added directory README if creating new subdirectory

**Verification:**
- [ ] All markdown links work (no 404s)
- [ ] Document renders correctly in GitHub/editor
- [ ] Table of contents updated (if present)
- [ ] Version numbers are consistent throughout

---

## Quick Reference

### Decision Trees

#### "Where should I put this document?"

```
Is it timeless technical documentation?
├─ YES → docs/guides/ (lowercase-hyphenated)
└─ NO
   ├─ Is it active project management?
   │  ├─ YES → docs/project/ (lowercase-hyphenated)
   │  └─ NO
   │     ├─ Is it a shipped feature spec?
   │     │  ├─ YES
   │     │  │  ├─ Is it from 2+ versions ago?
   │     │  │  │  ├─ YES → docs/archive/specs/ (vX.Y-name)
   │     │  │  │  └─ NO → docs/specs/ (lowercase-hyphenated)
   │     │  └─ NO
   │     │     ├─ Is it a contributor/process guide?
   │     │     │  ├─ YES → docs/contributing/ (SCREAMING_SNAKE_CASE)
   │     │     │  └─ NO
   │     │     │     ├─ Is it a historical roadmap/plan?
   │     │     │     │  ├─ YES → docs/archive/plans/ (vX.Y-name)
   │     │     │     │  └─ NO
   │     │     │     │     ├─ Is it a release note/summary?
   │     │     │     │     │  ├─ YES → docs/archive/summaries/ (vX.Y-name)
   │     │     │     │     │  └─ NO
   │     │     │     │     │     └─ Is it analysis/research/review?
   │     │     │     │     │        └─ YES → docs/archive/reviews/ (vX.Y-topic-type)
```

#### "What should I name this file?"

```
Is it going in archive/?
├─ YES
│  └─ Does it span multiple versions?
│     ├─ YES → vX.Y-vZ.W-description.md
│     └─ NO → vX.Y-description.md
│
└─ NO
   └─ Is it in contributing/?
      ├─ YES → SCREAMING_SNAKE_CASE.md
      └─ NO → lowercase-hyphenated-name.md
```

### Common Operations

**Rename Active Document:**
```bash
git mv docs/guides/old-name.md docs/guides/new-name.md
grep -r "old-name.md" docs/ --include="*.md"  # Find references
# Update found references
git add -A
git commit -m "Rename: old-name.md → new-name.md for clarity"
```

**Archive Completed Roadmap:**
```bash
git mv docs/project/ROADMAP.md docs/archive/plans/v3.2-roadmap.md
grep -r "ROADMAP.md" docs/ --include="*.md"
# Update references in CLAUDE.md, docs/README.md, etc.
# Add entry to docs/archive/README.md
git add -A
git commit -m "Archive: Move v3.2 roadmap after completion"
```

**Create New Archived Document:**
```bash
# Create file directly in archive with version prefix
touch docs/archive/summaries/v3.3-release-notes.md
# Edit file
git add docs/archive/summaries/v3.3-release-notes.md
# Add entry to docs/archive/README.md
git add docs/archive/README.md
git commit -m "Docs: Add v3.3 release notes"
```

### Quick Command Reference

**Find all references to a file:**
```bash
grep -r "filename.md" docs/ --include="*.md"
```

**Find all archived docs for a version:**
```bash
find docs/archive -name "v3.1-*"
```

**List all files not following naming convention:**
```bash
# Active docs with version prefixes (should be archived)
find docs/guides docs/project docs/specs -name "v[0-9]*"

# Archived docs without version prefixes (should be renamed)
find docs/archive/plans docs/archive/summaries -name "*.md" ! -name "v[0-9]*" ! -name "README.md"
```

**Verify all markdown links work:**
```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check all markdown files
find docs/ -name "*.md" -exec markdown-link-check {} \;
```

---

## Version History

### v1.0 (2025-10-25)

**Initial Release**
- Created comprehensive documentation conventions
- Based on learnings from 2025-10-25 archive reorganization
- Established version-based naming for archived documents
- Defined directory structure and purposes
- Codified git best practices for documentation

**Rationale:**
- Eliminated "Phase 4" duplication confusion
- Improved chronological organization
- Enhanced discoverability via consistent naming
- Preserved git history via git mv requirements

---

## Feedback & Evolution

### Proposing Changes

If these conventions need updating:

1. **Identify the issue** - Why current convention is problematic
2. **Propose solution** - Specific change to convention
3. **Create PR** - Update this document first
4. **Discuss impact** - How many existing docs need updating?
5. **Implement** - Update convention + apply to existing docs if needed
6. **Document** - Add to "Version History" section

### Triggers for Review

Consider reviewing conventions when:
- ❗ Directory structure becomes too deep (>3 levels)
- ❗ File count in a directory exceeds 20-25
- ❗ Naming collisions occur repeatedly
- ❗ Cross-references become hard to maintain
- ❗ New document type doesn't fit current categories
- ❗ Team confusion about where to put documents

---

## Related Documentation

- **[VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md)** - Code versioning conventions (separate from docs)
- **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)** - Testing process documentation
- **[docs/README.md](../README.md)** - Complete documentation index
- **[docs/archive/README.md](../archive/README.md)** - Archive navigation guide
- **[CLAUDE.md](../../CLAUDE.md)** - Overall project instructions

---

**Maintained By:** Project Contributors
**Questions?** Open an issue or consult [docs/README.md](../README.md)

---

_These conventions are living guidelines. When in doubt, prioritize clarity and consistency over rigid adherence to rules._
