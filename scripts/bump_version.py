#!/usr/bin/env python3
"""
Version Bump Helper Script

Automatically updates the version number in vscode_scanner/_version.py
and optionally updates documentation files.

Usage:
    python scripts/bump_version.py 2.3.0                        # Set version (manual doc update)
    python scripts/bump_version.py 2.3.0 --auto-update          # Set version + auto-update docs
    python scripts/bump_version.py 2.3.0 --validate-notes       # Set version (blocks if notes missing)
    python scripts/bump_version.py 2.3.0 --auto-update --validate-notes  # Combined flags
    python scripts/bump_version.py 2.3.0 --milestone            # Set version + create GitHub milestone
    python scripts/bump_version.py 2.3.0 --milestone --create-release-issue  # With tracking issue
    python scripts/bump_version.py --check                      # Check version consistency
    python scripts/bump_version.py --check-notes 2.3.0          # Check if release notes exist
    python scripts/bump_version.py --show                       # Show current version
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def get_version_file():
    """Get the path to the version file."""
    return Path(__file__).parent.parent / "vscode_scanner" / "_version.py"


def read_current_version():
    """Read the current version from _version.py."""
    version_file = get_version_file()
    content = version_file.read_text(encoding="utf-8")

    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find __version__ in _version.py")

    return match.group(1)


def read_schema_version():
    """Read the schema version from _version.py."""
    version_file = get_version_file()
    content = version_file.read_text(encoding="utf-8")

    match = re.search(r'SCHEMA_VERSION\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find SCHEMA_VERSION in _version.py")

    return match.group(1)


def set_version(new_version):
    """Update the version in _version.py."""
    version_file = get_version_file()
    content = version_file.read_text(encoding="utf-8")

    # Validate version format (basic semver)
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        raise ValueError(f"Invalid version format: {new_version}. Expected: X.Y.Z")

    # Update version
    new_content = re.sub(
        r'__version__\s*=\s*"[^"]+"', f'__version__ = "{new_version}"', content
    )

    version_file.write_text(new_content, encoding="utf-8")
    print(f"✓ Updated version to {new_version} in {version_file}")


def auto_update_docs(new_version):
    """Auto-update version in documentation files."""
    root = Path(__file__).parent.parent

    # Files that can be automatically updated with simple pattern replacement
    auto_update_files = {
        "README.md": [(r"(\*\*Version:\*\*\s+)\d+\.\d+\.\d+", rf"\g<1>{new_version}")],
        "CLAUDE.md": [(r"(\*\*Version:\*\*\s+)\d+\.\d+\.\d+", rf"\g<1>{new_version}")],
        "docs/project/PRD.md": [
            (r"(\*\*Version:\*\*\s+)\d+\.\d+\.\d+", rf"\g<1>{new_version}")
        ],
    }

    updated_files = []

    for doc_file, patterns in auto_update_files.items():
        full_path = root / doc_file
        if not full_path.exists():
            print(f"  ⚠ {doc_file}: File not found (skipping)")
            continue

        content = full_path.read_text(encoding="utf-8")
        modified = False

        for pattern, replacement in patterns:
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                modified = True

        if modified:
            full_path.write_text(content, encoding="utf-8")
            updated_files.append(doc_file)
            print(f"  ✓ {doc_file}: Version updated to {new_version}")

    if updated_files:
        print(f"\n✓ Auto-updated {len(updated_files)} documentation file(s)")
    else:
        print("\n⚠ No documentation files were auto-updated")

    return updated_files


def check_consistency():
    """Check that all files import from _version.py correctly and docs have consistent versions."""
    root = Path(__file__).parent.parent
    current_version = read_current_version()
    schema_version = read_schema_version()

    print(f"Current version: {current_version}")
    print(f"Schema version: {schema_version}")
    print()

    issues = []

    # === Python Files ===
    print("Python Files:")

    # Files that should import from _version
    files_to_check = [
        "vscode_scanner/__init__.py",
        "vscode_scanner/vscan.py",
        "vscode_scanner/output_formatter.py",
        "vscode_scanner/cache_manager.py",
        "vscode_scanner/html_report_generator.py",
        "vscan.py",
        "output_formatter.py",
        "cache_manager.py",
        "html_report_generator.py",
    ]

    for file_path in files_to_check:
        full_path = root / file_path
        if not full_path.exists():
            continue

        content = full_path.read_text(encoding="utf-8")

        # Check if file imports from _version
        if (
            "from vscode_scanner._version import" in content
            or "from ._version import" in content
        ):
            print(f"  ✓ {file_path}: Uses centralized version")
        else:
            # Check for hardcoded versions
            if re.search(r'VERSION\s*=\s*"[\d.]+"', content):
                issues.append(f"✗ {file_path}: Has hardcoded VERSION")
            elif re.search(r'__version__\s*=\s*"[\d.]+"', content):
                issues.append(f"✗ {file_path}: Has hardcoded __version__")
            elif re.search(r'SCHEMA_VERSION\s*=\s*"[\d.]+"', content):
                issues.append(f"✗ {file_path}: Has hardcoded SCHEMA_VERSION")

    # Check pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        if 'dynamic = ["version"]' in content:
            print(f"  ✓ pyproject.toml: Uses dynamic versioning")
        elif re.search(r'version\s*=\s*"[\d.]+"', content):
            issues.append(f"✗ pyproject.toml: Has hardcoded version")

    print()

    # === Documentation Files ===
    print("Documentation Files:")

    # Documentation files that should have consistent version numbers
    # Using standardized pattern: **Version:** X.Y.Z (no 'v' prefix)
    doc_checks = {
        "README.md": [
            (r"\*\*Version:\*\*\s+(\d+\.\d+\.\d+)", "version badge"),
        ],
        "CLAUDE.md": [
            (r"\*\*Version:\*\*\s+(\d+\.\d+\.\d+)", "Current Status version"),
        ],
        "docs/project/PRD.md": [
            (r"\*\*Version:\*\*\s+(\d+\.\d+\.\d+)", "Version field"),
        ],
    }

    for doc_file, patterns in doc_checks.items():
        full_path = root / doc_file
        if not full_path.exists():
            print(f"  ⚠ {doc_file}: File not found (skipping)")
            continue

        content = full_path.read_text(encoding="utf-8")
        file_has_issue = False

        for pattern, description in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Check if all matches are correct version
                incorrect_versions = [m for m in matches if m != current_version]
                if incorrect_versions:
                    # Show unique incorrect versions
                    unique_incorrect = list(set(incorrect_versions))
                    for wrong_ver in unique_incorrect:
                        issues.append(
                            f"✗ {doc_file}: {description} shows '{wrong_ver}' "
                            f"(expected '{current_version}')"
                        )
                    file_has_issue = True

        if not file_has_issue:
            print(f"  ✓ {doc_file}: Version {current_version} matches")

    print()

    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✓ All files use consistent versioning!")
        return True


def check_release_notes(version):
    """Check if release notes file exists for the given version."""
    root = Path(__file__).parent.parent
    notes_file = (
        root / "docs" / "archive" / "summaries" / f"v{version}-release-notes.md"
    )

    if not notes_file.exists():
        print(f"❌ ERROR: Release notes file missing for version {version}")
        print(f"   Expected: {notes_file.relative_to(root)}")
        print()
        print("📝 To create release notes:")
        print(f"   1. Copy template: docs/templates/release-notes-template.md")
        print(f"   2. Create: docs/archive/summaries/v{version}-release-notes.md")
        print(f"   3. Fill in all sections with version-specific information")
        print(f"   4. Commit the file BEFORE pushing the version tag")
        print()
        print("⚠️  The GitHub Actions release workflow requires this file to exist")
        print("   before pushing the version tag, otherwise the release will have")
        print("   only a generic message instead of comprehensive notes.")
        return False

    print(f"✓ Release notes file exists: {notes_file.relative_to(root)}")

    # Check file is not empty
    content = notes_file.read_text(encoding="utf-8")
    if len(content.strip()) < 100:  # Arbitrary minimum length
        print(f"⚠️  WARNING: Release notes file seems too short ({len(content)} chars)")
        print(f"   Expected comprehensive release notes (typically 1000+ chars)")
        return False

    print(f"✓ Release notes file has content ({len(content)} chars)")
    return True


def show_version():
    """Display the current version."""
    current_version = read_current_version()
    schema_version = read_schema_version()
    print(f"Application version: {current_version}")
    print(f"Schema version: {schema_version}")


def run_gh_command(args, capture_output=True):
    """Run a gh CLI command and return the result."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=capture_output,
            text=True,
            check=True,
        )
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: gh CLI command failed: {' '.join(args)}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("❌ ERROR: gh CLI not found. Install it from https://cli.github.com/")
        return None


