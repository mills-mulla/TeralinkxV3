# File: views/usage.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from ..models import ActiveUser
from ..utils.format_utils import format_bytes

def get_live_usage(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            voucher = data.get("dispatch_voucher_code")
            user = get_object_or_404(ActiveUser, username=voucher)
            formatted_usage = format_bytes(int(user.bytes_out))
            return JsonResponse({
                "dispatch_voucher_code": voucher,
                "dispatch_usage": formatted_usage
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)