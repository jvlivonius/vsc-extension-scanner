# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.5.x   | :white_check_mark: |
| < 3.5   | :x:                |

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

## Security Features

This tool is designed with security as a priority:

- **Path validation:** Prevents directory traversal attacks
- **String sanitization:** Context-aware input sanitization
- **HMAC cache integrity:** Cryptographic signatures prevent cache tampering
- **No external dependencies at runtime:** Minimal attack surface
- **Fail-fast design:** Invalid input rejected immediately

## Disclosure Policy

We follow responsible disclosure principles:

1. Report received via Security Advisory
2. Acknowledgment sent within 48 hours
3. Investigation and fix development
4. Coordinated disclosure after fix is available
5. Credit given to reporter (unless anonymity requested)

## Contact

For security concerns that don't fit the advisory process, contact the maintainer through GitHub.

## Past Security Issues

No security vulnerabilities have been reported or discovered to date.
