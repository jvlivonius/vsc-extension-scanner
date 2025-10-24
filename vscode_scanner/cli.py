"""
CLI module for vscan using Typer framework.

This module provides a modern CLI interface with subcommands,
organized help, and Rich formatting support.
"""

import sys
from typing import Optional
from pathlib import Path

try:
    import typer
    from rich.console import Console
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False

from ._version import __version__
from .scanner import run_scan
from .cache_manager import CacheManager
from .display import (
    should_use_rich, create_cache_stats_table,
    display_error, display_success, display_info,
    RICH_AVAILABLE
)

# Create Typer app
if TYPER_AVAILABLE:
    app = typer.Typer(
        name="vscan",
        help="🔍 VS Code Extension Security Scanner - Audit installed extensions using vscan.dev",
        add_completion=False,
        rich_markup_mode="rich" if RICH_AVAILABLE else None,
        no_args_is_help=True
    )

    # Create cache subcommand group
    cache_app = typer.Typer(
        name="cache",
        help="Manage scan result cache",
        add_completion=False,
        rich_markup_mode="rich" if RICH_AVAILABLE else None,
        no_args_is_help=True
    )
    app.add_typer(cache_app, name="cache")
else:
    # Fallback if Typer is not available
    app = None
    cache_app = None


def bounded_int_validator(value: int, min_val: int, max_val: int, name: str) -> int:
    """Validate integer is within bounds."""
    if value < min_val or value > max_val:
        raise typer.BadParameter(f"{name} must be between {min_val} and {max_val}")
    return value


def bounded_float_validator(value: float, min_val: float, max_val: float, name: str) -> float:
    """Validate float is within bounds."""
    if value < min_val or value > max_val:
        raise typer.BadParameter(f"{name} must be between {min_val} and {max_val}")
    return value


