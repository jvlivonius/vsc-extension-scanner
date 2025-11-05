#!/usr/bin/env python3
"""
Test Suite: Config Manager Tests
Purpose: Test configuration file management and validation
Coverage: vscode_scanner.config_manager (load, validate, create, update, delete)

This test suite validates configuration management including:
- Config file loading and parsing
- Value type validation (int, float, bool, string, choice, path)
- Range validation for numeric values
- Schema versioning
- Config file operations (create, update, delete)
- Warning generation for invalid values
- Default value fallbacks
- Path validation integration

Mocking Strategy:
- Patch get_config_path() to use temporary directories
- Use real ConfigParser for authentic behavior
- Test actual file I/O to catch real-world issues
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from vscode_scanner import config_manager
from vscode_scanner.config_manager import (
    get_config_path,
    config_exists,
    load_config,
    is_valid_config_key,
    parse_config_key,
    validate_config_value,
    get_config_value,
    get_default_value,
    create_default_config,
    update_config_value,
    delete_config,
    CONFIG_SCHEMA_VERSION,
)
from vscode_scanner.types import ConfigWarning


# ============================================================
# Config Path and Existence Tests
# ============================================================


@pytest.mark.unit
class TestConfigPath(unittest.TestCase):
    """Test suite for config path operations.

    **Purpose:** Ensure config path resolution and existence
    checking works correctly.

    **Scope:**
    - get_config_path() returns correct path
    - config_exists() detects presence/absence
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.temp_dir) / ".vscanrc"

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_exists_returns_false_when_missing(self, mock_path):
        """Test that config_exists returns False when file is missing."""
        # Arrange
        mock_path.return_value = self.test_config_path

        # Act
        result = config_exists()

        # Assert
        self.assertFalse(result)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_config_exists_returns_true_when_present(self, mock_path):
        """Test that config_exists returns True when file exists."""
        # Arrange
        mock_path.return_value = self.test_config_path
        self.test_config_path.write_text("# test config")

        # Act
        result = config_exists()

        # Assert
        self.assertTrue(result)


# ============================================================
# Config Loading Tests
# ============================================================


@pytest.mark.unit
class TestConfigLoad(unittest.TestCase):
    """Test suite for config file loading.

    **Purpose:** Ensure config files are loaded correctly
    with proper validation and warning generation.

    **Scope:**
    - Load default config when file missing
    - Parse valid config files
    - Generate warnings for invalid values
    - Schema version handling
    - Merge with defaults
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.temp_dir) / ".vscanrc"

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_returns_defaults_when_no_file(self, mock_path):
        """Test that load_config returns defaults when no file exists."""
        # Arrange
        mock_path.return_value = self.test_config_path

        # Act
        config, warnings = load_config()

        # Assert
        self.assertEqual(len(warnings), 0)
        self.assertIn("scan", config)
        self.assertIn("cache", config)
        self.assertIn("output", config)
        self.assertEqual(config["scan"]["delay"], 1.5)  # DEFAULT_REQUEST_DELAY

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_parses_valid_config(self, mock_path):
        """Test that load_config parses valid config correctly."""
        # Arrange
        mock_path.return_value = self.test_config_path
        config_content = """
[_meta]
schema_version = 1

[scan]
delay = 3.0
max_retries = 5

[cache]
cache_max_age = 30

[output]
plain = true
"""
        self.test_config_path.write_text(config_content)

        # Act
        config, warnings = load_config()

        # Assert
        self.assertEqual(len(warnings), 0)
        self.assertEqual(config["scan"]["delay"], 3.0)
        self.assertEqual(config["scan"]["max_retries"], 5)
        self.assertEqual(config["cache"]["cache_max_age"], 30)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_generates_warnings_for_invalid_values(self, mock_path):
        """Test that load_config generates warnings for invalid values."""
        # Arrange
        mock_path.return_value = self.test_config_path
        config_content = """
[scan]
delay = invalid_float
max_retries = 999
"""
        self.test_config_path.write_text(config_content)

        # Act
        config, warnings = load_config()

        # Assert
        self.assertGreater(len(warnings), 0)
        # Should fall back to defaults for invalid values
        self.assertEqual(config["scan"]["delay"], 1.5)  # default

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_handles_schema_version(self, mock_path):
        """Test that load_config handles schema version correctly."""
        # Arrange
        mock_path.return_value = self.test_config_path
        config_content = f"""
