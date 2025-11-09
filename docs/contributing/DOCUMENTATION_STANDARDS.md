# Documentation Standards

**Purpose:** Standards and best practices for creating and maintaining project documentation
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** Contributors, Documentation Maintainers

---

## Core Principles

### 1. HOW TO Over History

**Documents must focus on execution and implementation, not historical context.**

**✅ DO:**
- Lead with "HOW TO" in purpose statements
- Structure with actionable sections: "HOW TO measure", "HOW TO test", "HOW TO optimize"
- Include concrete commands, code examples, and workflows
- Reference theory/background in dedicated sections (§ 5+)

**❌ DON'T:**
- Mix historical results with implementation guidance
- Lead with explanations of "why" before "how"
- Include version-specific narratives in timeless guides

**Example:**

```markdown
# Performance Guide

**Purpose:** How to benchmark, optimize, profile, and troubleshoot performance

## § 1: Performance Testing

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/test_performance.py -v
```

### Writing Performance Tests

```python
def test_cache_provides_50x_speedup():
    """Cached results at least 50x faster than fresh scans."""
    # Test implementation...
```
```

**Anti-Pattern:**

```markdown
# Performance Documentation

**Document Type:** Living Benchmark Reference
**Last Benchmarked:** 2025-10-26

## Historical Results

Cache provides 28.6x speedup (measured 2025-10-26)...
```

---

### 2. Single Responsibility

**Each document has ONE clear purpose.**

**✅ DO:**
- Create focused documents with clear scope
- Use canonical references to avoid duplication
- Split complex topics into multiple specialized guides

**❌ DON'T:**
- Combine multiple unrelated topics in one document
- Duplicate content across multiple files
- Create documents that serve multiple audiences

**Example:**

```
✅ GOOD Structure:
- TESTING.md: Overview + quick start (11 lines on coverage)
- testing/TESTING_COVERAGE.md: HOW TO measure coverage (256 lines)
- STATUS.md: Current metrics (dynamic reference)

❌ BAD Structure:
- COVERAGE_STRATEGY.md: 676 lines mixing goals, strategy, metrics, roadmap
- TESTING_COVERAGE.md: 283 lines duplicating 60% of COVERAGE_STRATEGY.md
```

**Test:** If a document covers >3 unrelated topics, it should be split.

---

### 3. Timeless Content

**Documentation should not contain hardcoded versions, dates, or metrics.**

**✅ DO:**
- Use "Applies To: All versions" for timeless content
- Reference STATUS.md for current metrics
- Use commands to discover dynamic values
- Link to archive for historical context

**❌ DON'T:**
- Hardcode version numbers ("v3.5.3")
- Include specific dates in timeless content
- Hardcode test counts, coverage percentages, or metrics
- Reference completed phases without context ("Phase 2.6")

**Examples:**

```markdown
✅ GOOD:
**Current Metrics:** See [STATUS.md](../../project/STATUS.md) for current coverage by module
**Test Count:** Run `pytest --collect-only -q tests/` to see current count
**Applies To:** All versions

❌ BAD:
**Current Coverage:** 52.37% (as of v3.5.3)
**Test Count:** 24 tests
**Last Updated:** 2025-10-30 (v3.5.3 Testing Excellence - Phase 4)
**Applies To:** All 3.x versions
```

---

### 4. Dynamic References

**Link to current data instead of duplicating it.**

**✅ DO:**
- Reference STATUS.md for metrics, versions, features
- Use commands that discover current state
- Link to canonical sources for shared concepts
- Update references when source locations change

**❌ DON'T:**
- Copy metrics from STATUS.md into guides
- Hardcode values that change over time
- Duplicate definitions across multiple files

**Examples:**

```markdown
✅ GOOD Dynamic References:
- Coverage: "See [STATUS.md](../../project/STATUS.md) for current coverage"
- Test count: "Run: `pytest --collect-only -q tests/`"
- Exit codes: "See [ERROR_CODES.md](ERROR_CODES.md) for complete reference"

