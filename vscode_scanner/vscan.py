#!/usr/bin/env python3
"""
VS Code Extension Security Scanner

A standalone Python CLI tool that performs security audits of installed VS Code
extensions by leveraging the vscan.dev security analysis service.

Usage:
    python vscan.py                           # Scan all extensions
    python vscan.py --output results.json    # Save to file
    python vscan.py --verbose                # Show detailed progress
"""

import argparse
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Import our modules
from .extension_discovery import ExtensionDiscovery
from .vscan_api import VscanAPIClient
from .output_formatter import OutputFormatter
from .cache_manager import CacheManager
from .utils import log, setup_logging, validate_path, sanitize_string, show_error_help, get_error_type, safe_mkdir
from ._version import __version__ as VERSION


def load_config_file() -> dict:
    """
    Load configuration from ~/.vscan/config.json if it exists.

    Returns:
        dict: Configuration dictionary, or empty dict if file doesn't exist or is invalid
    """
    config_path = Path.home() / ".vscan" / "config.json"

    if not config_path.exists():
        return {}

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Validate that config is a dictionary
        if not isinstance(config, dict):
            log("Warning: config.json must be a JSON object, ignoring", "WARNING")
            return {}

        return config

    except json.JSONDecodeError as e:
        log(f"Warning: Invalid JSON in config.json: {e}", "WARNING")
        return {}
    except Exception as e:
        log(f"Warning: Could not read config.json: {e}", "WARNING")
        return {}


def bounded_int(min_val: int, max_val: int):
    """Create a validator for bounded integer values."""
    def validator(value):
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"must be an integer, got '{value}'")

        if ivalue < min_val or ivalue > max_val:
            raise argparse.ArgumentTypeError(
                f"must be between {min_val} and {max_val}, got {ivalue}"
            )
        return ivalue
    return validator


def bounded_float(min_val: float, max_val: float):
    """Create a validator for bounded float values."""
    def validator(value):
        try:
            fvalue = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"must be a number, got '{value}'")

        if fvalue < min_val or fvalue > max_val:
            raise argparse.ArgumentTypeError(
                f"must be between {min_val} and {max_val}, got {fvalue}"
            )
        return fvalue
    return validator


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="VS Code Extension Security Scanner - Audit installed extensions using vscan.dev",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                      Scan all extensions (JSON to stdout)
  %(prog)s --output results.json               Save JSON results to file
  %(prog)s --output report.html                Generate interactive HTML report
  %(prog)s --verbose                           Show detailed progress
  %(prog)s --publisher microsoft               Only scan Microsoft extensions
  %(prog)s --min-risk-level high               Only show high/critical risk extensions
  %(prog)s --include-ids "ms-python.python"    Scan only specific extension
  %(prog)s --exclude-ids "local.test"          Exclude specific extensions

Configuration:
  Settings can be saved in ~/.vscan/config.json (JSON format)
  Example: {"delay": 2.0, "max_retries": 5, "exclude_ids": "local.test"}
  Command-line arguments override config file settings

