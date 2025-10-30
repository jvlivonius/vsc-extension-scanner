# Product Requirements Document (PRD)
# VS Code Extension Security Scanner CLI

**Version:** 3.5.4
**Date:** 2025-10-31
**Status:** Production Ready (v3.5.4) ✅

---

## 1. Executive Summary

The VS Code Extension Security Scanner is a production-ready Python CLI tool that enables developers to perform comprehensive security audits of their installed VS Code extensions. The tool leverages the vscan.dev security analysis service to provide detailed vulnerability reports across multiple output formats.

### Current Capabilities (v3.5.1)

**Production Ready (v3.5.1):** Security Hardening + Technical Debt
- **Parallel by Default:** 4.88x speedup automatically with 3 workers (no flags needed!)
- **High Performance:** 66 extensions: 6min → 1.2min (by default, not opt-in)
- **Simplified API:** Removed `--parallel` flag, single code path (~100 lines eliminated)
- **Multi-Platform Support:** macOS, Windows, Linux
- **Intelligent Caching:** SQLite-based caching with 28x performance improvement
- **Rich Terminal UI:** Live progress bars, color-coded tables, interactive displays
- **Multiple Output Formats:** JSON (detailed), HTML (interactive), CSV (spreadsheet)
- **Configuration Management:** Persistent settings via ~/.vscanrc INI file
- **Retry Mechanism:** Exponential backoff with jitter for transient API errors
- **Security Hardened:** SQL injection prevention, path validation, sanitized errors
- **Architecture Compliance:** Zero layer violations, clean 3-layer separation
- **Comprehensive Testing:** 92+ test scenarios, 100% success rate

**Previous Capabilities (v3.2.0-v3.3.3):**
- **Enhanced Verbose Mode:** Security-focused standard output, operational details hidden by default
- **Failed Extensions Tracking:** Clear reporting of which extensions failed to scan and why
- **Custom Extensions Directory:** Configurable in ~/.vscanrc for persistent settings
- **Date Tracking:** Installation and scan date tracking with sorting
- **Enhanced Filtering:** Verification and vulnerability filters

---

## 2. Problem Statement

VS Code extensions have broad access to the editor environment and can potentially introduce security vulnerabilities. Developers lack an automated, efficient way to audit all their installed extensions for known security issues. While vscan.dev provides web-based security analysis, manually checking each extension is time-consuming and error-prone.

**This tool solves:**
- ✅ Time-consuming manual security audits
- ✅ Difficulty tracking security status across many extensions
- ✅ Lack of machine-readable security reports
- ✅ Need for periodic re-scanning with caching

---

## 3. User Personas & Use Cases

### 3.1 User Personas

#### Security-Conscious Developer
**Profile:** Individual developer maintaining a secure development environment
**Background:** Writes code daily in VS Code, concerned about supply chain security
**Goals:**
- Regular security audits of installed extensions
- Awareness of vulnerabilities in development tools
- Maintain compliance with organizational security policies

**Usage Pattern:** Weekly scans with HTML reports for documentation
**Pain Points:** Manual checking of extensions is tedious and error-prone

**Typical Workflow:**
```bash
# Weekly security check
vscan scan --output weekly-report.html

# Review HTML report
open weekly-report.html

# Share with security team if issues found
```

#### DevOps/Security Team Lead
**Profile:** Responsible for organizational security compliance and automation
**Background:** Manages security scanning infrastructure for development teams
**Goals:**
- Automated scanning integrated into CI/CD pipelines
- CSV exports for tracking and trending analysis
- Monitoring security posture across multiple developers

**Usage Pattern:** Automated daily scans with JSON/CSV output for monitoring systems
**Pain Points:** Need machine-readable output for integration with security dashboards

**Typical Workflow:**
```bash
# CI/CD pipeline integration
vscan scan --output results.csv --quiet

# Parse results for automated decision-making
if [ $? -eq 1 ]; then
  echo "Vulnerabilities found, review required"
  # Send CSV to security tracking system
fi
```

#### Extension Developer
**Profile:** VS Code extension author ensuring security best practices
**Background:** Develops and maintains VS Code extensions for community
**Goals:**
- Verify extension security before publishing updates
- Ensure dependencies are free from known vulnerabilities
- Maintain high security standards for users

