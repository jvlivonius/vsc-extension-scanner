"""
Shared fixtures for scanner test modules.

Provides common mock objects, test data, and helper functions used across
multiple scanner test files to reduce duplication and improve maintainability.
"""

import pytest
from unittest.mock import MagicMock
from pathlib import Path
from datetime import datetime
from typing import Dict, List


# ============================================================================
# Extension Data Fixtures
# ============================================================================


@pytest.fixture
def sample_extension() -> Dict:
    """Single sample extension for basic tests."""
    return {
        "id": "test.extension",
        "version": "1.0.0",
        "name": "extension",
        "publisher": "test",
        "display_name": "Test Extension",
    }


@pytest.fixture
def sample_extensions_list() -> List[Dict]:
    """List of sample extensions covering various scenarios."""
    return [
        {
            "id": "ms-python.python",
            "version": "2024.1.0",
            "name": "python",
            "publisher": "ms-python",
            "display_name": "Python",
        },
        {
            "id": "test.extension",
            "version": "1.0.0",
            "name": "extension",
            "publisher": "test",
            "display_name": "Test Extension",
        },
        {
            "id": "risky.extension",
            "version": "0.1.0",
            "name": "extension",
            "publisher": "risky",
            "display_name": "Risky Extension",
        },
    ]


# ============================================================================
# Scan Result Fixtures
# ============================================================================


@pytest.fixture
def sample_scan_result_success() -> Dict:
    """Successful scan result with no vulnerabilities."""
    return {
        "id": "test.extension",
        "risk_level": "low",
        "vulnerabilities": {
            "count": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
        "scan_status": "success",
        "scanned_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_scan_result_with_vulns() -> Dict:
    """Scan result with vulnerabilities."""
    return {
        "id": "test.extension",
        "risk_level": "high",
        "vulnerabilities": {
            "count": 3,
            "critical": 1,
            "high": 2,
            "medium": 0,
            "low": 0,
        },
        "scan_status": "success",
        "scanned_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_scan_results_list() -> List[Dict]:
    """List of scan results with mixed risk levels."""
    return [
        {
            "id": "test.ext1",
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
            "scan_status": "success",
        },
        {
            "id": "test.ext2",
            "risk_level": "high",
            "vulnerabilities": {"count": 3, "critical": 1, "high": 2},
            "scan_status": "success",
        },
        {
            "id": "test.ext3",
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
            "scan_status": "success",
        },
    ]


# ============================================================================
# Statistics Fixtures
# ============================================================================


@pytest.fixture
def sample_stats() -> Dict:
    """Sample scan statistics dictionary."""
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
    return {
        "vulnerabilities_found": 3,
        "successful_scans": 1,
        "failed_scans": 0,
        "cached_results": 0,
        "fresh_scans": 1,
        "api_client": MagicMock(),
    }


# ============================================================================
# Mock Objects
# ============================================================================


@pytest.fixture
def mock_extensions_path() -> Path:
    """Mock extensions directory path."""
    return Path("/fake/extensions/path")


@pytest.fixture
def mock_api_client():
    """Mock API client with common configuration."""
    mock_client = MagicMock()
    mock_client.scan_extension.return_value = {
        "scan_status": "success",
        "risk_level": "low",
        "vulnerabilities": {"count": 0},
    }
    return mock_client


# ============================================================================
# Helper Functions
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
    return {
        "vulnerabilities_found": vulns_found,
        "successful_scans": successful,
        "failed_scans": failed,
        "cached_results": cached,
        "fresh_scans": fresh,
        "api_client": MagicMock(),
    }
