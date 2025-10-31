# VS Code Extension Security Scanner

**Know what's running in your editor. Stay secure.**

A command-line tool that scans your installed VS Code extensions for security vulnerabilities, suspicious permissions, and risky dependencies. Get instant insights into the security posture of your development environment.

**Version:** 3.5.5 | **Status:** Production Ready

<!-- Test line for branch protection validation - contributor workflow simulation -->

---

## Why Use This Tool?

VS Code extensions have broad access to your code, files, and development environment. A malicious or vulnerable extension could:

- Access your source code and secrets
- Modify files without your knowledge
- Send data to external servers
- Introduce vulnerable dependencies

**This tool helps you:**

- Identify high-risk extensions before they cause problems
- Audit your entire extension collection in minutes
- Track security issues across your development team
- Make informed decisions about which extensions to trust

---

## Installation

**Requirements:** Python 3.8 or higher

```bash
# Install from PyPI (recommended)
pip install vscode-extension-scanner

# Verify installation
vscan --version
```

<details>
<summary>Install from source (for developers)</summary>

```bash
git clone https://github.com/username/vsc-extension-scanner.git
cd vsc-extension-scanner
pip install -e .
```
</details>

---

## Quick Start

**Most common commands:**

```bash
# Scan all your extensions (beautiful terminal output, 3 workers by default)
vscan scan

# Maximum performance with 5 workers (5x faster)
vscan scan --workers 5

# Save results as an interactive HTML report
vscan scan --output report.html

# Minimal output for CI/CD pipelines
vscan scan --quiet
```

That's it! The tool will automatically find your VS Code extensions and analyze them.

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

### 1. Personal Security Audit

Scan all your extensions to identify potential risks:

```bash
# Get a comprehensive view of all your extensions
vscan scan

# Focus on high-risk extensions only
vscan scan --min-risk-level high

# Save a report you can review later
vscan scan --output security-audit.html
```

### 2. Team Security Review

Share security findings with your team:

```bash
# Generate a shareable HTML report
vscan scan --output team-report.html

# Export to CSV for tracking in spreadsheets
vscan scan --output security-tracking.csv

# Filter by publisher to audit specific vendors
vscan scan --publisher microsoft --output ms-extensions.html
```

### 3. CI/CD Integration

Add security checks to your build pipeline:

```bash
# Fail the build if high-risk extensions are found
vscan scan --quiet --min-risk-level high
if [ $? -eq 1 ]; then
  echo "High-risk extensions detected!"
  exit 1
fi

# Generate reports as build artifacts
vscan scan --output ci-report.html --plain
```

### 4. Regular Security Monitoring

Set up periodic scans with cached results:

```bash
# Quick daily check (uses cache, instant results)
vscan scan

# Weekly deep scan (refresh all data)
vscan scan --refresh-cache --output weekly-report.html

# View trends with cache statistics
vscan cache stats
```

---

## Output Formats

Choose the format that works best for you:

### Terminal Output (Default)

Beautiful, color-coded tables displayed right in your terminal:

```bash
vscan scan
```

Features:
- Color-coded risk levels (red for critical/high, yellow for medium, green for low)
- Verified publisher checkmarks
- Real-time progress bars
- Cache indicators showing fresh vs. cached results
- Summary statistics

### HTML Reports

Interactive reports you can share and explore:

```bash
vscan scan --output report.html
```

Features:
- Sortable tables (click any column header)
- Search and filter extensions
- Data visualizations (pie charts, gauges, bar charts)
- Expandable rows with detailed security analysis
- Print-ready formatting
- Works offline (no external dependencies)

Perfect for: Team reviews, documentation, presentations

### CSV Export

Spreadsheet-compatible format for data analysis:

```bash
vscan scan --output results.csv
```

Features:
- 15 columns of security data
- Works with Excel, Google Sheets, LibreOffice
- Easy integration with other tools
- Track changes over time

Perfect for: Dashboards, tracking, data analysis

### JSON Output

Complete data for programmatic use:

```bash
vscan scan --output results.json
```

Features:
- All available security details
- Dependency lists
- Risk factor breakdowns
- Publisher information
- Machine-readable format

Perfect for: Automation, custom tools, data processing

### Quiet Mode

Minimal single-line output for scripts:

```bash
vscan scan --quiet
```

Output: `Scanned 66 extensions - Found 5 vulnerabilities`

Perfect for: CI/CD, monitoring scripts, automated alerts

---

## Key Features

**Easy to Use**
- Auto-detects your VS Code extensions (macOS, Windows, Linux)
- No configuration required to get started
- Clear, actionable results

**Fast & Efficient**
- Smart caching makes repeated scans 50x faster
- Typical cache hit rate: 70-90%
- Respectful of API rate limits

