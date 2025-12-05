# YogaFlow Production Deployment Checklist

This checklist ensures a safe and successful production deployment.

## Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] **Backend `.env.production` configured**
  - [ ] `SECRET_KEY` set to strong random value (64+ chars)
  - [ ] `JWT_SECRET_KEY` set to different strong random value
  - [ ] `DATABASE_URL` configured for PostgreSQL (not SQLite)
  - [ ] `ALLOWED_ORIGINS` set to production domain(s)
  - [ ] `EMAIL_ENABLED=True` and SMTP credentials configured
  - [ ] `FRONTEND_URL` set to production domain
  - [ ] `CDN_BASE_URL` configured if using CDN
  - [ ] `SENTRY_DSN` configured (optional but recommended)

- [ ] **Frontend `.env.production` configured**
  - [ ] `VITE_API_URL` points to production API
  - [ ] `VITE_CDN_URL` configured if using CDN
  - [ ] `VITE_APP_ENV=production`
  - [ ] `VITE_SENTRY_DSN` configured (optional)

### 2. Database

- [ ] **PostgreSQL database created**
  - [ ] Database user created with appropriate permissions
  - [ ] Database name matches `DATABASE_URL`
  - [ ] Connection verified from application server
  - [ ] SSL/TLS enabled for database connections

- [ ] **Database backup configured**
  - [ ] Automated daily backups scheduled
  - [ ] Backup restoration tested
  - [ ] Backup retention policy defined

- [ ] **Migrations ready**
  - [ ] All migrations tested in staging
  - [ ] Migration rollback plan documented
  - [ ] Database schema reviewed

### 3. Security

