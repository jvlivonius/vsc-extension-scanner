#!/usr/bin/env python3
"""
Summary Formatter Module

Responsibilities:
- Quiet summary text generation (pure function)
- Retry stats extraction (pure function)
- Conditional display logic (pure functions)
- Summary orchestration

Layer: Application
Dependencies: None (pure functions)
"""

from typing import Dict, List, Optional


class SummaryFormatter:
    """
    Handles scan summary formatting logic.

    Separates pure logic (text generation, conditional checks) from
    side effects (display, logging).
    """

    @staticmethod
    def format_quiet_summary(total_extensions: int, vulnerabilities_found: int) -> str:
        """
        Generate quiet mode summary text (pure function).

        Args:
            total_extensions: Total number of extensions scanned
            vulnerabilities_found: Number of vulnerabilities found

        Returns:
            Single-line summary string

        Examples:
            >>> SummaryFormatter.format_quiet_summary(10, 0)
            'Scanned 10 extensions - No vulnerabilities found ✓'
            >>> SummaryFormatter.format_quiet_summary(5, 3)
            'Scanned 5 extensions - Found 3 vulnerabilities'
        """
        if vulnerabilities_found > 0:
            return f"Scanned {total_extensions} extensions - Found {vulnerabilities_found} vulnerabilities"
        else:
            return f"Scanned {total_extensions} extensions - No vulnerabilities found ✓"

    @staticmethod
    def extract_retry_stats(stats: Dict) -> Optional[Dict]:
        """
        Extract retry statistics from stats dict (pure function).

        Args:
            stats: Statistics dictionary containing api_client

        Returns:
            Retry stats dict or None if unavailable

        Examples:
            >>> stats = {"api_client": MockClient()}
            >>> SummaryFormatter.extract_retry_stats(stats)
            {'total_retries': 5, 'successful_retries': 4}
        """
        if "api_client" in stats and stats["api_client"] is not None:
            try:
                return stats["api_client"].get_retry_stats()
            except Exception:
                # Catch all exceptions from api_client.get_retry_stats()
                return None
        return None

    @staticmethod
    def should_show_cache_stats(results: Dict, verbose: bool) -> bool:
        """
        Determine if cache statistics should be displayed (pure function).

        Args:
            results: Results dictionary
            verbose: Whether verbose mode is enabled

        Returns:
            True if cache stats should be displayed

        Examples:
            >>> results = {"summary": {"cache_statistics": {...}}}
            >>> SummaryFormatter.should_show_cache_stats(results, True)
            True
            >>> SummaryFormatter.should_show_cache_stats(results, False)
            False
        """
        if not verbose:
            return False

        cache_stats = results.get("summary", {}).get("cache_statistics")
        return cache_stats is not None and bool(cache_stats)

    @staticmethod
    def should_show_retry_stats(retry_stats: Optional[Dict], verbose: bool) -> bool:
        """
        Determine if retry statistics should be displayed (pure function).

        Args:
            retry_stats: Retry statistics dict or None
            verbose: Whether verbose mode is enabled

        Returns:
            True if retry stats should be displayed

        Examples:
            >>> SummaryFormatter.should_show_retry_stats({"total": 5}, True)
            True
            >>> SummaryFormatter.should_show_retry_stats(None, True)
            False
            >>> SummaryFormatter.should_show_retry_stats({"total": 5}, False)
            False
        """
        return verbose and retry_stats is not None

    @staticmethod
    def has_scan_results(results: Dict) -> bool:
        """
        Check if scan results exist (pure function).

        Args:
            results: Results dictionary

        Returns:
            True if there are scan results to display

        Examples:
            >>> SummaryFormatter.has_scan_results({"extensions": [{"id": "test"}]})
            True
            >>> SummaryFormatter.has_scan_results({"extensions": []})
            False
            >>> SummaryFormatter.has_scan_results({})
            False
        """
        scan_results = results.get("extensions", [])
        return bool(scan_results)

    @staticmethod
    def get_cache_stats(results: Dict) -> Optional[Dict]:
        """
        Extract cache statistics from results (pure function).

        Args:
            results: Results dictionary

        Returns:
            Cache stats dict or None if unavailable

        Examples:
            >>> results = {"summary": {"cache_statistics": {...}}}
            >>> SummaryFormatter.get_cache_stats(results) is not None
            True
        """
        return results.get("summary", {}).get("cache_statistics")

    @staticmethod
    def get_scan_results(results: Dict) -> List[Dict]:
        """
        Extract scan results from results dict (pure function).

        Args:
            results: Results dictionary

        Returns:
            List of extension scan results

        Examples:
            >>> results = {"extensions": [{"id": "ext1"}]}
            >>> SummaryFormatter.get_scan_results(results)
            [{'id': 'ext1'}]
        """
        return results.get("extensions", [])
