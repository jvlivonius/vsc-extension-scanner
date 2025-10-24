# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

VS Code Extension Security Scanner is a standalone Python CLI tool that performs manual security audits of installed VS Code extensions by leveraging the vscan.dev security analysis service. The tool automates discovery of installed extensions, queries vscan.dev for security information, and generates JSON reports of findings.

**Current Status:** Phase 5 Complete - CLI UX Enhancement (v3.0.0)

**Latest Updates (CLI UX Enhancement - 2025-10-24):**
- ✅ **Rich Terminal Formatting** - Beautiful, modern CLI output
  - Live progress bars showing real-time scan status
  - Rich formatted tables for results and statistics
  - Color-coded risk levels and status indicators
  - Graceful fallback to plain output when Rich unavailable
- ✅ **Typer CLI Framework** - Modern command-line interface
  - Organized subcommands: `scan`, `cache-stats`, `cache-clear`
  - Help panels grouped by category (Basic, Output, Filtering, Advanced, Cache)
  - Comprehensive examples in help text
  - Parameter validation with clear error messages
- ✅ **Refactored Architecture** - Clean separation of concerns
  - `display.py` - Rich formatting components (24 tests passing)
  - `scanner.py` - Core scan logic (15 tests passing)
  - `cli.py` - Typer CLI framework (18 tests passing)
  - Total: 57 new tests, all passing
- ✅ **Backward Compatibility** - No breaking changes for programmatic usage
  - Old `main()` function still available
  - `--plain` flag provides v2.x style output
  - Same exit codes (0=clean, 1=vulns, 2=error)
  - JSON/HTML output formats unchanged (schema still 2.0)

**Previous Updates (Version Management - 2025-10-24):**
- ✅ **Centralized Version Management** - Single source of truth for version numbers
  - Created `vscode_scanner/_version.py` as single source of truth
  - All modules now import from `_version.py` (no hardcoded versions)
  - Dynamic versioning in `setup.py` and `pyproject.toml`
  - Created `scripts/bump_version.py` for easy version management
  - Separated app version (2.2.1) from schema version (2.0)
- ✅ **Improved Output UX** - Human-readable output by default
  - Console output is now always human-readable summary
  - JSON output only saved to file when `--output` is specified
  - No more JSON dumped to console by default
  - Cleaner, more user-friendly CLI experience
- ✅ **Enhanced Filter Feedback** - Helpful messages when filters match nothing
  - Shows which filters are active when 0 extensions match
  - Displays count of extensions filtered out
  - Provides tips for troubleshooting filter issues
  - Example: "Tip: Publisher names are case-insensitive but must match exactly"

**Previous Updates (Cross-Platform Compatibility - 2025-10-24):**
- ✅ **Windows Compatibility** (NEW!) - Fixed critical import issues
  - Fixed package import statement for HTML report generator
  - Windows pip installation now works correctly
  - Verified on macOS, ready for Windows testing
- ✅ **Cross-Platform Path Security** (NEW!) - Platform-aware security checks
  - Blocks Windows system paths (C:\Windows, C:\Program Files, etc.)
  - Blocks Unix/Linux system paths (/etc, /sys, /var, etc.)
  - Allows legitimate temp directories on all platforms
  - 100% backward compatible with existing functionality
- ✅ **Safe File Permissions** (NEW!) - Unix/Windows permission handling
  - Graceful fallback on Windows (ignores Unix permissions)
  - Maintains security on Unix/macOS platforms
  - No crashes or errors on any platform
- ✅ **Explicit UTF-8 Encoding** - Consistent encoding across platforms
  - All file operations use explicit UTF-8 encoding
  - Handles international characters correctly
  - Prevents encoding errors on Windows
- ✅ **All Tests Passing** - 35/35 functional tests verified