❌ BAD Hardcoded Values:
- "Current coverage: 89.23%"
- "Test suite contains 1,142 tests"
- "Exit codes: 0=success, 1=vulnerabilities, 2=error" (duplicated from ERROR_CODES.md)
```

---

### 5. Canonical References

**Single source of truth for each concept. Reference, don't duplicate.**

**✅ DO:**
- Identify the authoritative source for each concept
- Reference canonical source from other documents
- Keep detailed information in one place only
- Update only the canonical source when information changes

**❌ DON'T:**
- Duplicate detailed information across multiple files
- Maintain the same content in multiple locations
- Create competing sources of truth

**Pattern:**

```markdown
# Canonical Source (SECURITY.md)
## Path Validation

**Function:** `validate_path(path, path_type)`

**Validation Rules:**
1. No path traversal: `../`, `..%2f`, etc.
2. No system directories: `/etc/`, `/sys/`, `C:\Windows\`
3. Must be absolute path
...

# Referencing Document (TESTING_SECURITY.md)
## Path Validation Tests

**Requirements:** See [SECURITY.md - Path Validation](../SECURITY.md#path-validation) for complete validation rules, protected paths, and restricted directories

**Test Coverage:** Tests cover all validation rules from [SECURITY.md](../SECURITY.md#path-validation) including...
```

**Canonical Sources in This Project:**

| Concept | Canonical Source | References From |
|---------|------------------|-----------------|
| Path validation rules | SECURITY.md | TESTING_SECURITY.md |
| Exit codes | ERROR_CODES.md | ERROR_HANDLING.md, TESTING.md |
| Coverage goals | TESTING.md | TESTING_COVERAGE.md, STATUS.md |
| Current metrics | STATUS.md | All guides (dynamic reference) |
| API endpoints | API_REFERENCE.md | ARCHITECTURE.md, SECURITY.md |

---

### 6. Standard Headers

**All guides must use consistent header format.**

**Required Header Format:**

```markdown
# Guide Title

**Purpose:** One-line statement of what this guide teaches you HOW TO do
**Document Type:** Timeless Reference | Living Document | Historical Record
**Applies To:** All versions | Specific version range
**Target Audience:** Who should read this (Developers, QA, Architects, etc.)

---

## § 1: First Major Section
```

**Examples:**

```markdown
✅ GOOD:
# Performance Guide

**Purpose:** How to benchmark, optimize, profile, and troubleshoot performance
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** Developers, Performance Engineers

✅ GOOD:
# v3.5.3 Roadmap

**Purpose:** Testing Excellence milestone plan and implementation tracking
**Document Type:** Historical Record
**Applies To:** v3.5.3 release
**Target Audience:** Project maintainers

❌ BAD (missing purpose, outdated version):
# Testing Coverage Strategy

**Document Type:** Timeless Reference
**Applies To:** All 3.x versions
**Target Audience:** Developers, QA Engineers
```

**Section Markers:**

- Use `§ 1`, `§ 2`, etc. for major sections (easy reference: "See TESTING.md § 3")
- Use `##` for major sections, `###` for subsections, `####` for details
- Group related subsections under clear major sections

---

### 7. Token Efficiency

**Focus and compression reduce maintenance burden.**

**✅ DO:**
- Remove verbose explanations in favor of concise examples
- Eliminate duplication through canonical references
- Consolidate related content into focused documents
- Archive or delete outdated content

**❌ DON'T:**
- Maintain multiple documents covering the same topic
- Include extensive background when HOW TO is sufficient
- Keep outdated roadmaps or plans in active documentation

**Results from 2025-11-09 Session:**

