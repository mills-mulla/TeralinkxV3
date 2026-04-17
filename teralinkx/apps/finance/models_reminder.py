# apps/finance/models_reminder.py
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel


class PaymentReminder(TimeStampedModel):
    """Tracks automated payment reminders sent to customers."""

    REMINDER_TYPES = [
        ('expiry_3d',   '3 Days Before Expiry'),
        ('expiry_1d',   '1 Day Before Expiry'),
        ('expiry_day',  'Expiry Day'),
        ('overdue_3d',  '3 Days Overdue'),
        ('overdue_7d',  '7 Days Overdue — Final Warning'),
    ]

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('sent',      'Sent'),
        ('failed',    'Failed'),
        ('skipped',   'Skipped (opted out)'),
    ]

    customer        = models.ForeignKey('users.ClientH', on_delete=models.CASCADE,
                                        related_name='payment_reminders')
    reminder_type   = models.CharField(max_length=20, choices=REMINDER_TYPES)
    scheduled_at    = models.DateTimeField()
    sent_at         = models.DateTimeField(null=True, blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message         = models.TextField(blank=True)
    phone_number    = models.CharField(max_length=20, blank=True)
    error_message   = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-scheduled_at']
        indexes = [
            models.Index(fields=['customer', 'reminder_type']),
            models.Index(fields=['status', 'scheduled_at']),
        ]

    def __str__(self):
        return f"{self.customer.account} — {self.get_reminder_type_display()} — {self.status}"

    def mark_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()

    def mark_failed(self, error=''):
        self.status = 'failed'
        self.error_message = error
        self.save()
