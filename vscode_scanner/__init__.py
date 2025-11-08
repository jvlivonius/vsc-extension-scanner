"""
VS Code Extension Security Scanner

A Python CLI tool for comprehensive security audits of VS Code extensions
using the vscan.dev security analysis service.
"""

from ._version import __version__, SCHEMA_VERSION

__author__ = "Joerg von Livonius"
__description__ = "Security scanner for VS Code extensions using vscan.dev"

# Make key components available at package level
from .cli import cli_main

__all__ = ["cli_main", "__version__", "SCHEMA_VERSION"]
