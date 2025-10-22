# vscan.dev API Research - Phase 1 Findings

**Date:** 2025-10-22
**Status:** ✅ Completed

## Executive Summary

Successfully reverse-engineered and validated the vscan.dev API endpoints. All three endpoints (analyze, status, results) are working as documented. The API uses an asynchronous analysis workflow with cached results, making it very efficient for repeated queries.

## API Endpoints

### 1. Submit Extension for Analysis

**Endpoint:** `POST https://vscan.dev/api/extensions/analyze`

**Request:**
```json
{
  "publisher": "ms-python",
  "name": "python"
}
```

**Response (HTTP 202):**
```json
{
  "analysisId": "23da418d-cbb1-4f76-899b-bc53f1aca5a6",
  "status": "pending",
  "message": "Extension accepted for analysis. Check status endpoint."
}
```

**Observations:**
- Always returns HTTP 202 (Accepted)
- Returns immediately with a UUID `analysisId`
- Analysis runs asynchronously in the background

### 2. Check Analysis Status

**Endpoint:** `GET https://vscan.dev/api/extensions/status/{analysisId}`

**Response (HTTP 200):**
```json
{
  "analysisId": "23da418d-cbb1-4f76-899b-bc53f1aca5a6",
  "status": "completed",
  "progress": 100,
  "message": "Analysis Complete",
  "details": "Report is ready",
  "updatedAt": "2025-10-16T12:27:01.757Z"
}
```

**Observations:**
- Status values observed: `"pending"`, `"completed"`
- Progress is 0-100 integer
- **IMPORTANT:** Popular extensions are already analyzed and cached
  - All test extensions returned `status: "completed"` immediately (0.0s)
  - No actual polling was required for ms-python, prettier-vscode, or vscode-docker
  - This means most user extensions will likely be cached

### 3. Retrieve Analysis Results

**Endpoint:** `GET https://vscan.dev/api/extensions/results/{analysisId}`

**Response (HTTP 200):** See full schema in [CLAUDE.md](CLAUDE.md)

**Key Fields:**
```json
{
  "securityScore": {
    "score": 82,
    "riskLevel": "high"
  },
  "analysisModules": {
    "dependencies": {
      "vulnerabilities": {
        "summary": {
          "info": 0,
          "low": 0,
          "moderate": 0,
          "high": 0,
          "critical": 0,
          "total": 0
        }
      }
    }
  }
}
```

## Test Results

### Extensions Tested

| Extension | Publisher | Security Score | Risk Level | Vulnerabilities | Analysis Time |
|-----------|-----------|----------------|------------|-----------------|---------------|
| Python | ms-python | 82/100 | high | 0 | 0.0s (cached) |
| Prettier | esbenp | 82/100 | medium | 0 | 0.0s (cached) |
| Docker | ms-azuretools | 93/100 | medium | 0 | 0.0s (cached) |

### Key Findings

1. **Caching Behavior**
   - Popular extensions are pre-analyzed and cached
   - All test extensions returned results instantly
   - This is excellent for user experience
   - Polling may only be needed for obscure/new extensions

2. **Risk Level vs Security Score**
   - Security score 82/100 can be "high" risk (ms-python.python)
   - Security score 82/100 can be "medium" risk (prettier-vscode)
   - Security score 93/100 is "medium" risk (vscode-docker)
   - **Risk level appears to be the authoritative severity indicator**

3. **Vulnerability Counts**
   - None of the tested extensions had dependency vulnerabilities
   - The `total` field in summary is the sum of all severity levels
   - Individual vulnerabilities would be in `details` object (not observed in tests)

4. **HTTP Behavior**
   - All endpoints return proper JSON
   - Status codes: 200 (success), 202 (accepted)
   - No rate limiting observed (tested 3 extensions with 3s delay)
   - No authentication required

## Implementation Recommendations

### 1. Polling Strategy

