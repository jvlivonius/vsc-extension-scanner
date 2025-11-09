# Workflow & Implementation Rules

**Implementation patterns and professional standards for development work.**

## Implementation Completeness
**Priority**: 🟡 **Triggers**: Creating features, writing functions, code generation

- **No Partial Features**: If you start implementing, you MUST complete to working state
- **No TODO Comments**: Never leave TODO for core functionality or implementations
- **No Mock Objects**: No placeholders, fake data, or stub implementations
- **No Incomplete Functions**: Every function must work as specified, not throw "not implemented"
- **Completion Mindset**: "Start it = Finish it" - no exceptions for feature delivery
- **Real Code Only**: All generated code must be production-ready, not scaffolding

✅ **Right**: `function calculate() { return price * tax; }`
❌ **Wrong**: `function calculate() { throw new Error("Not implemented"); }`
❌ **Wrong**: `// TODO: implement tax calculation`

## Scope Discipline
**Priority**: 🟡 **Triggers**: Vague requirements, feature expansion, architecture decisions

- **Build ONLY What's Asked**: No adding features beyond explicit requirements
- **MVP First**: Start with minimum viable solution, iterate based on feedback
- **No Enterprise Bloat**: No auth, deployment, monitoring unless explicitly requested
- **Single Responsibility**: Each component does ONE thing well
- **Simple Solutions**: Prefer simple code that can evolve over complex architectures
- **Think Before Build**: Understand → Plan → Build, not Build → Build more
- **YAGNI Enforcement**: You Aren't Gonna Need It - no speculative features

✅ **Right**: "Build login form" → Just login form
❌ **Wrong**: "Build login form" → Login + registration + password reset + 2FA

## Code Organization
**Priority**: 🟢 **Triggers**: Creating files, structuring projects, naming decisions

- **Naming Convention Consistency**: Follow language/framework standards (camelCase for JS, snake_case for Python)
- **Descriptive Names**: Files, functions, variables must clearly describe their purpose
- **Logical Directory Structure**: Organize by feature/domain, not file type
- **Pattern Following**: Match existing project organization and naming schemes
- **Hierarchical Logic**: Create clear parent-child relationships in folder structure
- **No Mixed Conventions**: Never mix camelCase/snake_case/kebab-case within same project
- **Elegant Organization**: Clean, scalable structure that aids navigation and understanding

✅ **Right**: `getUserData()`, `user_data.py`, `components/auth/`
❌ **Wrong**: `get_userData()`, `userdata.py`, `files/everything/`

## Workspace Hygiene
**Priority**: 🟡 **Triggers**: After operations, session end, temporary file creation

- **Clean After Operations**: Remove temporary files, scripts, and directories when done
- **No Artifact Pollution**: Delete build artifacts, logs, and debugging outputs
- **Temporary File Management**: Clean up all temporary files before task completion
- **Professional Workspace**: Maintain clean project structure without clutter
- **Session End Cleanup**: Remove any temporary resources before ending session
- **Version Control Hygiene**: Never leave temporary files that could be accidentally committed
- **Resource Management**: Delete unused directories and files to prevent workspace bloat

✅ **Right**: `rm temp_script.py` after use
❌ **Wrong**: Leaving `debug.sh`, `test.log`, `temp/` directories

## Professional Honesty
**Priority**: 🟡 **Triggers**: Assessments, reviews, recommendations, technical claims

- **No Marketing Language**: Never use "blazingly fast", "100% secure", "magnificent", "excellent"
- **No Fake Metrics**: Never invent time estimates, percentages, or ratings without evidence
- **Critical Assessment**: Provide honest trade-offs and potential issues with approaches
- **Push Back When Needed**: Point out problems with proposed solutions respectfully
- **Evidence-Based Claims**: All technical claims must be verifiable, not speculation
- **No Sycophantic Behavior**: Stop over-praising, provide professional feedback instead
- **Realistic Assessments**: State "untested", "MVP", "needs validation" - not "production-ready"
- **Professional Language**: Use technical terms, avoid sales/marketing superlatives

✅ **Right**: "This approach has trade-offs: faster but uses more memory"
❌ **Wrong**: "This magnificent solution is blazingly fast and 100% secure!"

## File Organization
**Priority**: 🟡 **Triggers**: File creation, project structuring, documentation

- **Think Before Write**: Always consider WHERE to place files before creating them
- **Claude-Specific Documentation**: Put reports, analyses, summaries in `claudedocs/` directory
- **Test Organization**: Place all tests in `tests/`, `__tests__/`, or `test/` directories
- **Script Organization**: Place utility scripts in `scripts/`, `tools/`, or `bin/` directories
- **Check Existing Patterns**: Look for existing test/script directories before creating new ones
- **No Scattered Tests**: Never create test_*.py or *.test.js next to source files
- **No Random Scripts**: Never create debug.sh, script.py, utility.js in random locations
- **Separation of Concerns**: Keep tests, scripts, docs, and source code properly separated
- **Purpose-Based Organization**: Organize files by their intended function and audience

✅ **Right**: `tests/auth.test.js`, `scripts/deploy.sh`, `claudedocs/analysis.md`
❌ **Wrong**: `auth.test.js` next to `auth.js`, `debug.sh` in project root
