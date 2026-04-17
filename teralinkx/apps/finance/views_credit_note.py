# apps/finance/views_credit_note.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from finance.models_credit_note import CreditNote


def _serialize(cn):
    return {
        'id': cn.id,
        'credit_note_number': cn.credit_note_number,
        'customer': {'id': cn.customer.id, 'account': cn.customer.account},
        'original_invoice': cn.original_invoice_id,
        'subtotal': float(cn.subtotal),
        'vat_amount': float(cn.vat_amount),
        'total': float(cn.total),
        'reason': cn.reason,
        'reason_display': cn.get_reason_display(),
        'description': cn.description,
        'issue_date': cn.issue_date.isoformat(),
        'status': cn.status,
        'status_display': cn.get_status_display(),
        'approved_at': cn.approved_at.isoformat() if cn.approved_at else None,
        'applied_at': cn.applied_at.isoformat() if cn.applied_at else None,
    }


class CreditNoteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = CreditNote.objects.select_related('customer')
        cn_status = request.query_params.get('status')
        if cn_status:
            qs = qs.filter(status=cn_status)
        return Response({'count': qs.count(), 'results': [_serialize(cn) for cn in qs[:100]]})

    def post(self, request):
        try:
            from users.models import ClientH
            from decimal import Decimal
            from finance.models_invoice import Invoice

            customer = ClientH.objects.get(id=request.data['customer_id'])
            invoice = None
            if request.data.get('invoice_id'):
                invoice = Invoice.objects.filter(id=request.data['invoice_id']).first()

            cn = CreditNote.create(
                customer=customer,
                amount=Decimal(str(request.data['amount'])),
                reason=request.data['reason'],
                description=request.data['description'],
                original_invoice=invoice,
            )
            return Response(_serialize(cn), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreditNoteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cn_id):
        try:
            return Response(_serialize(CreditNote.objects.get(id=cn_id)))
        except CreditNote.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, cn_id):
        try:
            cn = CreditNote.objects.get(id=cn_id)
            action = request.data.get('action')
            if action == 'approve':
                cn.approve(request.user)
                return Response({'message': 'Credit note approved', 'status': cn.status})
            elif action == 'apply':
                cn.apply_to_account()
                return Response({'message': 'Credit applied to customer balance', 'status': cn.status})
            elif action == 'void':
                cn.void()
                return Response({'message': 'Credit note voided', 'status': cn.status})
            return Response({'error': 'action must be approve, apply, or void'}, status=status.HTTP_400_BAD_REQUEST)
        except CreditNote.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
