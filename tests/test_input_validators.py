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
import pytest
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


@pytest.mark.unit
class TestBoundedIntValidator:
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
    # Happy Path Tests (Parametrized)
    # ========================================

    @pytest.mark.parametrize(
        "value,min_val,max_val,name,expected,description",
        [
            # Valid values within bounds
            (5, 1, 10, "test_param", 5, "valid integer within bounds"),
            (1, 1, 10, "test_param", 1, "minimum boundary value"),
            (10, 1, 10, "test_param", 10, "maximum boundary value"),
            (42, 1, 100, "test_param", 42, "returns exact input value"),
            # Zero as valid minimum
            (0, 0, 10, "max-retries", 0, "zero as valid minimum"),
            # Single value range
            (5, 5, 5, "test_param", 5, "single value range (min == max)"),
            # Large valid range
            (500, 1, 1000, "test_param", 500, "large valid range"),
            # Negative values within range
            (-5, -10, 0, "test_param", -5, "negative value within range"),
        ],
    )
    def test_valid_values(self, value, min_val, max_val, name, expected, description):
        """Test that valid integers are accepted and returned unchanged."""
        result = bounded_int_validator(value, min_val, max_val, name)
        assert result == expected, f"Failed: {description}"

    def test_returns_exact_same_object(self):
        """Test that validator returns exact same value object (identity check)."""
        value = 42
        result = bounded_int_validator(value, 1, 100, "test_param")
        assert result is value, "Should return exact same value object"

    # ========================================
    # Real CLI Parameter Tests (Parametrized)
    # ========================================

    @pytest.mark.parametrize(
        "param_name,min_val,max_val,valid_values",
        [
            ("workers", 1, 5, [1, 2, 3, 4, 5]),
            ("max-retries", 0, 10, [0, 5, 10]),
            ("cache-max-age", 1, 365, [1, 30, 180, 365]),
        ],
    )
    def test_cli_parameters_valid_ranges(
        self, param_name, min_val, max_val, valid_values
    ):
        """Test real CLI parameters with their actual valid ranges."""
        for value in valid_values:
            result = bounded_int_validator(value, min_val, max_val, param_name)
            assert result == value, f"{param_name}={value} should be accepted"

    # ========================================
    # Error Handling Tests (Parametrized)
    # ========================================

    @pytest.mark.parametrize(
        "value,min_val,max_val,name,description",
        [
            # Below minimum
            (0, 1, 5, "workers", "value below minimum"),
            (-1, 0, 10, "max-retries", "negative below zero minimum"),
            # Above maximum
            (6, 1, 5, "workers", "value above maximum"),
            (366, 1, 365, "cache-max-age", "value above maximum"),
            # Negative when min is positive
            (-5, 1, 10, "test_param", "negative value when min positive"),
        ],
    )
    def test_out_of_bounds_raises_error(
        self, value, min_val, max_val, name, description
    ):
        """Test that out-of-bounds values raise BadParameter."""
        with pytest.raises(typer.BadParameter):
            bounded_int_validator(value, min_val, max_val, name)

    def test_error_message_includes_parameter_name(self):
        """Test that error message includes parameter name."""
        with pytest.raises(typer.BadParameter) as exc_info:
            bounded_int_validator(100, 1, 10, "workers")

        error_message = str(exc_info.value)
        assert "workers" in error_message, "Error message should include parameter name"

    def test_error_message_includes_valid_range(self):
        """Test that error message includes valid range."""
        with pytest.raises(typer.BadParameter) as exc_info:
            bounded_int_validator(100, 1, 5, "workers")

        error_message = str(exc_info.value)
        assert "1" in error_message, "Error message should include minimum value"
        assert "5" in error_message, "Error message should include maximum value"

    @pytest.mark.parametrize(
        "invalid_value,min_val,max_val,param_name",
        [
            # Workers out-of-bounds (1-5)
            (0, 1, 5, "workers"),
            (-1, 1, 5, "workers"),
            (6, 1, 5, "workers"),
            (10, 1, 5, "workers"),
            (100, 1, 5, "workers"),
            # Cache max age out-of-bounds (1-365)
            (0, 1, 365, "cache-max-age"),
            (-1, 1, 365, "cache-max-age"),
            (366, 1, 365, "cache-max-age"),
            (1000, 1, 365, "cache-max-age"),
        ],
    )
    def test_cli_parameters_out_of_bounds(
        self, invalid_value, min_val, max_val, param_name
    ):
        """Test all out-of-bounds scenarios for real CLI parameters."""
        with pytest.raises(typer.BadParameter):
            bounded_int_validator(invalid_value, min_val, max_val, param_name)


