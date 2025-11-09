# Branch Protection Configuration

**Purpose:** GitHub branch protection rules configuration and management
**Document Type:** Reference Guide
**Last Updated:** 2025-10-31
**Version:** 1.1.0

---

## Overview

Branch protection rules enforce code quality standards and workflow requirements on the `main` branch. These rules ensure:

- ✅ All changes reviewed before merge
- ✅ All tests pass before merge
- ✅ Security checks complete
- ✅ No direct pushes to production code
- ✅ Consistent merge history

**Target Branch:** `main`

**Repository Type:** Solo Maintainer (Owner bypass enabled)

---

## Solo Maintainer Configuration

This repository uses a **solo maintainer configuration** optimized for single-owner workflows while maintaining code quality standards:

- ✅ **Owner Bypass Enabled** (`enforce_admins: false`) - Repository owner can merge PRs without approval for emergency situations
- ✅ **Contributor Enforcement** - Future contributors must pass all CI checks + receive owner approval
- ✅ **Policy-Based Workflow** - Owner should follow same PR process as contributors except in genuine emergencies

**Why This Configuration?**
- **GitHub Free Tier Limitation:** Cannot selectively enforce rules on admins while allowing emergency bypass
- **Solo Maintainer Reality:** Single maintainer may need to merge critical hotfixes without external approval
- **Future-Proof:** When contributors join, they will be fully blocked until owner approves

**Owner Workflow Policy:**
- **Standard Process:** Create PR → Wait for CI → Self-review → Merge
- **Emergency Bypass:** Use `gh pr merge --admin` only for critical security fixes or production incidents
- **Documentation:** Document bypass reason in commit message and create follow-up validation issue

---

## Quick Setup

### Option 1: GitHub Web Interface (Recommended for first-time setup)

1. Navigate to repository on GitHub
2. Go to **Settings** → **Branches**
3. Click **Add branch protection rule**
4. Follow configuration below

### Option 2: GitHub CLI (For automation)

```bash
# Ensure gh CLI is installed and authenticated
gh auth status

# Apply protection rules (run from repository root)
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --input .github/branch-protection-config.json
```

---

## Configuration Details

### 1. Branch Name Pattern

**Setting:** Branch name pattern
**Value:** `main`

This applies the rules only to the `main` branch.

---

### 2. Require Pull Request Reviews

**Purpose:** Ensure code is reviewed before merging

**Settings:**
- ✅ **Require a pull request before merging**
- ✅ **Require approvals:** `1`
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ⬜ **Require review from Code Owners** (optional, if CODEOWNERS file added)
- ⬜ **Restrict who can dismiss pull request reviews** (not needed for current team size)
- ⬜ **Allow specified actors to bypass required pull requests** (no bypasses allowed)
- ✅ **Require approval of the most recent reviewable push**

**Rationale:**
- Single approval provides balance between safety and velocity
- Stale reviews dismissed to ensure reviewers see final code
- No bypasses ensure everyone follows same process

**Web Interface Steps:**
1. Check **"Require a pull request before merging"**
2. Set **"Required number of approvals before merging"** to `1`
3. Check **"Dismiss stale pull request approvals when new commits are pushed"**
4. Check **"Require approval of the most recent reviewable push"**

---

### 3. Require Status Checks

**Purpose:** Ensure automated tests and security checks pass

**Settings:**
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- **Required status checks:**
  - `Security Analysis` (Bandit, Safety, pip-audit security scanning)
  - `Architecture Validation` (layer compliance, 0 violations required)
  - `Tests & Coverage Analysis` (all tests must pass, minimum 52% coverage enforced, 70% target)
  - `Semgrep Scan` (custom security rules enforcement)

**Rationale:**
- Prevents merging broken code
- Ensures security standards maintained
- Enforces test coverage requirements
- Catches security issues early

