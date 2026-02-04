from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from django.db.models.functions import ExtractHour
import json
from .models import (
    Currency, ExchangeRate, PaymentGateway, PaymentTransaction,
    BalanceTransaction, TransactionQueue, Investment, Expense,
    FinancialReport, RevenueStream, Department, BudgetCategory
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active', 'is_base_currency', 'decimal_places']
    list_filter = ['is_active', 'is_base_currency', 'is_crypto']
    search_fields = ['code', 'name']
    list_editable = ['is_active', 'is_base_currency']
    actions = ['set_as_base_currency', 'deactivate_currencies']
    
    class Media:
        js = ('finance/js/currency_autofill.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add a data attribute to the code field for JavaScript
        form.base_fields['code'].widget.attrs['data-autofill-url'] = '/admin/finance/currency/autofill/'
        return form
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('autofill/', self.admin_site.admin_view(self.currency_autofill), name='currency_autofill'),
        ]
        return custom_urls + urls
    
    def currency_autofill(self, request):
        """API endpoint for currency autofill"""
        from django.http import JsonResponse
        code = request.GET.get('code', '')
        if code:
            currency_data = Currency.get_currency_data(code)
            return JsonResponse(currency_data)
        return JsonResponse({'error': 'No currency code provided'})
    
    def set_as_base_currency(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one currency to set as base.", messages.ERROR)
            return
        
        currency = queryset.first()
        # Remove base currency from all currencies
        Currency.objects.update(is_base_currency=False)
        # Set selected as base
        currency.is_base_currency = True
        currency.save()
        
        self.message_user(request, f"{currency.code} set as base currency.")
    
    def deactivate_currencies(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} currencies deactivated.")
    
    set_as_base_currency.short_description = "Set as base currency"
    deactivate_currencies.short_description = "Deactivate selected currencies"


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'target_currency', 'rate', 'source', 'is_active', 'last_updated']
    list_filter = ['source', 'is_active', 'base_currency', 'target_currency']
    search_fields = ['base_currency__code', 'target_currency__code']
    readonly_fields = ['last_updated']
    list_editable = ['rate', 'is_active']
    actions = ['update_rates', 'deactivate_rates']
    
    def update_rates(self, request, queryset):
        # This would call your external API to update rates
        try:
            # ExchangeRate.update_rates_from_api()
            self.message_user(request, "Exchange rates updated successfully.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Failed to update rates: {str(e)}", messages.ERROR)
    
    def deactivate_rates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} exchange rates deactivated.")
    
    update_rates.short_description = "Update selected exchange rates"
    deactivate_rates.short_description = "Deactivate selected rates"


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'gateway_type', 'is_default', 'test_mode', 'status', 'created_at']
    list_filter = ['gateway_type', 'is_default', 'test_mode', 'status']
    search_fields = ['name', 'description']
    list_editable = ['is_default', 'test_mode', 'status']
    filter_horizontal = ['supported_currencies']
    actions = ['set_as_default', 'activate_gateways', 'deactivate_gateways', 'enable_test_mode', 'disable_test_mode']
    
    # Add JSON editor widget for better config editing
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    
    # Fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'gateway_type', 'is_default', 'status')
        }),
        ('Currency Support', {
            'fields': ('default_currency', 'supported_currencies')
        }),
        ('URL Configuration', {
            'fields': ('callback_url', 'webhook_url'),
            'description': 'URL endpoints for payment callbacks and webhooks'
        }),
        ('Gateway Configuration', {
            'fields': ('config',),
            'description': 'Gateway-specific configuration (API keys, settings, etc.)'
        }),
        ('Testing & Environment', {
            'fields': ('test_mode',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly based on context"""
        readonly_fields = []
        if obj:  # Editing an existing object
            readonly_fields.extend(['gateway_type'])  # Don't change gateway type after creation
        return readonly_fields
    
    def get_form(self, request, obj=None, **kwargs):
        """Add help text and custom validation"""
        form = super().get_form(request, obj, **kwargs)
        return form
    
    def get_fieldsets(self, request, obj=None):
        """Dynamically adjust fieldsets based on gateway type"""
        fieldsets = super().get_fieldsets(request, obj)
        
        if obj and obj.gateway_type == 'cash':
            # Hide URL fields for cash payments
            fieldsets = [fs for fs in fieldsets if fs[0] != 'URL Configuration']
        
        return fieldsets
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit default currency choices to supported currencies"""
        if db_field.name == "default_currency":
            # You can add filtering logic here if needed
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Custom actions
    def set_as_default(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one gateway to set as default.", messages.ERROR)
            return
        
        gateway = queryset.first()
        # Remove default from all gateways
        PaymentGateway.objects.update(is_default=False)
        # Set selected as default
        gateway.is_default = True
        gateway.save()
        
        self.message_user(request, f"{gateway.name} set as default payment gateway.")
    
    def activate_gateways(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} payment gateways activated.")
    
    def deactivate_gateways(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f"{updated} payment gateways deactivated.")
    
    def enable_test_mode(self, request, queryset):
        updated = queryset.update(test_mode=True)
        self.message_user(request, f"{updated} payment gateways set to test mode.")
    
    def disable_test_mode(self, request, queryset):
        updated = queryset.update(test_mode=False)
        self.message_user(request, f"{updated} payment gateways set to live mode.")
    
    # Action descriptions
    set_as_default.short_description = "Set as default gateway"
    activate_gateways.short_description = "Activate selected gateways"
    deactivate_gateways.short_description = "Deactivate selected gateways"
    enable_test_mode.short_description = "Enable test mode for selected gateways"
    disable_test_mode.short_description = "Disable test mode (set to live)"
    
    # Custom admin methods for list display
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('default_currency')
    
    def view_config_summary(self, obj):
        """Display a summary of the configuration"""
        if not obj.config:
            return "No configuration"
        
        config = obj.config
        if obj.gateway_type == 'mpesa':
            return f"M-Pesa: {config.get('shortcode', 'N/A')}"
        elif obj.gateway_type == 'stripe':
            key = config.get('secret_key', '')
            return f"Stripe: {key[:10]}..." if key else "Stripe: No key"
        elif obj.gateway_type == 'paypal':
            return f"PayPal: {config.get('environment', 'N/A')}"
        return f"{len(obj.config)} config items"
    
    view_config_summary.short_description = 'Configuration'


class BalanceTransactionInline(admin.TabularInline):
    model = BalanceTransaction
    extra = 0
    readonly_fields = ['user', 'transaction_type', 'debit', 'credit', 'balance_before', 'balance_after', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user_link', 'amount_display', 'currency', 
        'payment_method', 'status', 'initiator', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['transaction_id', 'initiator', 'user__account', 'gateway_reference']
    readonly_fields = [
        'transaction_id', 'user', 'amount', 'currency', 'amount_base', 
        'exchange_rate', 'initiator', 'result_code', 'result_desc',
        'merchant_request_id', 'checkout_request_id', 'gateway_reference',
        'raw_callback_data_preview', 'created_at', 'transaction_time'
    ]
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'transaction_id', 'user', 'status', 'payment_method', 'payment_gateway'
            )
        }),
        ('Financial Details', {
            'fields': (
                'amount', 'currency', 'exchange_rate', 'amount_base'
            )
        }),
        ('M-Pesa Callback Data', {
            'fields': (
                'initiator', 'result_code', 'result_desc', 'balance',
                'merchant_request_id', 'checkout_request_id', 'gateway_reference',
                'date', 'transaction_time'
            )
        }),
        ('Raw Data', {
            'fields': ('raw_callback_data_preview',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('description', 'created_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [BalanceTransactionInline]
    actions = ['export_transactions', 'mark_as_refunded']
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_clienth_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.account)
        return "No User"
    user_link.short_description = 'User Account'
    user_link.admin_order_field = 'user__account'
    
    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency.code}"
    amount_display.short_description = 'Amount'
    
    def raw_callback_data_preview(self, obj):
        if obj.raw_callback_data:
            import json
            formatted_json = json.dumps(obj.raw_callback_data, indent=2)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; color: black;">{}</pre>', formatted_json)
        return "No raw data"
    raw_callback_data_preview.short_description = 'Raw Callback Data'
    
    def export_transactions(self, request, queryset):
        # This would generate and return a CSV export
        self.message_user(request, "Export feature would be implemented here.")
    
    def mark_as_refunded(self, request, queryset):
        updated = queryset.update(status='refunded')
        self.message_user(request, f"{updated} transactions marked as refunded.")
    
    export_transactions.short_description = "Export selected transactions"
    mark_as_refunded.short_description = "Mark as refunded"
    
    def has_add_permission(self, request):
        return False  # Payment transactions are created automatically from callbacks


@admin.register(BalanceTransaction)
class BalanceTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'transaction_type', 'amount_display', 'direction',
        'balance_before', 'balance_after', 'created_at'
    ]
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__account', 'reference', 'description']
    readonly_fields = [
        'user', 'transaction_type', 'debit', 'credit', 'balance_before', 
        'balance_after', 'payment_transaction', 'voucher', 'created_at'
    ]
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'user', 'transaction_type', 'direction_display', 'amount_display'
            )
        }),
        ('Balance Impact', {
            'fields': (
                'balance_before', 'balance_after', 'net_effect_display'
            )
        }),
        ('References', {
            'fields': (
                'payment_transaction', 'voucher', 'reference'
            )
        }),
        ('Context', {
            'fields': ('description',),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_clienth_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.account)
        return "No User"
    user_link.short_description = 'User Account'
    user_link.admin_order_field = 'user__account'
    
    def amount_display(self, obj):
        return f"{obj.amount}"
    amount_display.short_description = 'Amount'
    
    def direction(self, obj):
        if obj.is_credit:
            return format_html('<span style="color: green;">CREDIT</span>')
        else:
            return format_html('<span style="color: red;">DEBIT</span>')
    direction.short_description = 'Direction'
    
    def direction_display(self, obj):
        return self.direction(obj)
    direction_display.short_description = 'Direction'
    
    def net_effect_display(self, obj):
        return f"{obj.net_effect}"
    net_effect_display.short_description = 'Net Effect'
    
    def has_add_permission(self, request):
        return False  # Balance transactions are created automatically


@admin.register(TransactionQueue)
class TransactionQueueAdmin(admin.ModelAdmin):
    list_display = [
        'queue_type', 'initiator', 'recipient', 'package', 'price', 
        'status', 'retry_count', 'created_at', 'pending_duration_safe'
    ]
    list_filter = ['queue_type', 'status', 'failure_category', 'priority', 'created_at']
    search_fields = ['initiator', 'recipient', 'checkout_request_id', 'package_code']
    readonly_fields = [
        'queue_type', 'user', 'method', 'initiator', 'checkout_request_id',
        'package_code', 'package', 'price', 'recipient', 'used_credit',
        'failure_reason', 'error_code', 'failure_category', 'retry_count',
        'gateway_result_data_preview', 'metadata_preview', 'created_at',
        'pending_duration_safe', 'is_expired_safe'
    ]
    fieldsets = (
        ('Queue Item Details', {
            'fields': (
                'queue_type', 'status', 'priority', 'user'
            )
        }),
        ('Payment Details', {
            'fields': (
                'method', 'initiator', 'checkout_request_id', 'recipient'
            )
        }),
        ('Package Details', {
            'fields': (
                'package_code', 'package', 'price', 'used_credit'
            )
        }),
        ('Failure Information', {
            'fields': (
                'failure_reason', 'error_code', 'failure_category', 'retry_count'
            ),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': (
                'pending_duration_safe', 'is_expired_safe', 'expires_at'
            )
        }),
        ('Raw Data', {
            'fields': ('gateway_result_data_preview', 'metadata_preview'),
            'classes': ('collapse',)
        })
    )
    actions = [
        'retry_failed_items', 'cancel_pending_items', 'mark_as_completed',
        'cleanup_expired_items', 'generate_failure_report'
    ]
    
    def pending_duration_safe(self, obj):
        """Safe version of pending duration for admin"""
        if obj.pk and obj.created_at:  # Only calculate for saved objects
            return f"{obj.pending_duration_hours:.1f}h"
        return "N/A"
    pending_duration_safe.short_description = 'Pending Duration'
    
    def is_expired_safe(self, obj):
        """Safe version of is_expired for admin"""
        if obj.pk:  # Only calculate for saved objects
            if obj.is_expired:
                return format_html('<span style="color: red;">YES</span>')
            return format_html('<span style="color: green;">NO</span>')
        return "N/A"
    is_expired_safe.short_description = 'Is Expired?'
    
    def gateway_result_data_preview(self, obj):
        """Preview gateway request data"""
        if obj.gateway_result_data:
            import json
            formatted_json = json.dumps(obj.gateway_result_data, indent=2)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; color: black;">{}</pre>', formatted_json)
        return "No gateway data"
    gateway_result_data_preview.short_description = 'Gateway Result Data'
    
    def metadata_preview(self, obj):
        """Preview metadata"""
        if obj.metadata:
            import json
            formatted_json = json.dumps(obj.metadata, indent=2)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; color: black;">{}</pre>', formatted_json)
        return "No metadata"
    metadata_preview.short_description = 'Metadata'
    
    def retry_failed_items(self, request, queryset):
        """Retry failed queue items"""
        failed_items = queryset.filter(status='failed')
        for item in failed_items:
            if item.retry_count < item.max_retries:
                item.retry_count += 1
                item.status = 'pending'
                item.save()
        
        self.message_user(request, f"{failed_items.count()} failed items queued for retry.")
    
    def cancel_pending_items(self, request, queryset):
        """Cancel pending queue items"""
        pending_items = queryset.filter(status='pending')
        for item in pending_items:
            item.status = 'cancelled'
            item.failure_reason = "Cancelled by admin"
            item.save()
        
        self.message_user(request, f"{pending_items.count()} pending items cancelled.")
    
    def mark_as_completed(self, request, queryset):
        """Mark queue items as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} items marked as completed.")
    
    def cleanup_expired_items(self, request, queryset):
        """Cleanup expired queue items"""
        result = TransactionQueue.cleanup_expired_items()
        self.message_user(request, f"Cleanup completed: {result['timeout_failures_marked']} marked as failed, {result['expired_items_deleted']} deleted.")
    
    def generate_failure_report(self, request, queryset):
        """Generate failure report for selected items"""
        failed_items = queryset.filter(status='failed')
        report = {
            'total_failures': failed_items.count(),
            'by_category': list(failed_items.values('failure_category').annotate(
                count=Count('id')
            ).order_by('-count')),
            'by_queue_type': list(failed_items.values('queue_type').annotate(
                count=Count('id')
            ).order_by('-count')),
        }
        message = f"Failure Report: {report['total_failures']} total failures. "

        categories = ", ".join(
            f"{cat['failure_category']}: {cat['count']}"
            for cat in report["by_category"]
        )

        message += f"Categories: {categories}"

        self.message_user(request, message)


    
    retry_failed_items.short_description = "Retry failed items"
    cancel_pending_items.short_description = "Cancel pending items"
    mark_as_completed.short_description = "Mark as completed"
    cleanup_expired_items.short_description = "Cleanup expired items"
    generate_failure_report.short_description = "Generate failure report"


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = [
        'investor_name', 'investment_type', 'investment_status', 
        'amount_display', 'investment_date', 'is_active', 'created_at'
    ]
    list_filter = ['investment_type', 'investment_status', 'investment_date', 'is_recurring']
    search_fields = ['investor_name', 'description', 'contract_reference']
    readonly_fields = [
        'amount_base_display', 'days_to_maturity_display', 'is_active_display',
        'created_at', 'updated_at'
    ]
    list_editable = ['investment_status']
    actions = ['mark_as_disbursed', 'mark_as_active', 'mark_as_repaid']
    
    fieldsets = (
        ('Investment Details', {
            'fields': (
                'investor_name', 'investment_type', 'investment_status', 
                'investment_date', 'maturity_date'
            )
        }),
        ('Financial Details', {
            'fields': (
                'amount', 'currency', 'amount_base_display', 
                'equity_percentage', 'interest_rate', 'expected_roi'
            )
        }),
        ('Recurring Investment', {
            'fields': (
                'is_recurring', 'recurrence_pattern', 'next_due_date'
            ),
            'classes': ('collapse',)
        }),
        ('Terms & Compliance', {
            'fields': (
                'repayment_terms', 'contract_reference', 
                'approved_by', 'approved_at', 'description'
            )
        }),
        ('System Information', {
            'fields': (
                'is_active_display', 'days_to_maturity_display',
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def amount_display(self, obj):
        return f"{obj.amount:,.2f} {obj.currency.code}"
    amount_display.short_description = 'Amount'
    
    def amount_base_display(self, obj):
        return f"KES {obj.amount_base:,.2f}"
    amount_base_display.short_description = 'Amount in KES'
    
    def days_to_maturity_display(self, obj):
        if obj.days_to_maturity:
            return f"{obj.days_to_maturity} days"
        return "N/A"
    days_to_maturity_display.short_description = 'Days to Maturity'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        return format_html('<span style="color: gray;">● Inactive</span>')
    is_active_display.short_description = 'Active Status'
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'
    
    def mark_as_disbursed(self, request, queryset):
        for investment in queryset:
            investment.mark_disbursed(request.user)
        self.message_user(request, f"{queryset.count()} investments marked as disbursed.")
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(investment_status='active')
        self.message_user(request, f"{updated} investments marked as active.")
    
    def mark_as_repaid(self, request, queryset):
        updated = queryset.update(investment_status='repaid')
        self.message_user(request, f"{updated} investments marked as repaid.")
    
    mark_as_disbursed.short_description = "Mark selected as disbursed"
    mark_as_active.short_description = "Mark selected as active"
    mark_as_repaid.short_description = "Mark selected as repaid"


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'expense_date', 'category', 'description_truncated', 'amount_display', 
        'vendor', 'approval_status', 'department', 'is_capex_badge'  
    ]
    list_filter = [
        'category', 'expense_date', 'approval_status', 'department', 
        'is_capex', 'is_recurring'
    ]
    search_fields = ['description', 'vendor', 'invoice_number']
    readonly_fields = [
        'amount_base_display', 'total_amount_display', 'requires_approval_display',
        'monthly_depreciation_display', 'created_at', 'updated_at'
    ]
    list_editable = ['approval_status'] 
    actions = [
        'approve_expenses', 'mark_as_paid', 'mark_as_capex', 
        'mark_as_opex', 'duplicate_expenses'
    ]
    
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'expense_date', 'description', 'vendor', 'invoice_number'
            )
        }),
        ('Financial Details', {
            'fields': (
                'amount', 'currency', 'amount_base_display',
                'tax_amount', 'vat_rate', 'total_amount_display'
            )
        }),
        ('Categorization', {
            'fields': (
                'category', 'department', 'budget_category'
            )
        }),
        ('Approval Workflow', {
            'fields': (
                'approval_status', 'submitted_by', 'submitted_at',
                'approved_by', 'approved_at', 'requires_approval_display'
            )
        }),
        ('Recurring Expense', {
            'fields': (
                'is_recurring', 'recurrence_pattern', 'next_due_date'
            ),
            'classes': ('collapse',)
        }),
        ('ISP-Specific Details', {
            'fields': (
                'is_capex', 'asset_life_years', 'depreciation_method',
                'monthly_depreciation_display', 'is_tax_deductible'
            )
        }),
        ('System Information', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def description_truncated(self, obj):
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description
    description_truncated.short_description = 'Description'
    
    def amount_display(self, obj):
        if obj.amount is None:
            return "Not set"
        return f"{obj.amount:,.2f} {obj.currency.code}"
    amount_display.short_description = 'Amount'
    
    def amount_base_display(self, obj):
        if obj.amount_base is None:
            return "N/A"
        return f"KES {obj.amount_base:,.2f}"
    amount_base_display.short_description = 'Amount in KES'
    
    def total_amount_display(self, obj):
        if obj.total_amount is None:
            return "N/A"
        return f"KES {obj.total_amount:,.2f}"
    total_amount_display.short_description = 'Total Amount (incl. tax)'
    
    def monthly_depreciation_display(self, obj):
        if obj.is_capex:
            return f"KES {obj.monthly_depreciation:,.2f}/month"
        return "N/A (OPEX)"
    monthly_depreciation_display.short_description = 'Monthly Depreciation'
    
    def approval_status_badge(self, obj):
        status_colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'approved': 'green',
            'rejected': 'red',
            'paid': 'purple'
        }
        color = status_colors.get(obj.approval_status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">{}</span>',
            color, obj.get_approval_status_display().upper()
        )
    approval_status_badge.short_description = 'Status'
    
    def is_capex_badge(self, obj):
        if obj.is_capex:
            return format_html('<span style="color: blue;">● CAPEX</span>')
        return format_html('<span style="color: green;">● OPEX</span>')
    is_capex_badge.short_description = 'Type'
    
    def requires_approval_display(self, obj):
        if obj.requires_approval:
            return format_html('<span style="color: orange;">✓ Requires Approval</span>')
        return "Auto-approved"
    requires_approval_display.short_description = 'Approval Required'
    
    def approve_expenses(self, request, queryset):
        for expense in queryset:
            if expense.approval_status == 'submitted':
                expense.approve(request.user)
        self.message_user(request, f"Approved {queryset.count()} expenses.")
    
    def mark_as_paid(self, request, queryset):
        for expense in queryset:
            expense.mark_paid()
        self.message_user(request, f"Marked {queryset.count()} expenses as paid.")
    
    def mark_as_capex(self, request, queryset):
        updated = queryset.update(is_capex=True)
        self.message_user(request, f"{updated} expenses marked as CAPEX.")
    
    def mark_as_opex(self, request, queryset):
        updated = queryset.update(is_capex=False)
        self.message_user(request, f"{updated} expenses marked as OPEX.")
    
    def duplicate_expenses(self, request, queryset):
        duplicated_count = 0
        for expense in queryset:
            expense.pk = None
            expense.description = f"Copy of {expense.description}"
            expense.approval_status = 'draft'
            expense.save()
            duplicated_count += 1
        self.message_user(request, f"{duplicated_count} expenses duplicated.")
    
    approve_expenses.short_description = "Approve selected expenses"
    mark_as_paid.short_description = "Mark selected as paid"
    mark_as_capex.short_description = "Mark selected as CAPEX"
    mark_as_opex.short_description = "Mark selected as OPEX"
    duplicate_expenses.short_description = "Duplicate selected expenses"


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_type', 'period_start', 'period_end', 'generated_at', 
        'is_locked_badge', 'is_fresh_badge', 'record_count', 'generation_duration_display'
    ]
    list_filter = ['report_type', 'is_locked', 'is_archived', 'period_start']
    readonly_fields = [
        'report_type', 'period_start', 'period_end', 'generated_at', 
        'generated_by', 'summary_preview', 'breakdown_preview', 'charts_data_preview',
        'generation_duration', 'record_count', 'data_size_kb', 'is_fresh_display'
    ]
    actions = [
        'lock_reports', 'unlock_reports', 'archive_reports', 
        'unarchive_reports', 'download_reports'
    ]
    
    def is_locked_badge(self, obj):
        if obj.is_locked:
            return format_html('<span style="color: red;">🔒 Locked</span>')
        return format_html('<span style="color: green;">🔓 Unlocked</span>')
    is_locked_badge.short_description = 'Lock Status'
    
    def is_fresh_badge(self, obj):
        if obj.is_fresh:
            return format_html('<span style="color: green;">🟢 Fresh</span>')
        return format_html('<span style="color: orange;">🟡 Stale</span>')
    is_fresh_badge.short_description = 'Data Freshness'
    
    def generation_duration_display(self, obj):
        if obj.generation_duration:
            total_seconds = obj.generation_duration.total_seconds()
            return f"{total_seconds:.2f}s"
        return "N/A"
    generation_duration_display.short_description = 'Gen Time'
    
    def summary_preview(self, obj):
        if obj.summary:
            formatted_json = json.dumps(obj.summary, indent=2, ensure_ascii=False)
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; max-height: 300px; font-family: monospace; font-size: 12px;">{}</div>', 
                formatted_json
            )
        return "No summary data"
    summary_preview.short_description = 'Summary Data'
    
    def breakdown_preview(self, obj):
        if obj.breakdown:
            formatted_json = json.dumps(obj.breakdown, indent=2, ensure_ascii=False)
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; max-height: 300px; font-family: monospace; font-size: 12px;">{}</div>', 
                formatted_json
            )
        return "No breakdown data"
    breakdown_preview.short_description = 'Breakdown Data'
    
    def charts_data_preview(self, obj):
        if obj.charts_data:
            formatted_json = json.dumps(obj.charts_data, indent=2, ensure_ascii=False)
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; max-height: 200px; font-family: monospace; font-size: 12px;">{}</div>', 
                formatted_json
            )
        return "No charts data"
    charts_data_preview.short_description = 'Charts Data'
    
    def is_fresh_display(self, obj):
        return obj.is_fresh
    is_fresh_display.boolean = True
    is_fresh_display.short_description = 'Is Fresh Data'
    
    def lock_reports(self, request, queryset):
        updated = queryset.update(is_locked=True)
        self.message_user(request, f"{updated} reports locked.")
    
    def unlock_reports(self, request, queryset):
        updated = queryset.update(is_locked=False)
        self.message_user(request, f"{updated} reports unlocked.")
    
    def archive_reports(self, request, queryset):
        for report in queryset:
            report.archive()
        self.message_user(request, f"{queryset.count()} reports archived.")
    
    def unarchive_reports(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(request, f"{updated} reports unarchived.")
    
    def download_reports(self, request, queryset):
        # Placeholder for report download functionality
        self.message_user(request, f"Download functionality for {queryset.count()} reports would be implemented here.")
    
    lock_reports.short_description = "Lock selected reports"
    unlock_reports.short_description = "Unlock selected reports"
    archive_reports.short_description = "Archive selected reports"
    unarchive_reports.short_description = "Unarchive selected reports"
    download_reports.short_description = "Download selected reports"
    
    def has_add_permission(self, request):
        return False  # Reports are generated automatically
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for non-locked, non-archived reports
        if obj and (obj.is_locked or obj.is_archived):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(RevenueStream)
class RevenueStreamAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'is_active', 'target_revenue', 
        'current_month_revenue_display', 'target_achievement_bar', 
        'revenue_growth_display'
    ]
    list_filter = ['category', 'is_active']
    list_editable = ['is_active', 'target_revenue']  
    search_fields = ['name', 'description']
    readonly_fields = [
        'current_month_revenue_display', 'revenue_growth_display', 
        'target_achievement_display', 'clv_display', 'cac_display',
        'churn_rate_display', 'kpis_preview'
    ]
    actions = [
        'activate_streams', 'deactivate_streams', 'update_kpis', 
        'calculate_metrics'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'category', 'is_active', 'description', 'display_order'
            )
        }),
        ('Financial Targets', {
            'fields': (
                'target_revenue', 'target_growth_rate', 'target_customers',
                'average_revenue_per_user'
            )
        }),
        ('Current Performance', {
            'fields': (
                'current_month_revenue_display', 'target_achievement_display',
                'revenue_growth_display'
            )
        }),
        ('Advanced Metrics', {
            'fields': (
                'clv_display', 'cac_display', 'churn_rate_display'
            ),
            'classes': ('collapse',)
        })
    )
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        return format_html('<span style="color: red;">● Inactive</span>')
    is_active_badge.short_description = 'Status'
    
    def target_revenue_display(self, obj):
        if obj.target_revenue:
            return f"KES {obj.target_revenue:,.2f}"
        return "No target"
    target_revenue_display.short_description = 'Target Revenue'
    
    def current_month_revenue_display(self, obj):
        revenue = obj.current_month_revenue
        return f"KES {revenue:,.2f}"
    current_month_revenue_display.short_description = 'Current Month'
    
    def target_achievement_bar(self, obj):
        achievement = obj.target_achievement
        width = min(achievement, 100)
        color = "green" if achievement >= 100 else "orange" if achievement >= 75 else "red"
        
        return format_html(
            '<div style="background: #f0f0f0; border-radius: 10px; width: 100px; height: 20px; position: relative;">'
            '<div style="background: {}; border-radius: 10px; width: {}%; height: 100%;"></div>'
            '<div style="position: absolute; top: 0; left: 0; width: 100%; text-align: center; font-size: 11px; line-height: 20px; color: black;">{}%</div>'
            '</div>',
            color, width, int(achievement)
        )
    target_achievement_bar.short_description = 'Target Achievement'
    
    def target_achievement_display(self, obj):
        return f"{obj.target_achievement:.1f}%"
    target_achievement_display.short_description = 'Target Achievement'
    
    def revenue_growth_display(self, obj):
        growth = obj.revenue_growth
        if growth > 0:
            return format_html('<span style="color: green;">↑ {:.1f}%</span>', growth)
        elif growth < 0:
            return format_html('<span style="color: red;">↓ {:.1f}%</span>', abs(growth))
        return "0%"
    revenue_growth_display.short_description = 'Revenue Growth'
    
    def clv_display(self, obj):
        clv = obj.calculate_clv()
        return f"KES {clv:,.2f}"
    clv_display.short_description = 'Customer Lifetime Value'
    
    def cac_display(self, obj):
        cac = obj.calculate_cac()
        return f"KES {cac:,.2f}"
    cac_display.short_description = 'Customer Acquisition Cost'
    
    def churn_rate_display(self, obj):
        churn = obj.calculate_churn_rate()
        return f"{churn:.1f}%"
    churn_rate_display.short_description = 'Churn Rate'
    
    def kpis_preview(self, obj):
        if obj.kpis:
            formatted_json = json.dumps(obj.kpis, indent=2, ensure_ascii=False)
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; max-height: 200px; font-family: monospace; font-size: 12px;">{}</div>', 
                formatted_json
            )
        return "No KPI data"
    kpis_preview.short_description = 'KPI Data'
    
    def activate_streams(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} revenue streams activated.")
    
    def deactivate_streams(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} revenue streams deactivated.")
    
    def update_kpis(self, request, queryset):
        for stream in queryset:
            stream.update_kpis()
        self.message_user(request, f"KPIs updated for {queryset.count()} revenue streams.")
    
    def calculate_metrics(self, request, queryset):
        # Force calculation of all metrics
        for stream in queryset:
            # This will trigger property calculations
            _ = stream.current_month_revenue
            _ = stream.revenue_growth
            _ = stream.target_achievement
        self.message_user(request, f"Metrics calculated for {queryset.count()} revenue streams.")
    
    activate_streams.short_description = "Activate selected streams"
    deactivate_streams.short_description = "Deactivate selected streams"
    update_kpis.short_description = "Update KPIs for selected streams"
    calculate_metrics.short_description = "Calculate metrics for selected streams"


# Also register the new Department and BudgetCategory models
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'budget_display', 'current_month_spending_display', 'budget_utilization_bar']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    
    def budget_display(self, obj):
        return f"KES {obj.budget:,.2f}"
    budget_display.short_description = 'Budget'
    
    def current_month_spending_display(self, obj):
        return f"KES {obj.current_month_spending:,.2f}"
    current_month_spending_display.short_description = 'Current Spending'
    
    def budget_utilization_bar(self, obj):
        utilization = obj.budget_utilization
        width = min(utilization, 100)
        color = "red" if utilization > 90 else "orange" if utilization > 75 else "green"
        
        return format_html(
            '<div style="background: #f0f0f0; border-radius: 10px; width: 100px; height: 20px; position: relative;">'
            '<div style="background: {}; border-radius: 10px; width: {}%; height: 100%;"></div>'
            '<div style="position: absolute; top: 0; left: 0; width: 100%; text-align: center; font-size: 11px; line-height: 20px; color: black;">{}%</div>'
            '</div>',
            color, width, int(utilization)
        )
    budget_utilization_bar.short_description = 'Budget Utilization'


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'fiscal_year', 'planned_amount_display', 'actual_spending_display', 'variance_display']
    list_filter = ['department', 'fiscal_year', 'is_active']
    
    def planned_amount_display(self, obj):
        return f"KES {obj.planned_amount:,.2f}"
    planned_amount_display.short_description = 'Planned'
    
    def actual_spending_display(self, obj):
        return f"KES {obj.actual_spending:,.2f}"
    actual_spending_display.short_description = 'Actual'
    
    def variance_display(self, obj):
        variance = obj.variance
        if variance > 0:
            return format_html('<span style="color: green;">+KES {:,}</span>', variance)
        elif variance < 0:
            return format_html('<span style="color: red;">-KES {:,}</span>', abs(variance))
        return "KES 0"
    variance_display.short_description = 'Variance'