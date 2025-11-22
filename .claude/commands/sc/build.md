---
name: build
description: "Build, compile, and package projects"
category: utility
complexity: standard
requires-config: true
---

# /sc:build

## Purpose
Execute project build systems, generate artifacts, and prepare for deployment.

## Triggers
- Project compilation and packaging requests
- Build optimization and artifact generation
- Error debugging during build processes
- Deployment preparation and artifact packaging

## Directives

[REQUIRED]
- Validate build environment and dependencies from PROJECT_CONFIG
- Execute {BUILD_TOOL} with monitoring and error detection
- Generate deployment artifacts
- Provide comprehensive build reports with timing metrics
- Clean build artifacts if requested

[OPTIONAL]
- Use {CODE_DOCS_TOOL} for build tool documentation and patterns
- Apply environment-specific optimizations (dev/prod/test)
- Run {TEST_RUNNER} for build validation
- Generate artifact analysis and size reports
- Optimize build artifacts for deployment

[FORBIDDEN]
- Modify build system configuration without permission
- Install missing build dependencies automatically
- Execute deployment operations beyond artifact preparation
- Skip validation or quality gates

## Workflow
1. Validate: Check environment → verify dependencies → confirm configuration
2. Execute: Run {BUILD_TOOL} → monitor progress → collect metrics
3. Package: Generate artifacts → validate outputs → create build report

## Configuration

Required from PROJECT_CONFIG.yaml:
- tools.build: Build command
- tools.build_clean: Clean command
- paths.build_output: Artifact output directory
- build.*: Build configuration settings

Build types:
- dev: Development build with debugging
- prod: Production build with optimizations
- test: Test build with coverage instrumentation

## Examples

PATTERN: /sc:build
RESULT: Standard build with artifact generation and comprehensive report

PATTERN: /sc:build --type prod --clean --optimize
RESULT: Clean production build with advanced optimizations

PATTERN: /sc:build --verbose
RESULT: Detailed build output with progress monitoring

PATTERN: /sc:build --type dev --validate
RESULT: Development build with test validation

## Reference
See .claude/commands/sc/_sc-reference.md for:
- Tool command patterns
- Error handling patterns
- Quality gate validation
