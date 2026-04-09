# Generated migration to update callback URLs to srv.teralinkxwaves.uk

from django.db import migrations

def update_callback_urls(apps, schema_editor):
    PaymentGateway = apps.get_model('finance', 'PaymentGateway')
    
    # Update existing PaymentGateway records
    PaymentGateway.objects.filter(
        callback_url='https://teralinkxwaves.uk/api/payments/callback/'
    ).update(
        callback_url='https://srv.teralinkxwaves.uk/api/payments/callback/'
    )
    
    PaymentGateway.objects.filter(
        webhook_url='https://teralinkxwaves.uk/api/webhooks/payment/'
    ).update(
        webhook_url='https://srv.teralinkxwaves.uk/api/webhooks/payment/'
    )

def reverse_callback_urls(apps, schema_editor):
    PaymentGateway = apps.get_model('finance', 'PaymentGateway')
    
    # Reverse the changes
    PaymentGateway.objects.filter(
        callback_url='https://srv.teralinkxwaves.uk/api/payments/callback/'
    ).update(
        callback_url='https://teralinkxwaves.uk/api/payments/callback/'
    )
    
    PaymentGateway.objects.filter(
        webhook_url='https://srv.teralinkxwaves.uk/api/webhooks/payment/'
    ).update(
        webhook_url='https://teralinkxwaves.uk/api/webhooks/payment/'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_payment_method_choices'),
    ]

    operations = [
        migrations.RunPython(update_callback_urls, reverse_callback_urls),
    ]