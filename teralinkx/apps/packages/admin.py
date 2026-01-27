# apps/packages/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PackageType, DispatchVoucher, AvailableVoucher, 
    Coupon, CouponUsage, FeaturedPromotion,
    PackageTypeLocation, FeaturedPromotionLocation  # Import the through models
)

# --------------------------------------------------------------------
# INLINE ADMIN FOR THROUGH MODELS
# --------------------------------------------------------------------

class PackageTypeLocationInline(admin.TabularInline):
    """Inline admin for PackageType locations through model"""
    model = PackageTypeLocation
    extra = 1
    autocomplete_fields = ['location']

class FeaturedPromotionLocationInline(admin.TabularInline):
    """Inline admin for FeaturedPromotion locations through model"""
    model = FeaturedPromotionLocation
    extra = 1
    autocomplete_fields = ['location']

# --------------------------------------------------------------------
# ADMIN CLASSES
# --------------------------------------------------------------------

@admin.register(PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'code', 
        'category', 
        'tier', 
        'price_display', 
        'duration_display',
        'speed_limit_mbps',
        'data_limit_display',
        'is_active',
        'is_featured',
        'sales_display'
    ]
    
    list_filter = [
        'category',
        'tier',
        'is_active',
        'is_featured',
        'allow_roaming',
        'qos_priority'
    ]
    
    search_fields = [
        'name',
        'code',
        'description',
        'radius_group'
    ]
    
    readonly_fields = [
        'sold_quantity',
        'availability_status',
        'created_display'
    ]
    
    # UPDATED: Removed 'locations' from fieldsets
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'code',
                'description',
                'category',
                'tier'
            )
        }),
        ('Pricing & Duration', {
            'fields': (
                'price',
                'original_price',
                'duration',
                'auto_renew'
            )
        }),
        ('Technical Specifications', {
            'fields': (
                'speed_limit_mbps',
                'data_limit_mb',
                'device_limit',
                'qos_priority'
            )
        }),
        ('Network Configuration', {
            'fields': (
                'radius_group',
                'allow_roaming'
            )
        }),
        ('Availability & Display', {
            'fields': (
                'is_active',        # REMOVED: 'locations',
                'is_public',
                'is_featured',
                'display_order',
                'color_code',
                'tags'
            )
        }),
        ('Inventory Management', {
            'fields': (
                'total_quantity',
                'sold_quantity',
                'availability_status'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_display',
            ),
            'classes': ('collapse',)
        })
    )
    
    # UPDATED: Removed 'locations' from filter_horizontal
    # filter_horizontal = []  # Don't include locations here
    
    # ADDED: Include the inline for locations
    inlines = [PackageTypeLocationInline]
    
    actions = [
        'activate_packages',
        'deactivate_packages',
        'feature_packages',
        'unfeature_packages'
    ]
    
    def price_display(self, obj):
        """Display price with discount if applicable"""
        if obj.original_price and obj.original_price > obj.price:
            return format_html(
                '<span style="color: green;">KES {} <small><s>KES {}</s></small></span>',
                obj.price,
                obj.original_price
            )
        return f"KES {obj.price}"
    price_display.short_description = 'Price'
    
    def duration_display(self, obj):
        """Display duration in human-readable format"""
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            if total_seconds < 3600:  # Less than 1 hour
                return f"{int(total_seconds / 60)} min"
            elif total_seconds < 86400:  # Less than 1 day
                return f"{int(total_seconds / 3600)} hours"
            else:
                return f"{int(total_seconds / 86400)} days"
        return "N/A"
    duration_display.short_description = 'Duration'
    
    def data_limit_display(self, obj):
        """Display data limit in human-readable format"""
        if obj.data_limit_mb:
            if obj.data_limit_mb >= 1024:
                return f"{obj.data_limit_mb / 1024:.1f} GB"
            else:
                return f"{obj.data_limit_mb} MB"
        return "Unlimited"
    data_limit_display.short_description = 'Data Limit'
    
    def sales_display(self, obj):
        """Display sold quantity with availability"""
        if obj.total_quantity:
            return f"{obj.sold_quantity}/{obj.total_quantity}"
        return f"{obj.sold_quantity} sold"
    sales_display.short_description = 'Sales'
    
    def created_display(self, obj):
        """Format created_at date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_display.short_description = 'Created'
    
    def availability_status(self, obj):
        """Display availability status with color coding"""
        if not obj.is_active:
            color = 'red'
            text = 'Inactive'
        elif obj.total_quantity and obj.sold_quantity >= obj.total_quantity:
            color = 'orange'
            text = 'Sold Out'
        else:
            color = 'green'
            text = 'Available'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    availability_status.short_description = 'Status'
    
    def activate_packages(self, request, queryset):
        """Admin action to activate packages"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} packages activated successfully.')
    activate_packages.short_description = "Activate selected packages"
    
    def deactivate_packages(self, request, queryset):
        """Admin action to deactivate packages"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} packages deactivated successfully.')
    deactivate_packages.short_description = "Deactivate selected packages"
    
    def feature_packages(self, request, queryset):
        """Admin action to feature packages"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} packages featured successfully.')
    feature_packages.short_description = "Feature selected packages"
    
    def unfeature_packages(self, request, queryset):
        """Admin action to unfeature packages"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} packages unfeatured successfully.')
    unfeature_packages.short_description = "Unfeature selected packages"


@admin.register(DispatchVoucher)
class DispatchVoucherAdmin(admin.ModelAdmin):
    list_display = [
        'voucher_code',
        'user_display',
        'package',
        'status_display',
        'price_paid_display',
        'activated_display',
        'expires_display',
        'usage_display',
        'is_roaming'
    ]
    
    list_filter = [
        'status',
        'is_roaming',
        'package',
        'location',
        'activated_at'
    ]
    
    search_fields = [
        'voucher_code',
        'user__username',
        'user__client_profile__account',
        'transaction_id'
    ]
    
    readonly_fields = [
        'usage_percentage',
        'remaining_time',
        'created_display'
    ]
    
    fieldsets = (
        ('Voucher Information', {
            'fields': (
                'voucher_code',
                'package',
                'user',
                'location',
                'status'
            )
        }),
        ('Purchase Details', {
            'fields': (
                'price_paid',
                'activated_at',
                'expires_at',
                'transaction_id',
                'payment_reference'
            )
        }),
        ('Usage Tracking', {
            'fields': (
                'download_bytes',
                'upload_bytes',
                'session_count',
                'usage_percentage',
                'remaining_time'
            )
        }),
        ('Device Management', {
            'fields': (
                'allowed_mac_addresses',
                'concurrent_sessions'
            )
        }),
        ('Roaming Information', {
            'fields': (
                'is_roaming',
                'home_location'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_display',
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'suspend_vouchers',
        'reactivate_vouchers',
        'cancel_vouchers'
    ]
    
    def user_display(self, obj):
        """Display user information"""
        return f"{obj.user.username} ({obj.user.client_profile.account})"
    user_display.short_description = 'User'
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'active': 'green',
            'expired': 'gray',
            'exhausted': 'orange',
            'suspended': 'red',
            'cancelled': 'darkred'
        }
        color = colors.get(obj.status, 'black')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def price_paid_display(self, obj):
        """Display price paid"""
        return f"KES {obj.price_paid}"
    price_paid_display.short_description = 'Price Paid'
    
    def activated_display(self, obj):
        """Format activated_at date"""
        return obj.activated_at.strftime("%m/%d %H:%M")
    activated_display.short_description = 'Activated'
    
    def expires_display(self, obj):
        """Format expires_at date"""
        return obj.expires_at.strftime("%m/%d %H:%M")
    expires_display.short_description = 'Expires'
    
    def usage_display(self, obj):
        """Display usage information"""
        if obj.package.is_unlimited:
            return "Unlimited"
        
        total_used_mb = (obj.download_bytes + obj.upload_bytes) / (1024 * 1024)
        if obj.package.data_limit_mb:
            percentage = (total_used_mb / obj.package.data_limit_mb) * 100
            return f"{total_used_mb:.1f}MB ({percentage:.1f}%)"
        return f"{total_used_mb:.1f}MB"
    usage_display.short_description = 'Usage'
    
    def created_display(self, obj):
        """Format created_at date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_display.short_description = 'Created'
    
    def usage_percentage(self, obj):
        """Calculate usage percentage"""
        if obj.package.is_unlimited or not obj.package.data_limit_mb:
            return "Unlimited"
        
        total_used_mb = (obj.download_bytes + obj.upload_bytes) / (1024 * 1024)
        percentage = (total_used_mb / obj.package.data_limit_mb) * 100
        
        color = 'green' if percentage < 80 else 'orange' if percentage < 95 else 'red'
        
        return format_html(
            '<div style="width: 100%; background: #f0f0f0; border-radius: 5px;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; border-radius: 5px; padding: 2px;">'
            '{:.1f}%</div></div>',
            min(percentage, 100),
            color,
            percentage
        )
    usage_percentage.short_description = 'Usage Progress'
    
    def remaining_time(self, obj):
        """Display remaining time"""
        if obj.expires_at:
            from django.utils import timezone
            now = timezone.now()
            if now > obj.expires_at:
                return "Expired"
            
            remaining = obj.expires_at - now
            if remaining.days > 0:
                return f"{remaining.days} days"
            else:
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        return "No expiry"
    remaining_time.short_description = 'Remaining Time'
    
    def suspend_vouchers(self, request, queryset):
        """Admin action to suspend vouchers"""
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated} vouchers suspended successfully.')
    suspend_vouchers.short_description = "Suspend selected vouchers"
    
    def reactivate_vouchers(self, request, queryset):
        """Admin action to reactivate vouchers"""
        updated = queryset.filter(status='suspended').update(status='active')
        self.message_user(request, f'{updated} vouchers reactivated successfully.')
    reactivate_vouchers.short_description = "Reactivate suspended vouchers"
    
    def cancel_vouchers(self, request, queryset):
        """Admin action to cancel vouchers"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} vouchers cancelled successfully.')
    cancel_vouchers.short_description = "Cancel selected vouchers"


@admin.register(AvailableVoucher)
class AvailableVoucherAdmin(admin.ModelAdmin):
    list_display = [
        'voucher_code',
        'package',
        'location',
        'voucher_type',
        'is_used',
        'valid_until_display',
        'price_display',
        'batch_id',
        'is_roaming'
    ]
    
    list_filter = [
        'voucher_type',
        'is_used',
        'is_roaming',
        'package',
        'location',
        'batch_id'
    ]
    
    search_fields = [
        'voucher_code',
        'batch_id',
        'package__name'
    ]
    
    readonly_fields = [
        'validity_status',
        'created_display'
    ]
    
    fieldsets = (
        ('Voucher Information', {
            'fields': (
                'voucher_code',
                'voucher_type',
                'package',
                'location',
                'batch_id'
            )
        }),
        ('Pricing & Validity', {
            'fields': (
                'price_override',
                'valid_until',
                'validity_status'
            )
        }),
        ('Status', {
            'fields': (
                'is_used',
                'used_at',
                'used_by',
                'is_roaming'
            )
        }),
        ('Generation Info', {
            'fields': (
                'generated_by',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_display',
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'mark_as_used',
        'mark_as_unused',
        'generate_voucher_report'
    ]
    
    def valid_until_display(self, obj):
        """Format valid_until date"""
        if obj.valid_until:
            return obj.valid_until.strftime("%Y-%m-%d %H:%M")
        return "No expiry"
    valid_until_display.short_description = 'Valid Until'
    
    def price_display(self, obj):
        """Display price information"""
        if obj.price_override:
            return f"KES {obj.price_override} (Override)"
        return f"KES {obj.package.price} (Package)"
    price_display.short_description = 'Price'
    
    def created_display(self, obj):
        """Format created_at date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_display.short_description = 'Created'
    
    def validity_status(self, obj):
        """Display validity status with color coding"""
        from django.utils import timezone
        
        if obj.is_used:
            color = 'red'
            text = 'Used'
        elif obj.valid_until and timezone.now() > obj.valid_until:
            color = 'orange'
            text = 'Expired'
        elif not obj.package.is_available:
            color = 'gray'
            text = 'Package Unavailable'
        else:
            color = 'green'
            text = 'Valid'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    validity_status.short_description = 'Validity Status'
    
    def mark_as_used(self, request, queryset):
        """Admin action to mark vouchers as used"""
        from django.utils import timezone
        updated = queryset.update(is_used=True, used_at=timezone.now())
        self.message_user(request, f'{updated} vouchers marked as used.')
    mark_as_used.short_description = "Mark selected as used"
    
    def mark_as_unused(self, request, queryset):
        """Admin action to mark vouchers as unused"""
        updated = queryset.update(is_used=False, used_at=None, used_by=None)
        self.message_user(request, f'{updated} vouchers marked as unused.')
    mark_as_unused.short_description = "Mark selected as unused"
    
    def generate_voucher_report(self, request, queryset):
        """Admin action to generate voucher report"""
        total = queryset.count()
        used = queryset.filter(is_used=True).count()
        valid = queryset.filter(is_used=False).count()
        
        self.message_user(
            request, 
            f'Voucher Report: Total: {total}, Used: {used}, Valid: {valid}'
        )
    generate_voucher_report.short_description = "Generate voucher report"


