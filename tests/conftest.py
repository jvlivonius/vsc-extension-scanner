"""
Shared Test Fixtures for VS Code Extension Scanner

This module provides pytest fixtures that can be used across all test files.
Fixtures handle setup and teardown automatically, reducing code duplication
and ensuring consistent test environments.

Usage:
    def test_something(temp_cache_dir, mock_vscan_api):
        # Fixtures are automatically provided
        cache = CacheManager(cache_dir=temp_cache_dir)
        # mock_vscan_api is already patched

Created: 2025-10-24 (Phase 4.0: Test Infrastructure)
Updated: 2025-01-04 (Phase 1.4: Integrated with canonical_fixtures)

Note: Core test data fixtures (extensions, scan results, etc.) are now
      provided by tests/fixtures/canonical_fixtures.py. This conftest.py
      focuses on test infrastructure fixtures (temp directories, API mocks).
"""

import pytest
import tempfile
import shutil
import uuid
from pathlib import Path
from typing import Generator
from unittest import mock
import functools

# Store original tempfile functions before patching
_original_mkdtemp = tempfile.mkdtemp
_original_TemporaryDirectory = tempfile.TemporaryDirectory


# Pytest Configuration for temp directory handling (v3.7.2+)
@pytest.fixture(autouse=True, scope="function")
def _patch_tempfile_for_cache_tests(monkeypatch):
    """
    Automatically patch tempfile functions to use home directory for all tests.

    This ensures cache directories are never created in system temp (/tmp, /var/folders)
    which would be blocked by validate_path() security checks in v3.7.2+.

    Applied automatically to all test functions.
    """

    def home_mkdtemp(suffix="", prefix="vscan_test_", dir=None):
        """Replacement for tempfile.mkdtemp() that uses home directory."""
        try:
            home = Path.home()
            # Check if home directory actually exists (may be mocked in tests)
            if home.exists():
                unique_name = f"{prefix}{uuid.uuid4().hex[:8]}{suffix}"
                tmpdir = home / unique_name
                tmpdir.mkdir(parents=True, exist_ok=True)
                return str(tmpdir)
        except (OSError, PermissionError, FileNotFoundError):
            pass
        # Fallback to original tempfile.mkdtemp if home directory is mocked/unavailable
        return _original_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

    # Patch tempfile.mkdtemp to use home directory
    monkeypatch.setattr(tempfile, "mkdtemp", home_mkdtemp)

    # Patch tempfile.TemporaryDirectory to use HomeTempDirectory
    monkeypatch.setattr(tempfile, "TemporaryDirectory", HomeTempDirectory)


# Import canonical fixtures for reuse (Phase 1.4)
# These can be used directly in tests via pytest's fixture discovery
# Helper functions for creating home-directory-based temp cache (v3.7.2+)
def create_temp_cache_dir() -> Path:
    """
    Create a temporary cache directory in home directory.

    This is a helper for tests that don't use fixtures or need multiple temp caches.
    Returns a Path that should be cleaned up by the caller using shutil.rmtree().

    Returns:
        Path: Temporary directory in home directory

    Example:
        tmpdir = create_temp_cache_dir()
        try:
            cache = CacheManager(cache_dir=str(tmpdir))
            # Use cache...
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
    """
    home = Path.home()
    tmpdir = home / f".vscan_test_cache_{uuid.uuid4().hex[:8]}"
    tmpdir.mkdir(parents=True, exist_ok=True)
    return tmpdir


class HomeTempDirectory:
    """
    Context manager for temporary cache directories in home directory.

    Drop-in replacement for tempfile.TemporaryDirectory() that uses home directory
    instead of system temp. This avoids validate_path() blocking cache in temp.

    Example:
        with HomeTempDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)
            # Use cache...
        # tmpdir is automatically cleaned up
    """

    def __init__(self):
        self.name = None

    def __enter__(self) -> str:
        self.name = str(create_temp_cache_dir())
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.name and Path(self.name).exists():
            shutil.rmtree(self.name, ignore_errors=True)
        return False


from fixtures.canonical_fixtures import (
    sample_extension,
    sample_extension_list,
    minimal_extension,
    sample_scan_result_success,
    sample_scan_result_with_vulns,
    sample_scan_result_error,
    mock_api_client,
    create_mock_extension,
    create_mock_scan_result,
)

# Re-export canonical fixtures so they're available to all tests
# (pytest autodiscovers them through conftest.py)
__all__ = [
    "sample_extension",
    "sample_extension_list",
    "minimal_extension",
    "sample_scan_result_success",
    "sample_scan_result_with_vulns",
    "sample_scan_result_error",
    "mock_api_client",
    "create_mock_extension",
    "create_mock_scan_result",
]


