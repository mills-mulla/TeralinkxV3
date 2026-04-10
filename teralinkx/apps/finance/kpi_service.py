# apps/finance/kpi_service.py
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import timedelta
from decimal import Decimal
import time


class KPICalculationService:
    """Service for calculating KPI metrics"""
    
    @staticmethod
    def calculate_mrr():
        """Calculate MRR — uses daily_revenue aggregate if available, falls back to raw query"""
        from django.db import connection
        from django.utils import timezone
        
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Try fast aggregate first
        try:
            with connection.cursor() as c:
                c.execute("""
                    SELECT COALESCE(SUM(total_revenue), 0)
                    FROM daily_revenue
                    WHERE day >= %s
                """, [current_month])
                result = c.fetchone()[0]
                if result is not None:
                    return Decimal(str(result))
        except Exception:
            pass
        
        # Fallback to raw query
        from .models import TransactionQueue
        mrr = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__gte=current_month
        ).aggregate(total=Sum('price'))['total'] or 0
        return Decimal(str(mrr))
    
    @staticmethod
    def calculate_mrr_last_month():
        """Calculate MRR for last month"""
        from .models import TransactionQueue
        
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        mrr = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__gte=last_month,
            created_at__lt=current_month
        ).aggregate(total=Sum('price'))['total'] or 0
        
        return Decimal(str(mrr))
    
    @staticmethod
    def get_mrr_target():
        """Get MRR target (configurable, default 10% growth)"""
        last_month_mrr = KPICalculationService.calculate_mrr_last_month()
        return last_month_mrr * Decimal('1.10')  # 10% growth target
    
    @staticmethod
    def calculate_active_customers():
        """Count active customers"""
        from users.models import ClientH
        
        return ClientH.objects.filter(
            Q(status='active') | Q(status__isnull=True)
        ).count()
    
    @staticmethod
    def calculate_active_customers_last_month():
        """Count active customers from last month"""
        from users.models import ClientH
        
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return ClientH.objects.filter(
            Q(status='active') | Q(status__isnull=True),
            created_at__lt=current_month
        ).count()
    
    @staticmethod
    def calculate_churn_rate(days=30):
        """Calculate churn rate for specified period"""
        from users.models import ClientH
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        total_customers = ClientH.objects.filter(created_at__lt=cutoff_date).count()
        if total_customers == 0:
            return 0.0
        
        churned_customers = ClientH.objects.filter(
            created_at__lt=cutoff_date,
            status='inactive'
        ).count()
        
        return (churned_customers / total_customers) * 100
    
    @staticmethod
    def calculate_new_customers(days=30):
        """Count new customers in last N days"""
        from users.models import ClientH
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return ClientH.objects.filter(created_at__gte=cutoff_date).count()
    
    @staticmethod
    def get_cash_position():
        """Calculate current cash position"""
        from .models import PaymentTransaction, Expense
        
        # Total revenue
        total_revenue = PaymentTransaction.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount_base'))['total'] or 0
        
        # Total expenses
        total_expenses = Expense.objects.filter(
            approval_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Decimal(str(total_revenue)) - Decimal(str(total_expenses))
    
    @staticmethod
    def get_cash_position_30d_ago():
        """Calculate cash position 30 days ago"""
        from .models import PaymentTransaction, Expense
        
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Revenue up to 30 days ago
        total_revenue = PaymentTransaction.objects.filter(
            status='completed',
            created_at__lt=cutoff_date
        ).aggregate(total=Sum('amount_base'))['total'] or 0
        
        # Expenses up to 30 days ago
        total_expenses = Expense.objects.filter(
            approval_status='paid',
            expense_date__lt=cutoff_date.date()
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Decimal(str(total_revenue)) - Decimal(str(total_expenses))
    
    @staticmethod
    def get_outstanding_receivables():
        """Calculate outstanding receivables by aging buckets"""
        from .models import TransactionQueue
        
        now = timezone.now()
        
        # Pending transactions (receivables)
        pending = TransactionQueue.objects.filter(status='pending')
        
        buckets = {
            'current': 0,  # 0-30 days
            '30_60': 0,
            '60_90': 0,
            'over_90': 0
        }
        
        for txn in pending:
            age_days = (now - txn.created_at).days
            
            if age_days <= 30:
                buckets['current'] += float(txn.price)
            elif age_days <= 60:
                buckets['30_60'] += float(txn.price)
            elif age_days <= 90:
                buckets['60_90'] += float(txn.price)
            else:
                buckets['over_90'] += float(txn.price)
        
        return buckets
    
    @staticmethod
    def calculate_network_uptime(days=7):
        """Calculate network uptime percentage (placeholder - needs HIDS data)"""
        # TODO: Integrate with HIDS when available
        # For now, return high uptime as placeholder
        return 99.5
    
    @staticmethod
    def get_revenue_at_risk():
        """Get total revenue at risk from churn predictions"""
        from .models_churn import ChurnPrediction
        
        high_risk = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            created_at__gte=timezone.now() - timedelta(days=30)
        ).aggregate(total=Sum('monthly_recurring_revenue'))['total'] or 0
        
        return Decimal(str(high_risk))
    
    @staticmethod
    def count_high_risk_customers():
        """Count customers at high churn risk"""
        from .models_churn import ChurnPrediction
        
        return ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
    
    @staticmethod
    def generate_kpi_snapshot():
        """Generate complete KPI snapshot"""
        from .models_kpi import KPISnapshot
        
        start_time = time.time()
        
        # Calculate all metrics
        mrr_current = KPICalculationService.calculate_mrr()
        mrr_last_month = KPICalculationService.calculate_mrr_last_month()
        mrr_target = KPICalculationService.get_mrr_target()
        
        # Calculate growth
        if mrr_last_month > 0:
            mrr_growth_pct = float((mrr_current - mrr_last_month) / mrr_last_month * 100)
        else:
            mrr_growth_pct = 0.0
        
        active_customers = KPICalculationService.calculate_active_customers()
        active_customers_last_month = KPICalculationService.calculate_active_customers_last_month()
        churn_rate = KPICalculationService.calculate_churn_rate(30)
        new_customers = KPICalculationService.calculate_new_customers(30)
        
        cash_position = KPICalculationService.get_cash_position()
        cash_position_30d_ago = KPICalculationService.get_cash_position_30d_ago()
        receivables = KPICalculationService.get_outstanding_receivables()
        total_receivables = sum(receivables.values())
        
        network_uptime = KPICalculationService.calculate_network_uptime(7)
        revenue_at_risk = KPICalculationService.get_revenue_at_risk()
        high_risk_customers = KPICalculationService.count_high_risk_customers()
        
        # Calculate computation time
        computation_time_ms = int((time.time() - start_time) * 1000)
        
        # Create snapshot
        snapshot = KPISnapshot.objects.create(
            mrr_current=mrr_current,
            mrr_last_month=mrr_last_month,
            mrr_target=mrr_target,
            mrr_growth_pct=mrr_growth_pct,
            active_customers=active_customers,
            active_customers_last_month=active_customers_last_month,
            churn_rate_30d=churn_rate,
            new_customers_30d=new_customers,
            cash_position=cash_position,
            cash_position_30d_ago=cash_position_30d_ago,
            outstanding_receivables=receivables,
            total_receivables=Decimal(str(total_receivables)),
            network_uptime_7d=network_uptime,
            revenue_at_risk=revenue_at_risk,
            high_risk_customers=high_risk_customers,
            computed_in_ms=computation_time_ms
        )
        
        # Cleanup old snapshots (keep last 24 hours)
        KPISnapshot.cleanup_old_snapshots(hours=24)
        
        return snapshot
