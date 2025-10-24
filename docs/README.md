# Documentation Index

Complete documentation for the VS Code Extension Security Scanner project.

## Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| [../README.md](../README.md) | Project overview and quick start | All users |
| [../CLAUDE.md](../CLAUDE.md) | Development guidance and specifications | Claude Code / Developers |
| [project/STATUS.md](project/STATUS.md) | Current status and roadmap | All users |
| [guides/ARCHITECTURE.md](guides/ARCHITECTURE.md) | System architecture and design principles | Developers / Architects |
| [guides/SECURITY.md](guides/SECURITY.md) | Security requirements and best practices | Developers / Security |
| [guides/ERROR_HANDLING.md](guides/ERROR_HANDLING.md) | Error handling strategy and patterns | Developers |
| [guides/TESTING.md](guides/TESTING.md) | Testing guidelines and best practices | Contributors / QA |

## Documentation Structure

```
docs/
├── README.md                      # This file - documentation index
│
├── guides/                        # Timeless developer reference
│   ├── ARCHITECTURE.md            # System architecture and design principles
│   ├── SECURITY.md                # Security requirements and best practices
│   ├── ERROR_HANDLING.md          # Error handling strategy
│   ├── ERROR_CODES.md             # Error code reference
│   ├── TESTING.md                 # Testing guidelines
│   └── API_REFERENCE.md           # vscan.dev API documentation
│
├── project/                       # Active project management
│   ├── STATUS.md                  # Current project status and progress
│   ├── PRD.md                     # Product Requirements Document
│   └── ROADMAP.md                 # Version 3.2 improvement plan
│
├── specs/                         # Shipped feature specifications
│   ├── html-reports.md            # HTML report feature (v2.2)
│   ├── retry-mechanism.md         # Retry mechanism (v2.2)
│   └── cli-ux.md                  # CLI UX enhancement (v3.0)
│
├── contributing/                  # Contributor guides
│   ├── TESTING_CHECKLIST.md       # Testing checklist
│   └── VERSION_MANAGEMENT.md      # Version management guide
│
└── archive/                       # Historical documentation
    ├── phases/                    # Phase requirements (completed)
    │   ├── phase1-research.md
    │   ├── phase2-implementation.md
    │   ├── phase3-testing.md
    │   └── phase4-enhanced-data.md
    ├── releases/                  # Release summaries
    │   ├── phase3-summary.md
    │   ├── phase4-summary.md
    │   ├── v3.1-plan.md
    │   └── v3.1-summary.md
    └── reviews/                   # Historical reviews and analysis
        ├── improvement-plan.md
        ├── improvement-phase1.md
        ├── improvement-phase2.md
        ├── improvement-phase3.md
        ├── security-analysis.md
        ├── security-fixes.md
        └── security-quick-fix.md
```

---

## Developer Guides

### Core Architecture

**[guides/ARCHITECTURE.md](guides/ARCHITECTURE.md)** - System architecture documentation
- Simple Layered Architecture (3 layers: Presentation, Application, Infrastructure)
- Design principles (KISS, Command-Query Separation, Fail Fast)
- Module responsibilities for all 13 modules
- Dependency rules and enforcement
- Data flow diagrams
- Anti-patterns to avoid

**[guides/SECURITY.md](guides/SECURITY.md)** - Security requirements and best practices
- Security architecture and defense layers
- Path validation requirements (CRITICAL)
- Input validation requirements (HIGH)
- Access control and file permissions
- Error handling and sanitization
- Threat model and attack vectors
- Security testing requirements
- Compliance status (CWE, OWASP)

**[guides/ERROR_HANDLING.md](guides/ERROR_HANDLING.md)** - Error handling strategy
- ERROR_HELP system documentation (7 error types)
- Error classification and display flow
- Comprehensive error suggestions
- Security-aware error messaging
- Implementation guide for new errors

**[guides/TESTING.md](guides/TESTING.md)** - Testing guidelines
- Test organization and categories (6 types)
- Writing tests (AAA pattern, fixtures, parameterization)
- Mocking guidelines
- Test coverage goals (85% overall, 95% for security modules)
- CI/CD integration
- Architecture enforcement tests

**[guides/API_REFERENCE.md](guides/API_REFERENCE.md)** - vscan.dev API documentation
- API endpoints (analyze, status, results)
- Request/response formats
- Test results from 3 extensions
- Implementation recommendations
- Edge cases and unknowns

**[guides/ERROR_CODES.md](guides/ERROR_CODES.md)** - Error code reference
- Error code format and ranges (E100-E399)
- Module-specific error codes (API, Cache, Discovery)
- Documented errors with causes and solutions
- Troubleshooting guide

---

## Project Management

**[project/STATUS.md](project/STATUS.md)** - Current project status
- Phase completion status (Phases 1-6 complete)
- Current version: v3.1.0
- Test results summary
- Timeline and milestones
- Risk assessment
- Next actions

