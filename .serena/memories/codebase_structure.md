# Codebase Structure

## Top-Level Organization
```
vsc-extension-scanner/
├── vscode_scanner/         # Main package (SINGLE SOURCE OF TRUTH)
├── tests/                  # Test suite (161+ tests)
├── docs/                   # Documentation
├── scripts/                # Utility scripts (version management)
├── .claude/                # Claude Code framework files
├── .github/                # GitHub workflows
├── vscan                   # Development wrapper script
├── setup.py                # Build configuration (legacy)
├── pyproject.toml         # Modern packaging config
└── MANIFEST.in            # Distribution rules
```

## Main Package (vscode_scanner/)
**Single source architecture - all code in one location**

### Presentation Layer
- `cli.py` - Typer CLI framework, command definitions
- `display.py` - Rich formatting (progress bars, tables, panels)
- `html_report_generator.py` - HTML report generation

### Application Layer
- `scanner.py` - Core scanning logic, orchestration
- `types.py` - Result dataclasses, type definitions

### Infrastructure Layer
- `vscan_api.py` - API client for vscan.dev
- `cache_manager.py` - SQLite caching with HMAC integrity
- `extension_discovery.py` - VS Code extension detection
- `output_formatter.py` - JSON/CSV export
- `config_manager.py` - Configuration file support
- `utils.py` - Path validation, string sanitization
- `constants.py` - Centralized constants

### Support Files
- `__init__.py` - Package initialization
- `_version.py` - Version management
- `vscan.py` - Entry point wrapper

## Tests Organization
```
tests/
├── conftest.py                      # Pytest configuration and fixtures
├── fixtures/                        # Test data and mocks
├── architecture_config.yaml         # Layer compliance rules
├── test_security*.py               # Security test suite
├── test_architecture.py            # Layer violation detection
├── test_*.py                       # Module-specific tests
└── ...                             # Additional test files
```

## Documentation (docs/)
```
docs/
├── guides/                 # Timeless technical reference (REQUIRED reading)
│   ├── ARCHITECTURE.md    # 3-layer architecture rules
│   ├── SECURITY.md        # Security requirements and patterns
│   ├── TESTING.md         # Testing patterns and coverage
│   └── ...
├── project/               # Active project management
│   ├── PRD.md            # Product requirements
│   ├── STATUS.md         # Current sprint status
│   └── v3.5.1-ROADMAP.md # Current roadmap
├── specs/                # Feature specifications
├── contributing/         # Contributor guides
└── archive/             # Historical documentation
```

## Key Patterns
- **No Duplicate Files**: Single source in vscode_scanner/
- **No Synchronization Issues**: One location for all code
- **Development**: Edit in vscode_scanner/, run with ./vscan
- **Distribution**: Built from vscode_scanner/ via setup.py/pyproject.toml
