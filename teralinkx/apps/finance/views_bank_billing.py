# apps/finance/views_bank_billing.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from finance.models_bank_import import BankStatement, BankStatementEntry, BankStatementParser
from finance.models_billing import RecurringBilling


# ── Bank Statement Import ─────────────────────────────────────────────────────

class BankStatementUploadView(APIView):
    """Upload and parse a bank statement CSV"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        statements = BankStatement.objects.all()[:20]
        return Response({'count': statements.count(), 'results': [{
            'id': s.id,
            'bank': s.bank,
            'bank_display': s.get_bank_display(),
            'filename': s.filename,
            'status': s.status,
            'total_entries': s.total_entries,
            'parsed_entries': s.parsed_entries,
            'period_start': s.period_start.isoformat() if s.period_start else None,
            'period_end': s.period_end.isoformat() if s.period_end else None,
            'created_at': s.created_at.isoformat(),
        } for s in statements]})

    def post(self, request):
        try:
            bank = request.data.get('bank', 'other')
            file_obj = request.FILES.get('file')

            if not file_obj:
                # Accept raw CSV content for API testing
                csv_content = request.data.get('csv_content', '')
                filename = request.data.get('filename', 'statement.csv')
            else:
                csv_content = file_obj.read().decode('utf-8', errors='ignore')
                filename = file_obj.name

            if not csv_content:
                return Response({'error': 'No file or csv_content provided'},
                                status=status.HTTP_400_BAD_REQUEST)

            statement = BankStatement.objects.create(
                bank=bank,
                filename=filename,
                uploaded_by=request.user,
                status='uploaded',
            )

            count = BankStatementParser.parse(statement, csv_content)

            # Auto-trigger reconciliation
            if count > 0:
                from finance.reconciliation_service import reconcile_payments
                if statement.period_start and statement.period_end:
                    try:
                        entries = BankStatementEntry.objects.filter(statement=statement, credit__gt=0)
                        source_items = [{
                            'reference': e.reference or e.description[:50],
                            'amount': float(e.credit),
                            'date': e.transaction_date.isoformat(),
                            'customer_info': e.description,
                        } for e in entries]

                        job = reconcile_payments(
                            period_start=statement.period_start,
                            period_end=statement.period_end,
                            source_items=source_items,
                        )
                        statement.status = 'completed'
                        statement.save()
                        return Response({
                            'statement_id': statement.id,
                            'entries_parsed': count,
                            'reconciliation_job': job.job_id,
                            'auto_match_rate': job.auto_match_rate,
                        }, status=status.HTTP_201_CREATED)
                    except Exception:
                        pass

            return Response({
                'statement_id': statement.id,
                'entries_parsed': count,
                'message': 'Statement parsed. Trigger reconciliation manually.'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BankStatementEntriesView(APIView):
    """List entries from a bank statement"""
    permission_classes = [IsAuthenticated]

    def get(self, request, statement_id):
        try:
            statement = BankStatement.objects.get(id=statement_id)
            entries = statement.entries.all()
            return Response({
                'statement': statement.filename,
                'count': entries.count(),
                'entries': [{
                    'id': e.id,
                    'date': e.transaction_date.isoformat(),
                    'description': e.description,
                    'reference': e.reference,
                    'debit': float(e.debit),
                    'credit': float(e.credit),
                    'balance': float(e.balance) if e.balance else None,
                    'is_reconciled': e.is_reconciled,
                } for e in entries[:200]]
            })
        except BankStatement.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# ── Recurring Billing ─────────────────────────────────────────────────────────

class RecurringBillingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        billings = RecurringBilling.objects.select_related('customer').all()
        bill_status = request.query_params.get('status')
        if bill_status:
            billings = billings.filter(status=bill_status)

        return Response({'count': billings.count(), 'results': [{
            'id': b.id,
            'customer': b.customer.account,
            'package_name': b.package_name,
            'amount': float(b.amount),
            'billing_day': b.billing_day,
            'next_billing_date': b.next_billing_date.isoformat(),
            'status': b.status,
            'status_display': b.get_status_display(),
            'retry_count': b.retry_count,
            'last_billed_at': b.last_billed_at.isoformat() if b.last_billed_at else None,
            'failure_reason': b.failure_reason,
        } for b in billings]})

    def post(self, request):
        try:
            from users.models import ClientH
            from decimal import Decimal
            from datetime import date
            customer = ClientH.objects.get(id=request.data['customer_id'])
            billing_day = int(request.data.get('billing_day', 1))
            today = date.today()
            import calendar
            max_day = calendar.monthrange(today.year, today.month)[1]
            next_date = date(today.year, today.month, min(billing_day, max_day))
            if next_date <= today:
                next_month = today.month + 1 if today.month < 12 else 1
                next_year = today.year if today.month < 12 else today.year + 1
                max_day = calendar.monthrange(next_year, next_month)[1]
                next_date = date(next_year, next_month, min(billing_day, max_day))

            billing, created = RecurringBilling.objects.update_or_create(
                customer=customer,
                defaults={
                    'package_name': request.data['package_name'],
                    'package_code': request.data.get('package_code', ''),
                    'amount': Decimal(str(request.data['amount'])),
                    'billing_day': billing_day,
                    'next_billing_date': next_date,
                    'status': 'active',
                }
            )
            return Response({
                'id': billing.id,
                'customer': customer.account,
                'next_billing_date': billing.next_billing_date.isoformat(),
                'created': created,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RecurringBillingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, billing_id):
        try:
            billing = RecurringBilling.objects.get(id=billing_id)
            action = request.data.get('action')
            if action == 'pause':
                billing.status = 'paused'
                billing.save()
                return Response({'message': 'Billing paused'})
            elif action == 'resume':
                billing.status = 'active'
                billing.retry_count = 0
                billing.save()
                return Response({'message': 'Billing resumed'})
            elif action == 'cancel':
                billing.status = 'cancelled'
                billing.save()
                return Response({'message': 'Billing cancelled'})
            return Response({'error': 'action must be pause, resume, or cancel'},
                            status=status.HTTP_400_BAD_REQUEST)
        except RecurringBilling.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class ProcessBillingView(APIView):
    """Manually trigger billing run"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            success, failed = RecurringBilling.process_due_billings()
            return Response({'success': success, 'failed': failed,
                             'message': f'{success} billed, {failed} failed'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
