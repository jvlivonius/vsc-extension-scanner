# Claude Code Configuration Archive

This directory contains archived SuperClaude framework components that were removed during optimization for the vsc-extension-scanner Python CLI project.

---

## Archive History

### Phase 1 Optimization (2025-11-05)

**Goal**: Focus Claude Code configuration on Python CLI development and reduce context window overhead.

**Results**:
- Reduced configuration from ~80,468 tokens to ~66,278 tokens (17.6% reduction)
- Removed misaligned components for frontend/business/educational contexts
- Eliminated redundant commands covered by native capabilities
- Fixed broken references (PM Agent)
- Improved configuration focus for Python CLI development

---

## Archived Components

### Agents (8 files archived)

**Frontend/Web Development** (Not applicable to Python CLI):
- `frontend-architect.md` - UI/frontend development specialist
- `devops-architect.md` - Infrastructure deployment (simple pip package)
- `backend-architect.md` - Web backend/API servers (not a web service)
- `system-architect.md` - Distributed systems (overlaps with python-expert)

**Business/Educational** (Out of scope):
- `business-panel-experts.md` - Business strategy panel
- `socratic-mentor.md` - Educational Socratic learning guide
- `requirements-analyst.md` - Requirements discovery (PRD stable)
- `technical-writer.md` - Documentation generation (docs comprehensive)
- `refactoring-expert.md` - Code refactoring (overlaps with python-expert)
- `pm-agent.md` - Project management meta-agent
- `learning-guide.md` - Programming education agent

**Rationale**: Python CLI tool (vsc-extension-scanner) uses pytest, typer, rich, hypothesis. No frontend, no distributed systems, no business strategy needs.

---

### Commands (14 files archived)

**Low-Utility Commands** (Overkill or redundant):
- `spec-panel.md` (2,101 words) - Expert panel system, excessive for CLI tool
- `help.md` (1,298 words) - Auto-generatable help content
- `brainstorm.md` (597 words) - Redundant with MODE_Brainstorming.md
- `estimate.md` (472 words) - Rarely used for established CLI project
- `workflow.md` (527 words) - Covered in RULES.md
- `spawn.md` (443 words) - Covered in MODE_Task_Management.md
- `explain.md` (442 words) - Native Claude capability
- `document.md` (405 words) - Native Claude capability
- `index.md` - Documentation indexing
- `load.md` - Redundant with Serena /sc:load
- `reflect.md` - Meta-analysis, rarely used
- `save.md` - Redundant with Serena /sc:save
- `select-tool.md` - Tool selection logic (covered by orchestration)
- `troubleshoot.md` - Debugging (covered by root-cause-analyst)

**Rationale**: 70% overlap with native Claude Code capabilities or other active configurations. Focusing on 9 core commands for Python CLI development.

---

### MCP Servers (4 archived, documented in other files)

**Frontend/Web Tools** (Not applicable):
- `MCP_Magic.md` - UI component generation from 21st.dev (web frontend)
- `MCP_Morphllm.md` - Pattern-based code edits (Serena handles Python symbols)
- `MCP_Playwright.md` - Browser E2E testing (Python uses pytest)
- `MCP_Tavily.md` - Multi-source web research (single API: vscan.dev)

**Rationale**: Python CLI has no UI, uses pytest for testing, single API source (vscan.dev), Serena MCP better for Python symbol operations.

---

### Modes (1 archived)

- `MODE_DeepResearch.md` - Multi-source research workflows (replaced by simplified deep-research-agent)
- `MODE_Business_Panel.md` - Business strategy analysis

**Rationale**: vscan.dev is only external API, no multi-source research needed. Native WebSearch + Sequential MCP sufficient.

---

### Configuration Files (3 archived)

- `RESEARCH_CONFIG.md` (891 words) - Deep research infrastructure settings
- `BUSINESS_PANEL_EXAMPLES.md` - Business strategy examples
- `BUSINESS_SYMBOLS.md` - Business analysis symbols
- `FLAGS.md` (old version) - Verbose archived MCP descriptions

