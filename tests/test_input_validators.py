#!/usr/bin/env python3
"""
Input Validator Test Suite

Tests the bounded_int_validator and bounded_float_validator functions
used for CLI parameter validation.

**Test Coverage:**
- bounded_int_validator: Integer boundary validation
- bounded_float_validator: Float boundary validation
- Edge cases: Min, max, boundary values
- Error handling: Out-of-bounds values
- Error messages: Clear and actionable

**Used By:**
- CLI scan command (delay, max_retries, retry_delay, cache_max_age, workers)
- CLI cache commands (cache_max_age)
- CLI report command (cache_max_age)

**See:**
- vscode_scanner/cli.py - Validator implementations
- docs/guides/TEST_FILE_TEMPLATE.md - Test file structure standard
"""

import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import validators from CLI module
from vscode_scanner.cli import bounded_int_validator, bounded_float_validator

# Import typer for exception handling
import typer


# ============================================================
# Integer Validator Tests
# ============================================================


class TestBoundedIntValidator(unittest.TestCase):
    """Test suite for bounded_int_validator function.

    **Purpose:** Ensure integer validation works correctly for all
    CLI parameters (workers, max_retries, cache_max_age).

    **Scope:**
    - Valid integer ranges
    - Boundary conditions (min, max)
    - Out-of-bounds detection
    - Clear error messages
    """

    # ========================================
    # Happy Path Tests
    # ========================================

    def test_valid_integer_within_bounds(self):
        """Test that valid integer within bounds is accepted."""
        # Arrange
        value = 5
        min_val = 1
        max_val = 10
        name = "test_param"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(
            result, value, msg="Valid integer should be returned unchanged"
        )

    def test_minimum_boundary_value(self):
        """Test that minimum boundary value is accepted."""
        # Arrange
        value = 1  # Minimum value
        min_val = 1
        max_val = 10
        name = "test_param"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 1, msg="Minimum boundary value should be accepted")

    def test_maximum_boundary_value(self):
        """Test that maximum boundary value is accepted."""
        # Arrange
        value = 10  # Maximum value
        min_val = 1
        max_val = 10
        name = "test_param"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 10, msg="Maximum boundary value should be accepted")

    def test_returns_exact_input_value(self):
        """Test that validator returns exact input value (no modification)."""
        # Arrange
        value = 42
        min_val = 1
        max_val = 100
        name = "test_param"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertIs(result, value, msg="Should return exact same value object")

    # ========================================
    # Real CLI Parameter Tests
    # ========================================

    def test_workers_parameter_valid_range(self):
        """Test workers parameter (1-5) with valid values."""
        # Workers can be 1, 2, 3, 4, or 5
        for workers in [1, 2, 3, 4, 5]:
            with self.subTest(workers=workers):
                result = bounded_int_validator(workers, 1, 5, "workers")
                self.assertEqual(result, workers)

    def test_max_retries_parameter_valid_range(self):
        """Test max-retries parameter (0-10) with valid values."""
        # Max retries can be 0 to 10
        for retries in [0, 5, 10]:
            with self.subTest(retries=retries):
                result = bounded_int_validator(retries, 0, 10, "max-retries")
                self.assertEqual(result, retries)

    def test_cache_max_age_parameter_valid_range(self):
        """Test cache-max-age parameter (1-365) with valid values."""
        # Cache max age in days
        for days in [1, 30, 180, 365]:
            with self.subTest(days=days):
                result = bounded_int_validator(days, 1, 365, "cache-max-age")
                self.assertEqual(result, days)

    # ========================================
    # Edge Case Tests
    # ========================================

    def test_zero_as_valid_minimum(self):
        """Test that zero can be a valid minimum value."""
        # Arrange - max-retries allows 0
        value = 0
        min_val = 0
        max_val = 10
        name = "max-retries"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 0, msg="Zero should be accepted when min is 0")

    def test_single_value_range(self):
        """Test range with min == max (single valid value)."""
        # Arrange
        value = 5
        min_val = 5
        max_val = 5
        name = "test_param"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 5, msg="Should accept value when min == max")

    def test_large_valid_range(self):
        """Test validator with large range (1-1000)."""
        # Arrange
        value = 500
        min_val = 1
        max_val = 1000
        name = "test_param"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 500, msg="Should handle large ranges correctly")

    # ========================================
    # Error Handling Tests
    # ========================================

    def test_value_below_minimum_raises_error(self):
        """Test that value below minimum raises BadParameter."""
        # Arrange
        value = 0  # Below min of 1
        min_val = 1
        max_val = 5
        name = "workers"

        # Act & Assert
        with self.assertRaises(
            typer.BadParameter, msg="Should reject value below minimum"
        ):
            bounded_int_validator(value, min_val, max_val, name)

    def test_value_above_maximum_raises_error(self):
        """Test that value above maximum raises BadParameter."""
        # Arrange
        value = 6  # Above max of 5
        min_val = 1
        max_val = 5
        name = "workers"

        # Act & Assert
        with self.assertRaises(
            typer.BadParameter, msg="Should reject value above maximum"
        ):
            bounded_int_validator(value, min_val, max_val, name)

    def test_error_message_includes_parameter_name(self):
        """Test that error message includes parameter name."""
        # Arrange
        value = 100
        min_val = 1
        max_val = 10
        name = "workers"

        # Act & Assert
        with self.assertRaises(typer.BadParameter) as context:
            bounded_int_validator(value, min_val, max_val, name)

        error_message = str(context.exception)
        self.assertIn(
            "workers", error_message, msg="Error message should include parameter name"
        )

    def test_error_message_includes_valid_range(self):
        """Test that error message includes valid range."""
        # Arrange
        value = 100
        min_val = 1
        max_val = 5
        name = "workers"

        # Act & Assert
        with self.assertRaises(typer.BadParameter) as context:
            bounded_int_validator(value, min_val, max_val, name)

        error_message = str(context.exception)
        self.assertIn(
            "1", error_message, msg="Error message should include minimum value"
        )
        self.assertIn(
            "5", error_message, msg="Error message should include maximum value"
        )

    def test_workers_out_of_bounds_scenarios(self):
        """Test all out-of-bounds scenarios for workers (1-5)."""
        # Arrange - Invalid worker values
        invalid_values = [0, -1, 6, 10, 100]

        for invalid_value in invalid_values:
            with self.subTest(workers=invalid_value):
                # Act & Assert
                with self.assertRaises(
                    typer.BadParameter, msg=f"Should reject workers={invalid_value}"
                ):
                    bounded_int_validator(invalid_value, 1, 5, "workers")

    def test_cache_max_age_out_of_bounds_scenarios(self):
        """Test out-of-bounds scenarios for cache-max-age (1-365)."""
        # Arrange - Invalid cache max age values
        invalid_values = [0, -1, 366, 1000]

        for invalid_value in invalid_values:
            with self.subTest(cache_max_age=invalid_value):
                # Act & Assert
                with self.assertRaises(
                    typer.BadParameter,
                    msg=f"Should reject cache_max_age={invalid_value}",
                ):
                    bounded_int_validator(invalid_value, 1, 365, "cache-max-age")

    # ========================================
    # Negative Value Tests
    # ========================================

    def test_negative_value_rejected_when_min_positive(self):
        """Test that negative values are rejected when min is positive."""
        # Arrange
        value = -5
        min_val = 1
        max_val = 10
        name = "test_param"

        # Act & Assert
        with self.assertRaises(
            typer.BadParameter, msg="Should reject negative value when min is positive"
        ):
            bounded_int_validator(value, min_val, max_val, name)

    def test_negative_value_accepted_when_in_range(self):
        """Test that negative values are accepted if within range."""
        # Arrange
        value = -5
        min_val = -10
        max_val = 0
        name = "test_param"

        # Act
        result = bounded_int_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(
            result, -5, msg="Negative value should be accepted if within range"
        )