**[project/PRD.md](project/PRD.md)** - Product Requirements Document
- Complete product requirements
- Scope and objectives
- User stories
- Technical specifications
- Success criteria
- Phase milestones with references

**[project/ROADMAP.md](project/ROADMAP.md)** - Version 3.2 improvement plan
- 18 specific recommendations prioritized by impact
- Security improvements (SQL injection, connection leaks, rate limiting)
- Usability enhancements (error display, UX consistency)
- Performance optimizations (cache, VACUUM, backoff)
- Implementation roadmap (Phase 1-3)

---

## Feature Specifications

**[specs/html-reports.md](specs/html-reports.md)** - HTML report feature (v2.2)
- Interactive HTML reports with sortable tables
- Data visualizations (pie charts, gauges, bar charts)
- Self-contained design (embedded CSS/JS)
- Print-optimized layout
- Auto-detection from `.html` file extension

**[specs/retry-mechanism.md](specs/retry-mechanism.md)** - Retry mechanism (v2.2)
- Exponential backoff with jitter (2s, 4s, 8s delays)
- Retry-After header support for rate limiting
- Configurable retry attempts and delays
- Statistics tracking and reporting

**[specs/cli-ux.md](specs/cli-ux.md)** - CLI UX enhancement (v3.0)
- Rich terminal formatting (progress bars, tables, panels)
- Typer CLI framework with subcommands
- Simplified help panels
- Graceful fallback to plain output

---

## Contributing

**[contributing/TESTING_CHECKLIST.md](contributing/TESTING_CHECKLIST.md)** - Testing checklist
- API behavior tests
- Extension discovery tests
- Caching system tests
- Error handling tests
- Performance tests
- Security tests

**[contributing/VERSION_MANAGEMENT.md](contributing/VERSION_MANAGEMENT.md)** - Version management guide
- Centralized version system (_version.py)
- How to bump versions (semantic versioning)
- Validation and troubleshooting
- Version history

---

## By Role

### For Developers

**Start Here:**
1. [../README.md](../README.md) - Project overview
2. [../CLAUDE.md](../CLAUDE.md) - Development guidance
3. [guides/ARCHITECTURE.md](guides/ARCHITECTURE.md) - System architecture
4. [guides/SECURITY.md](guides/SECURITY.md) - Security requirements
5. [guides/ERROR_HANDLING.md](guides/ERROR_HANDLING.md) - Error handling patterns
6. [guides/TESTING.md](guides/TESTING.md) - Testing best practices
7. [project/ROADMAP.md](project/ROADMAP.md) - Version 3.2 improvements
8. [guides/API_REFERENCE.md](guides/API_REFERENCE.md) - API details

### For Project Managers

**Start Here:**
1. [project/STATUS.md](project/STATUS.md) - Current progress
2. [project/PRD.md](project/PRD.md) - Requirements and scope
3. [project/ROADMAP.md](project/ROADMAP.md) - Version 3.2 plans
4. [archive/releases/](archive/releases/) - Phase completion summaries
5. [../README.md](../README.md) - Project summary

### For Contributors

**Start Here:**
1. [../README.md](../README.md) - Project overview
2. [contributing/TESTING_CHECKLIST.md](contributing/TESTING_CHECKLIST.md) - Test plan
3. [guides/TESTING.md](guides/TESTING.md) - Testing guidelines
4. [guides/ARCHITECTURE.md](guides/ARCHITECTURE.md) - Code architecture
5. [project/PRD.md](project/PRD.md) - Requirements to verify

### For Security Reviewers

**Start Here:**
1. [guides/SECURITY.md](guides/SECURITY.md) - Security requirements and status
2. [archive/reviews/security-analysis.md](archive/reviews/security-analysis.md) - Historical vulnerability analysis
3. [archive/reviews/security-fixes.md](archive/reviews/security-fixes.md) - Applied fixes
4. [guides/TESTING.md](guides/TESTING.md) - Security testing strategy

---

## Development History

### Phase 1: Research & Discovery ✅ COMPLETE

**Requirements:** [archive/phases/phase1-research.md](archive/phases/phase1-research.md)

**What Was Achieved:**
- Reverse-engineered vscan.dev API
- Validated 3 endpoints with real extensions
- 100% test success rate
- Documented all findings → [guides/API_REFERENCE.md](guides/API_REFERENCE.md)

### Phase 2: Core Implementation ✅ COMPLETE

**Requirements:** [archive/phases/phase2-implementation.md](archive/phases/phase2-implementation.md)

**What Was Achieved:**
- All 6 core modules implemented (1,590 LOC)
- Extension discovery for all platforms
- Complete API integration
- SQLite caching system
- 12+ CLI arguments

### Phase 3: Testing & Refinement ✅ COMPLETE

**Requirements:** [archive/phases/phase3-testing.md](archive/phases/phase3-testing.md)

**Summary:** [archive/releases/phase3-summary.md](archive/releases/phase3-summary.md)

