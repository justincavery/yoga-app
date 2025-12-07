# GitHub Actions Workflows - YogaFlow

This directory contains the CI/CD workflows for the YogaFlow application.

## Workflow Files

### Active Workflows

| File | Purpose | Triggers | Status |
|------|---------|----------|--------|
| **ci-cd-production.yml** | Main deployment pipeline | Push to main, PR, Manual | ✅ Active |
| **pull-request.yml** | PR quality gates | Pull request events | ✅ Active |
| **security-scan.yml** | Security scanning | Push, PR, Daily 2AM UTC | ✅ Active |
| **health-check.yml** | Production monitoring | Every 15 min, Manual | ✅ Active |
| **rollback.yml** | Deployment rollback | Manual only | ✅ Active |

### Deprecated Workflows

| File | Status | Notes |
|------|--------|-------|
| **ci-cd.yml.old** | ⚠️ Deprecated | Replaced by ci-cd-production.yml |

## Workflow Descriptions

### ci-cd-production.yml - Main CI/CD Pipeline

**Purpose:** Complete deployment pipeline from code to production

**When it runs:**
- Automatic: Push to `main` branch
- Automatic: Pull requests to `main`
- Manual: Via GitHub Actions UI or CLI

**What it does:**
1. **Quality Checks** (Parallel)
   - Backend linting (Black, isort, flake8)
   - Frontend linting (ESLint)
   - Security scanning (Bandit, Safety)

2. **Testing** (Parallel)
   - Backend tests with PostgreSQL
   - Frontend unit tests
   - Coverage reporting

3. **E2E Testing** (PR only)
   - Playwright full-stack tests

4. **Build & Package**
   - Docker image build (multi-arch)
   - Push to GitHub Container Registry
   - Frontend production build

5. **Deployment** (Main only)
   - Deploy backend to Railway
   - Deploy frontend to Railway
   - Run smoke tests

6. **Post-Deploy**
   - Security scan (Trivy)
   - Create release notes
   - Tag release

**Duration:** ~10-15 minutes
**Required secrets:** `RAILWAY_TOKEN`

---

### pull-request.yml - PR Quality Gates

**Purpose:** Enforce code quality standards on pull requests

**When it runs:**
- Automatic: PR opened
- Automatic: PR updated
- Automatic: PR reopened

**What it does:**
1. **Validation**
   - PR title format check
   - PR size analysis
   - Merge conflict detection
   - Secrets detection (Trufflehog)

2. **Quality Checks**
   - Code complexity analysis
   - Code formatting verification
   - Lint checks
   - Console.log detection

3. **Testing**
   - Backend tests
   - Frontend tests
   - Build verification

4. **Documentation**
   - Check for doc updates
   - README validation

5. **Summary**
   - Generate PR summary
   - Comment results

**Duration:** ~5-7 minutes
**Blocks merge:** Yes (if required checks fail)

---

### security-scan.yml - Security Scanning

**Purpose:** Continuous security monitoring

**When it runs:**
- Automatic: Push to main or development
- Automatic: Pull requests
- Scheduled: Daily at 2 AM UTC

**What it does:**
1. **Dependency Scanning**
   - Python: Safety check
   - Node: npm audit

2. **Code Security**
   - Bandit security analysis
   - Upload security reports

**Duration:** ~3-5 minutes
**Blocks merge:** No (informational)

---

### health-check.yml - Production Monitoring

**Purpose:** Continuous production health monitoring

**When it runs:**
- Scheduled: Every 15 minutes
- Manual: Via GitHub Actions UI

**What it does:**
1. **Health Checks**
   - Backend `/health` endpoint
   - Frontend accessibility
   - Database connectivity
   - Response time tracking

2. **Performance**
   - Load testing
   - SSL certificate monitoring

3. **Incident Management**
   - Create GitHub issue on failure
   - Auto-label with priority

