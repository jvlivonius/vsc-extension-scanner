# Architecture Documentation

**Version:** 3.1.0
**Last Updated:** 2025-10-24
**Status:** Current Architecture

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
10. [What We DON'T Do (Avoiding Over-Engineering)](#what-we-dont-do)

---

## Architecture Overview

VS Code Extension Security Scanner uses a **Simple Layered Architecture** designed for maintainability and clarity without over-engineering.

### Size & Complexity

- **~9,800 lines** of Python code
- **14 modules** organized in flat structure
- **3 architectural layers** (Presentation, Application, Infrastructure)
- **No sub-packages** (flat structure sufficient for this size)

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

**Lines of Code:** ~900
**Dependencies:** scanner, display, config_manager, utils

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

**Lines of Code:** ~500
**Dependencies:** utils, constants

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

**Lines of Code:** ~800
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

**Lines of Code:** ~600
**Dependencies:** utils, constants

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

**Lines of Code:** ~900
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

**Lines of Code:** ~400
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

### Forbidden Dependencies

❌ **Infrastructure → Application**
```python
# BAD - vscan_api.py should not import scanner
from vscode_scanner.scanner import perform_scan
```

❌ **Infrastructure → Presentation**
```python
# BAD - cache_manager.py should not import display
from vscode_scanner.display import display_error
```

❌ **Circular Dependencies**
```python
# BAD - A imports B, B imports A
# cli.py imports scanner.py
# scanner.py imports cli.py  # ❌ Circular!
```

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

### Performance Metrics

**Cache Performance:**
- First scan: ~1.5s per extension
- Cached scan: ~instant (50x faster)
- Typical hit rate: 70-90%

**Database Performance:**
- Batch operations: 87.6% faster than individual inserts
- VACUUM: 73.9% space reclaimed (when beneficial)

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

### Test Categories

**1. Layering Tests** (`tests/test_architecture.py`):
```python
def test_infrastructure_isolation():
    """Infrastructure layer doesn't import from application/presentation."""
    # Verify vscan_api, cache_manager, extension_discovery
    # Don't import scanner, cli, display

def test_no_circular_dependencies():
    """No circular imports exist."""
    # Use import detection
```

**2. Integration Tests** (`tests/test_integration.py`):
```python
def test_full_scan_workflow():
    """Verify complete scan workflow through all layers."""
    # CLI → Scanner → API → Cache → Output
```

**3. Performance Tests** (`tests/test_performance.py`):
```python
def test_cache_performance():
    """Verify cache provides expected speedup."""

def test_batch_operations():
    """Verify batch operations are faster than individual."""
```

### Continuous Validation

**On Every Commit:**
- Run architecture tests
- Verify no new circular dependencies
- Check import structure

**On Pull Requests:**
- Review new dependencies
- Verify layer boundaries maintained
- Check for over-engineering patterns

---

## Module Dependencies & Import Rules

### Dependency Graph

**Allowed Dependencies** (following layered architecture):

```
Presentation Layer:
  cli.py                   → scanner, display, config_manager, utils, constants
  display.py               → utils, constants
  output_formatter.py      → utils, constants
  html_report_generator.py → utils

Application Layer:
  scanner.py               → vscan_api, cache_manager, extension_discovery,
                             display, utils, constants
  vscan.py                 → cli, utils, constants
  config_manager.py        → utils, constants

Infrastructure Layer:
  vscan_api.py             → utils, constants
  cache_manager.py         → utils, constants
  extension_discovery.py   → utils, constants

Shared Utilities:
  utils.py                 → (standard library only)
  constants.py             → (standard library only)
  types.py                 → (standard library only)
  _version.py              → (standard library only)
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

### Testing Module Dependencies

**Automated Validation:**

Create `tests/test_architecture.py` to enforce dependency rules:

```python
def test_infrastructure_layer_isolation():
    """Infrastructure must NOT import from Application or Presentation."""
    infrastructure = ['vscan_api', 'cache_manager', 'extension_discovery']
    forbidden = ['scanner', 'cli', 'display', 'output_formatter']

    for module in infrastructure:
        imports = get_imports_from_file(f'vscode_scanner/{module}.py')
        violations = imports & set(forbidden)
        assert not violations, f"{module} illegally imports: {violations}"

def test_no_circular_dependencies():
    """Ensure no circular import dependencies."""
    # Build dependency graph and detect cycles using DFS
    assert no_cycles_detected(dependency_graph)
```

**Manual Review Checklist:**

When adding new modules or modifying imports:

1. ✅ Does this follow the layered architecture?
2. ✅ Are we importing from the same or lower layer only?
3. ✅ Are shared utilities (utils, constants) used instead of cross-layer imports?
4. ✅ Will this create a circular dependency?

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

---

## References

- **[project/ROADMAP.md](../project/ROADMAP.md)** - Version 3.2 improvement recommendations
- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling strategy
- **[TESTING.md](TESTING.md)** - Testing guidelines
- **[../CLAUDE.md](../CLAUDE.md)** - Development guidance
- **[project/PRD.md](../project/PRD.md)** - Product requirements

---

**Document Version:** 1.0
**Status:** Current
**Next Review:** When module count exceeds 15 or major refactoring planned
