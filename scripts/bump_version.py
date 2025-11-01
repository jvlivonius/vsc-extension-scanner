#!/usr/bin/env python3
"""
Version Bump Helper Script

Automatically updates the version number in vscode_scanner/_version.py
and optionally updates documentation files.

Usage:
    python scripts/bump_version.py 2.3.0                # Set version (manual doc update)
    python scripts/bump_version.py 2.3.0 --auto-update  # Set version + auto-update docs
    python scripts/bump_version.py --check              # Check version consistency
    python scripts/bump_version.py --show               # Show current version
"""

import re
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


def show_version():
    """Display the current version."""
    current_version = read_current_version()
    schema_version = read_schema_version()
    print(f"Application version: {current_version}")
    print(f"Schema version: {schema_version}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--check":
        success = check_consistency()
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
            # Check for --auto-update flag
            auto_update = len(sys.argv) > 2 and sys.argv[2] == "--auto-update"

            # Update _version.py
            set_version(arg)

            # Auto-update documentation files if flag is set
            if auto_update:
                print("\nAuto-updating documentation files:")
                auto_update_docs(arg)

            # Validate consistency
            print()
            check_consistency()
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
