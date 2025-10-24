# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## ⚠️ REQUIRED READING BEFORE CODE CHANGES

**STOP!** Before making any code changes, you **MUST** read these three documents:

1. **[docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)** - System architecture, design principles, module responsibilities, and anti-patterns
2. **[docs/guides/SECURITY.md](docs/guides/SECURITY.md)** - Security requirements, path validation, input sanitization, and threat model
3. **[docs/project/PRD.md](docs/project/PRD.md)** - Product requirements, feature scope, and constraints

These documents define critical constraints and requirements that must be followed. See the "Required Reading Documentation" section below for additional important documentation.

---

## Project Overview

VS Code Extension Security Scanner is a standalone Python CLI tool that performs manual security audits of installed VS Code extensions by leveraging the vscan.dev security analysis service. The tool automates discovery of installed extensions, queries vscan.dev for security information, and generates JSON reports of findings.

**Current Status:** v3.2 Code Quality Improvements (v3.2.0)

**Latest Updates (v3.2 - Code Quality & Reliability - 2025-10-24):**
- ✅ **Critical Bug Fix** - Database connection leak in batch mode
  - Added `_cleanup_batch_on_error()` method for safe cleanup
  - Prevents resource leaks and database lock issues
  - Comprehensive test coverage added
- ✅ **Defensive Programming** - Division by zero safeguard
  - More robust cache hit rate calculation
  - Prevents edge case errors during refactoring
- ✅ **Code Simplification** - Rich/Typer are now required dependencies
  - Removed ~70 lines of conditional logic across 4 files
  - Removed RICH_AVAILABLE and TYPER_AVAILABLE flags completely
  - Removed cli_fallback() function
  - Simplified CLI entry point
  - --plain flag still supported for CI/CD
- ✅ **Pythonic Refactoring** - SimpleNamespace instead of empty class
  - Replaced ScanConfig empty class with Python's SimpleNamespace
  - More idiomatic Python code
  - Clearer intent

**Previous Updates (v3.1 - Configuration & CSV Export - 2025-10-24):**
- ✅ **Configuration File Support** - Persistent settings with ~/.vscanrc
  - INI format configuration file with three sections (scan, cache, output)
  - Five config management commands: init, show, set, get, reset
  - Inline comment support with # syntax
  - Type validation for all configuration values
  - Config values serve as defaults, CLI arguments always override
  - Single unified table display showing full keys (e.g., "scan.delay")
- ✅ **CSV Export Feature** - Spreadsheet-compatible output format
  - 15-column CSV schema for security analysis
  - Available via: `vscan scan --output results.csv`
  - Available via: `vscan report results.csv` (from cache, no API calls)
  - Proper CSV escaping for commas, quotes, newlines
  - UTF-8 encoding with cross-platform newline handling
  - HTML report CSV export removed (CLI-only for consistency)
- ✅ **Improved Config UX** - Clearer configuration display
  - Single table instead of separate section tables
  - Full key format (scan.delay) instead of just option names
  - Helpful usage examples in output
  - Clear indication of config vs default values
- ✅ **Performance Improvements** - Database optimization
  - Batch commit optimization (87.6% faster)
  - VACUUM after bulk deletes (73.9% space reclaimed)
  - Performance benchmark tests added
- ✅ **Code Quality** - Refactoring and error handling
  - Centralized constants module
  - Improved error codes and messages
  - Better exception handling patterns

**Previous Updates (CLI UX Enhancement v3.0 - 2025-10-24):**
- ✅ **Rich Terminal Formatting** - Beautiful, modern CLI output
  - Live progress bars showing real-time scan status
  - Rich formatted tables for results and statistics
  - Color-coded risk levels and status indicators
  - Graceful fallback to plain output when Rich unavailable
- ✅ **Typer CLI Framework** - Modern command-line interface
  - Organized subcommands: `scan`, `cache stats`, `cache clear`, `report`
  - Simplified help panels - all options in single "Options" panel
  - Comprehensive examples in help text
  - Parameter validation with clear error messages
