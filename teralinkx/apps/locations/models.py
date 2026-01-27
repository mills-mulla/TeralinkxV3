# apps/locations/models.py
from django.db import models
from core.models import TimeStampedModel
from django.core.exceptions import ValidationError
import uuid

class Location(TimeStampedModel):
    """ISP-focused location management"""
    
    LOCATION_TYPES = [
        ('headquarters', 'Headquarters'),
        ('branch', 'Branch Office'), 
        ('hotspot', 'Public Hotspot'),
        ('commercial', 'Commercial Building'),
        ('fallback', 'Fallback Location'),  # Add fallback type
    ]
    
    # Core Identification
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=10, 
        unique=True, 
        help_text="Location code like HQ-001"
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
    description = models.TextField(
        blank=True,
        help_text="Description of the location"
    )

    class Meta:
        db_table = 'locations'
        ordering = ['name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        """Validate the model"""
        if not self.code:
            self.code = f"LOC-{uuid.uuid4().hex[:6].upper()}"
        
        # Ensure code starts with LOC-
        if not self.code.startswith('LOC-'):
            self.code = f"LOC-{self.code}"
        
        # Ensure unique code
        if Location.objects.filter(code=self.code).exclude(pk=self.pk).exists():
            raise ValidationError(f"Location with code {self.code} already exists")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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