#!/usr/bin/env python3
"""Test fixtures package for vsc-extension-scanner.

This package provides centralized, canonical test fixtures to eliminate
duplication across test files.
"""

from tests.fixtures.canonical_fixtures import (
    # Extension data
    sample_extension,
    sample_extension_list,
    minimal_extension,
    # API responses
    sample_scan_result_success,
    sample_scan_result_with_vulns,
    sample_scan_result_error,
    sample_scan_result_medium_risk,
    # Mock API clients
    mock_api_client,
    mock_api_client_with_retries,
    mock_api_client_with_vulns,
    mock_api_client_error,
    # Cache fixtures
    temp_cache_dir,
    sample_cache_entry,
    # Progress callbacks
    mock_progress_callback,
    # Display/output
    sample_scan_results_for_display,
    sample_summary_stats,
    # Configuration
    sample_config,
    # Statistics
    sample_stats,
    sample_stats_with_vulns,
    # Helper functions
    create_mock_extension,
    create_mock_scan_result,
    create_mock_stats,
)

__all__ = [
    # Extension data
    "sample_extension",
    "sample_extension_list",
    "minimal_extension",
    # API responses
    "sample_scan_result_success",
    "sample_scan_result_with_vulns",
    "sample_scan_result_error",
    "sample_scan_result_medium_risk",
    # Mock API clients
    "mock_api_client",
    "mock_api_client_with_retries",
    "mock_api_client_with_vulns",
    "mock_api_client_error",
    # Cache fixtures
    "temp_cache_dir",
    "sample_cache_entry",
    # Progress callbacks
    "mock_progress_callback",
    # Display/output
    "sample_scan_results_for_display",
    "sample_summary_stats",
    # Configuration
    "sample_config",
    # Statistics
    "sample_stats",
    "sample_stats_with_vulns",
    # Helper functions
    "create_mock_extension",
    "create_mock_scan_result",
    "create_mock_stats",
]
