# Archive Documentation Index

This directory contains **archived documentation** from completed project phases. All documents are organized by version and purpose for easy navigation.

## Directory Structure

```
docs/archive/
├── plans/      # Roadmaps, requirements, and planning documents
├── summaries/  # Release notes and completion summaries
└── reviews/    # Analysis, research, and retrospective documents
```

## Organization Principles

- **Version-based naming** - Files use `vX.Y-description.md` format for chronological clarity
- **Separation of concerns** - Plans, summaries, and reviews in distinct directories
- **Git history preservation** - All file moves preserve git history via `git mv`

---

## Version Timeline

### v1.0 - v2.0: Initial Implementation (2025-10)

**Plans:**
- [v1.0-v2.0-phase1-research.md](plans/v1.0-v2.0-phase1-research.md) - API research and validation
- [v1.0-v2.0-phase2-implementation.md](plans/v1.0-v2.0-phase2-implementation.md) - Core implementation
- [v1.0-v2.0-phase3-testing.md](plans/v1.0-v2.0-phase3-testing.md) - Testing and refinement
- [v1.0-v2.0-phase4-enhanced-data.md](plans/v1.0-v2.0-phase4-enhanced-data.md) - Enhanced data integration

**Summaries:**
- [v2.0-phase3-release-notes.md](summaries/v2.0-phase3-release-notes.md) - Phase 3 completion
- [v2.0-phase4-release-notes.md](summaries/v2.0-phase4-release-notes.md) - Phase 4 completion (Enhanced Data Integration)

**Reviews:**
- [v1.0-prd-original.md](reviews/v1.0-prd-original.md) - Original product requirements
- [v2.0-enhanced-data-integration-review.md](reviews/v2.0-enhanced-data-integration-review.md) - Data integration analysis

**Key Features:**
- vscan.dev API integration
- Extension discovery
- JSON output with dual modes (standard/detailed)
- SQLite caching system
- Publisher verification

---

### v2.1: Security Hardening (2025-10)

**Reviews:**
- [v2.1-security-analysis.md](reviews/v2.1-security-analysis.md) - Security vulnerability assessment
- [v2.1-security-fixes.md](reviews/v2.1-security-fixes.md) - Security improvements implemented
- [v2.1-security-quick-fix.md](reviews/v2.1-security-quick-fix.md) - Quick security patches

**Key Features:**
- Error message sanitization
- Path validation improvements
- Security vulnerability fixes

---

### v2.2: HTML Reports & Retry Mechanism (2025-10)

**Reviews:**
- [v2.2-retry-mechanism-analysis.md](reviews/v2.2-retry-mechanism-analysis.md) - Retry strategy analysis

**Key Features:**
- HTML report generation (interactive, self-contained)
- Intelligent retry mechanism with exponential backoff
- Retry-After header support

---

### v2.3: Version Management (2025-10)

**Key Features:**
- Centralized version management (`_version.py`)
- Single source of truth for versions
- Dynamic versioning in build tools

---

### v3.0: CLI UX Enhancement (2025-10-24)

**Summaries:**
- [v3.0-release-notes.md](summaries/v3.0-release-notes.md) - CLI UX enhancement completion (formerly "Phase 5")

**Reviews:**
- [v3.0-macos-testing-review.md](reviews/v3.0-macos-testing-review.md) - macOS testing results

**Key Features:**
- Rich terminal formatting (progress bars, tables, color-coded output)
- Typer CLI framework with subcommands
- Organized help panels
- Backward compatibility with `--plain` flag
- 57 new tests

---

### v3.1: Configuration & CSV Export (2025-10-24)

**Plans:**
- [v3.1-roadmap.md](plans/v3.1-roadmap.md) - Implementation roadmap

**Summaries:**
- [v3.1-release-notes.md](summaries/v3.1-release-notes.md) - Release completion summary

**Key Features:**
- Configuration file support (`~/.vscanrc` INI format)
- CSV export for spreadsheet analysis
- Performance improvements (87.6% faster database writes)
- Threshold-based VACUUM

---

### v3.2: Code Quality & Reliability (2025-10-24 - In Progress)

