"""
Scanner module for vscan - refactored main scan logic.

This module provides the core scanning functionality with support for
both Rich-formatted and plain text output.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Internal imports
from .extension_discovery import ExtensionDiscovery
from .vscan_api import VscanAPIClient
from .output_formatter import OutputFormatter
from .cache_manager import CacheManager
from .constants import DATABASE_BATCH_SIZE
from .utils import (
    log, setup_logging, validate_path, sanitize_string,
    show_error_help, get_error_type, safe_mkdir
)
from .display import (
    should_use_rich, create_scan_progress, create_results_table,
    create_cache_stats_table, create_filter_summary_table,
    ScanDashboard, display_summary, display_error, display_warning,
    display_info, display_success, display_failed_extensions, display_results_plain
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
    plain: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    parallel: bool = False,
    workers: int = 3,
    **kwargs
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
        plain: Disable Rich formatting
        quiet: Minimal output (single-line summary only)
        parallel: Enable parallel scanning with multiple workers
        workers: Number of parallel workers (2-5, default: 3)

    Returns:
        Exit code (0=clean, 1=vulnerabilities, 2=error)
    """
    # Setup logging
    setup_logging(False)  # No verbose logging needed

    # Determine if we should use Rich output
    use_rich = should_use_rich(plain_flag=plain) and not quiet

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

    # Print banner (plain mode only, Rich mode shows dashboard)
    if not use_rich and not quiet:
        log("VS Code Extension Scanner", "INFO")
        from ._version import __version__
        log(f"Version {__version__}", "INFO")
        log("=" * 60, "INFO")
        log("", "INFO")

    start_time = time.time()
    scan_timestamp = datetime.utcnow().isoformat() + 'Z'

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
        parallel=parallel,
        workers=workers
    )

    # Step 1: Discover extensions
    try:
        extensions, extensions_dir, original_count = _discover_extensions(args, use_rich, quiet)
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
        filter_table = create_filter_summary_table(args, original_count, len(extensions))
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
                _write_output_file(output, results, output.endswith('.html'), use_rich)
            except Exception as e:
                if use_rich:
                    display_error(f"Error writing output file: {type(e).__name__}", use_rich=True)
                else:
                    log(f"Error writing output file: {type(e).__name__}", "ERROR")
                return 2
            if use_rich:
                display_success(f"Empty results saved to {sanitize_string(output, max_length=100)}", use_rich=True)
            else:
                log(f"Empty results saved to {sanitize_string(output, max_length=100)}", "INFO")

        return 0

    # Step 2: Scan extensions
    if parallel:
        scan_results, stats = _scan_extensions_parallel(
            extensions, args, cache_manager, scan_timestamp, use_rich, quiet
        )
    else:
        scan_results, stats = _scan_extensions(
            extensions, args, cache_manager, scan_timestamp, use_rich, quiet
        )

    # Apply post-scan filters (risk level)
    scan_results = _apply_post_scan_filters(scan_results, args, use_rich)

    # Step 3: Generate output
    scan_duration = time.time() - start_time

    cache_stats_data = {
        "from_cache": stats['cached_results'],
        "fresh_scans": stats['fresh_scans'],
        "cache_hit_rate": round(
            (stats['cached_results'] / max(len(scan_results), 1) * 100), 1
        ) if scan_results else 0.0
    }

    try:
        results = _generate_output(scan_results, scan_duration, scan_timestamp, args, cache_stats_data, stats, use_rich)
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
    _print_summary(extensions, stats, scan_duration, use_rich, results, quiet, verbose)

    # Calculate and return exit code
    return _calculate_exit_code(stats['vulnerabilities_found'])


