# Documentation Index

Complete documentation for the VS Code Extension Security Scanner project.

## Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| [../README.md](../README.md) | Project overview and quick start | All users |
| [../CLAUDE.md](../CLAUDE.md) | Development guidance and specifications | Claude Code / Developers |
| [../CHANGELOG.md](../CHANGELOG.md) | Release history (Keep a Changelog format) | All users |
| [project/STATUS.md](project/STATUS.md) | Current status and roadmap | All users |
| [guides/ARCHITECTURE.md](guides/ARCHITECTURE.md) | System architecture and design principles | Developers / Architects |
| [guides/SECURITY.md](guides/SECURITY.md) | Security requirements and best practices | Developers / Security |
| [guides/ERROR_HANDLING.md](guides/ERROR_HANDLING.md) | Error handling strategy and patterns | Developers |
| [guides/TESTING.md](guides/TESTING.md) | Testing guidelines and best practices | Contributors / QA |
| [contributing/RELEASE_PROCESS.md](contributing/RELEASE_PROCESS.md) | Complete release process (11 steps) | Maintainers |

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
│   ├── TESTING.md                 # Testing guidelines (main overview)
│   ├── API_REFERENCE.md           # vscan.dev API documentation
│   └── testing/                   # Specialized testing documentation (v3.5.3+)
│       ├── README.md              # Testing documentation navigation index
│       ├── TESTING_SECURITY.md    # Security testing (95%+ coverage)
│       ├── TESTING_COVERAGE.md    # Coverage strategy (52% → 70%)
│       ├── TESTING_INTEGRATION.md # Integration testing patterns
│       ├── TESTING_MOCKING.md     # Mocking guidelines
│       ├── TESTING_PROPERTY_BASED.md # Hypothesis property testing
│       └── ... (6 more specialized testing guides)
│
├── project/                       # Active project management
│   ├── STATUS.md                  # Current project status and progress
│   └── PRD.md                     # Product Requirements Document
│
├── contributing/                  # Contributor guides
│   ├── TESTING_CHECKLIST.md       # Testing checklist
│   └── VERSION_MANAGEMENT.md      # Version management guide
│
└── archive/                       # Historical documentation (version-based organization)
    ├── README.md                  # Archive index and navigation guide
    ├── plans/                     # Roadmaps and requirements (what we planned to build)
    │   ├── v1.0-v2.0-phase1-research.md
    │   ├── v1.0-v2.0-phase2-implementation.md
    │   ├── v1.0-v2.0-phase3-testing.md
    │   ├── v1.0-v2.0-phase4-enhanced-data.md
    │   ├── v3.1-roadmap.md
    │   ├── v3.2-roadmap.md
    │   └── v3.4-roadmap.md
    ├── summaries/                 # Release notes and completion reports (what we built)
    │   ├── v2.0-phase3-release-notes.md
    │   ├── v2.0-phase4-release-notes.md
    │   ├── v3.0-release-notes.md
    │   ├── v3.1-release-notes.md
    │   └── v3.4.0-release-notes.md
    └── reviews/                   # Analysis and research (how we evaluated)
        ├── v1.0-prd-original.md
        ├── v2.0-enhanced-data-integration-review.md
        ├── v2.1-security-analysis.md
        ├── v2.1-security-fixes.md
        ├── v2.1-security-quick-fix.md
        ├── v2.2-retry-mechanism-analysis.md
        ├── v3.0-macos-testing-review.md
        ├── v3.2-phase1-review.md
        ├── v3.2-phase2-review.md
        ├── v3.2-phase3-review.md
        ├── v3.4-parallel-scan-poc-guide.md
        ├── v3.4-parallel-scan-poc-results.md
        ├── v3.4-architectural-review.md
        └── v3.4-phase1-implementation-plan.md
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
- Complete product requirements (v3.1)
- Scope and objectives
- User stories
- Technical specifications
- Success criteria
- Phase milestones with references

---

## Archived Feature Specifications

**[archive/plans/v2.2-html-reports-spec.md](archive/plans/v2.2-html-reports-spec.md)** - HTML report feature (v2.2)
- Interactive HTML reports with sortable tables
- Data visualizations (pie charts, gauges, bar charts)
- Self-contained design (embedded CSS/JS)
- Print-optimized layout
- Auto-detection from `.html` file extension

