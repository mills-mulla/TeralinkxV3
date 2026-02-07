# apps/users/dashboard.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from users.models import ClientH
from packages.models import PackageType, DispatchVoucher
from notifications.models import Notification
from core.serializers.package_serializer import PackageTypeSerializer, DispatchVoucherSerializer


class DashboardAPIView(APIView):
    """
    Unified dashboard API that consolidates all dashboard data in a single call.
    Replaces multiple separate API calls with one efficient endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all dashboard data for authenticated user:
        - Client info (account, balance, status, profile image)
        - Active vouchers
        - Available packages
        - Recent notifications
        """
        try:
            user = request.user
            
            # Get client profile
            try:
                client = user.client_profile
            except ClientH.DoesNotExist:
                return Response(
                    {"error": "Client profile not found for authenticated user"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 1. CLIENT DATA (matching get_client response structure)
            client_data = {
                "acc_no": client.account,
                "phone_number": user.username,  # Add phone number
                "acc_bal": {
                    "source": str(client.balance),
                    "parsedValue": float(client.balance)
                },
                "balance_status": client.balance_status,  # Add balance status
                "acc_stat": client.status,
                "client": client.display_name or client.account,
                "image": None
            }
            
            # Add profile image if exists
            if client.profile_image:
                client_data["image"] = request.build_absolute_uri(client.profile_image.url)
            
            # 2. VOUCHERS DATA (active and expired dispatch vouchers with limits)
            all_vouchers = DispatchVoucher.objects.filter(
                user=user
            ).order_by('-created_at')
            
            # Update statuses for all vouchers
            for voucher in all_vouchers:
                voucher.update_status()
                voucher.save(update_fields=['status'])
            
            # Separate active and expired vouchers with time filter
            active_vouchers = all_vouchers.filter(status='active')[:4]  # Limit to 4 active
            
            # Only show expired vouchers from the last 1 hour
            one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
            expired_vouchers = all_vouchers.exclude(status='active').filter(
                expires_at__gte=one_hour_ago
            )[:2]  # Limit to 2 recent expired
            
            # Combine for display (active first, then expired)
            display_vouchers = list(active_vouchers) + list(expired_vouchers)
            
            vouchers_data = []
            for voucher in display_vouchers:
                # Calculate total usage
                total_usage_bytes = voucher.download_bytes + voucher.upload_bytes
                
                # Get data limit from package
                data_limit_mb = voucher.package.data_limit_mb
                data_limit_bytes = data_limit_mb * 1024 * 1024 if data_limit_mb else None
                
                # Use computed status for accurate status determination
                computed_status = voucher.computed_status
                is_expired = computed_status in ['expired', 'exhausted']
                
                # Get active sessions for this voucher (only if active)
                active_sessions = []
                current_device_session = None
                
                if computed_status == 'active':
                    from users.models import UserSession
                    import logging
                    logger = logging.getLogger(__name__)
                    
                    active_sessions = UserSession.objects.filter(
                        user=client,
                        active_voucher=voucher.voucher_code,
                        session_type='network',
                        is_active=True
                    )
                    
                    # Get real client IP (handle proxy/docker)
                    request_ip = request.META.get('HTTP_X_FORWARDED_FOR')
                    if request_ip:
                        request_ip = request_ip.split(',')[0].strip()
                    else:
                        request_ip = request.META.get('REMOTE_ADDR')
                    
                    request_mac = request.META.get('HTTP_X_MAC_ADDRESS')
                    
                    logger.info(f"Checking device match for voucher {voucher.voucher_code}")
                    logger.info(f"Request IP: {request_ip}, Request MAC: {request_mac}")
                    logger.info(f"Active sessions: {active_sessions.count()}")
                    
                    for session in active_sessions:
                        logger.info(f"Session IP: {session.ip_address}, Device MAC: {session.device.mac_address}")
                        # Match by IP or MAC
                        if session.ip_address == request_ip:
                            current_device_session = session
                            logger.info(f"✓ Matched by IP: {request_ip}")
                            break
                        if request_mac and session.device.mac_address == request_mac:
                            current_device_session = session
                            logger.info(f"✓ Matched by MAC: {request_mac}")
                            break
                
                voucher_data = {
                    "id": voucher.id,
                    "voucher_code": voucher.voucher_code,
                    "package_name": voucher.package.name if voucher.package else "Unknown Package",
                    "dispatch_status": computed_status,
                    "is_expired": is_expired,
                    "expires_at": voucher.expires_at.isoformat() if voucher.expires_at else None,
                    "activated_at": voucher.activated_at.isoformat() if voucher.activated_at else None,
                    "is_roaming": voucher.is_roaming,
                    "location": str(voucher.location) if voucher.location else None,
                    # Usage data
                    "usage": {
                        "download_bytes": voucher.download_bytes,
                        "upload_bytes": voucher.upload_bytes,
                        "total_bytes": total_usage_bytes,
                        "data_limit_bytes": data_limit_bytes,
                        "data_limit_mb": data_limit_mb,
                        "is_unlimited": data_limit_mb is None,
                        "usage_percentage": (total_usage_bytes / data_limit_bytes * 100) if data_limit_bytes else 0
                    },
                    # Session data (only for active vouchers)
                    "sessions": {
                        "current_sessions": voucher.session_count,
                        "device_limit": voucher.package.device_limit,
                        "can_add_session": voucher.session_count < voucher.package.device_limit and computed_status == 'active',
                        "is_session_limit_reached": voucher.session_count >= voucher.package.device_limit,
                        "is_current_device_connected": current_device_session is not None,
                        "current_session_id": current_device_session.session_id if current_device_session else None,
                        "active_devices": [
                            {
                                "device_name": session.device.device_name,
                                "device_type": session.device.device_type,
                                "device_platform": session.device.device_platform,
                                "device_manufacturer": session.device.device_manufacturer,
                                "device_model": session.device.device_model,
                                "mac_address": session.device.mac_address,
                                "ip_address": session.ip_address,
                                "login_time": session.login_time.isoformat(),
                                "session_id": session.session_id,
                                "is_current_device": session == current_device_session
                            } for session in active_sessions
                        ] if computed_status == 'active' else []
                    }
                }
                vouchers_data.append(voucher_data)
            
            # 3. PACKAGES DATA (available packages)
            packages = PackageType.objects.filter(
                is_active=True,
                is_public=True
            ).order_by('-is_featured', 'display_order', 'tier', 'price')
            
            packages_data = []
            for package in packages:
                package_data = {
                    "id": package.id,
                    "name": package.name,
                    "code": package.code,
                    "description": package.description,
                    "price": {
                        "source": str(package.price),
                        "parsedValue": float(package.price)
                    },
                    "tier": package.tier,
                    "category": package.category,
                    "is_featured": package.is_featured,
                    "duration_days": package.duration.days if package.duration else 0,
                    "duration_hours": int(package.duration.total_seconds() / 3600) if package.duration else 0,
                    "duration_minutes": int(package.duration.total_seconds() / 60) if package.duration else 0,
                    "data_limit_mb": package.data_limit_mb,
                    "speed_limit_mbps": package.speed_limit_mbps,
                    "device_limit": package.device_limit,
                    "is_unlimited": package.is_unlimited,
                }
                packages_data.append(package_data)
            
            # 4. NOTIFICATIONS DATA (recent unread notifications)
            notifications = Notification.objects.filter(
                Q(user=user) | Q(client=client) | Q(scope='global'),
                is_read=False,
                is_archived=False
            ).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now())
            ).order_by('-created_at')[:10]  # Limit to 10 most recent
            
            notifications_data = []
            for notification in notifications:
                notification_data = {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "priority": notification.priority,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                    "action_url": notification.action_url,
                    "action_text": notification.action_text,
                    "icon": notification.icon,
                }
                notifications_data.append(notification_data)
            
            # 5. CONSOLIDATED RESPONSE
            dashboard_data = {
                "client": client_data,
                "vouchers": vouchers_data,
                "packages": packages_data,
                "notifications": notifications_data,
                "metadata": {
                    "user": user.username,
                    "client_id": str(client.id),
                    "last_updated": timezone.now().isoformat(),
                    "vouchers_count": len(vouchers_data),
                    "packages_count": len(packages_data),
                    "unread_notifications": len(notifications_data),
                }
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    "error": "Failed to load dashboard data",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )