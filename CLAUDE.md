# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

VS Code Extension Security Scanner is a standalone Python CLI tool that performs manual security audits of installed VS Code extensions by leveraging the vscan.dev security analysis service. The tool automates discovery of installed extensions, queries vscan.dev for security information, and generates JSON reports of findings.

**Current Status:** Phase 1 Complete (API Research & Validation)

See **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** for detailed progress tracking.

## Quick Reference Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[docs/design/PRD.md](docs/design/PRD.md)** - Full product requirements
- **[docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)** - vscan.dev API documentation
- **[docs/testing/TESTING_CHECKLIST.md](docs/testing/TESTING_CHECKLIST.md)** - Phase 3 test plan
- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** - Current project status

## Technology Stack

- **Language:** Python 3.8+
- **HTTP Library:** `urllib.request` (standard library, no external dependencies)
- **CLI Parsing:** `argparse` (standard library)
- **Distribution:** Standalone `.py` script (no installation required)
- **Output Format:** JSON

## Development Commands

```bash
# Phase 1: API Validation (complete)
python3 test_api.py

# Phase 2: Run the tool (once implemented)
python vscan.py
python vscan.py --extensions-dir /path/to/extensions
python vscan.py --output results.json
python vscan.py --verbose
python vscan.py --delay 2.0
python vscan.py --help
```

## Architecture Overview

### Extension Discovery
- **Auto-detect** VS Code extensions directory by platform:
  - macOS: `~/.vscode/extensions/`
  - Windows: `%USERPROFILE%\.vscode\extensions\`
  - Linux: `~/.vscode/extensions/`
- **Parse** extension metadata from `package.json` files
- **Support** custom paths via `--extensions-dir` argument
- **Use** `pathlib` for cross-platform path handling

### vscan.dev Integration

The vscan.dev API has been fully reverse-engineered and validated in Phase 1.

**API Workflow:**

1. **Submit** extension for analysis: `POST /api/extensions/analyze`
2. **Poll** status until complete: `GET /api/extensions/status/{analysisId}`
3. **Retrieve** results: `GET /api/extensions/results/{analysisId}`

**Key Implementation Details:**

- Asynchronous analysis with polling
- Popular extensions are cached (instant results)
- No authentication required
- Default 1.5s delay between requests
- Poll status every 2 seconds
- Maximum wait: 5 minutes per extension

**Complete API documentation:** [docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)

### Error Handling Strategy

**Exit Codes:**

- **0:** Scan completed successfully, no vulnerabilities found
- **1:** Scan completed successfully, vulnerabilities found
- **2:** Scan failed due to errors

**Error Handling Rules:**

- Warn (don't fail) for malformed/corrupted extension installations
- Continue scanning remaining extensions if individual queries fail
- Validate JSON responses before processing
- 30-second timeout per HTTP request
- Clear, actionable error messages for common scenarios

### JSON Output Schema

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
      "security_score": 82,
      "risk_level": "medium",
      "vulnerabilities": {
        "count": 0,
        "critical": 0,
        "high": 0,
        "moderate": 0,
        "low": 0,
        "info": 0
      },
      "last_updated": "2025-10-15",
      "vscan_url": "https://vscan.dev/extension/publisher.extension-name",
      "scan_status": "success"
    }
  ]
}
```

**Field Details:**

- `scan_status` values: `"success"`, `"not_found"`, `"error"`
- Include error message for failed scans
- All vscan.dev requests must use HTTPS
- Output to stdout by default, support `--output` for file output

### Progress Indicators

Display progress to stderr (not stdout, which is reserved for JSON output):

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

### Arguments

| Argument | Short | Type | Description | Default |
|----------|-------|------|-------------|---------|
| `--extensions-dir` | `-d` | path | VS Code extensions directory | Auto-detected |
| `--output` | `-o` | path | Output file path (JSON) | stdout |
| `--delay` | `-t` | float | Delay between requests (seconds) | 1.5 |
| `--verbose` | `-v` | flag | Enable verbose output | False |
| `--help` | `-h` | flag | Show help message | - |
| `--version` | `-V` | flag | Show version information | - |

## Performance Requirements

- **Target:** < 2 minutes for 50 extensions (with 1.5s delay between requests)
- **Memory:** < 100MB RAM usage
- **File I/O:** Minimize operations, only read package.json files
- **Processing:** Extensions scanned sequentially with proper throttling