**Web Interface Steps:**
1. Check **"Require status checks to pass before merging"**
2. Check **"Require branches to be up to date before merging"**
3. Search and add each required status check (use exact names):
   - `Security Analysis`
   - `Architecture Validation`
   - `Tests & Coverage Analysis`
   - `Semgrep Scan`

**Note:** Status check names are automatically derived from GitHub Actions job names. GitHub simplifies them by removing the workflow name prefix in most cases. These will appear as search suggestions after the first PR runs.

#### Security Scanner Behavior

**⚠️ IMPORTANT: Non-Blocking Security Checks**

The `Security Analysis` job uses `continue-on-error: true` for individual security scanners, making them **informational rather than strictly blocking**:

**Rationale:**
- Security tools (Bandit, Safety, pip-audit) can generate false positives
- Allows merging PRs with warnings after manual review
- Prevents development workflow disruption from low-severity findings
- Security reports are retained as artifacts for offline review

**Security Policy:**
- ⚠️ **Manual Review Required:** All security warnings must be reviewed before merge
- 🔒 **Critical Findings:** Must be fixed immediately (owner discretion)
- 📊 **Reports Available:** Security artifacts retained 90 days in workflow runs
- ✅ **Job Still Required:** Job must complete successfully (even if scanners warn)

**What This Means:**
- ✅ PRs **can** merge with security warnings (not errors)
- ✅ Security tools run and report findings
- ✅ Manual review process enforces security standards
- ❌ Automatic blocking only on job failure (infrastructure/setup issues)

**For Contributors:**
1. Review security scan output in CI logs
2. Address critical vulnerabilities before requesting review
3. Document why warnings are acceptable if present
4. Expect maintainer questions about security findings

---

### 4. Require Conversation Resolution

**Setting:**
- ✅ **Require conversation resolution before merging**

**Rationale:**
- Ensures all review comments addressed
- Prevents accidental merge of unresolved issues

**Web Interface Steps:**
1. Check **"Require conversation resolution before merging"**

---

### 5. Require Signed Commits (Optional)

**Setting:**
- ⬜ **Require signed commits** (optional, recommended for higher security)

**Rationale:**
- Adds cryptographic verification of commit authorship
- Prevents commit impersonation
- Recommended for security-sensitive projects

**Note:** Requires all contributors to set up GPG keys. May add friction for new contributors.

**Web Interface Steps:**
1. Check **"Require signed commits"** if desired

---

### 6. Require Linear History (Optional)

**Setting:**
- ⬜ **Require linear history** (optional, depends on merge strategy preference)

**Rationale:**
- Forces squash or rebase merges (no merge commits)
- Creates cleaner git history
- May lose some commit context

**Recommendation:** Leave unchecked to allow merge commits for preserving context (especially for hotfixes).

**Web Interface Steps:**
1. Leave unchecked for flexible merge strategies

---

### 7. Require Merge Queue (Optional)

**Setting:**
- ⬜ **Require merge queue** (not needed for current team size)

**Rationale:**
- Manages concurrent PR merges automatically
- Useful for high-traffic repositories
- Adds complexity for small teams

**Recommendation:** Skip for now. Enable when team grows or PR volume increases significantly.

---

### 8. Require Deployments to Succeed (Not Applicable)

**Setting:**
- ⬜ **Require deployments to succeed before merging**

**Rationale:**
- Not applicable (package distribution, not continuous deployment)
- No automated deployment to verify

**Web Interface Steps:**
1. Leave unchecked

---

### 9. Lock Branch

**Setting:**
- ⬜ **Lock branch** (only for emergencies)

**Rationale:**
- Makes branch read-only
- Prevents all commits, even via PR
- Use only during critical incidents

**Recommendation:** Leave unchecked under normal circumstances.

---

### 10. Administrator Enforcement (Solo Maintainer Configuration)

**Setting:**
- ⬜ **Do not allow bypassing the above settings** - UNCHECKED for solo maintainer

