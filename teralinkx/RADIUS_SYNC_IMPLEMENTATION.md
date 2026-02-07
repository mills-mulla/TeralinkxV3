# RADIUS Usage Sync Implementation

## Overview
Automatic synchronization of voucher usage data from FreeRADIUS to V3 DispatchVoucher model.

## Architecture

```
MikroTik → FreeRADIUS → radacct table
                            ↓
                      Radius API (REST)
                            ↓
                    V3 Celery Tasks (PULL)
                            ↓
                  DispatchVoucher model
```

## Components Created

### 1. Radius API Endpoints
- **Single**: `GET /api/vouchers/usage/?username={voucher_code}`
- **Batch**: `POST /api/vouchers/usage/batch/` (max 100 vouchers)

### 2. V3 Sync Service
**File**: `apps/sync/radius_sync.py`
- `RadiusUsageSyncService.sync_single_voucher()` - Sync one voucher
- `RadiusUsageSyncService.sync_batch_vouchers()` - Sync up to 100 vouchers
- `RadiusUsageSyncService.sync_active_vouchers()` - Sync all active vouchers
- `RadiusUsageSyncService.sync_critical_vouchers()` - Sync vouchers >80% data used

### 3. Celery Tasks
**File**: `apps/sync/tasks.py`
- `sync_radius_usage_all` - Runs every 5 minutes (all active vouchers)
- `sync_radius_usage_critical` - Runs every 2 minutes (critical vouchers)

### 4. Management Commands
**Test Sync**:
```bash
python manage.py test_radius_sync                    # Sync all active
python manage.py test_radius_sync --critical         # Sync critical only
python manage.py test_radius_sync --voucher CODE     # Sync specific voucher
```

**Setup Schedules**:
```bash
python manage.py setup_radius_sync
```

## Configuration

### Settings Added
```python
# teralinkx/settings.py
RADIUS_API_URL = 'http://localhost:8010/api'
```

## Sync Strategy

### Tier 1: Background Sync (Automated)
- **All Active Vouchers**: Every 5 minutes
- **Critical Vouchers** (>80% data used): Every 2 minutes

### Tier 2: On-Demand (Manual)
- Via management command
- Via admin action (future)

## Data Synced

For each voucher, the following fields are updated:
- `download_bytes` - Total bytes downloaded across all sessions
- `upload_bytes` - Total bytes uploaded across all sessions
- `session_count` - Total number of sessions (completed + active)
- `concurrent_sessions` - Currently active sessions
- `status` - Auto-updated if data exhausted

## Setup Instructions

### 1. Start Radius API (if not running)
```bash
cd /home/teralinkx/TeralinkxV3/radius_api
gunicorn --bind 0.0.0.0:8010 radius_api.wsgi:application
```

### 2. Setup Celery Beat Schedules
```bash
cd /home/teralinkx/TeralinkxV3/teralinkx
python manage.py setup_radius_sync
```

### 3. Restart Celery Beat
```bash
# Stop existing beat
pkill -f celery

# Start beat
celery -A teralinkx beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

# Start worker
celery -A teralinkx worker -l info &
```

### 4. Test Manual Sync
```bash
python manage.py test_radius_sync --voucher BAL-YCUL008YBKV55
```

## Monitoring

### Check Celery Tasks
```bash
# View scheduled tasks
python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.filter(name__contains='RADIUS').values('name', 'enabled', 'last_run_at')
```

### Check Sync Logs
```bash
# Celery logs
tail -f /var/log/celery/worker.log

# Django logs
tail -f /var/log/django/app.log
```

### Verify Sync Working
```bash
# Check voucher usage in database
python manage.py shell
>>> from packages.models import DispatchVoucher
>>> v = DispatchVoucher.objects.get(voucher_code='BAL-YCUL008YBKV55')
>>> print(f"Downloaded: {v.download_bytes / 1024 / 1024:.2f} MB")
>>> print(f"Uploaded: {v.upload_bytes / 1024 / 1024:.2f} MB")
>>> print(f"Sessions: {v.session_count}")
```

## Performance

- **Batch Size**: 100 vouchers per API call
- **Sync Time**: ~2-5 seconds per 100 vouchers
- **Database Impact**: Minimal (bulk updates with specific fields)
- **API Load**: 1 request per 100 vouchers

## Troubleshooting

### Sync Not Working
1. Check Radius API is running: `curl http://localhost:8010/api/vouchers/usage/?username=TEST`
2. Check Celery beat is running: `ps aux | grep celery`
3. Check task is enabled: `python manage.py shell` → Check PeriodicTask
4. Check logs for errors

### Data Not Updating
1. Verify FreeRADIUS is receiving accounting packets
2. Check radacct table has data: `docker exec postgres psql -U radius -d radius -c "SELECT * FROM radacct LIMIT 5;"`
3. Run manual sync to test: `python manage.py test_radius_sync --voucher CODE`

### High API Load
- Increase sync interval (5 min → 10 min)
- Reduce batch size in `radius_sync.py`
- Add caching layer

## Future Enhancements

1. **Real-time Sync** - Webhook from FreeRADIUS on Stop packets
2. **Admin Actions** - "Sync Usage" button in Django admin
3. **Usage Alerts** - Notify users at 80%, 90%, 95% data usage
4. **Analytics Dashboard** - Real-time usage graphs
5. **API Caching** - Redis cache for frequently accessed vouchers