For more information, see: https://github.com/your-repo/vsc-extension-scanner
        """
    )

    parser.add_argument(
        '--extensions-dir', '-d',
        type=str,
        default=None,
        help='Path to VS Code extensions directory (default: auto-detect)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output file path for results (.json or .html, default: stdout)'
    )

    parser.add_argument(
        '--delay', '-t',
        type=bounded_float(0.1, 30.0),
        default=1.5,
        help='Delay between API requests in seconds, 0.1-30.0 (default: 1.5)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output to stderr'
    )

    # Retry-related arguments
    parser.add_argument(
        '--max-retries',
        type=bounded_int(0, 10),
        default=3,
        help='Maximum retry attempts for failed API requests, 0-10 (default: 3)'
    )

    parser.add_argument(
        '--retry-delay',
        type=bounded_float(0.1, 60.0),
        default=2.0,
        help='Base delay for exponential backoff in seconds, 0.1-60.0 (default: 2.0)'
    )

    # Cache-related arguments
    parser.add_argument(
        '--cache-dir',
        type=str,
        default=None,
        help='Cache directory path (default: ~/.vscan/)'
    )

    parser.add_argument(
        '--cache-max-age',
        type=bounded_int(1, 365),
        default=7,
        help='Maximum age of cached results in days, 1-365 (default: 7)'
    )

    parser.add_argument(
        '--refresh-cache',
        action='store_true',
        help='Force refresh of all cached results'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable cache (always scan fresh)'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear all cached results and exit'
    )

    parser.add_argument(
        '--cache-stats',
        action='store_true',
        help='Show cache statistics and exit'
    )

    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed security analysis (dependencies, risk factors, score breakdown)'
    )

    # Filtering arguments
    parser.add_argument(
        '--include-ids',
        type=str,
        default=None,
        help='Comma-separated list of extension IDs to scan (e.g., "ms-python.python,esbenp.prettier-vscode")'
    )

    parser.add_argument(
        '--exclude-ids',
        type=str,
        default=None,
        help='Comma-separated list of extension IDs to exclude from scan'
    )

    parser.add_argument(
        '--publisher',
        type=str,
        default=None,
        help='Only scan extensions from this publisher'
    )

    parser.add_argument(
        '--min-risk-level',
        type=str,
        choices=['low', 'medium', 'high', 'critical'],
        default=None,
        help='Only scan extensions with this minimum risk level or higher'
    )

    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f'%(prog)s {VERSION}'
    )

    # Parse command line arguments first
    args = parser.parse_args()

    # Load configuration file and merge with defaults (CLI args take precedence)
    config = load_config_file()

    if config:
        # Map config file keys to argument attributes
        # Only apply config values if CLI argument is at default value
        config_mappings = {
            'delay': ('delay', 1.5),
            'max_retries': ('max_retries', 3),
            'retry_delay': ('retry_delay', 2.0),
            'cache_max_age': ('cache_max_age', 7),
            'cache_dir': ('cache_dir', None),
            'output': ('output', None),
            'extensions_dir': ('extensions_dir', None),
            'exclude_ids': ('exclude_ids', None),
            'publisher': ('publisher', None),
            'detailed': ('detailed', False),
        }

        for config_key, (attr_name, default_value) in config_mappings.items():
            if config_key in config:
                current_value = getattr(args, attr_name)

                # Only use config value if CLI arg is still at default
                if current_value == default_value:
                    config_value = config[config_key]

                    # Validate config value types
                    if config_key in ['delay', 'retry_delay']:
                        try:
                            config_value = float(config_value)
                        except (ValueError, TypeError):
                            log(f"Warning: Invalid value for '{config_key}' in config.json, using default", "WARNING")
                            continue

                    if config_key in ['max_retries', 'cache_max_age']:
                        try:
                            config_value = int(config_value)
                        except (ValueError, TypeError):
                            log(f"Warning: Invalid value for '{config_key}' in config.json, using default", "WARNING")
                            continue

                    if config_key == 'detailed' and not isinstance(config_value, bool):
                        log(f"Warning: 'detailed' in config.json must be boolean, using default", "WARNING")
                        continue

                    setattr(args, attr_name, config_value)

    return args


def handle_cache_commands(args, cache_manager):
    """
    Handle cache-only commands (stats, clear).

    Args:
        args: Parsed command-line arguments
        cache_manager: CacheManager instance or None

    Returns:
        Exit code (0 for success, 2 for error) or None if no cache command
    """
    if args.cache_stats:
        if cache_manager is None:
            log("Error: Cannot show cache stats when --no-cache is specified", "ERROR")
            return 2

        stats = cache_manager.get_cache_stats(max_age_days=args.cache_max_age)
        log("Cache Statistics", "INFO", force=True)
        log("=" * 60, "INFO", force=True)
        log(f"Database path: {stats['database_path']}", "INFO", force=True)
        log(f"Total entries: {stats['total_entries']}", "INFO", force=True)
        log(f"Database size: {stats['database_size_kb']:.2f} KB", "INFO", force=True)
        log("", "INFO", force=True)

        if stats['total_entries'] > 0:
            # Cache age information
            if stats.get('average_age_days') is not None:
                log(f"Average cache age: {stats['average_age_days']} days", "INFO", force=True)

            stale_count = stats.get('stale_entries', 0)
            stale_threshold = stats.get('stale_threshold_days', args.cache_max_age)

            if stale_count > 0:
                stale_percent = round((stale_count / stats['total_entries']) * 100, 1)
                log(f"Stale entries (>{stale_threshold} days): {stale_count} ({stale_percent}%)", "INFO", force=True)

                # Suggest refresh if many entries are stale
                if stale_percent >= 50:
                    log("", "INFO", force=True)
                    log("⚠️  Recommendation: Consider running with --refresh-cache to update stale entries", "WARNING", force=True)

            log("", "INFO", force=True)
            log("Risk breakdown:", "INFO", force=True)
            for risk, count in stats['risk_breakdown'].items():
                log(f"  {risk}: {count}", "INFO", force=True)
            log("", "INFO", force=True)
            log(f"Extensions with vulnerabilities: {stats['extensions_with_vulnerabilities']}", "INFO", force=True)

        return 0

    if args.clear_cache:
        if cache_manager is None:
            log("Error: Cannot clear cache when --no-cache is specified", "ERROR")
            return 2

        count = cache_manager.clear_cache()
        log(f"Cleared {count} cache entries", "SUCCESS", force=True)
        return 0

    # No cache command specified
    return None


def apply_pre_scan_filters(extensions, args):
    """
    Apply filters that can be applied before scanning.
    Filters: --include-ids, --exclude-ids, --publisher

    Args:
        extensions: List of extension metadata dicts
        args: Parsed command-line arguments

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


