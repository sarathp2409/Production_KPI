from django.contrib import admin
from .models import ScheduledTime


@admin.register(ScheduledTime)
class ScheduledTimeAdmin(admin.ModelAdmin):
    list_display = ['plant_name', 'scheduled_lprs', 'scheduled_print_start', 'is_active', 'updated_at']
    list_filter = ['is_active', 'scheduled_lprs', 'scheduled_print_start']
    search_fields = ['plant_name']
    ordering = ['plant_name']

    fieldsets = (
        ('Plant Information', {
            'fields': ('plant_name',)
        }),
        ('Schedule Times', {
            'fields': ('scheduled_lprs', 'scheduled_print_start')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
