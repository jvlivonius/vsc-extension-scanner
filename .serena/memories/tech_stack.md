# Technology Stack

## Core Technologies
- **Language**: Python 3.8+
- **Distribution**: Python package (pip installable)
- **Package Name**: vscode-extension-scanner
- **CLI Entry Point**: vscan

## Dependencies
**Required** (from pyproject.toml):
- Rich ≥13.0.0,<14.0.0 (terminal formatting, progress bars, tables, panels)
- Typer ≥0.9.0,<1.0.0 (modern CLI framework with Rich support)

**Standard Library** (no external deps):
- urllib.request (HTTP library for API calls)
- SQLite3 (caching with HMAC integrity)
- threading (ThreadPoolExecutor for parallel scanning)

**Test Dependencies**:
- pytest ≥7.0.0 (test framework)
- pyyaml ≥6.0.0 (architecture test configuration)

## Output Formats
- JSON (structured data export)
- HTML (self-contained interactive reports)
- CSV (spreadsheet compatible)
- Rich terminal (beautiful CLI output)

## Configuration
- Format: INI file
- Location: ~/.vscanrc
- Optional: Works with sensible defaults