**Previous Updates (Phase 3 Improvements - 2025-10-23):**
- ✅ **Database Integrity Checks** - Automatic corruption detection and recovery
  - PRAGMA integrity_check on database initialization
  - Automatic backup of corrupted databases with timestamps
  - Fresh database creation on corruption detection
  - Comprehensive test suite (3 tests)
- ✅ **Integration Tests** - Comprehensive workflow testing
  - 7 test suites covering all major workflows
  - Mock vscan.dev API for reliable testing
  - Full coverage: discovery, scanning, caching, output, errors
  - 100% test pass rate

**Previous Updates (v2.2 - 2025-10-23):**
- ✅ **HTML Report Generation** (NEW!) - Interactive, self-contained HTML reports
  - Auto-detected from `.html` file extension in `--output` flag
  - Includes sortable tables, risk filters, search, and expandable details
  - Data visualizations with pie charts, gauges, and bar charts
  - Print-optimized with embedded CSS/JS (no external dependencies)
- ✅ Implemented intelligent retry mechanism for transient API errors
- ✅ Exponential backoff with jitter (2s, 4s, 8s delays)
- ✅ Retry-After header support for rate limiting compliance
- ✅ Configurable retry attempts and delays (--max-retries, --retry-delay)
- ✅ Retry statistics tracking and reporting
- ✅ Verbose mode logging for retry attempts
- ✅ Comprehensive documentation and test suite

**Previous Updates (v2.1 - 2025-10-23):**
- ✅ Refactored security functions to eliminate unused code
- ✅ All error messages now sanitized to prevent information disclosure
- ✅ Test files organized in dedicated `tests/` directory
- ✅ Added `.gitignore` for Python artifacts and cache files

See **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** for detailed progress tracking.
See **[docs/security/SECURITY_FIXES_APPLIED.md](docs/security/SECURITY_FIXES_APPLIED.md)** for security improvements.

## Quick Reference Documentation

### Core Documentation
- **[README.md](README.md)** - Project overview and quick start
- **[docs/design/PRD.md](docs/design/PRD.md)** - Full product requirements
- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** - Current project status

### Phase Requirements
- **[docs/phases/PHASE1_REQUIREMENTS.md](docs/phases/PHASE1_REQUIREMENTS.md)** - Phase 1: Research & Discovery
- **[docs/phases/PHASE2_REQUIREMENTS.md](docs/phases/PHASE2_REQUIREMENTS.md)** - Phase 2: Core Implementation
- **[docs/phases/PHASE3_REQUIREMENTS.md](docs/phases/PHASE3_REQUIREMENTS.md)** - Phase 3: Testing & Refinement
- **[docs/phases/PHASE4_REQUIREMENTS.md](docs/phases/PHASE4_REQUIREMENTS.md)** - Phase 4: Enhanced Data Integration

### Features
- **[docs/features/IMPROVEMENT_PLAN.md](docs/features/IMPROVEMENT_PLAN.md)** - Phase 3 improvements plan
- **[docs/features/HTML_REPORT_SPECIFICATION.md](docs/features/HTML_REPORT_SPECIFICATION.md)** - HTML report feature spec (v2.2)
- **[docs/features/RETRY_MECHANISM.md](docs/features/RETRY_MECHANISM.md)** - Retry mechanism documentation (v2.2)

### Research & Testing
- **[docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)** - vscan.dev API documentation
- **[docs/testing/TESTING_CHECKLIST.md](docs/testing/TESTING_CHECKLIST.md)** - Testing checklist
- **[docs/testing/MACOS_TESTING.md](docs/testing/MACOS_TESTING.md)** - macOS test plan

### Results & Security
- **[docs/results/](docs/results/)** - Phase completion summaries and test results
- **[docs/security/](docs/security/)** - Security analysis and fixes

## Technology Stack

- **Language:** Python 3.8+
- **HTTP Library:** `urllib.request` (standard library)
- **Database:** SQLite3 (standard library, for caching)
- **CLI Framework:** Typer ≥0.9.0 (modern CLI with Rich support)
- **Terminal Formatting:** Rich ≥13.0.0 (progress bars, tables, panels)
- **Distribution:** Python package (pip installable)
- **Output Format:** JSON and HTML (self-contained with embedded CSS/JS)