**Duration:** ~2-3 minutes
**Creates alerts:** Yes (on failure)

---

### rollback.yml - Deployment Rollback

**Purpose:** One-click rollback to previous version

**When it runs:**
- Manual only (workflow dispatch)

**Required inputs:**
- `environment`: production or staging
- `version`: Git tag to rollback to
- `reason`: Audit trail description

**What it does:**
1. **Validation**
   - Verify version exists
   - Display rollback information

2. **Rollback**
   - Deploy previous version
   - Wait for stabilization
   - Run health checks

3. **Verification**
   - Verify rollback success
   - Create incident issue
   - Notify team

**Duration:** ~3-5 minutes
**Requires approval:** Optional (configurable in environment)

---

## Workflow Dependencies

```
┌─────────────────────────────────────────┐
│         ci-cd-production.yml            │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ Lint/Test   │  │  Security Scan  │  │
│  └──────┬──────┘  └────────┬────────┘  │
│         │                  │            │
│         ├──────────────────┤            │
│         ▼                               │
│  ┌──────────────┐                       │
│  │ Docker Build │                       │
│  └──────┬───────┘                       │
│         │                               │
│         ▼                               │
│  ┌──────────────┐                       │
│  │    Deploy    │◄─ RAILWAY_TOKEN      │
│  └──────┬───────┘                       │
│         │                               │
│         ▼                               │
│  ┌──────────────┐                       │
│  │    Verify    │                       │
│  └──────────────┘                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        health-check.yml (Every 15m)     │
│                                         │
│         ┌──────────────┐                │
│         │ Check Health │                │
│         └──────┬───────┘                │
│                │                        │
│         Failure│                        │
│                ▼                        │
│         ┌──────────────┐                │
│         │Create Issue  │                │
│         └──────────────┘                │
└─────────────────────────────────────────┘
```

## Configuration

### Required GitHub Secrets

| Secret | Description | How to get |
|--------|-------------|------------|
| `RAILWAY_TOKEN` | Railway deployment token | `railway token` |
| `GITHUB_TOKEN` | GitHub API token | Automatic (built-in) |

### Optional Secrets

| Secret | Description | When needed |
|--------|-------------|-------------|
| `SNYK_TOKEN` | Snyk security token | If using Snyk |
| `CODECOV_TOKEN` | Codecov upload token | For private repos |

### Environment Configuration

**Production Environment:**
- URL: https://yoga-app-production.up.railway.app
- Protection rules: Optional (reviewers, wait timer)
- Deployment branches: `main` only

## Branch Protection Rules

Recommended settings for `main` branch:

```
✅ Require pull request before merging
  ✅ Require approvals: 1
  ✅ Dismiss stale approvals

✅ Require status checks to pass
  Required checks:
  - Backend Quality Checks
  - Backend Tests (PR)
  - Frontend Quality Checks
  - Build Verification

✅ Require branches to be up to date

✅ Do not allow bypassing the above settings
```

## Workflow Triggers Reference

### Push Events
```yaml
on:
  push:
    branches: [main]
```
Triggers: `ci-cd-production.yml`, `security-scan.yml`

### Pull Request Events
```yaml
on:
  pull_request:
    branches: [main]
```
Triggers: `ci-cd-production.yml`, `pull-request.yml`, `security-scan.yml`

### Schedule
```yaml
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
```
Triggers: `health-check.yml`

```yaml
on:
  schedule:
    - cron: '0 2 * * *'     # Daily at 2 AM UTC
```
Triggers: `security-scan.yml`

### Manual Trigger
```yaml
on:
  workflow_dispatch:
```
Triggers: All workflows support manual trigger

## Monitoring Workflows

### View Workflow Runs

1. Go to repository **Actions** tab
2. Select workflow from left sidebar
3. View run history

### Check Workflow Status

**Via GitHub UI:**
- Green checkmark ✅ = Success
- Red X ❌ = Failed
- Yellow circle ⚡ = In progress