@app.command()
def scan(
    # Output options
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file path (.json or .html)",
        rich_help_panel="Options"
    ),

    # Display options
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Minimal output (only show single-line summary)",
        rich_help_panel="Options"
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Disable colors and rich formatting (for CI/scripts)",
        rich_help_panel="Options"
    ),

    # Filtering options
    publisher: Optional[str] = typer.Option(
        None,
        "--publisher",
        help="Only scan extensions from this publisher (case-insensitive)",
        rich_help_panel="Filtering Options"
    ),
    include_ids: Optional[str] = typer.Option(
        None,
        "--include-ids",
        help="Comma-separated list of extension IDs to scan",
        rich_help_panel="Filtering Options"
    ),
    exclude_ids: Optional[str] = typer.Option(
        None,
        "--exclude-ids",
        help="Comma-separated list of extension IDs to exclude from scan",
        rich_help_panel="Filtering Options"
    ),
    min_risk_level: Optional[str] = typer.Option(
        None,
        "--min-risk-level",
        help="Minimum risk level to include in results (low, medium, high, critical)",
        rich_help_panel="Filtering Options"
    ),

    # Advanced options
    extensions_dir: Optional[Path] = typer.Option(
        None,
        "--extensions-dir", "-d",
        help="Path to VS Code extensions directory (auto-detected if not specified)",
        rich_help_panel="Advanced Options"
    ),
    delay: float = typer.Option(
        1.5,
        "--delay", "-t",
        min=0.1,
        max=30.0,
        help="Delay between API requests in seconds",
        rich_help_panel="Advanced Options"
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        min=0,
        max=10,
        help="Maximum retry attempts for failed API requests",
        rich_help_panel="Advanced Options"
    ),
    retry_delay: float = typer.Option(
        2.0,
        "--retry-delay",
        min=0.1,
        max=60.0,
        help="Base delay for exponential backoff on retries (seconds)",
        rich_help_panel="Advanced Options"
    ),

    # Cache options
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable caching (always perform fresh scans)",
        rich_help_panel="Cache Options"
    ),
    refresh_cache: bool = typer.Option(
        False,
        "--refresh-cache",
        help="Force refresh of scanned extensions (ignore cached results for filtered extensions)",
        rich_help_panel="Cache Options"
    ),
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        help="Custom cache directory path (default: ~/.vscan/)",
        rich_help_panel="Cache Options"
    ),
    cache_max_age: int = typer.Option(
        7,
        "--cache-max-age",
        min=1,
        max=365,
        help="Maximum age of cached results in days",
        rich_help_panel="Cache Options"
    ),
):
    """
    Scan installed VS Code extensions for security vulnerabilities.

    Discovers installed VS Code extensions and analyzes them using vscan.dev
    to identify potential security risks, vulnerabilities, and suspicious patterns.

    [bold cyan]Examples:[/bold cyan]

        [dim]# Scan all extensions with default settings[/dim]
        $ vscan scan

        [dim]# Filter by publisher[/dim]
        $ vscan scan --publisher microsoft

        [dim]# Generate HTML report[/dim]
        $ vscan scan --output report.html

        [dim]# Use plain output for CI/CD pipelines[/dim]
        $ vscan scan --plain --output results.json

        [dim]# Minimal output for scripting[/dim]
        $ vscan scan --quiet

        [dim]# Scan specific extensions only[/dim]
        $ vscan scan --include-ids "ms-python.python,esbenp.prettier-vscode"
    """
    # Validate parameters
    try:
        delay = bounded_float_validator(delay, 0.1, 30.0, "delay")
        max_retries = bounded_int_validator(max_retries, 0, 10, "max-retries")
        retry_delay = bounded_float_validator(retry_delay, 0.1, 60.0, "retry-delay")
        cache_max_age = bounded_int_validator(cache_max_age, 1, 365, "cache-max-age")
    except typer.BadParameter as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)

    # Validate risk level if provided
    if min_risk_level and min_risk_level not in ['low', 'medium', 'high', 'critical']:
        typer.echo("Error: min-risk-level must be one of: low, medium, high, critical", err=True)
        raise typer.Exit(code=2)

    # Validate conflicting options
    if no_cache and refresh_cache:
        typer.echo("Error: --no-cache and --refresh-cache cannot be used together", err=True)
        raise typer.Exit(code=2)

    # Convert Path objects to strings for scanner
    extensions_dir_str = str(extensions_dir.resolve()) if extensions_dir else None
    output_str = str(output.resolve()) if output else None
    cache_dir_str = str(cache_dir.resolve()) if cache_dir else None

    # Run the scan
    try:
        exit_code = run_scan(
            extensions_dir=extensions_dir_str,
            output=output_str,
            delay=delay,
            max_retries=max_retries,
            retry_delay=retry_delay,
            cache_dir=cache_dir_str,
            cache_max_age=cache_max_age,
            refresh_cache=refresh_cache,
            no_cache=no_cache,
            publisher=publisher,
            include_ids=include_ids,
            exclude_ids=exclude_ids,
            min_risk_level=min_risk_level,
            plain=plain,
            quiet=quiet
        )
        raise typer.Exit(code=exit_code)
    except (typer.Exit, SystemExit):
        # Let these propagate naturally (they're expected exit mechanisms)
        raise
    except KeyboardInterrupt:
        typer.echo("\n\nScan interrupted by user", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        typer.echo(f"\n\nUnexpected error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=2)


@cache_app.command("stats")
def cache_stats(
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        help="Custom cache directory path (default: ~/.vscan/)"
    ),
    cache_max_age: int = typer.Option(
        7,
        "--cache-max-age",
        min=1,
        max=365,
        help="Age threshold in days for stale entries"
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Disable colors and rich formatting"
    ),
):
    """
    Display cache statistics and health information.

    Shows detailed information about cached scan results including:
    - Total number of cached entries
    - Database size
    - Age distribution of cached entries
    - Risk level breakdown
    - Extensions with vulnerabilities

    [bold cyan]Examples:[/bold cyan]

        [dim]# Show cache statistics with default settings[/dim]
        $ vscan cache stats

        [dim]# Check for stale entries older than 14 days[/dim]
        $ vscan cache stats --cache-max-age 14

        [dim]# Show stats with plain output (no colors)[/dim]
        $ vscan cache stats --plain
    """
    try:
        # Validate parameter
        cache_max_age = bounded_int_validator(cache_max_age, 1, 365, "cache-max-age")
    except typer.BadParameter as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)

    cache_dir_str = str(cache_dir.resolve()) if cache_dir else None
    use_rich = should_use_rich(plain_flag=plain)

    try:
        cache_manager = CacheManager(cache_dir=cache_dir_str)
        stats = cache_manager.get_cache_stats(max_age_days=cache_max_age)

        if use_rich and RICH_AVAILABLE:
            console = Console()

            # Display cache stats table
            table = create_cache_stats_table(stats)
            if table:
                console.print(table)

            # Additional stats
            console.print()
            console.print(f"[cyan]Database:[/cyan] {stats.get('database_path', 'N/A')}")
            console.print(f"[cyan]Total entries:[/cyan] {stats.get('total_entries', 0)}")
            console.print(f"[cyan]Database size:[/cyan] {stats.get('database_size', 'N/A')}")

            # Age distribution
            if 'age_distribution' in stats:
                console.print()
                console.print("[cyan]Age Distribution:[/cyan]")
                age_dist = stats['age_distribution']
                for category, count in age_dist.items():
                    console.print(f"  {category}: {count}")

            # Risk breakdown
            if 'risk_breakdown' in stats:
                console.print()
                console.print("[cyan]Risk Breakdown:[/cyan]")
                for risk, count in stats['risk_breakdown'].items():
                    console.print(f"  {risk}: {count}")

            # Vulnerabilities
            vuln_count = stats.get('extensions_with_vulnerabilities', 0)
            if vuln_count > 0:
                console.print()
                console.print(f"[yellow]Extensions with vulnerabilities:[/yellow] {vuln_count}")
        else:
            # Plain output
            print("Cache Statistics")
            print("=" * 60)
            print(f"Database: {stats.get('database_path', 'N/A')}")
            print(f"Total entries: {stats.get('total_entries', 0)}")
            print(f"Database size: {stats.get('database_size', 'N/A')}")

            if 'age_distribution' in stats:
                print()
                print("Age Distribution:")
                for category, count in stats['age_distribution'].items():
                    print(f"  {category}: {count}")

            if 'risk_breakdown' in stats:
                print()
                print("Risk Breakdown:")
                for risk, count in stats['risk_breakdown'].items():
                    print(f"  {risk}: {count}")

            vuln_count = stats.get('extensions_with_vulnerabilities', 0)
            if vuln_count > 0:
                print()
                print(f"Extensions with vulnerabilities: {vuln_count}")

            print("=" * 60)

        raise typer.Exit(code=0)

    except (typer.Exit, SystemExit):
        # Let these propagate naturally
        raise
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)


