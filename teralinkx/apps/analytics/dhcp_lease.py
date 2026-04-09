# File: views/dhcp_lease.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import DHCPLease
from ..serializers.dhcp_serializer import DHCPLeaseSerializer

class DHCPLeaseListCreateView(APIView):
    def get(self, request):
        leases = DHCPLease.objects.all()
        serializer = DHCPLeaseSerializer(leases, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        try:
            lease = DHCPLease.objects.get(mac_address=data['mac_address'])
            serializer = DHCPLeaseSerializer(lease, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        except DHCPLease.DoesNotExist:
            serializer = DHCPLeaseSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)