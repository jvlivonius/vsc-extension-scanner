# Product Requirements Document (PRD)
# VS Code Extension Security Scanner CLI

**Version:** 1.0
**Date:** 2025-10-22
**Status:** Draft

---

## 1. Executive Summary

The VS Code Extension Security Scanner is a standalone Python CLI tool that enables developers to perform manual security audits of their installed VS Code extensions by leveraging the vscan.dev security analysis service. The tool automates the process of discovering installed extensions, querying vscan.dev for security information, and generating a JSON report of findings.

---

## 2. Problem Statement

VS Code extensions have broad access to the editor environment and can potentially introduce security vulnerabilities. Developers currently lack an automated way to quickly audit all their installed extensions for known security issues. While vscan.dev provides a web-based security analysis service, manually checking each extension is time-consuming and error-prone.

---

## 3. Goals & Objectives

### Primary Goals
- Enable developers to quickly scan all installed VS Code extensions for security vulnerabilities
- Provide actionable security information in a machine-readable format (JSON)
- Support cross-platform usage (macOS, Windows, Linux)

### Success Criteria
- Tool successfully detects and scans 100% of installed VS Code extensions
- Generates accurate vulnerability reports based on vscan.dev data
- Completes full scan of typical extension set (20-50 extensions) within reasonable time
- Handles errors gracefully and provides clear feedback to users

---

## 4. Target Users

**Primary Audience:** Software developers who use VS Code

**User Personas:**
- Security-conscious developers performing periodic security audits
- Developers setting up new development environments
- Team leads ensuring consistent security standards across development teams

---

## 5. Use Cases

### Primary Use Case: Manual Security Audit
**Actor:** Developer
**Goal:** Audit all installed VS Code extensions for security vulnerabilities
**Flow:**
1. Developer runs the CLI tool
2. Tool auto-detects VS Code installation and extensions
3. Tool queries vscan.dev for each extension
4. Tool generates JSON report with findings
5. Developer reviews report and takes action on vulnerable extensions

### Secondary Use Case: Custom Extension Directory
**Actor:** Developer with multiple VS Code installations
**Goal:** Scan a specific VS Code installation
**Flow:**
1. Developer runs CLI tool with custom directory path argument
2. Tool scans specified directory instead of default location
3. Tool generates report as normal

---

## 6. Functional Requirements

### 6.1 Extension Discovery
- **FR-1.1:** Tool MUST auto-detect the default VS Code extensions directory on macOS, Windows, and Linux
- **FR-1.2:** Tool MUST support custom extension directory paths via command-line argument
- **FR-1.3:** Tool MUST read extension metadata (name, ID, version, publisher) from package.json files
- **FR-1.4:** Tool MUST validate that the extensions directory exists and is readable before scanning
- **FR-1.5:** Tool MUST display an error message and exit if VS Code installation cannot be found

### 6.2 vscan.dev Integration
- **FR-2.1:** Tool MUST query vscan.dev for security information for each discovered extension
- **FR-2.2:** Tool MUST implement request throttling with configurable delay between requests (default: 1-2 seconds)
- **FR-2.3:** Tool MUST stop execution and display an error if vscan.dev is unreachable or returns fatal errors
- **FR-2.4:** Tool MUST continue scanning remaining extensions if individual extension queries fail
- **FR-2.5:** Tool MUST warn users when extensions cannot be found on vscan.dev

### 6.3 Output & Reporting
- **FR-3.1:** Tool MUST generate output in JSON format
- **FR-3.2:** JSON output MUST include for each extension:
  - Extension name
  - Extension ID (publisher.extension-name)
  - Version
  - Publisher information
  - Vulnerability count/severity information
  - Last updated date
  - Direct link to vscan.dev results
- **FR-3.3:** Tool MUST include a summary section with:
  - Total extensions scanned
  - Number of vulnerabilities found
  - Scan timestamp
  - Scan duration
- **FR-3.4:** Tool MUST write JSON output to stdout by default
- **FR-3.5:** Tool SHOULD support optional output file parameter