@cache_app.command("clear")
def cache_clear(
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        help="Custom cache directory path (default: ~/.vscan/)"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt"
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Disable colors and rich formatting"
    ),
):
    """
    Clear all cached scan results.

    This will remove all cached extension data, forcing fresh scans
    on the next run. This is useful when you want to ensure the most
    up-to-date security information.

    [bold yellow]⚠ Warning:[/bold yellow] This action cannot be undone.

    [bold cyan]Examples:[/bold cyan]

        [dim]# Clear cache with confirmation prompt[/dim]
        $ vscan cache clear

        [dim]# Clear cache without confirmation[/dim]
        $ vscan cache clear --force

        [dim]# Clear custom cache directory[/dim]
        $ vscan cache clear --cache-dir /custom/path
    """
    cache_dir_str = str(cache_dir.resolve()) if cache_dir else None
    use_rich = should_use_rich(plain_flag=plain)

    try:
        # Confirm before clearing unless --force is used
        if not force:
            confirm = typer.confirm("Are you sure you want to clear all cached data?")
            if not confirm:
                if use_rich:
                    display_info("Operation cancelled", use_rich=True)
                else:
                    print("Operation cancelled")
                raise typer.Exit(code=1)

        cache_manager = CacheManager(cache_dir=cache_dir_str)
        count = cache_manager.clear_cache()

        if use_rich:
            display_success(f"Cleared {count} cache entries", use_rich=True)
        else:
            print(f"✓ Cleared {count} cache entries")

        raise typer.Exit(code=0)

    except (typer.Exit, SystemExit):
        # Let these propagate naturally
        raise
    except Exception as e:
        if use_rich:
            display_error(f"Error clearing cache: {e}", use_rich=True)
        else:
            print(f"Error clearing cache: {e}")
        raise typer.Exit(code=2)