**Usage Pattern:** Pre-release scanning with verbose output for detailed analysis
**Pain Points:** Need to verify extension security quickly during development cycles

**Typical Workflow:**
```bash
# Before publishing update
vscan scan --verbose --extensions-dir ~/my-extension-dev

# Review detailed output for any issues
# Fix vulnerabilities before release
```

### 3.2 Use Cases

#### UC-1: First-Time Security Audit
**Actor:** Security-Conscious Developer
**Precondition:** User has VS Code installed with multiple extensions
**Trigger:** User wants to perform initial security assessment

**Main Flow:**
1. User installs tool: `pip install vsc-extension-scanner`
2. User runs first scan: `vscan scan`
3. System auto-detects VS Code installation
4. System scans all installed extensions (shows progress bar)
5. System displays summary with security scores and risk levels
6. User generates HTML report: `vscan scan --output report.html`
7. User reviews interactive HTML report in browser
8. User shares findings with team if vulnerabilities found

**Postcondition:** User has comprehensive security assessment of all extensions
**Alternative Flow:** If VS Code not found, user specifies custom directory with `--extensions-dir`

#### UC-2: Continuous Security Monitoring
**Actor:** DevOps/Security Team Lead
**Precondition:** Tool is integrated into CI/CD pipeline
**Trigger:** Scheduled job or manual pipeline execution

**Main Flow:**
1. CI/CD system initializes config: `vscan config init`
2. System configures settings for automation:
   ```bash
   vscan config set scan.quiet true
   vscan config set cache.max_age 1  # Daily cache refresh
   ```
