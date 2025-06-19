from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'review_id', 'reviewer', 'target_type', 
        'rating', 'is_verified_purchase', 'is_visible', 'review_date'
    )
    list_filter = ('target_type', 'rating', 'is_verified_purchase', 'is_visible')
    search_fields = ('reviewer__username', 'comment')
    readonly_fields = ('review_id', 'reviewer', 'order_item', 'review_date')
