# Archive Documentation Index

This directory contains **archived documentation** from completed project phases. All documents are organized by version and purpose for easy navigation.

## Directory Structure

```
docs/archive/
├── code/       # Archived scripts and proof-of-concepts (version-tagged)
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

**Plans:**
- [v2.2-html-reports-spec.md](plans/v2.2-html-reports-spec.md) - HTML report feature specification
- [v2.2-retry-mechanism-spec.md](plans/v2.2-retry-mechanism-spec.md) - Retry mechanism specification

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

**Plans:**
- [v3.0-cli-ux-spec.md](plans/v3.0-cli-ux-spec.md) - CLI UX enhancement specification

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

### v3.2: Code Quality & Reliability (2025-10-24 - 2025-10-25) ✅ COMPLETE

**Plans:**
- [v3.2-roadmap.md](plans/v3.2-roadmap.md) - Comprehensive 4-phase quality improvement roadmap (2,664 lines)

**Summaries:**
- [v3.2-phase4-completion-summary.md](summaries/v3.2-phase4-completion-summary.md) - Phase 4 final completion (Architecture Layer Compliance)
- [v3.2-phase4b-test-maintainability-summary.md](summaries/v3.2-phase4b-test-maintainability-summary.md) - Phase 4.0b sub-phase completion
- [v3.2-roadmap-phase4-update.md](summaries/v3.2-roadmap-phase4-update.md) - Roadmap Phase 4 update summary

**Reviews:**
- [v3.2-phase1-review.md](reviews/v3.2-phase1-review.md) - Phase 1 high-priority fixes review
- [v3.2-phase2-review.md](reviews/v3.2-phase2-review.md) - Phase 2 medium-priority improvements review
- [v3.2-phase3-review.md](reviews/v3.2-phase3-review.md) - Phase 3 code quality review
- [v3.2-phase4-baseline-violations.md](reviews/v3.2-phase4-baseline-violations.md) - Architecture violation baseline analysis
- [v3.2-phase4-test-maintainability-review.md](reviews/v3.2-phase4-test-maintainability-review.md) - Test code maintainability review
- [v3.2-phase4-readiness-report.md](reviews/v3.2-phase4-readiness-report.md) - Phase 4 pre-implementation readiness assessment
- [v3.2-phase4-test-gap-analysis.md](reviews/v3.2-phase4-test-gap-analysis.md) - Test coverage gap analysis

**Key Achievements:**
- ✅ **Phase 1:** Critical bug fixes (database connection leak, division by zero)
- ✅ **Phase 2:** Security (SQL injection prevention), UX (consistent error display), Architecture (fail-fast)
- ✅ **Phase 3:** Code quality (SimpleNamespace refactoring)
- ✅ **Phase 4:** Architecture layer compliance (zero violations achieved)
- ✅ Required dependencies (Rich, Typer)
- ✅ Comprehensive test suite maintenance

**Status:** Complete (100% - all 4 phases done). v3.2.0 released 2025-10-25.

---

### v3.3: UX Enhancement (2025-10-25)

**Plans:**
- [v3.3-roadmap.md](plans/v3.3-roadmap.md) - UX improvement roadmap

**Key Features:**
- Security-focused output (hide operational details by default)
- Failed extension transparency (clear reporting of scan failures)
- Configuration flexibility (custom extension directory support)
- Enhanced CLI filtering (verified status, vulnerability presence)

**Status:** v3.3.0 complete, v3.3.1 in progress

---

### v3.4: Parallel Scanning (2025-10-25)

**Plans:**
- [v3.4-roadmap.md](plans/v3.4-roadmap.md) - Parallel scanning implementation roadmap

**Summaries:**
- [v3.4.0-release-notes.md](summaries/v3.4.0-release-notes.md) - Release completion summary

**Reviews:**
- [v3.4-architectural-review.md](reviews/v3.4-architectural-review.md) - Comprehensive architectural analysis
- [v3.4-parallel-scan-poc-guide.md](reviews/v3.4-parallel-scan-poc-guide.md) - Proof of concept guide
- [v3.4-parallel-scan-poc-results.md](reviews/v3.4-parallel-scan-poc-results.md) - PoC validation results
- [v3.4-phase1-implementation-plan.md](reviews/v3.4-phase1-implementation-plan.md) - Phase 1 implementation plan

**Key Features:**
- Parallel scanning with multiple workers (2-5 workers)
- 4.88x speedup with 3 workers (recommended)
- Thread-safe implementation (main-thread-only cache writes)
- Configuration support for parallel settings
- 100% backward compatibility

**Status:** Complete. v3.4.0 released 2025-10-25.

---

### v3.5.0: Parallel by Default (2025-10-26)

**Summaries:**
- [v3.5.0-release-notes.md](summaries/v3.5.0-release-notes.md) - Breaking change release notes

**Key Changes:**
- 🚨 **BREAKING:** Parallel processing now default (3 workers automatically)
- 🚨 **BREAKING:** Removed `--parallel` flag (no longer needed)
- 🚨 **BREAKING:** Workers range changed from 2-5 to 1-5
- 🚨 **BREAKING:** Removed `parallel` config setting

**Migration:**
- Old: `vscan scan` → sequential (slow)
- New: `vscan scan` → 3 workers (4.88x faster by default!)
- Sequential mode: Use `vscan scan --workers 1`

**Status:** Production ready. v3.5.0 released 2025-10-26.

---

### v3.5.1: Security Hardening & Technical Debt (2025-10-26)

**Plans:**
- [v3.5.1-roadmap.md](plans/v3.5.1-roadmap.md) - 2-phase roadmap (Security + Technical Debt)

**Summaries:**
- [v3.5.1-release-notes.md](summaries/v3.5.1-release-notes.md) - Release completion summary

**Reviews:**
- [v3.5.1-comprehensive-review.md](reviews/v3.5.1-comprehensive-review.md) - Architecture, code quality, and security review

**Phase 1: Security Hardening (COMPLETE ✅):**
- ✅ Unified path validation (blocks URL encoding, system directories)
- ✅ Unified string sanitization (context-aware, prevents injection)
- ✅ Cache integrity checks (HMAC-SHA256 signatures)
- ✅ Comprehensive regression test suite (35+ new security tests)

**Phase 2: Technical Debt & Reliability (COMPLETE ✅):**
- ✅ Thread-safe stats collection (ThreadSafeStats class with Lock protection)
- ✅ Transactional cache writes (Ctrl+C safe with try/finally pattern)
- ✅ Parallel architecture documentation (~200 lines in ARCHITECTURE.md)
- ✅ Integration tests with real API (test_integration_real_api.py)

**Key Achievement:** Security score improved from 7/10 → 9.5/10 (0 vulnerabilities remaining)

**Status:** Complete (8/8 tasks - both phases). v3.5.1 released 2025-10-26. Overall grade: A- (93/100).

---

### v3.5.2: Phase 2 Security Automation (2025-10-29) ✅ COMPLETE

**Plans:**
- [v3.5.2-roadmap.md](plans/v3.5.2-roadmap.md) - Phase 2 security automation implementation roadmap

**Summaries:**
- [v3.5.2-release-notes.md](summaries/v3.5.2-release-notes.md) - Release completion summary

**Reviews:**
- [tool-recommendations.md](reviews/tool-recommendations.md) - Comprehensive security tool evaluation (16 tools analyzed)

**Phase 2: Security Automation (4/4 Tools COMPLETE ✅):**
- ✅ **Dependabot** (30m) - Automated weekly dependency updates with grouped PRs
- ✅ **Coverage.py** (1h) - Branch coverage tracking with 85% CI threshold
- ✅ **Semgrep OSS** (3h) - 6 custom security rules (free CodeQL alternative for private repos)
- ✅ **Hypothesis** (4h) - Property-based testing with 4,000+ test cases

**Key Achievements:**
- 80% reduction in manual dependency management
- Branch coverage > line coverage (tests error paths)
- Custom security rules enforcing validate_path() and sanitize_string()
- Automated edge case discovery via property-based fuzzing
- $588/year savings (Semgrep OSS vs CodeQL GitHub Enterprise)

**Status:** Complete (4/4 tools implemented). v3.5.2 released 2025-10-29. Total investment: 8.5 hours, $0 cost.

---

### v3.5.3: Testing Excellence (2025-10-30) ✅ COMPLETE

**Plans:**
- [v3.5.3-roadmap.md](plans/v3.5.3-roadmap.md) - Testing Excellence implementation roadmap (6 phases)

**Summaries:**
- [v3.5.3-release-notes.md](summaries/v3.5.3-release-notes.md) - Release completion summary
- [v3.5.3-testing-phase-4-summary.md](summaries/v3.5.3-testing-phase-4-summary.md) - Comprehensive Phase 4 summary (400+ lines)

**Phase 4: Testing Excellence (6/6 Phases COMPLETE ✅):**
- ✅ **Phase 4.1** - Utility function testing (40 tests, utils.py coverage 64.50%)
- ✅ **Phase 4.2** - Display module testing (+30 tests, display.py coverage 80.58%)
- ✅ **Phase 4.3** - Integration test analysis (7 tests validated)
- ✅ **Phase 4.4** - Coverage validation (HTML reports, gap analysis)
- ✅ **Phase 4.5** - Documentation restructuring (TESTING.md: 2,800 → 486 lines, 11 specialized guides)
- ✅ **Phase 4.6** - Test infrastructure fix (100% pass rate achieved)

**Key Achievements:**
- Overall coverage: 52.07% → 72.60% (+20.53 percentage points, **103.7% of 70% target**)
- Total tests: 534 → 628 (+94 tests, +17.6% increase)
- Test pass rate: 100% (628 passed, 1 skipped)
- Security coverage: 95%+ maintained
- Property-based testing: 20 tests, 1,250+ scenarios
- Documentation excellence: 11 focused testing guides created

**Status:** Complete (6/6 phases). v3.5.3 released 2025-10-30. Exceeded coverage target by 3.7%.

---

## Archived Code

**Location:** [code/](code/)

Historical scripts and proof-of-concepts that are no longer actively used but preserved for development history. See [code/README.md](code/README.md) for details.

**Current Archive:**
- [v3.4-poc-parallel-scan.py](code/v3.4-poc-parallel-scan.py) - Parallel scanning PoC (feature shipped in v3.5.0)
- [v3.5.2-migration-add-pytest-markers.py](code/v3.5.2-migration-add-pytest-markers.py) - Pytest marker migration (complete)
- [v3.5.1-setup-security-tools.sh](code/v3.5.1-setup-security-tools.sh) - Security tools setup (superseded by `pip install -e .[dev]`)

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
- **[docs/contributing/](../contributing/)** - Contributor guides and checklists
- **[docs/README.md](../README.md)** - Complete documentation index

**Note:** Feature specifications are archived in this directory under `plans/` with version-based naming (e.g., `v2.2-html-reports-spec.md`).

---

**Last Updated:** 2025-10-29
**Reorganized By:** Claude Code Documentation Restructuring
**Reason:** Version-based organization for clarity and chronological alignment
