#!/usr/bin/env python3
"""
Configuration Manager for VS Code Extension Scanner

Manages persistent configuration file (~/.vscanrc) using INI format.
Allows users to set default values for common options.

Configuration Architecture
==========================

Hierarchy (highest priority first):
1. CLI Arguments (typer command parameters) - Always override everything
2. Config File (~/.vscanrc) - User-defined defaults
3. Defaults (constants.py) - Fallback values

Schema Versioning:
- Current: v1 (INI format)
- Future: Supports migration to v2 if needed (via [_meta] section)
- Schema version stored in [_meta] section for forward compatibility

Validation:
- Type checking on load (int, float, bool, str, choice, path)
- Range validation for numeric values
- Enum validation for fixed choices (e.g., min_risk_level)
- Invalid values trigger warnings and fall back to defaults

Configuration File Format (~/.vscanrc):
```ini
# VS Code Extension Scanner Configuration
# Schema version for future compatibility
[_meta]
schema_version = 1

[scan]
delay = 2.0                     # Seconds between API requests
max_retries = 3                 # Maximum HTTP retry attempts
retry_delay = 2.0               # Base HTTP retry delay in seconds

[cache]
cache_max_age = 14              # Cache expiration in days

[output]
quiet = false                   # Minimal output by default
plain = false                   # Disable Rich formatting
```

Usage:
- `vscan config init` - Create default config file
- `vscan config show` - Display current configuration
- `vscan config set <key> <value>` - Update config value
- `vscan config get <key>` - Get specific value
- `vscan config reset` - Delete config file

Implementation Notes:
- Config values loaded once at startup
- All validation happens at load time
- Malformed values trigger warnings, not errors
- Config file is optional (all values have defaults)
"""

from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import sys

from .types import ConfigWarning
from .constants import (
    DEFAULT_REQUEST_DELAY,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BASE_DELAY,
    DEFAULT_WORKFLOW_MAX_RETRIES,
    DEFAULT_WORKFLOW_RETRY_DELAY,
    DEFAULT_CACHE_MAX_AGE_DAYS,
    MIN_DELAY_SECONDS,
    MAX_DELAY_SECONDS,
    MIN_RETRIES,
    MAX_RETRIES,
    MIN_RETRY_DELAY,
    MAX_RETRY_DELAY,
    MIN_CACHE_AGE_DAYS,
    MAX_CACHE_AGE_DAYS
)

# Configuration schema version
CONFIG_SCHEMA_VERSION = 1

# Default configuration template with comments
DEFAULT_CONFIG_TEMPLATE = f"""# VS Code Extension Scanner Configuration
# File: ~/.vscanrc
# Edit this file to set default values for vscan options.
# CLI arguments always override config file values.

# Schema version for future compatibility
[_meta]
schema_version = {CONFIG_SCHEMA_VERSION}

[scan]
# API request settings
delay = {DEFAULT_REQUEST_DELAY}                  # Seconds between API requests (float, {MIN_DELAY_SECONDS}-{MAX_DELAY_SECONDS})
max_retries = {DEFAULT_MAX_RETRIES}             # Maximum HTTP retry attempts (int, {MIN_RETRIES}-{MAX_RETRIES})
retry_delay = {DEFAULT_RETRY_BASE_DELAY}           # Base HTTP retry delay in seconds (float, {MIN_RETRY_DELAY}-{MAX_RETRY_DELAY})
max_workflow_retries = {DEFAULT_WORKFLOW_MAX_RETRIES}  # Maximum workflow retry attempts (int, {MIN_RETRIES}-{MAX_RETRIES})
workflow_retry_delay = {DEFAULT_WORKFLOW_RETRY_DELAY}   # Base workflow retry delay in seconds (float, {MIN_RETRY_DELAY}-{MAX_RETRY_DELAY})

# Default filters (optional - leave commented to disable)
# publisher = microsoft     # Default publisher filter
# min_risk_level = medium   # Minimum risk level to report (low/medium/high/critical)
# exclude_ids =             # Comma-separated extension IDs to exclude

# Custom extensions directory (optional - leave commented to auto-detect)
# extensions_dir = ~/.vscode/extensions  # Path to VS Code extensions directory

[cache]
# Cache configuration
# cache_dir = ~/.vscan/      # Cache directory path
cache_max_age = {DEFAULT_CACHE_MAX_AGE_DAYS}           # Cache expiration in days (int, {MIN_CACHE_AGE_DAYS}-{MAX_CACHE_AGE_DAYS})
# no_cache = false          # Disable caching (true/false)

[output]
# Output preferences
# plain = false             # Disable Rich formatting by default (true/false)
# quiet = false             # Minimal output by default (true/false)
"""