```python
def wait_for_analysis(analysis_id, max_wait=300, poll_interval=2):
    """Poll status endpoint until completed or timeout."""
    start = time.time()

    while time.time() - start < max_wait:
        status = check_status(analysis_id)

        if status['status'] == 'completed':
            return True
        elif status['status'] == 'failed':
            return False

        time.sleep(poll_interval)

    return False  # Timeout
```

**Recommendations:**
- Initial poll interval: 2 seconds
- Maximum wait: 5 minutes (300s)
- Most extensions will complete in first poll (cached)
- Use exponential backoff if needed: 2s → 4s → 8s → 16s

### 2. Error Handling

**Expected Error Scenarios:**

| Scenario | HTTP Code | Handling |
|----------|-----------|----------|
| Extension not found | Unknown | Mark as "not_found", continue scanning |
| Network timeout | 0 | Retry 3 times, then fail scan |
| Rate limiting | 429 | Exponential backoff, retry |
| Server error | 500-599 | Log error, continue with other extensions |
| Invalid response | 200 + malformed JSON | Log error, mark as "error" |

### 3. Request Headers

Use the following User-Agent to identify the tool:

```python
headers = {
    "User-Agent": "VSCodeExtensionScanner/1.0.0 (+https://github.com/user/vsc-extension-scanner)",
    "Accept": "application/json",
    "Content-Type": "application/json"  # For POST requests
}
```

### 4. Data Extraction

From the results JSON, extract:

```python
def parse_results(response):
    """Parse vscan.dev results into scanner format."""
    return {
        "security_score": response["securityScore"]["score"],
        "risk_level": response["securityScore"]["riskLevel"],
        "vulnerabilities": {
            "count": response["analysisModules"]["dependencies"]["vulnerabilities"]["summary"]["total"],
            "severity": response["securityScore"]["riskLevel"],
            "critical": response["analysisModules"]["dependencies"]["vulnerabilities"]["summary"]["critical"],
            "high": response["analysisModules"]["dependencies"]["vulnerabilities"]["summary"]["high"],
            "moderate": response["analysisModules"]["dependencies"]["vulnerabilities"]["summary"]["moderate"],
            "low": response["analysisModules"]["dependencies"]["vulnerabilities"]["summary"]["low"],
        },
        "analysis_timestamp": response.get("analysisTimestamp"),
        "has_errors": response.get("hasErrors", False)
    }
```

## Edge Cases & Unknowns

### Tested ✅
- Popular extensions (cached results)
- Multiple consecutive requests (no rate limiting)
- Standard workflow: analyze → status → results

### Not Tested ❓
- Unpopular/new extensions (actual polling required)
- Rate limiting behavior (429 responses)
- Invalid extension names
- Non-existent publishers
- Extensions with actual vulnerabilities
- Very large extension sets (100+)
- Concurrent requests
- Failed analysis status
- Network errors/timeouts

### Recommended Additional Testing

1. **Test an obscure extension** to observe actual polling behavior
2. **Test invalid extension** to see error response format
3. **Test concurrent requests** to understand rate limits
4. **Test with no network** to validate error handling
5. **Find extension with vulnerabilities** to see `details` structure

## Validation Script

The complete API validation script is available at:
- **File:** [test_api.py](test_api.py)
- **Usage:** `python3 test_api.py`
- **Output:** JSON results to stdout, logs to stderr

## Conclusion

✅ **Phase 1 Complete**

The vscan.dev API is well-designed, predictable, and suitable for our use case:

1. **All endpoints validated and working**
2. **Response format documented**
3. **Caching behavior understood**
4. **Error handling strategy defined**
5. **Ready to proceed to Phase 2 implementation**

The asynchronous design with caching makes the API very efficient. Most user scans will complete quickly since popular extensions are pre-analyzed.

### Next Steps (Phase 2)

1. Implement extension discovery (find VS Code extensions directory)
2. Parse package.json files to extract publisher/name
3. Integrate vscan.dev API client
4. Implement JSON output generation
5. Add progress indicators and error handling
