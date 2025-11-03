"""
Output generation error tests for scanner.py

Tests output generation error handling to improve coverage from 69.93% to 75%+.
Focuses on _generate_output() exceptions in run_scan().
"""

import unittest
from unittest.mock import Mock, patch


class TestOutputGenerationErrors(unittest.TestCase):
    """Test output generation exception handling."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner.show_error_help")
    def test_output_generation_exception_plain(
        self,
        mock_show_help,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager,
    ):
        """Output generation exceptions handled in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
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
        mock_generate_output.side_effect = ValueError("Invalid output format")

        # Act
        result = run_scan(plain=True)

        # Assert
        self.assertEqual(result, 2)
        mock_show_help.assert_called_once()

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner.show_error_help")
    def test_output_generation_exception_rich(
        self,
        mock_show_help,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager,
    ):
        """Output generation exceptions handled in rich mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
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
        mock_generate_output.side_effect = KeyError("missing_field")

        # Act
        result = run_scan(plain=False)

        # Assert
        self.assertEqual(result, 2)
        mock_show_help.assert_called_once()


if __name__ == "__main__":
    unittest.main()
