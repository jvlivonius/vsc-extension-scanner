# Test File Template

**Purpose:** Standard template for creating new test files with consistent patterns
**Document Type:** Timeless Reference
**Applies To:** All versions
**Major Revision Trigger:** Test framework changes or pattern updates
**Target Audience:** Contributors, Developers

---

## Standard Test File Structure

Use this template when creating new test files to ensure consistency across the test suite.

```python
#!/usr/bin/env python3
"""
[Module Name] Test Suite

[Brief description of what this test file covers - 1-2 sentences]

**Test Coverage:**
- [Feature/Function 1]: [What aspects are tested]
- [Feature/Function 2]: [What aspects are tested]
- [Feature/Function 3]: [What aspects are tested]

**Test Categories:**
- Unit tests: [X tests]
- Integration tests: [Y tests]
- Edge case tests: [Z tests]

**See:**
- [Module under test path] - Source code being tested
- [Related documentation] - If applicable
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import module under test
from vscode_scanner.[module_name] import [functions_to_test]

# Import related modules as needed
from vscode_scanner.utils import validate_path, sanitize_string


class Test[FeatureName](unittest.TestCase):
    """Test suite for [feature/class/function name].

    **Purpose:** [Brief description of what this test class validates]

    **Scope:**
    - [Scope item 1]
    - [Scope item 2]
    """

    def setUp(self):
        """Set up test fixtures before each test method.

        Creates temporary resources, mock objects, or test data
        needed by multiple test methods.
        """
        # Example: Create temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Example: Initialize test data
        self.sample_data = {
            "key": "value",
            "count": 42
        }

        # Example: Create mock objects
        self.mock_api = MagicMock()

    def tearDown(self):
        """Clean up test fixtures after each test method.

        Removes temporary files, closes connections, resets mocks.
        """
        # Example: Clean up temporary directory
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # ============================================================
    # Happy Path Tests
    # ============================================================

    def test_[feature]_with_valid_input(self):
        """Test [feature] with valid input.

        **Arrange:** [What is set up]
        **Act:** [What action is performed]
        **Assert:** [What outcome is verified]
        """
        # Arrange
        valid_input = "test_value"
        expected_output = "expected_result"

        # Act
        result = function_under_test(valid_input)

        # Assert
        self.assertEqual(result, expected_output,
                        msg="Result should match expected output")

    def test_[feature]_returns_expected_type(self):
        """Test that [feature] returns correct data type."""
        # Arrange
        test_input = "value"

        # Act
        result = function_under_test(test_input)

        # Assert
        self.assertIsInstance(result, dict,
                            msg="Result should be a dictionary")

    # ============================================================
    # Edge Case Tests
    # ============================================================

    def test_[feature]_with_empty_input(self):
        """Test [feature] handles empty input correctly."""
        # Arrange
        empty_input = ""

        # Act & Assert
        with self.assertRaises(ValueError,
                              msg="Should reject empty input"):
            function_under_test(empty_input)

    def test_[feature]_with_none_input(self):
        """Test [feature] handles None input correctly."""
        # Arrange
        none_input = None

        # Act & Assert
        with self.assertRaises(ValueError,
                              msg="Should reject None input"):
            function_under_test(none_input)

    def test_[feature]_with_maximum_length_input(self):
        """Test [feature] handles maximum length input."""
        # Arrange
        max_input = "x" * 1000  # Maximum allowed length

        # Act
        result = function_under_test(max_input)

        # Assert
        self.assertIsNotNone(result,
                           msg="Should handle max length input")

    # ============================================================
    # Error Handling Tests
    # ============================================================

    def test_[feature]_raises_on_invalid_type(self):
        """Test that [feature] raises TypeError for invalid input type."""
        # Arrange
        invalid_input = 12345  # Expected string, got int

        # Act & Assert
        with self.assertRaises(TypeError,
                              msg="Should reject invalid type"):
            function_under_test(invalid_input)

    def test_[feature]_provides_clear_error_message(self):
        """Test that error messages are clear and actionable."""
        # Arrange
        invalid_input = "invalid"

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            function_under_test(invalid_input)

        error_message = str(context.exception)
        self.assertIn("invalid", error_message.lower(),
                     msg="Error message should mention 'invalid'")

    # ============================================================
    # Integration Tests (if applicable)
    # ============================================================

    def test_[feature]_integrates_with_[other_component](self):
        """Test integration between [feature] and [other component]."""
        # Arrange
        component_a = ComponentA()
        component_b = ComponentB()

        # Act
        component_a.process()
        result = component_b.retrieve()

        # Assert
        self.assertEqual(result, expected_value,
                        msg="Components should integrate correctly")

    # ============================================================
    # Mock/Patch Tests (when testing external dependencies)
    # ============================================================

    @patch('vscode_scanner.[module].external_service')
    def test_[feature]_calls_external_service(self, mock_service):
        """Test that [feature] calls external service correctly."""
        # Arrange
        mock_service.return_value = {"status": "success"}

        # Act
        result = function_under_test()

        # Assert
        mock_service.assert_called_once()
        self.assertEqual(result["status"], "success")

    @patch.dict(os.environ, {"TEST_VAR": "test_value"})
    def test_[feature]_reads_environment_variable(self):
        """Test that [feature] reads environment variable correctly."""
        # Act
        result = function_under_test()

        # Assert
        self.assertIn("test_value", result)


# ============================================================
# Additional Test Classes (if needed for organization)
# ============================================================

class Test[AnotherFeature](unittest.TestCase):
    """Test suite for [another feature].

    **Purpose:** [Brief description]
    """

    def test_[another_test](self):
        """Test [another aspect]."""
        # AAA pattern
        pass


# ============================================================
# Test Suite Runner
# ============================================================

def run_tests():
    """Run all test cases in this module.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(Test[FeatureName]))
    suite.addTests(loader.loadTestsFromTestCase(Test[AnotherFeature]))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
```

