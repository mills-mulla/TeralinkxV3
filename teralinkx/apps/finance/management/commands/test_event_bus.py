"""
Test Event Bus
Verifies signal firing and handler execution.
"""
from django.core.management.base import BaseCommand
from apps.finance.signals import (
    payment_completed,
    expense_created,
    budget_threshold_exceeded,
    hids_anomaly_detected,
    customer_churn_risk_high
)
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test event bus signal firing and handler execution'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== EVENT BUS TEST ===\n'))
        
        # Test payment_completed signal
        self.stdout.write('Testing payment_completed signal...')
        try:
            payment_completed.send(
                sender=self.__class__,
                payment=type('Payment', (), {
                    'transaction_id': 'TEST123',
                    'user_id': 1,
                    'amount': 1000
                })()
            )
            self.stdout.write(self.style.SUCCESS('  ✓ payment_completed signal fired'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
        
        # Test expense_created signal
        self.stdout.write('\nTesting expense_created signal...')
        try:
            expense_created.send(
                sender=self.__class__,
                expense=type('Expense', (), {
                    'id': 1,
                    'category': 'utilities',
                    'amount': 5000,
                    'date': timezone.now()
                })()
            )
            self.stdout.write(self.style.SUCCESS('  ✓ expense_created signal fired'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
        
        # Test budget_threshold_exceeded signal
        self.stdout.write('\nTesting budget_threshold_exceeded signal...')
        try:
            budget_threshold_exceeded.send(
                sender=self.__class__,
                budget=type('Budget', (), {
                    'category': 'utilities',
                    'alert_threshold': 80
                })(),
                utilization_rate=85
            )
            self.stdout.write(self.style.SUCCESS('  ✓ budget_threshold_exceeded signal fired'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
        
        # Test hids_anomaly_detected signal
        self.stdout.write('\nTesting hids_anomaly_detected signal...')
        try:
            hids_anomaly_detected.send(
                sender=self.__class__,
                anomaly={
                    'type': 'port_scan',
                    'src_ip': '192.168.1.100',
                    'timestamp': timezone.now().isoformat()
                }
            )
            self.stdout.write(self.style.SUCCESS('  ✓ hids_anomaly_detected signal fired'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
        
        # Test customer_churn_risk_high signal
        self.stdout.write('\nTesting customer_churn_risk_high signal...')
        try:
            customer_churn_risk_high.send(
                sender=self.__class__,
                customer=type('Customer', (), {
                    'id': 1,
                    'get_mrr': lambda: 3000
                })(),
                churn_score=0.85
            )
            self.stdout.write(self.style.SUCCESS('  ✓ customer_churn_risk_high signal fired'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n\n=== TEST COMPLETE ==='))
        self.stdout.write('Check logs for handler execution confirmation')
