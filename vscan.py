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
from extension_discovery import ExtensionDiscovery
from vscan_api import VscanAPIClient
from output_formatter import OutputFormatter
from cache_manager import CacheManager
from utils import log, setup_logging, validate_path, sanitize_string


VERSION = "2.0.0"


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="VS Code Extension Security Scanner - Audit installed extensions using vscan.dev",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Scan all extensions (JSON to stdout)
  %(prog)s --output results.json       Save JSON results to file
  %(prog)s --output report.html        Generate interactive HTML report
  %(prog)s --verbose                   Show detailed progress
  %(prog)s --delay 2.0                 Use 2 second delay between requests
  %(prog)s --extensions-dir /path     Use custom extensions directory

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
        type=float,
        default=1.5,
        help='Delay between API requests in seconds (default: 1.5)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output to stderr'
    )

    # Retry-related arguments
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum retry attempts for failed API requests (default: 3)'
    )

    parser.add_argument(
        '--retry-delay',
        type=float,
        default=2.0,
        help='Base delay for exponential backoff in seconds (default: 2.0)'
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
        type=int,
        default=7,
        help='Maximum age of cached results in days (default: 7)'
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

    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f'%(prog)s {VERSION}'
    )

    return parser.parse_args()


def main():
    """Main entry point for the scanner."""
    args = parse_arguments()

    # Setup logging based on verbose flag
    verbose = args.verbose
    setup_logging(verbose)

    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=args.cache_dir) if not args.no_cache else None

    # Handle cache-only commands
    if args.cache_stats:
        if cache_manager is None:
            log("Error: Cannot show cache stats when --no-cache is specified", "ERROR")
            return 2

        stats = cache_manager.get_cache_stats()
        log("Cache Statistics", "INFO", force=True)
        log("=" * 60, "INFO", force=True)
        log(f"Database path: {stats['database_path']}", "INFO", force=True)
        log(f"Total entries: {stats['total_entries']}", "INFO", force=True)
        log(f"Database size: {stats['database_size_kb']:.2f} KB", "INFO", force=True)
        log("", "INFO", force=True)

        if stats['total_entries'] > 0:
            log("Risk breakdown:", "INFO", force=True)
            for risk, count in stats['risk_breakdown'].items():
                log(f"  {risk}: {count}", "INFO", force=True)
            log("", "INFO", force=True)
            log(f"Extensions with vulnerabilities: {stats['extensions_with_vulnerabilities']}", "INFO", force=True)
            log(f"Oldest entry: {stats['oldest_entry']}", "INFO", force=True)
            log(f"Newest entry: {stats['newest_entry']}", "INFO", force=True)

        return 0

    if args.clear_cache:
        if cache_manager is None:
            log("Error: Cannot clear cache when --no-cache is specified", "ERROR")
            return 2

        count = cache_manager.clear_cache()
        log(f"Cleared {count} cache entries", "SUCCESS", force=True)
        return 0

    log("VS Code Extension Security Scanner", "INFO")
    log(f"Version {VERSION}", "INFO")
    log("=" * 60, "INFO")
    log("", "INFO")

    start_time = time.time()
    scan_timestamp = datetime.utcnow().isoformat() + 'Z'

    # Step 1: Discover extensions
    log("Step 1: Discovering VS Code extensions...", "INFO")
    discovery = ExtensionDiscovery(custom_dir=args.extensions_dir)

    try:
        extensions_dir = discovery.find_extensions_directory()
        log(f"Found VS Code extensions directory: {sanitize_string(str(extensions_dir), max_length=150)}", "SUCCESS")
    except FileNotFoundError as e:
        log(sanitize_string(str(e), max_length=200), "ERROR")
        log("", "ERROR")
        log("Please ensure VS Code is installed or specify a custom directory with --extensions-dir", "ERROR")
        return 2  # Exit code 2: Scan failed

    try:
        extensions = discovery.discover_extensions()
        log(f"Discovered {len(extensions)} extensions", "SUCCESS")
    except Exception as e:
        log(f"Error discovering extensions: {sanitize_string(str(e), max_length=200)}", "ERROR")
        return 2

    if len(extensions) == 0:
        log("No extensions found to scan", "WARNING")
        # Output empty results
        formatter = OutputFormatter()
        results = formatter.format_output([], scan_timestamp, 0)

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            log(f"Results written to {args.output}", "INFO")
        else:
            print(json.dumps(results, indent=2))

        return 0

    log("", "INFO")

    # Step 2: Scan extensions using vscan.dev API
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
    vulnerabilities_found = 0
    successful_scans = 0
    failed_scans = 0
    cached_results = 0  # Extensions loaded from cache
    fresh_scans = 0  # Extensions scanned fresh from API

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
            log(f"{progress_prefix} {extension_id} v{version}... ⚡ Cached", "INFO", newline=False)

            # Merge extension metadata with cached result
            cached_result.update({
                'id': ext['id'],
                'version': ext['version'],
                'path': ext['path']
            })

            scan_results.append(cached_result)
            cached_results += 1
            successful_scans += 1

            vuln_count = cached_result.get('vulnerabilities', {}).get('count', 0)
            if vuln_count > 0:
                vulnerabilities_found += vuln_count
                # In verbose mode, print on same line; in non-verbose, print full info
                if verbose:
                    log(" ⚠", "WARNING")
                else:
                    log(f"⚠ {extension_id}: {vuln_count} vulnerability(ies) found", "WARNING")
            else:
                log(" ✓", "SUCCESS")

        else:
            # Scan fresh from API
            log(f"{progress_prefix} Scanning {extension_id} v{version}... 🔍", "INFO", newline=False)

            # Define progress callback for this extension
            scan_start_time = time.time()
            did_show_progress = [False]  # Use list to allow modification in nested function

            def progress_callback(progress_pct, message):
                """Show progress updates during analysis."""
                if progress_pct > 0 and progress_pct < 100:
                    did_show_progress[0] = True
                    log(f" ({progress_pct}%: {message})", "INFO", newline=False)

            try:
                result = api_client.scan_extension(
                    ext['publisher'],
                    ext['name'],
                    progress_callback=progress_callback if verbose else None
                )

                scan_duration = time.time() - scan_start_time

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
                    successful_scans += 1
                    fresh_scans += 1

                    vuln_count = result.get('vulnerabilities', {}).get('count', 0)
                    if vuln_count > 0:
                        vulnerabilities_found += vuln_count
                        # In verbose mode, print on same line; in non-verbose, print full info
                        if verbose:
                            log(" ⚠ Vulnerabilities found", "WARNING")
                        else:
                            log(f"⚠ {extension_id}: {vuln_count} vulnerability(ies) found", "WARNING")
                    else:
                        log(" ✓", "SUCCESS")
                else:
                    failed_scans += 1
                    error_msg = result.get('error', 'Unknown error')
                    # In verbose mode, print on same line; in non-verbose, print full info
                    if verbose:
                        log(f" ✗ {error_msg}", "ERROR")
                    else:
                        log(f"✗ {extension_id}: {error_msg}", "ERROR")

            except Exception as e:
                failed_scans += 1
                # In verbose mode, print on same line; in non-verbose, print full info
                if verbose:
                    log(f" ✗ Error: {e}", "ERROR")
                else:
                    log(f"✗ {extension_id}: Error - {e}", "ERROR")
                scan_results.append({
                    'id': ext['id'],
                    'name': ext['name'],
                    'publisher': ext['publisher'],
                    'version': ext['version'],
                    'path': ext['path'],
                    'scan_status': 'error',
                    'error': str(e)
                })

    log("", "INFO")

    # Step 3: Generate output
    scan_duration = time.time() - start_time
    log("Step 3: Generating results...", "INFO")

    # Prepare cache statistics
    cache_stats_data = {
        "from_cache": cached_results,
        "fresh_scans": fresh_scans,
        "cache_hit_rate": round((cached_results / len(scan_results) * 100), 1) if len(scan_results) > 0 else 0.0
    }

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
        try:
            # Validate output path using centralized validation
            if not validate_path(args.output):
                log("Error: Invalid output path", "ERROR")
                log(sanitize_string(f"Path validation failed for: {args.output}", max_length=100), "ERROR")
                return 2

            output_path = Path(args.output).resolve()
            cwd = Path.cwd().resolve()

            # Double-check path is within current directory (validate_path already checks this)
            try:
                output_path.relative_to(cwd)
            except ValueError:
                log("Error: Output path must be within current directory", "ERROR")
                return 2

            # Create parent directories with restricted permissions
            output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)

            # Generate HTML or JSON based on file extension
            if is_html_output:
                from html_report_generator import HTMLReportGenerator

                log("Generating HTML report...", "INFO")
                html_gen = HTMLReportGenerator()
                html_content = html_gen.generate_report(results)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                log(f"HTML report written to {sanitize_string(args.output, max_length=100)}", "SUCCESS")
            else:
                # JSON output
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)

                log(f"Results written to {sanitize_string(args.output, max_length=100)}", "SUCCESS")

        except Exception as e:
            log(f"Error writing output file: {type(e).__name__}", "ERROR")
            if verbose:
                log(sanitize_string(f"Details: {str(e)}", max_length=200), "ERROR")
            return 2
    else:
        # Output to stdout
        print(json.dumps(results, indent=2))

    # Summary (always show, not just in verbose mode)
    log("", "INFO", force=True)
    log("=" * 60, "INFO", force=True)
    log("Scan Complete!", "SUCCESS", force=True)
    log(f"Total extensions scanned: {len(extensions)}", "INFO", force=True)
    log(f"Successful scans: {successful_scans}", "INFO", force=True)
    log(f"Failed scans: {failed_scans}", "INFO" if failed_scans == 0 else "WARNING", force=True)

    # Cache statistics (always show, not just in verbose mode)
    if cache_manager and (cached_results > 0 or fresh_scans > 0):
        log("", "INFO", force=True)
        log("Cache Statistics:", "INFO", force=True)
        log(f"  From cache: {cached_results} (⚡ instant)", "INFO", force=True)
        log(f"  Fresh scans: {fresh_scans} (🔍 API calls)", "INFO", force=True)
        if len(extensions) > 0:
            cache_hit_rate = (cached_results / len(extensions)) * 100
            log(f"  Cache hit rate: {cache_hit_rate:.1f}%", "INFO", force=True)

    # Retry statistics
    retry_stats = api_client.get_retry_stats()
    if retry_stats['total_retries'] > 0:
        log("", "INFO")
        log("Retry Statistics:", "INFO")
        log(f"  Total retry attempts: {retry_stats['total_retries']}", "INFO")
        log(f"  Successful retries: {retry_stats['successful_retries']}", "INFO")
        log(f"  Failed after retries: {retry_stats['failed_after_retries']}", "INFO" if retry_stats['failed_after_retries'] == 0 else "WARNING")

    log("", "INFO", force=True)
    log(f"Vulnerabilities found: {vulnerabilities_found}", "INFO" if vulnerabilities_found == 0 else "WARNING", force=True)
    log(f"Scan duration: {scan_duration:.1f} seconds", "INFO", force=True)
    if len(extensions) > 0:
        avg_time = scan_duration / len(extensions)
        log(f"Average time per extension: {avg_time:.1f}s", "INFO", force=True)
    log("=" * 60, "INFO", force=True)

    # Exit codes:
    # 0 - Scan completed, no vulnerabilities
    # 1 - Scan completed, vulnerabilities found
    # 2 - Scan failed
    if vulnerabilities_found > 0:
        return 1
    else:
        return 0


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
