# Integration Testing Guide

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Applies To:** All 3.x versions
**Target Audience:** Developers, QA Engineers

---

## Overview

Integration tests verify that multiple components work together correctly, testing real interactions between modules while mocking only external services.

**Test File:** `tests/test_integration.py` (7 tests covering major workflows)

**Characteristics:**
- **Speed:** Moderate (1-5s each)
- **Scope:** Multiple modules interacting
- **Mocking:** Real module interactions, mock external services only (API, filesystem)
- **Focus:** End-to-end workflows, data flow between components

---

## Existing Integration Tests

### Test 1: Full Scan Workflow

```python
def test_full_scan_workflow():
    """Complete scan workflow from discovery to output.

    Tests entire pipeline:
    1. Extension discovery (finds extensions)
    2. Scanning (processes each extension)
    3. Caching (saves results)
    4. Output (generates JSON/CSV)
    """
    with mock_vscan_api(), temp_cache(), temp_output_dir():
        result = perform_scan(
            extensions_dir="./tests/fixtures/sample_extensions",
            output="results.json",
            use_cache=True,
        )

        # Verify scan completed
        assert result['summary']['total_extensions_scanned'] > 0

        # Verify output file created
        assert os.path.exists("results.json")

        # Verify cache populated
        cache = CacheManager()
        stats = cache.get_cache_stats()
        assert stats['total_entries'] > 0

        # Verify output format
        with open("results.json") as f:
            data = json.load(f)
            assert data['schema_version'] == "2.0"
            assert 'extensions' in data
```

### Test 2: Cache Hit Workflow

```python
def test_cache_hit_workflow():
    """Cached results returned without API calls.

    Tests caching behavior:
    1. First scan populates cache
    2. Second scan retrieves from cache (no API calls)
    3. Results identical between scans
    """
    with mock_vscan_api() as mock_api:
        # First scan (cache miss)
        result1 = perform_scan(extensions_dir="./tests/fixtures/sample")
        api_calls_first = mock_api.call_count

        # Second scan (cache hit)
        result2 = perform_scan(extensions_dir="./tests/fixtures/sample")
        api_calls_second = mock_api.call_count

        # Second scan should not call API
        assert api_calls_second == api_calls_first

        # Results should be identical
        assert result1['summary'] == result2['summary']
```

### Test 3: Cache Miss and Save

```python
def test_cache_miss_and_save():
    """Cache miss triggers API call and saves result.

    Tests cache miss behavior:
    1. Query non-existent entry (cache miss)
    2. API call triggered
    3. Result saved to cache
    4. Subsequent query returns cached result
    """
    cache = CacheManager()
    extension_id = "test.extension"
    version = "1.0.0"

    # Cache miss
    result = cache.get_cached_result(extension_id, version)
    assert result is None

    # Perform scan (triggers API call)
    with mock_vscan_api():
        scan_result = scan_extension(extension_id)

    # Save to cache
    cache.save_result(extension_id, version, scan_result)

    # Cache hit
    cached = cache.get_cached_result(extension_id, version)
    assert cached is not None
    assert cached['extension_id'] == extension_id
```

### Test 4: Output Modes

```python
def test_output_modes():
    """Different output formats generated correctly.

    Tests output formatting:
    1. JSON output
    2. CSV output
    3. HTML report
    """
    scan_data = perform_scan(extensions_dir="./tests/fixtures/sample")

    # Test JSON output
    write_json_output(scan_data, "results.json")
    assert os.path.exists("results.json")
    with open("results.json") as f:
        json_data = json.load(f)
        assert 'schema_version' in json_data

    # Test CSV output
    write_csv_output(scan_data, "results.csv")
    assert os.path.exists("results.csv")
    with open("results.csv") as f:
        csv_data = f.read()
        assert 'extension_id' in csv_data

    # Test HTML report
    generate_html_report(scan_data, "report.html")
    assert os.path.exists("report.html")
    with open("report.html") as f:
        html_data = f.read()
        assert '<html' in html_data
```

