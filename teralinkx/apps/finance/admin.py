from django.contrib import admin
from django.utils import timezone
from .models import PaymentGateway, BalanceTransaction, Investment, InvestmentRepayment, Expense

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'gateway_type', 'is_default', 'test_mode', 'maintenance_mode', 'status')
    list_filter = ('gateway_type', 'is_default', 'test_mode', 'maintenance_mode', 'status')
    search_fields = ('name', 'webhook_url')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'gateway_type', 'is_default', 'status')
        }),
        ('Configuration', {
            'fields': ('config', 'webhook_url', 'callback_url')
        }),
        ('Fees', {
            'fields': ('transaction_fee_percentage', 'transaction_fee_fixed')
        }),
        ('Status', {
            'fields': ('test_mode', 'maintenance_mode')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BalanceTransaction)
class BalanceTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'direction', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'direction', 'created_at', 'location')
    search_fields = ('user__account', 'reference', 'external_reference', 'description')
    readonly_fields = ('created_at', 'updated_at', 'balance_before', 'balance_after')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'transaction_type', 'direction', 'amount', 'fee_amount')
        }),
        ('Balance Information', {
            'fields': ('balance_before', 'balance_after')
        }),
        ('References', {
            'fields': ('description', 'reference', 'external_reference')
        }),
        ('Context', {
            'fields': ('location', 'voucher', 'payment_gateway')
        }),
        ('Reversal Information', {
            'fields': ('is_reversible', 'reversed_at', 'reversal_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def net_amount(self, obj):
        return obj.net_amount
    net_amount.short_description = 'Net Amount'

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('investor_name', 'investment_type', 'amount_local', 'investment_date', 'status', 'is_active')
    list_filter = ('investment_type', 'status', 'is_active', 'investment_date', 'investor_type')
    search_fields = ('investor_name', 'contract_reference', 'invoice_number', 'investor_email')
    readonly_fields = ('created_at', 'updated_at', 'outstanding_balance')
    date_hierarchy = 'investment_date'
    
    fieldsets = (
        ('Investment Details', {
            'fields': ('investor_name', 'investor_type', 'investment_type', 'status', 'is_active')
        }),
        ('Financial Details', {
            'fields': ('amount', 'currency', 'exchange_rate', 'amount_local')
        }),
        ('Terms & Conditions', {
            'fields': ('interest_rate', 'equity_percentage', 'valuation', 'term_months')
        }),
        ('Dates', {
            'fields': ('investment_date', 'due_date', 'next_payment_date')
        }),
        ('Risk & Tracking', {
            'fields': ('risk_rating', 'outstanding_balance', 'total_repaid')
        }),
        ('Documentation', {
            'fields': ('contract_reference', 'invoice_number', 'description', 'terms_and_conditions')
        }),
        ('Contact Information', {
            'fields': ('investor_email', 'investor_phone', 'investor_address'),
            'classes': ('collapse',)
        }),
        ('Repayment Information', {
            'fields': ('repayment_schedule',),
            'classes': ('collapse',)
        }),
        ('Approval Information', {
            'fields': ('created_by', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def outstanding_balance(self, obj):
        return obj.outstanding_balance
    outstanding_balance.short_description = 'Outstanding Balance'
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True

@admin.register(InvestmentRepayment)
class InvestmentRepaymentAdmin(admin.ModelAdmin):
    list_display = ('investment', 'amount', 'payment_date', 'payment_method', 'reference')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('investment__investor_name', 'reference', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Repayment Details', {
            'fields': ('investment', 'amount', 'payment_date', 'payment_method')
        }),
        ('References', {
            'fields': ('reference', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_date', 'category', 'description', 'amount', 'vendor', 'location', 'is_approved')
    list_filter = ('category', 'expense_date', 'location', 'is_approved', 'payment_method')
    search_fields = ('description', 'vendor', 'invoice_number', 'receipt_number')
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'age_in_days')
    date_hierarchy = 'expense_date'
    
    fieldsets = (
        ('Expense Details', {
            'fields': ('expense_date', 'category', 'description', 'amount', 'currency')
        }),
        ('Vendor Information', {
            'fields': ('vendor', 'vendor_contact', 'vendor_tin')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference', 'invoice_number', 'receipt_number')
        }),
        ('Location & Department', {
            'fields': ('location', 'department', 'budget_category')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approved_at', 'is_approved')
        }),
        ('Recurring Expenses', {
            'fields': ('is_recurring', 'recurrence_pattern', 'next_recurrence'),
            'classes': ('collapse',)
        }),
        ('Tax Information', {
            'fields': ('is_tax_deductible', 'vat_amount', 'withholding_tax')
        }),
        ('Reimbursement', {
            'fields': ('is_reimbursable', 'reimbursement_status'),
            'classes': ('collapse',)
        }),
        ('Attachment', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount(self, obj):
        return obj.total_amount
    total_amount.short_description = 'Total Amount'
    
    def age_in_days(self, obj):
        return obj.age_in_days
    age_in_days.short_description = 'Age (days)'
    
    actions = ['approve_expenses']
    
    def approve_expenses(self, request, queryset):
        updated = queryset.update(is_approved=True, approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f'{updated} expenses approved successfully.')
    approve_expenses.short_description = "Approve selected expenses"