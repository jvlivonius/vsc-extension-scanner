#!/usr/bin/env python3
"""
Release Documentation Archival Script

Automates the archival of release documentation following v3.7.0 workflow:
1. Archive roadmap to docs/archive/plans/
2. Remove intermediate documents (handoffs, phase summaries)
3. Update docs/archive/README.md
4. Update docs/project/STATUS.md

Usage:
    # Preview changes (dry-run)
    python3 scripts/archive_release_docs.py v3.7.0 --dry-run

    # Execute archival with confirmations
    python3 scripts/archive_release_docs.py v3.7.0

    # Skip confirmations (after dry-run verification)
    python3 scripts/archive_release_docs.py v3.7.0 --yes

Document Naming Conventions:
    Handoff documents: v*.* *handoff.md (e.g., v3.7-phase2-handoff.md)
    Phase summaries: v*.* *summary.md (e.g., v3.7-phase1.2-completion-summary.md)
    Roadmaps: v*.* *roadmap.md (e.g., v3.7-testability-maintainability-roadmap.md)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Color:
    """ANSI color codes for terminal output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"


def info(msg: str) -> None:
    """Print info message in blue."""
    print(f"{Color.BLUE}ℹ {msg}{Color.END}")


def success(msg: str) -> None:
    """Print success message in green."""
    print(f"{Color.GREEN}✓ {msg}{Color.END}")


def warning(msg: str) -> None:
    """Print warning message in yellow."""
    print(f"{Color.YELLOW}⚠ {msg}{Color.END}")


def error(msg: str) -> None:
    """Print error message in red."""
    print(f"{Color.RED}✗ {msg}{Color.END}", file=sys.stderr)


def bold(msg: str) -> str:
    """Return bold text."""
    return f"{Color.BOLD}{msg}{Color.END}"


def confirm(msg: str) -> bool:
    """Ask user for confirmation."""
    response = input(f"{Color.YELLOW}? {msg} (y/N): {Color.END}").strip().lower()
    return response in ("y", "yes")


