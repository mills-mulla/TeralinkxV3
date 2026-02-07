from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
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
