#!/usr/bin/env python3
"""
Test suite for failed extensions tracking and reporting (v3.3 Feature 3).

Tests:
- Error categorization (rate_limit, network_timeout, network_error, api_error)
- Error message simplification
- Failed extensions tracking during scan
- Rich mode display
- Plain mode display
- JSON output includes failed_extensions
- Empty failures (no display)
- Mixed success/failure scenarios
"""

import unittest
import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.scanner import _categorize_error, _simplify_error_message, _scan_extension_fresh
from vscode_scanner.display import display_failed_extensions
from vscode_scanner.output_formatter import OutputFormatter


class TestErrorCategorization(unittest.TestCase):
    """Test error categorization logic."""

    def test_categorize_rate_limit_error(self):
        """Test rate limit error detection."""
        error1 = "HTTP error 429: Rate limit exceeded"
        error2 = "rate limit reached"
        self.assertEqual(_categorize_error(error1), 'rate_limit')
        self.assertEqual(_categorize_error(error2), 'rate_limit')

    def test_categorize_timeout_error(self):
        """Test timeout error detection."""
        error1 = "Request timed out after 30s"
        error2 = "Connection timeout"
        self.assertEqual(_categorize_error(error1), 'network_timeout')
        self.assertEqual(_categorize_error(error2), 'network_timeout')

    def test_categorize_network_error(self):
        """Test network error detection."""
        error1 = "Network error: connection refused"
        error2 = "Connection failed"
        self.assertEqual(_categorize_error(error1), 'network_error')
        self.assertEqual(_categorize_error(error2), 'network_error')

    def test_categorize_generic_api_error(self):
        """Test generic API error categorization."""
        error1 = "API returned invalid response"
        error2 = "Failed to parse JSON"
        self.assertEqual(_categorize_error(error1), 'api_error')
        self.assertEqual(_categorize_error(error2), 'api_error')

    def test_categorize_empty_error(self):
        """Test empty error message defaults to api_error."""
        self.assertEqual(_categorize_error(""), 'api_error')
        self.assertEqual(_categorize_error(None), 'api_error')


class TestErrorMessageSimplification(unittest.TestCase):
    """Test error message simplification."""

    def test_simplify_rate_limit(self):
        """Test rate limit message simplification."""
        self.assertEqual(_simplify_error_message('rate_limit'), 'Rate limit')

    def test_simplify_network_timeout(self):
        """Test network timeout message simplification."""
        self.assertEqual(_simplify_error_message('network_timeout'), 'Network timeout')

    def test_simplify_network_error(self):
        """Test network error message simplification."""
        self.assertEqual(_simplify_error_message('network_error'), 'Network error')

    def test_simplify_api_error(self):
        """Test API error message simplification."""
        self.assertEqual(_simplify_error_message('api_error'), 'API error')

    def test_simplify_unknown_error_type(self):
        """Test unknown error type defaults to API error."""
        self.assertEqual(_simplify_error_message('unknown_type'), 'API error')


class TestFailedExtensionsTracking(unittest.TestCase):
    """Test failed extensions tracking during scan."""

    def test_track_failed_extension_in_stats(self):
        """Test that failed extensions are added to stats."""
        ext = {
            'id': 'test.extension',
            'name': 'Test Extension',
            'display_name': 'Test Extension',
            'publisher': 'test'
        }
        stats = {
            'successful_scans': 0,
            'failed_scans': 0,
            'failed_extensions': [],
            'fresh_scans': 0,
            'vulnerabilities_found': 0
        }
        scan_results = []

        # Mock API client that returns error
        mock_api_client = MagicMock()
        mock_api_client.scan_extension_with_retry.return_value = {
            'scan_status': 'error',
            'error': 'HTTP error 429: Rate limit exceeded'
        }

        # Call the function
        _scan_extension_fresh(
            ext, 'test.extension', '1.0.0', '[1/1]',
            mock_api_client, None, stats, scan_results, False
        )

        # Verify failed extension was tracked
        self.assertEqual(stats['failed_scans'], 1)
        self.assertEqual(len(stats['failed_extensions']), 1)

        failed_ext = stats['failed_extensions'][0]
        self.assertEqual(failed_ext['id'], 'test.extension')
        self.assertEqual(failed_ext['name'], 'Test Extension')
        self.assertEqual(failed_ext['error_type'], 'rate_limit')
        self.assertEqual(failed_ext['error_message'], 'Rate limit')

    def test_successful_scan_not_tracked_as_failed(self):
        """Test that successful scans are not tracked as failures."""
        ext = {
            'id': 'test.extension',
            'name': 'Test Extension',
            'display_name': 'Test Extension',
            'publisher': 'test'
        }
        stats = {
            'successful_scans': 0,
            'failed_scans': 0,
            'failed_extensions': [],
            'fresh_scans': 0,
            'vulnerabilities_found': 0
        }
        scan_results = []

        # Mock API client that returns success
        mock_api_client = MagicMock()
        mock_api_client.scan_extension_with_retry.return_value = {
            'scan_status': 'success',
            'vulnerabilities': {'count': 0}
        }

        # Call the function
        _scan_extension_fresh(
            ext, 'test.extension', '1.0.0', '[1/1]',
            mock_api_client, None, stats, scan_results, False
        )

        # Verify no failed extension was tracked
        self.assertEqual(stats['failed_scans'], 0)
        self.assertEqual(stats['successful_scans'], 1)
        self.assertEqual(len(stats['failed_extensions']), 0)


