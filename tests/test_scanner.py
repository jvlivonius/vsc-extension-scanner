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
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 4)

    def test_medium_risk_filter(self):
        """Test filtering for medium+ risk."""
        class Args:
            min_risk_level = "medium"
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

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
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 2)
        # Should only include 'high' and 'critical'
        risk_levels = [ext['risk_level'] for ext in result]
        self.assertNotIn('low', risk_levels)
        self.assertNotIn('medium', risk_levels)
        self.assertIn('high', risk_levels)
        self.assertIn('critical', risk_levels)


class TestNewFilteringFeatures(unittest.TestCase):
    """Test new v3.3.1 filtering features (publisher verification, vulnerabilities)."""

    def setUp(self):
        """Set up test data with realistic structure (matches real scan results)."""
        self.scan_results = [
            # Unverified publisher (string from discovery, unverified in metadata)
            {
                'id': 'yzane.markdown-pdf',
                'publisher': 'yzane',  # String from discovery
                'metadata': {
                    'publisher': {
                        'id': 'yzane',
                        'name': 'yzane',
                        'verified': False
                    }
                },
                'vulnerabilities': {'count': 12}
            },
            # Verified publisher (GitHub) - no vulnerabilities
            {
                'id': 'github.vscode-pull-request-github',
                'publisher': 'github',  # String from discovery
                'metadata': {
                    'publisher': {
                        'id': 'github',
                        'name': 'GitHub',
                        'verified': True
                    }
                },
                'vulnerabilities': {'count': 0}
            },
            # Unverified publisher with vulnerabilities
            {
                'id': 'donjayamanne.githistory',
                'publisher': 'donjayamanne',  # String from discovery
                'metadata': {
                    'publisher': {
                        'id': 'donjayamanne',
                        'name': 'Don Jayamanne',
                        'verified': False
                    }
                },
                'vulnerabilities': {'count': 1}
            },
            # Verified publisher (Red Hat) with vulnerabilities
            {
                'id': 'redhat.vscode-rsp-ui',
                'publisher': 'redhat',  # String from discovery
                'metadata': {
                    'publisher': {
                        'id': 'redhat',
                        'name': 'Red Hat',
                        'verified': True
                    }
                },
                'vulnerabilities': {'count': 3}
            },
            # Extension without metadata (discovery only - treated as unverified)
            {
                'id': 'local.test-extension',
                'publisher': 'local',  # String from discovery only
                # No metadata - treated as unverified
            },
        ]

    def test_verified_only_filter(self):
        """Test --verified-only filter checks metadata.publisher.verified."""
        class Args:
            min_risk_level = None
            verified_only = True
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 2)  # GitHub and Red Hat (verified publishers)
        ids = [r['id'] for r in result]
        self.assertIn('github.vscode-pull-request-github', ids)
        self.assertIn('redhat.vscode-rsp-ui', ids)

    def test_unverified_only_filter(self):
        """Test --unverified-only filter excludes verified publishers in metadata."""
        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = True
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 3)  # yzane, donjayamanne, local (unverified)
        ids = [r['id'] for r in result]
        self.assertIn('yzane.markdown-pdf', ids)
        self.assertIn('donjayamanne.githistory', ids)
        self.assertIn('local.test-extension', ids)
        # Verified publishers should NOT be included
        self.assertNotIn('github.vscode-pull-request-github', ids)
        self.assertNotIn('redhat.vscode-rsp-ui', ids)

    def test_with_vulnerabilities_filter(self):
        """Test --with-vulnerabilities filter."""
        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = False
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 3)  # yzane (12), donjayamanne (1), redhat (3)
        ids = [r['id'] for r in result]
        self.assertIn('yzane.markdown-pdf', ids)
        self.assertIn('donjayamanne.githistory', ids)
        self.assertIn('redhat.vscode-rsp-ui', ids)

    def test_without_vulnerabilities_filter(self):
        """Test --without-vulnerabilities filter."""
        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = True

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 2)  # github (0 vulns), local (missing = 0)
        ids = [r['id'] for r in result]
        self.assertIn('github.vscode-pull-request-github', ids)
        self.assertIn('local.test-extension', ids)

    def test_combined_filters_verified_and_no_vulns(self):
        """Test --verified-only --without-vulnerabilities (safe extensions)."""
        class Args:
            min_risk_level = None
            verified_only = True
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = True

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 1)  # Only GitHub (verified + no vulns)
        self.assertEqual(result[0]['id'], 'github.vscode-pull-request-github')

    def test_combined_filters_unverified_and_with_vulns(self):
        """Test --unverified-only --with-vulnerabilities (risky extensions)."""
        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = True
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        self.assertEqual(len(result), 2)  # yzane (12 vulns) and donjayamanne (1 vuln)
        ids = [r['id'] for r in result]
        self.assertIn('yzane.markdown-pdf', ids)
        self.assertIn('donjayamanne.githistory', ids)
        # Verified Red Hat should NOT be included (even though it has vulns)
        self.assertNotIn('redhat.vscode-rsp-ui', ids)

    def test_missing_vulnerabilities_dict(self):
        """Test that missing vulnerabilities dict is treated as no vulnerabilities."""
        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = False
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        # local.test-extension has no vulnerabilities dict, should not be included
        ids = [r['id'] for r in result]
        self.assertNotIn('local.test-extension', ids)

    def test_extension_without_metadata_treated_as_unverified(self):
        """Test that extensions without metadata.publisher are treated as unverified."""
        class Args:
            min_risk_level = None
            verified_only = True
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(self.scan_results, Args(), use_rich=False)
        # local.test-extension has no metadata, should NOT be in verified-only results
        ids = [r['id'] for r in result]
        self.assertNotIn('local.test-extension', ids)
        # Should only include extensions with verified=true in metadata
        self.assertEqual(len(result), 2)  # GitHub and Red Hat only

    def test_all_filters_together(self):
        """Test combining risk level with new filters."""
        # Create test data with risk_level and realistic structure
        results_with_risk = [
            {
                'id': 'low-verified-clean',
                'risk_level': 'low',
                'publisher': 'pub1',
                'metadata': {
                    'publisher': {'id': 'pub1', 'verified': True}
                },
                'vulnerabilities': {'count': 0}
            },
            {
                'id': 'high-verified-vulns',
                'risk_level': 'high',
                'publisher': 'pub2',
                'metadata': {
                    'publisher': {'id': 'pub2', 'verified': True}
                },
                'vulnerabilities': {'count': 3}
            },
            {
                'id': 'high-unverified-vulns',
                'risk_level': 'high',
                'publisher': 'pub3',
                'metadata': {
                    'publisher': {'id': 'pub3', 'verified': False}
                },
                'vulnerabilities': {'count': 1}
            },
        ]

        class Args:
            min_risk_level = 'high'
            verified_only = True
            unverified_only = False
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(results_with_risk, Args(), use_rich=False)
        # Only high-verified-vulns: high risk + verified + has vulns
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'high-verified-vulns')

    def test_verification_status_from_metadata(self):
        """Test that _get_verification_status() checks metadata.publisher.verified first."""
        # Verified in metadata (primary source)
        result_verified_metadata = {
            'publisher': 'github',  # String from discovery
            'metadata': {
                'publisher': {
                    'id': 'github',
                    'verified': True  # ← Should use this
                }
            }
        }
        self.assertTrue(scanner._get_verification_status(result_verified_metadata))

        # Unverified in metadata
        result_unverified_metadata = {
            'publisher': 'yzane',
            'metadata': {
                'publisher': {
                    'id': 'yzane',
                    'verified': False  # ← Should use this
                }
            }
        }
        self.assertFalse(scanner._get_verification_status(result_unverified_metadata))

        # No metadata (fallback to top-level publisher dict - rare case)
        result_toplevel_verified = {
            'publisher': {
                'id': 'some-pub',
                'verified': True
            }
        }
        self.assertTrue(scanner._get_verification_status(result_toplevel_verified))

        # String publisher only (no metadata)
        result_string_only = {
            'publisher': 'local'
        }
        self.assertFalse(scanner._get_verification_status(result_string_only))

        # Empty result
        result_empty = {}
        self.assertFalse(scanner._get_verification_status(result_empty))


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
