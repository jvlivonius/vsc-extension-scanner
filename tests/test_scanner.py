#!/usr/bin/env python3
"""
Unit tests for scanner.py module.

Tests the refactored scan logic and integration with display components.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call

import pytest
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner import scanner


@pytest.mark.unit
class TestRunScan(unittest.TestCase):
    """Test the main run_scan() function."""

    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_run_scan_success_no_vulns(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_apply_filters,
        mock_scan_extensions,
        mock_discover,
    ):
        """Test successful scan with no vulnerabilities."""
        # Mock discovery
        mock_extensions = [
            {"id": "test.ext1", "version": "1.0.0", "name": "ext1", "publisher": "test"}
        ]
        mock_discover.return_value = (mock_extensions, Path("/fake/path"), 1)

        # Mock scanning
        mock_scan_results = [
            {"id": "test.ext1", "risk_level": "low", "vulnerabilities": {"count": 0}}
        ]
        mock_stats = {
            "vulnerabilities_found": 0,
            "successful_scans": 1,
            "failed_scans": 0,
            "cached_results": 0,
            "fresh_scans": 1,
            "api_client": MagicMock(),
        }
        mock_scan_extensions.return_value = (mock_scan_results, mock_stats)

        # Mock filters (no filtering)
        mock_apply_filters.return_value = mock_scan_results

        # Mock output
        mock_results = {"summary": {"total_extensions_scanned": 1}}
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

    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_run_scan_success_with_vulns(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_apply_filters,
        mock_scan_extensions,
        mock_discover,
    ):
        """Test successful scan with vulnerabilities found."""
        # Mock discovery
        mock_extensions = [
            {"id": "test.ext1", "version": "1.0.0", "name": "ext1", "publisher": "test"}
        ]
        mock_discover.return_value = (mock_extensions, Path("/fake/path"), 1)

        # Mock scanning with vulnerabilities
        mock_scan_results = [
            {"id": "test.ext1", "risk_level": "high", "vulnerabilities": {"count": 2}}
        ]
        mock_stats = {
            "vulnerabilities_found": 1,
            "successful_scans": 1,
            "failed_scans": 0,
            "cached_results": 0,
            "fresh_scans": 1,
            "api_client": MagicMock(),
        }
        mock_scan_extensions.return_value = (mock_scan_results, mock_stats)

        # Mock filters
        mock_apply_filters.return_value = mock_scan_results

        # Mock output
        mock_results = {"summary": {"total_extensions_scanned": 1}}
        mock_generate_output.return_value = mock_results

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (1 = vulnerabilities found)
        self.assertEqual(exit_code, 1)

    @patch("vscode_scanner.scanner._discover_extensions")
    def test_run_scan_discovery_error(self, mock_discover):
        """Test handling of discovery errors."""
        # Mock discovery failure
        mock_discover.side_effect = FileNotFoundError("Extensions directory not found")

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (2 = error)
        self.assertEqual(exit_code, 2)

    @patch("vscode_scanner.scanner._discover_extensions")
    def test_run_scan_empty_extensions(self, mock_discover):
        """Test handling of empty extension list."""
        # Mock discovery with no extensions
        mock_discover.return_value = ([], Path("/fake/path"), 0)

        # Run scan
        exit_code = scanner.run_scan(plain=True, quiet=True)

        # Verify exit code (0 = success but no extensions)
        self.assertEqual(exit_code, 0)


@pytest.mark.unit
class TestApplyPreScanFilters(unittest.TestCase):
    """Test pre-scan filtering logic."""

    def setUp(self):
        """Set up test data."""
        self.extensions = [
            {"id": "microsoft.python", "publisher": "microsoft", "name": "python"},
            {"id": "microsoft.vscode", "publisher": "microsoft", "name": "vscode"},
            {"id": "esbenp.prettier", "publisher": "esbenp", "name": "prettier"},
            {"id": "dbaeumer.eslint", "publisher": "dbaeumer", "name": "eslint"},
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
        self.assertTrue(all(ext["publisher"] == "microsoft" for ext in result))

    def test_include_ids_filter(self):
        """Test filtering by include IDs."""

        class Args:
            publisher = None
            include_ids = "microsoft.python,esbenp.prettier"
            exclude_ids = None

        result = scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 2)
        ids = [ext["id"] for ext in result]
        self.assertIn("microsoft.python", ids)
        self.assertIn("esbenp.prettier", ids)

    def test_exclude_ids_filter(self):
        """Test filtering by exclude IDs."""

        class Args:
            publisher = None
            include_ids = None
            exclude_ids = "microsoft.python,microsoft.vscode"

        result = scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 2)
        ids = [ext["id"] for ext in result]
        self.assertNotIn("microsoft.python", ids)
        self.assertNotIn("microsoft.vscode", ids)


@pytest.mark.unit
class TestApplyPostScanFilters(unittest.TestCase):
    """Test post-scan filtering logic (risk level)."""

    def setUp(self):
        """Set up test data."""
        self.scan_results = [
            {"id": "ext1", "risk_level": "low"},
            {"id": "ext2", "risk_level": "medium"},
            {"id": "ext3", "risk_level": "high"},
            {"id": "ext4", "risk_level": "critical"},
        ]

    def test_no_risk_filter(self):
        """Test with no risk level filter."""

        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 4)

    def test_medium_risk_filter(self):
        """Test filtering for medium+ risk."""

        class Args:
            min_risk_level = "medium"
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 3)
        # Should exclude 'low'
        risk_levels = [ext["risk_level"] for ext in result]
        self.assertNotIn("low", risk_levels)
        self.assertIn("medium", risk_levels)
        self.assertIn("high", risk_levels)
        self.assertIn("critical", risk_levels)

    def test_high_risk_filter(self):
        """Test filtering for high+ risk."""

        class Args:
            min_risk_level = "high"
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 2)
        # Should only include 'high' and 'critical'
        risk_levels = [ext["risk_level"] for ext in result]
        self.assertNotIn("low", risk_levels)
        self.assertNotIn("medium", risk_levels)
        self.assertIn("high", risk_levels)
        self.assertIn("critical", risk_levels)


@pytest.mark.unit
class TestNewFilteringFeatures(unittest.TestCase):
    """Test new v3.3.1 filtering features (publisher verification, vulnerabilities)."""

    def setUp(self):
        """Set up test data with realistic structure (matches real scan results)."""
        self.scan_results = [
            # Unverified publisher (string from discovery, unverified in metadata)
            {
                "id": "yzane.markdown-pdf",
                "publisher": "yzane",  # String from discovery
                "metadata": {
                    "publisher": {"id": "yzane", "name": "yzane", "verified": False}
                },
                "vulnerabilities": {"count": 12},
            },
            # Verified publisher (GitHub) - no vulnerabilities
            {
                "id": "github.vscode-pull-request-github",
                "publisher": "github",  # String from discovery
                "metadata": {
                    "publisher": {"id": "github", "name": "GitHub", "verified": True}
                },
                "vulnerabilities": {"count": 0},
            },
            # Unverified publisher with vulnerabilities
            {
                "id": "donjayamanne.githistory",
                "publisher": "donjayamanne",  # String from discovery
                "metadata": {
                    "publisher": {
                        "id": "donjayamanne",
                        "name": "Don Jayamanne",
                        "verified": False,
                    }
                },
                "vulnerabilities": {"count": 1},
            },
            # Verified publisher (Red Hat) with vulnerabilities
            {
                "id": "redhat.vscode-rsp-ui",
                "publisher": "redhat",  # String from discovery
                "metadata": {
                    "publisher": {"id": "redhat", "name": "Red Hat", "verified": True}
                },
                "vulnerabilities": {"count": 3},
            },
            # Extension without metadata (discovery only - treated as unverified)
            {
                "id": "local.test-extension",
                "publisher": "local",  # String from discovery only
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

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 2)  # GitHub and Red Hat (verified publishers)
        ids = [r["id"] for r in result]
        self.assertIn("github.vscode-pull-request-github", ids)
        self.assertIn("redhat.vscode-rsp-ui", ids)

    def test_unverified_only_filter(self):
        """Test --unverified-only filter excludes verified publishers in metadata."""

        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = True
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 3)  # yzane, donjayamanne, local (unverified)
        ids = [r["id"] for r in result]
        self.assertIn("yzane.markdown-pdf", ids)
        self.assertIn("donjayamanne.githistory", ids)
        self.assertIn("local.test-extension", ids)
        # Verified publishers should NOT be included
        self.assertNotIn("github.vscode-pull-request-github", ids)
        self.assertNotIn("redhat.vscode-rsp-ui", ids)

    def test_with_vulnerabilities_filter(self):
        """Test --with-vulnerabilities filter."""

        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = False
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 3)  # yzane (12), donjayamanne (1), redhat (3)
        ids = [r["id"] for r in result]
        self.assertIn("yzane.markdown-pdf", ids)
        self.assertIn("donjayamanne.githistory", ids)
        self.assertIn("redhat.vscode-rsp-ui", ids)

    def test_without_vulnerabilities_filter(self):
        """Test --without-vulnerabilities filter."""

        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = True

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 2)  # github (0 vulns), local (missing = 0)
        ids = [r["id"] for r in result]
        self.assertIn("github.vscode-pull-request-github", ids)
        self.assertIn("local.test-extension", ids)

    def test_combined_filters_verified_and_no_vulns(self):
        """Test --verified-only --without-vulnerabilities (safe extensions)."""

        class Args:
            min_risk_level = None
            verified_only = True
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = True

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 1)  # Only GitHub (verified + no vulns)
        self.assertEqual(result[0]["id"], "github.vscode-pull-request-github")

    def test_combined_filters_unverified_and_with_vulns(self):
        """Test --unverified-only --with-vulnerabilities (risky extensions)."""

        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = True
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        self.assertEqual(len(result), 2)  # yzane (12 vulns) and donjayamanne (1 vuln)
        ids = [r["id"] for r in result]
        self.assertIn("yzane.markdown-pdf", ids)
        self.assertIn("donjayamanne.githistory", ids)
        # Verified Red Hat should NOT be included (even though it has vulns)
        self.assertNotIn("redhat.vscode-rsp-ui", ids)

    def test_missing_vulnerabilities_dict(self):
        """Test that missing vulnerabilities dict is treated as no vulnerabilities."""

        class Args:
            min_risk_level = None
            verified_only = False
            unverified_only = False
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        # local.test-extension has no vulnerabilities dict, should not be included
        ids = [r["id"] for r in result]
        self.assertNotIn("local.test-extension", ids)

    def test_extension_without_metadata_treated_as_unverified(self):
        """Test that extensions without metadata.publisher are treated as unverified."""

        class Args:
            min_risk_level = None
            verified_only = True
            unverified_only = False
            with_vulnerabilities = False
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            self.scan_results, Args(), use_rich=False
        )
        # local.test-extension has no metadata, should NOT be in verified-only results
        ids = [r["id"] for r in result]
        self.assertNotIn("local.test-extension", ids)
        # Should only include extensions with verified=true in metadata
        self.assertEqual(len(result), 2)  # GitHub and Red Hat only

    def test_all_filters_together(self):
        """Test combining risk level with new filters."""
        # Create test data with risk_level and realistic structure
        results_with_risk = [
            {
                "id": "low-verified-clean",
                "risk_level": "low",
                "publisher": "pub1",
                "metadata": {"publisher": {"id": "pub1", "verified": True}},
                "vulnerabilities": {"count": 0},
            },
            {
                "id": "high-verified-vulns",
                "risk_level": "high",
                "publisher": "pub2",
                "metadata": {"publisher": {"id": "pub2", "verified": True}},
                "vulnerabilities": {"count": 3},
            },
            {
                "id": "high-unverified-vulns",
                "risk_level": "high",
                "publisher": "pub3",
                "metadata": {"publisher": {"id": "pub3", "verified": False}},
                "vulnerabilities": {"count": 1},
            },
        ]

        class Args:
            min_risk_level = "high"
            verified_only = True
            unverified_only = False
            with_vulnerabilities = True
            without_vulnerabilities = False

        result = scanner._apply_post_scan_filters(
            results_with_risk, Args(), use_rich=False
        )
        # Only high-verified-vulns: high risk + verified + has vulns
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "high-verified-vulns")

    def test_verification_status_from_metadata(self):
        """Test that _get_verification_status() checks metadata.publisher.verified first."""
        # Verified in metadata (primary source)
        result_verified_metadata = {
            "publisher": "github",  # String from discovery
            "metadata": {
                "publisher": {"id": "github", "verified": True}  # ← Should use this
            },
        }
        self.assertTrue(scanner._get_verification_status(result_verified_metadata))

        # Unverified in metadata
        result_unverified_metadata = {
            "publisher": "yzane",
            "metadata": {
                "publisher": {"id": "yzane", "verified": False}  # ← Should use this
            },
        }
        self.assertFalse(scanner._get_verification_status(result_unverified_metadata))

        # No metadata (fallback to top-level publisher dict - rare case)
        result_toplevel_verified = {"publisher": {"id": "some-pub", "verified": True}}
        self.assertTrue(scanner._get_verification_status(result_toplevel_verified))

        # String publisher only (no metadata)
        result_string_only = {"publisher": "local"}
        self.assertFalse(scanner._get_verification_status(result_string_only))

        # Empty result
        result_empty = {}
        self.assertFalse(scanner._get_verification_status(result_empty))


@pytest.mark.unit
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


@pytest.mark.unit
class TestProcessCachedResult(unittest.TestCase):
    """Test cached result processing."""

    def test_process_cached_result_clean(self):
        """Test processing a clean cached result."""
        cached_result = {
            "risk_level": "low",
            "security_score": 95,
            "vulnerabilities": {"count": 0},
        }

        ext = {
            "id": "test.ext",
            "version": "1.0.0",
            "name": "test",
            "publisher": "test",
        }

        stats = {"vulnerabilities_found": 0, "successful_scans": 0, "cached_results": 0}

        scan_results = []

        scanner._process_cached_result(
            cached_result, ext, "test.ext", "1.0.0", "[1/1]", stats, scan_results, False
        )

        # Verify result was added
        self.assertEqual(len(scan_results), 1)
        self.assertEqual(scan_results[0]["id"], "test.ext")

        # Verify stats
        self.assertEqual(stats["successful_scans"], 1)
        self.assertEqual(stats["cached_results"], 1)
        self.assertEqual(stats["vulnerabilities_found"], 0)

    def test_process_cached_result_with_vulns(self):
        """Test processing a cached result with vulnerabilities."""
        cached_result = {
            "risk_level": "high",
            "security_score": 65,
            "vulnerabilities": {"count": 2},
        }

        ext = {"id": "test.ext", "version": "1.0.0"}
        stats = {"vulnerabilities_found": 0, "successful_scans": 0, "cached_results": 0}
        scan_results = []

        scanner._process_cached_result(
            cached_result, ext, "test.ext", "1.0.0", "[1/1]", stats, scan_results, False
        )

        # Verify vulnerability was counted
        self.assertEqual(stats["vulnerabilities_found"], 1)


@pytest.mark.unit
class TestErrorCategorization(unittest.TestCase):
    """Test error categorization and message simplification.

    **Purpose:** Ensure error messages are properly categorized and simplified.

    **Scope:**
    - Error type detection (rate_limit, network_timeout, network_error, api_error)
    - Message simplification
    - Edge cases (empty messages, unknown errors)
    """

    def test_categorize_rate_limit_error(self):
        """Test that rate limit errors are correctly identified."""
        # Test with "rate limit" text
        result = scanner._categorize_error("Rate limit exceeded")
        self.assertEqual(result, "rate_limit")

        # Test with 429 status code
        result = scanner._categorize_error("HTTP 429: Too many requests")
        self.assertEqual(result, "rate_limit")

    def test_categorize_timeout_error(self):
        """Test that timeout errors are correctly identified."""
        result = scanner._categorize_error("Request timed out")
        self.assertEqual(result, "network_timeout")

        result = scanner._categorize_error("Connection timeout error")
        self.assertEqual(result, "network_timeout")

    def test_categorize_network_error(self):
        """Test that network errors are correctly identified."""
        result = scanner._categorize_error("Network connection failed")
        self.assertEqual(result, "network_error")

        result = scanner._categorize_error("Connection refused")
        self.assertEqual(result, "network_error")

    def test_categorize_generic_api_error(self):
        """Test that generic errors default to api_error."""
        result = scanner._categorize_error("Unknown API error")
        self.assertEqual(result, "api_error")

        result = scanner._categorize_error("Invalid response format")
        self.assertEqual(result, "api_error")

    def test_categorize_empty_error_message(self):
        """Test handling of empty error message."""
        result = scanner._categorize_error("")
        self.assertEqual(result, "api_error")

        result = scanner._categorize_error(None)
        self.assertEqual(result, "api_error")

    def test_simplify_error_message(self):
        """Test error type to user-friendly message conversion."""
        # Test known error types
        self.assertEqual(scanner._simplify_error_message("rate_limit"), "Rate limit")
        self.assertEqual(
            scanner._simplify_error_message("network_timeout"), "Network timeout"
        )
        self.assertEqual(
            scanner._simplify_error_message("network_error"), "Network error"
        )
        self.assertEqual(scanner._simplify_error_message("api_error"), "API error")

        # Test unknown error type defaults to "API error"
        self.assertEqual(scanner._simplify_error_message("unknown_error"), "API error")


@pytest.mark.unit
class TestExtensionDiscoveryErrors(unittest.TestCase):
    """Test error handling in extension discovery.

    **Purpose:** Ensure discovery failures are handled gracefully.

    **Scope:**
    - No extensions found
    - Discovery exceptions
    - Invalid extension data
    """

    @patch("vscode_scanner.scanner.ExtensionDiscovery")
    def test_discover_extensions_no_extensions_found(self, mock_discovery_class):
        """Test handling when no extensions are found."""
        # Mock discovery to return empty list
        mock_discovery = MagicMock()
        mock_discovery.find_extensions_directory.return_value = Path("/fake/path")
        mock_discovery.discover_extensions.return_value = []
        mock_discovery_class.return_value = mock_discovery

        # Create mock args
        mock_args = MagicMock()
        mock_args.publisher = None
        mock_args.include_ids = None
        mock_args.exclude_ids = None

        # Act
        extensions, extensions_dir, extension_count = scanner._discover_extensions(
            mock_args, use_rich=False, quiet=True
        )

        # Assert
        self.assertEqual(len(extensions), 0)
        self.assertEqual(extension_count, 0)

    @patch("vscode_scanner.scanner.ExtensionDiscovery")
    def test_discover_extensions_directory_not_found(self, mock_discovery_class):
        """Test handling when extensions directory is not found."""
        # Mock discovery to raise FileNotFoundError
        mock_discovery = MagicMock()
        mock_discovery.find_extensions_directory.side_effect = FileNotFoundError(
            "Extensions directory not found"
        )
        mock_discovery_class.return_value = mock_discovery

        # Create mock args
        mock_args = MagicMock()
        mock_args.extensions_dir = None

        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            scanner._discover_extensions(mock_args, use_rich=False, quiet=True)

    @patch("vscode_scanner.scanner.ExtensionDiscovery")
    def test_discover_extensions_permission_error(self, mock_discovery_class):
        """Test handling when permission denied on extensions directory."""
        # Mock discovery to raise PermissionError
        mock_discovery = MagicMock()
        mock_discovery.find_extensions_directory.return_value = Path("/fake/path")
        mock_discovery.discover_extensions.side_effect = PermissionError(
            "Permission denied"
        )
        mock_discovery_class.return_value = mock_discovery

        # Create mock args
        mock_args = MagicMock()
        mock_args.extensions_dir = None

        # Act & Assert
        with self.assertRaises(PermissionError):
            scanner._discover_extensions(mock_args, use_rich=False, quiet=True)


@pytest.mark.unit
class TestScanErrorPaths(unittest.TestCase):
    """Test error paths during scanning operations.

    **Purpose:** Ensure scan failures are handled gracefully.

    **Scope:**
    - API client errors
    - Network failures
    - Invalid API responses
    - Cache errors during scan
    """

    @patch("vscode_scanner.scanner._scan_extension_fresh")
    def test_scan_single_extension_api_error(self, mock_scan_fresh):
        """Test handling of API errors during scan."""
        # Arrange
        mock_api_client = MagicMock()
        mock_cache = MagicMock()
        mock_cache.get_cached_result.return_value = None
        mock_args = MagicMock()
        # Use regular dict for stats (not ThreadSafeStats)
        stats = {
            "successful_scans": 0,
            "failed_scans": 0,
            "vulnerabilities_found": 0,
            "failed_extensions": [],
            "api_client": mock_api_client,
        }
        scan_results = []

        # Mock API error - exception propagates out, not caught
        mock_scan_fresh.side_effect = Exception("API request failed")

        ext = {
            "id": "test.ext",
            "version": "1.0.0",
            "name": "Test Ext",
            "publisher": "test",
        }

        # Act & Assert - exception propagates out
        with self.assertRaises(Exception) as ctx:
            scanner._scan_single_extension(
                ext,  # ext
                1,  # idx
                1,  # total
                mock_cache,  # cache_manager
                mock_args,  # args
                mock_api_client,  # api_client
                stats,  # stats (Dict)
                scan_results,  # scan_results
                False,  # use_rich
            )

        self.assertIn("API request failed", str(ctx.exception))

    @patch("vscode_scanner.scanner._scan_extension_fresh")
    def test_scan_single_extension_cache_error(self, mock_scan_fresh):
        """Test handling of cache errors during scan."""
        # Arrange
        mock_cache = MagicMock()
        mock_api_client = MagicMock()
        # Mock cache to raise exception - should continue with fresh scan
        mock_cache.get_cached_result.side_effect = Exception("Cache read error")
        mock_args = MagicMock()
        # Use regular dict for stats (not ThreadSafeStats)
        stats = {
            "successful_scans": 0,
            "failed_scans": 0,
            "vulnerabilities_found": 0,
            "fresh_scans": 0,
            "failed_extensions": [],
            "api_client": mock_api_client,
        }
        scan_results = []

        ext = {
            "id": "test.ext",
            "version": "1.0.0",
            "name": "Test Ext",
            "publisher": "test",
        }

        # Mock successful API scan after cache error
        mock_scan_fresh.return_value = None  # Modifies scan_results in place

        # Act - should handle cache error gracefully and continue with fresh scan
        result = scanner._scan_single_extension(
            ext,  # ext
            1,  # idx
            1,  # total
            mock_cache,  # cache_manager
            mock_args,  # args
            mock_api_client,  # api_client
            stats,  # stats (Dict)
            scan_results,  # scan_results
            False,  # use_rich
        )

        # Assert - _scan_extension_fresh was called despite cache error
        mock_scan_fresh.assert_called_once()


@pytest.mark.unit
class TestOutputFileErrors(unittest.TestCase):
    """Test error handling for output file operations.

    **Purpose:** Ensure file writing errors are handled gracefully.

    **Scope:**
    - Permission errors
    - Invalid paths
    - Disk full scenarios
    """

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    @patch("vscode_scanner.scanner.safe_mkdir")
    def test_write_output_file_permission_error(self, mock_mkdir, mock_open):
        """Test handling of permission error when writing output file."""
        # Arrange
        results = {"extensions": [{"id": "test.ext", "version": "1.0.0"}]}
        output_file = "/protected/output.json"

        # Act & Assert - function lets exception propagate
        with self.assertRaises(PermissionError):
            scanner._write_output_file(
                output_file,  # output_path_str
                results,  # results
                False,  # is_html_output
                False,  # use_rich
            )

    @patch("builtins.open", side_effect=OSError("Disk full"))
    @patch("vscode_scanner.scanner.safe_mkdir")
    def test_write_output_file_disk_full(self, mock_mkdir, mock_open):
        """Test handling of disk full error when writing output file."""
        # Arrange
        results = {"extensions": [{"id": "test.ext", "version": "1.0.0"}]}
        output_file = "/tmp/output.json"

        # Act & Assert - function lets exception propagate
        with self.assertRaises(OSError):
            scanner._write_output_file(
                output_file,  # output_path_str
                results,  # results
                False,  # is_html_output
                False,  # use_rich
            )


@pytest.mark.unit
class TestThreadSafeStats(unittest.TestCase):
    """Test thread-safe statistics tracking.

    **Purpose:** Ensure stats tracking works correctly in multi-threaded environment.

    **Scope:**
    - Concurrent increments
    - Counter accuracy
    - Thread safety verification
    """

    def test_thread_safe_stats_initialization(self):
        """Test ThreadSafeStats initialization."""
        stats = scanner.ThreadSafeStats()

        self.assertEqual(stats.get("vulnerabilities_found"), 0)
        self.assertEqual(stats.get("successful_scans"), 0)
        self.assertEqual(stats.get("failed_scans"), 0)
        self.assertEqual(stats.get("cached_results"), 0)
        self.assertEqual(stats.get("fresh_scans"), 0)

    def test_thread_safe_stats_increment_vulnerabilities(self):
        """Test incrementing vulnerability count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("vulnerabilities_found")
        self.assertEqual(stats.get("vulnerabilities_found"), 1)

        stats.increment("vulnerabilities_found")
        self.assertEqual(stats.get("vulnerabilities_found"), 2)

    def test_thread_safe_stats_increment_successful_scans(self):
        """Test incrementing successful scan count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("successful_scans")
        self.assertEqual(stats.get("successful_scans"), 1)

    def test_thread_safe_stats_increment_failed_scans(self):
        """Test incrementing failed scan count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("failed_scans")
        self.assertEqual(stats.get("failed_scans"), 1)

    def test_thread_safe_stats_increment_cached_results(self):
        """Test incrementing cached result count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("cached_results")
        self.assertEqual(stats.get("cached_results"), 1)

    def test_thread_safe_stats_increment_fresh_scans(self):
        """Test incrementing fresh scan count."""
        stats = scanner.ThreadSafeStats()

        stats.increment("fresh_scans")
        self.assertEqual(stats.get("fresh_scans"), 1)

    def test_thread_safe_stats_to_dict(self):
        """Test converting stats to dictionary."""
        mock_api = MagicMock()
        stats = scanner.ThreadSafeStats()
        stats.set("api_client", mock_api)

        stats.increment("vulnerabilities_found")
        stats.increment("successful_scans")
        stats.increment("cached_results")

        result = stats.to_dict()

        self.assertEqual(result["vulnerabilities_found"], 1)
        self.assertEqual(result["successful_scans"], 1)
        self.assertEqual(result["cached_results"], 1)
        self.assertIn("api_client", result)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes (existing)
    suite.addTests(loader.loadTestsFromTestCase(TestRunScan))
    suite.addTests(loader.loadTestsFromTestCase(TestApplyPreScanFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestApplyPostScanFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateExitCode))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessCachedResult))

    # Add error path test classes (Phase 3.5)
    suite.addTests(loader.loadTestsFromTestCase(TestErrorCategorization))
    suite.addTests(loader.loadTestsFromTestCase(TestExtensionDiscoveryErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestScanErrorPaths))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFileErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestThreadSafeStats))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
