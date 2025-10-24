# Distribution Guide for VS Code Extension Security Scanner

**Package Name:** `vscode-extension-scanner`
**Distribution Method:** Python wheel file (`.whl`)

---

## Quick Start for Distribution

### For Package Maintainers

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

## Distribution Scenarios

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

### When You Release v2.3.0:

1. **Update version** in these files:
   - `pyproject.toml` (line 7)
   - `setup.py` (line 16)
   - `vscode_scanner/__init__.py` (line 7)
   - `vscode_scanner/vscan.py` (VERSION constant)

2. **Rebuild**:
   ```bash
   python3 -m build
   ```

3. **Distribute new wheel**:
   - New file: `vscode_extension_scanner-2.3.0-py3-none-any.whl`
   - Email/share as before

4. **Users upgrade**:
   ```bash
   pip install --upgrade vscode_extension_scanner-2.3.0-py3-none-any.whl
   ```

---

## Installation Troubleshooting

### Common Issues

**Issue 1: "pip: command not found"**

**Solution:**
```bash
# Use Python module instead
python3 -m pip install vscode_extension_scanner-2.2.0-py3-none-any.whl
```

---

**Issue 2: "vscan: command not found" after installation**

**Solution A (Temporary):**
```bash
# Use Python module to run
python3 -m vscode_scanner.vscan --help
```

**Solution B (Permanent - macOS/Linux):**
```bash
# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="$PATH:$HOME/Library/Python/3.9/bin"
```

**Solution C (Permanent - Windows):**
```
Add to PATH: %APPDATA%\Python\Python39\Scripts
```

---

**Issue 3: "Permission denied" during installation**

**Solution:**
```bash
# Install in user directory (no sudo needed)
pip install --user vscode_extension_scanner-2.2.0-py3-none-any.whl
```

---

**Issue 4: "ImportError: No module named 'vscode_scanner'"**

**Solution:**
```bash
# Reinstall with force
pip install --force-reinstall vscode_extension_scanner-2.2.0-py3-none-any.whl
```

---

**Issue 5: Wrong Python version**

**Check version:**
```bash
python3 --version
# Must be 3.8 or higher
```

**Solution:**
```bash
# Use specific Python version
python3.9 -m pip install vscode_extension_scanner-2.2.0-py3-none-any.whl
```

---

## Verification After Installation

### Test 1: Command Available
```bash
vscan --version
# Should show: vscan 2.2.0
```

### Test 2: Help Works
```bash
vscan --help
# Should show all options
```

### Test 3: Quick Scan
```bash
vscan --cache-stats
# Should auto-detect VS Code extensions and show stats
```

### Test 4: Import Works
```bash
python3 -c "from vscode_scanner import main; print('OK')"
# Should print: OK
```

---

## Advanced Distribution Options

### Option 1: Create Installation Script

Create `install_vscan.sh`:
```bash
#!/bin/bash
set -e

echo "Installing VS Code Extension Security Scanner v2.2.0..."

# Check Python version
python3 --version || { echo "Python 3.8+ required"; exit 1; }

# Install wheel
pip3 install --user vscode_extension_scanner-2.2.0-py3-none-any.whl

# Verify installation
if command -v vscan &> /dev/null; then
    echo "✓ Installation successful!"
    vscan --version
else
    echo "⚠ Installation complete, but 'vscan' command not in PATH"
    echo "Use: python3 -m vscode_scanner.vscan --help"
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
    echo "  pip install vscode_extension_scanner-2.2.0-py3-none-any.whl"
fi
```

---

## Package Contents

### What's Included in the Wheel

```
vscode_extension_scanner-2.2.0-py3-none-any.whl contains:

vscode_scanner/
├── __init__.py              # Package initialization
├── vscan.py                 # Main CLI entry point
├── vscan_api.py             # vscan.dev API client
├── cache_manager.py         # SQLite caching system
├── extension_discovery.py   # Extension detection
├── output_formatter.py      # JSON output generation
├── html_report_generator.py # HTML report generation
└── utils.py                 # Shared utilities

Plus:
- LICENSE (MIT)
- README.md
- Full documentation (docs/)
```

**Total size:** 44 KB (uncompressed: ~150 KB)

---

## Security Considerations

### Private Distribution Best Practices

1. **Verify Recipients**: Only send to authorized colleagues
2. **Use Secure Channels**: Company email, secure file sharing
3. **Version Control**: Track who received which version
4. **Update Policy**: Notify users of security updates
5. **Audit Trail**: Keep records of distributions

### Package Integrity

**Verify wheel integrity (optional):**
```bash
# Generate checksum when building
sha256sum vscode_extension_scanner-2.2.0-py3-none-any.whl > checksum.txt

# Users verify before installing
sha256sum -c checksum.txt
```

---

## FAQ

### Q: Can users modify the installed package?

**A:** No, the wheel is installed in Python's site-packages and should not be modified. If changes are needed, rebuild and redistribute a new version.

---

### Q: Do users need internet access?

**A:**
- **Installation**: No (offline install from wheel file)
- **Usage**: Yes (vscan needs internet to query vscan.dev API)

---

### Q: Can multiple versions be installed?

**A:** No, pip will replace the previous version. To run different versions, use virtual environments:
```bash
python3 -m venv vscan-env
source vscan-env/bin/activate
pip install vscode_extension_scanner-2.2.0-py3-none-any.whl
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
- ✅ **py3**: Python 3.x compatible
- ✅ **none**: No C extensions (pure Python)
- ✅ **any**: Any operating system (macOS, Windows, Linux)

---

### Q: Can I publish this to PyPI later?

**A:** Yes! If you decide to make it public later:
```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/vscode_extension_scanner-2.2.0-py3-none-any.whl

# Users install via
pip install vscode-extension-scanner
```

---

## Support

### For Maintainers

**Rebuild wheel:**
```bash
python3 -m build
```

**Test wheel locally:**
```bash
pip install dist/vscode_extension_scanner-2.2.0-py3-none-any.whl --force-reinstall
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
```

**Report issues:**
Contact: [your-email@company.com]

**Documentation:**
See README.md included in distribution

---

## Quick Reference Card (Print & Share)

```
┌─────────────────────────────────────────────────────────┐
│   VS Code Extension Security Scanner v2.2.0            │
├─────────────────────────────────────────────────────────┤
│ INSTALL:                                                │
│   pip install vscode_extension_scanner-2.2.0-py3-none-any.whl │
│                                                         │
│ RUN:                                                    │
│   vscan                    # Standard scan              │
│   vscan --detailed         # Detailed report           │
│   vscan --output scan.json # Save to file              │
│   vscan --verbose          # Show progress             │
│                                                         │
│ HELP:                                                   │
│   vscan --help             # All options                │
│                                                         │
│ UNINSTALL:                                              │
│   pip uninstall vscode-extension-scanner               │
│                                                         │
│ REQUIREMENTS:                                           │
│   Python 3.8+                                          │
│   Internet access (for vscan.dev API)                  │
│                                                         │
│ SUPPORT:                                                │
│   [your-email@company.com]                             │
└─────────────────────────────────────────────────────────┘
```

---

**Last Updated:** 2025-10-23
**Maintainer:** Joerg von Livonius
**License:** MIT
