# GitHub Repository Settings Checklist

Manual settings changes required via GitHub web interface to complete repository optimization.

**Context:** These settings cannot be configured via code/configuration files and must be set through the GitHub UI.

**Time Required:** ~5-10 minutes

---

## Settings to Configure

### 1. Pull Requests Settings

**Path:** Repository → Settings → General → Pull Requests

**Configure:**
- ✅ **Enable:** "Allow squash merging" (KEEP enabled)
- ❌ **Disable:** "Allow merge commits" (KEEP disabled)
- ❌ **Disable:** "Allow rebase merging" (KEEP disabled)
- ✅ **Enable:** "Automatically delete head branches" ⭐ **NEW - Enable this**
- ✅ **Enable:** "Allow auto-merge"
- ✅ **Enable:** "Suggest updating pull request branches"

**Rationale:**
- **Auto-delete branches:** Saves ~5 minutes/week on manual cleanup, prevents clutter
- **Squash-only merging:** Maintains clean linear history
- **Auto-merge:** Enables Dependabot auto-merge for patches

---

### 2. Actions Permissions

**Path:** Repository → Settings → Actions → General

**Configure:**

#### Workflow Permissions:
- ✅ **Select:** "Read repository contents and packages permissions" ⭐ **NEW - Change from default**
- ✅ **Enable:** "Allow GitHub Actions to create and approve pull requests"

**Rationale:**
- **Read-only default:** Reduces attack surface, workflows request explicit write permissions
- **Allow PR creation:** Enables Dependabot and automation workflows

---

### 3. Security Features (Verify Enabled)

**Path:** Repository → Settings → Code security and analysis

**Verify These Are Enabled (should already be active for public repos):**
- ✅ **Dependabot alerts** - Vulnerability notifications
- ✅ **Dependabot security updates** - Auto-PRs for security patches
- ✅ **Secret scanning** - Detects committed secrets (free for public repos)
- ✅ **Code scanning** (CodeQL) - Static analysis (free for public repos)

**No Action Needed:** These should already be enabled for public repositories.

---

### 4. Branch Protection (Already Configured)

**Path:** Repository → Settings → Branches → main

**Status:** ✅ **Already configured via PR #12-16**
- Branch protection rules active
- Status checks required (5 checks)
- Owner bypass enabled (`enforce_admins: false`)
- No changes needed

---

## Step-by-Step Instructions

### For Auto-Delete Branches

1. Go to: https://github.com/jvlivonius/vsc-extension-scanner/settings
2. Scroll to section: **"Pull Requests"**
3. Find checkbox: **"Automatically delete head branches"**
4. **Check the box** ✅
5. **No save button needed** - changes apply immediately

### For Workflow Permissions

1. Go to: https://github.com/jvlivonius/vsc-extension-scanner/settings/actions
2. Scroll to section: **"Workflow permissions"**
3. Select radio button: **"Read repository contents and packages permissions"**
4. Check box: **"Allow GitHub Actions to create and approve pull requests"**
5. Click **"Save"** button

### For Security Features

1. Go to: https://github.com/jvlivonius/vsc-extension-scanner/settings/security_analysis
2. **Verify** all features show as **"Enabled"**
3. If any are disabled, click **"Enable"** button for each

---

## Verification

After making changes, verify:

```bash
# Check that next merged PR auto-deletes its branch
gh pr list --state closed --limit 1 --json headRefName

# Verify workflow permissions in next workflow run
gh run view --log | grep "GITHUB_TOKEN"
```

---

## Impact Summary

**Time Savings:**
- **Auto-delete branches:** ~5 min/week = ~260 min/year (4.3 hours)
- **Workflow efficiency:** ~10% faster CI feedback (cancel redundant runs)

**Security Improvements:**
- **Read-only workflows:** Reduced attack surface for compromised dependencies
- **Explicit permissions:** Each workflow requests only needed permissions

**Repository Health:**
- **Clean branch list:** No accumulation of stale branches
- **Professional appearance:** Organized, maintained repository

---

## Troubleshooting

**Issue:** "Automatically delete head branches" option not visible
- **Solution:** Ensure you have admin access to the repository

**Issue:** Workflow permission changes don't take effect
- **Solution:** Click "Save" button after selecting radio button

**Issue:** CodeQL not enabled
- **Solution:** Public repos get CodeQL free; private repos require GitHub Advanced Security

---

## Rollback

If you need to revert any changes:

**Auto-delete branches:**
1. Go to Settings → Pull Requests
2. Uncheck "Automatically delete head branches"

**Workflow permissions:**
1. Go to Settings → Actions → General
2. Select "Read and write permissions"
3. Click "Save"

---

## Related Documentation

- [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) - Branch protection configuration
- [GIT_WORKFLOW.md](GIT_WORKFLOW.md) - Git workflow and branching strategy
- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Release workflow

---

**Last Updated:** 2025-10-31 (PR #17 - Repository Optimization)
