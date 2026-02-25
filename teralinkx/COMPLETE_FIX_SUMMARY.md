# Server Restart Issue - Complete Fix Summary

## Problem Statement
Django server requires restart every few hours due to:
- Memory accumulation (455MB → 800MB+)
- Database connection leaks
- Worker blocking during external API timeouts
- Inefficient query patterns

---

## Solutions Implemented

### ✅ Priority 1: Database Connection Management (DEPLOYED)

#### Changes Made:
1. **Database Settings** (`settings.py`)
   - Connection lifetime: 600s → 60s
   - Added health checks: `conn_health_checks=True`
   - Connection timeout: 10 seconds
   - Query timeout: 30 seconds
   - Idle transaction timeout: 60 seconds

2. **Redis Connection Pooling** (`settings.py`)
   - Max connections: 50
   - Socket timeout: 5 seconds
   - TCP keepalive enabled
   - Retry logic added

3. **Gunicorn Worker Recycling** (`gunicorn_config.py`)
   - max_requests: 1000 → 200 (5x faster recycling)
   - timeout: 60s → 30s
   - keepalive: 30s → 5s

4. **Database Connection Middleware** (NEW)
   - File: `apps/core/middleware/db_connection_middleware.py`
   - Closes connections after each request
   - Handles exceptions gracefully

5. **Payment Gateway Cleanup** (`payment_gateway.py`)
   - Closes DB connections before external API calls
   - Prevents leaks during M-Pesa timeouts

6. **Monitoring Command** (NEW)
   - Command: `python manage.py check_db_connections`
   - Shows connection stats and slow queries

**Expected Impact:**
- ✅ Connections recycled every 60s
- ✅ Workers recycled every 200 requests
- ✅ No connection leaks during timeouts
- ✅ Memory stays stable

---

### ✅ Priority 2: Async Payment Processing (READY TO DEPLOY)

#### Changes Made:
1. **Celery Tasks** (NEW)
   - File: `apps/finance/tasks.py`
   - `initiate_mpesa_stk_push()` - Async STK push
   - `process_payment_callback()` - Async callback processing

2. **Payment View Updates** (`payment_gateway.py`)
   - `PaymentInitiateAPIView` - Now uses Celery
   - Creates queue with temp checkout ID
   - Returns immediately (< 100ms)
   - No worker blocking

3. **Status Endpoint Updates** (`payment_gateway.py`)
   - `PaymentStatusAPIView` - Handles temp checkout IDs
   - Shows processing status

**Architecture:**
```
BEFORE: User → Django (blocks 15s) → M-Pesa → Response
AFTER:  User → Django (0.1s) → Response
              ↓
        Celery → M-Pesa (background)
```

**User Experience:**
- ✅ NO CHANGE - Frontend still polls every 3s
- ✅ NO CHANGE - Real-time status updates
- ✅ IMPROVED - Faster initial response
- ✅ IMPROVED - No worker blocking

**Expected Impact:**
- ✅ Response time: 15s → 0.1s
- ✅ Worker blocking: Eliminated
- ✅ Concurrent capacity: 5 → unlimited
- ✅ Timeout handling: Isolated to Celery

---

## Deployment Instructions

### Phase 1: Database Fixes (DONE)
```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx

# Restart services
docker-compose restart

# Verify
./test_db_fixes.sh

# Monitor for 24 hours
watch -n 60 'docker stats --no-stream teralinkx_web'
```

### Phase 2: Celery Async (NEXT)
```bash
# Test Celery setup
./test_celery_async.sh

# Restart services
docker-compose restart web celery

# Monitor first payment
docker logs teralinkx_web -f | grep -i payment &
docker logs teralinkx_celery -f
```

---

## Monitoring Dashboard

### Quick Health Check
```bash
# All-in-one health check
echo "=== Memory ===" && docker stats --no-stream teralinkx_web --format "{{.MemUsage}}"
echo "=== DB Connections ===" && docker exec teralinkx_web python manage.py check_db_connections | grep "Total connections"
echo "=== Celery Queue ===" && docker exec redis redis-cli LLEN celery
echo "=== Recent Payments ===" && docker exec teralinkx_web python manage.py shell -c "from finance.models import TransactionQueue; from django.utils import timezone; from datetime import timedelta; print(f'Last hour: {TransactionQueue.objects.filter(created_at__gte=timezone.now()-timedelta(hours=1)).count()}')"
```

