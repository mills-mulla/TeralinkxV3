# apps/locations/models.py
from django.db import models
from core.models import TimeStampedModel
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
import json
from decimal import Decimal

User = get_user_model()

class Location(TimeStampedModel):
    """Production-grade location management with multi-location support"""
    
    LOCATION_TYPES = [
        ('headquarters', 'Headquarters'),
        ('branch', 'Branch Office'), 
        ('hotspot', 'Public Hotspot'),
        ('commercial', 'Commercial Building'),
        ('fallback', 'Fallback Location'),
    ]
    
    # Core Identification
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=10, 
        unique=True, 
        help_text="Location code like HQ-001"
    )
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='hotspot')
    
    # Multi-Location Node Identity
    node_id = models.CharField(
        max_length=50, 
        unique=True, 
        null=True,
        blank=True,
        help_text="Unique node identifier: central, nairobi, mombasa"
    )
    is_central = models.BooleanField(
        default=False, 
        help_text="Is this the central coordination server?"
    )
    central_api_url = models.URLField(
        blank=True, 
        help_text="Central server API URL for sync"
    )
    sync_api_key = models.CharField(
        max_length=255, 
        blank=True,
        help_text="API key for authenticating with central server"
    )
    
    # Physical Location
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    coordinates = models.CharField(max_length=100, blank=True)
    
    # Router Configuration (per-location)
    router_config = models.JSONField(
        default=dict,
        help_text="RouterOS connection configuration"
    )
    # Expected format:
    # {
    #   "host": "192.168.88.1",
    #   "username": "admin",
    #   "password": "password",
    #   "port": 8728,
    #   "ssl": false,
    #   "webfig_url": "http://192.168.88.1",
    #   "webfig_port": 80
    # }
    
    # Legacy fields (keep for backward compatibility)
    router_ip = models.GenericIPAddressField(blank=True, null=True)
    nas_identifier = models.CharField(max_length=100, blank=True)
    
    # Connectivity & Health
    last_seen_online = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last successful communication with this location"
    )
    is_online = models.BooleanField(
        default=True,
        help_text="Current connectivity status"
    )
    health_check_interval = models.IntegerField(
        default=60,
        help_text="Health check interval in seconds"
    )
    
    # Capacity & Performance
    max_concurrent_users = models.IntegerField(default=100)
    current_user_count = models.IntegerField(default=0)
    bandwidth_limit_mbps = models.IntegerField(
        default=100,
        help_text="Total bandwidth limit in Mbps"
    )
    
    # Operational Status
    is_active = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Is location in maintenance mode?"
    )
    maintenance_message = models.TextField(
        blank=True,
        help_text="Message to display during maintenance"
    )
    
    # Roaming Configuration
    allow_roaming_in = models.BooleanField(
        default=True,
        help_text="Allow users from other locations to roam here"
    )
    allow_roaming_out = models.BooleanField(
        default=True, 
        help_text="Allow users from this location to roam elsewhere"
    )
    roaming_price_multiplier = models.DecimalField(
        max_digits=3, decimal_places=2, default=1.00,
        help_text="Price multiplier for roaming users (1.0 = same price, 1.2 = 20% surcharge)"
    )
    max_roaming_locations = models.IntegerField(
        default=3,
        help_text="Maximum locations a user can roam to simultaneously"
    )
    roaming_time_restrictions = models.JSONField(
        default=dict,
        help_text="Time-based roaming restrictions"
    )
    # Expected format:
    # {
    #   "maintenance_windows": ["02:00-04:00"],
    #   "blocked_days": ["sunday"],
    #   "timezone": "Africa/Nairobi"
    # }
    
    # Offline Operation Limits
    offline_credit_limit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Maximum credit allowed during offline operation"
    )
    offline_operation_enabled = models.BooleanField(
        default=True,
        help_text="Allow offline operation when central is unreachable"
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Description of the location"
    )
    priority = models.IntegerField(
        default=1,
        help_text="Location priority for load balancing (1=highest)"
    )
    
    class Meta:
        db_table = 'locations'
        ordering = ['priority', 'name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        indexes = [
            models.Index(fields=['node_id']),
            models.Index(fields=['is_central']),
            models.Index(fields=['is_online']),
            models.Index(fields=['last_seen_online']),
            models.Index(fields=['is_active', 'maintenance_mode']),
        ]

    def __str__(self):
        status = "🟢" if self.is_online else "🔴"
        role = "[CENTRAL]" if self.is_central else "[LOCATION]"
        return f"{status} {self.name} {role} ({self.node_id})"

    def clean(self):
        """Validate the model"""
        if not self.code:
            self.code = f"LOC-{uuid.uuid4().hex[:6].upper()}"
        
        if not self.node_id:
            self.node_id = self.code.lower().replace('-', '_') if self.code else f"node_{uuid.uuid4().hex[:6]}"
        
        # Ensure only one central location
        if self.is_central:
            existing_central = Location.objects.filter(is_central=True).exclude(pk=self.pk)
            if existing_central.exists():
                raise ValidationError("Only one central location is allowed")
        
        # Validate router config
        if self.router_config:
            required_fields = ['host', 'username', 'password']
            for field in required_fields:
                if field not in self.router_config:
                    raise ValidationError(f"Router config missing required field: {field}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_operational(self):
        """Check if location is operational"""
        return self.is_active and not self.maintenance_mode and self.is_online

    @property
    def capacity_percentage(self):
        """Get current capacity usage percentage"""
        if self.max_concurrent_users == 0:
            return 0
        return (self.current_user_count / self.max_concurrent_users) * 100

    @property
    def is_overloaded(self):
        """Check if location is over capacity"""
        return self.capacity_percentage > 90

    def get_router_config(self):
        """Get router configuration with defaults"""
        default_config = {
            'host': self.router_ip or '192.168.88.1',
            'username': 'admin',
            'password': 'password',
            'port': 8728,
            'ssl': False,
            'webfig_url': f'http://{self.router_ip or "192.168.88.1"}',
            'webfig_port': 80
        }
        
        if self.router_config:
            default_config.update(self.router_config)
        
        return default_config

    def can_roam_to(self, target_location):
        """Check if roaming is allowed to target location"""
        if not self.allow_roaming_out or not target_location.allow_roaming_in:
            return False, "Roaming not allowed"
        
        if not target_location.is_operational:
            return False, "Target location not operational"
        
        if target_location.is_overloaded:
            return False, "Target location over capacity"
        
        # Check time restrictions
        if not self._is_roaming_allowed_at_time(target_location):
            return False, "Roaming not allowed at this time"
        
        return True, "Roaming allowed"

    def _is_roaming_allowed_at_time(self, target_location):
        """Check time-based roaming restrictions"""
        restrictions = target_location.roaming_time_restrictions
        if not restrictions:
            return True
        
        now = timezone.now()
        
        # Check maintenance windows
        maintenance_windows = restrictions.get('maintenance_windows', [])
        for window in maintenance_windows:
            start_time, end_time = window.split('-')
            # Simplified time check - in production, use proper timezone handling
            current_time = now.strftime('%H:%M')
            if start_time <= current_time <= end_time:
                return False
        
        # Check blocked days
        blocked_days = restrictions.get('blocked_days', [])
        current_day = now.strftime('%A').lower()
        if current_day in blocked_days:
            return False
        
        return True

    def get_roaming_locations(self):
        """Get all locations where users can roam from this location"""
        return Location.objects.filter(
            allow_roaming_in=True,
            is_active=True,
            maintenance_mode=False
        ).exclude(id=self.id)

    def update_health_status(self, is_online=True):
        """Update location health status"""
        self.is_online = is_online
        self.last_seen_online = timezone.now() if is_online else self.last_seen_online
        self.save(update_fields=['is_online', 'last_seen_online'])

    def get_offline_duration(self):
        """Get duration since last seen online"""
        if self.is_online or not self.last_seen_online:
            return None
        return timezone.now() - self.last_seen_online

    def can_operate_offline(self):
        """Check if location can operate in offline mode"""
        return self.offline_operation_enabled and self.offline_credit_limit > 0


class NodeIdentity(models.Model):
    """Singleton model for node identity and role management"""
    
    ROLES = [
        ('central', 'Central Server'),
        ('location', 'Location Server'),
    ]
    
    OPERATIONAL_MODES = [
        ('online', 'Online - Full Connectivity'),
        ('degraded', 'Degraded - Limited Connectivity'),
        ('offline', 'Offline - Local Operation Only'),
        ('emergency', 'Emergency - Critical Functions Only'),
    ]
    
    # Node Identity
    role = models.CharField(max_length=20, choices=ROLES)
    node_id = models.CharField(max_length=50, unique=True)
    location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Associated location (null for central server)"
    )
    
    # Registration & Authentication
    is_registered = models.BooleanField(default=False)
    registration_token = models.CharField(max_length=255, blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    
    # Operational Status
    current_mode = models.CharField(
        max_length=20, 
        choices=OPERATIONAL_MODES, 
        default='online'
    )
    last_mode_change = models.DateTimeField(auto_now=True)
    
    # Central Server Connection (for location nodes)
    central_api_url = models.URLField(blank=True)
    central_connection_status = models.BooleanField(default=True)
    last_central_contact = models.DateTimeField(null=True, blank=True)
    
    # Performance Metrics
    sync_lag_seconds = models.IntegerField(default=0)
    pending_transactions = models.IntegerField(default=0)
    error_rate_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    
    # Circuit Breaker State
    circuit_breaker_state = models.CharField(
        max_length=20,
        choices=[
            ('closed', 'Closed - Normal Operation'),
            ('open', 'Open - Failing Fast'),
            ('half_open', 'Half Open - Testing Recovery'),
        ],
        default='closed'
    )
    circuit_breaker_failure_count = models.IntegerField(default=0)
    circuit_breaker_last_failure = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Node Identity"
        verbose_name_plural = "Node Identities"
        db_table = 'node_identity'
    
    def __str__(self):
        return f"{self.role.title()} Node: {self.node_id} ({self.current_mode})"
    
    @classmethod
    def get_current_node(cls):
        """Get the current node identity (singleton)"""
        return cls.objects.first()
    
    @classmethod
    def initialize_node(cls, role, node_id, location=None):
        """Initialize node identity from environment"""
        node, created = cls.objects.get_or_create(
            defaults={
                'role': role,
                'node_id': node_id,
                'location': location,
            }
        )
        return node
    
    def is_central_reachable(self):
        """Check if central server is reachable"""
        if self.role == 'central':
            return True
        
        if not self.last_central_contact:
            return False
        
        # Consider unreachable if no contact for 5 minutes
        threshold = timezone.now() - timezone.timedelta(minutes=5)
        return self.last_central_contact > threshold
    
    def update_central_contact(self, success=True):
        """Update central server contact status"""
        self.central_connection_status = success
        if success:
            self.last_central_contact = timezone.now()
            self.circuit_breaker_failure_count = 0
            if self.circuit_breaker_state == 'open':
                self.circuit_breaker_state = 'half_open'
        else:
            self.circuit_breaker_failure_count += 1
            self.circuit_breaker_last_failure = timezone.now()
            
            # Open circuit breaker after 5 failures
            if self.circuit_breaker_failure_count >= 5:
                self.circuit_breaker_state = 'open'
        
        self.save()
    
    def should_operate_offline(self):
        """Determine if node should operate in offline mode"""
        return (
            self.role == 'location' and 
            not self.is_central_reachable() and
            self.location and 
            self.location.can_operate_offline()
        )
    
    def get_operational_capabilities(self):
        """Get current operational capabilities based on mode"""
        capabilities = {
            'online': [
                'all_operations',
                'real_time_sync',
                'new_user_registration',
                'full_roaming',
                'unlimited_transactions'
            ],
            'degraded': [
                'local_users_only',
                'cached_packages',
                'queue_transactions',
                'limited_roaming',
                'existing_vouchers_only'
            ],
            'offline': [
                'existing_users_only',
                'emergency_credit',
                'local_voucher_validation',
                'no_roaming',
                'critical_transactions_only'
            ],
            'emergency': [
                'voucher_validation_only',
                'no_new_transactions',
                'read_only_operations'
            ]
        }
        return capabilities.get(self.current_mode, [])


class LocationMesh(models.Model):
    """Peer-to-peer location connectivity for resilience"""
    
    # Primary location
    location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='mesh_connections'
    )
    
    # Peer location
    peer_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='peer_connections'
    )
    
    # Connection Status
    is_connected = models.BooleanField(default=False)
    last_contact = models.DateTimeField(null=True, blank=True)
    connection_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('poor', 'Poor'),
            ('failed', 'Failed'),
        ],
        default='good'
    )
    
    # Performance Metrics
    latency_ms = models.IntegerField(default=0)
    bandwidth_mbps = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00
    )
    packet_loss_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    
    # Sync Capabilities
    can_sync_users = models.BooleanField(default=True)
    can_sync_transactions = models.BooleanField(default=True)
    can_sync_vouchers = models.BooleanField(default=True)
    
    # Priority for failover
    priority = models.IntegerField(
        default=1,
        help_text="Priority for peer selection (1=highest)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['location', 'peer_location']
        db_table = 'location_mesh'
        verbose_name = "Location Mesh Connection"
        verbose_name_plural = "Location Mesh Connections"
        indexes = [
            models.Index(fields=['location', 'is_connected']),
            models.Index(fields=['connection_quality']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        status = "🟢" if self.is_connected else "🔴"
        return f"{status} {self.location.name} ↔ {self.peer_location.name}"
    
    def update_connection_status(self, is_connected, latency_ms=None, quality=None):
        """Update connection status and metrics"""
        self.is_connected = is_connected
        if is_connected:
            self.last_contact = timezone.now()
        
        if latency_ms is not None:
            self.latency_ms = latency_ms
            
        if quality:
            self.connection_quality = quality
        
        self.save()
    
    @classmethod
    def get_available_peers(cls, location):
        """Get available peer locations for a given location"""
        return cls.objects.filter(
            location=location,
            is_connected=True,
            connection_quality__in=['excellent', 'good']
        ).order_by('priority', 'latency_ms')


class DistributedTransaction(models.Model):
    """Two-phase commit for distributed transactions"""
    
    TRANSACTION_STATES = [
        ('preparing', 'Preparing'),
        ('prepared', 'Prepared'),
        ('committing', 'Committing'),
        ('committed', 'Committed'),
        ('aborting', 'Aborting'),
        ('aborted', 'Aborted'),
        ('failed', 'Failed'),
    ]
    
    TRANSACTION_TYPES = [
        ('balance_update', 'Balance Update'),
        ('voucher_purchase', 'Voucher Purchase'),
        ('roaming_activation', 'Roaming Activation'),
        ('user_registration', 'User Registration'),
        ('package_activation', 'Package Activation'),
    ]
    
    # Transaction Identity
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    
    # State Management
    state = models.CharField(max_length=20, choices=TRANSACTION_STATES, default='preparing')
    coordinator_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE,
        related_name='coordinated_transactions'
    )
    
    # Participants
    participant_locations = models.ManyToManyField(
        Location,
        through='TransactionParticipant',
        related_name='participated_transactions'
    )
    
    # Transaction Data
    transaction_data = models.JSONField(default=dict)
    compensation_data = models.JSONField(default=dict)  # For rollback
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    committed_at = models.DateTimeField(null=True, blank=True)
    timeout_at = models.DateTimeField()
    
    # Error Handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    class Meta:
        db_table = 'distributed_transactions'
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['started_at']),
            models.Index(fields=['timeout_at']),
        ]
    
    def __str__(self):
        return f"TX-{self.transaction_id.hex[:8]} ({self.transaction_type}) - {self.state}"
    
    def add_participant(self, location, role='participant'):
        """Add a participant to the transaction"""
        TransactionParticipant.objects.create(
            transaction=self,
            location=location,
            role=role
        )
    
    def can_commit(self):
        """Check if all participants are prepared"""
        participants = self.participants.all()
        return all(p.state == 'prepared' for p in participants)
    
    def prepare_phase(self):
        """Execute prepare phase of 2PC"""
        self.state = 'preparing'
        self.save()
        
        # Send prepare requests to all participants
        for participant in self.participants.all():
            participant.send_prepare_request()
        
        # Set timeout for prepare phase
        self.timeout_at = timezone.now() + timezone.timedelta(minutes=5)
        self.save()
    
    def commit_phase(self):
        """Execute commit phase of 2PC"""
        if not self.can_commit():
            self.abort_transaction()
            return False
        
        self.state = 'committing'
        self.committed_at = timezone.now()
        self.save()
        
        # Send commit requests to all participants
        success = True
        for participant in self.participants.all():
            if not participant.send_commit_request():
                success = False
        
        self.state = 'committed' if success else 'failed'
        self.save()
        return success
    
    def abort_transaction(self):
        """Abort the transaction and rollback"""
        self.state = 'aborting'
        self.save()
        
        # Send abort requests to all participants
        for participant in self.participants.all():
            participant.send_abort_request()
        
        self.state = 'aborted'
        self.save()
    
    def is_expired(self):
        """Check if transaction has expired"""
        return timezone.now() > self.timeout_at


