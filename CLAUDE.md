# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

---

## Current Status

**Version:** v3.5.5 Complete ✅
**Latest:** Automated Release Workflow - GitHub Actions for automatic distribution builds on version tags
**Features:** CI/CD automation (38% release time reduction), comprehensive testing (628 tests, 72.60% coverage), modular HTML reports
**Completed Roadmap:** [v3.5.3-roadmap.md](docs/archive/plans/v3.5.3-roadmap.md) - Testing Excellence complete
**Previous Roadmap:** [docs/archive/plans/v3.5.2-roadmap.md](docs/archive/plans/v3.5.2-roadmap.md)

---

## ⚠️ REQUIRED READING BEFORE CODE CHANGES

**STOP!** Before making any code changes, you **MUST** read these three documents:

1. **[docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)** - System architecture, design principles, module responsibilities, and anti-patterns
2. **[docs/guides/SECURITY.md](docs/guides/SECURITY.md)** - Security requirements, path validation, input sanitization, and threat model
3. **[docs/project/PRD.md](docs/project/PRD.md)** - Product requirements, feature scope, and constraints

These documents define critical constraints and requirements that must be followed.

---

## Project Overview

VS Code Extension Security Scanner is a standalone Python CLI tool that performs manual security audits of installed VS Code extensions by leveraging the vscan.dev security analysis service.