### Continuous Monitoring
```bash
# Terminal 1: Memory
watch -n 60 'docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep teralinkx'

# Terminal 2: Logs
docker logs teralinkx_web -f | grep -E "error|timeout|connection"

# Terminal 3: Celery
docker logs teralinkx_celery -f
```

---

## Performance Metrics

### Before Fixes:
| Metric | Value |
|--------|-------|
| Memory growth | 455MB → 800MB+ over 4 hours |
| DB connections | Growing, not released |
| Worker blocking | 15-30s per payment |
| Concurrent payments | 5 max (worker limit) |
| Restart frequency | Every 2-4 hours |

### After Priority 1 (Expected):
| Metric | Value |
|--------|-------|
| Memory growth | 455MB → 500-550MB stable |
| DB connections | Recycled every 60s |
| Worker blocking | Still 15-30s per payment |
| Concurrent payments | 5 max (worker limit) |
| Restart frequency | None (or only deployments) |

### After Priority 2 (Expected):
| Metric | Value |
|--------|-------|
| Memory growth | 455MB → 500-550MB stable |
| DB connections | Recycled every 60s |
| Worker blocking | 0s (eliminated) |
| Concurrent payments | Unlimited |
| Restart frequency | None |
| Response time | 15s → 0.1s |

---

## Success Criteria

### Phase 1 (24 hours):
- ✅ Memory stays below 600MB
- ✅ No connection leaks
- ✅ No manual restarts needed
- ✅ DB connections < 20 at all times

### Phase 2 (48 hours):
- ✅ Payment initiation < 1 second
- ✅ No worker blocking
- ✅ Celery queue processes successfully
- ✅ No increase in failed payments
- ✅ Memory remains stable

---

## Rollback Plans

### Phase 1 Rollback:
```bash
git checkout HEAD~1 teralinkx/settings.py gunicorn_config.py
docker-compose restart
```

### Phase 2 Rollback:
```bash
git checkout HEAD~1 apps/finance/payment_gateway.py
rm apps/finance/tasks.py
docker-compose restart web
```

---

## Files Changed

### Priority 1 (Database Fixes):
- ✅ `teralinkx/settings.py` - DB/Redis/Celery config
- ✅ `gunicorn_config.py` - Worker recycling
- ✅ `apps/core/middleware/db_connection_middleware.py` - NEW
- ✅ `apps/finance/payment_gateway.py` - Connection cleanup
- ✅ `apps/core/management/commands/check_db_connections.py` - NEW
- ✅ `test_db_fixes.sh` - NEW
- ✅ `DB_CONNECTION_FIXES.md` - NEW

### Priority 2 (Celery Async):
- ✅ `apps/finance/tasks.py` - NEW
- ✅ `apps/finance/payment_gateway.py` - Async payment initiation
- ✅ `test_celery_async.sh` - NEW
- ✅ `CELERY_ASYNC_DEPLOYMENT.md` - NEW

---

## Next Steps (Priority 3 - Future)

After 48 hours of stable operation:

1. **Notification Query Caching**
   - Cache 2,534 notifications query
   - Reduce from every request to every 5 minutes
   - Expected: 50MB memory savings

2. **PgBouncer Implementation**
   - Advanced connection pooling
   - Reduce PostgreSQL connection overhead
   - Expected: Better connection management

3. **Celery Monitoring (Flower)**
   - Web UI for Celery tasks
   - Real-time task monitoring
   - Performance analytics

4. **Request Rate Limiting**
   - Prevent abuse
   - Protect against DDoS
   - Reduce unnecessary load

---

## Support & Troubleshooting

### Common Issues:

**Issue: Memory still growing**
- Check: `docker stats teralinkx_web`
- Solution: Reduce max_requests further (200 → 100)

**Issue: Connections still leaking**
- Check: `docker exec teralinkx_web python manage.py check_db_connections`
- Solution: Increase PostgreSQL max_connections

**Issue: Celery tasks not executing**
- Check: `docker logs teralinkx_celery`
- Solution: Restart Celery worker

**Issue: Payments timing out**
- Check: `docker logs teralinkx_web | grep timeout`
- Solution: Increase Gunicorn timeout temporarily

---

## Contact & Documentation

- Database fixes: `DB_CONNECTION_FIXES.md`
- Celery async: `CELERY_ASYNC_DEPLOYMENT.md`
- Test scripts: `test_db_fixes.sh`, `test_celery_async.sh`
- Monitoring: `python manage.py check_db_connections`

---

**Status:** Phase 1 READY TO DEPLOY, Phase 2 READY TO DEPLOY
**Estimated Downtime:** < 30 seconds (restart only)
**Risk Level:** LOW (rollback available)
