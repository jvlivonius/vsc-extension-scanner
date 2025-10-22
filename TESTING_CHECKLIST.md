# Testing Checklist for Phase 3

## API Behavior Testing

### ✅ Completed in Phase 1

- [x] Test analyze endpoint with popular extensions
- [x] Test status endpoint with cached results
- [x] Test results endpoint and parse response
- [x] Verify JSON response structure
- [x] Test sequential requests with delays

### ⏳ TODO: Additional API Tests

- [ ] **Test obscure/unpublished extension** to observe actual polling
  - Find a very unpopular extension
  - Observe status "pending" → "completed" transition
  - Measure actual analysis time
  - Document progress field behavior

- [ ] **Test invalid extension name**
  - Submit analysis for non-existent extension
  - Document error response format
  - Verify graceful error handling

- [ ] **Test invalid publisher**
  - Submit with fake publisher name
  - Document response behavior

- [ ] **Test extension with vulnerabilities**
  - Find extension with known vulnerabilities
  - Verify `vulnerabilities.details` structure
  - Document how individual CVEs are reported

- [ ] **Test rate limiting**
  - Submit many rapid requests
  - Document HTTP 429 response format
  - Test retry-after headers
  - Verify backoff strategy

- [ ] **Test concurrent requests**
  - Submit 5-10 simultaneous analyze requests
  - Check if server handles parallel requests
  - Monitor for rate limiting

- [ ] **Test network errors**
  - Simulate connection timeout
  - Simulate DNS failure
  - Verify error messages

- [ ] **Test malformed requests**
  - Missing publisher field
  - Missing name field
  - Invalid JSON
  - Empty strings

## Extension Discovery Testing

### Platform-Specific Tests

- [ ] **macOS**
  - Default path: `~/.vscode/extensions/`
  - Test with Intel and Apple Silicon
  - Test with VS Code Insiders
  - Verify symlinks are handled

