"""
Display components for vscan CLI using Rich library.

This module provides Rich-formatted output including progress bars, tables,
and live dashboards for the VS Code Extension Security Scanner.
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

try:
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
        TimeElapsedColumn
    )
    from rich.table import Table
    from rich.panel import Panel
    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Color scheme
COLORS = {
    'critical': 'red',
    'high': 'red',
    'medium': 'yellow',
    'low': 'green',
    'unknown': 'dim',
    'success': 'green',
    'warning': 'yellow',
    'error': 'red',
    'info': 'cyan',
    'cached': 'cyan',
    'scanning': 'blue'
}

# Risk level emojis and labels
RISK_DISPLAY = {
    'critical': ('🔴', 'CRIT'),
    'high': ('🔴', 'HIGH'),
    'medium': ('🟡', 'MED'),
    'low': ('🟢', 'LOW'),
    'unknown': ('⚪', '???')
}


def should_use_rich(plain_flag: bool = False) -> bool:
    """
    Determine if Rich output should be used.

    Args:
        plain_flag: Explicit --plain flag from CLI

    Returns:
        bool: True if Rich should be used, False for plain output
    """
    if not RICH_AVAILABLE:
        return False

    if plain_flag:
        return False

    # Don't use Rich if stdout is not a TTY (piped/redirected)
    if not sys.stdout.isatty():
        return False

    # Don't use Rich if TERM is dumb
    if os.environ.get("TERM") == "dumb":
        return False

    # Don't use Rich if NO_COLOR is set
    if os.environ.get("NO_COLOR"):
        return False

    # Don't use Rich in CI environments (common CI env vars)
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "TRAVIS"]
    if any(os.environ.get(var) for var in ci_vars):
        return False

    return True


def create_scan_progress() -> Optional[Progress]:
    """
    Create a Rich Progress bar for scanning operations.

    Returns:
        Progress instance or None if Rich not available
    """
    if not RICH_AVAILABLE:
        return None

    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        expand=True
    )


def create_results_table(scan_results: List[Dict], show_all: bool = False) -> Optional[Table]:
    """
    Create a Rich table for scan results.

    Args:
        scan_results: List of extension scan results
        show_all: If False, limit to first 10 results

    Returns:
        Table instance or None if Rich not available
    """
    if not RICH_AVAILABLE:
        return None

    table = Table(title="Scan Results", show_header=True, header_style="bold cyan")

    table.add_column("Extension", style="white", no_wrap=False, max_width=35)
    table.add_column("Version", style="cyan", no_wrap=True, width=12)
    table.add_column("Publisher", style="white", no_wrap=False, max_width=20)
    table.add_column("Risk", justify="center", width=9)
    table.add_column("Score", justify="right", width=7)
    table.add_column("Vulns", justify="right", width=6)

    # Define risk hierarchy for sorting (higher number = higher priority)
    risk_hierarchy = {
        'critical': 3,
        'high': 2,
        'medium': 1,
        'low': 0,
        'unknown': -1
    }

    # Sort results by risk level (descending) then by vulnerability count (descending)
    def sort_key(result):
        security = result.get('security', {})
        risk_level = (security.get('risk_level') or result.get('risk_level', 'unknown')).lower()
        vulns = security.get('vulnerabilities') or result.get('vulnerabilities', {})
        vuln_count = vulns.get('count', 0) if isinstance(vulns, dict) else 0

        risk_priority = risk_hierarchy.get(risk_level, -1)
        return (-risk_priority, -vuln_count)  # Negative for descending order

    sorted_results = sorted(scan_results, key=sort_key)

    # Limit results if show_all is False
    results_to_show = sorted_results if show_all else sorted_results[:10]
    remaining_count = len(sorted_results) - len(results_to_show)

    for result in results_to_show:
        # Get security data (handle both flat and nested structures)
        # OutputFormatter nests data in 'security' dict, but raw results are flat
        security = result.get('security', {})
        risk_level = (security.get('risk_level') or result.get('risk_level', 'unknown')).lower()
        vulns = security.get('vulnerabilities') or result.get('vulnerabilities', {})
        score = security.get('score') or result.get('security_score', 0)

        # Format risk level
        emoji, label = RISK_DISPLAY.get(risk_level, RISK_DISPLAY['unknown'])
        risk_display = f"{emoji} {label}"

        # Get vulnerability count
        vuln_count = vulns.get('count', 0) if isinstance(vulns, dict) else 0

        # Format extension name and version separately
        ext_name = result.get('display_name') or result.get('name', 'Unknown')
        ext_version = result.get('version', 'N/A')

        # Format security score
        score_display = f"{score}/100" if score else "N/A"

        # Get publisher information (handle both nested and flat structures)
        metadata = result.get('metadata', {})
        publisher_info = metadata.get('publisher', {})

        # Extract publisher name (handle dict or string)
        publisher_name = publisher_info.get('name') if isinstance(publisher_info, dict) else None
        if not publisher_name:
            # Fallback to top-level publisher field
            pub_field = result.get('publisher', 'Unknown')
            if isinstance(pub_field, dict):
                publisher_name = pub_field.get('name', 'Unknown')
            else:
                publisher_name = pub_field if pub_field else 'Unknown'

        # Get verification status (check metadata first, then top-level publisher)
        is_verified = publisher_info.get('verified', False) if isinstance(publisher_info, dict) else False
        if not is_verified:
            pub_field = result.get('publisher', {})
            if isinstance(pub_field, dict):
                is_verified = pub_field.get('verified', False)

        # Format publisher display with verification indicator
        if is_verified:
            publisher_display = f"{publisher_name} [green]✓[/green]"
        else:
            publisher_display = publisher_name

        # Add row with color based on risk
        table.add_row(
            ext_name,
            ext_version,
            publisher_display,
            risk_display,
            score_display,
            str(vuln_count)
        )

    # Add "more" row if needed
    if remaining_count > 0:
        table.add_row(
            f"... ({remaining_count} more)",
            "",  # Version column
            "",  # Publisher column
            "",  # Risk column
            "",  # Score column
            "",  # Vulns column
            style="dim"
        )

    return table


def create_cache_stats_table(stats: Dict) -> Optional[Table]:
    """
    Create a Rich table for cache statistics.

    Args:
        stats: Cache statistics dictionary

    Returns:
        Table instance or None if Rich not available
    """
    if not RICH_AVAILABLE:
        return None

    table = Table(show_header=True, header_style="bold cyan", title="Cache Statistics")

    table.add_column("Metric", style="white", no_wrap=True)
    table.add_column("Count", justify="right", style="green")
    table.add_column("Details", style="dim")

    # Basic stats
    from_cache = stats.get('from_cache', 0)
    fresh_scans = stats.get('fresh_scans', 0)
    total = from_cache + fresh_scans
    cache_hit_rate = (from_cache / total * 100) if total > 0 else 0

    table.add_row("From Cache", str(from_cache), "⚡ instant")
    table.add_row("Fresh Scans", str(fresh_scans), "🔍 API calls")
    table.add_row("Cache Hit Rate", f"{cache_hit_rate:.1f}%", "")

    return table


def create_filter_summary_table(args, original_count: int, filtered_count: int) -> Optional[Table]:
    """
    Create a table showing active filters and their effect.

    Args:
        args: Parsed CLI arguments
        original_count: Total extensions discovered
        filtered_count: Extensions after filtering

    Returns:
        Table instance or None if Rich not available
    """
    if not RICH_AVAILABLE:
        return None

    active_filters = []

    if args.publisher:
        active_filters.append(("Publisher", args.publisher))
    if args.include_ids:
        active_filters.append(("Include IDs", args.include_ids))
    if args.exclude_ids:
        active_filters.append(("Exclude IDs", args.exclude_ids))
    if args.min_risk_level:
        active_filters.append(("Min Risk", args.min_risk_level))

    if not active_filters:
        return None

    table = Table(show_header=True, header_style="bold yellow", title="Active Filters")
    table.add_column("Filter", style="yellow")
    table.add_column("Value", style="white")

    for filter_name, filter_value in active_filters:
        table.add_row(filter_name, str(filter_value))

    # Add summary row
    excluded = original_count - filtered_count
    table.add_row("", "", end_section=True)
    table.add_row("Result", f"{filtered_count} of {original_count} extensions selected")

    if excluded > 0:
        table.add_row("", f"({excluded} filtered out)", style="dim")

    return table


class ScanDashboard:
    """
    Real-time dashboard for scan progress.

    Displays live status including current extension, progress,
    results so far, and cache performance.
    """

    def __init__(self, total_extensions: int):
        """
        Initialize the dashboard.

        Args:
            total_extensions: Total number of extensions to scan
        """
        self.total = total_extensions
        self.current = 0
        self.current_extension = ""
        self.current_progress = ""
        self.clean_count = 0
        self.issues_count = 0
        self.error_count = 0
        self.cached_count = 0
        self.fresh_count = 0
        self.start_time = datetime.now()

    def update(self, **kwargs):
        """
        Update dashboard state.

        Args:
            **kwargs: State variables to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def generate_panel(self) -> Panel:
        """
        Generate the dashboard panel for display.

        Returns:
            Panel: Rich Panel with dashboard content
        """
        if not RICH_AVAILABLE:
            return None

        content = Text()

        # Progress percentage
        progress_pct = (self.current / self.total * 100) if self.total > 0 else 0

        # Header
        content.append(f"Status: Scanning ({self.current}/{self.total} complete)\n", style="bold white")

        # Progress bar (text-based)
        bar_width = 40
        filled = int(bar_width * progress_pct / 100)
        bar = "━" * filled + "─" * (bar_width - filled)
        content.append(f"{bar} {progress_pct:.0f}%\n\n", style="cyan")

        # Current extension
        if self.current_extension:
            content.append("📦 Current Extension:\n", style="cyan")
            content.append(f"   {self.current_extension}\n\n", style="white")

        # Current progress detail
        if self.current_progress:
            content.append("🔄 Progress: ", style="cyan")
            content.append(f"{self.current_progress}\n\n", style="yellow")

        content.append("─" * 50 + "\n\n")

        # Results so far
        content.append("📊 Results So Far:\n", style="cyan")
        content.append(f"   ✓ Clean Extensions: {self.clean_count}\n", style="green")
        content.append(f"   ⚠ Issues Found: {self.issues_count}\n", style="yellow")
        content.append(f"   ✗ Scan Errors: {self.error_count}\n\n", style="red")

        # Cache stats
        content.append("💾 Cache Performance:\n", style="cyan")
        total_processed = self.cached_count + self.fresh_count
        cache_pct = (self.cached_count / total_processed * 100) if total_processed > 0 else 0
        content.append(f"   ⚡ From Cache: {self.cached_count} ({cache_pct:.0f}%)\n", style="green")
        content.append(f"   🔍 Fresh Scans: {self.fresh_count}\n", style="blue")

        # Elapsed time
        elapsed = (datetime.now() - self.start_time).total_seconds()
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        content.append(f"\n⏱  Elapsed: {elapsed_min}m {elapsed_sec}s", style="dim")

        return Panel(content, title="VS Code Security Scan", border_style="blue", expand=False)


