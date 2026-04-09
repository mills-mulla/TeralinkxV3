# apps/finance/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Count, Avg
from django.db.models.functions import ExtractHour
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel, StatusTrackedModel

User = get_user_model()


class MLModel(models.Model):
    """ML Model Registry for version control and deployment management"""
    name = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    MODEL_TYPE_CHOICES = [('classification', 'Classification'), ('regression', 'Regression'), ('forecasting', 'Time Series Forecasting')]
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    USE_CASE_CHOICES = [('churn_prediction', 'Churn Prediction'), ('fraud_detection', 'Fraud Detection'), ('cash_flow_forecast', 'Cash Flow Forecasting')]
    use_case = models.CharField(max_length=50, choices=USE_CASE_CHOICES)
    model_file_path = models.CharField(max_length=500)
    accuracy = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    auc_roc = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    feature_importance = models.JSONField(null=True, blank=True)
    training_data_size = models.IntegerField(null=True, blank=True)
    training_date = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [('training', 'Training'), ('testing', 'Testing'), ('active', 'Active'), ('inactive', 'Inactive')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training')
    is_active = models.BooleanField(default=False)
    FALLBACK_CHOICES = [('rule_based', 'Rule-Based Model'), ('previous_version', 'Previous Model Version'), ('none', 'No Fallback')]
    fallback_strategy = models.CharField(max_length=50, choices=FALLBACK_CHOICES, default='rule_based')
    fallback_model = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    prediction_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'finance'
        verbose_name = "ML Model"
        verbose_name_plural = "ML Models"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.status})"
    
    def activate(self):
        MLModel.objects.filter(use_case=self.use_case, is_active=True).exclude(id=self.id).update(is_active=False, status='inactive')
        self.is_active = True
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save()
    
    def deactivate(self):
        self.is_active = False
        self.status = 'inactive'
        self.save()
    
    @classmethod
    def get_active_model(cls, use_case):
        try:
            return cls.objects.get(use_case=use_case, is_active=True, status='active')
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def register_model(cls, name, version, use_case, model_file_path, **kwargs):
        return cls.objects.create(name=name, version=version, use_case=use_case, model_file_path=model_file_path, status='testing', **kwargs)


