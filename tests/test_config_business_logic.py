"""
Unit tests for config business logic extracted from CLI.

Tests the merge_scan_config() function to ensure correct priority-based
config merging: hardcoded default < config file < CLI argument
"""

import unittest
from pathlib import Path
from vscode_scanner.config_manager import merge_scan_config


class TestMergeScanConfig(unittest.TestCase):
    """Test merge_scan_config() business logic."""

    def test_merge_all_defaults(self):
        """When CLI args are at defaults and config is empty, use defaults."""
        config = {"scan": {}, "cache": {}, "output": {}}
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)

        # All values should remain at defaults
        assert merged["delay"] == 1.5
        assert merged["max_retries"] == 3
        assert merged["retry_delay"] == 2.0
        assert merged["cache_max_age"] == 7
        assert merged["quiet"] is False
        assert merged["plain"] is False
        assert merged["no_cache"] is False
        assert merged["publisher"] is None
        assert merged["min_risk_level"] is None
        assert merged["exclude_ids"] is None
        assert merged["workers"] == 3
        assert merged["extensions_dir"] is None
        assert merged["cache_dir"] is None

    def test_merge_config_overrides_defaults(self):
        """Config file values override defaults when CLI args are at defaults."""
        config = {
            "scan": {"delay": 2.5, "max_retries": 5, "workers": 4},
            "cache": {"cache_max_age": 14, "no_cache": True},
            "output": {"quiet": True, "plain": True},
        }
        cli_args = {
            "delay": 1.5,  # default
            "max_retries": 3,  # default
            "retry_delay": 2.0,  # default
            "cache_max_age": 7,  # default
            "quiet": False,  # default
            "plain": False,  # default
            "no_cache": False,  # default
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,  # default
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)

        # Config values should override defaults
        assert merged["delay"] == 2.5
        assert merged["max_retries"] == 5
        assert merged["workers"] == 4
        assert merged["cache_max_age"] == 14
        assert merged["no_cache"] is True
        assert merged["quiet"] is True
        assert merged["plain"] is True

        # Unchanged defaults
        assert merged["retry_delay"] == 2.0
        assert merged["publisher"] is None

    def test_merge_cli_overrides_config(self):
        """CLI arguments override config file values."""
        config = {
            "scan": {"delay": 2.5, "max_retries": 5, "workers": 4},
            "cache": {"cache_max_age": 14},
            "output": {"quiet": True},
        }
        cli_args = {
            "delay": 3.0,  # user-specified
            "max_retries": 2,  # user-specified
            "retry_delay": 2.0,  # default
            "cache_max_age": 7,  # default
            "quiet": False,  # default
            "plain": False,  # default
            "no_cache": False,  # default
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,  # default
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)

        # CLI args override config
        assert merged["delay"] == 3.0
        assert merged["max_retries"] == 2

        # Config overrides remaining defaults
        assert merged["cache_max_age"] == 14
        assert merged["quiet"] is True
        assert merged["workers"] == 4

        # Unchanged defaults
        assert merged["retry_delay"] == 2.0
        assert merged["plain"] is False

    def test_merge_publisher_filter(self):
        """Publisher filter merging works correctly."""
        config = {"scan": {"publisher": "microsoft"}, "cache": {}, "output": {}}
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,  # default
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)
        assert merged["publisher"] == "microsoft"

        # Test CLI override
        cli_args["publisher"] = "google"
        merged = merge_scan_config(config, cli_args)
        assert merged["publisher"] == "google"

    def test_merge_min_risk_level(self):
        """Minimum risk level merging works correctly."""
        config = {"scan": {"min_risk_level": "high"}, "cache": {}, "output": {}}
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,  # default
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)
        assert merged["min_risk_level"] == "high"

        # Test CLI override
        cli_args["min_risk_level"] = "critical"
        merged = merge_scan_config(config, cli_args)
        assert merged["min_risk_level"] == "critical"

    def test_merge_exclude_ids(self):
        """Exclude IDs merging works correctly."""
        config = {"scan": {"exclude_ids": "ext1,ext2"}, "cache": {}, "output": {}}
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,  # default
            "workers": 3,
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)
        assert merged["exclude_ids"] == "ext1,ext2"

        # Test CLI override
        cli_args["exclude_ids"] = "ext3,ext4"
        merged = merge_scan_config(config, cli_args)
        assert merged["exclude_ids"] == "ext3,ext4"

    def test_merge_path_arguments(self):
        """Path arguments (extensions_dir, cache_dir) merge correctly."""
        config = {
            "scan": {"extensions_dir": "~/.vscode/extensions"},
            "cache": {"cache_dir": "~/.vscan"},
            "output": {},
        }
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": None,  # default
            "cache_dir": None,  # default
        }

        merged = merge_scan_config(config, cli_args)

        # Config paths should be expanded and converted to Path objects
        assert merged["extensions_dir"] is not None
        assert isinstance(merged["extensions_dir"], Path)
        assert merged["cache_dir"] is not None
        assert isinstance(merged["cache_dir"], Path)

    def test_merge_path_cli_override(self):
        """CLI path arguments override config paths."""
        config = {
            "scan": {"extensions_dir": "~/.vscode/extensions"},
            "cache": {"cache_dir": "~/.vscan"},
            "output": {},
        }
        custom_path = Path("/custom/path")
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": custom_path,  # user-specified
            "cache_dir": custom_path,  # user-specified
        }

        merged = merge_scan_config(config, cli_args)

        # CLI paths should override config
        assert merged["extensions_dir"] == custom_path
        assert merged["cache_dir"] == custom_path

    def test_merge_boolean_flags(self):
        """Boolean flags (quiet, plain, no_cache) merge correctly."""
        config = {
            "scan": {},
            "cache": {"no_cache": True},
            "output": {"quiet": True, "plain": True},
        }
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,  # default
            "plain": False,  # default
            "no_cache": False,  # default
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)

        # Config boolean flags should override defaults
        assert merged["quiet"] is True
        assert merged["plain"] is True
        assert merged["no_cache"] is True

    def test_merge_workers_boundary(self):
        """Workers parameter merges correctly with different values."""
        config = {"scan": {"workers": 5}, "cache": {}, "output": {}}

        # Test default (3) gets overridden by config (5)
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,  # default
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)
        assert merged["workers"] == 5

        # Test user-specified (2) overrides config (5)
        cli_args["workers"] = 2
        merged = merge_scan_config(config, cli_args)
        assert merged["workers"] == 2

    def test_merge_empty_sections(self):
        """Merging works when config sections are missing."""
        config = {"scan": {}, "cache": {}, "output": {}}
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)

        # All values should remain at CLI defaults
        assert merged == cli_args

    def test_merge_partial_config(self):
        """Merging works with only some config values set."""
        config = {
            "scan": {"delay": 2.5},  # Only delay set
            "cache": {},
            "output": {"quiet": True},  # Only quiet set
        }
        cli_args = {
            "delay": 1.5,  # default
            "max_retries": 3,  # default
            "retry_delay": 2.0,  # default
            "cache_max_age": 7,  # default
            "quiet": False,  # default
            "plain": False,  # default
            "no_cache": False,  # default
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,  # default
            "extensions_dir": None,
            "cache_dir": None,
        }

        merged = merge_scan_config(config, cli_args)

        # Only configured values override defaults
        assert merged["delay"] == 2.5
        assert merged["quiet"] is True

        # Unconfigured values remain at defaults
        assert merged["max_retries"] == 3
        assert merged["retry_delay"] == 2.0
        assert merged["cache_max_age"] == 7
        assert merged["plain"] is False
        assert merged["workers"] == 3

    def test_merge_preserves_cli_dict(self):
        """Merging doesn't mutate the original CLI args dict."""
        config = {"scan": {"delay": 2.5}, "cache": {}, "output": {}}
        cli_args = {
            "delay": 1.5,
            "max_retries": 3,
            "retry_delay": 2.0,
            "cache_max_age": 7,
            "quiet": False,
            "plain": False,
            "no_cache": False,
            "publisher": None,
            "min_risk_level": None,
            "exclude_ids": None,
            "workers": 3,
            "extensions_dir": None,
            "cache_dir": None,
        }
        cli_args_copy = cli_args.copy()

        merged = merge_scan_config(config, cli_args)

        # Original CLI args should be unchanged
        assert cli_args == cli_args_copy
        # Merged result should differ
        assert merged["delay"] == 2.5
        assert cli_args["delay"] == 1.5


if __name__ == "__main__":
    unittest.main()
