from django.db import models


class Voucher(models.Model):
    """Voucher tracking for time-based access"""
    username = models.CharField(max_length=255, unique=True, db_index=True)
    profile = models.CharField(max_length=255)
    duration_seconds = models.IntegerField(help_text="Voucher validity in seconds")
    activated_at = models.DateTimeField(null=True, blank=True, help_text="First login time")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiry time")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'vouchers'
    
    def __str__(self):
        return f"{self.username} - {self.profile}"
    
    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def remaining_seconds(self):
        if not self.expires_at:
            return self.duration_seconds
        from django.utils import timezone
        remaining = (self.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))
