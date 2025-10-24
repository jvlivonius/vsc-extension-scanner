#!/usr/bin/env python3
"""
Architecture Validation Tests

Ensures the codebase maintains Simple Layered Architecture:
- Presentation Layer: cli, display, output_formatter, html_report_generator
- Application Layer: scanner, vscan, config_manager
- Infrastructure Layer: vscan_api, cache_manager, extension_discovery
- Shared: utils, constants, _version

These tests automatically enforce architectural boundaries and prevent violations.
Run with: python3 tests/test_architecture.py

Created: 2025-10-24 (Phase 4.0: Test Infrastructure)
"""

import ast
import sys
import unittest
import yaml
from pathlib import Path
from typing import Set, List, Dict, Optional

# Get path to vscode_scanner package
VSCODE_SCANNER_DIR = Path(__file__).parent.parent / 'vscode_scanner'


def load_architecture_config() -> Dict:
    """
    Load architecture configuration from YAML file.

    Returns:
        Dict containing layer classifications, rules, and metadata

    Raises:
        ValueError: If schema version is unsupported
        FileNotFoundError: If config file doesn't exist
    """
    config_path = Path(__file__).parent / 'architecture_config.yaml'

    if not config_path.exists():
        raise FileNotFoundError(
            f"Architecture config not found: {config_path}\n"
            "Run: tests/architecture_config.yaml must exist"
        )

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Validate schema version
    schema_version = config.get('schema_version')
    if schema_version != 1:
        raise ValueError(
            f"Unsupported config schema version: {schema_version}\n"
            f"Expected: 1"
        )

    return config


# Load configuration from YAML file
_CONFIG = load_architecture_config()

# Extract module lists from config
PRESENTATION_MODULES = _CONFIG['layers']['presentation']['modules']
APPLICATION_MODULES = _CONFIG['layers']['application']['modules']
INFRASTRUCTURE_MODULES = _CONFIG['layers']['infrastructure']['modules']
SHARED_MODULES = _CONFIG['layers']['shared']['modules']

# Extract rules from config
INFRASTRUCTURE_FORBIDDEN = _CONFIG['rules']['infrastructure_forbidden_imports']
SHARED_FORBIDDEN = _CONFIG['rules']['shared_forbidden_imports']
PURE_PRESENTATION = _CONFIG['rules']['pure_presentation_modules']
EXPECTED_MODULE_COUNT = _CONFIG['expected_module_count']


