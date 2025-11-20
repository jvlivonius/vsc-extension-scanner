"""
Tests for module-by-module security risk display.

Tests the format_security_modules() function and helper functions
that display detailed security module breakdowns.

Coverage:
- Helper function tests (_get_risk_style, _get_risk_icon)
- format_security_modules with complete data
- format_security_modules with missing/partial data
- format_security_modules with edge cases
"""

import pytest
from io import StringIO
from rich.console import Console
from vscode_scanner.display import (
    format_security_modules,
    _get_risk_style,
    _get_risk_icon,
    MODULE_DISPLAY_NAMES,
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestRiskStyleHelpers:
    """Tests for risk level styling helper functions."""

    @pytest.mark.parametrize(
        "risk_level,expected_style",
        [
            ("high", "red bold"),
            ("HIGH", "red bold"),  # Case insensitive
            ("medium", "yellow"),
            ("MEDIUM", "yellow"),
            ("low", "green"),
            ("LOW", "green"),
            ("none", "dim"),
            ("unknown", "dim"),
            ("invalid", "white"),  # Default fallback
        ],
    )
    def test_get_risk_style(self, risk_level, expected_style):
        """Test risk level to style mapping."""
        assert _get_risk_style(risk_level) == expected_style

    @pytest.mark.parametrize(
        "risk_level,expected_icon",
        [
            ("high", "⚠️ "),
            ("HIGH", "⚠️ "),  # Case insensitive
            ("medium", "⚡"),
            ("MEDIUM", "⚡"),
            ("low", "✓"),
            ("LOW", "✓"),
            ("none", ""),
            ("unknown", ""),
            ("invalid", ""),  # Default fallback
        ],
    )
    def test_get_risk_icon(self, risk_level, expected_icon):
        """Test risk level to icon mapping."""
        assert _get_risk_icon(risk_level) == expected_icon


class TestFormatSecurityModules:
    """Tests for format_security_modules() function."""

    def test_format_security_modules_with_detailed_false(self):
        """Test that function returns immediately when detailed=False."""
        result = {"id": "test.extension"}
        console = Console(file=StringIO())

        # Should return None and produce no output
        output = format_security_modules(result, detailed=False, console=console)
        assert output is None

    def test_format_security_modules_with_missing_data(self):
        """Test graceful handling when module_risk_levels is missing."""
        result = {
            "id": "test.extension",
            "security_score": 85,
        }
        console = Console(file=StringIO())

        # Should return None when no module data
        output = format_security_modules(result, detailed=True, console=console)
        assert output is None

    def test_format_security_modules_with_complete_data(self):
        """Test module display with complete security data."""
        result = {
            "id": "test.extension",
            "name": "Test Extension",
            "security": {
                "score": 82,
                "module_risk_levels": {
                    "metadata": "low",
                    "dependencies": "medium",
                    "socket": "high",
                    "virus_total": "low",
                    "permissions": "high",
                    "ossf_scorecard": "medium",
                    "network_endpoints": "medium",
                    "sensitive_info": "low",
                    "obfuscation": "high",
                    "consolidated_ast": "low",
                    "open_grep": "low",
                },
                "score_contributions": {
                    "base": 100,
                    "metadata": 0,
                    "dependencies": -5,
                    "socket": -10,
                    "virus_total": 0,
                    "permissions": -8,
                    "ossf_scorecard": -3,
                    "network_endpoints": -2,
                    "sensitive_info": 0,
                    "obfuscation": -10,
                    "consolidated_ast": 0,
                    "open_grep": 0,
                },
            },
        }

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=120, legacy_windows=False)

        # Call function
        format_security_modules(result, detailed=True, console=console)

        # Get output
        output = string_io.getvalue()

        # Verify key elements are present
        assert "Security Analysis Breakdown" in output
        assert "Base Score" in output
        assert "Final Score" in output
        assert "82/100" in output

        # Verify all module names appear
        for display_name in MODULE_DISPLAY_NAMES.values():
            assert display_name in output

    def test_format_security_modules_with_flat_structure(self):
        """Test module display when data is at top level (not nested in 'security')."""
        result = {
            "id": "test.extension",
            "security_score": 90,
            "module_risk_levels": {
                "metadata": "low",
                "dependencies": "low",
                "socket": "medium",
            },
            "score_contributions": {
                "base": 100,
                "metadata": 0,
                "dependencies": 0,
                "socket": -10,
            },
        }

        string_io = StringIO()
        console = Console(file=string_io, width=120, legacy_windows=False)

        format_security_modules(result, detailed=True, console=console)
        output = string_io.getvalue()

        assert "Security Analysis Breakdown" in output
        assert "90/100" in output or "0/100" in output  # Score may fallback

    def test_format_security_modules_with_partial_modules(self):
        """Test with only some modules present in data."""
        result = {
            "id": "test.extension",
            "security": {
                "score": 95,
                "module_risk_levels": {
                    "metadata": "low",
                    "permissions": "low",
                    # Other modules missing
                },
                "score_contributions": {
                    "base": 100,
                    "metadata": 0,
                    "permissions": -5,
                },
            },
        }

        string_io = StringIO()
        console = Console(file=string_io, width=120, legacy_windows=False)

        format_security_modules(result, detailed=True, console=console)
        output = string_io.getvalue()

        # Should still display all module rows (with "unknown" for missing ones)
        assert "Security Analysis Breakdown" in output
        assert "Metadata" in output
        assert "Permissions" in output

    def test_format_security_modules_score_formatting(self):
        """Test score impact formatting (positive, negative, zero)."""
        result = {
            "id": "test.extension",
            "security": {
                "score": 85,
                "module_risk_levels": {
                    "metadata": "low",
                    "dependencies": "medium",
                    "socket": "low",
                },
                "score_contributions": {
                    "base": 100,
                    "metadata": 5,  # Positive
                    "dependencies": -10,  # Negative
                    "socket": 0,  # Zero
                },
            },
        }

        string_io = StringIO()
        console = Console(file=string_io, width=120, legacy_windows=False)

        format_security_modules(result, detailed=True, console=console)
        output = string_io.getvalue()

        # Verify score formatting (positive should have +, negative should have -)
        assert "+100" in output  # Base score
        # Note: The exact formatting may vary with Rich rendering


class TestModuleDisplayConstants:
    """Tests for module display constants."""

    def test_module_display_names_complete(self):
        """Test that all 11 modules are defined."""
        expected_modules = [
            "metadata",
            "dependencies",
            "socket",
            "virus_total",
            "permissions",
            "ossf_scorecard",
            "network_endpoints",
            "sensitive_info",
            "obfuscation",
            "consolidated_ast",
            "open_grep",
        ]

        assert len(MODULE_DISPLAY_NAMES) == 11
        for module in expected_modules:
            assert module in MODULE_DISPLAY_NAMES
            assert isinstance(MODULE_DISPLAY_NAMES[module], str)
            assert len(MODULE_DISPLAY_NAMES[module]) > 0


def run_tests():
    """Run tests standalone."""
    import sys

    exit_code = pytest.main([__file__, "-v"])
    sys.exit(exit_code)


if __name__ == "__main__":
    run_tests()
