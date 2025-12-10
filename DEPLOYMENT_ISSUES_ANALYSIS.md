# Deployment Issues Analysis & Resolution Plan

**Date**: December 10, 2025
**Status**: CI/CD Pipeline Broken - Manual Deployments Required
**Priority**: HIGH

## Executive Summary

The GitHub Actions CI/CD pipeline for deploying to Hetzner has been failing consistently since December 9th. The live site at `https://app.laurayoga.co.uk` is running on 28-hour-old containers that were manually deployed. New code pushes to GitHub are NOT being deployed to production.

## Current Production Status

✅ **Live Site Operational**
- Containers running for 28 hours (last manual deployment)
- Frontend: Fixed dashboard API endpoint issue (deployed manually via SCP on Dec 10)
- Backend: 80 poses in database, API functional
- All 3 containers healthy: postgres, backend, nginx

❌ **CI/CD Pipeline Broken**
- Last successful deployment: December 7, 23:31 UTC
- All subsequent deployments: **FAILED** (10+ consecutive failures)
- Recent code changes deployed manually, bypassing CI/CD

## Root Cause Analysis

### Primary Issue: Permission Conflicts with `sudo` Commands

The deployment script requires `sudo` for two operations:
1. Stopping system nginx: `sudo systemctl stop nginx`
2. Cleaning root-owned files: `sudo rm -rf content/ backend/ frontend/ infrastructure/`

**Problem**: The `deploy` user requires password for sudo, but GitHub Actions SSH doesn't provide a terminal for password input.

**Error logs show**:
```
sudo: a terminal is required to read the password; either use the -S option
to read from standard input or configure an askpass helper
sudo: a password is required
```

### Secondary Issue: File Permission Conflicts

Even when sudo fails, the script continues but encounters permission errors during tar extraction:

```
tar: content/poses.yaml: Cannot open: File exists
tar: content/images: Cannot utime: Operation not permitted
tar: Exiting with failure status due to previous errors
```

**Root Cause**:
- Previous failed runs leave root-owned files in `/opt/yogaflow/`
- `deploy` user cannot overwrite these files
- `sudo rm` fails (no password), so old files remain
- Tar extraction fails due to permission conflicts

## Why Manual Deployments Work

Manual deployments via `ssh root@23.88.127.14` work because:
1. Root user doesn't need sudo password
2. Root can delete and overwrite any files
3. No permission conflicts during deployment

## Impact Assessment

**Business Impact**: MEDIUM
- Site is functional with manually deployed fixes
- New features/fixes require manual deployment (slow, error-prone)
- No automated rollback capability
- Risk of configuration drift between Git and production

**Technical Debt**: HIGH
- CI/CD pipeline completely non-functional
- Manual deployment workflow not documented
- No deployment verification or health checks
- Cannot scale team (only root user can deploy)

## Solution Options

### Option 1: Configure Passwordless Sudo (RECOMMENDED)

**Approach**: Give `deploy` user passwordless sudo for specific commands

**Implementation**:
```bash
# On server as root
echo 'deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop nginx' >> /etc/sudoers.d/deploy-user
echo 'deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl disable nginx' >> /etc/sudoers.d/deploy-user
echo 'deploy ALL=(ALL) NOPASSWD: /bin/rm -rf /opt/yogaflow/content/' >> /etc/sudoers.d/deploy-user
echo 'deploy ALL=(ALL) NOPASSWD: /bin/rm -rf /opt/yogaflow/backend/' >> /etc/sudoers.d/deploy-user
echo 'deploy ALL=(ALL) NOPASSWD: /bin/rm -rf /opt/yogaflow/frontend/' >> /etc/sudoers.d/deploy-user
echo 'deploy ALL=(ALL) NOPASSWD: /bin/rm -rf /opt/yogaflow/infrastructure/' >> /etc/sudoers.d/deploy-user
chmod 440 /etc/sudoers.d/deploy-user
```

**Pros**:
- Minimal changes to existing workflow
- Follows principle of least privilege
- Most secure option for CI/CD
- Standard industry practice

**Cons**:
- Requires root server access to configure
- Need to maintain sudoers file

**Effort**: 15 minutes

### Option 2: Deploy as Root User

**Approach**: Use root SSH key in GitHub Actions instead of deploy user

