# Contributing to VS Code Extension Security Scanner

[![CI Status](https://github.com/jvlivonius/vsc-extension-scanner/workflows/CI/badge.svg)](https://github.com/jvlivonius/vsc-extension-scanner/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Your First Contribution](#-your-first-contribution)
- [Code of Conduct](#-code-of-conduct)
- [Types of Contributions](#-types-of-contributions)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Troubleshooting Setup](#-troubleshooting-setup)
- [Git Workflow](#git-workflow)
- [Making Changes](#making-changes)
- [Common Mistakes to Avoid](#-common-mistakes-to-avoid)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [What Happens After Submitting Your PR](#-what-happens-after-submitting-your-pr)
- [Code Style](#code-style)
- [Project Structure](#project-structure)
- [Glossary](#-glossary)
- [Getting Help](#getting-help)

---

## 🚀 Your First Contribution

**New to open source? Start here!** This quick guide walks you through making your first contribution.

### Quick Win: Fix a Typo or Improve Documentation (5-10 minutes)

1. **Find something small**: Look for typos, unclear explanations, or missing examples in docs/README
2. **Fork and edit**: Use GitHub's web editor (no git setup needed!) - click "Edit" on any file
3. **Submit PR**: Click "Create Pull Request" and describe your change
4. **Celebrate**: You're a contributor! 🎉

### Ready for Code? Start with "Good First Issues" (30-60 minutes)

1. Browse [good first issues](https://github.com/jvlivonius/vsc-extension-scanner/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) - labeled with difficulty and time estimates
2. Comment "I'd like to work on this" to claim it
3. Follow the [Development Setup](#development-setup) below
4. Ask questions anytime - we're here to help!

### What Should I Work On? Decision Guide

**Not comfortable with code yet?**
→ Start with [Documentation](#-documentation) improvements, bug reports, or testing

**Have 15-30 minutes?**
→ Pick a "good first issue" or fix documentation typos

**Have 1-2 hours?**
→ Work on bug fixes or test improvements

**Have 2+ hours and want a challenge?**
→ Check [PRD.md](docs/project/PRD.md) for feature ideas (create an issue first to discuss!)

---

## 📜 Code of Conduct

**Our Standards:**
- ✅ Be respectful and constructive in all interactions
- ✅ Welcome newcomers and answer questions patiently
- ✅ Focus on what's best for the project and community
- ✅ Accept constructive criticism gracefully
- ✅ Give credit where credit is due
- ❌ No harassment, discrimination, or unprofessional conduct
- ❌ No spam, trolling, or off-topic discussions

**Reporting:** If you experience or witness unacceptable behavior, please report it by contacting the project maintainers privately through [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new) or by opening a confidential issue.

**Enforcement:** Violations may result in temporary or permanent ban from the project.

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for full details.

---

## 🤝 Types of Contributions

We welcome ALL types of contributions! You don't need to write code to help.

### 📝 Documentation

- Fix typos or unclear explanations
- Add examples to documentation
- Write tutorials or blog posts about using the tool
- Improve code comments and docstrings

**Good for:** First-time contributors, technical writers, users who found something confusing

**Time commitment:** 5-30 minutes

### 🐛 Bug Reports

- Report issues you encounter while using the tool
- Provide detailed reproduction steps
- Test pre-release versions and report problems

**Good for:** Users who want to improve quality without writing code

**Time commitment:** 10-20 minutes per report

### ✨ Code Contributions

- Fix bugs (see [bugfix/* issues](https://github.com/jvlivonius/vsc-extension-scanner/issues?q=is%3Aissue+is%3Aopen+label%3Abug))
- Add features (check [PRD.md](docs/project/PRD.md) for scope first!)
- Improve performance
- Refactor code for better maintainability

**Good for:** Python developers familiar with CLI tools

**Time commitment:** 1-4 hours depending on complexity

### 🧪 Testing

- Write new test cases for uncovered code
- Improve test coverage (current: 72%, target: 85%)
- Manual testing of edge cases
- Review and improve test documentation

**Good for:** QA-minded contributors, testing enthusiasts

**Time commitment:** 30 minutes - 2 hours

### 🎨 Design & UX

- Improve CLI output formatting and readability
- Suggest UX improvements for better user experience
- Review error messages for clarity
- Propose better progress indicators or status displays

**Good for:** UX designers, CLI power users with feedback

**Time commitment:** 15 minutes - 1 hour

### 🔍 Issue Triage

- Reproduce reported bugs and add details
- Label and organize issues
- Help answer questions from other users
- Close duplicate or resolved issues

**Good for:** Community builders, project organizers

**Time commitment:** 15-30 minutes per session

---

## Getting Started

### ✅ Prerequisites

- ✅ Python 3.8+ installed ([Download](https://www.python.org/downloads/))
- ✅ Git installed ([Download](https://git-scm.com/downloads))
- ✅ GitHub account created ([Sign up](https://github.com/join))
- ✅ Basic Python familiarity (functions, classes, imports)

### First-Time Contributors

**Step-by-step workflow:**

1. ✅ Read the [Product Requirements Document](docs/project/PRD.md) to understand project scope
2. ✅ Review [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for system design principles
3. ✅ Read [SECURITY.md](docs/guides/SECURITY.md) for security requirements (CRITICAL)
4. ✅ Check [open issues](https://github.com/jvlivonius/vsc-extension-scanner/issues) for `good first issue` labels
5. ✅ Follow [Development Setup](#development-setup) below
6. ✅ Make your first contribution!

**Estimated time:** 30-45 minutes for initial setup and reading

---

## Development Setup

### 1. Fork and Clone (5 minutes)

```bash
# Fork the repository on GitHub (click "Fork" button), then clone your fork
git clone https://github.com/YOUR-USERNAME/vsc-extension-scanner.git
cd vsc-extension-scanner

# Add upstream remote to sync with main repository
git remote add upstream https://github.com/jvlivonius/vsc-extension-scanner.git
```

**✅ Verify:** Run `git remote -v` - you should see both `origin` (your fork) and `upstream` (main repo)

### 2. Install Development Dependencies (3-5 minutes)

```bash
# Install package in editable mode with development dependencies
pip install -e .[dev,test]

# Install pre-commit hooks (runs security checks automatically before each commit)
pre-commit install
```

**✅ Expected output:**
```
Successfully installed vscode-scanner ...
pre-commit installed at .git/hooks/pre-commit
```

### 3. Verify Setup (2-3 minutes)

```bash
# Run all tests to verify everything works
python3 -m pytest tests/ -v

# ✅ Expected output:
# ======================== test session starts ========================
# collected 628 items
# tests/test_security.py::test_path_validation PASSED          [ 1%]
# ...
# ======================== 628 passed in 45.2s ========================
```

```bash
# Run security checks
pre-commit run --all-files

# ✅ Expected: All checks pass (may take longer on first run while tools install)
```

```bash
# Try the tool
./vscan --help

# ✅ Expected: Help message displays with available commands
```

**Total setup time:** 10-15 minutes

---

## 🔧 Troubleshooting Setup

### Common Issues and Solutions

#### ❌ `pip install -e .[dev,test]` fails with "invalid syntax"

**Solution:** Upgrade pip first
```bash
python3 -m pip install --upgrade pip
pip install -e .[dev,test]
```

#### ❌ Pre-commit hooks fail on first run

**This is expected!** Pre-commit downloads tools on the first run.

**Solution:** Just run it again
```bash
pre-commit run --all-files
```

#### ❌ `./vscan` command not found or "Permission denied"

**Solution:** Make the script executable
```bash
# Make sure you're in the project root directory
cd vsc-extension-scanner
chmod +x vscan
./vscan --help
```

#### ❌ Tests fail with "ModuleNotFoundError: No module named 'vscode_scanner'"

**Solution:** Reinstall in editable mode
```bash
pip install -e .
```

#### ❌ `git push` fails with authentication error

**Solution:** Set up GitHub authentication
- Option 1: [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- Option 2: [SSH Keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

#### ❌ Pre-commit hooks are too slow

**Solution:** Run on staged files only (default behavior)
```bash
git add changed_file.py
git commit  # Only checks staged files
```

**Still stuck?**

Open an [issue](https://github.com/jvlivonius/vsc-extension-scanner/issues/new) with:
- Your OS and Python version (`python3 --version`)
- Complete error message (paste full output)
- What you were trying to do
- What you expected to happen

We're happy to help! 🙂

---

## Git Workflow

This project uses **Simplified GitHub Flow**. Full details in [GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md).

### Quick Guide

```bash
# 1. Always start from updated main
git checkout main
git pull upstream main

# 2. Create feature branch (use descriptive name!)
git checkout -b feature/your-feature-name

# 3. Make changes, commit frequently with clear messages
git add .
git commit -m "feat(scope): description"

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Create pull request on GitHub
gh pr create --title "feat: your feature" --body "Description"
# Or use GitHub web interface
```

### Branch Naming Conventions

Use the format: `<type>/<short-descriptive-name>`

- `feature/*` - New features (e.g., `feature/add-csv-export`)
- `bugfix/*` - Bug fixes (e.g., `bugfix/cache-corruption`)
- `hotfix/*` - Critical security/data fixes (e.g., `hotfix/path-traversal`)
- `docs/*` - Documentation changes (e.g., `docs/improve-testing-guide`)
- `test/*` - Test improvements (e.g., `test/add-integration-tests`)

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `hotfix` - Critical security/data fix
- `docs` - Documentation only
- `test` - Testing updates
- `refactor` - Code restructuring (no behavior change)
- `chore` - Maintenance (deps, build, etc.)
- `perf` - Performance improvements

**Examples:**
```
feat(scanner): add parallel processing support
fix(cache): prevent corruption with HMAC validation
docs(security): update vulnerability reporting process
test(cli): add integration tests for --output flag
refactor(display): simplify progress bar logic
chore(deps): update typer to 0.9.0
```

---

## Making Changes

### Before You Start

1. **✅ Check scope:** Is your change aligned with project goals? Review [PRD.md](docs/project/PRD.md)
2. **✅ Search existing issues/PRs:** Avoid duplicate work
3. **✅ Create an issue first:** For significant changes (new features, major refactors), create an issue to discuss approach before implementing

### Development Guidelines

#### Security Requirements (🔴 CRITICAL)

**All file paths MUST use `validate_path()`:**

```python
from vscode_scanner.utils import validate_path

# ✅ CORRECT - Always validate user-provided paths
validated_path = validate_path(user_input)
with open(validated_path, 'r') as f:
    data = f.read()

# ❌ NEVER DO THIS - Path traversal vulnerability!
with open(user_input, 'r') as f:  # Security vulnerability!
    data = f.read()
```

**All user-facing strings MUST use `sanitize_string()`:**

```python
from vscode_scanner.utils import sanitize_string

# ✅ CORRECT - Prevent injection attacks
print(sanitize_string(extension_name, context='output'))
console.print(sanitize_string(error_msg, context='error'))

# ❌ NEVER DO THIS - Potential injection vulnerability!
print(f"Extension: {extension_name}")  # Unsanitized!
console.print(f"Error: {error_msg}")   # Unsanitized!
```

**Why this matters:**
- `validate_path()` prevents directory traversal attacks (e.g., `../../etc/passwd`)
- `sanitize_string()` prevents terminal injection and control character exploits
- Security tests MUST pass with 0 vulnerabilities before any commit

See [SECURITY.md](docs/guides/SECURITY.md) for complete security requirements.

#### Architecture Principles

1. **3-Layer Architecture:** Presentation → Application → Infrastructure (one-way dependencies only)
2. **No layer violations:** Infrastructure layer must NEVER import from Presentation layer
3. **KISS Principle:** Simple solutions over clever ones
4. **Fail Fast:** Invalid input should raise errors immediately, don't continue processing

**Example of correct layering:**
```python
# ✅ CORRECT - Presentation can import from Application
# In cli.py (Presentation):
from vscode_scanner.scanner import scan_extensions  # OK

# ✅ CORRECT - Application can import from Infrastructure
# In scanner.py (Application):
from vscode_scanner.cache_manager import get_cached_result  # OK

# ❌ WRONG - Infrastructure importing from Presentation
# In cache_manager.py (Infrastructure):
from vscode_scanner.display import format_output  # VIOLATION!
```

See [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for complete architectural rules and anti-patterns.

#### Testing Requirements

- **All new features:** Must have tests demonstrating they work
- **Bug fixes:** Must have regression tests preventing the bug from returning
- **Security changes:** Must pass ALL security tests with 0 vulnerabilities
- **Coverage targets:**
  - Security modules (`utils.py`): ≥95% coverage
  - Core logic (`scanner.py`, `cache_manager.py`): ≥85% coverage
  - Presentation layer (`cli.py`, `display.py`): ≥70% coverage
  - Overall project: ≥70% coverage (target: 85%)

**Why different targets?** Security-critical code needs near-perfect coverage to prevent vulnerabilities. Presentation layer can have lower coverage as it's mostly formatting.

---

## ⚠️ Common Mistakes to Avoid

Learn from common pitfalls! Here's what to watch out for:

### ❌ Security: Not using validation functions

```python
# ❌ WRONG - Security vulnerability!
def read_extension_file(path):
    with open(path, 'r') as f:  # No validation!
        return f.read()

# ✅ CORRECT - Always validate paths
from vscode_scanner.utils import validate_path

def read_extension_file(path):
    validated_path = validate_path(path)
    with open(validated_path, 'r') as f:
        return f.read()
```

### ❌ Git: Working directly on main branch

```bash
# ❌ WRONG - Changes on main can't be easily managed in PRs
git checkout main
# make changes directly on main...
git commit -m "changes"

# ✅ CORRECT - Always use feature branches
git checkout main
git pull upstream main
git checkout -b feature/my-improvement
# make changes on feature branch...
git commit -m "feat: my improvement"
```

### ❌ Testing: Skipping or commenting out tests to make build pass

```python
# ❌ WRONG - Hiding test failures
# def test_security_validation():
#     assert validate_path("../../etc/passwd")  # Commented out!

# ❌ WRONG - Skipping tests
@pytest.mark.skip("TODO: fix this later")
def test_security_validation():
    assert validate_path("../../etc/passwd")

# ✅ CORRECT - Fix the code, don't hide the test failure
def test_security_validation():
    with pytest.raises(SecurityError):  # Fixed test
        validate_path("../../etc/passwd")
```

### ❌ Architecture: Layer violations

```python
# ❌ WRONG - Infrastructure importing from Presentation
# In cache_manager.py (Infrastructure layer):
from vscode_scanner.display import format_output  # Violation!

def get_cached_result(key):
    result = cache.get(key)
    return format_output(result)  # Presentation logic in Infrastructure!

# ✅ CORRECT - Keep layers separate
# In cache_manager.py (Infrastructure layer):
def get_cached_result(key):
    return cache.get(key)  # Just return data

# In cli.py (Presentation layer):
from vscode_scanner.cache_manager import get_cached_result
from vscode_scanner.display import format_output

result = get_cached_result(key)
formatted = format_output(result)  # Presentation handles formatting
```

### ❌ Code Style: Inconsistent formatting

```python
# ❌ WRONG - Mixed styles, no consistency
def myFunction( x,y ):
    if x>0:
        return x+y
    else: return x-y

# ✅ CORRECT - Consistent style (Black formatter enforces this)
def my_function(x, y):
    """Add or subtract y from x based on x's sign."""
    if x > 0:
        return x + y
    else:
        return x - y
```

**Pro tip:** Run `pre-commit run --all-files` before committing to catch these issues automatically!

See [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) and [SECURITY.md](docs/guides/SECURITY.md) for more details.

---

## Testing

### Running Tests

```bash
# Run all tests (recommended before committing)
python3 -m pytest tests/ -v

# Run specific test file
python3 tests/test_security.py

# Run with coverage report
pytest tests/ --cov=vscode_scanner --cov-report=html
# Open htmlcov/index.html to see detailed coverage

# Run only tests matching a pattern
pytest tests/ -k "security"
```

### Required Security Tests (MUST pass before ANY commit)

```bash
# Run security vulnerability tests
python3 tests/test_security.py

# Run comprehensive security regression suite
python3 tests/test_security_regression.py

# Run path validation tests
python3 tests/test_path_validation.py

# Run string sanitization tests
python3 tests/test_string_sanitization.py

# ✅ All must show: 0 vulnerabilities, all tests passed
```

### Additional Quality Tests

```bash
# Run architecture compliance tests (must show 0 layer violations)
python3 tests/test_architecture.py

# Run integration tests
python3 tests/test_integration.py

# Run performance benchmarks
python3 tests/test_performance.py
```

### Coverage Expectations by Module

| Module | Current | Target | Priority | Why? |
|--------|---------|--------|----------|------|
| `utils.py` | 95% | 95% | 🔴 Critical | Security functions - path validation, sanitization |
| `scanner.py` | 85% | 85% | 🟡 High | Core scanning logic - reliability essential |
| `cache_manager.py` | 85% | 85% | 🟡 High | HMAC integrity - prevents tampering |
| `cli.py` | 70% | 70% | 🟢 Standard | CLI interface - focus on critical paths |
| `display.py` | 60% | 70% | 🟢 Standard | Formatting - less critical than logic |
| **Overall** | **72%** | **85%** | 🟡 High | Project-wide quality target |

**Why different targets?**
- **95% for security modules:** Near-perfect coverage prevents vulnerabilities
- **85% for core logic:** High coverage ensures reliability
- **70% for presentation:** Focus on critical paths, formatting less critical

### Test Organization

```
tests/
├── test_security.py              # Security vulnerability tests
├── test_security_regression.py   # Comprehensive security suite (95%+ coverage)
├── test_path_validation.py       # Path validation coverage
├── test_string_sanitization.py   # String sanitization coverage
├── test_cache_integrity.py       # HMAC integrity tests
├── test_sqlite_security.py       # SQLite security audit
├── test_architecture.py          # Layer compliance verification
├── test_scanner.py               # Scanner module tests
├── test_cli.py                   # CLI module tests
├── test_display.py               # Display module tests
├── test_integration.py           # End-to-end workflow tests
├── test_performance.py           # Performance benchmarks
└── test_property_based.py        # Hypothesis property tests (1,250+ scenarios)
```

### Writing New Tests - Template

Use the **AAA (Arrange-Act-Assert)** pattern for all tests:

```python
def test_feature_name():
    """Test that feature_name handles expected_scenario correctly.

    This test verifies that [specific behavior] works as expected
    when [specific conditions].
    """
    # Arrange: Set up test data and conditions
    input_data = "test_value"
    expected_result = "expected_output"

    # Act: Execute the feature under test
    actual_result = feature_function(input_data)

    # Assert: Verify the expected outcome
    assert actual_result == expected_result
    assert isinstance(actual_result, str)  # Additional assertions as needed
```

**Example - Testing path validation:**

```python
def test_validate_path_blocks_directory_traversal():
    """Test that validate_path blocks directory traversal attempts.

    This test verifies that path validation raises SecurityError
    when user input contains directory traversal patterns.
    """
    # Arrange: Create malicious path input
    malicious_path = "../../etc/passwd"

    # Act & Assert: Should raise SecurityError
    with pytest.raises(SecurityError):
        validate_path(malicious_path)
```

See [TESTING.md](docs/guides/TESTING.md) for comprehensive testing guide and specialized testing documentation in [docs/guides/testing/](docs/guides/testing/).

---

## Pull Request Process

### Before Creating PR - Checklist

Run through this checklist before submitting your PR:

- [ ] **All tests pass:** `pytest tests/` shows all green
- [ ] **Security tests pass:** `python3 tests/test_security.py` shows 0 vulnerabilities
- [ ] **Architecture compliance:** `python3 tests/test_architecture.py` shows 0 violations
- [ ] **Pre-commit hooks pass:** `pre-commit run --all-files` succeeds
- [ ] **Code follows project style:** Black, Pylint, Bandit checks pass
- [ ] **Documentation updated:** If you changed behavior, update relevant docs
- [ ] **CHANGELOG.md updated:** For user-facing changes, add entry to "Unreleased" section
- [ ] **Branch is up to date:** `git pull upstream main` and resolve conflicts
- [ ] **Commits are clean:** Clear messages following conventional commits format

**Estimated time for checklist:** 5-10 minutes

### Creating the PR

```bash
# 1. Push your changes to your fork
git push origin feature/your-feature

# 2. Create PR using GitHub CLI (recommended)
gh pr create --title "feat: your feature" --body "Description of changes"

# OR create PR via GitHub web interface:
# - Go to your fork on GitHub
# - Click "Compare & pull request"
# - Fill out the PR template
```

### PR Requirements

1. **Title:** Follow commit message format (`type: description`)
   - Good: `feat: add CSV export support`
   - Bad: `Update code`

2. **Description:** Use the PR template, fill ALL sections:
   - What changes were made
   - Why these changes were needed
   - How to test the changes
   - Related issues (use `Fixes #123` to auto-close)

3. **Tests:** All CI checks must pass (security, tests, linting)

4. **Review:** Wait for maintainer approval (usually 1-3 days)

5. **Merge:** Maintainer will squash-merge (preserves clean git history)

### PR Template Sections

Your PR should address:
- **Summary:** What does this PR do?
- **Motivation:** Why is this change needed?
- **Changes:** What code/files were modified?
- **Testing:** How did you test this? What should reviewers test?
- **Screenshots:** (if UI/output changes) Before/after comparison
- **Checklist:** All items checked off

### After PR Merge

```bash
# 1. Switch back to main branch
git checkout main

# 2. Update your local main with merged changes
git pull upstream main

# 3. Delete your feature branch locally
git branch -d feature/your-feature

# 4. Delete your feature branch on your fork
git push origin --delete feature/your-feature
```

---

## 📬 What Happens After Submitting Your PR?

Understanding the PR lifecycle helps set expectations.

### Timeline

**1. Automated Checks (1-5 minutes)**
- ✅ CI runs tests (628 tests across all modules)
- ✅ Security scans (Bandit, pip-audit, safety)
- ✅ Linting and formatting (Black, Pylint)
- ✅ Architecture compliance verification

**2. Initial Review (1-3 days)**
- Maintainer reviews code quality, architecture, security
- Provides feedback or requests changes
- May ask clarifying questions

**3. Revisions (varies - depends on feedback)**
- You address feedback and push updates
- CI runs again on new commits
- Maintainer re-reviews changes

**4. Approval (1-2 days after revisions)**
- Final review and approval
- Maintainer may request minor final tweaks

**5. Merge (immediate after approval)**
- Maintainer squash-merges your PR
- Your changes are now in main branch!
- Branch can be safely deleted

**6. Release (varies - see [RELEASE_PROCESS.md](docs/contributing/RELEASE_PROCESS.md))**
- Change included in next version release
- Mentioned in CHANGELOG.md
- Published to PyPI (for package updates)

### What if my PR goes stale?

**After 7 days of inactivity:**
- We'll ping you with a friendly reminder
- Ask if you need help or want to continue

**After 14 days of inactivity:**
- We may close the PR with "help wanted" label
- You can always reopen when ready!
- Someone else may pick up the work

**Want to prevent staleness?**
- Respond to feedback within a week
- Comment if you need more time
- Ask for help if you're stuck

### Communication During Review

**Have questions?**
- Comment directly on your PR
- Tag `@jvlivonius` for maintainer attention
- Be specific about what you need help with

**Need urgent attention?**
- Mention urgency in PR description (rare, use sparingly)
- Explain why it's time-sensitive (security fix, blocking issue)

**Disagreeing with feedback?**
- That's OK! Explain your reasoning respectfully
- Provide evidence or examples supporting your approach
- Be open to compromise

### After Your PR is Merged

🎉 **Congratulations!** You're now a contributor!

**Next steps:**
- Update your local repository
- Delete your feature branch
- Look for your name in [Contributors](https://github.com/jvlivonius/vsc-extension-scanner/graphs/contributors)
- Check CHANGELOG.md for your contribution mention
- Consider tackling another issue!

---

## Code Style

### Python Style Guidelines

- **Formatter:** [Black](https://github.com/psf/black) (line length: 100 characters)
- **Linter:** [Pylint](https://pylint.org/) (enforced by pre-commit hooks)
- **Security:** [Bandit](https://github.com/PyCQA/bandit) (AST-based security analysis)
- **Import sorting:** [isort](https://pycqa.github.io/isort/) (groups: stdlib, third-party, local)
- **Type hints:** Encouraged for public APIs, required for security-critical functions
- **Docstrings:** [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for all public functions and classes

**All style checks run automatically via pre-commit hooks!**

### Docstring Example

```python
def scan_extension(extension_path: str, cache: bool = True) -> ScanResult:
    """Scan a VS Code extension for security vulnerabilities.

    Args:
        extension_path: Absolute path to extension directory
        cache: Whether to use cached results if available

    Returns:
        ScanResult object containing vulnerability information

    Raises:
        SecurityError: If path validation fails
        APIError: If vscan.dev API is unreachable

    Example:
        >>> result = scan_extension("/path/to/extension")
        >>> print(result.risk_level)
        'high'
    """
```

### Code Comments - Best Practices

```python
# ❌ BAD - Explaining what (obvious from code)
x = x + 1  # Increment x

# ✅ GOOD - Explaining why (non-obvious reasoning)
# Use exponential backoff to avoid overwhelming API during rate limit recovery
time.sleep(2 ** retry_count)

# ✅ GOOD - Warning about subtle issues
# Note: SQLite connections are not thread-safe, use separate connection per thread
connection = sqlite3.connect(db_path)
```

### Documentation Guidelines

- **Markdown formatting:** Follow project conventions (see [DOCUMENTATION_CONVENTIONS.md](docs/contributing/DOCUMENTATION_CONVENTIONS.md))
- **Line length:** Wrap at 100-120 characters for readability
- **Code blocks:** Always specify language for syntax highlighting
- **Links:** Use relative paths for internal docs, absolute for external
- **Examples:** Provide before/after or good/bad examples where helpful

---

## Project Structure

Understanding the codebase organization:

```
vsc-extension-scanner/
├── vscode_scanner/          # Main package (single source of truth)
│   ├── __init__.py         # Package initialization
│   ├── _version.py         # Version management
│   ├── cli.py              # Typer CLI framework (Presentation layer)
│   ├── scanner.py          # Core scan logic (Application layer)
│   ├── display.py          # Rich formatting (Presentation layer)
│   ├── config_manager.py   # Configuration file support (Infrastructure)
│   ├── constants.py        # Centralized constants
│   ├── vscan.py            # Entry point wrapper
│   ├── vscan_api.py        # API client (Infrastructure layer)
│   ├── cache_manager.py    # Caching with HMAC integrity (Infrastructure)
│   ├── extension_discovery.py  # Extension detection (Infrastructure)
│   ├── output_formatter.py     # JSON/CSV export (Infrastructure)
│   ├── html_report_generator.py  # HTML reports (Presentation)
│   ├── types.py            # Result dataclasses (Application layer)
│   └── utils.py            # Path validation, sanitization (Infrastructure)
├── tests/                   # Test suite (628 tests, 72.60% coverage)
│   ├── test_security.py             # Security vulnerability tests
│   ├── test_security_regression.py  # Comprehensive security suite
│   ├── test_path_validation.py      # Path validation tests
│   ├── test_string_sanitization.py  # Sanitization tests
│   ├── test_cache_integrity.py      # HMAC integrity tests
│   ├── test_architecture.py         # Layer compliance tests
│   ├── test_scanner.py              # Scanner module tests
│   ├── test_cli.py                  # CLI module tests
│   └── ...                          # Additional test files
├── docs/                    # Documentation
│   ├── guides/              # Technical references (ARCHITECTURE, SECURITY, etc.)
│   ├── project/             # Project management (PRD, STATUS, roadmaps)
│   ├── contributing/        # Contributor guides
│   └── archive/             # Historical documentation
├── .github/
│   ├── workflows/           # CI/CD pipelines (security, tests, semgrep)
│   ├── ISSUE_TEMPLATE/      # Issue templates (bug, feature, question)
│   └── pull_request_template.md  # PR template
├── scripts/                 # Development scripts
│   ├── bump_version.py      # Version management automation
│   ├── run_tests.py         # Test runner with pytest integration
│   └── check_doc_freshness.sh  # Documentation validation
├── vscan                    # Convenience wrapper for development
├── pyproject.toml           # Modern Python packaging (PEP 621)
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
└── MANIFEST.in              # Distribution rules
```

### Layer Architecture (CRITICAL - Read [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md))

**3-Layer Architecture with one-way dependencies:**

```
Presentation Layer (CLI, Display, HTML Reports)
    ↓ can import from
Application Layer (Scanner, Types)
    ↓ can import from
Infrastructure Layer (API, Cache, Utils, Config)
```

**Key rules:**
- ✅ Presentation can import from Application and Infrastructure
- ✅ Application can import from Infrastructure
- ❌ Infrastructure MUST NEVER import from Presentation or Application
- ❌ No circular dependencies between modules

See [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for detailed architectural guidelines and anti-patterns.

---

## 📚 Glossary

Understanding technical terms used in this project:

**AAA Pattern**
: Arrange-Act-Assert testing pattern (setup → execute → verify). Standard test structure used throughout the codebase.

**Architecture Layer**
: One of three layers (Presentation, Application, Infrastructure) defining module responsibilities and dependencies.

**Bandit**
: AST-based security analyzer for Python that detects common security issues.

**Black**
: Opinionated Python code formatter that enforces consistent style automatically.

**HMAC**
: Hash-based Message Authentication Code - ensures cache integrity and prevents tampering with security scores.

**Layer Violation**
: When code imports from a layer it shouldn't depend on (e.g., Infrastructure importing from Presentation).

**LSP (Language Server Protocol)**
: Protocol providing IDE features like go-to-definition, autocomplete, etc.

**Pre-commit Hook**
: Git hook that runs automated checks (linting, security, formatting) before allowing commits.

**Property-Based Testing**
: Testing approach using automatically generated inputs to test properties/invariants (we use Hypothesis library).

**Pytest**
: Python testing framework used for all tests in this project.

**Sanitization**
: Process of removing dangerous characters from user input to prevent injection attacks.

**Security Context**
: The intended use of a string (output, log, error) determining which characters to sanitize.

**Squash Merge**
: Git merge strategy that combines all PR commits into a single commit on main branch.

**Validation**
: Checking that input meets security and format requirements before processing.

**vscan.dev**
: Third-party security analysis service that powers the extension scanning functionality.

See full documentation in [docs/guides/](docs/guides/) for detailed explanations.

---

## Getting Help

We're here to help! Here's how to get assistance:

### Questions About Contributing

**Have a question about the project or how to contribute?**
- Open a [GitHub issue](https://github.com/jvlivonius/vsc-extension-scanner/issues/new) with `question` label
- Check existing issues first - your question may already be answered
- Be specific about what you're trying to do

### Bug Reports

**Found a bug while developing?**
- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include: OS, Python version, steps to reproduce, expected vs actual behavior
- Bonus points for including a failing test case!

### Feature Requests

**Have an idea for a new feature?**
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Check [PRD.md](docs/project/PRD.md) to see if it fits project scope
- Explain the use case and why it would be valuable

### Security Vulnerabilities

**Found a security issue? Please report privately!**
- Use [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new)
- **DO NOT** open a public issue for security vulnerabilities
- See [SECURITY.md](docs/guides/SECURITY.md) for responsible disclosure policy

### Development Environment Issues

**Setup not working?**
- Check [Troubleshooting Setup](#-troubleshooting-setup) section above
- Search existing issues for similar problems
- Open a new issue with full error details if not found

### Code Review Questions

**Need clarification on PR feedback?**
- Comment directly on the PR
- Ask specific questions about what needs to change
- Request examples if feedback is unclear

---

## Recognition

We value all contributions! Contributors are recognized in:

- **GitHub contributors page:** Automatically tracked by GitHub
- **CHANGELOG.md:** Significant contributions mentioned in release notes
- **Security advisories:** Vulnerability reporters credited (if desired)
- **Documentation:** Tutorial/blog post authors linked from README

**Recognition is automatic** - no need to ask! Just contribute and we'll make sure you're credited.

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

See [LICENSE](LICENSE) file for details.

---

## Thank You! 🎉

Thank you for taking the time to contribute to VS Code Extension Security Scanner!

Your contributions help make VS Code extensions safer for everyone. Whether you're fixing a typo, reporting a bug, or implementing a major feature - every contribution matters.

**Questions or feedback about this guide?** Open an issue - we're always looking to improve our documentation!

Happy contributing! 🚀
