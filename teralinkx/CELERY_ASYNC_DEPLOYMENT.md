# Celery Async Payment Processing - Deployment Guide

## What Changed (Priority 2 - Hybrid Approach)

### Architecture Change
**Before:** Django worker blocks for 10-30s during M-Pesa API calls
**After:** Django returns immediately, Celery handles M-Pesa API calls

### User Experience
- ✅ **NO CHANGE** - Frontend still polls every 3 seconds
- ✅ **NO CHANGE** - Payment status updates in real-time
- ✅ **IMPROVED** - Faster initial response (< 100ms vs 15s)
- ✅ **IMPROVED** - No worker blocking during timeouts

---

## Files Modified

### 1. New File: `apps/finance/tasks.py`
**Purpose:** Celery tasks for async M-Pesa processing

**Tasks:**
- `initiate_mpesa_stk_push(queue_item_id)` - Handles STK push async
- `process_payment_callback(callback_data)` - Optional callback processing

### 2. Modified: `apps/finance/payment_gateway.py`
**Changes:**
- `PaymentInitiateAPIView.post()` - Now uses Celery task
- Creates queue with temp checkout ID
- Returns immediately (no blocking)
- `PaymentStatusAPIView.get()` - Handles temp checkout IDs

---

## How It Works

### Payment Flow (Hybrid)

```
1. User clicks "Pay"
   ↓
2. Django View (< 100ms)
   - Validates request
   - Creates queue with TEMP_xxxxx checkout ID
   - Sends to Celery: initiate_mpesa_stk_push.delay(queue_id)
   - Returns immediately with temp checkout ID
   ↓
3. Frontend starts polling (same as before)
   - GET /api/payment-status/TEMP_xxxxx/
   - Every 3 seconds
   ↓
4. Celery Worker (parallel, in background)
   - Calls M-Pesa API (blocks Celery worker, not web worker)
   - Updates queue with real checkout ID
   - Updates status to 'pending'
   ↓
5. M-Pesa sends callback (same as before)
   - Updates payment status
   - Creates voucher
   ↓
6. Frontend poll detects completion
   - Shows success message
```

---

## Deployment Steps

### Step 1: Verify Celery is Running
```bash
# Check Celery worker status
docker ps | grep celery

# Should show:
# teralinkx_celery
# teralinkx_beat
```

### Step 2: Test Celery Tasks
```bash
# Enter Django shell
docker exec -it teralinkx_web python manage.py shell

# Test task import
>>> from finance.tasks import initiate_mpesa_stk_push
>>> print("Tasks imported successfully")
```

### Step 3: Restart Services
```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx

# Restart web and celery
docker-compose restart web celery

# Check logs
docker logs teralinkx_web --tail 50
docker logs teralinkx_celery --tail 50
```

### Step 4: Monitor First Payment
```bash
# Terminal 1: Watch web logs
docker logs teralinkx_web -f | grep -i "payment\|celery"

# Terminal 2: Watch Celery logs
docker logs teralinkx_celery -f

# Terminal 3: Monitor queue
watch -n 2 'docker exec redis redis-cli LLEN celery'
```

---

## Testing Checklist

### Test 1: Normal Payment
1. Initiate payment from frontend
2. Check response time (should be < 1 second)
3. Verify temp checkout ID returned (starts with TEMP_)
4. Check Celery logs for task execution
5. Verify payment completes normally
6. Confirm voucher is created

**Expected Timeline:**
- T+0s: User clicks pay
- T+0.1s: Frontend receives temp checkout ID
- T+0.1s: Frontend starts polling
- T+15s: M-Pesa callback received
- T+15s: Frontend shows success

### Test 2: M-Pesa Timeout
1. Initiate payment during M-Pesa downtime
2. Verify Django returns immediately
3. Check Celery handles timeout gracefully
4. Verify queue marked as failed
5. Confirm user sees error message

### Test 3: Concurrent Payments
1. Initiate 5 payments simultaneously
2. Verify all return immediately
3. Check all are processed by Celery
4. Confirm no worker blocking

---

## Monitoring Commands