def show_filter_help(args, original_count):
    """
    Show helpful information about active filters when no extensions match.

    Args:
        args: Parsed command-line arguments
        original_count: Number of extensions before filtering
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
        log("", "INFO")
        log("No extensions match the specified filters:", "WARNING")
        for filter_info in active_filters:
            log(filter_info, "INFO")
        log("", "INFO")

        # Provide helpful suggestions
        if original_count > 0:
            log(f"Tip: {original_count} extensions were found, but all were filtered out.", "INFO")

        if args.publisher:
            log("Tip: Publisher names are case-insensitive but must match exactly.", "INFO")
            log("     Run without filters to see available publishers.", "INFO")


def discover_extensions(args):
    """
    Discover installed VS Code extensions.

    Args:
        args: Parsed command-line arguments

    Returns:
        Tuple of (extensions_list, extensions_dir, original_count)

    Raises:
        FileNotFoundError: If extensions directory cannot be found
        Exception: If discovery fails
    """
    log("Step 1: Discovering VS Code extensions...", "INFO")
    discovery = ExtensionDiscovery(custom_dir=args.extensions_dir)

    extensions_dir = discovery.find_extensions_directory()
    log(f"Found VS Code extensions directory: {sanitize_string(str(extensions_dir), max_length=150)}", "SUCCESS")

    extensions = discovery.discover_extensions()
    log(f"Discovered {len(extensions)} extensions", "SUCCESS")

    # Apply pre-scan filters
    original_count = len(extensions)
    extensions = apply_pre_scan_filters(extensions, args)

    if len(extensions) < original_count:
        filtered_count = original_count - len(extensions)
        log(f"Filtered out {filtered_count} extensions based on criteria", "INFO")
        log(f"{len(extensions)} extensions selected for scanning", "SUCCESS")

    return extensions, extensions_dir, original_count


def scan_extensions(extensions, args, cache_manager, verbose, scan_timestamp):
    """
    Scan extensions for vulnerabilities.

    Args:
        extensions: List of extension metadata dicts
        args: Parsed command-line arguments
        cache_manager: CacheManager instance or None
        verbose: Verbose logging flag
        scan_timestamp: ISO timestamp of scan start

    Returns:
        Tuple of (scan_results, stats_dict)
    """
    log("", "INFO")
    log("Step 2: Scanning extensions for vulnerabilities...", "INFO")

    if cache_manager and not args.refresh_cache:
        log(f"Cache enabled (max age: {args.cache_max_age} days)", "INFO")
    elif args.no_cache:
        log("Cache disabled", "INFO")
    elif args.refresh_cache:
        log("Forcing cache refresh", "INFO")

    api_client = VscanAPIClient(
        delay=args.delay,
        verbose=verbose,
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

    for idx, ext in enumerate(extensions, 1):
        progress_prefix = f"[{idx}/{len(extensions)}]"
        extension_id = ext['id']
        version = ext['version']

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
                                   progress_prefix, verbose, stats, scan_results)
        else:
            # Scan fresh from API
            _scan_extension_fresh(ext, extension_id, version, progress_prefix,
                                 api_client, cache_manager, verbose, stats, scan_results)

    log("", "INFO")
    return scan_results, stats


def _get_status_symbol(status: str) -> str:
    """
    Get consistent status symbol for progress output.

    Args:
        status: Status type (cached, scanning, success, warning, error)

    Returns:
        Unicode symbol for the status
    """
    symbols = {
        'cached': '⚡',
        'scanning': '🔍',
        'success': '✓',
        'warning': '⚠',
        'error': '✗'
    }
    return symbols.get(status, '?')


def _print_scan_progress(extension_id: str, version: str, progress_prefix: str,
                         status: str, message: str = "", verbose: bool = False):
    """
    Print standardized scan progress with consistent formatting.

    Args:
        extension_id: Extension ID
        version: Extension version
        progress_prefix: Progress counter (e.g., "[1/42]")
        status: Status type (cached, scanning, success, warning, error)
        message: Additional message to display
        verbose: Whether in verbose mode
    """
    symbol = _get_status_symbol(status)

    if verbose:
        # Verbose mode: Append status on same line
        if message:
            log(f" {symbol} {message}", status.upper() if status in ['warning', 'error'] else "SUCCESS")
        else:
            log(f" {symbol}", "SUCCESS")
    else:
        # Non-verbose mode: Only show problems (warnings/errors)
        if status in ['warning', 'error']:
            log(f"{symbol} {extension_id}: {message}", status.upper())


def _process_cached_result(cached_result, ext, extension_id, version,
                           progress_prefix, verbose, stats, scan_results):
    """Process a cached scan result."""
    log(f"{progress_prefix} {extension_id} v{version}... {_get_status_symbol('cached')} Cached",
        "INFO", newline=False)

    # Merge extension metadata with cached result
    cached_result.update({
        'id': ext['id'],
        'version': ext['version'],
        'path': ext['path']
    })

    scan_results.append(cached_result)
    stats['cached_results'] += 1
    stats['successful_scans'] += 1

    vuln_count = cached_result.get('vulnerabilities', {}).get('count', 0)
    if vuln_count > 0:
        stats['vulnerabilities_found'] += vuln_count
        _print_scan_progress(extension_id, version, progress_prefix, 'warning',
                           f"{vuln_count} vulnerability(ies) found", verbose)
    else:
        _print_scan_progress(extension_id, version, progress_prefix, 'success', "", verbose)


def _scan_extension_fresh(ext, extension_id, version, progress_prefix,
                          api_client, cache_manager, verbose, stats, scan_results):
    """Scan an extension fresh from the API."""
    log(f"{progress_prefix} Scanning {extension_id} v{version}... {_get_status_symbol('scanning')}",
        "INFO", newline=False)

    # Define progress callback
    def progress_callback(progress_pct, message):
        """Show progress updates during analysis."""
        if progress_pct > 0 and progress_pct < 100:
            log(f" ({progress_pct}%: {message})", "INFO", newline=False)

    try:
        result = api_client.scan_extension(
            ext['publisher'],
            ext['name'],
            progress_callback=progress_callback if verbose else None
        )

        # Merge extension metadata with scan result
        result.update({
            'id': ext['id'],
            'version': ext['version'],
            'path': ext['path']
        })

        scan_results.append(result)

        # Save to cache if successful
        if result.get('scan_status') == 'success' and cache_manager:
            cache_manager.save_result(extension_id, version, result)

        # Check for vulnerabilities
        if result.get('scan_status') == 'success':
            stats['successful_scans'] += 1
            stats['fresh_scans'] += 1

            vuln_count = result.get('vulnerabilities', {}).get('count', 0)
            if vuln_count > 0:
                stats['vulnerabilities_found'] += vuln_count
                _print_scan_progress(extension_id, version, progress_prefix, 'warning',
                                   f"{vuln_count} vulnerability(ies) found", verbose)
            else:
                _print_scan_progress(extension_id, version, progress_prefix, 'success', "", verbose)
        else:
            stats['failed_scans'] += 1
            error_msg = result.get('error', 'Unknown error')
            _print_scan_progress(extension_id, version, progress_prefix, 'error', error_msg, verbose)

    except Exception as e:
        stats['failed_scans'] += 1
        error_msg = str(e)
        _print_scan_progress(extension_id, version, progress_prefix, 'error', error_msg, verbose)

        # Show error help for first few errors (avoid spam)
        if stats['failed_scans'] <= 3:
            error_type = get_error_type(error_msg)
            if error_type != "unknown":
                show_error_help(error_type, verbose)

        scan_results.append({
            'id': ext['id'],
            'name': ext['name'],
            'publisher': ext['publisher'],
            'version': ext['version'],
            'path': ext['path'],
            'scan_status': 'error',
            'error': error_msg
        })


def apply_post_scan_filters(scan_results, args):
    """
    Apply filters that require scan results.
    Filters: --min-risk-level

    Args:
        scan_results: List of scan result dicts
        args: Parsed command-line arguments

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
        log(f"Filtered out {filtered_count} extensions below '{args.min_risk_level}' risk level", "INFO")

    return filtered


