# Phase 3 Handoff: Marker-Based Auto-Discovery with Serena MCP

**Session Date**: 2025-10-30
**Prepared By**: Claude Code
**Next Session**: Phase 3 Implementation with Serena MCP

---

## 🎯 Current Status

**✅ Phase 1-2 Complete** (Committed: 98507cb)
- Coverage.py integration with multi-format reports (term, html, xml, json)
- Pytest integration with custom plugin for result collection
- Testing documentation restructured (11 specialized guides in docs/guides/testing/)
- TEST_REGISTRY updated (36/36 files, 100% coverage)
- run_tests.py v1.3 with hybrid execution model

**Current Metrics**:
- Total Tests: 604 tests
- Passing: 601 tests (99.5%)
- Failing: 3 tests (property validation edge cases)
- Overall Coverage: 52.37%
- Security Coverage: ~95%

**Git Branch**: `claude/create-vscan-prd-011CUNe8k7s3rGxcEUmMhyDF`

---

## 📋 Phase 3 Plan: Marker-Based Auto-Discovery

**Strategy**: Add explicit pytest markers to all test files, then implement auto-discovery functions

### Phase 3A: Add Pytest Markers (2-3 hours)

**16 Unit Test Files** (add `@pytest.mark.unit`):
```python
tests/test_utils.py
tests/test_config_manager.py
tests/test_output_formatter.py
tests/test_cli.py
tests/test_cache_commands.py
tests/test_config_commands.py
tests/test_report_commands.py
tests/test_input_validators.py
tests/test_error_handling.py
tests/test_extension_discovery.py
tests/test_display.py
tests/test_scanner.py
tests/test_html_report_generator.py
tests/test_vscan_api.py
tests/test_types.py
tests/test_cache_manager.py
```

**8 Security Test Files** (add `@pytest.mark.security`):
```python
tests/test_security.py
tests/test_security_regression.py
tests/test_path_validation.py
tests/test_string_sanitization.py
tests/test_cache_integrity.py
tests/test_sqlite_security.py
tests/test_property_validation.py
tests/test_property_cache.py
```

**12 Other Test Files** (various markers):
```python
tests/test_architecture.py → @pytest.mark.architecture
tests/test_parallel_scan.py → @pytest.mark.parallel
tests/test_parallel_safety.py → @pytest.mark.parallel
tests/test_db_integrity.py → @pytest.mark.integration
tests/test_integration.py → @pytest.mark.integration
tests/test_workflow_retry.py → @pytest.mark.integration
tests/test_performance.py → @pytest.mark.integration
tests/test_api_mock_validation.py → @pytest.mark.mock-validation
tests/test_api_real.py → @pytest.mark.real-api
```

**Marker Placement Pattern**:
```python
import pytest

@pytest.mark.unit
class TestUtils(unittest.TestCase):
    """Unit tests for utility functions."""

    def test_validate_path_basic(self):
        # ... test code ...
```

**Verification**:
```bash
pytest --collect-only -m unit      # Should show 16 files worth of tests
pytest --collect-only -m security  # Should show 8 files worth of tests
```

### Phase 3B: Implement Auto-Discovery Functions (2-3 hours)

**Function 1: discover_test_files()**
```python
def discover_test_files() -> Dict[TestGroup, List[TestFile]]:
    """
    Auto-discover test files using pytest collection and marker reading.

    Uses pytest's collection mechanism to find all test files, then reads
    their markers to determine which test group they belong to.

    Returns:
        Dictionary mapping TestGroup to list of TestFile objects
    """
```

**Serena MCP Usage**:
- Use `mcp__serena__find_file` to locate all test_*.py files
- Use `mcp__serena__search_for_pattern` to find pytest.mark decorators in each file
- Use `mcp__serena__get_symbols_overview` to understand test file structure

**Function 2: validate_registry()**
```python
def validate_registry() -> Tuple[bool, List[str]]:
    """
    Compare TEST_REGISTRY against auto-discovered tests.

    Returns:
        (is_valid, list_of_issues)
    """
```

