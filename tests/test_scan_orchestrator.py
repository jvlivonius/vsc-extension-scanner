"""
Tests for ScanOrchestrator and ParallelExecutor patterns.

This test suite validates the extracted orchestration pattern:
- ParallelExecutor base class (generic parallel execution)
- ScanOrchestrator (specialized for vulnerability scanning)
- Pure business logic separation from ThreadPoolExecutor

Coverage Focus:
- Unit tests for orchestration logic (no real threads)
- Integration tests with mocked workers
- Error handling and statistics tracking
- Cache integration and persistence
"""

import pytest
from typing import Callable, List, Tuple
from unittest.mock import Mock, MagicMock, patch, call

from vscode_scanner.parallel_executor import ParallelExecutor
from vscode_scanner.scan_orchestrator import ScanOrchestrator
from vscode_scanner.scanner import ThreadSafeStats

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


# ============================================================================
# Test ParallelExecutor Base Class
# ============================================================================


class TestParallelExecutor:
    """Test generic parallel execution pattern."""

    def test_init_default_values(self):
        """Test default initialization values."""
        executor = ParallelExecutor()
        assert executor.max_workers == 3
        assert executor.on_progress is None

    def test_init_custom_workers(self):
        """Test custom worker count initialization."""
        executor = ParallelExecutor(max_workers=5)
        assert executor.max_workers == 5

    def test_init_clamps_workers_to_range(self):
        """Test worker count is clamped to 1-5 range."""
        # Test lower bound
        executor_low = ParallelExecutor(max_workers=0)
        assert executor_low.max_workers == 1

        # Test upper bound
        executor_high = ParallelExecutor(max_workers=10)
        assert executor_high.max_workers == 5

    def test_init_with_progress_callback(self):
        """Test initialization with progress callback."""
        callback = Mock()
        executor = ParallelExecutor(on_progress=callback)
        assert executor.on_progress == callback

    def test_prepare_task_not_implemented(self):
        """Test prepare_task raises NotImplementedError."""
        executor = ParallelExecutor()
        with pytest.raises(NotImplementedError, match="prepare_task"):
            executor.prepare_task({"id": "test"}, 1, 10)

    def test_process_result_not_implemented(self):
        """Test process_result raises NotImplementedError."""
        executor = ParallelExecutor()
        with pytest.raises(NotImplementedError, match="process_result"):
            executor.process_result({"id": "test"}, "result", 1, 10)

    def test_handle_error_not_implemented(self):
        """Test handle_error raises NotImplementedError."""
        executor = ParallelExecutor()
        with pytest.raises(NotImplementedError, match="handle_error"):
            executor.handle_error({"id": "test"}, Exception("test"), 1, 10)

    def test_notify_start_with_callback(self):
        """Test notify_start calls progress callback."""
        callback = Mock()
        executor = ParallelExecutor(on_progress=callback)
        executor.notify_start(10)
        callback.assert_called_once_with("started", {"total": 10})

    def test_notify_start_without_callback(self):
        """Test notify_start without callback doesn't fail."""
        executor = ParallelExecutor()
        executor.notify_start(10)  # Should not raise

    def test_notify_complete_with_callback(self):
        """Test notify_complete calls progress callback."""
        callback = Mock()
        executor = ParallelExecutor(on_progress=callback)
        item = {"id": "test"}
        result = {"status": "success"}
        executor.notify_complete(item, result, 1, 10)
        callback.assert_called_once_with(
            "completed", {"item": item, "result": result, "index": 1, "total": 10}
        )

    def test_notify_error_with_callback(self):
        """Test notify_error calls progress callback."""
        callback = Mock()
        executor = ParallelExecutor(on_progress=callback)
        item = {"id": "test"}
        error = Exception("test error")
        executor.notify_error(item, error, 1, 10)
        callback.assert_called_once_with(
            "failed", {"item": item, "error": "test error", "index": 1, "total": 10}
        )


# ============================================================================
# Test ScanOrchestrator
# ============================================================================


class TestScanOrchestratorInit:
    """Test ScanOrchestrator initialization."""

    def test_init_default_values(self, temp_cache_dir):
        """Test default initialization values."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        assert orchestrator.cache_manager == cache
        assert orchestrator.args == args
        assert orchestrator.max_workers == 3
        assert orchestrator.on_progress is None
        assert isinstance(orchestrator.stats, ThreadSafeStats)
        assert orchestrator.scan_results == []

    def test_init_custom_workers(self, temp_cache_dir):
        """Test custom worker count initialization."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=5)
        orchestrator = ScanOrchestrator(cache, args, max_workers=5)
        assert orchestrator.max_workers == 5

    def test_init_with_progress_callback(self, temp_cache_dir):
        """Test initialization with progress callback."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        callback = Mock()
        orchestrator = ScanOrchestrator(cache, args, on_progress=callback)
        assert orchestrator.on_progress == callback

    def test_init_without_cache(self):
        """Test initialization without cache manager."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)
        assert orchestrator.cache_manager is None


