"""
Integration tests for scanner module.

Consolidates progress callbacks, error recovery, edge cases, and output
generation tests into a single file for easier maintenance.

Tests cover:
- Progress callback pattern and event dispatching
- Error categorization and message simplification
- Cache initialization and warning handling
- Extension discovery errors and edge cases
- Output generation error handling
"""

import unittest
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, call


# ============================================================================
# Progress Callback Tests (13 tests)
# ============================================================================
# FROM: test_scanner_progress.py


@pytest.mark.unit
class TestProgressCallback(unittest.TestCase):
    """Test ProgressCallback class for progress display abstraction."""

    def test_callback_quiet_mode_ignores_all_events(self):
        """Progress callback in quiet mode ignores all events."""
        from vscode_scanner.display import ProgressCallback

        callback = ProgressCallback(use_rich=False, quiet=True, worker_info="3 workers")

        # Act - send various events
        callback("started", {"total": 10})
        callback("completed", {"extension": {"id": "test.ext"}, "result": {}})
        callback("failed", {"extension": {"id": "test.ext"}, "error": "Error"})

        # Assert - no errors, no progress display
        assert callback.current_count == 0
        assert callback.total_count == 0
        assert callback.progress is None

    def test_callback_plain_mode_logs_progress(self):
        """Progress callback in plain mode logs extension progress."""
        from vscode_scanner.display import ProgressCallback

        callback = ProgressCallback(
            use_rich=False, quiet=False, worker_info="3 workers"
        )

        # Act - start scan
        callback("started", {"total": 3})

        assert callback.total_count == 3
        assert callback.current_count == 0

        # Act - process completed extension
        with patch("vscode_scanner.utils.log") as mock_log:
            callback(
                "completed",
                {
                    "extension": {"id": "test.ext", "version": "1.0"},
                    "result": {},
                    "from_cache": False,
                },
            )

            # Assert - log was called with fresh indicator
            mock_log.assert_called_once()
            log_msg = mock_log.call_args[0][0]
            assert "[1/3]" in log_msg
            assert "test.ext" in log_msg
            assert "v1.0" in log_msg
            assert "🔍 Fresh" in log_msg

        assert callback.current_count == 1

    def test_callback_plain_mode_cached_indicator(self):
        """Progress callback shows cached indicator for cached results."""
        from vscode_scanner.display import ProgressCallback

        callback = ProgressCallback(use_rich=False, quiet=False, worker_info="")

        callback("started", {"total": 2})

        # Act - process cached extension
        with patch("vscode_scanner.utils.log") as mock_log:
            callback(
                "cached",
                {
                    "extension": {"id": "cached.ext", "version": "2.0"},
                    "result": {},
                    "from_cache": True,
                },
            )

            # Assert - log shows cached indicator
            log_msg = mock_log.call_args[0][0]
            assert "[1/2]" in log_msg
            assert "cached.ext" in log_msg
            assert "v2.0" in log_msg
            assert "⚡ Cached" in log_msg

    @patch("vscode_scanner.display.create_scan_progress")
    def test_callback_rich_mode_creates_progress_bar(self, mock_create_progress):
        """Progress callback in Rich mode creates and manages progress bar."""
        from vscode_scanner.display import ProgressCallback

        # Arrange - mock Rich progress with context manager support
        mock_progress = MagicMock()
        mock_progress.add_task = Mock(return_value="task_id")
        mock_create_progress.return_value = mock_progress

        callback = ProgressCallback(use_rich=True, quiet=False, worker_info="5 workers")

        # Act - start scan
        callback("started", {"total": 10})

        # Assert - progress bar created and started
        mock_create_progress.assert_called_once()
        mock_progress.__enter__.assert_called_once()
        mock_progress.add_task.assert_called_once()

        # Verify description includes worker info
        task_description = mock_progress.add_task.call_args[0][0]
        assert "Scanning" in task_description
        assert "5 workers" in task_description

        assert callback.progress is not None
        assert callback.task == "task_id"

    @patch("vscode_scanner.display.create_scan_progress")
    def test_callback_rich_mode_updates_progress(self, mock_create_progress):
        """Progress callback in Rich mode updates progress bar."""
        from vscode_scanner.display import ProgressCallback

        # Arrange
        mock_progress = MagicMock()
        mock_progress.add_task = Mock(return_value="task_id")
        mock_create_progress.return_value = mock_progress

        callback = ProgressCallback(use_rich=True, quiet=False, worker_info="")
        callback("started", {"total": 5})

        # Act - process extensions
        callback("completed", {"extension": {"id": "ext1"}, "result": {}})
        callback("cached", {"extension": {"id": "ext2"}, "result": {}})
        callback("failed", {"extension": {"id": "ext3"}, "error": "Error"})

        # Assert - progress updated 3 times
        assert mock_progress.update.call_count == 3
        mock_progress.update.assert_has_calls(
            [
                call("task_id", advance=1),
                call("task_id", advance=1),
                call("task_id", advance=1),
            ]
        )
        assert callback.current_count == 3

    @patch("vscode_scanner.display.create_scan_progress")
    def test_callback_cleanup_closes_progress_bar(self, mock_create_progress):
        """Callback cleanup properly closes Rich progress bar."""
        from vscode_scanner.display import ProgressCallback

        # Arrange
        mock_progress = MagicMock()
        mock_progress.add_task = Mock(return_value="task_id")
        mock_create_progress.return_value = mock_progress

        callback = ProgressCallback(use_rich=True, quiet=False, worker_info="")
        callback("started", {"total": 1})

        # Act - cleanup
        callback.cleanup()

        # Assert - progress bar exited
        mock_progress.__exit__.assert_called_once()
        assert callback.progress is None
        assert callback.task is None

    def test_callback_cleanup_safe_when_no_progress(self):
        """Callback cleanup is safe when no progress bar was created."""
        from vscode_scanner.display import ProgressCallback

        callback = ProgressCallback(use_rich=False, quiet=False, worker_info="")

        # Act - cleanup without starting
        callback.cleanup()  # Should not raise

        # Assert - no errors
        assert callback.progress is None

    @patch("vscode_scanner.display.create_scan_progress")
    def test_callback_cleanup_handles_exceptions(self, mock_create_progress):
        """Callback cleanup handles exceptions gracefully."""
        from vscode_scanner.display import ProgressCallback

        # Arrange - progress bar that raises on exit
        mock_progress = MagicMock()
        mock_progress.add_task = Mock(return_value="task_id")
        mock_progress.__exit__ = Mock(side_effect=Exception("Cleanup error"))
        mock_create_progress.return_value = mock_progress

        callback = ProgressCallback(use_rich=True, quiet=False, worker_info="")
        callback("started", {"total": 1})

        # Act - cleanup should not raise
        callback.cleanup()  # Should handle exception silently

        # Assert - progress cleared despite exception
        assert callback.progress is None
        assert callback.task is None


