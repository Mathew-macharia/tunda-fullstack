from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['price_at_addition', 'subtotal', 'added_at', 'updated_at']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'customer', 'item_count', 'total_value', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__phone_number']
    inlines = [CartItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    
    def total_value(self, obj):
        return sum(item.quantity * item.price_at_addition for item in obj.items.all())
    
    item_count.short_description = 'Number of Items'
    total_value.short_description = 'Total Value'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart_item_id', 'cart', 'listing', 'quantity', 'price_at_addition', 'subtotal', 'added_at']
    readonly_fields = ['price_at_addition', 'added_at', 'updated_at']
    search_fields = ['cart__customer__first_name', 'cart__customer__last_name', 'listing__product__product_name']
    list_filter = ['added_at']
    
    def subtotal(self, obj):
        return obj.quantity * obj.price_at_addition
    
    subtotal.short_description = 'Subtotal'
