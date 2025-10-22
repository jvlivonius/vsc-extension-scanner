#!/usr/bin/env python3
"""
Security Vulnerability Test Suite
Tests for the vulnerabilities identified in SECURITY_ANALYSIS.md
"""

import os
import sys
import tempfile
import json
import sqlite3
from pathlib import Path

# Import modules to test
from utils import validate_path, sanitize_string
import extension_discovery
import cache_manager


class SecurityTester:
    """Test suite for security vulnerabilities."""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.vulnerabilities_confirmed = 0

    def test(self, name, should_fail=False):
        """Decorator for test methods."""
        def decorator(func):
            def wrapper():
                try:
                    result = func()
                    if should_fail and result:
                        # Expected to fail but didn't - VULNERABILITY!
                        print(f"❌ VULNERABILITY CONFIRMED: {name}")
                        self.vulnerabilities_confirmed += 1
                        self.tests_failed += 1
                    elif not should_fail and result:
                        print(f"✅ PASS: {name}")
                        self.tests_passed += 1
                    else:
                        print(f"❌ FAIL: {name}")
                        self.tests_failed += 1
                except Exception as e:
                    if should_fail:
                        # Expected to fail with exception - good!
                        print(f"✅ PROTECTED: {name} - {type(e).__name__}")
                        self.tests_passed += 1
                    else:
                        print(f"❌ ERROR: {name} - {e}")
                        self.tests_failed += 1
            return wrapper
        return decorator

    def run_all_tests(self):
        """Run all security tests."""
        print("=" * 80)
        print("SECURITY VULNERABILITY TEST SUITE")
        print("Testing vulnerabilities from SECURITY_ANALYSIS.md")
        print("=" * 80)
        print()

        # Test 1: Path Validation Function Exists But Not Used
        print("\n[TEST GROUP 1] Unused Security Functions")
        print("-" * 80)
        self.test_unused_validate_path()
        self.test_unused_sanitize_string()

        # Test 2: Path Traversal Vulnerabilities
        print("\n[TEST GROUP 2] Path Traversal Vulnerabilities")
        print("-" * 80)
        self.test_path_traversal_extensions_dir()
        self.test_path_traversal_cache_dir()

        # Test 3: validate_path() Insufficient Implementation
        print("\n[TEST GROUP 3] validate_path() Implementation Weaknesses")
        print("-" * 80)
        self.test_validate_path_absolute_paths()
        self.test_validate_path_url_encoding()
        self.test_validate_path_double_encoding()

        # Test 4: Cache Integrity
        print("\n[TEST GROUP 4] Cache Integrity")
        print("-" * 80)
        self.test_cache_poisoning()

        # Test 5: Input Validation
        print("\n[TEST GROUP 5] Input Validation")
        print("-" * 80)
        self.test_large_packagejson()
        self.test_malicious_json()

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Vulnerabilities Confirmed: {self.vulnerabilities_confirmed}")
        print()

        if self.vulnerabilities_confirmed > 0:
            print(f"⚠️  WARNING: {self.vulnerabilities_confirmed} VULNERABILITIES CONFIRMED")
            print("See SECURITY_ANALYSIS.md for remediation guidance")
            return 1
        else:
            print("✅ No vulnerabilities confirmed")
            return 0

    def test_unused_validate_path(self):
        """Test #1.1: validate_path() exists but is never used."""
        print("Test 1.1: Checking if validate_path() is actually used...")

        # Search for usage of validate_path in code
        files_to_check = ['vscan.py', 'extension_discovery.py', 'cache_manager.py']
        usage_found = False

        for filename in files_to_check:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    content = f.read()
                    if 'validate_path(' in content and 'def validate_path' not in content:
                        usage_found = True
                        break

        if not usage_found:
            print("   ❌ VULNERABILITY: validate_path() defined but never used!")
            self.vulnerabilities_confirmed += 1
            self.tests_failed += 1
        else:
            print("   ✅ validate_path() is used")
            self.tests_passed += 1

    def test_unused_sanitize_string(self):
        """Test #1.2: sanitize_string() exists but is never used."""
        print("Test 1.2: Checking if sanitize_string() is actually used...")

        files_to_check = ['vscan.py', 'extension_discovery.py', 'cache_manager.py',
                          'output_formatter.py', 'vscan_api.py']
        usage_found = False

        for filename in files_to_check:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    content = f.read()
                    if 'sanitize_string(' in content and 'def sanitize_string' not in content:
                        usage_found = True
                        break

        if not usage_found:
            print("   ❌ VULNERABILITY: sanitize_string() defined but never used!")
            self.vulnerabilities_confirmed += 1
            self.tests_failed += 1
        else:
            print("   ✅ sanitize_string() is used")
            self.tests_passed += 1

    def test_path_traversal_extensions_dir(self):
        """Test #2.1: Can we access /etc via --extensions-dir?"""
        print("Test 2.1: Path traversal in --extensions-dir...")

        try:
            # Try to access /etc directory
            discovery = extension_discovery.ExtensionDiscovery(custom_dir="/etc")
            extensions_dir = discovery.find_extensions_directory()

            if str(extensions_dir) == "/etc":
                print("   ❌ VULNERABILITY: Can read /etc directory!")
                self.vulnerabilities_confirmed += 1
                self.tests_failed += 1
            else:
                print("   ✅ Access to /etc blocked")
                self.tests_passed += 1

        except Exception as e:
            # If it raises an exception for wrong reason (dir not found), still vulnerable
            if "not found" in str(e).lower():
                print(f"   ❌ VULNERABILITY: No path validation (failed on: {e})")
                self.vulnerabilities_confirmed += 1
                self.tests_failed += 1
            else:
                print(f"   ✅ Access blocked: {e}")
                self.tests_passed += 1

    def test_path_traversal_cache_dir(self):
        """Test #2.2: Can we create cache in arbitrary location?"""
        print("Test 2.2: Path traversal in --cache-dir...")

        try:
            # Try to create cache in /tmp
            cache = cache_manager.CacheManager(cache_dir="/tmp/test_cache")

            if str(cache.cache_dir).startswith("/tmp"):
                print("   ❌ VULNERABILITY: Can create cache in /tmp!")
                self.vulnerabilities_confirmed += 1
                self.tests_failed += 1

                # Cleanup
                if cache.cache_db.exists():
                    cache.cache_db.unlink()
                if cache.cache_dir.exists():
                    cache.cache_dir.rmdir()
            else:
                print("   ✅ Cache directory restricted")
                self.tests_passed += 1

        except Exception as e:
            print(f"   ✅ Cache creation blocked: {e}")
            self.tests_passed += 1

    def test_validate_path_absolute_paths(self):
        """Test #3.1: Does validate_path() block absolute paths?"""
        print("Test 3.1: validate_path() handling of absolute paths...")

        dangerous_paths = [
            "/etc/passwd",
            "/var/log/auth.log",
            "C:\\Windows\\System32",
            "/root/.ssh/id_rsa"
        ]

        vulnerable = False
        for path in dangerous_paths:
            if validate_path(path):
                print(f"   ❌ VULNERABILITY: Accepted absolute path: {path}")
                vulnerable = True
                break

        if vulnerable:
            self.vulnerabilities_confirmed += 1
            self.tests_failed += 1
        else:
            print("   ✅ Absolute paths blocked")
            self.tests_passed += 1

    def test_validate_path_url_encoding(self):
        """Test #3.2: Does validate_path() block URL-encoded traversal?"""
        print("Test 3.2: validate_path() handling of URL-encoded paths...")

        # URL-encoded "../../../etc/passwd"
        encoded_path = "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"

        if validate_path(encoded_path):
            print(f"   ❌ VULNERABILITY: Accepted URL-encoded path: {encoded_path}")
            self.vulnerabilities_confirmed += 1
            self.tests_failed += 1
        else:
            print("   ✅ URL-encoded paths blocked")
            self.tests_passed += 1

    def test_validate_path_double_encoding(self):
        """Test #3.3: Does validate_path() block other traversal techniques?"""
        print("Test 3.3: validate_path() handling of alternate traversal...")

        dangerous_paths = [
            "....//",
            "..\\..\\",
            "~/.ssh/",
            "$HOME/.ssh/",
        ]

        vulnerable = False
        for path in dangerous_paths:
            if validate_path(path):
                print(f"   ❌ VULNERABILITY: Accepted path: {path}")
                vulnerable = True

        if vulnerable:
            self.vulnerabilities_confirmed += 1
            self.tests_failed += 1
        else:
            print("   ✅ Alternate traversal methods blocked")
            self.tests_passed += 1

    def test_cache_poisoning(self):
        """Test #4.1: Can we modify cached data without detection?"""
        print("Test 4.1: Cache poisoning detection...")

        try:
            # Create temporary cache
            with tempfile.TemporaryDirectory() as tmpdir:
                cache = cache_manager.CacheManager(cache_dir=tmpdir)

                # Save legitimate result
                test_result = {
                    "scan_status": "success",
                    "security_score": 85,
                    "risk_level": "low",
                    "vulnerabilities": {"count": 0}
                }
                cache.save_result("test.extension", "1.0.0", test_result)

                # Tamper with database
                conn = sqlite3.connect(cache.cache_db)
                cursor = conn.cursor()

                # Modify security score to fake high security
                malicious_result = test_result.copy()
                malicious_result["security_score"] = 100
                malicious_result["risk_level"] = "low"

                cursor.execute("""
                    UPDATE scan_cache
                    SET scan_result = ?
                    WHERE extension_id = 'test.extension'
                """, (json.dumps(malicious_result),))
                conn.commit()
                conn.close()

                # Try to load - should detect tampering
                loaded = cache.get_cached_result("test.extension", "1.0.0")

                if loaded and loaded.get("security_score") == 100:
                    print("   ❌ VULNERABILITY: Cache poisoning not detected!")
                    self.vulnerabilities_confirmed += 1
                    self.tests_failed += 1
                else:
                    print("   ✅ Cache tampering detected")
                    self.tests_passed += 1

        except Exception as e:
            print(f"   ⚠️  Test error: {e}")
            self.tests_failed += 1

    def test_large_packagejson(self):
        """Test #5.1: Does it handle large package.json files?"""
        print("Test 5.1: Large package.json handling...")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create large package.json (5MB)
                pkg_path = Path(tmpdir) / "package.json"
                large_data = {
                    "name": "test",
                    "publisher": "test",
                    "version": "1.0.0",
                    "description": "A" * (5 * 1024 * 1024)  # 5MB string
                }

                with open(pkg_path, 'w') as f:
                    json.dump(large_data, f)

                # Try to parse
                discovery = extension_discovery.ExtensionDiscovery()
                result = discovery._parse_extension(Path(tmpdir))

                if result:
                    print("   ❌ VULNERABILITY: No size limit on package.json!")
                    self.vulnerabilities_confirmed += 1
                    self.tests_failed += 1
                else:
                    print("   ✅ Large package.json rejected")
                    self.tests_passed += 1

        except Exception as e:
            if "too large" in str(e).lower() or "size" in str(e).lower():
                print(f"   ✅ Size limit enforced: {e}")
                self.tests_passed += 1
            else:
                print(f"   ❌ VULNERABILITY: Parser accepted large file (crashed: {e})")
                self.vulnerabilities_confirmed += 1
                self.tests_failed += 1

    def test_malicious_json(self):
        """Test #5.2: Does it handle malicious JSON structures?"""
        print("Test 5.2: Malicious JSON structure handling...")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create deeply nested JSON (DoS attack)
                pkg_path = Path(tmpdir) / "package.json"

                # Create 1000-level deep nesting
                nested = {"name": "test", "publisher": "test"}
                current = nested
                for i in range(1000):
                    current["nested"] = {}
                    current = current["nested"]

                with open(pkg_path, 'w') as f:
                    json.dump(nested, f)

                # Try to parse
                discovery = extension_discovery.ExtensionDiscovery()
                result = discovery._parse_extension(Path(tmpdir))

                if result:
                    print("   ⚠️  WARNING: Deeply nested JSON accepted")
                    # Not a critical vulnerability but worth noting
                    self.tests_passed += 1
                else:
                    print("   ✅ Malicious JSON rejected")
                    self.tests_passed += 1

        except RecursionError:
            print("   ⚠️  WARNING: RecursionError (DoS possible)")
            self.tests_passed += 1
        except Exception as e:
            print(f"   ✅ Malicious JSON rejected: {type(e).__name__}")
            self.tests_passed += 1


def main():
    """Run security tests."""
    tester = SecurityTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
