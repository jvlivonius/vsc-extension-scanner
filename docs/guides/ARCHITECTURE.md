# Architecture Guide

**Purpose:** System architecture, design principles, and module responsibilities
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** Developers, Architects

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

**Current Metrics:**
- **Line Count:** Run `cloc vscode_scanner/ --by-file` for current LOC
- **Module Count:** Run `ls vscode_scanner/*.py | wc -l` for module count
- **Architecture:** 3 layers (Presentation, Application, Infrastructure)
- **Organization:** Flat structure (no sub-packages, sufficient for current size)
- **Version:** See `vscode_scanner/_version.py` for current version

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
```toml
# pyproject.toml configuration
[project.scripts]
vscan = "vscode_scanner.vscan:cli_main"
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

**Design:** Self-contained HTML with embedded CSS/JavaScript (no external dependencies). See **[HTML_REPORTS.md](HTML_REPORTS.md)** for complete architecture, design decisions, and performance optimizations

### parallel_executor.py (Application)

```python
# Responsibilities:
# 1. Generic parallel execution pattern
# 2. ThreadPoolExecutor abstraction
# 3. Progress callback coordination
# 4. Worker task preparation and result processing

# Key Classes:
- ParallelExecutor - Base class for parallel operations (Generic[T, R])

# Design Pattern:
- Template Method pattern for parallel execution
- Subclasses implement: prepare_task(), process_result(), handle_error()
```

**Lines of Code:** ~210
**Dependencies:** concurrent.futures (standard library), typing
**Added:** v3.7.0 (Phase 2.1 - ScanOrchestrator extraction)

### scan_orchestrator.py (Application)

```python
# Responsibilities:
# 1. Orchestrate vulnerability scanning with parallel execution
# 2. Integrate cache persistence (instant save)
# 3. Collect thread-safe statistics
# 4. Emit progress notifications (started, completed, cached, failed)

# Key Classes:
- ScanOrchestrator - Extends ParallelExecutor for scanning

# Architecture:
- Separates business logic from ThreadPoolExecutor mechanics
- Delegates to _scan_single_extension_worker for actual scanning
- Handles cache failures gracefully (logs warnings, continues scan)
```

**Lines of Code:** ~230
**Dependencies:** parallel_executor, cache_manager, scan_helpers
**Added:** v3.7.0 (Phase 2.1 - Improved testability through orchestration pattern)

### scan_helpers.py (Application)

```python
# Responsibilities:
# 1. Thread-safe statistics collection (ThreadSafeStats class)
# 2. Worker function for scanning individual extensions
# 3. Error categorization and message simplification helpers

# Key Classes:
- ThreadSafeStats - Thread-safe statistics with Lock-based synchronization

# Key Functions:
- _scan_single_extension_worker() - Thread-safe worker for single extension scan
- _categorize_error() - Categorize error messages into types
- _simplify_error_message() - Convert error types to user-friendly messages

# Architecture:
- Shared code between scanner.py and scan_orchestrator.py
- Breaks circular dependency through isolated helper module
- No dependencies on other application modules
```

**Lines of Code:** ~225
**Dependencies:** cache_manager, vscan_api (imported locally in worker function)
**Added:** v3.7.0 (Phase 2.1 - Extracted to resolve circular dependency)

### scanner.py (Application)

```python
# Responsibilities:
# 1. Main scan entry point and coordination
# 2. Apply filtering (publisher, risk level, IDs)
# 3. Delegate to ScanOrchestrator for parallel execution
# 4. Aggregate results and build summary

# Key Functions:
- perform_scan() - Main scan orchestration
- _filter_extensions() - Apply user filters
- _scan_extensions() - Delegates to ScanOrchestrator (refactored v3.7)
- _scan_single_extension_worker() - Worker function for scanning
- _build_summary() - Aggregate statistics

# Refactored v3.7:
- Removed ThreadPoolExecutor logic (→ parallel_executor.py)
- Reduced _scan_extensions from 149 lines to 72 lines (-52%)
- Improved testability through orchestration pattern
```

**Lines of Code:** Run `wc -l vscode_scanner/scanner.py` for current count (baseline: ~650, reduced from ~800)
**Dependencies:** scan_orchestrator, vscan_api, cache_manager, extension_discovery, display

### parallel_executor.py (Application) [Phase 2.1]

```python
# Responsibilities:
# 1. Generic parallel execution pattern using ThreadPoolExecutor
# 2. Template Method pattern for customizable parallel workflows
# 3. Progress notification through callbacks
# 4. Error handling for worker failures

# Key Methods:
- prepare_task() - Abstract method for task preparation
- process_result() - Abstract method for result processing
- handle_error() - Abstract method for error handling
- execute() - Template method for parallel execution
```

**Lines of Code:** Run `wc -l vscode_scanner/parallel_executor.py` for current count (baseline: ~210)
**Dependencies:** None (pure generic pattern)
**Test Coverage:** 96% (37 tests)

### scan_orchestrator.py (Application) [Phase 2.1]

```python
# Responsibilities:
# 1. Specialized orchestrator for vulnerability scanning
# 2. Extends ParallelExecutor with scan-specific logic
# 3. Instant cache persistence (zero data loss)
# 4. Thread-safe statistics aggregation

# Key Methods:
- prepare_task() - Prepares extension for worker
- process_result() - Handles scan results + instant cache save
- handle_error() - Categorizes and logs scan errors
- update_stats_for_result() - Thread-safe stats updates
```

**Lines of Code:** Run `wc -l vscode_scanner/scan_orchestrator.py` for current count (baseline: ~230)
**Dependencies:** scan_helpers, cache_manager, vscan_api, utils
**Test Coverage:** 100% (37 tests)

### scan_helpers.py (Application) [Phase 2.1]

```python
# Responsibilities:
# 1. Shared code between scanner and scan_orchestrator
# 2. ThreadSafeStats class for parallel statistics
# 3. Worker function for single extension scanning
# 4. Error categorization and simplification