- ✅ **Streamlined CLI Options** - Removed low-value flags
  - ❌ Removed `--verbose` (minimal impact, only added TimeElapsed column)
  - ❌ Removed `--detailed` (scans are always comprehensive now)
  - ✅ Fixed `--quiet` to show minimal single-line summary
  - ✅ Consolidated cache commands into `vscan cache` subcommands
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
- ✅ Comprehensive documentation and test suite

**Previous Updates (v2.1 - 2025-10-23):**
- ✅ Refactored security functions to eliminate unused code
- ✅ All error messages now sanitized to prevent information disclosure
- ✅ Test files organized in dedicated `tests/` directory
- ✅ Added `.gitignore` for Python artifacts and cache files

See **[docs/project/STATUS.md](docs/project/STATUS.md)** for detailed progress tracking.
See **[docs/guides/SECURITY.md](docs/guides/SECURITY.md)** for security requirements and best practices.

## Required Reading Documentation

**IMPORTANT:** When working on this project, you MUST review these documents first to understand the architecture, requirements, and constraints.

### 🔴 REQUIRED - Core Architecture & Requirements
These documents define the system architecture, security requirements, and design constraints. Read these FIRST before making any code changes:

1. **[docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)** ⚠️ REQUIRED
   - Simple Layered Architecture (Presentation, Application, Infrastructure)
   - Design principles (KISS, Command-Query Separation, Fail Fast)
   - Module responsibilities and dependency rules
   - Anti-patterns to avoid

2. **[docs/guides/SECURITY.md](docs/guides/SECURITY.md)** ⚠️ REQUIRED
   - Security architecture and defense layers
   - CRITICAL: Path validation requirements
   - Input validation and sanitization rules
   - Error handling and information disclosure prevention
   - Threat model and attack vectors

3. **[docs/project/PRD.md](docs/project/PRD.md)** ⚠️ REQUIRED
   - Complete product requirements (v3.1)
   - Feature scope and objectives
   - Technical specifications
   - Success criteria and constraints

### 🟡 IMPORTANT - Development Guidelines
Read these when making changes to specific areas:

4. **[docs/guides/ERROR_HANDLING.md](docs/guides/ERROR_HANDLING.md)** - Error handling strategy
   - ERROR_HELP system documentation
   - Error classification and display flow
   - Security-aware error messaging

5. **[docs/guides/TESTING.md](docs/guides/TESTING.md)** - Testing guidelines
   - Test organization and categories
   - Writing tests (AAA pattern, fixtures)
   - Test coverage goals (85% overall, 95% for security)

6. **[docs/guides/API_REFERENCE.md](docs/guides/API_REFERENCE.md)** - vscan.dev API documentation
   - API endpoints and request/response formats
   - Implementation recommendations
   - Edge cases and rate limiting

### 🟢 Reference - Project Status & Planning

- **[README.md](README.md)** - Project overview and quick start
- **[docs/project/STATUS.md](docs/project/STATUS.md)** - Current project status and progress
- **[docs/project/ROADMAP.md](docs/project/ROADMAP.md)** - Version 3.2 improvement plan
- **[docs/README.md](docs/README.md)** - Complete documentation index

### Feature Specifications
- **[docs/specs/html-reports.md](docs/specs/html-reports.md)** - HTML report feature (v2.2)
- **[docs/specs/retry-mechanism.md](docs/specs/retry-mechanism.md)** - Retry mechanism (v2.2)
- **[docs/specs/cli-ux.md](docs/specs/cli-ux.md)** - CLI UX enhancement (v3.0)

### Contributor Resources
- **[docs/contributing/TESTING_CHECKLIST.md](docs/contributing/TESTING_CHECKLIST.md)** - Testing checklist
- **[docs/contributing/VERSION_MANAGEMENT.md](docs/contributing/VERSION_MANAGEMENT.md)** - Version management guide
- **[docs/guides/ERROR_CODES.md](docs/guides/ERROR_CODES.md)** - Error code reference

