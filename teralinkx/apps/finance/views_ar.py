# apps/finance/views_ar.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from finance.models_ar import ARAccount, DebtCollection


def _case(c):
    return {
        'id': c.id,
        'customer': {'id': c.customer.id, 'account': c.customer.account,
                     'name': c.customer.display_name or c.customer.user.get_full_name()},
        'amount_overdue': float(c.amount_overdue),
        'days_overdue': c.days_overdue,
        'status': c.status,
        'status_display': c.get_status_display(),
        'escalation_level': c.escalation_level,
        'escalation_display': c.get_escalation_level_display(),
        'notes': c.notes,
        'created_at': c.created_at.isoformat(),
    }


class ARAgingView(APIView):
    """AR aging dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        aging = DebtCollection.get_aging_summary()
        open_cases = DebtCollection.objects.filter(status__in=['open', 'in_progress']).count()
        total_written_off = DebtCollection.objects.filter(status='written_off').count()

        return Response({
            'aging': aging,
            'open_cases': open_cases,
            'total_written_off': total_written_off,
        })


class CollectionQueueView(APIView):
    """Collection queue sorted by amount × days overdue"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cases = DebtCollection.objects.filter(
            status__in=['open', 'in_progress']
        ).select_related('customer').order_by('-amount_overdue')

        # Sort by priority score: amount × days
        data = [_case(c) for c in cases]
        data.sort(key=lambda x: x['amount_overdue'] * x['days_overdue'], reverse=True)

        return Response({'count': len(data), 'results': data})

    def post(self, request):
        """Manually create collection case"""
        try:
            from users.models import ClientH
            from decimal import Decimal
            customer = ClientH.objects.get(id=request.data['customer_id'])
            case = DebtCollection.objects.create(
                customer=customer,
                amount_overdue=Decimal(str(request.data['amount_overdue'])),
                days_overdue=int(request.data.get('days_overdue', 0)),
                notes=request.data.get('notes', ''),
            )
            return Response(_case(case), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CollectionCaseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, case_id):
        try:
            return Response(_case(DebtCollection.objects.get(id=case_id)))
        except DebtCollection.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, case_id):
        try:
            case = DebtCollection.objects.get(id=case_id)
            action = request.data.get('action')

            if action == 'escalate':
                new_level = case.escalate()
                return Response({'message': f'Escalated to {new_level}', 'escalation_level': new_level})
            elif action == 'resolve':
                case.resolve()
                return Response({'message': 'Case resolved', 'status': case.status})
            elif action == 'write_off':
                case.write_off(request.user)
                return Response({'message': 'Debt written off', 'status': case.status})
            elif action == 'add_note':
                case.notes = request.data.get('notes', case.notes)
                case.status = 'in_progress'
                case.save()
                return Response(_case(case))
            return Response({'error': 'action must be escalate, resolve, write_off, or add_note'},
                            status=status.HTTP_400_BAD_REQUEST)
        except DebtCollection.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class ARRefreshView(APIView):
    """Trigger AR account recalculation"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            created = DebtCollection.create_collection_cases()
            return Response({'message': f'Collection cases updated', 'new_cases': created})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