# ============================================================
# Float Validator Tests
# ============================================================


class TestBoundedFloatValidator(unittest.TestCase):
    """Test suite for bounded_float_validator function.

    **Purpose:** Ensure float validation works correctly for all
    CLI parameters (delay, retry_delay).

    **Scope:**
    - Valid float ranges
    - Boundary conditions (min, max)
    - Precision handling
    - Out-of-bounds detection
    - Clear error messages
    """

    # ========================================
    # Happy Path Tests
    # ========================================

    def test_valid_float_within_bounds(self):
        """Test that valid float within bounds is accepted."""
        # Arrange
        value = 5.5
        min_val = 1.0
        max_val = 10.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, value, msg="Valid float should be returned unchanged")

    def test_minimum_boundary_value(self):
        """Test that minimum boundary value is accepted."""
        # Arrange
        value = 1.0  # Minimum value
        min_val = 1.0
        max_val = 10.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 1.0, msg="Minimum boundary value should be accepted")

    def test_maximum_boundary_value(self):
        """Test that maximum boundary value is accepted."""
        # Arrange
        value = 10.0  # Maximum value
        min_val = 1.0
        max_val = 10.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 10.0, msg="Maximum boundary value should be accepted")

    def test_returns_exact_input_value(self):
        """Test that validator returns exact input value (no modification)."""
        # Arrange
        value = 3.14159
        min_val = 0.0
        max_val = 10.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertIs(result, value, msg="Should return exact same value object")

    # ========================================
    # Real CLI Parameter Tests
    # ========================================

    def test_delay_parameter_valid_range(self):
        """Test delay parameter (0.1-30.0) with valid values."""
        # Delay in seconds
        for delay in [0.1, 1.0, 5.0, 15.0, 30.0]:
            with self.subTest(delay=delay):
                result = bounded_float_validator(delay, 0.1, 30.0, "delay")
                self.assertEqual(result, delay)

    def test_retry_delay_parameter_valid_range(self):
        """Test retry-delay parameter (0.1-60.0) with valid values."""
        # Retry delay in seconds
        for retry_delay in [0.1, 1.0, 10.0, 30.0, 60.0]:
            with self.subTest(retry_delay=retry_delay):
                result = bounded_float_validator(retry_delay, 0.1, 60.0, "retry-delay")
                self.assertEqual(result, retry_delay)

    # ========================================
    # Edge Case Tests
    # ========================================

    def test_very_small_positive_float(self):
        """Test very small positive float (0.1 for delay)."""
        # Arrange
        value = 0.1  # Minimum delay
        min_val = 0.1
        max_val = 30.0
        name = "delay"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertAlmostEqual(
            result, 0.1, places=10, msg="Should handle small float values precisely"
        )

    def test_integer_as_float(self):
        """Test that integer values work as floats."""
        # Arrange
        value = 5  # Integer, but should work as float
        min_val = 1.0
        max_val = 10.0
        name = "delay"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 5, msg="Integer should be accepted as float")

    def test_high_precision_float(self):
        """Test float with high precision (many decimal places)."""
        # Arrange
        value = 3.14159265359
        min_val = 0.0
        max_val = 10.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertAlmostEqual(
            result, 3.14159265359, places=10, msg="Should preserve high precision"
        )

    def test_single_value_range(self):
        """Test range with min == max (single valid value)."""
        # Arrange
        value = 5.0
        min_val = 5.0
        max_val = 5.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 5.0, msg="Should accept value when min == max")

    def test_zero_as_boundary(self):
        """Test zero as boundary value."""
        # Arrange
        value = 0.0
        min_val = 0.0
        max_val = 10.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(result, 0.0, msg="Zero should be accepted as boundary")

    # ========================================
    # Error Handling Tests
    # ========================================

    def test_value_below_minimum_raises_error(self):
        """Test that value below minimum raises BadParameter."""
        # Arrange
        value = 0.05  # Below min of 0.1
        min_val = 0.1
        max_val = 30.0
        name = "delay"

        # Act & Assert
        with self.assertRaises(
            typer.BadParameter, msg="Should reject value below minimum"
        ):
            bounded_float_validator(value, min_val, max_val, name)

    def test_value_above_maximum_raises_error(self):
        """Test that value above maximum raises BadParameter."""
        # Arrange
        value = 31.0  # Above max of 30.0
        min_val = 0.1
        max_val = 30.0
        name = "delay"

        # Act & Assert
        with self.assertRaises(
            typer.BadParameter, msg="Should reject value above maximum"
        ):
            bounded_float_validator(value, min_val, max_val, name)

    def test_error_message_includes_parameter_name(self):
        """Test that error message includes parameter name."""
        # Arrange
        value = 100.0
        min_val = 0.1
        max_val = 30.0
        name = "delay"

        # Act & Assert
        with self.assertRaises(typer.BadParameter) as context:
            bounded_float_validator(value, min_val, max_val, name)

        error_message = str(context.exception)
        self.assertIn(
            "delay", error_message, msg="Error message should include parameter name"
        )

    def test_error_message_includes_valid_range(self):
        """Test that error message includes valid range."""
        # Arrange
        value = 100.0
        min_val = 0.1
        max_val = 30.0
        name = "delay"

        # Act & Assert
        with self.assertRaises(typer.BadParameter) as context:
            bounded_float_validator(value, min_val, max_val, name)

        error_message = str(context.exception)
        self.assertIn(
            "0.1", error_message, msg="Error message should include minimum value"
        )
        self.assertIn(
            "30", error_message, msg="Error message should include maximum value"
        )

    def test_delay_out_of_bounds_scenarios(self):
        """Test out-of-bounds scenarios for delay (0.1-30.0)."""
        # Arrange - Invalid delay values
        invalid_values = [0.0, 0.09, -1.0, 30.1, 100.0]

        for invalid_value in invalid_values:
            with self.subTest(delay=invalid_value):
                # Act & Assert
                with self.assertRaises(
                    typer.BadParameter, msg=f"Should reject delay={invalid_value}"
                ):
                    bounded_float_validator(invalid_value, 0.1, 30.0, "delay")

    def test_retry_delay_out_of_bounds_scenarios(self):
        """Test out-of-bounds scenarios for retry-delay (0.1-60.0)."""
        # Arrange - Invalid retry delay values
        invalid_values = [0.0, 0.09, -1.0, 60.1, 100.0]

        for invalid_value in invalid_values:
            with self.subTest(retry_delay=invalid_value):
                # Act & Assert
                with self.assertRaises(
                    typer.BadParameter, msg=f"Should reject retry_delay={invalid_value}"
                ):
                    bounded_float_validator(invalid_value, 0.1, 60.0, "retry-delay")

    # ========================================
    # Negative Value Tests
    # ========================================

    def test_negative_value_rejected_when_min_positive(self):
        """Test that negative values are rejected when min is positive."""
        # Arrange
        value = -5.0
        min_val = 0.1
        max_val = 30.0
        name = "delay"

        # Act & Assert
        with self.assertRaises(
            typer.BadParameter, msg="Should reject negative value when min is positive"
        ):
            bounded_float_validator(value, min_val, max_val, name)

    def test_negative_value_accepted_when_in_range(self):
        """Test that negative values are accepted if within range."""
        # Arrange
        value = -5.5
        min_val = -10.0
        max_val = 0.0
        name = "test_param"

        # Act
        result = bounded_float_validator(value, min_val, max_val, name)

        # Assert
        self.assertEqual(
            result, -5.5, msg="Negative value should be accepted if within range"
        )

    # ========================================
    # Floating Point Precision Tests
    # ========================================

    def test_boundary_with_floating_point_imprecision(self):
        """Test boundary handling with floating point imprecision."""
        # Arrange - Test value very close to boundary
        value = 30.0000000001  # Slightly above max due to float imprecision
        min_val = 0.1
        max_val = 30.0
        name = "delay"

        # This might fail or pass depending on float comparison
        # The validator uses simple < > comparison which is correct
        # Act & Assert
        with self.assertRaises(
            typer.BadParameter, msg="Should reject value slightly above maximum"
        ):
            bounded_float_validator(value, min_val, max_val, name)


