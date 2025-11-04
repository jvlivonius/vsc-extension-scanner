"""
Generic parallel execution pattern for testable concurrency.

This module provides a reusable base class for parallel execution patterns,
separating business logic from ThreadPoolExecutor mechanics.

Architecture:
- ParallelExecutor: Generic base class for parallel operations
- Subclasses implement: prepare_task(), process_result(), handle_error()
- Pure functions enable easy unit testing without real threads
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar

# Type variables for generic parallel execution
T = TypeVar("T")  # Input type (e.g., extension dict)
R = TypeVar("R")  # Result type (e.g., scan result dict)


class ParallelExecutor(Generic[T, R]):
    """
    Generic base class for parallel execution patterns.

    Separates ThreadPoolExecutor mechanics from business logic,
    enabling easy unit testing through pure function extraction.

    Subclasses must implement:
    - prepare_task(): Convert input item to worker function and args
    - process_result(): Handle successful worker result
    - handle_error(): Handle worker failure

    Example:
        class ScanOrchestrator(ParallelExecutor[Dict, Dict]):
            def prepare_task(self, ext):
                return _scan_single_extension_worker, (ext, cache, args)

            def process_result(self, item, result):
                self.results.append(result)
                self.stats.increment("success")

            def handle_error(self, item, error):
                self.stats.increment("failed")
                self.failed_items.append(item)
    """

    def __init__(self, max_workers: int = 3, on_progress: Optional[Callable] = None):
        """
        Initialize parallel executor.

        Args:
            max_workers: Number of concurrent workers (1-5)
            on_progress: Optional callback for progress updates
        """
        self.max_workers = min(max(max_workers, 1), 5)  # Clamp to 1-5
        self.on_progress = on_progress

    def prepare_task(self, item: T, index: int, total: int) -> Tuple[Callable, Tuple]:
        """
        Prepare a single task for execution.

        Args:
            item: Input item to process
            index: 1-based index of item in collection
            total: Total number of items

        Returns:
            Tuple of (worker_function, args_tuple)

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement prepare_task()")

    def process_result(self, item: T, result: R, index: int, total: int) -> None:
        """
        Process a successful worker result.

        Args:
            item: Original input item
            result: Worker function result
            index: 1-based index of item
            total: Total number of items

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement process_result()")

    def handle_error(self, item: T, error: Exception, index: int, total: int) -> None:
        """
        Handle a worker failure.

        Args:
            item: Original input item
            error: Exception raised by worker
            index: 1-based index of item
            total: Total number of items

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement handle_error()")

    def notify_start(self, total: int) -> None:
        """
        Notify progress callback of execution start.

        Args:
            total: Total number of items to process
        """
        if self.on_progress:
            self.on_progress("started", {"total": total})

    def notify_complete(self, item: T, result: R, index: int, total: int) -> None:
        """
        Notify progress callback of successful completion.

        Args:
            item: Processed item
            result: Worker result
            index: 1-based index
            total: Total number of items
        """
        if self.on_progress:
            self.on_progress(
                "completed",
                {"item": item, "result": result, "index": index, "total": total},
            )

    def notify_error(self, item: T, error: Exception, index: int, total: int) -> None:
        """
        Notify progress callback of failure.

        Args:
            item: Failed item
            error: Exception raised
            index: 1-based index
            total: Total number of items
        """
        if self.on_progress:
            self.on_progress(
                "failed",
                {"item": item, "error": str(error), "index": index, "total": total},
            )

    def execute(self, items: List[T]) -> None:
        """
        Execute parallel processing on all items.

        This is the main entry point that orchestrates ThreadPoolExecutor,
        while delegating business logic to prepare_task(), process_result(),
        and handle_error().

        Args:
            items: List of items to process in parallel
        """
        if not items:
            return

        total = len(items)
        self.notify_start(total)

        # Execute parallel processing with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {}
            for idx, item in enumerate(items, 1):
                worker_func, args = self.prepare_task(item, idx, total)
                future = executor.submit(worker_func, *args)
                futures[future] = (item, idx)

            # Collect results as they complete
            for future in as_completed(futures):
                item, idx = futures[future]
                try:
                    result = future.result()
                    self.process_result(item, result, idx, total)
                    # Subclasses handle progress notifications in process_result()
                except Exception as e:
                    self.handle_error(item, e, idx, total)
                    # Subclasses handle error notifications in handle_error()
