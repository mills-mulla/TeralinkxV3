# apps/finance/models_asset.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date
from core.models import TimeStampedModel


class Asset(TimeStampedModel):
    """Fixed asset register with automatic depreciation."""

    ASSET_CATEGORIES = [
        ('network_equipment', 'Network Equipment'),
        ('vehicles',          'Vehicles'),
        ('computers',         'Computers & IT'),
        ('furniture',         'Furniture & Fixtures'),
        ('buildings',         'Buildings'),
        ('land',              'Land'),
        ('other',             'Other'),
    ]

    DEPRECIATION_METHODS = [
        ('straight_line',     'Straight Line'),
        ('reducing_balance',  'Reducing Balance'),
        ('none',              'No Depreciation (Land)'),
    ]

    STATUS_CHOICES = [
        ('active',    'Active'),
        ('disposed',  'Disposed'),
        ('written_off', 'Written Off'),
    ]

    # Identity
    asset_number    = models.CharField(max_length=30, unique=True, db_index=True)
    name            = models.CharField(max_length=200)
    category        = models.CharField(max_length=30, choices=ASSET_CATEGORIES)
    description     = models.TextField(blank=True)

    # Purchase
    purchase_date   = models.DateField()
    purchase_cost   = models.DecimalField(max_digits=14, decimal_places=2)
    supplier        = models.CharField(max_length=200, blank=True)
    invoice_number  = models.CharField(max_length=100, blank=True)

    # Depreciation
    useful_life_years = models.IntegerField(help_text='Expected useful life in years')
    depreciation_method = models.CharField(max_length=20, choices=DEPRECIATION_METHODS, default='straight_line')
    salvage_value   = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                          help_text='Residual value at end of life')
    
    # Current values
    accumulated_depreciation = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    current_book_value = models.DecimalField(max_digits=14, decimal_places=2)

    # Organization
    department      = models.ForeignKey('finance.Department', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    location        = models.CharField(max_length=200, blank=True)

    # Status
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    disposal_date   = models.DateField(null=True, blank=True)
    disposal_value  = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    disposal_notes  = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.asset_number} — {self.name} — KES {self.current_book_value}"

    @classmethod
    def generate_number(cls):
        year = timezone.now().year
        last = cls.objects.filter(asset_number__startswith=f'AST-{year}-').order_by('-asset_number').first()
        seq = int(last.asset_number.split('-')[-1]) + 1 if last else 1
        return f'AST-{year}-{seq:04d}'

    @property
    def monthly_depreciation(self):
        """Calculate monthly depreciation amount."""
        if self.depreciation_method == 'none' or self.status != 'active':
            return Decimal('0')

        if self.depreciation_method == 'straight_line':
            depreciable = self.purchase_cost - self.salvage_value
            months = self.useful_life_years * 12
            return (depreciable / months).quantize(Decimal('0.01'))
        
        elif self.depreciation_method == 'reducing_balance':
            # 20% reducing balance per year = 1.67% per month on current book value
            rate = Decimal('0.0167')
            return (self.current_book_value * rate).quantize(Decimal('0.01'))
        
        return Decimal('0')

    @property
    def age_months(self):
        """How many months since purchase."""
        today = date.today()
        return (today.year - self.purchase_date.year) * 12 + (today.month - self.purchase_date.month)

    @property
    def remaining_life_months(self):
        """Months of useful life remaining."""
        total_months = self.useful_life_years * 12
        return max(0, total_months - self.age_months)

    def calculate_depreciation_to_date(self):
        """Calculate total depreciation from purchase to today."""
        if self.depreciation_method == 'none':
            return Decimal('0')

        months = self.age_months
        if self.depreciation_method == 'straight_line':
            depreciable = self.purchase_cost - self.salvage_value
            monthly = depreciable / (self.useful_life_years * 12)
            total = monthly * months
            return min(total, depreciable).quantize(Decimal('0.01'))
        
        elif self.depreciation_method == 'reducing_balance':
            # Compound depreciation
            rate_annual = Decimal('0.20')
            years = Decimal(str(months / 12))
            depreciated = self.purchase_cost * (1 - rate_annual) ** years
            return (self.purchase_cost - depreciated).quantize(Decimal('0.01'))
        
        return Decimal('0')

    def update_book_value(self):
        """Recalculate and update current book value."""
        self.accumulated_depreciation = self.calculate_depreciation_to_date()
        self.current_book_value = self.purchase_cost - self.accumulated_depreciation
        self.save()

    def dispose(self, disposal_date, disposal_value, notes=''):
        """Record asset disposal and calculate gain/loss."""
        self.status = 'disposed'
        self.disposal_date = disposal_date
        self.disposal_value = disposal_value
        self.disposal_notes = notes
        self.update_book_value()
        
        gain_loss = disposal_value - self.current_book_value
        self.save()
        return gain_loss

    @classmethod
    def create_from_expense(cls, expense):
        """Create asset from a CapEx expense."""
        if not expense.is_capex:
            raise ValueError('Expense must be marked as CapEx')

        asset = cls.objects.create(
            asset_number = cls.generate_number(),
            name = expense.description[:200],
            category = 'network_equipment' if expense.category == 'network' else 'other',
            description = expense.description,
            purchase_date = expense.expense_date,
            purchase_cost = expense.amount,
            supplier = expense.vendor or '',
            invoice_number = expense.invoice_number or '',
            useful_life_years = expense.asset_life_years,
            depreciation_method = expense.depreciation_method,
            current_book_value = expense.amount,
            department = expense.department,
        )
        return asset