class TestScanOrchestratorPrepareTask:
    """Test ScanOrchestrator task preparation."""

    def test_prepare_task_returns_worker_and_args(self, temp_cache_dir):
        """Test prepare_task returns correct worker function and args."""
        from vscode_scanner.cache_manager import CacheManager
        from vscode_scanner.scanner import _scan_single_extension_worker

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        worker_func, worker_args = orchestrator.prepare_task(ext, 1, 10)

        assert worker_func == _scan_single_extension_worker
        assert worker_args == (ext, cache, args)

    def test_prepare_task_with_null_cache(self):
        """Test prepare_task with None cache manager."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        worker_func, worker_args = orchestrator.prepare_task(ext, 1, 10)

        assert worker_args == (ext, None, args)


class TestScanOrchestratorProcessResult:
    """Test ScanOrchestrator result processing."""

    def test_process_result_stores_scan_result(self, temp_cache_dir):
        """Test successful result is stored in scan_results."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, False, True)

        orchestrator.process_result(ext, result, 1, 10)

        assert len(orchestrator.scan_results) == 1
        assert orchestrator.scan_results[0] == scan_result

    def test_process_result_saves_to_cache(self, temp_cache_dir):
        """Test result is saved to cache when should_cache=True."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, False, True)

        with patch.object(cache, "save_result") as mock_save:
            orchestrator.process_result(ext, result, 1, 10)
            mock_save.assert_called_once_with("test.extension", "1.0.0", scan_result)

    def test_process_result_skips_cache_when_should_cache_false(self, temp_cache_dir):
        """Test cache is not saved when should_cache=False."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, False, False)  # should_cache=False

        with patch.object(cache, "save_result") as mock_save:
            orchestrator.process_result(ext, result, 1, 10)
            mock_save.assert_not_called()

    def test_process_result_handles_cache_error(self, temp_cache_dir):
        """Test cache save error doesn't fail the scan."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, False, True)

        with patch.object(cache, "save_result", side_effect=Exception("Cache error")):
            # Should not raise, just log warning
            orchestrator.process_result(ext, result, 1, 10)
            assert len(orchestrator.scan_results) == 1

    def test_process_result_updates_stats_for_success(self, temp_cache_dir):
        """Test statistics are updated for successful scan."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, False, True)

        orchestrator.process_result(ext, result, 1, 10)

        stats = orchestrator.stats.to_dict()
        assert stats["successful_scans"] == 1
        assert stats["fresh_scans"] == 1

    def test_process_result_updates_stats_for_vulnerabilities(self, temp_cache_dir):
        """Test statistics track vulnerabilities found."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 3}}
        result = (scan_result, False, True)

        orchestrator.process_result(ext, result, 1, 10)

        stats = orchestrator.stats.to_dict()
        assert stats["vulnerabilities_found"] == 1
        assert stats["successful_scans"] == 1

    def test_process_result_tracks_cached_results(self, temp_cache_dir):
        """Test cached results are tracked separately."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(cache, args)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, True, False)  # from_cache=True

        orchestrator.process_result(ext, result, 1, 10)

        stats = orchestrator.stats.to_dict()
        assert stats["cached_results"] == 1
        assert stats["fresh_scans"] == 0

    def test_process_result_notifies_progress_callback(self, temp_cache_dir):
        """Test progress callback is notified on successful result."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        callback = Mock()
        orchestrator = ScanOrchestrator(cache, args, on_progress=callback)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, False, True)

        orchestrator.process_result(ext, result, 1, 10)

        callback.assert_called_once_with(
            "completed",
            {
                "extension": ext,
                "result": scan_result,
                "from_cache": False,
                "index": 1,
                "total": 10,
            },
        )

    def test_process_result_notifies_cached_event(self, temp_cache_dir):
        """Test progress callback uses 'cached' event for cache hits."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=3)
        callback = Mock()
        orchestrator = ScanOrchestrator(cache, args, on_progress=callback)

        ext = {"id": "test.extension", "version": "1.0.0"}
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        result = (scan_result, True, False)  # from_cache=True

        orchestrator.process_result(ext, result, 1, 10)

        # Should use "cached" event instead of "completed"
        assert callback.call_args[0][0] == "cached"


