# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VS Code Extension Security Scanner is a standalone Python CLI tool that performs manual security audits of installed VS Code extensions by leveraging the vscan.dev security analysis service. The tool automates discovery of installed extensions, queries vscan.dev for security information, and generates JSON reports of findings.

## Technology Stack

- **Language:** Python 3.8+
- **HTTP Library:** `requests` or `httpx`
- **CLI Parsing:** `argparse`
- **Distribution:** Standalone `.py` script (no installation required)
- **Output Format:** JSON

## Development Commands

Since this is a standalone Python script project with no existing implementation yet:

```bash
# Run the tool (once implemented)
python vscan.py

# Run with custom directory
python vscan.py --extensions-dir /path/to/extensions

# Run with verbose output
python vscan.py --verbose

# Run with custom delay
python vscan.py --delay 3

# Output to file
python vscan.py --output results.json

# Show help
python vscan.py --help
```

## Architecture & Key Design Decisions

### Extension Discovery
- Auto-detect VS Code extensions directory based on platform:
  - macOS: `~/.vscode/extensions/`
  - Windows: `%USERPROFILE%\.vscode\extensions\`
  - Linux: `~/.vscode/extensions/`
- Read extension metadata from `package.json` files in each extension directory
- Support custom paths via `--extensions-dir` argument
- Use `pathlib` for cross-platform path handling

### vscan.dev Integration

**Critical:** vscan.dev does not provide a documented public API. The following endpoints have been reverse-engineered through browser analysis:

#### API Endpoints

**1. Submit Extension for Analysis**
- **Endpoint:** `https://vscan.dev/api/extensions/analyze`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Request Payload:**
  ```json
  {
    "publisher": "ms-azuretools",
    "name": "vscode-docker"
  }
  ```
- **Response (202 Accepted):**
  ```json
  {
    "analysisId": "60873001-f496-418f-b060-4d72e9c6218c",
    "status": "pending",
    "message": "Extension accepted for analysis. Check status endpoint."
  }
  ```

**2. Check Analysis Status**
- **Endpoint:** `https://vscan.dev/api/extensions/status/{analysisId}`
- **Method:** `GET`
- **Response (In Progress):**
  ```json
  {
    "analysisId": "60873001-f496-418f-b060-4d72e9c6218c",
    "status": "pending",
    "progress": 45,
    "message": "Analysis in progress",
    "details": "Running security checks",
    "updatedAt": "2025-10-16T12:14:44.989Z"
  }
  ```
- **Response (Completed):**
  ```json
  {
    "analysisId": "60873001-f496-418f-b060-4d72e9c6218c",
    "status": "completed",
    "progress": 100,
    "message": "Analysis Complete",
    "details": "Report is ready",
    "updatedAt": "2025-10-16T12:14:44.989Z"
  }
  ```