def _parse_file(file_path: Path) -> Optional[ast.AST]:
    """
    Parse Python file with error handling.

    Args:
        file_path: Path to Python file

    Returns:
        AST tree or None if parsing failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return None


def _extract_local_imports(tree: ast.AST) -> Set[str]:
    """
    Extract vscode_scanner imports from AST.

    Handles both relative imports (from .module) and absolute imports
    (from vscode_scanner.module).

    Args:
        tree: Python AST tree

    Returns:
        Set of module names imported from vscode_scanner package
    """
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Handle relative imports: from .module_name import X
            # node.level > 0 indicates relative import (. or .. or ...)
            if node.level > 0 and node.module:
                imports.add(node.module)
            # Handle absolute imports: from vscode_scanner.module import X
            elif node.module and node.module.startswith('vscode_scanner'):
                parts = node.module.split('.')
                if len(parts) > 1:
                    imports.add(parts[1])
        elif isinstance(node, ast.Import):
            # Handle direct imports: import vscode_scanner.module
            for alias in node.names:
                if alias.name.startswith('vscode_scanner.'):
                    parts = alias.name.split('.')
                    if len(parts) > 1:
                        imports.add(parts[1])

    return imports


def get_imports_from_file(file_path: Path) -> Set[str]:
    """
    Extract all local imports from a Python file.

    Orchestrates parsing and extraction into focused functions.

    Args:
        file_path: Path to Python file

    Returns:
        Set of module names imported from vscode_scanner package
        Example: "from .display import X" returns {'display'}
    """
    tree = _parse_file(file_path)
    if tree is None:
        return set()

    return _extract_local_imports(tree)


def get_all_modules() -> List[str]:
    """Get list of all Python modules in vscode_scanner/ (excluding __init__.py)."""
    python_files = VSCODE_SCANNER_DIR.glob('*.py')
    modules = [f.stem for f in python_files if f.name != '__init__.py']
    return sorted(modules)


class TestArchitectureLayering(unittest.TestCase):
    """Test suite for architectural layer boundary validation."""

    def _build_error_message(self, violations: List[Dict], header: str,
                            fix_suggestions: List[str]) -> str:
        """
        Build formatted error message from violations.

        Reduces code duplication and improves maintainability by using
        list + join pattern instead of repeated string concatenation.

        Args:
            violations: List of violation dicts with module, layer, illegal_imports, reason
            header: Error header message
            fix_suggestions: List of fix suggestion strings

        Returns:
            Formatted error message string
        """
        lines = [f"\n\n❌ {header}:\n\n"]

        for v in violations:
            lines.append(f"  {v['module']}.py")
            if 'layer' in v:
                lines.append(f" ({v['layer']} layer)")
            lines.append("\n")

            if 'illegal_imports' in v:
                lines.append(f"    Illegally imports: {', '.join(sorted(v['illegal_imports']))}\n")

            if 'reason' in v:
                lines.append(f"    Reason: {v['reason']}\n")

            lines.append("\n")

        # Add fix suggestions
        lines.append("\n".join(fix_suggestions))

        return ''.join(lines)

    def _check_modules_for_violations(self, modules: List[str],
                                     forbidden_modules: Set[str],
                                     layer_name: str,
                                     reason: str) -> List[Dict]:
        """
        Generic module checking pattern - reduces code duplication.

        Checks a list of modules for imports from forbidden modules.

        Args:
            modules: List of module names to check
            forbidden_modules: Set of module names that are forbidden
            layer_name: Layer name for violation reporting
            reason: Reason string for violation

        Returns:
            List of violation dicts
        """
        violations = []

        for module_name in modules:
            file_path = VSCODE_SCANNER_DIR / f'{module_name}.py'
            if not file_path.exists():
                continue

            imports = get_imports_from_file(file_path)
            violations_found = imports & forbidden_modules

            if violations_found:
                violations.append({
                    'module': module_name,
                    'layer': layer_name,
                    'illegal_imports': sorted(violations_found),
                    'reason': reason
                })

        return violations

    def _find_cycle(self, node: str, visited: Set[str], rec_stack: Set[str],
                   path: List[str], graph: Dict[str, Set[str]]) -> Optional[List[str]]:
        """
        Find cycle in dependency graph using DFS.

        This is extracted as a class method so it can be tested independently
        and reduces complexity of the test_no_circular_dependencies method.

        Args:
            node: Current node to check
            visited: Set of visited nodes
            rec_stack: Recursion stack for cycle detection
            path: Current path being explored
            graph: Dependency graph (module -> set of dependencies)

        Returns:
            List of nodes forming a cycle, or None if no cycle found
        """
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                cycle = self._find_cycle(neighbor, visited, rec_stack, path, graph)
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                # Cycle detected - build cycle path
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]

        path.pop()
        rec_stack.remove(node)
        return None

    def test_infrastructure_layer_isolation(self):
        """
        Infrastructure layer must NOT import from Application or Presentation layers.

        Infrastructure modules should be pure - they interact with external services
        (APIs, databases, filesystems) without knowledge of application logic or UI.

        Allowed imports for Infrastructure:
        - Other Infrastructure modules
        - Shared modules (utils, constants, _version)
        - Standard library only

        Forbidden imports:
        - Application modules (scanner, vscan, config_manager)
        - Presentation modules (cli, display, output_formatter, html_report_generator)
        """
        forbidden_modules = set(APPLICATION_MODULES + PRESENTATION_MODULES)
        violations = self._check_modules_for_violations(
            INFRASTRUCTURE_MODULES,
            forbidden_modules,
            'Infrastructure',
            'Infrastructure cannot import from Application or Presentation'
        )

        if violations:
            fix_suggestions = [
                "Fix: Infrastructure modules should return data/errors to callers.",
                "Let Application/Presentation layers handle display logic.",
                "",
                "See: docs/guides/ARCHITECTURE.md for layer boundaries"
            ]
            error_msg = self._build_error_message(
                violations,
                "ARCHITECTURE VIOLATIONS DETECTED",
                fix_suggestions
            )
            self.fail(error_msg)

    def test_no_circular_dependencies(self):
        """
        Ensure no circular import dependencies exist.

        Circular dependencies make code harder to test and understand.
        They indicate tight coupling and should be refactored.

        Example of circular dependency:
        - module_a imports module_b
        - module_b imports module_a

        This test uses DFS to detect any cycles in the dependency graph.
        """
        all_modules = (PRESENTATION_MODULES + APPLICATION_MODULES +
                      INFRASTRUCTURE_MODULES + SHARED_MODULES)

        # Build dependency graph
        dependency_graph: Dict[str, Set[str]] = {}
        for module_name in all_modules:
            file_path = VSCODE_SCANNER_DIR / f'{module_name}.py'
            if file_path.exists():
                imports = get_imports_from_file(file_path)
                # Only track imports within our module set
                dependency_graph[module_name] = imports & set(all_modules)

        # Check all modules for cycles using DFS
        visited: Set[str] = set()
        for module in dependency_graph:
            if module not in visited:
                cycle = self._find_cycle(module, visited, set(), [], dependency_graph)
                if cycle:
                    lines = [
                        "\n\n❌ CIRCULAR DEPENDENCY DETECTED:\n\n",
                        "  " + " → ".join(cycle) + "\n\n",
                        "Circular dependencies must be resolved.\n",
                        "Consider:\n",
                        "  1. Moving shared code to utils.py\n",
                        "  2. Inverting the dependency\n",
                        "  3. Creating a new shared module"
                    ]
                    self.fail(''.join(lines))

    def test_presentation_layer_dependencies(self):
        """
        Presentation layer can import from Application and Shared layers.
        Should minimize direct Infrastructure imports (use Application as intermediary).

        Presentation modules handle user interaction and output formatting.
        They should coordinate through the Application layer rather than
        directly accessing Infrastructure.

        Special rule: display.py and output_formatter.py should NOT import
        from Infrastructure - they are pure presentation logic.
        """
        violations = []

        # Check pure presentation modules (loaded from config)
        for module_name in PURE_PRESENTATION:
            file_path = VSCODE_SCANNER_DIR / f'{module_name}.py'
            if not file_path.exists():
                continue

            imports = get_imports_from_file(file_path)
            infrastructure_imports = imports & set(INFRASTRUCTURE_MODULES)

            if infrastructure_imports:
                violations.append({
                    'module': module_name,
                    'illegal_imports': sorted(infrastructure_imports),
                    'reason': 'Pure presentation modules should not import from Infrastructure'
                })

        if violations:
            fix_suggestions = [
                "Presentation layer should use Application layer as intermediary.",
                "Move Infrastructure access to scanner.py or vscan.py."
            ]
            error_msg = self._build_error_message(
                violations,
                "PRESENTATION LAYER VIOLATIONS",
                fix_suggestions
            )
            self.fail(error_msg)

    def test_module_count_accuracy(self):
        """
        Verify the documented module count matches reality.

        This test ensures ARCHITECTURE.md stays up to date as modules
        are added or removed from the codebase.

        When this test fails, update docs/guides/ARCHITECTURE.md with
        the current module count.
        """
        actual_modules = get_all_modules()
        actual_count = len(actual_modules)

        # Expected count loaded from architecture_config.yaml
        # Update the config file when modules are added/removed
        expected_count = EXPECTED_MODULE_COUNT

        if actual_count != expected_count:
            lines = [
                "\n\n❌ MODULE COUNT MISMATCH:\n\n",
                f"  Expected: {expected_count} modules (per ARCHITECTURE.md)\n",
                f"  Actual:   {actual_count} modules\n\n",
                "  Current modules:\n"
            ]

            for module in actual_modules:
                # Classify each module
                if module in PRESENTATION_MODULES:
                    layer = "Presentation"
                elif module in APPLICATION_MODULES:
                    layer = "Application"
                elif module in INFRASTRUCTURE_MODULES:
                    layer = "Infrastructure"
                elif module in SHARED_MODULES:
                    layer = "Shared"
                else:
                    layer = "UNCLASSIFIED"

                lines.append(f"    - {module}.py ({layer})\n")

            lines.extend([
                "\nAction: Update docs/guides/ARCHITECTURE.md with current module count.\n",
                "Also update module classifications if new modules exist."
            ])

            self.fail(''.join(lines))

    def test_shared_modules_have_no_app_dependencies(self):
        """
        Shared modules (utils, constants) must not import from any application layers.

        Shared modules should only use standard library to remain truly shared.
        They provide utilities that can be used by any layer without creating
        circular dependencies.

        Allowed imports:
        - Standard library only
        - Other shared modules (e.g., utils can import constants)

        Forbidden imports:
        - Infrastructure modules
        - Application modules
        - Presentation modules
        """
        forbidden = set(PRESENTATION_MODULES + APPLICATION_MODULES +
                       INFRASTRUCTURE_MODULES)

        # Check utils and constants specifically
        critical_shared = ['utils', 'constants']

        violations = self._check_modules_for_violations(
            critical_shared,
            forbidden,
            'Shared',
            'Shared modules must remain dependency-free'
        )

        if violations:
            fix_suggestions = [
                "Shared modules should only use standard library.",
                "They must remain dependency-free to be truly shared.",
                "",
                "If you need application functionality, move code out of utils/constants."
            ]
            error_msg = self._build_error_message(
                violations,
                "SHARED MODULE VIOLATIONS",
                fix_suggestions
            )
            self.fail(error_msg)


def main():
    """Run architecture tests and display results."""
    # Run tests with verbosity
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestArchitectureLayering)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Architecture Validation Summary")
    print("=" * 70)

    if result.wasSuccessful():
        print("\n✅ All architecture tests passed!")
        print("   - Infrastructure layer properly isolated")
        print("   - No circular dependencies detected")
        print("   - Presentation layer follows guidelines")
        print("   - Module count matches documentation")
        print("   - Shared modules remain dependency-free")
    else:
        print(f"\n❌ {len(result.failures)} architecture violation(s) detected")
        print("\nThese violations must be fixed to maintain architectural integrity.")
        print("See docs/guides/ARCHITECTURE.md for layer boundaries and rules.")

        # Return non-zero exit code for CI/CD integration
        sys.exit(1)

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
