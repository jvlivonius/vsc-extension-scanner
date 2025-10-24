#!/usr/bin/env python3
"""
Unit tests for scanner.py module.

Tests the refactored scan logic and integration with display components.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner import scanner


class TestRunScan(unittest.TestCase):
    """Test the main run_scan() function."""

    @patch('vscode_scanner.scanner._discover_extensions')
    @patch('vscode_scanner.scanner._scan_extensions')
    @patch('vscode_scanner.scanner._apply_post_scan_filters')
    @patch('vscode_scanner.scanner._generate_output')
    @patch('vscode_scanner.scanner._print_summary')
    def test_run_scan_success_no_vulns(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_apply_filters,
        mock_scan_extensions,
        mock_discover
    ):
        """Test successful scan with no vulnerabilities."""
        # Mock discovery
        mock_extensions = [
            {'id': 'test.ext1', 'version': '1.0.0', 'name': 'ext1', 'publisher': 'test'}
        ]
        mock_discover.return_value = (mock_extensions, Path('/fake/path'), 1)

        # Mock scanning
        mock_scan_results = [
            {'id': 'test.ext1', 'risk_level': 'low', 'vulnerabilities': {'count': 0}}
        ]
        mock_stats = {
            'vulnerabilities_found': 0,
            'successful_scans': 1,
            'failed_scans': 0,
            'cached_results': 0,
            'fresh_scans': 1,
            'api_client': MagicMock()
        }
        mock_scan_extensions.return_value = (mock_scan_results, mock_stats)

        # Mock filters (no filtering)
        mock_apply_filters.return_value = mock_scan_results

        # Mock output
        mock_results = {'summary': {'total_extensions_scanned': 1}}
        mock_generate_output.return_value = mock_results

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (0 = no vulnerabilities)
        self.assertEqual(exit_code, 0)

        # Verify functions were called
        mock_discover.assert_called_once()
        mock_scan_extensions.assert_called_once()
        mock_apply_filters.assert_called_once()
        mock_generate_output.assert_called_once()

    @patch('vscode_scanner.scanner._discover_extensions')
    @patch('vscode_scanner.scanner._scan_extensions')
    @patch('vscode_scanner.scanner._apply_post_scan_filters')
    @patch('vscode_scanner.scanner._generate_output')
    @patch('vscode_scanner.scanner._print_summary')
    def test_run_scan_success_with_vulns(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_apply_filters,
        mock_scan_extensions,
        mock_discover
    ):
        """Test successful scan with vulnerabilities found."""
        # Mock discovery
        mock_extensions = [
            {'id': 'test.ext1', 'version': '1.0.0', 'name': 'ext1', 'publisher': 'test'}
        ]
        mock_discover.return_value = (mock_extensions, Path('/fake/path'), 1)

        # Mock scanning with vulnerabilities
        mock_scan_results = [
            {'id': 'test.ext1', 'risk_level': 'high', 'vulnerabilities': {'count': 2}}
        ]
        mock_stats = {
            'vulnerabilities_found': 1,
            'successful_scans': 1,
            'failed_scans': 0,
            'cached_results': 0,
            'fresh_scans': 1,
            'api_client': MagicMock()
        }
        mock_scan_extensions.return_value = (mock_scan_results, mock_stats)

        # Mock filters
        mock_apply_filters.return_value = mock_scan_results

        # Mock output
        mock_results = {'summary': {'total_extensions_scanned': 1}}
        mock_generate_output.return_value = mock_results

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (1 = vulnerabilities found)
        self.assertEqual(exit_code, 1)

    @patch('vscode_scanner.scanner._discover_extensions')
    def test_run_scan_discovery_error(self, mock_discover):
        """Test handling of discovery errors."""
        # Mock discovery failure
        mock_discover.side_effect = FileNotFoundError("Extensions directory not found")

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (2 = error)
        self.assertEqual(exit_code, 2)

    @patch('vscode_scanner.scanner._discover_extensions')
    def test_run_scan_empty_extensions(self, mock_discover):
        """Test handling of empty extension list."""
        # Mock discovery with no extensions
        mock_discover.return_value = ([], Path('/fake/path'), 0)

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (0 = success but no extensions)
        self.assertEqual(exit_code, 0)


class TestApplyPreScanFilters(unittest.TestCase):
    """Test pre-scan filtering logic."""

    def setUp(self):
        """Set up test data."""
        self.extensions = [
            {'id': 'microsoft.python', 'publisher': 'microsoft', 'name': 'python'},
            {'id': 'microsoft.vscode', 'publisher': 'microsoft', 'name': 'vscode'},
            {'id': 'esbenp.prettier', 'publisher': 'esbenp', 'name': 'prettier'},
            {'id': 'dbaeumer.eslint', 'publisher': 'dbaeumer', 'name': 'eslint'},
        ]

    def test_no_filters(self):
        """Test with no filters applied."""
        class Args:
            publisher = None
            include_ids = None
            exclude_ids = None

        result = scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 4)

    def test_publisher_filter(self):
        """Test filtering by publisher."""
        class Args:
            publisher = "microsoft"
            include_ids = None
            exclude_ids = None

        result = scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 2)
        self.assertTrue(all(ext['publisher'] == 'microsoft' for ext in result))

    def test_include_ids_filter(self):
        """Test filtering by include IDs."""
        class Args:
            publisher = None
            include_ids = "microsoft.python,esbenp.prettier"
            exclude_ids = None

        result = scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 2)
        ids = [ext['id'] for ext in result]
        self.assertIn('microsoft.python', ids)
        self.assertIn('esbenp.prettier', ids)

    def test_exclude_ids_filter(self):
        """Test filtering by exclude IDs."""
        class Args:
            publisher = None
            include_ids = None
            exclude_ids = "microsoft.python,microsoft.vscode"

        result = scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 2)
        ids = [ext['id'] for ext in result]
        self.assertNotIn('microsoft.python', ids)
        self.assertNotIn('microsoft.vscode', ids)


class TestApplyPostScanFilters(unittest.TestCase):
    """Test post-scan filtering logic (risk level)."""

    def setUp(self):
        """Set up test data."""
        self.scan_results = [
            {'id': 'ext1', 'risk_level': 'low'},
            {'id': 'ext2', 'risk_level': 'medium'},
            {'id': 'ext3', 'risk_level': 'high'},
            {'id': 'ext4', 'risk_level': 'critical'},
        ]

    def test_no_risk_filter(self):
        """Test with no risk level filter."""
        class Args:
            min_risk_level = None

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 4)

    def test_medium_risk_filter(self):
        """Test filtering for medium+ risk."""
        class Args:
            min_risk_level = "medium"

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 3)
        # Should exclude 'low'
        risk_levels = [ext['risk_level'] for ext in result]
        self.assertNotIn('low', risk_levels)
        self.assertIn('medium', risk_levels)
        self.assertIn('high', risk_levels)
        self.assertIn('critical', risk_levels)

    def test_high_risk_filter(self):
        """Test filtering for high+ risk."""
        class Args:
            min_risk_level = "high"

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 2)
        # Should only include 'high' and 'critical'
        risk_levels = [ext['risk_level'] for ext in result]
        self.assertNotIn('low', risk_levels)
        self.assertNotIn('medium', risk_levels)
        self.assertIn('high', risk_levels)
        self.assertIn('critical', risk_levels)


class TestCalculateExitCode(unittest.TestCase):
    """Test exit code calculation."""

    def test_no_vulnerabilities(self):
        """Test exit code when no vulnerabilities found."""
        exit_code = scanner._calculate_exit_code(0)
        self.assertEqual(exit_code, 0)

    def test_with_vulnerabilities(self):
        """Test exit code when vulnerabilities found."""
        exit_code = scanner._calculate_exit_code(1)
        self.assertEqual(exit_code, 1)

        exit_code = scanner._calculate_exit_code(10)
        self.assertEqual(exit_code, 1)


class TestProcessCachedResult(unittest.TestCase):
    """Test cached result processing."""

    def test_process_cached_result_clean(self):
        """Test processing a clean cached result."""
        cached_result = {
            'risk_level': 'low',
            'security_score': 95,
            'vulnerabilities': {'count': 0}
        }

        ext = {
            'id': 'test.ext',
            'version': '1.0.0',
            'name': 'test',
            'publisher': 'test'
        }

        stats = {
            'vulnerabilities_found': 0,
            'successful_scans': 0,
            'cached_results': 0
        }

        scan_results = []

        scanner._process_cached_result(
            cached_result, ext, 'test.ext', '1.0.0',
            '[1/1]', stats, scan_results, False
        )

        # Verify result was added
        self.assertEqual(len(scan_results), 1)
        self.assertEqual(scan_results[0]['id'], 'test.ext')

        # Verify stats
        self.assertEqual(stats['successful_scans'], 1)
        self.assertEqual(stats['cached_results'], 1)
        self.assertEqual(stats['vulnerabilities_found'], 0)

    def test_process_cached_result_with_vulns(self):
        """Test processing a cached result with vulnerabilities."""
        cached_result = {
            'risk_level': 'high',
            'security_score': 65,
            'vulnerabilities': {'count': 2}
        }

        ext = {'id': 'test.ext', 'version': '1.0.0'}
        stats = {
            'vulnerabilities_found': 0,
            'successful_scans': 0,
            'cached_results': 0
        }
        scan_results = []

        scanner._process_cached_result(
            cached_result, ext, 'test.ext', '1.0.0',
            '[1/1]', stats, scan_results, False
        )

        # Verify vulnerability was counted
        self.assertEqual(stats['vulnerabilities_found'], 1)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRunScan))
    suite.addTests(loader.loadTestsFromTestCase(TestApplyPreScanFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestApplyPostScanFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateExitCode))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessCachedResult))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