### 6.4 Error Handling
- **FR-4.1:** Tool MUST warn (not fail) when encountering malformed or corrupted extension installations
- **FR-4.2:** Tool MUST provide clear error messages for common failure scenarios:
  - VS Code not installed
  - Extensions directory not readable
  - Network connectivity issues
  - vscan.dev unavailable
- **FR-4.3:** Tool MUST use appropriate exit codes:
  - 0: Scan completed successfully, no vulnerabilities found
  - 1: Scan completed successfully, vulnerabilities found
  - 2: Scan failed due to errors

### 6.5 Configuration & Options
- **FR-5.1:** Tool MUST support verbose mode for debugging (show request/response details)
- **FR-5.2:** Tool MUST allow users to customize request delay via command-line argument
- **FR-5.3:** Tool MUST display help information with `--help` or `-h` flag
- **FR-5.4:** Tool MUST display version information with `--version` flag

---

## 7. Non-Functional Requirements

### 7.1 Performance
- **NFR-1.1:** Tool SHOULD complete scanning of 50 extensions within 2 minutes (assuming 2-second delay between requests)
- **NFR-1.2:** Tool MUST minimize memory footprint (target: < 100MB RAM usage)

### 7.2 Compatibility
- **NFR-2.1:** Tool MUST support Python 3.8 and higher
- **NFR-2.2:** Tool MUST work on macOS, Windows 10/11, and Linux distributions
- **NFR-2.3:** Tool MUST be distributed as a standalone Python script (no installation required)

### 7.3 Reliability
- **NFR-3.1:** Tool MUST handle network timeouts gracefully (30-second timeout per request)
- **NFR-3.2:** Tool MUST validate JSON responses from vscan.dev before processing

### 7.4 Usability
- **NFR-4.1:** Tool MUST provide clear progress indicators during scanning
- **NFR-4.2:** Tool MUST use standard command-line conventions for arguments and flags
- **NFR-4.3:** Error messages MUST be actionable and user-friendly

### 7.5 Security
- **NFR-5.1:** Tool MUST use HTTPS for all requests to vscan.dev
- **NFR-5.2:** Tool MUST NOT store or transmit user credentials or sensitive data
- **NFR-5.3:** Tool MUST respect vscan.dev's rate limits to avoid being blocked

---

## 8. Technical Specifications

### 8.1 Technology Stack
- **Language:** Python 3.8+
- **HTTP Library:** `requests` (recommended) or `httpx`
- **JSON Processing:** Built-in `json` module
- **CLI Argument Parsing:** `argparse`
- **Distribution:** Standalone `.py` script

### 8.2 Default VS Code Extension Paths
```
macOS: ~/.vscode/extensions/
Windows: %USERPROFILE%\.vscode\extensions\
Linux: ~/.vscode/extensions/
```

### 8.3 vscan.dev API Research

**Note:** vscan.dev does not provide a documented public API. Implementation will require reverse-engineering the web interface to identify the endpoints used.

**Research Findings:**
- vscan.dev is a VSCode Extension Security Analyzer
- Users input extension name or ID for analysis
- Performs deep analysis including:
  - Metadata and publisher vetting
  - Dependency vulnerability scanning (GitHub Advisory DB)
  - OSSF Scorecard Analysis
  - VirusTotal integration
  - Static code analysis for hardcoded secrets
  - Obfuscation detection

**Implementation Requirements:**
1. Analyze network requests made by vscan.dev website
2. Identify API endpoint(s) for querying extension security data
3. Determine request format (likely extension ID as parameter)
4. Parse JSON/HTML response to extract vulnerability information
5. Implement proper User-Agent headers to identify the tool
6. Monitor for API changes and implement error handling for unexpected responses

**Endpoint Discovery Tasks:**
- [ ] Use browser developer tools to capture network requests when searching for an extension
- [ ] Document request method (GET/POST), headers, and parameters
- [ ] Document response format and structure
- [ ] Test with multiple extensions to confirm consistency
- [ ] Identify rate limiting behavior (status codes, response headers)

