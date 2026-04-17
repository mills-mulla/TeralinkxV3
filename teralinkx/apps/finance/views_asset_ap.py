# apps/finance/views_asset_ap.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from finance.models_asset import Asset
from finance.models_ap import VendorInvoice


# ── Asset Views ───────────────────────────────────────────────────────────────

def _asset(a):
    return {
        'id': a.id,
        'asset_number': a.asset_number,
        'name': a.name,
        'category': a.category,
        'category_display': a.get_category_display(),
        'purchase_date': a.purchase_date.isoformat(),
        'purchase_cost': float(a.purchase_cost),
        'current_book_value': float(a.current_book_value),
        'accumulated_depreciation': float(a.accumulated_depreciation),
        'monthly_depreciation': float(a.monthly_depreciation),
        'useful_life_years': a.useful_life_years,
        'depreciation_method': a.depreciation_method,
        'remaining_life_months': a.remaining_life_months,
        'age_months': a.age_months,
        'department': a.department.name if a.department else None,
        'location': a.location,
        'status': a.status,
        'supplier': a.supplier,
    }


class AssetListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Asset.objects.select_related('department').filter(status='active')
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        # Summary
        total_cost = sum(float(a.purchase_cost) for a in qs)
        total_book = sum(float(a.current_book_value) for a in qs)
        monthly_dep = sum(float(a.monthly_depreciation) for a in qs)

        return Response({
            'summary': {
                'total_assets': qs.count(),
                'total_purchase_cost': total_cost,
                'total_book_value': total_book,
                'total_depreciation': total_cost - total_book,
                'monthly_depreciation_expense': monthly_dep,
            },
            'assets': [_asset(a) for a in qs]
        })

    def post(self, request):
        try:
            from finance.models import Department
            dept = Department.objects.filter(id=request.data.get('department_id')).first()
            a = Asset.objects.create(
                asset_number = Asset.generate_number(),
                name         = request.data['name'],
                category     = request.data.get('category', 'other'),
                description  = request.data.get('description', ''),
                purchase_date = request.data['purchase_date'],
                purchase_cost = request.data['purchase_cost'],
                supplier     = request.data.get('supplier', ''),
                invoice_number = request.data.get('invoice_number', ''),
                useful_life_years = int(request.data.get('useful_life_years', 5)),
                depreciation_method = request.data.get('depreciation_method', 'straight_line'),
                salvage_value = request.data.get('salvage_value', 0),
                current_book_value = request.data['purchase_cost'],
                department   = dept,
                location     = request.data.get('location', ''),
            )
            a.update_book_value()
            return Response(_asset(a), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AssetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, asset_id):
        try:
            a = Asset.objects.get(id=asset_id)
            data = _asset(a)
            data['depreciation_schedule'] = _depreciation_schedule(a)
            return Response(data)
        except Asset.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, asset_id):
        try:
            a = Asset.objects.get(id=asset_id)
            action = request.data.get('action')
            if action == 'dispose':
                from decimal import Decimal
                from datetime import date
                gain_loss = a.dispose(
                    disposal_date=date.fromisoformat(request.data['disposal_date']),
                    disposal_value=Decimal(str(request.data['disposal_value'])),
                    notes=request.data.get('notes', '')
                )
                return Response({'message': 'Asset disposed', 'gain_loss': float(gain_loss)})
            elif action == 'refresh':
                a.update_book_value()
                return Response(_asset(a))
            return Response({'error': 'action must be dispose or refresh'}, status=status.HTTP_400_BAD_REQUEST)
        except Asset.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


def _depreciation_schedule(asset, years=5):
    """Generate depreciation schedule for next N years."""
    from datetime import date
    schedule = []
    book_value = float(asset.purchase_cost)
    monthly = float(asset.monthly_depreciation)
    salvage = float(asset.salvage_value)

    for year in range(1, min(years + 1, asset.useful_life_years + 1)):
        annual_dep = min(monthly * 12, book_value - salvage)
        book_value = max(book_value - annual_dep, salvage)
        schedule.append({
            'year': year,
            'annual_depreciation': round(annual_dep, 2),
            'book_value_end': round(book_value, 2),
        })
    return schedule