## Project Structure

**Single Source Architecture** - All code exists in `vscode_scanner/` package only:

```
vsc-extension-scanner/
├── vscode_scanner/          # Main package (single source of truth)
│   ├── __init__.py
│   ├── _version.py         # Version management
│   ├── cli.py              # Typer CLI framework (NEW v3.0)
│   ├── scanner.py          # Core scan logic (NEW v3.0)
│   ├── display.py          # Rich formatting (NEW v3.0)
│   ├── vscan.py            # Entry point wrapper
│   ├── vscan_api.py        # API client
│   ├── cache_manager.py    # Caching
│   ├── extension_discovery.py
│   ├── output_formatter.py
│   ├── html_report_generator.py
│   └── utils.py
├── scripts/
│   └── bump_version.py     # Version management tool
├── tests/                  # Test files (57 tests total)
│   ├── test_display.py     # Display module tests (24 tests)
│   ├── test_scanner.py     # Scanner module tests (15 tests)
│   ├── test_cli.py         # CLI module tests (18 tests)
│   └── ...                 # Legacy test files
├── docs/                   # Documentation
├── vscan                   # Convenience wrapper for development
├── setup.py                # Build configuration
├── pyproject.toml          # Modern Python packaging
└── MANIFEST.in             # Distribution rules
```

**Development Workflow:**
- Edit files in `vscode_scanner/` directory (single source)
- Run locally: `./vscan` or `python -m vscode_scanner.vscan`
- Build distribution: `python -m build`
- No duplicate files, no synchronization issues

## Development Commands

```bash
# Testing (v3.0)
python3 tests/test_display.py      # Display module tests (24 tests)
python3 tests/test_scanner.py      # Scanner module tests (15 tests)
python3 tests/test_cli.py          # CLI module tests (18 tests)
python3 tests/test_api.py          # API validation tests
python3 tests/test_retry.py        # Retry mechanism tests
python3 tests/test_security.py     # Security vulnerability tests
python3 tests/test_db_integrity.py # Database integrity tests
python3 tests/test_integration.py  # Integration tests

# Run the tool (v3.0 CLI with subcommands)
vscan                                         # Show help
vscan scan                                    # Standard scan with Rich UI
vscan scan --plain                            # Plain output (v2.x style)
vscan scan --quiet                            # Minimal output
vscan scan --verbose                          # Detailed progress

# Scan options
vscan scan --output results.json              # Save JSON to file
vscan scan --output report.html               # Generate HTML report
vscan scan --detailed                         # Include full security analysis
vscan scan --extensions-dir /path             # Custom directory

# Filtering options
vscan scan --publisher microsoft              # Only scan Microsoft extensions
vscan scan --min-risk-level high              # Only show high/critical risk
vscan scan --include-ids "ms-python.python"   # Scan specific extensions
vscan scan --exclude-ids "local.test"         # Exclude specific extensions

# Retry configuration
vscan scan --max-retries 5                    # More aggressive retries
vscan scan --retry-delay 3.0                  # Longer backoff delays
vscan scan --max-retries 0                    # Disable retries (fail fast)

# Cache options
vscan scan --no-cache                         # Disable caching
vscan scan --refresh-cache                    # Force refresh
vscan scan --cache-max-age 14                 # 14-day cache expiry
vscan scan --cache-dir /custom/path           # Custom cache location

# Cache management commands (v3.0 subcommands)
vscan cache-stats                             # Show cache statistics
vscan cache-stats --cache-max-age 14          # Check for stale entries
vscan cache-clear                             # Clear all cache (with confirmation)
vscan cache-clear --force                     # Clear without confirmation

# Help
vscan --help                                  # Main help with subcommands
vscan scan --help                             # Scan command help (organized panels)
vscan cache-stats --help                      # Cache stats help
vscan cache-clear --help                      # Cache clear help
vscan --version                               # Show version

# Development
python -m vscode_scanner.vscan                # Run via Python module
./vscan                                       # Convenience wrapper
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
| `--max-retries` | - | int | Maximum retry attempts for failed requests | 3 |
| `--retry-delay` | - | float | Base delay for exponential backoff (seconds) | 2.0 |
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
- ~~HTML report generation~~ ✅ **IMPLEMENTED in v2.2**
- PDF report generation
- Historical vulnerability tracking
- Extension installation/removal functionality
- GUI interface
- Auto-remediation of vulnerabilities

## Implementation Phases

### ✅ Phase 1: Research & Discovery (COMPLETE)

**Requirements:** [docs/phases/PHASE1_REQUIREMENTS.md](docs/phases/PHASE1_REQUIREMENTS.md)

- Reverse-engineer vscan.dev API endpoints
- Document request/response format
- Validate endpoint behavior with test extensions

**Results:** [docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)

### ✅ Phase 2: Core Implementation (COMPLETE)

**Requirements:** [docs/phases/PHASE2_REQUIREMENTS.md](docs/phases/PHASE2_REQUIREMENTS.md)

**Module Structure:**

```
vscan.py                     # Main CLI entry point (370 lines)
  ├── extension_discovery.py # Find and parse extensions (180 lines)
  ├── vscan_api.py           # vscan.dev API client (320 lines)
  ├── output_formatter.py    # Generate JSON output (180 lines)
  ├── html_report_generator.py # Generate HTML reports (2,300 lines) [NEW]
  ├── cache_manager.py       # SQLite caching system (360 lines)
  └── utils.py               # Shared utilities (180 lines)