class TestFailedExtensionsDisplayRich(unittest.TestCase):
    """Test Rich mode display for failed extensions."""

    def test_display_failed_extensions_rich_single(self):
        """Test Rich display with single failed extension."""
        failed_extensions = [
            {
                'id': 'test.ext',
                'name': 'Test Extension',
                'error_type': 'rate_limit',
                'error_message': 'Rate limit'
            }
        ]

        # Capture Rich output by redirecting stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            display_failed_extensions(failed_extensions, use_rich=True)
            output = captured_output.getvalue()

            # Verify output contains expected elements
            self.assertIn('Failed to Scan', output)
            self.assertIn('Test Extension', output)
            self.assertIn('Suggestion', output)
        finally:
            sys.stdout = sys.__stdout__

    def test_display_failed_extensions_rich_multiple(self):
        """Test Rich display with multiple failed extensions."""
        failed_extensions = [
            {
                'id': 'ext1',
                'name': 'Extension 1',
                'error_type': 'rate_limit',
                'error_message': 'Rate limit'
            },
            {
                'id': 'ext2',
                'name': 'Extension 2',
                'error_type': 'network_timeout',
                'error_message': 'Network timeout'
            }
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            display_failed_extensions(failed_extensions, use_rich=True)
            output = captured_output.getvalue()

            self.assertIn('Failed to Scan (2 extensions)', output)
            self.assertIn('Extension 1', output)
            self.assertIn('Extension 2', output)
        finally:
            sys.stdout = sys.__stdout__

    def test_display_failed_extensions_rich_empty(self):
        """Test Rich display with empty failed extensions list."""
        failed_extensions = []

        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            display_failed_extensions(failed_extensions, use_rich=True)
            output = captured_output.getvalue()

            # Should not output anything for empty list
            self.assertEqual(output, '')
        finally:
            sys.stdout = sys.__stdout__


class TestFailedExtensionsDisplayPlain(unittest.TestCase):
    """Test Plain mode display for failed extensions."""

    def test_display_failed_extensions_plain_single(self):
        """Test Plain display with single failed extension."""
        failed_extensions = [
            {
                'id': 'test.ext',
                'name': 'Test Extension',
                'error_type': 'api_error',
                'error_message': 'API error'
            }
        ]

        # Capture plain output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            display_failed_extensions(failed_extensions, use_rich=False)
            output = captured_output.getvalue()

            # Verify output contains expected elements
            self.assertIn('Failed to Scan (1 extension)', output)
            self.assertIn('Test Extension - API error', output)
            self.assertIn('Suggestion', output)
        finally:
            sys.stdout = sys.__stdout__

    def test_display_failed_extensions_plain_multiple(self):
        """Test Plain display with multiple failed extensions."""
        failed_extensions = [
            {
                'id': 'ext1',
                'name': 'Extension One',
                'error_type': 'rate_limit',
                'error_message': 'Rate limit'
            },
            {
                'id': 'ext2',
                'name': 'Extension Two',
                'error_type': 'network_error',
                'error_message': 'Network error'
            }
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            display_failed_extensions(failed_extensions, use_rich=False)
            output = captured_output.getvalue()

            self.assertIn('Failed to Scan (2 extensions)', output)
            self.assertIn('Extension One - Rate limit', output)
            self.assertIn('Extension Two - Network error', output)
        finally:
            sys.stdout = sys.__stdout__

    def test_display_failed_extensions_plain_empty(self):
        """Test Plain display with empty failed extensions list."""
        failed_extensions = []

        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            display_failed_extensions(failed_extensions, use_rich=False)
            output = captured_output.getvalue()

            # Should not output anything for empty list
            self.assertEqual(output, '')
        finally:
            sys.stdout = sys.__stdout__


class TestFailedExtensionsJSONOutput(unittest.TestCase):
    """Test JSON output includes failed_extensions."""

    def test_json_output_includes_failed_extensions(self):
        """Test that JSON output includes failed_extensions in summary."""
        formatter = OutputFormatter()

        scan_results = [
            {'scan_status': 'success', 'vulnerabilities': {'count': 0}, 'risk_level': 'low'},
            {'scan_status': 'error', 'error': 'Rate limit'}
        ]

        failed_extensions = [
            {
                'id': 'failed.ext',
                'name': 'Failed Extension',
                'error_type': 'rate_limit',
                'error_message': 'Rate limit'
            }
        ]

        output = formatter.format_output(
            scan_results,
            '2025-10-25T12:00:00Z',
            10.5,
            failed_extensions=failed_extensions
        )

        # Verify failed_extensions is in summary
        self.assertIn('failed_extensions', output['summary'])
        self.assertEqual(len(output['summary']['failed_extensions']), 1)
        self.assertEqual(output['summary']['failed_extensions'][0]['id'], 'failed.ext')

    def test_json_output_without_failed_extensions(self):
        """Test that JSON output works without failed_extensions."""
        formatter = OutputFormatter()

        scan_results = [
            {'scan_status': 'success', 'vulnerabilities': {'count': 0}, 'risk_level': 'low'}
        ]

        output = formatter.format_output(
            scan_results,
            '2025-10-25T12:00:00Z',
            10.5,
            failed_extensions=None
        )

        # Verify failed_extensions is not in summary when None
        self.assertNotIn('failed_extensions', output['summary'])

    def test_json_output_with_empty_failed_extensions(self):
        """Test that JSON output works with empty failed_extensions list."""
        formatter = OutputFormatter()

        scan_results = [
            {'scan_status': 'success', 'vulnerabilities': {'count': 0}, 'risk_level': 'low'}
        ]

        output = formatter.format_output(
            scan_results,
            '2025-10-25T12:00:00Z',
            10.5,
            failed_extensions=[]
        )

        # Verify failed_extensions is not in summary when empty list
        self.assertNotIn('failed_extensions', output['summary'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