[_meta]
schema_version = {CONFIG_SCHEMA_VERSION}

[scan]
delay = 2.5
"""
        self.test_config_path.write_text(config_content)

        # Act
        config, warnings = load_config()

        # Assert
        self.assertEqual(len(warnings), 0)  # Same version, no warnings

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_warns_on_schema_mismatch(self, mock_path):
        """Test that load_config warns on schema version mismatch."""
        # Arrange
        mock_path.return_value = self.test_config_path
        config_content = """
[_meta]
schema_version = 999

[scan]
delay = 2.5
"""
        self.test_config_path.write_text(config_content)

        # Act
        config, warnings = load_config()

        # Assert
        self.assertGreater(len(warnings), 0)
        # Should find "schema version mismatch" or similar in warnings
        warning_messages = [w.message.lower() for w in warnings]
        self.assertTrue(
            any("schema" in msg and "mismatch" in msg for msg in warning_messages)
        )


# ============================================================
# Value Validation Tests
# ============================================================


@pytest.mark.unit
class TestValueValidation(unittest.TestCase):
    """Test suite for config value validation.

    **Purpose:** Ensure config values are validated correctly
    with proper type checking and range validation.

    **Scope:**
    - Boolean parsing (true/false, yes/no, 1/0)
    - Integer parsing with range validation
    - Float parsing with range validation
    - String parsing
    - Choice validation
    - Path validation integration
    """

    def test_validate_bool_true_values(self):
        """Test that boolean true values are parsed correctly."""
        # Act & Assert
        for value in ["true", "TRUE", "yes", "YES", "1", "on", "ON"]:
            result = validate_config_value("output", "quiet", value)
            self.assertTrue(result, f"Failed to parse {value} as True")

    def test_validate_bool_false_values(self):
        """Test that boolean false values are parsed correctly."""
        # Act & Assert
        for value in ["false", "FALSE", "no", "NO", "0", "off", "OFF"]:
            result = validate_config_value("output", "quiet", value)
            self.assertFalse(result, f"Failed to parse {value} as False")

    def test_validate_bool_invalid_raises_error(self):
        """Test that invalid boolean values raise ValueError."""
        # Act & Assert
        with self.assertRaises(ValueError):
            validate_config_value("output", "quiet", "maybe")

    def test_validate_int_within_range(self):
        """Test that integers within range are accepted."""
        # Act
        result = validate_config_value("scan", "max_retries", "5")

        # Assert
        self.assertEqual(result, 5)

    def test_validate_int_below_minimum_raises_error(self):
        """Test that integers below minimum raise ValueError."""
        # Act & Assert
        with self.assertRaises(ValueError):
            validate_config_value("scan", "max_retries", "-1")

    def test_validate_int_above_maximum_raises_error(self):
        """Test that integers above maximum raise ValueError."""
        # Act & Assert
        with self.assertRaises(ValueError):
            validate_config_value("scan", "max_retries", "999")

    def test_validate_float_within_range(self):
        """Test that floats within range are accepted."""
        # Act
        result = validate_config_value("scan", "delay", "2.5")

        # Assert
        self.assertEqual(result, 2.5)

    def test_validate_float_below_minimum_raises_error(self):
        """Test that floats below minimum raise ValueError."""
        # Act & Assert
        with self.assertRaises(ValueError):
            validate_config_value("scan", "delay", "0.05")

    def test_validate_float_above_maximum_raises_error(self):
        """Test that floats above maximum raise ValueError."""
        # Act & Assert
        with self.assertRaises(ValueError):
            validate_config_value("scan", "delay", "100.0")

    def test_validate_choice_valid_value(self):
        """Test that valid choice values are accepted."""
        # Act
        result = validate_config_value("scan", "min_risk_level", "medium")

        # Assert
        self.assertEqual(result, "medium")

    def test_validate_choice_invalid_raises_error(self):
        """Test that invalid choice values raise ValueError."""
        # Act & Assert
        with self.assertRaises(ValueError):
            validate_config_value("scan", "min_risk_level", "extreme")

    def test_validate_string_value(self):
        """Test that string values are parsed correctly."""
        # Act
        result = validate_config_value("scan", "publisher", "microsoft")

        # Assert
        self.assertEqual(result, "microsoft")

    def test_validate_strips_inline_comments(self):
        """Test that inline comments are stripped from values."""
        # Act
        result = validate_config_value("scan", "delay", "3.0  # comment")

        # Assert
        self.assertEqual(result, 3.0)

    def test_validate_none_value(self):
        """Test that None/empty values are handled."""
        # Act
        result = validate_config_value("scan", "publisher", "none")

        # Assert
        self.assertIsNone(result)


# ============================================================
# Config Key Parsing Tests
# ============================================================


@pytest.mark.unit
class TestConfigKeyParsing(unittest.TestCase):
    """Test suite for config key parsing and validation.

    **Purpose:** Ensure config keys are validated and parsed
    correctly.

    **Scope:**
    - is_valid_config_key() validation
    - parse_config_key() parsing
    - Invalid key format handling
    """

    def test_is_valid_config_key_returns_true_for_valid(self):
        """Test that is_valid_config_key returns True for valid keys."""
        # Act & Assert
        self.assertTrue(is_valid_config_key("scan", "delay"))
        self.assertTrue(is_valid_config_key("cache", "cache_max_age"))
        self.assertTrue(is_valid_config_key("output", "quiet"))

    def test_is_valid_config_key_returns_false_for_invalid(self):
        """Test that is_valid_config_key returns False for invalid keys."""
        # Act & Assert
        self.assertFalse(is_valid_config_key("invalid", "option"))
        self.assertFalse(is_valid_config_key("scan", "unknown_option"))

    def test_parse_config_key_valid_format(self):
        """Test that parse_config_key parses valid keys correctly."""
        # Act
        section, option = parse_config_key("scan.delay")

        # Assert
        self.assertEqual(section, "scan")
        self.assertEqual(option, "delay")

    def test_parse_config_key_invalid_format_raises_error(self):
        """Test that parse_config_key raises error for invalid format."""
        # Act & Assert
        with self.assertRaises(ValueError):
            parse_config_key("nodot")

    def test_parse_config_key_unknown_key_raises_error(self):
        """Test that parse_config_key raises error for unknown keys."""
        # Act & Assert
        with self.assertRaises(ValueError):
            parse_config_key("unknown.option")


# ============================================================
# Config Operations Tests
# ============================================================


@pytest.mark.unit
class TestConfigOperations(unittest.TestCase):
    """Test suite for config file operations.

    **Purpose:** Ensure config file operations (create, update,
    delete) work correctly.

    **Scope:**
    - create_default_config() creation
    - create_default_config(force=True) overwrite
    - update_config_value() updates
    - delete_config() deletion
    - get_config_value() retrieval
    - get_default_value() defaults
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.temp_dir) / ".vscanrc"

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_create_default_config_creates_file(self, mock_path):
        """Test that create_default_config creates config file."""
        # Arrange
        mock_path.return_value = self.test_config_path

        # Act
        result_path = create_default_config()

        # Assert
        self.assertTrue(result_path.exists())
        content = result_path.read_text()
        self.assertIn("[scan]", content)
        self.assertIn("[cache]", content)
        self.assertIn("[output]", content)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_create_default_config_raises_error_if_exists(self, mock_path):
        """Test that create_default_config raises error if file exists."""
        # Arrange
        mock_path.return_value = self.test_config_path
        self.test_config_path.write_text("# existing")

        # Act & Assert
        with self.assertRaises(FileExistsError):
            create_default_config(force=False)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_create_default_config_overwrites_with_force(self, mock_path):
        """Test that create_default_config overwrites with force=True."""
        # Arrange
        mock_path.return_value = self.test_config_path
        self.test_config_path.write_text("# existing")

        # Act
        result_path = create_default_config(force=True)

        # Assert
        self.assertTrue(result_path.exists())
        content = result_path.read_text()
        self.assertIn("[scan]", content)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_update_config_value_updates_existing_file(self, mock_path):
        """Test that update_config_value updates existing config."""
        # Arrange
        mock_path.return_value = self.test_config_path
        create_default_config()

        # Act
        update_config_value("scan", "delay", "3.5")

        # Assert
        config, warnings = load_config()
        self.assertEqual(config["scan"]["delay"], 3.5)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_update_config_value_creates_file_if_missing(self, mock_path):
        """Test that update_config_value creates file if missing."""
        # Arrange
        mock_path.return_value = self.test_config_path

        # Act
        update_config_value("scan", "delay", "3.5")

        # Assert
        self.assertTrue(self.test_config_path.exists())

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_update_config_value_raises_error_for_invalid_key(self, mock_path):
        """Test that update_config_value raises error for invalid key."""
        # Arrange
        mock_path.return_value = self.test_config_path

        # Act & Assert
        with self.assertRaises(ValueError):
            update_config_value("invalid", "option", "value")

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_delete_config_removes_file(self, mock_path):
        """Test that delete_config removes config file."""
        # Arrange
        mock_path.return_value = self.test_config_path
        create_default_config()

        # Act
        result = delete_config()

        # Assert
        self.assertTrue(result)
        self.assertFalse(self.test_config_path.exists())

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_delete_config_returns_false_if_no_file(self, mock_path):
        """Test that delete_config returns False if no file exists."""
        # Arrange
        mock_path.return_value = self.test_config_path

        # Act
        result = delete_config()

        # Assert
        self.assertFalse(result)

    def test_get_config_value_returns_value_from_dict(self):
        """Test that get_config_value retrieves value from config dict."""
        # Arrange
        config = {"scan": {"delay": 3.0}, "cache": {"cache_max_age": 30}}

        # Act
        result = get_config_value(config, "scan", "delay")

        # Assert
        self.assertEqual(result, 3.0)

    def test_get_config_value_returns_none_for_missing_section(self):
        """Test that get_config_value returns None for missing section."""
        # Arrange
        config = {"scan": {"delay": 3.0}}

        # Act
        result = get_config_value(config, "unknown", "option")

        # Assert
        self.assertIsNone(result)

    def test_get_default_value_returns_default(self):
        """Test that get_default_value returns default value."""
        # Act
        result = get_default_value("scan", "delay")

        # Assert
        self.assertEqual(result, 1.5)  # DEFAULT_REQUEST_DELAY


