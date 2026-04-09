from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_remove_recipient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenttransaction',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('completed', 'Completed'),
                    ('refunded', 'Refunded'),
                    ('partially_refunded', 'Partially Refunded'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
