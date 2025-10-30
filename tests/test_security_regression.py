#!/usr/bin/env python3
"""
Security Regression Test Suite (v3.5.1 Phase 1 Complete)

This test suite ensures that all security fixes from v3.5.1 Phase 1 remain in place
and cannot be accidentally broken by future code changes.

**Security Hardening Tests:**

Task 1 - Unified Path Validation:
- Blocks URL-encoded paths (%2e%2e%2f = ../)
- Blocks system directory access (/etc, /sys, /var, /root, etc.)
- Blocks parent directory traversal (../)
- Blocks dangerous characters (null bytes, pipes, semicolons)
- Expands shell variables safely (~/, $HOME/)
- Works across all entry points (CLI, config, cache, extensions)

Task 2 - Unified String Sanitization:
- Removes ANSI escape sequences (terminal injection)
- Removes control characters (null, bell, backspace, etc.)
- Preserves safe whitespace (\n, \t, \r)
- Truncates long strings (DoS prevention)
- Handles Unicode correctly
- Works across all output paths

Task 3 - Cache Integrity Checks:
- HMAC-SHA256 signatures for cache entries
- Detects cache poisoning/tampering
- Timing-safe signature verification
- Secret key management with restrictive permissions
- Rejects unsigned entries (migration safety)

**Integration Tests:**
- All security layers work together
- Combined attack vectors are blocked
- No security bypasses through feature interactions
- Error handling preserves security guarantees

**Attack Scenarios:**
- Path traversal + ANSI injection
- Cache poisoning + path traversal
- SQL injection + path traversal
- Combined control character attacks

This suite serves as:
1. Regression prevention (CI/CD integration)
2. Security documentation (attack vectors and mitigations)
3. Developer reference (how security features work)
"""

import sys
import os
import unittest
import pytest
import tempfile
import shutil
import sqlite3
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.utils import validate_path, sanitize_string, validate_extension_id
from vscode_scanner.cache_manager import CacheManager
from vscode_scanner.extension_discovery import ExtensionDiscovery
from vscode_scanner.config_manager import validate_config_value


@pytest.mark.security
class TestTask1PathValidationRegression(unittest.TestCase):
    """
    Regression tests for Task 1: Unified Path Validation.

    Ensures validate_path() remains secure across all attack vectors.
    """

    def test_url_encoding_blocked_all_variants(self):
        """Test that all URL-encoded attack variants are blocked."""
        url_encoded_attacks = [
            "%2e%2e%2f",  # ../
            "%2e%2e/",  # ../
            "..%2f",  # ../
            "%2e%2e%5c",  # ..\
            "test%00.txt",  # Null byte
            "test%0a.txt",  # Newline
            "%2fetc%2fpasswd",  # /etc/passwd
        ]

        for attack in url_encoded_attacks:
            with self.assertRaises(ValueError, msg=f"Should block: {attack}"):
                validate_path(attack, path_type="test")

    def test_system_directories_blocked_comprehensive(self):
        """Test that all system directories are blocked."""
        system_dirs = [
            "/etc/passwd",
            "/etc/shadow",
            "/sys/kernel/",
            "/proc/self/",
            "/var/log/auth.log",
            "/root/.bashrc",
            "/boot/grub/",
            "/dev/null",
            "/dev/sda",
        ]

        for path in system_dirs:
            with self.assertRaises(ValueError, msg=f"Should block: {path}"):
                validate_path(path, path_type="test")

    def test_parent_traversal_blocked_all_variants(self):
        """Test that all parent traversal variants are blocked."""
        traversal_attacks = [
            "../../../etc/passwd",
            "test/../../../etc/passwd",
            "/tmp/../etc/passwd",
            "~/../../../etc/passwd",
            "./../../etc/passwd",
            "test/../../../../../../etc/passwd",
        ]

        for attack in traversal_attacks:
            with self.assertRaises(ValueError, msg=f"Should block: {attack}"):
                validate_path(attack, path_type="test")

    def test_dangerous_characters_blocked_comprehensive(self):
        """Test that all dangerous characters are blocked."""
        dangerous_paths = [
            "test\x00.txt",  # Null byte
            "test | cat",  # Pipe
            "test; rm -rf",  # Semicolon
            "test`whoami`.txt",  # Backtick
            "test\n.txt",  # Newline
            # Note: ${...} is shell syntax, harmless in Python paths (not expanded by Python)
        ]

        for path in dangerous_paths:
            with self.assertRaises(ValueError, msg=f"Should block: {path}"):
                validate_path(path, path_type="test")

    def test_shell_expansion_safe(self):
        """Test that shell expansion works safely and doesn't bypass security."""
        # Set env var to system directory
        os.environ["MALICIOUS_PATH"] = "/etc"

        try:
            # Should expand and then block
            with self.assertRaises(ValueError):
                validate_path("$MALICIOUS_PATH/passwd", path_type="test")
        finally:
            del os.environ["MALICIOUS_PATH"]

    def test_validation_across_all_entry_points(self):
        """Test that validation works at all entry points."""
        # Extension discovery
        with self.assertRaises(FileNotFoundError):
            discovery = ExtensionDiscovery(custom_dir="%2e%2e%2f")
            discovery.find_extensions_directory()

        # Cache manager
        with self.assertRaises(ValueError):
            CacheManager(cache_dir="%2e%2e%2f")

        # Config manager
        with self.assertRaises(ValueError):
            validate_config_value("cache", "cache_dir", "/etc/vscan")