**Plans:**
- [v3.2-roadmap.md](plans/v3.2-roadmap.md) - Code quality improvement roadmap

**Reviews:**
- [v3.2-phase1-review.md](reviews/v3.2-phase1-review.md) - Phase 1 high-priority fixes review
- [v3.2-phase2-review.md](reviews/v3.2-phase2-review.md) - Phase 2 medium-priority improvements review
- [v3.2-phase3-review.md](reviews/v3.2-phase3-review.md) - Phase 3 code quality review

**Key Features (Completed):**
- Critical bug fixes (database connection leak, division by zero)
- Required dependencies (Rich, Typer)
- SQL injection prevention
- Consistent error display
- Report command fail-fast behavior
- Architecture layer compliance enforcement

**Status:** In progress (see [docs/project/STATUS.md](../project/STATUS.md))

---

## Document Types Explained

### Plans (Roadmaps & Requirements)
Forward-looking documents that describe **what we're going to build** and **how we're going to build it**.

- Roadmaps for version releases
- Phase requirements and specifications
- Implementation strategies
- Architecture decisions

### Summaries (Release Notes & Completion Reports)
Backward-looking documents that describe **what we built** and **how it performed**.

- Release notes with feature lists
- Phase completion summaries
- Performance metrics
- Lessons learned

### Reviews (Analysis & Research)
Analysis documents that inform decisions and validate approaches.

- Security analysis
- Performance reviews
- Retrospectives
- Research findings
- Testing reports

---

## Naming Conventions

**Format:**
- Plans: `vX.Y-roadmap.md` or `vX.Y-phaseN-requirements.md`
- Summaries: `vX.Y-release-notes.md` or `vX.Y-phaseN-release-notes.md`
- Reviews: `vX.Y-{topic}-review.md` or `vX.Y-{topic}-analysis.md`

**Special Cases:**
- Multi-version scope: `vX.Y-vZ.W-description.md` (e.g., `v1.0-v2.0-phase1-research.md`)
- Original phases: Prefixed with version range to show they were part of initial implementation

**Benefits:**
- ✅ Chronological sorting (files sort by version)
- ✅ Clear version association
- ✅ No ambiguous "Phase X" references
- ✅ Easy to find all docs for a specific version

---

## Quick Reference

**Find all documents for a specific version:**
```bash
# All v3.1 documents
find docs/archive -name "v3.1-*"

# All v2.x documents
find docs/archive -name "v2.*-*"
```

**Find by document type:**
```bash
# All roadmaps
ls docs/archive/plans/*-roadmap.md

# All release notes
ls docs/archive/summaries/*-release-notes.md

# All security reviews
ls docs/archive/reviews/*-security-*.md
```

**Find by topic:**
```bash
# Security-related documents
find docs/archive -name "*security*"

# Performance-related documents
find docs/archive -name "*performance*" -o -name "*retry*"
```

---

## Migration Notes

**Archive Reorganization (2025-10-25):**

This structure was introduced to eliminate confusion from duplicate "Phase" terminology and create a version-based organization aligned with git history.

**Old Structure:**
```
docs/archive/
├── phases/       # Original phases 1-4
└── releases/     # Mixed: phase3-summary.md, v3.1-plan.md, etc.
```

**New Structure:**
```
docs/archive/
├── plans/        # All planning documents
├── summaries/    # All completion summaries
└── reviews/      # All analysis documents
```

**Key Changes:**
- Original phases (1-4) renamed to `v1.0-v2.0-phaseN-*.md` to show version scope
- All documents use version-based naming (`vX.Y-description.md`)
- Clear separation of planning vs retrospective documents
- Git history preserved via `git mv`

---

## Related Documentation

- **[docs/project/](../project/)** - Active project documentation (current status, roadmap, PRD)
- **[docs/guides/](../guides/)** - Timeless technical guides (architecture, security, testing, APIs)
- **[docs/specs/](../specs/)** - Shipped feature specifications
- **[docs/contributing/](../contributing/)** - Contributor guides and checklists
- **[docs/README.md](../README.md)** - Complete documentation index

---

**Last Updated:** 2025-10-25
**Reorganized By:** Claude Code Documentation Restructuring
**Reason:** Version-based organization for clarity and chronological alignment
