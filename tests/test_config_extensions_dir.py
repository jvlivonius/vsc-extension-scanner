#!/usr/bin/env python3
"""
Test suite for extensions_dir configuration option (v3.3 Feature 1).

Tests:
- Config file can store and retrieve extensions_dir
- CLI argument overrides config value
- Path expansion works (~)
- Auto-detect still works when not configured
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.config_manager import (
    load_config,
    create_default_config,
    update_config_value,
    get_config_value,
    delete_config,
    get_config_path,
    CONFIG_SCHEMA,
    DEFAULT_CONFIG,
)


class TestExtensionsDirConfigSchema(unittest.TestCase):
    """Test that extensions_dir is properly defined in config schema."""

    def test_extensions_dir_in_default_config(self):
        """Test extensions_dir exists in DEFAULT_CONFIG."""
        self.assertIn("scan", DEFAULT_CONFIG)
        self.assertIn("extensions_dir", DEFAULT_CONFIG["scan"])
        self.assertIsNone(DEFAULT_CONFIG["scan"]["extensions_dir"])

    def test_extensions_dir_in_config_schema(self):
        """Test extensions_dir exists in CONFIG_SCHEMA."""
        self.assertIn("scan", CONFIG_SCHEMA)
        self.assertIn("extensions_dir", CONFIG_SCHEMA["scan"])
        schema_entry = CONFIG_SCHEMA["scan"]["extensions_dir"]
        self.assertEqual(schema_entry[0], "path")
        self.assertIsNone(schema_entry[1])  # No min constraint
        self.assertIsNone(schema_entry[2])  # No max constraint


class TestExtensionsDirConfigOperations(unittest.TestCase):
    """Test config file operations for extensions_dir."""

    def setUp(self):
        """Set up test environment."""
        # Save original config path
        self.original_config_path = get_config_path()

        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config = Path(self.temp_dir) / ".vscanrc"

        # Monkey-patch get_config_path to use temp file
        import vscode_scanner.config_manager as cm

        self.original_get_config_path = cm.get_config_path
        cm.get_config_path = lambda: self.temp_config

    def tearDown(self):
        """Clean up test environment."""
        # Restore original get_config_path
        import vscode_scanner.config_manager as cm

        cm.get_config_path = self.original_get_config_path

        # Clean up temp files
        if self.temp_config.exists():
            self.temp_config.unlink()
        if Path(self.temp_dir).exists():
            os.rmdir(self.temp_dir)

    def test_set_and_get_extensions_dir(self):
        """Test setting and getting extensions_dir via config."""
        # Create config file
        create_default_config(force=True)

        # Set extensions_dir
        test_path = "~/custom/extensions"
        update_config_value("scan", "extensions_dir", test_path)

        # Load config and verify
        config, warnings = load_config()
        self.assertEqual(config["scan"]["extensions_dir"], test_path)
        self.assertEqual(len(warnings), 0)

    def test_extensions_dir_with_absolute_path(self):
        """Test extensions_dir with absolute path."""
        create_default_config(force=True)

        # Set absolute path
        test_path = "/absolute/path/to/extensions"
        update_config_value("scan", "extensions_dir", test_path)

        # Load and verify
        config, warnings = load_config()
        self.assertEqual(config["scan"]["extensions_dir"], test_path)

    def test_extensions_dir_defaults_to_none(self):
        """Test extensions_dir defaults to None when not set."""
        create_default_config(force=True)

        # Load config without setting extensions_dir
        config, warnings = load_config()

        # Should be None (triggering auto-detect)
        self.assertIsNone(config["scan"]["extensions_dir"])

    def test_extensions_dir_with_spaces(self):
        """Test extensions_dir with spaces in path."""
        create_default_config(force=True)

        # Set path with spaces
        test_path = "~/my documents/vscode extensions"
        update_config_value("scan", "extensions_dir", test_path)

        # Load and verify
        config, warnings = load_config()
        self.assertEqual(config["scan"]["extensions_dir"], test_path)


class TestExtensionsDirCLIIntegration(unittest.TestCase):
    """Test CLI integration with extensions_dir config."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary config
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config = Path(self.temp_dir) / ".vscanrc"

        # Monkey-patch config path
        import vscode_scanner.config_manager as cm

        self.original_get_config_path = cm.get_config_path
        cm.get_config_path = lambda: self.temp_config

    def tearDown(self):
        """Clean up test environment."""
        # Restore original
        import vscode_scanner.config_manager as cm

        cm.get_config_path = self.original_get_config_path

        # Clean up
        if self.temp_config.exists():
            self.temp_config.unlink()
        if Path(self.temp_dir).exists():
            os.rmdir(self.temp_dir)

    def test_cli_load_from_config(self):
        """Test CLI loads extensions_dir from config file."""
        # Create config with extensions_dir
        create_default_config(force=True)
        test_path = "~/test/extensions"
        update_config_value("scan", "extensions_dir", test_path)

        # Load config (simulating CLI behavior)
        config, warnings = load_config()

        # Simulate CLI logic
        extensions_dir_cli = None  # No CLI argument provided
        extensions_dir_final = extensions_dir_cli

        if (
            extensions_dir_final is None
            and config["scan"]["extensions_dir"] is not None
        ):
            extensions_dir_final = Path(config["scan"]["extensions_dir"]).expanduser()

        # Should use config value with expanded path
        self.assertIsNotNone(extensions_dir_final)
        self.assertEqual(str(extensions_dir_final), str(Path(test_path).expanduser()))

    def test_cli_override_config(self):
        """Test CLI argument overrides config file."""
        # Create config with extensions_dir
        create_default_config(force=True)
        config_path = "~/config/extensions"
        update_config_value("scan", "extensions_dir", config_path)

        # Load config
        config, warnings = load_config()

        # Simulate CLI with argument (overrides config)
        cli_path = Path("~/cli/extensions")
        extensions_dir_cli = cli_path
        extensions_dir_final = extensions_dir_cli

        if (
            extensions_dir_final is None
            and config["scan"]["extensions_dir"] is not None
        ):
            extensions_dir_final = Path(config["scan"]["extensions_dir"]).expanduser()

        # Should use CLI argument, not config
        self.assertEqual(extensions_dir_final, cli_path)

    def test_path_expansion_tilde(self):
        """Test that ~ is expanded to home directory."""
        create_default_config(force=True)
        test_path = "~/my/extensions"
        update_config_value("scan", "extensions_dir", test_path)

        # Load config
        config, warnings = load_config()

        # Simulate CLI path expansion
        if config["scan"]["extensions_dir"] is not None:
            expanded_path = Path(config["scan"]["extensions_dir"]).expanduser()

        # Should expand ~ to actual home directory
        self.assertNotIn("~", str(expanded_path))
        self.assertTrue(str(expanded_path).startswith(str(Path.home())))


