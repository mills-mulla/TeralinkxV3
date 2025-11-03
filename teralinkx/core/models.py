from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from decimal import Decimal
User = get_user_model()

# -----------------------------
# Voucher & Package Models
# -----------------------------
class AvailableVoucher(models.Model):
    voucher_code = models.CharField(max_length=255)
    package = models.CharField(null=True, max_length=255)
    package_desc = models.CharField(max_length=50)
    duration = models.DurationField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.voucher_code}, {self.package}, {self.duration}, {self.package_desc}, {self.price}"

    class Meta:
        indexes = [
            models.Index(fields=['voucher_code']),
            models.Index(fields=['package']),
            models.Index(fields=['package_desc']),
        ]



class Package(models.Model):
    id = models.AutoField(primary_key=True)
    package = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    package_desc = models.CharField(max_length=255)
    package_duration = models.DurationField(blank=True, null=True)
    devices = models.CharField(max_length=20)
    usage_limit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  

    def __str__(self):
        return (
            f"{self.id}, {self.package}, {self.price}, {self.package_desc}, "
            f"{self.package_duration}, {self.devices}, {self.usage_limit}"
        )

    class Meta:
        indexes = [
            models.Index(fields=['package']),
            models.Index(fields=['package_desc']),
        ]

class DailyPass(models.Model):
    id = models.AutoField(primary_key=True)
    package = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    package_desc = models.CharField(max_length=255)
    package_duration = models.DurationField(blank=True, null=True)
    devices = models.CharField(max_length=20)
    limit = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('soldout', 'Soldout'),
        
    ], default='soldout',null=True)
    banner = models.CharField(max_length=20, choices=[
        ('NEW', 'New'),
        ('HOT', 'HOT'),
        
    ], default='NEW',null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    usage_limit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  

    def __str__(self):
        return f"{self.id}, {self.package}, {self.price}, {self.package_desc},{self.package_duration},{self.devices},{self.limit}"

    class Meta:
        indexes = [
            models.Index(fields=['package']),
            models.Index(fields=['package_desc']),
        ]



class DispatchVoucher(models.Model):
    dispatch_id = models.AutoField(primary_key=True)
    dispatch_account = models.CharField(max_length=15)
    dispatch_price = models.DecimalField(max_digits=10, decimal_places=2)
    dispatch_package_desc = models.CharField(max_length=255)
    dispatch_package = models.CharField(max_length=255)
    dispatch_status = models.CharField(max_length=20)
    dispatch_voucher_code = models.CharField(max_length=255)
    dispatch_package_duration = models.DurationField(null=True)
    dispatch_devices = models.CharField(null=True)
    dispatch_time = models.DateTimeField(auto_now_add=True,null=True)
    dispatch_expiry = models.DateTimeField(null=True, blank=True)
    usermanid = models.CharField(null=True, blank=True)
    
    # Usage tracking
    uptime = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in MB/GB
    total_download = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in MB/GB
    total_upload = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    # in MB/GB
    active_sessions = models.IntegerField(default=0)
    usage_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    # MB/GB

    def save(self, *args, **kwargs):
        # Set dispatch_time if not already set
        if not self.dispatch_time:
            self.dispatch_time = timezone.now()
        # Calculate expiry
        if self.dispatch_package_duration:
            self.dispatch_expiry = self.dispatch_time + self.dispatch_package_duration
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.dispatch_account}, {self.dispatch_voucher_code}, {self.dispatch_status}, "
            f"{self.dispatch_price}, {self.dispatch_package}, {self.dispatch_package_desc}, "
            f"{self.dispatch_package_duration}, {self.usage_limit}"
        )

    def is_expired(self):
        # Always cast to Decimal safely
        total_download = Decimal(str(self.total_download or "0"))
        total_upload = Decimal(str(self.total_upload or "0"))
        usage_limit = self.usage_limit

        time_expired = self.dispatch_expiry and timezone.now() > self.dispatch_expiry
        usage_exhausted = usage_limit is not None and (total_download + total_upload) >= usage_limit

        return time_expired or usage_exhausted

    class Meta:
        indexes = [
            models.Index(fields=['dispatch_account']),
            models.Index(fields=['dispatch_voucher_code']),
            models.Index(fields=['dispatch_status']),
            models.Index(fields=['dispatch_expiry']),
        ]