**Function 3: sync_registry()**
```python
def sync_registry(dry_run: bool = True) -> str:
    """
    Generate Python code for TEST_REGISTRY from discovered tests.

    Args:
        dry_run: If True, return code as string; if False, update file

    Returns:
        Generated Python code for TEST_REGISTRY
    """
```

**Serena MCP Usage**:
- Use `mcp__serena__find_symbol` to locate TEST_REGISTRY definition
- Use `mcp__serena__replace_symbol_body` to update TEST_REGISTRY code

### Phase 3C: CLI Integration (1 hour)

**New CLI Arguments**:
```python
parser.add_argument(
    "--auto-discover",
    action="store_true",
    help="Auto-discover test files using pytest markers (bypass TEST_REGISTRY)"
)

parser.add_argument(
    "--validate-registry",
    action="store_true",
    help="Validate TEST_REGISTRY against discovered tests, exit 0 if valid"
)

parser.add_argument(
    "--sync-registry",
    action="store_true",
    help="Generate updated TEST_REGISTRY code from discovered tests"
)
```

**Test Commands**:
```bash
# Auto-discover mode
python3 scripts/run_tests.py --auto-discover

# Validate registry
python3 scripts/run_tests.py --validate-registry

# Generate registry code
python3 scripts/run_tests.py --sync-registry
```

---

## 🐛 Known Issues to Address

### 1. Property Validation Test Failures (3 tests)

**Location**: `tests/test_property_validation.py`

**Failing Tests**:
1. `test_safe_strings_minimally_modified` - Input `'\x1f'` produces empty output
2. `test_sanitize_not_empty_unless_input_empty` - Input `' '` produces empty output
3. `test_sanitize_removes_control_chars` - Input `'\r'` not properly removed

**Root Cause**: `sanitize_string()` function in `vscode_scanner/utils.py` has edge case bugs with:
- ASCII control characters (0x00-0x1F)
- Whitespace-only inputs
- Carriage return handling

**Impact**: Low (edge cases, not affecting normal operation)

**Recommended Fix**: Update `sanitize_string()` to:
- Preserve at least one character for non-empty inputs
- Properly handle all ASCII control characters
- Add special case for whitespace-only inputs

**Priority**: Medium (fix after Phase 3 implementation)

### 2. Pylint Code Quality Issues

**Files Affected**: Multiple files in `vscode_scanner/`

**Issues**:
- Line length violations (>100 chars)
- Too many arguments/attributes in some classes
- Some code duplication

**Impact**: Low (code quality, not functionality)

**Status**: Pre-existing issues, not blockers

**Code Rating**: 9.83/10 (improved from 9.82/10)

---

## 🔧 Serena MCP Integration Strategy

### Why Serena for Phase 3?

1. **Symbol Operations**: Need to find and update TEST_REGISTRY definition
2. **Pattern Search**: Need to locate all pytest.mark decorators across 36 files
3. **Code Generation**: Need to generate TEST_REGISTRY Python code
4. **File Discovery**: Need to locate all test_*.py files efficiently

### Serena MCP Tools to Use

**File Discovery**:
```python
mcp__serena__find_file(file_mask="test_*.py", relative_path="tests")
```

**Marker Search**:
```python
mcp__serena__search_for_pattern(
    substring_pattern="@pytest\\.mark\\.(unit|security|architecture|parallel|integration|real-api|mock-validation)",
    relative_path="tests",
    restrict_search_to_code_files=True
)
```

**Symbol Location**:
```python
mcp__serena__find_symbol(
    name_path="TEST_REGISTRY",
    relative_path="scripts/run_tests.py",
    include_body=True
)
```

**Code Update**:
```python
mcp__serena__replace_symbol_body(
    name_path="TEST_REGISTRY",
    relative_path="scripts/run_tests.py",
    body=generated_registry_code
)
```

### Expected Efficiency Gains

- **Parallel Search**: Serena can search multiple files simultaneously
- **Semantic Understanding**: Better parsing of Python decorators and symbols
- **Precise Updates**: Symbol-based editing vs. regex/string replacement
- **Context Preservation**: Maintains file structure and formatting

---

## 📊 Success Criteria

