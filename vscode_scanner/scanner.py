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
    display_info, display_success, RICH_AVAILABLE
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
    plain: bool = False,
    quiet: bool = False,
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

    Returns:
        Exit code (0=clean, 1=vulnerabilities, 2=error)
    """
    # Setup logging
    setup_logging(False)  # No verbose logging needed

    # Determine if we should use Rich output
    use_rich = should_use_rich(plain_flag=plain) and not quiet

    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=cache_dir) if not no_cache else None

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
    class ScanConfig:
        pass

    args = ScanConfig()
    args.extensions_dir = extensions_dir
    args.output = output
    args.delay = delay
    args.max_retries = max_retries
    args.retry_delay = retry_delay
    args.cache_dir = cache_dir
    args.cache_max_age = cache_max_age
    args.refresh_cache = refresh_cache
    args.no_cache = no_cache
    args.publisher = publisher
    args.include_ids = include_ids
    args.exclude_ids = exclude_ids
    args.min_risk_level = min_risk_level

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
        if filter_table and RICH_AVAILABLE:
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
        results = _generate_output(scan_results, scan_duration, scan_timestamp, args, cache_stats_data, use_rich)
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
    _print_summary(extensions, stats, scan_duration, use_rich, results, quiet)

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
        'api_client': api_client
    }

    # Begin batch commit for cache operations
    if cache_manager:
        cache_manager.begin_batch()

    # Use Rich progress bar if available
    if use_rich and RICH_AVAILABLE and not quiet:
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

    stats['fresh_scans'] += 1


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
    if not args.min_risk_level:
        return scan_results

    # Define risk level hierarchy
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

    filtered = [result for result in scan_results if meets_risk_threshold(result)]

    if len(filtered) < len(scan_results):
        filtered_count = len(scan_results) - len(filtered)
        if use_rich:
            display_info(f"Filtered out {filtered_count} extensions below '{args.min_risk_level}' risk level", use_rich=True)
        else:
            log(f"Filtered out {filtered_count} extensions below '{args.min_risk_level}' risk level", "INFO")

    return filtered


def _generate_output(
    scan_results: List[Dict],
    scan_duration: float,
    scan_timestamp: str,
    args,
    cache_stats_data: Dict,
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
        cache_stats=cache_stats_data if not args.no_cache else None
    )

    # Output results
    if args.output:
        _write_output_file(args.output, results, is_html_output, use_rich)

    return results


def _write_output_file(output_path_str: str, results: Dict, is_html_output: bool, use_rich: bool):
    """Write output to file (JSON, HTML, or CSV)."""
    # Validate output path
    if not validate_path(output_path_str, allow_absolute=True, path_type="output"):
        if use_rich:
            display_error("Invalid output path", use_rich=True)
        log(sanitize_string(f"Path validation failed for: {output_path_str}", max_length=100), "ERROR")
        raise ValueError("Invalid output path")

    output_path = Path(output_path_str).resolve()

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


def _print_summary(extensions: List[Dict], stats: Dict, scan_duration: float, use_rich: bool, results: Dict, quiet: bool = False):
    """
    Print scan summary statistics.

    Args:
        extensions: List of discovered extensions
        stats: Scan statistics dict
        scan_duration: Total scan duration in seconds
        use_rich: Whether to use Rich formatting
        results: Full results dict for Rich display
        quiet: Show minimal single-line summary only
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

    if use_rich and RICH_AVAILABLE:
        # Get retry stats if available
        retry_stats = None
        if 'api_client' in stats:
            retry_stats = stats['api_client'].get_retry_stats()

        # Use Rich formatted summary
        display_summary(results, scan_duration, retry_stats=retry_stats, use_rich=True)

        # Show results table
        scan_results = results.get('extensions', [])
        if scan_results:
            from rich.console import Console
            console = Console()

            table = create_results_table(scan_results, show_all=True)
            if table:
                console.print()
                console.print(table)

            # Cache stats table
            cache_stats = results.get('summary', {}).get('cache_statistics')
            if cache_stats:
                cache_table = create_cache_stats_table(cache_stats)
                if cache_table:
                    console.print()
                    console.print(cache_table)

            # Retry stats table (new)
            if retry_stats:
                from .display import create_retry_stats_table
                retry_table = create_retry_stats_table(retry_stats)
                if retry_table:
                    console.print()
                    console.print(retry_table)
    else:
        # Plain output
        log("", "INFO", force=True)
        log("=" * 60, "INFO", force=True)
        log("Scan Complete!", "SUCCESS", force=True)
        log(f"Total extensions scanned: {len(extensions)}", "INFO", force=True)
        log(f"Successful scans: {stats['successful_scans']}", "INFO", force=True)
        log(f"Failed scans: {stats['failed_scans']}",
            "INFO" if stats['failed_scans'] == 0 else "WARNING", force=True)

        # Cache statistics
        if stats.get('cached_results', 0) > 0 or stats.get('fresh_scans', 0) > 0:
            log("", "INFO", force=True)
            log("Cache Statistics:", "INFO", force=True)
            log(f"  From cache: {stats['cached_results']} (⚡ instant)", "INFO", force=True)
            log(f"  Fresh scans: {stats['fresh_scans']} (🔍 API calls)", "INFO", force=True)
            if len(extensions) > 0:
                cache_hit_rate = (stats['cached_results'] / len(extensions)) * 100
                log(f"  Cache hit rate: {cache_hit_rate:.1f}%", "INFO", force=True)

        # Retry statistics
        if 'api_client' in stats:
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

        log("", "INFO", force=True)
        log(f"Vulnerabilities found: {stats['vulnerabilities_found']}",
            "INFO" if stats['vulnerabilities_found'] == 0 else "WARNING", force=True)
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
