# Important Guidelines & Design Patterns

## Critical Documentation (READ BEFORE CHANGES)
Before ANY code changes, you MUST read:
1. `docs/guides/ARCHITECTURE.md` - System architecture, design principles, anti-patterns
2. `docs/guides/SECURITY.md` - Security requirements, validation patterns, threat model
3. `docs/project/PRD.md` - Product requirements, feature scope, constraints

## Security Patterns (NON-NEGOTIABLE)

### Path Validation
```python
from vscode_scanner.utils import validate_path
# ALWAYS validate paths before use
validated_path = validate_path(user_provided_path)
```
- Blocks URL-encoded traversal attacks
- Prevents access to system directories
- Enforces absolute paths only

### String Sanitization
```python
from vscode_scanner.utils import sanitize_string
# Context-aware sanitization for all user input
safe_output = sanitize_string(user_input, context='output')
safe_log = sanitize_string(user_input, context='log')
safe_error = sanitize_string(user_input, context='error')
```

### HMAC Cache Integrity
- All cache entries signed with HMAC-SHA256
- Prevents tampering with security scores
- Validation on every cache read

## Threading Model (v3.5.0+)
```python
# Parallel scanning with ThreadPoolExecutor
ThreadPoolExecutor(max_workers=3)  # Default: 3, Range: 1-5

# Thread-safe statistics
from vscode_scanner.scanner import ThreadSafeStats
stats = ThreadSafeStats()  # Uses locks for shared state

# Database writes - MAIN THREAD ONLY
# SQLite limitation: write operations in main thread
```

## Error Handling Philosophy
- **Exit Codes**:
  - 0 = Success, no vulnerabilities found
  - 1 = Success, vulnerabilities found
  - 2 = Scan failed
- **Fail Fast**: Invalid input → immediate error (don't continue)
- **Resilience**: Individual extension failure → continue scan
- **ERROR_HELP**: All errors include actionable guidance

## Design Patterns

### Command-Query Separation
- **Commands**: Modify state, fail fast, return None
- **Queries**: Return data, don't modify state

### KISS Principle
- Simple solutions > clever optimizations
- Measure before optimizing
- Avoid premature complexity

### Test-Driven Quality
- AAA pattern (Arrange-Act-Assert)
- 85% overall coverage, 95% for security
- All tests must pass before commit
- Security tests must show 0 vulnerabilities

## Anti-Patterns (AVOID)
- Infrastructure importing from Presentation layer
- Skipping path validation
- Bypassing string sanitization
- Disabling/commenting tests to make builds pass
- Working directly on main/master branch
- Incomplete implementations with TODO comments
- Mixed naming conventions (stick to snake_case for Python)