**Rationale (Solo Maintainer):**
- **Owner Bypass Capability:** Allows repository owner to merge critical hotfixes without external approval
- **Contributor Enforcement:** Future contributors are fully blocked until all checks pass + owner approves
- **GitHub Free Tier:** Cannot selectively enforce rules while allowing emergency bypass
- **Policy-Based:** Owner should follow same process voluntarily except in genuine emergencies

**Web Interface Steps:**
1. **Leave UNCHECKED:** "Do not allow bypassing the above settings"
2. This corresponds to `"enforce_admins": false` in JSON configuration

**Configuration Trade-offs:**
- ✅ **Owner can bypass:** Emergency capability for critical fixes (using `--admin` flag)
- ✅ **Contributors blocked:** All rules enforced on non-admin users (checks + approval required)
- ⚠️ **Policy-based for owner:** GitHub won't prevent owner merges (requires discipline)
- ✅ **Future-proof:** When team grows, easy to change to `enforce_admins: true`

**When to Use `--admin` Flag:**
- Critical security vulnerability requiring immediate fix
- Production outage requiring hotfix
- CI/CD system failure preventing normal merge
- Always document bypass reason in commit message

---

### 11. Restrict Pushes

**Setting:**
- ✅ **Restrict who can push to matching branches**
- **Allowed actors:** None (PRs only)

**Rationale:**
- Prevents direct pushes to main
- Forces all changes through PR process
- Ensures review and CI for every change

**Web Interface Steps:**
1. Check **"Restrict who can push to matching branches"**
2. Leave "Allowed actors" empty (or add CI/CD service accounts if needed)

---

### 12. Allow Force Pushes

**Setting:**
- ❌ **Allow force pushes: Disabled**

**Rationale:**
- Prevents rewriting main branch history
- Protects against accidental data loss
- Maintains stable production history

**Web Interface Steps:**
1. Ensure **"Allow force pushes"** is UNCHECKED

---

### 13. Allow Deletions

**Setting:**
- ❌ **Allow deletions: Disabled**

**Rationale:**
- Prevents accidental branch deletion
- Protects production code

**Web Interface Steps:**
1. Ensure **"Allow deletions"** is UNCHECKED

---

## GitHub CLI Configuration

### Complete Configuration File

Create `.github/branch-protection-config.json`:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Security Checks / Security Analysis",
      "Tests / Architecture Validation",
      "Tests & Coverage Analysis",
      "Semgrep Security Scan / Semgrep Scan"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
```

**Key Configuration Points:**
- `"enforce_admins": false` - Allows owner bypass for emergency situations
- `"required_approving_review_count": 1` - Enforced for contributors, not owner
- `"require_last_push_approval": true` - Better security (new commits require re-approval)
- Status checks use `"Workflow Name / Job Name"` format from GitHub Actions

### Apply via CLI

```bash
# Apply configuration
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --input .github/branch-protection-config.json

# Verify configuration
gh api repos/:owner/:repo/branches/main/protection | jq
```

### Update Specific Settings

```bash
# Update required approvals only
gh api repos/:owner/:repo/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field required_approving_review_count=1

# Add status check
gh api repos/:owner/:repo/branches/main/protection/required_status_checks/contexts \
  --method POST \
  --field contexts[]="new-check-name"
```

---

## Verification

### Test Branch Protection

After configuring, verify protection works:

#### 1. Test Direct Push (Should Fail)

```bash
# Create test file
echo "test" > test-protection.txt

# Try to push directly to main
git checkout main
git add test-protection.txt
git commit -m "test: verify branch protection"
git push origin main

# Expected output:
# remote: error: GH006: Protected branch update failed
# To https://github.com/owner/repo.git
#  ! [remote rejected] main -> main (protected branch hook declined)
```

#### 2. Test PR Without Approval (Should Block Merge)

```bash
# Create feature branch
git checkout -b test/verify-approval-required
git push -u origin test/verify-approval-required

# Create PR
gh pr create --title "Test: Verify approval required" --body "Testing branch protection"

# Try to merge without approval
gh pr merge --squash