# ── Accounts Payable Views ────────────────────────────────────────────────────

def _inv(i):
    return {
        'id': i.id,
        'vendor_name': i.vendor_name,
        'invoice_number': i.invoice_number,
        'subtotal': float(i.subtotal),
        'vat_amount': float(i.vat_amount),
        'total': float(i.total),
        'wht_amount': float(i.wht_amount),
        'net_payable': float(i.net_payable),
        'invoice_date': i.invoice_date.isoformat(),
        'due_date': i.due_date.isoformat(),
        'payment_date': i.payment_date.isoformat() if i.payment_date else None,
        'status': i.status,
        'status_display': i.get_status_display(),
        'is_overdue': i.is_overdue,
        'days_overdue': i.days_overdue,
        'aging_bucket': i.aging_bucket,
        'department': i.department.name if i.department else None,
        'expense_category': i.expense_category,
    }


class VendorInvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = VendorInvoice.objects.select_related('department')
        inv_status = request.query_params.get('status')
        if inv_status:
            qs = qs.filter(status=inv_status)

        aging = VendorInvoice.get_aging_summary()
        return Response({
            'aging_summary': aging,
            'invoices': [_inv(i) for i in qs[:100]]
        })

    def post(self, request):
        try:
            from finance.models import Department, Currency
            from decimal import Decimal
            dept = Department.objects.filter(id=request.data.get('department_id')).first()
            currency = Currency.objects.filter(code=request.data.get('currency', 'KES')).first()
            subtotal = Decimal(str(request.data['subtotal']))
            vat = Decimal(str(request.data.get('vat_amount', 0)))
            total = subtotal + vat

            inv = VendorInvoice.objects.create(
                vendor_name      = request.data['vendor_name'],
                vendor_pin       = request.data.get('vendor_pin', ''),
                invoice_number   = request.data['invoice_number'],
                subtotal         = subtotal,
                vat_amount       = vat,
                total            = total,
                net_payable      = total,
                currency         = currency,
                invoice_date     = request.data['invoice_date'],
                due_date         = request.data['due_date'],
                expense_category = request.data.get('expense_category', ''),
                department       = dept,
                wht_applicable   = request.data.get('wht_applicable', False),
                notes            = request.data.get('notes', ''),
            )
            return Response(_inv(inv), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VendorInvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, inv_id):
        try:
            return Response(_inv(VendorInvoice.objects.get(id=inv_id)))
        except VendorInvoice.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, inv_id):
        try:
            inv = VendorInvoice.objects.get(id=inv_id)
            action = request.data.get('action')
            if action == 'approve':
                inv.approve(request.user)
                return Response({'message': 'Invoice approved', 'status': inv.status})
            elif action == 'mark_paid':
                inv.mark_paid(request.data.get('payment_date'))
                return Response({'message': 'Invoice marked as paid', 'status': inv.status})
            elif action == 'dispute':
                inv.status = 'disputed'
                inv.notes = request.data.get('notes', inv.notes)
                inv.save()
                return Response({'message': 'Invoice disputed', 'status': inv.status})
            return Response({'error': 'action must be approve, mark_paid, or dispute'},
                            status=status.HTTP_400_BAD_REQUEST)
        except VendorInvoice.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class APAgingView(APIView):
    """AP aging dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        aging = VendorInvoice.get_aging_summary()
        overdue = VendorInvoice.objects.filter(status__in=['received', 'approved'])
        overdue = [_inv(i) for i in overdue if i.is_overdue]
        return Response({
            'aging': aging,
            'overdue_invoices': overdue,
            'overdue_count': len(overdue),
        })
