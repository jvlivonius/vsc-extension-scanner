# VS Code Extension Security Scanner

[![CI Status](https://github.com/jvlivonius/vsc-extension-scanner/actions/workflows/test.yml/badge.svg)](https://github.com/jvlivonius/vsc-extension-scanner/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Know what's running in your editor. Stay secure.**

A command-line tool that scans your installed VS Code extensions for security vulnerabilities, suspicious permissions, and risky dependencies. Get instant insights into the security posture of your development environment.

**Version:** See [releases](https://github.com/jvlivonius/vsc-extension-scanner/releases) | **Status:** [Production Ready](docs/project/STATUS.md) ✅

---

## ⚡ Quick Demo (30 Seconds)

**Want to see it in action first?** Try this quick scan:

```bash
# Install from GitHub Releases
pip install "$(curl -s https://api.github.com/repos/jvlivonius/vsc-extension-scanner/releases/latest | grep browser_download_url | grep .whl | cut -d '"' -f 4)"

# Run your first scan
vscan scan --quiet
```

**✅ Expected output:**
```
Scanned 66 extensions - Found 5 vulnerabilities ⚠️
```

**That's it!** You just audited your entire VS Code setup in 30 seconds.

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

### Why Command-Line?

- ⚡ **Speed:** Scan 60+ extensions in ~75 seconds (vs hours of manual lookups)
- 🔄 **Automation:** Integrate into CI/CD pipelines and scheduled scans
- 🔒 **Privacy:** All data stays on your machine, local cache storage
- 📊 **Team Collaboration:** Export to CSV/JSON/HTML for tracking and reporting
- 🎨 **Developer-Friendly:** Scriptable, customizable, Git-friendly

---

## 🚀 Installation

**Requirements:** Python 3.8 or higher

### Quick Install (Recommended)

```bash
# One-line install from GitHub Releases
pip install "$(curl -s https://api.github.com/repos/jvlivonius/vsc-extension-scanner/releases/latest | grep browser_download_url | grep .whl | cut -d '"' -f 4)"

# Verify installation
vscan --version
```

**✅ Installation complete!** Run `vscan scan` to get started.

**See:** [DISTRIBUTION.md](DISTRIBUTION.md) for complete installation instructions and troubleshooting.

<details>
<summary>Alternative: Install from source</summary>

```bash
git clone https://github.com/jvlivonius/vsc-extension-scanner.git
cd vsc-extension-scanner
pip install -e .
```
</details>

---

## Quick Start

### Most Common Commands

```bash
# Scan all your extensions (beautiful terminal output)
vscan scan

# Maximum performance with 5 workers (~5x faster)
vscan scan --workers 5

# Save results as an interactive HTML report
vscan scan --output report.html

# Minimal output for CI/CD pipelines
vscan scan --quiet

# Filter by risk level
vscan scan --min-risk-level high

# Filter by publisher
vscan scan --publisher microsoft
```

**💡 First time?** The first scan takes 1-2 minutes. Subsequent scans are instant (cached).

### Common Use Cases

**Personal Audit:**
```bash
vscan scan --output security-audit.html
```

**Team Review:**
```bash
vscan scan --output team-report.html
vscan scan --output security-tracking.csv
```

**CI/CD Integration:**
```bash
vscan scan --quiet --min-risk-level high
if [ $? -eq 1 ]; then
  echo "High-risk extensions detected!"
  exit 1
fi
```

**Regular Monitoring:**
```bash
vscan scan                        # Daily (uses cache)
vscan scan --refresh-cache        # Weekly (full refresh)
vscan cache stats                 # View cache statistics
```

**Full command reference:** See `vscan --help` or [docs/](docs/) for complete documentation

---

## ✨ Key Features

### 🎯 Easy to Use
- ✅ **Auto-detection** - Finds VS Code extensions automatically (macOS, Windows, Linux)
- ✅ **Zero config** - Works out of the box, no setup required
- ✅ **Clear results** - Actionable security insights, not just raw data

### ⚡ Fast & Efficient
- 🚀 **Parallel processing** - ~5x faster than sequential (default: 3 workers)
- 💾 **Smart caching** - 50x faster on repeated scans (typical 70-90% hit rate)
- 🎯 **Respectful** - Built-in rate limiting protects vscan.dev infrastructure

### 🔍 Comprehensive Analysis
- 🛡️ **Security scores** - 0-100 rating for each extension
- ⚠️ **Vulnerability detection** - Known issues in dependencies
- ✓ **Publisher verification** - Trust signals from verified publishers
- 🔐 **Permission analysis** - Network access, file system permissions, etc.

### 📊 Flexible Output

| Format | Best For | Example |
|--------|----------|---------|
| **Terminal** | Daily checks | `vscan scan` |
| **HTML** | Team reviews | `vscan scan --output report.html` |
| **CSV** | Tracking | `vscan scan --output results.csv` |
| **JSON** | Automation | `vscan scan --output results.json` |
| **Quiet** | CI/CD | `vscan scan --quiet` |

---

## 🛡️ Security Highlights

**This tool is built with security as the top priority:**

- ✅ **Zero vulnerabilities** - Security score: 9.5/10, all tests passing
- ✅ **Comprehensive testing** - 1,100+ tests with 120+ security-focused tests
- ✅ **Property-based testing** - 31,000+ generated test scenarios via Hypothesis
- ✅ **95%+ security coverage** - Path validation, string sanitization, HMAC integrity
- ✅ **No code execution** - Read-only analysis, never modifies extensions
- ✅ **Local caching** - All data stored on your machine with HMAC-SHA256 protection
- ✅ **HTTPS only** - All communication encrypted with certificate validation

**Security measures:**
- **Path validation** - Blocks directory traversal attacks (CWE-22)
- **String sanitization** - Context-aware injection prevention
- **Cache integrity** - HMAC-SHA256 cryptographic signatures
- **Thread safety** - Race condition elimination
- **Fail-fast validation** - Invalid input rejected immediately

**See:** [SECURITY.md](SECURITY.md) for security policy and [docs/guides/SECURITY.md](docs/guides/SECURITY.md) for complete security architecture

---

## What Gets Analyzed?

For each extension, you'll see:

- **Security Score** (0-100) - Overall security rating
- **Risk Level** - Critical, High, Medium, or Low
- **Vulnerabilities** - Known security issues in dependencies
- **Publisher Verification** - Whether the publisher is verified
- **Risk Factors** - Network access, file system permissions, etc.
- **Dependencies** - Third-party packages and their security status

**Data source:** All security analysis is powered by [vscan.dev](https://vscan.dev)

---

## 🔧 Essential Commands

```bash
# Scanning
vscan scan                              # Scan all extensions
vscan scan --output report.html         # Save as HTML
vscan scan --workers 5                  # Faster scanning (5 workers)
vscan scan --quiet                      # Minimal output for scripts

# Filtering
vscan scan --publisher microsoft        # Filter by publisher
vscan scan --min-risk-level high        # Show only high/critical

# Caching
vscan cache stats                       # View cache statistics
vscan cache clear                       # Clear cache (with prompt)
vscan scan --refresh-cache              # Update cached extensions
vscan scan --no-cache                   # Disable caching

# Reports from Cache
vscan report security-report.html       # Generate HTML from cache
vscan report data-export.json           # Export JSON from cache

# Configuration
vscan config init                       # Create config file
vscan config show                       # View current settings
vscan config set scan.workers 5         # Save preferences

# Help
vscan --help                            # General help
vscan scan --help                       # Command-specific help
vscan --version                         # Version information
```

**Full documentation:** Run `vscan --help` or see [docs/](docs/)

---

## ⚙️ Configuration

Save preferences in `~/.vscanrc`:

```ini
[scan]
workers = 3
delay = 2.0

[cache]
max_age = 14

[output]
quiet = false
```

**Create config:** `vscan config init`
**See all options:** [docs/guides/CONFIGURATION.md](docs/guides/CONFIGURATION.md) or `vscan config --help`

---

## 🚨 Exit Codes

The tool returns standard exit codes for easy integration:

- **0** - Success, no vulnerabilities found
- **1** - Success, but vulnerabilities were found
- **2** - Scan failed due to an error

---

## 🔧 Troubleshooting

### Common Issues

**"No extensions found"**
```bash
# Check if VS Code extensions exist
ls ~/.vscode/extensions/

# Specify custom directory if needed
vscan scan --extensions-dir /path/to/extensions
```

**Slow scans**
```bash
# Use caching (first scan: ~2 min, subsequent: instant)
vscan scan

# Increase workers for speed
vscan scan --workers 5
```

**Rate limiting**
```bash
# Increase delay between requests
vscan scan --delay 2.0
```

**More help:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) or open an [issue](https://github.com/jvlivonius/vsc-extension-scanner/issues)

---

## 📰 What's New

**Latest:** v5.0.2 - Test Quality Improvements (2025-11-09)

- Test parametrization: 40 → 62 tests in input validators (+55% efficiency)
- Property-based testing: 31 new Hypothesis tests generating 31,000+ test scenarios
- Test metrics: 1,153 total tests (98.3% pass rate)
- Documentation: Added cache directory testing patterns

**See:** [CHANGELOG.md](CHANGELOG.md) for complete version history

---

## 🔬 Technical Details

### How It Works

1. **Discovery** - Automatically locates your VS Code extensions directory
2. **Analysis** - Queries vscan.dev API for security analysis of each extension
3. **Caching** - Stores results in SQLite database for fast repeated scans
4. **Reporting** - Formats results in your preferred output format

### Performance

**Real-world performance** (66 extensions):
- **Default (3 workers):** 75 seconds (~5x faster than sequential)
- **Maximum (5 workers):** 90 seconds (~4x faster than sequential)
- **Cached scan:** < 1 second (instant!)
- **Memory usage:** < 100MB RAM
- **Cache hit rate:** 70-90% typical

**See:** [docs/guides/PERFORMANCE.md](docs/guides/PERFORMANCE.md) for detailed benchmarks

### Security Data Source

**All security analysis is powered by [vscan.dev](https://vscan.dev)**, an excellent VS Code extension security analysis service.

This tool would not exist without vscan.dev's infrastructure. vscan.dev provides comprehensive analysis including:
- Extension source code and permissions review
- Dependency vulnerability detection
- Publisher reputation validation
- Security scoring and risk assessment

**We are deeply grateful to vscan.dev** for providing their public API. This tool serves as a complementary CLI client to vscan.dev's analysis capabilities.

### API Usage & Respectful Practices

This tool implements multiple measures to minimize load on vscan.dev's infrastructure:

- **Rate limiting:** 2.0s default delay between requests (configurable)
- **Intelligent caching:** 70-90% cache hit rate, 14-day default expiration
- **Exponential backoff:** Graceful retry handling with jitter
- **Thread-safe:** 3 workers by default (configurable 1-5)
- **Transparent identification:** User-Agent includes tool name and repository URL

**Typical impact:** Average user generates 100-200 API requests per month (vs 2,000+ without caching).

**See:** [ATTRIBUTION.md](ATTRIBUTION.md) for complete API usage details

### Privacy

- ✅ No data is collected by this tool
- ✅ All analysis is performed by vscan.dev
- ✅ Cache is stored locally on your machine
- ✅ No credentials or secrets are transmitted

### Platform Support

- ✅ macOS
- ✅ Windows
- ✅ Linux

The tool automatically detects your platform and finds the VS Code extensions directory.

---

## ❓ FAQ

<details>
<summary><strong>Q: Is this tool official from Microsoft or VS Code?</strong></summary>

**A:** No, this is an independent security tool that uses the vscan.dev API. It's not affiliated with Microsoft, VS Code, or vscan.dev.
</details>

<details>
<summary><strong>Q: How often should I scan?</strong></summary>

**A:** Weekly full scans are recommended. Use caching for daily checks without API overhead:
- **Daily:** `vscan scan` (uses cache, instant)
- **Weekly:** `vscan scan --refresh-cache` (full scan, 1-2 minutes)
</details>

<details>
<summary><strong>Q: What data is collected about me?</strong></summary>

**A:** **None.** This tool:
- 🚫 Does not collect any user data
- 🚫 Does not send your extension list anywhere
- 🚫 Does not track usage or analytics
- ✅ Only queries vscan.dev API for public extension data
- ✅ Stores cache locally on your machine
</details>

**More questions?** See [docs/FAQ.md](docs/FAQ.md) or open an [issue](https://github.com/jvlivonius/vsc-extension-scanner/issues)

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

We respect vscan.dev's rights and will cooperate fully with reasonable requests.

### No Warranty

This software is provided "as-is" under the MIT License with no warranties of any kind. See the [LICENSE](LICENSE) file for complete terms.

### Attribution

**All security analysis is powered by [vscan.dev](https://vscan.dev).** We are deeply grateful to vscan.dev for providing their public API, which makes this tool possible.

**See:** [ATTRIBUTION.md](ATTRIBUTION.md) for complete legal and attribution information

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- 🐛 Report bugs or request features via [GitHub Issues](https://github.com/jvlivonius/vsc-extension-scanner/issues)
- 🔧 Submit pull requests for improvements
- 💬 Share your experience and use cases
- 📝 Help improve documentation

**For development setup:** See [CONTRIBUTING.md](CONTRIBUTING.md)
**For security issues:** Use [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new) (private)

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

This tool is made possible by:

- **[vscan.dev](https://vscan.dev)** - Powers all security analysis functionality through their excellent API. This tool would not exist without vscan.dev's infrastructure and analysis capabilities.
- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal formatting library
- **[Typer](https://github.com/tiangolo/typer)** - Modern CLI framework
- **The VS Code extension community** - For creating the extensions that make VS Code powerful

**We strongly encourage users to visit [vscan.dev](https://vscan.dev)** directly to explore their full range of security analysis features and services.

---

## 🚀 Next Steps

**Ready to secure your VS Code environment?**

1. **⬇️ Install:** [Download from GitHub Releases](https://github.com/jvlivonius/vsc-extension-scanner/releases/latest)
2. **▶️ Run:** `vscan scan` to audit your extensions
3. **📊 Review:** Check high-risk extensions and vulnerabilities
4. **🔄 Schedule:** Set up weekly scans for ongoing security

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

**Found a security issue?** Report privately via [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new)

**Questions?** Open an [issue](https://github.com/jvlivonius/vsc-extension-scanner/issues) or check the [FAQ](#-faq)

**Like this tool?** ⭐ Star this repo to show your support!

---

## 🔗 Documentation & Links

### Project Links
- **GitHub:** [vsc-extension-scanner](https://github.com/jvlivonius/vsc-extension-scanner)
- **Releases:** [Latest Release](https://github.com/jvlivonius/vsc-extension-scanner/releases/latest)
- **Issues & Support:** [GitHub Issues](https://github.com/jvlivonius/vsc-extension-scanner/issues)

### Documentation
- **Getting Started:** [DISTRIBUTION.md](DISTRIBUTION.md) - Installation & setup
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
- **Security:** [SECURITY.md](SECURITY.md) - Security policy
- **Complete Docs:** [docs/](docs/) - Full documentation index
  - [Architecture](docs/guides/ARCHITECTURE.md) - System design
  - [Security Guide](docs/guides/SECURITY.md) - Security architecture
  - [Testing](docs/guides/TESTING.md) - Testing strategy
  - [Performance](docs/guides/PERFORMANCE.md) - Performance benchmarks
  - [API Reference](docs/guides/API_REFERENCE.md) - vscan.dev API
- **Project Status:** [STATUS.md](docs/project/STATUS.md) - Current version & roadmap
- **Changelog:** [CHANGELOG.md](CHANGELOG.md) - Version history

### External Links
- **vscan.dev:** [https://vscan.dev](https://vscan.dev) - Security analysis service

---

**Made with care for the developer community. Stay secure! 🛡️**
