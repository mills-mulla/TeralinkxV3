# Production Deployment Guide - Finance App

**Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: Ready for Production Deployment

---

## Pre-Deployment Checklist

### 1. Install Dependencies (5 minutes)

```bash
cd /home/ghost/Desktop/TeralinkxV3
pip install -r requirements.txt

# Verify critical packages
pip list | grep -E "reportlab|python-pptx|xgboost|celery|redis"
```

### 2. Run Production Readiness Check (2 minutes)

```bash
cd teralinkx
python manage.py check_production_ready
```

Expected output:
```
✓ PRODUCTION READY - All checks passed!
```

### 3. Run Test Suite (10 minutes)

```bash
# Run all tests
python manage.py run_finance_tests

# Run with coverage
python manage.py run_finance_tests --coverage

# Target: >60% coverage
```

### 4. Database Migrations (2 minutes)

```bash
# Check for pending migrations
python manage.py showmigrations finance

# Apply migrations
python manage.py migrate finance

# Verify
python manage.py migrate --check
```

### 5. Configure Celery (15 minutes)

#### Update main Celery configuration

Edit `teralinkx/celery.py`:

```python
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')

app = Celery('teralinkx')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Import finance app tasks and schedules
from finance.celery_schedule import CELERY_BEAT_SCHEDULE, CELERY_TASK_ROUTES

app.conf.beat_schedule = CELERY_BEAT_SCHEDULE
app.conf.task_routes = CELERY_TASK_ROUTES

app.autodiscover_tasks()
```

#### Start Celery Workers

```bash
# Terminal 1: Default queue (4 workers)
celery -A teralinkx worker -Q default -c 4 -l info

# Terminal 2: ML queue (2 workers)
celery -A teralinkx worker -Q ml -c 2 -l info

# Terminal 3: OCR queue (3 workers)
celery -A teralinkx worker -Q ocr -c 3 -l info

# Terminal 4: HIDS queue (2 workers)
celery -A teralinkx worker -Q hids -c 2 -l info

# Terminal 5: Beat scheduler
celery -A teralinkx beat -l info
```

#### Verify Celery

```bash
# Check workers
celery -A teralinkx inspect active

# Check scheduled tasks
celery -A teralinkx inspect scheduled
```

### 6. Configure Monitoring (30 minutes)

#### Add Middleware to settings.py

```python
MIDDLEWARE = [
    # ... existing middleware
    'finance.middleware.RequestLoggingMiddleware',
    'finance.middleware.FinanceErrorHandlerMiddleware',
    'finance.middleware.SensitiveDataFilterMiddleware',
]
```

#### Configure Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/teralinkx/finance.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'finance': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

#### Set up Health Check Monitoring

Add to your monitoring system (Prometheus, Datadog, etc.):

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'teralinkx-finance'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/metrics/'
```

### 7. Configure Rate Limiting (10 minutes)

Add to `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'finance.throttling.FinanceAPIThrottle',
        'finance.throttling.FinanceAnonThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'finance_api': '1000/hour',
        'finance_anon': '100/hour',
        'payment_api': '500/hour',
        'export_api': '50/hour',
        'health_check': '10000/hour',
    }
}
```

### 8. Environment Variables (5 minutes)

Create `.env` file:

```bash
# Django
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=srv.teralinkxwaves.uk,localhost

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/teralinkx

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (for board reports)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@teralinkxwaves.uk

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
```

### 9. Database Backup (10 minutes)

```bash
# Create backup script
cat > /home/ghost/backup_finance.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/teralinkx"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump teralinkx > $BACKUP_DIR/teralinkx_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/teralinkx_$DATE.sql"
EOF

chmod +x /home/ghost/backup_finance.sh

# Add to crontab (daily at 2am)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ghost/backup_finance.sh") | crontab -
```

### 10. Security Hardening (15 minutes)

#### Update settings.py

```python
# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://cli.teralinkxwaves.uk",
    "https://su.teralinkxwaves.uk",
]

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

---

## Deployment Steps

### Step 1: Stop Services

