from django.contrib import admin
from .models import PaymentMethod, PaymentTransaction

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('payment_method_id', 'user', 'payment_type', 'mpesa_phone', 'is_default', 'is_active', 'created_at')
    list_filter = ('payment_type', 'is_default', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__phone_number', 'mpesa_phone')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'payment_type', 'mpesa_phone', 'is_default', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        })
    )

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'payment_method', 'amount', 'payment_status', 'payment_date', 'created_at')
    list_filter = ('payment_status',)
    search_fields = ('order__order_number', 'transaction_code')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('order', 'payment_method', 'amount', 'transaction_code', 'payment_status', 'payment_date')
        }),
        ('Additional Information', {
            'fields': ('failure_reason',),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        })
    )
