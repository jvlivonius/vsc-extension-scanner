"""
VS Code Extension Security Scanner

A Python CLI tool for comprehensive security audits of VS Code extensions
using the vscan.dev security analysis service.
"""

__version__ = "2.2.1"
__author__ = "Joerg von Livonius"
__description__ = "Security scanner for VS Code extensions using vscan.dev"

# Make key components available at package level
from .vscan import main

__all__ = ['main', '__version__']
