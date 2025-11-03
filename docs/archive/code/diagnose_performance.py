#!/usr/bin/env python3
"""
Performance Diagnostic Script for VSCode Extension Scanner

This script helps diagnose performance issues by:
1. Measuring API response times
2. Testing different worker configurations
3. Comparing sequential vs parallel performance
4. Detecting rate limiting and timeouts
5. Analyzing cache effectiveness

Usage:
    python3 scripts/diagnose_performance.py [--extensions-count N] [--output report.txt]
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.extension_discovery import ExtensionDiscovery
from vscode_scanner.vscan_api import VscanAPIClient
from vscode_scanner.cache_manager import CacheManager
from vscode_scanner.scanner import _scan_single_extension_worker


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def print_section(title: str, width: int = 80):
    """Print a section header."""
    print()
    print("=" * width)
    print(f" {title}")
    print("=" * width)


def discover_sample_extensions(max_count: int = 5) -> List[Dict]:
    """Discover a sample of installed extensions."""
    print_section("Step 1: Discovering Extensions")

    discovery = ExtensionDiscovery()
    extensions_dir = discovery.find_extensions_directory()
    print(f"Extensions directory: {extensions_dir}")

    all_extensions = discovery.discover_extensions()
    print(f"Total extensions found: {len(all_extensions)}")

    # Take first N extensions as sample
    sample = all_extensions[:max_count]
    print(f"Sample size: {len(sample)}")
    print()

    for i, ext in enumerate(sample, 1):
        print(f"  {i}. {ext['id']} v{ext['version']}")

    return sample


def test_sequential_scan(
    extensions: List[Dict], cache_manager: CacheManager, delay: float = 1.5
) -> Tuple[float, Dict]:
    """Test sequential scanning with timing."""
    print_section("Step 2: Sequential Scan Test (--workers 1)")

    from types import SimpleNamespace

    args = SimpleNamespace(
        delay=delay,
        max_retries=3,
        retry_delay=2.0,
        refresh_cache=False,
        no_cache=False,
        cache_max_age=7,
    )

    # Create API client
    api_client = VscanAPIClient(delay=delay, verbose=False)

    start_time = time.time()
    results = []

    print(f"Scanning {len(extensions)} extensions sequentially...")
    print(f"Request delay: {delay}s")
    print()

    for i, ext in enumerate(extensions, 1):
        ext_start = time.time()
        print(f"  [{i}/{len(extensions)}] Scanning {ext['id']}...", end=" ", flush=True)

        result, from_cache, _ = _scan_single_extension_worker(ext, cache_manager, args)
        results.append(result)

        ext_elapsed = time.time() - ext_start
        cache_indicator = "⚡ (cached)" if from_cache else "🔍 (fresh)"
        print(f"{cache_indicator} - {format_duration(ext_elapsed)}")

    total_elapsed = time.time() - start_time

    # Get timing stats from API client
    timing_stats = api_client.get_timing_stats()
    retry_stats = api_client.get_retry_stats()

    print()
    print(f"✓ Sequential scan completed in {format_duration(total_elapsed)}")
    print(
        f"  Average per extension: {format_duration(total_elapsed / len(extensions))}"
    )

    return total_elapsed, {
        "results": results,
        "timing": timing_stats,
        "retries": retry_stats,
    }


def test_parallel_scan(
    extensions: List[Dict],
    cache_manager: CacheManager,
    workers: int = 3,
    delay: float = 1.5,
) -> Tuple[float, Dict]:
    """Test parallel scanning with timing."""
    print_section(f"Step 3: Parallel Scan Test (--workers {workers})")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from types import SimpleNamespace

    args = SimpleNamespace(
        delay=delay,
        max_retries=3,
        retry_delay=2.0,
        refresh_cache=False,
        no_cache=False,
        cache_max_age=7,
    )

    start_time = time.time()
    results = []

    print(f"Scanning {len(extensions)} extensions with {workers} workers...")
    print(f"Request delay: {delay}s per worker")
    print()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        futures = {}
        for ext in extensions:
            future = executor.submit(
                _scan_single_extension_worker, ext, cache_manager, args
            )
            futures[future] = ext

        # Collect results
        completed = 0
        for future in as_completed(futures):
            ext = futures[future]
            completed += 1

            try:
                result, from_cache, _ = future.result()
                results.append(result)

                cache_indicator = "⚡" if from_cache else "🔍"
                print(
                    f"  [{completed}/{len(extensions)}] {ext['id']} {cache_indicator}"
                )
            except Exception as e:
                print(f"  [{completed}/{len(extensions)}] {ext['id']} ❌ Error: {e}")

    total_elapsed = time.time() - start_time

    # Note: In parallel mode, we can't easily get timing stats from individual workers
    # since each creates its own API client instance

    print()
    print(f"✓ Parallel scan completed in {format_duration(total_elapsed)}")
    print(
        f"  Average per extension: {format_duration(total_elapsed / len(extensions))}"
    )

    speedup = 0.0  # Will be calculated by caller

    return total_elapsed, {
        "results": results,
        "speedup": speedup,
    }


def analyze_api_performance(timing_stats: Dict, retry_stats: Dict):
    """Analyze API performance metrics."""
    print_section("Step 4: API Performance Analysis")

    print("📊 Timing Breakdown:")
    print(
        f"  Average submit time:  {format_duration(timing_stats.get('avg_submit_time', 0))}"
    )
    print(
        f"  Average poll time:    {format_duration(timing_stats.get('avg_poll_time', 0))}"
    )
    print(
        f"  Average results time: {format_duration(timing_stats.get('avg_results_time', 0))}"
    )
    print(
        f"  Average total time:   {format_duration(timing_stats.get('avg_total_time', 0))}"
    )

    print()
    print("⚠️  Issues Detected:")

    rate_limit_count = timing_stats.get("rate_limit_count", 0)
    timeout_count = timing_stats.get("timeout_count", 0)
    http_retries = retry_stats.get("total_retries", 0)
    workflow_retries = retry_stats.get("total_workflow_retries", 0)

    issues_found = False

    if rate_limit_count > 0:
        print(f"  🚨 Rate limiting: {rate_limit_count} occurrences")
        print(f"     → Recommendation: Increase --delay from 1.5s to 3.0s")
        print(f"     → Recommendation: Reduce --workers from 3 to 2")
        issues_found = True

    if timeout_count > 0:
        print(f"  ⏱️  Timeouts: {timeout_count} occurrences")
        print(f"     → Recommendation: API may be slow, consider sequential mode")
        issues_found = True

    if http_retries > len(timing_stats.get("total_scan_times", [])) * 0.3:
        print(
            f"  🔄 High retry rate: {http_retries} retries for {len(timing_stats.get('total_scan_times', []))} scans"
        )
        print(
            f"     → Recommendation: API instability, reduce workers or increase delay"
        )
        issues_found = True

    if workflow_retries > 0:
        print(f"  ⚠️  Workflow retries: {workflow_retries} occurrences")
        print(f"     → Recommendation: Transient API issues detected")
        issues_found = True

    # Check if polling is taking too long
    avg_poll = timing_stats.get("avg_poll_time", 0)
    if avg_poll > 30:
        print(f"  🐢 Slow analysis: Average {format_duration(avg_poll)} per extension")
        print(f"     → Issue: vscan.dev API analysis is slow")
        print(f"     → Not a configuration issue - API performance degraded")
        issues_found = True

    if not issues_found:
        print("  ✓ No rate limiting detected")
        print("  ✓ No timeout issues detected")
        print("  ✓ Retry rate is normal")
        print("  ✓ API performance is healthy")


def print_recommendations(
    sequential_time: float,
    parallel_time: float,
    workers: int,
    timing_stats: Dict,
    retry_stats: Dict,
):
    """Print performance recommendations."""
    print_section("Step 5: Recommendations")

    speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0

    print(f"⚡ Performance Comparison:")
    print(f"  Sequential (--workers 1): {format_duration(sequential_time)}")
    print(f"  Parallel (--workers {workers}):   {format_duration(parallel_time)}")
    print(f"  Speedup: {speedup:.2f}x")
    print()

    rate_limit_count = timing_stats.get("rate_limit_count", 0)
    avg_poll = timing_stats.get("avg_poll_time", 0)

    if rate_limit_count > 0:
        print("🎯 Recommended Configuration (Rate Limiting Detected):")
        print("   ~/.vscanrc:")
        print("   [scan]")
        print("   workers = 2")
        print("   delay = 3.0")
        print()
        print("   Command line:")
        print("   vscan scan --workers 2 --delay 3.0")
    elif avg_poll > 30:
        print("🎯 Root Cause: vscan.dev API Performance Degradation")
        print("   The vscan.dev API analysis is taking significantly longer.")
        print("   This is not a configuration issue with your scanner.")
        print()
        print("   Options:")
        print("   1. Use cache aggressively: Scan less frequently")
        print("   2. Use sequential mode: More reliable but slower")
        print("   3. Wait for API performance to improve")
        print()
        print("   Conservative configuration:")
        print("   ~/.vscanrc:")
        print("   [scan]")
        print("   workers = 1")
        print("   delay = 2.0")
    elif speedup < 2.0:
        print("🎯 Recommended Configuration (Limited Speedup):")
        print("   Performance improvement is limited.")
        print()
        print("   Try reducing workers:")
        print("   ~/.vscanrc:")
        print("   [scan]")
        print("   workers = 2")
        print("   delay = 2.0")
    else:
        print("🎯 Current Configuration is Optimal:")
        print("   Your parallel scanning is working well.")
        print()
        print("   Keep current settings:")
        print("   ~/.vscanrc:")
        print("   [scan]")
        print("   workers = 3")
        print("   delay = 1.5")


def main():
    """Main diagnostic function."""
    parser = argparse.ArgumentParser(
        description="Diagnose VSCode Extension Scanner performance"
    )
    parser.add_argument(
        "--extensions-count",
        type=int,
        default=5,
        help="Number of extensions to test (default: 5)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=3,
        help="Number of parallel workers to test (default: 3)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between API requests (default: 1.5s)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for diagnostic report",
    )

    args = parser.parse_args()

    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║  VSCode Extension Scanner - Performance Diagnostic Tool                ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")

    # Initialize cache manager
    cache_manager = CacheManager()

    # Step 1: Discover extensions
    try:
        extensions = discover_sample_extensions(args.extensions_count)
    except Exception as e:
        print(f"\n❌ Error discovering extensions: {e}")
        return 1

    if not extensions:
        print("\n❌ No extensions found to test")
        return 1

    # Step 2: Sequential test
    try:
        seq_time, seq_stats = test_sequential_scan(
            extensions, cache_manager, args.delay
        )
    except Exception as e:
        print(f"\n❌ Error in sequential scan: {e}")
        return 1

    # Step 3: Parallel test
    try:
        par_time, par_stats = test_parallel_scan(
            extensions, cache_manager, args.workers, args.delay
        )
    except Exception as e:
        print(f"\n❌ Error in parallel scan: {e}")
        return 1

    # Step 4: Analyze API performance
    analyze_api_performance(seq_stats["timing"], seq_stats["retries"])

    # Step 5: Print recommendations
    print_recommendations(
        seq_time, par_time, args.workers, seq_stats["timing"], seq_stats["retries"]
    )

    print()
    print("✓ Diagnostic complete!")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