---

## Key Principles

### 1. AAA Pattern (Arrange-Act-Assert)

**Every test should follow this structure:**

```python
def test_example(self):
    """Test description."""
    # Arrange - Set up test data and conditions
    input_data = "test"
    expected = "result"

    # Act - Execute the code under test
    actual = function_to_test(input_data)

    # Assert - Verify the outcome
    self.assertEqual(actual, expected)
```

### 2. Clear Test Names

**Test names should be descriptive and follow this pattern:**

```
test_[feature]_[condition]_[expected_result]
```

**Examples:**
```python
test_validate_path_with_traversal_raises_error()
test_cache_save_with_valid_data_succeeds()
test_sanitize_string_removes_ansi_codes()
```

### 3. Comprehensive Docstrings

**Every test should have a docstring explaining:**
- What is being tested
- Why it matters
- What the expected behavior is

```python
def test_cache_integrity_prevents_tampering(self):
    """Test that HMAC signatures prevent cache tampering.

    This is a CRITICAL security test. If cache entries can be
    tampered with, security scores could be manipulated.

    **Given:** A cached security scan result
    **When:** The database is modified directly (simulating attack)
    **Then:** The tampered data should be rejected
    """
```

### 4. Test Organization

**Group related tests with clear section headers:**

```python
# ============================================================
# Happy Path Tests - Normal operation cases
# ============================================================

# ============================================================
# Edge Case Tests - Boundary conditions
# ============================================================

# ============================================================
# Error Handling Tests - Exception cases
# ============================================================

# ============================================================
# Security Tests - Attack scenarios
# ============================================================
```

### 5. Fixture Management

**Use setUp/tearDown for shared resources:**

```python
def setUp(self):
    """Create resources needed by multiple tests."""
    self.temp_dir = tempfile.mkdtemp()
    self.test_file = os.path.join(self.temp_dir, "test.db")

def tearDown(self):
    """Clean up resources after tests."""
    if os.path.exists(self.temp_dir):
        shutil.rmtree(self.temp_dir)
```