**Rationale**: Business context not relevant, research infrastructure simplified, FLAGS.md replaced with compressed version.

---

## Active Components (Retained for Python CLI)

### Core Framework (8 files)
- ✅ CLAUDE.md - Entry point
- ✅ PRINCIPLES.md - Universal engineering principles
- ✅ RULES.md - Behavioral rules (compressed, PM Agent references removed)
- ✅ FLAGS.md - Tool activation flags (compressed)
- ✅ MODE_Brainstorming.md - Requirements discovery
- ✅ MODE_Introspection.md - Meta-cognitive analysis
- ✅ MODE_Orchestration.md - Tool selection optimization
- ✅ MODE_Task_Management.md - Multi-step task organization
- ✅ MODE_Token_Efficiency.md - Symbol-based communication (compressed)

### MCP Servers (3 active)
- ✅ MCP_Context7.md - Python library docs (pytest, typer, rich, hypothesis)
- ✅ MCP_Sequential.md - Complex debugging and architecture analysis
- ✅ MCP_Serena.md - Symbol operations, session persistence

### Agents (6 active)
- ✅ python-expert.md - Primary Python specialist
- ✅ security-engineer.md - Security auditing (SECURITY.md enforcement)
- ✅ quality-engineer.md - Testing and coverage (pytest + hypothesis)
- ✅ performance-engineer.md - Performance optimization
- ✅ root-cause-analyst.md - Debugging and failure investigation
- ✅ deep-research-agent.md - Research capabilities (simplified)

### Commands (9 active)
- ✅ analyze.md - Code analysis
- ✅ build.md - Build and package (pip distribution)
- ✅ cleanup.md - Code cleanup and organization
- ✅ design.md - Architecture design
- ✅ git.md - Git operations and workflow
- ✅ implement.md - Feature implementation
- ✅ improve.md - Code improvement and refactoring
- ✅ task.md - Complex task execution
- ✅ test.md - Testing operations (pytest, hypothesis, coverage)

---

## Restoration Instructions

If you need to restore archived components:

```bash
# Restore a specific agent
cp .claude/.archive/agents/frontend-architect.md .claude/agents/

# Restore a specific command
cp .claude/.archive/commands/sc/spec-panel.md .claude/commands/sc/

# Update metadata file
# Edit .claude/.superclaude-metadata.json to add back to agents_list or increment files_count
```

**Note**: Restoration requires updating `.superclaude-metadata.json` to reflect the change.

---

## Future Optimization (Phase 2)

If Phase 1 validation is successful (1 week), consider:

1. **Compress RULES.md** (30% reduction, ~930 tokens)
   - Consolidate repetitive examples
   - Reduce emoji usage by 50%
   - Compress Quick Reference section

2. **Consolidate Commands** (~8,000 tokens)
   - Merge 9 remaining command files into single reference
   - Eliminate template duplication
   - Easier maintenance

3. **Archive Deep Research Infrastructure** (~5,000 tokens)
   - `deep-research-agent.md` (735 words)
   - **Rationale**: vscan.dev is ONLY external API, no multi-source research
   - Native WebSearch + Sequential MCP sufficient

**Total Phase 2 Savings**: ~13,930 tokens (additional 17.3% reduction)

---

## Metadata

**Optimization Date**: 2025-11-05
**Phase**: Phase 1 (Low-Risk Quick Wins)
**Token Savings**: ~14,190 tokens (17.6% reduction)
**Files Archived**: 26 total (8 agents, 14 commands, 4 MCPs)
**Risk Level**: LOW - No functionality loss, easy rollback via git
**Project Context**: Python CLI tool (vsc-extension-scanner)
**Technology Stack**: pytest, typer, rich, hypothesis, SQLite, pip distribution
