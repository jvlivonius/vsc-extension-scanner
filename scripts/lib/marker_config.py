"""
Marker configuration module for dynamic pytest marker loading.

This module provides functionality to dynamically load pytest markers from
pyproject.toml, eliminating hardcoded marker definitions and creating a single
source of truth for test organization.

Features:
- Dynamic marker loading from pyproject.toml
- Python 3.8+ compatibility (tomllib for 3.11+, tomli for 3.8-3.10)
- Marker name normalization (underscore → hyphen standardization)
- Explicit marker categorization via marker_categories module
- Validation to ensure synchronization
- Caching for performance
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Type

# TOML parsing with fallback for older Python versions
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Python 3.8-3.10
    except ImportError:
        tomllib = None  # Should not happen with tomli dependency


# Module-level cache and category storage
_MARKERS_CACHE: Optional[Dict[str, str]] = None
_CATEGORIES_CACHE = {
    "groups": set(),
    "behavioral": set(),
}

# Meta markers (runtime-only, not in pyproject.toml)
META_MARKERS: frozenset = frozenset({"unmarked", "all"})


def parse_marker_category(description: str) -> Optional[str]:
    """
    Parse category tag from marker description.

    Extracts category tags like [GROUP] or [BEHAVIORAL] from the beginning
    of marker descriptions in pyproject.toml.

    Args:
        description: Marker description (e.g., "[GROUP] Unit tests...")

    Returns:
        Category name ("GROUP", "BEHAVIORAL") or None if no tag found

    Examples:
        >>> parse_marker_category("[GROUP] Unit tests")
        'GROUP'
        >>> parse_marker_category("[BEHAVIORAL] Slow tests")
        'BEHAVIORAL'
        >>> parse_marker_category("No tag here")
        None
    """
    if not description:
        return None

    desc = description.strip()
    if not desc.startswith("["):
        return None

    end_bracket = desc.find("]")
    if end_bracket <= 1:
        return None

    tag = desc[1:end_bracket].strip().upper()
    return tag if tag else None


def load_markers_from_pyproject() -> Dict[str, str]:
    """
    Load pytest markers from pyproject.toml.

    Returns:
        Dictionary mapping marker names to their descriptions.
        Format: {"marker-name": "Marker description"}

    Raises:
        FileNotFoundError: If pyproject.toml not found
        ValueError: If markers section not found or malformed
    """
    if tomllib is None:
        raise ImportError(
            "TOML parsing library not available. "
            "Install tomli for Python <3.11: pip install tomli"
        )

    # Navigate from scripts/lib/ to project root
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Navigate to pytest markers: tool.pytest.ini_options.markers
    markers_raw = (
        data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("markers", [])
    )

    if not markers_raw:
        raise ValueError(
            "No markers found in pyproject.toml under "
            "[tool.pytest.ini_options].markers"
        )

    # Parse "marker-name: Description" format and extract categories
    markers = {}
    groups = set()
    behavioral = set()

    for marker_def in markers_raw:
        if ":" in marker_def:
            name, desc = marker_def.split(":", 1)
            name = name.strip()
            desc = desc.strip()

            # Normalize to hyphenated format
            name = normalize_marker_name(name)
            markers[name] = desc

            # Parse category tag from description
            category = parse_marker_category(desc)
            if category == "GROUP":
                groups.add(name)
            elif category == "BEHAVIORAL":
                behavioral.add(name)
        else:
            # Marker without description
            name = marker_def.strip()
            name = normalize_marker_name(name)
            markers[name] = ""

    # Update category cache
    _CATEGORIES_CACHE["groups"] = groups
    _CATEGORIES_CACHE["behavioral"] = behavioral

    return markers


def get_markers(force_reload: bool = False) -> Dict[str, str]:
    """
    Get pytest markers with caching.

    Args:
        force_reload: If True, bypass cache and reload from pyproject.toml

    Returns:
        Dictionary mapping marker names to descriptions
    """
    global _MARKERS_CACHE  # pylint: disable=global-statement

    if _MARKERS_CACHE is None or force_reload:
        _MARKERS_CACHE = load_markers_from_pyproject()

    return _MARKERS_CACHE


def get_marker_names(force_reload: bool = False) -> Set[str]:
    """
    Get all pytest marker names.

    Args:
        force_reload: If True, bypass cache and reload markers

    Returns:
        Set of marker names
    """
    return set(get_markers(force_reload=force_reload).keys())


# Module-level accessors - these are populated when get_markers() is called
# IMPORTANT: Always call get_markers() or get_required_markers() before accessing these
def get_test_group_markers_set() -> frozenset:
    """Get test group markers. Ensures markers are loaded first."""
    if not _MARKERS_CACHE:
        get_markers()
    return frozenset(_CATEGORIES_CACHE["groups"])


def get_behavioral_markers_set() -> frozenset:
    """Get behavioral markers. Ensures markers are loaded first."""
    if not _MARKERS_CACHE:
        get_markers()
    return frozenset(_CATEGORIES_CACHE["behavioral"])


# Expose as pseudo-constants (but they're actually function calls)
# Use like: TEST_GROUP_MARKERS = get_test_group_markers_set()
TEST_GROUP_MARKERS = get_test_group_markers_set  # Function reference
BEHAVIORAL_MARKERS = get_behavioral_markers_set  # Function reference


def get_required_markers(force_reload: bool = False) -> Set[str]:
    """
    Get markers required for test discovery.

    Excludes behavioral markers that modify test execution but don't
    categorize tests (e.g., 'slow', 'property-based').

    Args:
        force_reload: If True, bypass cache and reload markers

    Returns:
        Set of required marker names for test grouping
    """
    # Ensure markers are loaded
    get_markers(force_reload=force_reload)

    # Return test group markers (which excludes behavioral markers)
    return frozenset(_CATEGORIES_CACHE["groups"])


def get_test_group_markers(force_reload: bool = False) -> Set[str]:
    """
    Get markers usable for test grouping.

    This is an alias for get_required_markers() to clarify intent when
    used for building test group enums or validating group selections.

    Args:
        force_reload: If True, bypass cache and reload markers

    Returns:
        Set of marker names suitable for test grouping
    """
    return get_required_markers(force_reload=force_reload)


def normalize_marker_name(name: str) -> str:
    """
    Normalize marker name (identity function after v3.8 standardization).

    Historically converted underscores to hyphens, but all markers now use
    underscore format consistently. Kept for API compatibility and defensive
    coding in case external code passes hyphenated names.

    Args:
        name: Marker name (underscore format standard)

    Returns:
        Marker name with hyphens converted to underscores for consistency
    """
    return name.replace("-", "_")


def is_valid_marker(name: str, force_reload: bool = False) -> bool:
    """
    Check if a marker name is valid (defined in pyproject.toml).

    Args:
        name: Marker name to validate
        force_reload: If True, bypass cache and reload markers

    Returns:
        True if marker is defined, False otherwise
    """
    normalized_name = normalize_marker_name(name)
    return normalized_name in get_marker_names(force_reload=force_reload)


def get_marker_description(name: str, force_reload: bool = False) -> Optional[str]:
    """
    Get description for a specific marker.

    Args:
        name: Marker name
        force_reload: If True, bypass cache and reload markers

    Returns:
        Marker description, or None if marker not found
    """
    normalized_name = normalize_marker_name(name)
    markers = get_markers(force_reload=force_reload)
    return markers.get(normalized_name)


def clear_cache() -> None:
    """
    Clear the marker cache.

    Useful for testing or when pyproject.toml has been modified.
    """
    global _MARKERS_CACHE  # pylint: disable=global-statement
    _MARKERS_CACHE = None


def is_test_group_marker(marker_name: str) -> bool:
    """
    Check if a marker is used for test grouping.

    Args:
        marker_name: Name of the marker to check

    Returns:
        True if marker categorizes tests, False otherwise
    """
    return marker_name in get_test_group_markers_set()


def is_behavioral_marker(marker_name: str) -> bool:
    """
    Check if a marker modifies test execution behavior.

    Args:
        marker_name: Name of the marker to check

    Returns:
        True if marker is behavioral, False otherwise
    """
    return marker_name in get_behavioral_markers_set()


def is_meta_marker(marker_name: str) -> bool:
    """
    Check if a marker is a runtime-only meta marker.

    Args:
        marker_name: Name of the marker to check

    Returns:
        True if marker is a meta marker, False otherwise
    """
    return marker_name in META_MARKERS


# Convenience function for debugging
def list_markers(verbose: bool = False) -> None:
    """
    Print all available markers.

    Args:
        verbose: If True, include descriptions
    """
    markers = get_markers()

    print(f"Available pytest markers ({len(markers)}):")
    print()

    if verbose:
        for name, desc in sorted(markers.items()):
            print(f"  {name}")
            if desc:
                print(f"    {desc}")
            print()
    else:
        for name in sorted(markers.keys()):
            print(f"  - {name}")


# ==============================================================================
# TestGroup Enum Factory
# ==============================================================================


def create_test_group_enum() -> Type[Enum]:
    """
    Factory function to create TestGroup enum with dynamic markers from pyproject.toml.

    This approach is needed because Python Enum doesn't support adding members after class definition.

    Returns:
        TestGroup Enum class with dynamic markers from pyproject.toml
    """
    from .test_utils import Colors  # Local import to avoid circular dependency

    try:
        # Get markers from pyproject.toml (GROUP markers only)
        markers = get_test_group_markers()

        # Build enum members dictionary
        members = {
            # Meta-groups (not pytest markers)
            "UNMARKED": "unmarked",  # Tests without required pytest markers
            "ALL": "all",  # Run all test groups
        }

        # Add dynamic marker members (GROUP markers only)
        for marker_name in sorted(markers):
            # Convert to valid Python identifier (markers already use underscores)
            member_name = marker_name.upper()
            members[member_name] = marker_name

        # Create enum class dynamically
        TestGroupClass = Enum("TestGroup", members)  # pylint: disable=invalid-name

        # Add helper class methods
        @classmethod
        def get_marker_groups(cls):
            """Get all test groups that correspond to pytest markers (exclude meta-groups)."""
            # pylint: disable=not-an-iterable,no-member
            return [g for g in cls if g not in (cls.UNMARKED, cls.ALL)]

        @classmethod
        def from_string(cls, value: str):
            """
            Get TestGroup from string value.

            Args:
                value: Group name (e.g., "unit", "real_api", "unmarked")

            Returns:
                TestGroup enum member, or None if not found
            """
            # Normalize to handle potential legacy hyphenated input
            normalized = normalize_marker_name(value)
            for member in cls:  # pylint: disable=not-an-iterable
                if member.value == normalized:
                    return member
            return None

        # Attach class methods
        TestGroupClass.get_marker_groups = get_marker_groups
        TestGroupClass.from_string = from_string

        return TestGroupClass

    except Exception as e:
        # Fallback to minimal enum if marker loading fails
        print(
            f"{Colors.YELLOW}Warning: Could not load markers from pyproject.toml: {e}{Colors.RESET}"
        )
        print(
            f"{Colors.YELLOW}Using minimal TestGroup enum with only meta-groups{Colors.RESET}"
        )

        class TestGroup(Enum):
            UNMARKED = "unmarked"
            ALL = "all"

            @classmethod
            def from_string(cls, value: str):
                normalized = normalize_marker_name(value)
                for member in cls:
                    if member.value == normalized:
                        return member
                return None

        return TestGroup


# ==============================================================================
# Filter Expression Parsing
# ==============================================================================


def parse_filter_expression(filter_arg: str) -> List[str]:
    """
    Parse --filter argument into pytest marker expressions.

    Args:
        filter_arg: Comma-separated filters like 'slow,not property_based'

    Returns:
        List of pytest marker expressions (OR logic)

    Examples:
        'slow' → ['slow']
        'not slow' → ['not slow']
        'slow,not property_based' → ['slow', 'not property_based']

    Raises:
        ValueError: If filter contains group markers or unknown markers
    """
    if not filter_arg:
        return []

    behavioral_markers = get_behavioral_markers_set()

    filters = []
    for item in filter_arg.split(","):
        item = item.strip()

        # Parse "not marker" format
        if item.startswith("not "):
            marker_name = item[4:].strip()
            expression = f"not {marker_name}"
        else:
            marker_name = item
            expression = item

        # Validate: only behavioral markers allowed
        if marker_name not in behavioral_markers:
            # Check if it's a group marker
            group_markers = list(get_test_group_markers())
            if marker_name in group_markers:
                raise ValueError(
                    f"Error: '{marker_name}' is a group marker. "
                    f"Use --include/--exclude for group markers, "
                    f"--filter is for behavioral markers only (e.g., slow, property_based)."
                )
            else:
                raise ValueError(
                    f"Error: Unknown marker '{marker_name}'. "
                    f"Available behavioral markers: {', '.join(sorted(behavioral_markers))}"
                )

        filters.append(expression)

    return filters
