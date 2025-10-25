#!/usr/bin/env python3
"""
Comprehensive Path Validation Tests (v3.5.1 Security Hardening)

Tests the enhanced validate_path() function to ensure it:
1. Allows absolute paths
2. Expands shell variables (~/, $HOME/, $USER/)
3. Blocks URL-encoded paths (%2e%2e%2f)
4. Blocks access to critical system directories
5. Blocks dangerous characters
6. Blocks parent directory traversal
7. Allows temp directories (legitimate use case)

This addresses security vulnerabilities identified in v3.4.1:
- validate_path() accepting URL-encoded paths
- validate_path() accepting shell expansion without validation
- validate_path() not blocking system directories
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.utils import validate_path


class TestPathValidation(unittest.TestCase):
    """Test the enhanced validate_path() function."""

    def test_valid_relative_path(self):
        """Test that valid relative paths are accepted."""
        # Should not raise
        result = validate_path("results.json", path_type="output")
        self.assertTrue(result)

        result = validate_path("data/results.json", path_type="output")
        self.assertTrue(result)

    def test_valid_absolute_path(self):
        """Test that absolute paths are allowed (per approved plan)."""
        # Should not raise, but may log warning
        result = validate_path("/tmp/test.json", path_type="output")
        self.assertTrue(result)

        result = validate_path("/Users/test/data.json", path_type="output")
        self.assertTrue(result)

    def test_shell_expansion_home_tilde(self):
        """Test that ~/path expands correctly and is validated."""
        # Should not raise - expands ~ and validates the expanded path
        result = validate_path("~/Documents/results.json", path_type="output")
        self.assertTrue(result)

    def test_shell_expansion_env_vars(self):
        """Test that $HOME and other env vars expand and are validated."""
        # Set test environment variable
        os.environ['TEST_PATH'] = '/tmp'

        try:
            # Should not raise - expands $TEST_PATH and validates
            result = validate_path("$TEST_PATH/results.json", path_type="output")
            self.assertTrue(result)
        finally:
            del os.environ['TEST_PATH']

    def test_url_encoding_blocked(self):
        """Test that URL-encoded paths are blocked."""
        # Block URL-encoded parent traversal: %2e%2e%2f = ../
        with self.assertRaises(ValueError) as cm:
            validate_path("%2e%2e%2f", path_type="output")
        self.assertIn("URL-encoded", str(cm.exception))
        self.assertIn("%", str(cm.exception))

        # Block URL-encoded null byte: %00
        with self.assertRaises(ValueError) as cm:
            validate_path("test%00.txt", path_type="output")
        self.assertIn("URL-encoded", str(cm.exception))

        # Block URL-encoded slash: %2f
        with self.assertRaises(ValueError) as cm:
            validate_path("test%2fpath.txt", path_type="output")
        self.assertIn("URL-encoded", str(cm.exception))

    def test_system_directories_blocked(self):
        """Test that critical system directories are blocked."""
        # Unix/Linux system directories
        system_paths = [
            "/etc/passwd",
            "/sys/kernel/",
            "/proc/self/",
            "/var/log/",
            "/root/.bashrc",
            "/boot/grub/",
            "/dev/null",
        ]

        for path in system_paths:
            with self.assertRaises(ValueError, msg=f"Should block: {path}") as cm:
                validate_path(path, path_type="cache directory")
            self.assertIn("system directories", str(cm.exception).lower())

    def test_macos_system_directories_blocked(self):
        """Test that macOS system directories are blocked."""
        import platform

        # Only test on macOS
        if platform.system() != "Darwin":
            self.skipTest("macOS-specific test")

        macos_paths = [
            "/System/Library/Extensions/",
            "/Library/System/Volumes/",
        ]

        for path in macos_paths:
            with self.assertRaises(ValueError, msg=f"Should block: {path}") as cm:
                validate_path(path, path_type="cache directory")
            self.assertIn("system directories", str(cm.exception).lower())

    def test_temp_directory_allowed(self):
        """Test that temp directories are allowed (legitimate use case)."""
        # Get system temp directory
        temp_dir = tempfile.gettempdir()

        # Temp paths should be allowed
        result = validate_path(f"{temp_dir}/test.json", path_type="output")
        self.assertTrue(result)

        # Create actual temp file path
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            result = validate_path(temp_path, path_type="output")
            self.assertTrue(result)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_dangerous_characters_blocked(self):
        """Test that dangerous characters are blocked."""
        # Null byte
        with self.assertRaises(ValueError) as cm:
            validate_path("test\x00.txt", path_type="output")
        self.assertIn("dangerous character", str(cm.exception).lower())

        # Pipe
        with self.assertRaises(ValueError) as cm:
            validate_path("test | cat", path_type="output")
        self.assertIn("dangerous character", str(cm.exception).lower())

        # Semicolon
        with self.assertRaises(ValueError) as cm:
            validate_path("test; rm -rf", path_type="output")
        self.assertIn("dangerous character", str(cm.exception).lower())

        # Backtick
        with self.assertRaises(ValueError) as cm:
            validate_path("test`whoami`.txt", path_type="output")
        self.assertIn("dangerous character", str(cm.exception).lower())

        # Newline
        with self.assertRaises(ValueError) as cm:
            validate_path("test\n.txt", path_type="output")
        self.assertIn("dangerous character", str(cm.exception).lower())

    def test_parent_traversal_blocked(self):
        """Test that parent directory traversal is blocked."""
        # Classic traversal
        with self.assertRaises(ValueError) as cm:
            validate_path("../../../etc/passwd", path_type="output")
        self.assertIn("..", str(cm.exception))

        # Mixed traversal
        with self.assertRaises(ValueError) as cm:
            validate_path("/tmp/../etc/passwd", path_type="output")
        self.assertIn("..", str(cm.exception))

        # Traversal in middle
        with self.assertRaises(ValueError) as cm:
            validate_path("/home/../etc/passwd", path_type="output")
        self.assertIn("..", str(cm.exception))

    def test_empty_path_blocked(self):
        """Test that empty paths are blocked."""
        with self.assertRaises(ValueError) as cm:
            validate_path("", path_type="output")
        self.assertIn("empty", str(cm.exception).lower())

    def test_error_messages_helpful(self):
        """Test that error messages are helpful and include context."""
        # URL encoding error should mention % character
        with self.assertRaises(ValueError) as cm:
            validate_path("%2e%2e%2f", path_type="cache directory")
        error_msg = str(cm.exception)
        self.assertIn("%", error_msg)
        self.assertIn("cache directory", error_msg)

        # System directory error should mention restricted access
        with self.assertRaises(ValueError) as cm:
            validate_path("/etc/passwd", path_type="extensions directory")
        error_msg = str(cm.exception)
        self.assertIn("system", error_msg.lower())
        self.assertIn("extensions directory", error_msg.lower())

    def test_shell_expansion_with_system_dir(self):
        """Test that shell expansion doesn't bypass system directory blocking."""
        # Set env var to system directory
        os.environ['EVIL_PATH'] = '/etc'

        try:
            # Should expand $EVIL_PATH to /etc and then block it
            with self.assertRaises(ValueError) as cm:
                validate_path("$EVIL_PATH/passwd", path_type="output")
            self.assertIn("system", str(cm.exception).lower())
        finally:
            del os.environ['EVIL_PATH']

    def test_path_type_parameter(self):
        """Test that path_type parameter is included in error messages."""
        # Test with different path types
        path_types = [
            "output",
            "cache directory",
            "extensions directory",
            "config file"
        ]

        for path_type in path_types:
            with self.assertRaises(ValueError) as cm:
                validate_path("/etc/passwd", path_type=path_type)
            self.assertIn(path_type, str(cm.exception).lower())


