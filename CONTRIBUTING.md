# Contributing to VS Code Extension Security Scanner

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Git Workflow](#git-workflow)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Project Structure](#project-structure)

---

## Code of Conduct

This project follows professional open-source standards. Be respectful, constructive, and collaborative.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- GitHub account
- Familiarity with Python development

### First-Time Contributors

1. Check [open issues](https://github.com/jvlivonius/vsc-extension-scanner/issues) for `good first issue` labels
2. Read the [Product Requirements Document](docs/project/PRD.md) to understand project scope
3. Review [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for system design principles
4. Read [SECURITY.md](SECURITY.md) for security requirements

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/vsc-extension-scanner.git
cd vsc-extension-scanner

# Add upstream remote
git remote add upstream https://github.com/jvlivonius/vsc-extension-scanner.git
```

### 2. Install Development Dependencies

```bash
# Install package in editable mode with development dependencies
pip install -e .[dev,test]

# Install pre-commit hooks (runs security checks automatically)
pre-commit install
```

### 3. Verify Setup

```bash
# Run all tests to verify setup
python3 -m pytest tests/ -v

# Run security checks
pre-commit run --all-files

# Try the tool
./vscan --help
```

---

## Git Workflow

This project uses **Simplified GitHub Flow**. Full details in [GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md).

### Quick Guide

```bash
# Always start from updated main
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit frequently
git add .
git commit -m "feat(scope): description"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
gh pr create --title "feat: your feature" --body "Description"
```

### Branch Naming

- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical security/data fixes
- `docs/*` - Documentation changes

### Commit Message Format

```
type(scope): subject

Examples:
feat(scanner): add parallel processing support
fix(cache): prevent corruption with HMAC validation
docs(security): update vulnerability reporting process
test(cli): add integration tests for --output flag
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `hotfix`

---

## Making Changes

### Before You Start

1. **Check scope:** Is your change aligned with project goals? Review [PRD.md](docs/project/PRD.md)
2. **Search existing issues/PRs:** Avoid duplicate work
3. **Create an issue:** For significant changes, create an issue first to discuss approach

### Development Guidelines

#### Security Requirements (CRITICAL)

**All file paths MUST use `validate_path()`:**
```python
from vscode_scanner.utils import validate_path

# ✅ Correct
validated_path = validate_path(user_input)

# ❌ Never do this
with open(user_input, 'r') as f:  # Security vulnerability!
```

**All user-facing strings MUST use `sanitize_string()`:**
```python
from vscode_scanner.utils import sanitize_string

# ✅ Correct
print(sanitize_string(extension_name, context='output'))

# ❌ Never do this
print(f"Extension: {extension_name}")  # Potential injection!
```

#### Architecture Principles

1. **3-Layer Architecture:** Presentation → Application → Infrastructure
2. **No layer violations:** Infrastructure cannot import from Presentation
3. **KISS Principle:** Simple solutions over clever ones
4. **Fail Fast:** Invalid input should raise errors immediately

See [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for complete rules.

#### Testing Requirements

- **All new features:** Must have tests
- **Bug fixes:** Must have regression tests
- **Security changes:** Must pass all security tests
- **Coverage:** Maintain ≥70% overall (≥95% for security modules)

---

## Testing

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 tests/test_security.py

# Run with coverage
pytest tests/ --cov=vscode_scanner --cov-report=html

# Run security tests (MUST pass before commit)
python3 tests/test_security.py
python3 tests/test_security_regression.py
python3 tests/test_path_validation.py
python3 tests/test_string_sanitization.py

# Run architecture compliance tests
python3 tests/test_architecture.py
```

### Test Patterns

Use AAA (Arrange-Act-Assert) pattern:

```python
def test_feature():
    # Arrange: Set up test conditions
    input_data = "test"

    # Act: Execute the functionality
    result = function_under_test(input_data)

    # Assert: Verify expected outcome
    assert result == expected_value
```

See [TESTING.md](docs/guides/TESTING.md) for comprehensive testing guide.

---

## Pull Request Process

### Before Creating PR

- [ ] All tests pass: `pytest tests/`
- [ ] Security tests pass: `python3 tests/test_security.py`
- [ ] Architecture compliance: `python3 tests/test_architecture.py`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] Code follows project style
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (for user-facing changes)

### Creating the PR

```bash
# Push your changes
git push origin feature/your-feature

# Create PR (will use PR template automatically)
gh pr create --title "feat: your feature" --body "Description"

# Or create PR via GitHub web interface
```

### PR Requirements

1. **Title:** Follow commit message format
2. **Description:** Use PR template, fill all sections
3. **Tests:** All CI checks must pass
4. **Review:** Wait for maintainer approval
5. **Merge:** Maintainer will squash-merge

### After PR Merge

```bash
# Clean up your branch
git checkout main
git pull upstream main
git branch -d feature/your-feature
git push origin --delete feature/your-feature
```

---

## Code Style

### Python Style

- **Formatter:** Black (enforced by pre-commit hooks)
- **Linter:** Pylint (enforced by pre-commit hooks)
- **Security:** Bandit (enforced by pre-commit hooks)
- **Max line length:** 100 characters
- **Docstrings:** Google style for public APIs

### Documentation

- **Code comments:** Explain "why", not "what"
- **Docstrings:** Required for public functions and classes
- **Markdown:** Follow project conventions (see [DOCUMENTATION_CONVENTIONS.md](docs/contributing/DOCUMENTATION_CONVENTIONS.md))

---

## Project Structure

```
vsc-extension-scanner/
├── vscode_scanner/          # Main package (single source of truth)
│   ├── __init__.py
│   ├── cli.py              # Typer CLI (Presentation layer)
│   ├── scanner.py          # Core logic (Application layer)
│   ├── utils.py            # Validation & sanitization (Infrastructure)
│   └── ...
├── tests/                   # Test suite (628 tests, 72% coverage)
├── docs/                    # Documentation
│   ├── guides/             # Technical references (ARCHITECTURE, SECURITY, etc.)
│   ├── project/            # Project management (PRD, STATUS, roadmaps)
│   └── contributing/       # Contributor guides
├── .github/
│   ├── workflows/          # CI/CD (security, tests, semgrep)
│   └── ISSUE_TEMPLATE/     # Issue templates
└── scripts/                # Development scripts
```

See [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for detailed architecture.

---

## Getting Help

- **Questions:** Open a [GitHub issue](https://github.com/jvlivonius/vsc-extension-scanner/issues) with `question` label
- **Bugs:** Use [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Features:** Use [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **Security:** Use [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new) (PRIVATE)

---

## Recognition

Contributors are recognized in:
- GitHub contributors page
- CHANGELOG.md (for significant contributions)
- Security advisories (for vulnerability reports)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing! 🎉
