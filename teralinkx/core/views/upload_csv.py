# File: views/upload_csv.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal, InvalidOperation
import json, logging
from ..models import AvailableVoucher
from ..utils.format_utils import parse_duration

class UploadCSVView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            vouchers_data_json = request.data.get('data')
            if not vouchers_data_json:
                return Response({'success': False, 'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                vouchers_data = json.loads(vouchers_data_json)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                return Response({'success': False, 'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)

            for voucher in vouchers_data:
                code = voucher.get('voucher_code')
                if not code:
                    continue

                try:
                    price = Decimal(voucher.get('price')) if voucher.get('price') else None
                except InvalidOperation:
                    return Response({'success': False, 'error': f'Invalid price for {code}'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    AvailableVoucher.objects.create(
                        voucher_code=code,
                        package=voucher.get('package', '').strip(),
                        package_desc=voucher.get('package_desc', '').strip(),
                        duration=parse_duration(voucher.get('duration')),
                        price=price
                    )
                except Exception as e:
                    return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': True}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return Response({'success': False, 'error': f'Unexpected error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)