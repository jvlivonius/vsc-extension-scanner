#!/usr/bin/env python3
"""
Canonical Mock for vscan.dev API

This module provides a canonical mock that matches the real vscan.dev API structure.
The structure is validated against the real API in test_mock_validation.py.

All test files should use this mock to ensure consistency and prevent mock drift.

Version: 1.0
Last Validated: 2025-10-26
Validated Against: vscan.dev API (real integration test)
"""

from typing import Dict, Any, List, Optional


class CanonicalVscanAPIMock:
    """
    Canonical mock that matches real vscan.dev API response structure.

    This mock is validated against the real API to ensure accuracy.
    Use these methods in all test files to maintain consistency.
    """

    @staticmethod
    def get_success_response(
        publisher: str,
        name: str,
        version: str = "1.0.0",
        security_score: int = 85,
        vuln_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Returns structure matching real vscan.dev API success response.

        Args:
            publisher: Extension publisher (e.g., "ms-python")
            name: Extension name (e.g., "python")
            version: Extension version (e.g., "2023.1.0")
            security_score: Security score 0-100 (default: 85)
            vuln_count: Number of vulnerabilities (default: 0)

        Returns:
            Dict matching real API success response structure
        """
        return {
            # Core identification
            "name": name,
            "publisher": publisher,
            "scan_status": "success",
            "error": None,
            # Comprehensive data categories (v3.0+)
            "metadata": {
                "id": f"{publisher}.{name}",
                "version": version,
                "display_name": f"{name.title()} Extension",
                "description": f"Mock extension {name}",
                "publisher_display_name": publisher.title(),
                "publisher_verified": True,
                "install_count": 1000000,
                "rating": 4.5,
                "rating_count": 1500,
            },
            "security": {
                "score": security_score,
                "risk_level": _calculate_risk_level(security_score),
                "analysis_version": "3.0",
                "last_updated": "2025-10-26T00:00:00Z",
            },
            "dependencies": {
                "total_count": 5,
                "npm_dependencies": ["express", "lodash"],
                "vulnerabilities": {
                    "total": vuln_count,
                    "critical": 0,
                    "high": 0,
                    "moderate": vuln_count,
                    "low": 0,
                },
            },
            "risk_factors": [
                {
                    "type": "network_access",
                    "severity": "medium",
                    "description": "Extension makes network requests",
                }
            ]
            if vuln_count > 0
            else [],
            # Legacy fields for backward compatibility
            "security_score": security_score,
            "risk_level": _calculate_risk_level(security_score),
            "vulnerabilities": {
                "count": vuln_count,
                "critical": 0,
                "high": 0,
                "moderate": vuln_count,
                "low": 0,
                "info": 0,
            },
            # Additional metadata
            "vscan_url": f"https://vscan.dev/extension/{publisher}.{name}",
            "analysis_timestamp": "2025-10-26T00:00:00Z",
            "has_errors": None,  # Real API returns None, not False
            "raw_response": None,
            "analysis_id": "mock-analysis-id-12345",  # Real API returns this
        }

    @staticmethod
    def get_error_response(
        publisher: str, name: str, error_msg: str = "Extension not found"
    ) -> Dict[str, Any]:
        """
        Returns structure matching real vscan.dev API error response.

        Args:
            publisher: Extension publisher
            name: Extension name
            error_msg: Error message

        Returns:
            Dict matching real API error response structure
        """
        return {
            # Core identification
            "name": name,
            "publisher": publisher,
            "scan_status": "error",
            "error": error_msg,
            # Empty/null data categories
            "metadata": {},
            "security": {},
            "dependencies": {},
            "risk_factors": [],
            # Legacy fields (null for errors)
            "security_score": None,
            "risk_level": None,
            "vulnerabilities": {
                "count": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0,
                "info": 0,
            },
            # Additional metadata
            "vscan_url": f"https://vscan.dev/extension/{publisher}.{name}",
            "analysis_timestamp": None,
            "has_errors": None,  # Real API returns None
            "raw_response": None,
            "analysis_id": None,  # No analysis ID for errors
        }

    @staticmethod
    def get_vulnerable_response(
        publisher: str, name: str, critical: int = 1, high: int = 2, moderate: int = 3
    ) -> Dict[str, Any]:
        """
        Returns response for extension with vulnerabilities.

        Args:
            publisher: Extension publisher
            name: Extension name
            critical: Number of critical vulnerabilities
            high: Number of high vulnerabilities
            moderate: Number of moderate vulnerabilities

        Returns:
            Dict with vulnerability data
        """
        total_vulns = critical + high + moderate
        # Security score decreases with vulnerabilities
        security_score = max(30, 90 - (critical * 20 + high * 10 + moderate * 5))

        response = CanonicalVscanAPIMock.get_success_response(
            publisher, name, security_score=security_score, vuln_count=total_vulns
        )

        # Update vulnerability counts
        response["vulnerabilities"] = {
            "count": total_vulns,
            "critical": critical,
            "high": high,
            "moderate": moderate,
            "low": 0,
            "info": 0,
        }

        response["dependencies"]["vulnerabilities"] = {
            "total": total_vulns,
            "critical": critical,
            "high": high,
            "moderate": moderate,
            "low": 0,
        }

        # Add risk factors
        response["risk_factors"] = [
            {
                "type": "vulnerable_dependencies",
                "severity": "high" if critical > 0 else "medium",
                "description": f"Found {total_vulns} vulnerabilities in dependencies",
            }
        ]

        return response


def _calculate_risk_level(security_score: int) -> str:
    """
    Calculate risk level from security score.

    Matches vscan.dev logic:
    - 80-100: low
    - 60-79: medium
    - 40-59: high
    - 0-39: critical
    """
    if security_score >= 80:
        return "low"
    elif security_score >= 60:
        return "medium"
    elif security_score >= 40:
        return "high"
    else:
        return "critical"


# Required fields that must be present in all responses
# Based on real API validation from ms-python.python on 2025-10-26
REQUIRED_SUCCESS_FIELDS = {
    "name",
    "publisher",
    "scan_status",
    "error",
    "metadata",
    "security",
    "dependencies",
    "risk_factors",
    "security_score",
    "risk_level",
    "vulnerabilities",
    "vscan_url",
    "analysis_timestamp",
    "has_errors",
    "raw_response",
    "analysis_id",
}

REQUIRED_ERROR_FIELDS = {
    "name",
    "publisher",
    "scan_status",
    "error",
    "metadata",
    "security",
    "dependencies",
    "risk_factors",
    "security_score",
    "risk_level",
    "vulnerabilities",
    "vscan_url",
    "analysis_timestamp",
    "has_errors",
    "raw_response",
    "analysis_id",
}

# Critical fields that scanner depends on
CRITICAL_FIELDS = {"scan_status", "security_score", "vulnerabilities"}
