from django.contrib import admin
from .models import MarketPrice, WeatherAlert

@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = (
        'price_id', 'product', 'location', 'average_price',
        'min_price', 'max_price', 'price_date', 'data_source'
    )
    list_filter = ('data_source', 'price_date', 'location')
    search_fields = ('product__name', 'location__name')
    date_hierarchy = 'price_date'
    readonly_fields = ('price_id', 'created_at')

@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = (
        'alert_id', 'location', 'alert_type', 'severity',
        'start_date', 'end_date', 'is_active'
    )
    list_filter = ('alert_type', 'severity', 'is_active', 'start_date')
    search_fields = ('alert_message', 'location__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('alert_id', 'created_at')
