"""
Test Reconciliation System
Tests automated payment reconciliation with confidence scoring.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from finance.reconciliation_service import ReconciliationService
from finance.models_reconciliation import ReconciliationJob, ReconciliationMatch, ReconciliationRule


class Command(BaseCommand):
    help = 'Test automated reconciliation system'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== TESTING RECONCILIATION SYSTEM ===\n'))
        
        # Test 1: Check service initialization
        self.stdout.write('Test 1: Service Initialization')
        service = ReconciliationService()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Service initialized'))
        self.stdout.write(f'  Auto-match threshold: {service.AUTO_MATCH_THRESHOLD}')
        self.stdout.write(f'  Review threshold: {service.REVIEW_THRESHOLD}')
        self.stdout.write(f'  Scoring weights: Amount={service.AMOUNT_WEIGHT}, Customer={service.CUSTOMER_WEIGHT}, Date={service.DATE_WEIGHT}\n')
        
        # Test 2: Create default rules
        self.stdout.write('Test 2: Creating Default Rules')
        self._create_default_rules()
        rules_count = ReconciliationRule.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ {rules_count} active rules configured\n'))
        
        # Test 3: Test confidence scoring
        self.stdout.write('Test 3: Confidence Scoring Algorithm')
        self._test_confidence_scoring(service)
        
        # Test 4: Test reconciliation job
        self.stdout.write('\nTest 4: Reconciliation Job')
        self._test_reconciliation_job(service)
        
        # Test 5: Show statistics
        self.stdout.write('\nTest 5: System Statistics')
        self._show_statistics()
        
        self.stdout.write(self.style.SUCCESS('\n=== RECONCILIATION SYSTEM TEST COMPLETE ==='))
    
    def _create_default_rules(self):
        """Create default reconciliation rules"""
        # Amount tolerance rule
        ReconciliationRule.objects.get_or_create(
            name='Standard Amount Tolerance',
            rule_type='amount_tolerance',
            defaults={
                'description': '5% tolerance for amount matching',
                'config': {'tolerance_percentage': 5},
                'is_active': True,
                'priority': 10
            }
        )
        
        # Date range rule
        ReconciliationRule.objects.get_or_create(
            name='Standard Date Range',
            rule_type='date_range',
            defaults={
                'description': '7-day window for date matching',
                'config': {'days': 7},
                'is_active': True,
                'priority': 10
            }
        )
        
        # Auto-match threshold rule
        ReconciliationRule.objects.get_or_create(
            name='High Confidence Auto-Match',
            rule_type='auto_match_threshold',
            defaults={
                'description': 'Auto-match when confidence >= 85%',
                'config': {'threshold': 0.85},
                'is_active': True,
                'priority': 10
            }
        )
    
    def _test_confidence_scoring(self, service):
        """Test confidence scoring with various scenarios"""
        test_cases = [
            {
                'name': 'Exact Match',
                'source': {'amount': Decimal('1000.00'), 'date': date.today()},
                'transaction': {'amount': Decimal('1000.00'), 'date': date.today()},
                'expected': 'High'
            },
            {
                'name': 'Within 2% Amount',
                'source': {'amount': Decimal('1000.00'), 'date': date.today()},
                'transaction': {'amount': Decimal('1015.00'), 'date': date.today()},
                'expected': 'High'
            },
            {
                'name': 'Within 5% Amount',
                'source': {'amount': Decimal('1000.00'), 'date': date.today()},
                'transaction': {'amount': Decimal('1045.00'), 'date': date.today()},
                'expected': 'Medium'
            },
            {
                'name': '3 Days Apart',
                'source': {'amount': Decimal('1000.00'), 'date': date.today()},
                'transaction': {'amount': Decimal('1000.00'), 'date': date.today() - timedelta(days=3)},
                'expected': 'High'
            },
        ]
        
        for test in test_cases:
            amount_score = service._score_amount_match(
                test['source']['amount'],
                test['transaction']['amount']
            )
            date_score = service._score_date_match(
                test['source']['date'],
                test['transaction']['date']
            )
            
            # Simplified confidence (no customer matching in test)
            confidence = (amount_score * 0.4) + (date_score * 0.25) + (0.5 * 0.35)
            
            self.stdout.write(
                f"  {test['name']}: "
                f"Amount={amount_score:.2f}, Date={date_score:.2f}, "
                f"Confidence={confidence:.2f}"
            )
    
    def _test_reconciliation_job(self, service):
        """Test reconciliation job creation"""
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        job = service.reconcile_period(start_date, end_date)
        
        self.stdout.write(f'  Job ID: {job.job_id}')
        self.stdout.write(f'  Status: {job.status}')
        self.stdout.write(f'  Period: {job.period_start} to {job.period_end}')
        self.stdout.write(f'  Total Items: {job.total_items}')
        self.stdout.write(f'  Matched: {job.matched_items}')
        self.stdout.write(f'  Review: {job.review_items}')
        self.stdout.write(f'  Unmatched: {job.unmatched_items}')
        
        if job.auto_match_rate is not None:
            self.stdout.write(self.style.SUCCESS(f'  Auto-Match Rate: {job.auto_match_rate:.1f}%'))
        
        if job.status == 'completed':
            self.stdout.write(self.style.SUCCESS('  ✓ Job completed successfully'))
        else:
            self.stdout.write(self.style.WARNING(f'  Job status: {job.status}'))
    
    def _show_statistics(self):
        """Show reconciliation statistics"""
        total_jobs = ReconciliationJob.objects.count()
        completed_jobs = ReconciliationJob.objects.filter(status='completed').count()
        
        self.stdout.write(f'  Total Jobs: {total_jobs}')
        self.stdout.write(f'  Completed Jobs: {completed_jobs}')
        
        if completed_jobs > 0:
            from django.db.models import Avg, Sum
            
            stats = ReconciliationJob.objects.filter(status='completed').aggregate(
                avg_auto_match=Avg('auto_match_rate'),
                avg_confidence=Avg('average_confidence'),
                total_matched=Sum('matched_items'),
                total_review=Sum('review_items'),
                total_unmatched=Sum('unmatched_items')
            )
            
            self.stdout.write(f"  Average Auto-Match Rate: {stats['avg_auto_match']:.1f}%")
            self.stdout.write(f"  Average Confidence: {stats['avg_confidence']:.2f}")
            self.stdout.write(f"  Total Matched: {stats['total_matched']}")
            self.stdout.write(f"  Total Review: {stats['total_review']}")
            self.stdout.write(f"  Total Unmatched: {stats['total_unmatched']}")
        
        # Show review queue
        review_queue = ReconciliationMatch.get_review_queue()
        self.stdout.write(f'\n  Review Queue: {review_queue.count()} items')
        
        if review_queue.exists():
            self.stdout.write('  Top 5 items needing review:')
            for match in review_queue[:5]:
                self.stdout.write(
                    f'    {match.source_reference}: KES {match.source_amount:,.2f} '
                    f'(Confidence: {match.confidence_score:.2f})'
                )
