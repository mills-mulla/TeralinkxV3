from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from finance.models import (
    RevenueStream, Expense, Investment, Department,
    PaymentTransaction, BalanceTransaction, TransactionQueue
)
from packages.models import PackageType
from users.models import ClientH
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


class FinancialMetricsAPIView(APIView):
    """Backend calculation of MRR, ARR, ARPU, LTV"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Calculate MRR from completed transactions
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mrr = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__gte=current_month
        ).aggregate(total=Sum('price'))['total'] or 0
        
        # ARR = MRR * 12
        arr = float(mrr) * 12
        
        # ARPU = MRR / Active Users
        active_users = ClientH.objects.filter(status='active').count()
        arpu = float(mrr) / active_users if active_users > 0 else 0
        
        # LTV = ARPU * Average Customer Lifespan (24 months)
        ltv = arpu * 24
        
        return Response({
            'mrr': float(mrr),
            'arr': arr,
            'arpu': arpu,
            'ltv': ltv,
            'active_users': active_users,
            'calculated_at': timezone.now().isoformat()
        })


class PackagePerformanceAPIView(APIView):
    """Backend calculation of package performance metrics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get package sales from TransactionQueue
        package_stats = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__gte=current_month
        ).values('package_code', 'package').annotate(
            sales=Count('id'),
            revenue=Sum('price')
        ).order_by('-revenue')
        
        # Enrich with package details
        data = []
        for stat in package_stats:
            try:
                pkg = PackageType.objects.get(code=stat['package_code'])
                data.append({
                    'package_code': stat['package_code'],
                    'package_name': stat['package'],
                    'sales': stat['sales'],
                    'revenue': float(stat['revenue']),
                    'price': float(pkg.price),
                    'validity_days': pkg.validity_days
                })
            except PackageType.DoesNotExist:
                data.append({
                    'package_code': stat['package_code'],
                    'package_name': stat['package'],
                    'sales': stat['sales'],
                    'revenue': float(stat['revenue']),
                    'price': 0,
                    'validity_days': 0
                })
        
        return Response(data)


class TransactionStatsAPIView(APIView):
    """Unified transaction statistics for all transaction types"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Payment Transactions Stats
        payment_stats = PaymentTransaction.objects.aggregate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount')
        )
        
        # Balance Transactions Stats
        balance_stats = BalanceTransaction.objects.aggregate(
            total_credit=Sum('credit'),
            total_debit=Sum('debit'),
            count=Count('id')
        )
        
        # Transaction Queue Stats
        queue_stats = TransactionQueue.objects.aggregate(
            total=Sum('price'),
            count=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            completed=Count('id', filter=Q(status__in=['completed', 'processed'])),
            failed=Count('id', filter=Q(status='failed'))
        )
        
        return Response({
            'payments': {
                'total_amount': float(payment_stats['total'] or 0),
                'count': payment_stats['count'],
                'average': float(payment_stats['avg'] or 0)
            },
            'balance': {
                'total_credit': float(balance_stats['total_credit'] or 0),
                'total_debit': float(balance_stats['total_debit'] or 0),
                'net': float((balance_stats['total_credit'] or 0) - (balance_stats['total_debit'] or 0)),
                'count': balance_stats['count']
            },
            'queue': {
                'total_amount': float(queue_stats['total'] or 0),
                'count': queue_stats['count'],
                'pending': queue_stats['pending'],
                'completed': queue_stats['completed'],
                'failed': queue_stats['failed']
            }
        })


class UnifiedTransactionsAPIView(APIView):
    """Unified endpoint for all transaction types with pagination"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        transaction_type = request.query_params.get('type', 'all')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        search = request.query_params.get('search', '')
        
        start = (page - 1) * page_size
        end = start + page_size
        
        result = {'payments': [], 'balance': [], 'queue': [], 'points': []}
        
        if transaction_type in ['all', 'payments']:
            payments = PaymentTransaction.objects.select_related('user', 'currency').all()
            if search:
                payments = payments.filter(
                    Q(transaction_id__icontains=search) |
                    Q(initiator__icontains=search) |
                    Q(user__account__icontains=search)
                )
            payments = payments.order_by('-created_at')[start:end]
            result['payments'] = [{
                'id': p.id,
                'transaction_id': p.transaction_id,
                'user': p.user.account,
                'amount': float(p.amount),
                'currency': p.currency.code,
                'method': p.payment_method,
                'status': p.status,
                'date': p.created_at.isoformat()
            } for p in payments]
        
        if transaction_type in ['all', 'balance']:
            balance = BalanceTransaction.objects.select_related('user').all()
            if search:
                balance = balance.filter(
                    Q(user__account__icontains=search) |
                    Q(description__icontains=search)
                )
            balance = balance.order_by('-created_at')[start:end]
            result['balance'] = [{
                'id': b.id,
                'user': b.user.account,
                'type': b.transaction_type,
                'debit': float(b.debit),
                'credit': float(b.credit),
                'balance_after': float(b.balance_after),
                'description': b.description,
                'date': b.created_at.isoformat()
            } for b in balance]
        
        if transaction_type in ['all', 'queue']:
            queue = TransactionQueue.objects.select_related('user').all()
            if search:
                queue = queue.filter(
                    Q(initiator__icontains=search) |
                    Q(package__icontains=search) |
                    Q(user__account__icontains=search)
                )
            queue = queue.order_by('-created_at')[start:end]
            result['queue'] = [{
                'id': q.id,
                'user': q.user.account,
                'initiator': q.initiator,
                'package': q.package,
                'price': float(q.price),
                'status': q.status,
                'method': q.method,
                'date': q.created_at.isoformat()
            } for q in queue]
        
        return Response(result)
