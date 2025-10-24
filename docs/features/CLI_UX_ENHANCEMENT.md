# CLI UX Enhancement Specification

**Version:** 3.0.0
**Status:** ✅ Completed
**Created:** 2025-10-24
**Completed:** 2025-10-24
**Dependencies:** Rich ≥13.0.0, Typer ≥0.9.0

## Overview

Transform vscan from a basic command-line tool into a modern, beautiful terminal application with:
- Live progress bars showing real-time scan status
- Rich formatted tables for results and statistics
- Real-time status dashboard during active scans
- Modern CLI framework with better help and command organization

### Goals

1. **Improved User Experience** - Make scan progress visible and engaging
2. **Better Information Display** - Use tables and formatting for clarity
3. **Modern CLI Standards** - Follow best practices for terminal applications
4. **Maintain Functionality** - All existing features work identically, just prettier

### Non-Goals

- Interactive mode (no prompts or user input during scan)
- GUI or web interface
- Backward compatibility with v2.x CLI syntax

---

## Dependencies

### Required External Libraries

**Rich** (≥13.0.0)
- Purpose: Terminal formatting, progress bars, tables, panels
- Size: ~1.5MB
- License: MIT
- Stability: Mature, widely used (100M+ downloads/month)

**Typer** (≥0.9.0)
- Purpose: Modern CLI framework built on Click
- Size: ~500KB
- License: MIT
- Stability: Mature, official FastAPI companion tool

### Installation

```bash
pip install vscan  # Installs with all dependencies
```

### Python Compatibility

- Python 3.8+ (unchanged from current requirement)
- Works on macOS, Linux, Windows

---

## Feature 1: Live Progress Bars

### Current Behavior

```
[1/42] Scanning ms-python.python v2024.10.0... 🔍
[2/42] Scanning esbenp.prettier-vscode v10.1.0... 🔍 ✓
[3/42] dbaeumer.vscode-eslint v2.4.2... ⚡ Cached ✓
...
```

**Problems:**
- No visual progress indication
- Hard to estimate time remaining
- Output scrolls too fast to read
- No summary of current status

### Proposed Behavior

```
Scanning Extensions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35/42  83% 0:01:15

  ⚡ ms-python.python v2024.10.0 [cached] ✓
  🔍 esbenp.prettier-vscode v10.1.0 [analyzing...]
  ✓ dbaeumer.vscode-eslint v2.4.2 [complete - 2 issues] ⚠
```

**Improvements:**
- Visual progress bar with percentage
- Elapsed time and ETA
- Recent extension statuses visible
- Live updating (no scroll spam)

### Implementation Details

**Module:** `display.py`

```python
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)

def create_scan_progress() -> Progress:
    """Create a Rich Progress bar for scanning."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        expand=True
    )
```

**Integration Point:** Replace progress output in `scan_extensions()` function

**Configuration:**
- `--verbose`: Show individual extension progress
- `--quiet`: Minimal output, only final summary
- `--plain`: Disable Rich output (for CI/scripts)

---

## Feature 2: Rich Formatted Tables

### Current Behavior

**Cache Statistics:**
```
Cache Statistics:
  From cache: 30 (⚡ instant)
  Fresh scans: 12 (🔍 API calls)
  Cache hit rate: 71.4%
```

**Scan Summary:**
```
Scan Complete!
Total extensions scanned: 42
Successful scans: 42
Failed scans: 0
Vulnerabilities found: 3
```

**Problems:**
- Plain text, hard to scan quickly
- No visual hierarchy
- Inconsistent alignment
- No color coding

### Proposed Behavior

**Cache Statistics Table:**
```
╭─────────────── Cache Statistics ────────────────╮
│                                                  │
│  ┏━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┓  │
│  ┃ Metric          ┃ Count ┃ Details       ┃  │
│  ┡━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━┩  │
│  │ From Cache      │    30 │ ⚡ instant     │  │
│  │ Fresh Scans     │    12 │ 🔍 API calls   │  │
│  │ Cache Hit Rate  │ 71.4% │               │  │
│  └─────────────────┴───────┴───────────────┘  │
│                                                  │
╰──────────────────────────────────────────────────╯
```

**Scan Results Table:**
```
╭─────────────────── Scan Results ───────────────────╮
│                                                     │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┓ │
│  ┃ Extension             ┃ Risk  ┃ Score ┃ Vulns┃ │
│  ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━┩ │
│  │ ms-python.python      │ 🟢 LOW│ 95/100│ 0    │ │
│  │ esbenp.prettier-vs... │ 🟡 MED│ 82/100│ 0    │ │
│  │ dbaeumer.vscode-es... │ 🔴 HI │ 65/100│ 2    │ │
│  └───────────────────────┴───────┴───────┴──────┘ │
│                                                     │
│  Summary: 42 scanned • 3 vulnerabilities found    │
│  Duration: 1m 23s • Cache hit rate: 71.4%         │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

**Improvements:**
- Clear visual structure with borders
- Color-coded risk levels (red/yellow/green)
- Aligned columns
- Compact but readable
- Summary footer with key metrics

### Implementation Details

**Module:** `display.py`

```python
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

