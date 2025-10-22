# macOS Testing Plan - Phase 3

**Platform Focus:** macOS only
**Objective:** Thoroughly test vscan on macOS, validate caching system, and refine user experience

---

## Test Environment

**System Info:**
- OS: macOS (Darwin 25.0.0)
- Python: 3.8+
- VS Code Extensions Directory: `~/.vscode/extensions/`

---

## Test Categories

### 1. Caching System Tests 🎯 HIGH PRIORITY

#### Test 1.1: First Scan (No Cache)
**Objective:** Verify fresh scan behavior and cache population

```bash
# Clear cache first
python vscan.py --clear-cache

# Run fresh scan with 5 extensions
python vscan.py --verbose --output test1_fresh.json
```

**Expected Results:**
- All extensions show 🔍 (fresh scan)
- Each scan takes 5-15 seconds
- Cache is populated after scan
- JSON output is valid

**Verification:**
- [ ] All extensions scanned fresh (no ⚡ cached indicators)
- [ ] Cache database created at `~/.vscan/cache.db`
- [ ] Valid JSON output generated
- [ ] Exit code 0 or 1 (success)

---

#### Test 1.2: Second Scan (All Cached)
**Objective:** Verify cache retrieval and performance improvement

```bash
# Run same scan again immediately
python vscan.py --verbose --output test1_cached.json
```

**Expected Results:**
- All extensions show ⚡ (cached)
- Results return instantly (<1s per extension)
- Cache hit rate: 100%
- Identical results to first scan (except timestamps)

**Verification:**
- [ ] All extensions retrieved from cache
- [ ] Scan completes 50x faster (~instant)
- [ ] Cache hit rate: 100%
- [ ] Results match first scan

---

#### Test 1.3: Version Change (Cache Invalidation)
**Objective:** Verify cache invalidation when extension version changes

```bash
# Manually modify an extension's version in package.json
# Then run scan again
python vscan.py --verbose --output test1_version_change.json
```

**Expected Results:**
- Modified extension shows 🔍 (fresh scan, cache miss)
- Other extensions show ⚡ (cached)
- New version's result cached

**Verification:**
- [ ] Version-changed extension rescanned
- [ ] Other extensions still cached
- [ ] New version result stored in cache
- [ ] Old version entry invalidated

---

#### Test 1.4: Cache Expiration
**Objective:** Verify cache respects max-age setting

```bash
# Set very short cache expiration
python vscan.py --cache-max-age 0 --verbose --output test1_expired.json
```

**Expected Results:**
- All cached entries treated as expired
- All extensions rescanned fresh
- New results cached with current timestamp

**Verification:**
- [ ] Cache entries ignored (treated as expired)
- [ ] All extensions rescanned
- [ ] --cache-max-age 0 forces fresh scans

---

### 2. Cache Management Commands 🎯 HIGH PRIORITY

#### Test 2.1: Cache Statistics
**Objective:** Verify --cache-stats displays accurate information

```bash
python vscan.py --cache-stats
```

**Expected Output:**
```
Cache Statistics:
  Location: /Users/username/.vscan/cache.db
  Total entries: 42
  Oldest entry: 2025-10-22 10:30:00 (0 days old)
  Newest entry: 2025-10-22 14:30:00 (0 days old)
  Database size: 256 KB
```

**Verification:**
- [ ] Statistics displayed correctly
- [ ] Entry counts accurate
- [ ] Timestamps correct
- [ ] Exit code 0

---

#### Test 2.2: Clear Cache
**Objective:** Verify --clear-cache removes all entries

```bash
python vscan.py --clear-cache
python vscan.py --cache-stats
```

**Expected Results:**
- Cache cleared successfully message
- cache-stats shows 0 entries after clear

**Verification:**
- [ ] All cache entries removed
- [ ] Database still exists (empty)
- [ ] Next scan repopulates cache
- [ ] Exit code 0

---

#### Test 2.3: Refresh Cache
**Objective:** Verify --refresh-cache forces fresh scans and updates cache

```bash
python vscan.py --refresh-cache --verbose --output test2_refresh.json
```

**Expected Results:**
- All extensions rescanned (ignore cache)
- Show 🔍 indicators (fresh)
- Cache updated with new results
- Respects --delay throttling

**Verification:**
- [ ] Cache ignored during scan
- [ ] All extensions rescanned fresh
- [ ] Cache updated with new timestamps
- [ ] Results stored back to cache

---

#### Test 2.4: No Cache Mode
**Objective:** Verify --no-cache disables caching completely

```bash
python vscan.py --no-cache --verbose --output test2_nocache.json
```

**Expected Results:**
- All extensions scanned fresh
- Results NOT stored in cache
- No cache indicators shown

**Verification:**
- [ ] Caching completely disabled
- [ ] No cache reads or writes
- [ ] Results not persisted
- [ ] No cache statistics shown

---

#### Test 2.5: Custom Cache Directory
**Objective:** Verify --cache-dir uses custom location

```bash
python vscan.py --cache-dir ./test_cache --verbose --output test2_custom.json
```

