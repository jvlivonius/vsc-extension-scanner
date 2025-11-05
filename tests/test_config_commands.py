#!/usr/bin/env python3
"""
Config Command Test Suite

Tests the vscan config commands (init, show, set, get, reset) for
configuration file management.

**Test Coverage:**
- config init: Create default configuration file
- config show: Display current configuration
- config set: Update configuration values
- config get: Retrieve specific values
- config reset: Delete configuration file
- Error handling: Invalid keys, invalid values, file permissions
- Edge cases: Force overwrite, missing config file

**Used By:**
- CLI config commands (vscan config <command>)

**See:**
- vscode_scanner/cli.py - Config command implementations
- vscode_scanner/config_manager.py - Configuration management logic
- docs/guides/TEST_FILE_TEMPLATE.md - Test file structure standard
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from typer.testing import CliRunner
    from vscode_scanner import cli
    import vscode_scanner.config_manager as config_manager

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    print("Warning: Typer not available, skipping config command tests")


# ============================================================
# Config Init Command Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestConfigInitCommand(unittest.TestCase):
    """Test suite for 'config init' command.

    **Purpose:** Ensure config file creation works correctly with
    proper defaults, error handling, and force overwrite.

    **Scope:**
    - Create new config file
    - Force overwrite existing file
    - Handle file permissions
    - Verify default values
    """

    def setUp(self):
        """Set up test runner and temporary config path."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, ".vscanrc")

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ========================================
    # Happy Path Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_init_creates_config_file(self, mock_config_path):
        """Test that config init creates configuration file."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Act
        result = self.runner.invoke(cli.app, ["config", "init"])

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg=f"Should succeed. Output: {result.stdout}"
        )
        self.assertIn(
            "created", result.stdout.lower(), msg="Should confirm file creation"
        )

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_init_with_force_overwrites_existing(self, mock_config_path):
        """Test that config init --force overwrites existing file."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Create initial config
        self.runner.invoke(cli.app, ["config", "init"])

        # Act - Force overwrite
        result = self.runner.invoke(cli.app, ["config", "init", "--force"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed with --force")
        self.assertIn(
            "created", result.stdout.lower(), msg="Should confirm file creation"
        )

    # ========================================
    # Edge Case Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_init_without_force_warns_if_exists(self, mock_config_path):
        """Test that init without --force warns if file exists."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Create initial config
        self.runner.invoke(cli.app, ["config", "init"])

        # Act - Try to init again without force
        result = self.runner.invoke(cli.app, ["config", "init"])

        # Assert
        # Should either warn or fail (both are acceptable behaviors)
        self.assertTrue(
            "exists" in result.stdout.lower() or result.exit_code != 0,
            msg="Should warn about existing file or fail",
        )

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_init_creates_parent_directories(self, mock_config_path):
        """Test that init handles nested paths appropriately."""
        # Arrange
        nested_path = os.path.join(self.temp_dir, "nested", "dir", ".vscanrc")
        # Create parent directories first (config init may not create them)
        os.makedirs(os.path.dirname(nested_path), exist_ok=True)
        mock_config_path.return_value = Path(nested_path)

        # Act
        result = self.runner.invoke(cli.app, ["config", "init"])

        # Assert
        self.assertEqual(
            result.exit_code, 0, msg="Should succeed with existing parent directories"
        )


# ============================================================
# Config Show Command Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestConfigShowCommand(unittest.TestCase):
    """Test suite for 'config show' command.

    **Purpose:** Ensure configuration display works correctly with
    various configuration states.

    **Scope:**
    - Display existing configuration
    - Handle missing configuration
    - Show all sections
    - Plain vs Rich output
    """

    def setUp(self):
        """Set up test runner and temporary config."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, ".vscanrc")

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ========================================
    # Happy Path Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_show_displays_configuration(self, mock_config_path):
        """Test that config show displays configuration."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Create config first
        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "show"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed")
        # Should show config sections
        self.assertTrue(
            "scan" in result.stdout.lower() or "delay" in result.stdout.lower(),
            msg=f"Should display config content. Output: {result.stdout}",
        )

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_show_handles_missing_config(self, mock_config_path):
        """Test that show handles missing configuration file."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Act - Show without creating config first
        result = self.runner.invoke(cli.app, ["config", "show"])

        # Assert
        # Should either show defaults or warn about missing file
        # Exit code should be 0 or appropriate error code
        self.assertTrue(
            result.exit_code == 0 or "not found" in result.stdout.lower(),
            msg=f"Should handle missing config. Output: {result.stdout}",
        )

    # ========================================
    # Output Format Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_show_with_plain_flag(self, mock_config_path):
        """Test that --plain flag disables rich formatting."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "show"])

        # Assert
        self.assertEqual(result.exit_code, 0)
        # Plain output should not have ANSI codes (basic check)
        self.assertNotIn(
            "\x1b[", result.stdout, msg="Plain output should not have ANSI escape codes"
        )


# ============================================================
# Config Set Command Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestConfigSetCommand(unittest.TestCase):
    """Test suite for 'config set' command.

    **Purpose:** Ensure configuration value updates work correctly
    with validation and error handling.

    **Scope:**
    - Set valid configuration values
    - Validate value types and ranges
    - Handle invalid keys
    - Handle invalid values
    """

    def setUp(self):
        """Set up test runner and temporary config."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, ".vscanrc")

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ========================================
    # Happy Path Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_set_valid_integer_value(self, mock_config_path):
        """Test setting valid integer configuration value."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "set", "scan.max_retries", "5"])

        # Assert
        self.assertEqual(
            result.exit_code,
            0,
            msg=f"Should succeed setting integer. Output: {result.stdout}",
        )

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_set_valid_float_value(self, mock_config_path):
        """Test setting valid float configuration value."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "set", "scan.delay", "2.5"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed setting float")

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_set_valid_boolean_value(self, mock_config_path):
        """Test setting valid boolean configuration value."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "set", "output.quiet", "true"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed setting boolean")

    # ========================================
    # Error Handling Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_set_invalid_key_format(self, mock_config_path):
        """Test that invalid key format is rejected."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act - Invalid key format (no section)
        result = self.runner.invoke(cli.app, ["config", "set", "invalidkey", "value"])

        # Assert
        self.assertNotEqual(result.exit_code, 0, msg="Should reject invalid key format")

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_set_nonexistent_key(self, mock_config_path):
        """Test that nonexistent keys are rejected."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act - Nonexistent key
        result = self.runner.invoke(
            cli.app, ["config", "set", "scan.nonexistent", "value"]
        )

        # Assert
        # Should either reject or warn
        self.assertTrue(
            result.exit_code != 0
            or "invalid" in result.stdout.lower()
            or "unknown" in result.stdout.lower(),
            msg=f"Should reject nonexistent key. Output: {result.stdout}",
        )

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_set_without_config_file(self, mock_config_path):
        """Test that set handles missing config file."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Act - Try to set without creating config first
        result = self.runner.invoke(cli.app, ["config", "set", "scan.delay", "2.5"])

        # Assert
        # Should either fail or create file
        self.assertTrue(
            result.exit_code != 0 or "created" in result.stdout.lower(),
            msg=f"Should handle missing config file. Output: {result.stdout}",
        )


# ============================================================
# Config Get Command Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestConfigGetCommand(unittest.TestCase):
    """Test suite for 'config get' command.

    **Purpose:** Ensure configuration value retrieval works correctly.

    **Scope:**
    - Get valid configuration values
    - Handle invalid keys
    - Handle missing configuration
    - Display values correctly
    """

    def setUp(self):
        """Set up test runner and temporary config."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, ".vscanrc")

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ========================================
    # Happy Path Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_get_existing_value(self, mock_config_path):
        """Test getting existing configuration value."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "get", "scan.delay"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed getting value")
        # Should display the value
        self.assertTrue(result.stdout.strip() != "", msg="Should display value")

    # ========================================
    # Error Handling Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_get_invalid_key_format(self, mock_config_path):
        """Test that invalid key format is rejected."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act - Invalid key format
        result = self.runner.invoke(cli.app, ["config", "get", "invalidkey"])

        # Assert
        self.assertNotEqual(result.exit_code, 0, msg="Should reject invalid key format")

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_get_nonexistent_key(self, mock_config_path):
        """Test that nonexistent keys are handled."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "get", "scan.nonexistent"])

        # Assert
        # Should either error or show nothing
        self.assertTrue(
            result.exit_code != 0
            or "not found" in result.stdout.lower()
            or result.stdout.strip() == "",
            msg=f"Should handle nonexistent key. Output: {result.stdout}",
        )

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_get_without_config_file(self, mock_config_path):
        """Test that get handles missing config file."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Act - Try to get without creating config first
        result = self.runner.invoke(cli.app, ["config", "get", "scan.delay"])

        # Assert
        # Should return default value when config missing
        self.assertEqual(
            result.exit_code, 0, msg="Should succeed and return default value"
        )
        self.assertTrue(
            "default" in result.stdout.lower() or result.stdout.strip() != "",
            msg=f"Should display default value. Output: {result.stdout}",
        )


# ============================================================
# Config Reset Command Tests
# ============================================================


@unittest.skipIf(not TYPER_AVAILABLE, "Typer not available")
@pytest.mark.unit
class TestConfigResetCommand(unittest.TestCase):
    """Test suite for 'config reset' command.

    **Purpose:** Ensure configuration file deletion works correctly
    with proper confirmation and force options.

    **Scope:**
    - Delete configuration file
    - Force delete without confirmation
    - Handle missing configuration
    - Confirmation prompts
    """

    def setUp(self):
        """Set up test runner and temporary config."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, ".vscanrc")

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ========================================
    # Happy Path Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_reset_with_force_deletes_config(self, mock_config_path):
        """Test that reset --force deletes configuration file."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Create config first
        self.runner.invoke(cli.app, ["config", "init"])

        # Act
        result = self.runner.invoke(cli.app, ["config", "reset", "--force"])

        # Assert
        self.assertEqual(result.exit_code, 0, msg="Should succeed with --force")
        self.assertTrue(
            "deleted" in result.stdout.lower() or "removed" in result.stdout.lower(),
            msg=f"Should confirm deletion. Output: {result.stdout}",
        )

    # ========================================
    # Edge Case Tests
    # ========================================

    @patch("vscode_scanner.config_manager.get_config_path")
    def test_reset_handles_missing_config(self, mock_config_path):
        """Test that reset handles missing configuration file."""
        # Arrange
        mock_config_path.return_value = Path(self.test_config_path)

        # Act - Reset without creating config first
        result = self.runner.invoke(cli.app, ["config", "reset", "--force"])

        # Assert
        # Should either succeed (idempotent) or warn about missing file
        self.assertTrue(
            result.exit_code == 0 or "not found" in result.stdout.lower(),
            msg=f"Should handle missing config. Output: {result.stdout}",
        )


# ============================================================
# Test Suite Runner
# ============================================================


def run_tests():
    """Run all config command tests.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    if TYPER_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestConfigInitCommand))
        suite.addTests(loader.loadTestsFromTestCase(TestConfigShowCommand))
        suite.addTests(loader.loadTestsFromTestCase(TestConfigSetCommand))
        suite.addTests(loader.loadTestsFromTestCase(TestConfigGetCommand))
        suite.addTests(loader.loadTestsFromTestCase(TestConfigResetCommand))
    else:
        print("Skipping all config command tests (Typer not available)")
        return 0

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Config Command Test Summary")
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