class Currency(TimeStampedModel):
    """
    Universal currency support for all world currencies
    """
    CODE_CHOICES = [
        ('AED', 'UAE Dirham'), ('AFN', 'Afghan Afghani'), ('ALL', 'Albanian Lek'),
        ('AMD', 'Armenian Dram'), ('ANG', 'Netherlands Antillian Guilder'),
        ('AOA', 'Angolan Kwanza'), ('ARS', 'Argentine Peso'), ('AUD', 'Australian Dollar'),
        ('AWG', 'Aruban Florin'), ('AZN', 'Azerbaijani Manat'), ('BAM', 'Bosnia and Herzegovina Mark'),
        ('BBD', 'Barbados Dollar'), ('BDT', 'Bangladeshi Taka'), ('BGN', 'Bulgarian Lev'),
        ('BHD', 'Bahraini Dinar'), ('BIF', 'Burundian Franc'), ('BMD', 'Bermudian Dollar'),
        ('BND', 'Brunei Dollar'), ('BOB', 'Bolivian Boliviano'), ('BRL', 'Brazilian Real'),
        ('BSD', 'Bahamian Dollar'), ('BTN', 'Bhutanese Ngultrum'), ('BWP', 'Botswana Pula'),
        ('BYN', 'Belarusian Ruble'), ('BZD', 'Belize Dollar'), ('CAD', 'Canadian Dollar'),
        ('CDF', 'Congolese Franc'), ('CHF', 'Swiss Franc'), ('CLP', 'Chilean Peso'),
        ('CNY', 'Chinese Renminbi'), ('COP', 'Colombian Peso'), ('CRC', 'Costa Rican Colon'),
        ('CUP', 'Cuban Peso'), ('CVE', 'Cape Verdean Escudo'), ('CZK', 'Czech Koruna'),
        ('DJF', 'Djiboutian Franc'), ('DKK', 'Danish Krone'), ('DOP', 'Dominican Peso'),
        ('DZD', 'Algerian Dinar'), ('EGP', 'Egyptian Pound'), ('ERN', 'Eritrean Nakfa'),
        ('ETB', 'Ethiopian Birr'), ('EUR', 'Euro'), ('FJD', 'Fiji Dollar'),
        ('FKP', 'Falkland Islands Pound'), ('FOK', 'Faroese Króna'), ('GBP', 'Pound Sterling'),
        ('GEL', 'Georgian Lari'), ('GGP', 'Guernsey Pound'), ('GHS', 'Ghanaian Cedi'),
        ('GIP', 'Gibraltar Pound'), ('GMD', 'Gambian Dalasi'), ('GNF', 'Guinean Franc'),
        ('GTQ', 'Guatemalan Quetzal'), ('GYD', 'Guyanese Dollar'), ('HKD', 'Hong Kong Dollar'),
        ('HNL', 'Honduran Lempira'), ('HRK', 'Croatian Kuna'), ('HTG', 'Haitian Gourde'),
        ('HUF', 'Hungarian Forint'), ('IDR', 'Indonesian Rupiah'), ('ILS', 'Israeli New Shekel'),
        ('IMP', 'Manx Pound'), ('INR', 'Indian Rupee'), ('IQD', 'Iraqi Dinar'),
        ('IRR', 'Iranian Rial'), ('ISK', 'Icelandic Króna'), ('JEP', 'Jersey Pound'),
        ('JMD', 'Jamaican Dollar'), ('JOD', 'Jordanian Dinar'), ('JPY', 'Japanese Yen'),
        ('KES', 'Kenyan Shilling'), ('KGS', 'Kyrgyzstani Som'), ('KHR', 'Cambodian Riel'),
        ('KID', 'Kiribati Dollar'), ('KMF', 'Comorian Franc'), ('KRW', 'South Korean Won'),
        ('KWD', 'Kuwaiti Dinar'), ('KYD', 'Cayman Islands Dollar'), ('KZT', 'Kazakhstani Tenge'),
        ('LAK', 'Lao Kip'), ('LBP', 'Lebanese Pound'), ('LKR', 'Sri Lanka Rupee'),
        ('LRD', 'Liberian Dollar'), ('LSL', 'Lesotho Loti'), ('LYD', 'Libyan Dinar'),
        ('MAD', 'Moroccan Dirham'), ('MDL', 'Moldovan Leu'), ('MGA', 'Malagasy Ariary'),
        ('MKD', 'Macedonian Denar'), ('MMK', 'Burmese Kyat'), ('MNT', 'Mongolian Tögrög'),
        ('MOP', 'Macanese Pataca'), ('MRU', 'Mauritanian Ouguiya'), ('MUR', 'Mauritian Rupee'),
        ('MVR', 'Maldivian Rufiyaa'), ('MWK', 'Malawian Kwacha'), ('MXN', 'Mexican Peso'),
        ('MYR', 'Malaysian Ringgit'), ('MZN', 'Mozambican Metical'), ('NAD', 'Namibian Dollar'),
        ('NGN', 'Nigerian Naira'), ('NIO', 'Nicaraguan Córdoba'), ('NOK', 'Norwegian Krone'),
        ('NPR', 'Nepalese Rupee'), ('NZD', 'New Zealand Dollar'), ('OMR', 'Omani Rial'),
        ('PAB', 'Panamanian Balboa'), ('PEN', 'Peruvian Sol'), ('PGK', 'Papua New Guinean Kina'),
        ('PHP', 'Philippine Peso'), ('PKR', 'Pakistani Rupee'), ('PLN', 'Polish Złoty'),
        ('PYG', 'Paraguayan Guaraní'), ('QAR', 'Qatari Riyal'), ('RON', 'Romanian Leu'),
        ('RSD', 'Serbian Dinar'), ('RUB', 'Russian Ruble'), ('RWF', 'Rwandan Franc'),
        ('SAR', 'Saudi Riyal'), ('SBD', 'Solomon Islands Dollar'), ('SCR', 'Seychellois Rupee'),
        ('SDG', 'Sudanese Pound'), ('SEK', 'Swedish Krona'), ('SGD', 'Singapore Dollar'),
        ('SHP', 'Saint Helena Pound'), ('SLE', 'Sierra Leonean Leone'), ('SOS', 'Somali Shilling'),
        ('SRD', 'Surinamese Dollar'), ('SSP', 'South Sudanese Pound'), ('STN', 'São Tomé and Príncipe Dobra'),
        ('SYP', 'Syrian Pound'), ('SZL', 'Eswatini Lilangeni'), ('THB', 'Thai Baht'),
        ('TJS', 'Tajikistani Somoni'), ('TMT', 'Turkmenistan Manat'), ('TND', 'Tunisian Dinar'),
        ('TOP', 'Tongan Paʻanga'), ('TRY', 'Turkish Lira'), ('TTD', 'Trinidad and Tobago Dollar'),
        ('TVD', 'Tuvaluan Dollar'), ('TWD', 'New Taiwan Dollar'), ('TZS', 'Tanzanian Shilling'),
        ('UAH', 'Ukrainian Hryvnia'), ('UGX', 'Ugandan Shilling'), ('USD', 'United States Dollar'),
        ('UYU', 'Uruguayan Peso'), ('UZS', 'Uzbekistani Soʻm'), ('VES', 'Venezuelan Bolívar Soberano'),
        ('VND', 'Vietnamese Đồng'), ('VUV', 'Vanuatu Vatu'), ('WST', 'Samoan Tālā'),
        ('XAF', 'Central African CFA Franc'), ('XCD', 'East Caribbean Dollar'),
        ('XDR', 'Special Drawing Rights'), ('XOF', 'West African CFA Franc'),
        ('XPF', 'CFP Franc'), ('YER', 'Yemeni Rial'), ('ZAR', 'South African Rand'),
        ('ZMW', 'Zambian Kwacha'), ('ZWL', 'Zimbabwean Dollar'),
    ]
    
    code = models.CharField(max_length=3, choices=CODE_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    is_base_currency = models.BooleanField(default=False)
    
    # Currency metadata
    decimal_places = models.IntegerField(default=2)
    is_crypto = models.BooleanField(default=False)
    unicode_symbol = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @classmethod
    def get_currency_data(cls, code):
        """Get currency data for a given code"""
        currency_data = {
            'KES': {'name': 'Kenyan Shilling', 'symbol': 'KSh', 'unicode_symbol': 'KSh', 'decimal_places': 2, 'is_crypto': False},
            'USD': {'name': 'US Dollar', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'EUR': {'name': 'Euro', 'symbol': '€', 'unicode_symbol': '€', 'decimal_places': 2, 'is_crypto': False},
            'GBP': {'name': 'British Pound', 'symbol': '£', 'unicode_symbol': '£', 'decimal_places': 2, 'is_crypto': False},
            'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'unicode_symbol': 'R', 'decimal_places': 2, 'is_crypto': False},
            'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ', 'unicode_symbol': 'د.إ', 'decimal_places': 2, 'is_crypto': False},
            'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'unicode_symbol': '¥', 'decimal_places': 0, 'is_crypto': False},
            'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'unicode_symbol': '¥', 'decimal_places': 2, 'is_crypto': False},
            'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'unicode_symbol': '₹', 'decimal_places': 2, 'is_crypto': False},
            'BTC': {'name': 'Bitcoin', 'symbol': '₿', 'unicode_symbol': '₿', 'decimal_places': 8, 'is_crypto': True},
            'ETH': {'name': 'Ethereum', 'symbol': 'Ξ', 'unicode_symbol': 'Ξ', 'decimal_places': 18, 'is_crypto': True},
            'CAD': {'name': 'Canadian Dollar', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'CHF': {'name': 'Swiss Franc', 'symbol': 'CHF', 'unicode_symbol': 'CHF', 'decimal_places': 2, 'is_crypto': False},
            'AUD': {'name': 'Australian Dollar', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'NZD': {'name': 'New Zealand Dollar', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'SGD': {'name': 'Singapore Dollar', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'HKD': {'name': 'Hong Kong Dollar', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'SEK': {'name': 'Swedish Krona', 'symbol': 'kr', 'unicode_symbol': 'kr', 'decimal_places': 2, 'is_crypto': False},
            'NOK': {'name': 'Norwegian Krone', 'symbol': 'kr', 'unicode_symbol': 'kr', 'decimal_places': 2, 'is_crypto': False},
            'DKK': {'name': 'Danish Krone', 'symbol': 'kr', 'unicode_symbol': 'kr', 'decimal_places': 2, 'is_crypto': False},
            'PLN': {'name': 'Polish Złoty', 'symbol': 'zł', 'unicode_symbol': 'zł', 'decimal_places': 2, 'is_crypto': False},
            'TRY': {'name': 'Turkish Lira', 'symbol': '₺', 'unicode_symbol': '₺', 'decimal_places': 2, 'is_crypto': False},
            'RUB': {'name': 'Russian Ruble', 'symbol': '₽', 'unicode_symbol': '₽', 'decimal_places': 2, 'is_crypto': False},
            'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'unicode_symbol': 'R$', 'decimal_places': 2, 'is_crypto': False},
            'MXN': {'name': 'Mexican Peso', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'ARS': {'name': 'Argentine Peso', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'CLP': {'name': 'Chilean Peso', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 0, 'is_crypto': False},
            'COP': {'name': 'Colombian Peso', 'symbol': '$', 'unicode_symbol': '$', 'decimal_places': 2, 'is_crypto': False},
            'PEN': {'name': 'Peruvian Sol', 'symbol': 'S/', 'unicode_symbol': 'S/', 'decimal_places': 2, 'is_crypto': False},
            'EGP': {'name': 'Egyptian Pound', 'symbol': '£', 'unicode_symbol': '£', 'decimal_places': 2, 'is_crypto': False},
            'NGN': {'name': 'Nigerian Naira', 'symbol': '₦', 'unicode_symbol': '₦', 'decimal_places': 2, 'is_crypto': False},
            'GHS': {'name': 'Ghanaian Cedi', 'symbol': '₵', 'unicode_symbol': '₵', 'decimal_places': 2, 'is_crypto': False},
            'MAD': {'name': 'Moroccan Dirham', 'symbol': 'د.م.', 'unicode_symbol': 'د.م.', 'decimal_places': 2, 'is_crypto': False},
            'THB': {'name': 'Thai Baht', 'symbol': '฿', 'unicode_symbol': '฿', 'decimal_places': 2, 'is_crypto': False},
            'IDR': {'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'unicode_symbol': 'Rp', 'decimal_places': 2, 'is_crypto': False},
            'MYR': {'name': 'Malaysian Ringgit', 'symbol': 'RM', 'unicode_symbol': 'RM', 'decimal_places': 2, 'is_crypto': False},
            'PHP': {'name': 'Philippine Peso', 'symbol': '₱', 'unicode_symbol': '₱', 'decimal_places': 2, 'is_crypto': False},
            'VND': {'name': 'Vietnamese Đồng', 'symbol': '₫', 'unicode_symbol': '₫', 'decimal_places': 0, 'is_crypto': False},
            'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'unicode_symbol': '₩', 'decimal_places': 0, 'is_crypto': False},
            'ILS': {'name': 'Israeli New Shekel', 'symbol': '₪', 'unicode_symbol': '₪', 'decimal_places': 2, 'is_crypto': False},
        }
        return currency_data.get(code, {
            'name': code,
            'symbol': code,
            'unicode_symbol': code,
            'decimal_places': 2,
            'is_crypto': False
        })
    
    def save(self, *args, **kwargs):
        """Auto-populate fields when code is set and other fields are empty"""
        # Only auto-populate if code is set and name is empty (indicating new currency)
        if self.code and not self.name:
            currency_data = self.get_currency_data(self.code)
            self.name = currency_data['name']
            if not self.symbol:
                self.symbol = currency_data['symbol']
            if not self.unicode_symbol:
                self.unicode_symbol = currency_data['unicode_symbol']
            if not self.decimal_places:
                self.decimal_places = currency_data['decimal_places']
            self.is_crypto = currency_data['is_crypto']
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_base_currency(cls):
        """Get the base currency (KES for your business)"""
        return cls.objects.filter(is_base_currency=True).first() or cls.objects.get(code='KES')
    
    @classmethod
    def get_active_currencies(cls):
        """Get all active currencies"""
        return cls.objects.filter(is_active=True)
    
    class Meta:
        # app_label = ""
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ['code']


class ExchangeRate(TimeStampedModel):
    """
    Real-time exchange rate tracking with multiple data sources
    """
    RATE_SOURCES = [
        ('openexchangerates', 'Open Exchange Rates'),
        ('central_bank', 'Central Bank'),
        ('fixer', 'Fixer.io'),
        ('currencylayer', 'CurrencyLayer'),
        ('manual', 'Manual Entry'),
    ]
    
    base_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='base_rates')
    target_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='target_rates')
    rate = models.DecimalField(max_digits=15, decimal_places=6)
    source = models.CharField(max_length=20, choices=RATE_SOURCES, default='openexchangerates')
    is_active = models.BooleanField(default=True)
    
    # Rate metadata
    last_updated = models.DateTimeField(auto_now=True)
    next_update = models.DateTimeField(null=True, blank=True)
    update_frequency = models.DurationField(default=timedelta(hours=1))
    
    def __str__(self):
        return f"1 {self.base_currency.code} = {self.rate} {self.target_currency.code}"
    
    def save(self, *args, **kwargs):
        """Set next update time"""
        if not self.next_update:
            self.next_update = timezone.now() + self.update_frequency
        super().save(*args, **kwargs)
    
    @classmethod
    def get_latest_rate(cls, base_currency_code, target_currency_code):
        """Get the latest exchange rate between two currencies"""
        if base_currency_code == target_currency_code:
            return Decimal('1.0')
        
        try:
            base_currency = Currency.objects.get(code=base_currency_code)
            target_currency = Currency.objects.get(code=target_currency_code)
            
            rate = cls.objects.filter(
                base_currency=base_currency,
                target_currency=target_currency,
                is_active=True
            ).order_by('-last_updated').first()
            
            return rate.rate if rate else Decimal('1.0')
            
        except (Currency.DoesNotExist, cls.DoesNotExist):
            return Decimal('1.0')
    
    @classmethod
    def convert_amount(cls, amount, from_currency_code, to_currency_code):
        """Convert amount between any two currencies"""
        if from_currency_code == to_currency_code:
            return amount
        
        rate = cls.get_latest_rate(from_currency_code, to_currency_code)
        return amount * rate
    
    @classmethod
    def update_rates_from_api(cls, source='openexchangerates'):
        """Update exchange rates from external API"""
        # This would be implemented based on your chosen API
        # Example with Open Exchange Rates
        try:
            # You would add your API key here
            api_key = "YOUR_OPEN_EXCHANGE_RATES_API_KEY"
            # response = requests.get(f"https://openexchangerates.org/api/latest.json?app_id={api_key}")
            # data = response.json()
            
            # For now, return True to indicate success
            # Actual implementation would parse the response and update rates
            return True
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update exchange rates: {e}")
            return False
    
    class Meta:
        unique_together = ['base_currency', 'target_currency']
        indexes = [
            models.Index(fields=['base_currency', 'target_currency']),
            models.Index(fields=['last_updated']),
        ]


class PaymentGateway(TimeStampedModel, StatusTrackedModel):
    """Payment gateway with universal currency support"""
    GATEWAY_TYPES = [
        ('mpesa', 'M-Pesa'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('card', 'Credit Card'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('crypto', 'Cryptocurrency'),
    ]
    
    name = models.CharField(max_length=100)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    is_default = models.BooleanField(default=False)
    
    # Universal currency support
    supported_currencies = models.ManyToManyField(Currency, blank=True)
    default_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='default_gateways')
    
    # Configuration
    config = models.JSONField(default=dict)
    callback_url = models.URLField(
        blank=True,
        default='https://srv.teralinkxwaves.uk/api/payments/callback/',
        help_text="System's callback URL for payment notifications. This is where payment gateways will send transaction updates."
    )
    webhook_url = models.URLField(
        blank=True,
        default='https://srv.teralinkxwaves.uk/api/webhooks/payment/',
        help_text="Webhook URL for real-time payment events (for supported gateways like Stripe)"
    )
    
    # Status
    test_mode = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.get_gateway_type_display()})"
    
    def supports_currency(self, currency_code):
        """Check if gateway supports specific currency"""
        return self.supported_currencies.filter(code=currency_code).exists()
    
    def get_supported_currency_codes(self):
        """Get list of supported currency codes"""
        return list(self.supported_currencies.values_list('code', flat=True))
    
    def get_effective_callback_url(self):
        """Get the appropriate callback URL based on gateway type"""
        # For gateways that need specific callback URLs in their config
        if self.gateway_type in ['mpesa', 'stripe', 'paypal']:
            return self.callback_url
        return self.config.get('callback_url', self.callback_url)
    
    def get_effective_webhook_url(self):
        """Get webhook URL if available, fallback to callback URL"""
        return self.webhook_url or self.callback_url
    
    def clean(self):
        """Validate model data"""
        super().clean()
        
        # Set appropriate default URLs based on gateway type
        if not self.callback_url:
            self.callback_url = 'https://srv.teralinkxwaves.uk/api/payments/callback/'
        
        if not self.webhook_url and self.gateway_type in ['stripe', 'paypal']:
            self.webhook_url = 'https://srv.teralinkxwaves.uk/api/webhooks/payment/'
        
        # Validate configuration based on gateway type
        self._validate_gateway_config()
    
    def _validate_gateway_config(self):
        """Validate configuration based on gateway type"""
        validators = {
            'mpesa': self._validate_mpesa_config,
            'stripe': self._validate_stripe_config,
            'paypal': self._validate_paypal_config,
            'bank': self._validate_bank_config,
            'cash': self._validate_cash_config,
        }
        
        validator = validators.get(self.gateway_type)
        if validator:
            validator()
    
    def _validate_mpesa_config(self):
        """Validate M-Pesa configuration"""
        required_fields = [
            'consumer_key', 'consumer_secret', 
            'shortcode', 'lipa_na_mpesa_passkey'
        ]
        
        for field in required_fields:
            if field not in self.config:
                raise ValidationError(f"M-Pesa config requires '{field}'")
        
        # Set default API URLs if not provided
        if 'api_base_url' not in self.config:
            self.config['api_base_url'] = (
                'https://sandbox.safaricom.co.ke' if self.test_mode 
                else 'https://api.safaricom.co.ke'
            )
        
        if 'access_token_url' not in self.config:
            self.config['access_token_url'] = '/oauth/v1/generate?grant_type=client_credentials'
        
        if 'payment_url' not in self.config:
            self.config['payment_url'] = '/mpesa/stkpush/v1/processrequest'
    
    def _validate_stripe_config(self):
        """Validate Stripe configuration"""
        required_fields = ['secret_key']
        for field in required_fields:
            if field not in self.config:
                raise ValidationError(f"Stripe config requires '{field}'")
    
    def _validate_paypal_config(self):
        """Validate PayPal configuration"""
        required_fields = ['client_id', 'client_secret']
        for field in required_fields:
            if field not in self.config:
                raise ValidationError(f"PayPal config requires '{field}'")
    
    def _validate_bank_config(self):
        """Validate Bank Transfer configuration"""
        required_fields = ['bank_name', 'account_number', 'account_name']
        for field in required_fields:
            if field not in self.config:
                raise ValidationError(f"Bank transfer config requires '{field}'")
    
    def _validate_cash_config(self):
        """Validate Cash payment configuration"""
        if 'instructions' not in self.config:
            self.config['instructions'] = "Pay with cash at our nearest location"
    
    def save(self, *args, **kwargs):
        """Override save to ensure proper URL handling"""
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default_gateway(cls):
        return cls.objects.filter(is_default=True, status='active').first()
    
    @classmethod
    def get_gateway_by_type(cls, gateway_type, currency_code=None):
        """Get active gateway by type, optionally filtering by currency"""
        gateways = cls.objects.filter(
            gateway_type=gateway_type, 
            status='active'
        )
        
        if currency_code:
            gateways = gateways.filter(
                supported_currencies__code=currency_code
            )
        
        return gateways.first()
    
    class Meta:
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"
        ordering = ['-is_default', 'name']


class PaymentTransaction(TimeStampedModel):
    """
    Universal payment transaction supporting all currencies
    ONLY for successful payments that received callbacks
    """
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('mpesa+balance', 'M-Pesa + Balance'),
        ('balance', 'Account Balance'),
        ('stripe', 'Stripe'),
        ('stripe+balance', 'Stripe + Balance'),
        ('card_visa', 'Visa Card'),
        ('card_visa+balance', 'Visa Card + Balance'),
        ('card_mastercard', 'MasterCard'),
        ('card_mastercard+balance', 'MasterCard + Balance'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('paypal', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    # Core Identity
    transaction_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey('users.ClientH', on_delete=models.PROTECT)
    
    # Universal Payment Details
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='mpesa')
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT, null=True, blank=True)
    
    # Universal Multi-Currency Support
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, default=1.0)
    amount_base = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Amount in base currency (KES) for unified reporting"
    )
    
    # V2 Transaction Fields (preserved for compatibility)
    initiator = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=1000, decimal_places=2, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    result_code = models.IntegerField(default=0)
    result_desc = models.CharField(max_length=255, blank=True, default='')
    merchant_request_id = models.CharField(max_length=255, blank=True, default='')
    checkout_request_id = models.CharField(max_length=255, blank=True, default='')
    transaction_time = models.DateTimeField(auto_now_add=True)
    
    # Gateway References
    gateway_reference = models.CharField(max_length=255, blank=True)
    account_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Client account ID from BillRefNumber (e.g. CLI000003)."
    )
    
    # Raw Callback Storage
    raw_callback_data = models.JSONField(default=dict)
    
    # Status field - ADD THIS BACK
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='completed'
    )
    
    # Metadata
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.initiator} - {self.amount} {self.currency.code}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        # Auto-convert to base currency for unified reporting
        if not self.amount_base:
            self.amount_base = self.convert_to_base_currency()
            
        # Auto-set exchange rate
        if self.exchange_rate == 1.0 and self.currency.code != 'KES':
            self.exchange_rate = ExchangeRate.get_latest_rate(self.currency.code, 'KES')
        
        # Auto-populate from raw callback
        if self.raw_callback_data and not self.checkout_request_id:
            self.populate_from_callback_data()
            
        super().save(*args, **kwargs)
    
    def convert_to_base_currency(self):
        """Convert amount to base currency (KES)"""
        if self.currency.code == 'KES':
            return self.amount
        return ExchangeRate.convert_amount(self.amount, self.currency.code, 'KES')
    
    def convert_to_currency(self, target_currency_code):
        """Convert amount to any target currency"""
        return ExchangeRate.convert_amount(self.amount, self.currency.code, target_currency_code)
    
    def generate_transaction_id(self):
        import uuid
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"TXN_{timestamp}_{uuid.uuid4().hex[:8].upper()}"
    
    def populate_from_callback_data(self):
        """Populate fields from raw callback data"""
        try:
            stk_callback = self.raw_callback_data.get('Body', {}).get('stkCallback', {})
            
            self.merchant_request_id = stk_callback.get('MerchantRequestID', '')
            self.checkout_request_id = stk_callback.get('CheckoutRequestID', '')
            self.result_code = stk_callback.get('ResultCode', 0)
            self.result_desc = stk_callback.get('ResultDesc', '')
            
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            for item in callback_metadata:
                name = item.get('Name')
                value = item.get('Value')
                
                if name == 'Amount':
                    self.amount = value
                elif name == 'MpesaReceiptNumber':
                    self.gateway_reference = value
                    if not self.transaction_id.startswith('TXN_'):
                        self.transaction_id = value
                elif name == 'Balance':
                    self.balance = value
                elif name == 'TransactionDate':
                    self.date = str(value)
                elif name == 'PhoneNumber':
                    self.initiator = str(value)
                    if not self.user_id:
                        self.user = self.find_user_by_phone(str(value))
                        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error populating from callback: {e}")
    
    def find_user_by_phone(self, phone_number):
        from apps.users.models import ClientH
        try:
            clean_phone = self.clean_phone_number(phone_number)
            return ClientH.objects.get(phone_number=clean_phone)
        except (ClientH.DoesNotExist, ClientH.MultipleObjectsReturned):
            return None
    
    def clean_phone_number(self, phone):
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '254' + clean_phone[1:]
        elif len(clean_phone) == 9:
            clean_phone = '254' + clean_phone
        return clean_phone

    # Universal currency conversion properties
    @property
    def amount_usd(self):
        return self.convert_to_currency('USD')
    
    @property
    def amount_eur(self):
        return self.convert_to_currency('EUR')
    
    @property
    def amount_gbp(self):
        return self.convert_to_currency('GBP')
    
    def get_amount_in_currency(self, currency_code):
        """Get amount in any currency"""
        return self.convert_to_currency(currency_code)

    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['initiator']),
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['currency']),
            models.Index(fields=['amount_base']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),  
        ]
        ordering = ['-created_at']

