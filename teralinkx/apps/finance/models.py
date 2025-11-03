# apps/finance/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model

from apps.core.models import TimeStampedModel, StatusTrackedModel

User = get_user_model()

class PaymentGateway(TimeStampedModel, StatusTrackedModel):
    """Enhanced payment gateway management"""
    GATEWAY_TYPES = [
        ('mpesa', 'M-Pesa'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('card', 'Credit Card'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]
    
    name = models.CharField(max_length=100)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    is_default = models.BooleanField(default=False)
    
    # Configuration
    config = models.JSONField(default=dict)
    webhook_url = models.URLField(blank=True)
    callback_url = models.URLField(blank=True)
    
    # Fees
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    transaction_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    test_mode = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)
    
    def __str__(self):
        mode = "TEST" if self.test_mode else "LIVE"
        return f"{self.name} ({self.get_gateway_type_display()}) - {mode}"
    
    class Meta:
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"
        indexes = [
            models.Index(fields=['gateway_type']),
            models.Index(fields=['is_default']),
            models.Index(fields=['test_mode']),
        ]

class BalanceTransaction(TimeStampedModel):
    """Comprehensive financial audit trail"""
    TRANSACTION_TYPES = [
        ('voucher_purchase', 'Voucher Purchase'),
        ('balance_topup', 'Balance Top-up'),
        ('refund', 'Refund'),
        ('usage_charge', 'Usage Charge'),
        ('adjustment', 'Adjustment'),
        ('roaming_charge', 'Roaming Charge'),
        ('initial_deposit', 'Initial Deposit'),
        ('commission', 'Commission Payment'),
        ('payout', 'Payout'),
    ]
    
    TRANSACTION_DIRECTIONS = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    user = models.ForeignKey('users.ClientH', on_delete=models.CASCADE, related_name='balance_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    direction = models.CharField(max_length=10, choices=TRANSACTION_DIRECTIONS)
    
    # Amounts
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # References
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    external_reference = models.CharField(max_length=255, blank=True)
    
    # Context
    location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True)
    voucher = models.ForeignKey('packages.DispatchVoucher', on_delete=models.SET_NULL, null=True, blank=True)
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    is_reversible = models.BooleanField(default=False)
    reversed_at = models.DateTimeField(null=True, blank=True)
    reversal_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.account} - {self.transaction_type} - {self.direction} KES {self.amount}"
    
    @property
    def net_amount(self):
        """Get net amount after fees"""
        if self.direction == 'debit':
            return -(self.amount + self.fee_amount)
        return self.amount - self.fee_amount
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['direction']),
            models.Index(fields=['reference']),
            models.Index(fields=['location']),
        ]
        ordering = ['-created_at']

class Investment(TimeStampedModel):
    """Comprehensive business investment tracking"""
    INVESTMENT_TYPES = [
        ('seed', 'Seed Funding'),
        ('angel', 'Angel Investment'),
        ('vc', 'Venture Capital'),
        ('loan', 'Business Loan'),
        ('personal', 'Personal Investment'),
        ('grant', 'Grant'),
        ('crowdfunding', 'Crowdfunding'),
        ('other', 'Other'),
    ]
    
    INVESTMENT_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('active', 'Active'),
        ('matured', 'Matured'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Investment Details
    investor_name = models.CharField(max_length=255)
    investor_type = models.CharField(max_length=50, choices=[
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('vc_firm', 'VC Firm'),
        ('bank', 'Bank'),
        ('government', 'Government'),
        ('other', 'Other'),
    ], default='individual')
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES, default='other')
    
    # Financial Details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    amount_local = models.DecimalField(max_digits=15, decimal_places=2, help_text="Amount in local currency")
    
    # Terms & Conditions
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    valuation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Company valuation at investment")
    term_months = models.IntegerField(null=True, blank=True, help_text="Investment term in months")
    
    # Dates
    investment_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=INVESTMENT_STATUS, default='pending')
    is_active = models.BooleanField(default=True)
    risk_rating = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], default='medium')
    
    # Documentation
    contract_reference = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)
    
    # Contact Information
    investor_email = models.EmailField(blank=True)
    investor_phone = models.CharField(max_length=20, blank=True)
    investor_address = models.TextField(blank=True)
    
    # Repayment Information (for loans)
    repayment_schedule = models.JSONField(default=dict, help_text="Repayment schedule details")
    total_repaid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_investments')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_investments')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.investor_name} - {self.get_investment_type_display()} - KES {self.amount_local}"
    
    def save(self, *args, **kwargs):
        if not self.amount_local:
            self.amount_local = self.amount * self.exchange_rate
        super().save(*args, **kwargs)
    
    @property
    def outstanding_balance(self):
        """Calculate outstanding balance for loans"""
        if self.investment_type == 'loan':
            return self.amount_local - self.total_repaid
        return Decimal('0')
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_overdue(self):
        """Check if investment is overdue"""
        if self.due_date and self.status in ['active', 'disbursed']:
            return timezone.now().date() > self.due_date
        return False
    
    def record_repayment(self, amount, payment_date=None, reference=""):
        """Record a repayment"""
        if payment_date is None:
            payment_date = timezone.now().date()
        
        self.total_repaid += amount
        self.save()
        
        InvestmentRepayment.objects.create(
            investment=self,
            amount=amount,
            payment_date=payment_date,
            reference=reference
        )
        
        if self.outstanding_balance <= 0:
            self.status = 'matured'
            self.save()
    
    def get_expected_return(self):
        """Calculate expected return on investment"""
        if self.investment_type == 'loan' and self.interest_rate:
            return self.amount_local * (self.interest_rate / 100)
        elif self.equity_percentage and self.valuation:
            return (self.equity_percentage / 100) * self.valuation
        return Decimal('0')
    
    class Meta:
        indexes = [
            models.Index(fields=['investment_type']),
            models.Index(fields=['status']),
            models.Index(fields=['investment_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['investor_name']),
        ]
        ordering = ['-investment_date']
        verbose_name = "Investment"
        verbose_name_plural = "Investments"

class InvestmentRepayment(TimeStampedModel):
    """Investment repayment tracking"""
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ], default='bank_transfer')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Repayment of KES {self.amount} for {self.investment}"
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Investment Repayment"
        verbose_name_plural = "Investment Repayments"

