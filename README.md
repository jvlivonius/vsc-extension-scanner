# VS Code Extension Security Scanner

A standalone Python CLI tool that performs security audits of installed VS Code extensions using the vscan.dev security analysis service.

## Project Status

**Phase 1 Complete ✅** | **Phase 2 Complete ✅** | Phase 3: Not Started ⏳

See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for detailed progress tracking.

## What This Tool Does

1. **Auto-discovers** installed VS Code extensions on your system
2. **Queries** vscan.dev for security analysis of each extension
3. **Reports** security scores, risk levels, and vulnerabilities
4. **Outputs** results in JSON format for easy parsing

## Quick Start

**The tool is now fully functional!** (Phase 2 complete)

```bash
# Run the scanner
python3 vscan.py                           # Scan all extensions
python3 vscan.py --output results.json    # Save to file
python3 vscan.py --verbose                # Show detailed progress
python3 vscan.py --delay 2.0              # Custom delay between requests

# Test API endpoints (Phase 1)
python3 test_api.py
```

## Phase 1 Results

### API Validation ✅

All three vscan.dev API endpoints have been reverse-engineered and validated:

1. **POST** `/api/extensions/analyze` - Submit extension for analysis
2. **GET** `/api/extensions/status/{analysisId}` - Check analysis status
3. **GET** `/api/extensions/results/{analysisId}` - Retrieve results

### Test Results

| Extension | Security Score | Risk Level | Status |
|-----------|---------------|------------|--------|
| ms-python.python | 82/100 | high | ✅ Validated |
| esbenp.prettier-vscode | 82/100 | medium | ✅ Validated |
| ms-azuretools.vscode-docker | 93/100 | medium | ✅ Validated |

**Key Finding:** Popular extensions are cached by vscan.dev and return results instantly (0.0s).

## Documentation

### Core Documentation

- **[README.md](README.md)** (this file) - Project overview
- **[CLAUDE.md](CLAUDE.md)** - Development guidance for Claude Code

### Detailed Documentation

- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** - Current status and roadmap
- **[docs/design/PRD.md](docs/design/PRD.md)** - Product requirements document
- **[docs/research/API_RESEARCH.md](docs/research/API_RESEARCH.md)** - vscan.dev API research
- **[docs/testing/TESTING_CHECKLIST.md](docs/testing/TESTING_CHECKLIST.md)** - Test plan

### Test Code

- **[test_api.py](test_api.py)** - API validation script (working implementation)

## Technology Stack

- **Language:** Python 3.8+
- **HTTP Library:** `urllib.request` (standard library, no external dependencies)
- **CLI Parsing:** `argparse` (standard library)
- **Distribution:** Standalone `.py` script (no installation required)
- **Output Format:** JSON

## Example Output

```json
{
  "summary": {
    "total_extensions_scanned": 42,
    "vulnerabilities_found": 3,
    "scan_timestamp": "2025-10-22T14:30:00Z",
    "scan_duration_seconds": 95.5
  },
  "extensions": [
    {
      "name": "Extension Name",
      "id": "publisher.extension-name",
      "version": "1.2.3",
      "security_score": 82,
      "risk_level": "medium",
      "vulnerabilities": {
        "count": 0,
        "critical": 0,
        "high": 0,
        "moderate": 0,
        "low": 0
      },
      "vscan_url": "https://vscan.dev/extension/publisher.extension-name",
      "scan_status": "success"
    }
  ]
}
```

## Next Steps

See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for detailed roadmap.

**Phase 2: Core Implementation** (4-6 hours estimated)

- Implement extension discovery for all platforms
- Integrate vscan.dev API client (based on test_api.py)
- Generate JSON output
- Add error handling and progress indicators

**Phase 3: Testing & Refinement** (2-4 hours estimated)

- Cross-platform testing (macOS, Windows, Linux)
- Edge case testing
- Performance optimization
- User experience polish

## Contributing

This is a standalone security tool. See [docs/design/PRD.md](docs/design/PRD.md) for scope and requirements.

## References

- [vscan.dev](https://vscan.dev) - VS Code Extension Security Analyzer
- [VS Code Extension API](https://code.visualstudio.com/api) - Extension documentation