### Phase 3A Success
- [ ] All 36 test files have appropriate pytest markers
- [ ] `pytest --collect-only -m unit` shows all unit tests
- [ ] `pytest --collect-only -m security` shows all security tests
- [ ] All markers verified with zero collection errors

### Phase 3B Success
- [ ] `discover_test_files()` returns all 36 test files with correct groups
- [ ] `validate_registry()` correctly identifies registry mismatches
- [ ] `sync_registry()` generates valid Python code for TEST_REGISTRY
- [ ] Generated code matches TEST_REGISTRY format and style

### Phase 3C Success
- [ ] `--auto-discover` mode runs all tests using marker discovery
- [ ] `--validate-registry` exits 0 when registry is synchronized
- [ ] `--sync-registry` outputs valid Python code
- [ ] Integration tests pass with all discovery modes

### Phase 4 Success
- [ ] All flag combinations tested (--coverage + --auto-discover, etc.)
- [ ] Documentation updated (TESTING.md, TESTING_COVERAGE.md, CLAUDE.md)
- [ ] Performance benchmarks: auto-discovery vs. registry lookup
- [ ] v3.5.3 ready for release

---

## 🚀 Next Session Action Plan

### 1. Initialize Serena MCP
```bash
# Verify Serena tools are available
mcp__serena__initial_instructions
mcp__serena__check_onboarding_performed
```

### 2. Start Phase 3A: Add Markers
- Use Serena to efficiently find all 36 test files
- Add appropriate pytest.mark decorators to each file
- Verify markers with pytest --collect-only

### 3. Implement Phase 3B: Auto-Discovery
- Implement `discover_test_files()` using Serena pattern search
- Implement `validate_registry()` with comparison logic
- Implement `sync_registry()` using Serena symbol replacement

### 4. Complete Phase 3C: CLI Integration
- Add CLI arguments (--auto-discover, --validate-registry, --sync-registry)
- Test all discovery modes
- Verify integration with existing --coverage and --pytest flags

### 5. Checkpoint and Documentation
- Commit Phase 3 changes
- Update documentation (STATUS.md, CLAUDE.md, CHANGELOG.md)
- Prepare for Phase 4 final integration

---

## 📁 File Locations Reference

**Modified Files (Phase 1-2)**:
- `scripts/run_tests.py` - v1.3 (main test runner)
- `tests/conftest.py` - Pytest markers configured
- `.semgrep.yml` - Fixed duplicate keys
- `docs/guides/testing/` - 11 specialized testing guides
- `docs/guides/TESTING.md` - Compact overview (486 lines)

**Files to Modify (Phase 3)**:
- `scripts/run_tests.py` - Add Phase 3B/3C functions and CLI args
- `tests/test_*.py` (36 files) - Add pytest markers
- `docs/project/STATUS.md` - Update progress
- `docs/project/v3.5.3-roadmap.md` - Mark Phase 3 complete
- `CHANGELOG.md` - Add Phase 3 entry

**Configuration Files**:
- `.coveragerc` - Coverage.py configuration
- `tests/conftest.py` - Pytest markers and fixtures
- `pyproject.toml` - Test dependencies

---

## 🔍 Debugging Tips

**If markers don't work**:
```bash
# Check pytest can see the markers
pytest --markers | grep "unit\|security\|architecture"

# Verify specific file has markers
grep -n "@pytest.mark" tests/test_utils.py
```

**If Serena search is slow**:
```python
# Use restrict_search_to_code_files to skip non-Python files
mcp__serena__search_for_pattern(
    substring_pattern="@pytest\\.mark\\.",
    restrict_search_to_code_files=True
)
```

**If registry sync fails**:
```python
# Use dry_run mode first to verify generated code
generated_code = sync_registry(dry_run=True)
print(generated_code)  # Inspect before applying
```

---

## 📚 Additional Context

**v3.5.3 Roadmap**: docs/project/v3.5.3-roadmap.md
**Testing Guide**: docs/guides/TESTING.md
**Coverage Strategy**: docs/guides/testing/TESTING_COVERAGE.md
**Serena Documentation**: .claude/MCP_Serena.md

**User Decision**: "Go with Option 1 and use the Serena MCP server in the upcoming phases!"

---

**Ready for Phase 3 Implementation** ✅
