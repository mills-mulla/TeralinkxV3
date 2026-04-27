# views/user_views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q, Count
from users.models import ClientH, UserDevice, UserSession
from ..serializers.user_serializers import (
    DjangoUserSerializer, 
    UserDeviceSerializer, 
    UserSessionSerializer
)
import logging

logger = logging.getLogger(__name__)


class DjangoUserViewSet(viewsets.ModelViewSet):
    """ViewSet for Django User model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all().select_related('client_profile')
    serializer_class = DjangoUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['id', 'username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        try:
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            staff_users = User.objects.filter(is_staff=True).count()
            superusers = User.objects.filter(is_superuser=True).count()
            
            return Response({
                'total_users': total_users,
                'active_users': active_users,
                'staff_users': staff_users,
                'superusers': superusers,
                'inactive_users': total_users - active_users
            })
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def all_groups(self, request):
        """List all available groups"""
        groups = Group.objects.all().values('id', 'name')
        return Response(list(groups))

    @action(detail=False, methods=['get'])
    def all_permissions(self, request):
        """List all permissions grouped by app"""
        key_apps = ['finance', 'users', 'packages', 'locations', 'analytics']
        perms = Permission.objects.filter(
            content_type__app_label__in=key_apps
        ).values(
            'id', 'codename', 'content_type__app_label', 'content_type__model'
        ).order_by('content_type__app_label', 'content_type__model', 'codename')
        # Group by app
        grouped = {}
        for p in perms:
            app = p['content_type__app_label']
            if app not in grouped:
                grouped[app] = []
            grouped[app].append(p)
        return Response(grouped)

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset user password"""
        user = self.get_object()
        new_password = request.data.get('password')
        if not new_password:
            return Response({'error': 'Password required'}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({'status': 'password reset successfully'})


class UserDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for UserDevice model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = UserDevice.objects.all().select_related('user', 'last_seen_location')
    serializer_class = UserDeviceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['mac_address', 'device_name', 'user__account', 'device_model']
    ordering_fields = ['id', 'last_seen', 'total_connections', 'created']
    ordering = ['-last_seen']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by user
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by online status
        online_only = self.request.query_params.get('online_only', None)
        if online_only == 'true':
            queryset = [d for d in queryset if d.is_online]
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get device statistics"""
        try:
            total_devices = UserDevice.objects.count()
            active_devices = UserDevice.objects.filter(status='active').count()
            trusted_devices = UserDevice.objects.filter(is_trusted=True).count()
            
            # Count online devices based on active network sessions
            # Get unique device MACs from active network sessions
            online_device_macs = UserSession.objects.filter(
                is_active=True,
                session_type='network'
            ).values_list('device__mac_address', flat=True).distinct()
            online_devices = len([mac for mac in online_device_macs if mac])
            
            # Devices by type
            devices_by_type = UserDevice.objects.values('device_type').annotate(
                count=Count('id')
            )
            
            return Response({
                'total_devices': total_devices,
                'active_devices': active_devices,
                'online_devices': online_devices,
                'trusted_devices': trusted_devices,
                'devices_by_type': list(devices_by_type)
            })
        except Exception as e:
            logger.error(f"Error fetching device stats: {e}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block a device"""
        device = self.get_object()
        reason = request.data.get('reason', 'Admin action')
        
        try:
            device.block_device(reason=reason)
            return Response({'message': 'Device blocked successfully'})
        except Exception as e:
            logger.error(f"Error blocking device: {e}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Unblock a device"""
        device = self.get_object()
        reason = request.data.get('reason', 'Admin request')
        
        try:
            device.unblock_device(reason=reason)
            return Response({'message': 'Device unblocked successfully'})
        except Exception as e:
            logger.error(f"Error unblocking device: {e}")
            return Response({'error': str(e)}, status=500)


class UserSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for UserSession model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = UserSession.objects.all().select_related('user', 'device', 'location')
    serializer_class = UserSessionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['session_id', 'user__account', 'device__device_name', 'ip_address']
    ordering_fields = ['id', 'login_time', 'last_activity']
    ordering = ['-last_activity']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by user
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by device
        device_id = self.request.query_params.get('device_id', None)
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get session statistics"""
        try:
            total_sessions = UserSession.objects.count()
            active_sessions = UserSession.objects.filter(is_active=True).count()
            voucher_sessions = UserSession.objects.filter(
                is_active=True, 
                active_voucher__isnull=False
            ).exclude(active_voucher='').count()
            
            return Response({
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'voucher_sessions': voucher_sessions,
                'inactive_sessions': total_sessions - active_sessions
            })
        except Exception as e:
            logger.error(f"Error fetching session stats: {e}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a session"""
        session = self.get_object()
        reason = request.data.get('reason', 'Admin action')
        try:
            session.terminate(reason=reason)
            return Response({'message': 'Session terminated successfully'})
        except Exception as e:
            logger.error(f"Error terminating session: {e}")
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        sessions = UserSession.objects.filter(id__in=ids)
        if action == 'terminate':
            for s in sessions:
                try: s.terminate(reason='Bulk admin action')
                except: s.is_active = False; s.save(update_fields=['is_active'])
        elif action == 'deactivate_vouchers':
            sessions.update(active_voucher=None)
        elif action == 'extend_voucher':
            from django.utils import timezone
            from datetime import timedelta
            from packages.models import DispatchVoucher
            for s in sessions:
                if s.active_voucher:
                    try:
                        v = DispatchVoucher.objects.get(voucher_code=s.active_voucher)
                        v.expires_at += timedelta(hours=1)
                        v.save(update_fields=['expires_at'])
                    except: pass
        else:
            return Response({'error': 'Invalid action'}, status=400)
        return Response({'updated': len(ids)})
