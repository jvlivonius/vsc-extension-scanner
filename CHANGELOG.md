# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.5.1] - 2025-10-26

### Security

**Phase 1: Security Hardening (4 Critical Tasks)**

- **Unified Path Validation**: Implemented `validate_path()` function now used in all path operations
  - Blocks URL-encoded path traversal attacks (`%2e%2e%2f`, `%252e`, etc.)
  - Blocks access to critical system directories (`/etc`, `/sys`, `/System`, `C:\Windows`, etc.)
  - Supports absolute paths and shell expansion (`~/`, `$HOME/`) securely
  - Applied to 4 critical locations: extension discovery, cache manager, CLI output, config manager

- **String Sanitization**: Implemented `sanitize_string()` function for all user-facing output
  - Context-aware sanitization (output, log, error contexts)
  - Prevents injection attacks in error messages, logs, JSON/CSV/HTML output
  - Hides sensitive path information in error messages
  - Removes control characters while preserving readability

- **HMAC Cache Integrity**: Added cryptographic signatures to prevent cache tampering
  - HMAC-SHA256 signatures for all cached scan results
  - Automatic detection and invalidation of tampered entries
  - Per-installation key (not hardcoded) stored securely
  - Backward compatible with existing cache (auto-migration)

- **Security Test Coverage**: Added comprehensive security regression test suite
  - 35+ new security tests covering all hardening features
  - Path validation tests (15 scenarios: allowed/blocked paths)
  - String sanitization tests (10 scenarios: context-aware behavior)
  - Cache integrity tests (5 scenarios: tampering detection)
  - End-to-end security tests (5 scenarios: full scan validation)

### Fixed

**Phase 2: Technical Debt & Reliability**

- **Thread Safety**: Implemented `ThreadSafeStats` class for guaranteed thread-safe statistics
  - Lock-protected statistics collection eliminates race conditions
  - Prevents incorrect counts in parallel scanning mode
  - Clean API with `increment()` and `to_dict()` methods

- **Fault Tolerance**: Added transactional cache writes with interrupt handling
  - Cache writes now use try/finally pattern for guaranteed commit
  - Partial results saved even on Ctrl+C interruption
  - Individual save failures don't prevent other cache writes
  - Better user experience with progress preservation

### Changed

- Security score improved from 7/10 to 9.5/10
- 0 security vulnerabilities remaining (was 6 in v3.5.0)
- All path operations now use centralized validation
- All user-facing output now sanitized

### Added

- **Documentation**: Parallel scanning architecture fully documented in ARCHITECTURE.md
  - Threading model and worker isolation pattern
  - Cache write strategy and SQLite thread safety
  - Performance characteristics and best practices
  - Thread safety guarantees for all operations

- **Testing**: Integration tests with real vscan.dev API
  - Real API validation (not just mocks)
  - Config file integration testing
  - Sequential vs parallel result consistency tests
  - Cache behavior with real data

### Technical Details

**Files Modified/Created (15 total):**

*Security (Phase 1):*
- `vscode_scanner/utils.py` - Enhanced `validate_path()` and `sanitize_string()`
- `vscode_scanner/extension_discovery.py` - Added path validation
- `vscode_scanner/cache_manager.py` - Added path validation + HMAC integrity
- `vscode_scanner/cli.py` - Added path validation + string sanitization
- `vscode_scanner/config_manager.py` - Added path validation
- `vscode_scanner/output_formatter.py` - Added string sanitization
- `vscode_scanner/display.py` - Added string sanitization
- `tests/test_security_regression.py` - NEW comprehensive security test suite
- `tests/test_path_validation.py` - NEW path validation tests
- `tests/test_string_sanitization.py` - NEW sanitization tests
- `tests/test_cache_integrity.py` - NEW HMAC integrity tests

*Reliability (Phase 2):*
- `vscode_scanner/scanner.py` - `ThreadSafeStats` class + transactional cache
- `docs/guides/ARCHITECTURE.md` - Parallel architecture documentation (~200 lines)
- `tests/test_integration_real_api.py` - NEW real API integration tests
- `tests/test_transactional_cache.py` - NEW cache transaction tests

**Impact Summary:**
- ~800 lines of improvements (Phase 1: ~400 lines, Phase 2: ~400 lines)
- Zero breaking changes (100% backward compatible)
- Performance maintained (no regression)
- All 161+ existing tests still passing

## [3.5.0] - 2025-10-26

