# Mocking Guidelines

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Applies To:** All 3.x versions
**Target Audience:** Developers, QA Engineers

---

## When to Mock

### DO Mock ✅

- **External API calls** (vscan.dev)
- **Filesystem operations** in unit tests
- **Time** (for testing time-dependent logic)
- **Network requests**
- **System calls**
- **Random values** (for deterministic tests)

### DON'T Mock ❌

- **Internal module interactions** (test real integration)
- **Simple data transformations**
- **Logic being tested**
- **Database operations** in integration tests (use temp DB)
- **Configuration objects** (use test configs)

---

## Mocking Examples

### Mock API Calls

```python
from unittest import mock

@mock.patch('vscode_scanner.vscan_api.scan_extension')
def test_scanner_handles_api_error(mock_scan):
    """Scanner handles API errors gracefully."""
    mock_scan.side_effect = ConnectionError("Network unavailable")

    result = perform_scan(extensions_dir="./test_extensions")

    assert result['failed_scans'] > 0
    assert result['error_message'] is not None
```

### Mock Time

```python
@mock.patch('time.time')
def test_cache_expiration(mock_time):
    """Cached results expire after max_age."""
    cache = CacheManager()

    # Cache entry created at t=0
    mock_time.return_value = 0
    cache.save_result("test.ext", "1.0", {"score": 80})

    # Check at t=8 days (should be expired with 7-day max age)
    mock_time.return_value = 8 * 24 * 60 * 60
    result = cache.get_cached_result("test.ext", "1.0", max_age_days=7)

    assert result is None  # Expired
```

### Mock Filesystem

```python
@mock.patch('os.path.exists')
@mock.patch('os.listdir')
def test_extension_discovery(mock_listdir, mock_exists):
    """Extension discovery finds extensions in directory."""
    mock_exists.return_value = True
    mock_listdir.return_value = ['ext1', 'ext2', 'ext3']

    extensions = discover_extensions("/fake/path")

    assert len(extensions) == 3
```

---

## Mock Validation

### The Problem

**Mocks can drift from real API behavior**, causing tests to pass while real integration fails.

**Example:**
```python
# Mock returns different fields than real API
mock_response = {"score": 85}  # Missing required fields!

# Test passes with mock
assert mock_response['score'] == 85  # ✅

# Real API returns
real_response = {"security_score": 85, "scan_status": "success", ...}

# Production fails!
assert real_response['score']  # ❌ KeyError
```

### The Solution: Canonical Mocks

Use validated mocks that match real API structure.

**Test File:** `tests/test_mock_validation.py`

**Canonical Mock:**
```python
# tests/fixtures/canonical_mock.py

class CanonicalVscanAPIMock:
    """Canonical mock matching real vscan.dev API structure.

    Validated against real API on 2025-10-26.
    Update when API changes.
    """

    @staticmethod
    def get_success_response(publisher, name, security_score=85, vuln_count=0):
        """Get success response with all required fields."""
        return {
            # Identity
            'name': name,
            'publisher': publisher,

            # Status
            'scan_status': 'success',
            'error': None,
            'has_errors': False,

            # Metadata
            'metadata': {
                'version': '1.0.0',
                'display_name': f"{name} Extension",
                'description': "Test extension"
            },

            # Security (CRITICAL)
            'security': {
                'score': security_score,
                'risk_level': 'low' if security_score >= 80 else 'high'
            },
            'security_score': security_score,
            'risk_level': 'low' if security_score >= 80 else 'high',

            # Vulnerabilities (CRITICAL)
            'vulnerabilities': {
                'total': vuln_count,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'items': []
            },

            # Additional
            'dependencies': [],
            'risk_factors': [],
            'vscan_url': f"https://vscan.dev/{publisher}/{name}",
            'analysis_timestamp': "2025-10-26T12:00:00Z",
            'analysis_id': "test-12345",
            'raw_response': {}
        }

    @staticmethod
    def get_error_response(publisher, name, error_message):
        """Get error response structure."""
        return {
            'name': name,
            'publisher': publisher,
            'scan_status': 'error',
            'error': error_message,
            'has_errors': True,
            'security_score': None,
            'vulnerabilities': None,
            'raw_response': {}
        }

    @staticmethod
    def get_vulnerable_response(publisher, name, critical_count=1):
        """Get response with vulnerabilities."""
        response = CanonicalVscanAPIMock.get_success_response(
            publisher, name, security_score=45, vuln_count=critical_count
        )
        response['vulnerabilities'] = {
            'total': critical_count,
            'critical': critical_count,
            'high': 0,
            'medium': 0,
            'low': 0,
            'items': [
                {
                    'id': 'CVE-2024-1234',
                    'severity': 'critical',
                    'description': 'Test vulnerability',
                    'affected_versions': '< 1.0.0'
                }
            ]
        }
        response['risk_level'] = 'critical'
        return response
```

### Using Canonical Mocks

