from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta

# Uncomment and update when models are available
# from .models import DowntimeRecord

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