class RefundLog(models.Model):
    account = models.CharField(max_length=15)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    downtime_minutes = models.IntegerField()
    refund_type = models.CharField(max_length=20, choices=[
        ('individual', 'Individual Refund'),
        ('batch', 'Batch Refund')
    ])
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Refund for {self.account} - KES {self.refund_amount}"
    
    class Meta:
        db_table = 'core_refundlog'
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['created_at']),
            models.Index(fields=['refund_type']),
        ]
        ordering = ['-created_at']


class DowntimeRecord(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    SERVICE_CHOICES = [
        ('all', 'All Services'),
        ('internet', 'Internet'),
        ('billing', 'Billing System'),
        ('authentication', 'Authentication'),
        ('voip', 'VoIP Services'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255, help_text="Descriptive name for the downtime event")
    start_time = models.DateTimeField(help_text="When the downtime started")
    end_time = models.DateTimeField(help_text="When the downtime ended")
    duration_minutes = models.IntegerField(help_text="Total downtime duration in minutes")
    
    affected_services = models.CharField(
        max_length=50, 
        choices=SERVICE_CHOICES, 
        default='all',
        help_text="Which services were affected"
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text="Severity level of the downtime"
    )
    
    reason = models.TextField(blank=True, null=True, help_text="Reason for the downtime")
    
    # Additional fields for better tracking
    impact_level = models.CharField(
        max_length=50,
        choices=[
            ('minimal', 'Minimal Impact'),
            ('partial', 'Partial Outage'),
            ('full', 'Full Outage'),
            ('regional', 'Regional Outage'),
        ],
        default='partial',
        help_text="Level of impact on services"
    )
    
    affected_regions = models.TextField(
        blank=True, 
        null=True,
        help_text="Comma-separated list of affected regions"
    )
    
    estimated_affected_users = models.IntegerField(
        default=0,
        help_text="Estimated number of users affected"
    )
    
    # Resolution fields
    resolution_notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Notes on how the issue was resolved"
    )
    
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_downtimes',
        help_text="Staff member who resolved the issue"
    )
    
    resolution_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the issue was fully resolved"
    )
    
    # Automated fields
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_downtimes',
        help_text="User who recorded this downtime"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status tracking
    is_resolved = models.BooleanField(default=False)
    requires_follow_up = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'core_downtimerecord'
        verbose_name = 'Downtime Record'
        verbose_name_plural = 'Downtime Records'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['name']),
            models.Index(fields=['severity']),
            models.Index(fields=['affected_services']),
            models.Index(fields=['is_resolved']),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        # Calculate duration automatically if not set
        if self.start_time and self.end_time and not self.duration_minutes:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        
        # Auto-set resolution status
        if self.resolution_time and not self.is_resolved:
            self.is_resolved = True
        
        # Set severity based on duration if not explicitly set
        if not self.severity and self.duration_minutes:
            if self.duration_minutes >= 120:  # 2 hours or more
                self.severity = 'critical'
            elif self.duration_minutes >= 60:  # 1-2 hours
                self.severity = 'high'
            elif self.duration_minutes >= 30:  # 30-60 minutes
                self.severity = 'medium'
            else:
                self.severity = 'low'
        
        super().save(*args, **kwargs)

    @property
    def duration_hours(self):
        """Return duration in hours with decimal precision"""
        return round(self.duration_minutes / 60, 2)

    @property
    def formatted_duration(self):
        """Return human-readable duration"""
        if self.duration_minutes < 60:
            return f"{self.duration_minutes} minutes"
        else:
            hours = self.duration_minutes // 60
            minutes = self.duration_minutes % 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours} hours"

    @property
    def is_ongoing(self):
        """Check if downtime is currently ongoing"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def affected_users_percentage(self):
        """Calculate percentage of affected users (if total users available)"""
        # This would need your total user count logic
        # For now, return a placeholder calculation
        if self.estimated_affected_users > 0:
            # You might want to get total active users from your system
            total_users = 1000  # Placeholder - replace with actual count
            return round((self.estimated_affected_users / total_users) * 100, 1)
        return 0

    def mark_resolved(self, resolved_by=None, notes=None):
        """Mark downtime as resolved"""
        self.is_resolved = True
        self.resolution_time = timezone.now()
        if resolved_by:
            self.resolved_by = resolved_by
        if notes:
            self.resolution_notes = notes
        self.save()

    @classmethod
    def get_recent_downtimes(cls, days=30):
        """Get recent downtimes within specified days"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return cls.objects.filter(start_time__gte=cutoff_date)

    @classmethod
    def get_critical_downtimes(cls, days=7):
        """Get critical severity downtimes in recent period"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return cls.objects.filter(
            start_time__gte=cutoff_date,
            severity__in=['critical', 'high']
        )

    @classmethod
    def get_ongoing_downtimes(cls):
        """Get currently ongoing downtimes"""
        now = timezone.now()
        return cls.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_resolved=False
        )

    @classmethod
    def get_downtime_stats(cls, days=30):
        """Get statistics for downtime analysis"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        downtimes = cls.objects.filter(start_time__gte=cutoff_date)
        
        stats = {
            'total_downtimes': downtimes.count(),
            'total_duration_minutes': downtimes.aggregate(
                total=models.Sum('duration_minutes')
            )['total'] or 0,
            'critical_count': downtimes.filter(severity='critical').count(),
            'high_count': downtimes.filter(severity='high').count(),
            'medium_count': downtimes.filter(severity='medium').count(),
            'low_count': downtimes.filter(severity='low').count(),
            'resolved_count': downtimes.filter(is_resolved=True).count(),
            'unresolved_count': downtimes.filter(is_resolved=False).count(),
        }
        
        # Calculate average duration
        if stats['total_downtimes'] > 0:
            stats['average_duration_minutes'] = round(
                stats['total_duration_minutes'] / stats['total_downtimes']
            )
        else:
            stats['average_duration_minutes'] = 0
            
        return stats
        
