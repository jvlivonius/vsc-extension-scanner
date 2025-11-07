#!/usr/bin/env python3
"""
Test Suite: Extension Discovery Tests
Purpose: Test VS Code extension discovery and parsing functionality
Coverage: vscode_scanner.extension_discovery (ExtensionDiscovery class)

This test suite validates extension discovery including:
- Platform-specific directory detection (macOS, Windows, Linux)
- Custom extensions directory support
- extensions.json parsing and validation
- package.json parsing and metadata extraction
- Extension filtering based on installed state
- Error handling for missing/malformed files

Mocking Strategy:
- Mock Path.home() for platform-specific paths
- Mock platform.system() for cross-platform testing
- Use temporary directories for filesystem operations
- Mock file operations to test error conditions
"""

import unittest
import tempfile
import os
import json
import platform
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from vscode_scanner.extension_discovery import ExtensionDiscovery


# ============================================================
# Platform Detection Tests
# ============================================================


@pytest.mark.unit
class TestPlatformDetection(unittest.TestCase):
    """Test suite for platform-specific directory detection.

    **Purpose:** Ensure extensions directory is correctly located on
    different operating systems.

    **Scope:**
    - macOS (.vscode/extensions)
    - Windows (.vscode/extensions)
    - Linux (.vscode/extensions)
    - Unsupported platform handling
    """

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_find_directory_macos(self, mock_home, mock_system):
        """Test directory detection on macOS."""
        # Arrange
        mock_system.return_value = "Darwin"
        mock_home.return_value = Path("/Users/testuser")

        # Create fake extensions directory
        test_dir = Path(tempfile.mkdtemp())
        extensions_dir = test_dir / ".vscode" / "extensions"
        extensions_dir.mkdir(parents=True, exist_ok=True)
        mock_home.return_value = test_dir

        # Act
        discovery = ExtensionDiscovery()
        result = discovery.find_extensions_directory()

        # Assert
        self.assertTrue(result.exists())
        self.assertIn(".vscode", str(result))
        self.assertIn("extensions", str(result))

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_find_directory_windows(self, mock_home, mock_system):
        """Test directory detection on Windows."""
        # Arrange
        mock_system.return_value = "Windows"
        mock_home.return_value = Path("C:/Users/testuser")

        # Create fake extensions directory
        test_dir = Path(tempfile.mkdtemp())
        extensions_dir = test_dir / ".vscode" / "extensions"
        extensions_dir.mkdir(parents=True, exist_ok=True)
        mock_home.return_value = test_dir

        # Act
        discovery = ExtensionDiscovery()
        result = discovery.find_extensions_directory()

        # Assert
        self.assertTrue(result.exists())

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_find_directory_linux(self, mock_home, mock_system):
        """Test directory detection on Linux."""
        # Arrange
        mock_system.return_value = "Linux"
        mock_home.return_value = Path("/home/testuser")

        # Create fake extensions directory
        test_dir = Path(tempfile.mkdtemp())
        extensions_dir = test_dir / ".vscode" / "extensions"
        extensions_dir.mkdir(parents=True, exist_ok=True)
        mock_home.return_value = test_dir

        # Act
        discovery = ExtensionDiscovery()
        result = discovery.find_extensions_directory()

        # Assert
        self.assertTrue(result.exists())

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    @patch("platform.system")
    def test_find_directory_unsupported_platform(self, mock_system):
        """Test that unsupported platforms raise FileNotFoundError."""
        # Arrange
        mock_system.return_value = "FreeBSD"

        # Act & Assert
        discovery = ExtensionDiscovery()
        with self.assertRaises(FileNotFoundError):
            discovery.find_extensions_directory()

    @patch("pathlib.Path.home")
    @patch("platform.system")
    def test_find_directory_missing_raises_error(self, mock_system, mock_home):
        """Test that missing extensions directory raises FileNotFoundError."""
        # Arrange
        mock_system.return_value = "Darwin"
        test_dir = Path(tempfile.mkdtemp())
        mock_home.return_value = test_dir
        # Don't create .vscode/extensions directory

        # Act & Assert
        discovery = ExtensionDiscovery()
        with self.assertRaises(FileNotFoundError):
            discovery.find_extensions_directory()

        # Cleanup
        import shutil

        if test_dir.exists():
            shutil.rmtree(test_dir)


# ============================================================
# Custom Directory Tests
# ============================================================


