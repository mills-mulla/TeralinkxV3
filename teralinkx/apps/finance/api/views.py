from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Count, Avg
from finance.models import RevenueStream, Expense, Investment, Department
from decimal import Decimal


class RevenueStreamAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        streams = RevenueStream.objects.all().order_by('display_order', 'name')
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
    
    def post(self, request):
        try:
            stream = RevenueStream.objects.create(
                name=request.data['name'],
                category=request.data['category'],
                target_revenue=request.data['target_revenue'],
                description=request.data.get('description', ''),
                is_active=request.data.get('is_active', True)
            )
            return Response({'id': stream.id, 'message': 'Created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            stream = RevenueStream.objects.get(pk=pk)
            stream.name = request.data.get('name', stream.name)
            stream.category = request.data.get('category', stream.category)
            stream.target_revenue = request.data.get('target_revenue', stream.target_revenue)
            stream.description = request.data.get('description', stream.description)
            stream.is_active = request.data.get('is_active', stream.is_active)
            stream.save()
            return Response({'message': 'Updated'})
        except RevenueStream.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            stream = RevenueStream.objects.get(pk=pk)
            stream.delete()
            return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        except RevenueStream.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class ExpenseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        expenses = Expense.objects.select_related('department').order_by('-expense_date')[:100]
        
        data = []
        for expense in expenses:
            data.append({
                'id': expense.id,
                'expense_date': expense.expense_date.isoformat(),
                'description': expense.description,
                'amount': float(expense.amount),
                'category': expense.category,
                'category_display': expense.get_category_display(),
                'department_name': expense.department.name if expense.department else None,
                'status': expense.approval_status,
                'status_display': expense.get_approval_status_display()
            })
        
        return Response(data)
    
    def post(self, request):
        try:
            expense = Expense.objects.create(
                description=request.data['description'],
                category=request.data['category'],
                amount=request.data['amount'],
                expense_date=request.data['expense_date'],
                approval_status=request.data.get('status', 'pending')
            )
            return Response({'id': expense.id, 'message': 'Created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)
            expense.description = request.data.get('description', expense.description)
            expense.category = request.data.get('category', expense.category)
            expense.amount = request.data.get('amount', expense.amount)
            expense.expense_date = request.data.get('expense_date', expense.expense_date)
            expense.approval_status = request.data.get('status', expense.approval_status)
            expense.save()
            return Response({'message': 'Updated'})
        except Expense.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)
            expense.delete()
            return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class InvestmentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        investments = Investment.objects.order_by('-investment_date')[:100]
        
        data = []
        for inv in investments:
            roi = ((float(inv.current_value or 0) - float(inv.amount)) / float(inv.amount) * 100) if inv.amount else 0
            data.append({
                'id': inv.id,
                'name': inv.investor_name,
                'amount': float(inv.amount),
                'current_value': float(inv.current_value or inv.amount),
                'investment_type': inv.investment_type,
                'type_display': inv.get_investment_type_display(),
                'investment_date': inv.investment_date.isoformat(),
                'status': inv.investment_status,
                'status_display': inv.get_investment_status_display(),
                'roi': roi
            })
        
        return Response(data)
    
    def post(self, request):
        try:
            investment = Investment.objects.create(
                investor_name=request.data['name'],
                investment_type=request.data['investment_type'],
                amount=request.data['amount'],
                current_value=request.data.get('current_value', request.data['amount']),
                investment_date=request.data['investment_date'],
                investment_status=request.data.get('status', 'active')
            )
            return Response({'id': investment.id, 'message': 'Created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            investment = Investment.objects.get(pk=pk)
            investment.investor_name = request.data.get('name', investment.investor_name)
            investment.investment_type = request.data.get('investment_type', investment.investment_type)
            investment.amount = request.data.get('amount', investment.amount)
            investment.current_value = request.data.get('current_value', investment.current_value)
            investment.investment_date = request.data.get('investment_date', investment.investment_date)
            investment.investment_status = request.data.get('status', investment.investment_status)
            investment.save()
            return Response({'message': 'Updated'})
        except Investment.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            investment = Investment.objects.get(pk=pk)
            investment.delete()
            return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Investment.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class DepartmentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        departments = Department.objects.all().order_by('name')
        
        data = []
        for dept in departments:
            spent = float(dept.current_month_spending)
            budget = float(dept.budget)
            utilization = (spent / budget * 100) if budget else 0
            data.append({
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'budget': budget,
                'spent': spent,
                'remaining': budget - spent,
                'utilization': utilization,
                'manager_name': dept.manager.username if dept.manager else None,
                'is_active': dept.is_active
            })
        
        return Response(data)
    
    def post(self, request):
        try:
            department = Department.objects.create(
                name=request.data['name'],
                code=request.data['code'],
                budget=request.data['budget'],
                is_active=request.data.get('is_active', True)
            )
            return Response({'id': department.id, 'message': 'Created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
            department.name = request.data.get('name', department.name)
            department.code = request.data.get('code', department.code)
            department.budget = request.data.get('budget', department.budget)
            department.is_active = request.data.get('is_active', department.is_active)
            department.save()
            return Response({'message': 'Updated'})
        except Department.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
            department.delete()
            return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Department.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