**Expected Results:**
- Cache database created at `./test_cache/cache.db`
- Normal caching behavior
- Statistics show custom location

**Verification:**
- [ ] Custom directory created
- [ ] cache.db created in custom location
- [ ] Caching works normally
- [ ] Subsequent scans use same custom cache

---

### 3. Extension Discovery on macOS 🎯 MEDIUM PRIORITY

#### Test 3.1: Auto-Detect Default Location
**Objective:** Verify automatic discovery of VS Code extensions

```bash
python vscan.py --verbose
```

**Expected Results:**
- Auto-detects `~/.vscode/extensions/`
- Finds all installed extensions
- Parses package.json correctly

**Verification:**
- [ ] Default directory auto-detected
- [ ] All extensions discovered
- [ ] Correct publisher, name, version extracted
- [ ] Progress shows "Discovered N extensions"

---

#### Test 3.2: Custom Extensions Directory
**Objective:** Test --extensions-dir with custom path

```bash
# Test with absolute path
python vscan.py --extensions-dir ~/.vscode/extensions --verbose

# Test with relative path
python vscan.py --extensions-dir ./test_extensions --verbose
```

**Expected Results:**
- Custom directory used
- Extensions discovered from specified path
- Error if directory doesn't exist

**Verification:**
- [ ] Absolute paths work
- [ ] Relative paths work
- [ ] Handles non-existent paths gracefully
- [ ] Clear error message if invalid

---

#### Test 3.3: Corrupted Extensions
**Objective:** Verify graceful handling of malformed extensions

**Setup:**
```bash
# Create test directory with corrupted extension
mkdir -p ./test_extensions/broken.extension
echo "invalid json" > ./test_extensions/broken.extension/package.json
```

```bash
python vscan.py --extensions-dir ./test_extensions --verbose
```

**Expected Results:**
- Warning logged for corrupted extension
- Scan continues with other extensions
- Exit code 0 (not fatal)

**Verification:**
- [ ] Corrupted extension skipped with warning
- [ ] Other extensions scanned normally
- [ ] No crash or exit
- [ ] Clear warning message

---

### 4. Larger Extension Set Tests 🎯 HIGH PRIORITY

#### Test 4.1: Scan 10-20 Extensions
**Objective:** Verify performance with moderate extension count

```bash
# First scan (no cache)
python vscan.py --clear-cache
time python vscan.py --verbose --output test4_medium.json
```

**Expected Results:**
- All extensions scanned successfully
- Progress indicators update correctly
- Reasonable performance (< 5 minutes)
- Cache statistics show cache population

**Verification:**
- [ ] All extensions scanned
- [ ] Progress indicators accurate
- [ ] Performance acceptable
- [ ] Cache hit rate: 0% (first scan)

**Then run again:**
```bash
time python vscan.py --verbose --output test4_medium_cached.json
```

**Expected Results:**
- 50x faster (~instant)
- Cache hit rate: 100%
- Identical results

**Verification:**
- [ ] Dramatic performance improvement
- [ ] All results from cache
- [ ] Cache hit rate: 100%
- [ ] Results consistent

---

#### Test 4.2: Test with All Installed Extensions
**Objective:** Real-world test with actual VS Code installation

```bash
# Clear cache and scan ALL extensions
python vscan.py --clear-cache
time python vscan.py --verbose --output test4_all_fresh.json

# Scan again with cache
time python vscan.py --verbose --output test4_all_cached.json
```

**Expected Results:**
- First scan: N extensions × (1.5s delay + API time)
- Second scan: Near-instant (cached)
- Cache dramatically improves UX

**Verification:**
- [ ] Handles large extension sets
- [ ] Memory usage < 100MB
- [ ] No crashes or errors
- [ ] Cache provides massive speedup

---

### 5. Error Scenarios 🎯 MEDIUM PRIORITY

#### Test 5.1: Network Errors
**Objective:** Verify graceful handling of network issues

```bash
# Simulate network failure (block vscan.dev in /etc/hosts)
# Add: 0.0.0.0 vscan.dev
python vscan.py --verbose --output test5_network.json
```

**Expected Results:**
- Connection error detected
- Clear error message
- Exit code 2 (failure)
- Partial results if some succeed

**Verification:**
- [ ] Network errors caught
- [ ] Clear error message
- [ ] Doesn't crash
- [ ] Exit code 2

---

#### Test 5.2: Invalid Extension Not Found
**Objective:** Verify handling of extensions not in vscan.dev

```bash
# Create fake extension
mkdir -p ./test_extensions/fake.extension
cat > ./test_extensions/fake.extension/package.json << EOF
{
  "name": "nonexistent-extension",
  "publisher": "fake-publisher",
  "version": "1.0.0"
}
EOF

python vscan.py --extensions-dir ./test_extensions --verbose
```

**Expected Results:**
- Extension marked as "not_found"
- Scan continues with other extensions
- JSON output includes not_found status

