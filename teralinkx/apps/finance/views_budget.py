# apps/finance/views_budget.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .budget_service import BudgetIntelligenceService
from .models import Department, BudgetCategory


class BudgetUtilizationView(APIView):
    """Get budget utilization for all departments or a specific one"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        department_id = request.query_params.get('department_id')
        category_id = request.query_params.get('category_id')
        
        # If specific department/category requested
        if department_id or category_id:
            try:
                utilization = BudgetIntelligenceService.calculate_utilization_rate(
                    department_id=department_id,
                    category_id=category_id
                )
                return Response(utilization)
            except (Department.DoesNotExist, BudgetCategory.DoesNotExist):
                return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Return all departments as a list
        results = []
        for dept in Department.objects.filter(is_active=True):
            utilization = BudgetIntelligenceService.calculate_utilization_rate(department_id=dept.id)
            if utilization:
                utilization['department'] = dept.name
                utilization['category'] = dept.name
                results.append(utilization)
        return Response(results)


class BudgetVarianceView(APIView):
    """Get variance analysis for all departments or a specific one"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        department_id = request.query_params.get('department_id')
        
        if department_id:
            try:
                variance = BudgetIntelligenceService.variance_analysis(department_id=department_id)
                return Response(variance)
            except Department.DoesNotExist:
                return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Return all departments as a list
        results = []
        for dept in Department.objects.filter(is_active=True):
            variance = BudgetIntelligenceService.variance_analysis(department_id=dept.id)
            if variance:
                variance['category'] = dept.name
                results.append(variance)
        return Response(results)


class BudgetTrendsView(APIView):
    """Get rolling spend trends"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        department_id = request.query_params.get('department_id')
        months = int(request.query_params.get('months', 3))
        
        if not department_id:
            return Response(
                {'error': 'department_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            trends = BudgetIntelligenceService.rolling_spend_trends(
                department_id=department_id,
                months=months
            )
            return Response({'trends': trends})
        except Department.DoesNotExist:
            return Response(
                {'error': 'Department not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class BudgetAlertsView(APIView):
    """Get budget alert notifications"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        alerts = BudgetIntelligenceService.get_budget_alerts()
        return Response({'alerts': alerts})


class DepartmentComparisonView(APIView):
    """Compare budget performance across departments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        comparison = BudgetIntelligenceService.department_comparison()
        return Response({'departments': comparison})


class BudgetDashboardView(APIView):
    """Unified budget intelligence dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        alerts = BudgetIntelligenceService.get_budget_alerts()
        comparison = BudgetIntelligenceService.department_comparison()
        
        return Response({
            'alerts': alerts,
            'departments': comparison,
            'summary': {
                'total_departments': len(comparison),
                'critical_count': len([d for d in comparison if d['status'] == 'critical']),
                'warning_count': len([d for d in comparison if d['status'] == 'warning']),
                'ok_count': len([d for d in comparison if d['status'] == 'ok'])
            }
        })
