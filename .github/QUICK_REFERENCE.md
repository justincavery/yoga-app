# CI/CD Quick Reference Card

## 🚀 Common Commands

### Deploy to Production
```bash
git push origin main  # Triggers automatic deployment
```

### Manual Deploy
```bash
# Via GitHub UI
# Actions → CI/CD Production Pipeline → Run workflow

# Via GitHub CLI
gh workflow run ci-cd-production.yml
```

### Rollback
```bash
# Via GitHub UI
# Actions → Rollback Deployment → Run workflow
# Fill in: environment, version, reason

# Via GitHub CLI
gh workflow run rollback.yml \
  -f environment=production \
  -f version=v2024.12.05-abc1234 \
  -f reason="Critical bug"
```

### Check Health
```bash
# Backend
curl https://your-backend.railway.app/health

# Full verification
./infrastructure/scripts/verify_deployment.sh \
  https://your-backend.railway.app \
  https://your-frontend.railway.app
```

### View Logs
```bash
# Railway logs
railway logs --service backend
railway logs --service frontend --tail

# GitHub Actions logs
# Actions → Workflow run → Job → Step
```

---

## 🔐 Required Secrets

### GitHub Secrets
| Secret | Value | Where |
|--------|-------|-------|
| `RAILWAY_TOKEN` | `railway token` | Settings → Secrets |

### Railway Variables (Backend)
```bash
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=${{Postgres.DATABASE_URL}}
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.railway.app
```

### Railway Variables (Frontend)
```bash
VITE_API_URL=https://your-backend.railway.app
NODE_ENV=production
```

---

## 📋 Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI/CD Production** | Push to main | Deploy to production |
| **Pull Request** | PR created/updated | Quality gates |
| **Security Scan** | Daily + Push | Security checks |
| **Health Check** | Every 15 min | Monitor production |
| **Rollback** | Manual only | Revert deployment |

---

## ✅ Quality Gates

### PR Must Pass
- ✅ Backend lint (Black, isort, flake8)
- ✅ Frontend lint (ESLint)
- ✅ All tests (Backend + Frontend)
- ✅ Security scans (Bandit, Safety, Trufflehog)
- ✅ Build verification (Docker + npm)

### Deploy Requirements
- ✅ On main branch
- ✅ All quality gates passed
- ✅ Tests passed
- ✅ Security scans clean

---

## 🐛 Troubleshooting

### Deployment Failed
```bash
# 1. Check workflow logs
# GitHub → Actions → Failed run → Job → Step

# 2. Check Railway
railway status
railway logs

# 3. Verify secrets
# GitHub → Settings → Secrets
railway variables
```

### Health Check Failed
```bash
# 1. Check health endpoint
curl -v https://your-backend.railway.app/health

# 2. Check database
railway connect postgres

# 3. Check environment
railway variables | grep -E "SECRET_KEY|DATABASE_URL"

# 4. Restart if needed
railway restart
```

### Tests Failed
```bash
# Run locally first
cd backend && pytest app/tests/ -v
cd frontend && npm test

# Check specific test
pytest app/tests/test_file.py::test_function -v
```

---

## 📊 Monitoring

### View Metrics
```bash
# Railway Dashboard
https://railway.app/dashboard

# GitHub Actions
https://github.com/[user]/[repo]/actions

# Health Check Results
# Actions → Production Health Check
```

### Check Deployment Status
```bash
railway status

# Or check GitHub
# Settings → Environments → production
```

---

## 🔄 Common Workflows

### Feature Development
```bash
1. git checkout -b feature/my-feature
2. # Make changes
3. git commit -m "feat: add new feature"
4. git push origin feature/my-feature
5. # Create PR in GitHub
6. # Wait for checks to pass
7. # Merge PR (auto-deploys to production)
```

### Hotfix
```bash
1. git checkout -b hotfix/critical-bug
2. # Fix bug
3. git commit -m "fix: resolve critical bug"
4. git push origin hotfix/critical-bug
5. # Create PR with "urgent" label
6. # Fast-track review
7. # Merge (auto-deploys)
8. # Monitor health checks
```

### Emergency Rollback
```bash
1. Actions → Rollback Deployment
2. Environment: production
3. Version: [previous working version]
4. Reason: "Critical production issue"
5. Click "Run workflow"
6. Monitor rollback completion
7. Verify: curl https://backend.railway.app/health
8. Investigate root cause
```

---

## 📚 Documentation

- **Quick Start:** `.github/GITHUB_ACTIONS_SETUP.md` (10 min)
- **Complete Guide:** `infrastructure/CICD_DEPLOYMENT_GUIDE.md` (full docs)
- **Readiness:** `infrastructure/DEPLOYMENT_READINESS_ASSESSMENT.md`
- **Summary:** `CICD_IMPLEMENTATION_SUMMARY.md`

---

## 🆘 Emergency Contacts

- **Documentation:** See files above
- **Railway Support:** https://discord.gg/railway
- **GitHub Actions:** https://docs.github.com/actions
- **Create Issue:** GitHub Issues tab

---

## ⚡ Quick Tips

1. **Always test locally before pushing**
2. **Small PRs are faster to review**
3. **Use conventional commits** (feat:, fix:, docs:)
4. **Check health after deploy** (automated, but good to verify)
5. **Don't panic - rollback is one click away**

---

## 📝 Checklist: First Deployment

Before first deploy:
- [ ] GitHub Secret `RAILWAY_TOKEN` set
- [ ] Railway backend variables configured
- [ ] Railway frontend variables configured
- [ ] Branch protection enabled
- [ ] GitHub Actions enabled

First deploy:
- [ ] Push to main branch
- [ ] Watch workflow in Actions tab
- [ ] All jobs pass (green checkmarks)
- [ ] Backend health returns 200
- [ ] Frontend loads successfully
- [ ] Smoke tests pass

Post-deploy:
- [ ] Monitor health checks
- [ ] Test user flows
- [ ] Check error rates
- [ ] Document any issues

---

**For detailed instructions, see `.github/GITHUB_ACTIONS_SETUP.md`**
