#!/bin/bash
# Test script for Celery async payment processing

echo "=========================================="
echo "Celery Async Payment Processing Test"
echo "=========================================="
echo ""

echo "1. Checking Celery containers..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "celery|beat"
echo ""

echo "2. Testing Celery task import..."
docker exec teralinkx_web python manage.py shell -c "
try:
    from finance.tasks import initiate_mpesa_stk_push, process_payment_callback
    print('✓ Tasks imported successfully')
    print('  - initiate_mpesa_stk_push')
    print('  - process_payment_callback')
except Exception as e:
    print(f'✗ Error importing tasks: {e}')
" 2>&1
echo ""

echo "3. Checking Celery worker status..."
docker exec teralinkx_celery celery -A teralinkx inspect ping 2>&1 | head -5
echo ""

echo "4. Checking Celery queue length..."
QUEUE_LEN=$(docker exec redis redis-cli LLEN celery 2>/dev/null)
echo "Tasks in queue: $QUEUE_LEN"
echo ""

echo "5. Checking recent payment queue items..."
docker exec teralinkx_web python manage.py shell -c "
from finance.models import TransactionQueue
from django.utils import timezone
from datetime import timedelta

recent = TransactionQueue.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
).order_by('-created_at')[:5]

print(f'Recent payments (last hour): {recent.count()}')
for item in recent:
    status_icon = '✓' if item.status == 'completed' else '⏳' if item.status == 'pending' else '✗'
    print(f'{status_icon} {item.checkout_request_id[:20]}: {item.status} - {item.package}')
" 2>&1
echo ""

echo "6. Checking for stuck temp checkout IDs..."
docker exec teralinkx_web python manage.py shell -c "
from finance.models import TransactionQueue
from django.utils import timezone
from datetime import timedelta

stuck = TransactionQueue.objects.filter(
    checkout_request_id__startswith='TEMP_',
    created_at__lt=timezone.now() - timedelta(minutes=5)
)
if stuck.exists():
    print(f'⚠ Warning: {stuck.count()} stuck temp checkout IDs')
    for item in stuck[:3]:
        print(f'  - {item.checkout_request_id}: {item.status} ({item.created_at})')
else:
    print('✓ No stuck temp checkout IDs')
" 2>&1
echo ""

echo "7. Checking Celery worker stats..."
docker exec teralinkx_celery celery -A teralinkx inspect stats 2>&1 | grep -E "total|pool" | head -10
echo ""

echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test a payment: curl -X POST http://localhost:8009/api/payment/initiate/"
echo "2. Monitor Celery: docker logs teralinkx_celery -f"
echo "3. Monitor web: docker logs teralinkx_web -f"
echo "4. Check queue: watch -n 2 'docker exec redis redis-cli LLEN celery'"
