# Archive Documentation Index

Archived documentation from completed project phases, organized by version for chronological clarity.

---

## Directory Structure

```
docs/archive/
├── README.md                    # This file - version timeline
├── plans/                       # Roadmaps, specifications, implementation plans
├── summaries/                   # Release notes, completion reports
├── reviews/                     # Analysis, research, retrospectives
└── code/                        # Archived scripts and proof-of-concepts
```

## Organization Principles

- **Version-based naming** - Files use `vX.Y-description.md` format
- **Separation of concerns** - Plans, summaries, reviews in distinct directories
- **Git history preserved** - All file moves via `git mv`

---

## Version Timeline

| Version | Date | Key Features | Docs |
|---------|------|--------------|------|
| **v1.0-v2.0** | 2025-10 | vscan.dev API, extension discovery, JSON output, SQLite cache, publisher verification | [Plans](plans/), [Summaries](summaries/), [Reviews](reviews/) |
| **v2.1** | 2025-10 | Security hardening: error sanitization, path validation | [Reviews](reviews/v2.1-security-*.md) |
| **v2.2** | 2025-10 | HTML reports, intelligent retry mechanism with exponential backoff | [Plans](plans/v2.2-*.md), [Reviews](reviews/) |
| **v2.3** | 2025-10 | Centralized version management (`_version.py`) | - |
| **v3.0** | 2025-10-24 | CLI UX: Rich formatting, Typer framework, subcommands, +57 tests | [Plan](plans/v3.0-cli-ux-spec.md), [Summary](summaries/v3.0-release-notes.md), [Review](reviews/v3.0-macos-testing-review.md) |
| **v3.1** | 2025-10-24 | Configuration files (`~/.vscanrc`), CSV export, 87.6% faster DB writes | [Plan](plans/v3.1-roadmap.md), [Summary](summaries/v3.1-release-notes.md) |
| **v3.2** | 2025-10-25 | Code quality: 4 phases, architecture compliance, zero violations ✅ | [Plan](plans/v3.2-roadmap.md), [Summaries](summaries/v3.2-*.md), [Reviews](reviews/v3.2-*.md) |
| **v3.3** | 2025-10-25 | UX enhancement: security-focused output, failed extension reporting | [Plan](plans/v3.3-roadmap.md) |
| **v3.4** | 2025-10-25 | Parallel scanning: 2-5 workers, 4.88x speedup with 3 workers ✅ | [Plan](plans/v3.4-roadmap.md), [Summary](summaries/v3.4.0-release-notes.md), [Reviews](reviews/v3.4-*.md) |
| **v3.5.0** | 2025-10-26 | 🚨 BREAKING: Parallel by default (3 workers), removed `--parallel` flag | [Summary](summaries/v3.5.0-release-notes.md) |
| **v3.5.1** | 2025-10-26 | Security hardening: path validation, string sanitization, HMAC cache integrity, 9.5/10 score ✅ | [Plan](plans/v3.5.1-roadmap.md), [Summary](summaries/v3.5.1-release-notes.md), [Review](reviews/v3.5.1-comprehensive-review.md) |
| **v3.5.2** | 2025-10-29 | Security automation: Dependabot, Coverage.py, Semgrep OSS, Hypothesis (4,000+ tests) ✅ | [Plan](plans/v3.5.2-roadmap.md), [Summary](summaries/v3.5.2-release-notes.md), [Review](reviews/tool-recommendations.md) |
| **v3.5.3** | 2025-10-30 | Testing excellence: 52.07% → 72.60% coverage (+20.53%), +94 tests, 11 testing guides ✅ | [Plan](plans/v3.5.3-roadmap.md), [Summaries](summaries/v3.5.3-*.md) |
| **v3.6.0** | 2025-11-04 | Coverage improvement: 77.83% → 78.94%, +52 tests, refactoring roadmap ✅ | [Plans](plans/v3.6-*.md), [Summary](summaries/v3.6.0-release-notes.md) |
| **v3.7.0** | 2025-11-05 | 🚨 BREAKING: Testability refactoring, 78.94% → 86.25% coverage, +204 tests, 6 modules extracted, removed `--plain` ✅ | [Plan](plans/v3.7-roadmap.md), [Summary](summaries/v3.7.0-release-notes.md) |
| **v3.7.1** | 2025-11-05 | Coverage excellence: 86.25% → 89.39%, +78 tests, cache_manager & scanner >80% ✅ | [Summary](summaries/v3.7.1-release-notes.md) |
| **v3.7.2** | 2025-11-08 | Release automation improvements, test quality enhancements | [Summary](summaries/v3.7.2-release-notes.md) |
| **v4.0.0** | 2025-11-08 | 🚨 BREAKING: Rich security data, 32 DB columns, 9 comprehensive security modules, VirusTotal filtering ✅ | [Plan](plans/v4.0-roadmap.md), [Summary](summaries/v4.0.0-release-notes.md) |
| **v5.0.0** | 2025-11-08 | 🚨 BREAKING: Schema redesign, 32 → 12 columns (-60%), 60% storage reduction, 30% faster queries ✅ | [Summary](summaries/v5.0.0-release-notes.md) |
| **v5.0.1** | 2025-11-09 | Stability improvements, bug fixes | [Summary](summaries/v5.0.1-release-notes.md) |
| **v5.0.2** | 2025-11-09 | Test quality improvements, comprehensive project state analysis ✅ | [Plan](plans/v5.0.2-roadmap.md), [Summary](summaries/v5.0.2-release-notes.md), [Review](reviews/v5.0.2-comprehensive-project-state-analysis.md) |
| **v5.0.3** | 2025-11-22 | Module-by-module risk display feature ✅ | [Summary](summaries/v5.0.3-release-notes.md) |
| **v5.0.4** | 2025-11-24 | Data visualization & portfolio analysis enhancements ✅ | [Plan](plans/v5.0.4-roadmap.md), [Summary](summaries/v5.0.4-release-notes.md) |

