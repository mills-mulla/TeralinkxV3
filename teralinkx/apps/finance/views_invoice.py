# apps/finance/views_invoice.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.core.files.base import ContentFile
from finance.models_invoice import Invoice
from finance.invoice_pdf import generate_invoice_pdf


class InvoiceListView(APIView):
    """List invoices with filtering"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        invoice_status = request.query_params.get('status')

        qs = Invoice.objects.select_related('customer', 'transaction')
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if invoice_status:
            qs = qs.filter(status=invoice_status)

        data = []
        for inv in qs[:100]:
            data.append({
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'customer': {
                    'id': inv.customer.id,
                    'account': inv.customer.account,
                    'name': inv.customer.display_name or inv.customer.user.get_full_name()
                },
                'subtotal': float(inv.subtotal),
                'vat_amount': float(inv.vat_amount),
                'total': float(inv.total),
                'issue_date': inv.issue_date.isoformat(),
                'due_date': inv.due_date.isoformat() if inv.due_date else None,
                'status': inv.status,
                'status_display': inv.get_status_display(),
                'pdf_url': request.build_absolute_uri(f'/api/finance/api/invoices/{inv.id}/pdf/') if inv.pdf_file else None,
                'created_at': inv.created_at.isoformat(),
            })

        return Response({'count': len(data), 'results': data})


class InvoiceDetailView(APIView):
    """Get invoice details"""
    permission_classes = [IsAuthenticated]

    def get(self, request, invoice_id):
        try:
            inv = Invoice.objects.select_related('customer', 'transaction').get(id=invoice_id)
            return Response({
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'customer': {
                    'id': inv.customer.id,
                    'account': inv.customer.account,
                    'name': inv.customer.display_name or inv.customer.user.get_full_name(),
                    'phone': inv.customer.phone_number,
                    'email': inv.customer.user.email,
                },
                'subtotal': float(inv.subtotal),
                'vat_rate': float(inv.vat_rate),
                'vat_amount': float(inv.vat_amount),
                'total': float(inv.total),
                'issue_date': inv.issue_date.isoformat(),
                'due_date': inv.due_date.isoformat() if inv.due_date else None,
                'status': inv.status,
                'status_display': inv.get_status_display(),
                'line_items': inv.line_items,
                'description': inv.description,
                'transaction_id': inv.transaction_id_ref or None,
                'pdf_url': request.build_absolute_uri(f'/api/finance/api/invoices/{inv.id}/pdf/'),
                'created_at': inv.created_at.isoformat(),
            })
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)


class InvoiceDownloadView(APIView):
    """Download invoice PDF"""
    permission_classes = [IsAuthenticated]

    def get(self, request, invoice_id):
        try:
            inv = Invoice.objects.get(id=invoice_id)

            # Generate PDF if not already cached
            if not inv.pdf_file:
                pdf_bytes = generate_invoice_pdf(inv)
                inv.pdf_file.save(f'{inv.invoice_number}.pdf', ContentFile(pdf_bytes), save=True)
            else:
                # Re-read from file
                inv.pdf_file.open('rb')
                pdf_bytes = inv.pdf_file.read()
                inv.pdf_file.close()

            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{inv.invoice_number}.pdf"'
            return response

        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)


class InvoiceCreateView(APIView):
    """Manually create invoice (for non-M-Pesa payments)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from users.models import ClientH
            from decimal import Decimal

            customer = ClientH.objects.get(id=request.data['customer_id'])
            subtotal = Decimal(str(request.data['subtotal']))
            vat_rate = Decimal(str(request.data.get('vat_rate', 16)))
            vat_amt  = (subtotal * vat_rate / 100).quantize(Decimal('0.01'))
            total    = subtotal + vat_amt

            line_items = request.data.get('line_items', [{
                'description': request.data.get('description', 'Internet Service'),
                'quantity': 1,
                'unit_price': float(subtotal),
                'vat_rate': float(vat_rate),
                'vat_amount': float(vat_amt),
                'total': float(total),
            }])

            inv = Invoice.objects.create(
                invoice_number = Invoice.generate_invoice_number(),
                customer       = customer,
                subtotal       = subtotal,
                vat_rate       = vat_rate,
                vat_amount     = vat_amt,
                total          = total,
                issue_date     = request.data.get('issue_date', timezone.now().date()),
                due_date       = request.data.get('due_date'),
                status         = 'issued',
                line_items     = line_items,
                description    = request.data.get('description', ''),
            )

            # Generate PDF immediately
            pdf_bytes = generate_invoice_pdf(inv)
            inv.pdf_file.save(f'{inv.invoice_number}.pdf', ContentFile(pdf_bytes), save=True)

            return Response({
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'message': 'Invoice created'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
