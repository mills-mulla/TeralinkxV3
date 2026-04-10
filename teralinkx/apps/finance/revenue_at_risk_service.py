"""
Revenue at Risk Service
Calculates and tracks revenue at risk from churning customers.
"""
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from finance.models_churn import ChurnPrediction, RetentionTask


class RevenueAtRiskService:
    """Service for calculating revenue at risk metrics"""
    
    @staticmethod
    def get_total_revenue_at_risk():
        """Calculate total MRR at risk from high/critical churn customers"""
        high_risk_predictions = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            is_active=True
        )
        
        total_mrr = sum(
            pred.monthly_recurring_revenue or 0 
            for pred in high_risk_predictions
        )
        
        # Revenue at risk = 6 months MRR
        return total_mrr * 6
    
    @staticmethod
    def get_week_over_week_trend():
        """Calculate week-over-week change in revenue at risk"""
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        # Current week
        current_predictions = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            is_active=True,
            prediction_date__gte=week_ago
        )
        current_mrr = sum(
            pred.monthly_recurring_revenue or 0 
            for pred in current_predictions
        )
        
        # Previous week
        two_weeks_ago = now - timedelta(days=14)
        previous_predictions = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            is_active=True,
            prediction_date__range=[two_weeks_ago, week_ago]
        )
        previous_mrr = sum(
            pred.monthly_recurring_revenue or 0 
            for pred in previous_predictions
        )
        
        if previous_mrr == 0:
            return 0
        
        change = ((current_mrr - previous_mrr) / previous_mrr) * 100
        return round(change, 1)
    
    @staticmethod
    def get_top_at_risk_accounts(limit=10):
        """Get top N accounts at risk by revenue"""
        predictions = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            is_active=True
        ).select_related('customer').order_by('-monthly_recurring_revenue')[:limit]
        
        accounts = []
        for pred in predictions:
            # Get latest retention task
            latest_task = RetentionTask.objects.filter(
                customer=pred.customer
            ).order_by('-created_at').first()
            
            accounts.append({
                'customer_id': pred.customer.id,
                'account': pred.customer.account,
                'phone': pred.customer.phone_number,
                'mrr': float(pred.monthly_recurring_revenue or 0),
                'revenue_at_risk': float((pred.monthly_recurring_revenue or 0) * 6),
                'churn_score': pred.churn_score,
                'risk_level': pred.risk_level,
                'top_factors': pred.top_factors,
                'days_since_last_session': pred.days_since_last_session,
                'retention_task_status': latest_task.status if latest_task else None,
                'retention_action': latest_task.action_type if latest_task else None,
                'outcome': latest_task.outcome if latest_task else None,
            })
        
        return accounts
    
    @staticmethod
    def get_retention_effectiveness():
        """Calculate retention effectiveness metrics"""
        all_tasks = RetentionTask.objects.all()
        
        # Overall stats
        total_tasks = all_tasks.count()
        completed_tasks = all_tasks.filter(status='completed').count()
        
        # Outcome breakdown
        retained = all_tasks.filter(outcome='retained').count()
        churned = all_tasks.filter(outcome='churned').count()
        relocated = all_tasks.filter(outcome='relocated').count()
        pending = all_tasks.filter(outcome='pending').count()
        
        # Calculate retention rate
        total_resolved = retained + churned
        retention_rate = (retained / total_resolved * 100) if total_resolved > 0 else 0
        
        # Revenue metrics
        total_revenue_at_risk = all_tasks.aggregate(
            total=Sum('revenue_at_risk')
        )['total'] or 0
        
        retained_revenue = all_tasks.filter(outcome='retained').aggregate(
            total=Sum('revenue_at_risk')
        )['total'] or 0
        
        # Action breakdown
        action_stats = list(all_tasks.values('action_type').annotate(
            count=Count('id'),
            retained_count=Count('id', filter=Q(outcome='retained'))
        ))
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'retention_rate': round(retention_rate, 1),
            'outcomes': {
                'retained': retained,
                'churned': churned,
                'relocated': relocated,
                'pending': pending,
            },
            'revenue': {
                'total_at_risk': float(total_revenue_at_risk),
                'retained': float(retained_revenue),
                'saved_percentage': round((retained_revenue / total_revenue_at_risk * 100), 1) if total_revenue_at_risk > 0 else 0,
            },
            'action_effectiveness': action_stats,
        }
    
    @staticmethod
    def get_automated_offers_sent():
        """Count automated offers sent by type"""
        last_30_days = timezone.now() - timedelta(days=30)
        
        offers = RetentionTask.objects.filter(
            automated=True,
            created_at__gte=last_30_days
        ).values('action_type').annotate(
            count=Count('id')
        )
        
        return {
            'total': sum(offer['count'] for offer in offers),
            'by_type': list(offers),
            'period': '30 days',
        }
    
    @staticmethod
    def get_relocated_customers():
        """Get customers who relocated (excluded from churn metrics)"""
        relocated_tasks = RetentionTask.objects.filter(
            outcome='relocated'
        ).select_related('customer')
        
        return [
            {
                'customer_id': task.customer.id,
                'account': task.customer.account,
                'mrr': float(task.monthly_recurring_revenue),
                'relocated_date': task.outcome_date,
                'notes': task.outcome_notes,
            }
            for task in relocated_tasks
        ]
    
    @staticmethod
    def get_dashboard_summary():
        """Get complete dashboard summary"""
        return {
            'total_revenue_at_risk': float(RevenueAtRiskService.get_total_revenue_at_risk()),
            'week_over_week_trend': RevenueAtRiskService.get_week_over_week_trend(),
            'top_at_risk_accounts': RevenueAtRiskService.get_top_at_risk_accounts(10),
            'retention_effectiveness': RevenueAtRiskService.get_retention_effectiveness(),
            'automated_offers_sent': RevenueAtRiskService.get_automated_offers_sent(),
            'relocated_customers_count': RetentionTask.objects.filter(outcome='relocated').count(),
            'timestamp': timezone.now().isoformat(),
        }
