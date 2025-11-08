#!/usr/bin/env python3
"""
Integration Tests for VS Code Extension Scanner

Tests the complete workflow from extension discovery to output generation,
including caching and API integration.
"""

import sys
import os
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest

# Module-level marker for all tests in this file
pytestmark = pytest.mark.integration

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vscode_scanner.extension_discovery import ExtensionDiscovery
from vscode_scanner.vscan_api import VscanAPIClient
from vscode_scanner.output_formatter import OutputFormatter
from vscode_scanner.cache_manager import CacheManager


class MockVscanAPI:
    """Mock vscan.dev API for testing."""

    def __init__(self):
        self.calls = []
        self.scan_count = 0

    def scan_extension(self, publisher, name, version, progress_callback=None):
        """Mock scan_extension method."""
        self.calls.append(("scan", publisher, name, version))
        self.scan_count += 1

        # Simulate API response
        if progress_callback:
            progress_callback("analyzing")
            progress_callback("completed")

        # Return mock result
        return {
            "name": name,
            "id": f"{publisher}.{name}",
            "version": version,
            "publisher": publisher,
            "publisher_verified": True,
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {
                "count": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0,
            },
            "dependencies_count": 5,
            "risk_factors_count": 1,
            "last_updated": "2024-10-01",
            "vscan_url": f"https://vscan.dev/extension/{publisher}.{name}",
            "scan_status": "success",
            "metadata": {
                "publisher": {
                    "verified": True,
                    "domain": "example.com",
                    "reputation": 95,
                }
            },
            "dependencies": {"total_count": 5},
            "risk_factors": [
                {
                    "type": "network_access",
                    "severity": "low",
                    "description": "Extension makes network requests",
                }
            ],
        }


def create_mock_extension(tmpdir, publisher, name, version):
    """Create a mock extension directory with package.json."""
    ext_dir = Path(tmpdir) / f"{publisher}.{name}-{version}"
    ext_dir.mkdir(parents=True, exist_ok=True)

    package_json = {
        "name": name,
        "publisher": publisher,
        "version": version,
        "displayName": f"{name.title()} Extension",
        "description": f"Mock extension {name}",
        "engines": {"vscode": "^1.60.0"},
    }

    with open(ext_dir / "package.json", "w") as f:
        json.dump(package_json, f)

    return ext_dir


def test_full_scan_workflow():
    """Test complete scan workflow from discovery to output."""
    print("TEST 1: Full scan workflow")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock extensions directory
        extensions_dir = Path(tmpdir) / "extensions"
        extensions_dir.mkdir()

        # Create 3 mock extensions
        create_mock_extension(extensions_dir, "microsoft", "python", "1.0.0")
        create_mock_extension(extensions_dir, "ms-vscode", "cpptools", "2.0.0")
        create_mock_extension(extensions_dir, "dbaeumer", "vscode-eslint", "3.0.0")

        print(f"✓ Created 3 mock extensions in {extensions_dir}")

        # Create cache directory
        cache_dir = Path(tmpdir) / ".vscan"

        # Test discovery
        discovery = ExtensionDiscovery(custom_dir=str(extensions_dir))
        extensions = discovery.discover_extensions()

        assert len(extensions) == 3, f"Expected 3 extensions, found {len(extensions)}"
        print(f"✓ Discovered {len(extensions)} extensions")

        # Test scanning with mock API
        mock_api = MockVscanAPI()
        cache = CacheManager(cache_dir=str(cache_dir))

        results = []
        for ext in extensions:
            result = mock_api.scan_extension(
                ext["publisher"], ext["name"], ext["version"]
            )
            results.append(result)

            # Cache the result
            cache.save_result(ext["id"], ext["version"], result)

        assert len(results) == 3, "Expected 3 scan results"
        assert mock_api.scan_count == 3, "Expected 3 API calls"
        print(f"✓ Scanned {len(results)} extensions")

        # Test output formatting (all scans are now comprehensive/detailed)
        formatter = OutputFormatter()
        scan_timestamp = datetime.now().isoformat()
        output = formatter.format_output(
            results,
            scan_timestamp=scan_timestamp,
            scan_duration=10.5,
            cache_stats={"from_cache": 0, "fresh_scans": 3, "cache_hit_rate": 0.0},
        )

        assert output["schema_version"] == "4.1", "Expected schema version 4.1"
        assert output["summary"]["total_extensions_scanned"] == 3
        assert len(output["extensions"]) == 3
        print("✓ Generated JSON output")

        # Test JSON serialization
        json_str = json.dumps(output, indent=2)
        assert len(json_str) > 0, "JSON output should not be empty"
        print("✓ JSON output is valid")

        print()


