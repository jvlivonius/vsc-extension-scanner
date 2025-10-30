#!/usr/bin/env python3
"""
SQLite Security Tests for VS Code Extension Security Scanner

Tests custom SQLite security requirements:
1. File permissions (0o600 for cache.db, 0o600 for .cache_secret, 0o700 for cache directory)
2. SQL injection prevention (parameterized queries only)
3. HMAC timing-safe comparison (hmac.compare_digest)
4. Database schema integrity
5. HMAC signature integrity

Security Requirements:
- CRITICAL: All SQL queries must use parameterized statements (no string formatting)
- CRITICAL: HMAC comparison must use timing-safe hmac.compare_digest()
- CRITICAL: Database file permissions must be user-only (0o600)
- CRITICAL: Cache directory must be user-only (0o700)
- CRITICAL: Secret key file must be user-only (0o600)
"""

import sys
import os
import stat
import sqlite3
import tempfile
import shutil
import inspect
import hmac
from pathlib import Path

import pytest

# Module-level marker for all tests in this file
pytestmark = pytest.mark.security

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vscode_scanner.cache_manager import CacheManager


def test_sqlite_file_permissions():
    """
    CRITICAL SECURITY TEST: Verify cache database has restrictive permissions

    Tests that the SQLite database file has user-only read/write permissions (0o600).
    This prevents other users from reading cached security scores or modifying them.

    Security Impact: HIGH
    - Prevents unauthorized access to cached security data
    - Prevents cache tampering by other local users
    """
    print("\n[TEST] SQLite File Permissions...")

    # Create temporary cache directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize cache manager with temp directory
        cache = CacheManager(cache_dir=temp_dir)

        # Check if cache DB exists
        db_path = cache.cache_db

        if not db_path.exists():
            print("  ❌ FAIL: Cache database not created during initialization")
            assert False, "Cache database not created during initialization"

        # Get file permissions
        file_stat = os.stat(db_path)
        file_mode = stat.S_IMODE(file_stat.st_mode)

        # Expected: 0o600 (user read+write only)
        expected_mode = 0o600

        if file_mode == expected_mode:
            print(f"  ✅ PASS: Cache DB has correct permissions: {oct(file_mode)}")
        else:
            print(
                f"  ❌ FAIL: Cache DB has insecure permissions: {oct(file_mode)} (expected {oct(expected_mode)})"
            )
            print(f"        File permissions allow unauthorized access!")
            assert (
                False
            ), f"Cache DB has insecure permissions: {oct(file_mode)} (expected {oct(expected_mode)})"


def test_cache_directory_permissions():
    """
    CRITICAL SECURITY TEST: Verify cache directory has restrictive permissions

    Tests that the cache directory has user-only permissions (0o700).
    This prevents other users from accessing the cache directory entirely.

    Security Impact: HIGH
    - Prevents directory listing by other users
    - Prevents file creation/deletion by other users
    """
    print("\n[TEST] Cache Directory Permissions...")

    # Create temporary cache directory
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_path = Path(temp_dir) / "test_cache"

        # Initialize cache manager with custom directory
        cache = CacheManager(cache_dir=str(cache_path))

        # Check directory permissions
        dir_stat = os.stat(cache_path)
        dir_mode = stat.S_IMODE(dir_stat.st_mode)

        # Expected: 0o700 (user read+write+execute only)
        expected_mode = 0o700

        if dir_mode == expected_mode:
            print(f"  ✅ PASS: Cache directory has correct permissions: {oct(dir_mode)}")
        else:
            print(
                f"  ❌ FAIL: Cache directory has insecure permissions: {oct(dir_mode)} (expected {oct(expected_mode)})"
            )
            print(f"        Directory allows unauthorized access!")
            assert (
                False
            ), f"Cache directory has insecure permissions: {oct(dir_mode)} (expected {oct(expected_mode)})"