# ============================================================
# Float Validator Tests
# ============================================================


@pytest.mark.unit
class TestBoundedFloatValidator:
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
    # Happy Path Tests (Parametrized)
    # ========================================

    @pytest.mark.parametrize(
        "value,min_val,max_val,name,expected,description",
        [
            # Valid values within bounds
            (5.5, 1.0, 10.0, "test_param", 5.5, "valid float within bounds"),
            (1.0, 1.0, 10.0, "test_param", 1.0, "minimum boundary value"),
            (10.0, 1.0, 10.0, "test_param", 10.0, "maximum boundary value"),
            (3.14159, 0.0, 10.0, "test_param", 3.14159, "returns exact input value"),
            # Edge cases
            (0.1, 0.1, 30.0, "delay", 0.1, "very small positive float"),
            (5, 1.0, 10.0, "delay", 5, "integer as float"),
            (
                3.14159265359,
                0.0,
                10.0,
                "test_param",
                3.14159265359,
                "high precision float",
            ),
            (5.0, 5.0, 5.0, "test_param", 5.0, "single value range (min == max)"),
            (0.0, 0.0, 10.0, "test_param", 0.0, "zero as boundary"),
            # Negative values within range
            (-5.5, -10.0, 0.0, "test_param", -5.5, "negative value within range"),
        ],
    )
    def test_valid_values(self, value, min_val, max_val, name, expected, description):
        """Test that valid floats are accepted and returned unchanged."""
        result = bounded_float_validator(value, min_val, max_val, name)
        # Use approximate equality for float comparison
        if isinstance(expected, float):
            assert abs(result - expected) < 1e-10, f"Failed: {description}"
        else:
            assert result == expected, f"Failed: {description}"

    def test_returns_exact_same_object(self):
        """Test that validator returns exact same value object (identity check)."""
        value = 3.14159
        result = bounded_float_validator(value, 0.0, 10.0, "test_param")
        assert result is value, "Should return exact same value object"

    # ========================================
    # Real CLI Parameter Tests (Parametrized)
    # ========================================

    @pytest.mark.parametrize(
        "param_name,min_val,max_val,valid_values",
        [
            ("delay", 0.1, 30.0, [0.1, 1.0, 5.0, 15.0, 30.0]),
            ("retry-delay", 0.1, 60.0, [0.1, 1.0, 10.0, 30.0, 60.0]),
        ],
    )
    def test_cli_parameters_valid_ranges(
        self, param_name, min_val, max_val, valid_values
    ):
        """Test real CLI parameters with their actual valid ranges."""
        for value in valid_values:
            result = bounded_float_validator(value, min_val, max_val, param_name)
            assert (
                abs(result - value) < 1e-10
            ), f"{param_name}={value} should be accepted"

    # ========================================
    # Error Handling Tests (Parametrized)
    # ========================================

    @pytest.mark.parametrize(
        "value,min_val,max_val,name,description",
        [
            # Below minimum
            (0.05, 0.1, 30.0, "delay", "value below minimum"),
            (0.0, 0.1, 60.0, "retry-delay", "zero below minimum"),
            # Above maximum
            (31.0, 0.1, 30.0, "delay", "value above maximum"),
            (60.1, 0.1, 60.0, "retry-delay", "value above maximum"),
            # Negative when min is positive
            (-5.0, 0.1, 30.0, "delay", "negative value when min positive"),
            # Floating point boundary edge case
            (
                30.0000000001,
                0.1,
                30.0,
                "delay",
                "slightly above maximum (float precision)",
            ),
        ],
    )
    def test_out_of_bounds_raises_error(
        self, value, min_val, max_val, name, description
    ):
        """Test that out-of-bounds values raise BadParameter."""
        with pytest.raises(typer.BadParameter):
            bounded_float_validator(value, min_val, max_val, name)

    def test_error_message_includes_parameter_name(self):
        """Test that error message includes parameter name."""
        with pytest.raises(typer.BadParameter) as exc_info:
            bounded_float_validator(100.0, 0.1, 30.0, "delay")

        error_message = str(exc_info.value)
        assert "delay" in error_message, "Error message should include parameter name"

    def test_error_message_includes_valid_range(self):
        """Test that error message includes valid range."""
        with pytest.raises(typer.BadParameter) as exc_info:
            bounded_float_validator(100.0, 0.1, 30.0, "delay")

        error_message = str(exc_info.value)
        assert "0.1" in error_message, "Error message should include minimum value"
        assert "30" in error_message, "Error message should include maximum value"

    @pytest.mark.parametrize(
        "invalid_value,min_val,max_val,param_name",
        [
            # Delay out-of-bounds (0.1-30.0)
            (0.0, 0.1, 30.0, "delay"),
            (0.09, 0.1, 30.0, "delay"),
            (-1.0, 0.1, 30.0, "delay"),
            (30.1, 0.1, 30.0, "delay"),
            (100.0, 0.1, 30.0, "delay"),
            # Retry delay out-of-bounds (0.1-60.0)
            (0.0, 0.1, 60.0, "retry-delay"),
            (0.09, 0.1, 60.0, "retry-delay"),
            (-1.0, 0.1, 60.0, "retry-delay"),
            (60.1, 0.1, 60.0, "retry-delay"),
            (100.0, 0.1, 60.0, "retry-delay"),
        ],
    )
    def test_cli_parameters_out_of_bounds(
        self, invalid_value, min_val, max_val, param_name
    ):
        """Test all out-of-bounds scenarios for real CLI parameters."""
        with pytest.raises(typer.BadParameter):
            bounded_float_validator(invalid_value, min_val, max_val, param_name)


