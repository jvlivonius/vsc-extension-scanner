#!/usr/bin/env python3
"""
Constants for VS Code Extension Scanner.

Centralized configuration values that can be easily tuned.
All magic numbers are extracted here for maintainability.
"""

# =============================================================================
# API Client Settings
# =============================================================================

# Request timing
DEFAULT_REQUEST_DELAY = 1.5  # Seconds between API requests
DEFAULT_POLL_INTERVAL = 2.0  # Seconds between status polls
DEFAULT_MAX_WAIT_SECONDS = 300  # Maximum wait for analysis (5 minutes)
API_TIMEOUT_SECONDS = 30  # HTTP request timeout

# Response size limits
MAX_RESPONSE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB maximum response size

# =============================================================================
# Retry Settings
# =============================================================================

# HTTP-level retry settings (retries individual API calls)
DEFAULT_MAX_RETRIES = 3  # Maximum retry attempts for HTTP requests
DEFAULT_RETRY_BASE_DELAY = 2.0  # Base delay for exponential backoff (seconds)

# Workflow-level retry settings (retries entire scan workflow)
DEFAULT_WORKFLOW_MAX_RETRIES = 2  # Maximum retry attempts for scan workflow
DEFAULT_WORKFLOW_RETRY_DELAY = 5.0  # Base delay between workflow retries (seconds)

# HTTP status codes that should trigger a retry (transient errors)
RETRYABLE_STATUS_CODES = {429, 502, 503, 504}

# Error message patterns that indicate retryable errors (HTTP level)
RETRYABLE_ERROR_PATTERNS = [
    "timeout",
    "timed out",
    "connection",
    "rate limit",
    "429",  # Rate limit in message
    "502",  # Bad Gateway in message
    "503",  # Service Unavailable in message
    "504",  # Gateway Timeout in message
]

# Error patterns that indicate workflow-level retry should be attempted
WORKFLOW_RETRYABLE_ERROR_PATTERNS = [
    "rate limit exceeded",
    "server error (http 503)",
    "server error (http 502)",
    "gateway timeout",
    "timeout after",  # Request timeout
    "analysis timeout",  # Polling timeout
    "service unavailable",
    "bad gateway",
]

# =============================================================================
# Cache Settings
# =============================================================================

DEFAULT_CACHE_MAX_AGE_DAYS = 7  # Default cache expiration
DATABASE_BATCH_SIZE = 10  # Number of results to batch before commit

# Cache report limits
CACHE_REPORT_MAX_AGE_DAYS = 365  # Maximum age for report generation

# =============================================================================
# File Size Limits
# =============================================================================

MAX_PACKAGE_JSON_SIZE = 1024 * 1024  # 1MB maximum for package.json files

# =============================================================================
# CLI Argument Bounds
# =============================================================================

# Delay bounds
MIN_DELAY_SECONDS = 0.1
MAX_DELAY_SECONDS = 30.0

# Retry bounds
MIN_RETRIES = 0
MAX_RETRIES = 10
MIN_RETRY_DELAY = 0.1
MAX_RETRY_DELAY = 60.0

# Cache age bounds
MIN_CACHE_AGE_DAYS = 1
MAX_CACHE_AGE_DAYS = 365

# =============================================================================
# Display Settings
# =============================================================================

# Progress indicators
PROGRESS_BAR_WIDTH = 40  # Character width for progress bars (if used)

# Table display limits
RESULTS_TABLE_LIMIT = 10  # Rows to show before "show more" (if implemented)

# =============================================================================
# Schema Version
# =============================================================================

OUTPUT_SCHEMA_VERSION = "2.0"  # JSON output schema version