class BalanceTransaction(TimeStampedModel):
    """
    Double-entry accounting system for user balances
    Every balance change creates a debit/credit pair
    """
    TRANSACTION_TYPES = [
        ('topup', 'Balance Top-up'),
        ('internet_purchase', 'Internet Package Purchase'),  
        ('ads_credit', 'Ads Revenue'),  
        ('refund', 'Refund'),
        ('adjustment', 'Manual Adjustment'),
        ('bonus', 'Bonus Credit'),
        ('penalty', 'Penalty Charge'),
       
    ]
    
    user = models.ForeignKey(
        'users.ClientH', 
        on_delete=models.PROTECT,
        related_name='balance_transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Accounting Fields
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Balance Tracking
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    # References
    payment_transaction = models.ForeignKey(
        PaymentTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    voucher = models.ForeignKey(
        'packages.DispatchVoucher', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Context
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.account} - {self.transaction_type} - {self.amount}"

    @property
    def amount(self):
        """Get transaction amount"""
        return self.credit if self.credit > 0 else -self.debit

    @property
    def net_effect(self):
        """Get net effect on balance"""
        return self.credit - self.debit
    
    @property
    def is_credit(self):
        """Check if this is a credit transaction"""
        return self.credit > 0
    
    @property
    def is_debit(self):
        """Check if this is a debit transaction"""
        return self.debit > 0

    def save(self, *args, **kwargs):
        """Calculate balance after"""
        if not self.balance_after:
            self.balance_after = self.balance_before + self.net_effect
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Balance Transaction"
        verbose_name_plural = "Balance Transactions"
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type']),
        ]
        ordering = ['-created_at']


class TransactionQueue(TimeStampedModel):
    """
    Enhanced async operation queue with failure analytics
    Handles payment lifecycle and failed transactions
    """
    QUEUE_TYPES = [
        ('payment_processing', 'Payment Processing'),
        ('voucher_activation', 'Voucher Activation'),
        ('balance_purchase', 'Balance Purchase'),  # Added for balance.py operations
        ('balance_topup', 'Balance Top-up'),
        ('auto_renewal', 'Auto Renewal'),
        ('refund_processing', 'Refund Processing'),
    ]
    
    PRIORITY_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ]
    
    FAILURE_CATEGORIES = [
        ('payment_gateway', 'Payment Gateway Failure'),
        ('insufficient_funds', 'Insufficient Funds'),
        ('network_timeout', 'Network Timeout'),
        ('system_error', 'System Error'),
        ('validation_error', 'Validation Error'),
        ('user_error', 'User Error'),
        ('unknown', 'Unknown Error'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),  
        ('processed', 'Processed'),  
    ]
    
    # Core Identity
    queue_type = models.CharField(max_length=20, choices=QUEUE_TYPES, default='payment_processing')
    user = models.ForeignKey('users.ClientH', on_delete=models.PROTECT, related_name='queue_items')
    
    # V2 Queue Fields (preserved)
    method = models.CharField(max_length=255, default='mpesa')
    initiator = models.CharField(max_length=25)
    checkout_request_id = models.CharField(max_length=255, null=True, blank=True)
    package_code = models.CharField(max_length=255)
    package = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    account_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Client account ID (e.g. CLI000003). Maps to BillRefNumber in M-Pesa callbacks."
    )
    used_credit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Enhanced Status Tracking
    failure_reason = models.TextField(blank=True)
    error_code = models.CharField(max_length=100, blank=True)
    failure_category = models.CharField(max_length=20, choices=FAILURE_CATEGORIES, blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    last_retry_at = models.DateTimeField(null=True, blank=True)  # Track when last retry was attempted
    
    # Priority & Timeouts
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    expires_at = models.DateTimeField(null=True, blank=True)
    pending_timeout_hours = models.IntegerField(default=24)
    
    # Gateway Data
    gateway_result_data = models.JSONField(default=dict)
    
    # Analytics
    metadata = models.JSONField(default=dict)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.queue_type} - {self.initiator} - {self.status}"

    @property
    def is_expired(self):
        """Check if queue item has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def pending_duration_hours(self):
        """How long this item has been pending"""
        if self.status in ['pending', 'Pending...']:
            return (timezone.now() - self.created_at).total_seconds() / 3600
        return 0

    @property
    def is_pending_timeout(self):
        """Check if pending item has timed out"""
        return (self.status in ['pending', 'Pending...'] and 
                self.pending_duration_hours >= self.pending_timeout_hours)

    @property
    def can_retry(self):
        """Check if this item is eligible for retry"""
        return (self.status == 'failed' and 
                self.retry_count < self.max_retries and
                not self.is_expired)

    @property
    def next_retry_delay_minutes(self):
        """Calculate exponential backoff delay for next retry"""
        if self.retry_count >= self.max_retries:
            return None
        return 2 ** (self.retry_count + 1)  # 2, 4, 8 minutes

    def mark_completed(self):
        """Mark as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def mark_processing(self):
        """
        Atomic compare-and-swap: only transitions pending → processing.
        Returns True if this caller won the claim, False if already claimed.
        """
        claimed = TransactionQueue.objects.filter(
            pk=self.pk, status='pending'
        ).update(status='processing')
        if claimed:
            self.status = 'processing'
        return bool(claimed)

    def mark_failed(self, reason, error_code='', failure_category='unknown', increment_retry=True):
        """Mark as failed with analytics - ONLY RECORDS, NO RETRY LOGIC"""
        self.status = 'failed'
        self.failure_reason = reason
        self.error_code = error_code
        self.failure_category = failure_category
        self.failed_at = timezone.now()
        
        # ONLY RECORD retry count - no scheduling logic
        if increment_retry:
            self.retry_count += 1
            self.last_retry_at = timezone.now()
        
        self.save()

    def mark_for_retry(self):
        """Mark item as eligible for retry by external service"""
        if self.retry_count < self.max_retries:
            self.status = 'pending'  # Move back to pending for retry
            self.last_retry_at = timezone.now()
            self.save()
            return True
        return False

    def mark_pending_timeout_failure(self, reason=None):
        """Mark a pending item as failed due to timeout"""
        timeout_reason = reason or f"Pending timeout after {self.pending_duration_hours:.1f} hours"
        self.mark_failed(
            reason=timeout_reason,
            error_code="PENDING_TIMEOUT",
            failure_category="system_error",
            increment_retry=False  # Timeouts don't count as retry attempts
        )

    def mark_processed(self):
        """V2 compatibility method"""
        self.status = 'processed'
        self.completed_at = timezone.now()
        self.save()

    @classmethod
    def get_pending_by_checkout_id(cls, checkout_id):
        """Get actionable record by checkout_request_id - includes failed voucher activations for retry"""
        # First try pending/processing
        record = cls.objects.filter(
            checkout_request_id=checkout_id,
            status__in=['pending', 'processing', 'Pending...']  # Handle both V2 and V3
        ).first()
        
        if record:
            return record
            
        # If not found, check for failed voucher activations that can be retried
        return cls.objects.filter(
            checkout_request_id=checkout_id,
            status='failed',
            failure_category='system_error',
            error_code='VOUCHER_PROCESSING_ERROR'
        ).first()

    @classmethod
    def get_retry_candidates(cls):
        """Get items that are eligible for retry - for external retry service"""
        return cls.objects.filter(
            status='failed',
            retry_count__lt=models.F('max_retries'),
            expires_at__gt=timezone.now()  # Not expired
        )

    @classmethod
    def cleanup_expired_items(cls):
        """
        Enhanced cleanup that marks long-pending items as failed
        """
        now = timezone.now()
        
        # Mark pending items that have timed out
        timeout_threshold = now - timedelta(hours=24)
        pending_timeout_items = cls.objects.filter(
            status__in=['pending', 'Pending...'],
            created_at__lt=timeout_threshold
        )
        
        timeout_count = 0
        for item in pending_timeout_items:
            item.mark_pending_timeout_failure()
            timeout_count += 1
        
        # Remove expired pending items that haven't reached timeout yet
        expired_pending_items = cls.objects.filter(
            status__in=['pending', 'Pending...'],
            expires_at__lt=now,
            created_at__gte=timeout_threshold
        )
        
        expired_count = expired_pending_items.delete()[0]
        
        return {
            'timeout_failures_marked': timeout_count,
            'expired_items_deleted': expired_count
        }

    @classmethod
    def get_failed_transactions_report(cls, days=30):
        """Generate report of failed transactions for analysis"""
        from_date = timezone.now() - timedelta(days=days)
        
        failed_items = cls.objects.filter(
            status='failed',
            created_at__gte=from_date
        )
        
        return {
            'total_failures': failed_items.count(),
            'by_category': list(failed_items.values('failure_category').annotate(
                count=Count('id')
            ).order_by('-count')),
            'by_queue_type': list(failed_items.values('queue_type').annotate(
                count=Count('id')
            ).order_by('-count')),
            'retry_analysis': list(failed_items.values('retry_count').annotate(
                count=Count('id')
            ).order_by('retry_count')),
        }

    class Meta:
        verbose_name = "Transaction Queue"
        verbose_name_plural = "Transaction Queue"
        indexes = [
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['initiator']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['failure_category']),
            models.Index(fields=['retry_count']),
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['last_retry_at']),  # For retry service
        ]
        ordering = ['-created_at']