- [ ] **Windows**
  - Default path: `%USERPROFILE%\.vscode\extensions\`
  - Test with Windows 10 and 11
  - Test with different user profiles
  - Handle path with spaces

- [ ] **Linux**
  - Default path: `~/.vscode/extensions/`
  - Test on Ubuntu, Fedora, Arch
  - Test with snap/flatpak installations
  - Verify permissions

### Edge Cases

- [ ] **No VS Code installed**
  - Extensions directory doesn't exist
  - Verify clear error message
  - Exit code 2

- [ ] **Empty extensions directory**
  - VS Code installed but no extensions
  - Should complete with 0 extensions scanned
  - Exit code 0

- [ ] **Corrupted extension**
  - Extension directory missing package.json
  - package.json with invalid JSON
  - package.json missing required fields
  - Should warn and continue scanning

- [ ] **Permissions issues**
  - Extensions directory not readable
  - package.json not readable
  - Verify error messages

- [ ] **Large number of extensions**
  - Test with 100+ extensions
  - Verify memory usage < 100MB
  - Verify progress indicators work
  - Test with --delay to ensure total time is reasonable

- [ ] **Custom extensions directory**
  - Use --extensions-dir with custom path
  - Verify relative paths work
  - Verify absolute paths work
  - Handle path that doesn't exist

- [ ] **Special characters in paths**
  - Paths with spaces
  - Paths with Unicode characters
  - Windows paths with backslashes

## package.json Parsing

- [ ] **Standard package.json**
  - Extract publisher from `publisher` field
  - Extract name from `name` field
  - Extract version from `version` field

- [ ] **Malformed package.json**
  - Invalid JSON syntax
  - Missing `name` field
  - Missing `publisher` field
  - Missing `version` field
  - Extra unexpected fields

- [ ] **Edge cases**
  - Very large package.json (>1MB)
  - package.json with comments (invalid JSON)
  - UTF-8 BOM markers
  - Different line endings (CRLF vs LF)

## Output Testing

### JSON Output

- [ ] **Valid JSON structure**
  - Verify all fields present
  - Verify types are correct
  - Verify arrays/objects properly nested

- [ ] **Output to stdout**
  - JSON goes to stdout
  - Logs go to stderr
  - Verify no mixing

- [ ] **Output to file**
  - Use --output flag
  - Verify file is created
  - Verify file is valid JSON
  - Handle existing file (overwrite)
  - Handle path that doesn't exist

- [ ] **Progress indicators**
  - Shown on stderr (not stdout)
  - Update correctly
  - Don't interfere with JSON output

- [ ] **Special characters in output**
  - Extension names with Unicode
  - Extension descriptions with quotes
  - Proper JSON escaping

### Exit Codes

- [ ] Exit code 0: Scan completed, no vulnerabilities
- [ ] Exit code 1: Scan completed, vulnerabilities found
- [ ] Exit code 2: Scan failed due to errors

## Performance Testing

- [ ] **Memory usage**
  - Scan 50 extensions
  - Verify < 100MB RAM usage
  - No memory leaks

- [ ] **Execution time**
  - 50 extensions with 1.5s delay
  - Should complete in < 2 minutes
  - Verify progress is linear

- [ ] **File I/O**
  - Minimize repeated reads
  - Don't load entire extension files
  - Only read package.json

## Error Handling

### Network Errors

- [ ] **Connection timeout**
  - vscan.dev unreachable
  - DNS failure
  - Verify retry logic
  - Verify clear error message

- [ ] **HTTP errors**
  - 404 Not Found
  - 429 Rate Limited
  - 500 Internal Server Error
  - 503 Service Unavailable

### Application Errors

- [ ] **Invalid arguments**
  - Invalid --delay value (negative, non-numeric)
  - Invalid --extensions-dir path
  - Unknown flags
  - Verify help message shown

- [ ] **Interrupted execution**
  - Ctrl+C during scan
  - Graceful shutdown
  - Partial results handling

## Security Testing

- [ ] **Path traversal**
  - --extensions-dir with ../../../etc/passwd
  - Verify path validation
  - Should reject dangerous paths

- [ ] **HTTPS verification**
  - All requests use HTTPS
  - Certificate validation enabled
  - No insecure requests

- [ ] **Sensitive data**
  - No credentials in output
  - No user paths in JSON (privacy)
  - Sanitize error messages

## Compatibility Testing

### Python Versions

- [ ] Python 3.8
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12

### Operating Systems

- [ ] macOS 13 (Ventura)
- [ ] macOS 14 (Sonoma)
- [ ] macOS 15 (Sequoia)
- [ ] Windows 10
- [ ] Windows 11
- [ ] Ubuntu 22.04 LTS
- [ ] Ubuntu 24.04 LTS
- [ ] Fedora (latest)

## User Experience Testing

- [ ] **Help message**
  - python vscan.py --help
  - Clear and concise
  - Examples provided

- [ ] **Version information**
  - python vscan.py --version
  - Shows correct version

- [ ] **Verbose mode**
  - --verbose flag works
  - Shows detailed progress
  - Helps with debugging

- [ ] **Error messages**
  - Clear and actionable
  - Suggest fixes when possible
  - No stack traces in normal mode

- [ ] **Progress indicators**
  - Show current/total extensions
  - Show extension being scanned
  - Show status (✓, ⚠, ✗)
  - Estimate time remaining

## Integration Testing

- [ ] **End-to-end workflow**
  - Fresh VS Code installation
  - Install 5-10 extensions
  - Run scanner
  - Verify results match vscan.dev website

- [ ] **Real-world scenarios**
  - Developer machine with 30+ extensions
  - CI/CD pipeline integration
  - Scheduled scanning via cron

## Documentation Testing

- [ ] README examples work
- [ ] CLAUDE.md instructions accurate
- [ ] API_RESEARCH.md findings current
- [ ] Code comments helpful
- [ ] Error messages reference docs

## Accessibility

- [ ] Works in terminal with screen readers
- [ ] Color output is optional
- [ ] Clear text-only progress indicators
- [ ] JSON output is machine-readable

---

## Test Execution Strategy

### Phase 2 (During Implementation)
- Unit tests for each function
- Test driven development where appropriate
- Manual testing of basic workflows

### Phase 3 (Testing & Refinement)
- Systematic execution of this checklist
- Automated testing where possible
- Cross-platform testing
- Performance benchmarking
- User acceptance testing

### Tools
- `pytest` for unit tests
- Manual testing for integration tests
- `time` and `memory_profiler` for performance
- `tox` for multi-Python version testing
- Virtual machines for cross-platform testing