- [ ] **HTTPS Configuration**
  - [ ] SSL/TLS certificate obtained (Let's Encrypt or commercial)
  - [ ] Certificate installed and configured
  - [ ] HTTP to HTTPS redirect enabled
  - [ ] Certificate auto-renewal configured

- [ ] **Secrets Management**
  - [ ] All secrets stored in environment variables (not in code)
  - [ ] `.env.production` file secured (chmod 600)
  - [ ] No secrets committed to version control
  - [ ] Secret rotation plan documented

- [ ] **API Security**
  - [ ] CORS configured with production domains only
  - [ ] Rate limiting enabled on auth endpoints
  - [ ] Security headers middleware enabled
  - [ ] No debug mode in production (`DEBUG=False`)

- [ ] **Authentication**
  - [ ] JWT secret keys are strong and unique
  - [ ] Password hashing using bcrypt with rounds >= 12
  - [ ] Account lockout after failed login attempts
  - [ ] Session timeout configured appropriately

### 4. Infrastructure

- [ ] **Server/Container Setup**
  - [ ] Application server provisioned (sufficient CPU/RAM)
  - [ ] Database server provisioned (or managed service configured)
  - [ ] CDN/Static file hosting configured
  - [ ] Load balancer configured (if using multiple instances)

- [ ] **Networking**
  - [ ] Domain name registered and DNS configured
  - [ ] Firewall rules configured (only necessary ports open)
  - [ ] DDoS protection enabled (CloudFlare, AWS Shield, etc.)

- [ ] **Docker/Container (if applicable)**
  - [ ] Docker images built for production
  - [ ] Images scanned for vulnerabilities
  - [ ] Container resource limits set
  - [ ] Container health checks configured

### 5. Monitoring & Logging

- [ ] **Error Tracking**
  - [ ] Sentry (or alternative) configured and tested
  - [ ] Error alerts configured
  - [ ] Error notification channels set up

- [ ] **Application Monitoring**
  - [ ] Health check endpoint responding
  - [ ] Uptime monitoring configured (UptimeRobot, Pingdom, etc.)
  - [ ] Performance monitoring enabled
  - [ ] Log aggregation configured (if using multiple instances)

- [ ] **Alerting**
  - [ ] Critical error alerts configured
  - [ ] High CPU/memory alerts configured
  - [ ] Database connection failure alerts
  - [ ] Disk space alerts

### 6. Testing

- [ ] **Pre-deployment Testing**
  - [ ] All unit tests passing
  - [ ] All integration tests passing
  - [ ] End-to-end tests passing
  - [ ] Security scan completed (no critical vulnerabilities)

- [ ] **Staging Deployment**
  - [ ] Application deployed to staging environment
  - [ ] Staging environment mirrors production
  - [ ] Smoke tests passed in staging
  - [ ] Performance tests passed in staging

### 7. Backup & Rollback

- [ ] **Backup Plan**
  - [ ] Current production data backed up
  - [ ] Backup verified and tested
  - [ ] Backup location documented

- [ ] **Rollback Plan**
  - [ ] Previous version tagged in Git
  - [ ] Rollback procedure documented
  - [ ] Database rollback plan ready (if schema changes)
  - [ ] Estimated rollback time known

## Deployment Steps

### Phase 1: Preparation (Before Deployment)

1. [ ] **Code Preparation**
   ```bash
   # Ensure you're on the correct branch
   git checkout main
   git pull origin main

   # Tag the release
   git tag -a v1.0.0 -m "Production release v1.0.0"
   git push origin v1.0.0
   ```

2. [ ] **Backend Preparation**
   ```bash
   cd backend
   # Run tests
   pytest app/tests/ -v
   # Build production image (if using Docker)
   docker build -t yogaflow-backend:v1.0.0 .
   ```

3. [ ] **Frontend Preparation**
   ```bash
   cd frontend
   # Run tests
   npm run test:run
   # Build for production
   npm run build
   ```

4. [ ] **Database Backup**
   ```bash
   # Backup current production database
   pg_dump -h localhost -U yogaflow_prod yogaflow_prod > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

### Phase 2: Database Migration

5. [ ] **Run Database Migrations**
   ```bash
   cd backend
   source venv/bin/activate
   # Review pending migrations
   alembic current
   # Apply migrations
   ./scripts/db_migrate.sh
   # Verify migration success
   alembic current
   ```

### Phase 3: Application Deployment

6. [ ] **Deploy Backend**

   **Option A: Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d backend
   ```

   **Option B: Systemd Service**
   ```bash
   sudo systemctl restart yogaflow-api
   ```

   **Option C: Manual**
   ```bash
   cd backend
   gunicorn app.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

7. [ ] **Deploy Frontend**

   **Option A: Static Hosting (Netlify/Vercel)**
   ```bash
   cd frontend
   netlify deploy --prod --dir=dist
   # or
   vercel --prod
   ```

   **Option B: S3 + CloudFront**
   ```bash
   aws s3 sync dist/ s3://your-bucket-name/ --delete
   aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
   ```

   **Option C: Nginx**
   ```bash
   sudo cp -r dist/* /var/www/yogaflow/
   sudo systemctl reload nginx
   ```

### Phase 4: Verification

8. [ ] **Health Checks**
   ```bash
   # Backend health check
   curl https://api.yourdomain.com/health
   # Should return: {"status":"healthy","service":"yogaflow-api","version":"1.0.0"}

   # Frontend accessibility
   curl -I https://yourdomain.com
   # Should return: 200 OK
   ```

9. [ ] **Functional Testing**
   - [ ] User registration works
   - [ ] User login works
   - [ ] Email verification works
   - [ ] Password reset works
   - [ ] Pose browsing works
   - [ ] Sequence browsing works
   - [ ] Practice session starts and completes
   - [ ] History/statistics display correctly

10. [ ] **Security Verification**
    ```bash
    # Check security headers
    curl -I https://api.yourdomain.com/health | grep -E "(X-Content-Type-Options|X-Frame-Options|Strict-Transport-Security)"

    # Verify HTTPS redirect
    curl -I http://yourdomain.com | grep Location
    # Should redirect to https://
    ```

11. [ ] **Performance Check**
    - [ ] Page load time < 2 seconds
    - [ ] API response time < 200ms
    - [ ] Images load quickly from CDN

### Phase 5: Post-Deployment

12. [ ] **Monitoring**
    - [ ] Check Sentry for errors
    - [ ] Monitor server logs for issues
    - [ ] Verify health check endpoint
    - [ ] Check database connections

13. [ ] **Documentation**
    - [ ] Update deployment notes
    - [ ] Document any issues encountered
    - [ ] Note any configuration changes made

14. [ ] **Communication**
    - [ ] Notify team of successful deployment
    - [ ] Update status page (if applicable)
    - [ ] Announce to users (if public launch)

## Post-Deployment Monitoring (First 24 Hours)

- [ ] **Hour 1**: Active monitoring
  - [ ] No critical errors in Sentry
  - [ ] Health check passing
  - [ ] No server alerts

- [ ] **Hour 4**: Check metrics
  - [ ] Response times normal
  - [ ] Error rate < 1%
  - [ ] User registrations working

- [ ] **Hour 12**: Review logs
  - [ ] No unexpected errors
  - [ ] Database performance normal
  - [ ] API endpoints responding

- [ ] **Hour 24**: Full review
  - [ ] Uptime > 99.5%
  - [ ] All features functional
  - [ ] User feedback reviewed

## Rollback Procedure

If critical issues are discovered:

1. [ ] **Assess Impact**
   - Determine severity of issue
   - Check if rollback is necessary

2. [ ] **Execute Rollback**
   ```bash
   # Rollback backend
   git checkout v1.0.0-previous
   docker-compose -f docker-compose.prod.yml up -d backend
   # or
   sudo systemctl restart yogaflow-api

   # Rollback frontend
   git checkout v1.0.0-previous
   cd frontend && npm run build
   # Deploy previous version
   ```

3. [ ] **Database Rollback (if needed)**
   ```bash
   # Restore from backup
   psql -h localhost -U yogaflow_prod yogaflow_prod < backup_TIMESTAMP.sql

   # Or use Alembic downgrade
   alembic downgrade -1
   ```

4. [ ] **Verify Rollback**
   - [ ] Application responding
   - [ ] Critical features working
   - [ ] No new errors

5. [ ] **Post-Rollback**
   - [ ] Document the issue
   - [ ] Create fix plan
   - [ ] Schedule redeployment

## Success Criteria

Deployment is considered successful when:

- [ ] All health checks passing
- [ ] Zero critical errors in first 24 hours
- [ ] Uptime > 99.5% in first 24 hours
- [ ] All core user flows working (registration → practice → tracking)
- [ ] Response times within acceptable range
- [ ] No security vulnerabilities reported
- [ ] Monitoring and alerts functioning

## Emergency Contacts

- **On-Call Engineer**: [Name/Contact]
- **Database Admin**: [Name/Contact]
- **DevOps Lead**: [Name/Contact]
- **Product Manager**: [Name/Contact]

## Resources

- **Runbooks**: `/docs/runbooks/`
- **Architecture Docs**: `/docs/architecture.md`
- **API Documentation**: `https://api.yourdomain.com/docs`
- **Monitoring Dashboard**: [Sentry/Grafana URL]
- **Status Page**: [Status page URL]

---

**Last Updated**: 2025-12-05
**Version**: 1.0.0
