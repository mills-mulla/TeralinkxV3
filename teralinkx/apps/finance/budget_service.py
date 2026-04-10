# apps/finance/budget_service.py
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from datetime import timedelta
from decimal import Decimal
from .models import Expense, Department, BudgetCategory


class BudgetIntelligenceService:
    """Dynamic budget tracking with variance analysis"""
    
    @staticmethod
    def calculate_utilization_rate(department_id=None, category_id=None):
        """Calculate budget utilization rate with days remaining context"""
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        days_in_month = (month_start.replace(month=month_start.month % 12 + 1, day=1) - timedelta(days=1)).day
        days_elapsed = now.day
        days_remaining = days_in_month - days_elapsed
        
        if category_id:
            category = BudgetCategory.objects.get(id=category_id)
            spent = Expense.objects.filter(
                budget_category=category,
                expense_date__gte=month_start,
                approval_status__in=['approved', 'paid']
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            budget = category.planned_amount
            utilization = (spent / budget * 100) if budget > 0 else 0
            
            return {
                'budget': float(budget),
                'spent': float(spent),
                'remaining': float(budget - spent),
                'utilization_rate': float(utilization),
                'days_elapsed': days_elapsed,
                'days_remaining': days_remaining,
                'expected_utilization': (days_elapsed / days_in_month * 100),
                'status': 'on_track' if utilization <= (days_elapsed / days_in_month * 100) + 10 else 'at_risk'
            }
        
        if department_id:
            dept = Department.objects.get(id=department_id)
            spent = dept.current_month_spending
            budget = dept.budget
            utilization = (spent / budget * 100) if budget > 0 else 0
            
            return {
                'budget': float(budget),
                'spent': float(spent),
                'remaining': float(budget - spent),
                'utilization_rate': float(utilization),
                'days_elapsed': days_elapsed,
                'days_remaining': days_remaining,
                'expected_utilization': (days_elapsed / days_in_month * 100),
                'status': 'on_track' if utilization <= (days_elapsed / days_in_month * 100) + 10 else 'at_risk'
            }
        
        return None
    
    @staticmethod
    def variance_analysis(department_id=None, months=3):
        """Analyze budget variance with explanations"""
        now = timezone.now()
        
        if department_id:
            dept = Department.objects.get(id=department_id)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            spent = dept.current_month_spending
            budget = dept.budget
            variance = budget - spent
            variance_pct = (variance / budget * 100) if budget > 0 else 0
            
            # Get top expense drivers
            top_expenses = Expense.objects.filter(
                department=dept,
                expense_date__gte=month_start,
                approval_status__in=['approved', 'paid']
            ).order_by('-amount')[:5].values('description', 'amount', 'category')
            
            return {
                'department': dept.name,
                'budget': float(budget),
                'actual': float(spent),
                'variance': float(variance),
                'variance_percentage': float(variance_pct),
                'status': 'under' if variance > 0 else 'over',
                'top_expenses': list(top_expenses),
                'explanation': f"{dept.name} {'overspent' if variance < 0 else 'underspent'} by KES {abs(variance):,.2f}"
            }
        
        return None
    
    @staticmethod
    def rolling_spend_trends(department_id, months=3):
        """Calculate rolling 3-month spend trends"""
        now = timezone.now()
        trends = []
        
        dept = Department.objects.get(id=department_id)
        
        for i in range(months):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start.replace(month=month_start.month % 12 + 1, day=1) - timedelta(days=1)).replace(hour=23, minute=59, second=59)
            
            spent = Expense.objects.filter(
                department=dept,
                expense_date__range=[month_start, month_end],
                approval_status__in=['approved', 'paid']
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            trends.append({
                'month': month_start.strftime('%Y-%m'),
                'spent': float(spent),
                'budget': float(dept.budget)
            })
        
        return list(reversed(trends))
    
    @staticmethod
    def get_budget_alerts():
        """Generate budget alert notifications"""
        alerts = []
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Check all departments
        for dept in Department.objects.filter(is_active=True):
            utilization = dept.budget_utilization
            
            if utilization > 90:
                alerts.append({
                    'severity': 'critical',
                    'department': dept.name,
                    'message': f"{dept.name} has exceeded 90% budget utilization ({utilization:.1f}%)",
                    'utilization': float(utilization)
                })
            elif utilization > 75:
                alerts.append({
                    'severity': 'warning',
                    'department': dept.name,
                    'message': f"{dept.name} approaching budget limit ({utilization:.1f}%)",
                    'utilization': float(utilization)
                })
        
        return alerts
    
    @staticmethod
    def department_comparison():
        """Compare budget performance across departments"""
        departments = []
        
        for dept in Department.objects.filter(is_active=True):
            utilization = dept.budget_utilization
            spent = dept.current_month_spending
            
            departments.append({
                'name': dept.name,
                'code': dept.code,
                'budget': float(dept.budget),
                'spent': float(spent),
                'utilization': float(utilization),
                'status': 'critical' if utilization > 90 else 'warning' if utilization > 75 else 'ok'
            })
        
        return sorted(departments, key=lambda x: x['utilization'], reverse=True)
