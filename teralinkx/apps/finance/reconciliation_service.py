"""
Automated Reconciliation Engine
Matches payments to invoices with confidence scoring.
"""
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from finance.models import PaymentTransaction
from finance.models_reconciliation import ReconciliationJob, ReconciliationMatch, ReconciliationRule
import uuid


class ReconciliationEngine:
    """Automated payment reconciliation with confidence scoring"""
    
    def __init__(self):
        self.rules = ReconciliationRule.get_active_rules()
    
    def create_job(self, period_start, period_end, initiated_by=None):
        """Create new reconciliation job"""
        job_id = f"REC-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        job = ReconciliationJob.objects.create(
            job_id=job_id,
            period_start=period_start,
            period_end=period_end,
            initiated_by=initiated_by
        )
        
        return job
    
    def process_job(self, job, source_items):
        """
        Process reconciliation job
        
        Args:
            job: ReconciliationJob instance
            source_items: List of dicts with keys: reference, amount, date, customer_info, description
        """
        job.start_processing()
        job.total_items = len(source_items)
        job.save()
        
        try:
            for item in source_items:
                self._process_item(job, item)
            
            # Update job statistics
            job.matched_items = job.matches.filter(match_action='auto').count()
            job.review_items = job.matches.filter(match_action='review').count()
            job.unmatched_items = job.matches.filter(status='unmatched').count()
            
            # Calculate average confidence
            matches = job.matches.all()
            if matches:
                job.average_confidence = sum(m.confidence_score for m in matches) / len(matches)
            
            job.complete()
            
        except Exception as e:
            job.fail(str(e))
            raise
        
        return job
    
    def _process_item(self, job, item):
        """Process single reconciliation item"""
        # Find candidate transactions
        candidates = self._find_candidates(item)
        
        if not candidates:
            # No candidates - create unmatched record
            ReconciliationMatch.objects.create(
                job=job,
                source_reference=item['reference'],
                source_amount=item['amount'],
                source_date=item['date'],
                source_customer_info=item.get('customer_info', ''),
                source_description=item.get('description', ''),
                status='unmatched',
                match_action='manual',
                confidence_score=0.0,
                amount_match_score=0.0,
                customer_match_score=0.0,
                date_match_score=0.0
            )
            return
        
        # Score each candidate
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score_data = self._calculate_confidence(item, candidate)
            
            if score_data['confidence'] > best_score:
                best_score = score_data['confidence']
                best_match = (candidate, score_data)
        
        # Create match record
        if best_match:
            transaction, score_data = best_match
            
            # Determine action based on confidence
            if score_data['confidence'] >= 0.85:
                match_action = 'auto'
                status = 'matched'
            elif score_data['confidence'] >= 0.60:
                match_action = 'review'
                status = 'pending'
            else:
                match_action = 'manual'
                status = 'unmatched'
            
            ReconciliationMatch.objects.create(
                job=job,
                source_reference=item['reference'],
                source_amount=item['amount'],
                source_date=item['date'],
                source_customer_info=item.get('customer_info', ''),
                source_description=item.get('description', ''),
                transaction_id_ref=transaction.transaction_id,
                match_action=match_action,
                status=status,
                confidence_score=score_data['confidence'],
                amount_match_score=score_data['amount_score'],
                customer_match_score=score_data['customer_score'],
                date_match_score=score_data['date_score'],
                match_factors=score_data['factors']
            )
    
    def _find_candidates(self, item):
        """Find candidate transactions for matching"""
        amount = Decimal(str(item['amount']))
        date = item['date']
        
        # Search within ±7 days and ±5% amount
        date_start = date - timedelta(days=7)
        date_end = date + timedelta(days=7)
        amount_min = amount * Decimal('0.95')
        amount_max = amount * Decimal('1.05')
        
        candidates = PaymentTransaction.objects.filter(
            created_at__date__gte=date_start,
            created_at__date__lte=date_end,
            amount__gte=amount_min,
            amount__lte=amount_max,
            status='completed'
        )[:10]  # Limit to top 10 candidates
        
        return list(candidates)
    
    def _calculate_confidence(self, item, transaction):
        """Calculate confidence score for match"""
        scores = {}
        factors = {}
        
        # Amount matching (50 points)
        amount_diff = abs(Decimal(str(item['amount'])) - transaction.amount)
        amount_pct = float(amount_diff / transaction.amount) if transaction.amount > 0 else 1.0
        
        if amount_pct == 0:
            scores['amount'] = 50.0
            factors['amount'] = 'Exact match'
        elif amount_pct < 0.02:
            scores['amount'] = 35.0
            factors['amount'] = f'Within 2% (diff: {amount_diff})'
        elif amount_pct < 0.05:
            scores['amount'] = 20.0
            factors['amount'] = f'Within 5% (diff: {amount_diff})'
        else:
            scores['amount'] = 0.0
            factors['amount'] = f'Difference: {amount_diff}'
        
        # Customer matching (30 points)
        customer_info = item.get('customer_info', '').lower()
        if transaction.user:
            account = transaction.user.account.lower()
            phone = transaction.user.phone_number
            
            if account in customer_info or customer_info in account:
                scores['customer'] = 30.0
                factors['customer'] = 'Account match'
            elif phone and phone in customer_info:
                scores['customer'] = 30.0
                factors['customer'] = 'Phone match'
            elif self._fuzzy_match(customer_info, account):
                scores['customer'] = 20.0
                factors['customer'] = 'Fuzzy name match'
            else:
                scores['customer'] = 0.0
                factors['customer'] = 'No customer match'
        else:
            scores['customer'] = 0.0
            factors['customer'] = 'No customer data'
        
        # Date proximity (15 points)
        date_diff = abs((item['date'] - transaction.created_at.date()).days)
        if date_diff == 0:
            scores['date'] = 15.0
            factors['date'] = 'Same day'
        elif date_diff <= 3:
            scores['date'] = 10.0
            factors['date'] = f'{date_diff} days apart'
        elif date_diff <= 7:
            scores['date'] = 5.0
            factors['date'] = f'{date_diff} days apart'
        else:
            scores['date'] = 0.0
            factors['date'] = f'{date_diff} days apart'
        
        # Phone matching (5 points)
        if transaction.initiator and item.get('customer_info'):
            if transaction.initiator in item['customer_info']:
                scores['phone'] = 5.0
                factors['phone'] = 'Phone match'
            else:
                scores['phone'] = 0.0
                factors['phone'] = 'No phone match'
        else:
            scores['phone'] = 0.0
            factors['phone'] = 'No phone data'
        
        # Calculate total confidence (0-1 scale)
        total_score = sum(scores.values())
        confidence = total_score / 100.0
        
        return {
            'confidence': confidence,
            'amount_score': scores['amount'] / 50.0,
            'customer_score': scores['customer'] / 30.0,
            'date_score': scores['date'] / 15.0,
            'factors': factors
        }
    
    def _fuzzy_match(self, str1, str2):
        """Simple fuzzy string matching"""
        # Levenshtein distance < 3
        if len(str1) < 3 or len(str2) < 3:
            return False
        
        # Check if one contains the other
        if str1 in str2 or str2 in str1:
            return True
        
        # Simple character overlap check
        set1 = set(str1.replace(' ', ''))
        set2 = set(str2.replace(' ', ''))
        overlap = len(set1 & set2) / max(len(set1), len(set2))
        
        return overlap > 0.7


def reconcile_payments(period_start, period_end, source_items, initiated_by=None):
    """
    Main reconciliation function
    
    Args:
        period_start: Start date
        period_end: End date
        source_items: List of payment records from bank statement
        initiated_by: User who initiated reconciliation
    
    Returns:
        ReconciliationJob instance
    """
    engine = ReconciliationEngine()
    job = engine.create_job(period_start, period_end, initiated_by)
    engine.process_job(job, source_items)
    return job