```
Coverage Documentation Consolidation:
- Before: 3 docs (970 lines, 60% duplication)
- After: 2 docs (267 lines, 0% duplication)
- Result: 73% reduction, improved clarity

Overall Documentation Improvements:
- Removed: 703+ lines (duplication, outdated content)
- Clarified: 8 broken references fixed
- Streamlined: All guides refocused on HOW TO
```

---

### 8. No Unclear Context

**Remove phase references and version-specific context without explanation.**

**✅ DO:**
- Use clear milestone descriptions
- Reference completed features in STATUS.md or CHANGELOG.md
- Keep phase-based plans in archive after completion

**❌ DON'T:**
- Reference "Phase 2.6" or "Phase 4" without context
- Use internal development terminology in user-facing docs
- Keep completed roadmaps in active documentation

**Examples:**

```markdown
✅ GOOD:
**Last Updated:** 2025-11-09
**Status:** Complete ✅

❌ BAD:
**Last Updated:** 2025-10-30 (v3.5.3 Testing Excellence - Phase 4)

✅ GOOD:
# With automated tools

**Automated Security Tools:**
- Bandit (static analysis)
- safety/pip-audit (dependency scanning)

❌ BAD:
# With automated tools (Phase 1)

**Phase 1 Security Tools (Automated):**
```

---

### 9. Systematic Reference Verification

**All cross-references must point to existing files.**

**✅ DO:**
- Verify all markdown links after making changes
- Use correct relative paths (include directory prefixes)
- Update references when moving or renaming files
- Run automated link checks before committing

**❌ DON'T:**
- Assume file paths without verification
- Leave broken links after refactoring
- Reference archived files from active documentation

**Common Reference Errors:**

```markdown
❌ BAD: Missing directory prefix
[TESTING_SECURITY.md](TESTING_SECURITY.md)

✅ GOOD: Correct path
[TESTING_SECURITY.md](testing/TESTING_SECURITY.md)

❌ BAD: Incorrect archive filename
[security-analysis.md](../archive/reviews/security-analysis.md)

✅ GOOD: Correct versioned filename
[v2.1-security-analysis.md](../archive/reviews/v2.1-security-analysis.md)

❌ BAD: Reference to deleted file
[v3.5.3-roadmap.md](../project/v3.5.3-roadmap.md)

✅ GOOD: Reference current status
[STATUS.md](../project/STATUS.md)
```

**Verification Process:**

```bash
# Find all markdown links
grep -r '\[.*\](.*\.md[^)]*)' docs/guides/ --include="*.md"

# Check if referenced files exist
for file in $(find docs/guides -name "*.md"); do
    grep -o '\](.*\.md[^)]*)' "$file" | sed 's/](\(.*\))/\1/' | while read link; do
        # Resolve relative path and check existence
        dir=$(dirname "$file")
        target="$dir/$link"
        if [ ! -f "$target" ]; then
            echo "Broken link in $file: $link"
        fi
    done
done
```

---

### 10. No Stub Files

**Only create documentation files when ready to populate with ≥50% content.**

**✅ DO:**
- Plan documentation structure in existing files (comments, TODO sections)
- Create files only when content is ready
- Provide working examples and commands from the start
- Archive or delete incomplete stub files

**❌ DON'T:**
- Create empty or minimal placeholder files
- Reference non-existent content (e.g., "See lines 1900-2518" in 641-line file)
- Commit files with only headers and TODOs

**Stub Prevention:**

```markdown
✅ GOOD: Plan in existing file
# Testing Guide

## Coverage Testing

See [TESTING_COVERAGE.md](testing/TESTING_COVERAGE.md) for complete coverage guide.

<!-- TODO: Add section on mutation testing when implemented -->

❌ BAD: Create stub file
# File: TESTING_MUTATION.md

## Mutation Testing

TODO: Write content about mutation testing
See main TESTING.md lines 1900-2518 for details. (File only has 641 lines!)
```

**Cleanup Process:**