**3. Retrieve Analysis Results**
- **Endpoint:** `https://vscan.dev/api/extensions/results/{analysisId}`
- **Method:** `GET`
- **Response:** See [Response Schema](#vscandev-response-schema) below

#### vscan.dev Response Schema

The results endpoint returns a comprehensive security analysis with the following structure:

```json
{
  "analysisId": "60873001-f496-418f-b060-4d72e9c6218c",
  "extensionInfo": {
    "name": "vscode-docker",
    "version": "2.0.0",
    "publisher": "Microsoft"
  },
  "securityScore": {
    "score": 93,
    "riskLevel": "medium",
    "contributions": {
      "base": 100,
      "metadata": 1,
      "dependencies": 1,
      "permissions": -5,
      "consolidatedAst": -5,
      "...": "..."
    },
    "moduleRiskLevels": {
      "metadata": "low",
      "dependencies": "low",
      "permissions": "medium",
      "consolidatedAst": "medium",
      "...": "..."
    },
    "notes": []
  },
  "analysisTimestamp": "2025-10-16T12:14:44.988Z",
  "hasErrors": false,
  "analysisModules": {
    "metadata": { "...": "..." },
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
    },
    "virusTotal": { "...": "..." },
    "permissions": { "...": "..." },
    "...": "..."
  }
}
```

#### Implementation Requirements

**Workflow:**
1. Submit extension for analysis via `/api/extensions/analyze` (POST)
2. Poll `/api/extensions/status/{analysisId}` (GET) until `status` is `"completed"`
3. Retrieve results from `/api/extensions/results/{analysisId}` (GET)
4. Parse `securityScore.riskLevel` and `analysisModules.dependencies.vulnerabilities.summary`

**Request Throttling:**
- Default: 1.5 second delay between API requests
- Configurable via `--delay` argument
- Poll status endpoint every 2 seconds while analysis is pending
- Maximum wait time: 5 minutes per extension analysis

**Error Handling:**
- Handle rate limiting (HTTP 429) gracefully
- Continue scanning if individual extension queries fail
- Stop execution only if vscan.dev is completely unreachable
- Implement exponential backoff for status polling if needed
- Use proper User-Agent headers to identify the tool

**Status Values:**
- `pending` - Analysis submitted, waiting to start
- `in_progress` - Analysis is running
- `completed` - Analysis finished successfully
- `failed` - Analysis encountered an error

### Error Handling Strategy

- **Exit Code 0:** Scan completed successfully, no vulnerabilities found
- **Exit Code 1:** Scan completed successfully, vulnerabilities found
- **Exit Code 2:** Scan failed due to errors

**Error Handling Rules:**
- Warn (don't fail) for malformed/corrupted extension installations
- Continue scanning remaining extensions if individual queries fail
- Validate JSON responses before processing
- 30-second timeout per request
- Clear, actionable error messages for:
  - VS Code not installed
  - Extensions directory not readable
  - Network connectivity issues
  - vscan.dev unavailable

### JSON Output Schema

The tool must generate JSON with this structure:
```json
{
  "summary": {
    "total_extensions_scanned": 42,
    "vulnerabilities_found": 3,
    "scan_timestamp": "2025-10-22T14:30:00Z",
    "scan_duration_seconds": 95.5
  },
  "extensions": [
    {
      "name": "Extension Name",
      "id": "publisher.extension-name",
      "version": "1.2.3",
      "publisher": "Publisher Name",
      "vulnerabilities": {
        "count": 1,
        "severity": "medium",
        "details": "Description of vulnerability"
      },
      "last_updated": "2025-10-15",
      "vscan_url": "https://vscan.dev/extension/publisher.extension-name",
      "scan_status": "success"
    }
  ]
}
```

- `scan_status` values: "success", "not_found", "error"
- Include error message for failed scans
- All requests must use HTTPS
- Output to stdout by default, support `--output` for file output

### Progress Indicators

Display progress to stderr (not stdout, which is for JSON output):
```
Detecting VS Code installation...
Found VS Code extensions directory: /home/user/.vscode/extensions
Discovered 42 extensions

Scanning extensions for vulnerabilities...
[1/42] Scanning ms-python.python v2024.10.0... ✓
[2/42] Scanning esbenp.prettier-vscode v10.1.0... ✓
[3/42] Scanning dbaeumer.vscode-eslint v2.4.2... ⚠ Vulnerabilities found
...

Scan complete! Found 3 vulnerabilities in 42 extensions.
Results written to stdout.
```

## Command-Line Interface

### Required Arguments
| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--extensions-dir` | `-d` | Path to VS Code extensions directory | Auto-detected |
| `--output` | `-o` | Output file path (JSON) | stdout |
| `--delay` | `-t` | Delay between requests (seconds) | 1.5 |
| `--verbose` | `-v` | Enable verbose output | False |
| `--help` | `-h` | Show help message | - |
| `--version` | `-V` | Show version information | - |

## Performance Requirements

- Target: < 2 minutes for 50 extensions (with 2-second delay)
- Memory usage: < 100MB RAM
- Minimize file I/O operations
- Process extensions sequentially with proper throttling

## Security Considerations

- All requests to vscan.dev must use HTTPS
- Never store or transmit user credentials or sensitive data
- Respect vscan.dev's rate limits to avoid being blocked
- Validate all input paths to prevent directory traversal
- Sanitize extension metadata before including in output

## Out of Scope (Do Not Implement)

- Support for VS Code variants (VSCodium, Cursor, etc.)
- CI/CD pipeline integration
- Scheduled/automated scanning
- HTML or PDF report generation
- Historical vulnerability tracking
- Local vulnerability database caching
- Extension installation/removal functionality
- GUI interface
- Auto-remediation of vulnerabilities

## Implementation Phases

### Phase 1: Research & Discovery
- Reverse-engineer vscan.dev API endpoints
- Document request/response format
- Validate endpoint behavior with test extensions

### Phase 2: Core Implementation
- Implement extension discovery for all platforms
- Implement vscan.dev API integration
- Implement JSON output generation
- Implement error handling and logging

### Phase 3: Testing & Refinement
- Test on macOS, Windows, Linux
- Test with various extension sets
- Test error scenarios
- Refine user experience (progress, messages)

## References

- [vscan.dev](https://vscan.dev) - VS Code Extension Security Analyzer
- [VS Code Extension API](https://code.visualstudio.com/api)
- Full requirements: See PRD.md
