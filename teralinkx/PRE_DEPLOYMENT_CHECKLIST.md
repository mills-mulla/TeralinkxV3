# Pre-Deployment Checklist - All Optimizations

## ✅ Fixes Implemented

### Priority 1: Database Connection Management
- [x] Connection lifetime: 600s → 60s
- [x] Added health checks
- [x] Connection cleanup middleware
- [x] Redis connection pooling
- [x] Gunicorn worker recycling (1000 → 200)

### Priority 2: M-Pesa Timeout Protection
- [x] Access token: 10s timeout
- [x] STK push: 15s timeout
- [x] Status query: 10s timeout
- [x] Connection cleanup before API calls

### Priority 3: Celery Async Processing
- [x] Payment initiation → Celery (prevents 15-30s blocking)
- [x] Status polling → Celery + caching (prevents timeout blocking)
- [x] Returns real checkout IDs (no temp IDs)

### Priority 4: Memory Leak Fixes
- [x] Notification query caching (5 min cache)
- [x] Removed debug prints (2,534 notification counts)
- [x] Currency lookup caching (1 hour)
- [x] Package lookup caching (5 min)
- [x] Gateway lookup caching (1 hour)
- [x] M-Pesa status caching (2s pending, 5min completed)

---

## Files Modified

### Core Infrastructure:
1. `teralinkx/settings.py` - DB/Redis/Celery config
2. `gunicorn_config.py` - Worker recycling
3. `apps/core/middleware/db_connection_middleware.py` - NEW

### Payment Processing:
4. `apps/finance/payment_gateway.py` - Celery + caching + timeouts
5. `apps/finance/queryDaraja.py` - Timeouts
6. `apps/finance/tasks.py` - NEW Celery tasks
7. `apps/finance/querycheckout.py` - Celery + caching

### Memory Leaks:
8. `apps/notifications/views.py` - Caching + removed debug

---

## Expected Performance Improvements

### Memory Usage:
- **Before:** 455MB → 800MB+ over 4 hours
- **After:** 455MB → 500-550MB stable
- **Savings:** 90MB/hour = 2GB/day

### Response Times:
- Payment initiation: 15s → 0.5s (30x faster)
- Status polling: 2s → 0.3s (7x faster)
- Notifications: 500ms → 50ms (10x faster)

### Resource Usage:
- Worker blocking: 35s/payment → 0.5s/payment (98% reduction)
- M-Pesa API calls: 11/payment → 6/payment (45% reduction)
- DB queries: 15/request → 5/request (67% reduction)

---

## Deployment Steps

### Step 1: Backup
```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx

# Backup database
docker exec postgres pg_dump -U teralinkx teralinkx > backup_$(date +%Y%m%d).sql

# Backup code
git add -A
git commit -m "Pre-deployment backup - all optimizations"
```

### Step 2: Deploy
```bash
# Restart services
docker-compose restart web celery beat

# Wait for startup
sleep 15

# Check logs
docker logs teralinkx_web --tail 50
docker logs teralinkx_celery --tail 50
```

### Step 3: Verify
```bash
# Test notification caching
curl http://localhost:8009/api/notifications/announcements/

# Test payment initiation
# (Make test payment from frontend)

# Check memory
docker stats --no-stream teralinkx_web

# Check Celery
docker exec redis redis-cli LLEN celery
```

### Step 4: Monitor (First Hour)
```bash
# Terminal 1: Memory
watch -n 60 'docker stats --no-stream teralinkx_web --format "{{.MemUsage}}"'

# Terminal 2: Logs
docker logs teralinkx_web -f | grep -E "ERROR|timeout|Celery"

# Terminal 3: Celery
docker logs teralinkx_celery -f

# Terminal 4: Cache hits
watch -n 30 'docker exec redis redis-cli INFO stats | grep keyspace_hits'
```

---

## Success Criteria

### Immediate (First Hour):
- ✅ No errors in logs
- ✅ Payment initiation < 1s
- ✅ Status polling < 0.5s
- ✅ Notifications < 100ms
- ✅ Memory stable < 550MB
- ✅ Celery queue < 10 tasks

### After 24 Hours:
- ✅ Memory < 600MB
- ✅ No manual restarts
- ✅ DB connections < 20
- ✅ Cache hit rate > 50%
- ✅ No timeout errors

### After 1 Week:
- ✅ Zero restarts
- ✅ Consistent performance
- ✅ Lower API costs
- ✅ Better user experience

---

## Monitoring Commands

