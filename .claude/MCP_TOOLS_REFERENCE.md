# MCP Tools Reference (Python CLI Development)

This guide covers the 3 MCP servers relevant to **vscode_scanner** Python CLI development.

## Tool Selection Quick Reference

| Need | Use | Example |
|------|-----|---------|
| Symbol refactoring | Serena | Rename function across all files |
| Session persistence | Serena | /sc:load, /sc:save for multi-session work |
| Complex debugging | Sequential | Root cause analysis with hypothesis testing |
| Architecture analysis | Sequential | 3-layer compliance validation |
| Python library docs | Context7 | pytest patterns, typer CLI best practices |

---

## Serena MCP - Semantic Code Understanding

**Purpose**: Symbol operations with project memory and session persistence

### When to Use Serena
✅ **Symbol operations**: Rename, extract, move functions/classes
✅ **Project memory**: Save/load session context across interruptions
✅ **Code navigation**: Find all references, dependency tracking
✅ **Large refactoring**: Multi-file symbol-aware changes

❌ **Not for**: Simple text replacements, pattern-based bulk edits

### Key Operations (Python CLI Context)

**Symbol Operations:**
```python
# Rename symbol across entire project
find_symbol(name_path="validate_path", relative_path="utils.py")
rename_symbol(name_path="validate_path", new_name="validate_extension_path")

# Replace function body
replace_symbol_body(name_path="ScannerApp/run", relative_path="scanner.py", body="...")

# Find references
find_referencing_symbols(name_path="ThreadSafeStats", relative_path="scanner.py")
```

**Session Persistence (v3.6 refactoring):**
```python
# Session start
list_memories()  # Check existing refactoring state
read_memory("plan_v3.6")  # Resume context

# During work
write_memory("phase_2", "Extracting ProgressCallback pattern")
write_memory("checkpoint", "Completed scanner.py refactoring")

# Session end
write_memory("session_summary", "Coverage improved to 78.94%")
```

**Project Navigation:**
```python
# Get file overview
get_symbols_overview(relative_path="scanner.py")

# Find test patterns
search_for_pattern(substring_pattern="@pytest.fixture", restrict_search_to_code_files=True)
```

### Integration with vscode_scanner
- **Symbol renames**: Update function names maintaining test references
- **Refactoring memory**: Track multi-session testability improvements
- **Architecture validation**: Find layer violations via dependency analysis

---

## Sequential MCP - Multi-Step Reasoning

**Purpose**: Complex analysis and systematic problem-solving

### When to Use Sequential
✅ **Complex debugging**: Multi-component failures (scanner + API + cache)
✅ **Architecture analysis**: 3-layer compliance, dependency issues
✅ **Performance investigation**: Threading bottlenecks, cache efficiency
✅ **Security analysis**: Path validation, sanitization, HMAC integrity

❌ **Not for**: Simple explanations, single-file changes, basic fixes

### Analysis Patterns (Python CLI Context)

**Root Cause Analysis:**
```
Problem: Test coverage stuck at 75%
→ Sequential reasoning:
1. Hypothesis: Hard-to-test components exist
2. Evidence: scanner.py has tightly-coupled progress callbacks
3. Analysis: Callback pattern prevents dependency injection
4. Solution: Extract ProgressCallback interface
5. Validation: Coverage improves to 78.94%
```

**Architecture Compliance:**
```
Question: Is new ConfigManager following 3-layer architecture?
→ Sequential analysis:
1. Layer check: Infrastructure layer ✓
2. Dependency check: No presentation imports ✓
3. Pattern check: Follows existing utils.py patterns ✓
4. Security check: Uses validate_path() ✓
5. Conclusion: Architecture-compliant
```

**Performance Optimization:**
```
Issue: Parallel scanning slower than expected
→ Sequential investigation:
1. Measure: Profile ThreadPoolExecutor execution
2. Identify: Lock contention in ThreadSafeStats
3. Analyze: Main thread database writes blocking workers
4. Solution: Batch database writes, reduce lock scope
5. Validate: Benchmark 3x improvement
```

