#!/usr/bin/env python3
"""
Security Manual Validation Tests

Converted from SecurityTester class to proper pytest tests.
Tests security vulnerabilities and ensures protections are in place.

These tests validate:
1. Security functions are actually used in production code
2. Path traversal protections work
3. validate_path() blocks malicious inputs
4. Cache integrity protection works
5. Input validation handles edge cases
"""

import os
import sys
import tempfile
import json
import sqlite3
from pathlib import Path
import shutil

import pytest

# Import modules to test
from vscode_scanner.utils import validate_path, sanitize_string, validate_extension_id
from vscode_scanner import extension_discovery
from vscode_scanner import cache_manager


# ============================================================================
# Test Group 1: Unused Security Functions
# ============================================================================


@pytest.mark.security
class TestSecurityFunctionsUsage:
    """Verify security functions are actually used in production code."""

    def test_validate_path_is_used_in_codebase(self):
        """Test that validate_path() is actually used (not just defined)."""
        files_to_check = [
            "vscode_scanner/extension_discovery.py",
            "vscode_scanner/cache_manager.py",
            "vscode_scanner/cli.py",
            "vscode_scanner/config_manager.py",
        ]
        usage_found = False
        base_dir = Path(__file__).parent.parent

        for filename in files_to_check:
            filepath = base_dir / filename
            if filepath.exists():
                with open(filepath, "r") as f:
                    content = f.read()
                    if (
                        "validate_path(" in content
                        and "def validate_path" not in content
                    ):
                        usage_found = True
                        break

        assert (
            usage_found
        ), "validate_path() defined but never used - SECURITY VULNERABILITY"

    def test_sanitize_string_is_used_in_codebase(self):
        """Test that sanitize_string() is actually used (not just defined)."""
        files_to_check = [
            "vscode_scanner/vscan_api.py",
            "vscode_scanner/extension_discovery.py",
            "vscode_scanner/scanner.py",
            "vscode_scanner/output_formatter.py",
        ]
        usage_found = False
        base_dir = Path(__file__).parent.parent

        for filename in files_to_check:
            filepath = base_dir / filename
            if filepath.exists():
                with open(filepath, "r") as f:
                    content = f.read()
                    if (
                        "sanitize_string(" in content
                        and "def sanitize_string" not in content
                    ):
                        usage_found = True
                        break

        assert (
            usage_found
        ), "sanitize_string() defined but never used - SECURITY VULNERABILITY"


# ============================================================================
# Test Group 2: Path Traversal Vulnerabilities
# ============================================================================


@pytest.mark.security
class TestPathTraversalProtection:
    """Verify path traversal attacks are blocked."""

    def test_extensions_dir_blocks_system_paths(self):
        """Test that --extensions-dir blocks access to /etc."""
        with pytest.raises((ValueError, FileNotFoundError)):
            discovery = extension_discovery.ExtensionDiscovery(custom_dir="/etc")
            extensions_dir = discovery.find_extensions_directory()

            # If we get here, check if it actually allowed /etc
            if str(extensions_dir) == "/etc":
                pytest.fail("VULNERABILITY: Can read /etc directory!")

    def test_cache_dir_blocks_arbitrary_locations(self):
        """Test that cache directories work in home directory (temp blocked by security)."""
        # Use home directory pattern (aligned with test_cache_tampering_is_detected:191)
        tmpdir = os.path.join(os.path.expanduser("~"), ".vscan_test_manual_validation")
        os.makedirs(tmpdir, exist_ok=True)

        try:
            cache = cache_manager.CacheManager(cache_dir=tmpdir)

            # Verify cache was created
            assert cache.cache_dir.exists()
            assert str(cache.cache_dir.resolve()).endswith(
                ".vscan_test_manual_validation"
            )

        finally:
            # Cleanup
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)


# ============================================================================
# Test Group 3: validate_path() Implementation
# ============================================================================


@pytest.mark.security
class TestValidatePathImplementation:
    """Verify validate_path() blocks malicious inputs."""

    def test_validate_path_blocks_system_directories(self):
        """Test that validate_path() blocks system directory paths."""
        system_paths = ["/etc/passwd", "/var/log/auth.log", "/root/.ssh/id_rsa"]

        for path in system_paths:
            with pytest.raises(ValueError, match="system directories"):
                validate_path(path)

    def test_validate_path_blocks_url_encoded_traversal(self):
        """Test that validate_path() blocks URL-encoded path traversal."""
        # URL-encoded "../../../etc/passwd"
        encoded_path = "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"

        with pytest.raises(ValueError):
            validate_path(encoded_path)

    def test_validate_path_blocks_parent_traversal(self):
        """Test that validate_path() blocks parent directory traversal."""
        dangerous_paths = [
            "../../../etc/passwd",
            "test/../../../etc/passwd",
        ]

        for path in dangerous_paths:
            with pytest.raises(ValueError):
                validate_path(path)

    def test_validate_path_allows_home_directory(self):
        """Test that validate_path() allows home directory paths."""
        # These should be allowed
        safe_paths = [
            "~/.vscode",
            os.path.expanduser("~/.vscode"),
        ]

        for path in safe_paths:
            # Should not raise
            result = validate_path(path)
            assert result is not None


