# Security Policy

## Supported Versions

**Current Version:** See [docs/project/STATUS.md](docs/project/STATUS.md) for the latest stable release.

**Support Policy:**

- **Latest stable release:** Full support (bug fixes, features, security updates)
- **Previous minor version:** Maintenance support (security fixes, critical bugs)
- **Older versions:** Security fixes only (upgrade recommended)
- **Unsupported versions:** No support (immediate upgrade required)

**Version Support Table:**

| Version Pattern | Support Level | Recommendation |
| --------------- | ------------- | -------------- |
| Latest stable (5.x) | ✅ Full support | Recommended |
| Previous minor (4.x) | ⚠️ Maintenance | Security updates only |
| Older (3.x and below) | ❌ Unsupported | Upgrade immediately |

**To check your version:** Run `vscan --version` or see [docs/project/STATUS.md](docs/project/STATUS.md)

## Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Use GitHub Security Advisories for responsible disclosure:
https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new

**Response Timeline:**
- **Acknowledgment:** Within 48 hours
- **Status update:** Within 7 days
- **Fix timeline:** Based on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: 4 weeks

## Security Scanning

This project uses multiple layers of security scanning:

- **Bandit:** AST-based security analysis for Python code
- **Safety:** Dependency vulnerability scanning
- **pip-audit:** PyPI package security auditing
- **Semgrep:** Custom security rules for project-specific patterns
- **Hypothesis:** Property-based testing with 1,250+ generated scenarios

All PRs must pass security checks before merge. Security tests run:
- On every push
- On every pull request
- Weekly scheduled scans
- Pre-commit hooks for local validation

## Running Security Tests

**For Contributors:**

```bash
# Quick security validation (~1 minute)
python3 scripts/run_tests.py --security-only

# Pre-commit hooks (automatic validation)
pip install -e .[dev]
pre-commit install
pre-commit run --all-files

# Comprehensive pre-release validation
python3 scripts/run_tests.py --pre-release
```

**Test Coverage:**

- 120+ security-focused tests across multiple test files
- 95%+ coverage of security-critical modules
- 1,000+ property-based test scenarios (Hypothesis framework)
- Comprehensive coverage of CWE patterns: CWE-22 (Path Traversal), CWE-345 (HMAC), CWE-209 (Error Disclosure)

**See:** [docs/guides/SECURITY.md](docs/guides/SECURITY.md) for comprehensive security architecture and [docs/guides/testing/TESTING_SECURITY.md](docs/guides/testing/TESTING_SECURITY.md) for detailed testing guide.

## Security Features

This tool is designed with security as a priority:

**Input Validation & Sanitization:**
- **Path validation:** Prevents directory traversal attacks (CWE-22)
- **String sanitization:** Context-aware input sanitization (output/log/error)
- **Size limits:** 10MB API response limit, file size restrictions

**Data Integrity:**
- **HMAC cache integrity:** Cryptographic signatures prevent cache tampering (CWE-345)
- **Timing-safe comparisons:** Prevents timing attacks on signature validation

**Access Control:**
- **File permissions:** Restrictive 0o600 (files) and 0o700 (directories)
- **Directory restrictions:** Blocks access to system paths
- **Home directory boundaries:** Enforced containment

**Network Security:**
- **HTTPS enforcement:** All API calls use HTTPS with certificate validation
- **Request throttling:** Rate limiting (2s default delay, configurable)
- **Response validation:** Size limits and content type verification

**Error Handling:**
- **Fail-fast design:** Invalid input rejected immediately
- **Sanitized errors:** ERROR_HELP system prevents information disclosure (CWE-209)
- **No stack traces:** Clean error messages without sensitive details

**Concurrency Safety (v3.5.0+):**
- **Thread-safe statistics:** Lock-protected shared state
- **Isolated workers:** Each worker has isolated API client
- **Main thread writes:** Database operations in single thread (SQLite requirement)

**See:** [docs/guides/SECURITY.md](docs/guides/SECURITY.md) for complete security architecture

## Disclosure Policy

We follow responsible disclosure principles:

1. Report received via Security Advisory
2. Acknowledgment sent within 48 hours
3. Investigation and fix development
4. Coordinated disclosure after fix is available
5. Credit given to reporter (unless anonymity requested)

## Security Documentation

**Root Policy (this file):** Vulnerability reporting and security overview
**Comprehensive Guide:** [docs/guides/SECURITY.md](docs/guides/SECURITY.md) - Complete security architecture, requirements, and threat model
**Security Testing:** [docs/guides/testing/TESTING_SECURITY.md](docs/guides/testing/TESTING_SECURITY.md) - 21K testing guide with 102 test examples
**Security Analysis:** [docs/archive/reviews/security-analysis.md](docs/archive/reviews/security-analysis.md) - Historical vulnerability analysis

## Contact

**Primary:** GitHub Security Advisories (recommended)
https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new

**Alternative Contact:**
- GitHub Issues (for non-sensitive security questions): https://github.com/jvlivonius/vsc-extension-scanner/issues
- Direct contact: Via GitHub profile [@jvlivonius](https://github.com/jvlivonius)

**Note:** This is a solo-maintained project. Response times may vary, but security issues are prioritized.

**For General Questions:** See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines

## Security Fixes History

**Recent Security Fixes:**

Security fixes are documented in [CHANGELOG.md](CHANGELOG.md) and release notes. Notable security improvements include:

- **Path traversal protection:** Comprehensive validation preventing directory traversal attacks (CWE-22)
- **HMAC cache integrity:** Cryptographic signatures prevent cache tampering (CWE-345)
- **Input validation:** Context-aware string sanitization preventing injection attacks
- **File permissions:** Restrictive permissions (0o600 files, 0o700 directories)
- **Error disclosure prevention:** Sanitized error messages without sensitive information (CWE-209)

**Transparency Commitment:**

- All security fixes are documented in [CHANGELOG.md](CHANGELOG.md)
- Critical vulnerabilities disclosed via [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories)
- Historical vulnerability analysis in [docs/archive/reviews/security-analysis.md](docs/archive/reviews/security-analysis.md)

**To review specific version fixes:** Check [CHANGELOG.md](CHANGELOG.md) or [docs/project/STATUS.md](docs/project/STATUS.md)
