from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum, Count
from .models import RadCheck, RadReply, RadUserGroup, RadGroupCheck, RadGroupReply, RadAcct, Nas, Voucher
from .serializers import (
    CreateUserSerializer, UserSerializer, CreateProfileSerializer, 
    ProfileSerializer, RadAcctSerializer, NasSerializer
)
from .coa import CoAClient


class UserAPIView(APIView):
    """Manage RADIUS users"""
    
    def post(self, request):
        """Create new user"""
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data.get('password', username)  # Use username as password if not provided
        profile = serializer.validated_data.get('profile')
        is_voucher = serializer.validated_data.get('is_voucher', False)
        duration_seconds = serializer.validated_data.get('duration_seconds')
        
        # Check if user exists
        if RadCheck.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create password entry
                RadCheck.objects.create(
                    username=username,
                    attribute='Cleartext-Password',
                    op=':=',
                    value=password
                )
                
                # Assign to profile if provided
                if profile:
                    if not RadGroupReply.objects.filter(groupname=profile).exists():
                        return Response({'error': f'Profile {profile} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    RadUserGroup.objects.create(
                        username=username,
                        groupname=profile,
                        priority=0
                    )
                
                # Create voucher tracking if it's a time-based voucher
                if is_voucher and duration_seconds:
                    Voucher.objects.create(
                        username=username,
                        profile=profile or 'default',
                        duration_seconds=duration_seconds,
                        is_active=True
                    )
            
            return Response({
                'message': 'User created successfully',
                'username': username,
                'profile': profile,
                'is_voucher': is_voucher,
                'duration_seconds': duration_seconds
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """List all users"""
        username = request.query_params.get('username')
        
        if username:
            # Get specific user
            users = RadCheck.objects.filter(username=username, attribute='Cleartext-Password')
            if not users.exists():
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            user = users.first()
            profile_mapping = RadUserGroup.objects.filter(username=username).first()
            
            return Response({
                'username': user.username,
                'profile': profile_mapping.groupname if profile_mapping else None
            })
        else:
            # List all users
            users = RadCheck.objects.filter(attribute='Cleartext-Password').values_list('username', flat=True).distinct()
            user_list = []
            
            for username in users:
                profile_mapping = RadUserGroup.objects.filter(username=username).first()
                user_list.append({
                    'username': username,
                    'profile': profile_mapping.groupname if profile_mapping else None
                })
            
            return Response({'users': user_list, 'count': len(user_list)})
    
    def delete(self, request):
        """Delete user"""
        username = request.query_params.get('username')
        if not username:
            return Response({'error': 'username parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                RadCheck.objects.filter(username=username).delete()
                RadReply.objects.filter(username=username).delete()
                RadUserGroup.objects.filter(username=username).delete()
            
            return Response({'message': f'User {username} deleted successfully'})
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileAPIView(APIView):
    """Manage RADIUS profiles (groups)"""
    
    def post(self, request):
        """Create new profile"""
        serializer = CreateProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        name = serializer.validated_data['name']
        upload_limit = serializer.validated_data['upload_limit']
        download_limit = serializer.validated_data['download_limit']
        session_timeout = serializer.validated_data.get('session_timeout')
        data_limit = serializer.validated_data.get('data_limit')
        
        # Check if profile exists
        if RadGroupReply.objects.filter(groupname=name).exists():
            return Response({'error': 'Profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create bandwidth limit
                RadGroupReply.objects.create(
                    groupname=name,
                    attribute='Mikrotik-Rate-Limit',
                    op='=',
                    value=f'{upload_limit}/{download_limit}'
                )
                
                # Add session timeout if provided
                if session_timeout:
                    RadGroupReply.objects.create(
                        groupname=name,
                        attribute='Session-Timeout',
                        op='=',
                        value=str(session_timeout)
                    )
                
                # Add data limit if provided (for tracking, disconnect via CoA)
                if data_limit:
                    RadGroupReply.objects.create(
                        groupname=name,
                        attribute='Mikrotik-Total-Limit',
                        op='=',
                        value=str(data_limit)
                    )
            
            return Response({
                'message': 'Profile created successfully',
                'name': name,
                'upload_limit': upload_limit,
                'download_limit': download_limit,
                'session_timeout': session_timeout,
                'data_limit': data_limit
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """List all profiles"""
        name = request.query_params.get('name')
        
        if name:
            # Get specific profile
            profiles = RadGroupReply.objects.filter(groupname=name, attribute='Mikrotik-Rate-Limit')
            if not profiles.exists():
                return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
            
            profile = profiles.first()
            rate_limit = profile.value.split('/')
            
            return Response({
                'name': profile.groupname,
                'upload_limit': rate_limit[0] if len(rate_limit) > 0 else None,
                'download_limit': rate_limit[1] if len(rate_limit) > 1 else None
            })
        else:
            # List all profiles
            profiles = RadGroupReply.objects.filter(attribute='Mikrotik-Rate-Limit')
            profile_list = []
            
            for profile in profiles:
                rate_limit = profile.value.split('/')
                profile_list.append({
                    'name': profile.groupname,
                    'upload_limit': rate_limit[0] if len(rate_limit) > 0 else None,
                    'download_limit': rate_limit[1] if len(rate_limit) > 1 else None
                })
            
            return Response({'profiles': profile_list, 'count': len(profile_list)})
    
    def delete(self, request):
        """Delete profile"""
        name = request.query_params.get('name')
        if not name:
            return Response({'error': 'name parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                RadGroupCheck.objects.filter(groupname=name).delete()
                RadGroupReply.objects.filter(groupname=name).delete()
                RadUserGroup.objects.filter(groupname=name).delete()
            
            return Response({'message': f'Profile {name} deleted successfully'})
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SessionAPIView(APIView):
    """View active sessions"""
    
    def get(self, request):
        """Get active sessions"""
        username = request.query_params.get('username')
        
        query = RadAcct.objects.filter(acctstoptime__isnull=True)
        if username:
            query = query.filter(username=username)
        
        serializer = RadAcctSerializer(query, many=True)
        return Response({'sessions': serializer.data, 'count': query.count()})


class VoucherUsageAPIView(APIView):
    """Get aggregated usage data for voucher across all sessions"""
    
    def get(self, request):
        """Get total usage for a voucher (username)"""
        username = request.query_params.get('username')
        
        if not username:
            return Response(
                {'error': 'username parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aggregate all sessions for this voucher
        sessions = RadAcct.objects.filter(username=username)
        
        if not sessions.exists():
            return Response({
                'username': username,
                'total_sessions': 0,
                'total_session_time': 0,
                'total_downloaded': 0,
                'total_uploaded': 0,
                'total_data': 0,
                'active_sessions': 0
            })
        
        # Aggregate totals
        totals = sessions.aggregate(
            total_sessions=Count('radacctid'),
            total_session_time=Sum('acctsessiontime'),
            total_downloaded=Sum('acctinputoctets'),
            total_uploaded=Sum('acctoutputoctets')
        )
        
        # Count active sessions
        active_count = sessions.filter(acctstoptime__isnull=True).count()
        
        # Calculate total data
        total_data = (totals['total_downloaded'] or 0) + (totals['total_uploaded'] or 0)
        
        return Response({
            'username': username,
            'total_sessions': totals['total_sessions'] or 0,
            'total_session_time': totals['total_session_time'] or 0,
            'total_downloaded': totals['total_downloaded'] or 0,
            'total_uploaded': totals['total_uploaded'] or 0,
            'total_data': total_data,
            'active_sessions': active_count
        })


class VoucherUsageBatchAPIView(APIView):
    """Get usage data for multiple vouchers in one request"""
    
    def post(self, request):
        """Batch get usage for multiple vouchers"""
        usernames = request.data.get('usernames', [])
        
        if not usernames or not isinstance(usernames, list):
            return Response(
                {'error': 'usernames array required in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(usernames) > 100:
            return Response(
                {'error': 'Maximum 100 usernames per batch request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        
        for username in usernames:
            # Aggregate all sessions for this voucher
            sessions = RadAcct.objects.filter(username=username)
            
            if not sessions.exists():
                results.append({
                    'username': username,
                    'total_sessions': 0,
                    'total_session_time': 0,
                    'total_downloaded': 0,
                    'total_uploaded': 0,
                    'total_data': 0,
                    'active_sessions': 0
                })
                continue
            
            # Aggregate totals
            totals = sessions.aggregate(
                total_sessions=Count('radacctid'),
                total_session_time=Sum('acctsessiontime'),
                total_downloaded=Sum('acctinputoctets'),
                total_uploaded=Sum('acctoutputoctets')
            )
            
            # Count active sessions and get their details
            active_sessions = sessions.filter(acctstoptime__isnull=True)
            active_count = active_sessions.count()
            
            # Get active session details (IP, MAC, data usage)
            active_devices = []
            for session in active_sessions:
                active_devices.append({
                    'ip_address': str(session.framedipaddress) if session.framedipaddress else None,
                    'mac_address': session.callingstationid,
                    'session_id': session.acctsessionid,
                    'login_time': session.acctstarttime.isoformat() if session.acctstarttime else None,
                    'input_octets': session.acctinputoctets or 0,
                    'output_octets': session.acctoutputoctets or 0,
                    'total_octets': (session.acctinputoctets or 0) + (session.acctoutputoctets or 0),
                    'session_time': session.acctsessiontime or 0
                })
            
            # Calculate total data
            total_data = (totals['total_downloaded'] or 0) + (totals['total_uploaded'] or 0)
            
            results.append({
                'username': username,
                'total_sessions': totals['total_sessions'] or 0,
                'total_session_time': totals['total_session_time'] or 0,
                'total_downloaded': totals['total_downloaded'] or 0,
                'total_uploaded': totals['total_uploaded'] or 0,
                'total_data': total_data,
                'active_sessions': active_count,
                'active_devices': active_devices
            })
        
        return Response({
            'count': len(results),
            'results': results
        })


class DisconnectAPIView(APIView):
    """Disconnect user sessions via CoA"""
    
    def post(self, request):
        """Disconnect user by username or session_id"""
        username = request.data.get('username')
        session_id = request.data.get('session_id')
        nas_ip = request.data.get('nas_ip')
        
        if not any([username, session_id]):
            return Response(
                {'error': 'Must provide username or session_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find active session
        query = RadAcct.objects.filter(acctstoptime__isnull=True)
        if username:
            query = query.filter(username=username)
        if session_id:
            query = query.filter(acctsessionid=session_id)
        
        session = query.first()
        if not session:
            return Response(
                {'error': 'No active session found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get NAS info
        target_nas_ip = nas_ip or str(session.nasipaddress)
        nas = Nas.objects.filter(nasname=target_nas_ip).first()
        
        if not nas:
            return Response(
                {'error': f'NAS {target_nas_ip} not found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Send CoA Disconnect
        coa = CoAClient(target_nas_ip, nas.secret)
        result = coa.disconnect_user(
            username=session.username,
            session_id=session.acctsessionid,
            framed_ip=str(session.framedipaddress) if session.framedipaddress else None
        )
        
        if result['success']:
            return Response({
                'message': result['message'],
                'username': session.username,
                'session_id': session.acctsessionid,
                'nas_ip': target_nas_ip
            })
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
