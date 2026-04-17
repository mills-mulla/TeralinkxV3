# apps/finance/views_low.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from finance.models_low import (
    PaymentAllocation, SLAPolicy, OutageEvent,
    RepaymentSchedule, Branch, InsurancePolicy,
    DividendDeclaration, CLVCohort
)


# ── 6.18 Payment Allocation ───────────────────────────────────────────────────

class PaymentAllocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List unallocated payments"""
        from finance.models import TransactionQueue
        from finance.models_invoice import Invoice
        # Payments not yet allocated
        allocated_txns = PaymentAllocation.objects.values_list('transaction_id', flat=True).distinct()
        unallocated = TransactionQueue.objects.filter(
            status__in=['completed', 'processed']
        ).exclude(id__in=allocated_txns)[:50]

        return Response({'unallocated_count': unallocated.count(), 'results': [{
            'id': t.id,
            'customer': t.user.account,
            'amount': float(t.price),
            'date': t.created_at.isoformat(),
            'package': t.package,
        } for t in unallocated]})

    def post(self, request):
        """Auto-allocate a payment to invoices"""
        try:
            from finance.models import TransactionQueue
            txn = TransactionQueue.objects.get(id=request.data['transaction_id'])
            allocations, remaining = PaymentAllocation.auto_allocate(
                str(txn.id), txn.user, txn.price
            )
            return Response({
                'allocated': len(allocations),
                'remaining_unallocated': float(remaining),
                'message': f'{len(allocations)} invoices allocated'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ── 6.19 SLA Credits ──────────────────────────────────────────────────────────

class SLAPolicyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        policies = SLAPolicy.objects.filter(is_active=True)
        return Response([{
            'id': p.id, 'name': p.name,
            'uptime_guarantee_pct': float(p.uptime_guarantee_pct),
            'credit_pct_per_hour': float(p.credit_pct_per_hour),
            'max_credit_pct': float(p.max_credit_pct),
        } for p in policies])

    def post(self, request):
        try:
            from decimal import Decimal
            p = SLAPolicy.objects.create(
                name=request.data.get('name', 'Standard SLA'),
                uptime_guarantee_pct=Decimal(str(request.data.get('uptime_guarantee_pct', 99.5))),
                credit_pct_per_hour=Decimal(str(request.data.get('credit_pct_per_hour', 2.0))),
                max_credit_pct=Decimal(str(request.data.get('max_credit_pct', 30.0))),
            )
            return Response({'id': p.id, 'name': p.name}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OutageEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = OutageEvent.objects.all()[:20]
        return Response([{
            'id': e.id, 'start_time': e.start_time.isoformat(),
            'end_time': e.end_time.isoformat() if e.end_time else None,
            'duration_hours': round(e.duration_hours, 2),
            'description': e.description, 'status': e.status,
            'affected_customers': e.affected_customers.count(),
            'credits_generated': e.credits_generated,
        } for e in events])

    def post(self, request):
        try:
            event = OutageEvent.objects.create(
                start_time=request.data['start_time'],
                description=request.data.get('description', 'Network outage'),
            )
            if request.data.get('customer_ids'):
                from users.models import ClientH
                customers = ClientH.objects.filter(id__in=request.data['customer_ids'])
                event.affected_customers.set(customers)
            return Response({'id': event.id, 'status': event.status}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, event_id):
        try:
            event = OutageEvent.objects.get(id=event_id)
            action = request.data.get('action')
            if action == 'resolve':
                event.resolve(request.data.get('end_time'))
                return Response({'message': 'Outage resolved', 'duration_hours': round(event.duration_hours, 2)})
            elif action == 'generate_credits':
                count = event.generate_credits()
                return Response({'message': f'{count} credit notes generated', 'credits': count})
            return Response({'error': 'action must be resolve or generate_credits'}, status=status.HTTP_400_BAD_REQUEST)
        except OutageEvent.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# ── 6.20 Loan Repayment ───────────────────────────────────────────────────────

class RepaymentScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, investment_id):
        schedule = RepaymentSchedule.objects.filter(investment_id=investment_id)
        paid = sum(float(s.total) for s in schedule if s.status == 'paid')
        outstanding = sum(float(s.total) for s in schedule if s.status != 'paid')
        return Response({
            'total_paid': paid, 'outstanding': outstanding,
            'schedule': [{
                'id': s.id, 'installment_no': s.installment_no,
                'due_date': s.due_date.isoformat(),
                'principal': float(s.principal), 'interest': float(s.interest),
                'total': float(s.total), 'status': s.status,
                'paid_date': s.paid_date.isoformat() if s.paid_date else None,
            } for s in schedule]
        })

    def post(self, request, investment_id):
        try:
            from finance.models import Investment
            inv = Investment.objects.get(id=investment_id)
            schedules = RepaymentSchedule.generate_for_investment(inv)
            return Response({'generated': len(schedules)}, status=status.HTTP_201_CREATED)
        except Investment.DoesNotExist:
            return Response({'error': 'Investment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, investment_id):
        try:
            installment_id = request.data.get('installment_id')
            s = RepaymentSchedule.objects.get(id=installment_id, investment_id=investment_id)
            s.status = 'paid'
            s.paid_date = request.data.get('paid_date', timezone.now().date())
            s.paid_amount = request.data.get('paid_amount', s.total)
            s.save()
            return Response({'message': f'Installment {s.installment_no} marked as paid'})
        except RepaymentSchedule.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# ── 6.21 Multi-Branch ─────────────────────────────────────────────────────────

class BranchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branches = Branch.objects.filter(is_active=True)
        return Response([{
            'id': b.id, 'name': b.name, 'code': b.code,
            'location': b.location, 'is_hq': b.is_hq,
            'manager': b.manager.username if b.manager else None,
        } for b in branches])

    def post(self, request):
        try:
            b = Branch.objects.create(
                name=request.data['name'],
                code=request.data['code'],
                location=request.data.get('location', ''),
                is_hq=request.data.get('is_hq', False),
            )
            return Response({'id': b.id, 'name': b.name}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ── 6.22 Insurance ────────────────────────────────────────────────────────────

class InsurancePolicyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        policies = InsurancePolicy.objects.filter(status='active').order_by('end_date')
        expiring = [p for p in policies if p.is_expiring_soon]
        return Response({
            'expiring_soon': len(expiring),
            'policies': [{
                'id': p.id, 'provider': p.provider, 'policy_number': p.policy_number,
                'coverage_type': p.coverage_type, 'premium_amount': float(p.premium_amount),
                'start_date': p.start_date.isoformat(), 'end_date': p.end_date.isoformat(),
                'days_until_expiry': p.days_until_expiry, 'is_expiring_soon': p.is_expiring_soon,
                'status': p.status,
            } for p in policies]
        })

    def post(self, request):
        try:
            from decimal import Decimal
            p = InsurancePolicy.objects.create(
                provider=request.data['provider'],
                policy_number=request.data['policy_number'],
                coverage_type=request.data['coverage_type'],
                premium_amount=Decimal(str(request.data['premium_amount'])),
                premium_frequency=request.data.get('premium_frequency', 'annual'),
                start_date=request.data['start_date'],
                end_date=request.data['end_date'],
                assets_covered=request.data.get('assets_covered', ''),
                notes=request.data.get('notes', ''),
            )
            return Response({'id': p.id, 'provider': p.provider}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ── 6.23 Dividends ────────────────────────────────────────────────────────────

class DividendView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        declarations = DividendDeclaration.objects.all()
        return Response([{
            'id': d.id, 'period_label': d.period_label,
            'total_profit': float(d.total_profit),
            'distribution_amount': float(d.distribution_amount),
            'wht_rate': float(d.wht_rate),
            'status': d.status,
            'declared_at': d.declared_at.isoformat() if d.declared_at else None,
        } for d in declarations])

    def post(self, request):
        try:
            from decimal import Decimal
            d = DividendDeclaration.objects.create(
                period_label=request.data['period_label'],
                total_profit=Decimal(str(request.data['total_profit'])),
                distribution_amount=Decimal(str(request.data['distribution_amount'])),
                notes=request.data.get('notes', ''),
            )
            return Response({'id': d.id, 'period_label': d.period_label}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, div_id):
        try:
            d = DividendDeclaration.objects.get(id=div_id)
            if request.data.get('action') == 'approve':
                d.approve(request.user)
                return Response({'message': 'Dividend approved', 'status': d.status})
            return Response({'error': 'action must be approve'}, status=status.HTTP_400_BAD_REQUEST)
        except DividendDeclaration.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# ── 6.24 CLV Cohorts ──────────────────────────────────────────────────────────

class CLVCohortView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import date
        year = int(request.query_params.get('year', timezone.now().year))
        cohorts = {}
        for month in range(1, 13):
            cohort_date = date(year, month, 1)
            rows = CLVCohort.objects.filter(cohort_month=cohort_date).order_by('month_offset')
            if rows.exists():
                cohorts[cohort_date.strftime('%b %Y')] = [{
                    'month_offset': r.month_offset,
                    'cohort_size': r.cohort_size,
                    'active_customers': r.active_customers,
                    'retention_rate': r.retention_rate,
                    'revenue': float(r.revenue),
                    'avg_revenue_per_customer': float(r.avg_revenue_per_customer),
                    'cumulative_clv': float(r.cumulative_clv),
                } for r in rows]
        return Response({'year': year, 'cohorts': cohorts})

    def post(self, request):
        try:
            from datetime import date
            year = int(request.data.get('year', timezone.now().year))
            month = int(request.data.get('month', timezone.now().month))
            cohort_date = date(year, month, 1)
            results = CLVCohort.calculate(cohort_date)
            return Response({'calculated': len(results), 'cohort': cohort_date.strftime('%b %Y')})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
