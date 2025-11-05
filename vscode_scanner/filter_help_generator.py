#!/usr/bin/env python3
"""
Filter Help Generator Module

Responsibilities:
- Extract active filters (pure function)
- Generate help messages (pure function)
- Filter help orchestration

Layer: Application
Dependencies: None (pure functions)
"""

from typing import Any, List, Tuple


class FilterHelpGenerator:
    """
    Handles filter help message generation.

    Separates pure logic (filter extraction, message generation) from
    side effects (display, logging).
    """

    @staticmethod
    def extract_active_filters(args: Any) -> List[str]:
        """
        Extract active filters from args (pure function).

        Args:
            args: Scan configuration object

        Returns:
            List of formatted filter strings

        Examples:
            >>> class Args:
            ...     publisher = "microsoft"
            ...     include_ids = None
            ...     exclude_ids = None
            ...     min_risk_level = None
            >>> FilterHelpGenerator.extract_active_filters(Args())
            ['  --publisher: microsoft']
        """
        active_filters = []

        if hasattr(args, "publisher") and args.publisher:
            active_filters.append(f"  --publisher: {args.publisher}")

        if hasattr(args, "include_ids") and args.include_ids:
            active_filters.append(f"  --include-ids: {args.include_ids}")

        if hasattr(args, "exclude_ids") and args.exclude_ids:
            active_filters.append(f"  --exclude-ids: {args.exclude_ids}")

        if hasattr(args, "min_risk_level") and args.min_risk_level:
            active_filters.append(f"  --min-risk-level: {args.min_risk_level}")

        return active_filters

    @staticmethod
    def has_publisher_filter(args: Any) -> bool:
        """
        Check if publisher filter is active (pure function).

        Args:
            args: Scan configuration object

        Returns:
            True if publisher filter is active

        Examples:
            >>> class Args:
            ...     publisher = "microsoft"
            >>> FilterHelpGenerator.has_publisher_filter(Args())
            True
        """
        return hasattr(args, "publisher") and bool(args.publisher)

    @staticmethod
    def generate_suggestion_messages(
        original_count: int, has_publisher_filter: bool
    ) -> List[str]:
        """
        Generate helpful suggestion messages (pure function).

        Args:
            original_count: Number of extensions before filtering
            has_publisher_filter: Whether publisher filter is active

        Returns:
            List of suggestion messages

        Examples:
            >>> FilterHelpGenerator.generate_suggestion_messages(10, False)
            ['Tip: 10 extensions were found, but all were filtered out.']
            >>> messages = FilterHelpGenerator.generate_suggestion_messages(5, True)
            >>> len(messages)
            3
        """
        messages = []

        if original_count > 0:
            messages.append(
                f"Tip: {original_count} extensions were found, but all were filtered out."
            )

        if has_publisher_filter:
            messages.append(
                "Tip: Publisher names are case-insensitive but must match exactly."
            )
            messages.append("     Run without filters to see available publishers.")

        return messages
