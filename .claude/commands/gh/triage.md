---
name: triage
description: "AI-assisted issue triage with intelligent label and priority suggestions"
category: workflow
complexity: advanced
mcp-servers: [sequential-thinking]
personas: [python-expert, quality-engineer]
---

# /gh:triage - AI-Assisted Issue Triage

## Triggers
- New issues requiring classification and prioritization
- Batch triage of multiple unassigned issues
- Issue quality improvement needs
- Label and metadata recommendations

## Usage

```bash
/gh:triage <issue-number> [--auto-apply] [--strict]
/gh:triage --batch [--milestone vX.Y.Z] [--limit N]
/gh:triage --review <issue-number> [--suggest-improvements]
```

**Parameters:**
- `<issue-number>`: Single issue to triage
- `--auto-apply`: Automatically apply suggested labels/metadata
- `--strict`: Use strict validation (all fields required)
- `--batch`: Triage multiple issues
- `--milestone vX.Y.Z`: Filter batch triage by milestone
- `--limit N`: Max issues to triage in batch mode
- `--review`: Review issue quality
- `--suggest-improvements`: Generate improvement suggestions

## Behavioral Flow

1. **Fetch**: Retrieve issue details (title, body, labels, comments)
2. **Analyze**: Use sequential-thinking MCP for comprehensive analysis:
   - Content analysis (what the issue describes)
   - Type classification (feature, bug, task, hotfix)
   - Priority assessment (P0-P3 based on impact/urgency)
   - Complexity estimation (XS, S, M, L, XL)
   - Required documentation identification
3. **Suggest**: Generate recommendations with rationale
4. **Apply**: Optionally update issue with suggestions
5. **Report**: Provide summary with confidence scores

Key behaviors:
- Deep content analysis using sequential-thinking
- Pattern matching against existing issues
- Intelligent label and priority suggestions
- Required documentation recommendations
- Acceptance criteria generation assistance

## Tool Coordination

- **sequential-thinking MCP**: Multi-step analysis and reasoning
- **gh CLI**: Issue fetching and updates (`gh issue view`, `gh issue edit`)
- **Grep**: Search for similar issues
- **Read**: Access project documentation (ARCHITECTURE.md, PRD.md)

## Key Patterns

### Pattern 1: Single Issue Triage

```bash
/gh:triage 160
```

**Analysis workflow:**
1. Fetch issue content
2. Sequential-thinking analysis (7 steps):
   - Parse content and extract key information
   - Classify issue type based on keywords
   - Assess impact (critical, high, medium, low)
   - Estimate complexity based on scope
   - Identify required documentation
   - Check for similar existing issues
   - Generate recommendations with confidence
3. Present suggestions
4. Apply if confirmed

**Example output:**
```
Issue #160: Add CSV export functionality

📊 Analysis Results:

Type: Feature ✓ (confidence: 95%)
Priority: P1-high ⚠️ (confidence: 85%)
Complexity: M (confidence: 80%)

Required Documentation:
- ARCHITECTURE.md (output formatting layer)
- SECURITY.md (CSV injection risks)
- PRD.md (feature scope)

Suggested Labels:
+ feature, P1-high, complexity/M

Apply suggestions? (y/n)
```

### Pattern 2: Batch Triage

```bash
/gh:triage --batch --milestone v3.8.0 --limit 10
```

**Batch workflow:**
1. Fetch untriaged issues for milestone
2. For each issue: run sequential-thinking analysis
3. Present batch summary with confidence grouping
4. Batch apply high-confidence suggestions