## Security Considerations

- All requests to vscan.dev must use **HTTPS**
- Never store or transmit user credentials or sensitive data
- Respect vscan.dev's rate limits to avoid being blocked
- Validate all input paths to prevent directory traversal
- Sanitize extension metadata before including in output

## Out of Scope (Do Not Implement)

The following features are explicitly **out of scope**:

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

### ✅ Phase 1: Research & Discovery (COMPLETE)

- Reverse-engineer vscan.dev API endpoints
- Document request/response format
- Validate endpoint behavior with test extensions

**Status:** Complete. See [docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)

### ⏳ Phase 2: Core Implementation (NEXT)

**Module Structure:**

```
vscan.py                  # Main CLI entry point
  ├── vscan_api.py       # vscan.dev API client
  ├── extension_discovery.py  # Find and parse extensions
  ├── output_formatter.py     # Generate JSON output
  └── utils.py                # Shared utilities
```

**Implementation Order:**

1. Extension discovery (find extensions, parse package.json)
2. API integration (reuse code from test_api.py)
3. JSON output generation
4. Error handling and logging
5. Progress indicators
6. CLI argument parsing

**Reference Implementation:**

- Use [test_api.py](test_api.py) as the foundation for vscan_api.py
- Implement same workflow: analyze → poll status → retrieve results
- Reuse request handling, polling logic, and result parsing

### ⏳ Phase 3: Testing & Refinement

- Test on macOS, Windows, Linux
- Test with various extension sets
- Test error scenarios
- Refine user experience

**Complete test plan:** [docs/testing/TESTING_CHECKLIST.md](docs/testing/TESTING_CHECKLIST.md)

## vscan.dev API Quick Reference

**Validated Endpoints:**

```python
# 1. Submit extension for analysis
POST https://vscan.dev/api/extensions/analyze
Body: {"publisher": "ms-python", "name": "python"}
Response: {"analysisId": "uuid", "status": "pending"}

# 2. Check analysis status
GET https://vscan.dev/api/extensions/status/{analysisId}
Response: {"status": "completed", "progress": 100}

# 3. Retrieve results
GET https://vscan.dev/api/extensions/results/{analysisId}
Response: {comprehensive security analysis}
```

**Key Response Fields:**

```python
response["securityScore"]["score"]      # 0-100
response["securityScore"]["riskLevel"]  # "low", "medium", "high"
response["analysisModules"]["dependencies"]["vulnerabilities"]["summary"]
# {"critical": 0, "high": 0, "moderate": 0, "low": 0, "total": 0}
```

**Complete API documentation with examples:** [docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)

## Testing Strategy

### Phase 1 ✅

- Validated API endpoints with [test_api.py](test_api.py)
- Tested with 3 popular extensions
- 100% success rate

### Phase 2

- Unit tests for each module
- Integration tests for end-to-end workflow
- Manual testing on current platform

### Phase 3

- Cross-platform testing (macOS, Windows, Linux)
- Edge case testing (see checklist)
- Performance benchmarking
- User acceptance testing

**Full checklist:** [docs/testing/TESTING_CHECKLIST.md](docs/testing/TESTING_CHECKLIST.md)

## Common Development Tasks

### Running Tests

```bash
# API validation (Phase 1)
python3 test_api.py

# Main tool (Phase 2+)
python vscan.py --verbose

# Unit tests (Phase 3)
pytest tests/
```

### Adding New Features

1. Check if feature is in scope (see PRD)
2. Update relevant documentation
3. Implement with error handling
4. Add tests
5. Update CHANGELOG (when created)

### Debugging

```bash
# Verbose mode shows detailed progress
python vscan.py --verbose

# Test with single extension
python vscan.py --extensions-dir ~/.vscode/extensions/ms-python.python-*

# Check API behavior
python3 test_api.py
```

## References

- **[vscan.dev](https://vscan.dev)** - VS Code Extension Security Analyzer
- **[VS Code Extension API](https://code.visualstudio.com/api)** - Extension API docs
- **[docs/design/PRD.md](docs/design/PRD.md)** - Full product requirements
- **[docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)** - API research findings

---

**For detailed requirements, implementation guidance, and test plans, see the documentation in the `docs/` directory.**
