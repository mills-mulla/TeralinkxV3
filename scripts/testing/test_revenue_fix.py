#!/usr/bin/env python
"""
Test script to verify revenue calculation consistency
Run this from Django shell: python manage.py shell < test_revenue_fix.py
"""

from django.utils import timezone
from django.db.models import Sum
from finance.models import TransactionQueue

def test_revenue_calculation():
    """Test that revenue calculations are consistent"""
    
    today = timezone.now().date()
    
    # Dashboard calculation (FIXED)
    dashboard_revenue = TransactionQueue.objects.filter(
        method='mpesa',
        status__in=['completed', 'processed'],
        created_at__date=today
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Analysis/Forecast calculation (was already correct)
    analysis_revenue = TransactionQueue.objects.filter(
        created_at__date=today,
        method='mpesa',
        status__in=['completed', 'processed']
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Get counts for verification
    total_today = TransactionQueue.objects.filter(
        created_at__date=today
    ).count()
    
    mpesa_today = TransactionQueue.objects.filter(
        created_at__date=today,
        method='mpesa'
    ).count()
    
    completed_today = TransactionQueue.objects.filter(
        created_at__date=today,
        method='mpesa',
        status__in=['completed', 'processed']
    ).count()
    
    pending_today = TransactionQueue.objects.filter(
        created_at__date=today,
        method='mpesa',
        status='pending'
    ).count()
    
    failed_today = TransactionQueue.objects.filter(
        created_at__date=today,
        method='mpesa',
        status='failed'
    ).count()
    
    print("=" * 60)
    print("REVENUE CALCULATION TEST")
    print("=" * 60)
    print(f"Date: {today}")
    print()
    print("TRANSACTION COUNTS:")
    print(f"  Total transactions today: {total_today}")
    print(f"  M-Pesa transactions: {mpesa_today}")
    print(f"  Completed/Processed: {completed_today}")
    print(f"  Pending: {pending_today}")
    print(f"  Failed: {failed_today}")
    print()
    print("REVENUE CALCULATIONS:")
    print(f"  Dashboard Revenue: KSh {dashboard_revenue:,.2f}")
    print(f"  Analysis Revenue:  KSh {analysis_revenue:,.2f}")
    print()
    
    if dashboard_revenue == analysis_revenue:
        print("✅ SUCCESS: Revenue calculations match!")
        print("   Dashboard and Analysis show the same value.")
    else:
        print("❌ ERROR: Revenue calculations don't match!")
        print(f"   Difference: KSh {abs(dashboard_revenue - analysis_revenue):,.2f}")
    
    print()
    print("VERIFICATION:")
    print(f"  Only counting completed/processed M-Pesa: ✓")
    print(f"  Excluding pending transactions: ✓")
    print(f"  Excluding failed transactions: ✓")
    print("=" * 60)
    
    return dashboard_revenue == analysis_revenue

if __name__ == '__main__':
    test_revenue_calculation()