**Benefits:**
- Reduces code duplication
- Ensures clean state for each test
- Prevents resource leaks

### 6. Assertion Messages

**Always provide descriptive assertion messages:**

```python
# ✅ GOOD - Clear message
self.assertEqual(result, expected,
                msg=f"Expected {expected}, got {result}")

# ❌ BAD - No message
self.assertEqual(result, expected)
```

### 7. Mock External Dependencies

**Use mocks for external services to keep tests fast and isolated:**

```python
@patch('vscode_scanner.vscan_api.VScanAPI.analyze_extension')
def test_scan_handles_api_failure(self, mock_api):
    """Test graceful handling of API failures."""
    # Arrange
    mock_api.side_effect = requests.ConnectionError("API unavailable")

    # Act & Assert
    with self.assertRaises(ConnectionError):
        scanner.scan("test.extension")
```

---

## Test Categories

### Unit Tests
**Purpose:** Test individual functions/methods in isolation
**Scope:** Single function or method
**Dependencies:** Mocked or minimal

```python
def test_sanitize_string_removes_ansi_codes(self):
    """Unit test for ANSI code removal."""
    input_str = "\x1b[31mRed Text\x1b[0m"
    result = sanitize_string(input_str, context="output")
    self.assertEqual(result, "Red Text")
```

### Integration Tests
**Purpose:** Test interaction between multiple components
**Scope:** Multiple functions/classes working together
**Dependencies:** Real implementations where possible

```python
def test_scan_and_cache_integration(self):
    """Integration test for scan → cache workflow."""
    scanner = Scanner(cache_enabled=True)
    result = scanner.scan("test.extension")

    # Verify cached
    cached = cache_manager.get("test.extension")
    self.assertEqual(cached, result)
```

### Property-Based Tests
**Purpose:** Test properties that should hold for all inputs
**Scope:** Validate invariants across large input space
**Dependencies:** Hypothesis framework

```python
@given(st.text())
@settings(max_examples=1000)
def test_sanitize_never_crashes(self, input_str):
    """Property: sanitize_string should handle ANY input."""
    try:
        result = sanitize_string(input_str)
        self.assertIsInstance(result, str)
    except Exception as e:
        self.fail(f"Should not crash: {e}")
```

### Security Tests
**Purpose:** Validate security properties and attack resistance
**Scope:** Attack scenarios and security boundaries
**Dependencies:** Real security functions (no mocks)

```python
def test_path_validation_blocks_all_traversal_variants(self):
    """Security test: Block all path traversal attempts."""
    attacks = [
        "../../../etc/passwd",
        "%2e%2e%2f",
        "..\\..\\windows\\system32"
    ]

    for attack in attacks:
        with self.assertRaises(ValueError,
                              msg=f"Should block: {attack}"):
            validate_path(attack)
```

---

## Common Patterns

### Testing Exceptions

```python
def test_function_raises_on_invalid_input(self):
    """Test that ValueError is raised for invalid input."""
    with self.assertRaises(ValueError) as context:
        function_under_test("invalid")

    # Optionally verify error message
    self.assertIn("invalid", str(context.exception))
```

### Testing File Operations

```python
def test_function_creates_file(self):
    """Test file creation."""
    # Arrange
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "output.txt")

    try:
        # Act
        function_under_test(file_path)

        # Assert
        self.assertTrue(os.path.exists(file_path))

        # Verify content
        with open(file_path, 'r') as f:
            content = f.read()
            self.assertIn("expected", content)
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
```

### Testing Async Operations (if applicable)

```python
async def test_async_function(self):
    """Test asynchronous function."""
    result = await async_function()
    self.assertEqual(result, expected)
```

### Testing with Temporary Files

```python
def test_function_with_temp_file(self):
    """Test function with temporary file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test data")
        temp_path = f.name

    try:
        result = function_under_test(temp_path)
        self.assertEqual(result, expected)
    finally:
        os.unlink(temp_path)
```

