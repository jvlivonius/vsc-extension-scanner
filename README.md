# VS Code Extension Security Scanner

A standalone Python CLI tool that performs security audits of installed VS Code extensions using the vscan.dev security analysis service.

## Project Status

- ✅ **Phase 1: Research & Discovery** - COMPLETED
- ⏳ **Phase 2: Core Implementation** - Not Started
- ⏳ **Phase 3: Testing & Refinement** - Not Started

## What This Tool Does

1. **Auto-discovers** installed VS Code extensions on your system
2. **Queries** vscan.dev for security analysis of each extension
3. **Reports** security scores, risk levels, and vulnerabilities
4. **Outputs** results in JSON format for easy parsing

## Quick Start

**Note:** Tool is not yet implemented. See Phase 1 research below.

```bash
# Once implemented:
python vscan.py                           # Scan all extensions
python vscan.py --output results.json    # Save to file
python vscan.py --verbose                # Show detailed progress
```

## Phase 1 Completion

### API Endpoints Validated ✅

All three vscan.dev API endpoints have been reverse-engineered and validated:

1. **POST** `/api/extensions/analyze` - Submit extension for analysis
2. **GET** `/api/extensions/status/{analysisId}` - Check analysis status
3. **GET** `/api/extensions/results/{analysisId}` - Retrieve results

### Test Results

Tested with 3 popular extensions:
- **ms-python.python** - Security Score: 82/100 (high risk)
- **esbenp.prettier-vscode** - Security Score: 82/100 (medium risk)
- **ms-azuretools.vscode-docker** - Security Score: 93/100 (medium risk)

**Key Finding:** Popular extensions are cached by vscan.dev and return results instantly (0.0s).

### Documentation

- **[API_RESEARCH.md](API_RESEARCH.md)** - Comprehensive API documentation and findings
- **[CLAUDE.md](CLAUDE.md)** - Project guidance and technical specifications
- **[PRD.md](PRD.md)** - Product Requirements Document
- **[test_api.py](test_api.py)** - API validation script

### Run API Tests

```bash
python3 test_api.py
```

Output: JSON results to stdout, detailed logs to stderr

## Architecture

### Extension Discovery
- Auto-detect VS Code extensions directory by platform:
  - macOS: `~/.vscode/extensions/`
  - Windows: `%USERPROFILE%\.vscode\extensions\`
  - Linux: `~/.vscode/extensions/`
- Parse `package.json` for extension metadata
- Support custom paths via `--extensions-dir`

### vscan.dev Integration
- Asynchronous analysis workflow
- Poll status until completion
- Parse security scores and vulnerability data
- Handle cached results (instant responses)

### Output Format

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

## Technology Stack

- **Language:** Python 3.8+
- **HTTP Library:** `urllib.request` (standard library, no dependencies)
- **CLI Parsing:** `argparse` (standard library)
- **Distribution:** Standalone `.py` script (no installation required)

## Next Steps

### Phase 2: Core Implementation

1. Implement extension discovery for all platforms
2. Parse package.json files
3. Integrate vscan.dev API client
4. Generate JSON output
5. Add error handling and logging
6. Create progress indicators

### Phase 3: Testing & Refinement

1. Test on macOS, Windows, Linux
2. Test with various extension sets
3. Test error scenarios
4. Refine user experience

## References

- [vscan.dev](https://vscan.dev) - VS Code Extension Security Analyzer
- [VS Code Extension API](https://code.visualstudio.com/api)

## License

See project requirements for licensing details.
