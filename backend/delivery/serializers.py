from rest_framework import serializers
from django.db import transaction
from .models import Vehicle, Delivery, DeliveryRoute
from users.models import User
from orders.models import Order
from locations.models import Location


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model"""
    rider_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'vehicle_id', 'rider', 'rider_name', 'vehicle_type', 'registration_number', 
            'capacity_kg', 'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['vehicle_id', 'created_at', 'updated_at']
    
    def get_rider_name(self, obj):
        """Return the rider's full name"""
        return obj.rider.get_full_name()
    
    def validate_rider(self, value):
        """Validate that the rider has the 'rider' role"""
        if value.user_role != 'rider':
            raise serializers.ValidationError("Only users with the role 'rider' can have a vehicle.")
        
        # Check if the rider already has a vehicle (unless this is an update)
        instance = getattr(self, 'instance', None)
        if instance is None or instance.rider != value:  # For new vehicle or changing rider
            if Vehicle.objects.filter(rider=value).exists():
                raise serializers.ValidationError("This rider already has a vehicle registered.")
        
        return value
    
    def validate_registration_number(self, value):
        """Validate the registration number is unique"""
        instance = getattr(self, 'instance', None)
        if instance is None or instance.registration_number != value:  # For new vehicle or changing reg num
            if Vehicle.objects.filter(registration_number=value).exists():
                raise serializers.ValidationError("This registration number is already in use.")
        
        return value


class DeliverySerializer(serializers.ModelSerializer):
    """Serializer for Delivery model"""
from orders.serializers import OrderSerializer # Import OrderSerializer

class DeliverySerializer(serializers.ModelSerializer):
    """Serializer for Delivery model"""
    rider_name = serializers.SerializerMethodField(read_only=True)
    customer_name = serializers.SerializerMethodField(read_only=True)
    delivery_location = serializers.SerializerMethodField(read_only=True)
    vehicle_details = serializers.SerializerMethodField(read_only=True)
    order = OrderSerializer(read_only=True) # Include full Order object

    class Meta:
        model = Delivery
        fields = [
            'delivery_id', 'order', 'rider', 'rider_name', 
            'vehicle', 'vehicle_details', 'delivery_status', 'pickup_time', 
            'delivery_time', 'delivery_notes', 'customer_name', 'delivery_location',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['delivery_id', 'pickup_time', 'delivery_time', 'created_at', 'updated_at']
    
    def get_rider_name(self, obj):
        """Return the rider's full name if a rider is assigned"""
        if obj.rider:
            return obj.rider.get_full_name()
        return None
    
    def get_customer_name(self, obj):
        """Return the customer's name"""
        return obj.order.customer.get_full_name()
    
    def get_delivery_location(self, obj):
        """Return the delivery location details"""
        location = obj.order.delivery_location
        if location:
            return {
                'location_id': location.location_id,
                'location_name': location.location_name,
                'sub_location': location.sub_location,
                'landmark': location.landmark,
                'latitude': str(location.latitude),
                'longitude': str(location.longitude)
            }
        return None
    
    def get_vehicle_details(self, obj):
        """Return vehicle details if a vehicle is assigned"""
        if obj.vehicle:
            return {
                'vehicle_id': obj.vehicle.vehicle_id,
                'vehicle_type': obj.vehicle.get_vehicle_type_display(),
                'registration_number': obj.vehicle.registration_number
            }
        return None
    
    def validate(self, data):
        """Validate delivery data"""
        # If rider is provided, check their role
        rider = data.get('rider')
        if rider and rider.user_role != 'rider':
            raise serializers.ValidationError({
                'rider': "Only users with the role 'rider' can be assigned to deliveries."
            })
        
        # Validate order status
        order = data.get('order', getattr(self.instance, 'order', None))
        if order:
            valid_order_statuses = ['confirmed', 'processing', 'out_for_delivery', 'delivered']
            if order.order_status not in valid_order_statuses:
                raise serializers.ValidationError({
                    'order': f"Only orders with status in {valid_order_statuses} can have deliveries."
                })
            
            # Validate payment status for non-COD orders
            if order.payment_method and order.payment_method.payment_type != 'CashOnDelivery' and order.payment_status != 'paid':
                raise serializers.ValidationError({
                    'order': "Orders must be paid before delivery can be assigned (except for Cash On Delivery)."
                })
        
        # Validate that the vehicle belongs to the rider
        vehicle = data.get('vehicle')
        if vehicle and rider and vehicle.rider != rider:
            raise serializers.ValidationError({
                'vehicle': "The vehicle must belong to the assigned rider."
            })
        
        return data


class DeliveryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Delivery status"""
    
    class Meta:
        model = Delivery
        fields = ['delivery_status', 'delivery_notes']
    
    def validate_delivery_status(self, value):
        """Validate the status transition is logical"""
        if not self.instance:
            return value
            
        current_status = self.instance.delivery_status
        valid_transitions = {
            'assigned': ['picked_up', 'failed'],
            'pending_pickup': ['on_the_way', 'failed'], 
            'picked_up': ['on_the_way', 'failed'],
            'on_the_way': ['delivered', 'failed'],
            'delivered': [],  # Terminal state
            'failed': []      # Terminal state
        }
        
        if value not in valid_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot change delivery status from '{current_status}' to '{value}'. "
                f"Valid transitions are: {valid_transitions[current_status]}"
            )
        
        return value


class DeliveryRouteSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryRoute model"""
    rider_name = serializers.SerializerMethodField(read_only=True)
    location_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DeliveryRoute
        fields = [
            'route_id', 'rider', 'rider_name', 'route_name', 'route_locations',
            'location_details', 'estimated_time_hours', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['route_id', 'created_at', 'updated_at']
    
    def get_rider_name(self, obj):
        """Return the rider's full name"""
        return obj.rider.get_full_name()
    
    def get_location_details(self, obj):
        """Return details for each location in the route"""
        # route_locations should be a list of location IDs
        location_ids = obj.route_locations
        if not isinstance(location_ids, list):
            return []
        
        locations = []
        for location_id in location_ids:
            try:
                location = Location.objects.get(location_id=location_id)
                locations.append({
                    'location_id': location.location_id,
                    'location_name': location.location_name,
                    'sub_location': location.sub_location,
                    'landmark': location.landmark,
                    'latitude': str(location.latitude),
                    'longitude': str(location.longitude)
                })
            except Location.DoesNotExist:
                # Include the ID but mark as not found
                locations.append({
                    'location_id': location_id,
                    'error': 'Location not found'
                })
        
        return locations
    
    def validate_rider(self, value):
        """Validate that the rider has the 'rider' role"""
        if value.user_role != 'rider':
            raise serializers.ValidationError("Only users with the role 'rider' can have delivery routes.")
        return value
    
    def validate_route_locations(self, value):
        """Validate that route_locations is a list of valid location IDs"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Route locations must be a list of location IDs.")
        
        if not value:
            raise serializers.ValidationError("Route must include at least one location.")
        
        # Check that all locations exist
        invalid_locations = []
        for location_id in value:
            if not Location.objects.filter(location_id=location_id).exists():
                invalid_locations.append(location_id)
        
        if invalid_locations:
            raise serializers.ValidationError(f"The following location IDs do not exist: {invalid_locations}")
        
        return value