@pytest.mark.unit
class TestScanExtensionsWithCallback(unittest.TestCase):
    """Test _scan_extensions() integration with progress callback."""

    @patch("vscode_scanner.scanner.ThreadPoolExecutor")
    @patch("vscode_scanner.scanner._scan_single_extension_worker")
    def test_scan_extensions_calls_callback_on_start(
        self, mock_worker, mock_executor_class
    ):
        """_scan_extensions calls callback with started event."""
        from vscode_scanner.scanner import _scan_extensions

        # Arrange
        mock_callback = Mock()
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor.submit = Mock(return_value=Mock())

        # Mock futures - empty for quick test
        mock_executor.submit.return_value = Mock()
        mock_worker.return_value = ({"scan_status": "success"}, False, False)

        from unittest.mock import MagicMock

        mock_future = MagicMock()
        mock_future.result.return_value = ({"scan_status": "success"}, False, False)

        with patch("vscode_scanner.scanner.as_completed", return_value=[]):
            extensions = [{"id": "test.ext", "version": "1.0"}]
            args = Mock(
                workers=1, refresh_cache=False, no_cache=False, cache_max_age=30
            )

            # Act
            _scan_extensions(
                extensions,
                args,
                None,
                "2024-11-03T00:00:00Z",
                use_rich=False,
                quiet=False,
                on_progress=mock_callback,
            )

            # Assert - callback called with started event
            mock_callback.assert_any_call("started", {"total": 1})

    @patch("vscode_scanner.scanner.ThreadPoolExecutor")
    @patch("vscode_scanner.scanner._scan_single_extension_worker")
    @patch("vscode_scanner.scanner.as_completed")
    def test_scan_extensions_calls_callback_on_completion(
        self, mock_as_completed, mock_worker, mock_executor_class
    ):
        """_scan_extensions calls callback with completed event."""
        from vscode_scanner.scanner import _scan_extensions

        # Arrange
        mock_callback = Mock()
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        # Mock successful scan
        mock_future = Mock()
        mock_future.result.return_value = (
            {"scan_status": "success", "id": "test.ext"},
            False,  # not from cache
            True,  # should cache
        )
        mock_executor.submit.return_value = mock_future
        mock_as_completed.return_value = [mock_future]

        extensions = [{"id": "test.ext", "version": "1.0"}]
        args = Mock(workers=1, refresh_cache=False, no_cache=False, cache_max_age=30)

        # Act
        _scan_extensions(
            extensions,
            args,
            None,
            "2024-11-03T00:00:00Z",
            use_rich=False,
            quiet=False,
            on_progress=mock_callback,
        )

        # Assert - callback called with completed event
        completed_calls = [
            c for c in mock_callback.call_args_list if c[0][0] == "completed"
        ]
        assert len(completed_calls) == 1

        event_data = completed_calls[0][0][1]
        assert event_data["extension"]["id"] == "test.ext"
        assert event_data["from_cache"] is False
        assert event_data["index"] == 1
        assert event_data["total"] == 1

    @patch("vscode_scanner.scanner.ThreadPoolExecutor")
    @patch("vscode_scanner.scanner.as_completed")
    def test_scan_extensions_calls_callback_on_cached(
        self, mock_as_completed, mock_executor_class
    ):
        """_scan_extensions calls callback with cached event for cached results."""
        from vscode_scanner.scanner import _scan_extensions

        # Arrange
        mock_callback = Mock()
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        # Mock cached result
        mock_future = Mock()
        mock_future.result.return_value = (
            {"scan_status": "success", "id": "cached.ext"},
            True,  # from cache
            False,  # should not cache again
        )
        mock_executor.submit.return_value = mock_future
        mock_as_completed.return_value = [mock_future]

        extensions = [{"id": "cached.ext", "version": "1.0"}]
        args = Mock(workers=1, refresh_cache=False, no_cache=False, cache_max_age=30)

        # Act
        _scan_extensions(
            extensions,
            args,
            None,
            "2024-11-03T00:00:00Z",
            use_rich=False,
            quiet=False,
            on_progress=mock_callback,
        )

        # Assert - callback called with cached event
        cached_calls = [c for c in mock_callback.call_args_list if c[0][0] == "cached"]
        assert len(cached_calls) == 1

        event_data = cached_calls[0][0][1]
        assert event_data["extension"]["id"] == "cached.ext"
        assert event_data["from_cache"] is True

    @patch("vscode_scanner.scanner.ThreadPoolExecutor")
    @patch("vscode_scanner.scanner.as_completed")
    def test_scan_extensions_calls_callback_on_failure(
        self, mock_as_completed, mock_executor_class
    ):
        """_scan_extensions calls callback with failed event on exceptions."""
        from vscode_scanner.scanner import _scan_extensions

        # Arrange
        mock_callback = Mock()
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        # Mock future that raises exception
        mock_future = Mock()
        mock_future.result.side_effect = Exception("Scan failed")
        mock_executor.submit.return_value = mock_future
        mock_as_completed.return_value = [mock_future]

        extensions = [{"id": "failed.ext", "version": "1.0"}]
        args = Mock(workers=1, refresh_cache=False, no_cache=False, cache_max_age=30)

        # Act
        _scan_extensions(
            extensions,
            args,
            None,
            "2024-11-03T00:00:00Z",
            use_rich=False,
            quiet=False,
            on_progress=mock_callback,
        )

        # Assert - callback called with failed event
        failed_calls = [c for c in mock_callback.call_args_list if c[0][0] == "failed"]
        assert len(failed_calls) == 1

        event_data = failed_calls[0][0][1]
        assert event_data["extension"]["id"] == "failed.ext"
        assert "Scan failed" in event_data["error"]

    @patch("vscode_scanner.scanner.ThreadPoolExecutor")
    @patch("vscode_scanner.scanner.as_completed")
    def test_scan_extensions_works_without_callback(
        self, mock_as_completed, mock_executor_class
    ):
        """_scan_extensions works correctly when callback is None."""
        from vscode_scanner.scanner import _scan_extensions

        # Arrange
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        mock_future = Mock()
        mock_future.result.return_value = ({"scan_status": "success"}, False, True)
        mock_executor.submit.return_value = mock_future
        mock_as_completed.return_value = [mock_future]

        extensions = [{"id": "test.ext", "version": "1.0"}]
        args = Mock(workers=1, refresh_cache=False, no_cache=False, cache_max_age=30)

        # Act - no callback provided
        results, stats = _scan_extensions(
            extensions,
            args,
            None,
            "2024-11-03T00:00:00Z",
            use_rich=False,
            quiet=False,
            on_progress=None,
        )

        # Assert - scan completes successfully
        assert len(results) == 1
        assert stats["successful_scans"] == 1