**Comprehensive Analysis**
- Security scores and risk levels
- Vulnerability detection in dependencies
- Publisher verification status
- Permission and access analysis

**Flexible Output**
- Terminal (with colors and tables)
- HTML (interactive reports)
- CSV (spreadsheet compatible)
- JSON (programmatic access)

**CI/CD Ready**
- Quiet mode for minimal output
- Exit codes for pass/fail checks
- Plain text for logs
- Fast execution with caching

**Configurable**
- Save preferences in `~/.vscanrc`
- Override with command-line flags
- Filter by publisher, risk level, or specific extensions
- Control retry behavior and delays

---

## All Commands

### Basic Scanning

```bash
# Scan all extensions
vscan scan

# Save to file (format detected from extension)
vscan scan --output report.html    # HTML report
vscan scan --output results.json   # JSON data
vscan scan --output results.csv    # CSV spreadsheet

# Control output style
vscan scan --quiet                 # Minimal single-line output
vscan scan --plain                 # No colors (for logs)
```

### Filtering

```bash
# Filter by publisher
vscan scan --publisher microsoft

# Filter by risk level
vscan scan --min-risk-level high   # Only show high/critical

# Scan specific extensions
vscan scan --include-ids "ms-python.python,GitHub.copilot"

# Exclude extensions
vscan scan --exclude-ids "local.test-extension"
```

### Caching

```bash
# View cache information
vscan cache stats

# Clear cache
vscan cache clear                  # With confirmation prompt
vscan cache clear --force          # Skip confirmation

# Control cache behavior during scan
vscan scan --refresh-cache         # Update scanned extensions
vscan scan --no-cache              # Disable cache entirely
vscan scan --cache-max-age 30      # Custom expiry (days)
```

### Reports from Cache

Generate reports instantly from cached data without making API calls:

```bash
vscan report security-report.html  # HTML report
vscan report data-export.json      # JSON export
vscan report analysis.csv          # CSV export
```

### Configuration

Save your preferences so you don't have to repeat them:

```bash
# Create config file with defaults
vscan config init

# View current settings
vscan config show

# Set a preference
vscan config set scan.delay 2.0
vscan config set cache.max_age 14
vscan config set output.quiet true

# Get a specific setting
vscan config get scan.delay

# Remove config file
vscan config reset
```

### Advanced Options

```bash
# Custom VS Code extensions directory
vscan scan --extensions-dir /custom/path

# Adjust API request timing
vscan scan --delay 2.0             # Delay between requests (seconds)

# Control retry behavior
vscan scan --max-retries 5         # More retry attempts
vscan scan --retry-delay 3.0       # Longer retry delays
vscan scan --max-retries 0         # Disable retries

# Custom cache location
vscan scan --cache-dir /custom/cache/path
```

### Help

```bash
# General help
vscan --help

# Command-specific help
vscan scan --help
vscan cache --help
vscan config --help
vscan report --help

# Version information
vscan --version
```

---

## Configuration File

Save your preferred settings in `~/.vscanrc`:

```ini
[scan]
delay = 2.0
max_retries = 3
retry_delay = 2.0

[cache]
max_age = 14

[output]
quiet = false
plain = false
```

Create a default config file:
```bash
vscan config init
```

**Note:** Command-line arguments always override config file settings.

---

## Exit Codes

The tool returns standard exit codes for easy integration with scripts:

- **0** - Success, no vulnerabilities found
- **1** - Success, but vulnerabilities were found
- **2** - Scan failed due to an error

Example usage:
```bash
vscan scan --quiet
if [ $? -eq 1 ]; then
  echo "Security issues detected!"
  exit 1
fi
```

---

## Troubleshooting

### "No extensions found"

Make sure VS Code is installed and you have extensions installed:
```bash
# Check if VS Code extensions directory exists
ls ~/.vscode/extensions/

# Specify custom directory if needed
vscan scan --extensions-dir /path/to/extensions
```

### Slow scans

Use caching to speed up repeated scans:
```bash
# First scan will be slower (API calls)
vscan scan

# Subsequent scans use cache (50x faster)
vscan scan

# Extend cache age to reduce API calls
vscan config set cache.max_age 30
```

### Rate limiting errors

The tool handles rate limiting automatically, but you can adjust:
```bash
# Increase delay between requests
vscan scan --delay 2.0

# Increase retry attempts
vscan scan --max-retries 5

# Increase retry delay
vscan scan --retry-delay 3.0
```

### No colors in terminal

Colors are automatically disabled in non-interactive environments. To force plain output:
```bash
vscan scan --plain
```

### Cache issues

Clear the cache if you're seeing stale or incorrect data:
```bash
vscan cache clear --force
```

---

## What's New

<details open>
<summary>Version 3.5.1 - Security Hardening & Technical Debt Cleanup</summary>

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
<summary>Version 3.5.0 - Parallel Processing by Default 🚨 BREAKING CHANGES</summary>

