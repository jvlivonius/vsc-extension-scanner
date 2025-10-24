#!/usr/bin/env python3
"""
Output Formatter Module

Formats scan results into comprehensive JSON output.
Schema version 2.0 with reorganized structure.
"""

from typing import List, Dict, Any
from ._version import SCHEMA_VERSION


class OutputFormatter:
    """Formats scan results into standardized JSON output with comprehensive data."""

    SCHEMA_VERSION = SCHEMA_VERSION

    def format_output(
        self,
        scan_results: List[Dict[str, Any]],
        scan_timestamp: str,
        scan_duration: float,
        cache_stats: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format scan results into comprehensive JSON output.

        Args:
            scan_results: List of extension scan results
            scan_timestamp: ISO 8601 timestamp of scan start
            scan_duration: Scan duration in seconds
            cache_stats: Optional cache statistics

        Returns:
            Formatted output dictionary with all available data
        """
        # Build summary
        summary = self._format_summary(scan_results, scan_timestamp, scan_duration, cache_stats)

        # Format extensions with all available data
        extensions = [self._format_extension(result) for result in scan_results]

        # Build output
        output = {
            "schema_version": self.SCHEMA_VERSION,
            "output_mode": "detailed",
            "summary": summary,
            "extensions": extensions
        }

        return output

    def _format_summary(
        self,
        scan_results: List[Dict[str, Any]],
        scan_timestamp: str,
        scan_duration: float,
        cache_stats: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format summary section with enhanced statistics.

        Args:
            scan_results: List of scan results
            scan_timestamp: Scan timestamp
            scan_duration: Duration in seconds
            cache_stats: Optional cache statistics

        Returns:
            Summary dictionary
        """
        total = len(scan_results)
        successful = sum(1 for r in scan_results if r.get('scan_status') == 'success')
        failed = total - successful

        # Count vulnerabilities
        total_vulnerabilities = 0
        for result in scan_results:
            if result.get('scan_status') == 'success':
                vuln_count = result.get('vulnerabilities', {}).get('count', 0)
                total_vulnerabilities += vuln_count

        # Count by risk level
        risk_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
        for result in scan_results:
            if result.get('scan_status') == 'success':
                risk_level = result.get('risk_level', 'unknown')
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1

        summary = {
            "total_extensions_scanned": total,
            "successful_scans": successful,
            "failed_scans": failed,
            "vulnerabilities_found": total_vulnerabilities,
            "critical_risk_extensions": risk_counts.get("critical", 0),
            "high_risk_extensions": risk_counts.get("high", 0),
            "medium_risk_extensions": risk_counts.get("medium", 0),
            "low_risk_extensions": risk_counts.get("low", 0),
            "scan_timestamp": scan_timestamp,
            "scan_duration_seconds": round(scan_duration, 2)
        }

        # Add cache statistics if provided
        if cache_stats:
            summary["cache_statistics"] = {
                "from_cache": cache_stats.get("from_cache", 0),
                "fresh_scans": cache_stats.get("fresh_scans", 0),
                "cache_hit_rate": cache_stats.get("cache_hit_rate", 0.0)
            }

        return summary

    def _format_extension(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format extension with comprehensive data.

        Args:
            result: Extension scan result

        Returns:
            Formatted extension dict with all available data
        """
        # Extract metadata
        metadata = result.get('metadata', {})
        display_name = metadata.get('display_name') or result.get('name', 'Unknown')
        publisher_info = metadata.get('publisher', {})
        statistics = metadata.get('statistics', {})

        # Build base extension structure
        extension = {
            "id": result.get('id') or f"{result.get('publisher')}.{result.get('name')}",
            "name": result.get('name', 'Unknown'),
            "display_name": display_name,
            "version": metadata.get('version') or result.get('version', 'unknown'),
            "publisher": {
                "id": publisher_info.get('id') or result.get('publisher'),
                "name": publisher_info.get('name'),
                "verified": publisher_info.get('verified', False),
                "domain": publisher_info.get('domain')
            },
            "description": metadata.get('description'),
            "repository_url": metadata.get('repository_url'),
            "license": metadata.get('license'),
            "last_updated": metadata.get('last_updated'),
            "statistics": {
                "installs": statistics.get('installs'),
                "rating": statistics.get('rating'),
                "rating_count": statistics.get('rating_count'),
                "updates": statistics.get('updates')
            },
            "scan_status": result.get('scan_status', 'error'),
            "scan_timestamp": result.get('analysis_timestamp')
        }

        # Add success-specific fields
        if result.get('scan_status') == 'success':
            security = result.get('security', {})
            dependencies = result.get('dependencies', {})
            risk_factors = result.get('risk_factors', [])

            # Add extended metadata
            extension["homepage_url"] = metadata.get('homepage_url')
            extension["support_url"] = metadata.get('support_url')
            extension["privacy_policy_url"] = metadata.get('privacy_policy_url')
            extension["keywords"] = metadata.get('keywords', [])
            extension["categories"] = metadata.get('categories', [])
            extension["author_name"] = metadata.get('author_name')

            # Add comprehensive security section
            extension["security"] = {
                "score": result.get('security_score'),
                "risk_level": result.get('risk_level'),
                "vulnerabilities": result.get('vulnerabilities', {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "moderate": 0,
                    "low": 0,
                    "info": 0
                }),
                "risk_factors_count": len(risk_factors),
                "risk_factors": risk_factors,
                "dependencies_count": dependencies.get('total_count', 0),
                "dependencies_with_vulnerabilities": dependencies.get('with_vulnerabilities', 0),
                "score_contributions": security.get('score_contributions', {}),
                "module_risk_levels": security.get('module_risk_levels', {}),
                "security_notes": security.get('security_notes', []),
                "dependencies": {
                    "total_count": dependencies.get('total_count', 0),
                    "runtime_count": dependencies.get('runtime_count', 0),
                    "dev_count": dependencies.get('dev_count', 0),
                    "with_vulnerabilities": dependencies.get('with_vulnerabilities', 0),
                    "high_risk_count": dependencies.get('high_risk_count', 0),
                    "medium_risk_count": dependencies.get('medium_risk_count', 0),
                    "low_risk_count": dependencies.get('low_risk_count', 0),
                    "vulnerabilities": dependencies.get('vulnerabilities', {}),
                    "list": dependencies.get('list', [])
                }
            }

            extension["vscan_url"] = result.get('vscan_url')
            extension["has_errors"] = result.get('has_errors', False)
            extension["raw_analysis_id"] = result.get('analysis_id')
        else:
            # Add error information
            extension["error"] = result.get('error', 'Unknown error')
            extension["security"] = {
                "score": None,
                "risk_level": None,
                "vulnerabilities": {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "moderate": 0,
                    "low": 0,
                    "info": 0
                },
                "risk_factors_count": 0,
                "dependencies_count": 0,
                "dependencies_with_vulnerabilities": 0
            }

        return extension

    def format_csv(self, scan_results: List[Dict[str, Any]]) -> str:
        """
        Format scan results as CSV for spreadsheet analysis.

        Args:
            scan_results: List of extension scan results

        Returns:
            CSV string with headers and data rows
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            'Extension ID',
            'Name',
            'Version',
            'Publisher',
            'Verified',
            'Risk Level',
            'Security Score',
            'Vulnerabilities',
            'Critical',
            'High',
            'Moderate',
            'Low',
            'Dependencies',
            'Last Updated',
            'vscan.dev URL'
        ])

        # Data rows
        for result in scan_results:
            security = result.get('security', {})
            metadata = result.get('metadata', {})
            publisher_info = result.get('publisher', {})
            vulnerabilities = security.get('vulnerabilities', {})
            dependencies = security.get('dependencies', {})

            # Extract values with fallbacks
            extension_id = result.get('id', '')
            display_name = result.get('display_name', result.get('name', ''))
            version = result.get('version', '')
            publisher_name = publisher_info.get('name', publisher_info.get('id', ''))
            verified = 'Yes' if publisher_info.get('verified', False) else 'No'
            risk_level = security.get('risk_level', 'unknown')
            security_score = security.get('score', '')
            vuln_total = vulnerabilities.get('total', 0)
            vuln_critical = vulnerabilities.get('critical', 0)
            vuln_high = vulnerabilities.get('high', 0)
            vuln_moderate = vulnerabilities.get('moderate', 0)
            vuln_low = vulnerabilities.get('low', 0)
            dep_count = dependencies.get('total_count', 0)
            last_updated = metadata.get('last_updated', '')
            vscan_url = result.get('vscan_url', '')

            writer.writerow([
                extension_id,
                display_name,
                version,
                publisher_name,
                verified,
                risk_level,
                security_score,
                vuln_total,
                vuln_critical,
                vuln_high,
                vuln_moderate,
                vuln_low,
                dep_count,
                last_updated,
                vscan_url
            ])

        return output.getvalue()


