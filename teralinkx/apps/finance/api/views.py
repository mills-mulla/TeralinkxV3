from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from finance.models import RevenueStream, Expense, Investment, Department
from decimal import Decimal


class RevenueStreamAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        streams = RevenueStream.objects.filter(is_active=True).order_by('display_order', 'name')
        data = []
        
        for stream in streams:
            data.append({
                'id': stream.id,
                'name': stream.name,
                'category': stream.category,
                'category_display': stream.get_category_display(),
                'current_revenue': float(stream.current_month_revenue),
                'target_revenue': float(stream.target_revenue or 0),
                'achievement': float(stream.target_achievement),
                'growth': float(stream.revenue_growth),
                'is_active': stream.is_active,
                'description': stream.description
            })
        
        return Response(data)


class ExpenseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        expenses = Expense.objects.filter(
            approval_status__in=['approved', 'paid']
        ).select_related('department', 'currency').order_by('-expense_date')[:50]
        
        data = []
        for expense in expenses:
            data.append({
                'id': expense.id,
                'date': expense.expense_date.isoformat(),
                'description': expense.description,
                'amount': float(expense.amount),
                'amount_base': float(expense.amount_base),
                'currency': expense.currency.code,
                'category': expense.get_category_display(),
                'department': expense.department.name if expense.department else None,
                'vendor': expense.vendor,
                'status': expense.get_approval_status_display(),
                'is_capex': expense.is_capex
            })
        
        return Response(data)


class InvestmentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        investments = Investment.objects.select_related('currency').order_by('-investment_date')[:50]
        
        data = []
        for inv in investments:
            data.append({
                'id': inv.id,
                'investor_name': inv.investor_name,
                'amount': float(inv.amount),
                'amount_base': float(inv.amount_base),
                'currency': inv.currency.code,
                'type': inv.get_investment_type_display(),
                'status': inv.get_investment_status_display(),
                'date': inv.investment_date.isoformat(),
                'equity_percentage': float(inv.equity_percentage) if inv.equity_percentage else None,
                'interest_rate': float(inv.interest_rate) if inv.interest_rate else None,
                'is_active': inv.is_active
            })
        
        return Response(data)


class DepartmentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        departments = Department.objects.filter(is_active=True).order_by('name')
        
        data = []
        for dept in departments:
            data.append({
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'budget': float(dept.budget),
                'current_spending': float(dept.current_month_spending),
                'budget_utilization': float(dept.budget_utilization),
                'manager': dept.manager.username if dept.manager else None,
                'is_active': dept.is_active
            })
        
        return Response(data)
