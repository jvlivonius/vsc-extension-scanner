# Archived Code

**Purpose:** Historical scripts and proof-of-concepts that are no longer actively used but preserved for reference and development history.

**Organization:** Files are named with version tags indicating when they were relevant (e.g., `v3.4-poc-parallel-scan.py` indicates a v3.4 proof-of-concept).

---

## Archived Scripts

### v3.4-poc-parallel-scan.py
**Original Location:** `scripts/poc_parallel_scan.py`
**Archived:** 2025-10-30
**Version Context:** v3.4 (proof-of-concept phase)
**Status:** Feature shipped in v3.5.0

**Purpose:** Proof-of-concept implementation for parallel scanning with ThreadPoolExecutor.

**Why Archived:**
- This was a PoC script to validate parallel scanning performance before integrating into the main codebase
- The parallel scanning feature was successfully integrated into `vscode_scanner/scanner.py` in v3.5.0
- The PoC demonstrated 4.88x speedup with 3 workers, which validated the approach
- Script is no longer needed as the production implementation is complete

**Historical Significance:**
- Proved feasibility of thread-safe parallel scanning
- Validated performance gains (4.88x with 3 workers, 6.2x with 5 workers)
- Informed the production implementation architecture
- Demonstrated ThreadPoolExecutor approach vs multiprocessing

**Related Documentation:**
- [v3.5.0 Release Notes](../summaries/v3.5.0-release-notes.md) - Parallel scanning feature
- [Performance Guide](../../guides/PERFORMANCE.md) - Parallel execution benchmarks
- [Architecture Guide](../../guides/ARCHITECTURE.md) - Threading model

---

### v3.5.2-migration-add-pytest-markers.py
**Original Location:** `scripts/add_pytest_markers.py`
**Archived:** 2025-10-30
**Version Context:** v3.5.2 (testing infrastructure migration)
**Status:** Migration complete, markers already added

**Purpose:** One-time migration script to add pytest markers to all test files.

**Why Archived:**
- This was a one-time migration utility to add pytest markers (unit, security, architecture, etc.) to test files
- All test files now have proper pytest markers in place
- The migration is complete and the script is no longer needed
- Test infrastructure now uses pytest markers for test organization and selective execution

**Historical Significance:**
- Enabled systematic test categorization across 604+ tests
- Allowed selective test execution by category (security, architecture, integration, etc.)
- Improved test organization and CI/CD pipeline flexibility
- Part of the v3.5.2 testing infrastructure enhancement

**Migration Details:**
- Added 7 marker categories: unit, security, architecture, parallel, integration, real_api, mock_validation
- Updated 20+ test files with appropriate markers
- Integrated with pytest.ini_options in pyproject.toml
- Enabled `pytest -m security` style selective execution

**Related Documentation:**
- [Testing Guide](../../guides/TESTING.md) - Pytest marker usage
- [Testing Checklist](../../contributing/TESTING_CHECKLIST.md) - Test execution by category
- [v3.5.2 Roadmap](../plans/v3.5.2-roadmap.md) - Testing phase details

---

### v3.5.1-setup-security-tools.sh
**Original Location:** `scripts/setup_security_tools.sh`
**Archived:** 2025-10-30
**Version Context:** v3.5.1 (Phase 1 security tools)
**Status:** Superseded by `pip install -e .[dev]`

**Purpose:** Install Phase 1 security scanning tools (bandit, safety, pip-audit) and configure pre-commit hooks.

**Why Archived:**
- Security tools are now managed through pyproject.toml `[project.optional-dependencies]`
- Modern installation method: `pip install -e .[dev]` handles all security tool dependencies
- Pre-commit configuration is managed through `.pre-commit-config.yaml`
- Script functionality is fully replaced by standard Python packaging practices

**Historical Significance:**
- Part of v3.5.1 Phase 1 security enhancement initiative
- Introduced AST-based security scanning (bandit)
- Added dependency vulnerability scanning (safety, pip-audit)
- Established automated pre-commit security checks
- Demonstrated security-first development approach

**Security Tools Covered:**
- **bandit** ≥1.7.6 - AST-based security scanner for Python code
- **safety** ≥2.3.0 - Dependency vulnerability scanner
- **pip-audit** ≥2.4.0 - PyPI package auditing tool
- **pre-commit** ≥3.0.0 - Pre-commit hooks framework

**Migration Path:**
```bash
# Old approach (archived script)
./scripts/setup_security_tools.sh

# New approach (current standard)
pip install -e .[dev]
pre-commit install
```

**Related Documentation:**
- [Security Guide](../../guides/SECURITY.md) - Security scanning practices
- [Release Process](../../contributing/RELEASE_PROCESS.md) - Security validation steps
- [v3.5.1 Summary](../summaries/v3.5.1-release-notes.md) - Phase 1 security details

---

## Archive Organization

**Naming Convention:**
- Format: `v[VERSION]-[descriptive-name].[ext]`
- Examples: `v3.4-poc-parallel-scan.py`, `v3.5.2-migration-add-pytest-markers.py`
- Version tag indicates when the script was relevant to development

**Categories:**
- **PoC (Proof of Concept):** Experimental scripts validating features before production
- **Migration:** One-time scripts for codebase migrations or updates
- **Setup/Config:** Superseded installation or configuration scripts

**Retention Policy:**
- Keep archived scripts indefinitely for historical reference
- Document why each script was archived and what replaced it
- Maintain version tags to understand development timeline
- Link to related documentation and release notes

---

## Using Archived Scripts

**⚠️ WARNING:** These scripts are archived and may not work with current codebase versions. They are preserved for historical reference only.

**Safe Usage:**
1. Read the "Why Archived" section to understand the context
2. Check "Related Documentation" for current approaches
3. Do NOT run archived scripts on production systems
4. Use archived scripts for learning or historical analysis only

**Modern Alternatives:**
- **Parallel scanning:** Use `vscan scan --workers 5` (production feature)
- **Pytest markers:** Already configured in `pyproject.toml` and test files
- **Security tools:** Use `pip install -e .[dev]` for all development dependencies

---

## See Also

- [Archive Index](../README.md) - Complete archive navigation
- [Release History](../../../CHANGELOG.md) - Version timeline
- [Development Scripts](../../../scripts/README.md) - Current active scripts (if exists)
