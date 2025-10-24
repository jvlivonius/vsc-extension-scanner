#!/usr/bin/env python3
"""
Setup script for vscode-extension-scanner

This file provides backward compatibility for older pip versions.
Modern builds use pyproject.toml instead.
"""

from setuptools import setup, find_packages
import os
import re

# Read version without importing the package (avoids dependency issues during build)
version_file = os.path.join(os.path.dirname(__file__), "vscode_scanner", "_version.py")
with open(version_file, "r", encoding="utf-8") as f:
    version_content = f.read()
    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', version_content, re.MULTILINE)
    if version_match:
        __version__ = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in _version.py")

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vscode-extension-scanner",
    version=__version__,
    author="Joerg von Livonius",
    author_email="your.email@example.com",
    description="Security scanner for VS Code extensions using vscan.dev",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jvlivonius/vsc-extension-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0,<14.0.0",
        "typer>=0.9.0,<1.0.0",
    ],
    extras_require={
        "test": [
            "pyyaml>=6.0.0,<7.0.0",  # For architecture tests configuration
            "pytest>=7.0.0",  # Test framework
        ],
    },
    entry_points={
        "console_scripts": [
            "vscan=vscode_scanner.vscan:cli_main",
        ],
    },
    keywords="vscode security scanner extensions audit vscan",
    project_urls={
        "Documentation": "https://github.com/jvlivonius/vsc-extension-scanner/blob/main/README.md",
        "Source": "https://github.com/jvlivonius/vsc-extension-scanner",
        "Issues": "https://github.com/jvlivonius/vsc-extension-scanner/issues",
    },
)