def create_results_table(scan_results: List[Dict]) -> Table:
    """Create a Rich table for scan results."""
    table = Table(title="Scan Results", show_header=True, header_style="bold")

    table.add_column("Extension", style="cyan", no_wrap=True)
    table.add_column("Risk", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Vulns", justify="right")

    for result in scan_results:
        risk_emoji = {
            "low": "🟢 LOW",
            "medium": "🟡 MED",
            "high": "🔴 HI",
            "critical": "🔴 CRIT"
        }

        table.add_row(
            result['name'],
            risk_emoji.get(result['risk_level'], "❓"),
            f"{result['security_score']}/100",
            str(result['vulnerabilities']['count'])
        )

    return table

def create_cache_stats_table(stats: Dict) -> Table:
    """Create a Rich table for cache statistics."""
    table = Table(show_header=True, header_style="bold")

    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Details", style="dim")

    table.add_row("From Cache", str(stats['from_cache']), "⚡ instant")
    table.add_row("Fresh Scans", str(stats['fresh_scans']), "🔍 API calls")
    table.add_row("Cache Hit Rate", f"{stats['cache_hit_rate']:.1f}%", "")

    return table
```

**Tables to Create:**
1. Scan results table (main output)
2. Cache statistics table
3. Retry statistics table (if retries occurred)
4. Filter summary table (when filters applied)

---

## Feature 3: Real-time Status Dashboard

### Current Behavior

No live status display during scan. Progress is shown line-by-line as extensions complete.

### Proposed Behavior

**Live Dashboard (updates in real-time):**
```
╭───────────── VS Code Security Scan ──────────────╮
│                                                   │
│  Status: Scanning (35/42 complete)               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 83% • 0:01:15   │
│                                                   │
│  📦 Current Extension:                           │
│     ms-python.python v2024.10.0                  │
│                                                   │
│  🔄 Progress: Analyzing dependencies... (45%)    │
│                                                   │
│  ─────────────────────────────────────────────   │
│                                                   │
│  📊 Results So Far:                              │
│     ✓ Clean Extensions: 28                       │
│     ⚠ Issues Found: 7                            │
│     ✗ Scan Errors: 0                             │
│                                                   │
│  💾 Cache Performance:                           │
│     ⚡ From Cache: 25 (71%)                      │
│     🔍 Fresh Scans: 10 (29%)                     │
│                                                   │
╰───────────────────────────────────────────────────╯
```

**After Scan (final state):**
```
╭───────────── Scan Complete ──────────────╮
│                                           │
│  ✓ Successfully scanned 42 extensions    │
│  ⚠ Found 3 vulnerabilities in 2 exts     │
│  ⚡ Cache hit rate: 71.4%                 │
│  ⏱  Duration: 1m 23s                      │
│                                           │
╰───────────────────────────────────────────╯
```

**Improvements:**
- Live updating display (no scrolling)
- Current extension and progress visible
- Running statistics
- Visual separation of sections
- Clean final summary

### Implementation Details

**Module:** `display.py`

```python
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

class ScanDashboard:
    """Real-time dashboard for scan progress."""

    def __init__(self, total_extensions: int):
        self.total = total_extensions
        self.current = 0
        self.current_extension = ""
        self.current_progress = ""
        self.clean_count = 0
        self.issues_count = 0
        self.error_count = 0
        self.cached_count = 0
        self.fresh_count = 0

    def update(self, **kwargs):
        """Update dashboard state."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def generate_panel(self) -> Panel:
        """Generate the dashboard panel."""
        content = Text()

        # Header
        content.append(f"Status: Scanning ({self.current}/{self.total} complete)\n\n", style="bold")

        # Current extension
        content.append("📦 Current Extension:\n", style="cyan")
        content.append(f"   {self.current_extension}\n\n", style="white")

        # Progress
        if self.current_progress:
            content.append("🔄 Progress: ", style="cyan")
            content.append(f"{self.current_progress}\n\n", style="yellow")

        content.append("─" * 50 + "\n\n")

        # Results
        content.append("📊 Results So Far:\n", style="cyan")
        content.append(f"   ✓ Clean Extensions: {self.clean_count}\n", style="green")
        content.append(f"   ⚠ Issues Found: {self.issues_count}\n", style="yellow")
        content.append(f"   ✗ Scan Errors: {self.error_count}\n\n", style="red")

        # Cache stats
        content.append("💾 Cache Performance:\n", style="cyan")
        total_processed = self.cached_count + self.fresh_count
        cache_pct = (self.cached_count / total_processed * 100) if total_processed > 0 else 0
        content.append(f"   ⚡ From Cache: {self.cached_count} ({cache_pct:.0f}%)\n", style="green")
        content.append(f"   🔍 Fresh Scans: {self.fresh_count}\n", style="blue")

        return Panel(content, title="VS Code Security Scan", border_style="blue")

# Usage in scan_extensions():
dashboard = ScanDashboard(total_extensions=len(extensions))
with Live(dashboard.generate_panel(), refresh_per_second=4) as live:
    for ext in extensions:
        dashboard.update(
            current=idx,
            current_extension=f"{ext['id']} v{ext['version']}",
            current_progress="Analyzing..."
        )
        live.update(dashboard.generate_panel())
        # ... perform scan ...
```

**Configuration:**
- Enabled by default in terminal mode
- Disabled automatically if:
  - stdout is not a TTY (e.g., piped to file)
  - `--plain` flag is used
  - `--output` flag is used (results go to file)
- Can be explicitly disabled with `--no-dashboard`

---

## Feature 4: Typer CLI Framework

### Current Behavior

**Using argparse:**
```bash
python vscan.py --help
python vscan.py --output results.json --verbose
python vscan.py --cache-stats
python vscan.py --clear-cache
```

**Help Output:**
```
usage: vscan.py [-h] [--extensions-dir EXTENSIONS_DIR] [--output OUTPUT]
                [--delay DELAY] [--verbose] [--max-retries MAX_RETRIES]
                ...

VS Code Extension Security Scanner - Audit installed extensions using vscan.dev

optional arguments:
  -h, --help            show this help message and exit
  --extensions-dir EXTENSIONS_DIR, -d EXTENSIONS_DIR
                        Path to VS Code extensions directory
  ...
```

**Problems:**
- All options in one flat list (hard to read)
- Cache operations mixed with scan options
- Help text is basic and plain
- No command organization
- No examples in help

### Proposed Behavior

**Using Typer:**
```bash
vscan scan --output results.json --verbose
vscan cache-stats
vscan cache-clear
vscan --help
```

**Help Output:**
```
╭─ VS Code Extension Security Scanner v3.0.0 ───────╮
│                                                    │
│  🔍 Security audit tool for VS Code extensions    │
│  Powered by vscan.dev                             │
│                                                    │
╰────────────────────────────────────────────────────╯

Usage: vscan [OPTIONS] COMMAND [ARGS]...

╭─ Commands ────────────────────────────────────────╮
│                                                    │
│  scan           Scan installed VS Code extensions │
│  cache-stats    Display cache statistics          │
│  cache-clear    Clear the scan cache              │
│                                                    │
╰────────────────────────────────────────────────────╯

╭─ Global Options ──────────────────────────────────╮
│                                                    │
│  --help     -h    Show this help message          │
│  --version  -V    Show version information        │
│                                                    │
╰────────────────────────────────────────────────────╯

Examples:
  $ vscan scan                           # Scan all extensions
  $ vscan scan --publisher microsoft     # Filter by publisher
  $ vscan scan --output report.html      # Generate HTML report
  $ vscan scan --plain                   # Plain output (no colors)
  $ vscan cache-stats                    # View cache statistics
  $ vscan cache-clear                    # Clear all cached data

For detailed help on a command:
  $ vscan COMMAND --help
```

**Scan Command Help:**
```bash
$ vscan scan --help
```

```
Usage: vscan scan [OPTIONS]

Scan installed VS Code extensions for security vulnerabilities.

╭─ Basic Options ───────────────────────────────────╮
│                                                    │
│  --verbose          -v    Show detailed progress  │
│  --quiet            -q    Minimal output          │
│  --plain                  Disable colors/tables   │
│                                                    │
╰────────────────────────────────────────────────────╯

╭─ Output Options ──────────────────────────────────╮
│                                                    │
│  --output      -o PATH    Save to file (.json/.html)
│  --detailed               Include full analysis   │
│                                                    │
╰────────────────────────────────────────────────────╯

╭─ Filtering Options ───────────────────────────────╮
│                                                    │
│  --publisher TEXT         Filter by publisher     │
│  --include-ids TEXT       Comma-separated IDs     │
│  --exclude-ids TEXT       Comma-separated IDs     │
│  --min-risk-level LEVEL   Minimum risk level      │
│                                                    │
╰────────────────────────────────────────────────────╯

╭─ Advanced Options ────────────────────────────────╮
│                                                    │
│  --extensions-dir  -d PATH  Custom extensions dir │
│  --delay           -t FLOAT Request delay (sec)   │
│  --max-retries INT          Max retry attempts    │
│  --retry-delay FLOAT        Retry backoff delay   │
│                                                    │
╰────────────────────────────────────────────────────╯

╭─ Cache Options ───────────────────────────────────╮
│                                                    │
│  --no-cache              Disable caching          │
│  --refresh-cache         Force refresh all        │
│  --cache-dir PATH        Custom cache location    │
│  --cache-max-age INT     Max age in days (def: 7) │
│                                                    │
╰────────────────────────────────────────────────────╯

Examples:
  $ vscan scan
  $ vscan scan --publisher microsoft --verbose
  $ vscan scan --output report.html --detailed
```

**Improvements:**
- Organized command structure
- Grouped options by category
- Rich formatted help
- Examples included
- Subcommands for clarity
- Better descriptions

### Implementation Details

**Module:** `cli.py`

```python
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console

app = typer.Typer(
    name="vscan",
    help="🔍 VS Code Extension Security Scanner",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()

@app.command()
def scan(
    # Output options
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file path (.json or .html)",
        rich_help_panel="Output Options"
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        help="Include detailed security analysis",
        rich_help_panel="Output Options"
    ),

    # Display options
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed progress",
        rich_help_panel="Basic Options"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Minimal output",
        rich_help_panel="Basic Options"
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Disable colors and rich formatting",
        rich_help_panel="Basic Options"
    ),

    # Filtering options
    publisher: Optional[str] = typer.Option(
        None,
        "--publisher",
        help="Filter by publisher name",
        rich_help_panel="Filtering Options"
    ),
    include_ids: Optional[str] = typer.Option(
        None,
        "--include-ids",
        help="Comma-separated extension IDs to scan",
        rich_help_panel="Filtering Options"
    ),
    exclude_ids: Optional[str] = typer.Option(
        None,
        "--exclude-ids",
        help="Comma-separated extension IDs to exclude",
        rich_help_panel="Filtering Options"
    ),
    min_risk_level: Optional[str] = typer.Option(
        None,
        "--min-risk-level",
        help="Minimum risk level (low, medium, high, critical)",
        rich_help_panel="Filtering Options"
    ),

    # Advanced options
    extensions_dir: Optional[Path] = typer.Option(
        None,
        "--extensions-dir", "-d",
        help="Path to VS Code extensions directory",
        rich_help_panel="Advanced Options"
    ),
    delay: float = typer.Option(
        1.5,
        "--delay", "-t",
        min=0.1,
        max=30.0,
        help="Delay between API requests (seconds)",
        rich_help_panel="Advanced Options"
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        min=0,
        max=10,
        help="Maximum retry attempts for failed requests",
        rich_help_panel="Advanced Options"
    ),
    retry_delay: float = typer.Option(
        2.0,
        "--retry-delay",
        min=0.1,
        max=60.0,
        help="Base delay for exponential backoff (seconds)",
        rich_help_panel="Advanced Options"
    ),

    # Cache options
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable caching (always scan fresh)",
        rich_help_panel="Cache Options"
    ),
    refresh_cache: bool = typer.Option(
        False,
        "--refresh-cache",
        help="Force refresh of all cached results",
        rich_help_panel="Cache Options"
    ),
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        help="Custom cache directory path",
        rich_help_panel="Cache Options"
    ),
    cache_max_age: int = typer.Option(
        7,
        "--cache-max-age",
        min=1,
        max=365,
        help="Maximum age of cached results (days)",
        rich_help_panel="Cache Options"
    ),
):
    """
    Scan installed VS Code extensions for security vulnerabilities.

    Examples:

        $ vscan scan

        $ vscan scan --publisher microsoft --verbose

        $ vscan scan --output report.html --detailed
    """
    # Import main scan logic
    from vscode_scanner.scanner import run_scan

    exit_code = run_scan(
        output=output,
        detailed=detailed,
        verbose=verbose,
        quiet=quiet,
        plain=plain,
        publisher=publisher,
        include_ids=include_ids,
        exclude_ids=exclude_ids,
        min_risk_level=min_risk_level,
        extensions_dir=extensions_dir,
        delay=delay,
        max_retries=max_retries,
        retry_delay=retry_delay,
        no_cache=no_cache,
        refresh_cache=refresh_cache,
        cache_dir=cache_dir,
        cache_max_age=cache_max_age,
    )

    raise typer.Exit(code=exit_code)


@app.command("cache-stats")
def cache_stats(
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        help="Custom cache directory path"
    ),
    cache_max_age: int = typer.Option(
        7,
        "--cache-max-age",
        min=1,
        max=365,
        help="Maximum age threshold (days)"
    ),
):
    """
    Display cache statistics and health information.

    Shows total cached entries, database size, risk breakdown,
    and age statistics.
    """
    from vscode_scanner.cache_manager import CacheManager
    from vscode_scanner.display import display_cache_stats

    cache_manager = CacheManager(cache_dir=cache_dir)
    stats = cache_manager.get_cache_stats(max_age_days=cache_max_age)

    display_cache_stats(stats, cache_max_age)

    raise typer.Exit(code=0)


@app.command("cache-clear")
def cache_clear(
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        help="Custom cache directory path"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt"
    ),
):
    """
    Clear all cached scan results.

    This will remove all cached extension data, forcing fresh
    scans on the next run.
    """
    from vscode_scanner.cache_manager import CacheManager

    if not force:
        confirm = typer.confirm("Are you sure you want to clear all cached data?")
        if not confirm:
            console.print("❌ Cancelled", style="yellow")
            raise typer.Exit(code=1)

    cache_manager = CacheManager(cache_dir=cache_dir)
    count = cache_manager.clear_cache()

    console.print(f"✓ Cleared {count} cache entries", style="green bold")

    raise typer.Exit(code=0)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version", "-V",
        help="Show version information"
    ),
):
    """
    🔍 VS Code Extension Security Scanner

    Audit installed VS Code extensions for security vulnerabilities
    using the vscan.dev analysis service.
    """
    if version:
        from vscode_scanner._version import __version__
        console.print(f"vscan version {__version__}", style="bold cyan")
        raise typer.Exit(code=0)

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
```

**Entry Point (vscan.py):**
```python
#!/usr/bin/env python3
"""VS Code Extension Security Scanner - CLI wrapper."""

from vscode_scanner.cli import app

if __name__ == "__main__":
    app()
```

**Console Script (pyproject.toml):**
```toml
[project.scripts]
vscan = "vscode_scanner.cli:app"
```

---

## Technical Implementation

### Code Structure Changes

```
vscode_scanner/
├── __init__.py                 # Package init
├── _version.py                 # Version: 3.0.0
├── cli.py                      # NEW: Typer CLI app (300 lines)
├── display.py                  # NEW: Rich display components (400 lines)
├── scanner.py                  # NEW: Refactored main logic from vscan.py
├── vscan_api.py                # Existing API client
├── cache_manager.py            # Existing cache manager
├── extension_discovery.py      # Existing discovery
├── output_formatter.py         # Existing formatter
├── html_report_generator.py    # Existing HTML generator
└── utils.py                    # Existing utilities

vscan.py                        # Simplified wrapper (10 lines)
pyproject.toml                  # Updated dependencies
setup.py                        # Updated entry points
```

### New Module: display.py

**Responsibilities:**
- Rich progress bar creation
- Table generation for all outputs
- Live dashboard management
- Console output formatting
- Color scheme definitions

**Key Classes:**
```python
class ScanDashboard:
    """Real-time scan status dashboard."""

class ResultsDisplay:
    """Format and display scan results."""

class CacheStatsDisplay:
    """Format and display cache statistics."""
```

**Key Functions:**
```python
def create_scan_progress() -> Progress
def create_results_table(results: List[Dict]) -> Table
def create_cache_stats_table(stats: Dict) -> Table
def display_summary(results: Dict, duration: float) -> None
def display_filter_help(args, original_count: int) -> None
```

### New Module: cli.py

**Responsibilities:**
- Typer app configuration
- Command definitions (scan, cache-stats, cache-clear)
- Argument parsing and validation
- Help text and examples
- Version display

### Refactored Module: scanner.py

**Responsibilities:**
- Core scan logic (moved from vscan.py main())
- Integration with display.py for output
- Configuration from CLI arguments
- Exit code calculation

**Key Function:**
```python
def run_scan(**kwargs) -> int:
    """
    Main scan logic.

    Args:
        All CLI arguments as keyword arguments

    Returns:
        Exit code (0=success, 1=vulnerabilities, 2=error)
    """
```

### Display Configuration

**Plain Mode (--plain flag):**
- Disable all Rich formatting
- Use basic text output (current behavior)
- For CI/CD, scripts, non-TTY environments

**Quiet Mode (--quiet flag):**
- Minimal output
- Only show final summary
- No progress bars or dashboards

**Verbose Mode (--verbose flag):**
- Show all progress details
- Individual extension progress updates
- API retry information
- Cache hits/misses

**Auto-detection:**
```python
def should_use_rich() -> bool:
    """Determine if Rich output should be used."""
    # Don't use Rich if:
    # - --plain flag is set
    # - stdout is not a TTY (piped/redirected)
    # - TERM environment variable is "dumb"
    # - NO_COLOR environment variable is set
    return (
        not args.plain
        and sys.stdout.isatty()
        and os.environ.get("TERM") != "dumb"
        and not os.environ.get("NO_COLOR")
    )
```

---

## API Changes

### Command Structure

**Before (v2.x):**
```bash
# All operations through main script with flags
python vscan.py [OPTIONS]
python vscan.py --cache-stats
python vscan.py --clear-cache
```

**After (v3.0):**
```bash
# Organized subcommands
vscan scan [OPTIONS]
vscan cache-stats [OPTIONS]
vscan cache-clear [OPTIONS]
vscan --version
vscan --help
```

### New Flags

**Display Control:**
- `--plain`: Disable Rich formatting (fallback to v2.x style)
- `--quiet`: Minimal output mode
- `--no-dashboard`: Disable live dashboard (keep progress bar)

**Cache Commands:**
- `vscan cache-stats`: Dedicated subcommand (was `--cache-stats`)
- `vscan cache-clear`: Dedicated subcommand (was `--clear-cache`)
- Added `--force` flag to `cache-clear` to skip confirmation

### Removed Flags

None - all existing flags maintained for backward compatibility in `scan` subcommand.

### Exit Codes

**Unchanged:**
- `0`: Scan completed successfully, no vulnerabilities found
- `1`: Scan completed successfully, vulnerabilities found
- `2`: Scan failed due to errors

---

## Visual Examples

### Example 1: Simple Scan

**Command:**
```bash
$ vscan scan --publisher Anthropic
```

**Output:**
```
╭────────────── VS Code Extension Scanner v3.0.0 ──────────────╮
│                                                               │
│  🔍 Scanning installed VS Code extensions                   │
│  Publisher filter: Anthropic                                 │
│                                                               │
╰───────────────────────────────────────────────────────────────╯

Discovering Extensions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

  ✓ Found 2 extensions matching filters (68 total discovered)

Scanning Extensions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2/2 100% 0:00:01

  ⚡ Anthropic.claude-code v2.0.25 [cached] ✓
  ⚡ Anthropic.claude-code v2.0.26 [cached] ✓

╭─────────────────── Scan Results ────────────────────╮
│                                                      │
│  ┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┓  │
│  ┃ Extension            ┃ Risk  ┃ Score ┃ Vulns┃  │
│  ┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━┩  │
│  │ claude-code v2.0.25  │ 🟡 MED│ 85/100│ 0    │  │
│  │ claude-code v2.0.26  │ 🟡 MED│ 85/100│ 0    │  │
│  └──────────────────────┴───────┴───────┴──────┘  │
│                                                      │
│  ✓ 2 extensions scanned • 0 vulnerabilities        │
│  ⚡ Cache hit rate: 100% • Duration: 1.2s          │
│                                                      │
╰──────────────────────────────────────────────────────╯
```

### Example 2: Scan with Issues

**Command:**
```bash
$ vscan scan --verbose
```

**Output (during scan):**
```
╭────────────── VS Code Security Scan ─────────────╮
│                                                   │
│  Status: Scanning (15/42 complete)               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 36% • 0:00:45   │
│                                                   │
│  📦 Current Extension:                           │
│     dbaeumer.vscode-eslint v2.4.2                │
│                                                   │
│  🔄 Progress: Analyzing dependencies... (67%)    │
│                                                   │
│  ─────────────────────────────────────────────   │
│                                                   │
│  📊 Results So Far:                              │
│     ✓ Clean Extensions: 12                       │
│     ⚠ Issues Found: 3                            │
│     ✗ Scan Errors: 0                             │
│                                                   │
│  💾 Cache Performance:                           │
│     ⚡ From Cache: 10 (67%)                      │
│     🔍 Fresh Scans: 5 (33%)                      │
│                                                   │
╰───────────────────────────────────────────────────╯
```

**Output (final):**
```
╭─────────────────── Scan Results ────────────────────╮
│                                                      │
│  ┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┓  │
│  ┃ Extension            ┃ Risk  ┃ Score ┃ Vulns┃  │
│  ┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━┩  │
│  │ ms-python.python     │ 🟢 LOW│ 95/100│ 0    │  │
│  │ prettier-vscode      │ 🟡 MED│ 82/100│ 0    │  │
│  │ vscode-eslint        │ 🔴 HI │ 65/100│ 2    │  │
│  │ docker               │ 🟢 LOW│ 90/100│ 0    │  │
│  │ githistory           │ 🟡 MED│ 75/100│ 1    │  │
│  │ ... (37 more)        │       │       │      │  │
│  └──────────────────────┴───────┴───────┴──────┘  │
│                                                      │
│  ⚠ 42 extensions scanned • 3 vulnerabilities       │
│  ⚡ Cache hit rate: 71.4% • Duration: 1m 23s       │
│                                                      │
╰──────────────────────────────────────────────────────╯

╭────────────── Cache Statistics ──────────────╮
│                                               │
│  ┏━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┓  │
│  ┃ Metric          ┃ Count ┃ Details     ┃  │
│  ┡━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━┩  │
│  │ From Cache      │    30 │ ⚡ instant   │  │
│  │ Fresh Scans     │    12 │ 🔍 API calls │  │
│  │ Cache Hit Rate  │ 71.4% │             │  │
│  └─────────────────┴───────┴─────────────┘  │
│                                               │
╰───────────────────────────────────────────────╯
```

### Example 3: Cache Stats Command

**Command:**
```bash
$ vscan cache-stats
```

**Output:**
```
╭──────────────── Cache Statistics ────────────────╮
│                                                   │
│  Database: ~/.vscan/cache.db                     │
│  Total entries: 156                              │
│  Database size: 245.3 KB                         │
│                                                   │
│  ─────────────────────────────────────────────   │
│                                                   │
│  Age Distribution:                               │
│    Fresh (< 1 day):     42 entries (27%)         │
│    Recent (1-3 days):   68 entries (44%)         │
│    Older (3-7 days):    31 entries (20%)         │
│    Stale (> 7 days):    15 entries (10%) ⚠       │
│                                                   │
│  Average age: 3.2 days                           │
│                                                   │
│  ─────────────────────────────────────────────   │
│                                                   │
│  ┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓        │
│  ┃ Risk Level   ┃ Count  ┃ Percentage ┃        │
│  ┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩        │
│  │ 🔴 High      │     12 │      7.7%  │        │
│  │ 🟡 Medium    │     58 │     37.2%  │        │
│  │ 🟢 Low       │     86 │     55.1%  │        │
│  └──────────────┴────────┴────────────┘        │
│                                                   │
│  Extensions with vulnerabilities: 23 (14.7%)     │
│                                                   │
│  ⚠ Tip: 15 stale entries detected               │
│     Run 'vscan scan --refresh-cache' to update  │
│                                                   │
╰───────────────────────────────────────────────────╯
```

### Example 4: Plain Mode (CI/CD)

**Command:**
```bash
$ vscan scan --plain --publisher Anthropic
```

**Output (v2.x compatible):**
```
VS Code Extension Scanner
Version 3.0.0
============================================================

Step 1: Discovering VS Code extensions...
[✓] Found VS Code extensions directory: /Users/user/.vscode/extensions
[✓] Discovered 68 extensions
Filtered out 66 extensions based on criteria
[✓] 2 extensions selected for scanning

Step 2: Scanning extensions for vulnerabilities...
Cache enabled (max age: 7 days)
[1/2] Anthropic.claude-code v2.0.25... ⚡ Cached ✓
[2/2] Anthropic.claude-code v2.0.26... ⚡ Cached ✓

============================================================
[✓] Scan Complete!
Total extensions scanned: 2
Successful scans: 2
Failed scans: 0

Cache Statistics:
  From cache: 2 (⚡ instant)
  Fresh scans: 0 (🔍 API calls)
  Cache hit rate: 100.0%

Vulnerabilities found: 0
Scan duration: 0.0 seconds
Average time per extension: 0.0s
============================================================
```

---

## Testing Strategy

### Unit Tests

**New test file:** `tests/test_display.py`

```python
def test_create_results_table():
    """Test Rich table generation for scan results."""

def test_create_cache_stats_table():
    """Test cache statistics table formatting."""

def test_scan_dashboard_update():
    """Test dashboard state updates."""

def test_display_auto_detection():
    """Test should_use_rich() logic."""
```

**New test file:** `tests/test_cli.py`

```python
def test_scan_command_basic():
    """Test basic scan command invocation."""

def test_scan_command_with_filters():
    """Test scan with publisher/ID filters."""

def test_cache_stats_command():
    """Test cache-stats subcommand."""

def test_cache_clear_command():
    """Test cache-clear subcommand."""

def test_version_flag():
    """Test --version output."""

def test_help_output():
    """Test help formatting."""
```

### Integration Tests

**Update:** `tests/test_integration.py`

```python
def test_scan_with_rich_output():
    """Test full scan with Rich display enabled."""

def test_scan_with_plain_output():
    """Test scan with --plain flag (v2.x compatible)."""

def test_live_dashboard_update():
    """Test real-time dashboard updates during scan."""

def test_ci_mode_detection():
    """Test auto-detection of CI environment (should use plain)."""
```

### Manual Testing Scenarios

1. **Terminal Compatibility**
   - macOS Terminal.app
   - iTerm2
   - VS Code integrated terminal
   - SSH session
   - Linux terminal (Ubuntu, Fedora)
   - Windows Terminal
   - Windows CMD (fallback to plain)

2. **Output Redirection**
   - `vscan scan > output.txt` (should auto-detect and use plain)
   - `vscan scan | less` (should auto-detect and use plain)
   - `vscan scan --plain` (explicitly plain)

3. **Progress Display**
   - Small scan (< 5 extensions)
   - Medium scan (10-50 extensions)
   - Large scan (> 100 extensions)
   - Scan with all cached results (fast)
   - Scan with all fresh results (slow)

4. **Error Scenarios**
   - Network failures during scan (with retry)
   - Invalid extension directory
   - No extensions found
   - All extensions filtered out

5. **Help Output**
   - `vscan --help`
   - `vscan scan --help`
   - `vscan cache-stats --help`
   - `vscan cache-clear --help`

### CI/CD Testing

Add to GitHub Actions workflow:

```yaml
- name: Test CLI output modes
  run: |
    # Test plain mode in CI
    vscan scan --plain --publisher test

    # Test that CI environment auto-detects plain mode
    vscan scan --publisher test

    # Verify exit codes
    vscan scan && echo "Exit code 0 works"
```

---

## Migration Path

### Version 2.3.1 → 3.0.0

**Breaking Changes:**
1. Command structure changed to subcommands
2. Installation requires `pip install vscan` (with dependencies)
3. Entry point changed from `python vscan.py` to `vscan` command

**Non-Breaking Changes:**
- All flags and options preserved in `scan` subcommand
- Plain mode (`--plain`) provides v2.x compatible output
- Exit codes unchanged
- JSON/HTML output formats unchanged

### Migration for Users

**Old Usage (v2.x):**
```bash
python vscan.py --verbose --output results.json
python vscan.py --cache-stats
python vscan.py --clear-cache
```

**New Usage (v3.0):**
```bash
vscan scan --verbose --output results.json
vscan cache-stats
vscan cache-clear
```

**For Scripts/CI:**
```bash
# Add --plain for v2.x compatible output
vscan scan --plain --verbose --output results.json
```

### Migration for Developers

**Code Organization:**
- `vscan.py` main() → `scanner.py` run_scan()
- Progress output → `display.py` components
- Argument parsing → `cli.py` Typer app

**Import Changes:**
```python
# Old (v2.x)
from vscan import main

# New (v3.0)
from vscode_scanner.scanner import run_scan
from vscode_scanner.cli import app
```

---

## Dependencies

### pyproject.toml

```toml
[project]
name = "vscan"
version = "3.0.0"
description = "VS Code Extension Security Scanner"
requires-python = ">=3.8"

dependencies = [
    "rich>=13.0.0,<14.0.0",
    "typer>=0.9.0,<1.0.0",
]

[project.scripts]
vscan = "vscode_scanner.cli:app"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
```

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="vscan",
    version="3.0.0",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0,<14.0.0",
        "typer>=0.9.0,<1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "vscan=vscode_scanner.cli:app",
        ],
    },
    python_requires=">=3.8",
)
```

---

## Success Criteria

1. **Functionality**
   - ✓ All v2.x features work identically
   - ✓ Exit codes unchanged
   - ✓ JSON/HTML output formats unchanged
   - ✓ Cache functionality identical

2. **UX Improvements**
   - ✓ Live progress bars during scans
   - ✓ Rich formatted tables for all output
   - ✓ Real-time dashboard updates
   - ✓ Organized help with examples
   - ✓ Subcommands for clarity

3. **Compatibility**
   - ✓ Works in terminal and CI/CD
   - ✓ Auto-detects plain mode when needed
   - ✓ `--plain` flag for explicit fallback
   - ✓ Tests pass on macOS, Linux, Windows

4. **Code Quality**
   - ✓ Clean separation of concerns
   - ✓ All existing tests pass
   - ✓ New tests for Rich/Typer features
   - ✓ Documentation updated

---

## Timeline Estimate

- **Setup & Dependencies:** 30 minutes
- **display.py Implementation:** 2-3 hours
- **cli.py Implementation:** 1-2 hours
- **scanner.py Refactoring:** 1 hour
- **Integration & Testing:** 1-2 hours
- **Documentation Updates:** 1 hour

**Total: 6-9 hours** (single development session or 1-2 days)

---

## Future Enhancements

**Not in scope for v3.0, potential for v3.1+:**

1. **Interactive Mode**
   - Use `rich.prompt` for user input
   - Select extensions to scan interactively
   - Configure options via prompts

2. **Custom Themes**
   - User-defined color schemes
   - Configuration file for appearance

3. **Export Formats**
   - PDF reports
   - Markdown summaries
   - CSV for spreadsheet import

4. **Notifications**
   - Desktop notifications on completion
   - Email/Slack integration for CI

5. **Plugin System**
   - Custom output formatters
   - Additional security data sources

---

## References

- **Rich Documentation:** https://rich.readthedocs.io/
- **Typer Documentation:** https://typer.tiangolo.com/
- **Current Implementation:** vscan v2.3.1
- **Design Inspiration:**
  - `poetry` - Modern Python packaging tool
  - `httpie` - Beautiful HTTP client
  - `rich-cli` - Reference implementation

---

## Appendix: Color Scheme

### Risk Levels
- 🔴 **Critical/High:** Red (`#FF0000`)
- 🟡 **Medium:** Yellow (`#FFA500`)
- 🟢 **Low:** Green (`#00FF00`)
- ⚪ **Unknown:** Gray (`#808080`)

### Status Indicators
- ✓ **Success:** Green
- ⚠ **Warning:** Yellow
- ✗ **Error:** Red
- ⚡ **Cached:** Cyan
- 🔍 **Scanning:** Blue

### UI Elements
- **Borders:** Blue (`#0000FF`)
- **Headers:** Bold Cyan
- **Values:** White
- **Dimmed:** Gray (`#808080`)

---

**END OF SPECIFICATION**
