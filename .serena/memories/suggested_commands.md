# Suggested Commands

## Development Workflow

### Running the Tool (Development)
```bash
./vscan scan                    # Run scan locally (3 workers default)
./vscan scan --plain            # Plain output for debugging
./vscan scan --workers 5        # Maximum performance (5 workers)
./vscan --version              # Check version
./vscan --help                 # Show all commands
```

### Testing (REQUIRED before commits)
```bash
# Security tests (CRITICAL - must pass with 0 vulnerabilities)
python3 tests/test_security.py
python3 tests/test_security_regression.py
python3 tests/test_path_validation.py
python3 tests/test_string_sanitization.py
python3 tests/test_cache_integrity.py

# Architecture compliance (must show 0 violations)
python3 tests/test_architecture.py

# Core functionality
python3 tests/test_display.py
python3 tests/test_scanner.py
python3 tests/test_cli.py

# Run all tests
python3 tests/test_*.py
# OR with pytest
pytest tests/
```

### Building & Distribution
```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info

# Build package
python3 -m build

# Test installation
python3 -m venv test_env
source test_env/bin/activate
pip install dist/*.whl
vscan --version
deactivate
```

### Version Management
```bash
python3 scripts/bump_version.py 3.5.2      # Bump version
python3 scripts/bump_version.py --show     # Show current version
python3 scripts/bump_version.py --check    # Verify version consistency
```

### Git Workflow
```bash
git status                      # Always check status first
git branch                      # Verify on feature branch (not main)
git diff                       # Review changes before commit
git add .
git commit -m "message"        # Use descriptive messages
```

## System Utilities (macOS Darwin)
```bash
ls -la                         # List files with details
find . -name "*.py"           # Find Python files
grep -r "pattern" .           # Search for pattern (use Grep tool instead)
cat file.py                   # View file (use Read tool instead)
```

Note: For file operations during development, prefer Claude Code tools (Read, Grep, Glob) over bash commands for better performance and safety.
