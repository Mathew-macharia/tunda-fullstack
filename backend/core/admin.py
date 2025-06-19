from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('setting_key', 'setting_value', 'setting_type', 'updated_at')
    list_filter = ('setting_type',)
    search_fields = ('setting_key', 'setting_value', 'description')
    readonly_fields = ('updated_at',)
    ordering = ('setting_key',)
    fieldsets = (
        (None, {
            'fields': ('setting_key', 'setting_value', 'setting_type', 'description')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        })
    )
