"""
Base Component for HTML Report Generation.

Provides common utilities and abstract interface for all report components.
"""

import html
from abc import ABC, abstractmethod
from typing import Any, Dict
from .._version import __version__


class BaseComponent(ABC):
    """
    Abstract base class for HTML report components.

    Provides common utility methods for HTML escaping, styling, and rendering.
    All component classes should inherit from this base and implement render().
    """

    def __init__(self):
        """Initialize base component with version information."""
        self.version = __version__

    @abstractmethod
    def render(self, *args, **kwargs) -> str:
        """
        Render the component as HTML string.

        This method must be implemented by all subclasses.

        Returns:
            HTML string for this component
        """
        pass

    def _safe_escape(self, value: Any, default: str = "N/A", quote: bool = True) -> str:
        """
        Safely escape HTML, handling None values.

        Args:
            value: Value to escape (any type)
            default: Default value if None (default: "N/A")
            quote: Whether to quote attribute values (default: True)

        Returns:
            HTML-escaped string
        """
        if value is None:
            return default
        return html.escape(str(value), quote=quote)

    def _get_gauge_color_class(self, score: int) -> str:
        """
        Get CSS class for gauge color based on score.

        Args:
            score: Score value (0-100)

        Returns:
            CSS class name: gauge-success (75+), gauge-warning (50-74), or gauge-danger (<50)
        """
        if score >= 75:
            return "gauge-success"
        elif score >= 50:
            return "gauge-warning"
        else:
            return "gauge-danger"

    def _get_risk_level_class(self, risk_level: str) -> str:
        """
        Get CSS class for risk level badge.

        Args:
            risk_level: Risk level string (critical/high/medium/low)

        Returns:
            CSS class name for the risk level
        """
        risk_level_lower = risk_level.lower() if risk_level else "unknown"
        return f"risk-badge risk-{risk_level_lower}"

    def _format_number(self, num: int) -> str:
        """
        Format large numbers with K/M/B suffixes.

        Args:
            num: Number to format

        Returns:
            Formatted string (e.g., 187936883 -> 187.9M)
        """
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