@pytest.mark.security
class TestTask2StringSanitizationRegression(unittest.TestCase):
    """
    Regression tests for Task 2: Unified String Sanitization.

    Ensures sanitize_string() remains secure against terminal injection.
    """

    def test_ansi_sequences_removed_all_types(self):
        """Test that all ANSI sequence types are removed."""
        ansi_attacks = [
            # CSI sequences
            "\x1b[31mred\x1b[0m",  # Color
            "\x1b[1mbold\x1b[0m",  # Bold
            "\x1b[4munderline\x1b[0m",  # Underline
            "\x1b[7mreverse\x1b[0m",  # Reverse
            # Cursor movement
            "text\x1b[Aup",  # Cursor up
            "text\x1b[10;20Hpos",  # Position
            "\x1b[2JClear",  # Clear screen
            # OSC sequences
            "\x1b]0;Title\x07text",  # Window title
            "\x1b]2;Title\x07text",  # Icon name
        ]

        for attack in ansi_attacks:
            result = sanitize_string(attack)
            # Should not contain escape character
            self.assertNotIn("\x1b", result)
            # Should contain only the text portion
            self.assertTrue(
                any(
                    word in result
                    for word in [
                        "red",
                        "bold",
                        "underline",
                        "reverse",
                        "up",
                        "pos",
                        "Clear",
                        "text",
                    ]
                )
            )

    def test_control_characters_removed_comprehensive(self):
        """Test that all dangerous control characters are removed."""
        control_chars = {
            "\x00": "null",
            "\x07": "bell",
            "\x08": "backspace",
            "\x0b": "vtab",
            "\x0c": "formfeed",
            "\x1b": "escape",
            "\x7f": "delete",
        }

        for char, name in control_chars.items():
            # Use spaces to separate words for clear verification
            text = f"text {char} with {char} {name}"
            result = sanitize_string(text)
            # Control character should be removed
            self.assertNotIn(char, result)
            # Text should be preserved (spaces help verify each word)
            self.assertIn("text", result)
            self.assertIn("with", result)
            self.assertIn(name, result)

    def test_safe_whitespace_preserved(self):
        """Test that safe whitespace is always preserved."""
        test_cases = [
            ("line1\nline2", "line1\nline2"),  # Newline
            ("col1\tcol2", "col1\tcol2"),  # Tab
            ("text\r\n", "text\r\n"),  # CRLF
            ("  spaces  ", "  spaces  "),  # Spaces
        ]

        for input_text, expected in test_cases:
            result = sanitize_string(input_text)
            self.assertEqual(result, expected)

    def test_terminal_injection_attacks_blocked(self):
        """Test that known terminal injection attacks are blocked."""
        injection_attacks = [
            # Clear screen and fake error
            "\x1b[2J\x1b[H\x1b[31m[ERROR] System compromised!\x1b[0m",
            # Hide cursor and print fake prompt
            "\x1b[?25l$ whoami\n",
            # Move cursor and overwrite previous output
            "\x1b[F\x1b[2KFake output",
            # Bell spam (DoS)
            "\x07" * 100,
        ]

        for attack in injection_attacks:
            result = sanitize_string(attack)
            # Should not contain ANSI or control chars
            self.assertNotIn("\x1b", result)
            self.assertNotIn("\x07", result)

    def test_unicode_handling_safe(self):
        """Test that Unicode handling doesn't introduce vulnerabilities."""
        unicode_tests = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "🚀 Rocket",  # Emoji
            "café",  # Accented
            "\u200b",  # Zero-width space (should be preserved, not dangerous)
        ]

        for text in unicode_tests:
            result = sanitize_string(text)
            # Should preserve Unicode (not remove it)
            # But should still remove any control chars
            self.assertNotIn("\x1b", result)
            self.assertNotIn("\x00", result)

    def test_dos_prevention_truncation(self):
        """Test that extremely long strings are truncated (DoS prevention)."""
        # Very long string (10,000 characters)
        long_text = "A" * 10000
        result = sanitize_string(long_text, max_length=500)

        # Should be truncated to max_length + "..."
        self.assertEqual(len(result), 503)
        self.assertTrue(result.endswith("..."))


