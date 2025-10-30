# Architecture Documentation

**Document Type:** Timeless Reference
**Applies To:** All 3.x versions
**Major Revision Trigger:** Layer count changes, module organization refactors, or architectural pattern shifts
**See:** [CHANGELOG.md](../../CHANGELOG.md) for version-specific changes

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Principles](#design-principles)
3. [Layered Architecture](#layered-architecture)
4. [Module Responsibilities](#module-responsibilities)
5. [Dependency Rules](#dependency-rules)
6. [Data Flow](#data-flow)
7. [Error Handling Strategy](#error-handling-strategy)
8. [Configuration Management](#configuration-management)
9. [Observability](#observability)
10. [Parallel Scanning Architecture](#parallel-scanning-architecture)
11. [What We DON'T Do (Avoiding Over-Engineering)](#what-we-dont-do)

---

## Architecture Overview

VS Code Extension Security Scanner uses a **Simple Layered Architecture** designed for maintainability and clarity without over-engineering.

### Size & Complexity

**Current Metrics:** Run `cloc vscode_scanner/ --by-file` for current line counts and `ls vscode_scanner/*.py | wc -l` for module count

**Baseline (v3.5.x):**
- ~9,800 lines of Python code
- 14 modules organized in flat structure
- 3 architectural layers (Presentation, Application, Infrastructure)
- No sub-packages (flat structure sufficient for this size)

### Architectural Style

**Simple Layered Architecture** with strict dependency rules:

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (CLI & Output)                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • User interaction via CLI                             │
│  • Output formatting (terminal, JSON, HTML, CSV)        │
│  • Progress display and error messages                  │
├─────────────────────────────────────────────────────────┤
│  APPLICATION LAYER (Business Logic)                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Scan orchestration                                   │
│  • Configuration management                             │
│  • Business rules                                       │
├─────────────────────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER (External Services)               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • vscan.dev API client                                 │
│  • SQLite cache operations                              │
│  • Filesystem operations                                │
└─────────────────────────────────────────────────────────┘

        Cross-Layer Utilities
        ━━━━━━━━━━━━━━━━━━━━━━
        • utils.py (helpers)
        • constants.py (shared values)
```

---

## Design Principles

### 1. KISS (Keep It Simple, Stupid)

**What This Means:**
- No unnecessary abstractions
- Standard library first
- Solve the problem simply, then optimize if needed
- Flat structure until complexity demands otherwise

**Examples:**
- ✅ Use `SimpleNamespace` for configuration objects
- ❌ Don't create custom config classes
- ✅ Use SQLite directly (no ORM)
- ❌ Don't add repository pattern

### 2. Command-Query Separation (CLI)

**Commands** (modify state):
- `vscan scan` - Performs scans, modifies cache
- `vscan cache clear` - Modifies cache

**Queries** (read-only):
- `vscan report` - Reads from cache only
- `vscan cache stats` - Reads cache statistics
- `vscan config show` - Reads configuration

**Benefits:**
- Predictable behavior
- Easy to compose (`vscan scan && vscan report output.html`)
- Safe for automation

### 3. Explicit Over Implicit

**Prefer:**
- Explicit error messages with suggestions
- Clear command names (`scan` vs `run`)
- Verbose help text
- Documented configuration precedence

**Avoid:**
- Magic behavior (auto-scanning when generating reports)
- Implicit conversions
- Hidden side effects

### 4. Fail Fast with Helpful Guidance

**Philosophy:**
- Detect errors early
- Provide actionable error messages
- Include suggestions for fixing issues
- Exit with meaningful codes (0, 1, 2)

**Example:**
```bash
$ vscan report output.html
✗ Error: Cannot generate report: Cache is empty.

Suggestions:
  • Run 'vscan scan' first to populate the cache
  • Then run 'vscan report <output>' to generate the report

Quick workflow:
  vscan scan && vscan report report.html
```

### 5. Observability Without Noise

**Balance:**
- Track metrics for debugging (retry stats, cache hit rates)
- Hide details by default (clean output)
- Show details in verbose mode (`--verbose`)
- Always include in structured output (JSON)

---

## Layered Architecture

### Layer 1: Presentation Layer

**Purpose:** Handle all user interaction and output formatting.

**Modules:**
- `cli.py` - Typer command definitions and CLI interface
- `display.py` - Rich terminal formatting and progress indicators
- `output_formatter.py` - JSON and CSV output formatters
- `html_report_generator.py` - HTML report generation

**Responsibilities:**
- Parse command-line arguments
- Display progress and results to user
- Format output in various formats
- Handle user prompts and confirmations

**Dependencies:**
- Can import from Application layer (scanner, config_manager)
- Can import from shared utilities (utils, constants)
- Should NOT import from Infrastructure directly

**Key Design Decisions:**
- Rich and Typer are **required dependencies** (not optional)
- `--plain` flag provides non-Rich output for CI/CD
- All user-facing errors route through `display.py`

### Layer 2: Application Layer

**Purpose:** Orchestrate business logic and workflows.

**Modules:**
- `scanner.py` - Scan orchestration and coordination
- `vscan.py` - Application entry point
- `config_manager.py` - Configuration file management

**Responsibilities:**
- Coordinate scanning workflow
- Apply business rules (filtering, retry logic)
- Manage configuration hierarchy (CLI > Config > Defaults)
- Aggregate results from infrastructure

**Dependencies:**
- Can import from Infrastructure layer
- Can import from shared utilities
- Limited imports from Presentation (only display.py for progress)

**Key Design Decisions:**
- Scanner uses batch operations for cache writes
- Configuration precedence is strictly enforced
- Filtering logic centralized in scanner

### Layer 3: Infrastructure Layer

**Purpose:** Interface with external systems and services.

**Modules:**
- `vscan_api.py` - HTTP client for vscan.dev API
- `cache_manager.py` - SQLite cache operations
- `extension_discovery.py` - Filesystem operations for extension discovery

**Responsibilities:**
- Make HTTP requests to vscan.dev
- Perform database operations (CRUD)
- Read extension metadata from filesystem
- Handle network errors and retries

**Dependencies:**
- Can ONLY import from shared utilities (utils, constants)
- CANNOT import from Application or Presentation layers
- No knowledge of CLI or display logic

**Key Design Decisions:**
- Intelligent retry with exponential backoff
- Cache schema versioning (currently v2)
- Automatic cache migration from v1 to v2
- Cross-platform extension discovery

### Shared Utilities

**Purpose:** Provide common functionality used by all layers.

**Modules:**
- `utils.py` - Helper functions (error sanitization, file operations)
- `constants.py` - Shared constants and configuration defaults
- `types.py` - Common data types and result objects (CacheWarning, CacheError, CacheInfo, ConfigWarning)

**Characteristics:**
- No dependencies on other application modules
- Pure functions where possible
- Cross-platform compatibility
- Shared data types for layer separation

**Key Functions:**
- `sanitize_error_message()` - Security-safe error display
- `safe_mkdir()`, `safe_touch()` - Cross-platform file operations
- `get_error_help()` - Contextual error suggestions

**Key Types:**
- `CacheWarning`, `CacheError`, `CacheInfo` - Cache operation results
- `ConfigWarning` - Configuration loading warnings

---

## Module Responsibilities

### cli.py (Presentation)

```python
# Responsibilities:
# 1. Define Typer commands and arguments
# 2. Route commands to appropriate functions
# 3. Handle user confirmations
# 4. Exit with appropriate codes

# Key Functions:
- scan() - Main scan command
- cache_stats() - Display cache statistics
- cache_clear() - Clear cache with confirmation
- report() - Generate reports from cache
- config_*() - Configuration management commands
```

**Lines of Code:** Run `wc -l vscode_scanner/cli.py` for current count (baseline: ~900)
**Dependencies:** scanner, display, config_manager, utils

**CLI Architecture (Typer/Rich Integration - v3.0+):**

**Typer App Configuration:**
```python
app = typer.Typer(
    name="vscan",
    help="VS Code Extension Security Scanner",
    add_completion=False,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False  # Custom error handling
)
```

**Help Panel Organization:**
- **Main Commands** - Primary operations (scan, report)
- **Cache Management** - Cache operations (stats, clear)
- **Configuration** - Config file management (init, show, set, get)
- Organized help reduces cognitive load for users

**Command Structure Rationale:**
- Subcommands over flags (clearer intent: `vscan cache clear` vs `vscan --clear-cache`)
- Consistent verb-noun pattern (`cache clear`, `config show`)
- Short and memorable command names
- Each command has comprehensive help text with examples

**Console Script Entry Points:**
```python
# setup.py configuration
entry_points={
    'console_scripts': [
        'vscan=vscode_scanner.vscan:main',
    ],
}
```

**Key Design Decisions:**
- Rich and Typer are required dependencies (not optional) for consistent UX
- `--plain` flag provides fallback for CI/CD environments
- All user-facing errors route through display.py for centralized formatting
- Command-query separation: Commands modify state (scan, cache clear), Queries read-only (report, cache stats)

### display.py (Presentation)

```python
# Responsibilities:
# 1. Rich formatting for terminal output
# 2. Progress bars and spinners
# 3. Tables and panels
# 4. Error message display

# Key Functions:
- display_scan_results() - Format scan results
- display_scan_summary() - Show summary statistics
- display_error() - Centralized error display
- create_progress_bar() - Live progress tracking
```

**Lines of Code:** Run `wc -l vscode_scanner/display.py` for current count (baseline: ~500)
**Dependencies:** utils, constants

### html_report_generator.py (Presentation)

```python
# Responsibilities:
# 1. Generate self-contained HTML reports
# 2. Embed CSS and JavaScript (no external dependencies)
# 3. Create interactive data visualizations
# 4. Optimize for both screen and print

# Key Functions:
- generate_report() - Main HTML generation
- _generate_header() - Summary and charts
- _generate_overview_table() - Sortable extension table
- _generate_detail_view() - Expandable details
- _generate_pie_chart_svg() - Risk distribution chart
```

**Lines of Code:** Run `wc -l vscode_scanner/html_report_generator.py` for current count (baseline: ~2,300)
**Dependencies:** utils

**Self-Contained HTML Design (v2.2+):**

**Zero External Dependencies:**
- All CSS embedded in `<style>` tags
- All JavaScript embedded in `<script>` tags
- No CDN dependencies (Chart.js, Bootstrap, etc.)
- Works offline and in any environment
- Single HTML file contains complete report

**Embedded CSS Strategy:**
```python
def _generate_styles(self) -> str:
    """Generate embedded CSS (no external stylesheets)."""
    # ~300 lines of CSS embedded directly
    # Includes: Layout, tables, charts, print media queries
    # Works in all modern browsers
```

**Embedded JavaScript Strategy:**
```python
def _generate_scripts(self) -> str:
    """Generate embedded JavaScript (no external libraries)."""
    # ~200 lines of vanilla JavaScript
    # Functions: Table sorting, filtering, row expansion, search
    # No jQuery, React, or other frameworks
```

**Data Visualizations (Pure CSS/SVG):**
- **Pie Charts**: SVG `<path>` elements (no Chart.js)
- **Bar Charts**: Colored `<div>` elements with CSS widths
- **Security Gauges**: Horizontal progress bars with color gradients
- Lightweight and fast (no library overhead)

**Performance Optimizations:**

**1. Collapsible Dependency Lists:**
```python
# Show first 10 dependencies by default
# "Show X more..." button to expand
# Reduces initial DOM size for large reports
```

**2. Lazy Rendering:**
```python
# Detail sections use display: none when collapsed
# Only visible when user expands row
# Minimizes initial rendering time
```

**3. Efficient DOM:**
```python
# Minimize DOM nodes
# Simple CSS selectors (no complex queries)
# Reuse elements where possible
```

**Print Optimization:**
```css
@media print {
  /* Auto-expand all rows for complete report */
  .extension-details { display: block !important; }

  /* Remove interactive controls */
  .controls, .expand-button { display: none; }

  /* Prevent page breaks in extension details */
  .extension-row { page-break-inside: avoid; }

  /* Black & white friendly colors */
  .risk-high { border: 2px solid #000; }
}
```

**Key Design Decisions:**
- Self-contained design enables easy sharing and archival
- No external dependencies reduces security risks (no CDN compromise)
- Works offline (air-gapped environments, security audits)
- Print-friendly format for documentation and compliance
- Performance optimized for reports with 100+ extensions

### scanner.py (Application)

```python
# Responsibilities:
# 1. Orchestrate scan workflow
# 2. Apply filtering (publisher, risk level, IDs)
# 3. Coordinate cache and API operations
# 4. Aggregate results

# Key Functions:
- perform_scan() - Main scan orchestration
- _filter_extensions() - Apply user filters
- _scan_extension() - Scan single extension
- _build_summary() - Aggregate statistics
```

**Lines of Code:** Run `wc -l vscode_scanner/scanner.py` for current count (baseline: ~800)
**Dependencies:** vscan_api, cache_manager, extension_discovery, display

### vscan_api.py (Infrastructure)

```python
# Responsibilities:
# 1. HTTP requests to vscan.dev
# 2. Retry logic with backoff
# 3. Rate limit handling
# 4. Response validation

# Key Functions:
- scan_extension() - Full scan workflow (analyze + poll + results)
- _analyze_extension() - POST /api/extensions/analyze
- _poll_status() - GET /api/extensions/status/{id}
- _get_results() - GET /api/extensions/results/{id}
- _calculate_backoff_delay() - Exponential backoff with ceiling
```

**Lines of Code:** Run `wc -l vscode_scanner/vscan_api.py` for current count (baseline: ~600)
**Dependencies:** utils, constants

**Retry Mechanism (v2.2+):**

The API client implements intelligent retry with exponential backoff and jitter to handle transient failures. See **[ERROR_HANDLING.md](ERROR_HANDLING.md#retry-mechanism)** for comprehensive documentation including:
- Error classification (retryable vs non-retryable)
- Exponential backoff algorithm with jitter
- Retry-After header handling
- Retry statistics tracking
- Configuration best practices

**Key Architectural Decisions:**
- Retry at API client layer (not scanner layer) for cleaner separation
- Non-retryable errors fail immediately (fail-fast principle)
- Retry statistics tracked for observability
- 30-second backoff ceiling prevents DoS from malicious headers

### cache_manager.py (Infrastructure)

```python
# Responsibilities:
# 1. SQLite database operations
# 2. Cache schema management
# 3. Automatic migrations
# 4. Batch operations for performance

# Key Functions:
- get_cached_result() - Retrieve from cache
- save_result() - Save single result
- save_result_batch() - Batch save for performance
- get_cache_stats() - Statistics from indexed columns
- clear_cache() - Clear with optional VACUUM
- _migrate_cache_to_v2() - Schema migration
```

**Lines of Code:** Run `wc -l vscode_scanner/cache_manager.py` for current count (baseline: ~900)
**Dependencies:** utils, constants

### config_manager.py (Application)

```python
# Responsibilities:
# 1. Load/save ~/.vscanrc configuration
# 2. Type validation and conversion
# 3. Configuration precedence
# 4. Schema versioning

# Key Functions:
- load_config() - Load with validation
- save_config() - Write config file
- get() - Get value with precedence
- set() - Set configuration value
- init_config() - Create default config
```

**Lines of Code:** Run `wc -l vscode_scanner/config_manager.py` for current count (baseline: ~400)
**Dependencies:** utils, constants

---

## Dependency Rules

### Allowed Dependencies

```
Presentation Layer:
  cli.py                   → scanner, display, config_manager, utils, constants
  display.py               → utils, constants
  output_formatter.py      → utils, constants
  html_report_generator.py → utils

Application Layer:
  scanner.py       → vscan_api, cache_manager, extension_discovery, display, utils, constants
  vscan.py         → cli, utils, constants
  config_manager.py → utils, constants

Infrastructure Layer:
  vscan_api.py            → utils, constants
  cache_manager.py        → utils, constants
  extension_discovery.py  → utils, constants

Shared Utilities:
  utils.py        → (standard library only)
  constants.py    → (standard library only)
  types.py        → (standard library only)
  _version.py     → (standard library only)
```

### Dependency Rules

**✅ Allowed:**
- Presentation → Application → Infrastructure (downward flow only)
- Any layer → utils.py, constants.py, types.py, _version.py (shared utilities)
- Infrastructure modules can import from other Infrastructure modules

**❌ Forbidden:**
- Infrastructure → Application (e.g., cache_manager → scanner)
- Infrastructure → Presentation (e.g., vscan_api → display)
- Application → Presentation (except scanner → display for progress)
- Circular dependencies at any level

### Import Patterns

**Good Examples:**
```python
# cli.py (Presentation) imports from Application
from .scanner import run_scan
from .display import should_use_rich

# scanner.py (Application) imports from Infrastructure
from .vscan_api import VscanAPIClient
from .cache_manager import CacheManager

# vscan_api.py (Infrastructure) uses only utilities
from .constants import MAX_BACKOFF_DELAY
from .utils import sanitize_error_message
```

**Bad Examples (Violations):**
```python
# ❌ cache_manager.py importing from Presentation
from .display import display_error  # WRONG: Infrastructure → Presentation

# ❌ vscan_api.py importing from Application
from .scanner import run_scan  # WRONG: Infrastructure → Application

# ❌ Circular dependency
# scanner.py imports vscan_api.py, vscan_api.py imports scanner.py
```

### Why These Rules Matter

**Testability:**
- Infrastructure can be tested in isolation (no UI dependencies)
- Mock at layer boundaries (e.g., mock API in Application tests)

**Maintainability:**
- Clear separation of concerns
- Changes in one layer don't cascade unexpectedly
- Easier to understand data flow

**Architecture Preservation:**
- Prevents erosion over time
- Enforces design decisions
- Makes refactoring safer

### How to Enforce

**1. Architecture Tests** (see `tests/test_architecture.py`):
```python
def test_layering_rules():
    """Verify infrastructure doesn't import from application/presentation."""
    infrastructure = ['vscan_api', 'cache_manager', 'extension_discovery']
    forbidden = ['scanner', 'cli', 'display']

    for module in infrastructure:
        assert not imports_any(module, forbidden)
```

**2. Code Review Checklist:**
- [ ] New imports follow layer rules
- [ ] No circular dependencies introduced
- [ ] Infrastructure remains isolated

**3. IDE Configuration:**
- Configure import linter to warn on violations
- Use dependency graph tools (pydeps)

---

## Data Flow

### Scan Workflow

```
User (CLI)
   │
   ├─> cli.py (parse args)
   │      │
   │      └─> scanner.py (orchestrate)
   │             │
   │             ├─> extension_discovery.py (find extensions)
   │             │      └─> Return: List[Extension]
   │             │
   │             ├─> config_manager.py (load config)
   │             │      └─> Return: Config values
   │             │
   │             ├─> cache_manager.py (check cache)
   │             │      ├─> Hit: Return cached result
   │             │      └─> Miss: Continue to API
   │             │
   │             ├─> vscan_api.py (scan extension)
   │             │      ├─> POST /analyze
   │             │      ├─> GET /status (poll)
   │             │      └─> GET /results
   │             │      └─> Return: Security analysis
   │             │
   │             ├─> cache_manager.py (save result)
   │             │
   │             └─> display.py (show progress)
   │
   └─> output_formatter.py (format output)
          ├─> JSON
          ├─> CSV
          └─> HTML
```

### Report Generation Workflow

```
User (CLI)
   │
   ├─> cli.py (report command)
   │      │
   │      └─> cache_manager.py (read cache)
   │             │
   │             ├─> Cache empty? → Error (fail fast)
   │             └─> Cache has data → Continue
   │                    │
   │                    └─> Return: List[CachedResult]
   │
   └─> output_formatter.py (format)
          ├─> JSON report
          ├─> CSV report
          └─> HTML report (html_report_generator.py)
```

### Configuration Loading Workflow

```
CLI Argument
   │
   ├─> Provided? → Use CLI value (highest priority)
   │
   └─> Not provided
          │
          └─> config_manager.py
                 │
                 ├─> Config file exists?
                 │      ├─> Yes: Load value from ~/.vscanrc
                 │      └─> No: Continue
                 │
                 └─> Use default from constants.py (lowest priority)
```

---

## Error Handling Strategy

See **[ERROR_HANDLING.md](ERROR_HANDLING.md)** for complete documentation.

### Architecture Summary

**Error Handling Flow:**
```
Exception occurs
   │
   └─> ErrorHandler.handle_error()
          │
          ├─> Classify error type
          ├─> Get contextual suggestions (ERROR_HELP)
          └─> Return ErrorContext
                │
                └─> display.display_error()
                       │
                       ├─> Rich formatting (if available)
                       └─> Plain formatting (fallback)
```

**Key Components:**

1. **ERROR_HELP Dictionary** (`utils.py`)
   - Maps error types to helpful suggestions
   - Provides actionable guidance

2. **ErrorHandler Class** (planned - `errors.py`)
   - Centralizes error classification
   - Manages error context

3. **display_error()** (`display.py`)
   - Single point for error display
   - Consistent formatting

**Design Principles:**
- **Comprehensive Help:** Detailed suggestions for common errors
- **Centralized Routing:** All errors through display layer
- **Consistent Formatting:** Same UX across all errors
- **Actionable Guidance:** Tell users how to fix the problem

---

## Configuration Management

### Configuration Hierarchy

**Precedence (highest to lowest):**

1. **CLI Arguments** - Direct user input
2. **Config File** (`~/.vscanrc`) - Persistent preferences
3. **Defaults** (`constants.py`) - Built-in values

**Example:**
```python
# User runs:
vscan scan --delay 3.0

# Config file has:
[scan]
delay = 2.0

# Default is:
DEFAULT_DELAY = 1.5

# Result: Uses 3.0 (CLI overrides all)
```

### Configuration File Structure

**Location:** `~/.vscanrc`
**Format:** INI
**Schema Version:** v1

```ini
# vscan configuration file (schema v1)

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

### Configuration Schema Versioning

**Current Version:** v1

**Future Migration:**
```python
def load_config(self):
    """Load config with schema migration."""
    config = configparser.ConfigParser()
    config.read(self.config_path)

    schema_version = config.get('_meta', 'schema_version', fallback='1')

    if schema_version != CURRENT_SCHEMA_VERSION:
        self._migrate_config(config, schema_version)

    return config
```

**Versioning Rules:**
- Major version changes require migration
- Backward compatibility maintained for 1 version
- Migration logs changes to user

---

## Observability

### What We Track

**1. Cache Metrics**
- Hit rate (% of results from cache)
- Total entries
- Database size
- Age distribution

**2. Retry Statistics** (verbose mode only)
- Total retry attempts
- Successful retries
- Failed after retry
- Rate limit hits
- Server error retries
- Timeout retries

**3. Scan Statistics**
- Total extensions scanned
- Successful scans
- Failed scans
- Vulnerabilities found
- Scan duration

### Display Strategy

**Terminal Output:**
- **Default:** Summary + Cache stats
- **Verbose:** Summary + Cache stats + Retry stats
- **Quiet:** Single line summary only

**JSON Output:**
- **Always:** All statistics included for tooling

**Example:**
```bash
# Default - Clean output
$ vscan scan
Scanned 66 extensions - 5 vulnerabilities found
Cache hit rate: 71.4%

# Verbose - Detailed diagnostics
$ vscan scan --verbose
Scanned 66 extensions - 5 vulnerabilities found
Cache hit rate: 71.4%

Retry Statistics:
  Total retries: 5
  Successful: 4
  Rate limit hits: 2
```

### Performance Characteristics

**See:** [PERFORMANCE.md](PERFORMANCE.md) for detailed benchmarks, optimization strategies, and resource usage metrics including:
- Cache performance (28x speedup for repeated scans)
- Parallel processing performance (4.88x speedup with 3 workers)
- Database optimization metrics
- Memory and disk usage patterns
- Troubleshooting guides

---

## What We DON'T Do

### Avoiding Over-Engineering

The architecture intentionally **avoids** these patterns to maintain simplicity:

❌ **Dependency Injection Frameworks**
- Not needed for 14 modules
- Adds complexity without benefit
- Manual dependency passing is clear

❌ **Abstract Base Classes Everywhere**
- Use ABC only when truly needed for polymorphism
- Prefer duck typing for simple interfaces
- Don't create interfaces "just in case"

❌ **Repository Pattern**
- `CacheManager` directly uses SQLite
- No abstraction layer between cache and database
- Simple is fast and clear

❌ **ORM (Object-Relational Mapping)**
- Direct SQL is performant and clear
- No impedance mismatch
- Easy to optimize queries

❌ **Plugin Architecture**
- No plugin system needed
- Output formatters are simple functions
- Extensibility through code, not plugins

❌ **Event-Driven Architecture**
- Sequential scan workflow is clear
- No need for event bus
- Callbacks used sparingly (progress updates)

❌ **Microservices**
- Single process is appropriate
- No network overhead
- Simple deployment

❌ **Sub-Packages**
- Flat structure works well for 14 modules
- Consider sub-packages only after 20+ modules
- Current organization is clear

### When to Reconsider

**Move to sub-packages when:**
- Module count exceeds 20
- Natural clusters form (5+ related modules)
- Plugins/extensions become necessary

**Add abstractions when:**
- Multiple implementations needed (not "might need")
- Testing requires mocking (use simple mocking, not DI)
- Actual polymorphism required (not "nice to have")

**General Rule:**
- Wait for pain before adding complexity
- Refactor when patterns emerge, not before
- Simple today > flexible tomorrow

---

## Architecture Evolution

### Version History

**v3.1.0 (Current)**
- Formalized Simple Layered Architecture
- Made Rich/Typer required dependencies
- Added configuration file support
- Improved error handling consistency

**v3.0.0**
- Introduced Rich terminal formatting
- Added Typer CLI framework
- Organized subcommands

**v2.2.0**
- Added HTML report generation
- Implemented retry mechanism

**v2.1.0**
- Initial architecture with 6 modules
- SQLite caching
- Basic CLI

### Future Considerations

**When to Refactor:**
- Module count exceeds 20 → Consider sub-packages
- Multiple output formats → Consider strategy pattern
- Complex workflows → Consider pipeline pattern

**What to Keep:**
- Layered architecture
- Dependency rules
- KISS principle
- Fail-fast philosophy

---

## Architecture Testing

Architecture compliance is validated through automated tests that enforce layer separation and dependency rules.

**Test Coverage:**
- Layer violation detection (zero violations required)
- Import dependency validation
- Circular dependency detection
- Module isolation verification

**See:** [TESTING.md](TESTING.md#architecture-tests) for complete test organization, examples, execution instructions, and CI/CD integration.

**Quick Verification:**
```bash
python3 tests/test_architecture.py  # Must show 0 violations
```


---

## Parallel Scanning Architecture (v3.5+)

### Overview

Since v3.5.0, parallel processing is the default mode with 3 workers (configurable 1-5). The parallel scanning architecture is designed around **worker isolation** and **main-thread coordination** to ensure thread safety while maintaining high performance.

### Threading Model

**Worker Isolation Pattern:**
- Each worker thread has its own isolated `VscanAPIClient` instance
- No shared mutable state between workers
- Thread-safe cache reads (SQLite supports concurrent reads)
- Cache writes serialized in main thread (avoids SQLite locking issues)
- Thread-safe stats collection via `ThreadSafeStats` class (v3.5.1+)

**Main Thread Responsibilities:**

1. **Cache writes** - Batch operations in single transaction
2. **Stats aggregation** - Collects stats from all workers via thread-safe class
3. **Progress display** - Updates Rich progress bars
4. **Result collection** - Gathers scan results from workers

**Worker Thread Responsibilities:**

1. **Cache reads** - Check cache for existing results (read-only, thread-safe)
2. **API scanning** - Scan extension via isolated API client
3. **Return results** - Pass result + metadata to main thread for caching

### Cache Write Strategy

**Why Main Thread Only:**

1. **SQLite Limitation:** Connection objects cannot safely cross thread boundaries
2. **Performance:** Single batch transaction more efficient than multiple separate transactions
3. **Error Recovery:** Easier to handle partial failures in one centralized location
4. **Simplicity:** No need for connection pooling, locks, or complex synchronization

**Implementation Pattern:**

```python
# Workers: Read + compute, return data
def _scan_single_extension_worker(ext, cache_manager, args):
    """Worker function (isolated, thread-safe)."""
    # Check cache (read-only, thread-safe)
    cached = cache_manager.get_cached_result(ext_id, version)
    if cached:
        return cached, True, False  # (result, from_cache, should_cache)

    # Scan (isolated API client instance per worker)
    api_client = VscanAPIClient(...)
    result = api_client.scan_extension_with_retry(publisher, name)

    # Return for main thread to cache
    return result, False, True  # (result, from_cache, should_cache)

# Main thread: Collect and batch write
results_to_cache = []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(_scan_single_extension_worker, ext, ...): ext
               for ext in extensions}

    for future in as_completed(futures):
        result, from_cache, should_cache = future.result()
        scan_results.append(result)

        if should_cache:
            results_to_cache.append((ext_id, version, result))

        # Update thread-safe stats
        stats.increment('successful_scans')

# Single batch write in main thread (transactional with try/finally)
try:
    cache_manager.begin_batch()
    for ext_id, version, result in results_to_cache:
        cache_manager.save_result_batch(ext_id, version, result)
finally:
    # ALWAYS commit, even on Ctrl+C or exception (v3.5.1+)
    cache_manager.commit_batch()
```

### Thread Safety Guarantees

**SQLite Operations:**
- ✅ **Cache reads** (from workers): Thread-safe (read-only operations)
- ✅ **Cache writes** (from main thread): Thread-safe (serialized in main thread)
- ✅ **No connection sharing** across threads (each worker isolation)

**API Client Operations:**
- ✅ **Worker isolation**: Each worker has its own `VscanAPIClient` instance
- ✅ **No shared state**: Workers operate completely independently
- ✅ **HTTP request delays**: Per-worker delay configuration

**Stats Collection (v3.5.1+):**
- ✅ **Thread-safe**: Using `Lock`-protected `ThreadSafeStats` class
- ✅ **No race conditions**: All updates protected by threading.Lock
- ✅ **Atomic operations**: increment(), append_failed(), set(), get(), to_dict()

**Transactional Cache Writes (v3.5.1+):**
- ✅ **Interrupt-safe**: try/finally ensures commit even on Ctrl+C
- ✅ **Partial saves**: Partial results committed if interrupted mid-batch
- ✅ **Error recovery**: Individual save failures don't prevent other saves

### Performance Characteristics

**Validated via PoC (30 extensions, real vscan.dev API):**

| Workers | Speedup | Success Rate | Recommendation |
|---------|---------|--------------|----------------|
| 1       | 1.00x   | 90.0%        | Sequential     |
| 3       | 4.88x   | 100.0%       | ✅ Default     |
| 5       | 4.27x   | 96.7%        | Advanced users |
| 7       | 4.07x   | 66.7%        | Not recommended |

**Real-World Impact:**
- **66 extensions**: 6 minutes → 1.2 minutes (3 workers, 5x faster)
- **Near-linear scaling** up to 3 workers
- **Diminishing returns** above 5 workers
- **No rate limiting** from vscan.dev API (tested up to 7 workers)

### Worker Count Limits

**Range:** 1-5 workers (configurable)

**Why this range:**
- **Minimum (1)**: Sequential mode for debugging or low-resource systems
- **Default (3)**: Optimal performance/reliability balance (4.88x speedup, 100% success)
- **Maximum (5)**: Prevents API overload and maintains high success rates

**Validation Logic:**
```python
max_workers = min(max(args.workers, 1), 5)  # Clamp to 1-5 range
```

### Evolution: v3.4 → v3.5 Breaking Changes

**v3.4.0 (Optional Parallel):**
- `--parallel` flag to enable (opt-in)
- Sequential mode by default
- Workers range: 2-5
- Two separate code paths (`_scan_extensions()` and `_scan_extensions_parallel()`)

**v3.5.0 (Parallel by Default):**
- **Breaking Change:** Removed `--parallel` flag (no longer needed)
- **Breaking Change:** Workers range changed to 1-5 (use `--workers 1` for sequential)
- **Breaking Change:** Removed `parallel` config setting
- **Benefit:** Simplified codebase (~100 lines eliminated, single unified code path)
- **Benefit:** 4.88x speedup by default (no flags needed)

**Migration:**
```bash
# v3.4
vscan scan --parallel --workers 3

# v3.5
vscan scan --workers 3  # or just 'vscan scan' (3 is default)
vscan scan --workers 1  # for sequential mode
```

### Design Decisions

**Why ThreadPoolExecutor instead of multiprocessing:**
- ✅ Simpler to implement and debug
- ✅ Lower overhead (no process spawning)
- ✅ Shared memory access (SQLite cache reads)
- ✅ Network I/O bound (not CPU bound) - GIL not a bottleneck
- ✅ Easier error handling and resource cleanup

**Why 3 workers as default:**
- ✅ Optimal speedup (4.88x) with 100% success rate
- ✅ Conservative resource usage
- ✅ Validated with real API (no rate limiting issues)
- ✅ Works well across different system sizes

**Why main-thread cache writes:**
- ✅ Avoids SQLite threading complexity
- ✅ Simpler error handling
- ✅ Batch transactions more efficient
- ✅ No need for connection pooling

### Anti-Patterns to Avoid

**❌ DON'T:** Share mutable state between workers
```python
# Bad: Shared dict updated from multiple threads
shared_stats = {'count': 0}
def worker():
    shared_stats['count'] += 1  # RACE CONDITION!
```

**✅ DO:** Use ThreadSafeStats or return results to main thread
```python
# Good: Thread-safe stats class with Lock protection
stats = ThreadSafeStats()
def worker():
    stats.increment('count')  # THREAD-SAFE
```

**❌ DON'T:** Write to database from worker threads
```python
# Bad: SQLite connection issues
def worker():
    cache_manager.save_result(...)  # NOT THREAD-SAFE
```

**✅ DO:** Return results for main thread to cache
```python
# Good: Worker returns data, main thread writes
def worker():
    return result, from_cache, should_cache
# Main thread collects and batches writes
```

**❌ DON'T:** Ignore KeyboardInterrupt in cache operations
```python
# Bad: Ctrl+C loses partial results
cache_manager.begin_batch()
for item in items:
    cache_manager.save_result_batch(...)  # May lose partial results on Ctrl+C
cache_manager.commit_batch()
```

**✅ DO:** Use try/finally to ensure commit
```python
# Good: Partial results saved even on interrupt
try:
    cache_manager.begin_batch()
    for item in items:
        cache_manager.save_result_batch(...)
finally:
    cache_manager.commit_batch()  # ALWAYS executes
```

### Testing Strategy

**Thread Safety Tests:**
- Concurrent stats updates (10 threads × 100 increments = 1000 expected)
- Concurrent list appends (verify no lost updates)
- Mixed operations (increments + appends + reads)
- Real-world parallel scan simulation

**Integration Tests:**
- Parallel vs sequential result consistency
- Worker count validation (1-5 range)
- Cache read/write concurrency
- Error handling in parallel mode

**Performance Benchmarks:**
- Worker count scaling (1, 3, 5 workers)
- Cache hit rate impact
- Real API integration tests

**Interrupt Handling Tests:**
- KeyboardInterrupt during cache writes
- Individual save failures
- Commit failures
- Begin_batch failures

**See:** `tests/test_parallel_scanning.py` and `tests/test_transactional_cache.py` for complete test suite.

---

## References

### System Design

- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling strategy and patterns
- **[TESTING.md](TESTING.md)** - Test architecture and verification
- **[SECURITY.md](SECURITY.md)** - Security architecture and validation patterns
- **[PERFORMANCE.md](PERFORMANCE.md)** - Performance benchmarks and optimization

### Project Context

- **[../CLAUDE.md](../../CLAUDE.md)** - Development guidelines and constraints
- **[project/PRD.md](../project/PRD.md)** - Product requirements and feature scope
- **[archive/plans/v3.5.1-roadmap.md](../archive/plans/v3.5.1-roadmap.md)** - Completed v3.5.1 roadmap

---

**Document Version:** 1.1
**Status:** Current
**Last Updated:** 2025-10-30 (Agentic coding optimization - dynamic metrics)
**Next Review:** When module count exceeds 15 or major refactoring planned
