#!/usr/bin/env python3
"""
Cache Manager for VS Code Extension Security Scanner

Manages SQLite-based caching of scan results to improve performance
for unchanged extensions.
"""

import sys
import sqlite3
import json
import time
import hmac
import hashlib
import secrets
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from datetime import datetime, timedelta

from .utils import (
    is_restricted_path,
    is_temp_directory,
    safe_mkdir,
    safe_touch,
    safe_chmod,
    sanitize_error_message,
    validate_path,
)
from ._version import SCHEMA_VERSION
from .constants import DEFAULT_CACHE_MAX_AGE_DAYS, CACHE_REPORT_MAX_AGE_DAYS
from .types import CacheWarning, CacheError, CacheInfo


class CacheManager:
    """Manages caching of extension scan results using SQLite."""

    SCHEMA_VERSION = SCHEMA_VERSION

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache database. Defaults to ~/.vscan/
        """
        # Batch commit support
        self._batch_connection = None
        self._batch_cursor = None
        self._batch_count = 0

        # Initialization messages (warnings, errors, info from setup)
        self._init_messages = []
        if cache_dir:
            # Validate cache directory using unified validation (v3.5.1)
            # Blocks: URL encoding, dangerous chars, parent traversal, system directories
            # Expands: shell variables (~/, $HOME/, $USER/)
            try:
                validate_path(
                    cache_dir, allow_absolute=True, path_type="cache directory"
                )
            except ValueError as e:
                raise ValueError(f"[E200] {str(e)}")

            # Expand and resolve path (validation already expanded for checking)
            import os

            expanded = os.path.expandvars(os.path.expanduser(cache_dir))
            cache_path = Path(expanded).resolve()

            self.cache_dir = cache_path
        else:
            self.cache_dir = Path.home() / ".vscan"

        self.cache_db = self.cache_dir / "cache.db"

        # Verify database integrity if it exists
        if self.cache_db.exists():
            if not self._verify_database_integrity():
                self._init_messages.extend(self._handle_corrupted_database())

        # Check if migration is needed before init
        if self.cache_db.exists():
            current_version = self._get_schema_version()

            if current_version == "1.0":
                # Migrate from v1.0 to v2.0
                self._migrate_v1_to_v2()
                # Then migrate from v2.0 to v2.1
                self._migrate_v2_0_to_v2_1()
                # Then migrate from v2.1 to v2.2
                self._migrate_v2_1_to_v2_2()
            elif current_version == "2.0":
                # Migrate from v2.0 to v2.1
                self._migrate_v2_0_to_v2_1()
                # Then migrate from v2.1 to v2.2
                self._migrate_v2_1_to_v2_2()
            elif current_version == "2.1":
                # Migrate from v2.1 to v2.2
                self._migrate_v2_1_to_v2_2()
            elif current_version == "2.2":
                # Already at latest version
                pass
            else:
                # Unknown version, init fresh
                self._init_database()
        else:
            self._init_database()

        # Initialize secret key for HMAC integrity checking (v3.5.1)
        self._secret_key = self._get_or_create_secret_key()

    def _get_or_create_secret_key(self) -> bytes:
        """
        Get or create secret key for HMAC integrity checking.

        The secret key is stored in ~/.vscan/.cache_secret with restrictive permissions
        (0o600, user-only read/write). If the file doesn't exist, generates a new
        cryptographically secure 32-byte key using secrets.token_bytes().

        Returns:
            bytes: 32-byte secret key for HMAC computation

        Security:
            - Uses secrets module for cryptographically secure random generation
            - File permissions restricted to user-only (0o600)
            - Key is 256 bits (32 bytes) for HMAC-SHA256
        """
        secret_file = self.cache_dir / ".cache_secret"

        try:
            if secret_file.exists():
                # Load existing key
                with open(secret_file, "rb") as f:
                    key = f.read()
                    if len(key) == 32:
                        return key
                    else:
                        # Invalid key size, regenerate
                        print(
                            "[WARNING] Invalid cache secret key, regenerating...",
                            file=sys.stderr,
                        )

            # Generate new key
            key = secrets.token_bytes(32)  # 256 bits for HMAC-SHA256

            # Write with restrictive permissions
            safe_touch(secret_file, mode=0o600)
            with open(secret_file, "wb") as f:
                f.write(key)

            return key

        except (OSError, IOError) as e:
            # Fallback to in-memory key (warnings only, don't fail)
            sanitized_error = sanitize_error_message(str(e), context="secret key")
            print(
                f"[WARNING] Failed to persist cache secret key: {sanitized_error}",
                file=sys.stderr,
            )
            print(
                "[WARNING] Using in-memory key (integrity checks won't persist across restarts)",
                file=sys.stderr,
            )
            return secrets.token_bytes(32)

    def _compute_integrity_signature(self, data: str) -> str:
        """
        Compute HMAC-SHA256 signature for cache integrity checking.

        Args:
            data: String data to sign (typically JSON-serialized scan result)

        Returns:
            str: Hex-encoded HMAC-SHA256 signature

        Security:
            - Uses HMAC-SHA256 for cryptographic integrity
            - Secret key is user-specific and stored with restrictive permissions
            - Signatures are 64 characters (32 bytes hex-encoded)
        """
        signature = hmac.new(self._secret_key, data.encode("utf-8"), hashlib.sha256)
        return signature.hexdigest()

    def _verify_integrity_signature(self, data: str, signature: str) -> bool:
        """
        Verify HMAC-SHA256 signature for cache integrity checking.

        Args:
            data: String data to verify (typically JSON-serialized scan result)
            signature: Hex-encoded HMAC-SHA256 signature to verify against

        Returns:
            bool: True if signature is valid, False otherwise

        Security:
            - Uses hmac.compare_digest() for timing-safe comparison
            - Prevents timing attacks that could leak signature information
        """
        if not signature:
            return False

        try:
            expected_signature = self._compute_integrity_signature(data)
            # Use timing-safe comparison to prevent timing attacks
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False

    def get_init_messages(self) -> List[Union[CacheWarning, CacheError, CacheInfo]]:
        """
        Get initialization messages (warnings, errors, info) from cache setup.

        Returns:
            List of CacheWarning, CacheError, and CacheInfo objects from initialization

        Example:
            cache_mgr = CacheManager()
            messages = cache_mgr.get_init_messages()
            for msg in messages:
                if isinstance(msg, CacheWarning):
                    display_warning(msg.message)
                elif isinstance(msg, CacheError):
                    display_error(msg.message)
                elif isinstance(msg, CacheInfo):
                    display_info(msg.message)
        """
        return self._init_messages

    @contextmanager
    def _db_connection(self):
        """
        Context manager for database connections.
        Provides automatic connection management with proper cleanup.

        Yields:
            sqlite3.Connection: Database connection

        Example:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM scan_cache")
                # Connection automatically closed on exit
        """
        conn = sqlite3.connect(self.cache_db)
        try:
            yield conn
        finally:
            conn.close()

    def _verify_database_integrity(self) -> bool:
        """
        Verify database integrity using SQLite's built-in integrity check.

        Returns:
            True if database is intact, False if corrupted
        """
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()

            # integrity_check returns "ok" if everything is fine
            # or a list of errors if there are problems
            if result and result[0] == "ok":
                return True
            else:
                sanitized_result = sanitize_error_message(
                    str(result), context="integrity check"
                )
                print(
                    f"[WARNING] Cache database integrity check failed: {sanitized_result}",
                    file=sys.stderr,
                )
                return False

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="integrity check")
            print(
                f"[WARNING] Cache database integrity check error: {sanitized_error}",
                file=sys.stderr,
            )
            return False

    def _handle_corrupted_database(
        self,
    ) -> List[Union[CacheWarning, CacheError, CacheInfo]]:
        """
        Handle corrupted database by backing it up and creating a fresh one.

        Returns:
            List of CacheWarning, CacheError, and CacheInfo objects describing the recovery process
        """
        import shutil

        messages = []
        messages.append(
            CacheWarning(
                message="Detected corrupted cache database",
                context="database_integrity",
            )
        )

        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.cache_db.parent / f"cache.db.corrupted.{timestamp}"

            messages.append(
                CacheInfo(
                    message=f"Backing up corrupted database to: {backup_path}",
                    context="database_backup",
                )
            )
            shutil.copy2(self.cache_db, backup_path)

            # Remove corrupted database
            messages.append(
                CacheInfo(
                    message="Removing corrupted database...", context="database_cleanup"
                )
            )
            self.cache_db.unlink()

            messages.append(
                CacheInfo(
                    message="Creating fresh cache database...",
                    context="database_recovery",
                )
            )

        except (OSError, IOError) as e:
            sanitized_error = sanitize_error_message(str(e), context="database backup")
            messages.append(
                CacheError(
                    message=f"Failed to handle corrupted database: {sanitized_error}",
                    context="database_recovery",
                    recoverable=False,
                )
            )
            messages.append(
                CacheInfo(
                    message="Cache functionality may be impaired",
                    context="database_recovery",
                )
            )

        return messages

    def _init_database(self):
        """Initialize SQLite database with schema v2.1."""
        # Create cache directory with restricted permissions (user-only)
        # Uses cross-platform safe_mkdir that handles Windows/Unix differences
        safe_mkdir(self.cache_dir, mode=0o700)

        # Ensure database file has restrictive permissions
        # Uses cross-platform safe functions that handle Windows/Unix differences
        if not self.cache_db.exists():
            safe_touch(self.cache_db, mode=0o600)
        else:
            # Update permissions on existing database
            safe_chmod(self.cache_db, 0o600)

        with self._db_connection() as conn:
            cursor = conn.cursor()

            # Create scan_cache table (v2.2 schema with integrity_signature field)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS scan_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extension_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    scan_result TEXT NOT NULL,
                    scanned_at TIMESTAMP NOT NULL,
                    risk_level TEXT,
                    security_score INTEGER,
                    vulnerabilities_count INTEGER DEFAULT 0,
                    dependencies_count INTEGER DEFAULT 0,
                    publisher_verified BOOLEAN DEFAULT 0,
                    has_risk_factors BOOLEAN DEFAULT 0,
                    installed_at TIMESTAMP,
                    integrity_signature TEXT,
                    UNIQUE(extension_id, version)
                )
            """
            )

            # Create metadata table for schema version and stats
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """
            )

            # Create indexes for performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_extension
                ON scan_cache(extension_id, version)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_scanned_at
                ON scan_cache(scanned_at)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_risk_level
                ON scan_cache(risk_level)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_security_score
                ON scan_cache(security_score)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_vulnerabilities
                ON scan_cache(vulnerabilities_count)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_publisher_verified
                ON scan_cache(publisher_verified)
            """
            )

            # Store schema version
            cursor.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("schema_version", self.SCHEMA_VERSION),
            )

            conn.commit()

    def _check_if_migration_needed(self) -> bool:
        """Check if database exists and needs migration."""
        if not self.cache_db.exists():
            return False  # New database, no migration needed

        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Check if scan_cache table exists
                cursor.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='scan_cache'
                """
                )
                if not cursor.fetchone():
                    return False  # No table yet, fresh install

                # Check if new columns exist
                cursor.execute("PRAGMA table_info(scan_cache)")
                columns = {row[1] for row in cursor.fetchall()}

                # If security_score column doesn't exist, we need migration
                return "security_score" not in columns

        except sqlite3.Error:
            return False

    def _get_schema_version(self) -> str:
        """Get current schema version from database."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT value FROM metadata WHERE key = 'schema_version'"
                )
                row = cursor.fetchone()
                return row[0] if row else "1.0"  # Default to 1.0 if not found
        except sqlite3.Error:
            return "1.0"  # If table doesn't exist, assume v1

    def _process_migration_batch(self, cursor, batch: List[Tuple]):
        """
        Process a batch of migration updates.

        Args:
            cursor: Database cursor
            batch: List of tuples (security_score, dependencies_count, publisher_verified, has_risk_factors, row_id)
        """
        cursor.executemany(
            """
            UPDATE scan_cache
            SET security_score = ?,
                dependencies_count = ?,
                publisher_verified = ?,
                has_risk_factors = ?
            WHERE id = ?
        """,
            batch,
        )

    def _migrate_v1_to_v2(self):
        """Migrate cache database from v1.0 to v2.0 schema."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Check if we need to migrate (check for missing columns)
                cursor.execute("PRAGMA table_info(scan_cache)")
                columns = {row[1] for row in cursor.fetchall()}

                if "security_score" in columns:
                    # Already migrated
                    return

                # Add new columns to existing table
                cursor.execute(
                    """
                    ALTER TABLE scan_cache
                    ADD COLUMN security_score INTEGER
                """
                )
                cursor.execute(
                    """
                    ALTER TABLE scan_cache
                    ADD COLUMN dependencies_count INTEGER DEFAULT 0
                """
                )
                cursor.execute(
                    """
                    ALTER TABLE scan_cache
                    ADD COLUMN publisher_verified BOOLEAN DEFAULT 0
                """
                )
                cursor.execute(
                    """
                    ALTER TABLE scan_cache
                    ADD COLUMN has_risk_factors BOOLEAN DEFAULT 0
                """
                )

                # Create new indexes
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_security_score
                    ON scan_cache(security_score)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_vulnerabilities
                    ON scan_cache(vulnerabilities_count)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_publisher_verified
                    ON scan_cache(publisher_verified)
                """
                )

                # Update existing rows with parsed data from scan_result JSON
                # Use batch processing to avoid loading all entries into memory
                cursor.execute("SELECT COUNT(*) FROM scan_cache")
                total_rows = cursor.fetchone()[0]

                if total_rows > 0:
                    print(f"Migrating cache schema (v1.0 → v2.0)...")
                    print(f"Processing {total_rows} cached entries...")

                updated_count = 0
                batch = []
                batch_size = 100

                # Process entries using cursor as iterator (not fetchall)
                cursor.execute("SELECT id, scan_result FROM scan_cache")
                for idx, (row_id, scan_result_json) in enumerate(cursor, 1):
                    try:
                        result = json.loads(scan_result_json)

                        # Extract new fields from result
                        security_score = result.get("security_score")
                        dependencies = result.get("dependencies", {})
                        dependencies_count = dependencies.get("total_count", 0)
                        metadata = result.get("metadata", {})
                        publisher = metadata.get("publisher", {})
                        publisher_verified = 1 if publisher.get("verified") else 0
                        risk_factors = result.get("risk_factors", [])
                        has_risk_factors = 1 if len(risk_factors) > 0 else 0

                        # Add to batch
                        batch.append(
                            (
                                security_score,
                                dependencies_count,
                                publisher_verified,
                                has_risk_factors,
                                row_id,
                            )
                        )

                        # Process batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            self._process_migration_batch(cursor, batch)
                            updated_count += len(batch)
                            batch = []

                        # Show progress every 10 entries or at the end
                        if idx % 10 == 0 or idx == total_rows:
                            print(
                                f"  Progress: {idx}/{total_rows} entries...",
                                file=sys.stderr,
                                end="\r",
                            )

                    except (json.JSONDecodeError, Exception):
                        # Skip rows that can't be parsed
                        continue

                # Process remaining batch
                if batch:
                    self._process_migration_batch(cursor, batch)
                    updated_count += len(batch)

                if total_rows > 0:
                    print()  # New line after progress
                    print(
                        f"Migration complete: {updated_count}/{total_rows} entries updated"
                    )

                # Update schema version
                cursor.execute(
                    "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                    ("schema_version", "2.0"),
                )

                conn.commit()

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="cache migration")
            print(f"Cache migration error: {sanitized_error}")

    def _migrate_v2_0_to_v2_1(self):
        """Migrate cache database from v2.0 to v2.1 schema (add installed_at column)."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Check if we need to migrate (check for missing column)
                cursor.execute("PRAGMA table_info(scan_cache)")
                columns = {row[1] for row in cursor.fetchall()}

                if "installed_at" in columns:
                    # Already migrated
                    return

                print("Migrating cache schema (v2.0 → v2.1)...")

                # Add new column to existing table
                cursor.execute(
                    """
                    ALTER TABLE scan_cache
                    ADD COLUMN installed_at TIMESTAMP
                """
                )

                # Update schema version
                cursor.execute(
                    "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                    ("schema_version", "2.1"),
                )

                conn.commit()
                print("Migration complete (v2.0 → v2.1)")

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(
                str(e), context="cache migration v2.0→v2.1"
            )
            print(f"Cache migration error: {sanitized_error}")

    def _migrate_v2_1_to_v2_2(self):
        """Migrate cache database from v2.1 to v2.2 schema (add integrity_signature column)."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Check if we need to migrate (check for missing column)
                cursor.execute("PRAGMA table_info(scan_cache)")
                columns = {row[1] for row in cursor.fetchall()}

                if "integrity_signature" in columns:
                    # Already migrated
                    return

                print("Migrating cache schema (v2.1 → v2.2)...")
                print("Adding HMAC integrity checking to cache entries...")

                # Add new column to existing table
                cursor.execute(
                    """
                    ALTER TABLE scan_cache
                    ADD COLUMN integrity_signature TEXT
                """
                )

                # Note: Existing entries will have NULL signatures
                # They will be re-signed on next access or treated as unsigned (cache miss)

                # Update schema version
                cursor.execute(
                    "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                    ("schema_version", "2.2"),
                )

                conn.commit()
                print("Migration complete (v2.1 → v2.2)")
                print("Note: Existing cache entries will be re-signed on next access")

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(
                str(e), context="cache migration v2.1→v2.2"
            )
            print(f"Cache migration error: {sanitized_error}")

    def get_cached_result(
        self,
        extension_id: str,
        version: str,
        max_age_days: int = DEFAULT_CACHE_MAX_AGE_DAYS,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached scan result if exists and not expired.

        Args:
            extension_id: Extension ID (e.g., "ms-python.python")
            version: Extension version
            max_age_days: Maximum age of cached result in days

        Returns:
            Cached result dict if found and valid, None otherwise
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Calculate cutoff timestamp
                cutoff = datetime.now() - timedelta(days=max_age_days)
                cutoff_str = cutoff.isoformat()

                cursor.execute(
                    """
                    SELECT scan_result, scanned_at, integrity_signature
                    FROM scan_cache
                    WHERE extension_id = ?
                      AND version = ?
                      AND scanned_at >= ?
                """,
                    (extension_id, version, cutoff_str),
                )

                row = cursor.fetchone()

                if row:
                    scan_result_json, scanned_at, integrity_signature = row

                    # Verify HMAC signature (v3.5.1 security hardening)
                    if integrity_signature:
                        if not self._verify_integrity_signature(
                            scan_result_json, integrity_signature
                        ):
                            # Signature mismatch - cache entry has been tampered with
                            print(
                                f"[WARNING] Cache integrity check failed for {extension_id} v{version}",
                                file=sys.stderr,
                            )
                            print(
                                "[WARNING] Cache entry rejected due to signature mismatch",
                                file=sys.stderr,
                            )
                            return None  # Treat as cache miss - will trigger fresh scan
                    else:
                        # No signature (old cache entry from v2.1 or earlier)
                        # Treat as cache miss to force re-scan with signature
                        print(
                            f"[INFO] Unsigned cache entry for {extension_id} v{version} (will re-scan)",
                            file=sys.stderr,
                        )
                        return None

                    result = json.loads(scan_result_json)

                    # Add cache metadata
                    result["_cache_hit"] = True
                    result["_cached_at"] = scanned_at

                    return result

                return None

        except (sqlite3.Error, json.JSONDecodeError) as e:
            # Log error but don't fail - just return None (cache miss)
            sanitized_error = sanitize_error_message(str(e), context="cache read")
            print(f"Cache read error: {sanitized_error}")
            return None

    def save_result(self, extension_id: str, version: str, result: Dict[str, Any]):
        """
        Save scan result to cache (v2 schema).

        Args:
            extension_id: Extension ID (e.g., "ms-python.python")
            version: Extension version
            result: Scan result dictionary to cache
        """
        # Don't cache failed scans
        if result.get("scan_status") != "success":
            return

        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Remove cache metadata before storing
                result_to_store = result.copy()
                result_to_store.pop("_cache_hit", None)
                result_to_store.pop("_cached_at", None)

                scan_result_json = json.dumps(result_to_store)
                scanned_at = datetime.now().isoformat()

                # Extract indexed fields for v2 schema
                risk_level = result_to_store.get("risk_level")
                security_score = result_to_store.get("security_score")

                # Vulnerabilities
                vulnerabilities = result_to_store.get("vulnerabilities", {})
                vuln_count = (
                    vulnerabilities.get("count", 0)
                    if isinstance(vulnerabilities, dict)
                    else 0
                )

                # Dependencies
                dependencies = result_to_store.get("dependencies", {})
                dependencies_count = dependencies.get("total_count", 0)

                # Publisher verification
                metadata = result_to_store.get("metadata", {})
                publisher = metadata.get("publisher", {})
                publisher_verified = 1 if publisher.get("verified") else 0

                # Risk factors
                risk_factors = result_to_store.get("risk_factors", [])
                has_risk_factors = 1 if len(risk_factors) > 0 else 0

                # Installation timestamp
                installed_at = result_to_store.get("installed_at")

                # Compute HMAC signature for integrity checking (v3.5.1)
                integrity_signature = self._compute_integrity_signature(
                    scan_result_json
                )

                # Insert or replace
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO scan_cache
                    (extension_id, version, scan_result, scanned_at, risk_level, security_score,
                     vulnerabilities_count, dependencies_count, publisher_verified, has_risk_factors, installed_at, integrity_signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        extension_id,
                        version,
                        scan_result_json,
                        scanned_at,
                        risk_level,
                        security_score,
                        vuln_count,
                        dependencies_count,
                        publisher_verified,
                        has_risk_factors,
                        installed_at,
                        integrity_signature,
                    ),
                )

                conn.commit()

        except (sqlite3.Error, json.JSONDecodeError) as e:
            # Log error but don't fail the scan
            sanitized_error = sanitize_error_message(str(e), context="cache write")
            print(f"Cache write error: {sanitized_error}")

    def begin_batch(self):
        """
        Begin a batch transaction for multiple save operations.
        This keeps the database connection open and defers commits.
        """
        if self._batch_connection is not None:
            # Batch already in progress
            return

        self._batch_connection = sqlite3.connect(self.cache_db)
        self._batch_cursor = self._batch_connection.cursor()
        self._batch_count = 0

    def save_result_batch(
        self, extension_id: str, version: str, result: Dict[str, Any]
    ):
        """
        Save scan result to cache without committing (batch mode).
        Must call begin_batch() first.

        Args:
            extension_id: Extension ID (e.g., "ms-python.python")
            version: Extension version
            result: Scan result dictionary to cache
        """
        # Don't cache failed scans
        if result.get("scan_status") != "success":
            return

        if self._batch_connection is None:
            # Fallback to regular save if batch not started
            self.save_result(extension_id, version, result)
            return

        try:
            # Remove cache metadata before storing
            result_to_store = result.copy()
            result_to_store.pop("_cache_hit", None)
            result_to_store.pop("_cached_at", None)

            scan_result_json = json.dumps(result_to_store)
            scanned_at = datetime.now().isoformat()

            # Extract indexed fields for v2 schema
            risk_level = result_to_store.get("risk_level")
            security_score = result_to_store.get("security_score")

            # Vulnerabilities
            vulnerabilities = result_to_store.get("vulnerabilities", {})
            vuln_count = (
                vulnerabilities.get("count", 0)
                if isinstance(vulnerabilities, dict)
                else 0
            )

            # Dependencies
            dependencies = result_to_store.get("dependencies", {})
            dependencies_count = dependencies.get("total_count", 0)

            # Publisher verification
            metadata = result_to_store.get("metadata", {})
            publisher = metadata.get("publisher", {})
            publisher_verified = 1 if publisher.get("verified") else 0

            # Risk factors
            risk_factors = result_to_store.get("risk_factors", [])
            has_risk_factors = 1 if len(risk_factors) > 0 else 0

            # Installation timestamp
            installed_at = result_to_store.get("installed_at")

            # Compute HMAC signature for integrity checking (v3.5.1)
            integrity_signature = self._compute_integrity_signature(scan_result_json)

            # Insert or replace
            self._batch_cursor.execute(
                """
                INSERT OR REPLACE INTO scan_cache
                (extension_id, version, scan_result, scanned_at, risk_level, security_score,
                 vulnerabilities_count, dependencies_count, publisher_verified, has_risk_factors, installed_at, integrity_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    extension_id,
                    version,
                    scan_result_json,
                    scanned_at,
                    risk_level,
                    security_score,
                    vuln_count,
                    dependencies_count,
                    publisher_verified,
                    has_risk_factors,
                    installed_at,
                    integrity_signature,
                ),
            )

            self._batch_count += 1

        except (sqlite3.Error, json.JSONDecodeError, TypeError) as e:
            # Log error and clean up batch connection
            sanitized_error = sanitize_error_message(
                str(e), context="batch cache write"
            )
            print(f"Cache write error: {sanitized_error}")
            # Clean up batch connection on error
            self._cleanup_batch_on_error()
            raise  # Re-raise to ensure caller knows about failure

    def _cleanup_batch_on_error(self):
        """Clean up batch connection and cursor on error."""
        if self._batch_connection:
            try:
                self._batch_connection.rollback()
                self._batch_connection.close()
            except Exception:
                pass  # Best-effort cleanup
            finally:
                self._batch_connection = None
                self._batch_cursor = None
                self._batch_count = 0

    def commit_batch(self):
        """
        Commit the current batch transaction and close the connection.

        Returns:
            int: Number of operations in the committed batch.
        """
        if self._batch_connection is None:
            return 0

        try:
            self._batch_connection.commit()
        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="batch commit")
            print(f"Batch commit error: {sanitized_error}")
            self._batch_connection.rollback()
        finally:
            self._batch_connection.close()
            self._batch_connection = None
            self._batch_cursor = None
            count = self._batch_count
            self._batch_count = 0

        return count

    def cleanup_old_entries(
        self, max_age_days: int = DEFAULT_CACHE_MAX_AGE_DAYS
    ) -> int:
        """
        Remove cache entries older than max_age_days.

        Args:
            max_age_days: Maximum age of entries to keep

        Returns:
            Number of entries removed
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                cutoff = datetime.now() - timedelta(days=max_age_days)
                cutoff_str = cutoff.isoformat()

                cursor.execute(
                    """
                    DELETE FROM scan_cache
                    WHERE scanned_at < ?
                """,
                    (cutoff_str,),
                )

                deleted_count = cursor.rowcount
                conn.commit()

                # VACUUM only if thresholds exceeded
                if self._should_vacuum(deleted_count=deleted_count):
                    cursor.execute("VACUUM")

                return deleted_count

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="cache cleanup")
            print(f"Cache cleanup error: {sanitized_error}")
            return 0

    def cleanup_orphaned_entries(
        self, valid_extension_ids: List[str]
    ) -> Tuple[int, List[CacheWarning]]:
        """
        Remove cache entries for extensions that are no longer installed.

        Args:
            valid_extension_ids: List of currently installed extension IDs

        Returns:
            Tuple of (number of entries removed, list of warnings)
        """
        warnings = []

        if not valid_extension_ids:
            return 0, warnings

        try:
            # Import validation function
            from .utils import validate_extension_id

            # Validate all extension IDs before database operation (SQL injection prevention)
            validated_ids = [
                eid for eid in valid_extension_ids if validate_extension_id(eid)
            ]

            if len(validated_ids) != len(valid_extension_ids):
                filtered_count = len(valid_extension_ids) - len(validated_ids)
                warnings.append(
                    CacheWarning(
                        message=f"Filtered out {filtered_count} invalid extension IDs",
                        context="cleanup_orphaned_entries",
                    )
                )

            if not validated_ids:
                return 0, warnings

            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Create placeholders for SQL IN clause (safe: programmatically generated, not user input)
                placeholders = ",".join("?" * len(validated_ids))

                # nosec B608: Safe SQL - placeholders are programmatically generated ("?", "?", ...),
                # actual extension IDs are passed as parameterized tuple (validated_ids).
                # All IDs validated by validate_extension_id() before reaching this code.
                cursor.execute(
                    f"""
                    DELETE FROM scan_cache
                    WHERE extension_id NOT IN ({placeholders})
                """,  # nosec B608
                    validated_ids,
                )

                deleted_count = cursor.rowcount
                conn.commit()

                # VACUUM only if thresholds exceeded
                if self._should_vacuum(deleted_count=deleted_count):
                    cursor.execute("VACUUM")

                return deleted_count, warnings

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="orphan cleanup")
            print(f"Cache orphan cleanup error: {sanitized_error}")
            return 0, warnings

    def get_cache_stats(
        self, max_age_days: int = DEFAULT_CACHE_MAX_AGE_DAYS
    ) -> Dict[str, Any]:
        """
        Get cache statistics including age information.

        Args:
            max_age_days: Maximum age threshold for stale detection (default: 7)

        Returns:
            Dictionary with cache statistics
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Total entries
                cursor.execute("SELECT COUNT(*) FROM scan_cache")
                total_entries = cursor.fetchone()[0]

                # Count by risk level
                cursor.execute(
                    """
                    SELECT risk_level, COUNT(*)
                    FROM scan_cache
                    GROUP BY risk_level
                """
                )
                risk_breakdown = {
                    row[0] or "unknown": row[1] for row in cursor.fetchall()
                }

                # Extensions with vulnerabilities
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM scan_cache
                    WHERE vulnerabilities_count > 0
                """
                )
                with_vulnerabilities = cursor.fetchone()[0]

                # Oldest entry
                cursor.execute(
                    """
                    SELECT MIN(scanned_at)
                    FROM scan_cache
                """
                )
                oldest_entry_row = cursor.fetchone()
                oldest_entry = (
                    oldest_entry_row[0]
                    if oldest_entry_row and oldest_entry_row[0]
                    else None
                )

                # Newest entry
                cursor.execute(
                    """
                    SELECT MAX(scanned_at)
                    FROM scan_cache
                """
                )
                newest_entry_row = cursor.fetchone()
                newest_entry = (
                    newest_entry_row[0]
                    if newest_entry_row and newest_entry_row[0]
                    else None
                )

                # Calculate average age of cache entries
                now = datetime.now()
                cursor.execute("SELECT scanned_at FROM scan_cache")
                timestamp_strs = [row[0] for row in cursor.fetchall() if row[0]]

                avg_age_days = None
                if timestamp_strs:
                    ages = []
                    for ts_str in timestamp_strs:
                        try:
                            ts = datetime.fromisoformat(ts_str)
                            age_days = (now - ts).total_seconds() / 86400
                            ages.append(age_days)
                        except (ValueError, TypeError):
                            continue
                    if ages:
                        avg_age_days = round(sum(ages) / len(ages), 1)

                # Count stale entries (older than max_age_days)
                cutoff = now - timedelta(days=max_age_days)
                cutoff_str = cutoff.isoformat()
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM scan_cache
                    WHERE scanned_at < ?
                """,
                    (cutoff_str,),
                )
                stale_entries = cursor.fetchone()[0]

                # Database size
                db_size_bytes = (
                    self.cache_db.stat().st_size if self.cache_db.exists() else 0
                )
                db_size_kb = db_size_bytes / 1024

                return {
                    "total_entries": total_entries,
                    "risk_breakdown": risk_breakdown,
                    "extensions_with_vulnerabilities": with_vulnerabilities,
                    "oldest_entry": oldest_entry,
                    "newest_entry": newest_entry,
                    "average_age_days": avg_age_days,
                    "stale_entries": stale_entries,
                    "stale_threshold_days": max_age_days,
                    "database_size_kb": round(db_size_kb, 2),
                    "database_path": str(self.cache_db),
                }

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="cache stats")
            print(f"Cache stats error: {sanitized_error}")
            return {"error": sanitized_error, "database_path": str(self.cache_db)}

    def _should_vacuum(self, deleted_count: int = 0) -> bool:
        """
        Determine if VACUUM should be run based on thresholds.

        Thresholds:
        - Database size > 10MB
        - Deleted count > 50 entries

        Args:
            deleted_count: Number of entries just deleted

        Returns:
            bool: True if VACUUM should be run
        """
        try:
            # Check database file size
            db_size_mb = self.cache_db.stat().st_size / (1024 * 1024)

            if db_size_mb > 10.0:
                return True

            if deleted_count > 50:
                return True

            return False

        except Exception:
            # If we can't determine, default to True for safety
            return True

    def clear_cache(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries removed
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM scan_cache")
                count = cursor.fetchone()[0]

                cursor.execute("DELETE FROM scan_cache")
                conn.commit()

                # VACUUM only if thresholds exceeded
                if self._should_vacuum(deleted_count=count):
                    cursor.execute("VACUUM")

                return count

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="cache clear")
            print(f"Cache clear error: {sanitized_error}")
            return 0

    def get_all_cached_extensions(self) -> List[Dict[str, str]]:
        """
        Get list of all cached extensions.

        Returns:
            List of dicts with extension_id, version, scanned_at
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT extension_id, version, scanned_at, risk_level, vulnerabilities_count
                    FROM scan_cache
                    ORDER BY scanned_at DESC
                """
                )

                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "extension_id": row[0],
                            "version": row[1],
                            "scanned_at": row[2],
                            "risk_level": row[3],
                            "vulnerabilities_count": row[4],
                        }
                    )

                return results

        except sqlite3.Error as e:
            sanitized_error = sanitize_error_message(str(e), context="cache list")
            print(f"Cache list error: {sanitized_error}")
            return []

    def get_all_cached_results(
        self, max_age_days: int = CACHE_REPORT_MAX_AGE_DAYS
    ) -> List[Dict[str, Any]]:
        """
        Get all cached scan results with full data.

        Used by the report command to generate reports from cache only.

        Args:
            max_age_days: Maximum age of cached results in days (default: 365)

        Returns:
            List of full scan result dicts
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Calculate cutoff timestamp
                cutoff = datetime.now() - timedelta(days=max_age_days)
                cutoff_str = cutoff.isoformat()

                cursor.execute(
                    """
                    SELECT scan_result, scanned_at
                    FROM scan_cache
                    WHERE scanned_at >= ?
                    ORDER BY scanned_at DESC
                """,
                    (cutoff_str,),
                )

                results = []
                for row in cursor.fetchall():
                    scan_result_json, scanned_at = row
                    result = json.loads(scan_result_json)
                    result["_cached_at"] = scanned_at
                    results.append(result)

                return results

        except sqlite3.Error as e:
            log(f"Database error retrieving all cached results: {e}", "ERROR")
            return []