```bash
# Find potential stub files (<100 lines with high TODO count)
find docs -name "*.md" -exec sh -c '
    lines=$(wc -l < "$1")
    todos=$(grep -c "TODO" "$1" 2>/dev/null || echo 0)
    if [ "$lines" -lt 100 ] && [ "$todos" -gt 5 ]; then
        echo "Potential stub: $1 ($lines lines, $todos TODOs)"
    fi
' sh {} \;
```

---

## Documentation Checklist

**Before creating or updating documentation, verify:**

### Structure ✅

- [ ] Follows standard header pattern (Purpose, Document Type, Applies To, Target Audience)
- [ ] Uses section markers (§ 1, § 2, etc.) for major sections
- [ ] Includes horizontal rule (`---`) separating header from content
- [ ] Has clear table of contents for documents >200 lines

### Content ✅

- [ ] Focused on HOW TO (actionable, implementation-focused)
- [ ] Single clear purpose (not mixing multiple unrelated topics)
- [ ] No hardcoded versions, dates, or metrics (uses dynamic references)
- [ ] No duplication (uses canonical references instead)
- [ ] No unclear phase references or internal terminology

### References ✅

- [ ] All markdown links verified (point to existing files)
- [ ] Relative paths include directory prefixes where needed
- [ ] References to STATUS.md for current metrics
- [ ] References to canonical sources (not duplicated content)
- [ ] Archive references use correct versioned filenames

### Quality ✅

- [ ] File has ≥50% meaningful content (not a stub)
- [ ] Includes concrete examples, commands, or code snippets
- [ ] Token efficient (focused, compressed, no verbosity)
- [ ] Professional appearance (consistent formatting, clear structure)
- [ ] Follows existing project conventions and patterns

### Maintenance ✅

- [ ] Footer includes version, last updated date, status
- [ ] Added to docs/README.md navigation (if new guide)
- [ ] Added to CLAUDE.md quick reference (if core guide)
- [ ] Cross-references updated in related documents

---

## Common Patterns

### Creating a New Guide

**1. Verify Need:**
- Does similar documentation exist?
- Can content fit in existing guide?
- Is this a canonical source or reference?

**2. Plan Structure:**
- Define single clear purpose
- Outline HOW TO sections (§ 1, § 2, etc.)
- Identify canonical sources to reference
- Plan examples and commands

**3. Create Header:**
```markdown
# Guide Title

**Purpose:** How to [specific actionable goal]
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** [Primary audience]

---
```

**4. Write Content:**
- Lead with HOW TO sections
- Include concrete examples
- Reference canonical sources
- Use dynamic references for metrics

**5. Add Navigation:**
- Update docs/README.md
- Update CLAUDE.md (if core guide)
- Add cross-references in related docs

### Archiving a Document

**When to Archive:**
- Document contains version-specific plans (roadmaps, milestones)
- Content is historical record (completed features, old benchmarks)
- Replaced by new focused documentation
- Outdated but has historical value

**Archive Process:**

```bash
# 1. Move to appropriate archive directory with version prefix
git mv docs/guides/OLD_DOC.md docs/archive/plans/v3.5.3-old-doc.md

# 2. Update references in active documentation
grep -r "OLD_DOC.md" docs/guides/ --include="*.md"
# Replace with archive path or remove if no longer needed

# 3. Add note in STATUS.md or CHANGELOG.md if significant
# 4. Commit with clear message
git commit -m "docs: Archive v3.5.3-old-doc.md (completed milestone)"
```

### Extracting from Archive

**When to Extract:**
- Feature is actively used and needs user guidance
- Implementation is stable (no major changes expected)
- Archive document was comprehensive specification
- Users need HOW TO guidance, not just historical context

**Extraction Process:**

1. **Verify Archive Content:** Read archive document fully
2. **Identify Relevant Sections:** Extract stable implementation details
3. **Transform to HOW TO:** Rewrite as actionable guide
4. **Remove Version Context:** Make timeless (remove "v2.2" references)
5. **Add Standard Headers:** Apply header format
6. **Update Navigation:** Add to docs/README.md and CLAUDE.md

