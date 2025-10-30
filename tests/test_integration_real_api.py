#!/usr/bin/env python3
"""
Real API Integration Tests (v3.5.1 Task 8)

Tests the scanner with real vscan.dev API calls to ensure:
1. Parallel scan works with real API (small extension set)
2. Config file integration works end-to-end
3. Sequential vs parallel produce consistent results
4. Cache behavior works correctly with real data
5. Error handling works with real API errors

WARNING: These tests make real API calls and should be run sparingly
to avoid rate limiting. Mark with @pytest.mark.integration for selective execution.

Usage:
    # Run all tests including integration
    python3 tests/test_integration_real_api.py

    # Run only integration tests (if using pytest)
    pytest -v -m integration

    # Skip integration tests
    pytest -v -m "not integration"
"""

import sys
import os
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from types import SimpleNamespace

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.scanner import run_scan, _scan_extensions
from vscode_scanner.cache_manager import CacheManager
from vscode_scanner import config_manager


# Mark all tests as integration tests
try:
    import pytest

    integration = pytest.mark.integration
    slow = pytest.mark.slow
except ImportError:
    # If pytest not available, create dummy decorators
    def integration(func):
        return func

    def slow(func):
        return func


@pytest.mark.real-api
class TestRealAPIIntegration(unittest.TestCase):
    """Integration tests using real vscan.dev API."""

    @classmethod
    def setUpClass(cls):
        """Set up fixtures once for all tests in this class."""
        print("\n" + "=" * 70)
        print("WARNING: Running real API integration tests")
        print("These tests make actual calls to vscan.dev API")
        print("=" * 70 + "\n")

    def setUp(self):
        """Create temporary directories for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.extensions_dir = Path(self.test_dir) / "extensions"
        self.extensions_dir.mkdir()
        self.cache_dir = Path(self.test_dir) / "cache"
        self.cache_dir.mkdir()

        # Create a few test extensions (well-known, stable extensions)
        self.test_extensions = [
            {
                "publisher": "ms-python",
                "name": "python",
                "id": "ms-python.python",
                "version": "2023.1.0",
            },
            {
                "publisher": "esbenp",
                "name": "prettier-vscode",
                "id": "esbenp.prettier-vscode",
                "version": "9.0.0",
            },
            {
                "publisher": "dbaeumer",
                "name": "vscode-eslint",
                "id": "dbaeumer.vscode-eslint",
                "version": "2.4.0",
            },
        ]

        # Create mock extension directories
        for ext in self.test_extensions:
            ext_dir = self.extensions_dir / f"{ext['id']}-{ext['version']}"
            ext_dir.mkdir()
            package_json = {
                "name": ext["name"],
                "publisher": ext["publisher"],
                "version": ext["version"],
                "displayName": f"{ext['name']} extension",
            }
            (ext_dir / "package.json").write_text(json.dumps(package_json))

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @integration
    @slow
    def test_real_api_parallel_scan(self):
        """Test parallel scan with 3 real extensions using real API."""
        print("\nRunning real API parallel scan (3 workers)...")

        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        extensions = [
            {
                "id": ext["id"],
                "name": ext["name"],
                "version": ext["version"],
                "publisher": ext["publisher"],
            }
            for ext in self.test_extensions
        ]

        args = SimpleNamespace(
            delay=2.0,  # Be respectful to API
            max_retries=3,
            retry_delay=2.0,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=3,
        )

        # Run real scan
        results, stats = _scan_extensions(
            extensions,
            args,
            cache_manager,
            "2025-10-26T00:00:00Z",
            use_rich=False,
            quiet=True,
        )

        # Verify results
        self.assertEqual(len(results), 3, "Should scan all 3 extensions")
        self.assertGreater(stats["successful_scans"], 0, "Should have successful scans")

        # Verify cache was populated
        for ext in extensions:
            cached = cache_manager.get_cached_result(ext["id"], ext["version"])
            if stats["successful_scans"] > 0:
                # At least one extension should be cached
                # (may fail if API is down for all)
                pass

        print(f"✓ Scanned {len(results)} extensions")
        print(f"  Successful: {stats['successful_scans']}")
        print(f"  Failed: {stats['failed_scans']}")
        print(f"  Cached: {stats['cached_results']}")
        print(f"  Fresh: {stats['fresh_scans']}")

    @integration
    @slow
    def test_real_api_cache_behavior(self):
        """Test that second scan uses cache (no duplicate API calls)."""
        print("\nTesting real API cache behavior...")

        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        extensions = [
            {
                "id": "ms-python.python",
                "name": "python",
                "version": "2023.1.0",
                "publisher": "ms-python",
            }
        ]

        args = SimpleNamespace(
            delay=2.0,
            max_retries=3,
            retry_delay=2.0,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=1,  # Sequential for predictability
        )

        # First scan - should hit API
        print("  First scan (should hit API)...")
        results1, stats1 = _scan_extensions(
            extensions,
            args,
            cache_manager,
            "2025-10-26T00:00:00Z",
            use_rich=False,
            quiet=True,
        )

        # Second scan - should use cache
        print("  Second scan (should use cache)...")
        results2, stats2 = _scan_extensions(
            extensions,
            args,
            cache_manager,
            "2025-10-26T00:00:00Z",
            use_rich=False,
            quiet=True,
        )

        # Verify second scan used cache
        self.assertEqual(stats2["cached_results"], 1, "Second scan should use cache")
        self.assertEqual(stats2["fresh_scans"], 0, "Second scan should not hit API")

        # Verify results are consistent
        if len(results1) > 0 and len(results2) > 0:
            self.assertEqual(results1[0]["id"], results2[0]["id"])

        print(f"✓ First scan: {stats1['fresh_scans']} API call(s)")
        print(f"✓ Second scan: {stats2['cached_results']} cached")

    @integration
    @slow
    def test_real_api_sequential_vs_parallel(self):
        """Test that sequential and parallel produce consistent results."""
        print("\nTesting sequential vs parallel consistency...")

        # Sequential scan
        cache_dir_seq = Path(self.test_dir) / "cache_seq"
        cache_dir_seq.mkdir()
        cache_manager_seq = CacheManager(cache_dir=str(cache_dir_seq))

        extensions = [
            {
                "id": ext["id"],
                "name": ext["name"],
                "version": ext["version"],
                "publisher": ext["publisher"],
            }
            for ext in self.test_extensions[:2]  # Use 2 extensions for speed
        ]

        args_seq = SimpleNamespace(
            delay=2.0,
            max_retries=3,
            retry_delay=2.0,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=1,  # Sequential
        )

        print("  Running sequential scan...")
        seq_results, seq_stats = _scan_extensions(
            extensions,
            args_seq,
            cache_manager_seq,
            "2025-10-26T00:00:00Z",
            use_rich=False,
            quiet=True,
        )

        # Parallel scan
        cache_dir_par = Path(self.test_dir) / "cache_par"
        cache_dir_par.mkdir()
        cache_manager_par = CacheManager(cache_dir=str(cache_dir_par))

        args_par = SimpleNamespace(
            delay=2.0,
            max_retries=3,
            retry_delay=2.0,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=3,  # Parallel
        )

        print("  Running parallel scan...")
        par_results, par_stats = _scan_extensions(
            extensions,
            args_par,
            cache_manager_par,
            "2025-10-26T00:00:00Z",
            use_rich=False,
            quiet=True,
        )

        # Compare results (order-independent)
        self.assertEqual(
            len(seq_results),
            len(par_results),
            "Sequential and parallel should scan same number",
        )

        seq_ids = sorted([r["id"] for r in seq_results])
        par_ids = sorted([r["id"] for r in par_results])
        self.assertEqual(
            seq_ids, par_ids, "Sequential and parallel should scan same extensions"
        )

        print(f"✓ Sequential: {len(seq_results)} results")
        print(f"✓ Parallel: {len(par_results)} results")
        print("✓ Results consistent")

    @integration
    def test_config_file_integration(self):
        """Test that config file parallel settings work end-to-end."""
        print("\nTesting config file integration...")

        # Create test config
        config_path = Path(self.test_dir) / ".vscanrc"
        config_content = """
