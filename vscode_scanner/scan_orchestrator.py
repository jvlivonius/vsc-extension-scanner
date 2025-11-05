"""
ScanOrchestrator - Specialized parallel executor for vulnerability scanning.

This module implements the ScanOrchestrator pattern, separating business logic
from ThreadPoolExecutor mechanics for improved testability.

Architecture:
- Extends ParallelExecutor for parallel scanning
- Integrates with CacheManager for persistence
- Tracks statistics with ThreadSafeStats
- Provides progress callbacks for UI integration
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

from .cache_manager import CacheManager
from .parallel_executor import ParallelExecutor
from .scan_helpers import (
    ThreadSafeStats,
    _categorize_error,
    _scan_single_extension_worker,
    _simplify_error_message,
)


class ScanOrchestrator(ParallelExecutor[Dict, Tuple[Dict, bool, bool]]):
    """
    Orchestrates parallel vulnerability scanning with caching and statistics.

    Responsibilities:
    - Parallel execution via ThreadPoolExecutor
    - Cache integration (instant persistence)
    - Thread-safe statistics collection
    - Progress callback integration
    - Error categorization and tracking

    Separates business logic (what to do) from concurrency (how to do it).

    Example:
        orchestrator = ScanOrchestrator(
            cache_manager=cache,
            args=args,
            max_workers=3,
            on_progress=progress_callback
        )
        results, stats = orchestrator.scan(extensions)
    """

    def __init__(
        self,
        cache_manager: Optional[CacheManager],
        args: Any,
        max_workers: int = 3,
        on_progress: Optional[Callable] = None,
    ):
        """
        Initialize scan orchestrator.

        Args:
            cache_manager: CacheManager instance or None
            args: Scan configuration object
            max_workers: Number of concurrent workers (1-5)
            on_progress: Optional callback for progress updates
        """
        super().__init__(max_workers=max_workers, on_progress=on_progress)
        self.cache_manager = cache_manager
        self.args = args
        self.stats = ThreadSafeStats()
        self.scan_results: List[Dict] = []

    def prepare_task(
        self, item: Dict, index: int, total: int
    ) -> Tuple[Callable, Tuple]:
        """
        Prepare a single extension scan task.

        Args:
            item: Extension metadata dict
            index: 1-based index of extension
            total: Total number of extensions

        Returns:
            Tuple of (worker_function, args_tuple)
        """
        return _scan_single_extension_worker, (item, self.cache_manager, self.args)

    def process_result(
        self, item: Dict, result: Tuple[Dict, bool, bool], index: int, total: int
    ) -> None:
        """
        Process a successful scan result.

        Handles:
        - Result storage
        - Cache persistence
        - Statistics updates
        - Progress notifications

        Args:
            item: Extension metadata dict
            result: Tuple of (scan_result, from_cache, should_cache)
            index: 1-based index
            total: Total number of extensions
        """
        scan_result, from_cache, should_cache = result

        # Store scan result
        self.scan_results.append(scan_result)

        # Instant cache persistence (zero data loss on interruption)
        if should_cache and self.cache_manager:
            try:
                self.cache_manager.save_result(item["id"], item["version"], scan_result)
            except Exception as e:
                # Cache errors should not fail the scan
                from .utils import log

                log(
                    f"Cache save failed for {item['id']}: {e}",
                    "WARNING",
                )

        # Update statistics (thread-safe operations)
        self._update_stats_for_result(scan_result, item)

        if from_cache:
            self.stats.increment("cached_results")
        else:
            self.stats.increment("fresh_scans")

        # Notify progress callback
        if self.on_progress:
            event = "cached" if from_cache else "completed"
            self.on_progress(
                event,
                {
                    "extension": item,
                    "result": scan_result,
                    "from_cache": from_cache,
                    "index": index,
                    "total": total,
                },
            )

    def handle_error(
        self, item: Dict, error: Exception, index: int, total: int
    ) -> None:
        """
        Handle a worker failure.

        Handles:
        - Error categorization
        - Statistics updates
        - Failed extension tracking
        - Progress notifications

        Args:
            item: Extension metadata dict
            error: Exception raised by worker
            index: 1-based index
            total: Total number of extensions
        """
        # Track failure statistics
        self.stats.increment("failed_scans")

        # Categorize and track error
        error_type = _categorize_error(str(error))
        self.stats.append_failed(
            {
                "id": item["id"],
                "name": item.get("display_name", item.get("name", item["id"])),
                "error_type": error_type,
                "error_message": _simplify_error_message(error_type),
            }
        )

        # Notify progress callback
        if self.on_progress:
            self.on_progress(
                "failed",
                {
                    "extension": item,
                    "error": str(error),
                    "index": index,
                    "total": total,
                },
            )

    def _update_stats_for_result(self, scan_result: Dict, ext: Dict) -> None:
        """
        Update statistics based on scan result.

        Pure business logic for stats updates, extracted for testability.

        Args:
            scan_result: Scan result dictionary
            ext: Extension metadata dict
        """
        if scan_result.get("scan_status") == "success":
            if scan_result.get("vulnerabilities", {}).get("count", 0) > 0:
                self.stats.increment("vulnerabilities_found")
            self.stats.increment("successful_scans")
        else:
            self.stats.increment("failed_scans")
            # Track failed extension
            error_message = scan_result.get("error", "")
            error_type = _categorize_error(error_message)
            self.stats.append_failed(
                {
                    "id": ext["id"],
                    "name": ext.get("display_name", ext.get("name", ext["id"])),
                    "error_type": error_type,
                    "error_message": _simplify_error_message(error_type),
                }
            )

    def scan(self, extensions: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Execute parallel scanning on all extensions.

        Main entry point for vulnerability scanning.

        Args:
            extensions: List of extension metadata dicts

        Returns:
            Tuple of (scan_results, stats_dict)
        """
        # Reset state for new scan
        self.scan_results = []

        # Execute parallel processing
        # False positive: execute() is ParallelExecutor method for parallel task execution, not SQL
        self.execute(extensions)  # nosemgrep: sql-injection-risk-execute

        # Return results and statistics
        return self.scan_results, self.stats.to_dict()