# Default configuration values
DEFAULT_CONFIG = {
    'scan': {
        'delay': DEFAULT_REQUEST_DELAY,
        'max_retries': DEFAULT_MAX_RETRIES,
        'retry_delay': DEFAULT_RETRY_BASE_DELAY,
        'max_workflow_retries': DEFAULT_WORKFLOW_MAX_RETRIES,
        'workflow_retry_delay': DEFAULT_WORKFLOW_RETRY_DELAY,
        'publisher': None,
        'min_risk_level': None,
        'exclude_ids': None,
        'extensions_dir': None,
    },
    'cache': {
        'cache_dir': None,
        'cache_max_age': DEFAULT_CACHE_MAX_AGE_DAYS,
        'no_cache': False,
    },
    'output': {
        'plain': False,
        'quiet': False,
    }
}

# Configuration schema for validation
CONFIG_SCHEMA = {
    'scan': {
        'delay': ('float', MIN_DELAY_SECONDS, MAX_DELAY_SECONDS),
        'max_retries': ('int', MIN_RETRIES, MAX_RETRIES),
        'retry_delay': ('float', MIN_RETRY_DELAY, MAX_RETRY_DELAY),
        'max_workflow_retries': ('int', MIN_RETRIES, MAX_RETRIES),
        'workflow_retry_delay': ('float', MIN_RETRY_DELAY, MAX_RETRY_DELAY),
        'publisher': ('string', None, None),
        'min_risk_level': ('choice', ['low', 'medium', 'high', 'critical'], None),
        'exclude_ids': ('string', None, None),
        'extensions_dir': ('path', None, None),
    },
    'cache': {
        'cache_dir': ('path', None, None),
        'cache_max_age': ('int', MIN_CACHE_AGE_DAYS, MAX_CACHE_AGE_DAYS),
        'no_cache': ('bool', None, None),
    },
    'output': {
        'plain': ('bool', None, None),
        'quiet': ('bool', None, None),
    }
}


def get_config_path() -> Path:
    """Get the configuration file path (~/.vscanrc)."""
    return Path.home() / ".vscanrc"


def config_exists() -> bool:
    """Check if configuration file exists."""
    return get_config_path().exists()


def load_config() -> Tuple[Dict[str, Dict[str, Any]], List[ConfigWarning]]:
    """
    Load configuration from ~/.vscanrc and merge with defaults.

    Returns:
        Tuple of (config dictionary, list of warnings)
        CLI arguments should override these values.
    """
    config_path = get_config_path()
    warnings = []

    # Start with defaults
    result = {}
    for section, options in DEFAULT_CONFIG.items():
        result[section] = options.copy()

    # If no config file, return defaults
    if not config_path.exists():
        return result, warnings

    # Load config file
    parser = ConfigParser()
    try:
        parser.read(config_path, encoding='utf-8')
    except Exception as e:
        warnings.append(ConfigWarning(
            message=f"Failed to read config file {config_path}: {e}",
            context="load_config"
        ))
        return result, warnings

    # Check schema version for future migrations
    schema_version = 1  # Default to v1 if not specified
    if parser.has_section('_meta'):
        try:
            schema_version = parser.getint('_meta', 'schema_version', fallback=1)
        except ValueError:
            warnings.append(ConfigWarning(
                message="Invalid schema_version in config file, using v1",
                context="load_config"
            ))

    # Handle schema migrations if needed
    if schema_version != CONFIG_SCHEMA_VERSION:
        warnings.append(ConfigWarning(
            message=f"Config schema version mismatch: found v{schema_version}, expected v{CONFIG_SCHEMA_VERSION}. Using compatibility mode.",
            context="load_config"
        ))
        # Future: Add migration logic here when schema v2 is introduced
        # For now, we only have v1, so this is just a placeholder

    # Merge config file values with defaults
    for section in parser.sections():
        # Skip internal sections
        if section.startswith('_'):
            continue
        if section not in result:
            continue  # Skip unknown sections

        for option in parser.options(section):
            if option not in DEFAULT_CONFIG.get(section, {}):
                continue  # Skip unknown options

            try:
                value = _parse_config_value(section, option, parser.get(section, option))
                result[section][option] = value
            except ValueError as e:
                warnings.append(ConfigWarning(
                    message=f"Invalid value for {section}.{option}: {e}",
                    context="load_config"
                ))
                # Keep default value on error

    return result, warnings


