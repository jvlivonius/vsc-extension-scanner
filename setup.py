#!/usr/bin/env python3
"""
Setup script for vscode-extension-scanner

This file provides backward compatibility for older pip versions.
Modern builds use pyproject.toml instead.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vscode-extension-scanner",
    version="2.2.1",
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
    entry_points={
        "console_scripts": [
            "vscan=vscode_scanner.vscan:main",
        ],
    },
    keywords="vscode security scanner extensions audit vscan",
    project_urls={
        "Documentation": "https://github.com/jvlivonius/vsc-extension-scanner/blob/main/README.md",
        "Source": "https://github.com/jvlivonius/vsc-extension-scanner",
        "Issues": "https://github.com/jvlivonius/vsc-extension-scanner/issues",
    },
)