class Expense(TimeStampedModel):
    """Comprehensive business expense tracking with budgeting"""
    EXPENSE_CATEGORIES = [
        ('network_infra', 'Network Infrastructure'),
        ('hardware', 'Hardware Purchase'),
        ('software', 'Software & Licensing'),
        ('maintenance', 'Maintenance & Repairs'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent & Leases'),
        ('salaries', 'Salaries & Wages'),
        ('marketing', 'Marketing & Advertising'),
        ('travel', 'Travel & Transportation'),
        ('office', 'Office Supplies'),
        ('professional', 'Professional Services'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes & Fees'),
        ('other', 'Other Expenses'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
        ('cheque', 'Cheque'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('other', 'Other'),
    ]
    
    # Expense Details
    expense_date = models.DateField()
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, default='other')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    
    # Vendor Information
    vendor = models.CharField(max_length=255, blank=True, null=True)
    vendor_contact = models.CharField(max_length=255, blank=True)
    vendor_tin = models.CharField(max_length=50, blank=True, help_text="Vendor Tax Identification Number")
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='bank_transfer')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Location & Department
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, help_text="Department or cost center")
    
    # Budget & Approval
    budget_category = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    approved_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    # Recurring Expenses
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], blank=True)
    next_recurrence = models.DateField(null=True, blank=True)
    
    # Tax Information
    is_tax_deductible = models.BooleanField(default=True)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    withholding_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Attachments
    attachment = models.FileField(upload_to='expense_attachments/', blank=True, null=True)
    
    # Status
    is_reimbursable = models.BooleanField(default=False)
    reimbursement_status = models.CharField(max_length=20, choices=[
        ('not_applicable', 'Not Applicable'),
        ('pending', 'Pending Reimbursement'),
        ('reimbursed', 'Reimbursed'),
        ('denied', 'Reimbursement Denied'),
    ], default='not_applicable')
    
    def __str__(self):
        return f"{self.expense_date} | {self.get_category_display()} | KES {self.amount}"
    
    @property
    def total_amount(self):
        """Get total amount including taxes"""
        return self.amount + self.vat_amount + self.withholding_tax
    
    @property
    def is_over_budget(self):
        """Check if expense is over budget"""
        return False
    
    @property
    def age_in_days(self):
        """Get age of expense in days"""
        return (timezone.now().date() - self.expense_date).days
    
    def approve(self, approved_by):
        """Approve expense"""
        self.is_approved = True
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()
    
    def create_recurring_instance(self):
        """Create next recurring expense instance"""
        if not self.is_recurring or not self.recurrence_pattern:
            return None
        
        next_date = self.expense_date
        
        if self.recurrence_pattern == 'monthly':
            next_date = next_date.replace(month=next_date.month + 1)
        elif self.recurrence_pattern == 'weekly':
            next_date = next_date + timedelta(weeks=1)
        
        new_expense = Expense.objects.create(
            expense_date=next_date,
            category=self.category,
            description=f"Recurring: {self.description}",
            amount=self.amount,
            vendor=self.vendor,
            payment_method=self.payment_method,
            location=self.location,
            department=self.department,
            is_recurring=True,
            recurrence_pattern=self.recurrence_pattern,
            next_recurrence=self.calculate_next_recurrence(next_date)
        )
        
        return new_expense
    
    def calculate_next_recurrence(self, current_date):
        """Calculate next recurrence date"""
        return current_date
    
    @classmethod
    def get_expense_summary(cls, start_date, end_date, location=None):
        """Get expense summary for period"""
        from django.db.models import Sum, Count
        
        expenses = cls.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date,
            is_approved=True
        )
        
        if location:
            expenses = expenses.filter(location=location)
        
        summary = expenses.aggregate(
            total_amount=Sum('amount'),
            total_expenses=Count('id'),
            average_expense=Sum('amount') / Count('id')
        )
        
        categories = expenses.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        summary['category_breakdown'] = list(categories)
        
        return summary
    
    class Meta:
        indexes = [
            models.Index(fields=['expense_date']),
            models.Index(fields=['category']),
            models.Index(fields=['location']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['vendor']),
        ]
        ordering = ['-expense_date']
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"