class ExpiredVoucher(models.Model):
    expired_account = models.CharField(max_length=15)
    expired_package = models.CharField(max_length=255)
    expired_voucher = models.CharField(max_length=255)
    expiry_time = models.DateTimeField(auto_now_add=True, null=True)
    user_mac = models.CharField(max_length=255, null=True)




class ClientH(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='clienth')
    account = models.CharField(max_length=15, unique=True)
    current_ip_address = models.GenericIPAddressField(blank=True, null=True)
    active_voucher = models.CharField(max_length=50, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    bound_ip = models.CharField(max_length=15, null=True, blank=True)
    voucher_expiry = models.DateTimeField(blank=True, null=True)
    otp = models.CharField(max_length=17, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    mac_addresses = models.ManyToManyField('ClientMAC', related_name='clients', blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"

    def can_afford(self, amount):
        return self.balance >= amount

    def deduct_balance(self, amount):
        if amount < 0:
            raise ValueError("Cannot deduct a negative amount.")
        if self.balance - amount < 0:
            raise ValueError("Insufficient balance for the requested deduction.")
        
        self.balance -= amount
        self.save()

    def add_balance(self, amount):
        self.balance += amount
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['voucher_expiry']),
        ]

class ClientMAC(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    bound_ip = models.CharField(max_length=15, null=True, blank=True)
    status = models.CharField(max_length=20, default='not connected')

    def __str__(self):
        return self.mac_address


class DHCPLease(models.Model):
    idD = models.CharField(max_length=50)
    client = models.ForeignKey('ClientH', on_delete=models.CASCADE, related_name='leases', null=True)
    address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=17)
    dhcp_client_id = models.CharField(max_length=50, null=True)
    address_lists = models.TextField(blank=True)
    server = models.CharField(max_length=50)
    dhcp_option = models.TextField(blank=True)
    status = models.CharField(max_length=20)
    expires_after = models.CharField(max_length=20)
    last_seen = models.CharField(max_length=20)
    age = models.CharField(max_length=20, blank=True, null=True)
    active_address = models.GenericIPAddressField()
    active_mac_address = models.CharField(max_length=17)
    active_client_id = models.CharField(max_length=50, null=True)
    active_server = models.CharField(max_length=50)
    host_name = models.CharField(max_length=50, blank=True, null=True)
    radius = models.CharField(max_length=50, blank=True)
    dynamic = models.CharField(max_length=50, blank=True)
    blocked = models.CharField(max_length=50, blank=True)
    disabled = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.mac_address} - {self.address}"

    class Meta:
        indexes = [
            models.Index(fields=['mac_address']),
            models.Index(fields=['active_mac_address']),
            models.Index(fields=['active_address']),
            models.Index(fields=['client']),
        ]

