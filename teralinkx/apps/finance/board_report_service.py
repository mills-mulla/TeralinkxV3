# apps/finance/board_report_service.py
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
from decimal import Decimal
import time


class BoardReportService:
    """Service for generating automated board reports"""
    
    @staticmethod
    def generate_monthly_report(year, month):
        """Generate complete board report for specified month"""
        from .models_board_report import BoardReport
        from .models import TransactionQueue, PaymentTransaction, Expense, Department
        from .models_churn import ChurnPrediction
        from .models_cashflow import CashFlowForecast
        from users.models import ClientH
        
        start_time = time.time()
        
        # Calculate report period
        report_date = timezone.datetime(year, month, 1).date()
        from django.utils.timezone import make_aware
        from datetime import timezone as dt_tz
        month_start = make_aware(timezone.datetime(year, month, 1, 0, 0, 0))
        if month == 12:
            month_end = make_aware(timezone.datetime(year + 1, 1, 1, 0, 0, 0)) - timedelta(seconds=1)
        else:
            month_end = make_aware(timezone.datetime(year, month + 1, 1, 0, 0, 0)) - timedelta(seconds=1)
        
        if month == 1:
            prev_month_start = make_aware(timezone.datetime(year - 1, 12, 1, 0, 0, 0))
            prev_month_end = make_aware(timezone.datetime(year, 1, 1, 0, 0, 0)) - timedelta(seconds=1)
        else:
            prev_month_start = make_aware(timezone.datetime(year, month - 1, 1, 0, 0, 0))
            prev_month_end = make_aware(timezone.datetime(year, month, 1, 0, 0, 0)) - timedelta(seconds=1)
        
        # 1. Financial Performance
        current_revenue = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__range=[month_start, month_end]
        ).aggregate(total=Sum('price'))['total'] or 0
        
        prev_revenue = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__range=[prev_month_start, prev_month_end]
        ).aggregate(total=Sum('price'))['total'] or 0
        
        revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        current_expenses = Expense.objects.filter(
            expense_date__range=[month_start.date(), month_end.date()],
            approval_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        prev_expenses = Expense.objects.filter(
            expense_date__range=[prev_month_start.date(), prev_month_end.date()],
            approval_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        net_profit = current_revenue - current_expenses
        profit_margin = (net_profit / current_revenue * 100) if current_revenue > 0 else 0
        
        financial_performance = {
            'revenue': {
                'current': float(current_revenue),
                'previous': float(prev_revenue),
                'growth_pct': float(revenue_growth)
            },
            'expenses': {
                'current': float(current_expenses),
                'previous': float(prev_expenses),
                'change_pct': float(((current_expenses - prev_expenses) / prev_expenses * 100) if prev_expenses > 0 else 0)
            },
            'net_profit': float(net_profit),
            'profit_margin_pct': float(profit_margin)
        }
        
        # 2. Customer Metrics
        current_customers = ClientH.objects.filter(
            created_at__lte=month_end
        ).exclude(status='inactive').count()
        
        prev_customers = ClientH.objects.filter(
            created_at__lte=prev_month_end
        ).exclude(status='inactive').count()
        
        new_customers = ClientH.objects.filter(
            created_at__range=[month_start, month_end]
        ).count()
        
        churned_customers = ClientH.objects.filter(
            status='inactive',
            updated_at__range=[month_start, month_end]
        ).count()
        
        churn_rate = (churned_customers / prev_customers * 100) if prev_customers > 0 else 0
        
        arpu = (current_revenue / current_customers) if current_customers > 0 else 0
        
        customer_metrics = {
            'active_customers': current_customers,
            'previous_customers': prev_customers,
            'new_customers': new_customers,
            'churned_customers': churned_customers,
            'churn_rate_pct': float(churn_rate),
            'arpu': float(arpu),
            'customer_growth_pct': float(((current_customers - prev_customers) / prev_customers * 100) if prev_customers > 0 else 0)
        }
        
        # 3. Operational Metrics
        total_transactions = TransactionQueue.objects.filter(
            created_at__range=[month_start, month_end]
        ).count()
        
        successful_transactions = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__range=[month_start, month_end]
        ).count()
        
        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        avg_transaction_value = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__range=[month_start, month_end]
        ).aggregate(avg=Avg('price'))['avg'] or 0
        
        operational_metrics = {
            'total_transactions': total_transactions,
            'successful_transactions': successful_transactions,
            'success_rate_pct': float(success_rate),
            'avg_transaction_value': float(avg_transaction_value),
            'network_uptime_pct': 99.5  # Placeholder
        }
        
        # 4. Risk Register
        high_risk_customers = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            created_at__gte=month_start
        ).count()
        
        revenue_at_risk = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            created_at__gte=month_start
        ).aggregate(total=Sum('monthly_recurring_revenue'))['total'] or 0
        
        budget_overruns = 0  # Simplified - would need proper query
        
        from django.db import models
        
        risk_register = {
            'high_risk_customers': high_risk_customers,
            'revenue_at_risk': float(revenue_at_risk),
            'budget_overruns': budget_overruns,
            'outstanding_receivables': float(BoardReportService._get_receivables())
        }
        
        # 5. Cash Flow Forecast
        latest_forecast = CashFlowForecast.objects.filter(
            scenario='base'
        ).order_by('-created_at').first()
        
        if latest_forecast:
            cash_flow_forecast = {
                'next_30_days': float(latest_forecast.total_forecasted),
                'scenario': latest_forecast.scenario,
                'confidence': float(latest_forecast.confidence_interval)
            }
        else:
            cash_flow_forecast = {
                'next_30_days': 0,
                'scenario': 'base',
                'confidence': 0
            }
        
        # Generate narrative sections
        key_highlights = BoardReportService._generate_highlights(
            revenue_growth, customer_metrics, operational_metrics
        )
        
        challenges = BoardReportService._generate_challenges(
            churn_rate, budget_overruns, high_risk_customers
        )
        
        recommendations = BoardReportService._generate_recommendations(
            financial_performance, customer_metrics, risk_register
        )
        
        executive_summary = BoardReportService._generate_executive_summary(
            report_date, financial_performance, customer_metrics
        )
        
        # Calculate generation time
        generation_time = int(time.time() - start_time)
        
        # Create or update report
        report, created = BoardReport.objects.update_or_create(
            report_year=year,
            report_month=report_date,
            defaults={
                'financial_performance': financial_performance,
                'customer_metrics': customer_metrics,
                'operational_metrics': operational_metrics,
                'risk_register': risk_register,
                'cash_flow_forecast': cash_flow_forecast,
                'key_highlights': key_highlights,
                'challenges': challenges,
                'recommendations': recommendations,
                'executive_summary': executive_summary,
                'generation_time_seconds': generation_time,
                'status': 'draft'
            }
        )
        
        return report
    
    @staticmethod
    def _get_receivables():
        """Calculate outstanding receivables"""
        from .models import TransactionQueue
        
        pending = TransactionQueue.objects.filter(
            status='pending'
        ).aggregate(total=Sum('price'))['total'] or 0
        
        return pending
    
    @staticmethod
    def _generate_highlights(revenue_growth, customer_metrics, operational_metrics):
        """Generate key highlights"""
        highlights = []
        
        if revenue_growth > 10:
            highlights.append(f"Strong revenue growth of {revenue_growth:.1f}% month-over-month")
        
        if customer_metrics['new_customers'] > customer_metrics['churned_customers']:
            net_growth = customer_metrics['new_customers'] - customer_metrics['churned_customers']
            highlights.append(f"Net customer growth of {net_growth} customers")
        
        if operational_metrics['success_rate_pct'] > 95:
            highlights.append(f"High transaction success rate of {operational_metrics['success_rate_pct']:.1f}%")
        
        return highlights
    
    @staticmethod
    def _generate_challenges(churn_rate, budget_overruns, high_risk_customers):
        """Generate challenges list"""
        challenges = []
        
        if churn_rate > 5:
            challenges.append(f"Elevated churn rate at {churn_rate:.1f}%")
        
        if budget_overruns > 0:
            challenges.append(f"{budget_overruns} departments over budget")
        
        if high_risk_customers > 10:
            challenges.append(f"{high_risk_customers} customers at high churn risk")
        
        return challenges
    
    @staticmethod
    def _generate_recommendations(financial_performance, customer_metrics, risk_register):
        """Generate recommendations"""
        recommendations = []
        
        if financial_performance['profit_margin_pct'] < 20:
            recommendations.append("Review cost structure to improve profit margins")
        
        if customer_metrics['churn_rate_pct'] > 5:
            recommendations.append("Implement targeted retention campaigns for at-risk customers")
        
        if risk_register['budget_overruns'] > 0:
            recommendations.append("Conduct budget review with department heads")
        
        return recommendations
    
    @staticmethod
    def _generate_executive_summary(report_date, financial_performance, customer_metrics):
        """Generate executive summary"""
        month_name = report_date.strftime('%B %Y')
        
        summary = f"Board Report for {month_name}\n\n"
        summary += f"Revenue: KES {financial_performance['revenue']['current']:,.2f} "
        summary += f"({financial_performance['revenue']['growth_pct']:+.1f}% MoM)\n"
        summary += f"Net Profit: KES {financial_performance['net_profit']:,.2f} "
        summary += f"({financial_performance['profit_margin_pct']:.1f}% margin)\n"
        summary += f"Active Customers: {customer_metrics['active_customers']} "
        summary += f"({customer_metrics['customer_growth_pct']:+.1f}% MoM)\n"
        
        return summary