def main():
    """Test the output formatter module."""
    import json
    from datetime import datetime

    formatter = OutputFormatter()

    # Test data with v2 fields
    test_results = [
        {
            "id": "ms-python.python",
            "name": "python",
            "publisher": "ms-python",
            "version": "2025.16.0",
            "scan_status": "success",
            "security_score": 82,
            "risk_level": "high",
            "vulnerabilities": {
                "count": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0,
                "info": 0
            },
            "vscan_url": "https://vscan.dev/extension/ms-python.python",
            "analysis_timestamp": "2025-10-16T12:27:01.757Z",
            "metadata": {
                "display_name": "Python",
                "description": "Python language support with extension access points...",
                "version": "2025.16.0",
                "publisher": {
                    "id": "ms-python",
                    "name": "Microsoft",
                    "verified": True,
                    "domain": "https://microsoft.com"
                },
                "repository_url": "https://github.com/Microsoft/vscode-python.git",
                "license": "See Marketplace",
                "keywords": ["python", "django"],
                "statistics": {
                    "installs": 187936883,
                    "rating": 4.19,
                    "rating_count": 618
                }
            },
            "security": {
                "score": 82,
                "risk_level": "high"
            },
            "dependencies": {
                "total_count": 21,
                "with_vulnerabilities": 0
            },
            "risk_factors": [
                {
                    "type": "missing-privacy-policy",
                    "description": "No privacy policy link found",
                    "severity": "low"
                }
            ]
        }
    ]

    timestamp = datetime.utcnow().isoformat() + 'Z'
    duration = 7.8
    cache_stats = {
        "from_cache": 1,
        "fresh_scans": 0,
        "cache_hit_rate": 100.0
    }

    # Test output formatter
    print("=== FORMATTED OUTPUT ===")
    output = formatter.format_output(test_results, timestamp, duration, cache_stats=cache_stats)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
