# Attribution & Legal Notice

**Document Type:** Legal & Attribution
**Last Updated:** 2025-10-30
**Status:** Official Project Documentation

---

## Legal Disclaimer

**IMPORTANT:** This is an **unofficial, community-maintained tool**. It is **NOT affiliated with, endorsed by, or sponsored by vscan.dev** or any related organizations.

### Unofficial Status

- This project is an independent, open-source CLI tool
- We are not part of the vscan.dev team or organization
- We do not represent vscan.dev in any official capacity
- This tool is maintained by the community, not by vscan.dev

### API Usage

We use **vscan.dev's publicly accessible API** to provide security analysis functionality:

- The API is accessed without authentication or technical barriers
- We make requests to publicly available HTTP endpoints
- We do not circumvent any security measures or access controls
- We implement respectful usage patterns (see [Respectful Usage](#respectful-usage) below)

### Compliance Commitment

**If vscan.dev requests that we cease using their API, we will comply immediately.**

We respect vscan.dev's rights to:
- Request cessation of API usage at any time
- Modify or restrict API access
- Add authentication or rate limiting
- Change terms of service

In the event of such a request, we will:
1. Cease all API usage immediately
2. Remove or archive the project as requested
3. Cooperate fully with any reasonable requests
4. Update users about the change in status

### No Warranty

This tool is provided "as-is" under the **MIT License** with no warranties of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.

See [LICENSE](../../LICENSE) for complete legal terms.

---

## Attribution to vscan.dev

### Primary Acknowledgment

**All security analysis functionality is powered by [vscan.dev](https://vscan.dev).**

vscan.dev is an excellent VS Code extension security analysis service that provides:
- Comprehensive extension source code analysis
- Dependency vulnerability detection
- Publisher reputation and verification checks
- Network access pattern analysis
- File system permission auditing
- Security scoring and risk level assessment

**We are deeply grateful to vscan.dev for providing their public API, which makes this tool possible.**

### What vscan.dev Provides

This tool would not exist without vscan.dev's infrastructure:

- **Analysis Engine**: All security analysis is performed by vscan.dev
- **Vulnerability Database**: Dependency vulnerability data from vscan.dev
- **Risk Assessment**: Security scores and risk levels calculated by vscan.dev
- **Publisher Verification**: Publisher status validated by vscan.dev
- **API Infrastructure**: Reliable, fast API endpoints provided by vscan.dev

### What This Tool Provides

This tool is a **complementary CLI client** that:
- Auto-detects VS Code extensions on your local machine
- Queries vscan.dev API for each extension's security analysis
- Caches results locally to minimize API load
- Presents results in multiple formats (terminal, HTML, JSON, CSV)
- Integrates into CI/CD pipelines and security workflows

**This tool is a front-end to vscan.dev's analysis capabilities.**

---

## Respectful Usage Practices

We take API usage ethics seriously and have implemented multiple measures to minimize load on vscan.dev's infrastructure:

### 1. Rate Limiting

**Default Delay**: 2.0 seconds between API requests (configurable)

```python
# Default configuration
delay = 2.0  # seconds between requests
```

**Benefits**:
- Prevents API overload
- Respects vscan.dev's server resources
- Configurable up to 5.0s for extra caution
- Automatically applied to all API calls

### 2. Intelligent Caching

**Cache Hit Rate**: 70-90% in typical usage

```python
# Cached results avoid API calls entirely
cache_max_age = 14  # days (default)
```

**Benefits**:
- Typical scan makes 10-30% new API calls (rest from cache)
- Repeated scans are 50x faster (instant from cache)
- Dramatically reduces vscan.dev server load
- Users benefit from faster results

**Implementation**:
- SQLite database with HMAC integrity protection
- Configurable cache expiration (default: 14 days)
- Users can disable caching if desired (`--no-cache`)
- Cache statistics available (`vscan cache stats`)

### 3. Retry Mechanism with Exponential Backoff

**Max Retries**: 3 attempts (default)
**Backoff Strategy**: Exponential with jitter

```python
# Retry delays: 2s → 4s → 8s (with random jitter)
retry_delay = base_delay * (2 ** attempt) + random(0, 1)
```

**Benefits**:
- Graceful handling of temporary failures
- Avoids hammering API during issues
- Jitter prevents thundering herd problem
- Configurable retry behavior

### 4. Thread-Safe Parallel Processing

**Default Workers**: 3 (configurable 1-5)

**Implementation**:
- Isolated API client per worker
- Thread-safe statistics collection
- Main thread handles all database writes
- Respects rate limits across all workers

**Benefits**:
- Faster user experience (4.88x speedup)
- Still respects API rate limits
- No concurrent request storms
- Conservative parallelism (max 5 workers)

### 5. Transparent User-Agent

**Identification**: `VSCodeExtensionScanner/3.5.6 (+https://github.com/jvlivonius/vsc-extension-scanner)`

**Benefits**:
- vscan.dev can identify our tool
- Enables communication if issues arise
- Transparency about API usage source
- Professional API etiquette

### 6. HTTPS-Only Communication

**Security**: All API calls use HTTPS with certificate validation

```python
# No insecure HTTP requests allowed
validate_https_only(url)
```

**Benefits**:
- Protects user data in transit
- Prevents man-in-the-middle attacks
- Respects security best practices

### 7. No Circumvention

We **never attempt to**:
- Bypass rate limiting
- Circumvent authentication (none required)
- Use multiple IP addresses to evade limits
- Cache-poison or manipulate responses
- Reverse-engineer API internals
- Access undocumented endpoints

---

## Performance Impact on vscan.dev

### Typical User Scan

**Scenario**: User with 66 VS Code extensions

**API Load**:
- **First scan**: 66 API requests over ~132 seconds (2s delay)
- **Subsequent scans**: ~10 API requests (85% cache hit rate)
- **Weekly scan**: ~20 API requests (refresh older cache entries)

**Total**: Average user generates ~100-200 API requests per month

### Aggregate Impact Estimate

**Assuming 1,000 active users**:
- Monthly API requests: 100,000-200,000
- Daily API requests: 3,300-6,600
- Hourly API requests: 140-275

**With caching**: 70-90% reduction compared to no-cache scenario

---

## User Privacy & Data

### What This Tool Does NOT Do

- **Does NOT collect** user data or telemetry
- **Does NOT transmit** credentials or secrets to vscan.dev
- **Does NOT share** extension lists with third parties
- **Does NOT track** usage patterns or analytics

### What Data Is Shared with vscan.dev

**Only**: Extension publisher and name (e.g., `ms-python.python`)

**Why**: vscan.dev requires these identifiers to perform security analysis

**Stored Locally**:
- Cache database with security results
- Configuration preferences
- Generated reports

**Never Transmitted**:
- Source code or file contents
- User credentials or API keys
- Personal information
- Installation paths

---

## Open Source & Community

### MIT License

This project is open source under the **MIT License**:
- Free to use, modify, and distribute
- No commercial restrictions
- No warranty or liability
- See [LICENSE](../../LICENSE) for full terms

### Community Contributions

We welcome:
- Bug reports and feature requests
- Code contributions and improvements
- Documentation enhancements
- Security vulnerability reports

See [CONTRIBUTING.md](../contributing/CONTRIBUTING.md) for guidelines.

---

## Changes to This Document

This attribution and legal notice may be updated to:
- Reflect changes in vscan.dev API usage terms
- Incorporate feedback from vscan.dev team
- Clarify legal or ethical aspects
- Update contact information

**Last Updated**: 2025-10-30
**Version**: 1.0

---

## Summary

**We are deeply grateful to vscan.dev** for providing the security analysis infrastructure that powers this tool.

**We are committed to respectful API usage** through rate limiting, caching, and ethical practices.

**We will comply immediately** with any requests from vscan.dev regarding API usage.

**This is an unofficial, community tool** that aims to complement vscan.dev's excellent security analysis service.

---

## Links

- **vscan.dev**: [https://vscan.dev](https://vscan.dev)
- **This Project**: [GitHub Repository](https://github.com/jvlivonius/vsc-extension-scanner)
- **License**: [MIT License](../../LICENSE)
- **API Documentation**: [API_REFERENCE.md](../guides/API_REFERENCE.md)