```python
from tests.fixtures.canonical_mock import CanonicalVscanAPIMock

def test_scanner_with_valid_response():
    """Test scanner with realistic API response."""
    # Use canonical mock that matches real API structure
    mock_response = CanonicalVscanAPIMock.get_success_response(
        publisher="test-publisher",
        name="test-extension",
        security_score=85,
        vuln_count=0
    )

    # All required fields are present
    assert 'scan_status' in mock_response
    assert 'metadata' in mock_response
    assert 'security' in mock_response
    assert 'vulnerabilities' in mock_response
    # ... all 16 required fields present

    # Test scanner processes response correctly
    result = process_scan_response(mock_response)
    assert result['risk_level'] == 'low'
```

### Validating Mocks

**Run mock validation tests:**
```bash
# Includes 1 real API call to validate mock structure
python3 tests/test_mock_validation.py
```

**Validation checks:**
1. All required fields present
2. Field types match (int, str, dict, list)
3. Field names match exactly (no typos)
4. Nested structure matches
5. Critical fields have correct values

**Required Fields (validated 2025-10-26):**
```python
REQUIRED_SUCCESS_FIELDS = {
    'name', 'publisher', 'scan_status', 'error',
    'metadata', 'security', 'dependencies', 'risk_factors',
    'security_score', 'risk_level', 'vulnerabilities',
    'vscan_url', 'analysis_timestamp', 'has_errors',
    'raw_response', 'analysis_id'
}
```

**Critical Fields (scanner depends on these):**
```python
CRITICAL_FIELDS = {
    'scan_status',      # 'success' or 'error'
    'security_score',   # int 0-100 or None
    'vulnerabilities'   # dict with 'count', 'critical', etc.
}
```

---

## Mock Best Practices

### DO ✅

- Use canonical mocks for API responses
- Validate mocks against real APIs periodically
- Mock at appropriate level (not too high, not too low)
- Verify mock was called with correct arguments
- Use `side_effect` for dynamic behavior
- Clean up patches after tests
- Document what's being mocked and why

### DON'T ❌

- Create ad-hoc mocks without validation
- Mock everything (test real interactions)
- Mock internal module functions
- Skip mock validation
- Use incomplete mock responses
- Patch too broadly (use specific paths)
- Leave mocks active between tests

### Example: Proper Mocking Level

```python
# ❌ TOO HIGH - Mocks too much
@mock.patch('vscode_scanner.scanner')
def test_bad_mock(mock_scanner):
    # Now you're not testing any real code!
    pass

# ❌ TOO LOW - Too granular
@mock.patch('vscode_scanner.scanner.Scanner._validate_input')
@mock.patch('vscode_scanner.scanner.Scanner._process_results')
@mock.patch('vscode_scanner.scanner.Scanner._save_cache')
def test_bad_mock(mock_save, mock_process, mock_validate):
    # Too many mocks, testing implementation details
    pass

# ✅ JUST RIGHT - Mock external boundary
@mock.patch('vscode_scanner.vscan_api.scan_extension')
def test_good_mock(mock_api):
    # Mock external API, test real scanner logic
    mock_api.return_value = CanonicalVscanAPIMock.get_success_response(...)
    result = scanner.run_scan(...)
    assert result['total_scanned'] > 0
```

---

## When Creating New Mocks

1. **Always use `CanonicalVscanAPIMock` as base**
2. **Run `test_mock_validation.py` to verify**
3. **Update canonical mock if real API changes**
4. **Re-run validation after updates**
5. **Document mock structure in docstring**

**Validation Frequency:**
- Run before each release
- Run when vscan.dev API updates
- Run if mock-based tests fail in production
- Run quarterly as preventive maintenance

---

## Advanced Mocking

### Mock with Side Effects

```python
def test_retry_mechanism():
    """Test retry logic with intermittent failures."""
    with mock.patch('vscode_scanner.vscan_api.scan_extension') as mock_api:
        # Fail twice, then succeed
        mock_api.side_effect = [
            ConnectionError("Network error"),
            ConnectionError("Network error"),
            {"scan_status": "success", "security_score": 85}
        ]

        result = scan_with_retry("test.ext")

        assert result['scan_status'] == 'success'
        assert mock_api.call_count == 3  # 2 failures + 1 success
```

### Mock Context Manager

```python
@mock.patch('builtins.open', new_callable=mock.mock_open, read_data='{"key": "value"}')
def test_read_config(mock_file):
    """Test config reading."""
    config = read_config_file("/path/to/config.json")

    assert config['key'] == 'value'
    mock_file.assert_called_once_with("/path/to/config.json", "r")
```

---

## References

- **[TESTING.md](../TESTING.md)** - Main testing guide
- **[TESTING_INTEGRATION.md](TESTING_INTEGRATION.md)** - Integration testing patterns
- **tests/fixtures/canonical_mock.py** - Canonical mock implementation
- **tests/test_mock_validation.py** - Mock validation tests

---

**Document Version:** 1.0
**Status:** Current
**Last Updated:** 2025-10-30 (v3.5.3 Testing Excellence - Phase 4)
**Maintained By:** Development Team
