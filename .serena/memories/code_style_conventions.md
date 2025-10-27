# Code Style & Conventions

## Naming Conventions
- **Functions/Variables**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Module Names**: lowercase with underscores

## Type Hints & Documentation
- **Type Hints**: Required for function signatures
- **Docstrings**: Required for public functions and classes
- **Format**: Google-style docstrings

## Architecture Constraints (CRITICAL)
**3-Layer Architecture - STRICT:**
- **Presentation Layer**: cli.py, display.py, html_report_generator.py
- **Application Layer**: scanner.py, types.py
- **Infrastructure Layer**: vscan_api.py, cache_manager.py, extension_discovery.py, output_formatter.py, config_manager.py, utils.py

**Rules:**
- One-way dependencies only: Presentation → Application → Infrastructure
- Infrastructure layer NEVER imports from Presentation layer
- Zero violations required (enforced by test_architecture.py)

## Security Patterns (MANDATORY)
- **All paths**: Use `validate_path()` from utils.py
- **All user input**: Use `sanitize_string()` with context (output/log/error)
- **All API calls**: HTTPS only, validate responses
- **Error messages**: Sanitized, use ERROR_HELP system
- **Cache integrity**: HMAC-SHA256 signatures

## Design Principles
- **KISS**: Simple solutions over clever ones
- **Fail Fast**: Invalid input raises errors immediately
- **Command-Query Separation**: Commands fail fast, queries return data
- **No Premature Optimization**: Measure first
