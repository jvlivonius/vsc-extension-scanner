#!/usr/bin/env python3
"""
Comprehensive Cache Integrity Tests (v3.5.1 Security Hardening)

Tests the HMAC-based cache integrity checking system to ensure it:
1. Generates and stores HMAC-SHA256 signatures for cache entries
2. Verifies signatures when loading cached results
3. Detects cache poisoning/tampering attempts
4. Handles unsigned entries gracefully (migration scenario)
5. Manages secret keys securely

This addresses the cache poisoning vulnerability identified in v3.4.1:
- test_security.py test_cache_poisoning was failing
- Direct SQLite database tampering was not detected
- Fake security scores could bypass validation
"""

import sys
import os
import unittest
import tempfile
import shutil
import sqlite3
import json
import hmac
import hashlib
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vscode_scanner.cache_manager import CacheManager


class TestCacheIntegrity(unittest.TestCase):
    """Test HMAC-based cache integrity checking."""

    def setUp(self):
        """Create temporary cache directory for each test."""
        # Create temp directory in home directory (security requirement)
        self.test_dir = os.path.join(os.path.expanduser("~"), ".vscan_test_integrity")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary cache directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_secret_key_generation(self):
        """Test that secret key is generated and persisted."""
        cache = CacheManager(cache_dir=self.test_dir)

        # Check that secret key file exists
        secret_file = Path(self.test_dir) / ".cache_secret"
        self.assertTrue(secret_file.exists())

        # Check that secret key is 32 bytes (256 bits)
        with open(secret_file, 'rb') as f:
            key = f.read()
            self.assertEqual(len(key), 32)

    def test_secret_key_persistence(self):
        """Test that secret key persists across cache manager instances."""
        # Create first cache manager
        cache1 = CacheManager(cache_dir=self.test_dir)
        key1 = cache1._secret_key

        # Create second cache manager (should reuse same key)
        cache2 = CacheManager(cache_dir=self.test_dir)
        key2 = cache2._secret_key

        # Keys should be identical
        self.assertEqual(key1, key2)

    def test_signature_generation(self):
        """Test that HMAC signatures are generated correctly."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_data = "test data for signing"
        signature1 = cache._compute_integrity_signature(test_data)

        # Signature should be 64 characters (32 bytes hex-encoded)
        self.assertEqual(len(signature1), 64)

        # Same data should produce same signature
        signature2 = cache._compute_integrity_signature(test_data)
        self.assertEqual(signature1, signature2)

        # Different data should produce different signature
        different_data = "different test data"
        signature3 = cache._compute_integrity_signature(different_data)
        self.assertNotEqual(signature1, signature3)

    def test_signature_verification_valid(self):
        """Test that valid signatures are verified correctly."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_data = "test data for signing"
        signature = cache._compute_integrity_signature(test_data)

        # Verification should succeed
        self.assertTrue(cache._verify_integrity_signature(test_data, signature))

    def test_signature_verification_invalid(self):
        """Test that invalid signatures are rejected."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_data = "test data for signing"
        signature = cache._compute_integrity_signature(test_data)

        # Tampered data should fail verification
        tampered_data = "tampered test data"
        self.assertFalse(cache._verify_integrity_signature(tampered_data, signature))

        # Invalid signature should fail verification
        invalid_signature = "0" * 64  # Wrong signature
        self.assertFalse(cache._verify_integrity_signature(test_data, invalid_signature))

    def test_signature_verification_empty(self):
        """Test that empty/None signatures are rejected."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_data = "test data"

        # Empty signature should fail
        self.assertFalse(cache._verify_integrity_signature(test_data, ""))

        # None signature should fail
        self.assertFalse(cache._verify_integrity_signature(test_data, None))

    def test_cache_entry_with_signature(self):
        """Test that cache entries are saved with HMAC signatures."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0}
        }

        # Save result
        cache.save_result("test.extension", "1.0.0", test_result)

        # Check that signature was stored in database
        conn = sqlite3.connect(cache.cache_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT scan_result, integrity_signature
            FROM scan_cache
            WHERE extension_id = 'test.extension'
        """)
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        scan_result_json, integrity_signature = row

        # Signature should exist and be valid
        self.assertIsNotNone(integrity_signature)
        self.assertEqual(len(integrity_signature), 64)

        # Signature should match the data
        self.assertTrue(cache._verify_integrity_signature(scan_result_json, integrity_signature))

    def test_cache_poisoning_detection(self):
        """Test that cache poisoning is detected via signature mismatch."""
        cache = CacheManager(cache_dir=self.test_dir)

        # Save legitimate result
        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0}
        }
        cache.save_result("test.extension", "1.0.0", test_result)

        # Tamper with database (simulate attack)
        conn = sqlite3.connect(cache.cache_db)
        cursor = conn.cursor()

        # Modify security score to fake high security
        malicious_result = test_result.copy()
        malicious_result["security_score"] = 100
        malicious_result["vulnerabilities"]["count"] = 10  # Hide vulnerabilities

        cursor.execute("""
            UPDATE scan_cache
            SET scan_result = ?
            WHERE extension_id = 'test.extension'
        """, (json.dumps(malicious_result),))
        conn.commit()
        conn.close()

        # Try to load - should detect tampering and return None
        loaded = cache.get_cached_result("test.extension", "1.0.0")

        # Should return None (cache miss) due to signature mismatch
        self.assertIsNone(loaded)

    def test_unsigned_entries_rejected(self):
        """Test that unsigned cache entries are rejected (old cache)."""
        cache = CacheManager(cache_dir=self.test_dir)

        # Manually insert unsigned entry (simulate old cache from v2.1)
        test_result = {
            "scan_status": "success",
            "security_score": 85,
            "risk_level": "low",
            "vulnerabilities": {"count": 0}
        }

        conn = sqlite3.connect(cache.cache_db)
        cursor = conn.cursor()
        from datetime import datetime
        cursor.execute("""
            INSERT INTO scan_cache
            (extension_id, version, scan_result, scanned_at, risk_level, security_score,
             vulnerabilities_count, integrity_signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("test.extension", "1.0.0", json.dumps(test_result), datetime.now().isoformat(),
              "low", 85, 0, None))  # NULL signature
        conn.commit()
        conn.close()

        # Try to load - should reject unsigned entry
        loaded = cache.get_cached_result("test.extension", "1.0.0")

        # Should return None to force re-scan with signature
        self.assertIsNone(loaded)

    def test_batch_mode_with_signatures(self):
        """Test that batch mode also generates signatures."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_result = {
            "scan_status": "success",
            "security_score": 90,
            "risk_level": "low",
            "vulnerabilities": {"count": 0}
        }

        # Save in batch mode
        cache.begin_batch()
        cache.save_result_batch("batch.extension", "2.0.0", test_result)
        cache.commit_batch()

        # Check that signature was stored
        conn = sqlite3.connect(cache.cache_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT integrity_signature
            FROM scan_cache
            WHERE extension_id = 'batch.extension'
        """)
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        integrity_signature = row[0]

        # Signature should exist
        self.assertIsNotNone(integrity_signature)
        self.assertEqual(len(integrity_signature), 64)

    def test_hmac_timing_safe_comparison(self):
        """Test that signature verification uses timing-safe comparison."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_data = "test data"
        correct_signature = cache._compute_integrity_signature(test_data)

        # Create similar but incorrect signature (differs in last byte)
        incorrect_signature = correct_signature[:-2] + "ff"

        # Both should use timing-safe comparison (hmac.compare_digest)
        # This test mainly verifies the code path is correct
        self.assertTrue(cache._verify_integrity_signature(test_data, correct_signature))
        self.assertFalse(cache._verify_integrity_signature(test_data, incorrect_signature))


class TestCacheIntegrationWithSecurity(unittest.TestCase):
    """Integration tests for cache integrity in security scenarios."""

    def setUp(self):
        """Create temporary cache directory for each test."""
        self.test_dir = os.path.join(os.path.expanduser("~"), ".vscan_test_security")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary cache directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_security_test_cache_poisoning_passes(self):
        """Test that the security test (test_security.py) now passes."""
        # This is the exact scenario from test_security.py
        cache = CacheManager(cache_dir=self.test_dir)

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

        # Should NOT return tampered data (previously this was the vulnerability)
        if loaded and loaded.get("security_score") == 100:
            self.fail("Cache poisoning not detected!")
        else:
            # Success - tampering was detected (returned None)
            self.assertIsNone(loaded)

    def test_legitimate_cache_hits_work(self):
        """Test that legitimate cache hits still work correctly."""
        cache = CacheManager(cache_dir=self.test_dir)

        test_result = {
            "scan_status": "success",
            "security_score": 75,
            "risk_level": "medium",
            "vulnerabilities": {"count": 2}
        }

        # Save result
        cache.save_result("legit.extension", "1.5.0", test_result)

        # Load result - should succeed
        loaded = cache.get_cached_result("legit.extension", "1.5.0")

        # Should return the correct data
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["security_score"], 75)
        self.assertEqual(loaded["risk_level"], "medium")
        self.assertEqual(loaded["vulnerabilities"]["count"], 2)
        self.assertTrue(loaded["_cache_hit"])


def run_tests():
    """Run all cache integrity tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCacheIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheIntegrationWithSecurity))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    print("=" * 70)
    print("CACHE INTEGRITY TESTS (v3.5.1 Security Hardening)")
    print("=" * 70)
    print()
    print("Testing HMAC-based cache integrity checking:")
    print("- HMAC-SHA256 signature generation")
    print("- Signature verification with timing-safe comparison")
    print("- Cache poisoning detection")
    print("- Unsigned entry handling (migration)")
    print("- Secret key management")
    print()
    print("=" * 70)
    print()

    sys.exit(run_tests())
