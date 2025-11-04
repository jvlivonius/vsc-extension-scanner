"""
Edge case tests for scanner.py run_scan() function

Tests error handling paths and edge cases to improve coverage from 65.16% to 75%+.
Focuses on cache initialization messages, discovery errors, empty results,
and output file handling.
"""

import unittest
import pytest
from unittest.mock import Mock, patch
import tempfile
import os


@pytest.mark.unit
class TestCacheInitializationMessages(unittest.TestCase):
    """Test cache initialization message display."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_cache_warning_plain_mode(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager_class,
    ):
        """Cache warnings display in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan
        from vscode_scanner.types import CacheWarning

        # Mock cache manager with warning
        mock_cache = Mock()
        mock_cache.get_init_messages.return_value = [
            CacheWarning(message="Cache directory created", context="init")
        ]
        mock_cache_manager_class.return_value = mock_cache

        # Mock discovery and scanning
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.return_value = {}

        # Act
        result = run_scan(plain=True, quiet=False)

        # Assert
        self.assertEqual(result, 0)
        mock_cache.get_init_messages.assert_called_once()

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_cache_error_plain_mode(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager_class,
    ):
        """Cache errors display in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan
        from vscode_scanner.types import CacheError

        # Mock cache manager with error
        mock_cache = Mock()
        mock_cache.get_init_messages.return_value = [
            CacheError(
                message="Database corrupted, recreating",
                context="init",
                recoverable=True,
            )
        ]
        mock_cache_manager_class.return_value = mock_cache

        # Mock discovery and scanning
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.return_value = {}

        # Act
        result = run_scan(plain=True, quiet=False)

        # Assert
        self.assertEqual(result, 0)
        mock_cache.get_init_messages.assert_called_once()

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_cache_info_plain_mode(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager_class,
    ):
        """Cache info messages display in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan
        from vscode_scanner.types import CacheInfo

        # Mock cache manager with info
        mock_cache = Mock()
        mock_cache.get_init_messages.return_value = [
            CacheInfo(message="Cache initialized successfully", context="init")
        ]
        mock_cache_manager_class.return_value = mock_cache

        # Mock discovery and scanning
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.return_value = {}

        # Act
        result = run_scan(plain=True, quiet=False)

        # Assert
        self.assertEqual(result, 0)
        mock_cache.get_init_messages.assert_called_once()


@pytest.mark.unit
class TestExtensionDiscoveryErrors(unittest.TestCase):
    """Test extension discovery error handling."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner.show_error_help")
    def test_discovery_generic_exception_plain(
        self, mock_show_help, mock_discover, mock_cache_manager
    ):
        """Generic discovery exceptions handled in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.side_effect = PermissionError("Access denied")

        # Act
        result = run_scan(plain=True)

        # Assert
        self.assertEqual(result, 2)
        mock_show_help.assert_called_once()


@pytest.mark.unit
class TestEmptyExtensionList(unittest.TestCase):
    """Test empty extension list handling."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._write_output_file")
    def test_empty_list_with_output_file_plain(
        self, mock_write_file, mock_discover, mock_cache_manager
    ):
        """Empty extension list saves output file in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.return_value = ([], "/path", 3)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            # Act
            result = run_scan(output=output_path, plain=True)

            # Assert
            self.assertEqual(result, 0)
            mock_write_file.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._write_output_file")
    def test_empty_list_output_write_failure_plain(
        self, mock_write_file, mock_discover, mock_cache_manager
    ):
        """Output write failure on empty list returns exit code 2 in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.return_value = ([], "/path", 4)
        mock_write_file.side_effect = IOError("Disk full")

        # Act
        result = run_scan(output="/invalid/path/output.html", plain=True)

        # Assert
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