def _parse_config_value(section: str, option: str, value_str: str) -> Any:
    """
    Parse a config value string into the appropriate Python type.

    Args:
        section: Config section name
        option: Option name
        value_str: String value from config file

    Returns:
        Parsed value in appropriate type

    Raises:
        ValueError: If value is invalid
    """
    if section not in CONFIG_SCHEMA or option not in CONFIG_SCHEMA[section]:
        raise ValueError(f"Unknown config key: {section}.{option}")

    type_info = CONFIG_SCHEMA[section][option]
    value_type = type_info[0]

    # Strip inline comments (anything after #)
    if '#' in value_str:
        value_str = value_str.split('#')[0]

    # Handle None/empty values
    if value_str.strip() == '' or value_str.strip().lower() == 'none':
        return None

    # Parse based on type
    if value_type == 'bool':
        value_lower = value_str.strip().lower()
        if value_lower in ('true', 'yes', '1', 'on'):
            return True
        elif value_lower in ('false', 'no', '0', 'off'):
            return False
        else:
            raise ValueError(f"Invalid boolean value: {value_str}")

    elif value_type == 'int':
        try:
            value = int(value_str.strip())
            min_val, max_val = type_info[1], type_info[2]
            if min_val is not None and value < min_val:
                raise ValueError(f"Value {value} is below minimum {min_val}")
            if max_val is not None and value > max_val:
                raise ValueError(f"Value {value} is above maximum {max_val}")
            return value
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid integer value: {value_str}")

    elif value_type == 'float':
        try:
            value = float(value_str.strip())
            min_val, max_val = type_info[1], type_info[2]
            if min_val is not None and value < min_val:
                raise ValueError(f"Value {value} is below minimum {min_val}")
            if max_val is not None and value > max_val:
                raise ValueError(f"Value {value} is above maximum {max_val}")
            return value
        except (ValueError, TypeError):
            raise ValueError(f"Invalid float value: {value_str}")

    elif value_type == 'choice':
        value = value_str.strip().lower()
        choices = type_info[1]
        if value not in choices:
            raise ValueError(f"Invalid choice: {value}. Must be one of: {', '.join(choices)}")
        return value

    elif value_type in ('string', 'path'):
        return value_str.strip()

    else:
        raise ValueError(f"Unknown value type: {value_type}")


def is_valid_config_key(section: str, option: str) -> bool:
    """Check if a config key is valid."""
    return section in CONFIG_SCHEMA and option in CONFIG_SCHEMA[section]


def parse_config_key(key: str) -> Tuple[str, str]:
    """
    Parse a config key in format 'section.option'.

    Args:
        key: Config key string

    Returns:
        Tuple of (section, option)

    Raises:
        ValueError: If key format is invalid
    """
    if '.' not in key:
        raise ValueError("Key must be in format 'section.option'")

    parts = key.split('.', 1)
    section, option = parts[0], parts[1]

    if not is_valid_config_key(section, option):
        raise ValueError(f"Unknown configuration key '{key}'")

    return section, option


def validate_config_value(section: str, option: str, value_str: str) -> Any:
    """
    Validate and parse a config value.

    Args:
        section: Config section name
        option: Option name
        value_str: String value to validate

    Returns:
        Validated and parsed value

    Raises:
        ValueError: If value is invalid
    """
    return _parse_config_value(section, option, value_str)


def get_config_value(config: Dict[str, Dict[str, Any]], section: str, option: str) -> Any:
    """
    Get a configuration value.

    Args:
        config: Configuration dictionary
        section: Config section
        option: Option name

    Returns:
        Config value or None if not set
    """
    if section not in config:
        return None
    return config[section].get(option)


def get_default_value(section: str, option: str) -> Any:
    """Get the default value for a config option."""
    if section not in DEFAULT_CONFIG:
        return None
    return DEFAULT_CONFIG[section].get(option)


def create_default_config(force: bool = False) -> Path:
    """
    Create default configuration file.

    Args:
        force: Overwrite existing file

    Returns:
        Path to created config file

    Raises:
        FileExistsError: If file exists and force=False
    """
    config_path = get_config_path()

    if config_path.exists() and not force:
        raise FileExistsError(f"Config file already exists: {config_path}")

    config_path.write_text(DEFAULT_CONFIG_TEMPLATE, encoding='utf-8')
    return config_path


def update_config_value(section: str, option: str, value: Any) -> None:
    """
    Update a configuration value in the config file.

    Args:
        section: Config section
        option: Option name
        value: New value

    Raises:
        ValueError: If key or value is invalid
    """
    config_path = get_config_path()

    # Validate key
    if not is_valid_config_key(section, option):
        raise ValueError(f"Unknown configuration key '{section}.{option}'")

    # Load existing config or create new
    parser = ConfigParser()
    if config_path.exists():
        parser.read(config_path, encoding='utf-8')

    # Add section if needed
    if section not in parser:
        parser.add_section(section)

    # Set value
    parser.set(section, option, str(value))

    # Write back
    with open(config_path, 'w', encoding='utf-8') as f:
        parser.write(f)


def delete_config() -> bool:
    """
    Delete the configuration file.

    Returns:
        True if file was deleted, False if file didn't exist
    """
    config_path = get_config_path()

    if not config_path.exists():
        return False

    config_path.unlink()
    return True