# Expected: Error requiring review approval
```

#### 3. Test PR Without Status Checks (Should Block Merge)

```bash
# Wait for CI to start but cancel it
gh run list --branch test/verify-status-checks
gh run cancel <run-id>

# Try to merge
gh pr merge --squash

# Expected: Error requiring status checks to pass
```

#### 4. Verify Configuration

```bash
# View current protection settings
gh api repos/:owner/:repo/branches/main/protection \
  | jq '{
      required_status_checks: .required_status_checks.contexts,
      required_approvals: .required_pull_request_reviews.required_approving_review_count,
      enforce_admins: .enforce_admins.enabled,
      restrictions: .restrictions
    }'
```

---

## Troubleshooting

| Problem | Solution | Verification |
|---------|----------|--------------|
| **Status checks not appearing** | Workflow must exist in `.github/workflows/`, run at least once, and name matches exactly (case-sensitive) | `gh workflow list` |
| **Can't enable protection** | Must be repo owner/admin; check org restrictions | `gh api repos/:owner/:repo \| jq '.permissions'` |
| **PR merges without approval** | Verify `enforce_admins` setting and user bypass permissions | `gh api repos/:owner/:repo/branches/main/protection \| jq '.enforce_admins'` |
| **Force push still works** | Verify `allow_force_pushes: false` and deploy key permissions | `gh api repos/:owner/:repo/branches/main/protection \| jq '.allow_force_pushes'` |

---

## Updating Protection Rules

**Common updates** (see "Update Specific Settings" section above for full commands):

```bash
# Add status check
gh api repos/:owner/:repo/branches/main/protection/required_status_checks/contexts \
  --method POST --field contexts[]="new-check-name"

# Change required approvals
gh api repos/:owner/:repo/branches/main/protection/required_pull_request_reviews \
  --method PATCH --field required_approving_review_count=2

# ⚠️ EMERGENCY ONLY: Disable protection temporarily
gh api repos/:owner/:repo/branches/main/protection --method DELETE
# Re-enable immediately: gh api repos/:owner/:repo/branches/main/protection --method PUT --input .github/branch-protection-config.json
```

---

## Best Practices

### For Maintainers

1. **Review rules quarterly:** Ensure protection rules match team needs
2. **Monitor bypasses:** Never allow bypassing (enforce_admins: true)
3. **Update status checks:** Add new checks as CI evolves
4. **Communicate changes:** Notify team when rules change

### For Contributors

1. **Expect protection:** Don't try to push directly to main
2. **Keep branches updated:** Rebase or merge main regularly
3. **Fix failing checks:** Don't request review until CI passes
4. **Respond to reviews:** Address all feedback before merge

### For Repository Admins

1. **Test before enabling:** Verify workflows work before requiring them
2. **Document exceptions:** If bypass needed, document why and how long
3. **Consistent enforcement:** Apply same rules to everyone
4. **Regular audits:** Review protection settings for gaps

---

## Security Considerations

### Required Checks for Security

**Minimum security checks:**
- `security-scan`: Bandit (AST-based security analysis)
- `security-scan`: Safety (dependency vulnerability checks)
- `security-scan`: pip-audit (PyPI package audit)
- `semgrep`: Static analysis for security patterns

**Additional recommended:**
- `codeql`: GitHub Advanced Security (if available)
- `dependency-review`: Automated dependency security

### Signed Commits

**When to require:**
- High-security projects
- Compliance requirements
- Multiple contributors
- Production releases

**When to skip:**
- Single maintainer
- Private repository
- Adds contributor friction

### Deploy Keys and Service Accounts

**Important:** If using deploy keys or service accounts:
1. Grant minimal necessary permissions
2. Don't give bypass permissions
3. Monitor usage via audit logs
4. Rotate keys regularly

---

## See Also

- [GIT_WORKFLOW.md](GIT_WORKFLOW.md) - Complete git workflow guide
- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Release workflow integration
- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)

---

**Last Updated:** 2025-10-31
**Version:** 1.1.0