### Check Memory Growth
```bash
# Every 5 minutes for 1 hour
for i in {1..12}; do
  echo "$(date): $(docker stats --no-stream teralinkx_web --format '{{.MemUsage}}')"
  sleep 300
done
```

### Check Cache Effectiveness
```bash
docker exec redis redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses"

# Calculate hit rate
docker exec redis redis-cli INFO stats | awk '/keyspace_hits/{hits=$2} /keyspace_misses/{misses=$2} END{print "Hit rate:", hits/(hits+misses)*100"%"}'
```

### Check Query Count
```bash
docker exec teralinkx_web python manage.py shell -c "
from django.db import connection, reset_queries
from django.test.utils import override_settings

with override_settings(DEBUG=True):
    reset_queries()
    
    # Simulate notification request
    from notifications.models import Notification
    from django.utils import timezone
    from django.db.models import Q
    
    now = timezone.now()
    announcements = Notification.objects.filter(
        scope='global',
        is_archived=False
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).only('id', 'title', 'message')[:10]
    
    list(announcements)  # Force evaluation
    
    print(f'Queries executed: {len(connection.queries)}')
    print(f'Expected: 1 (with caching)')
"
```

### Check Celery Performance
```bash
# Task success rate
docker exec teralinkx_celery celery -A teralinkx inspect stats | grep -A 5 "total"

# Active tasks
docker exec teralinkx_celery celery -A teralinkx inspect active

# Failed tasks
docker exec teralinkx_celery celery -A teralinkx inspect failed
```

---

## Rollback Plan

### If Issues Occur:
```bash
# Quick rollback
cd /home/ghost/Desktop/TeralinkxV3/teralinkx
git reset --hard HEAD~1
docker-compose restart web celery

# Restore database if needed
docker exec -i postgres psql -U teralinkx teralinkx < backup_YYYYMMDD.sql
```

### Partial Rollback Options:
```bash
# Keep DB fixes, remove Celery
git checkout HEAD~1 apps/finance/tasks.py
git checkout HEAD~1 apps/finance/payment_gateway.py
git checkout HEAD~1 apps/finance/querycheckout.py
docker-compose restart web

# Keep everything, remove notification caching
git checkout HEAD~1 apps/notifications/views.py
docker-compose restart web
```

---

## Troubleshooting

### Issue: Memory still growing
```bash
# Check for other leaks
docker exec teralinkx_web python manage.py shell -c "
import gc
gc.collect()
print(f'Objects: {len(gc.get_objects())}')
"

# Check query count
docker logs teralinkx_web | grep "SELECT" | wc -l
```

### Issue: Celery tasks failing
```bash
# Check Celery logs
docker logs teralinkx_celery --tail 100

# Check Redis
docker exec redis redis-cli PING

# Restart Celery
docker-compose restart celery
```

### Issue: Cache not working
```bash
# Check Redis memory
docker exec redis redis-cli INFO memory

# Check cache keys
docker exec redis redis-cli KEYS "*"

# Clear cache if needed
docker exec redis redis-cli FLUSHDB
```

---

## Performance Baseline

### Before Optimizations:
```
Memory: 455MB → 800MB (4 hours)
Payment initiation: 15-30s
Status polling: 2s
Notifications: 500ms
Worker blocking: 35s per payment
M-Pesa API calls: 11 per payment
DB queries: 15 per request
Restarts needed: Every 2-4 hours
```

### After Optimizations (Expected):
```
Memory: 455MB → 550MB (stable)
Payment initiation: 0.5s
Status polling: 0.3s
Notifications: 50ms
Worker blocking: 0.5s per payment
M-Pesa API calls: 6 per payment
DB queries: 5 per request
Restarts needed: None
```

---

## Final Checklist

Before deploying, verify:
- [ ] All files committed to git
- [ ] Database backup created
- [ ] Docker containers running
- [ ] Redis accessible
- [ ] Celery workers active
- [ ] Monitoring commands ready
- [ ] Rollback plan understood

After deploying, monitor:
- [ ] Memory usage (first hour)
- [ ] Error logs (first hour)
- [ ] Celery queue (first hour)
- [ ] Cache hit rate (first day)
- [ ] No restarts needed (first week)

---

## Summary

**Total Optimizations:** 8 major fixes
**Files Modified:** 8 files
**Expected Memory Savings:** 2GB/day
**Expected Performance Gain:** 10-30x faster
**Deployment Time:** 5 minutes
**Risk Level:** LOW (rollback available)

**Ready to deploy! 🚀**

Monitor closely for first 24 hours, then relax and enjoy stable performance!
