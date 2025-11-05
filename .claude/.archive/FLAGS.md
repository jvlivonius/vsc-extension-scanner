# SuperClaude Framework Flags

Behavioral flags for Claude Code to enable specific execution modes and tool selection patterns.

## Mode Activation Flags

**--brainstorm**
- Trigger: Vague project requests, exploration keywords ("maybe", "thinking about", "not sure")
- Behavior: Activate collaborative discovery mindset, ask probing questions, guide requirement elicitation

**--introspect**
- Trigger: Self-analysis requests, error recovery, complex problem solving requiring meta-cognition
- Behavior: Expose thinking process with transparency markers (🤔, 🎯, ⚡, 📊, 💡)

**--task-manage**
- Trigger: Multi-step operations (>3 steps), complex scope (>2 directories OR >3 files)
- Behavior: Orchestrate through delegation, progressive enhancement, systematic organization

**--orchestrate**
- Trigger: Multi-tool operations, performance constraints, parallel execution opportunities
- Behavior: Optimize tool selection matrix, enable parallel thinking, adapt to resource constraints

**--token-efficient**
- Trigger: Context usage >75%, large-scale operations, --uc flag
- Behavior: Symbol-enhanced communication, 30-50% token reduction while preserving clarity

## MCP Server Flags

**Python CLI Optimization Status:**

✅ **Available MCPs** (Python CLI development):
- `--c7 / --context7`: Python library documentation (pytest, typer, rich, hypothesis)
- `--seq / --sequential`: Complex debugging, architecture analysis, systematic reasoning
- `--serena`: Symbol operations, project memory, session persistence

⚠️ **Archived MCPs** (not applicable to Python CLI):
- `--magic`: UI component generation (web frontend tool) → See `.claude/archive/MCP_Magic.md`
- `--morph / --morphllm`: Pattern edits (Serena handles Python symbols better) → See `.claude/archive/MCP_Morphllm.md`
- `--play / --playwright`: Browser automation (E2E web testing) → See `.claude/archive/MCP_Playwright.md`
- `--tavily`: Multi-source web research (single API: vscan.dev) → See `.claude/archive/MCP_Tavily.md`
- `--chrome / --devtools`: Browser inspection (frontend tool)
- `--frontend-verify`: Frontend testing combination → See `.claude/archive/`

---

### Available MCP Server Flags

**--c7 / --context7**
- Trigger: Library imports, framework questions, official documentation needs
- Behavior: Enable Context7 for curated documentation lookup and pattern guidance
- **Python CLI Context**: pytest patterns, typer CLI design, rich formatting, hypothesis property testing

**--seq / --sequential**
- Trigger: Complex debugging, system design, multi-component analysis
- Behavior: Enable Sequential for structured multi-step reasoning and hypothesis testing
- **Python CLI Context**: Root cause analysis (scanner + API + cache), 3-layer architecture validation, performance investigation

**--serena**
- Trigger: Symbol operations, project memory needs, large codebase navigation
- Behavior: Enable Serena for semantic understanding and session persistence
- **Python CLI Context**: Symbol refactoring (rename/extract/move), multi-session work (/sc:load, /sc:save), testability improvements

---

### Archived MCP Server Flags

**⚠️ --magic** [ARCHIVED - Not applicable to Python CLI]
- ~~Trigger: UI component requests (/ui, /21), design system queries, frontend development~~
- ~~Behavior: Enable Magic for modern UI generation from 21st.dev patterns~~
- **Archived**: See `.claude/archive/MCP_Magic.md` for original documentation

**⚠️ --morph / --morphllm** [ARCHIVED - Serena handles Python symbol operations]
- ~~Trigger: Bulk code transformations, pattern-based edits, style enforcement~~
- ~~Behavior: Enable Morphllm for efficient multi-file pattern application~~
- **Archived**: See `.claude/archive/MCP_Morphllm.md` for original documentation

**⚠️ --play / --playwright** [ARCHIVED - Use pytest for Python testing]
- ~~Trigger: Browser testing, E2E scenarios, visual validation, accessibility testing~~
- ~~Behavior: Enable Playwright for real browser automation and testing~~
- **Archived**: See `.claude/archive/MCP_Playwright.md` for original documentation