# ============================================================================
# Error Recovery and Categorization Tests (15 tests)
# ============================================================================
# FROM: test_scanner_error_recovery.py


@pytest.mark.unit
class TestErrorCategorization(unittest.TestCase):
    """Test error categorization logic."""

    def test_categorize_timeout_error(self):
        """Timeout errors categorized correctly."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "Request timeout after 30 seconds"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "network_timeout")

    def test_categorize_timeout_timed_out(self):
        """'Timed out' errors categorized correctly."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "Connection timed out"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "network_timeout")

    def test_categorize_network_error(self):
        """Network errors categorized correctly."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "Connection refused"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "network_error")

    def test_categorize_connection_error(self):
        """Connection errors categorized correctly."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "Network connection failed"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "network_error")

    def test_categorize_rate_limit_error(self):
        """Rate limit errors categorized correctly."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "Rate limit exceeded"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "rate_limit")

    def test_categorize_rate_limit_429(self):
        """HTTP 429 errors categorized as rate limit."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "API error: 429 Too Many Requests"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "rate_limit")

    def test_categorize_api_error(self):
        """API errors categorized correctly."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "API returned error code 500"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "api_error")

    def test_categorize_unknown_error(self):
        """Unknown errors categorized as 'api_error'."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = "Something completely unexpected happened"

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "api_error")

    def test_categorize_empty_error(self):
        """Empty error message returns 'api_error'."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = ""

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "api_error")

    def test_categorize_none_error(self):
        """None error message returns 'api_error'."""
        from vscode_scanner.scanner import _categorize_error

        # Arrange
        error_msg = None

        # Act
        category = _categorize_error(error_msg)

        # Assert
        self.assertEqual(category, "api_error")


@pytest.mark.unit
class TestErrorMessageSimplification(unittest.TestCase):
    """Test error message simplification."""

    def test_simplify_rate_limit(self):
        """Rate limit error simplified."""
        from vscode_scanner.scanner import _simplify_error_message

        # Arrange
        error_type = "rate_limit"

        # Act
        simplified = _simplify_error_message(error_type)

        # Assert
        self.assertEqual(simplified, "Rate limit")

    def test_simplify_network_timeout(self):
        """Network timeout error simplified."""
        from vscode_scanner.scanner import _simplify_error_message

        # Arrange
        error_type = "network_timeout"

        # Act
        simplified = _simplify_error_message(error_type)

        # Assert
        self.assertEqual(simplified, "Network timeout")

    def test_simplify_network_error(self):
        """Network error simplified."""
        from vscode_scanner.scanner import _simplify_error_message

        # Arrange
        error_type = "network_error"

        # Act
        simplified = _simplify_error_message(error_type)

        # Assert
        self.assertEqual(simplified, "Network error")

    def test_simplify_api_error(self):
        """API error simplified."""
        from vscode_scanner.scanner import _simplify_error_message

        # Arrange
        error_type = "api_error"

        # Act
        simplified = _simplify_error_message(error_type)

        # Assert
        self.assertEqual(simplified, "API error")

    def test_simplify_unknown_type(self):
        """Unknown error type defaults to 'API error'."""
        from vscode_scanner.scanner import _simplify_error_message

        # Arrange
        error_type = "unknown_type"

        # Act
        simplified = _simplify_error_message(error_type)

        # Assert
        self.assertEqual(simplified, "API error")


# ============================================================================
# Edge Cases and Initialization Tests (6 tests)
# ============================================================================
# FROM: test_scanner_edge_cases.py


@pytest.mark.unit
class TestCacheInitializationMessages(unittest.TestCase):
    """Test cache initialization message display."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_cache_warning_plain_mode(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager_class,
    ):
        """Cache warnings display in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan
        from vscode_scanner.types import CacheWarning

        # Mock cache manager with warning
        mock_cache = Mock()
        mock_cache.get_init_messages.return_value = [
            CacheWarning(message="Cache directory created", context="init")
        ]
        mock_cache_manager_class.return_value = mock_cache

        # Mock discovery and scanning
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.return_value = {}

        # Act
        result = run_scan(plain=True, quiet=False)

        # Assert
        self.assertEqual(result, 0)
        mock_cache.get_init_messages.assert_called_once()

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_cache_error_plain_mode(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager_class,
    ):
        """Cache errors display in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan
        from vscode_scanner.types import CacheError

        # Mock cache manager with error
        mock_cache = Mock()
        mock_cache.get_init_messages.return_value = [
            CacheError(
                message="Database corrupted, recreating",
                context="init",
                recoverable=True,
            )
        ]
        mock_cache_manager_class.return_value = mock_cache

        # Mock discovery and scanning
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.return_value = {}

        # Act
        result = run_scan(plain=True, quiet=False)

        # Assert
        self.assertEqual(result, 0)
        mock_cache.get_init_messages.assert_called_once()

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner._print_summary")
    def test_cache_info_plain_mode(
        self,
        mock_print_summary,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager_class,
    ):
        """Cache info messages display in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan
        from vscode_scanner.types import CacheInfo

        # Mock cache manager with info
        mock_cache = Mock()
        mock_cache.get_init_messages.return_value = [
            CacheInfo(message="Cache initialized successfully", context="init")
        ]
        mock_cache_manager_class.return_value = mock_cache

        # Mock discovery and scanning
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.return_value = {}

        # Act
        result = run_scan(plain=True, quiet=False)

        # Assert
        self.assertEqual(result, 0)
        mock_cache.get_init_messages.assert_called_once()


@pytest.mark.unit
class TestExtensionDiscoveryErrors(unittest.TestCase):
    """Test extension discovery error handling."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner.show_error_help")
    def test_discovery_generic_exception_plain(
        self, mock_show_help, mock_discover, mock_cache_manager
    ):
        """Generic discovery exceptions handled in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.side_effect = PermissionError("Access denied")

        # Act
        result = run_scan(plain=True)

        # Assert
        self.assertEqual(result, 2)
        mock_show_help.assert_called_once()


@pytest.mark.unit
class TestEmptyExtensionList(unittest.TestCase):
    """Test empty extension list handling."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._write_output_file")
    def test_empty_list_with_output_file_plain(
        self, mock_write_file, mock_discover, mock_cache_manager
    ):
        """Empty extension list saves output file in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.return_value = ([], "/path", 3)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            # Act
            result = run_scan(output=output_path, plain=True)

            # Assert
            self.assertEqual(result, 0)
            mock_write_file.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._write_output_file")
    def test_empty_list_output_write_failure_plain(
        self, mock_write_file, mock_discover, mock_cache_manager
    ):
        """Output write failure on empty list returns exit code 2 in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.return_value = ([], "/path", 4)
        mock_write_file.side_effect = IOError("Disk full")

        # Act
        result = run_scan(output="/invalid/path/output.html", plain=True)

        # Assert
        self.assertEqual(result, 2)


