"""
Shared helpers for scan operations.

This module contains thread-safe statistics tracking and helper functions
shared between scanner.py and scan_orchestrator.py, avoiding circular dependencies.
"""

from datetime import datetime
from typing import Dict, Optional, Tuple


class ThreadSafeStats:
    """
    Thread-safe statistics collection for parallel scanning.

    This class provides thread-safe operations for collecting scan statistics
    from multiple worker threads. All operations are protected by a threading.Lock
    to prevent race conditions.

    Attributes:
        _lock: Threading lock for synchronization
        _stats: Internal statistics dictionary
    """

    def __init__(self):
        """Initialize thread-safe stats collection."""
        from threading import Lock

        self._lock = Lock()
        self._stats = {
            "successful_scans": 0,
            "failed_scans": 0,
            "vulnerabilities_found": 0,
            "cached_results": 0,
            "fresh_scans": 0,
            "failed_extensions": [],
            "api_client": None,
        }

    def increment(self, key: str, amount: int = 1):
        """
        Thread-safe increment operation.

        Args:
            key: Statistics key to increment
            amount: Amount to increment by (default: 1)
        """
        with self._lock:
            if key not in self._stats:
                self._stats[key] = 0
            self._stats[key] += amount

    def append_failed(self, ext_info: Dict):
        """
        Thread-safe list append for failed extensions.

        Args:
            ext_info: Extension failure information dict
        """
        with self._lock:
            self._stats["failed_extensions"].append(ext_info)

    def set(self, key: str, value):
        """
        Thread-safe set operation.

        Args:
            key: Statistics key to set
            value: Value to set
        """
        with self._lock:
            self._stats[key] = value

    def to_dict(self) -> Dict:
        """
        Get immutable copy of stats.

        Returns:
            Copy of statistics dictionary
        """
        with self._lock:
            return self._stats.copy()

    def get(self, key: str):
        """
        Thread-safe read operation.

        Args:
            key: Statistics key to read

        Returns:
            Value of the statistics key
        """
        with self._lock:
            return self._stats.get(key)


def _scan_single_extension_worker(
    ext: Dict, cache_manager: Optional["CacheManager"], args
) -> Tuple[Dict, bool, bool]:
    """
    Worker function to scan a single extension (thread-safe).

    Each worker gets its own API client instance for thread isolation.

    IMPORTANT: This function does NOT write to cache to avoid SQLite thread
    safety issues. Cache writes are handled by the main thread after all
    workers complete.

    Args:
        ext: Extension metadata dict
        cache_manager: Cache manager (used for reads only)
        args: Scan configuration

    Returns:
        Tuple of (result_dict, from_cache_bool, should_cache_bool)
    """
    # Import here to avoid circular dependency
    from .cache_manager import CacheManager
    from .vscan_api import VscanAPIClient

    extension_id = ext["id"]
    version = ext["version"]

    # Check cache first (read-only, thread-safe)
    cached_result = None
    if cache_manager and not args.refresh_cache:
        cached_result = cache_manager.get_cached_result(
            extension_id, version, max_age_days=args.cache_max_age
        )

    if cached_result:
        # Use cached result
        result = {**ext, **cached_result}

        # Add last_scanned_at from cache timestamp
        if "_cached_at" in cached_result:
            result["last_scanned_at"] = cached_result["_cached_at"]

        return result, True, False  # from_cache=True, should_cache=False

    # Create API client for this worker (thread isolation)
    api_client = VscanAPIClient(
        delay=args.delay,
        verbose=False,
        max_retries=args.max_retries,
        retry_base_delay=args.retry_delay,
    )

    # Scan via API
    publisher = ext.get("publisher", "")
    name = ext.get("name", "")

    result = api_client.scan_extension_with_retry(publisher, name)

    # Merge with discovery metadata
    result = {**ext, **result}

    # Add last_scanned_at for fresh scans
    result["last_scanned_at"] = datetime.now().isoformat() + "Z"

    # Determine if result should be cached (main thread will handle actual caching)
    should_cache = result.get("scan_status") == "success"

    return result, False, should_cache  # from_cache=False, should_cache=True/False


def _categorize_error(error_message: str) -> str:
    """
    Categorize error message into user-friendly error type.

    Args:
        error_message: The error message from API client

    Returns:
        Error type: 'rate_limit', 'network_timeout', 'network_error', or 'api_error'
    """
    if not error_message:
        return "api_error"

    error_lower = error_message.lower()

    # Check for specific error patterns
    if "rate limit" in error_lower or "429" in error_lower:
        return "rate_limit"
    elif "timeout" in error_lower or "timed out" in error_lower:
        return "network_timeout"
    elif "network" in error_lower or "connection" in error_lower:
        return "network_error"
    else:
        return "api_error"


def _simplify_error_message(error_type: str) -> str:
    """
    Convert error type to user-friendly message.

    Args:
        error_type: Categorized error type

    Returns:
        User-friendly error message
    """
    messages = {
        "rate_limit": "Rate limit",
        "network_timeout": "Network timeout",
        "network_error": "Network error",
        "api_error": "API error",
    }
    return messages.get(error_type, "API error")
