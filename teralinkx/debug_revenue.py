#!/usr/bin/env python
"""
Debug script to check revenue calculations
Run: python manage.py shell < debug_revenue.py
"""

from django.utils import timezone
from django.db.models import Sum
from finance.models import TransactionQueue
from datetime import timedelta

print("=" * 80)
print("REVENUE DEBUG SCRIPT")
print("=" * 80)

today = timezone.now().date()
print(f"\nToday's date: {today}")
print(f"Timezone: {timezone.get_current_timezone()}")

# Check all transactions today
all_today = TransactionQueue.objects.filter(created_at__date=today)
print(f"\n1. ALL transactions today: {all_today.count()}")

# Check M-Pesa only
mpesa_today = TransactionQueue.objects.filter(
    created_at__date=today,
    method='mpesa'
)
print(f"2. M-Pesa transactions today: {mpesa_today.count()}")

# Check completed/processed
completed_today = TransactionQueue.objects.filter(
    created_at__date=today,
    method='mpesa',
    status__in=['completed', 'processed']
)
print(f"3. Completed/Processed M-Pesa today: {completed_today.count()}")

# Show status breakdown
print("\n--- Status Breakdown (M-Pesa only) ---")
for status in ['pending', 'processing', 'completed', 'processed', 'failed']:
    count = TransactionQueue.objects.filter(
        created_at__date=today,
        method='mpesa',
        status=status
    ).count()
    if count > 0:
        print(f"  {status}: {count}")

# Calculate revenue using dashboard method
dashboard_qs = TransactionQueue.objects.filter(
    created_at__date=today,
    method='mpesa',
    status__in=['completed', 'processed']
)
dashboard_revenue = dashboard_qs.aggregate(total=Sum('price'))['total'] or 0

print(f"\n--- DASHBOARD CALCULATION ---")
print(f"Query: created_at__date={today}, method='mpesa', status__in=['completed', 'processed']")
print(f"Count: {dashboard_qs.count()}")
print(f"Revenue: KSh {dashboard_revenue:,.2f}")

# Show individual transactions
print("\n--- Individual Transactions (Completed/Processed) ---")
for txn in dashboard_qs[:10]:
    print(f"  ID: {txn.id} | User: {txn.initiator} | Price: KSh {txn.price} | Status: {txn.status} | Time: {txn.created_at}")

# Calculate revenue using analytics method (from RevenueAnalyticsView)
analytics_qs = TransactionQueue.objects.filter(
    created_at__date=today,
    method='mpesa',
    status__in=['completed', 'processed']
)
analytics_revenue = analytics_qs.aggregate(total=Sum('price'))['total'] or 0

print(f"\n--- ANALYTICS CALCULATION ---")
print(f"Query: created_at__date={today}, method='mpesa', status__in=['completed', 'processed']")
print(f"Count: {analytics_qs.count()}")
print(f"Revenue: KSh {analytics_revenue:,.2f}")

# Check if they match
print(f"\n--- COMPARISON ---")
if dashboard_revenue == analytics_revenue:
    print(f"✅ MATCH! Both show: KSh {dashboard_revenue:,.2f}")
else:
    print(f"❌ MISMATCH!")
    print(f"   Dashboard: KSh {dashboard_revenue:,.2f}")
    print(f"   Analytics: KSh {analytics_revenue:,.2f}")
    print(f"   Difference: KSh {abs(dashboard_revenue - analytics_revenue):,.2f}")

# Check for transactions with wrong status values
print(f"\n--- CHECKING FOR DATA ISSUES ---")
weird_status = TransactionQueue.objects.filter(
    created_at__date=today,
    method='mpesa'
).exclude(
    status__in=['pending', 'processing', 'completed', 'processed', 'failed', 'refunded']
)
if weird_status.exists():
    print(f"⚠️  Found {weird_status.count()} transactions with unusual status values:")
    for txn in weird_status[:5]:
        print(f"   ID: {txn.id} | Status: '{txn.status}'")
else:
    print("✅ All transactions have valid status values")

print("\n" + "=" * 80)