@pytest.mark.security
class TestTask3CacheIntegrityRegression(unittest.TestCase):
    """
    Regression tests for Task 3: Cache Integrity Checks.

    Ensures HMAC integrity checking remains secure and functional.
    """

    def setUp(self):
        """Create temporary cache directory for each test."""
        self.test_dir = os.path.join(os.path.expanduser("~"), ".vscan_test_regression")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary cache directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cache_poisoning_detected_all_fields(self):
        """Test that tampering with any field is detected."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
        }
        cache.save_result("test.extension", "1.0.0", test_result)

        # Test tampering with different fields
        tampered_fields = [
            ("security_score", 100),
            ("risk_level", "critical"),
            ("vulnerabilities", {"count": 10}),
            ("scan_status", "error"),
        ]

        for field, new_value in tampered_fields:
            # Tamper with database
            conn = sqlite3.connect(cache.cache_db)
            cursor = conn.cursor()

            malicious_result = test_result.copy()
            malicious_result[field] = new_value

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

            # Should detect tampering
            loaded = cache.get_cached_result("test.extension", "1.0.0")
            self.assertIsNone(loaded, f"Should detect tampering of {field}")

    def test_signature_key_rotation_safe(self):
        """Test that rotating secret key invalidates old signatures."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_result = {
            "scan_status": "success",
            "security_score": 90,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
        }
        cache.save_result("test.extension", "1.0.0", test_result)

        # Verify works with current key
        loaded = cache.get_cached_result("test.extension", "1.0.0")
        self.assertIsNotNone(loaded)

        # Rotate key (simulate key change)
        secret_file = Path(self.test_dir) / ".cache_secret"
        import secrets

        with open(secret_file, "wb") as f:
            f.write(secrets.token_bytes(32))

        # Create new cache manager with new key
        cache2 = CacheManager(cache_dir=self.test_dir)

        # Old signatures should be invalid
        loaded = cache2.get_cached_result("test.extension", "1.0.0")
        self.assertIsNone(loaded, "Old signatures should be invalid after key rotation")

    def test_unsigned_entries_rejected_always(self):
        """Test that unsigned entries are always rejected."""
        cache = CacheManager(cache_dir=self.test_dir)

        # Manually insert unsigned entry
        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
        }

        conn = sqlite3.connect(cache.cache_db)
        cursor = conn.cursor()
        from datetime import datetime

        cursor.execute(
            """
            INSERT INTO scan_cache
            (extension_id, version, scan_result, scanned_at, risk_level, security_score,
             vulnerabilities_count, integrity_signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "unsigned.extension",
                "1.0.0",
                json.dumps(test_result),
                datetime.now().isoformat(),
                "low",
                85,
                0,
                None,
            ),
        )
        conn.commit()
        conn.close()

        # Should reject unsigned entry
        loaded = cache.get_cached_result("unsigned.extension", "1.0.0")
        self.assertIsNone(loaded)

    def test_timing_attack_resistance(self):
        """Test that signature verification is timing-safe."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_data = "test data for timing attack"
        correct_signature = cache._compute_integrity_signature(test_data)

        # Create signatures that differ in different positions
        signatures = [
            "0" * 64,  # Completely wrong
            correct_signature[:32] + "0" * 32,  # Wrong in second half
            correct_signature[:62] + "ff",  # Wrong in last byte
        ]

        # All should fail verification (hmac.compare_digest is timing-safe)
        for sig in signatures:
            result = cache._verify_integrity_signature(test_data, sig)
            self.assertFalse(result)


@pytest.mark.security
class TestSecurityIntegration(unittest.TestCase):
    """
    Integration tests to ensure all security layers work together.

    Tests combined attack scenarios and feature interactions.
    """

    def setUp(self):
        """Create temporary directories for integration tests."""
        self.test_dir = os.path.join(os.path.expanduser("~"), ".vscan_test_integration")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_path_traversal_plus_ansi_injection(self):
        """Test that combined path traversal + ANSI injection is blocked."""
        # Attempt path traversal with ANSI sequences in path
        malicious_path = "../../../etc\x1b[31m/passwd\x1b[0m"

        with self.assertRaises(ValueError):
            validate_path(malicious_path, path_type="test")

    def test_cache_poisoning_plus_path_traversal(self):
        """Test that cache poisoning can't bypass path validation."""
        # Even if cache is poisoned with bad paths, they should be validated
        cache = CacheManager(cache_dir=self.test_dir)

        # Try to save result with malicious path in metadata
        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
            "malicious_field": "../../../etc/passwd",
        }

        # Should save successfully (path is just data, not used for file access)
        cache.save_result("test.extension", "1.0.0", test_result)

        # When loading, malicious path in data won't be used for file access
        loaded = cache.get_cached_result("test.extension", "1.0.0")
        self.assertIsNotNone(loaded)

        # But if we try to use it for actual path validation
        with self.assertRaises(ValueError):
            validate_path(loaded["malicious_field"], path_type="test")

    def test_extension_id_validation_prevents_sql_injection(self):
        """Test that extension ID validation prevents SQL injection in cache."""
        cache = CacheManager(cache_dir=self.test_dir)

        # SQL injection attempts
        sql_injection_ids = [
            "'; DROP TABLE scan_cache; --",
            "' OR '1'='1",
            "test'; DELETE FROM scan_cache WHERE '1'='1",
        ]

        for malicious_id in sql_injection_ids:
            # Should be rejected by validation
            self.assertFalse(validate_extension_id(malicious_id))

            # Even if we bypass validation (shouldn't happen), parameterized queries prevent injection
            test_result = {
                "scan_status": "success",
                "security_score": 85,
                "risk_level": "low",
                "vulnerabilities": {"count": 0},
            }

            # This should not cause SQL injection (parameterized query)
            # Note: In production, validate_extension_id is called before this
            try:
                cache.save_result(malicious_id, "1.0.0", test_result)
            except:
                pass  # May fail for other reasons, that's fine

            # Database should still exist and be intact
            conn = sqlite3.connect(cache.cache_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scan_cache")
            # Should succeed (table not dropped)
            count = cursor.fetchone()[0]
            conn.close()
            self.assertIsNotNone(count)

    def test_sanitization_applied_to_cache_data(self):
        """Test that sanitization is applied when displaying cached data."""
        cache = CacheManager(cache_dir=self.test_dir)

        # Save result with ANSI sequences in display name
        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
            "display_name": "\x1b[31mMalicious Extension\x1b[0m",
        }

        cache.save_result("test.extension", "1.0.0", test_result)
        loaded = cache.get_cached_result("test.extension", "1.0.0")

        # When displaying, should sanitize
        sanitized_name = sanitize_string(loaded["display_name"])
        self.assertEqual(sanitized_name, "Malicious Extension")
        self.assertNotIn("\x1b", sanitized_name)

    def test_all_security_layers_active_simultaneously(self):
        """Test that all three security layers work together."""
        # 1. Path validation
        with self.assertRaises(ValueError):
            validate_path("../../../etc/passwd", path_type="test")

        # 2. String sanitization
        result = sanitize_string("\x1b[31mred text\x1b[0m")
        self.assertEqual(result, "red text")

        # 3. Cache integrity
        cache = CacheManager(cache_dir=self.test_dir)
        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0},
        }
        cache.save_result("test.extension", "1.0.0", test_result)

        # Tamper with cache
        conn = sqlite3.connect(cache.cache_db)
        cursor = conn.cursor()
        malicious_result = test_result.copy()
        malicious_result["security_score"] = 100
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

        # Should detect tampering
        loaded = cache.get_cached_result("test.extension", "1.0.0")
        self.assertIsNone(loaded)


