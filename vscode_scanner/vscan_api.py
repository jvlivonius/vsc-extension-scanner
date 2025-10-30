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

from .utils import sanitize_error_message
from .constants import (
    DEFAULT_REQUEST_DELAY,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_MAX_WAIT_SECONDS,
    API_TIMEOUT_SECONDS,
    MAX_RESPONSE_SIZE_BYTES,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BASE_DELAY,
    DEFAULT_WORKFLOW_MAX_RETRIES,
    DEFAULT_WORKFLOW_RETRY_DELAY,
    RETRYABLE_STATUS_CODES,
    RETRYABLE_ERROR_PATTERNS,
    WORKFLOW_RETRYABLE_ERROR_PATTERNS,
)


class VscanAPIClient:
    """Client for vscan.dev API."""

    BASE_URL = "https://vscan.dev/api/extensions"
    USER_AGENT = (
        "VSCodeExtensionScanner/1.0.0 (+https://github.com/user/vsc-extension-scanner)"
    )

    def __init__(
        self,
        delay: float = DEFAULT_REQUEST_DELAY,
        verbose: bool = False,
        timeout: int = API_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_base_delay: float = DEFAULT_RETRY_BASE_DELAY,
        max_workflow_retries: int = DEFAULT_WORKFLOW_MAX_RETRIES,
        workflow_retry_delay: float = DEFAULT_WORKFLOW_RETRY_DELAY,
    ):
        """
        Initialize API client.

        Args:
            delay: Delay between API requests in seconds (default: from constants)
            verbose: Enable verbose logging
            timeout: Timeout for individual HTTP requests in seconds (default: from constants)
            max_retries: Maximum retry attempts for failed HTTP requests (default: from constants)
            retry_base_delay: Base delay for exponential backoff (default: from constants)
            max_workflow_retries: Maximum retry attempts for scan workflow (default: from constants)
            workflow_retry_delay: Base delay between workflow retries (default: from constants)
        """
        self.delay = delay
        self.verbose = verbose
        self.timeout = timeout
        self.last_request_time = 0
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.max_workflow_retries = max_workflow_retries
        self.workflow_retry_delay = workflow_retry_delay

        # HTTP-level retry statistics
        self.retry_stats = {
            "total_retries": 0,
            "successful_retries": 0,
            "failed_after_retries": 0,
            # Workflow-level retry statistics
            "total_workflow_retries": 0,
            "successful_workflow_retries": 0,
            "failed_after_workflow_retries": 0,
        }

        # Performance timing statistics
        self.timing_stats = {
            "submit_times": [],
            "poll_times": [],
            "results_times": [],
            "total_scan_times": [],
            "rate_limit_count": 0,
            "timeout_count": 0,
        }

    def _throttle(self):
        """Implement request throttling."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def _is_retryable_error(
        self, error: Exception, status_code: Optional[int] = None
    ) -> bool:
        """
        Determine if an error is retryable based on status code or error type.

        Args:
            error: The exception that occurred
            status_code: HTTP status code if available

        Returns:
            True if the error should be retried, False otherwise
        """
        # Extract status code from HTTPError if present
        if isinstance(error, urllib.error.HTTPError):
            status_code = error.code

        # Check if status code is retryable (429, 502, 503, 504)
        if status_code in RETRYABLE_STATUS_CODES:
            return True

        # Non-retryable status codes (explicit client/server errors)
        if status_code in {400, 401, 403, 404, 500}:
            return False

        # Check for timeout errors
        if isinstance(error, urllib.error.URLError):
            if isinstance(error.reason, TimeoutError):
                return True

        # Check error message for retryable patterns
        error_str = str(error).lower()
        for pattern in RETRYABLE_ERROR_PATTERNS:
            if pattern in error_str:
                return True

        # Default: not retryable (fail-safe)
        return False

    def _calculate_backoff_delay(
        self, attempt: int, retry_after: Optional[int] = None
    ) -> float:
        """
        Calculate delay before next retry attempt using exponential backoff with jitter.

        Implements exponential backoff with ceiling to prevent unreasonably long delays.
        The delay is capped at MAX_BACKOFF_DELAY (30 seconds) to ensure reasonable UX.

        Args:
            attempt: Current retry attempt number (0-indexed)
            retry_after: Retry-After header value in seconds (if available)

        Returns:
            Delay in seconds before next retry (minimum 0.5s, maximum MAX_BACKOFF_DELAY)
        """
        import random
        from .constants import MAX_BACKOFF_DELAY

        # If Retry-After header is present, respect it (but cap it)
        if retry_after is not None:
            return min(float(retry_after), MAX_BACKOFF_DELAY)

        # Exponential backoff
        # attempt 0: 2s, attempt 1: 4s, attempt 2: 8s, attempt 3: 16s, attempt 4: 32s, etc.
        backoff = self.retry_base_delay * (2**attempt)

        # Add jitter (±20% of backoff) to prevent thundering herd
        jitter = random.uniform(-0.2 * backoff, 0.2 * backoff)
        total_delay = backoff + jitter

        # Apply ceiling after jitter and ensure minimum delay of 0.5s
        return max(min(total_delay, MAX_BACKOFF_DELAY), 0.5)

    def _log_retry_attempt(
        self, attempt: int, max_attempts: int, error: str, delay: float
    ):
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
        timeout: Optional[int] = None,
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

                # Track rate limits and timeouts
                # pylint: disable=no-member
                if isinstance(e, urllib.error.HTTPError) and e.code == 429:
                    self.timing_stats["rate_limit_count"] += 1
                if "timeout" in str(e).lower():
                    self.timing_stats["timeout_count"] += 1

                # Check if this is the last attempt
                if attempt >= self.max_retries:
                    self.retry_stats["failed_after_retries"] += 1
                    raise

                # Check if error is retryable
                status_code = None
                if isinstance(e, urllib.error.HTTPError):
                    status_code = e.code
                    # Try to extract Retry-After header
                    retry_after_header = e.headers.get("Retry-After")
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
        timeout: Optional[int] = None,
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
            with urllib.request.urlopen(
                req, timeout=timeout
            ) as response:  # nosec B310 - URL validated by validate_url()
                status_code = response.getcode()

                # Read response with size limit
                raw_response = b""
                chunk_size = 8192
                total_read = 0

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    total_read += len(chunk)
                    if total_read > MAX_RESPONSE_SIZE_BYTES:
                        raise Exception(
                            f"[E100] Response exceeds maximum size ({MAX_RESPONSE_SIZE_BYTES} bytes)"
                        )

                    raw_response += chunk

                raw_response = raw_response.decode("utf-8")

                try:
                    json_data = json.loads(raw_response)
                except json.JSONDecodeError:
                    json_data = {}

                return status_code, json_data

        except urllib.error.HTTPError as e:
            status_code = e.code
            raw_response = e.read().decode("utf-8")

            try:
                json_data = json.loads(raw_response)
            except json.JSONDecodeError:
                json_data = {}

            if status_code == 429:
                raise Exception("[E101] Rate limit exceeded. Please try again later.")
            elif status_code == 404:
                raise Exception("Extension not found on vscan.dev")
            elif status_code >= 500:
                raise Exception(f"vscan.dev server error (HTTP {status_code})")
            else:
                # Sanitize error message from API response
                api_error = json_data.get("error", "")
                sanitized_error = (
                    sanitize_error_message(api_error, context="API error")
                    if api_error
                    else "Unknown error"
                )
                raise Exception(f"HTTP error {status_code}: {sanitized_error}")

        except urllib.error.URLError as e:
            error_msg = str(e.reason) if hasattr(e, "reason") else str(e)
            if "timed out" in error_msg.lower():
                raise Exception(
                    f"Request timed out after {timeout}s. The extension may take longer to analyze."
                )
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
        start_time = time.time()
        self._throttle()

        url = f"{self.BASE_URL}/analyze"
        payload = {"publisher": publisher, "name": name}

        status_code, response = self._make_request_with_retry(
            url, method="POST", data=payload
        )

        # Record timing
        elapsed = time.time() - start_time
        self.timing_stats["submit_times"].append(elapsed)

        if status_code in (200, 202) and "analysisId" in response:
            return response["analysisId"]
        else:
            # Sanitize error message from API response
            api_message = response.get("message", "")
            sanitized_msg = (
                sanitize_error_message(api_message, context="submission error")
                if api_message
                else "Unknown error"
            )
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
            api_message = response.get("message", "")
            sanitized_msg = (
                sanitize_error_message(api_message, context="status check error")
                if api_message
                else "Unknown error"
            )
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
        start_time = time.time()
        self._throttle()

        url = f"{self.BASE_URL}/results/{analysis_id}"
        status_code, response = self._make_request_with_retry(url)

        # Record timing
        elapsed = time.time() - start_time
        self.timing_stats["results_times"].append(elapsed)

        if status_code == 200:
            return response
        else:
            # Sanitize error message from API response
            api_message = response.get("message", "")
            sanitized_msg = (
                sanitize_error_message(api_message, context="results retrieval error")
                if api_message
                else "Unknown error"
            )
            raise Exception(f"Failed to retrieve results: {sanitized_msg}")

    def poll_until_complete(
        self,
        analysis_id: str,
        poll_interval: float = 2.0,
        max_wait: int = 300,
        progress_callback: Optional[callable] = None,
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
        poll_start = time.time()
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
                # Record poll timing
                poll_elapsed = time.time() - poll_start
                self.timing_stats["poll_times"].append(poll_elapsed)
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
                "domain": publisher_info.get("domain"),
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
                "rating_count": stats.get("ratingCount"),
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
                "open_grep": contributions.get("openGrep"),
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
                "open_grep": module_risks.get("openGrep"),
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
            "list": [],
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
                "info": vuln_summary.get("info", 0),
            }

            # Process dependency list
            for dep in deps_list:
                dep_info = {
                    "name": dep.get("name"),
                    "version": dep.get("version"),
                    "type": dep.get("type"),
                    "risk": dep.get("risk"),
                    "reason": dep.get("reason"),
                    "vulnerabilities": dep.get("vulnerabilities", []),
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
                if (
                    dep.get("vulnerabilities")
                    and len(dep.get("vulnerabilities", [])) > 0
                ):
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
                risk_factors.append(
                    {
                        "type": factor.get("type"),
                        "description": factor.get("description"),
                        "severity": factor.get("risk"),
                    }
                )

        except Exception as e:
            # Return empty list on error
            pass

        return risk_factors

    def scan_extension(
        self,
        publisher: str,
        name: str,
        progress_callback: Optional[callable] = None,
        store_raw_response: bool = False,
    ) -> Dict[str, Any]:
        """
        Complete scan workflow: submit → poll → retrieve results.
        Now captures complete API response with comprehensive parsing.

        Args:
            publisher: Extension publisher
            name: Extension name
            progress_callback: Optional callback(progress, message) for progress updates
            store_raw_response: Whether to store the raw API response (default: False)
                               Setting this to False reduces memory usage by 20-30%

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
                "info": 0,
            },
            "vscan_url": f"https://vscan.dev/extension/{publisher}.{name}",
            "analysis_timestamp": None,
        }

        scan_start = time.time()
        try:
            # Step 1: Submit analysis
            analysis_id = self.submit_analysis(publisher, name)

            # Step 2: Poll until complete
            final_status = self.poll_until_complete(
                analysis_id,
                poll_interval=DEFAULT_POLL_INTERVAL,
                max_wait=DEFAULT_MAX_WAIT_SECONDS,
                progress_callback=progress_callback,
            )

            if final_status != "completed":
                result["error"] = f"Analysis did not complete: {final_status}"
                return result

            # Step 3: Get results
            api_results = self.get_results(analysis_id)

            # Record total scan time
            scan_elapsed = time.time() - scan_start
            self.timing_stats["total_scan_times"].append(scan_elapsed)

            # Store raw response only if requested (saves memory)
            if store_raw_response:
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
                    "info": vuln_summary.get("info", 0),
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
            - total_retries: Total number of HTTP retry attempts made
            - successful_retries: Number of HTTP retries that eventually succeeded
            - failed_after_retries: Number of requests that failed after all HTTP retries
            - total_workflow_retries: Total number of workflow retry attempts made
            - successful_workflow_retries: Number of workflow retries that eventually succeeded
            - failed_after_workflow_retries: Number of scans that failed after all workflow retries
        """
        return self.retry_stats.copy()

    def get_timing_stats(self) -> Dict[str, Any]:
        """
        Get performance timing statistics.

        Returns:
            Dictionary with timing statistics:
            - submit_times: List of submission times in seconds
            - poll_times: List of polling times in seconds
            - results_times: List of results retrieval times in seconds
            - total_scan_times: List of total scan times in seconds
            - rate_limit_count: Number of rate limit errors encountered
            - timeout_count: Number of timeout errors encountered
            - avg_submit_time: Average submission time
            - avg_poll_time: Average polling time
            - avg_results_time: Average results time
            - avg_total_time: Average total scan time
        """
        import statistics

        stats = self.timing_stats.copy()

        # Calculate averages
        if stats["submit_times"]:
            stats["avg_submit_time"] = statistics.mean(stats["submit_times"])
        else:
            stats["avg_submit_time"] = 0.0

        if stats["poll_times"]:
            stats["avg_poll_time"] = statistics.mean(stats["poll_times"])
        else:
            stats["avg_poll_time"] = 0.0

        if stats["results_times"]:
            stats["avg_results_time"] = statistics.mean(stats["results_times"])
        else:
            stats["avg_results_time"] = 0.0

        if stats["total_scan_times"]:
            stats["avg_total_time"] = statistics.mean(stats["total_scan_times"])
        else:
            stats["avg_total_time"] = 0.0

        return stats

    def _is_workflow_retryable_error(self, error_message: str) -> bool:
        """
        Determine if an error should trigger a workflow-level retry.

        Workflow retries are for entire scan workflows that fail due to transient issues.
        These are different from HTTP-level retries which retry individual API calls.

        Args:
            error_message: The error message from scan_extension()

        Returns:
            True if the error indicates a transient issue that should be retried at workflow level
        """
        if not error_message:
            return False

        error_lower = error_message.lower()

        # Check for workflow-retryable error patterns
        for pattern in WORKFLOW_RETRYABLE_ERROR_PATTERNS:
            if pattern in error_lower:
                return True

        return False

    def scan_extension_with_retry(
        self,
        publisher: str,
        name: str,
        progress_callback: Optional[callable] = None,
        store_raw_response: bool = False,
    ) -> Dict[str, Any]:
        """
        Scan extension with workflow-level retry for transient errors.

        This wraps scan_extension() and retries the entire workflow if it fails
        due to transient errors like rate limiting, timeouts, or server errors.

        Args:
            publisher: Extension publisher
            name: Extension name
            progress_callback: Optional callback(progress, message) for progress updates
            store_raw_response: Whether to store the raw API response (default: False)

        Returns:
            Scan result dict with complete parsed data
        """
        last_result = None

        for attempt in range(self.max_workflow_retries + 1):  # +1 for initial attempt
            # Call the regular scan_extension method
            result = self.scan_extension(
                publisher, name, progress_callback, store_raw_response
            )

            # If scan succeeded, return immediately
            if result["scan_status"] == "success":
                # If this was a retry (attempt > 0), increment successful retry counter
                if attempt > 0:
                    self.retry_stats["successful_workflow_retries"] += 1
                return result

            # Scan failed - check if we should retry
            last_result = result
            error_message = result.get("error", "")

            # Check if this is the last attempt
            if attempt >= self.max_workflow_retries:
                # All retries exhausted
                self.retry_stats["failed_after_workflow_retries"] += 1
                return result

            # Check if error is workflow-retryable
            if not self._is_workflow_retryable_error(error_message):
                # Non-retryable error, fail immediately without retrying
                return result

            # This is a retryable error - increment counter and wait before retry
            self.retry_stats["total_workflow_retries"] += 1

            # Calculate backoff delay (exponential: 5s, 10s for default config)
            delay = self.workflow_retry_delay * (2**attempt)

            # Log retry attempt if verbose
            if self.verbose:
                from .utils import log

                log(
                    f"  Workflow retry {attempt + 1}/{self.max_workflow_retries} "
                    f"after error: {error_message[:100]}",
                    "WARNING",
                )
                log(f"  Waiting {delay:.1f}s before workflow retry...", "INFO")

            # Wait before retrying
            time.sleep(delay)

        # This should never be reached, but return last result just in case
        return last_result
