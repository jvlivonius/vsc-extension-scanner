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
from utils import log, setup_logging


VERSION = "1.0.0"


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="VS Code Extension Security Scanner - Audit installed extensions using vscan.dev",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Scan all extensions
  %(prog)s --output results.json       Save results to file
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
        help='Output file path for JSON results (default: stdout)'
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
        log("Cache Statistics", "INFO")
        log("=" * 60, "INFO")
        log(f"Database path: {stats['database_path']}", "INFO")
        log(f"Total entries: {stats['total_entries']}", "INFO")
        log(f"Database size: {stats['database_size_kb']:.2f} KB", "INFO")
        log("", "INFO")

        if stats['total_entries'] > 0:
            log("Risk breakdown:", "INFO")
            for risk, count in stats['risk_breakdown'].items():
                log(f"  {risk}: {count}", "INFO")
            log("", "INFO")
            log(f"Extensions with vulnerabilities: {stats['extensions_with_vulnerabilities']}", "INFO")
            log(f"Oldest entry: {stats['oldest_entry']}", "INFO")
            log(f"Newest entry: {stats['newest_entry']}", "INFO")

        return 0

    if args.clear_cache:
        if cache_manager is None:
            log("Error: Cannot clear cache when --no-cache is specified", "ERROR")
            return 2

        count = cache_manager.clear_cache()
        log(f"Cleared {count} cache entries", "SUCCESS")
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
        log(f"Found VS Code extensions directory: {extensions_dir}", "SUCCESS")
    except FileNotFoundError as e:
        log(str(e), "ERROR")
        log("", "ERROR")
        log("Please ensure VS Code is installed or specify a custom directory with --extensions-dir", "ERROR")
        return 2  # Exit code 2: Scan failed

    try:
        extensions = discovery.discover_extensions()
        log(f"Discovered {len(extensions)} extensions", "SUCCESS")
    except Exception as e:
        log(f"Error discovering extensions: {e}", "ERROR")
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

    api_client = VscanAPIClient(delay=args.delay, verbose=verbose)

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
                log(" ⚠", "WARNING")
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
                        log(" ⚠ Vulnerabilities found", "WARNING")
                    else:
                        log(" ✓", "SUCCESS")
                else:
                    failed_scans += 1
                    log(f" ✗ {result.get('error', 'Unknown error')}", "ERROR")

            except Exception as e:
                failed_scans += 1
                log(f" ✗ Error: {e}", "ERROR")
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

    formatter = OutputFormatter()
    results = formatter.format_output(scan_results, scan_timestamp, scan_duration)

    # Output results
    if args.output:
        try:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)

            log(f"Results written to {args.output}", "SUCCESS")
        except Exception as e:
            log(f"Error writing output file: {e}", "ERROR")
            return 2
    else:
        # Output to stdout
        print(json.dumps(results, indent=2))

    # Summary
    log("", "INFO")
    log("=" * 60, "INFO")
    log("Scan Complete!", "SUCCESS")
    log(f"Total extensions scanned: {len(extensions)}", "INFO")
    log(f"Successful scans: {successful_scans}", "INFO")
    log(f"Failed scans: {failed_scans}", "INFO" if failed_scans == 0 else "WARNING")

    # Cache statistics
    if cache_manager and (cached_results > 0 or fresh_scans > 0):
        log("", "INFO")
        log("Cache Statistics:", "INFO")
        log(f"  From cache: {cached_results} (⚡ instant)", "INFO")
        log(f"  Fresh scans: {fresh_scans} (🔍 API calls)", "INFO")
        if len(extensions) > 0:
            cache_hit_rate = (cached_results / len(extensions)) * 100
            log(f"  Cache hit rate: {cache_hit_rate:.1f}%", "INFO")

    log("", "INFO")
    log(f"Vulnerabilities found: {vulnerabilities_found}", "INFO" if vulnerabilities_found == 0 else "WARNING")
    log(f"Scan duration: {scan_duration:.1f} seconds", "INFO")
    if len(extensions) > 0:
        avg_time = scan_duration / len(extensions)
        log(f"Average time per extension: {avg_time:.1f}s", "INFO")
    log("=" * 60, "INFO")

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
