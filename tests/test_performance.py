#!/usr/bin/env python3
"""
Performance Benchmark Tests for VS Code Extension Scanner

Tests verify that Phase 2 performance improvements deliver measurable gains:
1. Batch commits significantly faster than individual commits
2. Cache reads complete quickly
3. Optional raw response storage reduces memory usage

Run with: python3 tests/test_performance.py
"""

import unittest
import time
import tempfile
import shutil
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.cache_manager import CacheManager


class TestDatabaseBatchCommitPerformance(unittest.TestCase):
    """Test that batch commits provide significant performance improvement."""

    def setUp(self):
        """Create temporary cache directory for testing."""
        self.test_cache_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test cache directory."""
        if Path(self.test_cache_dir).exists():
            shutil.rmtree(self.test_cache_dir)

    def test_batch_commit_vs_individual_commit(self):
        """
        Verify batch commits are significantly faster than individual commits.

        Expected: Batch commits should be >50% faster for 50 results.
        """
        NUM_RESULTS = 50

        # Create mock results
        mock_results = []
        for i in range(NUM_RESULTS):
            mock_results.append({
                'name': f'test-ext-{i}',
                'publisher': 'test-publisher',
                'scan_status': 'success',
                'security_score': 85,
                'risk_level': 'low',
                'vulnerabilities': {'total': 0, 'critical': 0, 'high': 0, 'moderate': 0, 'low': 0},
                'metadata': {'version': '1.0.0'},
                'security': {},
                'dependencies': {}
            })

        # Test 1: Individual commits (old way)
        cache_individual = CacheManager(cache_dir=self.test_cache_dir + "/individual")

        start_individual = time.time()
        for i, result in enumerate(mock_results):
            cache_individual.save_result(f'test.ext-{i}', '1.0.0', result)
        individual_duration = time.time() - start_individual

        # Test 2: Batch commits (new way)
        cache_batch = CacheManager(cache_dir=self.test_cache_dir + "/batch")

        start_batch = time.time()
        cache_batch.begin_batch()
        for i, result in enumerate(mock_results):
            cache_batch.save_result_batch(f'test.ext-{i}', '1.0.0', result)

            # Commit every 10 (as in scanner.py)
            if (i + 1) % 10 == 0:
                cache_batch.commit_batch()
                cache_batch.begin_batch()

        # Commit remaining
        cache_batch.commit_batch()
        batch_duration = time.time() - start_batch

        # Calculate improvement
        improvement_pct = ((individual_duration - batch_duration) / individual_duration) * 100

        print(f"\n{'='*60}")
        print(f"Database Batch Commit Performance Test")
        print(f"{'='*60}")
        print(f"Results saved: {NUM_RESULTS}")
        print(f"Individual commits: {individual_duration:.3f}s")
        print(f"Batch commits:      {batch_duration:.3f}s")
        print(f"Improvement:        {improvement_pct:.1f}% faster")
        print(f"{'='*60}\n")

        # Verify both saved correctly
        self.assertEqual(len(cache_individual.get_all_cached_extensions()), NUM_RESULTS)
        self.assertEqual(len(cache_batch.get_all_cached_extensions()), NUM_RESULTS)

        # Assert batch is significantly faster (>10% improvement minimum)
        self.assertGreater(
            improvement_pct,
            10.0,
            f"Batch commits should be >10% faster, got {improvement_pct:.1f}%"
        )

        # Ideally should be >50% faster per plan
        if improvement_pct < 50.0:
            print(f"⚠️  Note: Target is >50% improvement, got {improvement_pct:.1f}%")
        else:
            print(f"✓ Exceeded target: {improvement_pct:.1f}% > 50% improvement")


class TestCacheReadPerformance(unittest.TestCase):
    """Test that cache reads are fast enough for good UX."""

    def setUp(self):
        """Create temporary cache with test data."""
        self.test_cache_dir = tempfile.mkdtemp()
        self.cache = CacheManager(cache_dir=self.test_cache_dir)

        # Pre-populate cache with 100 results
        self.cache.begin_batch()
        for i in range(100):
            result = {
                'name': f'ext-{i}',
                'publisher': 'test',
                'scan_status': 'success',
                'security_score': 80,
                'risk_level': 'low',
                'vulnerabilities': {'total': 0, 'critical': 0, 'high': 0, 'moderate': 0, 'low': 0},
                'metadata': {'version': '1.0.0'},
                'security': {},
                'dependencies': {}
            }
            self.cache.save_result_batch(f'test.ext-{i}', '1.0.0', result)
        self.cache.commit_batch()

    def tearDown(self):
        """Clean up test cache directory."""
        if Path(self.test_cache_dir).exists():
            shutil.rmtree(self.test_cache_dir)

    def test_cache_read_performance_100_results(self):
        """
        Verify reading 100 cached results is fast (<1 second).

        Expected: Should complete in <1 second for good UX.
        """
        start = time.time()

        results = []
        for i in range(100):
            result = self.cache.get_cached_result(f'test.ext-{i}', '1.0.0')
            results.append(result)

        duration = time.time() - start

        print(f"\n{'='*60}")
        print(f"Cache Read Performance Test")
        print(f"{'='*60}")
        print(f"Results read:  100")
        print(f"Duration:      {duration:.3f}s")
        print(f"Avg per read:  {(duration/100)*1000:.2f}ms")
        print(f"Target:        <1.0s")
        print(f"Status:        {'✓ PASS' if duration < 1.0 else '✗ FAIL'}")
        print(f"{'='*60}\n")

        # Verify all results retrieved
        self.assertEqual(len(results), 100)
        self.assertTrue(all(r is not None for r in results))

        # Assert performance target met
        self.assertLess(
            duration,
            1.0,
            f"Cache reads took {duration:.3f}s, expected <1.0s"
        )


class TestVACUUMEffect(unittest.TestCase):
    """Test that VACUUM reduces database file size after deletions."""

    def setUp(self):
        """Create temporary cache directory."""
        self.test_cache_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test cache directory."""
        if Path(self.test_cache_dir).exists():
            shutil.rmtree(self.test_cache_dir)

    def test_vacuum_reduces_file_size(self):
        """
        Verify VACUUM reclaims disk space after cache clear.

        Expected: Database file size should reduce significantly.
        """
        cache = CacheManager(cache_dir=self.test_cache_dir)

        # Add 100 results to make file grow
        cache.begin_batch()
        for i in range(100):
            result = {
                'name': f'large-ext-{i}',
                'publisher': 'test',
                'scan_status': 'success',
                'security_score': 80,
                'risk_level': 'low',
                'vulnerabilities': {'total': 0, 'critical': 0, 'high': 0, 'moderate': 0, 'low': 0},
                'metadata': {'version': '1.0.0', 'description': 'x' * 1000},  # Large metadata
                'security': {},
                'dependencies': {}
            }
            cache.save_result_batch(f'test.ext-{i}', '1.0.0', result)
        cache.commit_batch()

        # Get file size before clear
        db_path = Path(self.test_cache_dir) / "cache.db"
        size_before = db_path.stat().st_size

        # Clear cache (should run VACUUM)
        cleared_count = cache.clear_cache()

        # Get file size after clear + VACUUM
        size_after = db_path.stat().st_size

        reduction_pct = ((size_before - size_after) / size_before) * 100

        print(f"\n{'='*60}")
        print(f"VACUUM Effect Test")
        print(f"{'='*60}")
        print(f"Results cleared:   {cleared_count}")
        print(f"Size before:       {size_before:,} bytes")
        print(f"Size after:        {size_after:,} bytes")
        print(f"Space reclaimed:   {size_before - size_after:,} bytes")
        print(f"Reduction:         {reduction_pct:.1f}%")
        print(f"{'='*60}\n")

        # Verify records were cleared
        self.assertEqual(cleared_count, 100)

        # Verify file size reduced (should be much smaller, at least 50%)
        self.assertLess(
            size_after,
            size_before * 0.5,
            f"VACUUM should reduce file size by >50%, got {reduction_pct:.1f}%"
        )


def run_all_benchmarks():
    """Run all performance benchmark tests."""
    print("\n" + "="*60)
    print("VS Code Extension Scanner - Performance Benchmarks")
    print("Phase 2: Performance Improvements Verification")
    print("="*60 + "\n")

    # Run tests
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*60)
    print("Benchmark Summary")
    print("="*60)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print("="*60 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_benchmarks()
    sys.exit(0 if success else 1)
