#!/usr/bin/env python3
"""
Comprehensive Path Validation Tests (v5.0.2 - Further Optimized)

Tests the enhanced validate_path() function to ensure it:
1. Allows absolute paths
2. Expands shell variables (~/, $HOME/, $USER/)
3. Blocks URL-encoded paths (%2e%2e%2f)
4. Blocks access to critical system directories
5. Blocks dangerous characters
6. Blocks parent directory traversal
7. Allows temp directories (legitimate use case)

v3.7.0 Phase 3: Initial parametrization
v5.0.2: Further consolidation and optimization
"""

import sys
import os
import tempfile
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.utils import validate_path


@pytest.mark.security
class TestPathValidation:
    """Test the enhanced validate_path() function."""

    @pytest.mark.parametrize(
        "valid_path,description",
        [
            # Relative paths
            ("results.json", "simple relative path"),
            ("data/results.json", "relative path with subdirectory"),
            # Absolute paths
            ("/tmp/test.json", "absolute path to /tmp"),
            ("/Users/test/data.json", "absolute path to user directory"),
            # Shell expansion
            ("~/Documents/results.json", "tilde expansion"),
        ],
    )
    def test_valid_paths(self, valid_path, description):
        """Test that valid paths are accepted (relative, absolute, shell expansion)."""
        result = validate_path(valid_path, path_type="output")
        assert result is True, f"Failed: {description}"

    def test_shell_expansion_env_vars(self):
        """Test that $HOME and other env vars expand and are validated."""
        # Set test environment variable
        os.environ["TEST_PATH"] = "/tmp"

        try:
            # Should not raise - expands $TEST_PATH and validates
            result = validate_path("$TEST_PATH/results.json", path_type="output")
            assert result is True
        finally:
            del os.environ["TEST_PATH"]

    @pytest.mark.parametrize(
        "malicious_path,attack_description",
        [
            # URL-encoded traversal
            ("%2e%2e%2f", "url_encoded_parent_traversal"),
            ("%2e%2e%2f%2e%2e%2f", "double_url_encoded_traversal"),
            # URL-encoded null byte
            ("test%00.txt", "url_encoded_null_byte"),
            # URL-encoded slash
            ("test%2fpath.txt", "url_encoded_slash"),
            # URL-encoded system paths
            ("%2fetc%2fpasswd", "url_encoded_etc_passwd"),
        ],
        ids=lambda x: x[1] if isinstance(x, tuple) else str(x),
    )
    def test_url_encoding_blocked(self, malicious_path, attack_description):
        """
        Test that URL-encoded paths are blocked.

        This parameterized test provides better test output with descriptive test IDs.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_path(malicious_path, path_type="output")
        assert "URL-encoded" in str(exc_info.value)

    @pytest.mark.parametrize(
        "system_path",
        [
            "/etc/passwd",
            "/sys/kernel/",
            "/proc/self/",
            "/var/log/",
            "/root/.bashrc",
            "/boot/grub/",
            "/dev/null",
        ],
    )
    def test_system_directories_blocked(self, system_path):
        """
        Test that critical system directories are blocked.

        Parameterized to test all Unix/Linux system paths individually
        with clear test output for each path.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_path(system_path, path_type="cache directory")
        assert "system directories" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "system_path_case_variation",
        [
            "/Sys",  # The exact case that triggered property test failure
            "/SYS",  # All uppercase
            "/sYs",  # Mixed case
            "/Etc/passwd",  # Mixed case etc
            "/ETC/passwd",  # All uppercase etc
            "/Proc/self",  # Capital P proc
            "/PROC/self",  # All uppercase proc
            "/Var/log",  # Capital V var
            "/Root/.bashrc",  # Capital R root
            "/Boot/grub",  # Capital B boot
            "/Dev/null",  # Capital D dev
        ],
    )
    def test_system_directories_case_insensitive_blocked(
        self, system_path_case_variation
    ):
        """
        Test that system directories are blocked with case variations.

        Security Fix (v3.5.5): Prevent bypassing system path restrictions
        on case-insensitive filesystems (macOS, Windows) using mixed case
        like /Sys, /ETC, /Proc.

        This test addresses the vulnerability found by property-based testing
        where /Sys (capital S) was not blocked on case-insensitive filesystems.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_path(system_path_case_variation, path_type="cache directory")
        assert "system directories" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "macos_system_path",
        [
            "/System/Library/Extensions/",
            "/Library/System/Volumes/",
        ],
    )
    def test_macos_system_directories_blocked(self, macos_system_path):
        """Test that macOS system directories are blocked."""
        import platform

        # Only test on macOS
        if platform.system() != "Darwin":
            pytest.skip("macOS-specific test")

        with pytest.raises(ValueError) as exc_info:
            validate_path(macos_system_path, path_type="cache directory")
        assert "system directories" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "macos_case_variation",
        [
            "/SYSTEM/Library/Extensions/",  # All uppercase
            "/system/Library/Extensions/",  # All lowercase
            "/SyStEm/Library/Extensions/",  # Mixed case
            "/System/LIBRARY/Extensions/",  # Library uppercase
            "/LIBRARY/System/Volumes/",  # Library uppercase
        ],
    )
    def test_macos_system_directories_case_insensitive_blocked(
        self, macos_case_variation
    ):
        """
        Test that macOS system directories are blocked with case variations.

        Security Fix (v3.5.5): macOS APFS/HFS+ with default case-insensitive
        settings allows /SYSTEM and /System to access the same directory.
        """
        import platform

        # Only test on macOS
        if platform.system() != "Darwin":
            pytest.skip("macOS-specific test")

        with pytest.raises(ValueError) as exc_info:
            validate_path(macos_case_variation, path_type="cache directory")
        assert "system directories" in str(exc_info.value).lower()

    def test_temp_directory_allowed(self):
        """Test that temp directories are allowed (legitimate use case)."""
        # Get system temp directory
        temp_dir = tempfile.gettempdir()

        # Temp paths should be allowed
        result = validate_path(f"{temp_dir}/test.json", path_type="output")
        assert result is True

        # Create actual temp file path
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            result = validate_path(temp_path, path_type="output")
            assert result is True
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.parametrize(
        "dangerous_path,dangerous_char_description",
        [
            # Null byte
            ("test\x00.txt", "null_byte"),
            # Pipe
            ("test | cat", "pipe"),
            # Semicolon
            ("test; rm -rf", "semicolon"),
            # Backtick
            ("test`whoami`.txt", "backtick"),
            # Newline
            ("test\n.txt", "newline"),
            # Carriage return
            ("test\r.txt", "carriage_return"),
        ],
        ids=lambda x: x[1] if isinstance(x, tuple) else str(x),
    )
    def test_dangerous_characters_blocked(
        self, dangerous_path, dangerous_char_description
    ):
        """
        Test that dangerous characters are blocked.

        Parameterized to test all dangerous characters individually
        for better test output clarity.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_path(dangerous_path, path_type="output")
        assert "dangerous character" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "traversal_path,traversal_type",
        [
            # Classic traversal
            ("../../../etc/passwd", "classic_traversal"),
            # Mixed traversal
            ("/tmp/../etc/passwd", "mixed_traversal"),
            # Traversal in middle
            ("/home/../etc/passwd", "middle_traversal"),
            # Multiple parent references
            ("../../..", "multiple_parent_refs"),
            # Dot-dot at start
            ("../data.json", "dotdot_at_start"),
        ],
        ids=lambda x: x[1] if isinstance(x, tuple) else str(x),
    )
    def test_parent_traversal_blocked(self, traversal_path, traversal_type):
        """
        Test that parent directory traversal is blocked.

        Parameterized to test all traversal patterns individually
        for better test output and maintainability.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_path(traversal_path, path_type="output")
        assert ".." in str(exc_info.value)

    def test_empty_path_blocked(self):
        """Test that empty paths are blocked."""
        with pytest.raises(ValueError) as exc_info:
            validate_path("", path_type="output")
        assert "empty" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "malicious_path,path_type,expected_error_content",
        [
            # URL encoding error
            ("%2e%2e%2f", "cache directory", ["%", "cache directory"]),
            # System directory error
            ("/etc/passwd", "extensions directory", ["system", "extensions directory"]),
            # Dangerous character error
            ("test\x00.txt", "output", ["dangerous", "output"]),
            # Parent traversal error
            ("../etc/passwd", "config file", ["..", "config file"]),
        ],
        ids=["url_encoding", "system_dir", "dangerous_char", "parent_traversal"],
    )
    def test_error_messages_helpful(
        self, malicious_path, path_type, expected_error_content
    ):
        """Test that error messages are helpful and include context."""
        with pytest.raises(ValueError) as exc_info:
            validate_path(malicious_path, path_type=path_type)
        error_msg = str(exc_info.value).lower()
        for expected_content in expected_error_content:
            assert (
                expected_content.lower() in error_msg
            ), f"Expected '{expected_content}' in error message"

    def test_shell_expansion_with_system_dir(self):
        """Test that shell expansion doesn't bypass system directory blocking."""
        # Set env var to system directory
        os.environ["EVIL_PATH"] = "/etc"

        try:
            # Should expand $EVIL_PATH to /etc and then block it
            with pytest.raises(ValueError) as exc_info:
                validate_path("$EVIL_PATH/passwd", path_type="output")
            assert "system" in str(exc_info.value).lower()
        finally:
            del os.environ["EVIL_PATH"]

    @pytest.mark.parametrize(
        "path_type",
        [
            "output",
            "cache directory",
            "extensions directory",
            "config file",
        ],
    )
    def test_path_type_parameter(self, path_type):
        """
        Test that path_type parameter is included in error messages.

        Parameterized to test all path types individually.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_path("/etc/passwd", path_type=path_type)
        assert path_type in str(exc_info.value).lower()


@pytest.mark.security
class TestPathValidationIntegration:
    """Integration tests for path validation in actual modules."""

    def test_extension_discovery_validates_paths(self):
        """Test that ExtensionDiscovery uses path validation."""
        from vscode_scanner.extension_discovery import ExtensionDiscovery

        # URL-encoded path should be rejected
        with pytest.raises(FileNotFoundError) as exc_info:
            discovery = ExtensionDiscovery(custom_dir="%2e%2e%2f")
            discovery.find_extensions_directory()
        # Error message should mention the validation failure
        assert "E300" in str(exc_info.value)

    def test_cache_manager_validates_paths(self):
        """Test that CacheManager uses path validation."""
        from vscode_scanner.cache_manager import CacheManager

        # URL-encoded path should be rejected
        with pytest.raises(ValueError) as exc_info:
            CacheManager(cache_dir="%2e%2e%2f")
        # Error message should mention the validation failure
        assert "E200" in str(exc_info.value)

    def test_config_manager_validates_paths(self):
        """Test that config_manager validates path config values."""
        from vscode_scanner.config_manager import validate_config_value

        # URL-encoded path in config should be rejected
        with pytest.raises(ValueError) as exc_info:
            validate_config_value("scan", "extensions_dir", "%2e%2e%2f")
        assert "URL-encoded" in str(exc_info.value)

        # System directory in config should be rejected
        with pytest.raises(ValueError) as exc_info:
            validate_config_value("cache", "cache_dir", "/etc/vscan")
        assert "system" in str(exc_info.value).lower()


if __name__ == "__main__":
    print("=" * 70)
    print("PATH VALIDATION TESTS (v5.0.2 - Further Optimized)")
    print("=" * 70)
    print()
    print("Testing enhanced validate_path() function:")
    print("- Absolute paths allowed")
    print("- Shell expansion supported")
    print("- URL encoding blocked (parametrized)")
    print("- System directories blocked (parametrized)")
    print("- Dangerous characters blocked (parametrized)")
    print("- Parent traversal blocked (parametrized)")
    print("- Temp directories allowed")
    print()
    print("=" * 70)
    print()

    # Run with pytest
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