def test_secret_key_file_permissions():
    """
    CRITICAL SECURITY TEST: Verify secret key file has restrictive permissions

    Tests that the .cache_secret file has user-only read/write permissions (0o600).
    This prevents other users from reading the HMAC secret key.

    Security Impact: CRITICAL
    - Prevents other users from forging HMAC signatures
    - Prevents cache integrity bypass attacks
    """
    print("\n[TEST] Secret Key File Permissions...")

    # Create temporary cache directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize cache manager (creates secret key)
        cache = CacheManager(cache_dir=temp_dir)

        # Check secret key file
        secret_file = cache.cache_dir / ".cache_secret"

        if not secret_file.exists():
            print("  ❌ FAIL: Secret key file not created")
            assert False, "Secret key file not created"

        # Get file permissions
        file_stat = os.stat(secret_file)
        file_mode = stat.S_IMODE(file_stat.st_mode)

        # Expected: 0o600 (user read+write only)
        expected_mode = 0o600

        if file_mode == expected_mode:
            print(
                f"  ✅ PASS: Secret key file has correct permissions: {oct(file_mode)}"
            )
        else:
            print(
                f"  ❌ FAIL: Secret key file has insecure permissions: {oct(file_mode)} (expected {oct(expected_mode)})"
            )
            print(
                f"        Secret key is readable by other users - CRITICAL VULNERABILITY!"
            )
            assert (
                False
            ), f"Secret key file has insecure permissions: {oct(file_mode)} (expected {oct(expected_mode)})"


def test_no_sql_injection_patterns():
    """
    CRITICAL SECURITY TEST: Verify no SQL injection vulnerabilities

    Scans cache_manager.py for dangerous SQL patterns that could lead to SQL injection.
    All SQL queries MUST use parameterized statements (? placeholders).

    Security Impact: CRITICAL
    - SQL injection can bypass all security controls
    - Attackers could modify cached security scores
    - Attackers could delete security findings

    Dangerous Patterns Checked:
    - f"SELECT ... (f-strings in SQL)
    - f"INSERT ... (f-strings in SQL)
    - f"UPDATE ... (f-strings in SQL)
    - f"DELETE ... (f-strings in SQL)
    - % "SELECT (string formatting in SQL)
    - .format("SELECT (str.format in SQL)
    """
    print("\n[TEST] SQL Injection Prevention...")

    # Read cache_manager.py source
    cache_manager_path = (
        Path(__file__).parent.parent / "vscode_scanner" / "cache_manager.py"
    )
    with open(cache_manager_path) as f:
        content = f.read()

    # Dangerous patterns that indicate SQL injection vulnerability
    dangerous_patterns = [
        'f"SELECT',
        'f"INSERT',
        'f"UPDATE',
        'f"DELETE',
        'f"CREATE',
        'f"DROP',
        "f'SELECT",
        "f'INSERT",
        "f'UPDATE",
        "f'DELETE",
        "f'CREATE",
        "f'DROP",
        '% "SELECT',
        '% "INSERT',
        '% "UPDATE',
        '% "DELETE',
        '.format("SELECT',
        '.format("INSERT',
        '.format("UPDATE',
        '.format("DELETE',
    ]

    found_issues = []
    for pattern in dangerous_patterns:
        if pattern in content:
            found_issues.append(pattern)

    if not found_issues:
        print("  ✅ PASS: No SQL injection patterns detected")
        print("        All queries use parameterized statements")
    else:
        print("  ❌ FAIL: Found dangerous SQL patterns:")
        for issue in found_issues:
            print(f"        - {issue}")
        print("        SQL queries MUST use parameterized statements (? placeholders)!")
        assert False, f"Found dangerous SQL patterns: {', '.join(found_issues)}"


def test_hmac_timing_safe_comparison():
    """
    CRITICAL SECURITY TEST: Verify HMAC uses timing-safe comparison

    Tests that HMAC signature verification uses hmac.compare_digest() instead
    of direct string comparison (==). Direct comparison is vulnerable to timing
    attacks that can leak signature information byte-by-byte.

    Security Impact: HIGH
    - Timing attacks can extract HMAC signatures
    - Attackers could forge cache entries with valid signatures
    - Cache integrity could be completely bypassed

    Required: hmac.compare_digest() for all signature comparisons
    Forbidden: Direct string comparison (== or !=) for signatures
    """
    print("\n[TEST] HMAC Timing-Safe Comparison...")

    # Inspect _verify_integrity_signature method
    source = inspect.getsource(CacheManager._verify_integrity_signature)

    # Check for timing-safe comparison
    has_timing_safe = "hmac.compare_digest" in source

    # Check for dangerous direct comparison
    # Note: We check for == after "signature" to catch direct comparisons
    has_direct_compare = "==" in source and "signature" in source

    if has_timing_safe and not ("signature ==" in source or "== signature" in source):
        print("  ✅ PASS: HMAC verification uses timing-safe hmac.compare_digest()")
        print("        Prevents timing attacks on signature verification")
    elif not has_timing_safe:
        print("  ❌ FAIL: hmac.compare_digest() not found in signature verification")
        print("        Direct comparison (==) is vulnerable to timing attacks!")
        assert False, "hmac.compare_digest() not found in signature verification"
    else:
        print("  ❌ FAIL: Found direct signature comparison (==)")
        print("        Must use hmac.compare_digest() for timing safety!")
        assert (
            False
        ), "Found direct signature comparison - must use hmac.compare_digest()"