@pytest.fixture
def temp_cache_dir() -> Generator[Path, None, None]:
    """
    Provide a temporary cache directory for tests.

    Uses home directory instead of system temp (/tmp, /var) to ensure:
    - Cross-platform compatibility (macOS, Linux, Windows)
    - Avoids validate_path() blocking cache in temp locations (v3.7.2+)
    - Matches production cache default location (~/.vscan)

    Note: System temp (/tmp on Linux, /var/folders on macOS) is blocked
    for cache directories to prevent persistent data in ephemeral locations.

    Automatically creates a temporary directory before the test
    and cleans it up after the test completes.

    Yields:
        Path: Temporary directory path in home directory

    Example:
        def test_cache_operations(temp_cache_dir):
            cache = CacheManager(cache_dir=temp_cache_dir)
            # Use cache...
            # temp_cache_dir is automatically cleaned up
    """
    # Use home directory for test cache (not system temp)
    home = Path.home()
    tmpdir = home / f".vscan_test_cache_{uuid.uuid4().hex[:8]}"
    tmpdir.mkdir(parents=True, exist_ok=True)
    try:
        yield tmpdir
    finally:
        # Cleanup after test
        if tmpdir.exists():
            shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def sample_extensions_dir() -> Path:
    """
    Provide path to sample extensions directory for testing.

    Returns:
        Path: Path to tests/fixtures/sample_extensions/

    Example:
        def test_extension_discovery(sample_extensions_dir):
            extensions = discover_extensions(sample_extensions_dir)
            assert len(extensions) > 0
    """
    fixtures_dir = Path(__file__).parent / "fixtures" / "sample_extensions"

    # Create fixtures directory if it doesn't exist
    if not fixtures_dir.exists():
        fixtures_dir.mkdir(parents=True, exist_ok=True)

    return fixtures_dir


@pytest.fixture
def mock_vscan_api():
    """
    Mock vscan.dev API responses for testing without network calls.

    Patches vscan_api.scan_extension to return mock data instead of
    making real HTTP requests.

    Yields:
        MagicMock: Mocked scan_extension function

    Example:
        def test_scanner(mock_vscan_api):
            mock_vscan_api.return_value = {
                "score": 85,
                "risk_level": "low",
                "vulnerabilities": {"total": 0}
            }
            result = perform_scan()
            assert result['extensions'][0]['security']['score'] == 85
    """
    with mock.patch(
        "vscode_scanner.vscan_api.VScanAPIClient.scan_extension"
    ) as mock_scan:
        # Default mock response
        mock_scan.return_value = {
            "security": {
                "score": 85,
                "risk_level": "low",
                "vulnerabilities": {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "moderate": 0,
                    "low": 0,
                },
            },
            "publisher": {
                "id": "test-publisher",
                "name": "Test Publisher",
                "verified": True,
            },
            "metadata": {
                "display_name": "Test Extension",
                "description": "A test extension",
            },
        }
        yield mock_scan


@pytest.fixture
def temp_output_file() -> Generator[Path, None, None]:
    """
    Provide a temporary output file for testing file generation.

    Automatically creates a temporary file and cleans it up after the test.

    Yields:
        Path: Temporary file path

    Example:
        def test_json_output(temp_output_file):
            generate_output(output_path=temp_output_file)
            assert temp_output_file.exists()
            # File is automatically cleaned up
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)

    try:
        yield temp_path
    finally:
        # Cleanup after test
        if temp_path.exists():
            temp_path.unlink()


@pytest.fixture
def mock_extension_data():
    """
    Provide sample extension data for testing.

    Returns:
        dict: Sample extension metadata

    Example:
        def test_output_formatter(mock_extension_data):
            formatted = format_extension(mock_extension_data)
            assert formatted['name'] == 'test-extension'
    """
    return {
        "name": "test-extension",
        "display_name": "Test Extension",
        "id": "test-publisher.test-extension",
        "version": "1.0.0",
        "publisher": {
            "id": "test-publisher",
            "name": "Test Publisher",
            "verified": True,
            "domain": "example.com",
            "reputation": 100,
        },
        "security": {
            "score": 85,
            "risk_level": "low",
            "vulnerabilities": {
                "total": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0,
            },
            "risk_factors": [],
            "dependencies": {"total_count": 5, "with_vulnerabilities": 0, "list": []},
        },
        "metadata": {
            "description": "A test extension for unit tests",
            "install_count": 1000,
            "rating": 4.5,
            "rating_count": 100,
            "keywords": ["test", "example"],
            "repository_url": "https://github.com/test/test-extension",
            "homepage_url": "https://github.com/test/test-extension",
            "last_updated": "2025-10-24",
        },
        "vscan_url": "https://vscan.dev/extension/test-publisher.test-extension",
        "scan_status": "success",
    }


@pytest.fixture
def reset_environment():
    """
    Reset environment variables before and after a test.

    This fixture only runs when explicitly requested by a test.
    Use this when your test modifies environment variables and needs
    a clean state.

    Example:
        def test_something(reset_environment):
            # Environment is reset before and after this test
            os.environ['TEST_VAR'] = 'value'
            # ... test code ...
    """
    # Store original environment
    import os

    original_env = dict(os.environ)

    yield  # Run the test

    # Restore original environment after test
    os.environ.clear()
    os.environ.update(original_env)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and path setup."""
    # Add project root to Python path for imports
    import sys
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Test group markers (for run_tests.py --pytest integration)
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "security: marks tests as security tests")
    config.addinivalue_line(
        "markers", "architecture: marks tests as architecture tests"
    )
    config.addinivalue_line(
        "markers", "parallel: marks tests as parallel/threading tests"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "real-api: marks tests that make real API calls")
    config.addinivalue_line("markers", "mock-validation: marks mock validation tests")

    # Additional markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