**Via GitHub CLI:**
```bash
# List recent runs
gh run list

# View specific run
gh run view [run-id]

# View logs
gh run view [run-id] --log
```

### Workflow Notifications

**Configure in:** Settings → Notifications → Actions

Options:
- Email on failure
- Email on success
- GitHub UI notifications

## Troubleshooting

### Workflow Not Triggering

**Check:**
1. GitHub Actions enabled: Settings → Actions → General
2. Workflow file syntax valid: Actions tab shows errors
3. Branch protection not blocking: Settings → Branches
4. Event matches trigger: Review `on:` section in workflow

**Fix:**
```bash
# Validate workflow syntax
cat .github/workflows/ci-cd-production.yml | yamllint -

# Check for Git issues
git status
git log --oneline -5
```

### Workflow Failing

**Steps:**
1. Go to Actions → Failed run
2. Click on failed job
3. Expand failed step
4. Review error message
5. Fix issue locally
6. Push fix

**Common issues:**

| Error | Cause | Fix |
|-------|-------|-----|
| "Secret not found" | Missing GitHub Secret | Add in Settings → Secrets |
| "Tests failed" | Test errors | Run tests locally, fix, push |
| "Docker build failed" | Dockerfile error | Test Docker build locally |
| "Railway deploy failed" | Railway config | Check Railway variables |

### Slow Workflows

**Optimization tips:**
1. Use caching for dependencies
2. Run jobs in parallel where possible
3. Skip unnecessary steps with conditionals
4. Use matrix strategy for testing

## Best Practices

### Workflow Development

1. **Test locally first**
   ```bash
   # Install act (GitHub Actions locally)
   brew install act

   # Run workflow locally
   act -j build
   ```

2. **Use workflow templates**
   - Copy existing working workflows
   - Modify incrementally
   - Test each change

3. **Keep workflows DRY**
   - Use reusable workflows
   - Extract common steps
   - Use composite actions

### Security

1. **Never commit secrets**
   - Use GitHub Secrets
   - Use environment variables
   - Mask sensitive output

2. **Limit permissions**
   ```yaml
   permissions:
     contents: read
     packages: write
   ```

3. **Pin action versions**
   ```yaml
   - uses: actions/checkout@v4  # Good
   - uses: actions/checkout@main  # Avoid
   ```

### Performance

1. **Use caching**
   ```yaml
   - uses: actions/setup-python@v5
     with:
       cache: 'pip'
   ```

2. **Parallel jobs**
   ```yaml
   jobs:
     test-backend:
     test-frontend:  # Runs in parallel
   ```

3. **Conditional steps**
   ```yaml
   - name: Deploy
     if: github.ref == 'refs/heads/main'
   ```

## Maintenance

### Regular Tasks

**Weekly:**
- Review failed workflow runs
- Check for security alerts
- Update dependencies in workflows

**Monthly:**
- Review workflow efficiency
- Update action versions
- Clean up old workflow runs

**Quarterly:**
- Audit workflow permissions
- Review branch protection rules
- Update documentation

### Updating Workflows

1. Create feature branch
2. Modify workflow file
3. Test with workflow dispatch
4. Create PR
5. Review and merge

## Resources

### Documentation
- [GitHub Actions Quick Start](../GITHUB_ACTIONS_SETUP.md)
- [CI/CD Deployment Guide](../../infrastructure/CICD_DEPLOYMENT_GUIDE.md)
- [Quick Reference](../QUICK_REFERENCE.md)

### External Links
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Railway Docs](https://docs.railway.app)

### Support
- Create issue in repository
- Check GitHub Actions status: https://www.githubstatus.com
- Railway Discord: https://discord.gg/railway

---

**Last Updated:** December 6, 2025
**Maintained By:** DevOps Team
**Questions?** See `.github/GITHUB_ACTIONS_SETUP.md`