### 🚨 BREAKING CHANGES
- **Removed `--parallel` flag**: Parallel processing is now always used (no flag needed)
- **Removed `parallel` config setting**: Remove `parallel = true/false` from `~/.vscanrc`
- **Default behavior changed**: Now uses 3 workers automatically (4.88x speedup by default)
- **Sequential mode**: Use `--workers 1` instead of omitting `--parallel`

### Changed
- ThreadPoolExecutor now always used with configurable workers (1-5, default: 3)
- `--workers` parameter: Range changed from 2-5 to 1-5
- Workers=1 provides sequential behavior via ThreadPoolExecutor
- Unified scan implementation: Removed duplicate sequential code path (~100 lines eliminated)

### Removed
- `--parallel` CLI flag (breaking change)
- `parallel` configuration setting (breaking change)
- Sequential `_scan_extensions()` function (internal API)

### Migration Guide

**Old Commands (v3.4.0):**
```bash
vscan scan                  # Sequential (slow)
vscan scan --parallel       # 3 workers (fast)
vscan scan --parallel --workers 5  # 5 workers
```

**New Commands (v3.5.0):**
```bash
vscan scan                  # 3 workers (fast) - NEW DEFAULT!
vscan scan --workers 1      # Sequential (if needed)
vscan scan --workers 5      # 5 workers
```

**Configuration File:**
- **Remove**: `parallel = true/false` from `[scan]` section
- **Keep**: `workers = 3` (or any value 1-5)

**Action Required:**
1. Remove `--parallel` flag from all scripts
2. Remove `parallel = true/false` from `~/.vscanrc`
3. For sequential behavior: use `--workers 1`

### Benefits
- ✅ Single code path eliminates maintenance burden
- ✅ Performance by default (3 workers = 4.88x speedup)
- ✅ Simpler API (one concept: workers, not two: parallel + workers)
- ✅ Eliminates code duplication (~100 lines removed)
- ✅ Solves v3.4.1 roadmap Task 1 (code duplication)
- ✅ Solves v3.4.1 roadmap Task 6 (progress display duplication)

## [3.4.0] - 2025-10-25

### Added
- Parallel scanning feature with `--parallel` flag for 2-5x performance improvement
- `--workers` CLI option to configure worker count (2-5, default: 3)
- Configuration file support for parallel scanning settings (`scan.parallel`, `scan.workers`)
- Thread-safe parallel implementation using ThreadPoolExecutor
- Worker count displayed in progress indicators (both Rich and plain modes)

### Changed
- Performance: 4.88x speedup with 3 workers (validated via PoC with 30 extensions)
- Real-world impact: 66 extensions reduced from 6 minutes to 1.2 minutes
- Near-linear scaling up to 3 workers with 100% success rate

### Fixed
- SQLite thread safety: Implemented main-thread-only cache writes to prevent cross-thread connection errors
- Batch cache writes after parallel workers complete (prevents database lock issues)

### Performance
- 3 workers: 4.88x speedup, 100% success rate (recommended default)
- 5 workers: 4.27x speedup, 96.7% success rate (advanced users)
- No rate limiting detected from vscan.dev API (tested up to 7 workers)

## [3.3.3] - 2025-10-25

### Fixed
- Eliminated duplicate extension entries from old versions on disk
- VS Code keeps old extension versions, but only current version is "installed"
- Scanner now uses extensions.json to filter discovered extensions
- Faster scans with fewer directories processed
- Accurate extension counts

### Changed
- Refactored `_read_extensions_json()` to return installed extension metadata
- Discovery process now filters to only scan directories listed in extensions.json

## [3.3.2] - 2025-10-25

### Fixed
- HTML report date column sorting (now uses proper timestamp parsing)
- Installation date matching between extensions.json and cache.db
- Date display consistency across HTML reports

### Changed
- Improved date handling in HTML report generator
- Better timestamp synchronization between discovery and caching

## [3.3.1] - 2025-10-25

### Added
- Installation date tracking for extensions (from extensions.json)
- Installed timestamp display in HTML reports
- Critical risk filter now properly filters extensions

### Fixed
- Critical bug: `--min-risk-level critical` filter was broken
- Filter comparison now correctly identifies critical-risk extensions

### Changed
- Schema version updated to 2.1 (added installed_at field)
- Cache database schema migration from v2.0 to v2.1

## [3.3.0] - 2025-10-25

### Added
- Enhanced verbose mode with security-focused output
- Failed extensions tracking with detailed error reporting
- Display of which extensions failed to scan and why
- Improved error context in scan reports

### Changed
- Verbose mode now hides operational details by default
- Standard output focuses on security-relevant information
- Better error categorization and display