def test_cache_hit_workflow():
    """Test that cached results are used and no API calls are made."""
    print("TEST 2: Cache hit workflow")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / ".vscan"
        cache = CacheManager(cache_dir=str(cache_dir))

        # Pre-populate cache
        test_result = {
            "name": "python",
            "id": "ms-python.python",
            "version": "1.0.0",
            "publisher": "ms-python",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
            "scan_status": "success",
            "metadata": {"publisher": {"verified": True}},
            "dependencies": {"total_count": 5},
            "risk_factors": [],
        }

        cache.save_result("ms-python.python", "1.0.0", test_result)
        print("✓ Populated cache with test result")

        # Retrieve from cache
        cached = cache.get_cached_result("ms-python.python", "1.0.0", max_age_days=7)

        assert cached is not None, "Should retrieve cached result"
        assert cached["_cache_hit"] is True, "Should be marked as cache hit"
        assert cached["name"] == "python", "Cached data should match"
        print("✓ Retrieved result from cache")

        # Verify cache stats
        stats = cache.get_cache_stats()
        assert stats["total_entries"] == 1, "Should have 1 cached entry"
        print(f"✓ Cache stats: {stats['total_entries']} entries")

        # Simulate scan with cached results (no API calls)
        mock_api = MockVscanAPI()

        # Check cache first
        result = cache.get_cached_result("ms-python.python", "1.0.0")
        if result is None:
            # Only call API if not cached
            result = mock_api.scan_extension("ms-python", "python", "1.0.0")

        assert mock_api.scan_count == 0, "Should not make API calls when cached"
        assert result is not None, "Should have result from cache"
        print("✓ No API calls made for cached extensions")

        print()


def test_cache_miss_and_save():
    """Test cache miss triggers API call and result is cached."""
    print("TEST 3: Cache miss and save workflow")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / ".vscan"
        cache = CacheManager(cache_dir=str(cache_dir))
        mock_api = MockVscanAPI()

        # Try to get non-existent result from cache
        cached = cache.get_cached_result("test.extension", "1.0.0")
        assert cached is None, "Should not find result in cache"
        print("✓ Cache miss detected")

        # Make API call
        result = mock_api.scan_extension("test", "extension", "1.0.0")
        assert mock_api.scan_count == 1, "Should make 1 API call"
        print("✓ Made API call for uncached extension")

        # Save to cache
        cache.save_result("test.extension", "1.0.0", result)
        print("✓ Saved result to cache")

        # Verify it's now cached
        cached = cache.get_cached_result("test.extension", "1.0.0")
        assert cached is not None, "Should now be in cache"
        assert cached["_cache_hit"] is True
        print("✓ Verified result is cached")

        # Second request should hit cache
        mock_api2 = MockVscanAPI()
        cached2 = cache.get_cached_result("test.extension", "1.0.0")
        if cached2 is None:
            result2 = mock_api2.scan_extension("test", "extension", "1.0.0")

        assert mock_api2.scan_count == 0, "Should use cache, not API"
        print("✓ Second request used cache")

        print()


def test_output_modes():
    """Test standard and detailed output modes."""
    print("TEST 4: Output mode formatting")
    print("-" * 50)

    # Mock result data
    results = [
        {
            "name": "python",
            "id": "ms-python.python",
            "version": "1.0.0",
            "publisher": "ms-python",
            "publisher_verified": True,
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {
                "count": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0,
            },
            "dependencies_count": 5,
            "risk_factors_count": 1,
            "scan_status": "success",
            "metadata": {
                "description": "Python support",
                "publisher": {"verified": True, "domain": "microsoft.com"},
            },
            "dependencies": {"total_count": 5},
            "risk_factors": [{"type": "network", "severity": "low"}],
        }
    ]

    cache_stats = {"from_cache": 1, "fresh_scans": 0, "cache_hit_rate": 100.0}
    scan_timestamp = datetime.now().isoformat()

    # All scans are now comprehensive/detailed (v3.0+)
    formatter = OutputFormatter()
    output = formatter.format_output(
        results,
        scan_timestamp=scan_timestamp,
        scan_duration=5.0,
        cache_stats=cache_stats,
    )

    assert output["output_mode"] == "detailed"
    assert "description" in output["extensions"][0]
    # All scans include comprehensive fields
    assert "keywords" in output["extensions"][0]
    assert "homepage_url" in output["extensions"][0]
    print("✓ All scans now include comprehensive/detailed fields (v3.0+)")

    # Verify output is valid JSON
    json.dumps(output)
    print("✓ Output is valid JSON")

    print()


