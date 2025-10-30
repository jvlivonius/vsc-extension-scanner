#!/usr/bin/env python3
"""
Script to automatically add pytest markers to test files.

Usage:
    python3 scripts/add_pytest_markers.py --marker unit --files test_utils.py test_cli.py
    python3 scripts/add_pytest_markers.py --marker security --pattern "test_security*.py"
"""

import re
import sys
from pathlib import Path
from typing import List

def add_pytest_marker_to_file(file_path: Path, marker: str) -> bool:
    """
    Add pytest marker to all test classes in a file.

    Args:
        file_path: Path to test file
        marker: Marker name (e.g., 'unit', 'security', 'integration')

    Returns:
        True if file was modified, False otherwise
    """
    content = file_path.read_text()

    # Check if pytest is already imported
    has_pytest_import = 'import pytest' in content

    # Check if any markers already exist
    has_markers = f'@pytest.mark.{marker}' in content

    if has_markers:
        print(f"⏭️  {file_path.name}: Already has markers")
        return False

    # Add pytest import if needed
    if not has_pytest_import:
        # Find the last import line before 'from vscode_scanner'
        import_pattern = r'(from unittest\.mock import [^\n]+\n)'
        replacement = r'\1\nimport pytest\n'
        content = re.sub(import_pattern, replacement, content)

        if 'import pytest' not in content:
            # Fallback: add after unittest import
            import_pattern = r'(import unittest\n)'
            replacement = r'\1import pytest\n'
            content = re.sub(import_pattern, replacement, content)

    # Add marker before each test class
    class_pattern = r'^(class Test[A-Za-z0-9_]+\(unittest\.TestCase\):)'
    replacement = f'@pytest.mark.{marker}\n\\1'
    modified_content = re.sub(class_pattern, replacement, content, flags=re.MULTILINE)

    if modified_content != content:
        file_path.write_text(modified_content)
        # Count how many markers were added
        marker_count = modified_content.count(f'@pytest.mark.{marker}')
        print(f"✅ {file_path.name}: Added {marker_count} markers")
        return True
    else:
        print(f"⚠️  {file_path.name}: No test classes found")
        return False

def main():
    # Unit test files (16 files)
    unit_test_files = [
        'test_utils.py',
        'test_config_manager.py',
        'test_output_formatter.py',
        'test_cli.py',
        'test_cache_commands.py',
        'test_config_commands.py',
        'test_report_commands.py',
        'test_input_validators.py',
        'test_error_handling.py',
        'test_extension_discovery.py',
        'test_display.py',
        'test_scanner.py',
        'test_api.py',  # vscan_api tests
        'test_transactional_cache.py',
        'test_failed_extensions.py',
        'test_config_extensions_dir.py',
    ]

    # Security test files (8 files)
    security_test_files = [
        'test_security.py',
        'test_security_regression.py',
        'test_path_validation.py',
        'test_string_sanitization.py',
        'test_cache_integrity.py',
        'test_sqlite_security.py',
        'test_property_validation.py',
        'test_property_cache.py',
    ]

    # Other test files with specific markers
    other_test_files = {
        'test_architecture.py': 'architecture',
        'test_parallel_scanning.py': 'parallel',
        'test_db_integrity.py': 'integration',
        'test_integration.py': 'integration',
        'test_workflow_retry.py': 'integration',
        'test_performance.py': 'integration',
        'test_mock_validation.py': 'mock-validation',
        'test_integration_real_api.py': 'real-api',
        'test_retry.py': 'integration',
        'test_retry_analysis.py': 'integration',
        'test_verbose_mode.py': 'integration',
        'test_report_empty_cache.py': 'integration',
    }

    tests_dir = Path('tests')

    print("=" * 60)
    print("Adding pytest markers to test files")
    print("=" * 60)

    # Process unit tests
    print("\n📦 Unit Test Files:")
    unit_count = 0
    for filename in unit_test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            if add_pytest_marker_to_file(file_path, 'unit'):
                unit_count += 1
        else:
            print(f"❌ {filename}: File not found")

    # Process security tests
    print("\n🛡️  Security Test Files:")
    security_count = 0
    for filename in security_test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            if add_pytest_marker_to_file(file_path, 'security'):
                security_count += 1
        else:
            print(f"❌ {filename}: File not found")

    # Process other tests with specific markers
    print("\n🎯 Other Test Files:")
    other_count = 0
    for filename, marker in other_test_files.items():
        file_path = tests_dir / filename
        if file_path.exists():
            if add_pytest_marker_to_file(file_path, marker):
                other_count += 1
        else:
            print(f"❌ {filename}: File not found")

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Modified {unit_count} unit test files")
    print(f"✅ Modified {security_count} security test files")
    print(f"✅ Modified {other_count} other test files")
    print(f"✅ Total: {unit_count + security_count + other_count} files updated")
    print("=" * 60)

if __name__ == '__main__':
    main()