def check_gh_authenticated():
    """Check if gh CLI is authenticated."""
    result = run_gh_command(["auth", "status"])
    return result is not None


def get_or_create_milestone(version):
    """Get or create a GitHub milestone for the version.

    Returns:
        str: Milestone number if successful, None otherwise
    """
    if not check_gh_authenticated():
        print("⚠️  WARNING: gh CLI not authenticated, skipping milestone creation")
        return None

    milestone_title = f"v{version}"

    # Check if milestone already exists
    print(f"Checking for milestone '{milestone_title}'...")
    result = run_gh_command(
        [
            "api",
            "repos/:owner/:repo/milestones",
            "--jq",
            f'.[] | select(.title == "{milestone_title}") | .number',
        ]
    )

    if result and result.strip():
        milestone_number = result.strip()
        print(f"  ✓ Milestone '{milestone_title}' already exists (#{milestone_number})")
        return milestone_number

    # Create new milestone
    print(f"  Creating milestone '{milestone_title}'...")
    result = run_gh_command(
        [
            "api",
            "repos/:owner/:repo/milestones",
            "-F",
            f"title={milestone_title}",
            "-F",
            f"description=Release {version}",
            "--jq",
            ".number",
        ]
    )

    if result:
        print(f"  ✓ Created milestone '{milestone_title}' (#{result})")
        return result
    else:
        print(f"  ❌ Failed to create milestone '{milestone_title}'")
        return None