class TransactionParticipant(models.Model):
    """Participant in a distributed transaction"""
    
    PARTICIPANT_STATES = [
        ('pending', 'Pending'),
        ('prepared', 'Prepared'),
        ('committed', 'Committed'),
        ('aborted', 'Aborted'),
        ('failed', 'Failed'),
    ]
    
    PARTICIPANT_ROLES = [
        ('coordinator', 'Coordinator'),
        ('participant', 'Participant'),
    ]
    
    transaction = models.ForeignKey(
        DistributedTransaction, 
        on_delete=models.CASCADE,
        related_name='participants'
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    
    role = models.CharField(max_length=20, choices=PARTICIPANT_ROLES, default='participant')
    state = models.CharField(max_length=20, choices=PARTICIPANT_STATES, default='pending')
    
    # Response data from participant
    response_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    # Timing
    prepared_at = models.DateTimeField(null=True, blank=True)
    committed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['transaction', 'location']
        db_table = 'transaction_participants'
    
    def send_prepare_request(self):
        """Send prepare request to participant location"""
        # Implementation would make API call to participant
        # For now, simulate success
        self.state = 'prepared'
        self.prepared_at = timezone.now()
        self.save()
        return True
    
    def send_commit_request(self):
        """Send commit request to participant location"""
        # Implementation would make API call to participant
        self.state = 'committed'
        self.committed_at = timezone.now()
        self.save()
        return True
    
    def send_abort_request(self):
        """Send abort request to participant location"""
        self.state = 'aborted'
        self.save()
        return True


class LocationHealthMetrics(models.Model):
    """Real-time health metrics for locations"""
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='health_metrics')
    
    # System Metrics
    cpu_usage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    memory_usage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    disk_usage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Network Metrics
    network_latency_ms = models.IntegerField(default=0)
    bandwidth_utilization_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    packet_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Application Metrics
    active_sessions = models.IntegerField(default=0)
    pending_transactions = models.IntegerField(default=0)
    sync_lag_seconds = models.IntegerField(default=0)
    error_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Database Metrics
    db_connection_count = models.IntegerField(default=0)
    db_query_avg_time_ms = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Timestamp
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'location_health_metrics'
        indexes = [
            models.Index(fields=['location', 'recorded_at']),
            models.Index(fields=['recorded_at']),
        ]
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.location.name} Health - {self.recorded_at.strftime('%H:%M:%S')}"
    
    @property
    def overall_health_score(self):
        """Calculate overall health score (0-100)"""
        # Weighted scoring
        cpu_score = max(0, 100 - self.cpu_usage_percentage)
        memory_score = max(0, 100 - self.memory_usage_percentage)
        network_score = max(0, 100 - (self.network_latency_ms / 10))  # 1000ms = 0 score
        error_score = max(0, 100 - (self.error_rate_percentage * 10))
        
        weights = {'cpu': 0.25, 'memory': 0.25, 'network': 0.25, 'error': 0.25}
        
        overall = (
            cpu_score * weights['cpu'] +
            memory_score * weights['memory'] +
            network_score * weights['network'] +
            error_score * weights['error']
        )
        
        return round(overall, 2)
    
    @property
    def health_status(self):
        """Get health status based on score"""
        score = self.overall_health_score
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 50:
            return 'fair'
        else:
            return 'poor'
    
    @classmethod
    def record_metrics(cls, location, metrics_data):
        """Record new health metrics for a location"""
        return cls.objects.create(
            location=location,
            **metrics_data
        )