def generate_output(scan_results, scan_duration, scan_timestamp, args, cache_stats_data):
    """
    Generate and write output (JSON or HTML).

    Args:
        scan_results: List of scan result dicts
        scan_duration: Total scan duration in seconds
        scan_timestamp: ISO timestamp of scan start
        args: Parsed command-line arguments
        cache_stats_data: Cache statistics dict

    Returns:
        Formatted results dict
    """
    log("Step 3: Generating results...", "INFO")

    # Detect output format
    is_html_output = args.output and args.output.endswith('.html')

    # For HTML output, always use detailed mode
    use_detailed = args.detailed or is_html_output

    formatter = OutputFormatter()
    results = formatter.format_output(
        scan_results,
        scan_timestamp,
        scan_duration,
        detailed=use_detailed,
        cache_stats=cache_stats_data if not args.no_cache else None
    )

    # Output results
    if args.output:
        _write_output_file(args.output, results, is_html_output)
    # Note: Human-readable summary is printed separately via print_summary()

    return results


def _write_output_file(output_path_str, results, is_html_output):
    """Write output to file (JSON or HTML)."""
    # Validate output path
    if not validate_path(output_path_str, allow_absolute=True, path_type="output"):
        log("Error: Invalid output path", "ERROR")
        log(sanitize_string(f"Path validation failed for: {output_path_str}", max_length=100), "ERROR")
        raise ValueError("Invalid output path")

    output_path = Path(output_path_str).resolve()

    # Create parent directories with restricted permissions (cross-platform)
    safe_mkdir(output_path.parent, mode=0o755)

    # Generate HTML or JSON based on file extension
    if is_html_output:
        from .html_report_generator import HTMLReportGenerator

        log("Generating HTML report...", "INFO")
        html_gen = HTMLReportGenerator()
        html_content = html_gen.generate_report(results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        log(f"HTML report written to {sanitize_string(output_path_str, max_length=100)}", "SUCCESS")
    else:
        # JSON output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        log(f"Results written to {sanitize_string(output_path_str, max_length=100)}", "SUCCESS")


def print_summary(extensions, stats, scan_duration):
    """
    Print scan summary statistics.

    Args:
        extensions: List of discovered extensions
        stats: Scan statistics dict
        scan_duration: Total scan duration in seconds
    """
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
        if retry_stats['total_retries'] > 0:
            log("", "INFO")
            log("Retry Statistics:", "INFO")
            log(f"  Total retry attempts: {retry_stats['total_retries']}", "INFO")
            log(f"  Successful retries: {retry_stats['successful_retries']}", "INFO")
            log(f"  Failed after retries: {retry_stats['failed_after_retries']}",
                "INFO" if retry_stats['failed_after_retries'] == 0 else "WARNING")

    log("", "INFO", force=True)
    log(f"Vulnerabilities found: {stats['vulnerabilities_found']}",
        "INFO" if stats['vulnerabilities_found'] == 0 else "WARNING", force=True)
    log(f"Scan duration: {scan_duration:.1f} seconds", "INFO", force=True)
    if len(extensions) > 0:
        avg_time = scan_duration / len(extensions)
        log(f"Average time per extension: {avg_time:.1f}s", "INFO", force=True)
    log("=" * 60, "INFO", force=True)


def calculate_exit_code(vulnerabilities_found):
    """
    Calculate exit code based on scan results.

    Args:
        vulnerabilities_found: Number of vulnerabilities found

    Returns:
        Exit code (0 = clean, 1 = vulnerabilities found)
    """
    # Exit codes:
    # 0 - Scan completed, no vulnerabilities
    # 1 - Scan completed, vulnerabilities found
    # 2 - Scan failed (handled elsewhere)
    return 1 if vulnerabilities_found > 0 else 0


def main():
    """Main entry point for the scanner - orchestration only."""
    args = parse_arguments()

    # Setup logging
    verbose = args.verbose
    setup_logging(verbose)

    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=args.cache_dir) if not args.no_cache else None

    # Handle cache-only commands
    cache_exit_code = handle_cache_commands(args, cache_manager)
    if cache_exit_code is not None:
        return cache_exit_code

    # Print banner
    log("VS Code Extension Scanner", "INFO")
    log(f"Version {VERSION}", "INFO")
    log("=" * 60, "INFO")
    log("", "INFO")

    start_time = time.time()
    scan_timestamp = datetime.utcnow().isoformat() + 'Z'

    # Step 1: Discover extensions
    try:
        extensions, extensions_dir, original_count = discover_extensions(args)
    except FileNotFoundError as e:
        error_msg = sanitize_string(str(e), max_length=200)
        log(error_msg, "ERROR")
        error_type = get_error_type(error_msg)
        show_error_help(error_type, verbose)
        return 2
    except Exception as e:
        error_msg = sanitize_string(str(e), max_length=200)
        log(f"Error discovering extensions: {error_msg}", "ERROR")
        error_type = get_error_type(error_msg)
        show_error_help(error_type, verbose)
        return 2

    # Handle empty extension list
    if len(extensions) == 0:
        log("No extensions found to scan", "WARNING")
        show_filter_help(args, original_count)

        # Still generate output for file if requested
        if args.output:
            formatter = OutputFormatter()
            results = formatter.format_output([], scan_timestamp, 0)
            try:
                _write_output_file(args.output, results, args.output.endswith('.html'))
            except Exception as e:
                log(f"Error writing output file: {type(e).__name__}", "ERROR")
                return 2
            log(f"Empty results saved to {sanitize_string(args.output, max_length=100)}", "INFO")

        return 0

    # Step 2: Scan extensions
    scan_results, stats = scan_extensions(extensions, args, cache_manager, verbose, scan_timestamp)

    # Apply post-scan filters (risk level)
    scan_results = apply_post_scan_filters(scan_results, args)

    # Step 3: Generate output
    scan_duration = time.time() - start_time

    cache_stats_data = {
        "from_cache": stats['cached_results'],
        "fresh_scans": stats['fresh_scans'],
        "cache_hit_rate": round((stats['cached_results'] / len(scan_results) * 100), 1) if len(scan_results) > 0 else 0.0
    }

    try:
        results = generate_output(scan_results, scan_duration, scan_timestamp, args, cache_stats_data)
    except Exception as e:
        error_msg = sanitize_string(str(e), max_length=200)
        log(f"Error generating output: {type(e).__name__}", "ERROR")
        if verbose:
            log(f"Details: {error_msg}", "ERROR")
        error_type = get_error_type(error_msg)
        show_error_help(error_type, verbose)
        return 2

    # Print summary
    print_summary(extensions, stats, scan_duration)

    # Calculate and return exit code
    return calculate_exit_code(stats['vulnerabilities_found'])


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log("\n\nScan interrupted by user", "WARNING")
        sys.exit(2)
    except Exception as e:
        log(f"\n\nUnexpected error: {e}", "ERROR")
        import traceback
        if '--verbose' in sys.argv or '-v' in sys.argv:
            traceback.print_exc()
        sys.exit(2)