class TestPathValidationIntegration(unittest.TestCase):
    """Integration tests for path validation in actual modules."""

    def test_extension_discovery_validates_paths(self):
        """Test that ExtensionDiscovery uses path validation."""
        from vscode_scanner.extension_discovery import ExtensionDiscovery

        # URL-encoded path should be rejected
        with self.assertRaises(FileNotFoundError) as cm:
            discovery = ExtensionDiscovery(custom_dir="%2e%2e%2f")
            discovery.find_extensions_directory()
        # Error message should mention the validation failure
        self.assertIn("E300", str(cm.exception))

    def test_cache_manager_validates_paths(self):
        """Test that CacheManager uses path validation."""
        from vscode_scanner.cache_manager import CacheManager

        # URL-encoded path should be rejected
        with self.assertRaises(ValueError) as cm:
            CacheManager(cache_dir="%2e%2e%2f")
        # Error message should mention the validation failure
        self.assertIn("E200", str(cm.exception))

    def test_config_manager_validates_paths(self):
        """Test that config_manager validates path config values."""
        from vscode_scanner.config_manager import validate_config_value

        # URL-encoded path in config should be rejected
        with self.assertRaises(ValueError) as cm:
            validate_config_value('scan', 'extensions_dir', '%2e%2e%2f')
        self.assertIn("URL-encoded", str(cm.exception))

        # System directory in config should be rejected
        with self.assertRaises(ValueError) as cm:
            validate_config_value('cache', 'cache_dir', '/etc/vscan')
        self.assertIn("system", str(cm.exception).lower())


def run_tests():
    """Run all path validation tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPathValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPathValidationIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    print("=" * 70)
    print("PATH VALIDATION TESTS (v3.5.1 Security Hardening)")
    print("=" * 70)
    print()
    print("Testing enhanced validate_path() function:")
    print("- Absolute paths allowed")
    print("- Shell expansion supported")
    print("- URL encoding blocked")
    print("- System directories blocked")
    print("- Dangerous characters blocked")
    print("- Parent traversal blocked")
    print("- Temp directories allowed")
    print()
    print("=" * 70)
    print()

    sys.exit(run_tests())
