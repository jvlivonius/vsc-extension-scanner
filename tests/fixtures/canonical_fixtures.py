#!/usr/bin/env python3
"""
Canonical test fixtures for vsc-extension-scanner test suite.

This module provides a single source of truth for test data used across
multiple test files. All fixtures are based on real extension data but
simplified for testing purposes.

Usage:
    from tests.fixtures.canonical_fixtures import (
        sample_extension,
        sample_scan_result_success,
        mock_api_client,
    )
"""

import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock

# ============================================================================
# Extension Data Fixtures
# ============================================================================


@pytest.fixture
def sample_extension() -> Dict:
    """Sample VS Code extension metadata.

    Returns a typical extension with verified publisher and common fields.
    """
    return {
        "id": "ms-python.python",
        "version": "2024.1.0",
        "publisher": "ms-python",
        "name": "python",
        "display_name": "Python",
        "publisher_domain": "microsoft.com",
        "verified": True,
        "install_count": 50000000,
        "last_updated": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_extension_list() -> List[Dict]:
    """List of sample extensions covering different scenarios.

    Includes:
    - Verified publisher (Microsoft Python)
    - Unverified publisher (test extension)
    - High-risk extension (risky extension)
    """
    return [
        # Verified publisher, no vulnerabilities
        {
            "id": "ms-python.python",
            "publisher": "ms-python",
            "name": "python",
            "display_name": "Python",
            "version": "2024.1.0",
            "verified": True,
            "install_count": 50000000,
        },
        # Unverified publisher, has vulnerabilities
        {
            "id": "test-publisher.test-extension",
            "publisher": "test-publisher",
            "name": "test-extension",
            "display_name": "Test Extension",
            "version": "1.0.0",
            "verified": False,
            "install_count": 1000,
        },
        # High risk extension
        {
            "id": "risky.extension",
            "publisher": "risky",
            "name": "extension",
            "display_name": "Risky Extension",
            "version": "0.1.0",
            "verified": False,
            "install_count": 100,
        },
    ]


@pytest.fixture
def minimal_extension() -> Dict:
    """Minimal extension with only required fields."""
    return {
        "id": "minimal.ext",
        "version": "1.0.0",
        "publisher": "minimal",
        "name": "ext",
    }


# ============================================================================
# API Response Fixtures
# ============================================================================


@pytest.fixture
def sample_scan_result_success() -> Dict:
    """Successful scan result with no vulnerabilities."""
    return {
        "scan_status": "success",
        "risk_level": "low",
        "vulnerabilities": {
            "count": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
        "analysis_id": "test-analysis-123",
        "scanned_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_scan_result_with_vulns() -> Dict:
    """Scan result with vulnerabilities (critical + high severity)."""
    return {
        "scan_status": "success",
        "risk_level": "high",
        "vulnerabilities": {
            "count": 3,
            "critical": 1,
            "high": 2,
            "medium": 0,
            "low": 0,
            "details": [
                {
                    "id": "VULN-001",
                    "severity": "critical",
                    "description": "Remote code execution vulnerability",
                },
                {
                    "id": "VULN-002",
                    "severity": "high",
                    "description": "Unauthorized data access",
                },
                {
                    "id": "VULN-003",
                    "severity": "high",
                    "description": "Insecure dependency",
                },
            ],
        },
        "analysis_id": "test-analysis-456",
        "scanned_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_scan_result_error() -> Dict:
    """Error scan result (analysis failed)."""
    return {
        "scan_status": "error",
        "error_type": "analysis_failed",
        "error_message": "Failed to analyze extension",
        "analysis_id": None,
    }


@pytest.fixture
def sample_scan_result_medium_risk() -> Dict:
    """Scan result with medium-severity vulnerabilities."""
    return {
        "scan_status": "success",
        "risk_level": "medium",
        "vulnerabilities": {
            "count": 2,
            "critical": 0,
            "high": 0,
            "medium": 2,
            "low": 0,
        },
        "analysis_id": "test-analysis-789",
        "scanned_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Mock API Client Fixtures
# ============================================================================


@pytest.fixture
def mock_api_client(mocker, sample_scan_result_success):
    """Pre-configured mock API client with realistic behavior.

    Returns a mock that succeeds with a clean scan result.
    """
    client = mocker.Mock()
    client.scan_extension.return_value = sample_scan_result_success
    client.delay = 1.5
    client.timeout = 30
    return client


@pytest.fixture
def mock_api_client_with_retries(mocker, sample_scan_result_success):
    """Mock API client that succeeds after retries.

    First two calls fail with temporary errors, third call succeeds.
    """
    client = mocker.Mock()
    # First two calls fail, third succeeds
    client.scan_extension.side_effect = [
        Exception("Temporary error"),
        Exception("Temporary error"),
        sample_scan_result_success,
    ]
    client.delay = 1.5
    client.timeout = 30
    return client


@pytest.fixture
def mock_api_client_with_vulns(mocker, sample_scan_result_with_vulns):
    """Mock API client that returns vulnerabilities."""
    client = mocker.Mock()
    client.scan_extension.return_value = sample_scan_result_with_vulns
    client.delay = 1.5
    client.timeout = 30
    return client


@pytest.fixture
def mock_api_client_error(mocker, sample_scan_result_error):
    """Mock API client that returns an error."""
    client = mocker.Mock()
    client.scan_extension.return_value = sample_scan_result_error
    client.delay = 1.5
    client.timeout = 30
    return client


# ============================================================================
# Cache Fixtures
# ============================================================================


@pytest.fixture
def temp_cache_dir(tmp_path) -> Path:
    """Temporary cache directory for testing.

    Creates a clean, isolated cache directory for each test.
    """
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


@pytest.fixture
def sample_cache_entry() -> Dict:
    """Sample cache entry with HMAC signature.

    Includes all fields stored in the cache database.
    """
    return {
        "extension_id": "ms-python.python",
        "version": "2024.1.0",
        "risk_level": "low",
        "vulnerabilities_count": 0,
        "scan_status": "success",
        "scanned_at": "2024-01-01T00:00:00Z",
        "analysis_id": "test-analysis-123",
        "hmac_signature": "test-signature-abc123",
    }


# ============================================================================
# Progress Callback Fixtures
# ============================================================================


@pytest.fixture
def mock_progress_callback(mocker):
    """Mock progress callback for scanner testing.

    Tracks calls to update() method for verification.
    """
    callback = mocker.Mock()
    callback.update = mocker.Mock()
    return callback


# ============================================================================
# Display and Output Fixtures
# ============================================================================


@pytest.fixture
def sample_scan_results_for_display() -> List[Dict]:
    """Complete scan results formatted for display/output.

    Includes extensions with various risk levels and statuses.
    """
    return [
        {
            "id": "ms-python.python",
            "publisher": "ms-python",
            "name": "python",
            "display_name": "Python",
            "version": "2024.1.0",
            "verified": True,
            "scan_status": "success",
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
        },
        {
            "id": "test.vulnerable",
            "publisher": "test",
            "name": "vulnerable",
            "display_name": "Vulnerable Extension",
            "version": "1.0.0",
            "verified": False,
            "scan_status": "success",
            "risk_level": "high",
            "vulnerabilities": {"count": 3, "critical": 1, "high": 2},
        },
        {
            "id": "test.failed",
            "publisher": "test",
            "name": "failed",
            "display_name": "Failed Extension",
            "version": "1.0.0",
            "verified": False,
            "scan_status": "error",
            "error_type": "analysis_failed",
        },
    ]


@pytest.fixture
def sample_summary_stats() -> Dict:
    """Sample summary statistics for display."""
    return {
        "total_extensions_scanned": 10,
        "vulnerabilities_found": 2,
        "successful_scans": 8,
        "failed_scans": 2,
        "cached_results": 5,
        "fresh_scans": 5,
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def sample_config() -> Dict:
    """Sample configuration dictionary."""
    return {
        "scan": {
            "delay": 1.5,
            "timeout": 30,
            "workers": 3,
        },
        "cache": {
            "enabled": True,
            "max_age_days": 7,
        },
        "output": {
            "format": "json",
            "quiet": False,
        },
    }


# ============================================================================
# Statistics Fixtures
# ============================================================================


@pytest.fixture
def sample_stats() -> Dict:
    """Sample scan statistics dictionary."""
    from unittest.mock import MagicMock

    return {
        "vulnerabilities_found": 0,
        "successful_scans": 1,
        "failed_scans": 0,
        "cached_results": 0,
        "fresh_scans": 1,
        "api_client": MagicMock(),
    }


@pytest.fixture
def sample_stats_with_vulns() -> Dict:
    """Sample scan statistics with vulnerabilities."""
    from unittest.mock import MagicMock

    return {
        "vulnerabilities_found": 3,
        "successful_scans": 1,
        "failed_scans": 0,
        "cached_results": 0,
        "fresh_scans": 1,
        "api_client": MagicMock(),
    }


# ============================================================================
# Helper Functions (Factory Methods)
# ============================================================================


def create_mock_extension(
    extension_id: str = "test.extension",
    version: str = "1.0.0",
    publisher: str = "test",
    name: str = "extension",
) -> Dict:
    """
    Create a mock extension dictionary with customizable values.

    Args:
        extension_id: Extension ID (publisher.name format)
        version: Version string
        publisher: Publisher name
        name: Extension name

    Returns:
        Dictionary representing an extension
    """
    return {
        "id": extension_id,
        "version": version,
        "name": name,
        "publisher": publisher,
        "display_name": f"{publisher.title()} {name.title()}",
    }


def create_mock_scan_result(
    extension_id: str = "test.extension",
    risk_level: str = "low",
    vuln_count: int = 0,
    status: str = "success",
) -> Dict:
    """
    Create a mock scan result dictionary with customizable values.

    Args:
        extension_id: Extension ID
        risk_level: Risk level (low, medium, high, critical)
        vuln_count: Number of vulnerabilities
        status: Scan status

    Returns:
        Dictionary representing a scan result
    """
    return {
        "id": extension_id,
        "risk_level": risk_level,
        "vulnerabilities": {"count": vuln_count},
        "scan_status": status,
        "scanned_at": datetime.utcnow().isoformat(),
    }


def create_mock_stats(
    vulns_found: int = 0,
    successful: int = 1,
    failed: int = 0,
    cached: int = 0,
    fresh: int = 1,
) -> Dict:
    """
    Create a mock statistics dictionary with customizable values.

    Args:
        vulns_found: Number of vulnerabilities found
        successful: Number of successful scans
        failed: Number of failed scans
        cached: Number of cached results
        fresh: Number of fresh scans

    Returns:
        Dictionary representing scan statistics
    """
    from unittest.mock import MagicMock

    return {
        "vulnerabilities_found": vulns_found,
        "successful_scans": successful,
        "failed_scans": failed,
        "cached_results": cached,
        "fresh_scans": fresh,
        "api_client": MagicMock(),
    }
