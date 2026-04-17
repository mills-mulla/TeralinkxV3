# apps/finance/views_medium.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from finance.models_medium import (
    NotificationPreference, ExpenseNotification,
    FinancialYear, PettyCashFund, PettyCashTransaction,
    PurchaseOrder, AuditLog
)


# ── 6.13 Expense Notifications ────────────────────────────────────────────────

class NotificationPrefsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        return Response({
            'expense_submitted_sms':   prefs.expense_submitted_sms,
            'expense_submitted_email': prefs.expense_submitted_email,
            'expense_approved_sms':    prefs.expense_approved_sms,
            'expense_approved_email':  prefs.expense_approved_email,
            'budget_alert_sms':        prefs.budget_alert_sms,
            'budget_alert_email':      prefs.budget_alert_email,
            'tax_deadline_sms':        prefs.tax_deadline_sms,
            'tax_deadline_email':      prefs.tax_deadline_email,
        })

    def patch(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        for field in ['expense_submitted_sms', 'expense_submitted_email',
                      'expense_approved_sms', 'expense_approved_email',
                      'budget_alert_sms', 'budget_alert_email',
                      'tax_deadline_sms', 'tax_deadline_email']:
            if field in request.data:
                setattr(prefs, field, request.data[field])
        prefs.save()
        return Response({'message': 'Preferences updated'})


class PendingApprovalsView(APIView):
    """Expenses pending approval — for approver dashboard badge."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from finance.models import Expense
        pending = Expense.objects.filter(approval_status='submitted').count()
        overdue = Expense.objects.filter(
            approval_status='submitted',
            submitted_at__lt=timezone.now() - timezone.timedelta(hours=48)
        ).count()
        return Response({'pending': pending, 'overdue_48h': overdue})


# ── 6.14 Financial Year ───────────────────────────────────────────────────────

class FinancialYearView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        years = FinancialYear.objects.all()
        current = FinancialYear.get_current()
        return Response({
            'current_year': {
                'year': current.year,
                'status': current.status,
                'start_date': current.start_date.isoformat(),
                'end_date': current.end_date.isoformat(),
                'opening_balance': float(current.opening_balance),
            },
            'all_years': [{
                'year': y.year, 'status': y.status,
                'start_date': y.start_date.isoformat(),
                'end_date': y.end_date.isoformat(),
                'closing_balance': float(y.closing_balance),
                'closed_at': y.closed_at.isoformat() if y.closed_at else None,
            } for y in years]
        })

    def post(self, request):
        action = request.data.get('action')
        if action == 'close':
            try:
                year = int(request.data.get('year', timezone.now().year))
                fy = FinancialYear.objects.get(year=year)
                from decimal import Decimal
                closing_balance = Decimal(str(request.data.get('closing_balance', 0)))
                fy.close(request.user, closing_balance)
                AuditLog.log('FinancialYear', fy.id, 'approve', request.user,
                             description=f'Financial year {year} closed')
                return Response({'message': f'FY {year} closed successfully'})
            except FinancialYear.DoesNotExist:
                return Response({'error': 'Financial year not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'action must be close'}, status=status.HTTP_400_BAD_REQUEST)


# ── 6.15 Petty Cash ───────────────────────────────────────────────────────────

class PettyCashView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        funds = PettyCashFund.objects.filter(is_active=True).select_related('department')
        return Response({'funds': [{
            'id': f.id,
            'name': f.name,
            'float_amount': float(f.float_amount),
            'current_balance': float(f.current_balance),
            'is_low': f.is_low,
            'low_balance_threshold': float(f.low_balance_threshold),
            'department': f.department.name if f.department else None,
            'custodian': f.custodian.username,
        } for f in funds]})

    def post(self, request):
        try:
            from finance.models import Department
            dept = Department.objects.filter(id=request.data.get('department_id')).first()
            from decimal import Decimal
            amount = Decimal(str(request.data['float_amount']))
            fund = PettyCashFund.objects.create(
                name=request.data['name'],
                float_amount=amount,
                current_balance=amount,
                custodian=request.user,
                department=dept,
                low_balance_threshold=Decimal(str(request.data.get('low_balance_threshold', 1000))),
            )
            return Response({'id': fund.id, 'name': fund.name}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PettyCashTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, fund_id):
        try:
            fund = PettyCashFund.objects.get(id=fund_id)
            txns = fund.transactions.all()[:50]
            return Response({
                'fund': fund.name,
                'current_balance': float(fund.current_balance),
                'is_low': fund.is_low,
                'transactions': [{
                    'id': t.id,
                    'type': t.transaction_type,
                    'amount': float(t.amount),
                    'description': t.description,
                    'receipt_number': t.receipt_number,
                    'balance_after': float(t.balance_after),
                    'date': t.created_at.isoformat(),
                } for t in txns]
            })
        except PettyCashFund.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, fund_id):
        try:
            fund = PettyCashFund.objects.get(id=fund_id)
            from decimal import Decimal
            txn = PettyCashTransaction.objects.create(
                fund=fund,
                transaction_type=request.data.get('transaction_type', 'expense'),
                amount=Decimal(str(request.data['amount'])),
                description=request.data['description'],
                receipt_number=request.data.get('receipt_number', ''),
                approved_by=request.user,
            )
            AuditLog.log('PettyCashTransaction', txn.id, 'create', request.user,
                         description=f'Petty cash {txn.transaction_type}: {txn.description}')
            return Response({'id': txn.id, 'balance_after': float(txn.balance_after)},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ── 6.16 Purchase Orders ──────────────────────────────────────────────────────

def _po(p):
    return {
        'id': p.id,
        'po_number': p.po_number,
        'vendor_name': p.vendor_name,
        'total_amount': float(p.total_amount),
        'status': p.status,
        'status_display': p.get_status_display(),
        'department': p.department.name if p.department else None,
        'expected_delivery': p.expected_delivery.isoformat() if p.expected_delivery else None,
        'line_items': p.line_items,
        'notes': p.notes,
        'created_at': p.created_at.isoformat(),
    }


class PurchaseOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = PurchaseOrder.objects.select_related('department')
        po_status = request.query_params.get('status')
        if po_status:
            qs = qs.filter(status=po_status)
        return Response({'count': qs.count(), 'results': [_po(p) for p in qs[:100]]})

    def post(self, request):
        try:
            from finance.models import Department
            from decimal import Decimal
            dept = Department.objects.filter(id=request.data.get('department_id')).first()
            line_items = request.data.get('line_items', [])
            total = sum(Decimal(str(item.get('total', 0))) for item in line_items)

            po = PurchaseOrder.objects.create(
                po_number=PurchaseOrder.generate_number(),
                vendor_name=request.data['vendor_name'],
                department=dept,
                total_amount=total or Decimal(str(request.data.get('total_amount', 0))),
                expected_delivery=request.data.get('expected_delivery'),
                notes=request.data.get('notes', ''),
                line_items=line_items,
                submitted_by=request.user,
                status='submitted',
            )
            AuditLog.log('PurchaseOrder', po.id, 'create', request.user,
                         description=f'PO {po.po_number} submitted for {po.vendor_name}')
            return Response(_po(po), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, po_id):
        try:
            return Response(_po(PurchaseOrder.objects.get(id=po_id)))
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, po_id):
        try:
            po = PurchaseOrder.objects.get(id=po_id)
            action = request.data.get('action')
            old_status = po.status
            if action == 'approve':
                po.approve(request.user)
            elif action == 'receive':
                po.mark_received()
            elif action == 'cancel':
                po.status = 'cancelled'
                po.save()
            else:
                return Response({'error': 'action must be approve, receive, or cancel'},
                                status=status.HTTP_400_BAD_REQUEST)
            AuditLog.log('PurchaseOrder', po.id, 'approve' if action == 'approve' else 'update',
                         request.user, old_values={'status': old_status},
                         new_values={'status': po.status})
            return Response({'message': f'PO {action}d', 'status': po.status})
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# ── 6.17 Audit Trail ──────────────────────────────────────────────────────────

class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = AuditLog.objects.select_related('changed_by')
        model_name = request.query_params.get('model')
        record_id  = request.query_params.get('record_id')
        user_id    = request.query_params.get('user_id')
        action     = request.query_params.get('action')

        if model_name:
            qs = qs.filter(model_name=model_name)
        if record_id:
            qs = qs.filter(record_id=record_id)
        if user_id:
            qs = qs.filter(changed_by_id=user_id)
        if action:
            qs = qs.filter(action=action)

        return Response({'count': qs.count(), 'results': [{
            'id': log.id,
            'model_name': log.model_name,
            'record_id': log.record_id,
            'action': log.action,
            'action_display': log.get_action_display(),
            'changed_by': log.changed_by.username if log.changed_by else 'System',
            'changed_at': log.changed_at.isoformat(),
            'old_values': log.old_values,
            'new_values': log.new_values,
            'description': log.description,
        } for log in qs[:200]]})