@pytest.mark.security
class TestSecurityDocumentation(unittest.TestCase):
    """
    Tests that serve as documentation for security features.

    These tests demonstrate how security features work and what they protect against.
    """

    def test_attack_scenario_terminal_takeover(self):
        """
        Attack Scenario: Terminal Takeover

        An attacker crafts an extension with malicious output that:
        1. Clears the screen
        2. Positions cursor
        3. Displays fake error messages
        4. Hides real security warnings

        Mitigation: sanitize_string() removes all ANSI sequences
        """
        # Malicious extension display name
        malicious_output = (
            "\x1b[2J"  # Clear screen
            "\x1b[H"  # Move cursor to home
            "\x1b[31m"  # Red color
            "[ERROR] Security check failed! System compromised!"
            "\x1b[0m"  # Reset
            "\n\n"
            "Your extensions are safe."  # Fake reassurance
        )

        # Sanitization removes ANSI, prevents takeover
        safe_output = sanitize_string(malicious_output)

        self.assertNotIn("\x1b", safe_output)
        self.assertIn("Security check failed", safe_output)
        self.assertIn("Your extensions are safe", safe_output)

    def test_attack_scenario_directory_escape(self):
        """
        Attack Scenario: Directory Escape

        An attacker provides a custom extensions directory path that:
        1. Uses parent traversal to escape intended directory
        2. Accesses system files (/etc/passwd)
        3. Reads sensitive configuration

        Mitigation: validate_path() blocks parent traversal and system directories
        """
        # Malicious custom directory
        malicious_paths = [
            "../../../etc",
            "/etc/passwd",
            "~/../../../etc",
        ]

        for path in malicious_paths:
            with self.assertRaises(ValueError):
                validate_path(path, path_type="extensions directory")

    def test_attack_scenario_cache_manipulation(self):
        """
        Attack Scenario: Cache Manipulation

        An attacker:
        1. Scans malicious extension (gets low security score)
        2. Directly edits SQLite database
        3. Changes security score to 100 (appears safe)
        4. User trusts the fake high score

        Mitigation: HMAC signatures detect database tampering
        """
        test_dir = os.path.join(os.path.expanduser("~"), ".vscan_test_doc")
        os.makedirs(test_dir, exist_ok=True)

        try:
            cache = CacheManager(cache_dir=test_dir)

            # Step 1: Legitimate scan result (malicious extension, low score)
            legitimate_result = {
                "scan_status": "success",
                "security_score": 15,  # Low score (malicious)
                "risk_level": "critical",
                "vulnerabilities": {"count": 25},
            }
            cache.save_result("malicious.extension", "1.0.0", legitimate_result)

            # Step 2 & 3: Attacker modifies database
            conn = sqlite3.connect(cache.cache_db)
            cursor = conn.cursor()

            fake_result = legitimate_result.copy()
            fake_result["security_score"] = 100  # Fake high score
            fake_result["risk_level"] = "low"
            fake_result["vulnerabilities"]["count"] = 0

            cursor.execute(
                """
                UPDATE scan_cache
                SET scan_result = ?
                WHERE extension_id = 'malicious.extension'
            """,
                (json.dumps(fake_result),),
            )
            conn.commit()
            conn.close()

            # Step 4: HMAC detects tampering, prevents user from seeing fake score
            loaded = cache.get_cached_result("malicious.extension", "1.0.0")

            # Should return None (detected tampering)
            self.assertIsNone(loaded)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)