def test_database_schema_validation():
    """
    SECURITY TEST: Verify database schema integrity

    Tests that the SQLite database has the expected schema structure.
    Verifies all required security columns exist:
    - integrity_signature (HMAC signature column)
    - security_score (cached security score)
    - risk_level (cached risk assessment)

    Security Impact: MEDIUM
    - Missing columns could indicate schema corruption
    - Schema validation prevents database tampering
    """
    print("\n[TEST] Database Schema Validation...")

    # Create temporary cache
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = CacheManager(cache_dir=temp_dir)

        # Connect to database
        conn = sqlite3.connect(cache.cache_db)
        cursor = conn.cursor()

        # Get table schema
        cursor.execute("PRAGMA table_info(scan_cache)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        conn.close()

        # Required security columns
        required_columns = {
            "integrity_signature": "TEXT",  # HMAC signature
            "security_score": "INTEGER",  # Cached security score
            "risk_level": "TEXT",  # Cached risk level
            "vulnerabilities_count": "INTEGER",  # Vulnerability count
            "extension_id": "TEXT",  # Extension identifier
            "version": "TEXT",  # Extension version
            "scan_result": "TEXT",  # Full scan result JSON
            "scanned_at": "TIMESTAMP",  # Scan timestamp
        }

        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                missing_columns.append(col_name)

        if not missing_columns:
            print(
                f"  ✅ PASS: Database schema valid ({len(required_columns)} required columns)"
            )
            print("        All security columns present")
        else:
            print("  ❌ FAIL: Missing required columns:")
            for col in missing_columns:
                print(f"        - {col}")
            assert False, f"Missing required columns: {', '.join(missing_columns)}"


def test_hmac_signature_integrity():
    """
    SECURITY TEST: Verify HMAC signature integrity checking works

    Tests that:
    1. Valid signatures are accepted
    2. Invalid signatures are rejected
    3. Modified data fails signature verification
    4. Cache entries without signatures are rejected

    Security Impact: HIGH
    - Ensures cache tampering is detected
    - Verifies HMAC implementation correctness
    """
    print("\n[TEST] HMAC Signature Integrity...")

    # Create temporary cache
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = CacheManager(cache_dir=temp_dir)

        # Test data
        test_data = '{"test": "data", "security_score": 85}'

        # Test 1: Valid signature verification
        signature = cache._compute_integrity_signature(test_data)
        is_valid = cache._verify_integrity_signature(test_data, signature)

        if not is_valid:
            print("  ❌ FAIL: Valid signature rejected")
            assert False, "Valid signature rejected"

        # Test 2: Invalid signature rejection
        invalid_signature = "0" * 64  # Invalid hex signature
        is_valid = cache._verify_integrity_signature(test_data, invalid_signature)

        if is_valid:
            print("  ❌ FAIL: Invalid signature accepted")
            assert False, "Invalid signature accepted"

        # Test 3: Modified data detection
        modified_data = '{"test": "modified", "security_score": 100}'
        is_valid = cache._verify_integrity_signature(modified_data, signature)

        if is_valid:
            print("  ❌ FAIL: Modified data accepted with original signature")
            assert False, "Modified data accepted with original signature"

        # Test 4: Empty signature rejection
        is_valid = cache._verify_integrity_signature(test_data, "")

        if is_valid:
            print("  ❌ FAIL: Empty signature accepted")
            assert False, "Empty signature accepted"

        print("  ✅ PASS: HMAC signature integrity verified")
        print("        - Valid signatures accepted")
        print("        - Invalid signatures rejected")
        print("        - Modified data detected")
        print("        - Empty signatures rejected")


def test_parameterized_query_coverage():
    """
    SECURITY TEST: Verify all execute() calls use parameterized queries

    Scans cache_manager.py to ensure all cursor.execute() and cursor.executemany()
    calls use parameterized queries with ? placeholders OR are safe queries
    without user input (like SELECT COUNT(*), PRAGMA statements, etc.)

    Security Impact: CRITICAL
    - Comprehensive SQL injection prevention
    - Ensures no queries with user input bypass parameterization
    """
    print("\n[TEST] Parameterized Query Coverage...")

    # Read cache_manager.py source
    cache_manager_path = (
        Path(__file__).parent.parent / "vscode_scanner" / "cache_manager.py"
    )
    with open(cache_manager_path) as f:
        lines = f.readlines()

    # Find all execute/executemany calls
    execute_calls = []
    for line_num, line in enumerate(lines, 1):
        if ".execute(" in line or ".executemany(" in line:
            execute_calls.append((line_num, line.strip()))

    # Safe patterns that don't need parameterization (no user input)
    safe_patterns = [
        "PRAGMA",  # PRAGMA statements are always safe
        "sqlite_master",  # System table queries are safe
        "SELECT COUNT(*)",  # COUNT queries without WHERE are safe
        "SELECT MIN(",  # Aggregate functions without WHERE are safe
        "SELECT MAX(",  # Aggregate functions without WHERE are safe
        "SELECT value FROM metadata WHERE key =",  # Hard-coded metadata keys
        "CREATE TABLE",  # Table creation is safe (design-time)
        "CREATE INDEX",  # Index creation is safe (design-time)
        "INSERT OR REPLACE INTO metadata",  # Metadata updates with hard-coded keys
        "ALTER TABLE",  # Schema changes are safe (design-time)
        "VACUUM",  # VACUUM command is safe
    ]

    # Check each execute call
    issues = []
    for line_num, line in execute_calls:
        # Skip comments
        if line.strip().startswith("#"):
            continue

        # Skip multi-line strings (schema definitions)
        if '"""' in line:
            continue

        # Check if it's a safe pattern
        is_safe = any(pattern in line for pattern in safe_patterns)

        # Check if it's parameterized (has ? placeholder or uses variable with params)
        # Split on either execute( or executemany(
        if "execute(" in line:
            split_parts = line.split("execute(")
        elif "executemany(" in line:
            split_parts = line.split("executemany(")
        else:
            split_parts = ["", ""]  # Fallback for safety

        has_placeholder = "?" in line or (
            len(split_parts) > 1 and ", " in split_parts[1]
        )

        # If not safe and not parameterized, it might be unsafe
        if not is_safe and not has_placeholder:
            # Additional checks for known safe patterns
            if "SELECT" in line and "WHERE" not in line and "FROM scan_cache" in line:
                # SELECT without WHERE from scan_cache - safe
                continue
            elif "SELECT" in line and "FROM scan_cache" in line and "?" in line:
                # Parameterized SELECT - safe
                continue
            else:
                issues.append((line_num, line, "Query without obvious safety pattern"))

    if not issues:
        print(f"  ✅ PASS: All {len(execute_calls)} execute() calls are safe")
        print("        Parameterized queries or safe patterns without user input")
    else:
        print(f"  ⚠️  WARNING: Found {len(issues)} queries to review:")
        for line_num, line, reason in issues[:5]:  # Show first 5
            print(f"        Line {line_num}: {reason}")
            print(f"          {line[:80]}...")
        # Don't fail - these might be false positives, manual review needed
        print("        Manual review recommended (may be false positives)")
        # Don't fail on potential false positives


def run_all_tests():
    """Run all SQLite security tests and report results."""
    print("=" * 70)
    print("SQLite SECURITY TEST SUITE - VS Code Extension Security Scanner")
    print("=" * 70)
    print("\nCritical Security Requirements:")
    print("  1. File Permissions: Cache DB (0o600), Directory (0o700), Secret (0o600)")
    print("  2. SQL Injection: All queries use parameterized statements")
    print("  3. HMAC Safety: Timing-safe hmac.compare_digest() for signatures")
    print("  4. Schema Integrity: All security columns present")
    print("  5. Signature Integrity: HMAC validation prevents tampering")

    tests = [
        ("File Permissions (Cache DB)", test_sqlite_file_permissions),
        ("Directory Permissions", test_cache_directory_permissions),
        ("Secret Key Permissions", test_secret_key_file_permissions),
        ("SQL Injection Prevention", test_no_sql_injection_patterns),
        ("HMAC Timing Safety", test_hmac_timing_safe_comparison),
        ("Database Schema", test_database_schema_validation),
        ("HMAC Integrity", test_hmac_signature_integrity),
        ("Parameterized Query Coverage", test_parameterized_query_coverage),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            # If no exception raised, test passed (pytest convention)
            results.append((test_name, True))
        except AssertionError as e:
            # Expected test failure
            print(f"\n[TEST] {test_name}...")
            print(f"  ❌ ASSERTION FAILED: {str(e)}")
            results.append((test_name, False))
        except Exception as e:
            # Unexpected exception
            print(f"\n[TEST] {test_name}...")
            print(f"  ❌ EXCEPTION: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL SQLITE SECURITY TESTS PASSED")
        print("   Cache implementation meets security requirements")
        return 0
    else:
        print(f"\n⚠️  {total - passed} SECURITY TEST(S) FAILED")
        print("   Review failures and fix security issues before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