def test_error_handling():
    """Test error handling in scan workflow."""
    print("TEST 5: Error handling")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test invalid extensions directory
        discovery = ExtensionDiscovery(custom_dir="/nonexistent/path")

        try:
            discovery.discover_extensions()
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError as e:
            assert "not found" in str(e).lower()
            print("✓ Handles invalid extensions directory")

        # Test malformed package.json
        extensions_dir = Path(tmpdir) / "extensions"
        extensions_dir.mkdir()

        bad_ext_dir = extensions_dir / "bad.extension-1.0.0"
        bad_ext_dir.mkdir()

        # Create invalid JSON
        with open(bad_ext_dir / "package.json", "w") as f:
            f.write("{ invalid json }")

        discovery = ExtensionDiscovery(custom_dir=str(extensions_dir))
        extensions = discovery.discover_extensions()

        # Should skip malformed extension
        assert len(extensions) == 0, "Should skip malformed extensions"
        print("✓ Skips malformed package.json files")

        # Test cache error handling
        cache_dir = Path(tmpdir) / ".vscan"
        cache = CacheManager(cache_dir=str(cache_dir))

        # Try to save result with missing required fields
        invalid_result = {"name": "test", "scan_status": "error"}  # Failed scan

        # Should not raise error, just skip caching
        cache.save_result("test.extension", "1.0.0", invalid_result)
        print("✓ Handles failed scan results gracefully")

        # Verify it wasn't cached
        cached = cache.get_cached_result("test.extension", "1.0.0")
        assert cached is None, "Failed scans should not be cached"
        print("✓ Failed scans are not cached")

        print()


def test_cache_cleanup():
    """Test cache cleanup operations."""
    print("TEST 6: Cache cleanup operations")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / ".vscan"
        cache = CacheManager(cache_dir=str(cache_dir))

        # Add test results
        for i in range(5):
            result = {
                "name": f"extension{i}",
                "version": "1.0.0",
                "scan_status": "success",
                "security_score": 80,
                "risk_level": "low",
                "vulnerabilities": {"count": 0},
                "metadata": {"publisher": {"verified": True}},
                "dependencies": {"total_count": 0},
                "risk_factors": [],
            }
            cache.save_result(f"test.extension{i}", "1.0.0", result)

        stats = cache.get_cache_stats()
        assert stats["total_entries"] == 5, "Should have 5 cached entries"
        print(f"✓ Created {stats['total_entries']} cache entries")

        # Test clear cache
        cleared = cache.clear_cache()
        assert cleared == 5, "Should clear 5 entries"
        print(f"✓ Cleared {cleared} cache entries")

        stats = cache.get_cache_stats()
        assert stats["total_entries"] == 0, "Cache should be empty"
        print("✓ Cache is empty after clear")

        print()


def test_extension_metadata_parsing():
    """Test extension metadata extraction."""
    print("TEST 7: Extension metadata parsing")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as tmpdir:
        extensions_dir = Path(tmpdir) / "extensions"
        extensions_dir.mkdir()

        # Create extension with full metadata
        ext_dir = create_mock_extension(
            extensions_dir, "microsoft", "python", "2024.10.0"
        )

        # Add additional metadata
        with open(ext_dir / "package.json", "r") as f:
            package = json.load(f)

        package["displayName"] = "Python"
        package["description"] = "Python language support"
        package["repository"] = {"url": "https://github.com/microsoft/vscode-python"}

        with open(ext_dir / "package.json", "w") as f:
            json.dump(package, f)

        # Discover and parse
        discovery = ExtensionDiscovery(custom_dir=str(extensions_dir))
        extensions = discovery.discover_extensions()

        assert len(extensions) == 1
        ext = extensions[0]

        assert ext["name"] == "python"
        assert ext["publisher"] == "microsoft"
        assert ext["version"] == "2024.10.0"
        assert ext["id"] == "microsoft.python"
        assert ext["display_name"] == "Python"
        print("✓ Extracted all metadata fields correctly")

        print()


def main():
    """Run all integration tests."""
    print("=" * 50)
    print("Integration Tests")
    print("=" * 50)
    print()

    try:
        test_full_scan_workflow()
        test_cache_hit_workflow()
        test_cache_miss_and_save()
        test_output_modes()
        test_error_handling()
        test_cache_cleanup()
        test_extension_metadata_parsing()

        print("=" * 50)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("=" * 50)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