### 8.4 JSON Output Schema

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
      "name": "Example Extension",
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
    },
    {
      "name": "Safe Extension",
      "id": "publisher.safe-extension",
      "version": "2.0.0",
      "publisher": "Trusted Publisher",
      "vulnerabilities": {
        "count": 0,
        "severity": null,
        "details": null
      },
      "last_updated": "2025-10-20",
      "vscan_url": "https://vscan.dev/extension/publisher.safe-extension",
      "scan_status": "success"
    },
    {
      "name": "Unknown Extension",
      "id": "publisher.unknown",
      "version": "0.5.0",
      "publisher": "Unknown Publisher",
      "vulnerabilities": null,
      "last_updated": "2025-09-01",
      "vscan_url": null,
      "scan_status": "not_found",
      "error": "Extension not found on vscan.dev"
    }
  ]
}
```

---

## 9. User Interface

### 9.1 Command-Line Interface

**Basic Usage:**
```bash
python vscan.py
```

**Custom Directory:**
```bash
python vscan.py --extensions-dir /path/to/extensions
```

**Verbose Mode:**
```bash
python vscan.py --verbose
```

**Custom Delay:**
```bash
python vscan.py --delay 3
```

**Output to File:**
```bash
python vscan.py --output results.json
```

**Help:**
```bash
python vscan.py --help
```

### 9.2 Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--extensions-dir` | `-d` | Path to VS Code extensions directory | Auto-detected |
| `--output` | `-o` | Output file path (JSON) | stdout |
| `--delay` | `-t` | Delay between requests (seconds) | 1.5 |
| `--verbose` | `-v` | Enable verbose output | False |
| `--help` | `-h` | Show help message | - |
| `--version` | `-V` | Show version information | - |

### 9.3 Output Examples

**Progress Indicator (stderr):**
```
Detecting VS Code installation...
Found VS Code extensions directory: /home/user/.vscode/extensions
Discovered 42 extensions

Scanning extensions for vulnerabilities...
[1/42] Scanning ms-python.python v2024.10.0... ✓
[2/42] Scanning esbenp.prettier-vscode v10.1.0... ✓
[3/42] Scanning dbaeumer.vscode-eslint v2.4.2... ⚠ Vulnerabilities found
...
[42/42] Scanning xyz.unknown-ext v1.0.0... ⚠ Not found on vscan.dev

Scan complete! Found 3 vulnerabilities in 42 extensions.
Results written to stdout.
```

**Error Message Examples:**
```
Error: VS Code installation not found. Please specify --extensions-dir manually.
Error: Cannot read extensions directory: /path/to/extensions (Permission denied)
Error: vscan.dev is unreachable. Please check your internet connection.
Warning: Extension 'publisher.extension-name' not found on vscan.dev
Warning: Malformed extension directory: /path/to/corrupted-extension (skipping)
```

---

## 10. Dependencies

### 10.1 Python Standard Library
- `argparse` - Command-line argument parsing
- `json` - JSON encoding/decoding
- `pathlib` - Cross-platform path handling
- `sys` - System-specific parameters and functions
- `os` - Operating system interfaces
- `time` - Time-related functions (delays)
- `datetime` - Timestamp generation

### 10.2 Third-Party Libraries
- `requests` - HTTP library for API requests
  - Alternative: `httpx` (async support for future enhancements)

---

## 11. Constraints & Assumptions

### 11.1 Constraints
- Tool depends on vscan.dev availability and stability
- No documented API means implementation may break if vscan.dev changes
- Rate limiting on vscan.dev may limit scan speed
- Cannot scan extensions that are not indexed by vscan.dev

### 11.2 Assumptions
- VS Code stores extensions in standard directories
- Extension metadata is available in package.json files
- vscan.dev provides consistent response format
- Users have internet connectivity when running the tool
- Users have read permissions for VS Code extensions directory

