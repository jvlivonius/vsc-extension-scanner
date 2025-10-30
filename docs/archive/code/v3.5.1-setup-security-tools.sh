#!/bin/bash
# Setup script for Phase 1 security tools
# Installs Bandit, Safety, pip-audit, pre-commit, and configures pre-commit hooks

set -e  # Exit on error

echo "=========================================="
echo "Phase 1 Security Tools Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found. Please run this script from the project root."
    exit 1
fi

echo "Step 1: Installing project in editable mode..."
pip install -e .

echo ""
echo "Step 2: Installing security tools..."
pip install bandit>=1.7.6 safety>=2.3.0 pip-audit>=2.4.0 pre-commit>=3.0.0

echo ""
echo "Step 3: Installing code quality tools..."
pip install black>=23.12.0 pylint>=3.0.0

# Try to install pylint-security (may not be available on all Python versions)
echo ""
echo "Step 4: Installing pylint-security (optional)..."
pip install pylint-security || echo "⚠️  Warning: pylint-security not available for this Python version (continuing without it)"

echo ""
echo "Step 4: Installing pre-commit hooks..."
pre-commit install

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Verifying installations..."
echo ""

# Verify tools are installed
echo "Checking installed tools:"
echo "  Bandit:     $(bandit --version 2>&1 | head -1)"
echo "  Safety:     $(safety --version 2>&1)"
echo "  pip-audit:  $(pip-audit --version 2>&1)"
echo "  pre-commit: $(pre-commit --version 2>&1)"
echo "  Black:      $(black --version 2>&1)"
echo "  Pylint:     $(pylint --version 2>&1 | head -1)"

echo ""
echo "=========================================="
echo "Quick Start Commands"
echo "=========================================="
echo ""
echo "Run all pre-commit hooks:"
echo "  pre-commit run --all-files"
echo ""
echo "Run security scans manually:"
echo "  bandit -r vscode_scanner/ -ll"
echo "  safety check"
echo "  pip-audit"
echo ""
echo "Run security tests:"
echo "  python3 tests/test_sqlite_security.py"
echo "  python3 tests/test_security_regression.py"
echo ""
echo "=========================================="
echo "🎉 Phase 1 Security Tools Ready!"
echo "=========================================="
