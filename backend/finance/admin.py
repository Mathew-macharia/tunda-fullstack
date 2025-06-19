from django.contrib import admin
from .models import Payout

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        'payout_id', 'user', 'amount', 'status',
        'transaction_reference', 'payout_date', 'processed_date'
    )
    list_filter = ('status', 'payout_date', 'processed_date')
    search_fields = ('user__username', 'transaction_reference', 'notes')
    date_hierarchy = 'payout_date'
    readonly_fields = ('payout_id', 'payout_date')