# ============================================================
# Cross-Validator Consistency Tests
# ============================================================


@pytest.mark.unit
class TestValidatorConsistency:
    """Test consistency between int and float validators.

    **Purpose:** Ensure both validators behave consistently for
    equivalent inputs and error scenarios.
    """

    def test_error_message_format_consistency(self):
        """Test that both validators use consistent error message format."""
        # Trigger errors from both validators
        with pytest.raises(typer.BadParameter) as int_exc:
            bounded_int_validator(100, 1, 10, "test_param")

        with pytest.raises(typer.BadParameter) as float_exc:
            bounded_float_validator(100.0, 1.0, 10.0, "test_param")

        int_error = str(int_exc.value)
        float_error = str(float_exc.value)

        # Both should mention parameter name and range
        assert "test_param" in int_error
        assert "test_param" in float_error
        assert "between" in int_error.lower()
        assert "between" in float_error.lower()

    @pytest.mark.parametrize(
        "int_val,float_val,min_val,max_val",
        [
            (1, 1.0, 1, 10),  # Minimum boundary
            (10, 10.0, 1, 10),  # Maximum boundary
        ],
    )
    def test_equivalent_boundary_behavior(self, int_val, float_val, min_val, max_val):
        """Test that int and float validators handle boundaries equivalently."""
        int_result = bounded_int_validator(int_val, min_val, max_val, "test")
        float_result = bounded_float_validator(
            float_val, float(min_val), float(max_val), "test"
        )

        assert int_result == int_val
        assert float_result == float_val


# ============================================================
# Test Suite Runner
# ============================================================


def run_tests():
    """Run all input validator tests using pytest.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Run pytest programmatically
    return pytest.main([__file__, "-v"])


if __name__ == "__main__":
    sys.exit(run_tests())
