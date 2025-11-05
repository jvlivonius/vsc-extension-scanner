# CLAUDE.md

Guidance for Claude Code when working with this repository.

---

## ⚠️ REQUIRED READING BEFORE CODE CHANGES

**STOP!** Before any code changes, you **MUST** read these three documents:

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) | 3-layer architecture, design principles, anti-patterns, module responsibilities |
| [SECURITY.md](docs/guides/SECURITY.md) | `validate_path()`, `sanitize_string()`, threat model, HMAC integrity |
| [PRD.md](docs/project/PRD.md) | Feature scope, requirements, constraints, what's in/out of scope |

**Current Status:** → [STATUS.md](docs/project/STATUS.md) for version, features, test metrics, active roadmap

---

## Project Overview

VS Code Extension Security Scanner - Python CLI tool for manual security audits of VS Code extensions via vscan.dev API.

**IMPORTANT**: Unofficial, community-maintained. Security analysis **powered by [vscan.dev](https://vscan.dev)**. Not affiliated with vscan.dev. → [ATTRIBUTION.md](ATTRIBUTION.md)

**Tech Stack:**

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| HTTP | urllib.request (stdlib) |
| Database | SQLite3 (stdlib, HMAC integrity) |
| CLI | Typer ≥0.9.0 |
| Formatting | Rich ≥13.0.0 |
| Output | JSON, HTML (self-contained), CSV |
| Config | INI format (~/.vscanrc) |

---

## Documentation Quick Reference

### 🔴 Critical (Always Required)

| Task | Documents |
|------|-----------|
| Architecture | [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) - 3-layer, KISS, fail-fast |
| Security | [SECURITY.md](docs/guides/SECURITY.md) - Validation patterns, defense layers |
| Scope | [PRD.md](docs/project/PRD.md) - Feature requirements |

### 🟡 Task-Specific

| Task | Primary Doc | Related |
|------|-------------|---------|
| **Features** | [PRD.md](docs/project/PRD.md), [STATUS.md](docs/project/STATUS.md) | [v3.7 roadmap](docs/project/v3.7-testability-maintainability-roadmap.md) |
| **Security** | [SECURITY.md](docs/guides/SECURITY.md) | [ERROR_HANDLING.md](docs/guides/ERROR_HANDLING.md) |
| **API** | [API_REFERENCE.md](docs/guides/API_REFERENCE.md) | vscan.dev endpoints |
| **Performance** | [PERFORMANCE.md](docs/guides/PERFORMANCE.md) | Threading, benchmarks |
| **Testing** | [TESTING.md](docs/guides/TESTING.md) | [testing/](docs/guides/testing/) guides |
| **Releasing** | [RELEASE_PROCESS.md](docs/contributing/RELEASE_PROCESS.md) | [VERSION_MANAGEMENT.md](docs/contributing/VERSION_MANAGEMENT.md) |
| **Git** | [GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md) | [BRANCH_PROTECTION.md](docs/contributing/BRANCH_PROTECTION.md) |

### 🟢 Reference

| Type | Location |
|------|----------|
| Current work | [STATUS.md](docs/project/STATUS.md) |
| History | [docs/archive/README.md](docs/archive/README.md) |
| Error codes | [ERROR_CODES.md](docs/guides/ERROR_CODES.md) |
| Full index | [docs/README.md](docs/README.md) |

---

## Key Constraints & Principles

**Security (CRITICAL):**
- **All paths:** `validate_path()` - blocks traversal, system dirs
- **All input:** `sanitize_string()` - context-aware, prevents injection
- **All API:** HTTPS only, validate responses
- **Errors:** Sanitized, no path disclosure, use ERROR_HELP
- **Cache:** HMAC-SHA256 integrity

**Architecture (3-Layer - STRICT):**
- Layers: Presentation → Application → Infrastructure (one-way only)
- NO violations: Infrastructure NEVER imports Presentation
- Command-Query Separation, KISS principle
- → [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for rules

**Testing (REQUIRED):**
- Pattern: AAA (Arrange-Act-Assert)
- Property testing: Hypothesis (1,000+ scenarios)
- Security: 0 vulnerabilities before commit
- → [STATUS.md](docs/project/STATUS.md) for metrics
- → [TESTING.md](docs/guides/TESTING.md) for guides

**Error Handling:**
- Exit codes: 0=no vulns, 1=vulns found, 2=failed
- Fail fast on invalid input
- Continue on individual scan failures
- Use ERROR_HELP system

**Threading:**
- Parallel default: ThreadPoolExecutor, 3 workers (1-5)
- Thread-safe: locks for shared state
- Main thread only: DB writes (SQLite limitation)
- Worker isolation: API client per worker
- → [PERFORMANCE.md](docs/guides/PERFORMANCE.md) for details

---

## Essential Commands

### Development
```bash
./vscan scan                           # Run scan (3 workers)
python3 -m pytest tests/               # Run all tests
python3 scripts/bump_version.py X.Y.Z # Bump version
python3 -m build                       # Build package
```

### Common Operations

| Task | Command | Notes |
|------|---------|-------|
| **Output** | `vscan scan --output FILE` | .json/.html/.csv |
| **Workers** | `vscan scan --workers N` | 1-5 (3 default) |
| **Filter** | `vscan scan --publisher X` | Filter extensions |
| **Cache** | `vscan cache stats/clear` | Manage cache |
| **Config** | `vscan config show/set` | Manage ~/.vscanrc |
| **Report** | `vscan report FILE` | From cache (no API) |

### Testing

| Test Type | Command |
|-----------|---------|
| Security (CRITICAL) | `python3 tests/test_security.py` |
| Architecture | `python3 tests/test_architecture.py` |
| Full suite | `python3 -m pytest tests/` |

→ Full reference: `vscan --help` or [TESTING.md](docs/guides/TESTING.md)

---

## Project Structure

**Single Source** - All code in `vscode_scanner/` package:

- **Core Package:** `vscode_scanner/`
  - `cli.py` (Presentation) - Typer CLI
  - `scanner.py` (Application) - Core scan logic
  - `display.py` (Presentation) - Rich formatting
  - `vscan_api.py` (Infrastructure) - API client
  - `cache_manager.py` (Infrastructure) - HMAC caching
  - `extension_discovery.py` (Infrastructure) - Extension detection
  - `output_formatter.py` (Infrastructure) - JSON/CSV export
  - `html_report_generator.py` (Presentation) - HTML reports
  - `config_manager.py` (Infrastructure) - Config support
  - `types.py` (Application) - Result dataclasses
  - `utils.py` (Infrastructure) - `validate_path()`, `sanitize_string()`
  - `_version.py`, `constants.py`, `vscan.py`

- **Support:**
  - `scripts/` - bump_version.py, check_doc_freshness.sh, run_tests.py
  - `tests/` - Test suite (→ [STATUS.md](docs/project/STATUS.md) for metrics)
  - `docs/` - Documentation (→ [docs/README.md](docs/README.md))
  - `vscan` - Dev wrapper

**Workflow:** Edit `vscode_scanner/` → Run `./vscan` → Build `python -m build`

→ [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for layer rules

---

## Development Workflows

### Adding Features
1. Check scope: [PRD.md](docs/project/PRD.md)
2. Read: [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)
3. Implement: error handling + security validation
4. Test: maintain 87%+ overall, 80%+ critical, 95%+ security
5. Docs: update relevant files
6. Verify: `python3 -m pytest tests/`

### Security Changes
1. **MUST READ:** [SECURITY.md](docs/guides/SECURITY.md)
2. Use patterns: `validate_path()`, `sanitize_string()`
3. Add tests: `tests/test_security_regression.py`
4. Verify: 0 vulnerabilities
5. Review: architectural approval

### Before Committing

**Checklist:**
```bash
# 1. Git workflow (CRITICAL)
git status && git branch                    # Verify feature/* branch

# 2. Pre-commit (RECOMMENDED)
pre-commit run --all-files                  # Security checks

# 3. Tests (REQUIRED)
python3 -m pytest tests/                    # All pass
python3 tests/test_security.py              # 0 vulnerabilities
python3 tests/test_architecture.py          # 0 violations

# 4. Commit
git add . && git commit -m "type(scope): subject"
git push origin feature/branch-name
gh pr create --title "..." --body "..."

# 5. Cleanup after merge
git checkout main && git pull
git branch -D feature/branch-name
```

→ [GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md) for complete workflow
→ [TESTING.md](docs/guides/TESTING.md) for pre-commit hooks setup

---

## Documentation Organization

- `docs/guides/` - Timeless technical reference (REQUIRED reading)
- `docs/project/` - Active project management (status, requirements, roadmap)
- `docs/contributing/` - Contributor guides, checklists
- `docs/archive/` - Historical documentation (version-based)

→ [docs/README.md](docs/README.md) for complete navigation

---

## External Resources

- [vscan.dev](https://vscan.dev) - VS Code Extension Security Analyzer
- [VS Code Extension API](https://code.visualstudio.com/api) - Extension docs