---

## Coverage Requirements

### Target Coverage by Test Type

| Test Type | Target | Why |
|-----------|--------|-----|
| Security modules | 95%+ | Critical security functions must be thoroughly tested |
| Core business logic | 85%+ | Main functionality needs comprehensive coverage |
| Utility functions | 70%+ | Support code needs good coverage |
| UI/Display code | 60%+ | Presentation layer has acceptable lower coverage |

### What to Test

**✅ DO Test:**
- Public APIs and exported functions
- Error handling and edge cases
- Security-critical code paths
- Integration points between modules
- Data validation logic

**❌ DON'T Test:**
- Private implementation details
- Third-party library internals
- Trivial getters/setters
- Generated code
- External services (mock instead)

---

## Best Practices

### 1. Test Independence
- Tests should not depend on execution order
- Each test should clean up after itself
- Use fresh fixtures for each test

### 2. Fast Execution
- Unit tests: < 0.1 seconds each
- Integration tests: < 1 second each
- Use mocks to avoid slow external calls

### 3. Clear Failure Messages
- Include context in assertion messages
- Show expected vs actual values
- Explain what went wrong and why it matters

### 4. Test Maintenance
- Keep tests simple and readable
- Avoid complex setup logic
- Update tests when behavior changes

### 5. Documentation
- Explain WHY test exists, not just WHAT it tests
- Document expected behavior clearly
- Link to relevant requirements or bugs

---

## Checklist for New Test Files

Before submitting a new test file, verify:

- [ ] File has proper shebang and module docstring
- [ ] All imports are organized (standard lib → third party → local)
- [ ] Test classes have descriptive names and docstrings
- [ ] All tests follow AAA pattern
- [ ] Test names are descriptive and follow convention
- [ ] Each test has a clear docstring
- [ ] setUp/tearDown handle resources properly
- [ ] All assertions include messages
- [ ] Tests are organized with section headers
- [ ] File includes run_tests() function
- [ ] Tests can be run with `python3 test_[name].py`
- [ ] All tests pass successfully
- [ ] Coverage targets are met for the module

---

## Examples

### Complete Example: Testing Path Validation

```python
#!/usr/bin/env python3
"""
Path Validation Test Suite

Tests the validate_path() function for security and correctness.

**Test Coverage:**
- Path traversal attack prevention
- System directory blocking
- URL-encoded path handling
- Valid path acceptance
- Error message clarity

**Security Focus:**
This is a CRITICAL security module. All tests must pass.
"""

import sys
import os
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.utils import validate_path


class TestPathValidationSecurity(unittest.TestCase):
    """Security tests for path validation.

    **Purpose:** Ensure path traversal attacks are blocked.
    """

    def test_blocks_parent_directory_traversal(self):
        """Test that ../ paths are blocked."""
        # Arrange
        attack_path = "../../../etc/passwd"

        # Act & Assert
        with self.assertRaises(ValueError,
                              msg="Should block parent traversal"):
            validate_path(attack_path)

    def test_blocks_url_encoded_traversal(self):
        """Test that URL-encoded ../ is blocked."""
        # Arrange
        attack_path = "%2e%2e%2f%2e%2e%2f"

        # Act & Assert
        with self.assertRaises(ValueError,
                              msg="Should block URL-encoded traversal"):
            validate_path(attack_path)

    def test_accepts_safe_path(self):
        """Test that safe paths are accepted."""
        # Arrange
        safe_path = "/home/user/safe/path"

        # Act
        result = validate_path(safe_path)

        # Assert
        self.assertTrue(result,
                       msg="Should accept safe path")


def run_tests():
    """Run all path validation tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPathValidationSecurity)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
```

---

## References

- **[TESTING.md](../TESTING.md)** - Complete testing guide
- **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - Coverage goals and measurement
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture and module responsibilities
- **[../SECURITY.md](../SECURITY.md)** - Security requirements and validation patterns
