# Property-Based Testing Guide

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Framework:** Hypothesis
**Target Audience:** Developers, Security Engineers

---

## Quick Reference

**Test Files:**
- `tests/test_property_validation.py` - Path/string validation (14 tests, 14K scenarios)
- `tests/test_property_cache.py` - Cache integrity (6 tests, 700 scenarios)

**Run Property Tests:**
```bash
python3 tests/test_property_validation.py
python3 tests/test_property_cache.py
pytest tests/test_property_*.py -v
```

**Current Status:** See → [STATUS.md](../../project/STATUS.md) for current property test counts and pass rates.

**Baseline:** 20+ property tests generating 1,000+ scenarios automatically

---

## What is Property-Based Testing?

Instead of writing individual test examples, you define **properties** (invariants that should always hold) and let Hypothesis generate hundreds of test cases automatically.

**Example-Based (Traditional):**
```python
def test_path_traversal_examples():
    """Test specific path traversal attempts."""
    assert_blocked("../../etc/passwd")
    assert_blocked("%2e%2e%2f/etc")
    # Tests 2 cases
```

**Property-Based (Hypothesis):**
```python
@given(st.text())
@settings(max_examples=1000)
def test_path_traversal_property(self, path):
    """ANY path with '..' should be blocked."""
    if ".." in path:
        with self.assertRaises(ValueError):
            validate_path(path)
    # Tests 1000+ generated cases, finds edge cases automatically!
```

---

## Key Security Properties

### 1. Robustness - Never Crash
```python
@given(st.text())
def test_validate_path_never_crashes(self, path):
    """validate_path handles ANY input without crashing."""
    try:
        result = validate_path(path)
        self.assertTrue(result)
    except (ValueError, OSError):
        pass  # Expected for invalid paths
    # Any other exception = test failure
```

### 2. Security - Always Block Attacks
```python
@given(st.text(min_size=1))
@example("../../../etc/passwd")  # Explicit regression test
def test_traversal_always_blocked(self, path):
    """Path traversal ALWAYS blocked (CRITICAL)."""
    if ".." in path or "%2e%2e" in path.lower():
        with self.assertRaises(ValueError):
            validate_path(path)
```

### 3. Data Integrity - Roundtrip Preservation
```python
@given(extension_ids, versions, scan_results)
def test_cache_roundtrip(self, ext_id, version, data):
    """Data stored = data retrieved."""
    cache.save_result(ext_id, version, data)
    retrieved = cache.get_cached_result(ext_id, version)
    self.assertEqual(retrieved, data)
```

### 4. Tampering Detection (CRITICAL)
```python
@given(extension_ids, versions, scan_results)
def test_tampering_detected(self, ext_id, version, data):
    """Any cache tampering MUST be detected."""
    cache.save_result(ext_id, version, data)

    # Tamper directly in SQLite
    tamper_database(ext_id, fake_data)

    # Tampered data MUST be rejected
    result = cache.get_cached_result(ext_id, version)
    assert result is None or result != fake_data
```

---

## Hypothesis Strategies

```python
from hypothesis import given, strategies as st

# Generate any string
@given(st.text())

# Generate specific patterns
extension_ids = st.builds(
    lambda p, e: f"{p}.{e}",
    st.text(alphabet='a-z0-9-', min_size=2, max_size=20),
    st.text(alphabet='a-z0-9-', min_size=2, max_size=20)
)

# Generate semantic versions
versions = st.from_regex(r'[0-9]+\.[0-9]+\.[0-9]+')

# Generate structured data
scan_results = st.fixed_dictionaries({
    'scan_status': st.just('success'),
    'security_score': st.integers(0, 100),
    'risk_level': st.sampled_from(['low', 'medium', 'high'])
})
```

---

## Benefits

1. **Automatic Edge Case Discovery** - Finds cases you wouldn't think to test
2. **Comprehensive Coverage** - 1000+ scenarios per property
3. **Regression Prevention** - Failed cases become explicit examples
4. **High Confidence** - Security functions validated under extensive fuzzing

---

## Key Lessons from Property-Based Testing

**Property-based testing excels at finding edge cases that example-based tests miss:**

### Common Bug Patterns Discovered

1. **Regex Edge Cases**
   - Example: Escape sequence handling that removes both escape and following character
   - Lesson: Test with comprehensive character ranges, not just expected inputs

2. **String Boundary Conditions**
   - Example: Whitespace-only strings, empty strings, control characters
   - Lesson: Define "valid" precisely - whitespace may be printable but not meaningful

3. **Test Strategy Configuration**
   - Example: Hypothesis categories vs explicit codepoint ranges
   - Lesson: Use explicit constraints (`min_codepoint=0x20`) over category exclusions

### Best Practices

✅ **Property Testing Works**
- Finds bugs traditional unit tests miss
- Validates security invariants across large input spaces
- High ROI for security-critical functions

⚠️ **Test Expectations Matter**
- Define precise requirements (not just "printable")
- Document edge case handling explicitly
- Test failures may indicate bugs OR incorrect expectations

🔧 **Strategy Tuning Critical**
- Use explicit constraints for security code
- Tune generators for realistic attack patterns
- Leverage failed examples for regression tests

---

## See Full Guide

For complete property-based testing documentation including:
- All 20 property tests detailed
- Attack vectors covered
- Hypothesis configuration
- Debugging failed properties
- Writing new property tests

**See:** Original [TESTING.md](../TESTING.md) section "Property-Based Testing" for complete implementation details

---

**Full Documentation:** See [TESTING.md](../TESTING.md) § Property-Based Testing