# ============================================================================
# Output Generation Error Tests (2 tests)
# ============================================================================
# FROM: test_scanner_output_errors.py


@pytest.mark.unit
class TestOutputGenerationErrors(unittest.TestCase):
    """Test output generation exception handling."""

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner.show_error_help")
    def test_output_generation_exception_plain(
        self,
        mock_show_help,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager,
    ):
        """Output generation exceptions handled in plain mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.side_effect = ValueError("Invalid output format")

        # Act
        result = run_scan(plain=True)

        # Assert
        self.assertEqual(result, 2)
        mock_show_help.assert_called_once()

    @patch("vscode_scanner.scanner.CacheManager")
    @patch("vscode_scanner.scanner._discover_extensions")
    @patch("vscode_scanner.scanner._scan_extensions")
    @patch("vscode_scanner.scanner._apply_post_scan_filters")
    @patch("vscode_scanner.scanner._generate_output")
    @patch("vscode_scanner.scanner.show_error_help")
    def test_output_generation_exception_rich(
        self,
        mock_show_help,
        mock_generate_output,
        mock_post_filters,
        mock_scan_extensions,
        mock_discover,
        mock_cache_manager,
    ):
        """Output generation exceptions handled in rich mode."""
        # Arrange
        from vscode_scanner.scanner import run_scan

        mock_cache_manager.return_value = Mock(get_init_messages=Mock(return_value=[]))
        mock_discover.return_value = (
            [{"id": "test.ext", "version": "1.0"}],
            "/path",
            1,
        )
        mock_scan_extensions.return_value = (
            [],
            {"vulnerabilities_found": 0, "cached_results": 0, "fresh_scans": 0},
        )
        mock_post_filters.return_value = []
        mock_generate_output.side_effect = KeyError("missing_field")

        # Act
        result = run_scan(plain=False)

        # Assert
        self.assertEqual(result, 2)
        mock_show_help.assert_called_once()


if __name__ == "__main__":
    unittest.main()