### GitHub Projects Documentation (2025-11-20) ✅

| Document | Purpose |
|----------|---------|
| [ARCHIVE_INDEX.md](ARCHIVE_INDEX.md) | Complete reorganization summary |
| [GITHUB_PROJECTS-v1-ARCHIVED.md](GITHUB_PROJECTS-v1-ARCHIVED.md) | Archive notice with migration guide |
| [GITHUB_PROJECTS-v1.md](GITHUB_PROJECTS-v1.md) | Original comprehensive guide (1,196 lines) |

**Key Changes:**
- Monolithic guide split into focused documents (~50KB token savings)
- Created shared reference: `_gh-reference.md`
- New structure: QUICKSTART → WORKFLOWS → specialized guides

---

## Archived Code

**Location:** [code/](code/)

| File | Purpose | Status |
|------|---------|--------|
| [v3.4-poc-parallel-scan.py](code/v3.4-poc-parallel-scan.py) | Parallel scanning PoC | Shipped in v3.5.0 |
| [v3.5.2-migration-add-pytest-markers.py](code/v3.5.2-migration-add-pytest-markers.py) | Pytest marker migration | Complete |
| [v3.5.1-setup-security-tools.sh](code/v3.5.1-setup-security-tools.sh) | Security tools setup | Superseded by `pip install -e .[dev]` |
| [diagnose_performance.py](code/diagnose_performance.py) | Performance diagnostics | Archived 2025-11-03 |

**Archived Documentation:**
- [PERFORMANCE_DIAGNOSTICS.md](PERFORMANCE_DIAGNOSTICS.md) - Merged into PERFORMANCE.md (2025-11-03)
- [TESTING_PERFORMANCE.md](TESTING_PERFORMANCE.md) - Merged into PERFORMANCE.md (2025-11-03)
- [GITHUB_SETTINGS_CHECKLIST.md](GITHUB_SETTINGS_CHECKLIST.md) - Archived 2025-11-03

---

## Document Types

| Type | Purpose | Examples |
|------|---------|----------|
| **Plans** | What we're building and how | Roadmaps, specifications, implementation strategies |
| **Summaries** | What we built and results | Release notes, completion reports, metrics |
| **Reviews** | Analysis and research | Security analysis, performance reviews, retrospectives |

---

## Naming Conventions

**Format:**
- Plans: `vX.Y-roadmap.md` or `vX.Y-phaseN-requirements.md`
- Summaries: `vX.Y-release-notes.md` or `vX.Y-phaseN-completion-summary.md`
- Reviews: `vX.Y-{topic}-review.md` or `vX.Y-{topic}-analysis.md`

**Special Cases:**
- Multi-version: `vX.Y-vZ.W-description.md` (e.g., `v1.0-v2.0-phase1-research.md`)
- Original phases: Prefixed with version range for chronological context

---

## Quick Reference

**Find all documents for a version:**
```bash
# All v3.7 documents
find docs/archive -name "v3.7*"

# All v5.x documents
find docs/archive -name "v5.*"
```

**Find by document type:**
```bash
# All roadmaps
ls docs/archive/plans/*-roadmap.md

# All release notes
ls docs/archive/summaries/*-release-notes.md
```

**Find by topic:**
```bash
# Security-related
find docs/archive -name "*security*"

# Performance-related
find docs/archive -name "*performance*" -o -name "*parallel*"
```

---

## Related Documentation

- **[docs/project/](../project/)** - Active project docs (STATUS.md, PRD.md)
- **[docs/guides/](../guides/)** - Technical guides (ARCHITECTURE.md, SECURITY.md, TESTING.md)
- **[docs/contributing/](../contributing/)** - Contributor guides
- **[docs/README.md](../README.md)** - Complete documentation index

---

**Last Updated:** 2025-11-20
**Maintained By:** Claude Code Documentation
**Organization:** Version-based chronological structure