def display_summary(results: Dict, duration: float, use_rich: bool = True) -> None:
    """
    Display final scan summary.

    Args:
        results: Scan results dictionary
        duration: Scan duration in seconds
        use_rich: Whether to use Rich formatting
    """
    summary = results.get('summary', {})
    cache_stats = results.get('cache_stats', {})

    total = summary.get('total_extensions_scanned', 0)
    vulns = summary.get('vulnerabilities_found', 0)

    if use_rich and RICH_AVAILABLE:
        console = Console()

        # Create summary panel
        content = Text()
        content.append(f"✓ Successfully scanned {total} extensions\n", style="green bold")

        if vulns > 0:
            content.append(f"⚠ Found {vulns} vulnerabilities\n", style="yellow bold")
        else:
            content.append("✓ No vulnerabilities found\n", style="green")

        # Cache stats
        from_cache = cache_stats.get('from_cache', 0)
        fresh = cache_stats.get('fresh_scans', 0)
        hit_rate = cache_stats.get('cache_hit_rate', 0)

        content.append(f"\n⚡ Cache hit rate: {hit_rate:.1f}%\n", style="cyan")

        # Duration
        duration_min = int(duration // 60)
        duration_sec = int(duration % 60)
        if duration_min > 0:
            content.append(f"⏱  Duration: {duration_min}m {duration_sec}s\n", style="dim")
        else:
            content.append(f"⏱  Duration: {duration:.1f}s\n", style="dim")

        panel = Panel(content, title="Scan Complete", border_style="green", expand=False)
        console.print(panel)
    else:
        # Plain output (fallback)
        print("\n" + "=" * 60)
        print(f"[✓] Scan Complete!")
        print(f"Total extensions scanned: {total}")
        if vulns > 0:
            print(f"⚠  Vulnerabilities found: {vulns}")
        else:
            print("✓  No vulnerabilities found")
        print(f"Duration: {duration:.1f}s")
        print("=" * 60)


def display_error(message: str, use_rich: bool = True) -> None:
    """
    Display an error message.

    Args:
        message: Error message
        use_rich: Whether to use Rich formatting
    """
    if use_rich and RICH_AVAILABLE:
        console = Console()
        console.print(f"[bold red]✗ Error:[/bold red] {message}")
    else:
        print(f"✗ Error: {message}")


def display_warning(message: str, use_rich: bool = True) -> None:
    """
    Display a warning message.

    Args:
        message: Warning message
        use_rich: Whether to use Rich formatting
    """
    if use_rich and RICH_AVAILABLE:
        console = Console()
        console.print(f"[bold yellow]⚠ Warning:[/bold yellow] {message}")
    else:
        print(f"⚠ Warning: {message}")


def display_info(message: str, use_rich: bool = True) -> None:
    """
    Display an info message.

    Args:
        message: Info message
        use_rich: Whether to use Rich formatting
    """
    if use_rich and RICH_AVAILABLE:
        console = Console()
        console.print(f"[cyan]ℹ[/cyan] {message}")
    else:
        print(f"ℹ {message}")


def display_success(message: str, use_rich: bool = True) -> None:
    """
    Display a success message.

    Args:
        message: Success message
        use_rich: Whether to use Rich formatting
    """
    if use_rich and RICH_AVAILABLE:
        console = Console()
        console.print(f"[bold green]✓[/bold green] {message}")
    else:
        print(f"✓ {message}")