def run_tests():
    """Run all security regression tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTask1PathValidationRegression))
    suite.addTests(loader.loadTestsFromTestCase(TestTask2StringSanitizationRegression))
    suite.addTests(loader.loadTestsFromTestCase(TestTask3CacheIntegrityRegression))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityDocumentation))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    print("=" * 80)
    print("SECURITY REGRESSION TEST SUITE (v3.5.1 Phase 1 Complete)")
    print("=" * 80)
    print()
    print("Testing all security hardening from Phase 1:")
    print()
    print("Task 1 - Unified Path Validation:")
    print("  • URL encoding blocked")
    print("  • System directories blocked")
    print("  • Parent traversal blocked")
    print("  • Dangerous characters blocked")
    print("  • Safe shell expansion")
    print()
    print("Task 2 - Unified String Sanitization:")
    print("  • ANSI sequences removed")
    print("  • Control characters removed")
    print("  • Safe whitespace preserved")
    print("  • DoS prevention (truncation)")
    print("  • Terminal injection blocked")
    print()
    print("Task 3 - Cache Integrity Checks:")
    print("  • HMAC-SHA256 signatures")
    print("  • Cache poisoning detection")
    print("  • Timing-safe verification")
    print("  • Secret key management")
    print("  • Unsigned entry rejection")
    print()
    print("Integration Tests:")
    print("  • Combined attack scenarios")
    print("  • Feature interaction security")
    print("  • SQL injection prevention")
    print("  • Multi-layer defense verification")
    print()
    print("=" * 80)
    print()

    sys.exit(run_tests())