# -----------------------------
# Active Session, Messaging & Logs
# -----------------------------
class ActiveUser(models.Model):
    idA = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=15)
    mac_address = models.CharField(max_length=17)
    radius = models.CharField(max_length=50)
    login_by = models.CharField(max_length=50)
    server = models.CharField(max_length=100)
    uptime = models.CharField(max_length=50)
    idle_time = models.CharField(max_length=50)
    bytes_in = models.CharField(max_length=50)
    bytes_out = models.CharField(max_length=50)
    packets_in = models.CharField(max_length=50)
    packets_out = models.CharField(max_length=50)

    def __str__(self):
        return self.username

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['mac_address']),
        ]


class alternateSessions(models.Model):
    alternate_no = models.CharField(max_length=15)
    alternate_current_ip = models.GenericIPAddressField()
    alternate_current_mac = models.CharField(max_length=17)
    alternate_bound_mac = models.CharField(max_length=17)
    alternate_status = models.CharField(max_length=20)
    alternate_bound_ip = models.GenericIPAddressField(null=True)
    alternate_active_voucher = models.CharField(max_length=50, blank=True, null=True)
    alternate_voucher_expiry = models.CharField(max_length=50, blank=True, null=True)
    last_login = models.DateTimeField(auto_now_add=True)
    session_timeout = models.DurationField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['alternate_no']),
            models.Index(fields=['alternate_bound_mac']),
        ]



class Room(models.Model):
    room_name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name='rooms', blank=True)    

    def __str__(self):
        return self.room_name

    def return_room_messages(self):
        return Message.objects.filter(room=self)

    def create_new_room_message(self, sender, message):
        return Message.objects.create(room=self, sender=sender, message=message)


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room} - {self.time}"

    class Meta:
        indexes = [
            models.Index(fields=['room']),
            models.Index(fields=['time']),
        ]


# -----------------------------
# Announcements, Investments & Expenses
# -----------------------------
class Announce(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
        ]


class Investment(models.Model):
    INVESTMENT_TYPE_CHOICES = [
        ('seed', 'Seed Funding'),
        ('angel', 'Angel Investment'),
        ('vc', 'Venture Capital'),
        ('other', 'Other'),
    ]

    investor_name = models.CharField(max_length=255)
    investment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPE_CHOICES, default='other')
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.investor_name} - {self.amount} on {self.investment_date}"

    class Meta:
        indexes = [
            models.Index(fields=['investment_type']),
            models.Index(fields=['investment_date']),
        ]


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('network', 'Network Infrastructure'),
        ('maintenance', 'Maintenance & Repairs'),
        ('labor', 'Labor & Salaries'),
        ('marketing', 'Marketing & Advertising'),
        ('office', 'Office Expenses'),
        ('utility', 'Utilities'),
        ('software', 'Software & Licensing'),
        ('other', 'Other'),
    ]

    expense_date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    vendor = models.CharField(max_length=255, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.expense_date} | {self.get_category_display()} | ${self.amount}"

    class Meta:
        indexes = [
            models.Index(fields=['expense_date']),
            models.Index(fields=['category']),
        ]

# ----------------------------------
# Transaction Model
# ----------------------------------
class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255)
    initiator = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=1000, decimal_places=2)
    balance = models.DecimalField(max_digits=1000, decimal_places=2, null=True)
    date = models.CharField(max_length=255, null=True)
    result_code = models.IntegerField()
    result_desc = models.CharField(max_length=255)
    merchant_request_id = models.CharField(max_length=255)
    checkout_request_id = models.CharField(max_length=255)
    transaction_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Transaction ID: {self.transaction_id}"

    class Meta:
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['initiator']),
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['merchant_request_id']),
        ]

# ----------------------------------
# Queue Model (with indexes)
# ----------------------------------
class Queue(models.Model):
    id = models.BigAutoField(primary_key=True)
    method = models.CharField(max_length=255)
    initiator = models.CharField(max_length=25)
    checkout_request_id = models.CharField(max_length=255, null=True)
    package_desc = models.CharField(max_length=255)
    package = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    queue_time = models.DateTimeField(auto_now_add=True)
    recipient = models.CharField(max_length=25)
    used_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Account No: {self.recipient}, Package Desc: {self.package_desc}"

    class Meta:
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['status']),
        ]



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Advertisement(models.Model):
    title = models.CharField(max_length=100)
    caption = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/')  # saved under MEDIA_ROOT/ads/
    active = models.BooleanField(default=True)   # easily enable/disable an ad
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title