### Historical Documentation (Archive)
- **[docs/archive/phases/](docs/archive/phases/)** - Completed phase requirements
- **[docs/archive/releases/](docs/archive/releases/)** - Phase completion summaries
- **[docs/archive/reviews/](docs/archive/reviews/)** - Historical reviews and analysis

## Technology Stack

- **Language:** Python 3.8+
- **HTTP Library:** `urllib.request` (standard library)
- **Database:** SQLite3 (standard library, for caching)
- **CLI Framework:** Typer ≥0.9.0 (modern CLI with Rich support)
- **Terminal Formatting:** Rich ≥13.0.0 (progress bars, tables, panels)
- **Distribution:** Python package (pip installable)
- **Output Format:** JSON, HTML (self-contained with embedded CSS/JS), and CSV
- **Configuration:** INI format config file at ~/.vscanrc

## Project Structure

**Single Source Architecture** - All code exists in `vscode_scanner/` package only:

```
vsc-extension-scanner/
├── vscode_scanner/          # Main package (single source of truth)
│   ├── __init__.py
│   ├── _version.py         # Version management
│   ├── cli.py              # Typer CLI framework (v3.0)
│   ├── scanner.py          # Core scan logic (v3.0)
│   ├── display.py          # Rich formatting (v3.0)
│   ├── config_manager.py   # Configuration file support (NEW v3.1)
│   ├── constants.py        # Centralized constants (NEW v3.1)
│   ├── vscan.py            # Entry point wrapper
│   ├── vscan_api.py        # API client
│   ├── cache_manager.py    # Caching
│   ├── extension_discovery.py
│   ├── output_formatter.py # Includes CSV export (v3.1)
│   ├── html_report_generator.py
│   └── utils.py
├── scripts/
│   └── bump_version.py     # Version management tool
├── tests/                  # Test files (57+ tests total)
│   ├── test_display.py     # Display module tests (24 tests)
│   ├── test_scanner.py     # Scanner module tests (15 tests)
│   ├── test_cli.py         # CLI module tests (18 tests)
│   ├── test_performance.py # Performance tests (NEW v3.1)
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

# Run the tool (v3.1 CLI with subcommands)
vscan                                         # Show help
vscan scan                                    # Standard scan with Rich UI (always comprehensive)
vscan scan --plain                            # Plain output (v2.x style)
vscan scan --quiet                            # Minimal single-line summary for CI/CD

# Scan options
vscan scan --output results.json              # Save JSON to file
vscan scan --output report.html               # Generate HTML report
vscan scan --output results.csv               # Export to CSV (NEW v3.1)
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
vscan cache stats                             # Show cache statistics
vscan cache stats --cache-max-age 14          # Check for stale entries
vscan cache clear                             # Clear all cache (with confirmation)
vscan cache clear --force                     # Clear without confirmation

# Configuration management commands (NEW v3.1)
vscan config init                             # Create default ~/.vscanrc file
vscan config show                             # Display current config (unified table)
vscan config set scan.delay 2.0               # Set config value
vscan config get scan.delay                   # Get specific config value
vscan config reset                            # Delete config file (with confirmation)

# Report generation from cache (no API calls)
vscan report report.html                      # Generate HTML report from cache
vscan report results.json                     # Generate JSON report from cache
vscan report results.csv                      # Generate CSV report from cache (NEW v3.1)

# Help
vscan --help                                  # Main help with subcommands
vscan scan --help                             # Scan command help (simplified Options panel)
vscan cache --help                            # Cache command help
vscan cache stats --help                      # Cache stats help
vscan cache clear --help                      # Cache clear help
vscan config --help                           # Config command help (NEW v3.1)
vscan report --help                           # Report command help
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

**Complete API documentation:** [docs/guides/API_REFERENCE.md](docs/guides/API_REFERENCE.md)

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

**All scans are comprehensive** (always include full security analysis):

```json
{
  "schema_version": "2.0",
  "output_mode": "detailed",
  "summary": {
    "total_extensions_scanned": 42,
    "vulnerabilities_found": 3,
    "scan_timestamp": "2025-10-24T14:30:00Z",
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
      "publisher": {
        "id": "ms-python",
        "name": "Microsoft",
        "verified": true,
        "domain": "microsoft.com",
        "reputation": 100
      },
      "security": {
        "score": 82,
        "risk_level": "high",
        "vulnerabilities": {
          "total": 0,
          "critical": 0,
          "high": 0,
          "moderate": 0,
          "low": 0
        },
        "risk_factors": [
          {
            "type": "network_access",
            "severity": "medium",
            "description": "Extension makes network requests"
          }
        ],
        "dependencies": {
          "total_count": 45,
          "with_vulnerabilities": 0,
          "list": [
            {
              "name": "vscode-languageclient",
              "version": "8.1.0",
              "risk_level": "low",
              "has_vulnerabilities": false
            }
          ]
        },
        "score_breakdown": {
          "code_quality": 85,
          "dependencies": 90,
          "permissions": 75,
          "network_usage": 80
        }
      },
      "metadata": {
        "description": "IntelliSense, linting, debugging...",
        "install_count": 50000000,
        "rating": 4.5,
        "rating_count": 1234,
        "keywords": ["python", "intellisense", "linting"],
        "repository_url": "https://github.com/microsoft/vscode-python",
        "homepage_url": "https://github.com/microsoft/vscode-python",
        "last_updated": "2024-10-15"
      },
      "vscan_url": "https://vscan.dev/extension/ms-python.python",
      "scan_status": "success"
    }
  ]
}
```

**Field Details:**

- `schema_version`: "2.0" (for v2.0 output format)
- `output_mode`: Always "detailed" (v3.0+ includes full security analysis)
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
vscan cache stats                  # View statistics
vscan cache clear                  # Clear all entries
vscan scan --refresh-cache         # Force refresh of scanned extensions
vscan scan --no-cache              # Disable caching
vscan scan --cache-max-age 14      # Custom expiry (days)
vscan report report.html           # Generate report from cache (no API calls)
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

## Command-Line Interface (v3.0)

### Main Commands

- `vscan scan` - Scan VS Code extensions for vulnerabilities
- `vscan cache stats` - Show cache statistics
- `vscan cache clear` - Clear cache (with confirmation)
- `vscan report` - Generate reports from cache without API calls

### Scan Command Arguments

| Argument | Short | Type | Description | Default |
|----------|-------|------|-------------|---------|
| `--extensions-dir` | `-d` | path | VS Code extensions directory | Auto-detected |
| `--output` | `-o` | path | Output file path (JSON/HTML) | Console output |
| `--delay` | `-t` | float | Delay between requests (seconds) | 1.5 |
| `--quiet` | `-q` | flag | Minimal output (single-line summary) | False |
| `--plain` | - | flag | Plain output without Rich formatting | False |
| `--max-retries` | - | int | Maximum retry attempts for failed requests | 3 |
| `--retry-delay` | - | float | Base delay for exponential backoff (seconds) | 2.0 |
| `--cache-dir` | - | path | Cache directory path | `~/.vscan/` |
| `--cache-max-age` | - | int | Max age of cached results (days) | 7 |
| `--refresh-cache` | - | flag | Force refresh scanned extensions | False |
| `--no-cache` | - | flag | Disable cache (always scan fresh) | False |
| `--publisher` | - | str | Filter by publisher name | None |
| `--include-ids` | - | str | Comma-separated extension IDs to include | None |
| `--exclude-ids` | - | str | Comma-separated extension IDs to exclude | None |
| `--min-risk-level` | - | str | Minimum risk level (low/medium/high/critical) | None |
| `--help` | `-h` | flag | Show help message | - |

### Global Options

| Argument | Short | Description |
|----------|-------|-------------|
| `--version` | `-V` | Show version information |
| `--help` | `-h` | Show help message |

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

**Requirements:** [docs/archive/phases/phase1-research.md](docs/archive/phases/phase1-research.md)

- Reverse-engineer vscan.dev API endpoints
- Document request/response format
- Validate endpoint behavior with test extensions

**Results:** [docs/guides/API_REFERENCE.md](docs/guides/API_REFERENCE.md)

### ✅ Phase 2: Core Implementation (COMPLETE)

**Requirements:** [docs/archive/phases/phase2-implementation.md](docs/archive/phases/phase2-implementation.md)

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

**Requirements:** [docs/archive/phases/phase3-testing.md](docs/archive/phases/phase3-testing.md)

- Test caching system thoroughly
- Test on macOS (focused platform)
- Test with various extension sets (3, 66 extensions)
- Test error scenarios (rate limiting)
- Refine user experience (fixed cache-stats UX bug)

**Results:** [docs/archive/releases/phase3-summary.md](docs/archive/releases/phase3-summary.md)

### ✅ Phase 4: Enhanced Data Integration (COMPLETE)

**Requirements:** [docs/archive/phases/phase4-enhanced-data.md](docs/archive/phases/phase4-enhanced-data.md)

**Implemented Features:**

✅ Complete vscan.dev data capture (all fields)
✅ Dual-mode JSON output (standard/detailed)
✅ Publisher verification and reputation tracking
✅ Comprehensive dependency analysis
✅ Security score breakdown by module
✅ Risk factor identification and reporting
✅ Cache schema v2.0 with automatic v1→v2 migration
✅ Maintained performance (28x speedup with cache)

**Results:** [docs/archive/releases/phase4-summary.md](docs/archive/releases/phase4-summary.md)

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

**Complete API documentation with examples:** [docs/guides/API_REFERENCE.md](docs/guides/API_REFERENCE.md)

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

**Full checklist:** [docs/contributing/TESTING_CHECKLIST.md](docs/contributing/TESTING_CHECKLIST.md)

## Common Development Tasks

### Running Tests

```bash
# Display module tests (v3.0)
python3 tests/test_display.py

