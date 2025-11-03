from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

from apps.core.models import TimeStampedModel

User = get_user_model()

class Notification(TimeStampedModel):
    """Advanced notification system with multiple channels"""
    NOTIFICATION_TYPES = [
        ('system', 'System Notification'),
        ('billing', 'Billing & Payment'),
        ('security', 'Security Alert'),
        ('promotional', 'Promotional'),
        ('maintenance', 'Maintenance Alert'),
        ('usage', 'Usage Alert'),
        ('voucher', 'Voucher Notification'),
        ('roaming', 'Roaming Notification'),
        ('package_expiry', 'Package Expiry'),
        ('low_balance', 'Low Balance Alert'),
        ('data_exhausted', 'Data Exhausted'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CHANNELS = [
        ('in_app', 'In-App Persistent'),  # Bell icon notifications
        ('alert', 'Real-time Alert'),     # Temporary popups
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('all', 'All Channels'),
    ]
    
    SCOPE_CHOICES = [
        ('user', 'User Specific'),      # For individual user
        ('client', 'Client Specific'),  # For all users of a client
        ('global', 'Global'),           # For all users system-wide
    ]
    
    # Recipient Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    client = models.ForeignKey('users.ClientH', on_delete=models.CASCADE, null=True, blank=True, related_name="client_notifications")
    
    # NEW: Notification Scope & Targeting
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='user')
    is_broadcast = models.BooleanField(default=False, help_text="Send to multiple users")
    target_audience = models.JSONField(default=list, help_text="Target specific user segments")
    target_locations = models.ManyToManyField('locations.Location', blank=True)
    target_packages = models.ManyToManyField('packages.PackageType', blank=True)
    
    # Notification Content
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    title = models.CharField(max_length=255)
    message = models.TextField()
    short_message = models.CharField(max_length=160, blank=True, help_text="Short version for SMS/push")
    
    # NEW: Real-time & Persistence Settings
    is_persistent = models.BooleanField(default=True, help_text="Stay in notifications until manually dismissed")
    auto_dismiss_seconds = models.IntegerField(null=True, blank=True, help_text="Auto dismiss after X seconds (for alerts)")
    
    # NEW: Pusher Integration Fields
    pusher_channel = models.CharField(max_length=100, blank=True, help_text="Pusher channel name")
    pusher_event = models.CharField(max_length=100, blank=True, help_text="Pusher event name")
    
    # Delivery Configuration
    channels = models.JSONField(default=list, help_text="List of channels to deliver through")
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="Schedule for future delivery")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Notification expiration")
    
    # Status Tracking
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery Status
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    in_app_delivered = models.BooleanField(default=False)
    pusher_sent = models.BooleanField(default=False)  # NEW: Pusher delivery status
    
    # Action & Context
    action_url = models.URLField(blank=True, help_text="URL for action button")
    action_text = models.CharField(max_length=50, blank=True, help_text="Text for action button")
    context_data = models.JSONField(default=dict, help_text="Additional context data")
    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # NEW: Client-specific context
    client_context = models.JSONField(default=dict, help_text="Client-specific data like location, package, etc.")
    
    # NEW: Real-time notification specific
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name for UI display")
    badge = models.CharField(max_length=20, blank=True, help_text="Badge text/count")
    vibration_pattern = models.JSONField(default=list, help_text="Vibration pattern for mobile")
    
    # Metadata
    source = models.CharField(max_length=100, default='system', help_text="Source system/module")
    template_id = models.CharField(max_length=100, blank=True, help_text="Template identifier")
    
    def __str__(self):
        if self.scope == 'client' and self.client:
            return f"{self.title} - {self.client.name}"
        elif self.user:
            return f"{self.title} - {self.user.username}"
        else:
            return f"{self.title} - {self.get_scope_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-generate Pusher channel/event if not provided"""
        if not self.pusher_channel:
            if self.user:
                self.pusher_channel = f"private-user-{self.user.id}"
            elif self.client:
                self.pusher_channel = f"private-client-{self.client.id}"
            elif self.scope == 'global':
                self.pusher_channel = "global-notifications"
        
        if not self.pusher_event:
            self.pusher_event = "new-notification"
        
        # Set appropriate channels based on persistence
        if not self.is_persistent and 'in_app' in self.channels:
            self.channels = [ch if ch != 'in_app' else 'alert' for ch in self.channels]
        
        super().save(*args, **kwargs)
    
    @property
    def is_scheduled(self):
        """Check if notification is scheduled for future delivery"""
        return self.scheduled_for and self.scheduled_for > timezone.now()
    
    @property
    def is_expired(self):
        """Check if notification is expired"""
        return self.expires_at and self.expires_at < timezone.now()
    
    @property
    def can_send(self):
        """Check if notification can be sent"""
        return not self.is_sent and not self.is_scheduled and not self.is_expired
    
    @property
    def is_for_current_client(self, client_id):
        """Check if notification is relevant for specific client"""
        if self.scope == 'global':
            return True
        elif self.scope == 'client':
            return str(self.client.id) == str(client_id)
        elif self.scope == 'user' and self.client:
            return str(self.client.id) == str(client_id)
        return True
    
    def mark_as_sent(self, channel=None):
        """Mark notification as sent for specific channel"""
        self.is_sent = True
        self.sent_at = timezone.now()
        
        if channel == 'email':
            self.email_sent = True
        elif channel == 'sms':
            self.sms_sent = True
        elif channel == 'push':
            self.push_sent = True
        elif channel == 'in_app':
            self.in_app_delivered = True
        elif channel == 'pusher':
            self.pusher_sent = True
        
        self.save()
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
        
        # Send real-time update when notification is read
        self._send_pusher_update('notification-read')
    
    def mark_as_archived(self):
        """Mark notification as archived"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save()
    
    def deliver(self):
        """Deliver notification through configured channels"""
        if not self.can_send:
            return False
        
        from .services.notification_service import NotificationService
        success = NotificationService.deliver_notification(self)
        
        if success:
            self.mark_as_sent('all')
        
        return success
    
    def send_via_pusher(self):
        """Send real-time notification via Pusher"""
        try:
            import pusher
            
            pusher_client = pusher.Pusher(
                app_id='your-app-id',
                key='your-key',
                secret='your-secret',
                cluster='your-cluster',
                ssl=True
            )
            
            pusher_data = {
                'id': self.id,
                'title': self.title,
                'message': self.short_message or self.message,
                'type': self.notification_type,
                'priority': self.priority,
                'scope': self.scope,
                'client_id': str(self.client.id) if self.client else None,
                'is_persistent': self.is_persistent,
                'auto_dismiss_seconds': self.auto_dismiss_seconds,
                'action_url': self.action_url,
                'action_text': self.action_text,
                'icon': self.icon,
                'badge': self.badge,
                'created_at': self.created_at.isoformat(),
                'client_context': self.client_context,
            }
            
            pusher_client.trigger(
                self.pusher_channel,
                self.pusher_event,
                pusher_data
            )
            
            self.mark_as_sent('pusher')
            return True
            
        except Exception as e:
            print(f"Pusher error: {e}")
            return False
    
    def _send_pusher_update(self, event_type):
        """Send real-time updates for notification changes"""
        try:
            import pusher
            
            pusher_client = pusher.Pusher(
                app_id='your-app-id',
                key='your-key',
                secret='your-secret',
                cluster='your-cluster',
                ssl=True
            )
            
            update_data = {
                'notification_id': self.id,
                'event_type': event_type,
                'timestamp': timezone.now().isoformat(),
                'client_id': str(self.client.id) if self.client else None,
            }
            
            pusher_client.trigger(
                self.pusher_channel,
                'notification-updated',
                update_data
            )
            
        except Exception as e:
            print(f"Pusher update error: {e}")
    
    def get_delivery_status(self):
        """Get delivery status across all channels"""
        status = {
            'email': self.email_sent,
            'sms': self.sms_sent,
            'push': self.push_sent,
            'in_app': self.in_app_delivered,
            'pusher': self.pusher_sent,
            'overall': self.is_sent,
        }
        
        return status
    
    @classmethod
    def send_instant_notification(cls, user, title, message, notification_type='system', priority='medium', channels=None, client=None, is_persistent=True):
        """Send instant notification to user"""
        if channels is None:
            channels = ['in_app', 'pusher'] if is_persistent else ['alert', 'pusher']
        
        notification = cls.objects.create(
            user=user,
            client=client,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            channels=channels,
            is_persistent=is_persistent,
            scope='user' if user else 'client'
        )
        
        return notification.deliver()
    
    @classmethod
    def send_client_notification(cls, client, title, message, notification_type='system', target_locations=None, target_packages=None):
        """Send notification to all users of a specific client"""
        notification = cls.objects.create(
            client=client,
            title=title,
            message=message,
            notification_type=notification_type,
            scope='client',
            channels=['in_app', 'pusher'],
            is_persistent=True,
            target_locations=target_locations or [],
            target_packages=target_packages or []
        )
        
        # Handle client-wide delivery logic
        return notification.deliver()
    
    @classmethod
    def send_broadcast_notification(cls, title, message, notification_type='system', target_audience=None):
        """Send broadcast notification to all users or specific audience"""
        notification = cls.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            is_broadcast=True,
            scope='global',
            target_audience=target_audience or [],
            channels=['in_app', 'pusher'],
            is_persistent=True
        )
        
        return notification.deliver()
    
    @classmethod
    def send_bulk_notification(cls, users, title, message, notification_type='system', priority='medium', client=None):
        """Send bulk notification to multiple users"""
        notifications = []
        for user in users:
            notification = cls(
                user=user,
                client=client,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                channels=['in_app', 'pusher'],
                is_persistent=True,
                scope='user'
            )
            notifications.append(notification)
        
        cls.objects.bulk_create(notifications)
        
        # Deliver notifications
        for notification in notifications:
            notification.deliver()
        
        return len(notifications)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['client', 'created_at']),
            models.Index(fields=['scope', 'created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_sent']),
            models.Index(fields=['is_read']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_persistent']),
            models.Index(fields=['is_broadcast']),
            models.Index(fields=['pusher_sent']),
        ]
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"


class NotificationTemplate(TimeStampedModel):
    """Reusable notification templates"""
    TEMPLATE_TYPES = [
        ('email', 'Email Template'),
        ('sms', 'SMS Template'),
        ('push', 'Push Template'),
        ('in_app', 'In-App Template'),
        ('pusher', 'Pusher Template'),
        ('alert', 'Alert Template'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=10, choices=TEMPLATE_TYPES)
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    
    # Template Content
    subject = models.CharField(max_length=255, blank=True, help_text="Email subject or push title")
    message_template = models.TextField(help_text="Template with {{ variables }}")
    short_template = models.TextField(blank=True, help_text="Short version for SMS/push")
    
    # NEW: Pusher-specific template fields
    pusher_template = models.JSONField(default=dict, help_text="Pusher message structure")
    
    # Configuration
    is_active = models.BooleanField(default=True)
    default_priority = models.CharField(max_length=10, choices=Notification.PRIORITY_LEVELS, default='medium')
    default_channels = models.JSONField(default=list)
    
    # NEW: Persistence settings
    default_persistent = models.BooleanField(default=True)
    default_auto_dismiss = models.IntegerField(null=True, blank=True)
    
    # NEW: Real-time specific
    default_icon = models.CharField(max_length=50, blank=True)
    default_badge = models.CharField(max_length=20, blank=True)
    
    # Variables
    available_variables = models.JSONField(default=list, help_text="List of available template variables")
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render_template(self, context):
        """Render template with context variables"""
        from django.template import Template, Context
        template = Template(self.message_template)
        return template.render(Context(context))
    
    def render_pusher_template(self, context):
        """Render Pusher-specific template"""
        import json
        from django.template import Template, Context
        
        rendered_data = {}
        for key, value in self.pusher_template.items():
            if isinstance(value, str) and '{{' in value:
                template = Template(value)
                rendered_data[key] = template.render(Context(context))
            else:
                rendered_data[key] = value
        
        return rendered_data
    
    class Meta:
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"