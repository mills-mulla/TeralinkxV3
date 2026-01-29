# from django.contrib import admin
# from .models import *

# @admin.register(AvailableVoucher)
# class AvailableVoucherAdmin(admin.ModelAdmin):
#     list_display = ('voucher_code', 'package', 'package_code', 'duration', 'price')
#     search_fields = ('voucher_code', 'package_code')
#     list_filter = ('package',)


# @admin.register(Package)
# class PackageAdmin(admin.ModelAdmin):
#     list_display = ('package', 'price', 'package_code', 'package_duration', 'devices')
#     search_fields = ('package', 'package_code')


# @admin.register(DailyPass)
# class DailyPassAdmin(admin.ModelAdmin):
#     list_display = ('package', 'price','usage_limit', 'package_code', 'package_duration', 'devices','limit','status')
#     search_fields = ('package', 'package_code')


# @admin.register(DispatchVoucher)
# class DispatchVoucherAdmin(admin.ModelAdmin):
#     list_display = (
#         'dispatch_account', 
#         'dispatch_package',
#         'dispatch_voucher_code', 
#         'dispatch_status', 
#         'dispatch_price', 
#         'dispatch_expiry',
#         # 'usermanid', 
#         # 'uptime', 
#         'total_download', 
#         'total_upload', 
#         'active_sessions',
#         'usage_limit',
#         'expired',  # custom column to show if voucher is expired
#     )
#     search_fields = ('dispatch_account', 'dispatch_voucher_code')
#     list_filter = ('dispatch_status',)

#     # Custom field for display
#     def expired(self, obj):
#         return obj.is_expired()
#     expired.boolean = True  # shows as a True/False icon in admin
#     expired.short_description = 'Expired'


# @admin.register(ClientH)
# class ClientHAdmin(admin.ModelAdmin):
#     list_display = ('account', 'current_ip_address', 'active_voucher', 'status', 'balance','image','date_joined', 'last_login', 'voucher_expiry')
#     search_fields = ('account', 'active_voucher')
#     list_filter = ('status',)


# @admin.register(ClientMAC)
# class ClientMACAdmin(admin.ModelAdmin):
#     list_display = ('mac_address', 'ip_address', 'status')
#     search_fields = ('mac_address',)
#     list_filter = ('status',)


# @admin.register(DHCPLease)
# class DHCPLeaseAdmin(admin.ModelAdmin):
#     list_display = ('mac_address', 'address', 'active_address', 'status', 'client')
#     search_fields = ('mac_address', 'active_mac_address')
#     list_filter = ('status',)


# @admin.register(ActiveUser)
# class ActiveUserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'ip_address', 'mac_address', 'bytes_out')
#     search_fields = ('username', 'mac_address')


# @admin.register(alternateSessions)
# class alternateSessionsAdmin(admin.ModelAdmin):
#     list_display = ('alternate_no', 'alternate_bound_mac', 'alternate_status')
#     search_fields = ('alternate_no', 'alternate_bound_mac')


# @admin.register(Room)
# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('room_name',)
#     search_fields = ('room_name',)


# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('room', 'sender', 'time')
#     search_fields = ('room__room_name', 'sender')


# @admin.register(Announce)
# class AnnounceAdmin(admin.ModelAdmin):
#     list_display = ('title', 'start_date', 'end_date', 'is_active', 'priority')
#     search_fields = ('title', 'content')
#     list_filter = ('is_active',)


# @admin.register(Investment)
# class InvestmentAdmin(admin.ModelAdmin):
#     list_display = ('investor_name', 'amount', 'investment_type', 'investment_date')
#     search_fields = ('investor_name', 'investment_type')
#     list_filter = ('investment_type',)


# @admin.register(Expense)
# class ExpenseAdmin(admin.ModelAdmin):
#     list_display = ('expense_date', 'category', 'amount', 'vendor')
#     search_fields = ('vendor', 'description')
#     list_filter = ('category', 'expense_date')


# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ('transaction_id', 'initiator', 'amount', 'result_code', 'transaction_time')
#     search_fields = ('transaction_id', 'checkout_request_id', 'merchant_request_id')
#     list_filter = ('result_code', 'transaction_time')

# @admin.register(Queue)
# class QueueAdmin(admin.ModelAdmin):
#     list_display = ('recipient', 'package_code', 'package', 'price','used_credit', 'status', 'queue_time')
#     search_fields = ('recipient', 'package_code', 'checkout_request_id')
#     list_filter = ('status', 'queue_time')


# @admin.register(Advertisement)
# class AdvertisementAdmin(admin.ModelAdmin):
#     list_display = ('title', 'active', 'created_at')
#     list_filter = ('active',)
#     search_fields = ('title', 'caption')

# @admin.register(ExpiredVoucher)
# class ExpiredVoucherAdmin(admin.ModelAdmin):
#     list_display = ("expired_account", "expired_package", "expired_voucher", "expiry_time", "user_mac")
#     search_fields = ("expired_account", "expired_voucher", "user_mac")
#     list_filter = ("expiry_time", "expired_package")
#     ordering = ("-expiry_time",)

# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ("user", "message", "seen", "created_at")
#     list_filter = ("seen", "created_at")
#     search_fields = ("user__username", "message")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)



# @admin.register(DowntimeRecord)
# class DowntimeRecordAdmin(admin.ModelAdmin):
#     list_display = [
#         'name', 
#         'start_time', 
#         'end_time', 
#         'duration_minutes',
#         'severity', 
#         'affected_services',
#         'is_resolved',
#         'created_at'
#     ]
    
#     list_filter = [
#         'severity',
#         'affected_services',
#         'is_resolved',
#         'requires_follow_up',
#         'start_time',
#         'created_at'
#     ]
    
#     search_fields = [
#         'name',
#         'reason',
#         'resolution_notes',
#         'affected_regions'
#     ]
    
#     readonly_fields = [
#         'duration_minutes',
#         'duration_hours',
#         'formatted_duration',
#         'is_ongoing',
#         'affected_users_percentage',
#         'created_at',
#         'updated_at'
#     ]
    
#     fieldsets = (
#         ('Basic Information', {
#             'fields': (
#                 'name', 
#                 'start_time', 
#                 'end_time',
#                 'duration_minutes',
#                 'formatted_duration'
#             )
#         }),
#         ('Impact Details', {
#             'fields': (
#                 'affected_services',
#                 'severity',
#                 'impact_level',
#                 'affected_regions',
#                 'estimated_affected_users',
#                 'affected_users_percentage'
#             )
#         }),
#         ('Description', {
#             'fields': ('reason',)
#         }),
#         ('Resolution', {
#             'fields': (
#                 'is_resolved',
#                 'resolution_notes',
#                 'resolved_by',
#                 'resolution_time',
#                 'requires_follow_up',
#                 'follow_up_notes'
#             )
#         }),
#         ('Metadata', {
#             'fields': (
#                 'created_by',
#                 'created_at',
#                 'updated_at',
#                 'is_ongoing'
#             )
#         }),
#     )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related(
#             'created_by', 
#             'resolved_by'
#         )