def _discover_extensions(args, use_rich: bool, quiet: bool) -> Tuple[List[Dict], Path, int]:
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
            display_success(f"Found extensions directory: {sanitize_string(str(extensions_dir), max_length=150)}", use_rich=True)
        else:
            log(f"Found VS Code extensions directory: {sanitize_string(str(extensions_dir), max_length=150)}", "SUCCESS")

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
            display_info(f"Filtered out {filtered_count} extensions based on criteria", use_rich=True)
            display_success(f"{len(extensions)} extensions selected for scanning", use_rich=True)
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
        include_ids = set(id.strip() for id in args.include_ids.split(',') if id.strip())

    if args.exclude_ids:
        exclude_ids = set(id.strip() for id in args.exclude_ids.split(',') if id.strip())

    # Apply filters with AND logic (all filters must match)
    def matches_filters(ext):
        ext_id = ext.get('id', '')
        publisher = ext.get('publisher', '')

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
    scan_timestamp: str,
    use_rich: bool,
    quiet: bool
) -> Tuple[List[Dict], Dict]:
    """
    Scan extensions for vulnerabilities.

    Args:
        extensions: List of extension metadata dicts
        args: Scan configuration
        cache_manager: CacheManager instance or None
        scan_timestamp: ISO timestamp of scan start
        use_rich: Whether to use Rich formatting
        quiet: Minimal output mode

    Returns:
        Tuple of (scan_results, stats_dict)
    """
    if not quiet and not use_rich:
        log("", "INFO")
        log("Step 2: Scanning extensions for vulnerabilities...", "INFO")

        if cache_manager and not args.refresh_cache:
            log(f"Cache enabled (max age: {args.cache_max_age} days)", "INFO")
        elif args.no_cache:
            log("Cache disabled", "INFO")
        elif args.refresh_cache:
            log("Forcing cache refresh for scanned extensions", "INFO")

    api_client = VscanAPIClient(
        delay=args.delay,
        verbose=False,  # No verbose logging
        max_retries=args.max_retries,
        retry_base_delay=args.retry_delay
    )

    scan_results = []
    stats = {
        'vulnerabilities_found': 0,
        'successful_scans': 0,
        'failed_scans': 0,
        'cached_results': 0,
        'fresh_scans': 0,
        'failed_extensions': [],  # Track failed extensions with details
        'api_client': api_client
    }

    # Begin batch commit for cache operations
    if cache_manager:
        cache_manager.begin_batch()

    # Use Rich progress bar if available
    if use_rich and not quiet:
        from rich.console import Console
        console = Console()

        progress = create_scan_progress()
        if progress:
            with progress:
                task = progress.add_task("Scanning extensions...", total=len(extensions))

                for idx, ext in enumerate(extensions, 1):
                    _scan_single_extension(
                        ext, idx, len(extensions), cache_manager, args,
                        api_client, stats, scan_results, use_rich
                    )
                    progress.update(task, advance=1)

                    # Commit batch every DATABASE_BATCH_SIZE fresh scans
                    if cache_manager and stats['fresh_scans'] % DATABASE_BATCH_SIZE == 0:
                        cache_manager.commit_batch()
                        cache_manager.begin_batch()
    else:
        # Plain output
        for idx, ext in enumerate(extensions, 1):
            _scan_single_extension(
                ext, idx, len(extensions), cache_manager, args,
                api_client, stats, scan_results, use_rich
            )

            # Commit batch every DATABASE_BATCH_SIZE fresh scans
            if cache_manager and stats['fresh_scans'] % DATABASE_BATCH_SIZE == 0:
                cache_manager.commit_batch()
                cache_manager.begin_batch()

    # Commit any remaining results
    if cache_manager:
        cache_manager.commit_batch()

    if not quiet and not use_rich:
        log("", "INFO")

    return scan_results, stats