@pytest.mark.unit
class TestCustomDirectory(unittest.TestCase):
    """Test suite for custom extensions directory support.

    **Purpose:** Ensure custom extension directories are validated and used correctly.

    **Scope:**
    - Custom directory validation
    - Path expansion (~/, $HOME/)
    - Security validation (no traversal, no system dirs)
    - Missing directory handling
    """

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_custom_directory_valid(self):
        """Test that valid custom directory is accepted."""
        # Arrange
        custom_dir = os.path.join(self.test_dir, "custom_extensions")
        os.makedirs(custom_dir)

        # Act
        discovery = ExtensionDiscovery(custom_dir=custom_dir)
        result = discovery.find_extensions_directory()

        # Assert
        self.assertEqual(result, Path(custom_dir).resolve())

    def test_custom_directory_missing_raises_error(self):
        """Test that missing custom directory raises FileNotFoundError."""
        # Arrange
        custom_dir = os.path.join(self.test_dir, "nonexistent")

        # Act & Assert
        discovery = ExtensionDiscovery(custom_dir=custom_dir)
        with self.assertRaises(FileNotFoundError):
            discovery.find_extensions_directory()

    def test_custom_directory_not_a_directory(self):
        """Test that file path (not directory) raises FileNotFoundError."""
        # Arrange
        custom_file = os.path.join(self.test_dir, "not_a_dir.txt")
        with open(custom_file, "w") as f:
            f.write("test")

        # Act & Assert
        discovery = ExtensionDiscovery(custom_dir=custom_file)
        with self.assertRaises(FileNotFoundError):
            discovery.find_extensions_directory()

    def test_custom_directory_path_traversal_blocked(self):
        """Test that path traversal attempts are blocked."""
        # Arrange
        malicious_path = "../../../etc/passwd"

        # Act & Assert
        discovery = ExtensionDiscovery(custom_dir=malicious_path)
        with self.assertRaises(FileNotFoundError):
            discovery.find_extensions_directory()


# ============================================================
# extensions.json Parsing Tests
# ============================================================


@pytest.mark.unit
class TestExtensionsJsonParsing(unittest.TestCase):
    """Test suite for extensions.json parsing.

    **Purpose:** Ensure extensions.json file is correctly parsed and validated.

    **Scope:**
    - Valid extensions.json parsing
    - Missing file handling
    - Invalid JSON handling
    - Invalid format (not a list)
    - Malformed entries
    """

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.discovery = ExtensionDiscovery()

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_read_extensions_json_valid(self):
        """Test parsing valid extensions.json."""
        # Arrange
        extensions_json = {
            "version": "1",
            "extensions": [
                {
                    "identifier": {"id": "ms-python.python"},
                    "version": "2023.1.0",
                    "relativeLocation": "ms-python.python-2023.1.0",
                    "metadata": {
                        "id": "ms-python.python",
                        "publisherId": "ms-python",
                        "publisherDisplayName": "Microsoft",
                        "targetPlatform": "undefined",
                        "updated": True,
                        "isPreReleaseVersion": False,
                        "installedTimestamp": 1234567890000,
                    },
                }
            ],
        }

        json_path = Path(self.test_dir) / "extensions.json"
        with open(json_path, "w") as f:
            json.dump(extensions_json.get("extensions", []), f)

        # Act
        result = self.discovery._read_extensions_json(Path(self.test_dir))

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn("ms-python.python-2023.1.0", result)
        self.assertEqual(result["ms-python.python-2023.1.0"]["id"], "ms-python.python")
        self.assertEqual(result["ms-python.python-2023.1.0"]["version"], "2023.1.0")

    def test_read_extensions_json_missing_file(self):
        """Test handling of missing extensions.json file."""
        # Act
        result = self.discovery._read_extensions_json(Path(self.test_dir))

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    def test_read_extensions_json_invalid_json(self):
        """Test handling of invalid JSON in extensions.json."""
        # Arrange
        json_path = Path(self.test_dir) / "extensions.json"
        with open(json_path, "w") as f:
            f.write("{ invalid json }")

        # Act
        result = self.discovery._read_extensions_json(Path(self.test_dir))

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    def test_read_extensions_json_not_a_list(self):
        """Test handling of extensions.json that is not a list."""
        # Arrange
        json_path = Path(self.test_dir) / "extensions.json"
        with open(json_path, "w") as f:
            json.dump({"not": "a list"}, f)

        # Act
        result = self.discovery._read_extensions_json(Path(self.test_dir))

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    def test_read_extensions_json_malformed_entries(self):
        """Test handling of malformed entries in extensions.json."""
        # Arrange
        extensions_list = [
            {
                "identifier": {"id": "valid.ext"},
                "version": "1.0.0",
                "relativeLocation": "valid.ext-1.0.0",
            },
            "not a dict",  # Malformed entry
            {"identifier": "not a dict", "version": "1.0.0"},  # Malformed identifier
            {
                "identifier": {"id": "missing.version"},
                "relativeLocation": "missing.version-1.0.0",
            },  # Missing version
            {},  # Empty entry
        ]

        json_path = Path(self.test_dir) / "extensions.json"
        with open(json_path, "w") as f:
            json.dump(extensions_list, f)

        # Act
        result = self.discovery._read_extensions_json(Path(self.test_dir))

        # Assert
        self.assertIsInstance(result, dict)
        # Should only have the valid entry
        self.assertEqual(len(result), 1)
        self.assertIn("valid.ext-1.0.0", result)