### Test 5: Error Handling

```python
def test_error_handling():
    """Graceful error handling throughout workflow.

    Tests error scenarios:
    1. Invalid directories handled
    2. Malformed JSON handled
    3. API errors don't crash scan
    """
    # Invalid extensions directory
    with pytest.raises(ValueError):
        perform_scan(extensions_dir="/nonexistent/path")

    # Malformed cache entry (graceful degradation)
    cache = CacheManager()
    # Manually insert corrupted entry
    result = cache.get_cached_result("corrupted.ext", "1.0")
    assert result is None  # Returns None instead of crashing

    # API error during scan (partial results)
    with mock_api_error():
        result = perform_scan(extensions_dir="./tests/fixtures/sample")
        assert result['failed_scans'] > 0
        assert 'error_message' in result
```

### Test 6: Cache Cleanup

```python
def test_cache_cleanup():
    """Cache cleanup removes old entries.

    Tests cache maintenance:
    1. Add entries
    2. Age entries (mock time)
    3. Run cleanup
    4. Verify old entries removed
    """
    cache = CacheManager()

    # Add entries
    cache.save_result("ext1", "1.0", {"score": 80})
    cache.save_result("ext2", "1.0", {"score": 85})

    # Mock time passing (8 days)
    with mock.patch('time.time') as mock_time:
        mock_time.return_value = time.time() + (8 * 24 * 60 * 60)

        # Run cleanup (7-day max age)
        removed = cache.cleanup_old_entries(max_age_days=7)

        assert removed == 2
```

### Test 7: Extension Metadata Parsing

```python
def test_extension_metadata_parsing():
    """Extension metadata extracted correctly.

    Tests metadata extraction:
    1. Parse package.json
    2. Extract publisher, name, version
    3. Validate required fields
    """
    from vscode_scanner.extension_discovery import parse_extension_metadata

    metadata = parse_extension_metadata("./tests/fixtures/sample_ext/package.json")

    assert metadata['publisher'] == "test-publisher"
    assert metadata['name'] == "test-extension"
    assert metadata['version'] == "1.0.0"
    assert 'displayName' in metadata
    assert 'description' in metadata
```

---

## Writing Integration Tests

### Test Structure

```python
def test_integration_workflow():
    """Test description explaining workflow being tested."""
    # ARRANGE - Set up test environment
    with temp_cache(), mock_vscan_api():
        test_extensions = create_test_extensions()

    # ACT - Execute workflow
    result = perform_complete_workflow(test_extensions)

    # ASSERT - Verify end-to-end behavior
    assert workflow_completed_successfully(result)
    assert output_files_created()
    assert cache_updated_correctly()

    # CLEANUP - Handled by context managers
```

### Context Managers for Integration Tests

```python
# tests/conftest.py

@contextmanager
def temp_cache():
    """Provide temporary cache directory."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

@contextmanager
def mock_vscan_api():
    """Mock vscan.dev API responses."""
    with mock.patch('vscode_scanner.vscan_api.scan_extension') as mock_scan:
        mock_scan.return_value = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"total": 0}
        }
        yield mock_scan

@contextmanager
def temp_output_dir():
    """Provide temporary output directory."""
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        yield temp_dir
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
```

---

## Integration Test Best Practices

### DO ✅

- Test real module interactions (not mocked)
- Mock only external services (API, filesystem)
- Test complete workflows end-to-end
- Verify data flow between components
- Test error handling at integration points
- Use fixtures and context managers for cleanup
- Test both happy path and error scenarios

### DON'T ❌

- Mock internal module interactions
- Test individual functions (use unit tests)
- Skip error path testing
- Leave test artifacts (use cleanup)
- Test too many scenarios in one test
- Duplicate unit test coverage

---

## References

- **[TESTING.md](../TESTING.md)** - Main testing guide
- **[TESTING_MOCKING.md](TESTING_MOCKING.md)** - Mocking guidelines

---
