"""
Common data types and result objects.

This module provides shared data types used across the application,
particularly for returning structured results from infrastructure
and application layers to presentation layer.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class CacheWarning:
    """
    Warning from cache operations.

    Used by cache_manager to return warnings to callers instead of
    displaying directly, maintaining layer separation.

    Attributes:
        message: Human-readable warning message
        context: Context where warning occurred (for logging/debugging)

    Example:
        warning = CacheWarning(
            message="Filtered out 5 invalid extension IDs",
            context="cleanup_invalid_entries"
        )
    """
    message: str
    context: str


@dataclass
class CacheError:
    """
    Error from cache operations.

    Used by cache_manager to return errors to callers instead of
    displaying directly, maintaining layer separation.

    Attributes:
        message: Human-readable error message
        context: Context where error occurred (for logging/debugging)
        recoverable: Whether the operation can be retried or continued

    Example:
        error = CacheError(
            message="Failed to handle corrupted database",
            context="database_integrity_check",
            recoverable=False
        )
    """
    message: str
    context: str
    recoverable: bool


@dataclass
class CacheInfo:
    """
    Informational message from cache operations.

    Used by cache_manager to return informational messages to callers
    instead of displaying directly, maintaining layer separation.

    Attributes:
        message: Human-readable informational message
        context: Context where info was generated (for logging/debugging)

    Example:
        info = CacheInfo(
            message="Creating fresh cache database...",
            context="database_recovery"
        )
    """
    message: str
    context: str


@dataclass
class ConfigWarning:
    """
    Warning from configuration operations.

    Used by config_manager to return warnings to callers instead of
    displaying directly, maintaining layer separation.

    Attributes:
        message: Human-readable warning message
        context: Context where warning occurred (for logging/debugging)

    Example:
        warning = ConfigWarning(
            message="Invalid schema_version in config file, using v1",
            context="load_config"
        )
    """
    message: str
    context: str