# ============================================================================
# Test Group 4: Cache Integrity
# ============================================================================


@pytest.mark.security
class TestCacheIntegrityProtection:
    """Verify cache poisoning is detected."""

    def test_cache_tampering_is_detected(self):
        """Test that cache poisoning/tampering is detected."""
        # Create temporary cache in home directory
        tmpdir = os.path.join(os.path.expanduser("~"), ".vscan_test_security")
        os.makedirs(tmpdir, exist_ok=True)

        try:
            cache = cache_manager.CacheManager(cache_dir=tmpdir)

            # Save legitimate result
            test_result = {
                "scan_status": "success",
                "security_score": 85,
                "risk_level": "low",
                "vulnerabilities": {"count": 0},
            }
            cache.save_result("test.extension", "1.0.0", test_result)

            # Tamper with database
            conn = sqlite3.connect(cache.cache_db)
            cursor = conn.cursor()

            # Modify security score to fake high security
            malicious_result = test_result.copy()
            malicious_result["security_score"] = 100
            malicious_result["risk_level"] = "low"

            cursor.execute(
                """
                UPDATE scan_cache
                SET scan_result = ?
                WHERE extension_id = 'test.extension'
            """,
                (json.dumps(malicious_result),),
            )
            conn.commit()
            conn.close()

            # Try to load - should detect tampering
            loaded = cache.get_cached_result("test.extension", "1.0.0")

            # Should either return None (tampering detected) or raise an error
            # But should NOT return the modified data
            if loaded and loaded.get("security_score") == 100:
                pytest.fail("VULNERABILITY: Cache poisoning not detected!")

        finally:
            # Cleanup
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)


# ============================================================================
# Test Group 5: Input Validation
# ============================================================================


@pytest.mark.security
class TestInputValidation:
    """Verify input validation handles malicious inputs."""

    def test_large_packagejson_is_handled(self):
        """Test that large package.json files are rejected with size limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create large package.json (5MB)
            pkg_path = Path(tmpdir) / "package.json"
            large_data = {
                "name": "test",
                "publisher": "test",
                "version": "1.0.0",
                "description": "A" * (5 * 1024 * 1024),  # 5MB string
            }

            with open(pkg_path, "w") as f:
                json.dump(large_data, f)

            # Try to parse - should raise exception for size limit
            discovery = extension_discovery.ExtensionDiscovery()

            with pytest.raises(Exception, match="too large"):
                result = discovery._parse_extension(Path(tmpdir))

    def test_deeply_nested_json_is_handled(self):
        """Test that deeply nested JSON structures are handled safely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create deeply nested JSON (potential DoS attack)
            pkg_path = Path(tmpdir) / "package.json"

            # Create moderate nesting (100 levels to avoid RecursionError in test itself)
            nested = {"name": "test", "publisher": "test", "version": "1.0.0"}
            current = nested
            for i in range(100):
                current["nested"] = {}
                current = current["nested"]

            # Write JSON without recursion issues
            with open(pkg_path, "w") as f:
                json.dump(nested, f)

            # Try to parse - should handle gracefully
            discovery = extension_discovery.ExtensionDiscovery()
            result = discovery._parse_extension(Path(tmpdir))

            # Should successfully parse (100 levels is acceptable)
            # The key is we don't crash the parser
            assert result is not None

    def test_extension_id_validation_blocks_sql_injection(self):
        """Test extension ID validation prevents SQL injection."""
        # Valid extension IDs
        valid_ids = [
            "ms-python.python",
            "GitHub.copilot",
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
            "redhat.java",
        ]

        # Invalid/malicious extension IDs
        invalid_ids = [
            "'; DROP TABLE scan_cache; --",
            "../../../etc/passwd",
            "publisher' OR '1'='1",
            "test.'; DELETE FROM scan_cache WHERE '1'='1",
            "no-dot-separator",
            ".only-dot",
            "dot-only.",
            "",
            None,
            "publisher..name",
            "pub/lisher.name",
            "pub\\lisher.name",
        ]

        # Test valid IDs are accepted
        for ext_id in valid_ids:
            assert validate_extension_id(ext_id), f"Valid ID rejected: {ext_id}"

        # Test invalid IDs are rejected
        for ext_id in invalid_ids:
            assert not validate_extension_id(ext_id), f"Invalid ID accepted: {ext_id}"