---

## 12. Out of Scope

The following features are explicitly **NOT** included in this version:

- Support for VS Code variants (VSCodium, Cursor, etc.)
- Automated CI/CD pipeline integration
- Scheduled/automated scanning
- HTML or PDF report generation
- Historical vulnerability tracking
- Local vulnerability database caching
- Extension installation/removal functionality
- Integration with other vulnerability databases beyond vscan.dev
- GUI interface
- Auto-remediation of vulnerabilities
- Extension version update recommendations

---

## 13. Future Enhancements

While not included in the initial version, the following enhancements may be considered for future releases:

- Support for additional editors (VSCodium, Cursor)
- Multiple output formats (HTML, PDF, CSV)
- Local caching to avoid redundant scans
- Integration with CI/CD pipelines
- Severity-based filtering
- Scheduled scanning with notifications
- Extension update recommendations
- Comparison reports (before/after updates)

---

## 14. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| vscan.dev API changes break tool | High | Medium | Implement robust error handling; version-check responses; provide clear error messages |
| Rate limiting blocks scans | Medium | High | Implement configurable delays; respect HTTP 429 responses; provide retry logic |
| vscan.dev service outage | High | Low | Graceful error handling; clear user communication; suggest retry later |
| Extension not found on vscan.dev | Low | Medium | Warn user but continue scan; document in JSON output |
| Malformed extension data | Low | Low | Validate extension metadata; skip corrupted extensions with warning |
| Cross-platform path issues | Medium | Low | Use pathlib for cross-platform compatibility; test on all OSes |

---

## 15. Success Metrics

### 15.1 Functional Metrics
- Successfully detects VS Code installation on 100% of supported platforms
- Scans 100% of readable, well-formed extensions
- Generates valid JSON output for 100% of scans
- Proper exit codes returned for 100% of executions

### 15.2 Performance Metrics
- Scan completion time < 3 minutes for 50 extensions (with 2s delay)
- Memory usage < 100MB during execution
- Zero crashes or unhandled exceptions

### 15.3 User Experience Metrics
- Clear error messages for 100% of error scenarios
- Progress indicators visible during scan
- Help documentation comprehensive and accurate

---

## 16. Timeline & Milestones

### Phase 1: Research & Discovery (Week 1)
- [ ] Reverse-engineer vscan.dev API endpoints
- [ ] Document request/response format
- [ ] Validate endpoint behavior with test extensions

### Phase 2: Core Implementation (Week 2)
- [ ] Implement extension discovery for all platforms
- [ ] Implement vscan.dev API integration
- [ ] Implement JSON output generation
- [ ] Implement error handling and logging

### Phase 3: Testing & Refinement (Week 3)
- [ ] Test on macOS, Windows, Linux
- [ ] Test with various extension sets
- [ ] Test error scenarios
- [ ] Refine user experience (progress, messages)

### Phase 4: Documentation & Release (Week 4)
- [ ] Write comprehensive README
- [ ] Document usage examples
- [ ] Create troubleshooting guide
- [ ] Release v1.0

---

## 17. Appendix

### 17.1 Glossary
- **Extension ID:** Unique identifier for VS Code extension (format: `publisher.extension-name`)
- **vscan.dev:** Web-based security analysis service for VS Code extensions
- **Rate Limiting:** Restriction on number of API requests within a time period
- **Throttling:** Intentional delay between requests to avoid rate limiting

### 17.2 References
- [vscan.dev](https://vscan.dev) - VS Code Extension Security Analyzer
- [VS Code Extension API](https://code.visualstudio.com/api) - Official VS Code documentation
- [VS Code Extension Marketplace](https://marketplace.visualstudio.com/vscode)

### 17.3 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-22 | Initial | Initial PRD creation based on stakeholder requirements |

---

## 18. Approval

**Stakeholders:**
- Product Owner: _[Pending]_
- Engineering Lead: _[Pending]_
- Security Team: _[Pending]_

**Approval Date:** _[Pending]_