class TestExtensionsDirValidation(unittest.TestCase):
    """Test validation behavior for extensions_dir."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config = Path(self.temp_dir) / ".vscanrc"

        import vscode_scanner.config_manager as cm

        self.original_get_config_path = cm.get_config_path
        cm.get_config_path = lambda: self.temp_config

    def tearDown(self):
        """Clean up test environment."""
        import vscode_scanner.config_manager as cm

        cm.get_config_path = self.original_get_config_path

        if self.temp_config.exists():
            self.temp_config.unlink()
        if Path(self.temp_dir).exists():
            os.rmdir(self.temp_dir)

    def test_lazy_validation(self):
        """Test that path validation is lazy (doesn't check existence on config set)."""
        create_default_config(force=True)

        # Set non-existent path (should succeed - lazy validation)
        nonexistent_path = "/this/path/does/not/exist/extensions"
        try:
            update_config_value("scan", "extensions_dir", nonexistent_path)
            config, warnings = load_config()
            # Should succeed - validation happens at scan time, not config time
            self.assertEqual(config["scan"]["extensions_dir"], nonexistent_path)
        except Exception as e:
            self.fail(f"Should allow non-existent path (lazy validation): {e}")

    def test_empty_string_treated_as_none(self):
        """Test that empty string is treated as None (auto-detect)."""
        create_default_config(force=True)

        # Manually set empty string in config file
        with open(self.temp_config, "a") as f:
            f.write("\nextensions_dir = \n")

        # Load config
        config, warnings = load_config()

        # Empty string should be treated as None
        self.assertIsNone(config["scan"]["extensions_dir"])


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