```

**Implemented Features:**

✅ Extension discovery for all platforms (macOS, Windows, Linux)
✅ vscan.dev API integration with progress callbacks
✅ JSON output generation matching PRD specification
✅ **HTML report generation** (interactive, self-contained reports) [NEW]
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

**Requirements:** [docs/phases/PHASE3_REQUIREMENTS.md](docs/phases/PHASE3_REQUIREMENTS.md)

- Test caching system thoroughly
- Test on macOS (focused platform)
- Test with various extension sets (3, 66 extensions)
- Test error scenarios (rate limiting)
- Refine user experience (fixed cache-stats UX bug)

**Results:** [docs/testing/MACOS_TEST_RESULTS.md](docs/testing/MACOS_TEST_RESULTS.md) | [docs/results/PHASE3_COMPLETION_SUMMARY.md](docs/results/PHASE3_COMPLETION_SUMMARY.md)

### ✅ Phase 4: Enhanced Data Integration (COMPLETE)

**Requirements:** [docs/phases/PHASE4_REQUIREMENTS.md](docs/phases/PHASE4_REQUIREMENTS.md)

**Implemented Features:**

✅ Complete vscan.dev data capture (all fields)
✅ Dual-mode JSON output (standard/detailed)
✅ Publisher verification and reputation tracking
✅ Comprehensive dependency analysis
✅ Security score breakdown by module
✅ Risk factor identification and reporting
✅ Cache schema v2.0 with automatic v1→v2 migration
✅ Maintained performance (28x speedup with cache)

**Results:** [docs/design/ENHANCED_DATA_INTEGRATION_PLAN.md](docs/design/ENHANCED_DATA_INTEGRATION_PLAN.md) | [docs/results/PHASE4_COMPLETION_SUMMARY.md](docs/results/PHASE4_COMPLETION_SUMMARY.md)

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
- **[docs/features/RETRY_MECHANISM.md](docs/features/RETRY_MECHANISM.md)** - Retry mechanism documentation (v2.2)

---

**For detailed requirements, implementation guidance, and test plans, see the documentation in the `docs/` directory.**
