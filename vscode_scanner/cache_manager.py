#!/usr/bin/env python3
"""
Cache Manager for VS Code Extension Security Scanner

Manages SQLite-based caching of scan results to improve performance
for unchanged extensions.
"""

import sqlite3
import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from .utils import is_restricted_path, is_temp_directory, safe_mkdir, safe_touch, safe_chmod
from ._version import SCHEMA_VERSION


class CacheManager:
    """Manages caching of extension scan results using SQLite."""

    SCHEMA_VERSION = SCHEMA_VERSION

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache database. Defaults to ~/.vscan/
        """
        if cache_dir:
            # Validate cache directory path (cross-platform)
            # Block parent directory traversal
            if ".." in cache_dir:
                raise ValueError(f"Invalid cache directory path: {cache_dir}")

            # Check if path is in restricted system directory
            # Allow temp directories for testing
            if is_restricted_path(cache_dir) and not is_temp_directory(cache_dir):
                raise ValueError(f"Invalid cache directory path: {cache_dir}")

            cache_path = Path(cache_dir).expanduser().resolve()

            self.cache_dir = cache_path
        else:
            self.cache_dir = Path.home() / ".vscan"

        self.cache_db = self.cache_dir / "cache.db"

        # Verify database integrity if it exists
        if self.cache_db.exists():
            if not self._verify_database_integrity():
                self._handle_corrupted_database()

        # Check if migration is needed before init
        needs_migration = self._check_if_migration_needed()

        if needs_migration:
            self._migrate_v1_to_v2()
        else:
            self._init_database()

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
                print(f"[WARNING] Cache database integrity check failed: {result}",
                      file=__import__('sys').stderr)
                return False

        except sqlite3.Error as e:
            print(f"[WARNING] Cache database integrity check error: {e}",
                  file=__import__('sys').stderr)
            return False

    def _handle_corrupted_database(self):
        """
        Handle corrupted database by backing it up and creating a fresh one.
        """
        import sys
        import shutil

        print("[WARNING] Detected corrupted cache database", file=sys.stderr)

        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.cache_db.parent / f"cache.db.corrupted.{timestamp}"

            print(f"[INFO] Backing up corrupted database to: {backup_path}", file=sys.stderr)
            shutil.copy2(self.cache_db, backup_path)

            # Remove corrupted database
            print("[INFO] Removing corrupted database...", file=sys.stderr)
            self.cache_db.unlink()

            print("[INFO] Creating fresh cache database...", file=sys.stderr)

        except (OSError, IOError) as e:
            print(f"[ERROR] Failed to handle corrupted database: {e}", file=sys.stderr)
            print("[INFO] Cache functionality may be impaired", file=sys.stderr)

    def _init_database(self):
        """Initialize SQLite database with schema v2.0."""
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

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            # Create scan_cache table (v2 schema with additional fields)
            cursor.execute("""
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
                    UNIQUE(extension_id, version)
                )
            """)

            # Create metadata table for schema version and stats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_extension
                ON scan_cache(extension_id, version)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scanned_at
                ON scan_cache(scanned_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_risk_level
                ON scan_cache(risk_level)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_security_score
                ON scan_cache(security_score)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vulnerabilities
                ON scan_cache(vulnerabilities_count)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_publisher_verified
                ON scan_cache(publisher_verified)
            """)

            # Store schema version
            cursor.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("schema_version", self.SCHEMA_VERSION)
            )

            conn.commit()
        finally:
            conn.close()

    def _check_if_migration_needed(self) -> bool:
        """Check if database exists and needs migration."""
        if not self.cache_db.exists():
            return False  # New database, no migration needed

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            # Check if scan_cache table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='scan_cache'
            """)
            if not cursor.fetchone():
                return False  # No table yet, fresh install

            # Check if new columns exist
            cursor.execute("PRAGMA table_info(scan_cache)")
            columns = {row[1] for row in cursor.fetchall()}

            # If security_score column doesn't exist, we need migration
            return "security_score" not in columns

        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def _get_schema_version(self) -> str:
        """Get current schema version from database."""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
            row = cursor.fetchone()
            return row[0] if row else "1.0"  # Default to 1.0 if not found
        except sqlite3.Error:
            return "1.0"  # If table doesn't exist, assume v1
        finally:
            conn.close()

    def _migrate_v1_to_v2(self):
        """Migrate cache database from v1.0 to v2.0 schema."""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            # Check if we need to migrate (check for missing columns)
            cursor.execute("PRAGMA table_info(scan_cache)")
            columns = {row[1] for row in cursor.fetchall()}

            if "security_score" in columns:
                # Already migrated
                return

            # Add new columns to existing table
            cursor.execute("""
                ALTER TABLE scan_cache
                ADD COLUMN security_score INTEGER
            """)
            cursor.execute("""
                ALTER TABLE scan_cache
                ADD COLUMN dependencies_count INTEGER DEFAULT 0
            """)
            cursor.execute("""
                ALTER TABLE scan_cache
                ADD COLUMN publisher_verified BOOLEAN DEFAULT 0
            """)
            cursor.execute("""
                ALTER TABLE scan_cache
                ADD COLUMN has_risk_factors BOOLEAN DEFAULT 0
            """)

            # Create new indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_security_score
                ON scan_cache(security_score)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vulnerabilities
                ON scan_cache(vulnerabilities_count)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_publisher_verified
                ON scan_cache(publisher_verified)
            """)

            # Update existing rows with parsed data from scan_result JSON
            cursor.execute("SELECT id, scan_result FROM scan_cache")
            rows = cursor.fetchall()

            total_rows = len(rows)
            if total_rows > 0:
                print(f"Migrating cache schema (v1.0 → v2.0)...", file=__import__('sys').stderr)
                print(f"Processing {total_rows} cached entries...", file=__import__('sys').stderr)

            updated_count = 0
            for idx, (row_id, scan_result_json) in enumerate(rows, 1):
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

                    # Update row
                    cursor.execute("""
                        UPDATE scan_cache
                        SET security_score = ?,
                            dependencies_count = ?,
                            publisher_verified = ?,
                            has_risk_factors = ?
                        WHERE id = ?
                    """, (security_score, dependencies_count, publisher_verified, has_risk_factors, row_id))

                    updated_count += 1

                    # Show progress every 10 entries or at the end
                    if idx % 10 == 0 or idx == total_rows:
                        print(f"  Progress: {idx}/{total_rows} entries...", file=__import__('sys').stderr, end='\r')

                except (json.JSONDecodeError, Exception):
                    # Skip rows that can't be parsed
                    continue

            if total_rows > 0:
                print()  # New line after progress
                print(f"Migration complete: {updated_count}/{total_rows} entries updated", file=__import__('sys').stderr)

            # Update schema version
            cursor.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("schema_version", "2.0")
            )

            conn.commit()

        except sqlite3.Error as e:
            print(f"Cache migration error: {e}", file=__import__('sys').stderr)
            conn.rollback()
        finally:
            conn.close()

    def get_cached_result(
        self,
        extension_id: str,
        version: str,
        max_age_days: int = 7
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

                cursor.execute("""
                    SELECT scan_result, scanned_at
                    FROM scan_cache
                    WHERE extension_id = ?
                      AND version = ?
                      AND scanned_at >= ?
                """, (extension_id, version, cutoff_str))

                row = cursor.fetchone()

                if row:
                    scan_result_json, scanned_at = row
                    result = json.loads(scan_result_json)

                    # Add cache metadata
                    result['_cache_hit'] = True
                    result['_cached_at'] = scanned_at

                    return result

                return None

        except (sqlite3.Error, json.JSONDecodeError) as e:
            # Log error but don't fail - just return None (cache miss)
            print(f"Cache read error: {e}", file=__import__('sys').stderr)
            return None

    def save_result(
        self,
        extension_id: str,
        version: str,
        result: Dict[str, Any]
    ):
        """
        Save scan result to cache (v2 schema).

        Args:
            extension_id: Extension ID (e.g., "ms-python.python")
            version: Extension version
            result: Scan result dictionary to cache
        """
        # Don't cache failed scans
        if result.get('scan_status') != 'success':
            return

        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Remove cache metadata before storing
                result_to_store = result.copy()
                result_to_store.pop('_cache_hit', None)
                result_to_store.pop('_cached_at', None)

                scan_result_json = json.dumps(result_to_store)
                scanned_at = datetime.now().isoformat()

                # Extract indexed fields for v2 schema
                risk_level = result_to_store.get('risk_level')
                security_score = result_to_store.get('security_score')

                # Vulnerabilities
                vulnerabilities = result_to_store.get('vulnerabilities', {})
                vuln_count = vulnerabilities.get('count', 0) if isinstance(vulnerabilities, dict) else 0

                # Dependencies
                dependencies = result_to_store.get('dependencies', {})
                dependencies_count = dependencies.get('total_count', 0)

                # Publisher verification
                metadata = result_to_store.get('metadata', {})
                publisher = metadata.get('publisher', {})
                publisher_verified = 1 if publisher.get('verified') else 0

                # Risk factors
                risk_factors = result_to_store.get('risk_factors', [])
                has_risk_factors = 1 if len(risk_factors) > 0 else 0

                # Insert or replace
                cursor.execute("""
                    INSERT OR REPLACE INTO scan_cache
                    (extension_id, version, scan_result, scanned_at, risk_level, security_score,
                     vulnerabilities_count, dependencies_count, publisher_verified, has_risk_factors)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (extension_id, version, scan_result_json, scanned_at, risk_level, security_score,
                      vuln_count, dependencies_count, publisher_verified, has_risk_factors))

                conn.commit()

        except (sqlite3.Error, json.JSONDecodeError) as e:
            # Log error but don't fail the scan
            print(f"Cache write error: {e}", file=__import__('sys').stderr)

    def cleanup_old_entries(self, max_age_days: int = 7) -> int:
        """
        Remove cache entries older than max_age_days.

        Args:
            max_age_days: Maximum age of entries to keep

        Returns:
            Number of entries removed
        """
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            cutoff = datetime.now() - timedelta(days=max_age_days)
            cutoff_str = cutoff.isoformat()

            cursor.execute("""
                DELETE FROM scan_cache
                WHERE scanned_at < ?
            """, (cutoff_str,))

            deleted_count = cursor.rowcount
            conn.commit()

            return deleted_count

        except sqlite3.Error as e:
            print(f"Cache cleanup error: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return 0
        finally:
            conn.close()

    def cleanup_orphaned_entries(self, valid_extension_ids: List[str]) -> int:
        """
        Remove cache entries for extensions that are no longer installed.

        Args:
            valid_extension_ids: List of currently installed extension IDs

        Returns:
            Number of entries removed
        """
        if not valid_extension_ids:
            return 0

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            # Create placeholders for SQL IN clause
            placeholders = ','.join('?' * len(valid_extension_ids))

            cursor.execute(f"""
                DELETE FROM scan_cache
                WHERE extension_id NOT IN ({placeholders})
            """, valid_extension_ids)

            deleted_count = cursor.rowcount
            conn.commit()

            return deleted_count

        except sqlite3.Error as e:
            print(f"Cache orphan cleanup error: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return 0
        finally:
            conn.close()

    def get_cache_stats(self, max_age_days: int = 7) -> Dict[str, Any]:
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
                cursor.execute("""
                    SELECT risk_level, COUNT(*)
                    FROM scan_cache
                    GROUP BY risk_level
                """)
                risk_breakdown = {row[0] or 'unknown': row[1] for row in cursor.fetchall()}

                # Extensions with vulnerabilities
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM scan_cache
                    WHERE vulnerabilities_count > 0
                """)
                with_vulnerabilities = cursor.fetchone()[0]

                # Oldest entry
                cursor.execute("""
                    SELECT MIN(scanned_at)
                    FROM scan_cache
                """)
                oldest_entry_row = cursor.fetchone()
                oldest_entry = oldest_entry_row[0] if oldest_entry_row and oldest_entry_row[0] else None

                # Newest entry
                cursor.execute("""
                    SELECT MAX(scanned_at)
                    FROM scan_cache
                """)
                newest_entry_row = cursor.fetchone()
                newest_entry = newest_entry_row[0] if newest_entry_row and newest_entry_row[0] else None

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
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM scan_cache
                    WHERE scanned_at < ?
                """, (cutoff_str,))
                stale_entries = cursor.fetchone()[0]

                # Database size
                db_size_bytes = self.cache_db.stat().st_size if self.cache_db.exists() else 0
                db_size_kb = db_size_bytes / 1024

                return {
                    'total_entries': total_entries,
                    'risk_breakdown': risk_breakdown,
                    'extensions_with_vulnerabilities': with_vulnerabilities,
                    'oldest_entry': oldest_entry,
                    'newest_entry': newest_entry,
                    'average_age_days': avg_age_days,
                    'stale_entries': stale_entries,
                    'stale_threshold_days': max_age_days,
                    'database_size_kb': round(db_size_kb, 2),
                    'database_path': str(self.cache_db)
                }

        except sqlite3.Error as e:
            print(f"Cache stats error: {e}", file=__import__('sys').stderr)
            return {
                'error': str(e),
                'database_path': str(self.cache_db)
            }

    def clear_cache(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries removed
        """
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM scan_cache")
            count = cursor.fetchone()[0]

            cursor.execute("DELETE FROM scan_cache")
            conn.commit()

            return count

        except sqlite3.Error as e:
            print(f"Cache clear error: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return 0
        finally:
            conn.close()

    def get_all_cached_extensions(self) -> List[Dict[str, str]]:
        """
        Get list of all cached extensions.

        Returns:
            List of dicts with extension_id, version, scanned_at
        """
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT extension_id, version, scanned_at, risk_level, vulnerabilities_count
                FROM scan_cache
                ORDER BY scanned_at DESC
            """)

            results = []
            for row in cursor.fetchall():
                results.append({
                    'extension_id': row[0],
                    'version': row[1],
                    'scanned_at': row[2],
                    'risk_level': row[3],
                    'vulnerabilities_count': row[4]
                })

            return results

        except sqlite3.Error as e:
            print(f"Cache list error: {e}", file=__import__('sys').stderr)
            return []
        finally:
            conn.close()
