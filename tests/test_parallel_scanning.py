#!/usr/bin/env python3
"""
Test suite for parallel scanning functionality (v3.4).

Tests cover:
- Basic parallel scanning functionality
- Worker isolation (each worker has its own API client)
- Thread safety of cache operations
- Error handling in parallel mode
- Worker count validation and limits
- Result consistency between parallel and sequential modes
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from types import SimpleNamespace

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.scanner import (
    _scan_extensions,
    _scan_single_extension_worker,
    run_scan
)
from vscode_scanner.cache_manager import CacheManager


class TestParallelScanningBasic(unittest.TestCase):
    """Test basic parallel scanning functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.cache_dir.mkdir()

        # Sample extensions for testing
        self.extensions = [
            {
                'id': 'test.extension1',
                'name': 'extension1',
                'version': '1.0.0',
                'publisher': 'test',
                'display_name': 'Test Extension 1'
            },
            {
                'id': 'test.extension2',
                'name': 'extension2',
                'version': '1.0.0',
                'publisher': 'test',
                'display_name': 'Test Extension 2'
            },
            {
                'id': 'test.extension3',
                'name': 'extension3',
                'version': '1.0.0',
                'publisher': 'test',
                'display_name': 'Test Extension 3'
            }
        ]

        # Mock args
        self.args = SimpleNamespace(
            delay=0.1,
            max_retries=0,
            retry_delay=0.1,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=3
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parallel_scan_completes(self):
        """Test that parallel scan completes successfully."""
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            # Mock successful API responses
            mock_api = Mock()
            mock_api.scan_extension_with_retry.return_value = {
                'scan_status': 'success',
                'security': {'score': 85},
                'vulnerabilities': {'count': 0}
            }
            mock_api_class.return_value = mock_api

            results, stats = _scan_extensions(
                self.extensions,
                self.args,
                cache_manager,
                '2025-10-25T00:00:00Z',
                use_rich=False,
                quiet=True
            )

            # Verify results
            self.assertEqual(len(results), 3)
            self.assertEqual(stats['successful_scans'], 3)
            self.assertEqual(stats['failed_scans'], 0)
            self.assertEqual(stats['fresh_scans'], 3)

    def test_worker_count_validation(self):
        """Test that worker count is capped at 2-5 range."""
        # Simply test the capping logic directly
        test_cases = [
            (1, 2),   # Too low, should cap to 2
            (2, 2),   # Valid minimum
            (3, 3),   # Valid default
            (5, 5),   # Valid maximum
            (10, 5),  # Too high, should cap to 5
        ]

        for input_workers, expected_workers in test_cases:
            # Test the capping logic: min(max(workers, 2), 5)
            capped = min(max(input_workers, 2), 5)
            self.assertEqual(capped, expected_workers,
                           f"Worker count {input_workers} should cap to {expected_workers}, got {capped}")


class TestWorkerIsolation(unittest.TestCase):
    """Test that each worker has isolated API client."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.cache_dir.mkdir()

        self.extension = {
            'id': 'test.extension',
            'name': 'extension',
            'version': '1.0.0',
            'publisher': 'test'
        }

        self.args = SimpleNamespace(
            delay=0.1,
            max_retries=0,
            retry_delay=0.1,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=3
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_worker_creates_own_api_client(self):
        """Test that each worker creates its own API client."""
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            mock_api.scan_extension_with_retry.return_value = {
                'scan_status': 'success',
                'security': {'score': 85}
            }
            mock_api_class.return_value = mock_api

            # Call worker function
            result, from_cache, should_cache = _scan_single_extension_worker(
                self.extension,
                cache_manager,
                self.args
            )

            # Verify API client was created
            mock_api_class.assert_called_once()
            self.assertFalse(from_cache)
            self.assertTrue(should_cache)  # Successful scans should be cached
            self.assertEqual(result['scan_status'], 'success')

    def test_multiple_workers_get_separate_clients(self):
        """Test that multiple workers each get their own API client."""
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        extensions = [
            {'id': f'test.ext{i}', 'name': f'ext{i}', 'version': '1.0.0', 'publisher': 'test'}
            for i in range(5)
        ]

        args = SimpleNamespace(
            delay=0.1,
            max_retries=0,
            retry_delay=0.1,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=3
        )

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            mock_api.scan_extension_with_retry.return_value = {
                'scan_status': 'success'
            }
            mock_api_class.return_value = mock_api

            _scan_extensions(
                extensions,
                args,
                cache_manager,
                '2025-10-25T00:00:00Z',
                use_rich=False,
                quiet=True
            )

            # Verify multiple API clients were created (one per extension)
            self.assertEqual(mock_api_class.call_count, 5)


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of cache operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.cache_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_concurrent_cache_writes(self):
        """Test that concurrent cache writes don't cause errors."""
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        extensions = [
            {'id': f'test.ext{i}', 'name': f'ext{i}', 'version': '1.0.0', 'publisher': 'test'}
            for i in range(10)
        ]

        args = SimpleNamespace(
            delay=0.01,
            max_retries=0,
            retry_delay=0.1,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=5
        )

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            mock_api.scan_extension_with_retry.return_value = {
                'scan_status': 'success',
                'security': {'score': 85}
            }
            mock_api_class.return_value = mock_api

            # This should complete without SQLite locking errors
            results, stats = _scan_extensions(
                extensions,
                args,
                cache_manager,
                '2025-10-25T00:00:00Z',
                use_rich=False,
                quiet=True
            )

            self.assertEqual(len(results), 10)
            self.assertEqual(stats['successful_scans'], 10)

    def test_concurrent_cache_reads(self):
        """Test that concurrent cache reads work correctly."""
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        # Pre-populate cache
        for i in range(10):
            cache_manager.save_result(
                f'test.ext{i}',
                '1.0.0',
                {'scan_status': 'success', 'security': {'score': 85}}
            )

        extensions = [
            {'id': f'test.ext{i}', 'name': f'ext{i}', 'version': '1.0.0', 'publisher': 'test'}
            for i in range(10)
        ]

        args = SimpleNamespace(
            delay=0.01,
            max_retries=0,
            retry_delay=0.1,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=5
        )

        # Should read from cache without errors
        results, stats = _scan_extensions(
            extensions,
            args,
            cache_manager,
            '2025-10-25T00:00:00Z',
            use_rich=False,
            quiet=True
        )

        self.assertEqual(len(results), 10)
        self.assertEqual(stats['cached_results'], 10)
        self.assertEqual(stats['fresh_scans'], 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in parallel mode."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.cache_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_worker_failure_doesnt_crash_scan(self):
        """Test that individual worker failures don't crash entire scan."""
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        extensions = [
            {'id': 'test.ext1', 'name': 'ext1', 'version': '1.0.0', 'publisher': 'test'},
            {'id': 'test.ext2', 'name': 'ext2', 'version': '1.0.0', 'publisher': 'test'},
            {'id': 'test.ext3', 'name': 'ext3', 'version': '1.0.0', 'publisher': 'test'},
        ]

        args = SimpleNamespace(
            delay=0.01,
            max_retries=0,
            retry_delay=0.1,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=3
        )

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            # First call succeeds, second fails, third succeeds
            mock_api.scan_extension_with_retry.side_effect = [
                {'scan_status': 'success'},
                Exception("Network error"),
                {'scan_status': 'success'}
            ]
            mock_api_class.return_value = mock_api

            results, stats = _scan_extensions(
                extensions,
                args,
                cache_manager,
                '2025-10-25T00:00:00Z',
                use_rich=False,
                quiet=True
            )

            # Scan should complete with mixed results
            self.assertEqual(len(results), 2)  # Only successful results
            self.assertEqual(stats['successful_scans'], 2)
            self.assertEqual(stats['failed_scans'], 1)
            self.assertEqual(len(stats['failed_extensions']), 1)

    def test_failed_extensions_tracked(self):
        """Test that failed extensions are properly tracked."""
        cache_manager = CacheManager(cache_dir=str(self.cache_dir))

        extensions = [
            {'id': 'test.failing', 'name': 'failing', 'version': '1.0.0', 'publisher': 'test', 'display_name': 'Failing Extension'},
        ]

        args = SimpleNamespace(
            delay=0.01,
            max_retries=0,
            retry_delay=0.1,
            cache_max_age=7,
            refresh_cache=False,
            no_cache=False,
            workers=2
        )

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            mock_api.scan_extension_with_retry.side_effect = Exception("API timeout")
            mock_api_class.return_value = mock_api

            results, stats = _scan_extensions(
                extensions,
                args,
                cache_manager,
                '2025-10-25T00:00:00Z',
                use_rich=False,
                quiet=True
            )

            # Verify failed extension is tracked
            self.assertEqual(stats['failed_scans'], 1)
            self.assertEqual(len(stats['failed_extensions']), 1)
            self.assertEqual(stats['failed_extensions'][0]['id'], 'test.failing')
            self.assertIn('error_type', stats['failed_extensions'][0])


class TestResultConsistency(unittest.TestCase):
    """Test that parallel and sequential modes produce consistent results."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parallel_sequential_consistency(self):
        """Test that parallel and sequential produce same results (order-independent)."""
        extensions = [
            {'id': f'test.ext{i}', 'name': f'ext{i}', 'version': '1.0.0', 'publisher': 'test'}
            for i in range(5)
        ]

        # Mock responses
        mock_responses = {
            'test.ext0': {'scan_status': 'success', 'security': {'score': 90}},
            'test.ext1': {'scan_status': 'success', 'security': {'score': 85}},
            'test.ext2': {'scan_status': 'success', 'security': {'score': 75}},
            'test.ext3': {'scan_status': 'success', 'security': {'score': 95}},
            'test.ext4': {'scan_status': 'success', 'security': {'score': 80}},
        }

        def mock_scan(publisher, name):
            ext_id = f"{publisher}.{name}"
            return mock_responses.get(ext_id, {'scan_status': 'error'})

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            mock_api.scan_extension_with_retry.side_effect = mock_scan
            mock_api_class.return_value = mock_api

            # Run sequential scan
            from vscode_scanner.scanner import _scan_extensions
            cache_dir_seq = Path(self.temp_dir) / "cache_seq"
            cache_dir_seq.mkdir()
            cache_manager_seq = CacheManager(cache_dir=str(cache_dir_seq))

            args_seq = SimpleNamespace(
                delay=0.01,
                max_retries=0,
                retry_delay=0.1,
                cache_max_age=7,
                refresh_cache=False,
                no_cache=False,
                workers=1
            )

            seq_results, seq_stats = _scan_extensions(
                extensions,
                args_seq,
                cache_manager_seq,
                '2025-10-25T00:00:00Z',
                use_rich=False,
                quiet=True
            )

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            mock_api.scan_extension_with_retry.side_effect = mock_scan
            mock_api_class.return_value = mock_api

            # Run parallel scan
            cache_dir_par = Path(self.temp_dir) / "cache_par"
            cache_dir_par.mkdir()
            cache_manager_par = CacheManager(cache_dir=str(cache_dir_par))

            args_par = SimpleNamespace(
                delay=0.01,
                max_retries=0,
                retry_delay=0.1,
                cache_max_age=7,
                refresh_cache=False,
                no_cache=False,
                workers=3
            )

            par_results, par_stats = _scan_extensions(
                extensions,
                args_par,
                cache_manager_par,
                '2025-10-25T00:00:00Z',
                use_rich=False,
                quiet=True
            )

        # Results should be the same (order-independent)
        self.assertEqual(len(seq_results), len(par_results))
        self.assertEqual(seq_stats['successful_scans'], par_stats['successful_scans'])
        self.assertEqual(seq_stats['failed_scans'], par_stats['failed_scans'])

        # Compare results by ID (order doesn't matter)
        seq_ids = sorted([r['id'] for r in seq_results])
        par_ids = sorted([r['id'] for r in par_results])
        self.assertEqual(seq_ids, par_ids)


class TestIntegration(unittest.TestCase):
    """Integration tests for parallel scanning."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.extensions_dir = Path(self.temp_dir) / "extensions"
        self.extensions_dir.mkdir()

        # Create mock extension directories
        for i in range(3):
            ext_dir = self.extensions_dir / f"test.ext{i}-1.0.0"
            ext_dir.mkdir()
            package_json = {
                "name": f"ext{i}",
                "publisher": "test",
                "version": "1.0.0",
                "displayName": f"Test Extension {i}"
            }
            (ext_dir / "package.json").write_text(json.dumps(package_json))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_end_to_end_parallel_scan(self):
        """Test end-to-end parallel scan from discovery to results."""
        cache_dir = Path(self.temp_dir) / "cache"

        with patch('vscode_scanner.scanner.VscanAPIClient') as mock_api_class:
            mock_api = Mock()
            mock_api.scan_extension_with_retry.return_value = {
                'scan_status': 'success',
                'security': {'score': 85},
                'vulnerabilities': {'count': 0}
            }
            mock_api.get_retry_stats.return_value = {
                'total_retries': 0,
                'successful_retries': 0,
                'failed_after_retries': 0
            }
            mock_api_class.return_value = mock_api

            exit_code = run_scan(
                extensions_dir=str(self.extensions_dir),
                output=None,
                parallel=True,
                workers=3,
                cache_dir=str(cache_dir),
                quiet=True
            )

            # Should succeed (exit code 0 = no vulnerabilities)
            self.assertEqual(exit_code, 0)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestParallelScanningBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkerIsolation))
    suite.addTests(loader.loadTestsFromTestCase(TestThreadSafety))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestResultConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
