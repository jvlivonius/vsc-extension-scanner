"""
Unit tests for scanner progress callback pattern.

Tests the ProgressCallback class and callback integration in _scan_extensions()
to verify the refactored progress display logic.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call


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


if __name__ == "__main__":
    unittest.main()
