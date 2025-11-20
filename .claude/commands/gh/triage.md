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
1. **Fetch issue content:**
   ```bash
   gh issue view 160 --json number,title,body,labels,comments
   ```

2. **Sequential-thinking analysis:**
   - **Step 1**: Parse issue content and extract key information
   - **Step 2**: Classify issue type based on keywords and description
   - **Step 3**: Assess impact (critical, high, medium, low)
   - **Step 4**: Estimate complexity based on scope
   - **Step 5**: Identify required documentation
   - **Step 6**: Check for similar existing issues
   - **Step 7**: Generate recommendations with confidence

3. **Present suggestions:**
   ```
   Issue #160: Add CSV export functionality

   📊 Analysis Results:

   Type: Feature ✓ (confidence: 95%)
   Rationale: New functionality addition, not fixing existing behavior

   Priority: P1-high ⚠️ (confidence: 85%)
   Rationale: User-requested feature with clear demand, impacts usability

   Complexity: M (confidence: 80%)
   Rationale: Requires new class, CLI integration, tests (~200-400 LOC)

   Required Documentation:
   - ARCHITECTURE.md (understand output formatting layer)
   - SECURITY.md (validate CSV injection risks)
   - PRD.md (verify feature scope)

   Similar Issues:
   - #145: JSON export (closed) - can reuse patterns

   Suggested Labels:
   + feature (add)
   + P1-high (add)
   + complexity/M (add)

   Acceptance Criteria Suggestion:
   - [ ] CSV formatter class with proper escaping
   - [ ] --output-csv CLI flag
   - [ ] Tests for edge cases (special chars, large datasets)
   - [ ] Documentation updated

   Apply suggestions? (y/n)
   ```

4. **Apply if confirmed:**
   ```bash
   gh issue edit 160 \
     --add-label "feature,P1-high,complexity/M"
   ```

### Pattern 2: Batch Triage

```bash
/gh:triage --batch --milestone v3.8.0 --limit 10
```

**Batch workflow:**
1. **Fetch untriaged issues:**
   ```bash
   gh issue list \
     --milestone v3.8.0 \
     --state open \
     --label "needs-triage" \
     --limit 10 \
     --json number,title,body
   ```

2. **For each issue:**
   - Run sequential-thinking analysis
   - Generate recommendations
   - Store results

3. **Present batch summary:**
   ```
   Batch Triage: v3.8.0 (10 issues)

   High Confidence (8 issues):
   - #160: Feature, P1-high, M → Auto-apply? ✓
   - #161: Bug, P0-critical, S → Auto-apply? ✓
   - #162: Task, P2-medium, S → Auto-apply? ✓
   ...

   Low Confidence (2 issues):
   - #165: Unclear type, needs clarification
   - #167: Complex scope, requires discussion

   Apply high-confidence suggestions? (y/n)
   ```

4. **Batch apply:**
   ```bash
   # For each high-confidence issue
   gh issue edit <N> --add-label "..."
   ```

### Pattern 3: Issue Quality Review

```bash
/gh:triage --review 160 --suggest-improvements
```

**Review analysis:**
1. **Validate issue structure:**
   ```bash
   ./scripts/github-projects/validate-issue-structure.sh 160 --strict
   ```

2. **Content quality analysis:**
   - Title clarity (specific, actionable)
   - Description completeness
   - Acceptance criteria quality
   - Required documentation presence
   - Reproducibility (for bugs)

3. **Generate improvement suggestions:**
   ```
   Issue #160 Quality Review:

   ✓ Title: Clear and specific
   ✗ Description: Missing user story context
   ⚠️ Acceptance Criteria: Present but vague
   ✗ Required Documentation: Not specified
   ✓ Labels: Properly tagged

   Quality Score: 6/10

   Improvement Suggestions:

   1. Add user story context:
      "As a security auditor, I want to export scan results as CSV
       so that I can analyze them in spreadsheet tools"

   2. Enhance acceptance criteria:
      - [ ] CSV formatter handles special characters (commas, quotes)
      - [ ] Supports large datasets (>1000 extensions)
      - [ ] Compatible with Excel and Google Sheets

   3. Add required documentation:
      Required Documentation: ARCHITECTURE.md, SECURITY.md, PRD.md

   4. Consider edge cases:
      - Empty scan results
      - Unicode characters in extension names
      - Very large result sets

   Would you like me to update the issue with these improvements? (y/n)
   ```

### Pattern 4: Similar Issue Detection

During triage, automatically check for duplicates or related issues:

```python
# Pseudocode for similar issue detection
def find_similar_issues(issue_title, issue_body):
    # Search for issues with similar titles
    similar_titles = search_issues_by_title_similarity(issue_title)

    # Search for issues with related keywords
    keywords = extract_keywords(issue_body)
    related_issues = search_issues_by_keywords(keywords)

    # Calculate similarity scores
    for issue in (similar_titles + related_issues):
        score = calculate_similarity(issue_title, issue_body, issue)
        if score > 0.7:  # High similarity
            suggest_duplicate(issue)
        elif score > 0.4:  # Related
            suggest_related(issue)
```

**Output:**
```
Similar Issues Found:

🔴 Potential Duplicate:
- #145: "Add JSON export" (closed, v3.7.0)
  Similarity: 85%
  Recommendation: Review #145 implementation for reusable patterns

🟡 Related Issues:
- #132: "Improve output formatting" (open)
  Similarity: 65%
  Recommendation: Consider coordinating implementation
```