# ============================================================
# package.json Parsing Tests
# ============================================================


@pytest.mark.unit
class TestPackageJsonParsing(unittest.TestCase):
    """Test suite for package.json parsing.

    **Purpose:** Ensure package.json files are correctly parsed and validated.

    **Scope:**
    - Valid package.json parsing
    - Missing package.json
    - Invalid JSON
    - Too large files
    - Missing required fields
    - Metadata extraction
    """

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.discovery = ExtensionDiscovery()

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parse_extension_valid(self):
        """Test parsing valid package.json."""
        # Arrange
        ext_dir = Path(self.test_dir) / "test.extension-1.0.0"
        ext_dir.mkdir()

        package_json = {
            "name": "extension",
            "publisher": "test",
            "version": "1.0.0",
            "displayName": "Test Extension",
            "description": "A test extension",
        }

        package_path = ext_dir / "package.json"
        with open(package_path, "w") as f:
            json.dump(package_json, f)

        # Act
        result = self.discovery._parse_extension(ext_dir)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "extension")
        self.assertEqual(result["publisher"], "test")
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(result["id"], "test.extension")
        self.assertEqual(result["display_name"], "Test Extension")

    def test_parse_extension_missing_package_json(self):
        """Test handling of missing package.json."""
        # Arrange
        ext_dir = Path(self.test_dir) / "no-package"
        ext_dir.mkdir()

        # Act
        result = self.discovery._parse_extension(ext_dir)

        # Assert
        self.assertIsNone(result)

    def test_parse_extension_invalid_json(self):
        """Test handling of invalid JSON in package.json."""
        # Arrange
        ext_dir = Path(self.test_dir) / "invalid-json"
        ext_dir.mkdir()

        package_path = ext_dir / "package.json"
        with open(package_path, "w") as f:
            f.write("{ invalid json }")

        # Act & Assert
        with self.assertRaises(Exception):
            self.discovery._parse_extension(ext_dir)

    def test_parse_extension_missing_required_fields(self):
        """Test handling of package.json with missing required fields."""
        # Arrange
        ext_dir = Path(self.test_dir) / "missing-fields"
        ext_dir.mkdir()

        # Missing publisher
        package_json = {"name": "extension", "version": "1.0.0"}

        package_path = ext_dir / "package.json"
        with open(package_path, "w") as f:
            json.dump(package_json, f)

        # Act
        result = self.discovery._parse_extension(ext_dir)

        # Assert
        self.assertIsNone(result)

    def test_parse_extension_missing_version(self):
        """Test handling of package.json with missing version (defaults to 'unknown')."""
        # Arrange
        ext_dir = Path(self.test_dir) / "no-version"
        ext_dir.mkdir()

        package_json = {"name": "extension", "publisher": "test"}

        package_path = ext_dir / "package.json"
        with open(package_path, "w") as f:
            json.dump(package_json, f)

        # Act
        result = self.discovery._parse_extension(ext_dir)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["version"], "unknown")

    def test_parse_extension_too_large_file(self):
        """Test handling of package.json that exceeds size limit."""
        # Arrange
        ext_dir = Path(self.test_dir) / "too-large"
        ext_dir.mkdir()

        # Create file larger than MAX_PACKAGE_JSON_SIZE
        package_path = ext_dir / "package.json"
        with open(package_path, "w") as f:
            f.write(
                '{"name":"test","publisher":"test","version":"1.0.0",'
                + '"x":"'
                + "x" * (10 * 1024 * 1024)
                + '"}'
            )

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.discovery._parse_extension(ext_dir)
        self.assertIn("too large", str(context.exception).lower())


# ============================================================
# Extension Discovery Integration Tests
# ============================================================


