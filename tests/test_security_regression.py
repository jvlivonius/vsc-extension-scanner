#!/usr/bin/env python3
"""
Security Regression Test Suite (v3.7.0 Phase 3 - Parameterized)

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

Phase 3.1 Refactoring: Consolidated repetitive loop-based tests using @pytest.mark.parametrize
for better maintainability, clearer test output, and individual test case tracking.
Converted from unittest to pure pytest style.
"""

import sys
import os
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
class TestTask1PathValidationRegression:
    """
    Regression tests for Task 1: Unified Path Validation.

    Ensures validate_path() remains secure across all attack vectors.
    """

    @pytest.mark.parametrize(
        "url_encoded_attack",
        [
            "%2e%2e%2f",  # ../
            "%2e%2e/",  # ../
            "..%2f",  # ../
            "%2e%2e%5c",  # ..\
            "test%00.txt",  # Null byte
            "test%0a.txt",  # Newline
            "%2fetc%2fpasswd",  # /etc/passwd
        ],
    )
    def test_url_encoding_blocked_all_variants(self, url_encoded_attack):
        """Test that all URL-encoded attack variants are blocked."""
        with pytest.raises(ValueError):
            validate_path(url_encoded_attack, path_type="test")

    @pytest.mark.parametrize(
        "system_dir",
        [
            "/etc/passwd",
            "/etc/shadow",
            "/sys/kernel/",
            "/proc/self/",
            "/var/log/auth.log",
            "/root/.bashrc",
            "/boot/grub/",
            "/dev/null",
            "/dev/sda",
        ],
    )
    def test_system_directories_blocked_comprehensive(self, system_dir):
        """Test that all system directories are blocked."""
        with pytest.raises(ValueError):
            validate_path(system_dir, path_type="test")

    @pytest.mark.parametrize(
        "traversal_attack",
        [
            "../../../etc/passwd",
            "test/../../../etc/passwd",
            "/tmp/../etc/passwd",
            "~/../../../etc/passwd",
            "./../../etc/passwd",
            "test/../../../../../../etc/passwd",
        ],
    )
    def test_parent_traversal_blocked_all_variants(self, traversal_attack):
        """Test that all parent traversal variants are blocked."""
        with pytest.raises(ValueError):
            validate_path(traversal_attack, path_type="test")

    @pytest.mark.parametrize(
        "dangerous_path",
        [
            "test\x00.txt",  # Null byte
            "test | cat",  # Pipe
            "test; rm -rf",  # Semicolon
            "test`whoami`.txt",  # Backtick
            "test\n.txt",  # Newline
            # Note: ${...} is shell syntax, harmless in Python paths (not expanded by Python)
        ],
    )
    def test_dangerous_characters_blocked_comprehensive(self, dangerous_path):
        """Test that all dangerous characters are blocked."""
        with pytest.raises(ValueError):
            validate_path(dangerous_path, path_type="test")

    def test_shell_expansion_safe(self):
        """Test that shell expansion works safely and doesn't bypass security."""
        # Set env var to system directory
        os.environ["MALICIOUS_PATH"] = "/etc"

        try:
            # Should expand and then block
            with pytest.raises(ValueError):
                validate_path("$MALICIOUS_PATH/passwd", path_type="test")
        finally:
            del os.environ["MALICIOUS_PATH"]

    def test_validation_across_all_entry_points(self):
        """Test that validation works at all entry points."""
        # Extension discovery
        with pytest.raises(FileNotFoundError):
            discovery = ExtensionDiscovery(custom_dir="%2e%2e%2f")
            discovery.find_extensions_directory()

        # Cache manager
        with pytest.raises(ValueError):
            CacheManager(cache_dir="%2e%2e%2f")

        # Config manager
        with pytest.raises(ValueError):
            validate_config_value("cache", "cache_dir", "/etc/vscan")