@app.command("report")
def report(
    output: Path = typer.Argument(
        ...,
        help="Output file path (.json or .html)",
        exists=False
    ),
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        help="Custom cache directory path (default: ~/.vscan/)"
    ),
    cache_max_age: int = typer.Option(
        365,
        "--cache-max-age",
        min=1,
        max=365,
        help="Maximum age of cached data to include (days)"
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Disable colors and rich formatting"
    ),
):
    """
    Generate a report from cached scan results without performing new scans.

    This command creates JSON or HTML reports using only data that is already
    cached from previous scans. No API calls are made, so this is very fast.
    The output format is determined by the file extension (.json or .html).

    [bold yellow]Note:[/bold yellow] Only cached data is used. Run 'vscan scan' first
    to populate the cache with scan results.

    [bold cyan]Examples:[/bold cyan]

        [dim]# Generate HTML report from cached data[/dim]
        $ vscan report security-report.html

        [dim]# Generate JSON report from last 30 days of cached data[/dim]
        $ vscan report report.json --cache-max-age 30

        [dim]# Generate report from custom cache directory[/dim]
        $ vscan report report.html --cache-dir /custom/path
    """
    from .cache_manager import CacheManager
    from .output_formatter import OutputFormatter
    from .html_report_generator import HTMLReportGenerator
    from .utils import validate_path, safe_mkdir

    use_rich = should_use_rich(plain_flag=plain)

    try:
        # Validate parameter
        cache_max_age = bounded_int_validator(cache_max_age, 1, 365, "cache-max-age")
    except typer.BadParameter as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)

    # Convert paths to strings
    cache_dir_str = str(cache_dir.resolve()) if cache_dir else None
    output_str = str(output.resolve())

    # Validate output path
    try:
        validate_path(output_str, allow_absolute=True, path_type="output file")
        # Create parent directory if needed
        output_parent = Path(output_str).parent
        safe_mkdir(output_parent)
    except (ValueError, PermissionError) as e:
        if use_rich:
            display_error(f"Invalid output path: {e}", use_rich=True)
        else:
            print(f"Error: Invalid output path: {e}")
        raise typer.Exit(code=2)

    # Determine output format from extension
    output_path = Path(output_str)
    output_format = output_path.suffix.lower()

    if output_format not in ['.json', '.html']:
        if use_rich:
            display_error("Output file must have .json or .html extension", use_rich=True)
        else:
            print("Error: Output file must have .json or .html extension")
        raise typer.Exit(code=2)

    try:
        # Notify user that we're using cache only
        if use_rich:
            display_info("Generating report from cached data only (no new scans will be performed)", use_rich=True)
        else:
            print("ℹ Generating report from cached data only (no new scans will be performed)")

        # Retrieve all cached results
        cache_manager = CacheManager(cache_dir=cache_dir_str)
        cached_results = cache_manager.get_all_cached_results(max_age_days=cache_max_age)

        if not cached_results:
            if use_rich:
                display_warning(
                    f"No cached data found (max age: {cache_max_age} days). "
                    "Run 'vscan scan' first to populate the cache.",
                    use_rich=True
                )
            else:
                print(f"⚠ Warning: No cached data found (max age: {cache_max_age} days). "
                      "Run 'vscan scan' first to populate the cache.")
            raise typer.Exit(code=1)

        # Show cache statistics
        if use_rich:
            display_info(f"Found {len(cached_results)} cached extensions", use_rich=True)
        else:
            print(f"ℹ Found {len(cached_results)} cached extensions")

        # Format output with all available data
        from datetime import datetime
        formatter = OutputFormatter()
        formatted_results = formatter.format_output(
            scan_results=cached_results,
            scan_timestamp=datetime.now().isoformat(),
            scan_duration=0.0,
            cache_stats={'from_cache': len(cached_results), 'fresh_scans': 0}
        )

        # Generate output based on format
        if output_format == '.html':
            # Generate HTML report
            html_generator = HTMLReportGenerator()
            html_content = html_generator.generate_report(formatted_results)

            with open(output_str, 'w', encoding='utf-8') as f:
                f.write(html_content)

            if use_rich:
                display_success(f"HTML report generated: {output_str}", use_rich=True)
            else:
                print(f"✓ HTML report generated: {output_str}")

        else:  # JSON
            import json
            with open(output_str, 'w', encoding='utf-8') as f:
                json.dump(formatted_results, f, indent=2, ensure_ascii=False)

            if use_rich:
                display_success(f"JSON report generated: {output_str}", use_rich=True)
            else:
                print(f"✓ JSON report generated: {output_str}")

        raise typer.Exit(code=0)

    except (typer.Exit, SystemExit):
        # Let these propagate naturally
        raise
    except Exception as e:
        if use_rich:
            display_error(f"Error generating report: {e}", use_rich=True)
        else:
            print(f"Error generating report: {e}")
        raise typer.Exit(code=2)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version", "-V",
        help="Show version information and exit"
    ),
):
    """
    🔍 VS Code Extension Security Scanner

    Audit installed VS Code extensions for security vulnerabilities using
    the vscan.dev analysis service. Discover potential risks, dependencies,
    and suspicious patterns in your installed extensions.

    Use [bold cyan]--help[/bold cyan] with any command for detailed information.
    """
    if version:
        use_rich = should_use_rich(plain_flag=False)
        if use_rich and RICH_AVAILABLE:
            console = Console()
            console.print(f"[bold cyan]vscan[/bold cyan] version [green]{__version__}[/green]")
        else:
            print(f"vscan version {__version__}")
        raise typer.Exit(code=0)

    # If no command and no version flag, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


# Fallback for when Typer is not available
def cli_fallback():
    """Fallback CLI when Typer is not installed."""
    print("Error: Typer is not installed.")
    print("Install it with: pip install 'vscode-extension-scanner[cli]'")
    sys.exit(2)


if __name__ == "__main__":
    if TYPER_AVAILABLE and app:
        app()
    else:
        cli_fallback()
