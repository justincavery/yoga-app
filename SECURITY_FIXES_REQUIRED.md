# YogaFlow Security Fixes - Quick Reference

## 🚨 PRODUCTION BLOCKERS (Must Fix Before Launch)

### 1. Rate Limiting - NOT IMPLEMENTED ⛔
**Status:** CRITICAL
**File:** `backend/app/main.py`
**Action Required:**
```bash
cd backend
pip install slowapi
```

Add to `backend/app/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

Apply to endpoints:
```python
@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
```

---

### 2. CORS Configuration - LOCALHOST IN PRODUCTION ⛔
**Status:** CRITICAL
**File:** `backend/.env.production`
**Action Required:**

Update line 22 with actual domain:
```bash
ALLOWED_ORIGINS=https://yogaflow.app,https://www.yogaflow.app
```

---

### 3. Secret Keys - DEFAULT VALUES ⛔
**Status:** CRITICAL
**File:** `backend/.env.production`
**Action Required:**

Generate strong secrets:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Update `.env.production`:
```bash
SECRET_KEY=<paste-generated-key-here>
JWT_SECRET_KEY=<paste-different-generated-key-here>
```

---

## ⚠️ HIGH PRIORITY (Should Fix Before Launch)

### 4. Admin Authorization - Email Domain Check
**File:** `backend/app/api/dependencies.py`
**Issue:** Uses `@admin.yogaflow.com` email check instead of RBAC
**Action:** Add `role` field to User model and implement proper role checking

### 5. JWT Token Revocation - Not Implemented
**File:** `backend/app/api/v1/endpoints/auth.py`
**Issue:** Logout doesn't invalidate tokens
**Action:** Implement Redis token blacklist

### 6. Account Lockout - Not Enforced
**File:** `backend/app/services/auth_service.py`
**Issue:** Config exists but no tracking/enforcement
**Action:** Add `failed_login_attempts` tracking

### 7. CSP Too Permissive
**File:** `backend/app/middleware/security_headers.py`
**Issue:** Contains `unsafe-inline` and `unsafe-eval`
**Action:** Remove unsafe directives for production

### 8. Deprecated datetime.utcnow()
**Files:** Multiple throughout codebase
**Issue:** Using deprecated timezone-unaware datetime
**Action:** Replace with `datetime.now(timezone.utc)`

### 9. Missing Database Indexes
**File:** `backend/app/models/practice_session.py`
**Issue:** No indexes on `started_at`, `completed_at`
**Action:** Create Alembic migration to add indexes

---

## 📋 MEDIUM PRIORITY (Recommended Improvements)

10. No HTML sanitization (install bleach)
11. Email enumeration in registration
12. Missing Cache-Control headers on auth endpoints
13. File upload needs magic byte validation
14. Access token expiry too long (24h → 15-60min)
15. No HTTPS enforcement in code

---

## Quick Fix Script

```bash
#!/bin/bash
# Run this from the project root

cd backend

# 1. Install required packages
pip install slowapi redis bleach python-magic

# 2. Generate secrets
echo "Generate these secrets and add to .env.production:"
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"

# 3. Update requirements.txt
cat >> requirements.txt << EOF

# Security enhancements
slowapi>=0.1.9
redis>=5.0.0
bleach>=6.0.0
python-magic>=0.4.27
EOF

echo "✅ Security dependencies added"
echo "⚠️  Now manually update .env.production with:"
echo "   - Real SECRET_KEY values (generated above)"
echo "   - Production CORS origins"
echo "   - Then implement rate limiting in main.py"
```

---

## Testing Checklist

After implementing fixes, test:

- [ ] Rate limiting blocks after 5 login attempts
- [ ] CORS blocks requests from unauthorized origins
- [ ] JWT tokens work with new secret keys
- [ ] Admin endpoints check role, not email
- [ ] Logout invalidates tokens (if token revocation implemented)
- [ ] Account locks after 5 failed login attempts
- [ ] CSP blocks inline scripts
- [ ] Database queries are fast with new indexes

---

## Timeline Estimate

- **Critical fixes:** 1-2 days
- **High priority fixes:** 3-5 days
- **Full production readiness:** 1 week

---

## Resources

- Full audit report: `SECURITY_AUDIT_REPORT.md`
- OWASP Top 10: https://owasp.org/Top10/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Slowapi docs: https://slowapi.readthedocs.io/