## [3.2.0] - 2025-10-25

### Added
- Architecture layer compliance enforcement
- Comprehensive test coverage for architecture violations
- Database connection leak prevention in batch mode

### Fixed
- Critical bug: Database connection leak in batch mode
- Division by zero safeguard in cache hit rate calculation
- SQL injection prevention with extension ID validation

### Changed
- Rich and Typer are now required dependencies (not optional)
- Removed ~70 lines of conditional logic for optional dependencies
- Report command now uses fail-fast pattern (Command-Query Separation)

### Security
- Added extension ID validation before database operations
- Blocks SQL injection, path traversal, and boolean injection patterns
- Centralized error display through display.py for consistency

## [3.1.0] - 2025-10-24

### Added
- Configuration file support with ~/.vscanrc (INI format)
- Five config management commands: init, show, set, get, reset
- CSV export feature for spreadsheet-compatible output
- Inline comment support in config files with # syntax
- Type validation for all configuration values

### Changed
- Config values serve as defaults, CLI arguments always override
- Single unified table display for configuration (shows full keys)
- Batch commit optimization (87.6% faster)
- VACUUM after bulk deletes (73.9% space reclaimed)

### Added
- Performance benchmark tests
- Centralized constants module
- Improved error codes and messages

## [3.0.0] - 2025-10-24

### Added
- Rich terminal formatting with live progress bars
- Typer CLI framework with organized subcommands
- Color-coded risk levels and status indicators
- Beautiful tables and formatted output

### Changed
- New CLI structure: `vscan scan`, `vscan cache`, `vscan config`, `vscan report`
- Simplified help panels (all options in single "Options" panel)
- Streamlined CLI options (removed --verbose and --detailed flags)
- Fixed --quiet to show minimal single-line summary

### Removed
- Removed --verbose flag (minimal impact on output)
- Removed --detailed flag (scans are always comprehensive)

## [2.2.1] - 2025-10-24

### Added
- Centralized version management with _version.py
- Dynamic versioning in setup.py and pyproject.toml
- Version bump helper script (scripts/bump_version.py)

### Changed
- All modules now import from _version.py (no hardcoded versions)
- Separated app version (2.2.1) from schema version (2.0)
- Human-readable output by default (no JSON to console)
- JSON output only saved to file when --output is specified

### Added
- Enhanced filter feedback when 0 extensions match
- Helpful messages showing active filters and troubleshooting tips

## [2.2.0] - 2025-10-23

### Added
- HTML report generation feature with interactive, self-contained reports
- Auto-detected from .html file extension in --output flag
- Sortable tables, risk filters, search functionality
- Data visualizations (pie charts, gauges, bar charts)
- Print-optimized layout with embedded CSS/JS
- Intelligent retry mechanism for transient API errors
- Exponential backoff with jitter (2s, 4s, 8s delays)
- Retry-After header support for rate limiting compliance
- Configurable retry attempts and delays (--max-retries, --retry-delay)
- Retry statistics tracking and reporting

## [2.1.0] - 2025-10-23

### Changed
- Refactored security functions to eliminate unused code
- All error messages now sanitized to prevent information disclosure
- Test files organized in dedicated tests/ directory

### Added
- .gitignore for Python artifacts and cache files

## [2.0.0] - 2025-10-22

### Added
- Phase 4: Enhanced data integration
- Complete vscan.dev data capture (all fields)
- Dual-mode JSON output (standard/detailed)
- Publisher verification and reputation tracking
- Comprehensive dependency analysis
- Security score breakdown by module
- Risk factor identification and reporting

### Changed
- Cache schema v2.0 with automatic v1→v2 migration
- Maintained performance (28x speedup with cache)

## [1.0.0] - 2025-10-20

### Added
- Initial release with Phases 1-3 complete
- Extension discovery for macOS, Windows, Linux
- vscan.dev API integration
- JSON output generation
- SQLite-based caching system
- Error handling and logging
- Progress indicators
- CLI argument parsing
- Cross-platform compatibility
- Security checks and path validation

[Unreleased]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.4.0...HEAD
[3.4.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.3.3...v3.4.0
[3.3.3]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.3.2...v3.3.3
[3.3.2]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.3.1...v3.3.2
[3.3.1]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.3.0...v3.3.1
[3.3.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.2.0...v3.3.0
[3.2.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v2.2.1...v3.0.0
[2.2.1]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/jvlivonius/vsc-extension-scanner/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/jvlivonius/vsc-extension-scanner/releases/tag/v1.0.0