3. Scheduled job executes: `vscan scan --output results.csv --quiet`
4. System scans all extensions using cache when available
5. System exports results to CSV format
6. CI/CD system parses exit code (see [ERROR_HANDLING.md § Exit Codes](../guides/ERROR_HANDLING.md#exit-codes))
7. System sends CSV to security tracking dashboard
8. If vulnerabilities found, system triggers alerts/notifications

**Postcondition:** Security metrics are tracked and trended over time
**Alternative Flow:** If API fails, system uses cached results with warning

#### UC-3: Pre-Release Extension Validation
**Actor:** Extension Developer
**Precondition:** Extension developer has development environment set up
**Trigger:** Developer is ready to publish extension update

**Main Flow:**
1. Developer updates extension dependencies
2. Developer runs verbose scan: `vscan scan --verbose`
3. System performs deep scan with operational details
4. System displays detailed security analysis including:
   - Dependency tree with versions
   - Known vulnerabilities in dependencies
   - Security scores and risk factors
5. Developer reviews verbose output
6. Developer addresses any identified vulnerabilities
7. Developer re-runs scan to verify fixes
8. Developer publishes extension update with confidence

**Postcondition:** Extension is verified secure before public release
**Alternative Flow:** If vulnerabilities cannot be fixed, developer documents risks in extension README

---

## 4. User Stories & Acceptance Criteria

### Epic: Security Scanning

**US-1: Initial Security Audit**
> As a developer, I want to scan all my VS Code extensions for vulnerabilities so that I can maintain a secure development environment.

**Acceptance Criteria:**
- ✅ Tool auto-detects VS Code installation on macOS, Windows, Linux
- ✅ Scans all installed extensions in one command (`vscan scan`)
- ✅ Displays clear security summary with risk levels (high, medium, low)
- ✅ Completes scan of 66 extensions in <2 minutes (without cache)
- ✅ Exit code 0 (clean) or 1 (vulnerabilities found) for automation
- ✅ Shows progress bar with real-time status updates

**US-2: Export Security Reports**
> As a security lead, I want to export scan results to CSV so that I can track vulnerabilities across the organization.

**Acceptance Criteria:**
- ✅ CSV includes all security metrics (score, vulnerabilities, dependencies)
- ✅ Compatible with Excel and Google Sheets (UTF-8 encoding)
- ✅ Proper escaping for special characters (commas, quotes)
- ✅ 15-column schema with complete extension data
- ✅ Command: `vscan scan --output results.csv`

**US-3: Interactive HTML Reports**
> As a developer, I want interactive HTML reports so that I can share findings with my team in a professional format.

**Acceptance Criteria:**
- ✅ Self-contained HTML file with embedded CSS/JS (no external dependencies)
- ✅ Sortable tables by risk level, name, publisher
- ✅ Risk filters (show only high/medium/low risk extensions)
- ✅ Search functionality for finding specific extensions
- ✅ Data visualizations (pie charts, security score gauges)
- ✅ Print-optimized layout for documentation
- ✅ Command: `vscan scan --output report.html`

### Epic: Performance & Caching

**US-4: Fast Repeated Scans**
> As a developer, I want fast repeated scans so that I can run security checks frequently without waiting.

**Acceptance Criteria:**
- ✅ First scan caches results for 7 days (configurable)
- ✅ Subsequent scans complete in <15 seconds for 66 extensions
- ✅ Cache invalidates when extension version changes
- ✅ Manual cache refresh available via `--refresh-cache`
- ✅ Cache statistics command: `vscan cache stats`
- ✅ Achieves 28x speedup for cached results

**US-5: Parallel Processing**
> As a user with many extensions, I want parallel scanning so that initial scans complete faster.

**Acceptance Criteria:**
- ✅ Parallel processing enabled by default (3 workers)
- ✅ Achieves 4.88x speedup compared to sequential scanning
- ✅ Configurable worker count (1-5 workers)
- ✅ Thread-safe operation with isolated API clients
- ✅ Automatic rate limiting to respect API constraints
- ✅ Configuration: `vscan config set scan.workers 5`

### Epic: Configuration & Customization

**US-6: Persistent Configuration**
> As a power user, I want to configure default behavior so that I don't need to pass flags every time.

**Acceptance Criteria:**
- ✅ Persistent config file at ~/.vscanrc (INI format)
- ✅ CLI flags override config file settings
- ✅ `vscan config init` creates default configuration
- ✅ `vscan config show` displays current settings
- ✅ `vscan config set` modifies individual settings
- ✅ `vscan config get` retrieves specific values
- ✅ Type validation (int, float, bool, string, choice, path)

**US-7: Custom Extensions Directory**
> As a developer with multiple VS Code installations, I want to specify a custom extensions directory so that I can scan any installation.

**Acceptance Criteria:**
- ✅ Command-line flag: `--extensions-dir /path/to/extensions`
- ✅ Persistent config setting: `vscan config set scan.extensions_dir /path`
- ✅ Path validation prevents security issues
- ✅ Clear error message if directory not found or invalid
- ✅ Works with relative and absolute paths

### Epic: Error Handling & Reliability

**US-8: Graceful Failure Handling**
> As a user, I want the tool to continue scanning even if individual extensions fail so that I get results for all working extensions.

**Acceptance Criteria:**
- ✅ Individual extension failures don't stop entire scan
- ✅ Failed extensions are tracked and reported at the end
- ✅ Error categorization (rate limit, timeout, network, API error)
- ✅ Clear table showing which extensions failed and why
- ✅ Actionable suggestions for resolution (e.g., increase --delay)
- ✅ JSON output includes `failed_extensions` array for automation

**US-9: Automatic Retry Logic**
> As a user, I want automatic retries for transient failures so that temporary network issues don't cause scan failures.

**Acceptance Criteria:**
- ✅ Exponential backoff retry (2s, 4s, 8s delays)
- ✅ Jitter to prevent thundering herd effect
- ✅ Maximum 3 retries by default (configurable with `--max-retries`)
- ✅ Per-worker retry tracking in parallel mode
- ✅ Clear logging of retry attempts in verbose mode
- ✅ Disable retries with `--max-retries 0` for fail-fast behavior

---

## 5. Core Features

### 5.1 Extension Discovery
- **Auto-detection** of VS Code installation on all platforms
- **Custom directory** support via `--extensions-dir`
- **Metadata parsing** from package.json files
- **Cross-platform** path handling with pathlib

### 5.2 Security Scanning
- **vscan.dev Integration:** Complete API integration with 3 endpoints
- **Request Throttling:** Configurable delays (default 1.5s)
- **Retry Logic:** Exponential backoff (2s, 4s, 8s) with jitter
- **Parallel Processing:** Default 3 workers (configurable 1-5), 4.88x speedup by default
- **Error Handling:** Graceful degradation, continue on failures

### 5.3 Output Formats

**JSON (Detailed Security Data)**
- Schema version 2.0
- Complete vulnerability information
- Publisher verification status
- Dependency analysis with risk levels
- Security score breakdowns
- Risk factor descriptions

**HTML (Interactive Reports)**
- Self-contained with embedded CSS/JS
- Sortable tables, risk filters, search
- Data visualizations (pie charts, gauges, bar charts)
- Print-optimized layout
- No external dependencies

**CSV (Spreadsheet Export)**
- 15-column schema
- Compatible with Excel, Google Sheets
- Proper escaping for special characters
- UTF-8 encoding

### 5.4 Caching System
- **SQLite Database:** ~/.vscan/cache.db
- **Version-Based Invalidation:** Re-scan on version changes
- **Configurable Expiry:** Default 7 days, adjustable
- **Performance:** 28x faster for cached results
- **Management Commands:** `vscan cache stats`, `vscan cache clear`

### 5.5 Configuration Management
- **Configuration File:** ~/.vscanrc (INI format)
- **Three Sections:** scan, cache, output
- **Type Validation:** int, float, bool, string, choice, path
- **CLI Override:** Arguments always override config
- **Management Commands:** init, show, set, get, reset

### 5.6 Rich Terminal UI
- **Live Progress Bars:** Real-time scan status
- **Color-Coded Tables:** Risk levels (🔴 high, 🟡 medium, 🟢 low)
- **Interactive Display:** Rich formatted output
- **Graceful Fallback:** Plain mode when Rich unavailable
- **Three Output Modes (v3.3):** Quiet, Standard (security-focused), Verbose (all details)

### 5.7 Failed Extensions Reporting
- **Tracking:** Capture failed extensions during scan with error categorization
- **Error Types:** Rate limit, network timeout, network error, API error
- **Display:** Clear table/list showing which extensions failed and why
- **JSON Schema:** Include failed_extensions array in summary for automation
- **Suggestions:** Actionable recommendations (e.g., increase --delay or --max-retries)
- **Rich/Plain Support:** Both modes display failures clearly

### 5.8 Parallel Scanning
- **Performance:** 2-3x faster scanning with concurrent workers
- **Worker Count:** 2-3 parallel workers (conservative to avoid rate limits)
- **Thread-Safe:** Each worker has own API client, shared cache manager
- **Rate Limit Protection:** Distributed delays, exponential backoff per worker
- **Configuration:** Persistent setting via config file (parallel, workers)
- **Rich/Plain Support:** Progress display works in both modes

---

## 6. Non-Functional Requirements

### NFR-1: Performance
**Response Time:**
- Cached scans complete in <15 seconds for 66 extensions
- Initial scan completes in <2 minutes per 10 extensions
- Progress updates every 100ms for responsive UI

**Throughput:**
- Handle 5 concurrent extension scans (parallel mode with 3 workers)
- Process up to 200 extensions without performance degradation
- Sustain 1.5 requests/second to vscan.dev API (configurable)

**Resource Usage:**
- Memory footprint <50MB during typical operation
- Disk cache <5MB per 100 extensions
- Network bandwidth respects rate limits (configurable delay)

### NFR-2: Reliability
**Availability:**
- Graceful degradation when vscan.dev API is unavailable (use cached data)
- Continue scanning even if individual extensions fail
- No complete scan failures due to single extension errors

**Error Handling:**
- Automatic retry with exponential backoff (3 attempts by default)
- Clear error categorization (rate limit, timeout, network, API)
- Actionable error messages with resolution suggestions

**Data Integrity:**
- HMAC-SHA256 signatures prevent cache tampering
- Version-based cache invalidation ensures accuracy
- Atomic database transactions prevent corruption

### NFR-3: Usability
**Learning Curve:**
- New users can run first scan in <2 minutes
- Command help available via `--help` for all commands
- Interactive configuration wizard: `vscan config init`

**Error Messages:**
- Clear, sanitized error messages (no sensitive path disclosure)
- ERROR_HELP system provides actionable guidance
- Contextual suggestions based on error type

**Documentation:**
- Complete user guide integrated into PRD
- Command reference with examples for all features
- Quick start guide in README.md

### NFR-4: Security
**Data Privacy:**
- No sensitive data transmitted to vscan.dev (only extension IDs)
- No logging of user file system paths
- Sanitized error messages prevent information disclosure

**File Permissions:**
- Restrictive permissions (0o600/0o700) for cache and config files
- Path validation blocks URL-encoded traversal attacks
- System directory access prevention

**Network Security:**
- HTTPS-only API communication (no HTTP fallback)
- Certificate validation enforced
- 10 MB response size limit prevents memory exhaustion

### NFR-5: Maintainability
**Code Coverage:**
- ≥85% overall test coverage
- ≥95% coverage for security modules (utils.py, cache_manager.py)
- 161+ test scenarios, 100% passing

**Architecture:**
- Clean 3-layer separation (Presentation, Application, Infrastructure)
- Zero layer violations (enforced by test_architecture.py)
- SOLID principles and design patterns

**Documentation:**
- All public APIs documented with examples
- Architecture decision records for major changes
- Comprehensive inline code comments

### NFR-6: Compatibility
**Platform Support:**
- macOS (10.14+), Windows (10+), Linux (Ubuntu 18.04+)
- Cross-platform path handling with pathlib
- Platform-specific VS Code directory detection

**Python Version:**
- Python 3.8+ (supports 4 years of Python releases)
- Type hints for IDE support and documentation
- Standard library preference (minimal dependencies)

**VS Code Versions:**
- All VS Code versions with standard extension directory structure
- VS Code Insiders support
- Remote development extension support

---

## 7. Constraints & Assumptions

### Technical Constraints

**API Dependency:**
- Requires vscan.dev API availability for initial scans
- API must provide consistent JSON response format
- API rate limits must be respected (configurable delay)
- **Impact:** Offline operation limited to cached results only

**Network Requirement:**
- Internet connection required for initial scans
- HTTPS access to vscan.dev (port 443) must be available
- **Impact:** Cannot scan new extensions without network

**Python Version:**
- Minimum Python 3.8 (for typing support and pathlib features)
- **Impact:** Users on older Python versions must upgrade

**VS Code Structure:**
- Assumes standard VS Code extension directory structure
- package.json file must exist for each extension
- **Impact:** Non-standard installations may not be detected

### Operational Constraints

**Rate Limits:**
- vscan.dev API imposes rate limits (respect required)
- Default 1.5s delay between requests (configurable 0.5-10s)
- **Impact:** Large extension counts require time for initial scan

**Cache Size:**
- Cache grows with extension count (~50KB per extension)
- No automatic cache size limit (manual clearing required)
- **Impact:** Users with 1000+ extensions may need periodic cache cleanup

**Memory Limit:**
- Designed for <50MB memory usage (typical operation)
- 10 MB API response limit prevents memory exhaustion
- **Impact:** Systems with <100MB free RAM may experience issues

### Legal/Compliance Constraints

**API Terms:**
- Must comply with vscan.dev terms of service
- No commercial use restrictions (verify with vscan.dev)
- **Impact:** Tool usage subject to third-party terms

**Data Privacy:**
- GDPR-compliant (no personal data transmission)
- Only extension IDs sent to vscan.dev
- **Impact:** Users in regulated industries can use safely

**Open Source:**
- MIT license for tool code
- All dependencies must be MIT-compatible
- **Impact:** Free to use, modify, and distribute

### Assumptions

**User Environment Assumptions:**
- Users have admin/sudo access for pip installation
- VS Code is installed in standard system locations
- Users have stable internet connection (>1 Mbps)
- Users understand basic command-line operations

**API Behavior Assumptions:**
- vscan.dev API maintains stable endpoint structure
- Popular extensions are pre-analyzed and cached by vscan.dev
- API response times remain <5 seconds per extension
- API availability >99% uptime (not guaranteed)

**Security Landscape Assumptions:**
- Vulnerability databases are regularly updated by vscan.dev
- vscan.dev continues providing free tier access
- Extension security remains critical concern for developers
- Supply chain attacks on VS Code extensions remain relevant threat

---

## 8. Dependencies & Integrations

### External Services

| Service | Purpose | Criticality | Fallback |
|---------|---------|-------------|----------|
| **vscan.dev API** | Security analysis of extensions | Critical | Cache provides degraded mode for previously scanned extensions |
| **PyPI** | Package distribution | High | Manual installation from source available |

**vscan.dev API Details:**
- **Endpoints:** 3 endpoints (search, extension details, vulnerability data)
- **Rate Limits:** Configurable delay (default 1.5s between requests)
- **Authentication:** None required (public API)
- **Availability:** No SLA guarantee, community service

### Required Libraries

| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| **typer** | ≥0.9.0 | CLI framework with subcommands | MIT |
| **rich** | ≥13.0.0 | Terminal UI (progress bars, tables, formatting) | MIT |
| **Python stdlib** | 3.8+ | Core functionality (urllib, sqlite3, configparser) | PSF |

**Dependency Rationale:**
- **Minimal Dependencies:** Only 2 external libraries (typer, rich)
- **Standard Library Priority:** All core functionality uses stdlib
- **No Transitive Security Risks:** Minimal dependency tree reduces attack surface

### System Requirements

**Disk Space:**
- <10MB: Tool installation
- Variable: Cache database (~50KB per extension)
- **Total Recommended:** 50 MB (includes room for reports and cache)

**RAM:**
- <50MB: Typical operation (3 workers)
- Peak: <100MB (5 workers + large report generation)

**Network:**
- Outbound HTTPS (port 443) for vscan.dev API access
- ~8 KB data transfer per extension (initial scan)
- ~500 KB total for 66 extensions

**Permissions:**
- Read access to VS Code extensions directory
- Write access to ~/.vscan/ (cache) and ~/.vscanrc (config)
- No elevated privileges required (runs as user)

### Integration Points

**Current Integrations (v3.5.1):**
- **JSON Export:** Machine-readable format for automation and monitoring systems
- **CSV Export:** Spreadsheet import for reporting and tracking (Excel, Google Sheets)
- **Exit Codes:** Standard codes for CI/CD decision logic (see [ERROR_HANDLING.md § Exit Codes](../guides/ERROR_HANDLING.md#exit-codes))
- **Configuration File:** Integration with dotfile management tools

**Planned Integrations (Future):**
- **CI/CD Pipelines:** GitHub Actions, GitLab CI, Jenkins examples and templates
- **Monitoring Systems:** Prometheus metrics export for dashboards
- **Security Dashboards:** Grafana visualization templates
- **Notification Services:** Slack/Teams webhooks for critical vulnerabilities
- **Vulnerability Databases:** Integration with additional CVE sources (NVD, GitHub Advisory)

### Integration Architecture

**Data Flow:**
```
VS Code Extensions
      ↓
Extension Discovery (extension_discovery.py)
      ↓
Security Scanner (scanner.py)
      ↓
vscan.dev API (vscan_api.py)
      ↓
Cache Manager (cache_manager.py) ←→ SQLite Database
      ↓
Output Formatters (output_formatter.py, html_report_generator.py)
      ↓
JSON / HTML / CSV Reports
```

**Integration Points:**
- **Input:** VS Code extension directory (auto-detected or user-specified)
- **Processing:** vscan.dev API + local caching
- **Output:** Multiple formats (JSON, HTML, CSV) for different use cases
- **Configuration:** ~/.vscanrc for persistent settings
- **State:** ~/.vscan/cache.db for performance optimization

---

## 9. User Guide

### 9.1 Installation

```bash
# Install from source
pip install -e .

# Or run directly
python -m vscode_scanner.vscan
```

### 9.2 Quick Start

```bash
# Basic scan with Rich UI
vscan scan

# Scan and save to file
vscan scan --output results.json
vscan scan --output report.html
vscan scan --output results.csv

# Initialize configuration
vscan config init
vscan config show

# Manage cache
vscan cache stats
vscan cache clear

# Generate report from cache (no API calls)
vscan report report.html
```

### 9.3 Common Commands

**Scanning:**
```bash
vscan scan                              # Standard scan (security-focused, v3.3)
vscan scan --verbose                    # Verbose mode (show operational details, v3.3)
vscan scan --quiet                      # Minimal summary for CI/CD
vscan scan --plain                      # Plain output (no Rich UI)
vscan scan --no-cache                   # Disable caching
vscan scan --refresh-cache              # Force refresh
vscan scan --extensions-dir /custom/path
vscan scan --parallel                   # Enable parallel scanning (v3.4 planned)
vscan scan --parallel --workers 2       # Custom worker count (v3.4 planned)
```

**Filtering:**
```bash
vscan scan --publisher microsoft        # Only scan Microsoft extensions
vscan scan --min-risk-level high        # Only show high/critical risk
vscan scan --include-ids "ms-python.python"
vscan scan --exclude-ids "local.test"
```

**Configuration:**
```bash
vscan config init                       # Create default ~/.vscanrc
vscan config show                       # Display current config
vscan config set scan.delay 2.0         # Set API delay
vscan config set scan.extensions_dir ~/custom/path  # Set custom directory
vscan config set scan.workers 3         # Set worker count
vscan config get scan.delay             # Get specific value
vscan config reset                      # Delete config file
```

**Cache Management:**
```bash
vscan cache stats                       # Show statistics
vscan cache stats --cache-max-age 14    # Check for stale entries
vscan cache clear                       # Clear all (with confirmation)
vscan cache clear --force               # Clear without confirmation
```

**Retry Configuration:**
```bash
vscan scan --max-retries 5              # More aggressive retries
vscan scan --retry-delay 3.0            # Longer backoff delays
vscan scan --max-retries 0              # Disable retries (fail fast)
```

---

## 10. Technical Dependencies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.8+ | Cross-platform compatibility |
| **CLI Framework** | Typer ≥0.9.0 | Modern CLI with subcommands |
| **Terminal UI** | Rich ≥13.0.0 | Progress bars, tables, formatting |
| **HTTP Client** | urllib.request | Standard library (no dependencies) |
| **Database** | SQLite3 | Caching with version tracking |
| **Configuration** | configparser | INI file parsing |
| **Testing** | unittest | Standard library testing |

**Key Dependencies:**
- `typer` - Modern CLI framework
- `rich` - Terminal formatting and UI
- All other functionality uses Python stdlib

**Architecture Details:** See [guides/ARCHITECTURE.md](/docs/guides/ARCHITECTURE.md) for complete system design, layering principles, and design patterns.

---

## 11. Security

**Security Posture:** Enterprise-grade security with comprehensive validation and protection (Risk Level: LOW ✅)

**Core Security Features:**
- Path traversal protection
- Input validation and sanitization
- HTTPS-only API communication
- Restrictive file permissions (0o600/0o700)
- Resource exhaustion protection (10MB response limit)
- Error message sanitization
- Cache integrity with HMAC-SHA256 signatures

**Complete Security Documentation:**
- **[guides/SECURITY.md](/docs/guides/SECURITY.md)** - Threat model, validation patterns, security requirements
- **[guides/ERROR_CODES.md](/docs/guides/ERROR_CODES.md)** - Error code reference and handling

---

## 12. Performance

**User Experience:**
- Scans 66 extensions in ~15 seconds (with cache)
- First scan: ~6 minutes, subsequent scans: ~15 seconds (28x speedup)
- Parallel processing by default (3 workers) provides 4.88x faster scanning
- Minimal memory footprint (<50MB typical usage)
- Efficient caching: 97% cache hit rate on repeated scans

**Resource Requirements:**
- **Memory:** < 50MB typical usage
- **Disk:** ~/.vscan/cache.db (~2-5MB for 100 extensions)
- **Network:** Configurable rate limiting (default 1.5s delay between requests)

**Detailed Benchmarks:** See [guides/PERFORMANCE.md](/docs/guides/PERFORMANCE.md) for comprehensive performance data, optimization strategies, and troubleshooting.

---

## 13. Documentation

**For Users:**
- Quick Start: See Section 9 (User Guide)
- Command Reference: See Section 9.3 (Common Commands)

**For Developers:**
- **Complete Documentation Index:** [docs/README.md](/docs/README.md)
- **Architecture:** [guides/ARCHITECTURE.md](/docs/guides/ARCHITECTURE.md)
- **Security:** [guides/SECURITY.md](/docs/guides/SECURITY.md)
- **Testing:** [guides/TESTING.md](/docs/guides/TESTING.md)
- **Performance:** [guides/PERFORMANCE.md](/docs/guides/PERFORMANCE.md)
- **API Reference:** [guides/API_REFERENCE.md](/docs/guides/API_REFERENCE.md)

---

## 14. Version History

**Current Version:** v3.5.1 (Production Ready) ✅

**Major Milestones:**
- **v3.5.1:** Security hardening & technical debt resolution
- **v3.4.0:** Parallel processing by default (4.88x speedup)
- **v3.0.0:** CLI UX enhancement with Rich UI
- **v2.0.0:** Enhanced data integration
- **v1.0.0:** Initial release

**Complete History:**
- **[CHANGELOG.md](/CHANGELOG.md)** - Detailed release notes
- **[project/STATUS.md](/docs/project/STATUS.md)** - Implementation history and current status
- **[archive/README.md](/docs/archive/README.md)** - Overview of previous implementation plans, summaries and reviews

---

## 15. Success Metrics

### 15.1 Functional Metrics (Achieved)

- ✅ 100% extension detection on all platforms
- ✅ 100% scan success rate (with graceful failure handling)
- ✅ Valid output in all formats (JSON, HTML, CSV)
- ✅ Correct exit codes (see [ERROR_HANDLING.md § Exit Codes](../guides/ERROR_HANDLING.md#exit-codes))

### 15.2 Performance Metrics (Achieved)

- ✅ < 15 seconds for 66 extensions (with cache)
- ✅ < 50MB memory usage
- ✅ Zero unhandled exceptions (92+ test scenarios)
- ✅ 28x performance improvement with caching

### 15.3 Quality Metrics (Achieved)

- ✅ 92+ test scenarios, 100% passing
- ✅ 82% security vulnerability reduction
- ✅ Comprehensive documentation (20,000+ lines)
- ✅ Clear error messages with actionable suggestions

---

## 16. Out of Scope

The following features are **not included** in the current version:

### 16.1 Not Implemented

- ❌ Support for VS Code variants (VSCodium, Cursor)
- ❌ CI/CD pipeline integration templates
- ❌ Scheduled/automated scanning
- ❌ PDF report generation
- ❌ Historical vulnerability tracking over time
- ❌ Extension installation/removal functionality
- ❌ GUI interface
- ❌ Auto-remediation of vulnerabilities
- ❌ Extension update recommendations
- ❌ Integration with other vulnerability databases

### 16.2 Previously Considered (Now Implemented)

- ~~HTML report generation~~ ✅ Implemented in v2.2
- ~~Local caching~~ ✅ Implemented in Phase 2.5
- ~~CSV output format~~ ✅ Implemented in v3.1
- ~~Configuration file~~ ✅ Implemented in v3.1

---

## 17. Future Enhancements

---

## 18. References

### 18.1 External Resources

- **[vscan.dev](https://vscan.dev)** - VS Code Extension Security Analyzer
- **[VS Code Extension API](https://code.visualstudio.com/api)** - Official VS Code documentation
- **[Typer Documentation](https://typer.tiangolo.com/)** - CLI framework docs
- **[Rich Documentation](https://rich.readthedocs.io/)** - Terminal formatting docs

### 18.2 Standards & Compliance

- **[CWE Top 25](https://cwe.mitre.org/top25/)** - Common Weakness Enumeration
- **[OWASP Top 10 (2021)](https://owasp.org/Top10/)** - Web application security risks
- **[Semantic Versioning](https://semver.org/)** - Version numbering standard

---

## 19. Contact & Support

**Issues & Feedback:**
- GitHub Issues: https://github.com/anthropics/claude-code/issues

**Documentation:**
- Full documentation: [/docs/README.md](/docs/README.md)
- Quick user reference: [/README.md](/README.md)

---

**Document Version:** 3.4.1
**Last Updated:** 2025-10-25
**Status:** Production Ready ✅
