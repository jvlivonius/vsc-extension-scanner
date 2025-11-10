# Contributing to VS Code Extension Security Scanner

[![CI Status](https://github.com/jvlivonius/vsc-extension-scanner/workflows/CI/badge.svg)](https://github.com/jvlivonius/vsc-extension-scanner/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

Thank you for your interest in contributing! This guide helps you get started quickly and points you to detailed documentation for specific tasks.

---

## Quick Start

**Get up and running in 10 minutes:**

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/vsc-extension-scanner.git
cd vsc-extension-scanner

# 2. Install dependencies
pip install -e .[dev,test]

# 3. Set up pre-commit hooks
pre-commit install

# 4. Verify everything works
python3 -m pytest tests/ -v

# 5. Try the tool
./vscan --help
```

**✅ You're ready to contribute!**

---

## I Want To...

Choose what you'd like to do:

### 📝 Improve Documentation

**Good for:** First-time contributors, no code required

- Fix typos or unclear explanations
- Add examples or clarify existing docs
- Improve code comments

**Time:** 5-30 minutes

**Next steps:**
1. Edit files directly on GitHub (use web editor)
2. Submit a pull request with your changes
3. See [docs/contributing/DOCUMENTATION_STANDARDS.md](docs/contributing/DOCUMENTATION_STANDARDS.md) for guidelines

### 🐛 Report a Bug

**Good for:** Users who found issues

- Report problems you encountered
- Provide reproduction steps
- Help improve quality

**Time:** 10-20 minutes

**Next steps:**
1. Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
2. Include: OS, Python version, steps to reproduce
3. Check existing issues first to avoid duplicates

### ✨ Add Features or Fix Bugs

**Good for:** Python developers

**Before you start:**
1. **Check scope:** Review [docs/project/PRD.md](docs/project/PRD.md) - is your feature in scope?
2. **Create an issue:** Discuss your approach before implementing
3. **Read required docs:**
   - [docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) - 3-layer architecture rules
   - [docs/guides/SECURITY.md](docs/guides/SECURITY.md) - Security patterns (validate_path, sanitize_string)
   - [docs/project/PRD.md](docs/project/PRD.md) - Project scope and constraints

**Time:** 1-4 hours depending on complexity

**Next steps:**
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Make changes following [Git Workflow](#git-workflow-essentials)
3. Write tests: See [docs/guides/TESTING.md](docs/guides/TESTING.md)
4. Submit PR: Follow [Pull Request Process](#pull-request-checklist)

### 🧪 Improve Tests

**Good for:** QA-minded contributors

- Write new test cases
- Improve test coverage
- Add edge case testing

**Time:** 30 minutes - 2 hours

**Next steps:**
1. Check current coverage: `pytest tests/ --cov=vscode_scanner --cov-report=html`
2. See [docs/guides/TESTING.md](docs/guides/TESTING.md) for testing patterns
3. Add tests following AAA pattern (Arrange-Act-Assert)

### 🔒 Report Security Vulnerability

**IMPORTANT:** Do not report security issues publicly

**Next steps:**
1. Use [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new)
2. See [SECURITY.md](SECURITY.md) for disclosure policy
3. Response within 48 hours

---

## Git Workflow Essentials

**Simple process for all contributions:**

```bash
# 1. Start from updated main
git checkout main
git pull upstream main

# 2. Create feature branch (descriptive name!)
git checkout -b feature/your-feature-name
# Branch types: feature/*, bugfix/*, hotfix/*, docs/*, test/*

# 3. Make changes and commit with clear messages
git add .
git commit -m "feat(scope): description of changes"
# Commit types: feat, fix, hotfix, docs, test, refactor, chore

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Create pull request on GitHub
gh pr create --title "feat: your feature" --body "Description"
# Or use GitHub web interface
```

**Full workflow details:** [docs/contributing/GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md)

---

## Pull Request Checklist

Before submitting your PR, verify:

- [ ] **Tests pass:** `pytest tests/` shows all green
- [ ] **Security tests pass:** `python3 tests/test_security.py` shows 0 vulnerabilities
- [ ] **Pre-commit hooks pass:** `pre-commit run --all-files` succeeds
- [ ] **Documentation updated:** If you changed behavior, update relevant docs
- [ ] **Branch is up to date:** `git pull upstream main` and resolve conflicts

**After submitting:**
1. CI checks will run automatically (5 minutes)
2. Maintainer review (1-3 days)
3. Address any feedback
4. PR merged!

**Full PR process:** [docs/contributing/GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md)

---

## Critical Rules

### 🔴 Security (MUST follow)

**All file paths MUST use `validate_path()`:**

```python
from vscode_scanner.utils import validate_path

# ✅ CORRECT
validated_path = validate_path(user_input)
with open(validated_path, 'r') as f:
    data = f.read()

# ❌ WRONG - Security vulnerability!
with open(user_input, 'r') as f:
    data = f.read()
```

**All user-facing strings MUST use `sanitize_string()`:**

```python
from vscode_scanner.utils import sanitize_string

# ✅ CORRECT
print(sanitize_string(extension_name, context='output'))

# ❌ WRONG - Injection vulnerability!
print(f"Extension: {extension_name}")
```

**Why:** Prevents directory traversal (CWE-22) and injection attacks

**See:** [docs/guides/SECURITY.md](docs/guides/SECURITY.md) for complete security requirements

### 🟡 Architecture (IMPORTANT)

**3-Layer Architecture with one-way dependencies:**

```
Presentation Layer (CLI, Display, HTML Reports)
    ↓ can import from
Application Layer (Scanner, Types)
    ↓ can import from
Infrastructure Layer (API, Cache, Utils, Config)
```

**Rules:**
- ✅ Presentation can import from Application and Infrastructure
- ✅ Application can import from Infrastructure
- ❌ Infrastructure MUST NEVER import from Presentation or Application

**See:** [docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for detailed rules

### 🟢 Testing (REQUIRED)

**Coverage targets:**
- Security modules (`utils.py`): ≥95% coverage
- Core logic (`scanner.py`, `cache_manager.py`): ≥85% coverage
- Presentation layer (`cli.py`, `display.py`): ≥70% coverage

**Test pattern (AAA):**

```python
def test_feature_name():
    """Test that feature_name handles expected_scenario correctly."""
    # Arrange: Set up test data
    input_data = "test_value"

    # Act: Execute the feature
    result = feature_function(input_data)

    # Assert: Verify expected outcome
    assert result == "expected_output"
```

**See:** [docs/guides/TESTING.md](docs/guides/TESTING.md) for comprehensive testing guide

---

## Documentation Reference

### Essential Reading (Required for Code Changes)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) | 3-layer architecture, design principles | Before coding |
| [docs/guides/SECURITY.md](docs/guides/SECURITY.md) | Security patterns, validation functions | Before coding |
| [docs/project/PRD.md](docs/project/PRD.md) | Project scope, requirements | Before proposing features |

### Workflow Guides (Task-Specific)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [docs/contributing/GIT_WORKFLOW.md](docs/contributing/GIT_WORKFLOW.md) | Complete git workflow, branching strategy | When contributing |
| [docs/guides/TESTING.md](docs/guides/TESTING.md) | Testing philosophy, patterns, tools | When writing tests |
| [docs/contributing/RELEASE_PROCESS.md](docs/contributing/RELEASE_PROCESS.md) | Release procedure (11 steps) | For maintainers |
| [docs/contributing/DOCUMENTATION_STANDARDS.md](docs/contributing/DOCUMENTATION_STANDARDS.md) | Documentation style, structure | When writing docs |

### Reference Documentation (As Needed)

| Document | Purpose |
|----------|---------|
| [docs/project/STATUS.md](docs/project/STATUS.md) | Current version, test metrics, roadmap |
| [docs/guides/API_REFERENCE.md](docs/guides/API_REFERENCE.md) | vscan.dev API documentation |
| [docs/guides/PERFORMANCE.md](docs/guides/PERFORMANCE.md) | Performance optimization guide |
| [docs/guides/ERROR_HANDLING.md](docs/guides/ERROR_HANDLING.md) | Error handling strategy |
| [docs/guides/testing/](docs/guides/testing/) | Specialized testing guides (security, coverage, mocking, etc.) |

**Full documentation index:** [docs/README.md](docs/README.md)

---

## Code Style

**Automated enforcement via pre-commit hooks:**

- **Formatter:** Black (line length: 100 characters)
- **Linter:** Pylint
- **Security:** Bandit (AST-based security analysis)
- **Import sorting:** isort
- **Type hints:** Encouraged for public APIs, required for security-critical functions
- **Docstrings:** Google style for public functions

**Run all checks:** `pre-commit run --all-files`

---

## Project Structure

```
vsc-extension-scanner/
├── vscode_scanner/          # Main package
│   ├── cli.py              # CLI framework (Presentation)
│   ├── scanner.py          # Core scan logic (Application)
│   ├── display.py          # Rich formatting (Presentation)
│   ├── vscan_api.py        # API client (Infrastructure)
│   ├── cache_manager.py    # Caching with HMAC (Infrastructure)
│   ├── utils.py            # validate_path, sanitize_string (Infrastructure)
│   └── ...                 # Other modules
├── tests/                   # Test suite (1,100+ tests)
├── docs/                    # Documentation
│   ├── guides/              # Technical references
│   ├── project/             # Project management (PRD, STATUS)
│   ├── contributing/        # Contributor guides
│   └── archive/             # Historical documentation
├── scripts/                 # Development scripts
└── .github/                 # CI/CD, issue templates
```

**See:** [docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md) for layer responsibilities

---

## Getting Help

**Have questions?**

- 💬 **Contributing questions:** Open a [GitHub issue](https://github.com/jvlivonius/vsc-extension-scanner/issues/new) with `question` label
- 🐛 **Bug reports:** Use [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- 💡 **Feature ideas:** Use [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- 🔒 **Security issues:** Use [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new) (private)

**Setup issues?**

Common solutions:
- `pip install -e .[dev,test]` fails → Upgrade pip: `python3 -m pip install --upgrade pip`
- Pre-commit hooks fail first run → Expected! Run again: `pre-commit run --all-files`
- `./vscan` not found → Make executable: `chmod +x vscan`

---

## Code of Conduct

**Our Standards:**

- ✅ Be respectful and constructive in all interactions
- ✅ Welcome newcomers and answer questions patiently
- ✅ Focus on what's best for the project and community
- ✅ Accept constructive criticism gracefully
- ❌ No harassment, discrimination, or unprofessional conduct

**Reporting:** Contact maintainers via [GitHub Security Advisories](https://github.com/jvlivonius/vsc-extension-scanner/security/advisories/new) for conduct issues

**Full code of conduct:** [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## Recognition

Contributors are recognized in:

- GitHub contributors page (automatic)
- [CHANGELOG.md](CHANGELOG.md) release notes (significant contributions)
- Security advisories (vulnerability reporters, if desired)

**Recognition is automatic** - just contribute and we'll credit you!

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

See [LICENSE](LICENSE) file for details.

---

## Thank You! 🎉

Your contributions help make VS Code extensions safer for everyone. Whether you're fixing a typo, reporting a bug, or implementing a feature - every contribution matters.

**Questions about this guide?** Open an issue - we're always improving our documentation!

Happy contributing! 🚀
