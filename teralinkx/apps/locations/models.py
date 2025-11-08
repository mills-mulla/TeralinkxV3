# apps/locations/models.py
from django.db import models
from core.models import TimeStampedModel

class Location(TimeStampedModel):
    """ISP-focused location management"""
    
    LOCATION_TYPES = [
        ('headquarters', 'Headquarters'),
        ('branch', 'Branch Office'), 
        ('hotspot', 'Public Hotspot'),
        ('commercial', 'Commercial Building'),
    ]
    
    # Core Identification
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=10, 
        unique=True, 
        help_text="Location code like HQ-001",
        default="LOC-001"  # Add default value
    )
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='hotspot')
    
    # Physical Location
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    coordinates = models.CharField(max_length=100, blank=True)
    
    # Network Configuration
    router_ip = models.GenericIPAddressField(blank=True, null=True)
    nas_identifier = models.CharField(max_length=100, blank=True)
    
    # Capacity
    max_concurrent_users = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    
    # Simple Roaming Settings
    allow_roaming_in = models.BooleanField(
        default=True,
        help_text="Allow users from other locations to roam here"
    )
    allow_roaming_out = models.BooleanField(
        default=True, 
        help_text="Allow users from this location to roam elsewhere"
    )
    roaming_price_multiplier = models.DecimalField(
        max_digits=3, decimal_places=2, default=1.0,
        help_text="Price multiplier for roaming users"
    )

    class Meta:
        db_table = 'locations'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def is_operational(self):
        return self.is_active

    def can_roam_to(self, target_location):
        """Check if roaming is allowed to target location"""
        return (self.allow_roaming_out and 
                target_location.allow_roaming_in and 
                target_location.is_operational)

    def get_roaming_locations(self):
        """Get all locations where users can roam from this location"""
        return Location.objects.filter(
            allow_roaming_in=True,
            is_active=True
        ).exclude(id=self.id)