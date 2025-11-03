# CODE_REVIEW_CHECKLIST.md

**Purpose:** Security-focused code review checklist for pull requests
**Document Type:** Process Guide
**Audience:** Code Reviewers, Contributors

---

## Overview

This checklist ensures consistent security review for all code changes, with special focus on Bandit suppressions, path validation, and security controls.

---

## Pre-Review Checks

**Before reviewing PR:**

- [ ] All CI checks pass (tests, security, Bandit)
- [ ] No new Bandit critical findings
- [ ] PR description explains security considerations (if applicable)
- [ ] Security tests included for security-related changes

---

## Code Review Checklist

### Security Controls

**Path Validation:**
- [ ] All user paths validated with `validate_path()`
- [ ] No absolute paths or system directories accessed
- [ ] Path types correctly specified (`output`, `extensions`, `cache`)

**Input Validation:**
- [ ] Error messages sanitized with `sanitize_string()`
- [ ] File sizes checked before reading
- [ ] JSON structure validated after parsing
- [ ] No sensitive data in logs or error messages

**Access Control:**
- [ ] File permissions set restrictively (0o600/0o700)
- [ ] Cache directory created with user-only access
- [ ] No world-readable security-sensitive files

**Network Security:**
- [ ] All network requests use HTTPS only
- [ ] Response size limits enforced
- [ ] Timeouts configured for all requests

**Data Integrity:**
- [ ] SQL queries use parameterized statements
- [ ] HMAC signatures verified for cached data
- [ ] No string formatting in SQL queries

### Bandit Suppressions

**If PR adds `# nosec` suppressions:**

- [ ] **Rule code specified** - Format: `# nosec BXXX`
- [ ] **Justification is clear** - Explains WHY code is safe
- [ ] **Validation function referenced** - Points to security control
- [ ] **Security control actually implemented** - Function exists and works
- [ ] **Alternative approaches considered** - Better solution doesn't exist
- [ ] **Risk is acceptable** - Security team approved if critical path
- [ ] **No invalid reasons** - Not "works fine", "deadline pressure", etc.

**Suppression Format Check:**
```python
✅ GOOD:
with urllib.request.urlopen(req, timeout=timeout) as response:
    # nosec B310 - URL validated by validate_url() for HTTPS enforcement

❌ BAD:
result = subprocess.run(cmd, shell=True)  # nosec - needed
```

**Critical Path Review:**

If suppression is for any of these, **security team review required:**
- [ ] Authentication or authorization code
- [ ] User input handling
- [ ] File system operations
- [ ] Network operations
- [ ] Cryptographic operations
- [ ] SQL queries

---

## Architecture Compliance

**Layer Violations:**
- [ ] No Infrastructure imports in Presentation layer
- [ ] Dependencies flow one-way only (Presentation → Application → Infrastructure)
- [ ] No circular dependencies between modules

**Design Principles:**
- [ ] Follows KISS principle (simple > clever)
- [ ] Fail-fast validation (rejects invalid input immediately)
- [ ] Command-Query separation maintained

---

## Testing Requirements

**Test Coverage:**
- [ ] New code has tests (85% overall, 95% security modules)
- [ ] Security functions have comprehensive tests
- [ ] All test suites pass locally and in CI

**Security Tests:**
- [ ] Path validation tests for new paths
- [ ] String sanitization tests for new output
- [ ] Regression tests for security fixes
- [ ] Property-based tests for complex logic

---

## Documentation Updates

**If PR changes:**
- [ ] Security requirements → Update SECURITY.md
- [ ] Error handling → Update ERROR_HANDLING.md
- [ ] Architecture → Update ARCHITECTURE.md
- [ ] API behavior → Update API_REFERENCE.md
- [ ] Testing patterns → Update TESTING.md or testing/ subdirectory

---

## Common Issues to Watch For

### Anti-Patterns

❌ **Don't:**
- Accept generic suppression justifications ("safe", "needed", "works fine")
- Skip validation for "temporary" code
- Merge PRs with failing Bandit critical findings
- Allow hard-coded paths or credentials
- Permit SQL string formatting (`f"SELECT {user_input}"`)

✅ **Do:**
- Request specific security justifications
- Verify validation functions are called
- Run security tests locally
- Check for path traversal vulnerabilities
- Ensure parameterized SQL queries

### Security Red Flags

**Immediate rejection if:**
- [ ] New suppression without rule code or justification
- [ ] Path validation bypassed or commented out
- [ ] User input used in SQL without parameterization
- [ ] File operations on absolute paths or system directories
- [ ] Error messages expose sensitive information
- [ ] Network requests use HTTP instead of HTTPS
- [ ] File permissions set to world-readable (0o644, 0o777)

---

## Approval Criteria

**PR can be approved if:**

1. ✅ All security controls properly implemented
2. ✅ No new Bandit critical findings
3. ✅ Any suppressions properly justified and validated
4. ✅ Security tests pass with 95%+ coverage for security modules
5. ✅ Architecture compliance verified
6. ✅ Documentation updated appropriately

**PR requires changes if:**

1. ❌ Security vulnerabilities introduced
2. ❌ Suppressions lack proper justification
3. ❌ Validation functions bypassed
4. ❌ Tests fail or coverage drops
5. ❌ Architecture violations present

---

## References

- **[SECURITY.md](../guides/SECURITY.md)** - Security requirements and Bandit suppression policy
- **[testing/TESTING_SECURITY.md](../guides/testing/TESTING_SECURITY.md)** - Security testing and suppression validation
- **[ARCHITECTURE.md](../guides/ARCHITECTURE.md)** - Architecture principles and layer rules
- **[GIT_WORKFLOW.md](GIT_WORKFLOW.md)** - PR process and commit standards

---

**Version:** 1.0
**Last Updated:** 2025-11-03
**Maintained By:** Security Team