**Verification:**
- [ ] Extension marked as not_found
- [ ] Other extensions scanned
- [ ] Exit code 0 (not fatal)
- [ ] Clear status in JSON output

---

### 6. Output Format Tests 🎯 MEDIUM PRIORITY

#### Test 6.1: Output to stdout
**Objective:** Verify JSON output to stdout

```bash
python vscan.py > test6_stdout.json 2> test6_stderr.log
```

**Expected Results:**
- JSON output to stdout (captured in file)
- Progress/logs to stderr (captured separately)
- Valid JSON structure

**Verification:**
- [ ] JSON in stdout only
- [ ] Logs in stderr only
- [ ] No mixing of output
- [ ] Valid JSON syntax

---

#### Test 6.2: Output to File
**Objective:** Verify --output flag

```bash
python vscan.py --output test6_file.json --verbose
```

**Expected Results:**
- JSON written to specified file
- Progress shown to stderr
- File is valid JSON

**Verification:**
- [ ] File created successfully
- [ ] Contains valid JSON
- [ ] Progress still visible
- [ ] File overwrites existing

---

#### Test 6.3: JSON Validity
**Objective:** Verify JSON output structure

```bash
python vscan.py --output test6_validate.json
python3 -m json.tool test6_validate.json > /dev/null
```

**Expected Results:**
- JSON is valid and well-formed
- Matches PRD specification
- All required fields present

**Verification:**
- [ ] Valid JSON syntax
- [ ] Matches schema
- [ ] All fields present
- [ ] Correct data types

---

### 7. CLI Arguments Tests 🎯 LOW PRIORITY

#### Test 7.1: Help Message
```bash
python vscan.py --help
```

**Verification:**
- [ ] Clear and comprehensive
- [ ] All arguments documented
- [ ] Examples included
- [ ] Exit code 0

---

#### Test 7.2: Version Information
```bash
python vscan.py --version
```

**Verification:**
- [ ] Shows version number
- [ ] Exit code 0

---

#### Test 7.3: Invalid Arguments
```bash
# Invalid delay
python vscan.py --delay -1

# Non-existent directory
python vscan.py --extensions-dir /fake/path

# Unknown flag
python vscan.py --unknown-flag
```

**Verification:**
- [ ] Clear error messages
- [ ] Shows usage/help
- [ ] Exit code 2

---

### 8. Performance Benchmarking 🎯 HIGH PRIORITY

#### Test 8.1: Benchmark Without Cache
```bash
python vscan.py --clear-cache
time python vscan.py --no-cache --output bench_nocache.json
```

**Measure:**
- Total execution time
- Time per extension
- Memory usage

**Verification:**
- [ ] < 2 minutes for 50 extensions
- [ ] < 100MB memory usage
- [ ] Linear performance

---

#### Test 8.2: Benchmark With Cache
```bash
# Populate cache first
python vscan.py --output populate.json

# Benchmark cached scan
time python vscan.py --output bench_cache.json
```

**Measure:**
- Total execution time
- Time per extension
- Speedup vs no-cache

**Verification:**
- [ ] ~50x faster than fresh scan
- [ ] Near-instant per extension
- [ ] Cache provides massive benefit

---

#### Test 8.3: Memory Profiling
```bash
# Install memory_profiler if needed
pip3 install memory_profiler

# Profile memory usage
python3 -m memory_profiler vscan.py --output mem_test.json
```

**Verification:**
- [ ] Peak memory < 100MB
- [ ] No memory leaks
- [ ] Efficient caching

---

## Test Execution Order

**Priority 1 - Core Functionality:**
1. Caching system tests (1.1 - 1.4)
2. Cache management commands (2.1 - 2.5)
3. Larger extension set (4.1 - 4.2)

**Priority 2 - Validation:**
4. Extension discovery (3.1 - 3.3)
5. Output format tests (6.1 - 6.3)
6. Performance benchmarking (8.1 - 8.3)

**Priority 3 - Edge Cases:**
7. Error scenarios (5.1 - 5.2)
8. CLI arguments (7.1 - 7.3)

---

## Success Criteria

**Must Pass:**
- ✅ All caching tests (1.1 - 1.4)
- ✅ All cache management commands work (2.1 - 2.5)
- ✅ Handles 20+ extensions efficiently (4.1 - 4.2)
- ✅ Cache provides 50x performance improvement
- ✅ Valid JSON output (6.1 - 6.3)
- ✅ No crashes or data corruption

**Should Pass:**
- ✅ Extension discovery works (3.1 - 3.2)
- ✅ Graceful error handling (5.1 - 5.2)
- ✅ Performance benchmarks acceptable (8.1 - 8.3)

**Nice to Have:**
- ✅ Handles corrupted extensions (3.3)
- ✅ All CLI edge cases (7.1 - 7.3)

---

## Test Results Log

Results will be documented in: [MACOS_TEST_RESULTS.md](MACOS_TEST_RESULTS.md)

---

## Next Steps After Testing

1. Document all test results
2. Fix any bugs discovered
3. Update documentation with findings
4. Create final implementation summary
5. Update PROJECT_STATUS.md
