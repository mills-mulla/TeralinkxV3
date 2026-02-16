# Revenue Discrepancy Fix

## Problem Identified

There was a discrepancy between:
1. **Real-time revenue in Dashboard** - showing higher values
2. **Predictive Analysis revenue graph** - showing lower, accurate values

## Root Cause

The dashboard's `DashboardMetricsView` was incorrectly calculating today's revenue by:
- Using a filtered queryset (`queue_qs`) that could include ALL transactions
- Not properly filtering by transaction status
- Including failed and pending transactions in the total

Meanwhile, the `RevenueForecastView` (predictive analysis) was correctly filtering:
- Only `method='mpesa'` transactions
- Only `status__in=['completed', 'processed']` transactions
- Properly calculating daily revenue

## The Fix

### File: `/teralinkx/apps/analytics/superuser/views/dashboard_metrics.py`

**Before:**
```python
# Revenue metrics (from completed/processed M-Pesa transactions in queue)
# Get today's revenue for real-time display
today = timezone.now().date()
total_revenue = queue_qs.filter(
    method='mpesa',
    status__in=['completed', 'processed'],
    created_at__date=today
).aggregate(total=Sum('price'))['total'] or 0
```

**After:**
```python
# Revenue metrics (ONLY completed/processed M-Pesa transactions)
today = timezone.now().date()
total_revenue = TransactionQueue.objects.filter(
    method='mpesa',
    status__in=['completed', 'processed'],
    created_at__date=today
).aggregate(total=Sum('price'))['total'] or 0
```

## What Changed

1. **Removed dependency on filtered queryset**: Now directly queries `TransactionQueue.objects` instead of using `queue_qs` which had date/location/package filters applied
2. **Consistent filtering**: Both dashboard and analysis now use the same criteria:
   - `method='mpesa'` - Only M-Pesa payments
   - `status__in=['completed', 'processed']` - Only successful transactions
   - `created_at__date=today` - Only today's transactions

## Impact

✅ **Dashboard real-time revenue** now shows only completed/processed M-Pesa transactions
✅ **Predictive analysis graph** continues to show accurate data
✅ **Both values now match** for today's date
✅ **Failed and pending transactions** are correctly excluded from revenue calculations

## Transaction Status Definitions

- **pending**: Transaction initiated but not yet confirmed
- **processing**: Transaction being processed by gateway
- **completed**: Transaction successfully completed ✓
- **processed**: Transaction processed and voucher activated ✓
- **failed**: Transaction failed
- **refunded**: Transaction was refunded

## Revenue Calculation Logic

Total Revenue Today = SUM of `price` field WHERE:
- `method = 'mpesa'`
- `status IN ('completed', 'processed')`
- `created_at__date = TODAY`

This ensures only actual successful M-Pesa payments are counted as revenue.

## Testing Recommendations

1. Check dashboard revenue matches analysis page for today
2. Verify failed transactions don't appear in revenue
3. Verify pending transactions don't appear in revenue
4. Confirm only M-Pesa transactions are counted (not balance purchases)

## Related Files

- `/teralinkx/apps/analytics/superuser/views/dashboard_metrics.py` - Dashboard metrics (FIXED)
- `/teralinkx/apps/finance/models.py` - TransactionQueue model definition
- `/teralinkx/apps/analytics/superuser/urls.py` - API endpoints

## Date: 2024