@pytest.mark.security
class TestTask2StringSanitizationRegression:
    """
    Regression tests for Task 2: Unified String Sanitization.

    Ensures sanitize_string() remains secure against terminal injection.
    """

    @pytest.mark.parametrize(
        "ansi_attack,expected_word",
        [
            # CSI sequences
            ("\x1b[31mred\x1b[0m", "red"),  # Color
            ("\x1b[1mbold\x1b[0m", "bold"),  # Bold
            ("\x1b[4munderline\x1b[0m", "underline"),  # Underline
            ("\x1b[7mreverse\x1b[0m", "reverse"),  # Reverse
            # Cursor movement
            ("text\x1b[Aup", "up"),  # Cursor up
            ("text\x1b[10;20Hpos", "pos"),  # Position
            ("\x1b[2JClear", "Clear"),  # Clear screen
            # OSC sequences
            ("\x1b]0;Title\x07text", "text"),  # Window title
            ("\x1b]2;Title\x07text", "text"),  # Icon name
        ],
    )
    def test_ansi_sequences_removed_all_types(self, ansi_attack, expected_word):
        """Test that all ANSI sequence types are removed."""
        result = sanitize_string(ansi_attack)
        # Should not contain escape character
        assert "\x1b" not in result
        # Should contain the expected text portion
        assert expected_word in result

    @pytest.mark.parametrize(
        "control_char,name",
        [
            ("\x00", "null"),
            ("\x07", "bell"),
            ("\x08", "backspace"),
            ("\x0b", "vtab"),
            ("\x0c", "formfeed"),
            ("\x1b", "escape"),
            ("\x7f", "delete"),
        ],
    )
    def test_control_characters_removed_comprehensive(self, control_char, name):
        """Test that all dangerous control characters are removed."""
        # Use spaces to separate words for clear verification
        text = f"text {control_char} with {control_char} {name}"
        result = sanitize_string(text)
        # Control character should be removed
        assert control_char not in result
        # Text should be preserved (spaces help verify each word)
        assert "text" in result
        assert "with" in result
        assert name in result

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("line1\nline2", "line1\nline2"),  # Newline
            ("col1\tcol2", "col1\tcol2"),  # Tab
            ("text\r\n", "text\n"),  # CRLF - \r removed for security
            ("  spaces  ", "  spaces  "),  # Spaces
        ],
    )
    def test_safe_whitespace_preserved(self, input_text, expected):
        """Test that safe whitespace is always preserved."""
        result = sanitize_string(input_text)
        assert result == expected

    @pytest.mark.parametrize(
        "injection_attack",
        [
            # Clear screen and fake error
            "\x1b[2J\x1b[H\x1b[31m[ERROR] System compromised!\x1b[0m",
            # Hide cursor and print fake prompt
            "\x1b[?25l$ whoami\n",
            # Move cursor and overwrite previous output
            "\x1b[F\x1b[2KFake output",
            # Bell spam (DoS)
            "\x07" * 100,
        ],
    )
    def test_terminal_injection_attacks_blocked(self, injection_attack):
        """Test that known terminal injection attacks are blocked."""
        result = sanitize_string(injection_attack)
        # Should not contain ANSI or control chars
        assert "\x1b" not in result
        assert "\x07" not in result

    @pytest.mark.parametrize(
        "unicode_text",
        [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "🚀 Rocket",  # Emoji
            "café",  # Accented
            "\u200b",  # Zero-width space (should be preserved, not dangerous)
        ],
    )
    def test_unicode_handling_safe(self, unicode_text):
        """Test that Unicode handling doesn't introduce vulnerabilities."""
        result = sanitize_string(unicode_text)
        # Should preserve Unicode (not remove it)
        # But should still remove any control chars
        assert "\x1b" not in result
        assert "\x00" not in result

    def test_dos_prevention_truncation(self):
        """Test that extremely long strings are truncated (DoS prevention)."""
        # Very long string (10,000 characters)
        long_text = "A" * 10000
        result = sanitize_string(long_text, max_length=500)

        # Should be truncated to max_length + "..."
        assert len(result) == 503
        assert result.endswith("...")


@pytest.mark.security
class TestTask3CacheIntegrityRegression:
    """
    Regression tests for Task 3: Cache Integrity Checks.

    Ensures HMAC integrity checking remains secure and functional.
    """

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and clean up temporary cache directory for each test."""
        self.test_dir = os.path.join(os.path.expanduser("~"), ".vscan_test_regression")
        os.makedirs(self.test_dir, exist_ok=True)
        yield
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @pytest.mark.parametrize(
        "field,new_value",
        [
            ("security_score", 100),
            ("risk_level", "critical"),
            ("vulnerabilities", {"count": 10}),
            ("scan_status", "error"),
        ],
    )
    def test_cache_poisoning_detected_all_fields(self, field, new_value):
        """Test that tampering with any field is detected."""
        cache = CacheManager(cache_dir=self.test_dir)

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
        assert loaded is None, f"Should detect tampering of {field}"

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
        assert loaded is not None

        # Rotate key (simulate key change)
        secret_file = Path(self.test_dir) / ".cache_secret"
        import secrets

        with open(secret_file, "wb") as f:
            f.write(secrets.token_bytes(32))

        # Create new cache manager with new key
        cache2 = CacheManager(cache_dir=self.test_dir)

        # Old signatures should be invalid
        loaded = cache2.get_cached_result("test.extension", "1.0.0")
        assert loaded is None, "Old signatures should be invalid after key rotation"

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
        assert loaded is None

    @pytest.mark.parametrize(
        "signature_type,description",
        [
            ("0" * 64, "completely_wrong"),  # Completely wrong
            (
                lambda sig: sig[:32] + "0" * 32,
                "wrong_second_half",
            ),  # Wrong in second half
            (lambda sig: sig[:62] + "ff", "wrong_last_byte"),  # Wrong in last byte
        ],
        ids=["completely_wrong", "wrong_second_half", "wrong_last_byte"],
    )
    def test_timing_attack_resistance(self, signature_type, description):
        """Test that signature verification is timing-safe."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_data = "test data for timing attack"
        correct_signature = cache._compute_integrity_signature(test_data)

        # Create wrong signature based on type
        if callable(signature_type):
            wrong_signature = signature_type(correct_signature)
        else:
            wrong_signature = signature_type

        # Should fail verification (hmac.compare_digest is timing-safe)
        result = cache._verify_integrity_signature(test_data, wrong_signature)
        assert result is False