# ============================================================
# Edge Cases Tests
# ============================================================


@pytest.mark.unit
class TestEdgeCases(unittest.TestCase):
    """Test suite for edge cases and error handling.

    **Purpose:** Ensure robust handling of edge cases,
    malformed config, and unusual input.

    **Scope:**
    - Malformed config files
    - Empty config files
    - Missing sections
    - Invalid UTF-8 encoding
    - File permission errors
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.temp_dir) / ".vscanrc"

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_handles_empty_config(self, mock_path):
        """Test that load_config handles empty config file."""
        # Arrange
        mock_path.return_value = self.test_config_path
        self.test_config_path.write_text("")

        # Act
        config, warnings = load_config()

        # Assert
        # Should return defaults
        self.assertIn("scan", config)
        self.assertEqual(config["scan"]["delay"], 1.5)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_handles_malformed_config(self, mock_path):
        """Test that load_config handles malformed config gracefully."""
        # Arrange
        mock_path.return_value = self.test_config_path
        self.test_config_path.write_text("this is not valid INI format {")

        # Act
        config, warnings = load_config()

        # Assert
        self.assertGreater(len(warnings), 0)
        # Should return defaults despite error
        self.assertIn("scan", config)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_ignores_unknown_sections(self, mock_path):
        """Test that load_config ignores unknown sections."""
        # Arrange
        mock_path.return_value = self.test_config_path
        config_content = """
[scan]
delay = 2.5

[unknown_section]
unknown_option = value
"""
        self.test_config_path.write_text(config_content)

        # Act
        config, warnings = load_config()

        # Assert
        self.assertEqual(len(warnings), 0)
        self.assertEqual(config["scan"]["delay"], 2.5)
        self.assertNotIn("unknown_section", config)

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_load_ignores_unknown_options(self, mock_path):
        """Test that load_config ignores unknown options."""
        # Arrange
        mock_path.return_value = self.test_config_path
        config_content = """
[scan]
delay = 2.5
unknown_option = value
"""
        self.test_config_path.write_text(config_content)

        # Act
        config, warnings = load_config()

        # Assert
        self.assertEqual(len(warnings), 0)
        self.assertEqual(config["scan"]["delay"], 2.5)
        self.assertNotIn("unknown_option", config["scan"])


# ============================================================
# Test Runner
# ============================================================


def run_tests():
    """Run the test suite and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigPath))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigLoad))
    suite.addTests(loader.loadTestsFromTestCase(TestValueValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigKeyParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Config Manager Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_tests())