def run_git_command(cmd: List[str], dry_run: bool = False) -> Tuple[bool, str]:
    """
    Execute git command.

    Args:
        cmd: Git command as list
        dry_run: If True, only print command without executing

    Returns:
        Tuple of (success, output/error)
    """
    if dry_run:
        info(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
        return True, ""

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def extract_version_prefix(version: str) -> str:
    """
    Extract major.minor version prefix from full version.

    Examples:
        v3.7.0 → v3.7
        v3.6.0 → v3.6
        v2.1.3 → v2.1
    """
    match = re.match(r"(v\d+\.\d+)", version)
    if match:
        return match.group(1)
    return version  # Return as-is if pattern doesn't match


def find_matching_files(
    base_path: Path, pattern: str, version_prefix: str
) -> List[Path]:
    """
    Find files matching pattern and version prefix.

    Args:
        base_path: Directory to search
        pattern: Glob pattern with version prefix placeholder
        version_prefix: Version to match (e.g., 'v3.7')

    Returns:
        List of matching file paths
    """
    if not base_path.exists():
        return []

    # Replace placeholder with version and create glob pattern
    glob_pattern = pattern.replace("{version}", version_prefix)
    matching_files = list(base_path.glob(glob_pattern))

    # Additional filtering for more precise matching
    filtered = []
    for file in matching_files:
        if file.stem.startswith(version_prefix):
            filtered.append(file)

    return sorted(filtered)


def find_roadmap(docs_project: Path, version_prefix: str) -> List[Path]:
    """Find roadmap files for version."""
    patterns = [f"{version_prefix}-roadmap.md", f"{version_prefix}-*-roadmap.md"]

    roadmaps = []
    for pattern in patterns:
        roadmaps.extend(find_matching_files(docs_project, pattern, version_prefix))

    return roadmaps


def find_handoffs(docs_project: Path, version_prefix: str) -> List[Path]:
    """Find handoff documents for version."""
    return find_matching_files(
        docs_project, f"{version_prefix}-*handoff.md", version_prefix
    )


def find_phase_summaries(
    docs_project: Path, docs_summaries: Path, version_prefix: str
) -> List[Path]:
    """Find phase summary documents for version."""
    summaries = []

    # Search in docs/project/
    summaries.extend(
        find_matching_files(
            docs_project, f"{version_prefix}-*summary.md", version_prefix
        )
    )

    # Search in docs/archive/summaries/
    summaries.extend(
        find_matching_files(
            docs_summaries, f"{version_prefix}-*summary.md", version_prefix
        )
    )

    # Remove release notes from results (they should be kept)
    summaries = [s for s in summaries if "release-notes" not in s.stem]

    return summaries


def archive_roadmap(
    roadmap: Path, archive_plans: Path, dry_run: bool, skip_confirm: bool
) -> bool:
    """Archive roadmap to docs/archive/plans/."""
    dest_name = (
        f"{roadmap.stem}.md" if roadmap.stem.endswith("-roadmap") else roadmap.name
    )
    dest = archive_plans / dest_name

    print(f"\n{bold('Archive Roadmap:')}")
    info(f"Source: {roadmap}")
    info(f"Destination: {dest}")

    if not skip_confirm and not dry_run:
        if not confirm("Archive this roadmap?"):
            warning("Skipped by user")
            return False

    cmd = ["git", "mv", str(roadmap), str(dest)]
    success_result, output = run_git_command(cmd, dry_run)

    if success_result:
        success(
            f"Archived: {roadmap.name} → {dest.relative_to(dest.parent.parent.parent)}"
        )
        return True
    else:
        error(f"Failed to archive roadmap: {output}")
        return False


def remove_intermediate_docs(
    files: List[Path], doc_type: str, dry_run: bool, skip_confirm: bool
) -> int:
    """Remove intermediate documents."""
    if not files:
        return 0

    print(f"\n{bold(f'Remove {doc_type}:')}")
    for file in files:
        info(f"  • {file}")

    if not skip_confirm and not dry_run:
        if not confirm(f"Remove these {len(files)} {doc_type.lower()}?"):
            warning("Skipped by user")
            return 0

    removed_count = 0
    for file in files:
        cmd = ["git", "rm", str(file)]
        success_result, output = run_git_command(cmd, dry_run)

        if success_result:
            success(f"Removed: {file.name}")
            removed_count += 1
        else:
            error(f"Failed to remove {file.name}: {output}")

    return removed_count


def update_status_md(status_file: Path, version: str, dry_run: bool) -> bool:
    """Update STATUS.md to mark version as released."""
    if not status_file.exists():
        warning(f"STATUS.md not found at {status_file}")
        return False

    print(f"\n{bold('Update STATUS.md:')}")

    if dry_run:
        info("[DRY-RUN] Would update STATUS.md to mark version as released")
        return True

    content = status_file.read_text()

    # Replace "Release Ready" or similar with "Released"
    patterns = [
        (r"Release Ready", "Released"),
        (r"Phase \d+ Complete.*?- Release Ready", "Released"),
    ]

    updated = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updated = True

    if updated:
        status_file.write_text(content)
        success("Updated STATUS.md: Changed status to 'Released'")
        return True
    else:
        info("STATUS.md already up-to-date or no matching patterns found")
        return False


def print_summary(
    version: str, roadmap_count: int, handoff_count: int, summary_count: int
):
    """Print operation summary."""
    print(f"\n{bold('=== Summary ===')}")
    print(f"Version: {bold(version)}")
    print(f"Roadmaps archived: {roadmap_count}")
    print(f"Handoffs removed: {handoff_count}")
    print(f"Phase summaries removed: {summary_count}")
    print(f"Total operations: {roadmap_count + handoff_count + summary_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Automate release documentation archival",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes (recommended first step)
  python3 scripts/archive_release_docs.py v3.7.0 --dry-run

  # Execute with confirmations
  python3 scripts/archive_release_docs.py v3.7.0

  # Skip confirmations (after verifying with dry-run)
  python3 scripts/archive_release_docs.py v3.7.0 --yes

Document Types:
  Roadmaps: v3.7-*roadmap.md (archived to docs/archive/plans/)
  Handoffs: v3.7-*handoff.md (removed)
  Summaries: v3.7-*summary.md (removed, except release-notes)
        """,
    )

    parser.add_argument("version", help="Version to archive (e.g., v3.7.0)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without executing"
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompts"
    )

    args = parser.parse_args()

    # Paths
    repo_root = Path(__file__).parent.parent
    docs_project = repo_root / "docs" / "project"
    docs_archive = repo_root / "docs" / "archive"
    docs_summaries = docs_archive / "summaries"
    archive_plans = docs_archive / "plans"
    status_file = docs_project / "STATUS.md"

    # Validate paths
    if not docs_project.exists():
        error(f"docs/project/ not found at {docs_project}")
        sys.exit(1)

    if not archive_plans.exists():
        error(f"docs/archive/plans/ not found at {archive_plans}")
        sys.exit(1)

    # Extract version prefix (v3.7.0 → v3.7)
    version_prefix = extract_version_prefix(args.version)

    print(f"\n{bold('='  * 60)}")
    print(f"{bold('Release Documentation Archival')}")
    print(f"{bold('='  * 60)}")
    print(f"Version: {bold(args.version)} (prefix: {bold(version_prefix)})")
    print(f"Mode: {bold('DRY-RUN' if args.dry_run else 'EXECUTE')}")
    if args.yes:
        print(f"Confirmations: {bold('SKIPPED')}")
    print(f"{bold('='  * 60)}\n")

    if args.dry_run:
        warning("DRY-RUN MODE: No changes will be made")

    # Find documents
    info("Scanning for documents...")
    roadmaps = find_roadmap(docs_project, version_prefix)
    handoffs = find_handoffs(docs_project, version_prefix)
    summaries = find_phase_summaries(docs_project, docs_summaries, version_prefix)

    if not roadmaps and not handoffs and not summaries:
        warning(f"No documents found for version {version_prefix}")
        info("This might mean:")
        info("  • Documents already archived")
        info("  • Wrong version number")
        info("  • Documents use different naming pattern")
        sys.exit(0)

    # Display found documents
    print(f"\n{bold('Found Documents:')}")
    print(f"Roadmaps ({len(roadmaps)}):")
    for r in roadmaps:
        print(f"  • {r.relative_to(repo_root)}")

    print(f"\nHandoff documents ({len(handoffs)}):")
    for h in handoffs:
        print(f"  • {h.relative_to(repo_root)}")

    print(f"\nPhase summaries ({len(summaries)}):")
    for s in summaries:
        print(f"  • {s.relative_to(repo_root)}")

    # Confirm proceeding
    if not args.yes and not args.dry_run:
        print()
        if not confirm("Proceed with archival?"):
            info("Aborted by user")
            sys.exit(0)

    # Execute operations
    roadmap_count = 0
    handoff_count = 0
    summary_count = 0

    # Archive roadmaps
    for roadmap in roadmaps:
        if archive_roadmap(roadmap, archive_plans, args.dry_run, args.yes):
            roadmap_count += 1

    # Remove handoffs
    handoff_count = remove_intermediate_docs(
        handoffs, "Handoff Documents", args.dry_run, args.yes
    )

    # Remove phase summaries
    summary_count = remove_intermediate_docs(
        summaries, "Phase Summaries", args.dry_run, args.yes
    )

    # Update STATUS.md
    if update_status_md(status_file, args.version, args.dry_run):
        if not args.dry_run:
            cmd = ["git", "add", str(status_file)]
            run_git_command(cmd, args.dry_run)

    # Print summary
    print_summary(args.version, roadmap_count, handoff_count, summary_count)

    # Next steps
    print(f"\n{bold('=== Next Steps ===')}")
    if args.dry_run:
        info("Review the output above, then run without --dry-run to execute")
    else:
        info("Manual steps remaining:")
        info("  1. Review changes: git status")
        info("  2. Update docs/archive/README.md (add version entry)")
        info("  3. Commit: git commit -m 'docs(vX.Y): Archive release documentation'")
        info("  4. Push and create PR")

    print()


if __name__ == "__main__":
    main()