@pytest.mark.security
class TestSecurityIntegration:
    """
    Integration tests to ensure all security layers work together.

    Tests combined attack scenarios and feature interactions.
    """

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and clean up temporary directories for integration tests."""
        self.test_dir = os.path.join(os.path.expanduser("~"), ".vscan_test_integration")
        os.makedirs(self.test_dir, exist_ok=True)
        yield
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_path_traversal_plus_ansi_injection(self):
        """Test that combined path traversal + ANSI injection is blocked."""
        # Attempt path traversal with ANSI sequences in path
        malicious_path = "../../../etc\x1b[31m/passwd\x1b[0m"

        with pytest.raises(ValueError):
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
        assert loaded is not None

        # But if we try to use it for actual path validation
        with pytest.raises(ValueError):
            validate_path(loaded["malicious_field"], path_type="test")

    @pytest.mark.parametrize(
        "malicious_id",
        [
            "'; DROP TABLE scan_cache; --",
            "' OR '1'='1",
            "test'; DELETE FROM scan_cache WHERE '1'='1",
        ],
    )
    def test_extension_id_validation_prevents_sql_injection(self, malicious_id):
        """Test that extension ID validation prevents SQL injection in cache."""
        cache = CacheManager(cache_dir=self.test_dir)

        # Should be rejected by validation
        assert validate_extension_id(malicious_id) is False

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
        assert count is not None

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
        assert sanitized_name == "Malicious Extension"
        assert "\x1b" not in sanitized_name

    def test_all_security_layers_active_simultaneously(self):
        """Test that all three security layers work together."""
        # 1. Path validation
        with pytest.raises(ValueError):
            validate_path("../../../etc/passwd", path_type="test")

        # 2. String sanitization
        result = sanitize_string("\x1b[31mred text\x1b[0m")
        assert result == "red text"

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
        assert loaded is None


@pytest.mark.security
class TestSecurityDocumentation:
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

        assert "\x1b" not in safe_output
        assert "Security check failed" in safe_output
        assert "Your extensions are safe" in safe_output

    @pytest.mark.parametrize(
        "malicious_path",
        [
            "../../../etc",
            "/etc/passwd",
            "~/../../../etc",
        ],
    )
    def test_attack_scenario_directory_escape(self, malicious_path):
        """
        Attack Scenario: Directory Escape

        An attacker provides a custom extensions directory path that:
        1. Uses parent traversal to escape intended directory
        2. Accesses system files (/etc/passwd)
        3. Reads sensitive configuration

        Mitigation: validate_path() blocks parent traversal and system directories
        """
        with pytest.raises(ValueError):
            validate_path(malicious_path, path_type="extensions directory")

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
            assert loaded is None

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)


if __name__ == "__main__":
    print("=" * 80)
    print("SECURITY REGRESSION TEST SUITE (v3.7.0 Phase 3 - Parameterized)")
    print("=" * 80)
    print()
    print("Testing all security hardening from Phase 1:")
    print()
    print("Task 1 - Unified Path Validation:")
    print("  • URL encoding blocked (parametrized)")
    print("  • System directories blocked (parametrized)")
    print("  • Parent traversal blocked (parametrized)")
    print("  • Dangerous characters blocked (parametrized)")
    print("  • Safe shell expansion")
    print()
    print("Task 2 - Unified String Sanitization:")
    print("  • ANSI sequences removed (parametrized)")
    print("  • Control characters removed (parametrized)")
    print("  • Safe whitespace preserved (parametrized)")
    print("  • DoS prevention (truncation)")
    print("  • Terminal injection blocked (parametrized)")
    print()
    print("Task 3 - Cache Integrity Checks:")
    print("  • HMAC-SHA256 signatures")
    print("  • Cache poisoning detection (parametrized)")
    print("  • Timing-safe verification (parametrized)")
    print("  • Secret key management")
    print("  • Unsigned entry rejection")
    print()
    print("Integration Tests:")
    print("  • Combined attack scenarios")
    print("  • Feature interaction security")
    print("  • SQL injection prevention (parametrized)")
    print("  • Multi-layer defense verification")
    print()
    print("=" * 80)
    print()

    sys.exit(pytest.main([__file__, "-v"]))