def create_release_issue(version, milestone_number=None):
    """Create a release tracking issue.

    Args:
        version: Version number (e.g., "3.8.0")
        milestone_number: Optional milestone number to link to

    Returns:
        str: Issue number if successful, None otherwise
    """
    if not check_gh_authenticated():
        print("⚠️  WARNING: gh CLI not authenticated, skipping release issue creation")
        return None

    print(f"Creating release tracking issue for v{version}...")

    # Read the release issue template
    root = Path(__file__).parent.parent
    template_file = root / ".github" / "ISSUE_TEMPLATE" / "release.md"

    if not template_file.exists():
        print(f"  ❌ Release issue template not found: {template_file}")
        return None

    template_content = template_file.read_text(encoding="utf-8")

    # Replace version placeholders in template
    issue_body = template_content.replace("vX.Y.Z", f"v{version}")
    issue_body = issue_body.replace("X.Y.Z", version)
    issue_body = issue_body.replace("YYYY-MM-DD", "TBD")  # User will fill in dates

    # Remove the frontmatter (YAML between ---) for issue body
    issue_body = re.sub(r"^---\n.*?---\n", "", issue_body, flags=re.DOTALL)

    # Create the issue
    args = [
        "issue",
        "create",
        "--title",
        f"[RELEASE] v{version}",
        "--body",
        issue_body,
        "--label",
        "release,P1-high",
    ]

    if milestone_number:
        args.extend(["--milestone", f"v{version}"])

    result = run_gh_command(args)

    if result:
        # Extract issue number from URL (gh returns URL)
        match = re.search(r"/issues/(\d+)$", result)
        if match:
            issue_number = match.group(1)
            print(f"  ✓ Created release tracking issue: #{issue_number}")
            print(f"    {result}")
            return issue_number
        else:
            print(f"  ✓ Created release tracking issue")
            print(f"    {result}")
            return "created"
    else:
        print(f"  ❌ Failed to create release tracking issue")
        return None


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--check":
        success = check_consistency()
        sys.exit(0 if success else 1)
    elif arg == "--check-notes":
        if len(sys.argv) < 3:
            print("Error: --check-notes requires a version number")
            print("Usage: python scripts/bump_version.py --check-notes X.Y.Z")
            sys.exit(1)
        version = sys.argv[2]
        success = check_release_notes(version)
        sys.exit(0 if success else 1)
    elif arg == "--show":
        show_version()
    elif arg.startswith("--"):
        print(f"Unknown option: {arg}")
        print(__doc__)
        sys.exit(1)
    else:
        # Treat as version number
        try:
            # Check for flags
            auto_update = False
            validate_notes = False
            create_milestone = False
            create_issue = False
            for i in range(2, len(sys.argv)):
                if sys.argv[i] == "--auto-update":
                    auto_update = True
                elif sys.argv[i] == "--validate-notes":
                    validate_notes = True
                elif sys.argv[i] == "--milestone":
                    create_milestone = True
                elif sys.argv[i] == "--create-release-issue":
                    create_issue = True

            # Check release notes exist if validation requested
            if validate_notes:
                print("Checking for release notes...")
                if not check_release_notes(arg):
                    print()
                    print("❌ Version bump aborted: Release notes validation failed")
                    print("   Create the release notes file and try again.")
                    sys.exit(1)
                print()

            # Update _version.py
            set_version(arg)

            # Auto-update documentation files if flag is set
            if auto_update:
                print("\nAuto-updating documentation files:")
                auto_update_docs(arg)

            # Create or get milestone if requested
            milestone_number = None
            if create_milestone:
                print("\nGitHub Milestone:")
                milestone_number = get_or_create_milestone(arg)

            # Create release tracking issue if requested
            if create_issue:
                if not milestone_number and create_milestone:
                    print(
                        "\n⚠️  WARNING: Milestone creation failed, release issue may not be linked"
                    )
                print("\nRelease Tracking Issue:")
                issue_number = create_release_issue(arg, milestone_number)
                if issue_number:
                    print(f"\n✓ Release tracking issue created successfully")
                    print(f"  Update the issue with:")
                    print(f"  - Target date")
                    print(f"  - Feature list")
                    print(f"  - Test results")
                else:
                    print("\n⚠️  WARNING: Release tracking issue creation failed")

            # Validate consistency
            print()
            check_consistency()

            # Summary and reminders
            print()
            if create_milestone or create_issue:
                print("✓ Version bump complete with GitHub integration!")
                print(f"\nNext steps for v{arg}:")
                if milestone_number:
                    print(f"  1. Link issues to milestone v{arg}")
                    print(f"     gh issue edit <number> --milestone v{arg}")
                if create_issue:
                    print(f"  2. Update release tracking issue with details")
                if not validate_notes:
                    print(f"  3. Create release notes:")
                    print(f"     docs/archive/summaries/v{arg}-release-notes.md")
            else:
                # Reminder about release notes if not validated
                if not validate_notes:
                    print(
                        "📝 REMINDER: Before tagging this release, ensure release notes exist:"
                    )
                    print(f"   python scripts/bump_version.py --check-notes {arg}")
                    print(
                        f"   Or create: docs/archive/summaries/v{arg}-release-notes.md"
                    )
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