## Examples

### Triage New Feature Request

```bash
/gh:triage 160

# Agent analyzes issue content:
# Title: "Add CSV export"
# Body: "Users want to export scan results as CSV for analysis in Excel"

# Sequential-thinking process:
# - Step 1: Identify type → Feature (new functionality)
# - Step 2: Assess impact → High (frequently requested)
# - Step 3: Estimate effort → Medium (new formatter + tests)
# - Step 4: Check docs → Needs ARCHITECTURE.md, SECURITY.md
# - Step 5: Find similar → #145 (JSON export, closed)

# Suggestions:
# Type: feature ✓
# Priority: P1-high (user demand + clear use case)
# Complexity: M (200-400 LOC, new class + tests)
# Docs: ARCHITECTURE.md, SECURITY.md, PRD.md

# Apply? User confirms → labels added automatically
```

### Batch Triage Milestone Issues

```bash
/gh:triage --batch --milestone v3.8.0

# Fetches 15 untriaged issues
# Analyzes each with sequential-thinking
# Groups by confidence level:
# - 12 high confidence (auto-suggest)
# - 3 low confidence (needs review)

# Presents summary with bulk apply option
# User approves → all high-confidence labels applied
# Low-confidence issues marked for manual review
```

### Review Issue Quality

```bash
/gh:triage --review 160 --suggest-improvements

# Validates structure:
# ✓ Title clear
# ✗ Missing user story
# ⚠️ Vague acceptance criteria
# ✗ No required docs listed

# Generates improvement template:
# - User story format
# - Specific acceptance criteria
# - Required documentation
# - Edge case checklist

# User approves → issue updated with improvements
```

### Auto-Apply Triage

```bash
/gh:triage 161 --auto-apply

# Analyzes issue
# High confidence (>90%) → automatically applies labels
# Reports: "Auto-applied: bug, P0-critical, complexity/S"
```

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
   - Parse title for keywords (add, fix, improve, etc.)
   - Extract user story if present
   - Identify technical terms and components
   - Analyze description length and clarity

2. Type Classification:
   Keywords:
   - feature: "add", "new", "implement", "support"
   - bug: "fix", "error", "crash", "fails", "broken"
   - task: "refactor", "update", "improve", "optimize"
   - hotfix: "critical", "security", "urgent", "CVE"

3. Priority Assessment:
   P0 (Critical):
   - Security vulnerabilities
   - Data loss/corruption
   - Complete feature breakage
   - Production incidents

   P1 (High):
   - Major feature requests with clear demand
   - Significant bugs affecting many users
   - Blocking issues for releases

   P2 (Medium):
   - Nice-to-have features
   - Minor bugs with workarounds
   - Performance improvements

   P3 (Low):
   - Polish and refinements
   - Documentation updates
   - Minor enhancements

4. Complexity Estimation:
   XS (<50 LOC): Label changes, typo fixes
   S (50-150 LOC): Small features, simple bug fixes
   M (150-400 LOC): Medium features, refactoring
   L (400-1000 LOC): Large features, architecture changes
   XL (>1000 LOC): Major initiatives, system redesigns

5. Required Documentation:
   - ARCHITECTURE.md: New components, layer changes
   - SECURITY.md: Input validation, external data
   - PRD.md: Feature scope verification
   - TESTING.md: Test strategy changes
   - PERFORMANCE.md: Performance implications
```

### Confidence Scoring

```python
def calculate_confidence(analysis):
    confidence = 0.5  # Base confidence

    # Boost confidence if:
    if has_clear_keywords(issue):
        confidence += 0.2
    if similar_issues_exist(issue):
        confidence += 0.15
    if description_is_detailed(issue):
        confidence += 0.15

    # Reduce confidence if:
    if title_is_vague(issue):
        confidence -= 0.2
    if missing_context(issue):
        confidence -= 0.15
    if conflicting_signals(issue):
        confidence -= 0.25

    return min(1.0, max(0.0, confidence))
```

**Confidence thresholds:**
- **>0.9**: Auto-apply safe (if --auto-apply flag)
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
Recommendation: Request more information from author before triaging
```

**Conflicting Signals:**
```
Warning: Issue #160 has mixed signals
- Title suggests bug fix
- Body describes new feature
- Comments discuss refactoring
Recommendation: Manual triage required, or ask author to clarify intent
```

**Rate Limit:**
```
Warning: GitHub API rate limit low (15 requests remaining)
Action: Batch triage paused. Continue after rate limit resets (45 minutes)
```

## Integration with Workflow

### New Issue Created
```bash
# Webhook or manual trigger
/gh:triage 160

# Review suggestions
# Apply labels
# Add to milestone
# Assign if clear owner
```

### Weekly Triage Session
```bash
# Batch triage all untriaged
/gh:triage --batch --limit 50

# Review low-confidence issues manually
# Apply high-confidence suggestions
# Close obvious duplicates
```

### Issue Quality Gate
```bash
# Before assigning to agent
/gh:triage --review 160 --suggest-improvements

# Ensure issue meets quality standards
# Add missing information
# Then assign: /gh:implement-issue 160
```

## References

- [Issue Templates](.github/ISSUE_TEMPLATE/)
- [GitHub Projects Workflow](../../docs/contributing/GITHUB_PROJECTS.md)
- [Issue Validation Script](../../scripts/github-projects/validate-issue-structure.sh)
- [Sequential-thinking MCP](../mcp/Sequential.md)
