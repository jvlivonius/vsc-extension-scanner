# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

VS Code Extension Security Scanner is a standalone Python CLI tool that performs manual security audits of installed VS Code extensions by leveraging the vscan.dev security analysis service. The tool automates discovery of installed extensions, queries vscan.dev for security information, and generates JSON reports of findings.

**Current Status:** Phase 4 Complete (v2.0 - Enhanced Data Integration)

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
- **Database:** SQLite3 (standard library, for caching)
- **CLI Parsing:** `argparse` (standard library)
- **Distribution:** Standalone `.py` script (no installation required)
- **Output Format:** JSON

## Development Commands

```bash
# Phase 1: API Validation (complete)
python3 test_api.py

# Phase 2+: Run the tool (v2.0 implemented)
python vscan.py                          # Standard scan
python vscan.py --detailed               # Detailed scan with full data
python vscan.py --extensions-dir /path   # Custom directory
python vscan.py --output results.json    # Save to file
python vscan.py --verbose                # Detailed progress
python vscan.py --delay 2.0              # Custom delay

# Cache management
python vscan.py --cache-stats            # Show cache statistics
python vscan.py --clear-cache            # Clear all cache
python vscan.py --refresh-cache          # Force refresh
python vscan.py --no-cache               # Disable cache
python vscan.py --cache-max-age 14       # 14-day cache expiry
python vscan.py --cache-dir /custom/path # Custom cache location

# Help
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

### JSON Output Schema (v2.0)

**Standard Mode (default):**
```json
{
  "schema_version": "2.0",
  "output_mode": "standard",
  "summary": {
    "total_extensions_scanned": 42,
    "vulnerabilities_found": 3,
    "scan_timestamp": "2025-10-23T14:30:00Z",
    "scan_duration_seconds": 95.5
  },
  "cache_stats": {
    "from_cache": 30,
    "fresh_scans": 12,
    "cache_hit_rate": 71.4
  },
  "extensions": [
    {
      "name": "python",
      "display_name": "Python",
      "id": "ms-python.python",
      "version": "2024.10.0",
      "publisher": "ms-python",
      "publisher_verified": true,
      "security_score": 82,
      "risk_level": "high",
      "vulnerabilities": {
        "count": 0,
        "critical": 0,
        "high": 0,
        "moderate": 0,
        "low": 0
      },
      "dependencies_count": 45,
      "risk_factors_count": 3,
      "last_updated": "2024-10-15",
      "vscan_url": "https://vscan.dev/extension/ms-python.python",
      "scan_status": "success"
    }
  ]
}
```

**Detailed Mode (--detailed flag):**
```json
{
  "schema_version": "2.0",
  "output_mode": "detailed",
  "summary": { /* same as standard */ },
  "cache_stats": { /* same as standard */ },
  "extensions": [
    {
      /* All standard fields, plus: */
      "description": "IntelliSense, linting, debugging...",
      "publisher_domain": "microsoft.com",
      "publisher_reputation": 100,
      "install_count": 50000000,
      "rating": 4.5,
      "rating_count": 1234,
      "dependencies": [
        {
          "name": "vscode-languageclient",
          "version": "8.1.0",
          "risk_level": "low",
          "has_vulnerabilities": false
        }
      ],
      "security_score_breakdown": {
        "code_quality": 85,
        "dependencies": 90,
        "permissions": 75,
        "network_usage": 80
      },
      "risk_factors": [
        {
          "type": "network_access",
          "severity": "medium",
          "description": "Extension makes network requests"
        }
      ],
      "keywords": ["python", "intellisense", "linting"],
      "repository_url": "https://github.com/microsoft/vscode-python",
      "homepage_url": "https://github.com/microsoft/vscode-python"
    }
  ]
}
```

**Field Details:**

- `schema_version`: "2.0" (for v2.0 output format)
- `output_mode`: "standard" or "detailed"
- `scan_status` values: `"success"`, `"not_found"`, `"error"`
- Include error message for failed scans
- All vscan.dev requests must use HTTPS
- Output to stdout by default, support `--output` for file output

### Caching System

To improve performance for repeated scans, vscan uses an SQLite-based caching system:

**Cache Behavior:**
- Automatically caches successful scan results
- Cache key: extension ID + version
- Default expiration: 7 days (configurable)
- Failed scans are NOT cached (always retry)
- Version changes invalidate cache

**Cache Location:**
- Default: `~/.vscan/cache.db`
- Configurable via `--cache-dir`

**Performance Impact:**
- Cached results: ~instant (50x faster)
- Fresh scans: 5-15 seconds per extension

**Cache Management:**
```bash
python vscan.py --cache-stats      # View statistics
python vscan.py --clear-cache      # Clear all entries
python vscan.py --refresh-cache    # Force refresh all
python vscan.py --no-cache         # Disable caching
python vscan.py --cache-max-age 14 # Custom expiry (days)
```

### Progress Indicators

Display progress to stderr (not stdout, which is reserved for JSON output):

```
Detecting VS Code installation...
Found VS Code extensions directory: /home/user/.vscode/extensions
Discovered 42 extensions

