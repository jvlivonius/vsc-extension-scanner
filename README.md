# VS Code Extension Security Scanner

A standalone Python CLI tool that performs comprehensive security audits of installed VS Code extensions using the vscan.dev security analysis service.

**Version:** 2.0.0 | **Status:** Production Ready ✅

All phases complete - ready for production use. See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for development history.

## What's New in v2.0

- **🔍 Complete Data Capture:** All vscan.dev analysis data including dependencies, risk factors, and security score breakdowns
- **📊 Dual Output Modes:** Standard (concise) and Detailed (comprehensive with `--detailed` flag)
- **✅ Publisher Verification:** See verified publisher status and reputation
- **📦 Dependency Analysis:** Complete list of dependencies with individual risk assessments
- **🔒 Security Insights:** Understand WHY extensions have specific risk levels
- **⚡ Enhanced Cache:** Auto-migrates from v1.0, 28x faster with intelligent caching
- **📈 Better Statistics:** Install counts, ratings, and update frequencies

## What This Tool Does

1. **Auto-discovers** installed VS Code extensions on your system
2. **Queries** vscan.dev for comprehensive security analysis
3. **Analyzes** dependencies, permissions, and security score components
4. **Reports** security scores, risk levels, vulnerabilities, and risk factors
5. **Outputs** results in JSON format (standard or detailed mode)

## Quick Start

```bash
# Standard scan (concise output)
python3 vscan.py

# Detailed scan (comprehensive security data)
python3 vscan.py --detailed

# Save to file with progress indicators
python3 vscan.py --output results.json --verbose

# Cache management
python3 vscan.py --cache-stats             # View cache statistics
python3 vscan.py --refresh-cache           # Force refresh all
python3 vscan.py --clear-cache             # Clear cache

# Advanced options
python3 vscan.py --delay 2.0               # Custom delay between requests
python3 vscan.py --cache-max-age 14        # 14-day cache expiry
python3 vscan.py --no-cache                # Disable caching
```

## Features

✅ **Dual output modes** - Standard (concise) and Detailed (comprehensive) JSON output
✅ **Auto-discovery** - Finds VS Code extensions on all platforms (macOS, Windows, Linux)
✅ **Complete security analysis** - Dependencies, risk factors, security score breakdowns
✅ **Publisher verification** - Verified status and reputation tracking
✅ **Intelligent caching** - 28x faster with SQLite-based cache
✅ **Progress indicators** - Real-time updates with visual symbols
✅ **Zero dependencies** - Uses only Python 3.8+ standard library

## Output Modes

### Standard Mode (default)

Concise output with essential security information:

- Security scores and risk levels
- Vulnerability counts by severity
- Publisher verification status
- Dependency and risk factor counts
- Cache statistics

### Detailed Mode (`--detailed`)

Comprehensive output including:

- Complete dependency lists with risk assessments
- Security score breakdowns by module
- Individual risk factors with descriptions
- Publisher reputation and install counts
- Extension metadata (keywords, URLs, ratings)

## Example Output (Standard Mode)

```json
{
  "schema_version": "2.0",
  "output_mode": "standard",
  "summary": {
    "total_extensions_scanned": 42,
    "vulnerabilities_found": 0,
    "scan_timestamp": "2025-10-23T14:30:00Z",
    "scan_duration_seconds": 28.5
  },
  "cache_stats": {
    "from_cache": 35,
    "fresh_scans": 7,
    "cache_hit_rate": 83.3
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

## Documentation

### Quick Links

- **[CLAUDE.md](CLAUDE.md)** - Development guidance and architecture details
- **[docs/README.md](docs/README.md)** - Complete documentation index
- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** - Development history and status

### Detailed Documentation

- **Phase Requirements:**
  - [Phase 1: Research & Discovery](docs/phases/PHASE1_REQUIREMENTS.md)
  - [Phase 2: Core Implementation](docs/phases/PHASE2_REQUIREMENTS.md)
  - [Phase 3: Testing & Refinement](docs/phases/PHASE3_REQUIREMENTS.md)
  - [Phase 4: Enhanced Data Integration](docs/phases/PHASE4_REQUIREMENTS.md)

- **Design & Research:**
  - [Product Requirements Document (PRD)](docs/design/PRD.md)
  - [vscan.dev API Research](docs/research/API_RESEARCH.md)

- **Testing & Results:**
  - [Testing Checklist](docs/testing/TESTING_CHECKLIST.md)
  - [macOS Test Results](docs/testing/MACOS_TEST_RESULTS.md)
  - [Phase Completion Summaries](docs/results/)

- **Security:**
  - [Security Analysis](docs/security/SECURITY_ANALYSIS.md)
  - [Security Fixes Applied](docs/security/SECURITY_FIXES_APPLIED.md)

## References

- **[vscan.dev](https://vscan.dev)** - VS Code Extension Security Analyzer
- **[VS Code Extension API](https://code.visualstudio.com/api)** - Extension documentation
