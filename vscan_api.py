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

from utils import sanitize_error_message


class VscanAPIClient:
    """Client for vscan.dev API."""

    BASE_URL = "https://vscan.dev/api/extensions"
    USER_AGENT = "VSCodeExtensionScanner/1.0.0 (+https://github.com/user/vsc-extension-scanner)"

    # Maximum response size (10MB)
    MAX_RESPONSE_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        delay: float = 1.5,
        verbose: bool = False,
        timeout: int = 30,
        max_retries: int = 3,
        retry_base_delay: float = 2.0
    ):
        """
        Initialize API client.

        Args:
            delay: Delay between API requests in seconds
            verbose: Enable verbose logging
            timeout: Timeout for individual HTTP requests in seconds
            max_retries: Maximum retry attempts for failed requests (default: 3)
            retry_base_delay: Base delay for exponential backoff (default: 2.0)
        """
        self.delay = delay
        self.verbose = verbose
        self.timeout = timeout
        self.last_request_time = 0
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.retry_stats = {
            "total_retries": 0,
            "successful_retries": 0,
            "failed_after_retries": 0
        }

    def _throttle(self):
        """Implement request throttling."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def _is_retryable_error(self, error: Exception, status_code: Optional[int] = None) -> bool:
        """
        Determine if an error is retryable.

        Args:
            error: The exception that occurred
            status_code: HTTP status code if available

        Returns:
            True if the error should be retried, False otherwise
        """
        error_str = str(error).lower()

        # Timeout errors are retryable
        if isinstance(error, urllib.error.URLError):
            if isinstance(error.reason, TimeoutError):
                return True
            # Connection errors are retryable
            if "connection" in str(error.reason).lower():
                return True

        # HTTP errors with specific status codes
        if isinstance(error, urllib.error.HTTPError):
            status_code = error.code

        # Check status code (from HTTPError or explicit parameter)
        if status_code:
            # Rate limiting - retryable with backoff
            if status_code == 429:
                return True
            # Server errors - retryable
            if status_code in [502, 503, 504]:
                return True
            # Other errors - not retryable
            # 404 (not found), 500 (internal error), 4xx (client errors)
            return False

        # Check error message patterns for retryable errors
        retryable_patterns = [
            "timeout",
            "timed out",
            "connection",
            "rate limit",
            "502",  # Bad Gateway
            "503",  # Service Unavailable
            "504",  # Gateway Timeout
            "429",  # Too Many Requests
        ]

        for pattern in retryable_patterns:
            if pattern in error_str:
                return True

        # Non-retryable error patterns
        non_retryable_patterns = [
            "not found",
            "404",
            "500",  # Internal Server Error (not transient)
            "400",  # Bad Request
            "401",  # Unauthorized
            "403",  # Forbidden
        ]

        for pattern in non_retryable_patterns:
            if pattern in error_str:
                return False

        # Default: not retryable (fail safe)
        return False

    def _calculate_backoff_delay(self, attempt: int, retry_after: Optional[int] = None) -> float:
        """
        Calculate delay before next retry attempt using exponential backoff with jitter.

        Args:
            attempt: Current retry attempt number (0-indexed)
            retry_after: Retry-After header value in seconds (if available)

        Returns:
            Delay in seconds before next retry
        """
        import random

        # If Retry-After header is present, respect it
        if retry_after is not None:
            return float(retry_after)

        # Exponential backoff: base_delay * 2^attempt
        # attempt 0: 2s, attempt 1: 4s, attempt 2: 8s
        backoff = self.retry_base_delay * (2 ** attempt)

        # Add jitter (0-1 second randomization)
        jitter = random.uniform(0, 1)

        return backoff + jitter

    def _log_retry_attempt(self, attempt: int, max_attempts: int, error: str, delay: float):
        """
        Log retry attempt information (only in verbose mode).

        Args:
            attempt: Current retry attempt number (1-indexed for display)
            max_attempts: Maximum number of retry attempts
            error: Error message that triggered the retry
            delay: Delay before next retry in seconds
        """
        if self.verbose:
            from utils import log
            log(f"  Retry {attempt}/{max_attempts} after error: {error}", "WARNING")
            log(f"  Waiting {delay:.1f}s before retry...", "INFO")

    def _make_request_with_retry(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Make HTTP request with retry logic.

        Wraps _make_request() with exponential backoff retry for transient errors.

        Args:
            url: Request URL
            method: HTTP method (GET or POST)
            data: Request payload (for POST)
            timeout: Request timeout in seconds (None = use default)

        Returns:
            Tuple of (status_code, json_response)

        Raises:
            Exception: If request fails after all retries
        """
        last_error = None
        retry_after = None

        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                # Make the actual request
                return self._make_request(url, method, data, timeout)

            except Exception as e:
                last_error = e

                # Check if this is the last attempt
                if attempt >= self.max_retries:
                    self.retry_stats["failed_after_retries"] += 1
                    raise

                # Check if error is retryable
                status_code = None
                if isinstance(e, urllib.error.HTTPError):
                    status_code = e.code
                    # Try to extract Retry-After header
                    retry_after_header = e.headers.get('Retry-After')
                    if retry_after_header:
                        try:
                            retry_after = int(retry_after_header)
                        except ValueError:
                            retry_after = None

                if not self._is_retryable_error(e, status_code):
                    # Not retryable, raise immediately
                    raise

                # Calculate backoff delay
                delay = self._calculate_backoff_delay(attempt, retry_after)

                # Update stats
                self.retry_stats["total_retries"] += 1

                # Log retry attempt
                self._log_retry_attempt(attempt + 1, self.max_retries, str(e), delay)

                # Wait before retrying
                time.sleep(delay)

                # Reset retry_after for next attempt
                retry_after = None

        # If we somehow get here, mark as successful retry
        self.retry_stats["successful_retries"] += 1
        raise last_error  # This should never happen, but just in case

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Make HTTP request to vscan.dev API.

        Args:
            url: Request URL
            method: HTTP method (GET or POST)
            data: Request payload (for POST)
            timeout: Request timeout in seconds (None = use default)

        Returns:
            Tuple of (status_code, json_response)

        Raises:
            Exception: If request fails
        """
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.timeout

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

                # Read response with size limit
                raw_response = b''
                chunk_size = 8192
                total_read = 0

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    total_read += len(chunk)
                    if total_read > self.MAX_RESPONSE_SIZE:
                        raise Exception(f"Response exceeds maximum size ({self.MAX_RESPONSE_SIZE} bytes)")

                    raw_response += chunk

                raw_response = raw_response.decode('utf-8')

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
                json_data = {}

            if status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            elif status_code == 404:
                raise Exception("Extension not found on vscan.dev")
            elif status_code >= 500:
                raise Exception(f"vscan.dev server error (HTTP {status_code})")
            else:
                # Sanitize error message from API response
                api_error = json_data.get('error', '')
                sanitized_error = sanitize_error_message(api_error, context="API error") if api_error else "Unknown error"
                raise Exception(f"HTTP error {status_code}: {sanitized_error}")

        except urllib.error.URLError as e:
            error_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
            if "timed out" in error_msg.lower():
                raise Exception(f"Request timed out after {timeout}s. The extension may take longer to analyze.")
            # Sanitize network error message
            sanitized_error = sanitize_error_message(error_msg, context="network error")
            raise Exception(f"Network error: {sanitized_error}")

        except Exception as e:
            # Sanitize generic error message
            sanitized_error = sanitize_error_message(str(e), context="request error")
            raise Exception(f"Request failed: {sanitized_error}")

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

        status_code, response = self._make_request_with_retry(url, method="POST", data=payload)

        if status_code in (200, 202) and "analysisId" in response:
            return response["analysisId"]
        else:
            # Sanitize error message from API response
            api_message = response.get('message', '')
            sanitized_msg = sanitize_error_message(api_message, context="submission error") if api_message else "Unknown error"
            raise Exception(f"Failed to submit analysis: {sanitized_msg}")

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
        status_code, response = self._make_request_with_retry(url)

        if status_code == 200 and "status" in response:
            return response
        else:
            # Sanitize error message from API response
            api_message = response.get('message', '')
            sanitized_msg = sanitize_error_message(api_message, context="status check error") if api_message else "Unknown error"
            raise Exception(f"Failed to check status: {sanitized_msg}")

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
        status_code, response = self._make_request_with_retry(url)

        if status_code == 200:
            return response
        else:
            # Sanitize error message from API response
            api_message = response.get('message', '')
            sanitized_msg = sanitize_error_message(api_message, context="results retrieval error") if api_message else "Unknown error"
            raise Exception(f"Failed to retrieve results: {sanitized_msg}")

    def poll_until_complete(
        self,
        analysis_id: str,
        poll_interval: float = 2.0,
        max_wait: int = 300,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Poll status endpoint until analysis is complete.

        Args:
            analysis_id: Analysis ID to poll
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait
            progress_callback: Optional callback(progress, message) for progress updates

        Returns:
            Final status ("completed" or "failed")

        Raises:
            Exception: If polling times out or fails
        """
        start_time = time.time()
        last_progress = 0

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait:
                raise Exception(f"Analysis timeout after {elapsed:.1f}s")

            status_response = self.check_status(analysis_id)
            status = status_response.get("status")
            progress = status_response.get("progress", 0)
            message = status_response.get("message", "")

            # Call progress callback if provided and progress changed
            if progress_callback and progress != last_progress:
                progress_callback(progress, message)
                last_progress = progress

            if status == "completed":
                return status
            elif status == "failed":
                raise Exception("Analysis failed")

            # Wait before next poll
            time.sleep(poll_interval)

    def _parse_extension_metadata(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract extension metadata from API response.

        Args:
            api_response: Full API response from vscan.dev

        Returns:
            Parsed metadata dictionary
        """
        metadata = {}

        try:
            ext_info = api_response.get("extensionInfo", {})
            analysis_modules = api_response.get("analysisModules", {})
            meta_module = analysis_modules.get("metadata", {})
            meta_data = meta_module.get("metadata", {})

            # Basic extension info
            metadata["name"] = ext_info.get("name")
            metadata["version"] = ext_info.get("version")
            metadata["display_name"] = meta_data.get("displayName")
            metadata["description"] = meta_data.get("description")

            # Publisher info
            publisher_info = meta_data.get("publisherInfo", {})
            metadata["publisher"] = {
                "id": publisher_info.get("name"),
                "name": publisher_info.get("displayName"),
                "verified": publisher_info.get("isVerified", False),
                "domain": publisher_info.get("domain")
            }

            # URLs
            metadata["repository_url"] = meta_data.get("repositoryUrl")
            metadata["homepage_url"] = meta_data.get("homepageUrl")
            metadata["support_url"] = meta_data.get("supportUrl")
            metadata["privacy_policy_url"] = meta_data.get("privacyPolicyUrl")

            # License and categories
            metadata["license"] = meta_data.get("license")
            metadata["keywords"] = meta_data.get("keywords", [])
            metadata["categories"] = meta_data.get("categories", [])

            # Statistics
            stats = meta_data.get("statistics", {})
            metadata["statistics"] = {
                "installs": stats.get("installCount"),
                "updates": stats.get("updateCount"),
                "rating": round(stats.get("averageRating", 0), 2),
                "rating_count": stats.get("ratingCount")
            }

            # Dates
            metadata["last_updated"] = meta_data.get("lastUpdated")

            # Author
            author = meta_data.get("author", {})
            metadata["author_name"] = author.get("name")

        except Exception as e:
            # Return partial metadata on error
            pass

        return metadata

    def _parse_security_details(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed security score breakdown from API response.

        Args:
            api_response: Full API response from vscan.dev

        Returns:
            Parsed security details dictionary
        """
        security = {}

        try:
            security_score = api_response.get("securityScore", {})

            # Basic security score
            security["score"] = security_score.get("score")
            security["risk_level"] = security_score.get("riskLevel")

            # Score contributions (how each module affected the score)
            contributions = security_score.get("contributions", {})
            security["score_contributions"] = {
                "base": contributions.get("base"),
                "metadata": contributions.get("metadata"),
                "dependencies": contributions.get("dependencies"),
                "socket": contributions.get("socket"),
                "virus_total": contributions.get("virusTotal"),
                "permissions": contributions.get("permissions"),
                "ossf_scorecard": contributions.get("ossfScorecard"),
                "network_endpoints": contributions.get("networkEndpoints"),
                "sensitive_info": contributions.get("sensitiveInfo"),
                "obfuscation": contributions.get("obfuscation"),
                "consolidated_ast": contributions.get("consolidatedAst"),
                "open_grep": contributions.get("openGrep")
            }

            # Module risk levels
            module_risks = security_score.get("moduleRiskLevels", {})
            security["module_risk_levels"] = {
                "metadata": module_risks.get("metadata"),
                "dependencies": module_risks.get("dependencies"),
                "socket": module_risks.get("socket"),
                "virus_total": module_risks.get("virusTotal"),
                "permissions": module_risks.get("permissions"),
                "ossf_scorecard": module_risks.get("ossfScorecard"),
                "network_endpoints": module_risks.get("networkEndpoints"),
                "sensitive_info": module_risks.get("sensitiveInfo"),
                "obfuscation": module_risks.get("obfuscation"),
                "consolidated_ast": module_risks.get("consolidatedAst"),
                "open_grep": module_risks.get("openGrep")
            }

            # Security notes
            security["security_notes"] = security_score.get("notes", [])

        except Exception as e:
            # Return partial security data on error
            pass

        return security

    def _parse_dependencies(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure dependency information from API response.

        Args:
            api_response: Full API response from vscan.dev

        Returns:
            Parsed dependencies dictionary with summary and list
        """
        dependencies_data = {
            "total_count": 0,
            "runtime_count": 0,
            "dev_count": 0,
            "with_vulnerabilities": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "list": []
        }

        try:
            analysis_modules = api_response.get("analysisModules", {})
            deps_module = analysis_modules.get("dependencies", {})
            deps_list = deps_module.get("dependencies", [])

            # Vulnerability summary
            vuln_summary = deps_module.get("vulnerabilities", {}).get("summary", {})
            dependencies_data["vulnerabilities"] = {
                "total": vuln_summary.get("total", 0),
                "critical": vuln_summary.get("critical", 0),
                "high": vuln_summary.get("high", 0),
                "moderate": vuln_summary.get("moderate", 0),
                "low": vuln_summary.get("low", 0),
                "info": vuln_summary.get("info", 0)
            }

            # Process dependency list
            for dep in deps_list:
                dep_info = {
                    "name": dep.get("name"),
                    "version": dep.get("version"),
                    "type": dep.get("type"),
                    "risk": dep.get("risk"),
                    "reason": dep.get("reason"),
                    "vulnerabilities": dep.get("vulnerabilities", [])
                }

                dependencies_data["list"].append(dep_info)

                # Count by type
                if dep.get("type") == "runtime":
                    dependencies_data["runtime_count"] += 1
                elif dep.get("type") == "dev":
                    dependencies_data["dev_count"] += 1

                # Count by risk
                risk = dep.get("risk", "").lower()
                if risk == "high":
                    dependencies_data["high_risk_count"] += 1
                elif risk == "medium":
                    dependencies_data["medium_risk_count"] += 1
                elif risk == "low":
                    dependencies_data["low_risk_count"] += 1

                # Count vulnerabilities
                if dep.get("vulnerabilities") and len(dep.get("vulnerabilities", [])) > 0:
                    dependencies_data["with_vulnerabilities"] += 1

            dependencies_data["total_count"] = len(deps_list)

        except Exception as e:
            # Return partial dependency data on error
            pass

        return dependencies_data

    def _parse_risk_factors(self, api_response: Dict[str, Any]) -> list:
        """
        Extract risk factor details from API response.

        Args:
            api_response: Full API response from vscan.dev

        Returns:
            List of risk factor dictionaries
        """
        risk_factors = []

        try:
            analysis_modules = api_response.get("analysisModules", {})
            meta_module = analysis_modules.get("metadata", {})
            factors = meta_module.get("riskFactors", [])

            for factor in factors:
                risk_factors.append({
                    "type": factor.get("type"),
                    "description": factor.get("description"),
                    "severity": factor.get("risk")
                })

        except Exception as e:
            # Return empty list on error
            pass

        return risk_factors

    def scan_extension(
        self,
        publisher: str,
        name: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Complete scan workflow: submit → poll → retrieve results.
        Now captures complete API response with comprehensive parsing.

        Args:
            publisher: Extension publisher
            name: Extension name
            progress_callback: Optional callback(progress, message) for progress updates

        Returns:
            Scan result dict with complete parsed data

        Raises:
            Exception: If scan fails
        """
        result = {
            "name": name,
            "publisher": publisher,
            "scan_status": "error",
            "error": None,
            "raw_response": None,
            "metadata": {},
            "security": {},
            "dependencies": {},
            "risk_factors": [],
            # Legacy fields for backward compatibility
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
            final_status = self.poll_until_complete(
                analysis_id,
                poll_interval=2.0,
                max_wait=300,
                progress_callback=progress_callback
            )

            if final_status != "completed":
                result["error"] = f"Analysis did not complete: {final_status}"
                return result

            # Step 3: Get results
            api_results = self.get_results(analysis_id)

            # Store raw response
            result["raw_response"] = api_results
            result["analysis_id"] = analysis_id

            # Parse all data categories
            result["metadata"] = self._parse_extension_metadata(api_results)
            result["security"] = self._parse_security_details(api_results)
            result["dependencies"] = self._parse_dependencies(api_results)
            result["risk_factors"] = self._parse_risk_factors(api_results)

            # Extract legacy fields for backward compatibility
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

            # Check for errors in analysis
            result["has_errors"] = api_results.get("hasErrors", False)

            result["scan_status"] = "success"

        except Exception as e:
            result["error"] = str(e)
            result["scan_status"] = "error"

        return result

    def get_retry_stats(self) -> Dict[str, int]:
        """
        Get retry statistics.

        Returns:
            Dictionary with retry statistics:
            - total_retries: Total number of retry attempts made
            - successful_retries: Number of retries that eventually succeeded
            - failed_after_retries: Number of requests that failed after all retries
        """
        return self.retry_stats.copy()
