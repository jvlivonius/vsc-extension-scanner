# Task Completion Checklist

Before marking any task as complete or committing changes, execute this checklist:

## 1. Security Validation (CRITICAL)
```bash
# Must pass with 0 vulnerabilities
python3 tests/test_security.py
python3 tests/test_security_regression.py
python3 tests/test_path_validation.py
python3 tests/test_string_sanitization.py
python3 tests/test_cache_integrity.py
```

## 2. Architecture Compliance
```bash
# Must show 0 layer violations
python3 tests/test_architecture.py
```

## 3. Core Tests
```bash
# Run relevant module tests
python3 tests/test_display.py
python3 tests/test_scanner.py
python3 tests/test_cli.py
# ... other relevant tests
```

## 4. Code Quality Checks
- [ ] No TODO comments for core functionality
- [ ] No mock/placeholder implementations
- [ ] All functions complete and working
- [ ] Type hints present for function signatures
- [ ] Docstrings added for public functions
- [ ] Security patterns followed (validate_path, sanitize_string)

## 5. Version Consistency (if version changed)
```bash
python3 scripts/bump_version.py --check
```

## 6. Git Review
```bash
git status              # Verify working on feature branch
git diff               # Review all changes
git branch             # Ensure not on main/master
```

## 7. Documentation (if applicable)
- [ ] Updated relevant docs in docs/
- [ ] Updated CHANGELOG.md if user-facing changes
- [ ] Updated README.md if CLI changes

## Coverage Requirements
- **Overall**: 85% minimum
- **Security modules** (utils.py, cache_manager.py): 95% minimum

## Before Commit
- [ ] All tests passing
- [ ] 0 security vulnerabilities
- [ ] 0 architecture violations
- [ ] On feature branch (not main)
- [ ] Changes reviewed with git diff
