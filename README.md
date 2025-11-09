# VS Code Extension Security Scanner

[![CI Status](https://github.com/jvlivonius/vsc-extension-scanner/actions/workflows/test.yml/badge.svg)](https://github.com/jvlivonius/vsc-extension-scanner/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Tests: 1,224 passed](https://img.shields.io/badge/tests-1%2C224%20passed-success.svg)](tests/)
[![Coverage: 88.84%](https://img.shields.io/badge/coverage-88.84%25-green.svg)](htmlcov/)

**Know what's running in your editor. Stay secure.**

A command-line tool that scans your installed VS Code extensions for security vulnerabilities, suspicious permissions, and risky dependencies. Get instant insights into the security posture of your development environment.

**Version:** See [releases](https://github.com/jvlivonius/vsc-extension-scanner/releases) | **Status:** Production Ready ✅

**Latest:** v5.0.2 - Test Quality Improvements (1,224 tests, 88.84% coverage, 0 vulnerabilities, parametrization + property-based testing)

---

## 📋 Table of Contents

- [⚡ Quick Demo](#-quick-demo-30-seconds)
- [Why Use This Tool?](#why-use-this-tool)
  - [Why CLI vs Web?](#why-command-line-vs-web-interface)
- [🚀 Installation](#-installation)
- [Quick Start](#quick-start)
- [✨ Key Features](#-key-features)
- [🛡️ Security Highlights](#-security-highlights)
- [What Gets Analyzed?](#what-gets-analyzed)
- [Common Use Cases](#common-use-cases)
- [📊 Output Formats](#-output-formats)
- [🔧 All Commands](#-all-commands)
- [⚙️ Configuration File](#-configuration-file)
- [🚨 Exit Codes](#-exit-codes)
- [🔧 Troubleshooting](#-troubleshooting)
- [📰 What's New](#-whats-new)
- [🔬 Technical Details](#-technical-details)
- [❓ FAQ](#-faq)
- [⚠️ Disclaimer](#-disclaimer)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [🚀 Next Steps](#-next-steps)
- [🔗 Links](#-links)

---

## ⚡ Quick Demo (30 Seconds)

**Want to see it in action first?** Try this quick scan:

```bash
# 👇 Install (one command)
pip install ~/Downloads/vscode_extension_scanner-*.whl

# 👇 Run your first scan
vscan scan --quiet
```

**✅ Expected output:**
```
Scanned 66 extensions - Found 5 vulnerabilities ⚠️
```

**That's it!** You just audited your entire VS Code setup in 30 seconds.

**What you'll see:**
- ✅ Total extensions scanned
- ⚠️ Vulnerabilities found (if any)
- 🚀 Scan completed in < 2 minutes (with caching: instant!)

**Want more details?** Run `vscan scan` for the full interactive report.

---

## Why Use This Tool?

VS Code extensions have broad access to your code, files, and development environment. A malicious or vulnerable extension could:

- 🚨 Access your source code and secrets
- 📝 Modify files without your knowledge
- 🌐 Send data to external servers
- ⚠️ Introduce vulnerable dependencies

**This tool helps you:**

- 🔍 Identify high-risk extensions before they cause problems
- ⚡ Audit your entire extension collection in minutes (not hours)
- 👥 Track security issues across your development team
- ✅ Make informed decisions about which extensions to trust

### Why Command-Line vs Web Interface?

**Speed & Automation:**
- ⚡ Scan 66 extensions in 75 seconds (vs manual web lookups: hours)
- 🔄 Integrate into CI/CD pipelines
- 📊 Batch processing and scheduled scans
- 💾 Local caching for instant repeated scans

**Privacy & Control:**
- 🔒 All data stays on your machine
- 🚫 No browser tracking or analytics
- 📁 Local cache storage (SQLite)
- 🎯 Audit offline from cached data

**Team Collaboration:**
- 📄 Export to CSV/JSON for tracking
- 📊 HTML reports for presentations
- 🤝 Standardized security audits
- 📈 Historical trend analysis

**Developer Workflow:**
- 🔧 Scriptable and automatable
- 🎨 Customizable output formats
- ⚙️ Configuration file support
- 🔀 Git-friendly (track changes in CSV)

---

## 🚀 Installation

**Requirements:** Python 3.8 or higher

### Option 1: Download from GitHub Releases (Recommended - 2 minutes)

```bash
# 👇 One-line install (copy and run):
pip install "$(curl -s https://api.github.com/repos/jvlivonius/vsc-extension-scanner/releases/latest | grep browser_download_url | grep .whl | cut -d '"' -f 4)"

# Or manual download:
# 1. Visit: https://github.com/jvlivonius/vsc-extension-scanner/releases/latest
# 2. Download: vscode_extension_scanner-*.whl
# 3. Install: pip install ~/Downloads/vscode_extension_scanner-*.whl

# ✅ Verify installation:
vscan --version
# Expected: vscode-extension-scanner, version 5.0.2
```

**✅ Installation complete!** Run `vscan scan` to get started.

**See:** [DISTRIBUTION.md](DISTRIBUTION.md) for complete installation instructions and troubleshooting.

<details>
<summary>Option 2: Install from source (for developers)</summary>

```bash
git clone https://github.com/jvlivonius/vsc-extension-scanner.git
cd vsc-extension-scanner
pip install -e .
```
</details>

<details>
<summary>Option 3: Install from PyPI (planned for future)</summary>

PyPI publishing is planned but not yet available. Use GitHub Releases or install from source for now.

```bash
# When available:
pip install vscode-extension-scanner
```
</details>

---

## Quick Start

**Most common commands:**

```bash
# 👇 Scan all your extensions (beautiful terminal output, 3 workers by default)
vscan scan
```

**✅ Expected output:**
```
╭─────────────────────────────────────────────────╮
│ Scanning 66 extensions...                       │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 100% (1m 15s)   │
│ ✓ 61 from cache | ⟳ 5 refreshed                │
╰─────────────────────────────────────────────────╯

Risk Level  │ Count │ Extensions
─────────────┼───────┼────────────────────────
🔴 Critical  │   0   │ -
🟠 High      │   5   │ extension-a, extension-b...
🟡 Medium    │  12   │ extension-c, extension-d...
🟢 Low       │  49   │ (remaining extensions)

Summary: Found 5 vulnerabilities across 5 extensions
```

```bash
# 👇 Maximum performance with 5 workers (4.27x faster)
vscan scan --workers 5
```

```bash
# 👇 Save results as an interactive HTML report
vscan scan --output report.html
# ✅ Creates: report.html (open in browser for interactive analysis)
```

```bash
# 👇 Minimal output for CI/CD pipelines
vscan scan --quiet
# ✅ Output: "Scanned 66 extensions - Found 5 vulnerabilities"
```

**That's it!** The tool will automatically find your VS Code extensions and analyze them.

**💡 First time?** The first scan takes 1-2 minutes. Subsequent scans are instant (cached).

---

## ✨ Key Features

### 🎯 Easy to Use
- ✅ **Auto-detection** - Finds your VS Code extensions automatically (macOS, Windows, Linux)
- ✅ **Zero config** - Works out of the box, no setup required
- ✅ **Clear results** - Actionable security insights, not just raw data

### ⚡ Fast & Efficient
- 🚀 **Parallel processing** - 4.88x faster than sequential (default: 3 workers)
- 💾 **Smart caching** - 50x faster on repeated scans (typical 70-90% hit rate)
- 🎯 **Respectful** - Built-in rate limiting protects vscan.dev infrastructure

### 🔍 Comprehensive Analysis
- 🛡️ **Security scores** - 0-100 rating for each extension
- ⚠️ **Vulnerability detection** - Known issues in dependencies
- ✓ **Publisher verification** - Trust signals from verified publishers
- 🔐 **Permission analysis** - Network access, file system, etc.

### 📊 Flexible Output

| Format | Best For | Features |
|--------|----------|----------|
| **Terminal** | Daily checks | Color-coded, real-time progress |
| **HTML** | Team reviews | Interactive, sortable, searchable |
| **CSV** | Tracking | Excel/Sheets compatible |
| **JSON** | Automation | Complete data, machine-readable |
| **Quiet** | CI/CD | Single-line summary |

### 🔄 CI/CD Ready
- ✅ Exit codes for pass/fail checks
- ✅ Quiet mode for minimal output
- ✅ Plain text for logs
- ✅ Fast execution with caching

### ⚙️ Configurable
- 💾 Save preferences in `~/.vscanrc`
- 🎛️ Override with command-line flags
- 🔍 Filter by publisher, risk level, or specific extensions
- 🔁 Control retry behavior and delays

---

## 🛡️ Security Highlights

**This tool is built with security as the top priority:**

### ✅ Zero Vulnerabilities Achieved
- **Security Score:** 9.5/10 (improved from 7/10 in v3.5.0)
- **Vulnerabilities:** 0 remaining (100% resolved)
- **Test Coverage:** 78.94% overall, **95%+ for security modules**

### 🔒 Security-First Architecture

| Layer | Protection | Coverage |
|-------|------------|----------|
| **Path Validation** | Blocks directory traversal, URL encoding attacks | 95%+ |
| **String Sanitization** | Context-aware injection prevention | 95%+ |
| **Cache Integrity** | HMAC-SHA256 cryptographic signatures | 100% |
| **Thread Safety** | Race condition elimination | 100% |
| **HTTPS Only** | Certificate validation, no downgrades | 100% |

### 🧪 Comprehensive Testing
- **1,224 tests** - All passing (100% success rate)
- **127 security tests** - Path traversal, injection, integrity, HMAC validation
- **31 property-based tests** - Hypothesis framework generating 1,000+ test scenarios each
- **Parametrized tests** - 62 sanitization tests, 61 path validation tests (data-driven testing)
- **Pre-commit hooks** - Bandit, safety, pip-audit, Semgrep

### 🛡️ Security Measures
- ✅ **No code execution** - Read-only analysis, never modifies extensions
- ✅ **Local caching** - All data stored on your machine, not transmitted
- ✅ **No credentials** - No API keys, tokens, or secrets required
- ✅ **HTTPS only** - All communication encrypted with certificate validation
- ✅ **Fail-fast validation** - Invalid input rejected immediately
- ✅ **Transactional cache** - Ctrl+C safe, preserves progress

**See:** [SECURITY.md](docs/guides/SECURITY.md) for complete security documentation and threat model.

---

## What Gets Analyzed?

For each extension, you'll see:

- **Security Score** (0-100) - Overall security rating
- **Risk Level** - Critical, High, Medium, or Low
- **Vulnerabilities** - Known security issues in the extension or its dependencies
- **Publisher Verification** - Whether the publisher is verified
- **Risk Factors** - Network access, file system permissions, etc.
- **Dependencies** - Third-party packages and their security status

---

## Common Use Cases

### 1. Personal Security Audit (5-10 minutes)

Scan all your extensions to identify potential risks:

```bash
# 👇 Get a comprehensive view of all your extensions
vscan scan

# 👇 Focus on high-risk extensions only
vscan scan --min-risk-level high

# 👇 Save a report you can review later
vscan scan --output security-audit.html
```

### 2. Team Security Review (15-30 minutes)

Share security findings with your team:

```bash
# 👇 Generate a shareable HTML report
vscan scan --output team-report.html

# 👇 Export to CSV for tracking in spreadsheets
vscan scan --output security-tracking.csv

# 👇 Filter by publisher to audit specific vendors
vscan scan --publisher microsoft --output ms-extensions.html
```

### 3. CI/CD Integration (2-5 minutes to set up)

Add security checks to your build pipeline:

```bash
# 👇 Fail the build if high-risk extensions are found
vscan scan --quiet --min-risk-level high
if [ $? -eq 1 ]; then
  echo "High-risk extensions detected!"
  exit 1
fi

# 👇 Generate reports as build artifacts
vscan scan --output ci-report.html --plain
```

### 4. Regular Security Monitoring (Daily/Weekly)

Set up periodic scans with cached results:

```bash
# 👇 Quick daily check (uses cache, instant results)
vscan scan

# 👇 Weekly deep scan (refresh all data)
vscan scan --refresh-cache --output weekly-report.html

# 👇 View trends with cache statistics
vscan cache stats
```

---

## 📊 Output Formats

Choose the format that works best for you:

### Terminal Output (Default)

Beautiful, color-coded tables displayed right in your terminal:

```bash
# 👇 Copy and run this command
vscan scan
```

**What you'll see:**

```
╭───────────────────────────────────────────────────────────╮
│ Extension Security Scan Results                           │
├───────────────────────────────────────────────────────────┤
│ Extension Name         │ Risk   │ Score │ Verified │ Vulns│
├────────────────────────┼────────┼───────┼──────────┼──────┤
│ Python                 │ 🟢 Low │  85   │    ✓     │  0   │
│ ESLint                 │ 🟡 Med │  65   │    ✓     │  2   │
│ Docker                 │ 🟠 High│  45   │    ✓     │  5   │
╰────────────────────────┴────────┴───────┴──────────┴──────╯
```

Features:
- ✅ Color-coded risk levels (red for critical/high, yellow for medium, green for low)
- ✅ Verified publisher checkmarks
- ✅ Real-time progress bars with ETA
- ✅ Cache indicators showing fresh vs. cached results
- ✅ Summary statistics and recommendations

### HTML Reports

Interactive reports you can share and explore:

```bash
# 👇 Copy and run this command
vscan scan --output report.html
```

Features:
- ✅ Sortable tables (click any column header)
- ✅ Search and filter extensions
- ✅ Data visualizations (pie charts, gauges, bar charts)
- ✅ Expandable rows with detailed security analysis
- ✅ Print-ready formatting
- ✅ Works offline (no external dependencies)

**Perfect for:** Team reviews, documentation, presentations

### CSV Export

Spreadsheet-compatible format for data analysis:

```bash
# 👇 Copy and run this command
vscan scan --output results.csv
```

Features:
- ✅ 15 columns of security data
- ✅ Works with Excel, Google Sheets, LibreOffice
- ✅ Easy integration with other tools
- ✅ Track changes over time

**Perfect for:** Dashboards, tracking, data analysis

### JSON Output

Complete data for programmatic use:

```bash
# 👇 Copy and run this command
vscan scan --output results.json
```

Features:
- ✅ All available security details
- ✅ Dependency lists
- ✅ Risk factor breakdowns
- ✅ Publisher information
- ✅ Machine-readable format

**Perfect for:** Automation, custom tools, data processing

### Quiet Mode

Minimal single-line output for scripts:

```bash
# 👇 Copy and run this command
vscan scan --quiet
```

**Output:** `Scanned 66 extensions - Found 5 vulnerabilities`

**Perfect for:** CI/CD, monitoring scripts, automated alerts

---

## 🔧 All Commands

### Basic Scanning

```bash
# 👇 Scan all extensions
vscan scan

# 👇 Save to file (format detected from extension)
vscan scan --output report.html    # HTML report
vscan scan --output results.json   # JSON data
vscan scan --output results.csv    # CSV spreadsheet

# 👇 Control output style
vscan scan --quiet                 # Minimal single-line output
vscan scan --plain                 # No colors (for logs)
```

### Filtering

```bash
# 👇 Filter by publisher
vscan scan --publisher microsoft

# 👇 Filter by risk level
vscan scan --min-risk-level high   # Only show high/critical

# 👇 Scan specific extensions
vscan scan --include-ids "ms-python.python,GitHub.copilot"

# 👇 Exclude extensions
vscan scan --exclude-ids "local.test-extension"
```

### Performance Control

```bash
# 👇 Adjust worker count (1-5 workers)
vscan scan --workers 5             # Maximum performance
vscan scan --workers 1             # Sequential mode (debugging)
vscan scan --workers 3             # Default (balanced)
```

### Caching

```bash
# 👇 View cache information
vscan cache stats

# 👇 Clear cache
vscan cache clear                  # With confirmation prompt
vscan cache clear --force          # Skip confirmation

# 👇 Control cache behavior during scan
vscan scan --refresh-cache         # Update scanned extensions
vscan scan --no-cache              # Disable cache entirely
vscan scan --cache-max-age 30      # Custom expiry (days)
```

### Reports from Cache

Generate reports instantly from cached data without making API calls:

```bash
# 👇 Generate reports from cache
vscan report security-report.html  # HTML report
vscan report data-export.json      # JSON export
vscan report analysis.csv          # CSV export
```

### Configuration

Save your preferences so you don't have to repeat them:

```bash
# 👇 Create config file with defaults
vscan config init

# 👇 View current settings
vscan config show

# 👇 Set a preference
vscan config set scan.delay 2.0
vscan config set scan.workers 5
vscan config set cache.max_age 14
vscan config set output.quiet true

# 👇 Get a specific setting
vscan config get scan.delay

# 👇 Remove config file
vscan config reset
```

### Advanced Options

```bash
# 👇 Custom VS Code extensions directory
vscan scan --extensions-dir /custom/path

# 👇 Adjust API request timing
vscan scan --delay 2.0             # Delay between requests (seconds)

# 👇 Control retry behavior
vscan scan --max-retries 5         # More retry attempts
vscan scan --retry-delay 3.0       # Longer retry delays
vscan scan --max-retries 0         # Disable retries

# 👇 Custom cache location
vscan scan --cache-dir /custom/cache/path
```

### Help

```bash
# 👇 General help
vscan --help

# 👇 Command-specific help
vscan scan --help
vscan cache --help
vscan config --help
vscan report --help

# 👇 Version information
vscan --version
```

---

## ⚙️ Configuration File

Save your preferred settings in `~/.vscanrc`:

```ini
[scan]
delay = 2.0
max_retries = 3
retry_delay = 2.0
workers = 3

[cache]
max_age = 14

[output]
quiet = false
plain = false
```

Create a default config file:
```bash
# 👇 Copy and run this command
vscan config init
```

**Note:** Command-line arguments always override config file settings.

---

## 🚨 Exit Codes

The tool returns standard exit codes for easy integration with scripts:

- **0** - Success, no vulnerabilities found
- **1** - Success, but vulnerabilities were found
- **2** - Scan failed due to an error

Example usage:
```bash
# 👇 Copy and run this command
vscan scan --quiet
if [ $? -eq 1 ]; then
  echo "Security issues detected!"
  exit 1
fi
```

---

## 🔧 Troubleshooting

### "No extensions found"

Make sure VS Code is installed and you have extensions installed:
```bash
# 👇 Check if VS Code extensions directory exists
ls ~/.vscode/extensions/

# 👇 Specify custom directory if needed
vscan scan --extensions-dir /path/to/extensions
```

### Slow scans

Use caching to speed up repeated scans:
```bash
# 👇 First scan will be slower (API calls)
vscan scan

# 👇 Subsequent scans use cache (50x faster)
vscan scan

# 👇 Extend cache age to reduce API calls
vscan config set cache.max_age 30
```

### Rate limiting errors

The tool handles rate limiting automatically, but you can adjust:
```bash
# 👇 Increase delay between requests
vscan scan --delay 2.0

# 👇 Increase retry attempts
vscan scan --max-retries 5

# 👇 Increase retry delay
vscan scan --retry-delay 3.0
```

### No colors in terminal

Colors are automatically disabled in non-interactive environments. To force plain output:
```bash
# 👇 Copy and run this command
vscan scan --plain
```

### Cache issues

Clear the cache if you're seeing stale or incorrect data:
```bash
# 👇 Copy and run this command
vscan cache clear --force
```

---

## 📰 What's New

<details open>
<summary><strong>Version 5.0.2 - Test Quality Improvements (Latest)</strong></summary>

- **Test parametrization**: Refactored repetitive tests to use pytest parametrization
  - `test_input_validators.py`: 40 → 62 tests (+55%), 756 → 404 lines (-46.6% duplication)
  - `test_path_validation.py`: 51 → 61 tests (+19.6%), improved maintainability
  - Benefits: Reduced code duplication, clearer test output, easier to add new test cases
- **Property-based testing**: Added comprehensive Hypothesis property tests
  - NEW: `test_property_sanitization.py` (16 property tests for string sanitization)
  - NEW: `test_property_path_validation.py` (15 property tests for path validation)
  - Automatically generates 1,000+ test cases per test to find edge cases
  - Found and documented edge cases with xfail markers (whitespace paths, control characters)
- **Test metrics**: 1,153 total tests (was 1,121, +32), 98.3% pass rate (1,134 passed, 19 skipped)
- **Documentation**: Added cache directory testing patterns to prevent regressions
- See CHANGELOG.md for complete v5.0.2 improvements
</details>

<details>
<summary><strong>Version 5.0.1 - CLI Cleanup & Version Bump</strong></summary>

- **CLI cleanup**: Removed deprecated --parallel flag (parallel processing is default since v3.5.0)
- **Version bump**: Updated to v5.0.1 for schema version alignment
- **Maintenance**: Code cleanup and deprecation removal
</details>

<details>
<summary><strong>Version 5.0.0 - Database Optimization & Schema Redesign</strong></summary>

- **Database schema v5.0**: Redesigned for performance and flexibility
  - Removed scan_date primary key (fixes cache integrity issues)
  - Added analysis_id for unique scan identification
  - Improved timestamp handling and data retrieval
- **Cache optimization**: 87.6% faster database operations
- **Test improvements**: Enhanced cache integrity and tampering detection tests
- **Breaking change**: Requires cache clear on upgrade (schema incompatible with v4.x)
- See CHANGELOG.md for migration guide and complete v5.0.0 improvements
</details>

<details>
<summary><strong>Version 3.6.0 - Coverage Improvement & Testability Refactoring</strong></summary>

- **Coverage improvement**: 77.83% → 78.94% (+1.11%, exceeds 75% target by 5.3%)
- **scanner.py improvement**: 64.91% → 71.03% (+6.12%)
- **Test count**: 779 → 831 (+52 high-quality tests)
- **Testability refactoring**: 4-phase architectural improvements
  - Phase 1: ProgressCallback pattern (+1.43% coverage, 13 tests)
  - Phase 2: CLI business logic extraction (+0.25% coverage, 13 tests)
  - Phase 3: Legacy migration removal (+0.56% coverage, -160 lines)
  - Phase 4: Retry logic simplification (+0.02% coverage, 9 tests)
- **Benefits**: Business logic now testable without Rich/Typer frameworks
- See CHANGELOG.md for complete v3.6.0 improvements
</details>

<details>
<summary><strong>Version 3.5.6 - Automated Release Workflow</strong></summary>

- **GitHub Actions automation** - Automatic distribution builds on version tags
- **Release efficiency** - 38% reduction in release time
- **Improved changelog extraction** - Better release notes generation
- **CI/CD maturity** - Comprehensive automated release pipeline
</details>

<details>
<summary><strong>Version 3.5.1 - Security Hardening & Technical Debt Cleanup</strong></summary>

- **Security score improved from 7/10 to 9.5/10** (0 vulnerabilities remaining)
- Unified path validation blocking URL-encoded traversal and system directories
- Context-aware string sanitization for all user-facing output
- HMAC cache integrity with cryptographic signatures (prevents tampering)
- Thread-safe statistics collection (eliminates race conditions)
- Transactional cache writes with interrupt handling (preserves progress on Ctrl+C)
- Comprehensive security test suite (35+ new tests, 95% coverage)
- See CHANGELOG.md for complete security improvements
</details>

<details>
<summary><strong>Version 3.5.0 - Parallel Processing by Default 🚨 BREAKING CHANGES</strong></summary>

- **Parallel processing is now the default** (4.88x faster automatically!)
- Configurable worker count (1-5 workers, default: 3)
- Breaking change: Removed `--parallel` flag (no longer needed)
- Breaking change: Use `--workers 1` for sequential behavior
- Simplified API: Single code path, ~100 lines of code eliminated
- Real-world impact: 66 extensions from 6 minutes → 1.2 minutes (by default)
- Thread-safe SQLite implementation
</details>

<details>
<summary><strong>Version 3.1.0 - Configuration & CSV Export</strong></summary>

- Configuration file support with `~/.vscanrc`
- Config management commands (`init`, `show`, `set`, `get`, `reset`)
- CSV export format for spreadsheet analysis
- Performance improvements (87.6% faster database operations)
- Better error handling and user experience
</details>

<details>
<summary><strong>Version 3.0.0 - Modern CLI Overhaul</strong></summary>

- Beautiful terminal UI with Rich library
- Organized subcommands (scan, cache, report, config)
- Always comprehensive scans (no more modes)
- Improved filtering options
- Cache-based report generation
- Refined cache refresh behavior
</details>

<details>
<summary><strong>Version 2.2.0 - HTML Reports & Retry Mechanism</strong></summary>

- Interactive HTML reports with charts and tables
- Intelligent retry mechanism for API resilience
- Exponential backoff with jitter
- Retry statistics tracking
</details>

---

## 🔬 Technical Details

### How It Works

1. **Discovery** - Automatically locates your VS Code extensions directory
2. **Analysis** - Queries vscan.dev API for security analysis of each extension
3. **Caching** - Stores results in SQLite database for fast repeated scans
4. **Reporting** - Formats results in your preferred output format

### Performance

**Real-world benchmark** (66 extensions scan):

| Mode | Time | Speed vs v3.4 | Speed vs Sequential |
|------|------|---------------|---------------------|
| **Sequential (1 worker)** | 6 min 6s | 1.0x (baseline) | 1.0x |
| **Default (3 workers)** | 1 min 15s | **4.88x faster** | **4.88x faster** |
| **Maximum (5 workers)** | 1 min 26s | **4.27x faster** | **4.27x faster** |
| **Cached scan** | < 1 second | **366x faster** | **366x faster** |

**Per-extension performance:**
- **Default (3 workers):** ~0.3 seconds per extension
- **Sequential (1 worker):** ~1.5 seconds per extension
- **Maximum (5 workers):** ~0.35 seconds per extension
- **Cached:** Instant (< 0.01s per extension)

**Resource usage:**
- **Memory:** < 100MB RAM
- **Cache hit rate:** 70-90% (typical usage)
- **API calls saved:** 70-90% reduction after first scan

### Security Data Sources

**All security analysis is powered by [vscan.dev](https://vscan.dev)**, an excellent VS Code extension security analysis service.

This tool would not exist without vscan.dev's infrastructure. vscan.dev provides comprehensive analysis including:
- Extension source code and permissions review
- Third-party dependencies and known vulnerabilities detection
- Publisher reputation and verification status validation
- Network access patterns analysis
- File system permissions auditing
- Security scoring and risk level assessment

**We are deeply grateful to vscan.dev** for providing their public API, which makes this tool possible. This tool serves as a complementary CLI client to vscan.dev's analysis capabilities.

### Privacy

- ✅ No data is collected by this tool
- ✅ All analysis is performed by vscan.dev
- ✅ Cache is stored locally on your machine
- ✅ No credentials or secrets are transmitted

### API Usage & Respectful Practices

This tool implements multiple measures to minimize load on vscan.dev's infrastructure while providing excellent user experience:

**Rate Limiting**:
- Default 2.0s delay between API requests (configurable 1.0-5.0s)
- Prevents API overload and respects server resources
- Applied automatically across all worker threads

**Intelligent Caching**:
- 70-90% cache hit rate in typical usage
- 14-day default cache expiration (configurable)
- Reduces API calls by 70-90% after initial scan
- Makes repeated scans 50x faster (instant from cache)
- SQLite database with HMAC integrity protection

**Exponential Backoff Retry**:
- Maximum 3 retry attempts (configurable)
- Exponential delays: 2s → 4s → 8s with random jitter
- Prevents hammering API during temporary failures
- Graceful handling of network issues

**Thread-Safe Implementation**:
- 3 workers by default (configurable 1-5)
- Isolated API client per worker
- Thread-safe statistics collection
- Conservative parallelism respects rate limits

**Transparent Identification**:
- User-Agent: `VSCodeExtensionScanner/3.5.6 (+https://github.com/jvlivonius/vsc-extension-scanner)`
- Enables vscan.dev to identify and monitor tool usage
- Professional API etiquette

**Security**:
- HTTPS-only communication with certificate validation
- No circumvention of rate limits or access controls
- No attempt to bypass authentication (none required)

**Typical Impact**: Average user generates 100-200 API requests per month (vs 2,000+ without caching).

For complete details on ethical API usage, see [ATTRIBUTION.md](ATTRIBUTION.md).

### Platform Support

- ✅ macOS
- ✅ Windows
- ✅ Linux

The tool automatically detects your platform and finds the VS Code extensions directory.

---

## ❓ FAQ

### Getting Started

<details>
<summary><strong>Q: Is this tool official from Microsoft or VS Code?</strong></summary>

**A:** No, this is an independent security tool that uses the vscan.dev API. It's not affiliated with Microsoft, VS Code, or vscan.dev.
</details>

<details>
<summary><strong>Q: Will this slow down my VS Code?</strong></summary>

**A:** No, this is a standalone CLI tool that doesn't affect VS Code performance. It runs separately and only reads your extensions directory.
</details>

<details>
<summary><strong>Q: Does it modify my extensions?</strong></summary>

**A:** No, this tool is read-only. It only analyzes extensions, never modifies them.
</details>

### Usage & Best Practices

<details>
<summary><strong>Q: How often should I scan?</strong></summary>

**A:** Weekly scans are recommended. Use caching for daily checks without API overhead:
- **Daily:** `vscan scan` (uses cache, instant)
- **Weekly:** `vscan scan --refresh-cache` (full scan, 1-2 minutes)
</details>

<details>
<summary><strong>Q: Can I use this in my company's security workflow?</strong></summary>

**A:** Yes! The tool supports:
- ✅ CI/CD integration with exit codes
- ✅ JSON output for automated processing
- ✅ CSV export for compliance tracking
- ✅ HTML reports for audits and documentation
</details>

### Understanding Results

<details>
<summary><strong>Q: What does a "high risk" rating mean?</strong></summary>

**A:** It indicates potential security concerns such as:
- Network access to external servers
- Elevated file system permissions
- Known vulnerabilities in dependencies
- Unverified publisher

Always review the detailed analysis to assess actual risk for your use case.
</details>

<details>
<summary><strong>Q: Are verified publishers always safe?</strong></summary>

**A:** Verification confirms identity but doesn't guarantee security. A verified publisher means:
- ✅ Identity verified by marketplace
- ✅ Established track record
- ❌ Not a security audit

Always review the security analysis regardless of verification status.
</details>

### Technical Questions

<details>
<summary><strong>Q: What data is collected about me?</strong></summary>

**A:** **None.** This tool:
- 🚫 Does not collect any user data
- 🚫 Does not send your extension list anywhere
- 🚫 Does not track usage or analytics
- ✅ Only queries vscan.dev API for public extension data
- ✅ Stores cache locally on your machine
</details>

<details>
<summary><strong>Q: Why does the first scan take longer?</strong></summary>

**A:** The first scan makes API calls to vscan.dev for each extension. Subsequent scans use cached results (14-day default) which are instant.

**Performance:**
- First scan: 1-2 minutes (66 extensions)
- Cached scan: < 1 second (instant!)
- Cache hit rate: 70-90% typical
</details>

---

## ⚠️ Disclaimer

**IMPORTANT LEGAL NOTICE**

This is an **unofficial, community-maintained tool**. It is **NOT affiliated with, endorsed by, or sponsored by vscan.dev** or any related organizations.

### What This Means

- This project is an independent, open-source CLI tool
- We are not part of the vscan.dev team or organization
- We use vscan.dev's publicly accessible API to provide security analysis
- We do not represent vscan.dev in any official capacity

### Our Commitment

**If vscan.dev requests that we cease using their API, we will comply immediately.**

We respect vscan.dev's rights and will:
- Stop all API usage if requested
- Remove or archive the project as needed
- Cooperate fully with reasonable requests

### No Warranty

This software is provided "as-is" under the MIT License with no warranties of any kind, express or implied. See the [LICENSE](LICENSE) file for complete terms.

### Attribution

**All security analysis is powered by [vscan.dev](https://vscan.dev).** We are deeply grateful to vscan.dev for providing their public API, which makes this tool possible.

For complete legal and attribution information, see [ATTRIBUTION.md](ATTRIBUTION.md).

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- 🐛 Report bugs or request features via [GitHub Issues](https://github.com/jvlivonius/vsc-extension-scanner/issues)
- 🔧 Submit pull requests for improvements
- 💬 Share your experience and use cases
- 📝 Help improve documentation

**For development setup, see the [CONTRIBUTING.md](CONTRIBUTING.md) guide.**

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

This tool is made possible by:

- **[vscan.dev](https://vscan.dev)** - Powers all security analysis functionality through their excellent API. This tool would not exist without vscan.dev's infrastructure and analysis capabilities. We are deeply grateful for their public API.
- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal formatting library
- **[Typer](https://github.com/tiangolo/typer)** - Modern CLI framework
- **The VS Code extension community** - For creating the extensions that make VS Code powerful

### Special Thanks to vscan.dev

vscan.dev provides the core security analysis engine that powers this tool:
- Comprehensive extension source code analysis
- Dependency vulnerability detection
- Publisher verification and reputation assessment
- Risk scoring and security metrics
- Reliable, fast API infrastructure

**We strongly encourage users to visit [vscan.dev](https://vscan.dev)** directly to explore their full range of security analysis features and services.

---

## 🚀 Next Steps

**Ready to secure your VS Code environment?**

1. **⬇️ Install:** [Download from GitHub Releases](https://github.com/jvlivonius/vsc-extension-scanner/releases/latest)
2. **▶️ Run:** `vscan scan` to audit your extensions
3. **📊 Review:** Check high-risk extensions and vulnerabilities
4. **🔄 Schedule:** Set up weekly scans for ongoing security

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

**Found a security issue?** Please report privately via [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new).

**Questions?** Open an [issue](https://github.com/jvlivonius/vsc-extension-scanner/issues) or check the [FAQ](#-faq).

**Like this tool?** ⭐ Star this repo to show your support!

---

## 🔗 Links

- **GitHub:** [vsc-extension-scanner](https://github.com/jvlivonius/vsc-extension-scanner)
- **Documentation:** [docs/](docs/)
- **Issues & Support:** [GitHub Issues](https://github.com/jvlivonius/vsc-extension-scanner/issues)
- **Security:** [SECURITY.md](docs/guides/SECURITY.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **vscan.dev:** [https://vscan.dev](https://vscan.dev)

---

**Made with care for the developer community. Stay secure! 🛡️**
