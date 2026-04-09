from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_account_reference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactionqueue',
            name='recipient',
        ),
    ]