**⚠️ --chrome / --devtools** [ARCHIVED - Frontend debugging tool]
- ~~Trigger: Performance auditing, debugging, layout issues, network analysis, console errors~~
- ~~Behavior: Enable Chrome DevTools for real-time browser inspection and performance analysis~~
- **Archived**: See `.claude/archive/` for original documentation

**⚠️ --tavily** [ARCHIVED - Single API source (vscan.dev), use WebSearch]
- ~~Trigger: Web search requests, real-time information needs, research queries, current events~~
- ~~Behavior: Enable Tavily for web search and real-time information gathering~~
- **Archived**: See `.claude/archive/MCP_Tavily.md` for original documentation

**⚠️ --frontend-verify** [ARCHIVED - Frontend testing combination]
- ~~Trigger: UI testing requests, frontend debugging, layout validation, component verification~~
- ~~Behavior: Enable Playwright + Chrome DevTools + Serena for comprehensive frontend verification and debugging~~
- **Archived**: See `.claude/archive/` for original documentation

---

### MCP Control Flags

**--all-mcp**
- Trigger: Maximum complexity scenarios, multi-domain problems
- Behavior: Enable all **available** MCP servers (serena, sequential, context7)
- **Note**: Only enables Python CLI relevant MCPs, not archived frontend/web tools

**--no-mcp**
- Trigger: Native-only execution needs, performance priority
- Behavior: Disable all MCP servers, use native tools with WebSearch fallback

## Analysis Depth Flags

**--think**
- Trigger: Multi-component analysis needs, moderate complexity
- Behavior: Standard structured analysis (~4K tokens), enables Sequential
- **Python CLI Context**: Module-level refactoring, test strategy planning

**--think-hard**
- Trigger: Architectural analysis, system-wide dependencies
- Behavior: Deep analysis (~10K tokens), enables Sequential + Context7
- **Python CLI Context**: 3-layer architecture compliance, threading model analysis, security validation

**--ultrathink**
- Trigger: Critical system redesign, legacy modernization, complex debugging
- Behavior: Maximum depth analysis (~32K tokens), enables all **available** MCP servers (serena, sequential, context7)
- **Python CLI Context**: v3.6 testability refactoring, comprehensive security audit, parallel processing optimization

## Execution Control Flags

**--delegate [auto|files|folders]**
- Trigger: >7 directories OR >50 files OR complexity >0.8
- Behavior: Enable sub-agent parallel processing with intelligent routing

**--concurrency [n]**
- Trigger: Resource optimization needs, parallel operation control
- Behavior: Control max concurrent operations (range: 1-15)

**--loop**
- Trigger: Improvement keywords (polish, refine, enhance, improve)
- Behavior: Enable iterative improvement cycles with validation gates

**--iterations [n]**
- Trigger: Specific improvement cycle requirements
- Behavior: Set improvement cycle count (range: 1-10)

**--validate**
- Trigger: Risk score >0.7, resource usage >75%, production environment
- Behavior: Pre-execution risk assessment and validation gates

**--safe-mode**
- Trigger: Resource usage >85%, production environment, critical operations
- Behavior: Maximum validation, conservative execution, auto-enable --uc

## Output Optimization Flags

**--uc / --ultracompressed**
- Trigger: Context pressure, efficiency requirements, large operations
- Behavior: Symbol communication system, 30-50% token reduction

**--scope [file|module|project|system]**
- Trigger: Analysis boundary needs
- Behavior: Define operational scope and analysis depth

**--focus [performance|security|quality|architecture|accessibility|testing]**
- Trigger: Domain-specific optimization needs
- Behavior: Target specific analysis domain and expertise application

## Flag Priority Rules

**Safety First**: --safe-mode > --validate > optimization flags
**Explicit Override**: User flags > auto-detection
**Depth Hierarchy**: --ultrathink > --think-hard > --think
**MCP Control**: --no-mcp overrides all individual MCP flags
**Scope Precedence**: system > project > module > file