class TestScanOrchestratorHandleError:
    """Test ScanOrchestrator error handling."""

    def test_handle_error_increments_failed_scans(self):
        """Test error handling increments failed_scans counter."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        ext = {"id": "test.extension", "version": "1.0.0", "name": "Test Extension"}
        error = Exception("API error")

        orchestrator.handle_error(ext, error, 1, 10)

        stats = orchestrator.stats.to_dict()
        assert stats["failed_scans"] == 1

    def test_handle_error_tracks_failed_extension(self):
        """Test error handling tracks failed extension details."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        ext = {"id": "test.extension", "version": "1.0.0", "name": "Test Extension"}
        error = Exception("API error")

        orchestrator.handle_error(ext, error, 1, 10)

        stats = orchestrator.stats.to_dict()
        failed = stats["failed_extensions"]
        assert len(failed) == 1
        assert failed[0]["id"] == "test.extension"
        assert failed[0]["name"] == "Test Extension"
        assert "error_type" in failed[0]
        assert "error_message" in failed[0]

    def test_handle_error_uses_display_name(self):
        """Test error handling prefers display_name over name."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        ext = {
            "id": "test.extension",
            "version": "1.0.0",
            "name": "Test Extension",
            "display_name": "Test Extension Display",
        }
        error = Exception("API error")

        orchestrator.handle_error(ext, error, 1, 10)

        stats = orchestrator.stats.to_dict()
        failed = stats["failed_extensions"]
        assert failed[0]["name"] == "Test Extension Display"

    def test_handle_error_notifies_progress_callback(self):
        """Test error handling notifies progress callback."""
        args = Mock(workers=3)
        callback = Mock()
        orchestrator = ScanOrchestrator(None, args, on_progress=callback)

        ext = {"id": "test.extension", "version": "1.0.0", "name": "Test Extension"}
        error = Exception("API error")

        orchestrator.handle_error(ext, error, 1, 10)

        callback.assert_called_once_with(
            "failed", {"extension": ext, "error": "API error", "index": 1, "total": 10}
        )


class TestScanOrchestratorUpdateStatsForResult:
    """Test ScanOrchestrator statistics update logic."""

    def test_update_stats_for_successful_scan(self):
        """Test stats update for successful scan without vulnerabilities."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        ext = {"id": "test.extension", "version": "1.0.0"}

        orchestrator._update_stats_for_result(scan_result, ext)

        stats = orchestrator.stats.to_dict()
        assert stats["successful_scans"] == 1
        assert stats["vulnerabilities_found"] == 0

    def test_update_stats_for_scan_with_vulnerabilities(self):
        """Test stats update for scan with vulnerabilities."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 5}}
        ext = {"id": "test.extension", "version": "1.0.0"}

        orchestrator._update_stats_for_result(scan_result, ext)

        stats = orchestrator.stats.to_dict()
        assert stats["successful_scans"] == 1
        assert stats["vulnerabilities_found"] == 1

    def test_update_stats_for_failed_scan(self):
        """Test stats update for failed scan."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        scan_result = {"scan_status": "failed", "error": "API error"}
        ext = {"id": "test.extension", "version": "1.0.0", "name": "Test Extension"}

        orchestrator._update_stats_for_result(scan_result, ext)

        stats = orchestrator.stats.to_dict()
        assert stats["failed_scans"] == 1
        assert len(stats["failed_extensions"]) == 1


class TestScanOrchestratorScan:
    """Test ScanOrchestrator main scan method."""

    @patch("vscode_scanner.scan_orchestrator._scan_single_extension_worker")
    def test_scan_returns_results_and_stats(self, mock_worker, temp_cache_dir):
        """Test scan returns tuple of results and statistics."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=1)
        orchestrator = ScanOrchestrator(cache, args, max_workers=1)

        # Mock worker to return success result
        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        mock_worker.return_value = (scan_result, False, True)

        extensions = [{"id": "ext1", "version": "1.0.0"}]
        results, stats = orchestrator.scan(extensions)

        assert isinstance(results, list)
        assert isinstance(stats, dict)
        assert len(results) == 1
        assert results[0] == scan_result

    @patch("vscode_scanner.scan_orchestrator._scan_single_extension_worker")
    def test_scan_resets_state_for_new_scan(self, mock_worker, temp_cache_dir):
        """Test scan resets scan_results for each new scan."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=1)
        orchestrator = ScanOrchestrator(cache, args, max_workers=1)

        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        mock_worker.return_value = (scan_result, False, True)

        # First scan
        extensions1 = [{"id": "ext1", "version": "1.0.0"}]
        results1, _ = orchestrator.scan(extensions1)
        assert len(results1) == 1

        # Second scan should reset results
        extensions2 = [{"id": "ext2", "version": "2.0.0"}]
        results2, _ = orchestrator.scan(extensions2)
        assert len(results2) == 1  # Not 2

    @patch("vscode_scanner.scan_orchestrator._scan_single_extension_worker")
    def test_scan_with_empty_list(self, mock_worker):
        """Test scan handles empty extension list."""
        args = Mock(workers=3)
        orchestrator = ScanOrchestrator(None, args)

        results, stats = orchestrator.scan([])

        assert results == []
        assert isinstance(stats, dict)
        mock_worker.assert_not_called()

    @patch("vscode_scanner.scan_orchestrator._scan_single_extension_worker")
    def test_scan_notifies_progress_start(self, mock_worker, temp_cache_dir):
        """Test scan notifies progress callback at start."""
        from vscode_scanner.cache_manager import CacheManager

        cache = CacheManager(str(temp_cache_dir))
        args = Mock(workers=1)
        callback = Mock()
        orchestrator = ScanOrchestrator(
            cache, args, max_workers=1, on_progress=callback
        )

        scan_result = {"scan_status": "success", "vulnerabilities": {"count": 0}}
        mock_worker.return_value = (scan_result, False, True)

        extensions = [{"id": "ext1", "version": "1.0.0"}]
        orchestrator.scan(extensions)

        # First call should be "started" event
        first_call = callback.call_args_list[0]
        assert first_call[0][0] == "started"
        assert first_call[0][1]["total"] == 1
