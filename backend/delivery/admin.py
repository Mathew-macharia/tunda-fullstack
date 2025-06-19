from django.contrib import admin
from .models import Vehicle, Delivery, DeliveryRoute

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_id', 'rider', 'vehicle_type', 'registration_number', 'capacity_kg', 'is_active')
    list_filter = ('vehicle_type', 'is_active')
    search_fields = ('registration_number', 'rider__first_name', 'rider__last_name', 'rider__phone_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('delivery_id', 'order', 'rider', 'vehicle', 'delivery_status', 'pickup_time', 'delivery_time')
    list_filter = ('delivery_status',)
    search_fields = ('order__order_number', 'rider__first_name', 'rider__last_name', 'rider__phone_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('order', 'rider', 'vehicle')

@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ('route_id', 'rider', 'route_name', 'estimated_time_hours', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('route_name', 'rider__first_name', 'rider__last_name', 'rider__phone_number')
    readonly_fields = ('created_at', 'updated_at')