**[archive/plans/v2.2-retry-mechanism-spec.md](archive/plans/v2.2-retry-mechanism-spec.md)** - Retry mechanism (v2.2)
- Exponential backoff with jitter (2s, 4s, 8s delays)
- Retry-After header support for rate limiting
- Configurable retry attempts and delays
- Statistics tracking and reporting

**[archive/plans/v3.0-cli-ux-spec.md](archive/plans/v3.0-cli-ux-spec.md)** - CLI UX enhancement (v3.0)
- Rich terminal formatting (progress bars, tables, panels)
- Typer CLI framework with subcommands
- Simplified help panels
- Graceful fallback to plain output

---

## Contributing

**[contributing/RELEASE_PROCESS.md](contributing/RELEASE_PROCESS.md)** - Release process guide
- Complete 11-step release process (3 phases)
- Pre-release preparation (version, documentation, testing)
- Build & package (clean build, verification, checksums)
- Version control (commit, tag, push, GitHub release)
- Documentation update checklist (8 specific files)

**[contributing/RELEASE_CHECKLIST.md](contributing/RELEASE_CHECKLIST.md)** - Release checklist
- Printable step-by-step release checklist
- Quick reference for release execution
- Verification checkpoints and quality gates
- Post-release notes and improvement tracking

**[contributing/GIT_WORKFLOW.md](contributing/GIT_WORKFLOW.md)** - Git workflow guide
- Simplified GitHub Flow branching strategy
- Branch types and naming conventions (feature/*, bugfix/*, hotfix/*)
- Feature development workflow (create → develop → PR → merge)
- Release workflow (from main branch with tags)
- Hotfix procedures for critical issues
- Pull request guidelines and commit message standards
- Branch protection configuration recommendations

**[contributing/BRANCH_PROTECTION.md](contributing/BRANCH_PROTECTION.md)** - Branch protection setup
- GitHub branch protection configuration for main branch
- Required status checks (tests, security, coverage)
- PR approval requirements (1 approval + CI passing)
- GitHub CLI and web interface setup instructions
- Verification procedures and troubleshooting

**[contributing/TESTING_CHECKLIST.md](contributing/TESTING_CHECKLIST.md)** - Testing checklist
- API behavior tests
- Extension discovery tests
- Caching system tests
- Error handling tests
- Performance tests
- Security tests

**[contributing/CODE_REVIEW_CHECKLIST.md](contributing/CODE_REVIEW_CHECKLIST.md)** - Code review checklist
- Security controls validation (path validation, input sanitization, access control)
- Bandit suppression review (format, justification, security approval)
- Architecture compliance (layer violations, design principles)
- Testing requirements (coverage, security tests, regression tests)
- Documentation updates and common anti-patterns

**[contributing/VERSION_MANAGEMENT.md](contributing/VERSION_MANAGEMENT.md)** - Version management guide
- Centralized version system (_version.py)
- How to bump versions (semantic versioning)
- Enhanced --check command (Python + documentation validation)
- Validation and troubleshooting
- Version history

**[contributing/DOCUMENTATION_CONVENTIONS.md](contributing/DOCUMENTATION_CONVENTIONS.md)** - Documentation conventions
- Naming conventions (version-based, lowercase-hyphenated)
- Directory structure and organization
- Archiving procedures and git best practices
- Cross-reference management
- Validation checklist and quick reference

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
7. [guides/API_REFERENCE.md](guides/API_REFERENCE.md) - API details

### For Project Managers

**Start Here:**
1. [project/STATUS.md](project/STATUS.md) - Current progress
2. [project/PRD.md](project/PRD.md) - Requirements and scope
3. [archive/summaries/](archive/summaries/) - Release notes and completion summaries
4. [archive/plans/](archive/plans/) - Historical roadmaps and requirements
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
2. [archive/reviews/v2.1-security-analysis.md](archive/reviews/v2.1-security-analysis.md) - Historical vulnerability analysis
3. [archive/reviews/v2.1-security-fixes.md](archive/reviews/v2.1-security-fixes.md) - Applied fixes
4. [guides/TESTING.md](guides/TESTING.md) - Security testing strategy

---

## Development History

### Phase 1: Research & Discovery ✅ COMPLETE

**Requirements:** [archive/plans/v1.0-v2.0-phase1-research.md](archive/plans/v1.0-v2.0-phase1-research.md)

**What Was Achieved:**
- Reverse-engineered vscan.dev API
- Validated 3 endpoints with real extensions
- 100% test success rate
- Documented all findings → [guides/API_REFERENCE.md](guides/API_REFERENCE.md)

### Phase 2: Core Implementation ✅ COMPLETE

**Requirements:** [archive/plans/v1.0-v2.0-phase2-implementation.md](archive/plans/v1.0-v2.0-phase2-implementation.md)

**What Was Achieved:**
- All 6 core modules implemented (1,590 LOC)
- Extension discovery for all platforms
- Complete API integration
- SQLite caching system
- 12+ CLI arguments

### Phase 3: Testing & Refinement ✅ COMPLETE

**Requirements:** [archive/plans/v1.0-v2.0-phase3-testing.md](archive/plans/v1.0-v2.0-phase3-testing.md)

**Summary:** [archive/summaries/v2.0-phase3-release-notes.md](archive/summaries/v2.0-phase3-release-notes.md)

**What Was Achieved:**
- Comprehensive caching system testing
- macOS testing (100% pass rate)
- Tested with 3, 66, and 100+ extensions
- Performance validation (28x cache speedup)
- UX refinements

### Phase 4: Enhanced Data Integration ✅ COMPLETE

**Requirements:** [archive/plans/v1.0-v2.0-phase4-enhanced-data.md](archive/plans/v1.0-v2.0-phase4-enhanced-data.md)

**Summary:** [archive/summaries/v2.0-phase4-release-notes.md](archive/summaries/v2.0-phase4-release-notes.md)

**What Was Achieved:**
- Complete vscan.dev data capture
- Dual output modes (standard/detailed)
- Publisher verification
- Dependency analysis
- Security score breakdown
- Cache schema v2.0
- Version 2.0 release

### Phase 5: CLI UX Enhancement ✅ COMPLETE (v3.0)

**Specification:** [archive/plans/v3.0-cli-ux-spec.md](archive/plans/v3.0-cli-ux-spec.md)

**What Was Achieved:**
- Rich terminal formatting with live progress
- Typer CLI framework with subcommands
- Simplified options and help
- 57 new tests, all passing

### Phase 6: Configuration & CSV Export ✅ COMPLETE (v3.1)

**Summary:** [archive/summaries/v3.1-release-notes.md](archive/summaries/v3.1-release-notes.md)

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
| **Contributing Guides** | 4 (Git Workflow, Branch Protection, Testing Checklist, Version Management) |
| **Feature Specifications** | 3 (HTML Reports, Retry Mechanism, CLI UX) |
| **API Endpoints Documented** | 3 |
| **Test Suites** | 13+ (Display, Scanner, CLI, API, Cache, Config, Security, Performance, Integration, etc.) |
| **Phases Completed** | 6 (all complete) |
| **Modules Implemented** | 13 |
| **V3.2 Planned Improvements** | 18 prioritized recommendations |
| **Security Vulnerabilities Fixed** | 82% reduction (15 → 2 remaining) |

---

## Recent Updates

- **2025-10-25** - Archive Reorganization (Version-Based Organization)
  - Reorganized docs/archive/ with version-based naming scheme
  - Created three subdirectories: plans/, summaries/, reviews/
  - Eliminated "Phase 4" duplication (v1.0-v2.0 vs v3.2)
  - All files renamed to vX.Y-description.md format
  - Created [archive/README.md](archive/README.md) navigation guide
  - Git history preserved via git mv for all moves

- **2025-10-24** - Documentation Restructure
  - Created organization: Active (guides/, project/) + Archive + Contributing
  - Consolidated security docs into single [guides/SECURITY.md](guides/SECURITY.md)
  - Renamed files to lowercase-hyphenated naming convention
  - Clear separation of concerns: timeless guides vs. project management vs. historical archive
  - Improved navigation and discoverability

- **2025-10-24** - Comprehensive Architecture Documentation (v2.0)
  - Created [guides/ARCHITECTURE.md](guides/ARCHITECTURE.md) - Simple Layered Architecture
  - Created [guides/ERROR_HANDLING.md](guides/ERROR_HANDLING.md) - ERROR_HELP system
  - Created [guides/TESTING.md](guides/TESTING.md) - Testing guidelines
  - Created v3.2 roadmap with 18 prioritized improvements (now archived)
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
- **project/** - Active project management (status, requirements)
- **contributing/** - Contributor guides and checklists
- **archive/** - Historical documentation (roadmaps, specs, releases, reviews)

### Guidelines

1. **Guides are timeless** - Focus on principles, not specific bugs or versions
2. **Project docs are current** - Reflect active status and plans
3. **Archive is historical** - Roadmaps, specs, release notes, reviews, analysis
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