**What Was Achieved:**
- Comprehensive caching system testing
- macOS testing (100% pass rate)
- Tested with 3, 66, and 100+ extensions
- Performance validation (28x cache speedup)
- UX refinements

### Phase 4: Enhanced Data Integration ✅ COMPLETE

**Requirements:** [archive/phases/phase4-enhanced-data.md](archive/phases/phase4-enhanced-data.md)

**Summary:** [archive/releases/phase4-summary.md](archive/releases/phase4-summary.md)

**What Was Achieved:**
- Complete vscan.dev data capture
- Dual output modes (standard/detailed)
- Publisher verification
- Dependency analysis
- Security score breakdown
- Cache schema v2.0
- Version 2.0 release

### Phase 5: CLI UX Enhancement ✅ COMPLETE (v3.0)

**Specification:** [specs/cli-ux.md](specs/cli-ux.md)

**What Was Achieved:**
- Rich terminal formatting with live progress
- Typer CLI framework with subcommands
- Simplified options and help
- 57 new tests, all passing

### Phase 6: Configuration & CSV Export ✅ COMPLETE (v3.1)

**Summary:** [archive/releases/v3.1-summary.md](archive/releases/v3.1-summary.md)

**What Was Achieved:**
- Configuration file support (~/.vscanrc)
- CSV export feature
- Performance improvements (87.6% faster batch commits)
- Code quality improvements

---

## Statistics

| Metric | Value |
|--------|-------|
| **Total Documentation** | ~20,000+ lines |
| **Number of Documents** | 32+ files |
| **Core Guide Docs** | 6 (Architecture, Security, Error Handling, Testing, API Reference, Error Codes) |
| **Contributing Guides** | 2 (Testing Checklist, Version Management) |
| **Feature Specifications** | 3 (HTML Reports, Retry Mechanism, CLI UX) |
| **API Endpoints Documented** | 3 |
| **Test Suites** | 13+ (Display, Scanner, CLI, API, Cache, Config, Security, Performance, Integration, etc.) |
| **Phases Completed** | 6 (all complete) |
| **Modules Implemented** | 13 |
| **V3.2 Planned Improvements** | 18 prioritized recommendations |
| **Security Vulnerabilities Fixed** | 82% reduction (15 → 2 remaining) |

---

## Recent Updates

- **2025-10-24** - Documentation Restructure
  - Created 3-tier organization: Active (guides/, project/, specs/) + Archive + Contributing
  - Consolidated security docs into single [guides/SECURITY.md](guides/SECURITY.md)
  - Renamed files to lowercase-hyphenated naming convention
  - Clear separation of concerns: timeless guides vs. project management vs. historical archive
  - Improved navigation and discoverability

- **2025-10-24** - Comprehensive Architecture Documentation (v2.0)
  - Created [guides/ARCHITECTURE.md](guides/ARCHITECTURE.md) - Simple Layered Architecture
  - Created [guides/ERROR_HANDLING.md](guides/ERROR_HANDLING.md) - ERROR_HELP system
  - Created [guides/TESTING.md](guides/TESTING.md) - Testing guidelines
  - Created [project/ROADMAP.md](project/ROADMAP.md) - 18 prioritized improvements
  - Formalized architectural principles: KISS, Command-Query Separation, Fail Fast

- **2025-10-24** - Cross-platform Compatibility
  - Fixed Windows import issues
  - Implemented cross-platform path security
  - Safe file permission handling (Windows/Unix)
  - All tests passing (35/35 functional tests)

---

## Contributing to Documentation

### Folder Structure

- **guides/** - Timeless technical reference (architecture, security, APIs)
- **project/** - Active project management (status, requirements, roadmap)
- **specs/** - Shipped feature specifications
- **contributing/** - Contributor guides and checklists
- **archive/** - Historical documentation (phases, releases, reviews)

### Guidelines

1. **Guides are timeless** - Focus on principles, not specific bugs or versions
2. **Project docs are current** - Reflect active status and plans
3. **Specs document shipped features** - Implementation details for released features
4. **Archive is historical** - Phase requirements, old reviews, past summaries
5. **Use lowercase-hyphenated naming** - For new files: `my-new-document.md`
6. **Update cross-references** - When moving files, update links in CLAUDE.md, README.md
7. **Keep this index current** - Update navigation when adding files

---

## Questions?

- **Implementation questions?** See [../CLAUDE.md](../CLAUDE.md)
- **Architecture questions?** See [guides/ARCHITECTURE.md](guides/ARCHITECTURE.md)
- **Security questions?** See [guides/SECURITY.md](guides/SECURITY.md)
- **Requirements questions?** See [project/PRD.md](project/PRD.md)
- **API questions?** See [guides/API_REFERENCE.md](guides/API_REFERENCE.md)
- **Testing questions?** See [guides/TESTING.md](guides/TESTING.md) or [contributing/TESTING_CHECKLIST.md](contributing/TESTING_CHECKLIST.md)
- **Project status?** See [project/STATUS.md](project/STATUS.md)