Scanning extensions for vulnerabilities...
Cache enabled (max age: 7 days)
[1/42] ms-python.python v2024.10.0... ⚡ Cached ✓
[2/42] Scanning esbenp.prettier-vscode v10.1.0... 🔍 ✓
[3/42] Scanning dbaeumer.vscode-eslint v2.4.2... 🔍 ⚠ Vulnerabilities found
...

Scan complete!
Total extensions scanned: 42
Successful scans: 42
Failed scans: 0

Cache Statistics:
  From cache: 30 (⚡ instant)
  Fresh scans: 12 (🔍 API calls)
  Cache hit rate: 71.4%

Vulnerabilities found: 3
Scan duration: 25.3 seconds
Average time per extension: 0.6s
```

**Symbols:**
- ⚡ = Cached result (instant)
- 🔍 = Fresh API scan
- ✓ = Success, no vulnerabilities
- ⚠ = Vulnerabilities found
- ✗ = Error

## Command-Line Interface

### Arguments

| Argument | Short | Type | Description | Default |
|----------|-------|------|-------------|---------|
| `--extensions-dir` | `-d` | path | VS Code extensions directory | Auto-detected |
| `--output` | `-o` | path | Output file path (JSON) | stdout |
| `--delay` | `-t` | float | Delay between requests (seconds) | 1.5 |
| `--verbose` | `-v` | flag | Enable verbose output | False |
| `--cache-dir` | - | path | Cache directory path | `~/.vscan/` |
| `--cache-max-age` | - | int | Max age of cached results (days) | 7 |
| `--refresh-cache` | - | flag | Force refresh all cached results | False |
| `--no-cache` | - | flag | Disable cache (always scan fresh) | False |
| `--clear-cache` | - | flag | Clear all cached results and exit | False |
| `--cache-stats` | - | flag | Show cache statistics and exit | False |
| `--detailed` | - | flag | Include detailed security analysis | False |
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
- Extension installation/removal functionality
- GUI interface
- Auto-remediation of vulnerabilities

## Implementation Phases

### ✅ Phase 1: Research & Discovery (COMPLETE)

- Reverse-engineer vscan.dev API endpoints
- Document request/response format
- Validate endpoint behavior with test extensions

**Status:** Complete. See [docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)

### ✅ Phase 2: Core Implementation (COMPLETE)

**Module Structure:**

```
vscan.py                     # Main CLI entry point (370 lines)
  ├── extension_discovery.py # Find and parse extensions (180 lines)
  ├── vscan_api.py           # vscan.dev API client (320 lines)
  ├── output_formatter.py    # Generate JSON output (180 lines)
  ├── cache_manager.py       # SQLite caching system (360 lines)
  └── utils.py               # Shared utilities (180 lines)
```

**Implemented Features:**

✅ Extension discovery for all platforms (macOS, Windows, Linux)
✅ vscan.dev API integration with progress callbacks
✅ JSON output generation matching PRD specification
✅ Error handling and logging system
✅ Progress indicators with visual symbols
✅ CLI argument parsing with 12+ arguments
✅ **SQLite-based caching system**
✅ **Cache management commands** (stats, clear, refresh)
✅ **Performance optimization** (50x faster for cached results)

**Reference Implementation:**

- Built vscan_api.py using [test_api.py](test_api.py) as foundation
- Implements analyze → poll status → retrieve results workflow
- Added caching layer for performance optimization

### ✅ Phase 3: Testing & Refinement (COMPLETE)

- Test caching system thoroughly
- Test on macOS (focused platform)
- Test with various extension sets (3, 66 extensions)
- Test error scenarios (rate limiting)
- Refine user experience (fixed cache-stats UX bug)

**Status:** Complete. See [docs/testing/MACOS_TEST_RESULTS.md](docs/testing/MACOS_TEST_RESULTS.md)

### ✅ Phase 4: Enhanced Data Integration (COMPLETE)

**Implemented Features:**

✅ Complete vscan.dev data capture (all fields)
✅ Dual-mode JSON output (standard/detailed)
✅ Publisher verification and reputation tracking
✅ Comprehensive dependency analysis
✅ Security score breakdown by module
✅ Risk factor identification and reporting
✅ Cache schema v2.0 with automatic v1→v2 migration
✅ Maintained performance (28x speedup with cache)

**Reference Documentation:**

- Implementation plan: [docs/design/ENHANCED_DATA_INTEGRATION_PLAN.md](docs/design/ENHANCED_DATA_INTEGRATION_PLAN.md)
- Phase 4 summary: [docs/PHASE4_COMPLETION_SUMMARY.md](docs/PHASE4_COMPLETION_SUMMARY.md)

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
