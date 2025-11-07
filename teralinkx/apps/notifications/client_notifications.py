from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Notification
import logging

logger = logging.getLogger(__name__)

@require_GET
def get_user_notifications(request):
    # Retrieve the account number from query parameters
    account_number = request.GET.get('account')

    if account_number:
        # Filter notifications by the provided account number
        notifications = Notification.objects.filter(user=account_number).order_by('-created_at')

        notifications_data = [
            {
                'id': notification.id,
                'message': notification.message,
                'seen': notification.seen,
                'created_at': notification.created_at.isoformat(),
            }
            for notification in notifications
        ]
        return JsonResponse({'notifications': notifications_data}, status=200)
    else:
        logger.warning("Account number not provided")
        return JsonResponse({'error': 'Account number is required.'}, status=400)