**See**: [_gh-reference.md](_gh-reference.md#label-sync-timing) for label sync after batch operations

### Pattern 3: Issue Quality Review

```bash
/gh:triage --review 160 --suggest-improvements
```

**Review analysis:**
1. Validate structure using validation script
2. Content quality analysis (title, description, criteria)
3. Generate improvement suggestions
4. Optionally update issue with improvements

### Pattern 4: Similar Issue Detection

During triage, automatically check for duplicates:

```python
# Search for issues with similar titles and keywords
similar_titles = search_issues_by_title_similarity(issue_title)
keywords = extract_keywords(issue_body)
related_issues = search_issues_by_keywords(keywords)

# Calculate similarity scores
for issue in (similar_titles + related_issues):
    if similarity_score > 0.7:  # High similarity
        suggest_duplicate(issue)
    elif similarity_score > 0.4:  # Related
        suggest_related(issue)
```

## Examples

### Triage New Feature Request

```bash
/gh:triage 160

# Sequential-thinking analysis:
# - Type: Feature (new functionality)
# - Priority: P1-high (user demand + clear use case)
# - Complexity: M (200-400 LOC, new class + tests)
# - Docs: ARCHITECTURE.md, SECURITY.md, PRD.md
# - Similar: #145 (JSON export, closed)

# Suggestions applied → labels added automatically
```

### Batch Triage Milestone

```bash
/gh:triage --batch --milestone v3.8.0

# Analyzes 15 untriaged issues
# Groups by confidence:
#   - 12 high confidence (auto-suggest)
#   - 3 low confidence (needs review)
# User approves → high-confidence labels applied
```

### Auto-Apply Triage

```bash
/gh:triage 161 --auto-apply

# High confidence (>90%) → automatically applies labels
# Reports: "Auto-applied: bug, P0-critical, complexity/S"
```

**Label Sync**: After applying labels, GitHub Actions syncs to project fields within 1-5 minutes.

**See**: [_gh-reference.md](_gh-reference.md#label-sync-timing) for sync automation

## Boundaries

**Will:**
- Analyze issue content using AI reasoning
- Suggest appropriate labels, priority, complexity
- Identify required documentation
- Detect similar/duplicate issues
- Generate acceptance criteria suggestions
- Validate issue structure and quality
- Batch process multiple issues efficiently

**Will Not:**
- Close issues without explicit confirmation
- Modify issue body without user approval
- Assign issues to people without permission
- Make architectural decisions (only suggest documentation)
- Override user's manual classifications
- Auto-triage without confidence thresholds

## Implementation Details

### Analysis Algorithm

```
1. Content Extraction:
   - Parse title for keywords
   - Extract user story if present
   - Identify technical terms and components
   - Analyze description length and clarity

2. Type Classification:
   - feature: "add", "new", "implement", "support"
   - bug: "fix", "error", "crash", "fails", "broken"
   - task: "refactor", "update", "improve", "optimize"
   - hotfix: "critical", "security", "urgent", "CVE"

3. Priority Assessment:
   P0 (Critical): Security, data loss, complete breakage
   P1 (High): Major features, significant bugs, blockers
   P2 (Medium): Nice-to-have features, minor bugs
   P3 (Low): Polish, documentation, minor enhancements

4. Complexity Estimation:
   XS (<50 LOC), S (50-150), M (150-400),
   L (400-1000), XL (>1000)

5. Required Documentation:
   - ARCHITECTURE.md: New components, layer changes
   - SECURITY.md: Input validation, external data
   - PRD.md: Feature scope verification
```

### Confidence Scoring

```python
def calculate_confidence(analysis):
    confidence = 0.5  # Base

    # Boost confidence if:
    if has_clear_keywords(issue): confidence += 0.2
    if similar_issues_exist(issue): confidence += 0.15
    if description_is_detailed(issue): confidence += 0.15

    # Reduce confidence if:
    if title_is_vague(issue): confidence -= 0.2
    if missing_context(issue): confidence -= 0.15
    if conflicting_signals(issue): confidence -= 0.25

    return min(1.0, max(0.0, confidence))
```

**Confidence thresholds:**
- **>0.9**: Auto-apply safe (if --auto-apply)
- **0.7-0.9**: High confidence (suggest with approval)
- **0.5-0.7**: Medium confidence (manual review recommended)
- **<0.5**: Low confidence (requires human judgment)

## Error Handling

**Issue Not Found:**
```
Error: Issue #160 not found
Action: Verify issue number and repository context
```

**Insufficient Context:**
```
Warning: Issue #160 has minimal description
Confidence: Low (45%)
Recommendation: Request more information before triaging
```

**Conflicting Signals:**
```
Warning: Issue #160 has mixed signals
- Title suggests bug fix
- Body describes new feature
Recommendation: Manual triage required or ask author to clarify
```

**See**: [_gh-reference.md](_gh-reference.md#common-error-patterns) for full error reference

## Rate Limiting

**API Call Breakdown:**

| Operation | Issues Processed | API Calls |
|-----------|------------------|-----------|
| Single triage | 1 | ~3-5 |
| Batch triage | 10 | ~35-50 |
| Batch triage | 50 | ~170-250 |

**Rate Limit Management:**
1. Built-in rate limit checking during batch operations
2. Automatic pausing when rate limit drops below 100
3. Resume support after rate limit reset

**Batch Size Guidelines:**
- **>4000 remaining**: Process up to 100 issues
- **1000-4000 remaining**: Process up to 50 issues
- **500-1000 remaining**: Process up to 20 issues
- **<500 remaining**: Single issue only

**See**: [_gh-reference.md](_gh-reference.md#rate-limiting-essentials) for rate limit best practices

## Integration with Workflow

### New Issue Created

```bash
# Webhook or manual trigger
/gh:triage 160

# Review suggestions → Apply labels → Add to milestone
```

### Weekly Triage Session

```bash
# Batch triage untriaged issues
/gh:triage --batch --limit 50

# Review low-confidence manually
# Apply high-confidence suggestions
```

### Issue Quality Gate

```bash
# Before assigning to agent
/gh:triage --review 160 --suggest-improvements

# Ensure quality standards → Add missing info
# Then: /gh:issues-implement 160
```

## References

- [_gh-reference.md](_gh-reference.md) - Shared GitHub command reference
- [GITHUB_PROJECTS.md](../../docs/contributing/GITHUB_PROJECTS.md) - Project workflow
- [validate-issue-structure.sh](../../scripts/github-projects/validate-issue-structure.sh)
- [Sequential-thinking MCP](../mcp/Sequential.md)
