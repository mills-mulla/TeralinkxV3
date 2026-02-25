# Database Connection Timeout & Leak Prevention - Deployment Guide

## Changes Made (Priority 1 Fixes)

### 1. Database Configuration (`settings.py`)
**Changes:**
- Reduced `conn_max_age` from 600s → 60s (faster connection recycling)
- Added `conn_health_checks=True` (automatic stale connection detection)
- Added connection timeout: 10 seconds
- Added statement timeout: 30 seconds (kills slow queries)
- Added idle transaction timeout: 60 seconds

**Impact:** Prevents connection leaks and hanging queries

### 2. Redis Connection Pooling (`settings.py`)
**Changes:**
- Added connection pool with max 50 connections
- Added socket timeouts (5 seconds)
- Added TCP keepalive settings
- Added connection retry logic
- Added graceful failure handling

**Impact:** Prevents Redis connection exhaustion

### 3. Celery Configuration (`settings.py`)
**Changes:**
- Added `CELERY_WORKER_MAX_TASKS_PER_CHILD=100` (recycle workers)
- Added Redis connection pool settings
- Added broker connection retry logic

**Impact:** Prevents Celery worker memory leaks

### 4. Gunicorn Worker Recycling (`gunicorn_config.py`)
**Changes:**
- Reduced `max_requests` from 1000 → 200 (recycle workers 5x faster)
- Reduced `timeout` from 60s → 30s (kill slow requests faster)
- Reduced `keepalive` from 30s → 5s (close idle connections faster)
- Added `graceful_timeout=30` (clean worker shutdown)

**Impact:** Prevents worker memory accumulation

### 5. Database Connection Middleware (NEW)
**File:** `apps/core/middleware/db_connection_middleware.py`
**Purpose:** Explicitly closes database connections after each request

**Impact:** Ensures connections are released even on errors

### 6. Payment Gateway Connection Cleanup (`payment_gateway.py`)
**Changes:**
- Added `connection.close_if_unusable_or_obsolete()` before external API calls
- Added connection cleanup on API timeout/error

**Impact:** Prevents connection leaks during M-Pesa API timeouts

### 7. Database Health Monitoring Command (NEW)
**File:** `apps/core/management/commands/check_db_connections.py`
**Usage:** `docker exec teralinkx_web python manage.py check_db_connections`

**Shows:**
- Active/idle connections
- Long-running queries
- Connection pool status

---

## Deployment Steps

### Step 1: Backup Current State
```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx
docker-compose exec web python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

### Step 2: Restart Services
```bash
# Restart all containers to apply changes
docker-compose restart

# Or rebuild if needed
docker-compose down
docker-compose up -d --build
```

### Step 3: Verify Changes
```bash
# Check Gunicorn config
docker logs teralinkx_web --tail 20 | grep "Starting Gunicorn"

# Should show:
# Starting Gunicorn with 5 workers on 0.0.0.0:8009
# Worker recycling: max_requests=200, jitter=50
# Timeout: 30s, Keepalive: 5s

# Check database connections
docker exec teralinkx_web python manage.py check_db_connections

# Monitor memory over time
watch -n 60 'docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"'
```

### Step 4: Monitor for 24 Hours
```bash
# Check if restarts are still needed
docker ps --format "table {{.Names}}\t{{.Status}}"

# Monitor logs for connection errors
docker logs teralinkx_web -f | grep -i "connection\|timeout\|error"

# Check PostgreSQL connections
docker exec postgres psql -U teralinkx -d teralinkx -c "SELECT count(*), state FROM pg_stat_activity WHERE datname='teralinkx' GROUP BY state;"
```

---

## Expected Results

### Before Changes:
- Memory: 455MB → 800MB+ over hours
- Connections: Growing, not released
- Restarts needed: Every 2-4 hours

### After Changes:
- Memory: 455MB → stable around 500-550MB
- Connections: Recycled every 60s
- Workers: Recycled every 200 requests
- Restarts needed: None (or only for deployments)

---

## Monitoring Commands

### Check Database Connections
```bash
docker exec teralinkx_web python manage.py check_db_connections
```

### Check Memory Growth
```bash
# Run every 30 minutes
docker stats teralinkx_web --no-stream --format "{{.MemUsage}}"
```

### Check PostgreSQL Connection Count
```bash
docker exec postgres psql -U teralinkx -d teralinkx -c "SELECT count(*) FROM pg_stat_activity WHERE datname='teralinkx';"
```

### Check for Hanging Queries
```bash
docker exec postgres psql -U teralinkx -d teralinkx -c "SELECT pid, now() - query_start as duration, state, query FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '10 seconds';"
```

---

## Rollback Plan (If Issues Occur)

### Quick Rollback
```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx
git checkout HEAD~1 teralinkx/settings.py gunicorn_config.py apps/finance/payment_gateway.py
docker-compose restart
```

### Remove Middleware (if causing issues)
Edit `settings.py` and remove:
```python
'core.middleware.db_connection_middleware.DatabaseConnectionMiddleware',
```

---

## Next Steps (Priority 2 & 3)

After 24 hours of stable operation, implement:

1. **Move M-Pesa API calls to Celery tasks** (prevents worker blocking)
2. **Add notification query caching** (reduces database load)
3. **Implement PgBouncer** (advanced connection pooling)
4. **Add request rate limiting** (prevents abuse)

---

## Troubleshooting

### If memory still grows:
```bash
# Check for memory leaks in specific views
docker exec teralinkx_web python manage.py shell
>>> import gc
>>> gc.collect()
>>> len(gc.get_objects())
```

### If connections still leak:
```bash
# Check PostgreSQL max_connections
docker exec postgres psql -U teralinkx -d teralinkx -c "SHOW max_connections;"

# Increase if needed (default 100)
docker exec postgres psql -U teralinkx -d teralinkx -c "ALTER SYSTEM SET max_connections = 200;"
docker-compose restart db
```

### If workers timeout:
```bash
# Increase timeout temporarily
# Edit gunicorn_config.py: timeout = 60
docker-compose restart web
```