# ============================================================
# Cross-Validator Consistency Tests
# ============================================================


class TestValidatorConsistency(unittest.TestCase):
    """Test consistency between int and float validators.

    **Purpose:** Ensure both validators behave consistently for
    equivalent inputs and error scenarios.
    """

    def test_error_message_format_consistency(self):
        """Test that both validators use consistent error message format."""
        # Arrange
        int_value = 100
        float_value = 100.0
        name = "test_param"

        # Act - Trigger errors from both validators
        try:
            bounded_int_validator(int_value, 1, 10, name)
            int_error = None
        except typer.BadParameter as e:
            int_error = str(e)

        try:
            bounded_float_validator(float_value, 1.0, 10.0, name)
            float_error = None
        except typer.BadParameter as e:
            float_error = str(e)

        # Assert - Both should have error messages with same structure
        self.assertIsNotNone(int_error, msg="Int validator should raise error")
        self.assertIsNotNone(float_error, msg="Float validator should raise error")

        # Both should mention parameter name and range
        self.assertIn(name, int_error)
        self.assertIn(name, float_error)
        self.assertIn("between", int_error.lower())
        self.assertIn("between", float_error.lower())

    def test_equivalent_boundary_behavior(self):
        """Test that int and float validators handle boundaries equivalently."""
        # Arrange - Test minimum boundary
        int_result = bounded_int_validator(1, 1, 10, "test")
        float_result = bounded_float_validator(1.0, 1.0, 10.0, "test")

        # Assert
        self.assertEqual(int_result, 1)
        self.assertEqual(float_result, 1.0)

        # Arrange - Test maximum boundary
        int_result = bounded_int_validator(10, 1, 10, "test")
        float_result = bounded_float_validator(10.0, 1.0, 10.0, "test")

        # Assert
        self.assertEqual(int_result, 10)
        self.assertEqual(float_result, 10.0)


# ============================================================
# Test Suite Runner
# ============================================================


def run_tests():
    """Run all input validator tests.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBoundedIntValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundedFloatValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestValidatorConsistency))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Input Validator Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
