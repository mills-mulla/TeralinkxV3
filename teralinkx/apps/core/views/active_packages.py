# File: views/active_packages.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import DispatchVoucher
from ..serializers.dispatch_serializer import DispatchSerializer
import logging
# Setup logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Show logs in the console
    ]
)

class ActivePackages(APIView):
    def post(self, request):
        acc = request.data.get('account')
        logging.info(acc)
        active = DispatchVoucher.objects.filter(dispatch_account=acc)

        if active.exists():
            try:
                serializer = DispatchSerializer(active, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "No active subscriptions found."}, status=status.HTTP_404_NOT_FOUND)