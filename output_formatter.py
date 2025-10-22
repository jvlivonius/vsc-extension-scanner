#!/usr/bin/env python3
"""
Output Formatter Module

Formats scan results into JSON output according to the schema defined in CLAUDE.md
"""

from typing import List, Dict, Any


class OutputFormatter:
    """Formats scan results into standardized JSON output."""

    def format_output(
        self,
        scan_results: List[Dict[str, Any]],
        scan_timestamp: str,
        scan_duration: float
    ) -> Dict[str, Any]:
        """
        Format scan results into JSON output.

        Args:
            scan_results: List of extension scan results
            scan_timestamp: ISO 8601 timestamp of scan start
            scan_duration: Scan duration in seconds

        Returns:
            Formatted output dictionary
        """
        # Count vulnerabilities
        total_vulnerabilities = 0
        for result in scan_results:
            if result.get('scan_status') == 'success':
                vuln_count = result.get('vulnerabilities', {}).get('count', 0)
                total_vulnerabilities += vuln_count

        # Build summary
        summary = {
            "total_extensions_scanned": len(scan_results),
            "vulnerabilities_found": total_vulnerabilities,
            "scan_timestamp": scan_timestamp,
            "scan_duration_seconds": round(scan_duration, 2)
        }

        # Format extensions
        extensions = []
        for result in scan_results:
            extension = self._format_extension(result)
            extensions.append(extension)

        # Build output
        output = {
            "summary": summary,
            "extensions": extensions
        }

        return output

    def _format_extension(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a single extension result.

        Args:
            result: Extension scan result

        Returns:
            Formatted extension dict
        """
        extension = {
            "name": result.get('display_name') or result.get('name', 'Unknown'),
            "id": result.get('id', 'unknown.unknown'),
            "version": result.get('version', 'unknown'),
            "publisher": result.get('publisher', 'Unknown'),
            "scan_status": result.get('scan_status', 'error')
        }

        # Add success-specific fields
        if result.get('scan_status') == 'success':
            extension.update({
                "security_score": result.get('security_score'),
                "risk_level": result.get('risk_level'),
                "vulnerabilities": result.get('vulnerabilities', {
                    "count": 0,
                    "critical": 0,
                    "high": 0,
                    "moderate": 0,
                    "low": 0,
                    "info": 0
                }),
                "vscan_url": result.get('vscan_url'),
                "analysis_timestamp": result.get('analysis_timestamp')
            })
        else:
            # Add error information
            extension["error"] = result.get('error', 'Unknown error')
            extension["vulnerabilities"] = {
                "count": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0,
                "info": 0
            }

        return extension


def main():
    """Test the output formatter module."""
    import json
    from datetime import datetime

    formatter = OutputFormatter()

    # Test data
    test_results = [
        {
            "id": "ms-python.python",
            "name": "python",
            "publisher": "ms-python",
            "version": "2024.10.0",
            "display_name": "Python",
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
            "analysis_timestamp": "2025-10-16T12:27:01.757Z"
        },
        {
            "id": "esbenp.prettier-vscode",
            "name": "prettier-vscode",
            "publisher": "esbenp",
            "version": "10.1.0",
            "display_name": "Prettier",
            "scan_status": "success",
            "security_score": 82,
            "risk_level": "medium",
            "vulnerabilities": {
                "count": 2,
                "critical": 0,
                "high": 1,
                "moderate": 1,
                "low": 0,
                "info": 0
            },
            "vscan_url": "https://vscan.dev/extension/esbenp.prettier-vscode",
            "analysis_timestamp": "2025-10-16T13:00:20.505Z"
        },
        {
            "id": "unknown.failed-extension",
            "name": "failed-extension",
            "publisher": "unknown",
            "version": "1.0.0",
            "display_name": "Failed Extension",
            "scan_status": "error",
            "error": "Extension not found on vscan.dev"
        }
    ]

    timestamp = datetime.utcnow().isoformat() + 'Z'
    duration = 95.5

    output = formatter.format_output(test_results, timestamp, duration)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
