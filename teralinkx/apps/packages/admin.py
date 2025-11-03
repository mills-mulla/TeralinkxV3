# apps/packages/admin.py
from django.contrib import admin
from .models import (
    PackageType, 
    UserPackagePreference, 
    PersonalizedPackageOffer,
    AvailableVoucher, 
    DispatchVoucher
)

@admin.register(PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'package_category', 'price', 'is_active', 'status']
    list_filter = ['package_category', 'is_active', 'status']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserPackagePreference)
class UserPackagePreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'package_type', 'preference_score', 'purchase_count']
    list_filter = ['frequently_purchased', 'typical_usage_time']
    search_fields = ['user__username', 'package_type__name']

@admin.register(PersonalizedPackageOffer)
class PersonalizedPackageOfferAdmin(admin.ModelAdmin):
    list_display = ['user', 'package_type', 'personalized_price', 'is_active', 'valid_until']
    list_filter = ['is_active', 'valid_until']
    search_fields = ['user__username', 'package_type__name']

@admin.register(AvailableVoucher)
class AvailableVoucherAdmin(admin.ModelAdmin):
    list_display = ['voucher_code', 'package_type', 'is_used', 'created_at']
    list_filter = ['is_used', 'voucher_type', 'is_roaming']
    search_fields = ['voucher_code', 'package_type__name']

@admin.register(DispatchVoucher)
class DispatchVoucherAdmin(admin.ModelAdmin):
    list_display = ['voucher_code', 'dispatch_account', 'package_type', 'status', 'activated_at']
    list_filter = ['status', 'is_roaming', 'activated_at']
    search_fields = ['voucher_code', 'dispatch_account', 'package_type__name']