### Integration with vscode_scanner
- **Test strategy**: Plan property-based test scenarios with hypothesis
- **Security validation**: Systematic threat model analysis
- **Refactoring plans**: Multi-phase testability improvement strategies

---

## Context7 MCP - Official Documentation

**Purpose**: Library documentation lookup for Python ecosystem

### When to Use Context7
✅ **Python libraries**: pytest, hypothesis, typer, rich patterns
✅ **API best practices**: SQLite security, threading best practices
✅ **Version-specific**: Python 3.8+ features, library updates
✅ **Official patterns**: Preferred idioms over generic solutions

❌ **Not for**: Generic Python questions answerable from training

### Library Lookups (Python CLI Context)

**Testing Frameworks:**
```
"pytest fixture best practices" → Context7
"hypothesis property testing strategies" → Context7
"pytest parametrize with multiple params" → Context7
```

**CLI Frameworks:**
```
"typer command groups and callbacks" → Context7
"rich progress bar customization" → Context7
"typer config file integration" → Context7
```

**Standard Library:**
```
"sqlite3 thread safety patterns" → Context7
"threading.Lock vs RLock for stats" → Context7
"urllib.request security best practices" → Context7
```

### Integration with vscode_scanner
- **Test patterns**: Canonical pytest and hypothesis idioms
- **CLI design**: Typer command structure best practices
- **Threading**: Python threading model official guidance

---

## Tool Coordination Patterns

### Serena → Sequential
**Pattern**: Symbol analysis → Architectural reasoning
```
1. Serena: find_referencing_symbols("validate_path")
2. Serena: Identify 15 call sites across 8 files
3. Sequential: Analyze layer compliance of call sites
4. Sequential: Detect 2 presentation→infrastructure violations
5. Result: Refactoring plan to fix architecture
```

### Sequential → Context7
**Pattern**: Problem decomposition → Official solution lookup
```
1. Sequential: Analyze test coverage gaps
2. Sequential: Identify property testing opportunity
3. Context7: Lookup hypothesis strategies for path validation
4. Context7: Provide official patterns and examples
5. Result: Implement property tests, improve coverage
```

### Serena → Serena (Memory)
**Pattern**: Multi-session refactoring with persistence
```
Session 1:
  - write_memory("plan_v3.6", "Extract ProgressCallback")
  - write_memory("phase_1", "Analysis complete")

Session 2:
  - read_memory("plan_v3.6") → Resume context
  - Continue refactoring with full history
  - write_memory("phase_2", "Implementation complete")
```

---

## Decision Matrix

### Choose Serena When...
- Need symbol-aware refactoring (rename, extract, move)
- Working across multiple sessions (load/save context)
- Navigating large codebase with LSP integration
- Preserving references during refactoring

### Choose Sequential When...
- Debugging involves 3+ interconnected components
- Need hypothesis testing and systematic validation
- Analyzing architecture or security systematically
- Performance investigation requires structured approach

### Choose Context7 When...
- Need official Python library documentation
- Want version-specific best practices
- Require canonical testing/CLI patterns
- Official docs preferred over generic knowledge

### Use Native Claude When...
- Simple explanations or single-file changes
- Basic Python syntax questions
- Quick fixes or typos
- Generic programming concepts

---

## Not Applicable to This Project

The following MCP servers are **archived** (see `.claude/archive/`) as they're not relevant to Python CLI development:

- **Magic**: UI component generation (web frontend tool)
- **Playwright**: Browser automation (E2E web testing)
- **Morphllm**: Pattern-based bulk edits (Serena handles Python symbols better)
- **Tavily**: Multi-source web research (single API source: vscan.dev)

To retrieve archived MCP documentation, see `.claude/archive/README.md`.
