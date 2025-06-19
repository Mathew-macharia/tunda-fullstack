from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['order_item_id', 'listing', 'farmer', 'quantity', 'price_at_purchase', 'total_price']
    can_delete = False
    fields = [
        'order_item_id', 'listing', 'farmer', 'quantity', 
        'price_at_purchase', 'total_price', 'item_status'
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'order_date', 'total_amount',
        'order_status', 'payment_status', 'estimated_delivery_date'
    ]
    list_filter = ['order_status', 'payment_status', 'delivery_time_slot']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__phone_number']
    readonly_fields = [
        'order_id', 'order_number', 'order_date', 'customer',
        'total_amount', 'created_at', 'updated_at'
    ]
    fieldsets = [
        ('Order Information', {
            'fields': [
                'order_id', 'order_number', 'customer', 'order_date',
                'total_amount', 'delivery_fee'
            ]
        }),
        ('Delivery Information', {
            'fields': [
                'delivery_location', 'estimated_delivery_date',
                'delivery_time_slot', 'special_instructions', 'rider'
            ]
        }),
        ('Payment & Status', {
            'fields': [
                'payment_method_id', 'order_status', 'payment_status'
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at']
        })
    ]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order_item_id', 'order', 'listing', 'farmer',
        'quantity', 'price_at_purchase', 'total_price', 'item_status'
    ]
    list_filter = ['item_status']
    search_fields = ['order__order_number', 'listing__product__product_name', 'farmer__first_name', 'farmer__last_name']
    readonly_fields = [
        'order_item_id', 'order', 'listing', 'farmer',
        'quantity', 'price_at_purchase', 'total_price',
        'created_at', 'updated_at'
    ]
    fieldsets = [
        ('Order Item Information', {
            'fields': [
                'order_item_id', 'order', 'listing', 'farmer',
                'quantity', 'price_at_purchase', 'total_price', 'item_status'
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at']
        })
    ]
