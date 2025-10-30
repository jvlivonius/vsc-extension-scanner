#!/usr/bin/env python3
"""
VS Code Extension Scanner - Phase 1: API Validation Script

This script validates the vscan.dev API endpoints and documents their behavior.
It tests the three-step workflow: analyze → status → results
"""

import json
import time
import sys
from typing import Dict, Any, Optional, Tuple
import urllib.request
import urllib.error
import urllib.parse

import pytest


@pytest.mark.unit
class VscanAPITester:
    """Test and validate vscan.dev API endpoints."""

    BASE_URL = "https://vscan.dev/api/extensions"
    USER_AGENT = "VSCodeExtensionScanner/0.1.0 (API Validation)"

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = []

    def log(self, message: str, level: str = "INFO"):
        """Print log message to stderr."""
        if self.verbose:
            print(f"[{level}] {message}", file=sys.stderr)

    def make_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Tuple[int, Dict[str, Any], str]:
        """
        Make HTTP request and return status code, JSON response, and raw response.

        Returns:
            Tuple of (status_code, json_data, raw_response_text)
        """
        headers = {"User-Agent": self.USER_AGENT, "Accept": "application/json"}

        if data is not None:
            headers["Content-Type"] = "application/json"
            data_bytes = json.dumps(data).encode("utf-8")
        else:
            data_bytes = None

        req = urllib.request.Request(
            url, data=data_bytes, headers=headers, method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                raw_response = response.read().decode("utf-8")

                try:
                    json_data = json.loads(raw_response)
                except json.JSONDecodeError:
                    json_data = {}

                return status_code, json_data, raw_response

        except urllib.error.HTTPError as e:
            status_code = e.code
            raw_response = e.read().decode("utf-8")

            try:
                json_data = json.loads(raw_response)
            except json.JSONDecodeError:
                json_data = {"error": raw_response}

            return status_code, json_data, raw_response

        except urllib.error.URLError as e:
            self.log(f"Network error: {e.reason}", "ERROR")
            return 0, {"error": str(e.reason)}, ""

        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            return 0, {"error": str(e)}, ""

    def submit_analysis(self, publisher: str, name: str) -> Optional[str]:
        """
        Submit extension for analysis.

        Returns:
            analysisId if successful, None otherwise
        """
        url = f"{self.BASE_URL}/analyze"
        payload = {"publisher": publisher, "name": name}

        self.log(f"Submitting {publisher}.{name} for analysis...")
        self.log(f"POST {url}")
        self.log(f"Payload: {json.dumps(payload)}")

        status_code, response, raw = self.make_request(url, method="POST", data=payload)

        self.log(f"Status: {status_code}")
        self.log(f"Response: {json.dumps(response, indent=2)}")

        if status_code in (200, 202) and "analysisId" in response:
            analysis_id = response["analysisId"]
            self.log(f"✓ Analysis submitted successfully: {analysis_id}", "SUCCESS")
            return analysis_id
        else:
            self.log(f"✗ Failed to submit analysis", "ERROR")
            return None

    def check_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Check analysis status.

        Returns:
            Status response dict if successful, None otherwise
        """
        url = f"{self.BASE_URL}/status/{analysis_id}"

        self.log(f"Checking status for {analysis_id}...")
        self.log(f"GET {url}")

        status_code, response, raw = self.make_request(url)

        self.log(f"Status: {status_code}")
        self.log(f"Response: {json.dumps(response, indent=2)}")

        if status_code == 200 and "status" in response:
            return response
        else:
            self.log(f"✗ Failed to check status", "ERROR")
            return None

    def get_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis results.

        Returns:
            Results dict if successful, None otherwise
        """
        url = f"{self.BASE_URL}/results/{analysis_id}"

        self.log(f"Retrieving results for {analysis_id}...")
        self.log(f"GET {url}")

        status_code, response, raw = self.make_request(url)

        self.log(f"Status: {status_code}")

        if status_code == 200:
            # Don't log full response (too large), just key fields
            if "securityScore" in response:
                score = response["securityScore"]
                self.log(f"Security Score: {score.get('score')}/100")
                self.log(f"Risk Level: {score.get('riskLevel')}")

            if (
                "analysisModules" in response
                and "dependencies" in response["analysisModules"]
            ):
                vuln_summary = (
                    response["analysisModules"]["dependencies"]
                    .get("vulnerabilities", {})
                    .get("summary", {})
                )
                self.log(f"Vulnerabilities: {json.dumps(vuln_summary)}")

            return response
        else:
            self.log(f"✗ Failed to retrieve results", "ERROR")
            return None

    def poll_until_complete(
        self, analysis_id: str, poll_interval: int = 2, max_wait: int = 300
    ) -> Optional[str]:
        """
        Poll status endpoint until analysis is complete.

        Returns:
            Final status ("completed", "failed", etc.) or None if timeout
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait:
                self.log(f"✗ Timeout after {elapsed:.1f}s", "ERROR")
                return None

            status_response = self.check_status(analysis_id)

            if status_response is None:
                self.log("✗ Failed to get status", "ERROR")
                return None

            status = status_response.get("status")
            progress = status_response.get("progress", 0)

            self.log(
                f"Status: {status}, Progress: {progress}%, Elapsed: {elapsed:.1f}s"
            )

            if status == "completed":
                self.log(f"✓ Analysis completed in {elapsed:.1f}s", "SUCCESS")
                return status

            if status == "failed":
                self.log(f"✗ Analysis failed", "ERROR")
                return status

            # Wait before next poll
            time.sleep(poll_interval)

    def test_extension(
        self, publisher: str, name: str, wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Test complete workflow for a single extension.

        Returns:
            Test result summary
        """
        self.log(f"\n{'='*60}", "INFO")
        self.log(f"Testing: {publisher}.{name}", "INFO")
        self.log(f"{'='*60}", "INFO")

        result = {
            "extension": f"{publisher}.{name}",
            "publisher": publisher,
            "name": name,
            "analysis_id": None,
            "status": None,
            "security_score": None,
            "risk_level": None,
            "vulnerabilities": None,
            "success": False,
            "error": None,
        }

        # Step 1: Submit analysis
        analysis_id = self.submit_analysis(publisher, name)
        if not analysis_id:
            result["error"] = "Failed to submit analysis"
            return result

        result["analysis_id"] = analysis_id

        # Step 2: Poll status
        if wait_for_completion:
            final_status = self.poll_until_complete(analysis_id)

            if final_status != "completed":
                result["error"] = f"Analysis did not complete: {final_status}"
                result["status"] = final_status
                return result

            result["status"] = final_status

            # Step 3: Get results
            results = self.get_results(analysis_id)

            if not results:
                result["error"] = "Failed to retrieve results"
                return result

            # Parse results
            if "securityScore" in results:
                result["security_score"] = results["securityScore"].get("score")
                result["risk_level"] = results["securityScore"].get("riskLevel")

            if "analysisModules" in results:
                deps = results["analysisModules"].get("dependencies", {})
                vuln_summary = deps.get("vulnerabilities", {}).get("summary", {})
                result["vulnerabilities"] = vuln_summary

            result["success"] = True
        else:
            result["status"] = "submitted"
            result["success"] = True

        return result


def main():
    """Run API validation tests."""
    print("VS Code Extension Scanner - API Validation Test", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)

    tester = VscanAPITester(verbose=True)

    # Test extensions with different characteristics
    test_cases = [
        # Well-known Microsoft extension
        ("ms-python", "python"),
        # Popular third-party extension
        ("esbenp", "prettier-vscode"),
        # Another Microsoft extension (from user's example)
        ("ms-azuretools", "vscode-docker"),
    ]

    results = []

    for publisher, name in test_cases:
        result = tester.test_extension(publisher, name, wait_for_completion=True)
        results.append(result)

        # Delay between tests
        print(f"\n{'='*60}", file=sys.stderr)
        print("Waiting 3 seconds before next test...", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        time.sleep(3)

    # Print summary
    print("\n" + "=" * 60, file=sys.stderr)
    print("TEST SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    for result in results:
        print(f"\nExtension: {result['extension']}", file=sys.stderr)
        print(f"  Success: {result['success']}", file=sys.stderr)
        print(f"  Analysis ID: {result['analysis_id']}", file=sys.stderr)
        print(f"  Status: {result['status']}", file=sys.stderr)
        print(f"  Security Score: {result['security_score']}", file=sys.stderr)
        print(f"  Risk Level: {result['risk_level']}", file=sys.stderr)
        print(f"  Vulnerabilities: {result['vulnerabilities']}", file=sys.stderr)
        if result["error"]:
            print(f"  Error: {result['error']}", file=sys.stderr)

    # Output JSON results to stdout
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
