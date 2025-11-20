"""
Scanner module for vscan - refactored main scan logic.

This module provides the core scanning functionality with Rich-formatted
output and optional quiet mode for CI/CD environments.
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Internal imports
from .extension_discovery import ExtensionDiscovery
from .vscan_api import VscanAPIClient
from .output_formatter import OutputFormatter
from .cache_manager import CacheManager
from .constants import DATABASE_BATCH_SIZE
from .scan_helpers import (
    ThreadSafeStats,
    _categorize_error,
    _scan_single_extension_worker,
    _simplify_error_message,
)
from .utils import (
    log,
    setup_logging,
    validate_path,
    sanitize_string,
    show_error_help,
    get_error_type,
    safe_mkdir,
)
from .display import (
    create_scan_progress,
    create_results_table,
    create_cache_stats_table,
    create_filter_summary_table,
    ScanDashboard,
    display_summary,
    display_error,
    display_warning,
    display_info,
    display_success,
    display_failed_extensions,
)


def run_scan(
    extensions_dir: Optional[str] = None,
    output: Optional[str] = None,
    delay: float = 1.5,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    cache_dir: Optional[str] = None,
    cache_max_age: int = 7,
    refresh_cache: bool = False,
    no_cache: bool = False,
    publisher: Optional[str] = None,
    include_ids: Optional[str] = None,
    exclude_ids: Optional[str] = None,
    min_risk_level: Optional[str] = None,
    verified_only: bool = False,
    unverified_only: bool = False,
    with_vulnerabilities: bool = False,
    without_vulnerabilities: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    detailed: bool = False,
    workers: int = 3,
    **_kwargs,  # Reserved for future extensibility
) -> int:
    """
    Run the extension security scan.

    Args:
        extensions_dir: Custom VS Code extensions directory
        output: Output file path (.json or .html)
        delay: Delay between API requests
        max_retries: Maximum retry attempts
        retry_delay: Base delay for exponential backoff
        cache_dir: Custom cache directory
        cache_max_age: Maximum cache age in days
        refresh_cache: Force refresh of scanned extensions (ignore cache for filtered extensions)
        no_cache: Disable caching
        publisher: Filter by publisher name
        include_ids: Comma-separated extension IDs to include
        exclude_ids: Comma-separated extension IDs to exclude
        min_risk_level: Minimum risk level filter
        quiet: Minimal output (single-line summary only)
        verbose: Show operational details (cache stats, retry stats, timing)
        detailed: Show detailed security module breakdown
        workers: Number of concurrent workers (1-5, default: 3)

    Returns:
        Exit code (0=clean, 1=vulnerabilities, 2=error)
    """
    # Setup logging
    setup_logging(False)  # No verbose logging needed

    # Determine if we should use Rich output
    use_rich = not quiet  # Always use Rich formatting unless quiet mode

    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=cache_dir) if not no_cache else None

    # Display any cache initialization messages (corrupted database warnings, etc.)
    if cache_manager:
        from .types import CacheWarning, CacheError, CacheInfo

        init_messages = cache_manager.get_init_messages()
        for msg in init_messages:
            if isinstance(msg, CacheWarning):
                if use_rich:
                    display_warning(msg.message, use_rich=True)
                else:
                    log(f"WARNING: {msg.message}", "WARNING")
            elif isinstance(msg, CacheError):
                if use_rich:
                    display_error(msg.message, use_rich=True)
                else:
                    log(f"ERROR: {msg.message}", "ERROR")
            elif isinstance(msg, CacheInfo):
                if use_rich:
                    display_info(msg.message, use_rich=True)
                else:
                    log(f"INFO: {msg.message}", "INFO")

    # Note: Banner display is now handled by Rich dashboard only
    # Quiet mode suppresses all output except errors and summary

    start_time = time.time()
    scan_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create args-like object for compatibility with existing functions
    from types import SimpleNamespace

    args = SimpleNamespace(
        extensions_dir=extensions_dir,
        output=output,
        delay=delay,
        max_retries=max_retries,
        retry_delay=retry_delay,
        cache_dir=cache_dir,
        cache_max_age=cache_max_age,
        refresh_cache=refresh_cache,
        no_cache=no_cache,
        publisher=publisher,
        include_ids=include_ids,
        exclude_ids=exclude_ids,
        min_risk_level=min_risk_level,
        verified_only=verified_only,
        unverified_only=unverified_only,
        with_vulnerabilities=with_vulnerabilities,
        without_vulnerabilities=without_vulnerabilities,
        workers=workers,
    )

    # Step 1: Discover extensions
    try:
        extensions, extensions_dir, original_count = _discover_extensions(
            args, use_rich, quiet
        )
    except FileNotFoundError as e:
        error_msg = sanitize_string(str(e), max_length=200)
        if use_rich:
            display_error(error_msg, use_rich=True)
        else:
            log(error_msg, "ERROR")
        error_type = get_error_type(error_msg)
        show_error_help(error_type)
        return 2
    except Exception as e:
        error_msg = sanitize_string(str(e), max_length=200)
        if use_rich:
            display_error(f"Error discovering extensions: {error_msg}", use_rich=True)
        else:
            log(f"Error discovering extensions: {error_msg}", "ERROR")
        error_type = get_error_type(error_msg)
        show_error_help(error_type)
        return 2

    # Show filter summary if filters were applied
    if use_rich and len(extensions) < original_count:
        filter_table = create_filter_summary_table(
            args, original_count, len(extensions)
        )
        if filter_table:
            from rich.console import Console

            console = Console()
            console.print(filter_table)

    # Handle empty extension list
    if len(extensions) == 0:
        if use_rich:
            display_warning("No extensions found to scan", use_rich=True)
        else:
            log("No extensions found to scan", "WARNING")

        _show_filter_help(args, original_count, use_rich)

        # Still generate output for file if requested
        if output:
            formatter = OutputFormatter()
            results = formatter.format_output([], scan_timestamp, 0)
            try:
                _write_output_file(output, results, output.endswith(".html"), use_rich)
            except Exception as e:
                if use_rich:
                    display_error(
                        f"Error writing output file: {type(e).__name__}", use_rich=True
                    )
                else:
                    log(f"Error writing output file: {type(e).__name__}", "ERROR")
                return 2
            if use_rich:
                display_success(
                    f"Empty results saved to {sanitize_string(output, max_length=100)}",
                    use_rich=True,
                )
            else:
                log(
                    f"Empty results saved to {sanitize_string(output, max_length=100)}",
                    "INFO",
                )

        return 0

    # Step 2: Scan extensions
    # Create progress callback for display
    from .display import ProgressCallback

    max_workers = min(max(args.workers, 1), 5)
    worker_info = f"{max_workers} worker{'s' if max_workers > 1 else ''}"
    progress_callback = ProgressCallback(
        use_rich=use_rich, quiet=quiet, worker_info=worker_info
    )

    try:
        scan_results, stats = _scan_extensions(
            extensions,
            args,
            cache_manager,
            scan_timestamp,
            use_rich,
            quiet,
            on_progress=progress_callback,
        )
    finally:
        progress_callback.cleanup()

    # Apply post-scan filters (risk level)
    scan_results = _apply_post_scan_filters(scan_results, args, use_rich)

    # Step 3: Generate output
    scan_duration = time.time() - start_time

    cache_stats_data = {
        "from_cache": stats["cached_results"],
        "fresh_scans": stats["fresh_scans"],
        "cache_hit_rate": (
            round((stats["cached_results"] / max(len(scan_results), 1) * 100), 1)
            if scan_results
            else 0.0
        ),
    }

    try:
        results = _generate_output(
            scan_results,
            scan_duration,
            scan_timestamp,
            args,
            cache_stats_data,
            stats,
            use_rich,
        )
    except Exception as e:
        error_msg = sanitize_string(str(e), max_length=200)
        if use_rich:
            display_error(f"Error generating output: {type(e).__name__}", use_rich=True)
            display_error(f"Details: {error_msg}", use_rich=True)
        else:
            log(f"Error generating output: {type(e).__name__}", "ERROR")
            log(f"Details: {error_msg}", "ERROR")
        error_type = get_error_type(error_msg)
        show_error_help(error_type)
        return 2

    # Print summary (always show, but minimal in quiet mode)
    _print_summary(
        extensions, stats, scan_duration, use_rich, results, quiet, verbose, detailed
    )

    # Calculate and return exit code
    return _calculate_exit_code(stats["vulnerabilities_found"])


def _discover_extensions(
    args, use_rich: bool, quiet: bool
) -> Tuple[List[Dict], Path, int]:
    """
    Discover installed VS Code extensions.

    Args:
        args: Scan configuration
        use_rich: Whether to use Rich formatting
        quiet: Minimal output mode

    Returns:
        Tuple of (extensions_list, extensions_dir, original_count)
    """
    if not quiet:
        if use_rich:
            display_info("Discovering VS Code extensions...", use_rich=True)
        else:
            log("Step 1: Discovering VS Code extensions...", "INFO")

    discovery = ExtensionDiscovery(custom_dir=args.extensions_dir)

    extensions_dir = discovery.find_extensions_directory()

    if not quiet:
        if use_rich:
            display_success(
                f"Found extensions directory: {sanitize_string(str(extensions_dir), max_length=150)}",
                use_rich=True,
            )
        else:
            log(
                f"Found VS Code extensions directory: {sanitize_string(str(extensions_dir), max_length=150)}",
                "SUCCESS",
            )

    extensions = discovery.discover_extensions()

    if not quiet:
        if use_rich:
            display_success(f"Discovered {len(extensions)} extensions", use_rich=True)
        else:
            log(f"Discovered {len(extensions)} extensions", "SUCCESS")

    # Apply pre-scan filters
    original_count = len(extensions)
    extensions = _apply_pre_scan_filters(extensions, args)

    if len(extensions) < original_count and not quiet:
        filtered_count = original_count - len(extensions)
        if use_rich:
            display_info(
                f"Filtered out {filtered_count} extensions based on criteria",
                use_rich=True,
            )
            display_success(
                f"{len(extensions)} extensions selected for scanning", use_rich=True
            )
        else:
            log(f"Filtered out {filtered_count} extensions based on criteria", "INFO")
            log(f"{len(extensions)} extensions selected for scanning", "SUCCESS")

    return extensions, extensions_dir, original_count


def _apply_pre_scan_filters(extensions: List[Dict], args) -> List[Dict]:
    """
    Apply filters that can be applied before scanning.

    Args:
        extensions: List of extension metadata dicts
        args: Scan configuration

    Returns:
        Filtered list of extensions
    """
    filtered = extensions

    # Parse include/exclude IDs if provided
    include_ids = None
    exclude_ids = None

    if args.include_ids:
        include_ids = set(
            id.strip() for id in args.include_ids.split(",") if id.strip()
        )

    if args.exclude_ids:
        exclude_ids = set(
            id.strip() for id in args.exclude_ids.split(",") if id.strip()
        )

    # Apply filters with AND logic (all filters must match)
    def matches_filters(ext):
        ext_id = ext.get("id", "")
        publisher = ext.get("publisher", "")

        # Include IDs filter (if specified, extension MUST be in the list)
        if include_ids and ext_id not in include_ids:
            return False

        # Exclude IDs filter (if specified, extension MUST NOT be in the list)
        if exclude_ids and ext_id in exclude_ids:
            return False

        # Publisher filter (if specified, extension MUST match publisher)
        if args.publisher and publisher.lower() != args.publisher.lower():
            return False

        return True

    filtered = [ext for ext in filtered if matches_filters(ext)]
    return filtered


def _scan_extensions(
    extensions: List[Dict],
    args,
    cache_manager: Optional[CacheManager],
    _scan_timestamp: str,  # Reserved for future use
    use_rich: bool,
    quiet: bool,
    on_progress: Optional[callable] = None,  # NEW: Progress callback
) -> Tuple[List[Dict], Dict]:
    """
    Scan extensions for vulnerabilities using ScanOrchestrator.

    Uses configurable number of workers (1-5). Workers=1 provides sequential behavior.

    This function now delegates to ScanOrchestrator for improved testability
    and separation of concerns. The orchestrator handles:
    - Parallel execution via ThreadPoolExecutor
    - Cache integration and persistence
    - Thread-safe statistics collection
    - Progress callback notifications
    - Error handling and categorization

    Args:
        extensions: List of extension metadata dicts
        args: Scan configuration
        cache_manager: CacheManager instance or None (thread-safe)
        scan_timestamp: ISO timestamp of scan start
        use_rich: Whether to use Rich formatting
        quiet: Minimal output mode
        on_progress: Optional callback(event, data) for progress updates

    Returns:
        Tuple of (scan_results, stats_dict)
    """
    # Import here to avoid circular dependency
    from .scan_orchestrator import ScanOrchestrator

    # Validate and cap worker count (1-5, default: 3)
    max_workers = min(max(args.workers, 1), 5)  # Range: 1-5
    worker_info = f"{max_workers} worker{'s' if max_workers > 1 else ''}"

    if not quiet and not use_rich:
        log("", "INFO")
        log(
            f"Step 2: Scanning extensions for vulnerabilities ({worker_info})...",
            "INFO",
        )

        if cache_manager and not args.refresh_cache:
            log(f"Cache enabled (max age: {args.cache_max_age} days)", "INFO")
        elif args.no_cache:
            log("Cache disabled", "INFO")
        elif args.refresh_cache:
            log("Forcing cache refresh for scanned extensions", "INFO")

    # Create orchestrator with cache, args, and progress callback
    orchestrator = ScanOrchestrator(
        cache_manager=cache_manager,
        args=args,
        max_workers=max_workers,
        on_progress=on_progress,
    )

    # Execute parallel scanning (all complexity handled by orchestrator)
    scan_results, stats = orchestrator.scan(extensions)

    if not quiet and not use_rich:
        log("", "INFO")

    # Return results and statistics
    return scan_results, stats


def _get_verification_status(result: Dict) -> bool:
    """
    Get publisher verification status from result.

    Checks metadata.publisher.verified first (from API scan),
    then falls back to publisher.verified (rare case).
    This matches the display logic in display.py.

    Args:
        result: Extension scan result dict

    Returns:
        True if publisher is verified, False otherwise
    """
    # Check metadata first (from API scan - primary source)
    metadata = result.get("metadata", {})
    publisher_info = metadata.get("publisher", {})
    # Only use metadata source if it actually exists (has content)
    if isinstance(publisher_info, dict) and publisher_info:
        return publisher_info.get("verified", False)

    # Fallback to top-level publisher (rare case)
    publisher = result.get("publisher", {})
    if isinstance(publisher, dict):
        return publisher.get("verified", False)

    # String publishers are unverified
    return False


def _apply_post_scan_filters(
    scan_results: List[Dict], args, use_rich: bool
) -> List[Dict]:
    """
    Apply filters that require scan results.

    Args:
        scan_results: List of scan result dicts
        args: Scan configuration
        use_rich: Whether to use Rich formatting

    Returns:
        Filtered list of scan results
    """
    original_count = len(scan_results)
    filtered = scan_results

    # Filter by risk level
    if args.min_risk_level:
        risk_hierarchy = {"low": 0, "medium": 1, "high": 2, "critical": 3}

        min_level = risk_hierarchy.get(args.min_risk_level, 0)

        def meets_risk_threshold(result):
            risk_level = result.get("risk_level", "low")
            result_level = risk_hierarchy.get(risk_level, 0)
            return result_level >= min_level

        filtered = [result for result in filtered if meets_risk_threshold(result)]

    # Filter by publisher verification status
    if args.verified_only:
        filtered = [r for r in filtered if _get_verification_status(r)]

    if args.unverified_only:
        filtered = [r for r in filtered if not _get_verification_status(r)]

    # Filter by vulnerability presence
    if args.with_vulnerabilities:

        def has_vulns(result):
            vulns = result.get("vulnerabilities", {})
            if isinstance(vulns, dict):
                return vulns.get("count", 0) > 0
            return False

        filtered = [r for r in filtered if has_vulns(r)]

    if args.without_vulnerabilities:

        def no_vulns(result):
            vulns = result.get("vulnerabilities", {})
            if isinstance(vulns, dict):
                return vulns.get("count", 0) == 0
            return True  # No vulnerabilities dict means no vulns

        filtered = [r for r in filtered if no_vulns(r)]

    # Show filtering summary if any extensions were filtered out
    if len(filtered) < original_count:
        filtered_count = original_count - len(filtered)
        filters_applied = []

        if args.min_risk_level:
            filters_applied.append(f"min risk level: {args.min_risk_level}")
        if args.verified_only:
            filters_applied.append("verified publishers only")
        if args.unverified_only:
            filters_applied.append("unverified publishers only")
        if args.with_vulnerabilities:
            filters_applied.append("with vulnerabilities")
        if args.without_vulnerabilities:
            filters_applied.append("without vulnerabilities")

        filter_msg = (
            f"Filtered out {filtered_count} extension(s) ({', '.join(filters_applied)})"
        )

        if use_rich:
            display_info(filter_msg, use_rich=True)
        else:
            log(filter_msg, "INFO")

    return filtered


def _generate_output(
    scan_results: List[Dict],
    scan_duration: float,
    scan_timestamp: str,
    args,
    cache_stats_data: Dict,
    stats: Dict,
    use_rich: bool,
) -> Dict:
    """
    Generate and write output (JSON or HTML).

    Args:
        scan_results: List of scan result dicts
        scan_duration: Total scan duration in seconds
        scan_timestamp: ISO timestamp of scan start
        args: Scan configuration
        cache_stats_data: Cache statistics dict
        stats: Scan statistics including failed_extensions
        use_rich: Whether to use Rich formatting

    Returns:
        Formatted results dict
    """
    if not use_rich:
        log("Step 3: Generating results...", "INFO")

    # Detect output format
    is_html_output = args.output and args.output.endswith(".html")

    # Format output with all available data
    formatter = OutputFormatter()
    results = formatter.format_output(
        scan_results,
        scan_timestamp,
        scan_duration,
        cache_stats=cache_stats_data if not args.no_cache else None,
        failed_extensions=stats.get("failed_extensions", []),
    )

    # Output results
    if args.output:
        _write_output_file(args.output, results, is_html_output, use_rich)

    return results


def _write_output_file(
    output_path_str: str, results: Dict, is_html_output: bool, use_rich: bool
):
    """
    Write output to file (JSON, HTML, or CSV).

    Delegates to OutputWriter for all format handling and file operations.

    Args:
        output_path_str: Absolute path to output file
        results: Scan results dictionary
        is_html_output: Legacy parameter (unused, kept for backward compatibility)
        use_rich: Whether to use rich display for progress messages
    """
    from .output_writer import OutputWriter

    writer = OutputWriter()
    writer.write_output(output_path_str, results, use_rich)


def _print_summary(
    extensions: List[Dict],
    stats: Dict,
    scan_duration: float,
    use_rich: bool,
    results: Dict,
    quiet: bool = False,
    verbose: bool = False,
    detailed: bool = False,
):
    """
    Print scan summary statistics.

    Delegates formatting logic to SummaryFormatter for testability.

    Args:
        extensions: List of discovered extensions
        stats: Scan statistics dict
        scan_duration: Total scan duration in seconds
        use_rich: Whether to use Rich formatting
        results: Full results dict for Rich display
        quiet: Show minimal single-line summary only
        verbose: Show all operational details (cache, retry stats, timing)
        detailed: Show detailed security module breakdown for each extension
    """
    from .summary_formatter import SummaryFormatter

    formatter = SummaryFormatter()

    # Quiet mode: show minimal single-line summary
    if quiet:
        summary_text = formatter.format_quiet_summary(
            len(extensions), stats["vulnerabilities_found"]
        )
        print(summary_text)
        return

    # Standard mode (default): security-focused, hide operational details
    # Verbose mode: show everything (cache stats, retry stats, timing)
    if use_rich:
        # Get retry stats if available
        retry_stats = formatter.extract_retry_stats(stats)

        # Use Rich formatted summary (pass verbose flag)
        display_summary(
            results,
            scan_duration,
            retry_stats=retry_stats,
            use_rich=True,
            verbose=verbose,
        )

        # Show results table
        if formatter.has_scan_results(results):
            from rich.console import Console

            console = Console()

            scan_results = formatter.get_scan_results(results)
            table = create_results_table(scan_results, show_all=True)
            if table:
                console.print()
                console.print(table)

            # Detailed module breakdown (when --detailed flag is set)
            if detailed and scan_results:
                from .display import format_security_modules

                console.print()
                console.print(
                    "[bold cyan]═══ Detailed Security Module Breakdown ═══[/bold cyan]"
                )
                console.print()

                for result in scan_results:
                    # Show extension header (sanitize user input from filesystem)
                    ext_name = result.get("display_name") or result.get(
                        "name", "Unknown"
                    )
                    ext_id = result.get("id", "")
                    ext_name_safe = sanitize_string(ext_name)
                    ext_id_safe = sanitize_string(ext_id)
                    console.print(
                        f"[bold white]Extension:[/bold white] {ext_name_safe} ({ext_id_safe})"
                    )
                    console.print()

                    # Show module breakdown
                    format_security_modules(result, detailed=True, console=console)

            # Cache stats table (only in verbose mode)
            if formatter.should_show_cache_stats(results, verbose):
                cache_stats = formatter.get_cache_stats(results)
                cache_table = create_cache_stats_table(cache_stats)
                if cache_table:
                    console.print()
                    console.print(cache_table)

            # Retry stats table (only in verbose mode)
            if formatter.should_show_retry_stats(retry_stats, verbose):
                from .display import create_retry_stats_table

                retry_table = create_retry_stats_table(retry_stats)
                if retry_table:
                    console.print()
                    console.print(retry_table)

        # Display failed extensions if any (both standard and verbose modes)
        if stats.get("failed_extensions"):
            display_failed_extensions(stats["failed_extensions"], use_rich=True)


def _calculate_exit_code(vulnerabilities_found: int) -> int:
    """
    Calculate exit code based on scan results.

    Args:
        vulnerabilities_found: Number of vulnerabilities found

    Returns:
        Exit code (0 = clean, 1 = vulnerabilities found)
    """
    # Exit codes:
    # 0 = scan completed successfully, no vulnerabilities
    # 1 = scan completed successfully, vulnerabilities found
    # 2 = scan failed due to errors (handled elsewhere)
    return 1 if vulnerabilities_found > 0 else 0


def _show_filter_help(args, original_count: int, use_rich: bool):
    """
    Show helpful information about active filters when no extensions match.

    Delegates formatting logic to FilterHelpGenerator for testability.

    Args:
        args: Scan configuration
        original_count: Number of extensions before filtering
        use_rich: Whether to use Rich formatting
    """
    from .filter_help_generator import FilterHelpGenerator

    generator = FilterHelpGenerator()

    # Extract active filters
    active_filters = generator.extract_active_filters(args)

    if active_filters:
        # Display main message
        if use_rich:
            display_warning("No extensions match the specified filters:", use_rich=True)
            for filter_info in active_filters:
                display_info(filter_info, use_rich=True)
        else:
            log("", "INFO")
            log("No extensions match the specified filters:", "WARNING")
            for filter_info in active_filters:
                log(filter_info, "INFO")
            log("", "INFO")

        # Generate and display suggestions
        has_publisher = generator.has_publisher_filter(args)
        suggestions = generator.generate_suggestion_messages(
            original_count, has_publisher
        )

        for suggestion in suggestions:
            if use_rich:
                display_info(suggestion, use_rich=True)
            else:
                log(suggestion, "INFO")