### Check Celery Queue Length
```bash
docker exec redis redis-cli LLEN celery
```

### Check Active Celery Tasks
```bash
docker exec teralinkx_celery celery -A teralinkx inspect active
```

### Check Failed Tasks
```bash
docker exec teralinkx_celery celery -A teralinkx inspect failed
```

### Check Task Stats
```bash
docker exec teralinkx_celery celery -A teralinkx inspect stats
```

### Monitor Payment Queue
```bash
docker exec teralinkx_web python manage.py shell -c "
from finance.models import TransactionQueue
from django.utils import timezone
from datetime import timedelta

recent = TransactionQueue.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
)
print(f'Total: {recent.count()}')
print(f'Pending: {recent.filter(status=\"pending\").count()}')
print(f'Completed: {recent.filter(status=\"completed\").count()}')
print(f'Failed: {recent.filter(status=\"failed\").count()}')
"
```

---

## Expected Results

### Before (Blocking):
```
Request → [Django blocks 15s] → Response
Worker: BLOCKED for 15s
Throughput: 5 workers = 5 concurrent payments max
```

### After (Async):
```
Request → [Django 0.1s] → Response
Worker: FREE immediately
Celery: Handles API call in background
Throughput: Unlimited concurrent payments
```

### Performance Metrics:
- Initial response time: 15s → 0.1s (150x faster)
- Worker blocking: 15s → 0s (eliminated)
- Concurrent capacity: 5 → unlimited
- Memory leaks: Reduced (workers don't block)

---

## Troubleshooting

### Issue: Tasks not executing
```bash
# Check Celery worker is running
docker ps | grep celery

# Check Celery logs
docker logs teralinkx_celery --tail 100

# Restart Celery
docker-compose restart celery
```

### Issue: Tasks stuck in queue
```bash
# Check queue length
docker exec redis redis-cli LLEN celery

# Purge queue (CAUTION: only in emergency)
docker exec teralinkx_celery celery -A teralinkx purge
```

### Issue: Temp checkout IDs not updating
```bash
# Check Celery task logs
docker logs teralinkx_celery -f | grep "STK push"

# Check queue items
docker exec teralinkx_web python manage.py shell -c "
from finance.models import TransactionQueue
temp_items = TransactionQueue.objects.filter(checkout_request_id__startswith='TEMP_')
print(f'Temp items: {temp_items.count()}')
for item in temp_items[:5]:
    print(f'{item.id}: {item.status} - {item.created_at}')
"
```

### Issue: Frontend shows "processing" forever
**Cause:** Celery task failed but queue not updated

**Fix:**
```bash
# Find stuck items
docker exec teralinkx_web python manage.py shell -c "
from finance.models import TransactionQueue
from django.utils import timezone
from datetime import timedelta

stuck = TransactionQueue.objects.filter(
    status='pending',
    checkout_request_id__startswith='TEMP_',
    created_at__lt=timezone.now() - timedelta(minutes=5)
)
print(f'Stuck items: {stuck.count()}')
for item in stuck:
    item.mark_failed('Timeout - task did not complete', 'TASK_TIMEOUT', 'system_error')
    print(f'Marked {item.id} as failed')
"
```

---

## Rollback Plan

### Quick Rollback (if issues)
```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx

# Revert payment_gateway.py
git checkout HEAD~1 apps/finance/payment_gateway.py

# Remove tasks.py
rm apps/finance/tasks.py

# Restart
docker-compose restart web
```

---

## Next Steps (Priority 3)

After 24 hours of stable operation:

1. **Add notification query caching** (reduces DB load)
2. **Implement PgBouncer** (advanced connection pooling)
3. **Add Celery monitoring dashboard** (Flower)
4. **Optimize Celery worker count** (based on load)

---

## Success Criteria

✅ Payment initiation responds in < 1 second
✅ No Django worker blocking during M-Pesa calls
✅ Celery queue processes tasks successfully
✅ Frontend polling works unchanged
✅ Payment completion time unchanged
✅ No increase in failed payments
✅ Memory usage remains stable
✅ No restarts needed for 48+ hours