**Example:** HTML_REPORTS.md extracted from archive/plans/v2.2-html-reports-spec.md
- Removed: v2.2 planning context, implementation timeline
- Kept: Report structure, self-contained design, usage examples
- Added: HOW TO sections, standard headers, timeless content

---

## Validation Commands

**Before committing documentation changes:**

```bash
# 1. Find broken markdown links
grep -r '\[.*\](.*\.md[^)]*)' docs/guides/ --include="*.md" | \
    grep -v "http" | \
    while IFS=: read file link; do
        # Extract link path and verify existence
        # (Implementation depends on your link checker)
    done

# 2. Check for hardcoded versions
grep -r "v[0-9]\+\.[0-9]\+\.[0-9]\+" docs/guides/ --include="*.md" | \
    grep -v "Applies To\|Document Type\|archive"

# 3. Find potential stub files
find docs/guides -name "*.md" -exec sh -c '
    lines=$(wc -l < "$1")
    if [ "$lines" -lt 100 ]; then
        todos=$(grep -c "TODO" "$1" 2>/dev/null || echo 0)
        echo "$1: $lines lines, $todos TODOs"
    fi
' sh {} \;

# 4. Verify standard headers
for file in docs/guides/*.md; do
    if ! grep -q "^\*\*Purpose:\*\*" "$file"; then
        echo "Missing Purpose header: $file"
    fi
done

# 5. Check for duplication (manual review)
# Look for similar content across multiple files
```

---

## Examples

### ✅ GOOD: Focused HOW TO Guide

```markdown
# Performance Guide

**Purpose:** How to benchmark, optimize, profile, and troubleshoot performance
**Document Type:** Timeless Reference
**Applies To:** All versions
**Target Audience:** Developers, Performance Engineers

---

## § 1: Performance Testing

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/test_performance.py -v
```

### Writing Performance Tests

**Cache performance test pattern:**
```python
def test_cache_provides_50x_speedup():
    """Cached results at least 50x faster than fresh scans."""
    import time

    # First scan (fresh, no cache)
    start = time.time()
    scan_extension("ms-python.python")
    fresh_duration = time.time() - start

    # Second scan (cached)
    start = time.time()
    scan_extension("ms-python.python")
    cached_duration = time.time() - start

    speedup = fresh_duration / cached_duration
    assert speedup >= 50, f"Cache speedup {speedup}x below 50x threshold"
```

**Current Metrics:** See [STATUS.md](../project/STATUS.md) for latest benchmark results

---

**Document Version:** 2.0.0 (Refocused as actionable guide)
**Last Updated:** 2025-11-09
**Status:** Complete ✅
```

### ❌ BAD: Mixed Historical/Guidance

```markdown
# Performance Documentation

**Document Type:** Living Benchmark Reference
**Last Benchmarked:** 2025-10-26 (parallel processing), 2025-10-22 (caching)
**Platform:** macOS (Darwin 25.0.0), Python 3.11

## Cache Performance Results

### Benchmark Results (2025-10-22)

| Scenario | Duration | Speedup |
|----------|----------|---------|
| Fresh scan | 14.3s | 1.0x |
| Cached scan | 0.5s | 28.6x |

**Platform:** macOS, Python 3.11, SSD storage

## Historical Comparison

- v3.4.0: 15.2x speedup
- v3.5.0: 22.1x speedup
- v3.5.1: 28.6x speedup

## How to Run Tests

Run the test suite...
```

---

## References

- **[docs/README.md](../README.md)** - Documentation index and navigation
- **[CHANGELOG.md](../../CHANGELOG.md)** - Historical documentation changes
- **[STATUS.md](../project/STATUS.md)** - Current project status and metrics

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-09
**Status:** Complete ✅
