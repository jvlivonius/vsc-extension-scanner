# VS Code Extension Security Scanner

**Know what's running in your editor. Stay secure.**

A command-line tool that scans your installed VS Code extensions for security vulnerabilities, suspicious permissions, and risky dependencies. Get instant insights into the security posture of your development environment.

**Version:** 3.4.0 | **Status:** Production Ready

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
# Scan all your extensions (beautiful terminal output)
vscan scan

# Fast parallel scanning (2-5x faster, recommended for large extension sets)
vscan scan --parallel

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
<summary>Version 3.4.0 - Parallel Scanning Performance Boost</summary>

- Parallel scanning with `--parallel` flag (2-5x faster)
- Configurable worker count (2-5 workers, default: 3)
- 4.88x speedup validated with 3 workers
- Real-world impact: 66 extensions from 6 minutes → 1.2 minutes
- Thread-safe implementation with SQLite cache
- Configuration file support for parallel settings
- Works with both Rich and plain output modes
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

- **Parallel mode (3 workers):** ~0.3 seconds per extension (4.88x faster)
- **Sequential mode:** ~1.5 seconds per extension (API rate limiting)
- **Cached scans:** Instant (50x faster)
- **Memory usage:** < 100MB RAM
- **Typical cache hit rate:** 70-90%

### Security Data Sources

All security analysis is provided by [vscan.dev](https://vscan.dev), which analyzes:
- Extension source code and permissions
- Third-party dependencies and known vulnerabilities
- Publisher reputation and verification status
- Network access patterns
- File system permissions

### Privacy

- No data is collected by this tool
- All analysis is performed by vscan.dev
- Cache is stored locally on your machine
- No credentials or secrets are transmitted

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

- [vscan.dev](https://vscan.dev) - Security analysis API
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [Typer](https://github.com/tiangolo/typer) - Modern CLI framework
- The VS Code extension community

---

## Links

- **GitHub:** [vsc-extension-scanner](https://github.com/username/vsc-extension-scanner)
- **Documentation:** [docs/](docs/)
- **Issues & Support:** [GitHub Issues](https://github.com/username/vsc-extension-scanner/issues)
- **vscan.dev:** [https://vscan.dev](https://vscan.dev)

---

**Made with care for the developer community. Stay secure!**
