# Distribution Guide for VS Code Extension Security Scanner

**Package Name:** `vscode-extension-scanner`
**Current Version:** 3.5.6
**Distribution Methods:** GitHub Releases (primary), Manual wheel distribution (alternative)

---

## Quick Start

### For Users (Download & Install)

**Recommended: Download from GitHub Releases**

```bash
# 1. Visit GitHub Releases page
open https://github.com/jvlivonius/vsc-extension-scanner/releases

# 2. Download latest wheel file
# Click on latest release → Assets → vscode_extension_scanner-X.Y.Z-py3-none-any.whl

# 3. Install downloaded wheel
pip install ~/Downloads/vscode_extension_scanner-*.whl

# 4. Verify installation
vscan --version
vscan --help
```

**See [Method 1: GitHub Releases](#method-1-github-releases-recommended) for complete instructions.**

---

### For Package Maintainers (Build & Release)

**Build the distribution wheel:**

```bash
# 1. Navigate to project directory
cd /path/to/vsc-extension-scanner

# 2. Install build tools (if needed)
python3 -m pip install build

# 3. Build wheel from source
python3 -m build

# 4. Find the wheel file in dist/ directory
ls -lh dist/
# Output: vscode_extension_scanner-{VERSION}-py3-none-any.whl
```

**Note:** The version number in the wheel filename is automatically derived from `vscode_scanner/_version.py`.

**Distribute the wheel file:**

- **Email**: Attach the `.whl` file from the `dist/` directory
- **Shared Drive**: Upload to Google Drive, Dropbox, OneDrive, network share
- **Chat**: Share in Slack, Teams, or other messaging platform
- **Wiki/Intranet**: Upload to company documentation site

---

### For End Users

**Installation (One Command):**

```bash
pip install vscode_extension_scanner-*.whl
```

**If pip is not in PATH:**
```bash
python3 -m pip install vscode_extension_scanner-*.whl
```

**Usage:**

```bash
# Check installation and version
vscan --version

# Get help
vscan --help

# Run a scan
vscan scan

# Generate reports
vscan scan --output report.html
vscan scan --output results.json
vscan scan --output data.csv
```

---

## Detailed Distribution Instructions

### Prerequisites

**For installation, users need:**
- ✅ Python 3.8 or higher (check with `python3 --version`)
- ✅ pip (usually comes with Python)
- ✅ Internet access (for installation of dependencies: Rich and Typer)

**To check if Python is installed:**
```bash
python3 --version
# Should show: Python 3.8.x or higher
```

**If Python is not installed:**

- **macOS**: Pre-installed on recent versions, or install via Homebrew: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: Use package manager: `sudo apt install python3` or `sudo yum install python3`

---

## Distribution Methods

### Method 1: GitHub Releases (Recommended)

**Best for:** Public distribution, team access, automated updates

#### Download & Install

**Step 1: Navigate to Releases Page**

Visit: **https://github.com/jvlivonius/vsc-extension-scanner/releases**

Or use command line:
```bash
# macOS/Linux
open https://github.com/jvlivonius/vsc-extension-scanner/releases

# Windows (PowerShell)
start https://github.com/jvlivonius/vsc-extension-scanner/releases
```

**Step 2: Download Latest Release**

1. Click on the **latest release** (top of the page)
2. Scroll to **Assets** section
3. Download files:
   - `vscode_extension_scanner-X.Y.Z-py3-none-any.whl` (required)
   - `SHA256SUMS.txt` (optional, for verification)

**Step 3: Verify Checksum (Optional but Recommended)**

```bash
# macOS/Linux
cd ~/Downloads
shasum -a 256 -c SHA256SUMS.txt

# Windows (PowerShell)
cd $env:USERPROFILE\Downloads
Get-FileHash vscode_extension_scanner-*.whl -Algorithm SHA256
# Compare with value in SHA256SUMS.txt
```

**Step 4: Install**

```bash
# Standard installation
pip install vscode_extension_scanner-*.whl

# If pip not in PATH
python3 -m pip install vscode_extension_scanner-*.whl

# User installation (no admin rights)
pip install --user vscode_extension_scanner-*.whl
```

**Step 5: Verify Installation**

```bash
vscan --version  # Should show installed version
vscan --help     # Should display help menu
```

#### Benefits of GitHub Releases

- ✅ **Automated Builds**: GitHub Actions builds packages automatically on version tags
- ✅ **Quality Assurance**: Package installation verified before release creation
- ✅ **Checksums**: SHA256 checksums automatically generated for integrity verification
- ✅ **Release Notes**: Changelog entries included with each release
- ✅ **Public Access**: Team members can download anytime
- ✅ **Version History**: All previous versions available
- ✅ **No Manual Building**: Maintainers don't need to build/distribute manually

#### How Releases Are Created (For Maintainers)

GitHub Releases are **fully automated** via GitHub Actions:

1. Maintainer bumps version in `vscode_scanner/_version.py`
2. Maintainer updates CHANGELOG.md
3. Maintainer pushes version tag: `git tag v3.5.6 && git push origin v3.5.6`
4. GitHub Actions automatically:
   - Builds wheel and source distribution
   - Generates SHA256 checksums
   - Verifies package installation
   - Extracts release notes from CHANGELOG.md
   - Creates GitHub Release with all artifacts

**See:** [RELEASE_PROCESS.md](docs/contributing/RELEASE_PROCESS.md) for complete release workflow

**Workflow:** `.github/workflows/release.yml` contains automation logic

---

### Method 2: Manual Wheel Distribution (Alternative)

**Best for:** Offline environments, internal-only distribution, air-gapped systems

#### When to Use Manual Distribution

- No access to GitHub (firewall/network restrictions)
- Internal company distribution only
- Offline installation requirements
- Custom build/modification needed

### Scenario 1: Email Distribution

**Steps:**

1. **Attach wheel file** to email
   - File: `vscode_extension_scanner-{VERSION}-py3-none-any.whl`
   - Size: Small (typically under 100KB, well below attachment limits)

2. **Include installation instructions** in email body:
   ```
   Hi team,

   Attached is the VS Code Extension Security Scanner.

   To install:
   1. Save the attached .whl file
   2. Open terminal/command prompt
   3. Run: pip install vscode_extension_scanner-*.whl
   4. Test: vscan --version

   To scan your extensions:
   - vscan scan                        # Standard scan with Rich UI
   - vscan scan --output report.html   # HTML report
   - vscan scan --output results.json  # JSON export
   - vscan scan --output data.csv      # CSV export

   Full documentation: [link to README if available]

   Questions? Reply to this email.
   ```

3. **Send to recipients**

---

### Scenario 2: Shared Drive Distribution

**Setup:**

1. Create shared folder structure:
   ```
   Shared-Drive/
   └── tools/
       └── vscode-security-scanner/
           ├── vscode_extension_scanner-{VERSION}-py3-none-any.whl
           ├── INSTALL.txt
           └── README.md (optional)
   ```

2. Create `INSTALL.txt`:
   ```
   VS Code Extension Security Scanner
   ==================================

   Installation:
   1. Download the .whl file from this directory
   2. Install: pip install vscode_extension_scanner-*.whl
   3. Verify: vscan --version

   Requirements:
   - Python 3.8+
   - pip (included with Python)
   - Internet access (for dependencies)

   Usage Examples:
   - vscan scan                         # Standard scan with Rich UI
   - vscan scan --output report.html    # Generate HTML report
   - vscan scan --output results.json   # Export to JSON
   - vscan scan --output data.csv       # Export to CSV
   - vscan scan --quiet                 # Minimal output for CI/CD
   - vscan cache stats                  # View cache statistics
   - vscan config show                  # View configuration

   Support: [your-email@company.com]
   ```

3. Share folder link with team

---

### Scenario 3: Internal Wiki/Documentation

**Create wiki page:**

```markdown
# VS Code Extension Security Scanner

## What It Does
Scans your installed VS Code extensions for security vulnerabilities using vscan.dev.

## Installation

### Step 1: Download
[Download the latest wheel file](link-to-file)

### Step 2: Install
```bash
pip install vscode_extension_scanner-*.whl
```

### Step 3: Verify
```bash
vscan --version
vscan --help
```

## Usage

### Standard Scan
```bash
vscan scan
```

### Generate Reports

```bash
vscan scan --output report.html    # Interactive HTML report
vscan scan --output results.json   # JSON format
vscan scan --output data.csv       # CSV format
```

### Configuration

```bash
vscan config init                  # Create config file
vscan config show                  # View current settings
```

### Cache Management

```bash
vscan cache stats                  # View cache statistics
vscan cache clear                  # Clear cache
```

### All Options

See: `vscan --help` or `vscan scan --help`

## Troubleshooting

**"vscan: command not found"**

- Use full path: `python3 -m vscode_scanner.vscan --version`
- Or add Python bin directory to PATH

**"No module named 'vscode_scanner'"**

- Reinstall: `pip install --force-reinstall vscode_extension_scanner-*.whl`

**Permission denied**

- Install with --user flag: `pip install --user vscode_extension_scanner-*.whl`

## Support

Contact: [your-email@company.com]
```

---

## Updating to New Versions

### For Package Maintainers

1. **Update version** in `vscode_scanner/_version.py`:

   ```python
   __version__ = "X.Y.Z"
   ```

   This is the single source of truth for version numbers.

2. **Rebuild the wheel**:

   ```bash
   python3 -m build
   ```

3. **Distribute new wheel**:
   - New file will be: `vscode_extension_scanner-X.Y.Z-py3-none-any.whl`
   - Distribute via your preferred method (email, shared drive, etc.)

### For End Users

**Upgrade to new version**:

```bash
pip install --upgrade vscode_extension_scanner-*.whl
```

**Check installed version**:

```bash
vscan --version
```

---

## Common Installation Issues

### Issue 1: "pip: command not found"

**Solution:**

```bash
# Use Python module instead
python3 -m pip install vscode_extension_scanner-*.whl
```

---

### Issue 2: "vscan: command not found" after installation

**Solution A (Temporary):**

```bash
# Use Python module to run
python3 -m vscode_scanner.vscan --version
```

**Solution B (Permanent - macOS/Linux):**

```bash
# Add Python bin directory to PATH in ~/.bashrc or ~/.zshrc
export PATH="$PATH:$HOME/Library/Python/3.9/bin"
# Or for Homebrew Python:
export PATH="$PATH:/usr/local/bin"
```

**Solution C (Permanent - Windows):**

Add to PATH environment variable: `%APPDATA%\Python\Python3X\Scripts`

---

### Issue 3: "Permission denied" during installation

**Solution:**

```bash
# Install in user directory (no sudo/admin rights needed)
pip install --user vscode_extension_scanner-*.whl
```

---

### Issue 4: "ImportError: No module named 'vscode_scanner'"

**Solution:**

```bash
# Reinstall with force flag
pip install --force-reinstall vscode_extension_scanner-*.whl
```

---

### Issue 5: Wrong Python version

**Check version:**

```bash
python3 --version
# Must be 3.8 or higher
```

**Solution:**

```bash
# Use specific Python version if multiple are installed
python3.9 -m pip install vscode_extension_scanner-*.whl
```

---

## Verification After Installation

### Test 1: Command Available

```bash
vscan --version
# Should show version number
```

### Test 2: Help Works

```bash
vscan --help
# Should show main commands (scan, cache, config, report)
```

### Test 3: Check Cache Stats

```bash
vscan cache stats
# Should show cache statistics
```

### Test 4: Python Import Works

```bash
python3 -c "import vscode_scanner; print('OK')"
# Should print: OK
```

---

## Advanced Distribution Options

### Option 1: Create Installation Script

Create `install_vscan.sh`:

```bash
#!/bin/bash
set -e

echo "Installing VS Code Extension Security Scanner..."

# Check Python version
python3 --version || { echo "Error: Python 3.8+ required"; exit 1; }

# Find wheel file
WHEEL=$(ls vscode_extension_scanner-*.whl 2>/dev/null | head -1)
if [ -z "$WHEEL" ]; then
    echo "Error: No wheel file found"
    exit 1
fi

# Install wheel
pip3 install --user "$WHEEL"

# Verify installation
if command -v vscan &> /dev/null; then
    echo "✓ Installation successful!"
    vscan --version
else
    echo "⚠ Installation complete, but 'vscan' command not in PATH"
    echo "Use: python3 -m vscode_scanner.vscan --version"
fi
```

Distribute: `install_vscan.sh` + `.whl` file

---

### Option 2: Create Uninstall Script

Create `uninstall_vscan.sh`:

```bash
#!/bin/bash
pip3 uninstall -y vscode-extension-scanner
echo "VS Code Extension Security Scanner has been removed."
```

---

### Option 3: Version Check Script

Create `check_vscan_version.sh`:

```bash
#!/bin/bash
if command -v vscan &> /dev/null; then
    echo "Current version:"
    vscan --version
else
    echo "Not installed. Install with:"
    echo "  pip install vscode_extension_scanner-*.whl"
fi
```

---

## Package Contents

### What's Included in the Wheel

```
vscode_extension_scanner-{VERSION}-py3-none-any.whl contains:

vscode_scanner/
├── __init__.py              # Package initialization
├── _version.py              # Version management
├── vscan.py                 # Main CLI entry point
├── cli.py                   # Typer CLI framework
├── scanner.py               # Core scan logic
├── display.py               # Rich formatting
├── vscan_api.py             # vscan.dev API client
├── cache_manager.py         # SQLite caching system
├── config_manager.py        # Configuration file support
├── constants.py             # Centralized constants
├── extension_discovery.py   # Extension detection
├── output_formatter.py      # JSON/CSV output generation
├── html_report_generator.py # HTML report generation
└── utils.py                 # Shared utilities

Plus:
- LICENSE (MIT)
- README.md
- Package metadata
```

**Typical size:** Under 100 KB compressed

---

## Security Considerations

### Private Distribution Best Practices

1. **Verify Recipients**: Only send to authorized colleagues
2. **Use Secure Channels**: Company email, secure file sharing
3. **Version Control**: Track who received which version
4. **Update Policy**: Notify users of security updates
5. **Audit Trail**: Keep records of distributions

### Package Integrity

**Generate checksum when building (optional):**

```bash
# macOS
shasum -a 256 vscode_extension_scanner-*.whl > checksum.txt

# Linux
sha256sum vscode_extension_scanner-*.whl > checksum.txt

# Windows (PowerShell)
Get-FileHash vscode_extension_scanner-*.whl -Algorithm SHA256 > checksum.txt
```

**Users verify before installing:**

```bash
# macOS
shasum -a 256 -c checksum.txt

# Linux
sha256sum -c checksum.txt
```

---

## FAQ

### Q: Can users modify the installed package?

**A:** No, the wheel is installed in Python's site-packages and should not be modified. If changes are needed, rebuild and redistribute a new version.

---

### Q: Do users need internet access?

**A:**

- **Installation**: Yes (to download dependencies: Rich and Typer from PyPI)
- **Usage**: Yes (to query vscan.dev API for security analysis)
- **Offline mode**: Cache can be used for repeated scans without API calls

---

### Q: Can multiple versions be installed?

**A:** No, pip will replace the previous version. To run different versions, use virtual environments:

```bash
python3 -m venv vscan-env
source vscan-env/bin/activate  # On Windows: vscan-env\Scripts\activate
pip install vscode_extension_scanner-*.whl
```

---

### Q: How do users uninstall?

**A:**

```bash
pip uninstall vscode-extension-scanner
```

---

### Q: Does it work on all operating systems?

**A:** Yes! The wheel is `py3-none-any` which means:

- ✅ **py3**: Python 3.x compatible (3.8+)
- ✅ **none**: No C extensions (pure Python)
- ✅ **any**: Any operating system (macOS, Windows, Linux)

---

### Q: Is this available on PyPI?

**A:** Not yet. Currently distributed via:

- ✅ **Primary**: GitHub Releases (automated, public)
- ✅ **Alternative**: Manual wheel distribution (offline/internal)

**Future PyPI Publishing:**

PyPI publication is planned but not yet implemented. When published, users will be able to install with:

```bash
pip install vscode-extension-scanner
```

**For Maintainers (when ready for PyPI):**

```bash
# Install twine
pip install twine

# Upload to PyPI (requires PyPI account and credentials)
twine upload dist/vscode_extension_scanner-*.whl

# Or configure in GitHub Actions for automated PyPI publishing
```

**Current Status:** GitHub Releases provides public distribution without PyPI overhead.

---

## Support

### For Maintainers

**Rebuild wheel:**

```bash
python3 -m build
```

**Test wheel locally:**

```bash
pip install dist/vscode_extension_scanner-*.whl --force-reinstall
vscan --version
vscan --help
```

**Clean build artifacts:**

```bash
rm -rf build/ dist/ *.egg-info
```

---

### For Users

**Get help:**

```bash
vscan --help
vscan scan --help
vscan cache --help
vscan config --help
```

**Report issues:**

Contact: [your-email@company.com]

**Documentation:**

See README.md included in distribution

---

## Quick Reference Card (Print & Share)

```
┌──────────────────────────────────────────────────────────┐
│   VS Code Extension Security Scanner                    │
├──────────────────────────────────────────────────────────┤
│ INSTALL:                                                 │
│   pip install vscode_extension_scanner-*.whl            │
│                                                          │
│ RUN:                                                     │
│   vscan scan                    # Standard scan          │
│   vscan scan --output report.html  # HTML report        │
│   vscan scan --output data.csv     # CSV export         │
│   vscan cache stats             # Cache statistics      │
│   vscan config show             # View configuration    │
│                                                          │
│ HELP:                                                    │
│   vscan --help                  # Main help             │
│   vscan scan --help             # Scan options          │
│                                                          │
│ UNINSTALL:                                               │
│   pip uninstall vscode-extension-scanner                │
│                                                          │
│ REQUIREMENTS:                                            │
│   Python 3.8+                                           │
│   Internet access (for dependencies and API)            │
│                                                          │
│ SUPPORT:                                                 │
│   [your-email@company.com]                              │
└──────────────────────────────────────────────────────────┘
```

---

**License:** MIT
