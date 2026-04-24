from django.contrib import admin
from .models import Monitor


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'timeout', 'alert_email', 'last_heartbeat', 'expires_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'alert_email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('id', 'timeout', 'alert_email')
        }),
        ('Status', {
            'fields': ('status', 'last_heartbeat', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