# Key Components:
- ThreadSafeStats - Lock-based thread-safe statistics
- _scan_single_extension_worker() - Worker for parallel scan
- _categorize_error() - Error type classification
- _simplify_error_message() - User-friendly error messages
```

**Lines of Code:** Run `wc -l vscode_scanner/scan_helpers.py` for current count (baseline: ~225)
**Dependencies:** vscan_api, cache_manager, utils
**Test Coverage:** 97.33%

**Why scan_helpers.py exists:** Created to break circular dependency between scanner.py and scan_orchestrator.py. Both modules needed ThreadSafeStats and worker functions, so extracting to a separate module maintained clean layering.

### output_writer.py (Application) [Phase 2.2]

```python
# Responsibilities:
# 1. Output format detection (CSV, HTML, JSON)
# 2. Content generation delegation to formatters
# 3. File writing with proper encoding
# 4. Output orchestration and progress logging

# Key Methods:
- detect_format() - Pure function: file extension → format
- generate_content() - Pure function: results + format → content
- write_to_file() - I/O operation: content → file
- write_output() - Orchestrates full workflow
```

**Lines of Code:** Run `wc -l vscode_scanner/output_writer.py` for current count (baseline: ~220)
**Dependencies:** output_formatter, html_report_generator, display, utils
**Test Coverage:** 100% (31 tests)

### summary_formatter.py (Application) [Phase 2.2]

```python
# Responsibilities:
# 1. Quiet mode summary text generation
# 2. Retry statistics extraction
# 3. Conditional display logic (cache/retry stats)
# 4. Pure functions for testable formatting

# Key Methods:
- format_quiet_summary() - Pure function: counts → summary text
- extract_retry_stats() - Pure function: stats dict → retry stats
- should_show_cache_stats() - Pure function: results + verbose → bool
- should_show_retry_stats() - Pure function: retry_stats + verbose → bool
```

**Lines of Code:** Run `wc -l vscode_scanner/summary_formatter.py` for current count (baseline: ~160)
**Dependencies:** None (pure functions)
**Test Coverage:** 100% (29 tests)

### filter_help_generator.py (Application) [Phase 2.2]

```python
# Responsibilities:
# 1. Active filter extraction from args
# 2. Publisher filter detection
# 3. Suggestion message generation
# 4. Pure functions for testable help text

# Key Methods:
- extract_active_filters() - Pure function: args → filter list
- has_publisher_filter() - Pure function: args → bool
- generate_suggestion_messages() - Pure function: counts + filters → messages
```

**Lines of Code:** Run `wc -l vscode_scanner/filter_help_generator.py` for current count (baseline: ~110)
**Dependencies:** None (pure functions)
**Test Coverage:** 100% (18 tests)

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
- Not needed for 16 modules
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
- Flat structure works well for 16 modules
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

**Note:** See [CHANGELOG.md](../../CHANGELOG.md) and release notes in [docs/archive/summaries/](../archive/summaries/) for complete version history.

**Key Milestones:**
- **v3.7+**: Modular extraction (parallel_executor, scan_orchestrator, scan_helpers, output_writer, summary_formatter, filter_help_generator)
- **v3.1**: Formalized 3-layer architecture, configuration support
- **v3.0**: Rich/Typer framework adoption
- **v2.2**
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
2. **Simplicity:** No need for connection pooling, locks, or complex synchronization
3. **Sequential Processing:** `as_completed()` delivers results one-at-a-time to main thread

**Implementation Pattern (v3.5.4+: Instant Persistence):**

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

# Main thread: Instant persistence (v3.5.4+)
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(_scan_single_extension_worker, ext, ...): ext
               for ext in extensions}

    for future in as_completed(futures):
        result, from_cache, should_cache = future.result()
        scan_results.append(result)

        # Instant cache persistence - zero data loss on interrupt
        if should_cache and cache_manager:
            try:
                cache_manager.save_result(ext_id, version, result)
            except Exception as e:
                # Cache errors should not fail the scan
                log(f"Cache save failed for {ext_id}: {e}", "WARNING")

        # Update thread-safe stats
        stats.increment('successful_scans')
```

**Architecture Evolution:**

- **v3.5.0-v3.5.3:** Batch write at end - 0.03% faster but **100% data loss** on interrupt
- **v3.5.4+:** Instant persistence - 0.3% overhead but **zero data loss** on interrupt

**Trade-off Analysis:**

| Approach | Speed | Data Loss on Ctrl+C | Code Complexity |
|----------|-------|---------------------|-----------------|
| Batch at end | 100% | 100% (all results) | High (~25 lines) |
| Instant save | 99.7% | 0% (zero loss) | Low (2 lines) |

**Why Instant Persistence:**

1. **Reliability:** Zero data loss on interruption (Ctrl+C)
2. **Simplicity:** Eliminates ~25 lines of batch management code
3. **User Experience:** Resume scans only process missing extensions
4. **Negligible Cost:** 10ms per save × 10 extensions = 100ms vs 210s scan = 0.3%

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

**Instant Cache Persistence (v3.5.4+):**
- ✅ **Zero data loss**: Each result saved immediately as it completes
- ✅ **Interrupt recovery**: Ctrl+C preserves all completed extensions
- ✅ **Resume capability**: Re-running scan only processes missing extensions
- ✅ **Error isolation**: Cache failures don't abort entire scan (logged as warnings)

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
