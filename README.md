# VS Code Extension Security Scanner

A standalone Python CLI tool that performs comprehensive security audits of installed VS Code extensions using the vscan.dev security analysis service.

**Version:** 3.1.0 | **Status:** Production Ready ✅

## What's New in v3.1

- **⚙️ Configuration File Support:** Persistent settings with `~/.vscanrc` (INI format)
- **📋 Config Management Commands:** `vscan config` subcommands (`init`, `show`, `set`, `get`, `reset`)
- **📊 CSV Export:** Spreadsheet-compatible output format for security analysis
- **📈 Performance Improvements:** 87.6% faster database operations, 73.9% space reclaimed
- **🎯 Improved Config UX:** Single unified table showing full keys (e.g., "scan.delay")
- **🔧 Better Error Handling:** Centralized constants and improved error codes

## What's New in v3.0

- **🎨 Modern CLI with Rich & Typer:** Beautiful terminal UI with tables, progress bars, and colors
- **📊 Interactive Results Tables:** Sortable tables with risk indicators, security scores, and publisher verification
- **⚡ Smart Cache Commands:** Organized `vscan cache` subcommands (`stats`, `clear`)
- **🎯 Always Comprehensive:** All scans include complete security data (no more modes)
- **🔇 Minimal Quiet Mode:** `--quiet` shows single-line summaries perfect for CI/CD
- **🗂️ Generate Reports from Cache:** New `vscan report` command for instant report generation
- **🎛️ Filtering Options:** Filter by publisher, extension IDs, risk levels
- **⚙️ Refined Refresh:** `--refresh-cache` only refreshes scanned extensions, not entire cache

## What's New in v2.2

- **📊 HTML Report Generation:** Interactive, self-contained HTML reports with sortable tables, charts, and expandable details
- **🎨 Data Visualizations:** Pie charts for risk distribution, gauges for security scores, bar charts for vulnerabilities
- **🔍 Advanced Filtering:** Search extensions, filter by risk level, toggle column visibility
- **🖨️ Print-Optimized:** Professional reports ready for documentation and sharing
- **🔄 Intelligent Retry Mechanism:** Automatic recovery from rate limiting, server errors, and network timeouts
- **⏱️ Exponential Backoff:** Smart retry delays (2s, 4s, 8s) with randomized jitter
- **🎯 Retry-After Support:** Respects vscan.dev rate limit headers
- **📈 Retry Statistics:** Track retry attempts, successes, and failures
- **⚙️ Configurable:** Control retry behavior with `--max-retries` and `--retry-delay`

## What This Tool Does

1. **Auto-discovers** installed VS Code extensions on your system
2. **Queries** vscan.dev for comprehensive security analysis
3. **Analyzes** dependencies, permissions, and security score components
4. **Reports** security scores, risk levels, vulnerabilities, and risk factors
5. **Outputs** results in JSON, interactive HTML, or CSV format
6. **Configures** persistent settings via `~/.vscanrc` configuration file

## Quick Start

```bash
# Standard scan with Rich UI
vscan scan

# Minimal output for CI/CD pipelines
vscan scan --quiet

# Generate interactive HTML report
vscan scan --output report.html

# Save comprehensive JSON to file
vscan scan --output results.json

# Export to CSV for spreadsheet analysis (NEW v3.1)
vscan scan --output results.csv

# Plain output (no colors, for scripts)
vscan scan --plain

# Filter by publisher
vscan scan --publisher microsoft

# Filter by risk level
vscan scan --min-risk-level high

# Scan specific extensions only
vscan scan --include-ids "ms-python.python,esbenp.prettier-vscode"

# Exclude specific extensions
vscan scan --exclude-ids "local.test-extension"

# Cache management
vscan cache stats                  # View cache statistics
vscan cache clear                  # Clear all cache
vscan scan --refresh-cache         # Force refresh scanned extensions
vscan scan --no-cache              # Disable caching
vscan scan --cache-max-age 14      # 14-day cache expiry

# Generate reports from cache (no API calls)
vscan report report.html           # HTML report from cache
vscan report results.json          # JSON report from cache
vscan report results.csv           # CSV report from cache (NEW v3.1)

# Configuration management (NEW v3.1)
vscan config init                  # Create ~/.vscanrc config file
vscan config show                  # Display current configuration
vscan config set scan.delay 2.0    # Set configuration value
vscan config get scan.delay        # Get specific config value
vscan config reset                 # Delete config file

# Retry configuration (resilience)
vscan scan --max-retries 5         # More aggressive retries
vscan scan --retry-delay 3.0       # Longer backoff delays
vscan scan --max-retries 0         # Disable retries (fail fast)

# Advanced options
vscan scan --delay 2.0             # Custom delay between requests
vscan scan --extensions-dir /path  # Custom extensions directory
```