def _scan_extensions_parallel(
    extensions: List[Dict],
    args,
    cache_manager: Optional[CacheManager],
    scan_timestamp: str,
    use_rich: bool,
    quiet: bool
) -> Tuple[List[Dict], Dict]:
    """
    Scan extensions in parallel using ThreadPoolExecutor.

    Args:
        extensions: List of extension metadata dicts
        args: Scan configuration
        cache_manager: CacheManager instance or None (thread-safe)
        scan_timestamp: ISO timestamp of scan start
        use_rich: Whether to use Rich formatting
        quiet: Minimal output mode

    Returns:
        Tuple of (scan_results, stats_dict)
    """
    # Validate and cap worker count (based on PoC findings)
    max_workers = min(max(args.workers, 2), 5)  # Range: 2-5

    if not quiet and not use_rich:
        log("", "INFO")
        log(f"Step 2: Scanning extensions for vulnerabilities (parallel mode: {max_workers} workers)...", "INFO")

        if cache_manager and not args.refresh_cache:
            log(f"Cache enabled (max age: {args.cache_max_age} days)", "INFO")
        elif args.no_cache:
            log("Cache disabled", "INFO")
        elif args.refresh_cache:
            log("Forcing cache refresh for scanned extensions", "INFO")

    # Initialize stats with thread-safe counters
    stats = {
        'vulnerabilities_found': 0,
        'successful_scans': 0,
        'failed_scans': 0,
        'cached_results': 0,
        'fresh_scans': 0,
        'failed_extensions': [],
        'api_client': None  # Will be set from worker results
    }

    scan_results = []
    results_to_cache = []  # Collect results for main-thread batch caching

    # Use Rich progress bar if available
    if use_rich and not quiet:
        from rich.console import Console
        console = Console()

        progress = create_scan_progress()
        if progress:
            with progress:
                task = progress.add_task(f"Scanning ({max_workers} workers)...", total=len(extensions))

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all scan tasks
                    futures = {}
                    for ext in extensions:
                        future = executor.submit(
                            _scan_single_extension_worker,
                            ext,
                            cache_manager,
                            args
                        )
                        futures[future] = ext

                    # Collect results as they complete
                    for future in as_completed(futures):
                        ext = futures[future]
                        try:
                            result, from_cache, should_cache = future.result()

                            scan_results.append(result)

                            # Collect for caching (main thread will handle writes)
                            if should_cache:
                                results_to_cache.append((ext['id'], ext['version'], result))

                            # Update stats (safe operations)
                            if result.get('scan_status') == 'success':
                                if result.get('vulnerabilities', {}).get('count', 0) > 0:
                                    stats['vulnerabilities_found'] += 1
                                stats['successful_scans'] += 1
                            else:
                                stats['failed_scans'] += 1
                                # Track failed extension
                                error_message = result.get('error', '')
                                error_type = _categorize_error(error_message)
                                stats['failed_extensions'].append({
                                    'id': ext['id'],
                                    'name': ext.get('display_name', ext.get('name', ext['id'])),
                                    'error_type': error_type,
                                    'error_message': _simplify_error_message(error_type)
                                })

                            if from_cache:
                                stats['cached_results'] += 1
                            else:
                                stats['fresh_scans'] += 1

                            # Update progress display
                            progress.update(task, advance=1)

                        except Exception as e:
                            # Handle worker failure
                            stats['failed_scans'] += 1
                            error_type = _categorize_error(str(e))
                            stats['failed_extensions'].append({
                                'id': ext['id'],
                                'name': ext.get('display_name', ext.get('name', ext['id'])),
                                'error_type': error_type,
                                'error_message': _simplify_error_message(error_type)
                            })

                            progress.update(task, advance=1)
    else:
        # Plain output
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scan tasks
            futures = {}
            for idx, ext in enumerate(extensions, 1):
                future = executor.submit(
                    _scan_single_extension_worker,
                    ext,
                    cache_manager,
                    args
                )
                futures[future] = (ext, idx)

            # Collect results as they complete
            for future in as_completed(futures):
                ext, idx = futures[future]
                try:
                    result, from_cache, should_cache = future.result()

                    scan_results.append(result)

                    # Collect for caching (main thread will handle writes)
                    if should_cache:
                        results_to_cache.append((ext['id'], ext['version'], result))

                    # Log progress in plain mode
                    if not quiet:
                        extension_id = ext['id']
                        version = ext['version']
                        progress_prefix = f"[{idx}/{len(extensions)}]"
                        if from_cache:
                            log(f"{progress_prefix} {extension_id} v{version}... ⚡ Cached", "INFO")
                        else:
                            log(f"{progress_prefix} {extension_id} v{version}... 🔍 Fresh", "INFO")

                    # Update stats
                    if result.get('scan_status') == 'success':
                        if result.get('vulnerabilities', {}).get('count', 0) > 0:
                            stats['vulnerabilities_found'] += 1
                        stats['successful_scans'] += 1
                    else:
                        stats['failed_scans'] += 1
                        error_message = result.get('error', '')
                        error_type = _categorize_error(error_message)
                        stats['failed_extensions'].append({
                            'id': ext['id'],
                            'name': ext.get('display_name', ext.get('name', ext['id'])),
                            'error_type': error_type,
                            'error_message': _simplify_error_message(error_type)
                        })

                    if from_cache:
                        stats['cached_results'] += 1
                    else:
                        stats['fresh_scans'] += 1

                except Exception as e:
                    # Handle worker failure
                    stats['failed_scans'] += 1
                    error_type = _categorize_error(str(e))
                    stats['failed_extensions'].append({
                        'id': ext['id'],
                        'name': ext.get('display_name', ext.get('name', ext['id'])),
                        'error_type': error_type,
                        'error_message': _simplify_error_message(error_type)
                    })

    # Batch write all results to cache in main thread (thread-safe)
    if cache_manager and results_to_cache:
        cache_manager.begin_batch()
        for ext_id, version, result in results_to_cache:
            try:
                cache_manager.save_result_batch(ext_id, version, result)
            except Exception:
                # Cache errors should not fail the scan
                pass
        cache_manager.commit_batch()

    if not quiet and not use_rich:
        log("", "INFO")

    return scan_results, stats


