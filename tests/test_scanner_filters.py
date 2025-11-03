"""
Comprehensive filter tests for scanner.py

Tests filter combinations and edge cases to improve coverage from 64.91% to 75%+.
Focuses on pre-scan filters (publisher, include/exclude IDs) and post-scan filters
(risk level, verification status, vulnerabilities).
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from vscode_scanner.scanner import (
    _apply_pre_scan_filters,
    _apply_post_scan_filters,
    run_scan,
)


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


if __name__ == "__main__":
    unittest.main()