class Investment(TimeStampedModel):
    """Business investment tracking with multi-currency support"""
    INVESTMENT_TYPES = [
        ('seed', 'Seed Funding'),
        ('angel', 'Angel Investment'),
        ('vc', 'Venture Capital'),
        ('loan', 'Business Loan'),
        ('personal', 'Personal Investment'),
        ('equity', 'Equity Investment'),
    ]
    
    INVESTMENT_STATUS = [
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('active', 'Active'),
        ('repaid', 'Repaid'),
        ('converted', 'Converted'),
        ('written_off', 'Written Off'),
    ]
    
    investor_name = models.CharField(max_length=255)
    investment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default=1)
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES, default='personal')
    investment_status = models.CharField(max_length=20, choices=INVESTMENT_STATUS, default='proposed')
    
    # Enhanced Fields
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # For loans
    repayment_terms = models.TextField(blank=True)
    expected_roi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    
    # Recurring Investment Support
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ], blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    
    # Compliance & Tracking
    contract_reference = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.investor_name} - {self.amount} {self.currency.code} - {self.get_investment_status_display()}"

    @property
    def amount_base(self):
        """Get amount in base currency"""
        if self.currency.code == 'KES':
            return self.amount
        return ExchangeRate.convert_amount(self.amount, self.currency.code, 'KES')

    @property
    def is_active(self):
        """Check if investment is currently active"""
        return self.investment_status in ['disbursed', 'active']

    @property
    def days_to_maturity(self):
        """Days remaining until maturity"""
        if self.maturity_date:
            return (self.maturity_date - timezone.now().date()).days
        return None

    def mark_disbursed(self, disbursed_by):
        """Mark investment as disbursed"""
        self.investment_status = 'disbursed'
        self.approved_by = disbursed_by
        self.approved_at = timezone.now()
        self.save()

    class Meta:
        ordering = ['-investment_date']
        indexes = [
            models.Index(fields=['investment_status', 'investment_date']),
            models.Index(fields=['investor_name']),
            models.Index(fields=['maturity_date']),
        ]