@pytest.mark.unit
class TestExtensionDiscovery(unittest.TestCase):
    """Test suite for extension discovery integration.

    **Purpose:** Ensure complete extension discovery workflow works correctly.

    **Scope:**
    - discover_extensions with valid extensions
    - discover_extensions with mixed valid/invalid
    - get_extension_count
    - Extension filtering based on extensions.json
    """

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test resources."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_discover_extensions_with_valid_extensions(self):
        """Test discovering valid extensions."""
        # Arrange
        # Create extension 1
        ext1_dir = Path(self.test_dir) / "test.ext1-1.0.0"
        ext1_dir.mkdir()
        with open(ext1_dir / "package.json", "w") as f:
            json.dump({"name": "ext1", "publisher": "test", "version": "1.0.0"}, f)

        # Create extension 2
        ext2_dir = Path(self.test_dir) / "test.ext2-2.0.0"
        ext2_dir.mkdir()
        with open(ext2_dir / "package.json", "w") as f:
            json.dump({"name": "ext2", "publisher": "test", "version": "2.0.0"}, f)

        # Create extensions.json
        extensions_json = [
            {
                "identifier": {"id": "test.ext1"},
                "version": "1.0.0",
                "relativeLocation": "test.ext1-1.0.0",
            },
            {
                "identifier": {"id": "test.ext2"},
                "version": "2.0.0",
                "relativeLocation": "test.ext2-2.0.0",
            },
        ]
        with open(Path(self.test_dir) / "extensions.json", "w") as f:
            json.dump(extensions_json, f)

        # Act
        discovery = ExtensionDiscovery(custom_dir=self.test_dir)
        extensions = discovery.discover_extensions()

        # Assert
        self.assertEqual(len(extensions), 2)
        ext_ids = [e["id"] for e in extensions]
        self.assertIn("test.ext1", ext_ids)
        self.assertIn("test.ext2", ext_ids)

    def test_discover_extensions_filters_old_versions(self):
        """Test that only installed versions from extensions.json are returned."""
        # Arrange
        # Create current version
        ext1_current = Path(self.test_dir) / "test.ext-2.0.0"
        ext1_current.mkdir()
        with open(ext1_current / "package.json", "w") as f:
            json.dump({"name": "ext", "publisher": "test", "version": "2.0.0"}, f)

        # Create old version (should be ignored)
        ext1_old = Path(self.test_dir) / "test.ext-1.0.0"
        ext1_old.mkdir()
        with open(ext1_old / "package.json", "w") as f:
            json.dump({"name": "ext", "publisher": "test", "version": "1.0.0"}, f)

        # extensions.json only lists current version
        extensions_json = [
            {
                "identifier": {"id": "test.ext"},
                "version": "2.0.0",
                "relativeLocation": "test.ext-2.0.0",
            }
        ]
        with open(Path(self.test_dir) / "extensions.json", "w") as f:
            json.dump(extensions_json, f)

        # Act
        discovery = ExtensionDiscovery(custom_dir=self.test_dir)
        extensions = discovery.discover_extensions()

        # Assert
        self.assertEqual(len(extensions), 1)
        self.assertEqual(extensions[0]["version"], "2.0.0")

    def test_get_extension_count(self):
        """Test get_extension_count returns correct count."""
        # Arrange
        ext1_dir = Path(self.test_dir) / "test.ext1-1.0.0"
        ext1_dir.mkdir()

        ext2_dir = Path(self.test_dir) / "test.ext2-2.0.0"
        ext2_dir.mkdir()

        # Act
        discovery = ExtensionDiscovery(custom_dir=self.test_dir)
        count = discovery.get_extension_count()

        # Assert
        self.assertEqual(count, 2)

    def test_discover_extensions_handles_mixed_valid_invalid(self):
        """Test discovering extensions with mixed valid and invalid dirs."""
        # Arrange
        # Valid extension
        valid_dir = Path(self.test_dir) / "test.valid-1.0.0"
        valid_dir.mkdir()
        with open(valid_dir / "package.json", "w") as f:
            json.dump({"name": "valid", "publisher": "test", "version": "1.0.0"}, f)

        # Invalid extension (no package.json)
        invalid_dir = Path(self.test_dir) / "test.invalid-1.0.0"
        invalid_dir.mkdir()

        # extensions.json lists both
        extensions_json = [
            {
                "identifier": {"id": "test.valid"},
                "version": "1.0.0",
                "relativeLocation": "test.valid-1.0.0",
            },
            {
                "identifier": {"id": "test.invalid"},
                "version": "1.0.0",
                "relativeLocation": "test.invalid-1.0.0",
            },
        ]
        with open(Path(self.test_dir) / "extensions.json", "w") as f:
            json.dump(extensions_json, f)

        # Act
        discovery = ExtensionDiscovery(custom_dir=self.test_dir)
        extensions = discovery.discover_extensions()

        # Assert
        # Should only return valid extension
        self.assertEqual(len(extensions), 1)
        self.assertEqual(extensions[0]["id"], "test.valid")


# ============================================================
# Test Runner
# ============================================================


def run_tests():
    """Run the test suite and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomDirectory))
    suite.addTests(loader.loadTestsFromTestCase(TestExtensionsJsonParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestPackageJsonParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestExtensionDiscovery))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Extension Discovery Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_tests())
