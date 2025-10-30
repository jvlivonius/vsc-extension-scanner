# CLI Testing Guide

**Document Type:** Timeless Reference
**Parent Document:** [TESTING.md](../TESTING.md)
**Framework:** Typer + CliRunner
**Target Audience:** Developers

---

## Overview

**Test File:** `tests/test_cli.py` (17 tests)
**Framework:** Typer with CliRunner for testing

**Run CLI Tests:**
```bash
python3 tests/test_cli.py
pytest tests/test_cli.py -v
```

---

## CLI Testing Examples

### Test 1: Command Structure
```python
from typer.testing import CliRunner
from vscode_scanner.cli import app

def test_scan_command_exists():
    """Verify scan command is available."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert "scan" in result.stdout.lower()
    assert result.exit_code == 0
```

### Test 2: Parameter Validation
```python
def test_invalid_risk_level():
    """Invalid risk level rejected."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", "--min-risk-level", "invalid"])

    assert result.exit_code != 0
    assert "error" in result.output.lower()
```

### Test 3: Help Text
```python
def test_help_completeness():
    """Help text is comprehensive."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", "--help"])

    assert "--output" in result.stdout
    assert "--workers" in result.stdout
    assert "Examples:" in result.stdout
```

---

## Terminal Compatibility

**Tested Terminals:**
- iTerm2 (macOS) ✅
- Terminal.app ✅
- GNOME Terminal ✅
- Windows Terminal ✅
- CMD.exe (partial) ⚠️
- CI/CD (plain mode) ✅

**Test Matrix:**
- Rich formatting in color terminals
- Plain fallback without color
- Output redirection to files
- SSH sessions

---

## See Full Guide

For complete CLI testing documentation:
- **Location:** Original [TESTING.md](../TESTING.md) section "CLI Testing (v3.0+)" (lines 2073-2206)
- **Coverage:** Command structure, terminal compatibility, help text validation

---

**Document Version:** 1.0 (Summary)
**Full Documentation:** See TESTING.md § CLI Testing
**Last Updated:** 2025-10-30