# --------------------------------------------------------------------
# ADDITIONAL ADMIN CLASSES FOR OTHER MODELS
# --------------------------------------------------------------------

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'coupon_type', 'discount_value', 'is_valid', 'total_uses']
    list_filter = ['coupon_type', 'applicable_to', 'is_active']
    search_fields = ['code', 'name', 'description']
    filter_horizontal = ['applicable_packages']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'package', 'discount_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['coupon__code', 'user__username']
    autocomplete_fields = ['coupon', 'user', 'package', 'voucher']


@admin.register(FeaturedPromotion)
class FeaturedPromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'package', 'is_active', 'is_live', 'start_date', 'end_date']
    list_filter = ['promotion_type', 'is_active', 'start_date']
    search_fields = ['name', 'headline', 'package__name']
    
    # ADDED: Include the inline for locations
    inlines = [FeaturedPromotionLocationInline]
    
    def is_live(self, obj):
        return obj.is_live
    is_live.boolean = True
    is_live.short_description = 'Live Now'


# --------------------------------------------------------------------
# OPTIONAL: REGISTER THROUGH MODELS FOR DIRECT ADMIN ACCESS
# --------------------------------------------------------------------

@admin.register(PackageTypeLocation)
class PackageTypeLocationAdmin(admin.ModelAdmin):
    list_display = ['packagetype', 'location']
    list_filter = ['packagetype', 'location']
    autocomplete_fields = ['packagetype', 'location']

@admin.register(FeaturedPromotionLocation)
class FeaturedPromotionLocationAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'location']
    list_filter = ['promotion', 'location']
    autocomplete_fields = ['promotion', 'location']