```bash
# Stop Django
sudo systemctl stop gunicorn

# Stop Celery workers
sudo systemctl stop celery-worker
sudo systemctl stop celery-beat
```

### Step 2: Pull Latest Code

```bash
cd /home/ghost/Desktop/TeralinkxV3
git pull origin main
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations

```bash
cd teralinkx
python manage.py migrate
```

### Step 5: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 6: Run Production Check

```bash
python manage.py check_production_ready
```

### Step 7: Start Services

```bash
# Start Django
sudo systemctl start gunicorn

# Start Celery
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Verify
sudo systemctl status gunicorn
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

### Step 8: Verify Deployment

```bash
# Check health endpoint
curl https://srv.teralinkxwaves.uk/api/health/

# Expected response:
# {"status": "healthy", "timestamp": "...", "checks": {...}}

# Check metrics
curl https://srv.teralinkxwaves.uk/api/metrics/

# Run smoke tests
python manage.py test finance.tests.api.test_endpoints --failfast
```

---

## Post-Deployment Monitoring

### 1. Monitor Logs

```bash
# Django logs
tail -f /var/log/teralinkx/finance.log

# Celery logs
tail -f /var/log/celery/worker.log

# Nginx logs
tail -f /var/log/nginx/access.log
```

### 2. Monitor Health Checks

```bash
# Set up monitoring alerts
watch -n 30 'curl -s https://srv.teralinkxwaves.uk/api/health/ | jq'
```

### 3. Monitor Celery Tasks

```bash
# Check task queue depth
celery -A teralinkx inspect active

# Check failed tasks
celery -A teralinkx inspect failed
```

### 4. Monitor Database Performance

```bash
# Check slow queries
psql teralinkx -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

---

## Rollback Procedure

If issues are detected:

### Quick Rollback

```bash
# Stop services
sudo systemctl stop gunicorn celery-worker celery-beat

# Restore database backup
psql teralinkx < /var/backups/teralinkx/teralinkx_YYYYMMDD_HHMMSS.sql

# Checkout previous version
git checkout <previous-commit-hash>

# Restart services
sudo systemctl start gunicorn celery-worker celery-beat
```

---

## Troubleshooting

### Issue: Health check fails

```bash
# Check database
python manage.py dbshell

# Check Redis
redis-cli ping

# Check Celery
celery -A teralinkx inspect ping
```

### Issue: Tests failing

```bash
# Run specific test
python manage.py test finance.tests.unit.test_models.CurrencyModelTest

# Run with verbose output
python manage.py test finance --verbosity=2
```

### Issue: Celery tasks not running

```bash
# Check Beat scheduler
celery -A teralinkx inspect scheduled

# Check worker status
celery -A teralinkx inspect active

# Restart workers
sudo systemctl restart celery-worker celery-beat
```

### Issue: High memory usage

```bash
# Check Celery worker memory
ps aux | grep celery

# Restart workers with lower concurrency
celery -A teralinkx worker -Q default -c 2 -l info
```

---

## Performance Optimization

### 1. Database Indexes

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_payment_transaction_status ON finance_paymenttransaction(status);
CREATE INDEX idx_transaction_queue_status ON finance_transactionqueue(status);
CREATE INDEX idx_churn_prediction_risk ON finance_churnprediction(risk_level);
```

### 2. Redis Configuration

```bash
# Edit /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 3. Celery Optimization

```python
# settings.py
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes
```

---

## Success Criteria

Deployment is successful when:

- ✅ All health checks return "healthy"
- ✅ All tests pass (>60% coverage)
- ✅ Celery workers are active
- ✅ API endpoints respond < 500ms
- ✅ No errors in logs for 1 hour
- ✅ Board report export works
- ✅ Scheduled tasks execute on time

---

## Support Contacts

- **Technical Lead**: [Your Name]
- **DevOps**: [DevOps Contact]
- **On-Call**: [On-Call Number]

---

**Deployment Completed By**: _______________  
**Date**: _______________  
**Sign-off**: _______________