## Features

✅ **Modern CLI with Rich UI** - Beautiful tables, progress bars, and colors (automatic in terminals)
✅ **Multiple output formats** - JSON, interactive HTML, and CSV for spreadsheet analysis
✅ **Configuration file support** - Persistent settings with `~/.vscanrc` (v3.1)
✅ **Config management commands** - Easy configuration with `vscan config` subcommands (v3.1)
✅ **Comprehensive analysis** - All scans include dependencies, risk factors, security score breakdowns
✅ **Auto-discovery** - Finds VS Code extensions on all platforms (macOS, Windows, Linux)
✅ **Publisher verification** - Verified status and reputation tracking
✅ **Intelligent retry mechanism** - Automatic recovery from rate limits, server errors, timeouts
✅ **Smart caching** - 50x faster with SQLite-based cache
✅ **Filtering options** - By publisher, extension IDs, or risk level
✅ **Cache-only reports** - Generate reports instantly from cache without API calls
✅ **Progress indicators** - Real-time updates with visual symbols
✅ **CI/CD friendly** - Quiet mode, plain output, proper exit codes

## Output Formats

### Rich Terminal Output (default)

When running in a terminal, vscan displays:

- **📊 Interactive Results Table:** Sortable table showing extensions with risk indicators
- **✓ Verified Publishers:** Green checkmarks for verified publishers
- **🎨 Color-coded Risks:** CRIT (red), HIGH (red), MED (yellow), LOW (green)
- **⚡ Cache Indicators:** Shows which results came from cache vs fresh scans
- **📈 Statistics:** Summary with scan duration, cache hit rate, vulnerabilities found

### Quiet Mode (`--quiet`)

Perfect for CI/CD scripts:

```bash
$ vscan scan --quiet
Scanned 66 extensions - Found 5 vulnerabilities
```

Single line output with essential information. Exit codes:
- `0` = No vulnerabilities found
- `1` = Vulnerabilities found
- `2` = Scan failed

### Plain Output (`--plain`)

For scripts and log files:

```bash
$ vscan scan --plain
Step 1: Discovering VS Code extensions...
[✓] Found VS Code extensions directory
[✓] Discovered 66 extensions

Step 2: Scanning extensions for vulnerabilities...
[1/66] ms-python.python v2024.10.0... ⚡ Cached
[2/66] esbenp.prettier-vscode v10.1.0... 🔍 ✓
...

[✓] Scan Complete!
Total extensions scanned: 66
Vulnerabilities found: 5
```

### HTML Reports (`--output report.html`)

Interactive, self-contained HTML reports with:

- **Sortable overview table** - Click column headers to sort by any field
- **Risk-based filtering** - Filter extensions by high/medium/low risk
- **Search functionality** - Find extensions by name or publisher
- **Data visualizations** - Pie charts, security gauges, bar charts
- **Expandable details** - Click rows to see complete security analysis
- **Print-optimized** - Professional formatting for documentation
- **No external dependencies** - All CSS/JS embedded, works offline

Perfect for sharing with teams, documentation, or visual analysis.

### CSV Export (`--output results.csv`) ✨ New in v3.1

Spreadsheet-compatible format for analysis and reporting:

- **15-column schema** - Extension ID, Name, Version, Publisher, Verified, Risk Level, Security Score, Vulnerabilities (Total, Critical, High, Moderate, Low), Dependencies, Last Updated, vscan.dev URL
- **Proper CSV escaping** - Handles commas, quotes, and newlines correctly
- **UTF-8 encoding** - Supports international characters
- **Works with all spreadsheet tools** - Excel, Google Sheets, LibreOffice, etc.

Perfect for data analysis, dashboards, or importing into other tools.

### JSON Output (`--output results.json`)

Comprehensive output with all available security data:

- Complete dependency lists with risk assessments
- Security score breakdowns by module
- Individual risk factors with descriptions
- Publisher reputation and install counts
- Extension metadata (keywords, URLs, ratings)
- Vulnerability details by severity

## Example JSON Output

```json
{
  "schema_version": "2.0",
  "output_mode": "detailed",
  "summary": {
    "total_extensions_scanned": 42,
    "vulnerabilities_found": 0,
    "scan_timestamp": "2025-10-24T14:30:00Z",
    "scan_duration_seconds": 28.5
  },
  "cache_stats": {
    "from_cache": 35,
    "fresh_scans": 7,
    "cache_hit_rate": 83.3
  },
  "extensions": [
    {
      "id": "ms-python.python",
      "name": "python",
      "display_name": "Python",
      "version": "2024.10.0",
      "publisher": {
        "id": "ms-python",
        "name": "Microsoft",
        "verified": true,
        "domain": "microsoft.com"
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
          "list": [...]
        }
      },
      "vscan_url": "https://vscan.dev/extension/ms-python.python",
      "scan_status": "success"
    }
  ]
}
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install from PyPI

```bash
pip install vscode-extension-scanner
```

### Install from Source

```bash
git clone https://github.com/username/vsc-extension-scanner.git
cd vsc-extension-scanner
pip install -e .
```

### Development Setup

```bash
# Install with CLI dependencies (Rich, Typer)
pip install -e ".[cli]"

# Run from source
python -m vscode_scanner.vscan scan
```

## Usage Examples

### Basic Scanning

```bash
# Scan all installed extensions
vscan scan

# Save results to JSON file
vscan scan --output results.json

# Generate HTML report
vscan scan --output report.html
```

### Filtering

```bash
# Scan only Microsoft extensions
vscan scan --publisher microsoft

# Scan only high-risk extensions
vscan scan --min-risk-level high

# Scan specific extensions
vscan scan --include-ids "ms-python.python,GitHub.copilot"

# Exclude test extensions
vscan scan --exclude-ids "local.test"
```

### Caching

```bash
# View cache statistics
vscan cache stats

# Clear all cached data
vscan cache clear

# Force refresh (ignore cache for scanned extensions)
vscan scan --refresh-cache

# Disable cache entirely
vscan scan --no-cache

# Custom cache age threshold
vscan scan --cache-max-age 30
```

### Report Generation

```bash
# Generate HTML report from cache (instant, no API calls)
vscan report security-report.html

# Generate JSON report from cache
vscan report cache-dump.json

# Control cache age for reports
vscan report report.html --cache-max-age 7
```

### CI/CD Integration

```bash
# Minimal output for scripts
vscan scan --quiet

# Exit code handling
vscan scan --quiet
if [ $? -eq 1 ]; then
  echo "Vulnerabilities found!"
  exit 1
fi

# Plain output for logs
vscan scan --plain --output results.json

# Combine with filtering
vscan scan --quiet --min-risk-level high
```

## Exit Codes

- **0** - Scan completed successfully, no vulnerabilities found
- **1** - Scan completed successfully, vulnerabilities found
- **2** - Scan failed (error occurred)

## Performance

- **First scan:** ~1.5 seconds per extension (respects API rate limits)
- **Cached results:** ~instant (50x faster)
- **Memory usage:** < 100MB RAM
- **Cache hit rate:** Typically 70-90% on repeated scans

## Troubleshooting

### Rate Limiting

vscan automatically handles rate limiting with intelligent retry:

```bash
# Increase retry attempts
vscan scan --max-retries 5

# Increase delay between requests
vscan scan --delay 2.0

# Adjust retry backoff
vscan scan --retry-delay 3.0
```

### Slow Scans

```bash
# Use cached results (much faster)
vscan scan  # Uses 7-day cache by default

# Extend cache age
vscan scan --cache-max-age 30

# Generate reports from cache without scanning
vscan report report.html
```

### No Color/Formatting

```bash
# Force plain output
vscan scan --plain

# Check environment
echo $TERM  # Should not be "dumb"
echo $NO_COLOR  # Should be empty
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **vscan.dev** - Security analysis API
- **Rich** - Beautiful terminal formatting
- **Typer** - Modern CLI framework
- VS Code Extension community

## Links

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/username/vsc-extension-scanner/issues)
- **vscan.dev:** [https://vscan.dev](https://vscan.dev)
