# Branch Protection Configuration

Complete guide for configuring GitHub branch protection rules for the VS Code Extension Scanner project.

---

## Overview

Branch protection rules enforce code quality standards and workflow requirements on the `main` branch. These rules ensure:

- ✅ All changes reviewed before merge
- ✅ All tests pass before merge
- ✅ Security checks complete
- ✅ No direct pushes to production code
- ✅ Consistent merge history

**Target Branch:** `main`

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
  - `security-scan` (Bandit, Safety, pip-audit via GitHub Actions)
  - `coverage-test` (minimum 70% coverage requirement)
  - `test` (all 628 tests must pass)
  - `semgrep` (static security analysis)

**Rationale:**
- Prevents merging broken code
- Ensures security standards maintained
- Enforces test coverage requirements
- Catches security issues early

**Web Interface Steps:**
1. Check **"Require status checks to pass before merging"**
2. Check **"Require branches to be up to date before merging"**
3. Search and add each required status check:
   - Type `security-scan` → Select
   - Type `coverage-test` → Select
   - Type `test` → Select
   - Type `semgrep` → Select

**Note:** Status check names must match exactly what's defined in `.github/workflows/*.yml` files.

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

### 10. Do Not Allow Bypassing

**Setting:**
- ✅ **Do not allow bypassing the above settings**

**Rationale:**
- Applies rules to administrators
- Ensures no one can skip quality gates
- Creates consistent process for entire team

**Web Interface Steps:**
1. Check **"Do not allow bypassing the above settings"** under "Rules applied to everyone including administrators"

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
      "security-scan",
      "coverage-test",
      "test",
      "semgrep"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismissal_restrictions": {},
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

### Status Checks Not Appearing

**Problem:** Status check names don't appear in protection settings dropdown

**Solutions:**
1. Ensure workflow file exists in `.github/workflows/`
2. Workflow must have been triggered at least once
3. Check workflow name matches exactly (case-sensitive)
4. Wait a few minutes for GitHub to register workflows

**Verify workflows:**
```bash
gh workflow list
gh workflow view <workflow-name>
```

### Can't Enable Protection Rules

**Problem:** "You don't have permission to enable branch protection"

**Solutions:**
1. Must be repository owner or admin
2. Organization may have restrictions
3. Check repository settings permissions

**Verify permissions:**
```bash
gh api repos/:owner/:repo | jq '.permissions'
```

### PR Merges Without Approval

**Problem:** PRs can merge without review despite protection rules

**Solutions:**
1. Verify "enforce_admins" is enabled
2. Check if user has bypass permissions
3. Ensure protection rule is active (not draft)

**Verify enforcement:**
```bash
gh api repos/:owner/:repo/branches/main/protection \
  | jq '.enforce_admins'
```

### Force Push Still Works

**Problem:** Can still force push to main despite protection

**Solutions:**
1. Verify "allow_force_pushes" is false
2. Check if using deploy keys with force push permission
3. Verify protection rule targets correct branch

**Verify force push setting:**
```bash
gh api repos/:owner/:repo/branches/main/protection \
  | jq '.allow_force_pushes'
```

---

## Updating Protection Rules

### Add New Status Check

```bash
# Get current checks
gh api repos/:owner/:repo/branches/main/protection/required_status_checks \
  | jq '.contexts'

# Add new check
gh api repos/:owner/:repo/branches/main/protection/required_status_checks/contexts \
  --method POST \
  --field contexts[]="new-check-name"
```

### Change Required Approvals

```bash
# Increase to 2 approvals
gh api repos/:owner/:repo/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field required_approving_review_count=2
```

### Temporarily Disable Protection

**⚠️ DANGER:** Only for critical emergencies

```bash
# Disable protection (DANGEROUS!)
gh api repos/:owner/:repo/branches/main/protection \
  --method DELETE

# Re-enable immediately after emergency
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --input .github/branch-protection-config.json
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

**Last Updated:** 2025-01-31
**Version:** 1.0.0
