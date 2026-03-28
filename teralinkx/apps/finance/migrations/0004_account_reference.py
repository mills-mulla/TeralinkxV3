from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_alter_paymenttransaction_checkout_request_id_and_more'),
    ]

    operations = [
        # Add account_reference to TransactionQueue
        migrations.AddField(
            model_name='transactionqueue',
            name='account_reference',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text='Client account ID (e.g. CLI000003). Maps to BillRefNumber in M-Pesa callbacks.',
                max_length=100,
            ),
            preserve_default=False,
        ),
        # Copy existing recipient values into account_reference
        migrations.RunSQL(
            sql="UPDATE finance_transactionqueue SET account_reference = recipient WHERE account_reference = ''",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Add account_reference to PaymentTransaction
        migrations.AddField(
            model_name='paymenttransaction',
            name='account_reference',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text='Client account ID from BillRefNumber (e.g. CLI000003).',
                max_length=100,
            ),
            preserve_default=False,
        ),
        # Widen recipient to match (keep for backward compat)
        migrations.AlterField(
            model_name='transactionqueue',
            name='recipient',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