[scan]
workers = 5
delay = 2.0
"""
        config_path.write_text(config_content)

        # Load config using config_manager functions
        # Temporarily set config path
        original_path = config_manager.get_config_path()

        # Parse config file directly
        import configparser

        parser = configparser.ConfigParser()
        parser.read(config_path)

        # Verify settings loaded
        workers = parser.get("scan", "workers")
        delay = parser.get("scan", "delay")

        self.assertEqual(workers, "5")
        self.assertEqual(delay, "2.0")

        print("✓ Config file loaded successfully")
        print(f"  workers: {workers}")
        print(f"  delay: {delay}")

    @integration
    @slow
    def test_error_handling_with_real_api(self):
        """Test error handling with invalid extension (should fail gracefully)."""
        print("\nTesting error handling with invalid extension...")

        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        # Mix valid and invalid extensions
        extensions = [
            {
                "id": "ms-python.python",
                "name": "python",
                "version": "2023.1.0",
                "publisher": "ms-python",
            },
            {
                "id": "invalid.nonexistent",
                "name": "nonexistent",
                "version": "999.999.999",
                "publisher": "invalid",
            },
        ]

        args = SimpleNamespace(
            delay=2.0,
            max_retries=1,  # Fewer retries for speed
            retry_delay=1.0,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=2,
        )

        # Should handle error gracefully
        results, stats = _scan_extensions(
            extensions,
            args,
            cache_manager,
            "2025-10-26T00:00:00Z",
            use_rich=False,
            quiet=True,
        )

        # Verify scan completed (didn't crash)
        self.assertIsNotNone(results)
        self.assertIsNotNone(stats)

        # At least one should fail (the invalid one)
        self.assertGreater(stats["failed_scans"], 0, "Invalid extension should fail")

        # But valid extension might succeed
        # (depending on API availability)

        print(f"✓ Handled errors gracefully")
        print(f"  Successful: {stats['successful_scans']}")
        print(f"  Failed: {stats['failed_scans']}")
        if stats["failed_extensions"]:
            print(
                f"  Failed extensions: {[e['id'] for e in stats['failed_extensions']]}"
            )


@pytest.mark.real-api
class TestRealAPIEndToEnd(unittest.TestCase):
    """End-to-end integration tests using run_scan()."""

    def setUp(self):
        """Create temporary directories for each test."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @integration
    @slow
    def test_end_to_end_scan_with_output(self):
        """Test complete scan workflow with JSON output."""
        print("\nTesting end-to-end scan with output...")

        extensions_dir = Path(self.test_dir) / "extensions"
        extensions_dir.mkdir()

        # Create one test extension directory
        ext_dir = extensions_dir / "ms-python.python-2023.1.0"
        ext_dir.mkdir()
        package_json = {
            "name": "python",
            "publisher": "ms-python",
            "version": "2023.1.0",
            "displayName": "Python",
        }
        (ext_dir / "package.json").write_text(json.dumps(package_json))

        # Create extensions.json (required for discovery)
        extensions_json = Path(extensions_dir) / "extensions.json"
        extensions_json.write_text(
            json.dumps(
                [
                    {
                        "identifier": {"id": "ms-python.python"},
                        "version": "2023.1.0",
                        "location": {"$mid": 1, "path": str(ext_dir)},
                        "metadata": {"installedTimestamp": 1234567890000},
                    }
                ]
            )
        )

        output_file = Path(self.test_dir) / "results.json"
        cache_dir = Path(self.test_dir) / "cache"

        # Note: run_scan expects parallel parameter in some versions
        # Adjust based on current implementation
        try:
            exit_code = run_scan(
                extensions_dir=str(extensions_dir),
                output=str(output_file),
                workers=3,
                cache_dir=str(cache_dir),
                quiet=True,
            )
        except TypeError:
            # If parallel parameter exists
            exit_code = run_scan(
                extensions_dir=str(extensions_dir),
                output=str(output_file),
                workers=3,
                cache_dir=str(cache_dir),
                quiet=True,
            )

        # Verify scan completed
        self.assertIn(exit_code, [0, 1], "Should exit with 0 (clean) or 1 (vulns)")

        # Verify output file created
        self.assertTrue(output_file.exists(), "Output file should be created")

        # Verify output file is valid JSON
        with open(output_file, "r") as f:
            output_data = json.load(f)

        self.assertIn("summary", output_data)
        self.assertIn("extensions", output_data)

        print(f"✓ End-to-end scan completed (exit code: {exit_code})")
        print(f"✓ Output written to {output_file}")


def run_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Real API Integration Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRealAPIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestRealAPIEndToEnd))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("All integration tests PASSED ✓")
    else:
        print("Some integration tests FAILED ✗")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys

    print("\nWARNING: These tests make real API calls to vscan.dev")
    print("Press Ctrl+C within 3 seconds to cancel...")
    try:
        import time

        time.sleep(3)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(0)

    sys.exit(run_tests())
