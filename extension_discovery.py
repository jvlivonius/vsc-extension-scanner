#!/usr/bin/env python3
"""
Extension Discovery Module

Discovers and parses VS Code extensions from the filesystem.
Supports macOS, Windows, and Linux platforms.
"""

import json
import platform
from pathlib import Path
from typing import List, Dict, Optional

from utils import log, sanitize_string, sanitize_error_message

# Maximum package.json size (1MB)
MAX_PACKAGE_JSON_SIZE = 1024 * 1024


class ExtensionDiscovery:
    """Discovers and parses VS Code extensions."""

    def __init__(self, custom_dir: Optional[str] = None):
        """
        Initialize extension discovery.

        Args:
            custom_dir: Optional custom extensions directory path
        """
        self.custom_dir = custom_dir

    def find_extensions_directory(self) -> Path:
        """
        Find the VS Code extensions directory based on platform.

        Returns:
            Path to extensions directory

        Raises:
            FileNotFoundError: If extensions directory cannot be found
        """
        if self.custom_dir:
            # Validate path doesn't contain dangerous patterns
            if ".." in self.custom_dir or self.custom_dir.startswith("/etc") or self.custom_dir.startswith("/var") or self.custom_dir.startswith("/sys"):
                raise FileNotFoundError(f"Invalid or restricted path: {self.custom_dir}")

            custom_path = Path(self.custom_dir).expanduser().resolve()

            if not custom_path.exists():
                raise FileNotFoundError(f"Custom extensions directory not found: {custom_path}")
            if not custom_path.is_dir():
                raise FileNotFoundError(f"Custom extensions path is not a directory: {custom_path}")

            return custom_path

        # Auto-detect based on platform
        system = platform.system()
        home = Path.home()

        if system == "Darwin":  # macOS
            extensions_dir = home / ".vscode" / "extensions"
        elif system == "Windows":
            extensions_dir = home / ".vscode" / "extensions"
        elif system == "Linux":
            extensions_dir = home / ".vscode" / "extensions"
        else:
            raise FileNotFoundError(f"Unsupported platform: {system}")

        if not extensions_dir.exists():
            raise FileNotFoundError(
                f"VS Code extensions directory not found: {extensions_dir}\n"
                f"Please ensure VS Code is installed or use --extensions-dir to specify a custom path"
            )

        return extensions_dir

    def discover_extensions(self) -> List[Dict[str, str]]:
        """
        Discover all VS Code extensions in the extensions directory.

        Returns:
            List of extension metadata dictionaries

        Raises:
            Exception: If extensions directory cannot be read
        """
        extensions_dir = self.find_extensions_directory()
        extensions = []

        try:
            # Iterate through all subdirectories
            for ext_dir in extensions_dir.iterdir():
                if not ext_dir.is_dir():
                    continue

                # Skip hidden directories
                if ext_dir.name.startswith('.'):
                    continue

                # Try to parse extension metadata
                try:
                    metadata = self._parse_extension(ext_dir)
                    if metadata:
                        extensions.append(metadata)
                except Exception as e:
                    # Log warning but continue with other extensions
                    log(f"Warning: Failed to parse extension at {sanitize_string(str(ext_dir), max_length=100)}: {sanitize_string(str(e), max_length=150)}", "WARNING")
                    continue

        except PermissionError as e:
            raise Exception(f"Permission denied reading extensions directory: {sanitize_string(str(e), max_length=200)}")

        return extensions

    def _parse_extension(self, ext_dir: Path) -> Optional[Dict[str, str]]:
        """
        Parse extension metadata from package.json.

        Args:
            ext_dir: Path to extension directory

        Returns:
            Dictionary with extension metadata or None if invalid

        Raises:
            Exception: If package.json cannot be parsed
        """
        package_json_path = ext_dir / "package.json"

        if not package_json_path.exists():
            # Not a valid extension directory
            return None

        try:
            # Check file size first
            file_size = package_json_path.stat().st_size
            if file_size > MAX_PACKAGE_JSON_SIZE:
                raise Exception(f"package.json too large: {file_size} bytes (max: {MAX_PACKAGE_JSON_SIZE})")

            # Read and parse
            with open(package_json_path, 'r', encoding='utf-8') as f:
                content = f.read()
                package_data = json.loads(content)

                # Validate it's a dictionary
                if not isinstance(package_data, dict):
                    raise Exception("package.json must be a JSON object")

        except json.JSONDecodeError as e:
            # Sanitize JSON decode error message
            sanitized_error = sanitize_error_message(str(e), context="JSON parsing error")
            raise Exception(f"Invalid JSON in package.json: {sanitized_error}")
        except Exception as e:
            # Sanitize generic error message
            sanitized_error = sanitize_error_message(str(e), context="file reading error")
            raise Exception(f"Error reading package.json: {sanitized_error}")

        # Extract required fields
        name = package_data.get('name')
        publisher = package_data.get('publisher')
        version = package_data.get('version')

        if not name or not publisher:
            # Missing required fields
            return None

        # Build extension metadata
        metadata = {
            'name': name,
            'publisher': publisher,
            'version': version or 'unknown',
            'id': f"{publisher}.{name}",
            'display_name': package_data.get('displayName', name),
            'description': package_data.get('description', ''),
            'path': str(ext_dir)
        }

        return metadata

    def get_extension_count(self) -> int:
        """
        Get the count of extensions without full parsing.

        Returns:
            Number of extension directories found
        """
        try:
            extensions_dir = self.find_extensions_directory()
            count = sum(1 for d in extensions_dir.iterdir()
                       if d.is_dir() and not d.name.startswith('.'))
            return count
        except Exception:
            return 0


def main():
    """Test the extension discovery module."""
    import sys
    from utils import setup_logging

    setup_logging(verbose=True)

    log("Testing Extension Discovery Module", "INFO")
    log("=" * 60, "INFO")

    discovery = ExtensionDiscovery()

    try:
        extensions_dir = discovery.find_extensions_directory()
        log(f"Extensions directory: {extensions_dir}", "SUCCESS")

        extensions = discovery.discover_extensions()
        log(f"Found {len(extensions)} extensions", "SUCCESS")

        log("\nFirst 5 extensions:", "INFO")
        for ext in extensions[:5]:
            log(f"  - {ext['id']} v{ext['version']}", "INFO")

    except Exception as e:
        log(f"Error: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
