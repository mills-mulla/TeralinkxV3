# apps/finance/views_reminder.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from finance.models_reminder import PaymentReminder


class ReminderListView(APIView):
    """List payment reminders"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = PaymentReminder.objects.select_related('customer').order_by('-scheduled_at')
        rem_status = request.query_params.get('status')
        if rem_status:
            qs = qs.filter(status=rem_status)

        data = [{
            'id': r.id,
            'customer': r.customer.account,
            'reminder_type': r.reminder_type,
            'reminder_type_display': r.get_reminder_type_display(),
            'scheduled_at': r.scheduled_at.isoformat(),
            'sent_at': r.sent_at.isoformat() if r.sent_at else None,
            'status': r.status,
            'message': r.message,
            'phone_number': r.phone_number,
        } for r in qs[:100]]

        return Response({'count': len(data), 'results': data})


class ReminderStatsView(APIView):
    """Reminder delivery statistics"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        last_30 = timezone.now() - timezone.timedelta(days=30)
        qs = PaymentReminder.objects.filter(scheduled_at__gte=last_30)

        return Response({
            'last_30_days': {
                'total': qs.count(),
                'sent': qs.filter(status='sent').count(),
                'failed': qs.filter(status='failed').count(),
                'pending': qs.filter(status='pending').count(),
            }
        })
