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
    sanitize_string,
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
            # Validate cache directory using unified validation (v3.5.1+)
            # Blocks: URL encoding, dangerous chars, parent traversal, system directories, temp dirs
            # Expands: shell variables (~/, $HOME/, $USER/)
            try:
                validate_path(
                    cache_dir,
                    allow_absolute=True,
                    path_type="cache directory",
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

        # Check for schema version mismatch and auto-regenerate if needed (v3.7.0)
        # Philosophy: Cache is ephemeral data - can always be regenerated from source
        if self.cache_db.exists():
            # Verify database integrity first
            if not self._verify_database_integrity():
                self._init_messages.extend(self._handle_corrupted_database())

            # Check schema version
            existing_version = self._get_schema_version()

            if existing_version != self.SCHEMA_VERSION:
                # Schema mismatch - remove old cache and regenerate
                self._init_messages.append(
                    CacheInfo(
                        message=(
                            f"Cache schema version {existing_version} detected. "
                            f"Current version is {self.SCHEMA_VERSION}. "
                            "Removing old cache and regenerating with new schema..."
                        ),
                        context="schema_migration",
                    )
                )
                try:
                    self.cache_db.unlink()  # Remove old database
                except OSError as e:
                    sanitized_error = sanitize_error_message(
                        str(e), context="cache removal"
                    )
                    self._init_messages.append(
                        CacheWarning(
                            message=f"Could not remove old cache: {sanitized_error}",
                            context="cache_removal",
                        )
                    )

        # Initialize database with current schema
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
        """Initialize SQLite database with schema v4.1."""
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

            # Create scan_cache table (v4.1 schema with comprehensive security findings)
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

                    -- v4.0: Rich security data (JSON columns)
                    module_risk_levels TEXT,
                    score_contributions TEXT,
                    security_notes TEXT,

                    -- v4.0: Enhanced metadata
                    installs INTEGER,
                    rating REAL,
                    rating_count INTEGER,
                    repository_url TEXT,
                    license TEXT,
                    keywords TEXT,
                    categories TEXT,

                    -- v4.1: Comprehensive security findings (JSON columns)
                    virustotal_details TEXT,
                    permissions_details TEXT,
                    ossf_checks TEXT,
                    ast_findings TEXT,
                    socket_findings TEXT,
                    network_endpoints TEXT,
                    obfuscation_findings TEXT,
                    sensitive_findings TEXT,
                    opengrep_findings TEXT,
                    vscode_engine TEXT,

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

    def _get_schema_version(self) -> str:
        """Get current schema version from database."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Check if metadata table exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='metadata'"
                )
                if not cursor.fetchone():
                    # No metadata table = empty/unknown database, not v1.0
                    return "unknown"

                # Metadata table exists, check for version
                cursor.execute(
                    "SELECT value FROM metadata WHERE key = 'schema_version'"
                )
                row = cursor.fetchone()
                return row[0] if row else "unknown"  # No version = empty/unknown
        except sqlite3.Error:
            return "unknown"  # Error accessing = empty/unknown

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
                            # Sanitize extension_id and version (user-controlled filesystem input)
                            sanitized_id = sanitize_string(extension_id)
                            sanitized_ver = sanitize_string(version)
                            print(
                                f"[WARNING] Cache integrity check failed for {sanitized_id} v{sanitized_ver}",
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
                        # Sanitize extension_id and version (user-controlled filesystem input)
                        sanitized_id = sanitize_string(extension_id)
                        sanitized_ver = sanitize_string(version)
                        print(
                            f"[INFO] Unsigned cache entry for {sanitized_id} v{sanitized_ver} (will re-scan)",
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
        Save scan result to cache (v4.1 schema with comprehensive security findings).

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

                # v4.0: Extract rich security data
                security = result_to_store.get("security", {})
                module_risk_levels = security.get("module_risk_levels")
                score_contributions = security.get("score_contributions")
                security_notes = security.get("security_notes")

                # Serialize JSON fields for v4.0
                module_risk_levels_json = (
                    json.dumps(module_risk_levels) if module_risk_levels else None
                )
                score_contributions_json = (
                    json.dumps(score_contributions) if score_contributions else None
                )
                security_notes_json = (
                    json.dumps(security_notes) if security_notes else None
                )

                # v4.0: Extract enhanced metadata
                statistics = metadata.get("statistics", {})
                installs = statistics.get("installs")
                rating = statistics.get("rating")
                rating_count = statistics.get("rating_count")
                repository_url = metadata.get("repository_url")
                license_info = metadata.get("license")
                keywords = metadata.get("keywords")
                categories = metadata.get("categories")

                # Serialize list fields
                keywords_json = json.dumps(keywords) if keywords else None
                categories_json = json.dumps(categories) if categories else None

                # v4.1: Extract comprehensive security findings
                virustotal_details = result_to_store.get("virustotal_details")
                permissions_details = result_to_store.get("permissions_details")
                ossf_checks = result_to_store.get("ossf_checks")
                ast_findings = result_to_store.get("ast_findings")
                socket_findings = result_to_store.get("socket_findings")
                network_endpoints = result_to_store.get("network_endpoints")
                obfuscation_findings = result_to_store.get("obfuscation_findings")
                sensitive_findings = result_to_store.get("sensitive_findings")
                opengrep_findings = result_to_store.get("opengrep_findings")
                vscode_engine = metadata.get("vscode_engine")

                # Serialize v4.1 JSON fields
                virustotal_json = (
                    json.dumps(virustotal_details) if virustotal_details else None
                )
                permissions_json = (
                    json.dumps(permissions_details) if permissions_details else None
                )
                ossf_json = json.dumps(ossf_checks) if ossf_checks else None
                ast_json = json.dumps(ast_findings) if ast_findings else None
                socket_json = json.dumps(socket_findings) if socket_findings else None
                network_json = (
                    json.dumps(network_endpoints) if network_endpoints else None
                )
                obfuscation_json = (
                    json.dumps(obfuscation_findings) if obfuscation_findings else None
                )
                sensitive_json = (
                    json.dumps(sensitive_findings) if sensitive_findings else None
                )
                opengrep_json = (
                    json.dumps(opengrep_findings) if opengrep_findings else None
                )

                # Compute HMAC signature for integrity checking (v3.5.1)
                integrity_signature = self._compute_integrity_signature(
                    scan_result_json
                )

                # Insert or replace with v4.1 fields
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO scan_cache
                    (extension_id, version, scan_result, scanned_at, risk_level, security_score,
                     vulnerabilities_count, dependencies_count, publisher_verified, has_risk_factors, installed_at, integrity_signature,
                     module_risk_levels, score_contributions, security_notes,
                     installs, rating, rating_count, repository_url, license, keywords, categories,
                     virustotal_details, permissions_details, ossf_checks, ast_findings, socket_findings,
                     network_endpoints, obfuscation_findings, sensitive_findings, opengrep_findings, vscode_engine)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        # v4.0 fields
                        module_risk_levels_json,
                        score_contributions_json,
                        security_notes_json,
                        installs,
                        rating,
                        rating_count,
                        repository_url,
                        license_info,
                        keywords_json,
                        categories_json,
                        # v4.1 fields
                        virustotal_json,
                        permissions_json,
                        ossf_json,
                        ast_json,
                        socket_json,
                        network_json,
                        obfuscation_json,
                        sensitive_json,
                        opengrep_json,
                        vscode_engine,
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

            # v4.0: Extract rich security data
            security = result_to_store.get("security", {})
            module_risk_levels = security.get("module_risk_levels")
            score_contributions = security.get("score_contributions")
            security_notes = security.get("security_notes")

            # Serialize JSON fields for v4.0
            module_risk_levels_json = (
                json.dumps(module_risk_levels) if module_risk_levels else None
            )
            score_contributions_json = (
                json.dumps(score_contributions) if score_contributions else None
            )
            security_notes_json = json.dumps(security_notes) if security_notes else None

            # v4.0: Extract enhanced metadata
            statistics = metadata.get("statistics", {})
            installs = statistics.get("installs")
            rating = statistics.get("rating")
            rating_count = statistics.get("rating_count")
            repository_url = metadata.get("repository_url")
            license_info = metadata.get("license")
            keywords = metadata.get("keywords")
            categories = metadata.get("categories")

            # Serialize list fields
            keywords_json = json.dumps(keywords) if keywords else None
            categories_json = json.dumps(categories) if categories else None

            # v4.1: Extract comprehensive security findings
            virustotal_details = result_to_store.get("virustotal_details")
            permissions_details = result_to_store.get("permissions_details")
            ossf_checks = result_to_store.get("ossf_checks")
            ast_findings = result_to_store.get("ast_findings")
            socket_findings = result_to_store.get("socket_findings")
            network_endpoints = result_to_store.get("network_endpoints")
            obfuscation_findings = result_to_store.get("obfuscation_findings")
            sensitive_findings = result_to_store.get("sensitive_findings")
            opengrep_findings = result_to_store.get("opengrep_findings")
            vscode_engine = metadata.get("vscode_engine")

            # Serialize v4.1 JSON fields
            virustotal_json = (
                json.dumps(virustotal_details) if virustotal_details else None
            )
            permissions_json = (
                json.dumps(permissions_details) if permissions_details else None
            )
            ossf_json = json.dumps(ossf_checks) if ossf_checks else None
            ast_json = json.dumps(ast_findings) if ast_findings else None
            socket_json = json.dumps(socket_findings) if socket_findings else None
            network_json = json.dumps(network_endpoints) if network_endpoints else None
            obfuscation_json = (
                json.dumps(obfuscation_findings) if obfuscation_findings else None
            )
            sensitive_json = (
                json.dumps(sensitive_findings) if sensitive_findings else None
            )
            opengrep_json = json.dumps(opengrep_findings) if opengrep_findings else None

            # Compute HMAC signature for integrity checking (v3.5.1)
            integrity_signature = self._compute_integrity_signature(scan_result_json)

            # Insert or replace with v4.1 fields
            self._batch_cursor.execute(
                """
                INSERT OR REPLACE INTO scan_cache
                (extension_id, version, scan_result, scanned_at, risk_level, security_score,
                 vulnerabilities_count, dependencies_count, publisher_verified, has_risk_factors, installed_at, integrity_signature,
                 module_risk_levels, score_contributions, security_notes,
                 installs, rating, rating_count, repository_url, license, keywords, categories,
                 virustotal_details, permissions_details, ossf_checks, ast_findings, socket_findings,
                 network_endpoints, obfuscation_findings, sensitive_findings, opengrep_findings, vscode_engine)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    # v4.0 fields
                    module_risk_levels_json,
                    score_contributions_json,
                    security_notes_json,
                    installs,
                    rating,
                    rating_count,
                    repository_url,
                    license_info,
                    keywords_json,
                    categories_json,
                    # v4.1 fields
                    virustotal_json,
                    permissions_json,
                    ossf_json,
                    ast_json,
                    socket_json,
                    network_json,
                    obfuscation_json,
                    sensitive_json,
                    opengrep_json,
                    vscode_engine,
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
