# VS Code Extension Scanner - Error Codes

This document provides a reference for error codes that may appear in exception messages.
Error codes help identify the source of errors for faster debugging and troubleshooting.

## Error Code Format

Error codes follow the format `[Exxx]` where:
- `E` = Error
- `xxx` = Three-digit code identifying the module and specific error

## Error Code Ranges

- **E100-E199**: API Client (`vscan_api.py`) - Network and vscan.dev API errors
- **E200-E299**: Cache Manager (`cache_manager.py`) - Database and caching errors
- **E300-E399**: Extension Discovery (`extension_discovery.py`) - File system and discovery errors
- **E400-E499**: HTML Report Generator (`html_report_generator.py`) - Report generation errors
- **E001-E099**: Scanner (`scanner.py`) - Core scanning logic errors

## Implemented Error Codes

### API Client Errors (E100-E199)

#### E100: Response Exceeds Maximum Size
**Error:** `[E100] Response exceeds maximum size (10485760 bytes)`

**Cause:** The API response from vscan.dev exceeded the 10MB safety limit.

**Solution:**
- This is a safety check to prevent memory exhaustion
- The extension data is unusually large
- Try scanning the extension individually with `--include-ids`
- Report the issue if this occurs repeatedly

#### E101: Rate Limit Exceeded
**Error:** `[E101] Rate limit exceeded. Please try again later.`

**Cause:** Too many requests sent to vscan.dev API (HTTP 429 status).

**Solution:**
- Wait a few minutes before retrying
- Increase `--delay` parameter (default: 1.5 seconds)
- Use `--max-retries 0` to fail fast and retry manually later
- Check vscan.dev status if problem persists

### Cache Manager Errors (E200-E299)

#### E200: Invalid Cache Directory Path
**Error:** `[E200] Invalid cache directory path: /path/to/cache`

**Cause:** The specified cache directory path is restricted or in a protected system location.

**Solution:**
- Don't use system directories like `/etc`, `/sys`, `C:\Windows`
- Use a user-accessible directory like `~/.vscan/` (default)
- Verify the path exists and you have write permissions
- Use `--cache-dir /custom/path` to specify an alternative location

### Extension Discovery Errors (E300-E399)

#### E300: Invalid or Restricted Path
**Error:** `[E300] Invalid or restricted path: /path/to/extensions`

**Cause:** The custom extensions directory path is restricted (system directory) or in a temp directory.

**Solution:**
- Don't use system directories like `/etc`, `/sys`, `C:\Windows`, `C:\Program Files`
- Don't use temporary directories
- Use the default VS Code extensions directory (auto-detected)
- Verify the path with: `--extensions-dir /path/to/vscode/extensions`

#### E301: Custom Extensions Directory Not Found
**Error:** `[E301] Custom extensions directory not found: /path/to/extensions`

**Cause:** The specified custom extensions directory does not exist.

**Solution:**
- Verify the path is correct
- Check for typos in the path
- Ensure VS Code is installed
- Omit `--extensions-dir` to use auto-detection
- Valid paths:
  - macOS: `~/.vscode/extensions/`
  - Windows: `%USERPROFILE%\.vscode\extensions\`
  - Linux: `~/.vscode/extensions/`

## Getting Help

If you encounter an error not listed here:

1. **Check the full error message** - It often contains helpful context
2. **Search GitHub Issues** - https://github.com/anthropics/claude-code/issues
3. **Report the issue** - Include:
   - Full error message with error code
   - Command you ran
   - Operating system
   - VS Code version

## Adding Error Codes

When adding new error codes:

1. Choose the appropriate range (E100-E199, E200-E299, etc.)
2. Use the next available number in sequence
3. Add error code to exception: `raise ValueError("[E200] Error message")`
4. Document it in this file with:
   - Error code and title
   - Full error message
   - Cause explanation
   - Solution steps

## Error Code Source of Truth

**Implementation:** All error codes are defined in `vscode_scanner/constants.py` as the single source of truth.

**See Also:** → [STATUS.md](../project/STATUS.md) for current error code statistics and coverage.