**IMPORTANT**: This is an **unofficial, community-maintained tool**. All security analysis is **powered by [vscan.dev](https://vscan.dev)**. We are deeply grateful to vscan.dev for providing their public API. This tool is NOT affiliated with or endorsed by vscan.dev. For complete legal and attribution information, see [docs/project/ATTRIBUTION.md](docs/project/ATTRIBUTION.md).

**See:** [README.md](README.md) for features and [docs/project/STATUS.md](docs/project/STATUS.md) for current development status.

---

## Technology Stack

- **Language:** Python 3.8+
- **HTTP Library:** `urllib.request` (standard library)
- **Database:** SQLite3 (standard library, for caching with HMAC integrity)
- **CLI Framework:** Typer ≥0.9.0 (modern CLI with Rich support)
- **Terminal Formatting:** Rich ≥13.0.0 (progress bars, tables, panels)
- **Distribution:** Python package (pip installable)
- **Output Formats:** JSON, HTML (self-contained), CSV
- **Configuration:** INI format config file at ~/.vscanrc

---

## Documentation Navigation

### 🔴 Before ANY Code Change - Read These First:

1. **[ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)** - System design (3-layer architecture), design principles (KISS, fail-fast), anti-patterns
2. **[SECURITY.md](docs/guides/SECURITY.md)** - Path validation (`validate_path()`), string sanitization (`sanitize_string()`), threat model, HMAC cache integrity
3. **[PRD.md](docs/project/PRD.md)** - Feature scope, requirements, constraints, what's in/out of scope

### 🟡 When Working On Specific Tasks:

**Adding Features:**
- Check scope: [PRD.md](docs/project/PRD.md) - Is this feature in scope?
- Check roadmap: [STATUS.md](docs/project/STATUS.md) - Current sprint priorities
- Check roadmap: [v3.5.3-roadmap.md](docs/project/v3.5.3-roadmap.md) - Testing Excellence (planned)

**Security Changes:**
- [SECURITY.md](docs/guides/SECURITY.md) - Complete security requirements, validation patterns, defense layers
- [ERROR_HANDLING.md](docs/guides/ERROR_HANDLING.md) - ERROR_HELP system, sanitized error messages

**API Integration:**
- [API_REFERENCE.md](docs/guides/API_REFERENCE.md) - vscan.dev endpoints, request/response formats, edge cases

**Performance Optimization:**
- [PERFORMANCE.md](docs/guides/PERFORMANCE.md) - Benchmarks, threading model, resource usage, optimization strategies
- [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) - Parallel processing architecture

**Testing:**
- [TESTING.md](docs/guides/TESTING.md) - Overview (compact), test patterns (AAA), quick start (486 lines)
- **Specialized Testing Guides (v3.5.3+):** [testing/](docs/guides/testing/)
  - [TESTING_SECURITY.md](docs/guides/testing/TESTING_SECURITY.md) - Security testing (21K, 95%+ coverage)
  - [TESTING_COVERAGE.md](docs/guides/testing/TESTING_COVERAGE.md) - Coverage strategy (52% → 70%)
  - [TESTING_INTEGRATION.md](docs/guides/testing/TESTING_INTEGRATION.md) - Integration patterns
  - [TESTING_MOCKING.md](docs/guides/testing/TESTING_MOCKING.md) - Canonical mocks
  - [TESTING_PROPERTY_BASED.md](docs/guides/testing/TESTING_PROPERTY_BASED.md) - Hypothesis (1,250+ scenarios)
  - [TESTING_CLI.md](docs/guides/testing/TESTING_CLI.md) - CLI testing
  - [TESTING_PERFORMANCE.md](docs/guides/testing/TESTING_PERFORMANCE.md) - Performance benchmarks
  - [TESTING_PARALLEL.md](docs/guides/testing/TESTING_PARALLEL.md) - Parallel execution
  - [TESTING_RETRY.md](docs/guides/testing/TESTING_RETRY.md) - Retry mechanism
  - [TESTING_HTML_REPORTS.md](docs/guides/testing/TESTING_HTML_REPORTS.md) - HTML report validation
- [TESTING_CHECKLIST.md](docs/contributing/TESTING_CHECKLIST.md) - Pre-release testing checklist
- [v3.5.3-roadmap.md](docs/project/v3.5.3-roadmap.md) - Testing Excellence: Phase 4 complete (5/5)

**Releasing:**
- [RELEASE_PROCESS.md](docs/contributing/RELEASE_PROCESS.md) - Complete 11-step release process (3 phases)
- [RELEASE_CHECKLIST.md](docs/contributing/RELEASE_CHECKLIST.md) - Printable release checklist
- [VERSION_MANAGEMENT.md](docs/contributing/VERSION_MANAGEMENT.md) - Version bumping with `bump_version.py`

**Git Workflow:**
- [GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md) - Branching strategy (Simplified GitHub Flow), branch types, PR guidelines
- [BRANCH_PROTECTION.md](docs/contributing/BRANCH_PROTECTION.md) - GitHub branch protection configuration

**Documentation:**
- [DOCUMENTATION_CONVENTIONS.md](docs/contributing/DOCUMENTATION_CONVENTIONS.md) - Naming conventions, structure, archive organization
- [_CANONICAL_REFERENCES.md](docs/guides/_CANONICAL_REFERENCES.md) - Single source of truth index, prevent duplication

**Error Codes:**
- [ERROR_CODES.md](docs/guides/ERROR_CODES.md) - Error code reference and meanings

### 🟢 Reference & History:

**Current Work:**
- [STATUS.md](docs/project/STATUS.md) - Current sprint status, version progress, metrics
- [v3.5.3-roadmap.md](docs/project/v3.5.3-roadmap.md) - Current roadmap: Testing Excellence (4 weeks, 52% → 70% coverage)

**Finding Historical Info:**
- [docs/archive/README.md](docs/archive/README.md) - Version timeline & complete archive index
- [docs/archive/code/](docs/archive/code/) - Archived scripts (PoCs, migrations, superseded tools)
- [docs/archive/plans/](docs/archive/plans/) - Historical roadmaps (vX.Y-roadmap.md format)
- [docs/archive/summaries/](docs/archive/summaries/) - Release notes (vX.Y.Z-release-notes.md format)
- [docs/archive/reviews/](docs/archive/reviews/) - Decision rationale, architectural reviews, analysis

**Archived Feature Specifications:**
- [docs/archive/plans/v2.2-html-reports-spec.md](docs/archive/plans/v2.2-html-reports-spec.md) - HTML report feature (v2.2)
- [docs/archive/plans/v2.2-retry-mechanism-spec.md](docs/archive/plans/v2.2-retry-mechanism-spec.md) - Retry mechanism (v2.2)
- [docs/archive/plans/v3.0-cli-ux-spec.md](docs/archive/plans/v3.0-cli-ux-spec.md) - CLI UX enhancement (v3.0)

**Complete Index:**
- [docs/README.md](docs/README.md) - Complete documentation navigation and index

---

## Key Constraints & Principles

**Security (CRITICAL):**
- **All paths:** Use `validate_path()` - blocks URL-encoded traversal, system directories
- **All user input:** Use `sanitize_string()` - context-aware (output/log/error), prevents injection
- **All API calls:** HTTPS only, validate all responses before processing
- **Error messages:** Sanitized, no sensitive path disclosure (use ERROR_HELP system)
- **Cache integrity:** HMAC-SHA256 signatures prevent tampering with security scores

**Architecture (3-Layer - STRICT):**
- **Layers:** Presentation → Application → Infrastructure (one-way dependencies only)
- **NO violations:** Infrastructure layer must NEVER import from Presentation layer
- **Command-Query Separation:** Commands fail fast, queries return data
- **KISS principle:** Simple solutions over clever ones, avoid premature optimization
- **See:** [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for complete rules and anti-patterns

**Testing (REQUIRED):**
- **Test Suite:** 604 tests (Phase 4: +70 tests), 100% passing
- **Coverage:** Current 52.37%, target 70% (85% overall goal, 95% security modules)
- **Pattern:** AAA (Arrange-Act-Assert) for all tests
- **Property Testing:** 20 tests generating 1,250+ scenarios (Hypothesis)
- **Run ALL tests before commits:** `python3 tests/test_*.py` or `pytest tests/`
- **Security tests:** Must pass with 0 vulnerabilities before any commit
- **Documentation:** See [TESTING.md](docs/guides/TESTING.md) + 10 specialized guides

**Error Handling:**
- **Exit codes:** 0=success/no vulns, 1=success/vulns found, 2=scan failed
- **Fail fast:** Invalid input should raise errors immediately (don't continue)
- **Continue on failures:** Individual extension scan failures should not stop entire scan
- **Use ERROR_HELP:** Provide actionable guidance in all error messages

**Threading (v3.5.0+):**
- **Parallel by default:** ThreadPoolExecutor with 3 workers (configurable 1-5)
- **Thread-safe:** All shared state must use locks (ThreadSafeStats class)
- **Main thread only:** Database writes happen in main thread (SQLite limitation)
- **Worker isolation:** Each worker has isolated API client instance
- **Performance details:** See [PERFORMANCE.md](docs/guides/PERFORMANCE.md) for benchmarks and optimization

→ **Full details:** See [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md), [SECURITY.md](docs/guides/SECURITY.md), [TESTING.md](docs/guides/TESTING.md), [PERFORMANCE.md](docs/guides/PERFORMANCE.md)

---

## Quick Command Reference

**Development:**
```bash
./vscan scan                           # Run scan (3 workers default, 4.88x faster)
python3 tests/test_*.py               # Run all tests
python3 scripts/bump_version.py X.Y.Z # Bump version
python3 -m build                      # Build distribution package
```

**Common Scan Tasks:**
```bash
vscan scan --output report.html       # Generate HTML report
vscan scan --output results.csv       # Export to CSV
vscan scan --workers 5                # Maximum performance (5 workers)
vscan scan --workers 1                # Sequential mode
vscan cache stats                     # Check cache statistics
vscan config show                     # View current configuration
```

**Development Workflow:**
```bash
./vscan scan --plain                  # Test with plain output (v2.x style)
python3 tests/test_security.py        # Run security tests
python3 tests/test_architecture.py    # Verify layer compliance
python3 scripts/bump_version.py --check  # Verify version consistency
```

→ **Full command reference:** Run `vscan --help` or see [Development Commands](#development-commands) section below

---

## Project Structure

**Single Source Architecture** - All code exists in `vscode_scanner/` package only:

```
vsc-extension-scanner/
├── vscode_scanner/          # Main package (single source of truth)
│   ├── __init__.py
│   ├── _version.py         # Version management
│   ├── cli.py              # Typer CLI framework (Presentation)
│   ├── scanner.py          # Core scan logic (Application)
│   ├── display.py          # Rich formatting (Presentation)
│   ├── config_manager.py   # Configuration file support (Infrastructure)
│   ├── constants.py        # Centralized constants
│   ├── vscan.py            # Entry point wrapper
│   ├── vscan_api.py        # API client (Infrastructure)
│   ├── cache_manager.py    # Caching with HMAC integrity (Infrastructure)
│   ├── extension_discovery.py  # Extension detection (Infrastructure)
│   ├── output_formatter.py     # JSON/CSV export (Infrastructure)
│   ├── html_report_generator.py  # HTML reports (Presentation)
│   ├── types.py           # Result dataclasses (Application)
│   └── utils.py           # Path validation, sanitization (Infrastructure)
├── scripts/
│   ├── bump_version.py           # Version management tool
│   ├── check_doc_freshness.sh    # Documentation quality validation
│   └── run_tests.py              # Test runner with pytest integration
├── tests/                 # Test files (604 tests, 100% passing, 52% coverage)
│   ├── test_security_regression.py  # Security test suite
│   ├── test_path_validation.py      # Path validation tests
│   ├── test_string_sanitization.py  # Sanitization tests
│   ├── test_cache_integrity.py      # HMAC integrity tests
│   ├── test_sqlite_security.py      # SQLite security audit
│   ├── test_display.py              # Display module tests
│   ├── test_scanner.py              # Scanner module tests
│   ├── test_cli.py                  # CLI module tests
│   ├── test_architecture.py         # Layer compliance tests
│   └── ...                          # Additional test files
├── docs/                  # Documentation (see docs/README.md)
│   └── archive/code/      # Archived scripts (PoCs, migrations, superseded tools)
├── vscan                  # Convenience wrapper for development
├── pyproject.toml         # Modern Python packaging (PEP 621)
└── MANIFEST.in            # Distribution rules
```

**Development Workflow:**
- Edit files in `vscode_scanner/` directory (single source)
- Run locally: `./vscan` or `python -m vscode_scanner.vscan`
- Build distribution: `python -m build`
- No duplicate files, no synchronization issues

→ **Architecture details:** See [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for layer responsibilities and dependency rules

---

## Development Commands

**Testing:**
```bash
# Security tests (MUST pass before any commit)
python3 tests/test_security.py              # Security vulnerability tests
python3 tests/test_security_regression.py   # Comprehensive security suite
python3 tests/test_path_validation.py       # Path validation coverage
python3 tests/test_string_sanitization.py   # String sanitization coverage
python3 tests/test_cache_integrity.py       # HMAC integrity tests

# Architecture & Core tests
python3 tests/test_architecture.py          # Layer compliance (0 violations required)
python3 tests/test_display.py              # Display module tests
python3 tests/test_scanner.py              # Scanner module tests
python3 tests/test_cli.py                  # CLI module tests

# Integration & Performance
python3 tests/test_integration.py          # Integration tests
python3 tests/test_performance.py          # Performance benchmarks
python3 tests/test_db_integrity.py         # Database integrity tests

# Run all tests
python3 -m pytest tests/                   # Full test suite
```

**Documentation Quality:**
```bash
# Check documentation freshness and detect staleness
./scripts/check_doc_freshness.sh              # Automated validation (6 checks)
```

**Running the Tool:**
```bash
# Basic usage
vscan                                      # Show help
vscan scan                                 # Scan with default settings (3 workers)
vscan scan --plain                         # Plain output (v2.x style, for CI/CD)
vscan scan --quiet                         # Minimal single-line summary

# Output formats
vscan scan --output results.json           # Save JSON to file
vscan scan --output report.html            # Generate interactive HTML report
vscan scan --output results.csv            # Export to CSV spreadsheet

# Performance tuning (v3.5.0+)
vscan scan --workers 5                     # Maximum performance (5 workers)
vscan scan --workers 1                     # Sequential mode (for debugging)
vscan config set scan.workers 3            # Set default worker count

# Filtering
vscan scan --publisher microsoft           # Only Microsoft extensions
vscan scan --min-risk-level high           # Only high/critical risk
vscan scan --verified-only                 # Only verified publishers
vscan scan --with-vulnerabilities          # Only extensions with vulnerabilities

# Cache management
vscan cache stats                          # View cache statistics
vscan cache clear                          # Clear all cache (with confirmation)
vscan scan --refresh-cache                 # Force refresh of scanned extensions
vscan scan --no-cache                      # Disable caching

# Configuration
vscan config init                          # Create default ~/.vscanrc file
vscan config show                          # Display current configuration
vscan config set scan.delay 2.0            # Set config value
vscan config get scan.delay                # Get specific config value

# Report generation from cache (no API calls)
vscan report report.html                   # Generate HTML report from cache
vscan report results.json                  # Generate JSON report from cache
vscan report results.csv                   # Generate CSV report from cache
```

**Version Management:**
```bash
python3 scripts/bump_version.py 3.5.1      # Bump version
python3 scripts/bump_version.py --show     # Show current version
python3 scripts/bump_version.py --check    # Verify version consistency across all files
```

**Building & Distribution:**
```bash
# Build package
rm -rf build/ dist/ *.egg-info            # Clean build artifacts
python3 -m build                           # Build wheel and source distribution

# Test installation
python3 -m venv test_env                   # Create test environment
source test_env/bin/activate               # Activate (Unix/macOS)
pip install dist/*.whl                     # Install package
vscan --version                            # Verify installation
deactivate                                 # Exit test environment
```

→ **Full release process:** See [RELEASE_PROCESS.md](docs/contributing/RELEASE_PROCESS.md) for complete 11-step workflow

---

## Common Development Tasks

**Adding a New Feature:**
1. Check if feature is in scope: See [PRD.md](docs/project/PRD.md)
2. Read relevant architecture docs: [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)
3. Implement with error handling and security validation
4. Add tests (maintain 85% coverage, 95% for security)
5. Update relevant documentation
6. Run all tests: `python3 tests/test_*.py`

**Making Security Changes:**
1. **MUST READ:** [SECURITY.md](docs/guides/SECURITY.md) - Complete requirements
2. Use existing patterns: `validate_path()`, `sanitize_string()`
3. Add regression tests to `tests/test_security_regression.py`
4. Verify 0 vulnerabilities: `python3 tests/test_security.py`
5. Get architectural review before commit

**Debugging Issues:**
```bash
# Run with plain output to see detailed progress
vscan scan --plain

# Test with custom extensions directory
vscan scan --extensions-dir ~/.vscode/extensions/

# Check API behavior with test extensions
python3 tests/test_api.py

# Run with Python debugger
python3 -m pdb -m vscode_scanner.vscan scan
```

**Before Committing:**
```bash
# 0. Verify git workflow (CRITICAL - See GIT_WORKFLOW.md)
git status                                 # Check working directory state
git branch                                 # Verify on feature branch, NOT main
# Expected: On branch feature/* or bugfix/* or hotfix/*
# Never commit directly to main!

# 1. Pre-commit hooks (RECOMMENDED - Phase 1)
# Install once: pip install -e .[dev] && pre-commit install
pre-commit run --all-files                 # Runs security checks automatically

# 2. Run ALL tests
python3 tests/test_*.py                    # All tests must pass

# 3. Verify security (CRITICAL - Phase 1 Enhanced)
python3 tests/test_security.py             # Must show 0 vulnerabilities
python3 tests/test_security_regression.py  # All security tests must pass
python3 tests/test_sqlite_security.py      # SQLite security audit (Phase 1)

# Phase 1 Security Tools (automated in pre-commit + CI/CD)
bandit -r vscode_scanner/ -ll              # AST-based security scan
safety check                               # Dependency vulnerabilities
pip-audit                                  # PyPI package audit

# 4. Check architecture compliance
python3 tests/test_architecture.py         # Must show 0 layer violations

# 5. Verify version consistency (if version changed)
python3 scripts/bump_version.py --check    # All files must have matching versions

# 6. Check documentation freshness (if docs changed)
./scripts/check_doc_freshness.sh           # Must show "✓ All checks passed!"

# 7. Commit and push (after all checks pass)
git add .                                  # Stage all changes
git commit -m "type(scope): subject"       # Follow commit message standards
git push origin feature/branch-name        # Push to feature branch
gh pr create --title "..." --body "..."    # Create pull request
```

→ **Git workflow details:** See [GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md) for complete branching strategy, PR guidelines, and commit standards

**Phase 1 Security Tools Setup (v3.5.1):**
```bash
# Install development tools (includes security tools)
pip install -e .[dev]

# Install pre-commit hooks (runs security checks automatically)
pre-commit install

# Test pre-commit hooks
pre-commit run --all-files

# Manual security scans (also run automatically in CI/CD)
bandit -r vscode_scanner/ -ll              # AST security analysis
safety check --full-report                 # Dependency vulnerabilities
pip-audit --desc                           # PyPI package audit
```

→ **Full testing guide:** See [TESTING.md](docs/guides/TESTING.md) and [TESTING_CHECKLIST.md](docs/contributing/TESTING_CHECKLIST.md)

---

## Documentation Structure

The `docs/` directory is organized into:

- **`docs/guides/`** - Timeless technical reference (**REQUIRED** reading for architecture, security, APIs)
- **`docs/project/`** - Active project management (status, requirements, current roadmap)
- **`docs/contributing/`** - Contributor guides and checklists
- **`docs/archive/`** - Historical documentation (version-based organization: plans/, summaries/, reviews/)

**⚠️ IMPORTANT:** Before making any code changes, you MUST review the REQUIRED documents:
1. [docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) - System design and constraints
2. [docs/guides/SECURITY.md](docs/guides/SECURITY.md) - Security requirements and threat model
3. [docs/project/PRD.md](docs/project/PRD.md) - Product requirements and scope

**For complete documentation navigation, see [docs/README.md](docs/README.md)**

---

## Key References

- **[README.md](README.md)** - Project overview, installation, quick start
- **[CHANGELOG.md](CHANGELOG.md)** - Release history (Keep a Changelog format)
- **[docs/project/STATUS.md](docs/project/STATUS.md)** - Current project status and progress
- **[docs/project/PRD.md](docs/project/PRD.md)** - Product requirements document
- **[docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)** ⚠️ REQUIRED - System architecture
- **[docs/guides/SECURITY.md](docs/guides/SECURITY.md)** ⚠️ REQUIRED - Security requirements
- **[docs/guides/API_REFERENCE.md](docs/guides/API_REFERENCE.md)** - vscan.dev API documentation
- **[docs/archive/README.md](docs/archive/README.md)** - Archive navigation and version timeline

**External:**
- **[vscan.dev](https://vscan.dev)** - VS Code Extension Security Analyzer
- **[VS Code Extension API](https://code.visualstudio.com/api)** - Extension API documentation