class Department(TimeStampedModel):
    """Cost centers for expense allocation"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def current_month_spending(self):
        """Calculate current month spending"""
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return Expense.objects.filter(
            department=self,
            expense_date__gte=current_month
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def budget_utilization(self):
        """Calculate budget utilization percentage"""
        if self.budget == 0:
            return 0
        return (self.current_month_spending / self.budget) * 100


class BudgetCategory(TimeStampedModel):
    """Budget categories for expense planning"""
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    planned_amount = models.DecimalField(max_digits=12, decimal_places=2)
    fiscal_year = models.IntegerField(default=timezone.now().year)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.department.code} - {self.name} ({self.fiscal_year})"

    @property
    def actual_spending(self):
        """Calculate actual spending against budget"""
        return Expense.objects.filter(
            budget_category=self,
            expense_date__year=self.fiscal_year
        ).aggregate(total=Sum('amount_base'))['total'] or 0

    @property
    def variance(self):
        """Calculate budget variance"""
        return self.planned_amount - self.actual_spending

    @property
    def variance_percentage(self):
        """Calculate budget variance percentage"""
        if self.planned_amount == 0:
            return 0
        return (self.variance / self.planned_amount) * 100


class Expense(TimeStampedModel):
    """Business expense tracking with enhanced features"""
    EXPENSE_CATEGORIES = [
        ('network', 'Network Infrastructure'),
        ('maintenance', 'Maintenance & Repairs'),
        ('salaries', 'Salaries & Wages'),
        ('marketing', 'Marketing & Advertising'),
        ('office', 'Office Expenses'),
        ('utility', 'Utilities'),
        ('software', 'Software & Licensing'),
        ('travel', 'Travel & Accommodation'),
        ('training', 'Training & Development'),
        ('other', 'Other'),
    ]
    
    APPROVAL_STATUS = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    expense_date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default=1)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, default='other')
    vendor = models.CharField(max_length=255, blank=True, null=True)
    
    # Enhanced Fields
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    budget_category = models.ForeignKey(BudgetCategory, on_delete=models.PROTECT, null=True, blank=True)
    
    # Approval Workflow
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='draft')
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='submitted_expenses', null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Recurring Expense Support
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ], blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    
    # Tax and Compliance
    is_tax_deductible = models.BooleanField(default=True)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.0)  # Kenya VAT
    invoice_number = models.CharField(max_length=100, blank=True)
    
    # ISP-Specific Fields
    is_capex = models.BooleanField(default=False)  # Capital vs Operational expense
    asset_life_years = models.IntegerField(default=5)  # Depreciation period
    depreciation_method = models.CharField(max_length=20, choices=[
        ('straight_line', 'Straight Line'),
        ('reducing_balance', 'Reducing Balance'),
    ], default='straight_line')

    def __str__(self):
        return f"{self.expense_date} | {self.description} | {self.amount} {self.currency.code}"

    @property
    def amount_base(self):
        """Get amount in base currency"""
        if self.currency.code == 'KES':
            return self.amount
        return ExchangeRate.convert_amount(self.amount, self.currency.code, 'KES')

    @property
    def requires_approval(self):
        """Large expenses require approval"""
        return self.amount_base > 50000  # 50K KES threshold

    @property
    def total_amount(self):
        """Get total amount including tax - with None handling"""
        if self.amount is None:
            return None
        return self.amount + (self.tax_amount or 0)

    @property
    def monthly_depreciation(self):
        """Calculate monthly depreciation for capital expenses"""
        if self.is_capex and self.asset_life_years > 0:
            return self.amount_base / (self.asset_life_years * 12)
        return 0

    def submit_for_approval(self, user):
        """Submit expense for approval"""
        if self.approval_status == 'draft':
            self.approval_status = 'submitted'
            self.submitted_by = user
            self.submitted_at = timezone.now()
            self.save()

    def approve(self, user):
        """Approve expense"""
        if self.approval_status == 'submitted':
            self.approval_status = 'approved'
            self.approved_by = user
            self.approved_at = timezone.now()
            self.save()

    def mark_paid(self):
        """Mark expense as paid"""
        self.approval_status = 'paid'
        self.save()

    def save(self, *args, **kwargs):
        """Auto-calculate tax amount with None handling"""
        if self.amount is not None and self.vat_rate is not None:
            self.tax_amount = (self.amount * self.vat_rate) / 100
        else:
            self.tax_amount = 0
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['expense_date', 'category']),
            models.Index(fields=['approval_status', 'expense_date']),
            models.Index(fields=['department', 'expense_date']),
            models.Index(fields=['is_capex']),
        ]

class FinancialReport(TimeStampedModel):
    """
    Pre-generated financial reports for analytics with performance optimizations
    """
    REPORT_TYPES = [
        ('daily_sales', 'Daily Sales Report'),
        ('weekly_revenue', 'Weekly Revenue Report'),
        ('monthly_income', 'Monthly Income Statement'),
        ('quarterly_profit', 'Quarterly Profit & Loss'),
        ('annual_financial', 'Annual Financial Report'),
        ('budget_variance', 'Budget vs Actual Report'),
        ('cash_flow', 'Cash Flow Statement'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Report Data (all amounts in base currency KES)
    summary = models.JSONField(default=dict)
    breakdown = models.JSONField(default=dict)
    charts_data = models.JSONField(default=dict)  # Pre-calculated chart data
    
    # Performance & Caching
    cache_key = models.CharField(max_length=255, blank=True)
    generation_duration = models.DurationField(null=True, blank=True)
    record_count = models.IntegerField(default=0)
    data_size_kb = models.IntegerField(default=0)  # Report data size
    
    # Metadata
    is_locked = models.BooleanField(default=False)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.period_start} to {self.period_end}"

    @property
    def is_fresh(self):
        """Check if report is fresh (generated within last hour)"""
        return self.generated_at >= timezone.now() - timedelta(hours=1)

    @classmethod
    def get_latest_report(cls, report_type, period_start=None):
        """Get the latest report of specified type"""
        queryset = cls.objects.filter(report_type=report_type, is_archived=False)
        
        if period_start:
            queryset = queryset.filter(period_start=period_start)
            
        return queryset.order_by('-generated_at').first()

    @classmethod
    def generate_daily_sales_report(cls, date, generated_by=None):
        """Optimized report generation with caching"""
        cache_key = f"daily_sales_{date}"
        
        # Check for fresh existing report
        existing = cls.objects.filter(
            report_type='daily_sales',
            period_start=date,
            period_end=date,
            generated_at__gte=timezone.now() - timedelta(hours=1),
            is_archived=False
        ).first()
        
        if existing:
            return existing
            
        # Generate new report
        start_time = timezone.now()
        
        # Calculate report data
        daily_transactions = PaymentTransaction.objects.filter(
            created_at__date=date,
            status='completed'
        )
        
        summary = {
            'total_revenue': daily_transactions.aggregate(total=Sum('amount_base'))['total'] or 0,
            'transaction_count': daily_transactions.count(),
            'average_transaction_value': daily_transactions.aggregate(avg=Avg('amount_base'))['avg'] or 0,
            'top_packages': list(daily_transactions.values('package').annotate(
                count=Count('id'),
                revenue=Sum('amount_base')
            ).order_by('-revenue')[:5])
        }
        
        breakdown = {
            'by_hour': list(daily_transactions.annotate(
                hour=ExtractHour('created_at')
            ).values('hour').annotate(
                count=Count('id'),
                revenue=Sum('amount_base')
            ).order_by('hour')),
            'by_payment_method': list(daily_transactions.values('payment_method').annotate(
                count=Count('id'),
                revenue=Sum('amount_base')
            ).order_by('-revenue'))
        }
        
        # Calculate generation metrics
        generation_duration = timezone.now() - start_time
        record_count = daily_transactions.count()
        
        report = cls.objects.create(
            report_type='daily_sales',
            period_start=date,
            period_end=date,
            summary=summary,
            breakdown=breakdown,
            cache_key=cache_key,
            generation_duration=generation_duration,
            record_count=record_count,
            data_size_kb=len(str(summary)) + len(str(breakdown)) // 1024,
            generated_by=generated_by
        )
        
        return report

    def archive(self):
        """Archive this report"""
        self.is_archived = True
        self.save()

    class Meta:
        verbose_name = "Financial Report"
        verbose_name_plural = "Financial Reports"
        unique_together = ['report_type', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['report_type', 'period_start']),
            models.Index(fields=['is_archived', 'generated_at']),
            models.Index(fields=['cache_key']),
        ]
        ordering = ['-period_start']


class RevenueStream(TimeStampedModel):
    """
    Track different revenue sources for analytics with advanced metrics
    """
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[
        ('voucher_sales', 'Voucher Sales'),
        ('package_sales', 'Package Sales'),
        ('usage_charges', 'Usage Charges'),
        ('premium_services', 'Premium Services'),
        ('ads_revenue', 'Advertising Revenue'),
        ('value_added', 'Value Added Services'),
        ('other', 'Other Revenue'),
    ])
    is_active = models.BooleanField(default=True)
    
    # Financial Tracking
    target_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    target_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)  # Percentage
    
    # ISP-Specific Metrics
    target_customers = models.IntegerField(null=True, blank=True)
    average_revenue_per_user = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    kpis = models.JSONField(default=dict)  # Custom KPIs for this stream

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def current_month_revenue(self):
        """Calculate revenue for current month in base currency"""
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get revenue from TransactionQueue (completed transactions)
        transaction_revenue = TransactionQueue.objects.filter(
            method='mpesa',
            status__in=['completed', 'processed'],
            created_at__gte=current_month
        ).aggregate(total=Sum('price'))['total'] or 0
        
        # Get ads revenue if this is ads category
        ads_revenue = 0
        if self.category == 'ads_revenue':
            from ads.models import Advertisement
            ads_revenue = Advertisement.objects.filter(
                status='active',
                created_at__gte=current_month
            ).aggregate(total=Sum('total_spent'))['total'] or 0
        
        return transaction_revenue + ads_revenue

    @property
    def revenue_growth(self):
        """Calculate revenue growth compared to previous month"""
        current_month = timezone.now().replace(day=1)
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        
        current_revenue = self.get_revenue_for_period(current_month, timezone.now())
        previous_revenue = self.get_revenue_for_period(previous_month, current_month - timedelta(seconds=1))
        
        if previous_revenue == 0:
            return 0
        return ((current_revenue - previous_revenue) / previous_revenue) * 100

    @property
    def target_achievement(self):
        """Calculate target achievement percentage"""
        if not self.target_revenue:
            return 0
        return (self.current_month_revenue / self.target_revenue) * 100

    def calculate_clv(self):
        """Calculate Customer Lifetime Value for this revenue stream"""
        # ISP-specific CLV calculation using TransactionQueue
        avg_transaction_value = TransactionQueue.objects.filter(
            method='mpesa',
            status__in=['completed', 'processed']
        ).aggregate(avg=Avg('price'))['avg'] or 0
        
        from users.models import ClientH
        total_customers = ClientH.objects.count()
        
        avg_purchase_frequency = TransactionQueue.objects.filter(
            method='mpesa',
            status__in=['completed', 'processed'],
            created_at__gte=timezone.now() - timedelta(days=365)
        ).count() / max(total_customers, 1)  # Avoid division by zero
        
        customer_lifespan = 24  # Average months a customer stays
        
        return avg_transaction_value * avg_purchase_frequency * customer_lifespan

    def get_revenue_trend(self, months=6):
        """Get revenue trend for last N months"""
        from django.db.models.functions import TruncMonth
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30*months)
        
        # Get transaction revenue
        monthly_revenue = TransactionQueue.objects.filter(
            method='mpesa',
            status__in=['completed', 'processed'],
            created_at__range=[start_date, end_date]
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_revenue=Sum('price')
        ).order_by('month')
        
        # Add ads revenue if applicable
        if self.category == 'ads_revenue':
            from ads.models import Advertisement
            ads_monthly = Advertisement.objects.filter(
                status='active',
                created_at__range=[start_date, end_date]
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                total_revenue=Sum('total_spent')
            ).order_by('month')
            
            # Merge the two querysets
            revenue_dict = {item['month']: item['total_revenue'] for item in monthly_revenue}
            for item in ads_monthly:
                revenue_dict[item['month']] = revenue_dict.get(item['month'], 0) + item['total_revenue']
            
            return [{'month': k, 'total_revenue': v} for k, v in sorted(revenue_dict.items())]
        
        return list(monthly_revenue)

    def get_revenue_for_period(self, start_date, end_date):
        """Get revenue for specific period"""
        # Get transaction revenue
        transaction_revenue = TransactionQueue.objects.filter(
            method='mpesa',
            status__in=['completed', 'processed'],
            created_at__range=[start_date, end_date]
        ).aggregate(total=Sum('price'))['total'] or 0
        
        # Get ads revenue if applicable
        ads_revenue = 0
        if self.category == 'ads_revenue':
            from ads.models import Advertisement
            ads_revenue = Advertisement.objects.filter(
                status='active',
                created_at__range=[start_date, end_date]
            ).aggregate(total=Sum('total_spent'))['total'] or 0
        
        return transaction_revenue + ads_revenue

    def update_kpis(self):
        """Update custom KPIs for this revenue stream"""
        self.kpis = {
            'customer_acquisition_cost': self.calculate_cac(),
            'lifetime_value': float(self.calculate_clv()),
            'monthly_recurring_revenue': float(self.current_month_revenue),
            'churn_rate': self.calculate_churn_rate(),
            'net_promoter_score': self.calculate_nps(),  # Would need survey data
            'updated_at': timezone.now().isoformat()
        }
        self.save()

    def calculate_cac(self):
        """Calculate Customer Acquisition Cost"""
        # This would need marketing expense data
        # Simplified calculation for now
        marketing_expenses = Expense.objects.filter(
            category='marketing',
            expense_date__month=timezone.now().month,
            approval_status='paid'
        ).aggregate(total=Sum('amount_base'))['total'] or 0
        
        from users.models import ClientH
        new_customers = ClientH.objects.filter(
            created_at__month=timezone.now().month
        ).count()
        
        if new_customers == 0:
            return 0
        return float(marketing_expenses / new_customers)

    def calculate_churn_rate(self):
        """Calculate customer churn rate"""
        # Simplified churn calculation
        current_month = timezone.now().replace(day=1)
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        
        from users.models import ClientH
        current_customers = ClientH.objects.filter(created_at__lt=current_month).count()
        lost_customers = ClientH.objects.filter(
            created_at__lt=previous_month,
            status='inactive'
        ).count()
        
        if current_customers == 0:
            return 0
        return (lost_customers / current_customers) * 100

    class Meta:
        verbose_name = "Revenue Stream"
        verbose_name_plural = "Revenue Streams"
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['target_revenue']),
        ]

     