def _scan_single_extension_worker(
    ext: Dict,
    cache_manager: Optional[CacheManager],
    args
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
    extension_id = ext['id']
    version = ext['version']

    # Check cache first (read-only, thread-safe)
    cached_result = None
    if cache_manager and not args.refresh_cache:
        cached_result = cache_manager.get_cached_result(
            extension_id,
            version,
            max_age_days=args.cache_max_age
        )

    if cached_result:
        # Use cached result
        result = {**ext, **cached_result}

        # Add last_scanned_at from cache timestamp
        if '_cached_at' in cached_result:
            result['last_scanned_at'] = cached_result['_cached_at']

        return result, True, False  # from_cache=True, should_cache=False

    # Create API client for this worker (thread isolation)
    api_client = VscanAPIClient(
        delay=args.delay,
        verbose=False,
        max_retries=args.max_retries,
        retry_base_delay=args.retry_delay
    )

    # Scan via API
    publisher = ext.get('publisher', '')
    name = ext.get('name', '')

    result = api_client.scan_extension_with_retry(publisher, name)

    # Merge with discovery metadata
    result = {**ext, **result}

    # Add last_scanned_at for fresh scans
    result['last_scanned_at'] = datetime.now().isoformat() + 'Z'

    # Determine if result should be cached (main thread will handle actual caching)
    should_cache = result.get('scan_status') == 'success'

    return result, False, should_cache  # from_cache=False, should_cache=True/False


def _scan_single_extension(
    ext: Dict,
    idx: int,
    total: int,
    cache_manager: Optional[CacheManager],
    args,
    api_client: VscanAPIClient,
    stats: Dict,
    scan_results: List[Dict],
    use_rich: bool
):
    """Scan a single extension (extracted for clarity)."""
    extension_id = ext['id']
    version = ext['version']
    progress_prefix = f"[{idx}/{total}]"

    # Check cache first (unless refresh or no-cache is requested)
    cached_result = None
    if cache_manager and not args.refresh_cache:
        cached_result = cache_manager.get_cached_result(
            extension_id,
            version,
            max_age_days=args.cache_max_age
        )

    if cached_result:
        # Use cached result
        _process_cached_result(cached_result, ext, extension_id, version,
                               progress_prefix, stats, scan_results, use_rich)
    else:
        # Scan fresh from API
        _scan_extension_fresh(ext, extension_id, version, progress_prefix,
                             api_client, cache_manager, stats, scan_results, use_rich)


def _process_cached_result(
    cached_result: Dict,
    ext: Dict,
    extension_id: str,
    version: str,
    progress_prefix: str,
    stats: Dict,
    scan_results: List[Dict],
    use_rich: bool
):
    """Process a cached scan result."""
    if not use_rich:
        log(f"{progress_prefix} {extension_id} v{version}... ⚡ Cached", "INFO")

    # Merge with discovery metadata
    result = {**ext, **cached_result}

    # Add last_scanned_at from cache timestamp
    if '_cached_at' in cached_result:
        result['last_scanned_at'] = cached_result['_cached_at']

    scan_results.append(result)

    # Update stats
    if result.get('vulnerabilities', {}).get('count', 0) > 0:
        stats['vulnerabilities_found'] += 1

    stats['successful_scans'] += 1
    stats['cached_results'] += 1


def _scan_extension_fresh(
    ext: Dict,
    extension_id: str,
    version: str,
    progress_prefix: str,
    api_client: VscanAPIClient,
    cache_manager: Optional[CacheManager],
    stats: Dict,
    scan_results: List[Dict],
    use_rich: bool
):
    """Scan an extension fresh from the API."""
    if not use_rich:
        log(f"{progress_prefix} Scanning {extension_id} v{version}... 🔍", "INFO")

    # Scan via API with workflow-level retry
    publisher = ext.get('publisher', '')
    name = ext.get('name', '')

    result = api_client.scan_extension_with_retry(publisher, name)

    # Merge with discovery metadata
    result = {**ext, **result}

    # Add last_scanned_at for fresh scans (current time)
    result['last_scanned_at'] = datetime.now().isoformat() + 'Z'

    # Cache the result if cache is enabled (using batch mode)
    if cache_manager and result.get('scan_status') == 'success':
        try:
            cache_manager.save_result_batch(extension_id, version, result)
        except Exception:
            # Cache errors should not fail the scan
            # Error already logged by cache_manager
            pass

    scan_results.append(result)

    # Update stats
    if result.get('scan_status') == 'success':
        if result.get('vulnerabilities', {}).get('count', 0) > 0:
            stats['vulnerabilities_found'] += 1
        stats['successful_scans'] += 1
    else:
        stats['failed_scans'] += 1
        # Track failed extension with categorized error
        error_message = result.get('error', '')
        error_type = _categorize_error(error_message)
        stats['failed_extensions'].append({
            'id': extension_id,
            'name': ext.get('display_name', ext.get('name', extension_id)),
            'error_type': error_type,
            'error_message': _simplify_error_message(error_type)
        })

    stats['fresh_scans'] += 1


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
    metadata = result.get('metadata', {})
    publisher_info = metadata.get('publisher', {})
    # Only use metadata source if it actually exists (has content)
    if isinstance(publisher_info, dict) and publisher_info:
        return publisher_info.get('verified', False)

    # Fallback to top-level publisher (rare case)
    publisher = result.get('publisher', {})
    if isinstance(publisher, dict):
        return publisher.get('verified', False)

    # String publishers are unverified
    return False


def _apply_post_scan_filters(scan_results: List[Dict], args, use_rich: bool) -> List[Dict]:
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
        risk_hierarchy = {
            'low': 0,
            'medium': 1,
            'high': 2,
            'critical': 3
        }

        min_level = risk_hierarchy.get(args.min_risk_level, 0)

        def meets_risk_threshold(result):
            risk_level = result.get('risk_level', 'low')
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
            vulns = result.get('vulnerabilities', {})
            if isinstance(vulns, dict):
                return vulns.get('count', 0) > 0
            return False
        filtered = [r for r in filtered if has_vulns(r)]

    if args.without_vulnerabilities:
        def no_vulns(result):
            vulns = result.get('vulnerabilities', {})
            if isinstance(vulns, dict):
                return vulns.get('count', 0) == 0
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

        filter_msg = f"Filtered out {filtered_count} extension(s) ({', '.join(filters_applied)})"

        if use_rich:
            display_info(filter_msg, use_rich=True)
        else:
            log(filter_msg, "INFO")

    return filtered


def _categorize_error(error_message: str) -> str:
    """
    Categorize error message into user-friendly error type.

    Args:
        error_message: The error message from API client

    Returns:
        Error type: 'rate_limit', 'network_timeout', 'network_error', or 'api_error'
    """
    if not error_message:
        return 'api_error'

    error_lower = error_message.lower()

    # Check for specific error patterns
    if 'rate limit' in error_lower or '429' in error_lower:
        return 'rate_limit'
    elif 'timeout' in error_lower or 'timed out' in error_lower:
        return 'network_timeout'
    elif 'network' in error_lower or 'connection' in error_lower:
        return 'network_error'
    else:
        return 'api_error'


def _simplify_error_message(error_type: str) -> str:
    """
    Convert error type to user-friendly message.

    Args:
        error_type: Categorized error type

    Returns:
        User-friendly error message
    """
    messages = {
        'rate_limit': 'Rate limit',
        'network_timeout': 'Network timeout',
        'network_error': 'Network error',
        'api_error': 'API error'
    }
    return messages.get(error_type, 'API error')


def _generate_output(
    scan_results: List[Dict],
    scan_duration: float,
    scan_timestamp: str,
    args,
    cache_stats_data: Dict,
    stats: Dict,
    use_rich: bool
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
    is_html_output = args.output and args.output.endswith('.html')

    # Format output with all available data
    formatter = OutputFormatter()
    results = formatter.format_output(
        scan_results,
        scan_timestamp,
        scan_duration,
        cache_stats=cache_stats_data if not args.no_cache else None,
        failed_extensions=stats.get('failed_extensions', [])
    )

    # Output results
    if args.output:
        _write_output_file(args.output, results, is_html_output, use_rich)

    return results


def _write_output_file(output_path_str: str, results: Dict, is_html_output: bool, use_rich: bool):
    """Write output to file (JSON, HTML, or CSV)."""
    # Path validation happens in cli.py before resolve() to preserve relative/absolute distinction
    # Here we receive already-resolved absolute paths
    output_path = Path(output_path_str)

    # Create parent directories with restricted permissions (cross-platform)
    safe_mkdir(output_path.parent, mode=0o755)

    # Detect CSV format
    is_csv_output = output_path.suffix.lower() == '.csv'

    # Generate CSV, HTML, or JSON based on file extension
    if is_csv_output:
        # CSV output
        if use_rich:
            display_info("Generating CSV export...", use_rich=True)
        else:
            log("Generating CSV export...", "INFO")

        formatter = OutputFormatter()
        csv_content = formatter.format_csv(results.get('extensions', []))

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            f.write(csv_content)

        if use_rich:
            display_success(f"CSV export written to {sanitize_string(output_path_str, max_length=100)}", use_rich=True)
        else:
            log(f"CSV export written to {sanitize_string(output_path_str, max_length=100)}", "SUCCESS")
    elif is_html_output:
        from .html_report_generator import HTMLReportGenerator

        if use_rich:
            display_info("Generating HTML report...", use_rich=True)
        else:
            log("Generating HTML report...", "INFO")

        html_gen = HTMLReportGenerator()
        html_content = html_gen.generate_report(results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        if use_rich:
            display_success(f"HTML report written to {sanitize_string(output_path_str, max_length=100)}", use_rich=True)
        else:
            log(f"HTML report written to {sanitize_string(output_path_str, max_length=100)}", "SUCCESS")
    else:
        # JSON output
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        if use_rich:
            display_success(f"Results written to {sanitize_string(output_path_str, max_length=100)}", use_rich=True)
        else:
            log(f"Results written to {sanitize_string(output_path_str, max_length=100)}", "SUCCESS")


def _print_summary(extensions: List[Dict], stats: Dict, scan_duration: float, use_rich: bool, results: Dict, quiet: bool = False, verbose: bool = False):
    """
    Print scan summary statistics.

    Args:
        extensions: List of discovered extensions
        stats: Scan statistics dict
        scan_duration: Total scan duration in seconds
        use_rich: Whether to use Rich formatting
        results: Full results dict for Rich display
        quiet: Show minimal single-line summary only
        verbose: Show all operational details (cache, retry stats, timing)
    """
    # Quiet mode: show minimal single-line summary
    if quiet:
        total = len(extensions)
        vulns = stats['vulnerabilities_found']
        if vulns > 0:
            print(f"Scanned {total} extensions - Found {vulns} vulnerabilities")
        else:
            print(f"Scanned {total} extensions - No vulnerabilities found ✓")
        return

    # Standard mode (default): security-focused, hide operational details
    # Verbose mode: show everything (cache stats, retry stats, timing)
    if use_rich:
        # Get retry stats if available
        retry_stats = None
        if 'api_client' in stats and stats['api_client'] is not None:
            retry_stats = stats['api_client'].get_retry_stats()

        # Use Rich formatted summary (pass verbose flag)
        display_summary(results, scan_duration, retry_stats=retry_stats, use_rich=True, verbose=verbose)

        # Show results table
        scan_results = results.get('extensions', [])
        if scan_results:
            from rich.console import Console
            console = Console()

            table = create_results_table(scan_results, show_all=True)
            if table:
                console.print()
                console.print(table)

            # Cache stats table (only in verbose mode)
            if verbose:
                cache_stats = results.get('summary', {}).get('cache_statistics')
                if cache_stats:
                    cache_table = create_cache_stats_table(cache_stats)
                    if cache_table:
                        console.print()
                        console.print(cache_table)

            # Retry stats table (only in verbose mode)
            if verbose and retry_stats:
                from .display import create_retry_stats_table
                retry_table = create_retry_stats_table(retry_stats)
                if retry_table:
                    console.print()
                    console.print(retry_table)

        # Display failed extensions if any (both standard and verbose modes)
        if stats.get('failed_extensions'):
            display_failed_extensions(stats['failed_extensions'], use_rich=True)
    else:
        # Plain output
        log("", "INFO", force=True)
        log("=" * 60, "INFO", force=True)
        log("Scan Complete!", "SUCCESS", force=True)
        log(f"Total extensions scanned: {len(extensions)}", "INFO", force=True)
        log(f"Successful scans: {stats['successful_scans']}", "INFO", force=True)
        log(f"Failed scans: {stats['failed_scans']}",
            "INFO" if stats['failed_scans'] == 0 else "WARNING", force=True)

        # Show scan results list (all extensions)
        scan_results = results.get('extensions', [])
        if scan_results:
            display_results_plain(scan_results)

        # Cache statistics (only in verbose mode)
        if verbose and (stats.get('cached_results', 0) > 0 or stats.get('fresh_scans', 0) > 0):
            log("", "INFO", force=True)
            log("Cache Statistics:", "INFO", force=True)
            log(f"  From cache: {stats['cached_results']} (⚡ instant)", "INFO", force=True)
            log(f"  Fresh scans: {stats['fresh_scans']} (🔍 API calls)", "INFO", force=True)
            if len(extensions) > 0:
                cache_hit_rate = (stats['cached_results'] / len(extensions)) * 100
                log(f"  Cache hit rate: {cache_hit_rate:.1f}%", "INFO", force=True)

        # Retry statistics (only in verbose mode and if retries occurred)
        if verbose and 'api_client' in stats and stats['api_client'] is not None:
            retry_stats = stats['api_client'].get_retry_stats()
            http_retries = retry_stats.get('total_retries', 0)
            workflow_retries = retry_stats.get('total_workflow_retries', 0)

            if http_retries > 0 or workflow_retries > 0:
                log("", "INFO")
                log("Retry Statistics:", "INFO")

                # HTTP-level retries
                if http_retries > 0:
                    log(f"  HTTP retry attempts: {http_retries}", "INFO")
                    log(f"    Successful: {retry_stats.get('successful_retries', 0)}", "INFO")
                    failed_http = retry_stats.get('failed_after_retries', 0)
                    if failed_http > 0:
                        log(f"    Failed: {failed_http}", "WARNING")

                # Workflow-level retries
                if workflow_retries > 0:
                    log(f"  Workflow retry attempts: {workflow_retries}", "INFO")
                    log(f"    Successful: {retry_stats.get('successful_workflow_retries', 0)}", "INFO")
                    failed_workflow = retry_stats.get('failed_after_workflow_retries', 0)
                    if failed_workflow > 0:
                        log(f"    Failed (need manual rescan): {failed_workflow}", "WARNING")

        # Display failed extensions if any (both standard and verbose modes)
        if stats.get('failed_extensions'):
            display_failed_extensions(stats['failed_extensions'], use_rich=False)

        log("", "INFO", force=True)
        log(f"Vulnerabilities found: {stats['vulnerabilities_found']}",
            "INFO" if stats['vulnerabilities_found'] == 0 else "WARNING", force=True)

        # Timing details (only in verbose mode)
        if verbose:
            log(f"Scan duration: {scan_duration:.1f} seconds", "INFO", force=True)
            if len(extensions) > 0:
                avg_time = scan_duration / len(extensions)
                log(f"Average time per extension: {avg_time:.1f}s", "INFO", force=True)

        log("=" * 60, "INFO", force=True)


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

    Args:
        args: Scan configuration
        original_count: Number of extensions before filtering
        use_rich: Whether to use Rich formatting
    """
    active_filters = []

    if args.publisher:
        active_filters.append(f"  --publisher: {args.publisher}")
    if args.include_ids:
        active_filters.append(f"  --include-ids: {args.include_ids}")
    if args.exclude_ids:
        active_filters.append(f"  --exclude-ids: {args.exclude_ids}")
    if args.min_risk_level:
        active_filters.append(f"  --min-risk-level: {args.min_risk_level}")

    if active_filters:
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

        # Provide helpful suggestions
        if original_count > 0:
            msg = f"Tip: {original_count} extensions were found, but all were filtered out."
            if use_rich:
                display_info(msg, use_rich=True)
            else:
                log(msg, "INFO")

        if args.publisher:
            msg1 = "Tip: Publisher names are case-insensitive but must match exactly."
            msg2 = "     Run without filters to see available publishers."
            if use_rich:
                display_info(msg1, use_rich=True)
                display_info(msg2, use_rich=True)
            else:
                log(msg1, "INFO")
                log(msg2, "INFO")
