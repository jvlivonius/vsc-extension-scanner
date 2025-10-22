#!/usr/bin/env python3
"""
vscan.dev API Client Module

Integrates with the vscan.dev API to analyze VS Code extensions.
Based on the validated API endpoints from Phase 1 research.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple


class VscanAPIClient:
    """Client for vscan.dev API."""

    BASE_URL = "https://vscan.dev/api/extensions"
    USER_AGENT = "VSCodeExtensionScanner/1.0.0 (+https://github.com/user/vsc-extension-scanner)"

    def __init__(self, delay: float = 1.5, verbose: bool = False):
        """
        Initialize API client.

        Args:
            delay: Delay between API requests in seconds
            verbose: Enable verbose logging
        """
        self.delay = delay
        self.verbose = verbose
        self.last_request_time = 0

    def _throttle(self):
        """Implement request throttling."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Make HTTP request to vscan.dev API.

        Args:
            url: Request URL
            method: HTTP method (GET or POST)
            data: Request payload (for POST)
            timeout: Request timeout in seconds

        Returns:
            Tuple of (status_code, json_response)

        Raises:
            Exception: If request fails
        """
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json"
        }

        if data is not None:
            headers["Content-Type"] = "application/json"
            data_bytes = json.dumps(data).encode('utf-8')
        else:
            data_bytes = None

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                raw_response = response.read().decode('utf-8')

                try:
                    json_data = json.loads(raw_response)
                except json.JSONDecodeError:
                    json_data = {}

                return status_code, json_data

        except urllib.error.HTTPError as e:
            status_code = e.code
            raw_response = e.read().decode('utf-8')

            try:
                json_data = json.loads(raw_response)
            except json.JSONDecodeError:
                json_data = {"error": raw_response}

            if status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            elif status_code == 404:
                raise Exception("Extension not found on vscan.dev")
            elif status_code >= 500:
                raise Exception(f"vscan.dev server error (HTTP {status_code})")
            else:
                raise Exception(f"HTTP error {status_code}: {json_data.get('error', 'Unknown error')}")

        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")

        except Exception as e:
            raise Exception(f"Request failed: {e}")

    def submit_analysis(self, publisher: str, name: str) -> str:
        """
        Submit extension for analysis.

        Args:
            publisher: Extension publisher
            name: Extension name

        Returns:
            Analysis ID

        Raises:
            Exception: If submission fails
        """
        self._throttle()

        url = f"{self.BASE_URL}/analyze"
        payload = {"publisher": publisher, "name": name}

        status_code, response = self._make_request(url, method="POST", data=payload)

        if status_code in (200, 202) and "analysisId" in response:
            return response["analysisId"]
        else:
            raise Exception(f"Failed to submit analysis: {response.get('message', 'Unknown error')}")

    def check_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Check analysis status.

        Args:
            analysis_id: Analysis ID from submit_analysis

        Returns:
            Status response dict

        Raises:
            Exception: If status check fails
        """
        self._throttle()

        url = f"{self.BASE_URL}/status/{analysis_id}"
        status_code, response = self._make_request(url)

        if status_code == 200 and "status" in response:
            return response
        else:
            raise Exception(f"Failed to check status: {response.get('message', 'Unknown error')}")

    def get_results(self, analysis_id: str) -> Dict[str, Any]:
        """
        Retrieve analysis results.

        Args:
            analysis_id: Analysis ID from submit_analysis

        Returns:
            Results dict

        Raises:
            Exception: If results retrieval fails
        """
        self._throttle()

        url = f"{self.BASE_URL}/results/{analysis_id}"
        status_code, response = self._make_request(url)

        if status_code == 200:
            return response
        else:
            raise Exception(f"Failed to retrieve results: {response.get('message', 'Unknown error')}")

    def poll_until_complete(
        self,
        analysis_id: str,
        poll_interval: float = 2.0,
        max_wait: int = 300
    ) -> str:
        """
        Poll status endpoint until analysis is complete.

        Args:
            analysis_id: Analysis ID to poll
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait

        Returns:
            Final status ("completed" or "failed")

        Raises:
            Exception: If polling times out or fails
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait:
                raise Exception(f"Analysis timeout after {elapsed:.1f}s")

            status_response = self.check_status(analysis_id)
            status = status_response.get("status")

            if status == "completed":
                return status
            elif status == "failed":
                raise Exception("Analysis failed")

            # Wait before next poll
            time.sleep(poll_interval)

    def scan_extension(self, publisher: str, name: str) -> Dict[str, Any]:
        """
        Complete scan workflow: submit → poll → retrieve results.

        Args:
            publisher: Extension publisher
            name: Extension name

        Returns:
            Scan result dict with standardized fields

        Raises:
            Exception: If scan fails
        """
        result = {
            "name": name,
            "publisher": publisher,
            "scan_status": "error",
            "error": None,
            "security_score": None,
            "risk_level": None,
            "vulnerabilities": {
                "count": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0,
                "info": 0
            },
            "vscan_url": f"https://vscan.dev/extension/{publisher}.{name}",
            "analysis_timestamp": None
        }

        try:
            # Step 1: Submit analysis
            analysis_id = self.submit_analysis(publisher, name)

            # Step 2: Poll until complete
            final_status = self.poll_until_complete(analysis_id, poll_interval=2.0, max_wait=300)

            if final_status != "completed":
                result["error"] = f"Analysis did not complete: {final_status}"
                return result

            # Step 3: Get results
            api_results = self.get_results(analysis_id)

            # Parse results
            if "securityScore" in api_results:
                result["security_score"] = api_results["securityScore"].get("score")
                result["risk_level"] = api_results["securityScore"].get("riskLevel")

            if "analysisModules" in api_results:
                deps = api_results["analysisModules"].get("dependencies", {})
                vuln_summary = deps.get("vulnerabilities", {}).get("summary", {})

                result["vulnerabilities"] = {
                    "count": vuln_summary.get("total", 0),
                    "critical": vuln_summary.get("critical", 0),
                    "high": vuln_summary.get("high", 0),
                    "moderate": vuln_summary.get("moderate", 0),
                    "low": vuln_summary.get("low", 0),
                    "info": vuln_summary.get("info", 0)
                }

            if "analysisTimestamp" in api_results:
                result["analysis_timestamp"] = api_results["analysisTimestamp"]

            result["scan_status"] = "success"

        except Exception as e:
            result["error"] = str(e)
            result["scan_status"] = "error"

        return result
