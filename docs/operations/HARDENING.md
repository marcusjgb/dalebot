# Security Hardening Checklist

## Pre-Deployment

### Secrets Management
- [ ] All secrets in `.env` changed from defaults
- [ ] `DJANGO_SECRET_KEY` generated with `django.core.management.utils.get_random_secret_key()`
- [ ] `WHATSAPP_VERIFY_TOKEN` unique per environment
- [ ] `WHATSAPP_ACCESS_TOKEN` stored securely (not in repo)
- [ ] Database password strong and unique
- [ ] Redis password configured

### Database
- [ ] PostgreSQL `pg_hba.conf` restricts connections
- [ ] No `trust` auth method exposed externally
- [ ] SSL connections required for production
- [ ] Regular backups scheduled

### Application
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] HTTPS enforced via proxy/load balancer
- [ ] Security headers enabled (HSTS, CSP, etc.)
- [ ] Rate limiting enabled and tuned
- [ ] Admin URL changed from `/admin/`

### Docker/Infra
- [ ] No container running as root
- [ ] Images built from verified base images
- [ ] Docker socket not mounted in containers
- [ ] Healthcheck endpoints configured
- [ ] Logs not containing PII or secrets

## Post-Deployment Verification

### Functional
- [ ] Health check returns 200
- [ ] Webhook verifies signature correctly
- [ ] Rate limiting blocks excess requests
- [ ] Authentication works for all user roles
- [ ] Multi-tenant isolation verified

### Security
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] CSRF tokens working
- [ ] No verbose errors exposed
- [ ] Webhook signature validation works

### Performance
- [ ] Response times < 200ms p95
- [ ] No memory leaks after 1 hour
- [ ] Database connections properly pooled
- [ ] Celery tasks executing correctly

## Monitoring
- [ ] Error rates tracked
- [ ] Response times monitored
- [ ] Backup success/failure alerts
- [ ] Disk usage alerts
- [ ] Certificate expiration alerts