**Implementation**:
1. Generate new SSH key for GitHub Actions (as root)
2. Update `HETZNER_SSH_PRIVATE_KEY` secret with root key
3. Change all `deploy@` references to `root@` in workflow

**Pros**:
- Simplest fix
- No permission issues
- Works immediately

**Cons**:
- Less secure (root SSH access from CI/CD)
- Violates security best practices
- Higher risk if GitHub secrets compromised

**Effort**: 10 minutes

### Option 3: Restructure Deployment to Avoid Sudo

**Approach**: Redesign deployment to work within deploy user permissions

**Implementation**:
1. Move nginx to run on non-privileged ports (8080, 8443)
2. Use iptables redirect rules (configured once by root) to forward 80→8080, 443→8443
3. Change file ownership to deploy user after first deployment
4. Never require sudo in deployment script

**Pros**:
- Most secure long-term solution
- No privileged operations in CI/CD
- Better separation of concerns

**Cons**:
- Requires architectural changes
- More complex setup
- Need to reconfigure existing server

**Effort**: 2-3 hours

## Recommended Action Plan

### Immediate (Today)
1. **Implement Option 1** - Configure passwordless sudo for deploy user
   - SSH to server as root
   - Create `/etc/sudoers.d/deploy-user` with specific command whitelist
   - Test manual deployment as deploy user
   - Trigger GitHub Actions deployment
   - Verify containers restart with new code

2. **Document Manual Deployment Procedure**
   - Create `MANUAL_DEPLOYMENT.md` with step-by-step instructions
   - Include rollback procedures
   - Add to team wiki/runbook

### Short-term (This Week)
3. **Add Deployment Verification**
   - Add health check after deployment
   - Verify API returns 80 poses
   - Check frontend loads correctly
   - Send notification on success/failure

4. **Fix Frontend Build in CI**
   - Ensure `VITE_USE_MOCK_API=false` in workflow (line 97 - already added)
   - Verify environment variables in build logs
   - Add smoke test for built assets

### Medium-term (Next Sprint)
5. **Implement Blue-Green Deployment**
   - Run new containers alongside old
   - Health check new deployment
   - Switch nginx upstream on success
   - Enable instant rollback

6. **Add Deployment Monitoring**
   - Track deployment frequency
   - Monitor failure rates
   - Alert on deployment issues
   - Log deployment metrics

## Files Modified Recently (Manual Deployments)

**December 10, 2025**:
- `frontend/src/lib/api.js:238` - Fixed dashboard API endpoint from `/history/stats` to `/stats`
- `frontend/dist/` - Rebuilt and deployed manually via SCP

**December 9, 2025**:
- Multiple failed GitHub Actions deployments
- Database manually seeded with 80 poses using inline script

**December 8, 2025**:
- Last partially successful automated deployment
- Containers started but database remained empty

## Testing Requirements

Before marking CI/CD as fixed:
1. ✅ GitHub Actions workflow completes successfully
2. ✅ Containers restart with new code
3. ✅ Health check returns 200
4. ✅ API returns 80 poses
5. ✅ Frontend displays correctly
6. ✅ Dashboard loads without hanging
7. ✅ User registration works
8. ✅ Playwright E2E tests pass

## Risk Assessment

**Current Risk Level**: MEDIUM-HIGH

**Risks**:
1. Manual deployments are error-prone
2. Configuration drift between Git and production
3. No audit trail for manual deployments
4. Single point of failure (only one person can deploy)
5. Cannot quickly respond to production issues

**Mitigation**:
- Fix CI/CD within 24 hours (Option 1)
- Document manual procedure as backup
- Add deployment verification
- Create rollback runbook

## Questions for Project Manager

1. **Server Access**: Who has root SSH access to configure sudoers? (Required for Option 1)
2. **Security Policy**: Are passwordless sudo rules acceptable for CI/CD? (Standard practice)
3. **Priority**: Should we fix CI/CD before new features, or continue manual deployments?
4. **Monitoring**: Do we have budget/time for deployment monitoring tools?
5. **Team**: Who should be trained on manual deployment procedures as backup?

## Next Steps

**Immediate action required**:
1. Get root server access
2. Implement Option 1 (passwordless sudo)
3. Test GitHub Actions deployment
4. Verify production health

**Assignee**: DevOps/Senior Engineer
**ETA**: 1 hour
**Blocker**: Need root server access