# Scanner module tests (v3.0)
python3 tests/test_scanner.py

# CLI module tests (v3.0)
python3 tests/test_cli.py

# API validation tests
python3 tests/test_api.py

# Integration tests
python3 tests/test_integration.py

# Full test suite
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
# Run scan with plain output (shows per-extension progress)
vscan scan --plain

# Test with custom extensions directory
vscan scan --extensions-dir ~/.vscode/extensions/

# Check API behavior
python3 tests/test_api.py

# Run with trace logging
python3 -m pdb -m vscode_scanner.vscan scan
```

## References

- **[vscan.dev](https://vscan.dev)** - VS Code Extension Security Analyzer
- **[VS Code Extension API](https://code.visualstudio.com/api)** - Extension API docs
- **[docs/project/PRD.md](docs/project/PRD.md)** - Product requirements (v3.1)
- **[docs/guides/API_REFERENCE.md](docs/guides/API_REFERENCE.md)** - API reference
- **[docs/specs/retry-mechanism.md](docs/specs/retry-mechanism.md)** - Retry mechanism spec (v2.2)

---

## Documentation Structure

The `docs/` directory is organized into:

- **`docs/guides/`** - Timeless technical reference (REQUIRED reading for architecture, security, APIs)
- **`docs/project/`** - Active project management (status, requirements, roadmap)
- **`docs/specs/`** - Shipped feature specifications
- **`docs/contributing/`** - Contributor guides and checklists
- **`docs/archive/`** - Historical documentation (phases, releases, reviews)

**⚠️ IMPORTANT:** Before making any code changes, you MUST review the REQUIRED documents in the "Required Reading Documentation" section above, especially:
1. docs/guides/ARCHITECTURE.md (system design and constraints)
2. docs/guides/SECURITY.md (security requirements and threat model)
3. docs/project/PRD.md (product requirements and scope)

**For complete documentation navigation, see [docs/README.md](docs/README.md)**
