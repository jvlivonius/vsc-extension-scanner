# Bandit Suppression Guidelines

This document provides guidelines for using `# nosec` comments to suppress Bandit security warnings in the VS Code Extension Security Scanner project.

## Table of Contents
- [When to Suppress](#when-to-suppress)
- [When NOT to Suppress](#when-not-to-suppress)
- [Suppression Format](#suppression-format)
- [Review Process](#review-process)
- [Existing Suppressions](#existing-suppressions)

---

## When to Suppress

Use `# nosec` suppressions **only** in these justified cases:

### ✅ Valid Reasons for Suppression

1. **False Positive with Security Validation**
   - Bandit flags code that appears unsafe but is protected by validation
   - Security controls are in place and documented
   - Example: URL access with HTTPS enforcement

2. **Required Unsafe Operation with Mitigation**
   - Operation is necessary for functionality
   - Comprehensive security mitigations are implemented
   - Risk is understood and acceptable
   - Example: Dynamic SQL with parameterized queries

3. **Well-Documented Justification**
   - Clear explanation of why code is safe
   - References to validation functions or security controls
   - Evidence that security was considered

---

## When NOT to Suppress

### ❌ Invalid Reasons for Suppression

**Never suppress warnings for these reasons:**

1. **"The code works fine"**
   - Working code can still be insecure
   - Functionality ≠ Security

2. **"Too many warnings"**
   - Multiple warnings indicate systemic issues
   - Fix the root cause, don't hide symptoms

3. **"Deadline pressure"**
   - Security debt accrues interest
   - Technical debt becomes security debt
   - Schedule pressure is not a security justification

4. **"Will fix later"**
   - Create an issue instead of suppressing
   - Suppressions become permanent
   - Use TODOs sparingly and track them

5. **"Bandit doesn't understand my code"**
   - If Bandit is confused, so are reviewers
   - Refactor for clarity
   - Security through obscurity is not security

---

## Suppression Format

### Standard Format

```python
# nosec <RULE_CODE> - <CLEAR_JUSTIFICATION_WITH_VALIDATION_DETAILS>
```

### Required Elements

1. **Rule Code**: Specific Bandit test ID (e.g., `B310`, `B608`)
2. **Justification**: Why this code is safe despite the warning
3. **Validation Reference**: Function/control that makes it safe
4. **Evidence**: Proof that security was considered

### Format Examples

#### ✅ Good Suppression (URL Access)

```python
with urllib.request.urlopen(
    req, timeout=timeout
) as response:  # nosec B310 - URL validated by validate_url() for HTTPS enforcement
```

**Why this is good:**
- ✅ Specific rule code (B310)
- ✅ References validation function (`validate_url()`)
- ✅ Explains security control (HTTPS enforcement)
- ✅ Mentions timeout (DoS prevention)

#### ✅ Good Suppression (SQL Query)

```python
# nosec B608: Safe SQL - placeholders programmatically generated ("?", "?", ...),
# actual extension IDs passed as parameterized tuple (validated_ids).
# All IDs validated by validate_extension_id() before reaching this code.
cursor.execute(
    f"""
    DELETE FROM scan_cache
    WHERE extension_id NOT IN ({placeholders})
    """,  # nosec B608
    validated_ids,
)
```

**Why this is good:**
- ✅ Specific rule code and name (B608: Safe SQL)
- ✅ Explains parameterization mechanism
- ✅ References validation function
- ✅ Multi-line explanation for complex case
- ✅ Shows understanding of SQL injection prevention

#### ❌ Bad Suppression (Insufficient)

```python
result = subprocess.run(cmd, shell=True)  # nosec - needed for pipeline
```

**Why this is bad:**
- ❌ No rule code specified
- ❌ No explanation of what makes it safe
- ❌ No reference to input validation
- ❌ "needed" is not a security justification

#### ❌ Bad Suppression (Vague)

```python
xml_data = minidom.parseString(user_input)  # nosec B318 - safe
```

**Why this is bad:**
- ❌ "safe" without explaining why
- ❌ No validation reference
- ❌ Parsing user input with vulnerable function
- ❌ This should be fixed, not suppressed

---

## Review Process

### Before Adding a Suppression

1. **Question the Warning**
   - Is Bandit correct about the risk?
   - What attack scenarios exist?

2. **Explore Alternatives**
   - Can the code be refactored to avoid the issue?
   - Are there safer library functions available?
   - Would a different approach eliminate the warning?

3. **Implement Security Controls**
   - Add input validation
   - Use parameterization or escaping
   - Implement rate limiting or timeouts
   - Add bounds checking

4. **Document Thoroughly**
   - Explain the security reasoning
   - Reference validation functions
   - Provide attack scenario analysis

### Code Review Checklist

When reviewing code with suppressions:

- [ ] Rule code is specified (`# nosec BXXX`)
- [ ] Justification is clear and specific
- [ ] Validation function is referenced
- [ ] Security control is actually implemented
- [ ] Alternative approaches were considered
- [ ] Risk is acceptable and documented
- [ ] No better solution exists

### Security Team Review

**All suppressions require security review for:**

- Critical code paths (authentication, authorization)
- User input handling
- File system operations
- Network operations
- Cryptographic operations
- SQL queries

---

## Existing Suppressions

### Current Project Suppressions

As of the latest audit, this project has **3 suppressions** across **2 files**:

#### 1. `urllib.request.urlopen` (vscan_api.py:311)

**Rule**: B310 - Audit URL open for permitted schemes

```python
with urllib.request.urlopen(
    req, timeout=timeout
) as response:  # nosec B310 - URL validated by validate_url()
```

**Status**: ✅ Approved
**Justification**: URL validation enforces HTTPS-only, timeout prevents DoS
**Security Controls**:
- `validate_url()` function validates HTTPS requirement
- Response size limits (10MB max)
- Timeout configuration
- TLS validation via default SSL context

---

#### 2 & 3. SQL Dynamic IN Clause (cache_manager.py:1137, 1144)

**Rule**: B608 - Hardcoded SQL expressions

```python
# nosec B608: Safe SQL - placeholders programmatically generated
cursor.execute(
    f"""
    DELETE FROM scan_cache
    WHERE extension_id NOT IN ({placeholders})
    """,  # nosec B608
    validated_ids,
)
```

**Status**: ✅ Approved
**Justification**: Parameterized query with validated inputs
**Security Controls**:
- Programmatic placeholder generation (`",".join("?" * len(validated_ids))`)
- Parameterized tuple prevents SQL injection
- Input validation via `validate_extension_id()`
- F-string used only for placeholder count, not user data

---

#### 4. XML Parsing (scripts/run_tests.py:1671)

**Rule**: B318 - Use of minidom.parseString

```python
xml_str = parseString(tostring(testsuites)).toprettyxml(  # nosec B318
    indent="  "
)
```

**Status**: ✅ Approved
**Justification**: XML generated by script (trusted source), not from external input
**Security Controls**:
- Data source is internal test results
- No external XML input parsing
- Used only for test report generation

---

## Best Practices

### 1. Prefer Refactoring Over Suppression

**Bad**:
```python
os.system(user_input)  # nosec B605 - validated
```

**Good**:
```python
# Use subprocess with list arguments instead
subprocess.run([validated_command, validated_arg], check=True)
```

### 2. Document Security Analysis

**Bad**:
```python
eval(expression)  # nosec - safe
```

**Good**:
```python
# Validated against allowlist of safe mathematical operators (+, -, *, /)
# Maximum expression length: 100 characters
# No variable access allowed
# Runs in restricted environment with timeout
safe_eval(validated_expression)  # nosec B307 - validated by safe_eval()
```

### 3. Reference Security Tests

**Good**:
```python
# This pattern is validated by tests/test_path_validation.py::test_path_traversal
# which confirms all ../ sequences are rejected
sanitized_path = validate_path(user_path)  # nosec B108 - validated
```

### 4. Use Type Hints for Clarity

**Good**:
```python
def process_safe_data(validated_input: str) -> str:
    """Process input that has been validated by validate_input().

    Security: Input validation prevents injection attacks.
    See: tests/test_security.py::test_input_validation
    """
    return execute_safe_operation(validated_input)  # nosec B603 - validated
```

---

## Tools & Commands

### Find All Suppressions

```bash
# Find all nosec comments in codebase
grep -r "# nosec" vscode_scanner/

# Find suppressions without rule codes
grep -r "# nosec[^B]" vscode_scanner/

# Find suppressions without justification
grep -r "# nosec B[0-9]\\+$" vscode_scanner/
```

### Validate Suppressions

```bash
# Run Bandit with baseline to track suppression changes
bandit -r vscode_scanner/ -ll -f json -o bandit-current.json

# Compare against baseline
diff bandit-baseline.json bandit-current.json
```

### Generate Suppression Report

```bash
# Run Bandit and show only suppressed issues
bandit -r vscode_scanner/ -ll --confidence-level MEDIUM --severity-level MEDIUM
```

---

## References

### Internal Documentation
- [SECURITY.md](../guides/SECURITY.md) - Complete security requirements
- [ARCHITECTURE.md](../guides/ARCHITECTURE.md) - Security architecture principles
- [TESTING_SECURITY.md](../guides/testing/TESTING_SECURITY.md) - Security test patterns

### External Resources
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)

---

## Summary

**Golden Rule**: If you need to suppress a Bandit warning, you need to **prove** the code is safe, not just **claim** it is safe.

**Three Questions Before Suppressing**:
1. **Why is Bandit wrong?** (False positive analysis)
2. **What makes this code safe?** (Security controls)
3. **How do we prove it?** (Tests and validation)

If you can't answer all three, don't suppress the warning.

---

**Version**: 1.0
**Last Updated**: 2025-11-01
**Maintainer**: Security Team
