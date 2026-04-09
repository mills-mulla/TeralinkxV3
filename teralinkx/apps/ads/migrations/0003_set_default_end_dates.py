# Generated migration to set default end_dates
from django.db import migrations
from django.utils import timezone
from datetime import timedelta

def set_default_end_dates(apps, schema_editor):
    """Set default end_dates for existing ads without end_date"""
    Advertisement = apps.get_model('ads', 'Advertisement')
    
    # Set end_date to 30 days from start_date for ads without end_date
    ads_without_end_date = Advertisement.objects.filter(end_date__isnull=True)
    
    for ad in ads_without_end_date:
        if ad.start_date:
            ad.end_date = ad.start_date + timedelta(days=30)
        else:
            ad.end_date = timezone.now() + timedelta(days=30)
        ad.save()

def reverse_set_default_end_dates(apps, schema_editor):
    """Reverse migration - set end_dates back to None"""
    pass  # We don't want to remove end_dates

class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_alter_advertisement_end_date'),
    ]

    operations = [
        migrations.RunPython(set_default_end_dates, reverse_set_default_end_dates),
    ]