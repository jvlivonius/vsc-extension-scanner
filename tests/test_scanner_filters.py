"""
Comprehensive filter tests for scanner.py

Tests filter combinations and edge cases to improve coverage from 64.91% to 75%+.
Focuses on pre-scan filters (publisher, include/exclude IDs) and post-scan filters
(risk level, verification status, vulnerabilities).
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
from vscode_scanner.scanner import (
    _apply_pre_scan_filters,
    _apply_post_scan_filters,
    run_scan,
)


@pytest.mark.unit
class TestPreScanFilters(unittest.TestCase):
    """Test pre-scan filter logic."""

    def setUp(self):
        """Create test extension data."""
        self.extensions = [
            {"id": "ms-python.python", "publisher": "ms-python"},
            {"id": "ms-vscode.cpptools", "publisher": "ms-vscode"},
            {"id": "esbenp.prettier-vscode", "publisher": "esbenp"},
            {"id": "dbaeumer.vscode-eslint", "publisher": "dbaeumer"},
            {"id": "github.copilot", "publisher": "github"},
        ]

    def test_no_filters(self):
        """No filters applied returns all extensions."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids=None,
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 5)

    def test_publisher_filter_case_insensitive(self):
        """Publisher filter is case-insensitive."""
        # Arrange
        args = Mock(
            publisher="MS-PYTHON",  # Uppercase
            include_ids=None,
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["publisher"], "ms-python")

    def test_publisher_filter_no_matches(self):
        """Publisher filter with no matches returns empty list."""
        # Arrange
        args = Mock(
            publisher="nonexistent",
            include_ids=None,
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 0)

    def test_include_ids_single(self):
        """Include IDs with single ID."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids="ms-python.python",
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ms-python.python")

    def test_include_ids_multiple(self):
        """Include IDs with comma-separated list."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids="ms-python.python,github.copilot",
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 2)
        ids = [ext["id"] for ext in result]
        self.assertIn("ms-python.python", ids)
        self.assertIn("github.copilot", ids)

    def test_include_ids_with_spaces(self):
        """Include IDs handles spaces around commas."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids=" ms-python.python , github.copilot ",
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 2)

    def test_include_ids_empty_string(self):
        """Include IDs with empty string is ignored."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids="",
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert: No filtering applied
        self.assertEqual(len(result), 5)

    def test_exclude_ids_single(self):
        """Exclude IDs with single ID."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids=None,
            exclude_ids="ms-python.python",
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 4)
        ids = [ext["id"] for ext in result]
        self.assertNotIn("ms-python.python", ids)

    def test_exclude_ids_multiple(self):
        """Exclude IDs with comma-separated list."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids=None,
            exclude_ids="ms-python.python,github.copilot",
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert
        self.assertEqual(len(result), 3)
        ids = [ext["id"] for ext in result]
        self.assertNotIn("ms-python.python", ids)
        self.assertNotIn("github.copilot", ids)

    def test_publisher_and_include_ids(self):
        """Publisher filter combined with include IDs (AND logic)."""
        # Arrange
        args = Mock(
            publisher="ms-python",
            include_ids="ms-python.python,ms-vscode.cpptools",
            exclude_ids=None,
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert: Only ms-python.python matches both filters
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ms-python.python")

    def test_publisher_and_exclude_ids(self):
        """Publisher filter combined with exclude IDs."""
        # Arrange: Get ms-python extensions, but exclude one
        args = Mock(
            publisher="ms-python",
            include_ids=None,
            exclude_ids="ms-python.python",
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert: No ms-python extensions remain
        self.assertEqual(len(result), 0)

    def test_include_and_exclude_ids(self):
        """Include and exclude IDs (exclude takes precedence)."""
        # Arrange
        args = Mock(
            publisher=None,
            include_ids="ms-python.python,github.copilot",
            exclude_ids="github.copilot",
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert: Only ms-python.python remains (copilot excluded)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ms-python.python")

    def test_all_filters_combined(self):
        """All three filters combined."""
        # Arrange: Complex scenario
        self.extensions.append({"id": "ms-python.debugpy", "publisher": "ms-python"})
        args = Mock(
            publisher="ms-python",
            include_ids="ms-python.python,ms-python.debugpy",
            exclude_ids="ms-python.debugpy",
        )

        # Act
        result = _apply_pre_scan_filters(self.extensions, args)

        # Assert: Only ms-python.python survives all filters
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ms-python.python")


@pytest.mark.unit
class TestPostScanFilters(unittest.TestCase):
    """Test post-scan filter logic."""

    def setUp(self):
        """Create test scan results."""
        self.scan_results = [
            {
                "id": "ext1",
                "risk_level": "low",
                "verification_status": "verified",
                "vulnerabilities": {"count": 0},
            },
            {
                "id": "ext2",
                "risk_level": "medium",
                "verification_status": "verified",
                "vulnerabilities": {"count": 2},
            },
            {
                "id": "ext3",
                "risk_level": "high",
                "verification_status": "unverified",
                "vulnerabilities": {"count": 5},
            },
            {
                "id": "ext4",
                "risk_level": "critical",
                "verification_status": "unverified",
                "vulnerabilities": {"count": 10},
            },
            {
                "id": "ext5",
                "risk_level": "low",
                "verification_status": "verified",
                "vulnerabilities": {"count": 0},
            },
        ]

    def test_no_filters(self):
        """No filters applied returns all results."""
        # Arrange
        args = Mock(
            min_risk_level=None,
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert
        self.assertEqual(len(result), 5)

    def test_min_risk_level_low(self):
        """Min risk level 'low' includes all."""
        # Arrange
        args = Mock(
            min_risk_level="low",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert
        self.assertEqual(len(result), 5)

    def test_min_risk_level_medium(self):
        """Min risk level 'medium' excludes 'low'."""
        # Arrange
        args = Mock(
            min_risk_level="medium",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert: Only medium, high, critical
        self.assertEqual(len(result), 3)
        risk_levels = [r["risk_level"] for r in result]
        self.assertNotIn("low", risk_levels)

    def test_min_risk_level_high(self):
        """Min risk level 'high' excludes 'low' and 'medium'."""
        # Arrange
        args = Mock(
            min_risk_level="high",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert: Only high, critical
        self.assertEqual(len(result), 2)
        risk_levels = [r["risk_level"] for r in result]
        self.assertIn("high", risk_levels)
        self.assertIn("critical", risk_levels)

    def test_min_risk_level_critical(self):
        """Min risk level 'critical' only includes critical."""
        # Arrange
        args = Mock(
            min_risk_level="critical",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert: Only critical
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["risk_level"], "critical")

    def test_verified_only(self):
        """Verified only filter."""
        # Arrange
        args = Mock(
            min_risk_level=None,
            verified_only=True,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        with patch("vscode_scanner.scanner._get_verification_status") as mock_verify:
            # Mock verification: ext1, ext2, ext5 are verified
            mock_verify.side_effect = lambda r: r["id"] in ["ext1", "ext2", "ext5"]
            result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert
        self.assertEqual(len(result), 3)
        ids = [r["id"] for r in result]
        self.assertEqual(ids, ["ext1", "ext2", "ext5"])

    def test_unverified_only(self):
        """Unverified only filter."""
        # Arrange
        args = Mock(
            min_risk_level=None,
            verified_only=False,
            unverified_only=True,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        with patch("vscode_scanner.scanner._get_verification_status") as mock_verify:
            # Mock verification: ext3, ext4 are unverified
            mock_verify.side_effect = lambda r: r["id"] not in ["ext3", "ext4"]
            result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert
        self.assertEqual(len(result), 2)
        ids = [r["id"] for r in result]
        self.assertEqual(ids, ["ext3", "ext4"])

    def test_with_vulnerabilities(self):
        """With vulnerabilities filter."""
        # Arrange
        args = Mock(
            min_risk_level=None,
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=True,
            without_vulnerabilities=False,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert: ext2, ext3, ext4 have vulnerabilities
        self.assertEqual(len(result), 3)
        ids = [r["id"] for r in result]
        self.assertEqual(ids, ["ext2", "ext3", "ext4"])

    def test_without_vulnerabilities(self):
        """Without vulnerabilities filter."""
        # Arrange
        args = Mock(
            min_risk_level=None,
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=True,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert: ext1, ext5 have no vulnerabilities
        self.assertEqual(len(result), 2)
        ids = [r["id"] for r in result]
        self.assertEqual(ids, ["ext1", "ext5"])

    def test_risk_and_verified_combined(self):
        """Risk level and verified status combined."""
        # Arrange
        args = Mock(
            min_risk_level="medium",
            verified_only=True,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        with patch("vscode_scanner.scanner._get_verification_status") as mock_verify:
            # ext2 is medium+verified
            mock_verify.side_effect = lambda r: r["id"] == "ext2"
            result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ext2")

    def test_risk_and_vulnerabilities_combined(self):
        """Risk level and vulnerability presence combined."""
        # Arrange
        args = Mock(
            min_risk_level="high",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=True,
            without_vulnerabilities=False,
        )

        # Act
        result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert: ext3 (high, 5 vulns), ext4 (critical, 10 vulns)
        self.assertEqual(len(result), 2)
        ids = [r["id"] for r in result]
        self.assertIn("ext3", ids)
        self.assertIn("ext4", ids)

    def test_all_filters_combined(self):
        """All post-scan filters combined."""
        # Arrange
        args = Mock(
            min_risk_level="medium",
            verified_only=False,
            unverified_only=True,
            with_vulnerabilities=True,
            without_vulnerabilities=False,
        )

        # Act
        with patch("vscode_scanner.scanner._get_verification_status") as mock_verify:
            # ext3, ext4 are unverified
            mock_verify.side_effect = lambda r: r["id"] not in ["ext3", "ext4"]
            result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

        # Assert: ext3 (high, unverified, 5 vulns), ext4 (critical, unverified, 10 vulns)
        self.assertEqual(len(result), 2)
        ids = [r["id"] for r in result]
        self.assertIn("ext3", ids)
        self.assertIn("ext4", ids)

    def test_filtering_summary_displayed_rich(self):
        """Filtering summary displayed with Rich."""
        # Arrange
        args = Mock(
            min_risk_level="high",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        with patch("vscode_scanner.scanner.display_info") as mock_display:
            result = _apply_post_scan_filters(self.scan_results, args, use_rich=True)

            # Assert: display_info was called with filtering summary
            mock_display.assert_called_once()
            call_args = mock_display.call_args[0][0]
            self.assertIn("Filtered out", call_args)
            self.assertIn("min risk level: high", call_args)

    def test_filtering_summary_displayed_plain(self):
        """Filtering summary displayed without Rich."""
        # Arrange
        args = Mock(
            min_risk_level="high",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        with patch("vscode_scanner.scanner.log") as mock_log:
            result = _apply_post_scan_filters(self.scan_results, args, use_rich=False)

            # Assert: log was called with filtering summary
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            self.assertIn("Filtered out", call_args[0])
            self.assertEqual(call_args[1], "INFO")

    def test_no_filtering_no_summary(self):
        """No filtering summary when no extensions filtered."""
        # Arrange: All extensions pass filters
        args = Mock(
            min_risk_level="low",
            verified_only=False,
            unverified_only=False,
            with_vulnerabilities=False,
            without_vulnerabilities=False,
        )

        # Act
        with patch("vscode_scanner.scanner.display_info") as mock_display:
            result = _apply_post_scan_filters(self.scan_results, args, use_rich=True)

            # Assert: No filtering summary displayed
            mock_display.assert_not_called()


# Integration test removed - complex mocking required for run_scan
# Filter functions tested comprehensively above (28 tests)
# Integration is validated in existing test_scanner.py and test_integration.py


# ============================================================================
# Additional Filter Tests from test_scanner.py (14 tests)
# ============================================================================
# FROM: test_scanner.py (lines 153-564)


@pytest.mark.unit
class TestApplyPreScanFilters(unittest.TestCase):
    """Test pre-scan filtering logic."""

    def setUp(self):
        """Set up test data."""
        from vscode_scanner import scanner

        self.scanner = scanner
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

        result = self.scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 4)

    def test_publisher_filter(self):
        """Test filtering by publisher."""

        class Args:
            publisher = "microsoft"
            include_ids = None
            exclude_ids = None

        result = self.scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 2)
        self.assertTrue(all(ext["publisher"] == "microsoft" for ext in result))

    def test_include_ids_filter(self):
        """Test filtering by include IDs."""

        class Args:
            publisher = None
            include_ids = "microsoft.python,esbenp.prettier"
            exclude_ids = None

        result = self.scanner._apply_pre_scan_filters(self.extensions, Args())
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

        result = self.scanner._apply_pre_scan_filters(self.extensions, Args())
        self.assertEqual(len(result), 2)
        ids = [ext["id"] for ext in result]
        self.assertNotIn("microsoft.python", ids)
        self.assertNotIn("microsoft.vscode", ids)


@pytest.mark.unit
class TestApplyPostScanFilters(unittest.TestCase):
    """Test post-scan filtering logic (risk level)."""

    def setUp(self):
        """Set up test data."""
        from vscode_scanner import scanner

        self.scanner = scanner
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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
        from vscode_scanner import scanner

        self.scanner = scanner
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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

        result = self.scanner._apply_post_scan_filters(
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
        self.assertTrue(self.scanner._get_verification_status(result_verified_metadata))

        # Unverified in metadata
        result_unverified_metadata = {
            "publisher": "yzane",
            "metadata": {
                "publisher": {"id": "yzane", "verified": False}  # ← Should use this
            },
        }
        self.assertFalse(
            self.scanner._get_verification_status(result_unverified_metadata)
        )

        # No metadata (fallback to top-level publisher dict - rare case)
        result_toplevel_verified = {"publisher": {"id": "some-pub", "verified": True}}
        self.assertTrue(self.scanner._get_verification_status(result_toplevel_verified))

        # String publisher only (no metadata)
        result_string_only = {"publisher": "local"}
        self.assertFalse(self.scanner._get_verification_status(result_string_only))

        # Empty result
        result_empty = {}
        self.assertFalse(self.scanner._get_verification_status(result_empty))


if __name__ == "__main__":
    unittest.main()