- **Parallel processing is now the default** (4.88x faster automatically!)
- Configurable worker count (1-5 workers, default: 3)
- Breaking change: Removed `--parallel` flag (no longer needed)
- Breaking change: Use `--workers 1` for sequential behavior
- Simplified API: Single code path, ~100 lines of code eliminated
- Real-world impact: 66 extensions from 6 minutes → 1.2 minutes (by default)
- Thread-safe SQLite implementation
</details>

<details>
<summary>Version 3.1.0 - Configuration & CSV Export</summary>

- Configuration file support with `~/.vscanrc`
- Config management commands (`init`, `show`, `set`, `get`, `reset`)
- CSV export format for spreadsheet analysis
- Performance improvements (87.6% faster database operations)
- Better error handling and user experience
</details>

<details>
<summary>Version 3.0.0 - Modern CLI Overhaul</summary>

- Beautiful terminal UI with Rich library
- Organized subcommands (scan, cache, report, config)
- Always comprehensive scans (no more modes)
- Improved filtering options
- Cache-based report generation
- Refined cache refresh behavior
</details>

<details>
<summary>Version 2.2.0 - HTML Reports & Retry Mechanism</summary>

- Interactive HTML reports with charts and tables
- Intelligent retry mechanism for API resilience
- Exponential backoff with jitter
- Retry statistics tracking
</details>

---

## Technical Details

### How It Works

1. **Discovery** - Automatically locates your VS Code extensions directory
2. **Analysis** - Queries vscan.dev API for security analysis of each extension
3. **Caching** - Stores results in SQLite database for fast repeated scans
4. **Reporting** - Formats results in your preferred output format

### Performance

- **Default (3 workers):** ~0.3 seconds per extension (4.88x faster than v3.4)
- **Sequential mode (1 worker):** ~1.5 seconds per extension (API rate limiting)
- **Maximum (5 workers):** ~0.35 seconds per extension (4.27x faster)
- **Cached scans:** Instant (50x faster)
- **Memory usage:** < 100MB RAM
- **Typical cache hit rate:** 70-90%

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

- No data is collected by this tool
- All analysis is performed by vscan.dev
- Cache is stored locally on your machine
- No credentials or secrets are transmitted

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
- User-Agent: `VSCodeExtensionScanner/3.5.3 (+https://github.com/username/vsc-extension-scanner)`
- Enables vscan.dev to identify and monitor tool usage
- Professional API etiquette

**Security**:
- HTTPS-only communication with certificate validation
- No circumvention of rate limits or access controls
- No attempt to bypass authentication (none required)

**Typical Impact**: Average user generates 100-200 API requests per month (vs 2,000+ without caching).

For complete details on ethical API usage, see [docs/project/ATTRIBUTION.md](docs/project/ATTRIBUTION.md).

### Platform Support

- macOS
- Windows
- Linux

The tool automatically detects your platform and finds the VS Code extensions directory.

---

## FAQ

**Q: Is this tool official from Microsoft or VS Code?**
A: No, this is an independent security tool that uses the vscan.dev API.

**Q: Will this slow down my VS Code?**
A: No, this is a standalone CLI tool that doesn't affect VS Code performance.

**Q: Does it modify my extensions?**
A: No, this tool is read-only. It only analyzes extensions, never modifies them.

**Q: How often should I scan?**
A: Weekly scans are recommended. Use caching for daily checks without API overhead.

**Q: Can I use this in my company's security workflow?**
A: Yes! The tool supports CI/CD integration, JSON output, and CSV export for compliance tracking.

**Q: What does a "high risk" rating mean?**
A: It indicates potential security concerns like network access, elevated permissions, or vulnerable dependencies. Review the details to assess actual risk.

**Q: Are verified publishers always safe?**
A: Verification confirms identity but doesn't guarantee security. Always review the security analysis.

---

## Disclaimer

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

For complete legal and attribution information, see [docs/project/ATTRIBUTION.md](docs/project/ATTRIBUTION.md).

---

## Contributing

Contributions are welcome! Here's how you can help:

- Report bugs or request features via [GitHub Issues](https://github.com/username/vsc-extension-scanner/issues)
- Submit pull requests for improvements
- Share your experience and use cases
- Help improve documentation

For development setup, see the [CONTRIBUTING.md](CONTRIBUTING.md) guide.

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

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

## Links

- **GitHub:** [vsc-extension-scanner](https://github.com/username/vsc-extension-scanner)
- **Documentation:** [docs/](docs/)
- **Issues & Support:** [GitHub Issues](https://github.com/username/vsc-extension-scanner/issues)
- **vscan.dev:** [https://vscan.dev](https://vscan.dev)

---

**Made with care for the developer community. Stay secure!**
