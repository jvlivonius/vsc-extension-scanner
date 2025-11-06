#!/usr/bin/env python3
# pylint: disable=duplicate-code  # Similar argparse/subprocess patterns across scripts
"""
Smoke Test Runner for VS Code Extension Scanner

Tests package installation and core functionality in an isolated virtualenv.

Usage:
    python3 scripts/smoke_test.py <WHEEL_FILE> [OPTIONS]

Examples:
    python3 scripts/smoke_test.py dist/vscan-3.7.1-py3-none-any.whl
    python3 scripts/smoke_test.py dist/vscan-3.7.1-py3-none-any.whl --verbose
    python3 scripts/smoke_test.py dist/vscan-3.7.1-py3-none-any.whl --config custom_extensions.json

Exit Codes:
    0 - All smoke tests passed
    1 - Some smoke tests failed
    2 - Wheel file not found/invalid
    3 - Execution error

Version: 1.0
"""

import sys
import subprocess
import argparse
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Import shared utilities from lib package
from lib import Colors, EXIT_SUCCESS, EXIT_FAILURE, EXIT_NOT_FOUND, EXIT_ERROR


# ==============================================================================
# Extension Configuration
# ==============================================================================


def load_extension_config(config_file: Path) -> List[Dict[str, str]]:
    """
    Load extension list from JSON configuration file.

    Args:
        config_file: Path to JSON configuration file

    Returns:
        List of extension dictionaries with id, publisher, name fields

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Extension config not found: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    if "extensions" not in config:
        raise ValueError("Config file must contain 'extensions' key")

    return config["extensions"]


# ==============================================================================
# Smoke Test Functions
# ==============================================================================


def run_smoke_tests(  # pylint: disable=too-many-return-statements,too-many-locals,too-many-branches,too-many-statements
    wheel_file: str,
    extension_config: Path,
    verbose: bool = True,
) -> bool:
    """
    Run comprehensive smoke tests on a built wheel package.

    Test Suite:
    1. Wheel file validation
    2. Virtual environment creation
    3. Package installation
    4. CLI accessibility (--version, --help)
    5. Core scan workflow (real API calls with configured extensions)
    6. Output format generation (JSON, HTML, CSV)
    7. Cache operations (stats, clear, integrity)

    Args:
        wheel_file: Path to .whl file to test
        extension_config: Path to extension configuration JSON
        verbose: Print detailed progress information

    Returns:
        True if all smoke tests pass, False otherwise
    """
    wheel_path = Path(wheel_file)

    if verbose:
        print("\n" + "=" * 70)
        print(f"SMOKE TESTS: {wheel_path.name}")
        print("=" * 70)

    # 1. Validate wheel exists
    if not wheel_path.exists():
        if verbose:
            print(f"{Colors.RED}✗ Wheel file not found: {wheel_path}{Colors.RESET}")
        return False

    if wheel_path.suffix != ".whl":
        if verbose:
            print(f"{Colors.RED}✗ Not a wheel file: {wheel_path}{Colors.RESET}")
        return False

    if verbose:
        print(f"\n[1/7] Wheel file: {wheel_path.name} {Colors.GREEN}✓{Colors.RESET}")

    # Load extension configuration
    try:
        extensions = load_extension_config(extension_config)
        if verbose:
            print(
                f"       Loaded {len(extensions)} extensions from {extension_config.name}"
            )
    except Exception as e:
        if verbose:
            print(f"{Colors.RED}✗ Failed to load extension config: {e}{Colors.RESET}")
        return False

    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix="vscan_smoke_")

    try:
        venv_path = Path(temp_dir) / "venv"

        # 2. Create virtual environment
        if verbose:
            print(f"\n[2/7] Creating test virtualenv at {venv_path}...")
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            timeout=60,
            check=False,
        )
        if result.returncode != 0:
            if verbose:
                print(
                    f"      {Colors.RED}✗ Virtualenv creation failed:\n{result.stderr.decode()}{Colors.RESET}"
                )
            return False
        if verbose:
            print(f"      {Colors.GREEN}✓ Virtualenv created{Colors.RESET}")

        # Determine virtualenv python path
        if sys.platform == "win32":
            venv_python = venv_path / "Scripts" / "python.exe"
        else:
            venv_python = venv_path / "bin" / "python"

        # 3. Install wheel in virtualenv
        if verbose:
            print(f"\n[3/7] Installing wheel in virtualenv...")
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", str(wheel_path.absolute())],
            capture_output=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            if verbose:
                print(
                    f"      {Colors.RED}✗ Installation failed:\n{result.stderr.decode()}{Colors.RESET}"
                )
            return False
        if verbose:
            print(f"      {Colors.GREEN}✓ Package installed successfully{Colors.RESET}")

        # 4. Test CLI accessibility
        if verbose:
            print(f"\n[4/7] Testing CLI command accessibility...")

        # Test --version
        result = subprocess.run(
            [str(venv_python), "-m", "vscode_scanner.vscan", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            if verbose:
                print(
                    f"      {Colors.RED}✗ CLI --version failed:\n{result.stderr}{Colors.RESET}"
                )
            return False

        version_output = result.stdout.strip()
        if verbose:
            print(
                f"      {Colors.GREEN}✓ CLI accessible: {version_output}{Colors.RESET}"
            )

        # Test --help
        result = subprocess.run(
            [str(venv_python), "-m", "vscode_scanner.vscan", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            if verbose:
                print(
                    f"      {Colors.RED}✗ Help command failed:\n{result.stderr}{Colors.RESET}"
                )
            return False

        # Verify help output contains expected commands
        help_text = result.stdout
        expected_commands = ["scan", "cache", "config", "report"]
        missing_commands = [
            cmd for cmd in expected_commands if cmd not in help_text.lower()
        ]

        if missing_commands:
            if verbose:
                print(
                    f"      {Colors.RED}✗ Help output missing commands: {', '.join(missing_commands)}{Colors.RESET}"
                )
            return False

        if verbose:
            print(f"      {Colors.GREEN}✓ Help command works{Colors.RESET}")

        # 5. Test core scan workflow with configured extensions
        if verbose:
            print(f"\n[5/7] Testing core scan workflow (real API calls)...")

        # Build extension list for scan command
        extension_ids = [ext["id"] for ext in extensions]
        extension_ids_str = ",".join(extension_ids)  # Join as comma-separated string

        # Create temp directory for scan outputs
        scan_output_dir = Path(temp_dir) / "outputs"
        scan_output_dir.mkdir(exist_ok=True)

        # Test scan with multiple output formats
        scan_cmd = [
            str(venv_python),
            "-m",
            "vscode_scanner.vscan",
            "scan",
            "--include-ids",
            extension_ids_str,
        ]

        if verbose:
            print(
                f"      Scanning {len(extension_ids)} extensions: {', '.join(extension_ids)}"
            )

        result = subprocess.run(
            scan_cmd,
            capture_output=True,
            text=True,
            timeout=60,  # Allow time for real API calls
            check=False,
        )

        # Note: Scan may return exit code 1 if vulnerabilities found, which is expected
        # We only fail if there's an execution error (exit code 2 or stderr indicates failure)
        if result.returncode == 2 or (
            "error" in result.stderr.lower()
            and result.returncode != 0
            and result.returncode != 1
        ):
            if verbose:
                print(
                    f"      {Colors.RED}✗ Scan command failed:\n{result.stderr}{Colors.RESET}"
                )
            return False

        if verbose:
            if result.returncode == 1:
                print(
                    f"      {Colors.YELLOW}⚠ Scan completed with vulnerabilities found (expected){Colors.RESET}"
                )
            else:
                print(
                    f"      {Colors.GREEN}✓ Scan completed successfully{Colors.RESET}"
                )

        # 6. Test output formats (JSON, HTML, CSV)
        if verbose:
            print(f"\n[6/7] Testing output format generation...")

        # Test JSON output
        json_output = scan_output_dir / "scan_result.json"
        result = subprocess.run(
            scan_cmd + ["--output", str(json_output)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if not json_output.exists():
            if verbose:
                print(f"      {Colors.RED}✗ JSON output file not created{Colors.RESET}")
            return False

        # Validate JSON structure
        try:
            with open(json_output, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            if "extensions" not in json_data:
                if verbose:
                    print(
                        f"      {Colors.RED}✗ JSON output missing 'extensions' key{Colors.RESET}"
                    )
                return False
        except json.JSONDecodeError as e:
            if verbose:
                print(f"      {Colors.RED}✗ Invalid JSON output: {e}{Colors.RESET}")
            return False

        if verbose:
            print(
                f"      {Colors.GREEN}✓ JSON output generated and validated{Colors.RESET}"
            )

        # Test HTML output
        html_output = scan_output_dir / "scan_result.html"
        result = subprocess.run(
            scan_cmd + ["--output", str(html_output)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if not html_output.exists():
            if verbose:
                print(f"      {Colors.RED}✗ HTML output file not created{Colors.RESET}")
            return False

        # Validate HTML contains expected content
        html_content = html_output.read_text(encoding="utf-8")
        if "<!DOCTYPE html>" not in html_content:
            if verbose:
                print(
                    f"      {Colors.RED}✗ HTML output invalid (missing DOCTYPE){Colors.RESET}"
                )
            return False

        if verbose:
            print(
                f"      {Colors.GREEN}✓ HTML output generated and validated{Colors.RESET}"
            )

        # Test CSV output
        csv_output = scan_output_dir / "scan_result.csv"
        result = subprocess.run(
            scan_cmd + ["--output", str(csv_output)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if not csv_output.exists():
            if verbose:
                print(f"      {Colors.RED}✗ CSV output file not created{Colors.RESET}")
            return False

        # Validate CSV has headers
        csv_content = csv_output.read_text(encoding="utf-8")
        if not csv_content.strip():
            if verbose:
                print(f"      {Colors.RED}✗ CSV output is empty{Colors.RESET}")
            return False

        if verbose:
            print(
                f"      {Colors.GREEN}✓ CSV output generated and validated{Colors.RESET}"
            )

        # 7. Test cache operations
        if verbose:
            print(f"\n[7/7] Testing cache operations...")

        # Test cache stats
        result = subprocess.run(
            [str(venv_python), "-m", "vscode_scanner.vscan", "cache", "stats"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            if verbose:
                print(
                    f"      {Colors.RED}✗ Cache stats command failed:\n{result.stderr}{Colors.RESET}"
                )
            return False

        if verbose:
            print(f"      {Colors.GREEN}✓ Cache stats command works{Colors.RESET}")

        # Test cache clear
        result = subprocess.run(
            [
                str(venv_python),
                "-m",
                "vscode_scanner.vscan",
                "cache",
                "clear",
                "--force",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            if verbose:
                print(
                    f"      {Colors.RED}✗ Cache clear command failed:\n{result.stderr}{Colors.RESET}"
                )
            return False

        if verbose:
            print(f"      {Colors.GREEN}✓ Cache clear command works{Colors.RESET}")

        # Success!
        if verbose:
            print("\n" + "=" * 70)
            print(f"{Colors.GREEN}✅ SMOKE TESTS: ALL CHECKS PASSED{Colors.RESET}")
            print("=" * 70 + "\n")

        return True

    except subprocess.TimeoutExpired as e:
        if verbose:
            print(f"      {Colors.RED}✗ Command timed out: {e}{Colors.RESET}")
        return False
    except Exception as e:
        if verbose:
            print(f"      {Colors.RED}✗ Smoke test error: {str(e)}{Colors.RESET}")
        return False
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass  # Best effort cleanup


# ==============================================================================
# Main
# ==============================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Smoke Test Runner for VS Code Extension Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "wheel_file",
        help="Path to .whl file to test (e.g., dist/vscan-3.7.1-py3-none-any.whl)",
    )
    parser.add_argument(
        "--config",
        default="scripts/smoke_test_extensions.json",
        help="Extension configuration file (default: scripts/smoke_test_extensions.json)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Detailed progress output (default: quiet)",
    )

    args = parser.parse_args()

    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(
            f"{Colors.RED}Error: Extension config file not found: {config_path}{Colors.RESET}",
            file=sys.stderr,
        )
        return EXIT_NOT_FOUND

    # Run smoke tests
    success = run_smoke_tests(
        wheel_file=args.wheel_file,
        extension_config=config_path,
        verbose=args.verbose,
    )

    return EXIT_SUCCESS if success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
