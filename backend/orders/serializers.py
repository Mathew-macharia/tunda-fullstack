from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

from .models import Order, OrderItem
from products.models import ProductListing
from locations.models import Location, County, SubCounty, UserAddress
from carts.models import Cart, CartItem
from products.serializers import ProductListingSerializer
from locations.serializers import LocationSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    listing_details = serializers.SerializerMethodField(read_only=True)
    order_details = serializers.SerializerMethodField(read_only=True)
    farm_details = serializers.SerializerMethodField(read_only=True) # New field
    
    class Meta:
        model = OrderItem
        fields = [
            'order_item_id', 'order', 'listing', 'listing_details', 'order_details', 'farmer',
            'quantity', 'price_at_purchase', 'total_price', 'item_status',
            'created_at', 'updated_at', 'farm_details' # Add farm_details here
        ]
        read_only_fields = [
            'order_item_id', 'order', 'listing', 'farmer',
            'quantity', 'price_at_purchase', 'total_price', 'created_at', 'updated_at'
        ]
        
    def get_listing_details(self, obj):
        """Get detailed information about the product listing"""
        return ProductListingSerializer(obj.listing, context=self.context).data
    
    def get_order_details(self, obj):
        """Get order details including payment information"""
        from payments.models import PaymentMethod
        
        order = obj.order
        order_data = {
            'order_id': order.order_id,
            'order_number': order.order_number,
            'order_status': order.order_status,
            'payment_status': order.payment_status,
            'total_amount': order.total_amount,
            'delivery_fee': order.delivery_fee,
            'order_date': order.order_date,
            'estimated_delivery_date': order.estimated_delivery_date,
            'delivery_time_slot': order.delivery_time_slot,
            'special_instructions': order.special_instructions,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
            'payment_method': None
        }
        
        # Include payment method details if available
        if order.payment_method:
            order_data['payment_method'] = {
                'payment_method_id': order.payment_method.payment_method_id,
                'payment_type': order.payment_method.payment_type,
                'is_default': order.payment_method.is_default
            }
        
        return order_data

    def get_farm_details(self, obj):
        """Get detailed information about the farm associated with the product listing"""
        if obj.listing and obj.listing.farm:
            return {
                'farm_id': obj.listing.farm.farm_id,
                'farm_name': obj.listing.farm.farm_name,
                'location_name': obj.listing.farm.location_name
            }
        return None


class AdminOrderItemSerializer(serializers.ModelSerializer):
    """Admin-specific serializer for order items with full details"""
    listing = serializers.SerializerMethodField(read_only=True)
    farmer = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'order_item_id', 'listing', 'farmer', 'quantity', 
            'price_at_purchase', 'total_price', 'item_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
        
    def get_listing(self, obj):
        """Get detailed listing information"""
        if not obj.listing:
            return None
            
        return {
            'listing_id': obj.listing.listing_id,
            'product': {
                'product_id': obj.listing.product.product_id,
                'name': obj.listing.product.product_name,
                'category': {
                    'category_id': obj.listing.product.category.category_id,
                    'name': obj.listing.product.category.category_name
                } if obj.listing.product.category else None,
                'image_url': obj.listing.product.image_url,
                'description': obj.listing.product.description
            },
            'farm': {
                'farm_id': obj.listing.farm.farm_id,
                'name': obj.listing.farm.farm_name,
                'location': obj.listing.farm.location_name
            } if obj.listing.farm else None,

            'current_price': obj.listing.current_price,
            'quantity_available': obj.listing.quantity_available
        }
    
    def get_farmer(self, obj):
        """Get farmer information"""
        if not obj.farmer:
            return None
            
        return {
            'user_id': obj.farmer.user_id,
            'first_name': obj.farmer.first_name,
            'last_name': obj.farmer.last_name,
            'phone_number': obj.farmer.phone_number,
            'email': obj.farmer.email
        }


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating a new order from a cart"""
    # New address-based approach
    delivery_address = serializers.DictField(required=False, allow_null=True)
    
    # Legacy location-based approach (for backward compatibility)
    delivery_location_id = serializers.IntegerField(required=False, allow_null=True)
    
    payment_method_id = serializers.IntegerField(required=False, allow_null=True)
    payment_method = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    estimated_delivery_date = serializers.DateField(required=False, allow_null=True)
    delivery_time_slot = serializers.ChoiceField(
        choices=Order.DELIVERY_TIME_SLOT_CHOICES,
        required=False,
        allow_null=True
    )
    special_instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    expected_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    def validate(self, data):
        """Validate order creation data"""
        delivery_address = data.get('delivery_address')
        delivery_location_id = data.get('delivery_location_id')
        
        # Must have either delivery_address or delivery_location_id
        if not delivery_address and not delivery_location_id:
            raise serializers.ValidationError({
                "delivery": "Either delivery_address or delivery_location_id must be provided."
            })
        
        # If delivery_address is provided, validate its structure
        if delivery_address:
            required_fields = ['full_name', 'phone_number', 'location', 'detailed_address']
            for field in required_fields:
                if field not in delivery_address:
                    raise serializers.ValidationError({
                        "delivery_address": f"Missing required field: {field}"
                    })
        
        return data
    
    def validate_delivery_location_id(self, value):
        """Validate that the delivery location belongs to the user (legacy)"""
        if value is None:
            return value
            
        user = self.context['request'].user
        try:
            from locations.models import Location
            location = Location.objects.get(location_id=value, user=user)
            return value
        except Location.DoesNotExist:
            raise serializers.ValidationError("This location does not exist or doesn't belong to you.")
    
    def create(self, validated_data):
        """Create a new order from the user's cart"""
        user = self.context['request'].user
        
        # Get the user's cart
        try:
            cart = Cart.objects.get(customer=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"cart": "You don't have an active cart or it's empty."})
        
        # Ensure cart is not empty
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            raise serializers.ValidationError({"cart": "Your cart is empty."})
        
        # Handle delivery location
        delivery_location = None
        delivery_address = validated_data.get('delivery_address')
        delivery_location_id = validated_data.get('delivery_location_id')
        
        if delivery_address:
            # Create new location from address
            subcounty = SubCounty.objects.get(sub_county_id=delivery_address['location'])
            county = subcounty.county
            
            # Create a temporary UserAddress for this order
            user_address = UserAddress.objects.create(
                user=user,
                full_name=delivery_address['full_name'],
                phone_number=delivery_address['phone_number'],
                county=county,
                sub_county=subcounty,
                location_name=f"{subcounty.sub_county_name}, {county.county_name}",
                detailed_address=delivery_address['detailed_address']
            )
            
            # Create a corresponding Location for backward compatibility
            delivery_location = Location.objects.create(
                user=user,
                location_name=f"{subcounty.sub_county_name}, {county.county_name}",
                sub_location=delivery_address['detailed_address'],
                latitude=Decimal('0.0'),  # Default coordinates
                longitude=Decimal('0.0'),
                is_default=False
            )
            
        elif delivery_location_id:
            # Use existing location (legacy)
            delivery_location = Location.objects.get(location_id=delivery_location_id, user=user)
        
        # Start a transaction to ensure all operations succeed or fail together
        with transaction.atomic():
            # Check stock availability and update product quantities
            inventory_issues = []
            for cart_item in cart_items:
                listing = cart_item.listing
                
                # Verify quantity is available
                if cart_item.quantity > listing.quantity_available:
                    inventory_issues.append({
                        "product": listing.product.product_name,
                        "requested": cart_item.quantity,
                        "available": listing.quantity_available
                    })
            
            # If inventory issues, abort order creation
            if inventory_issues:
                error_messages = []
                for issue in inventory_issues:
                    error_messages.append(
                        f"Insufficient stock for {issue['product']}: "
                        f"requested {issue['requested']}, available {issue['available']}"
                    )
                raise serializers.ValidationError({"inventory": error_messages})
            
            # Calculate total amount
            total_amount = sum(item.quantity * item.price_at_addition for item in cart_items)
            
            # Calculate delivery fee using centralized logic
            delivery_fee = Order.calculate_delivery_fee_for_cart(cart_items, delivery_location)
            
            # Determine order status based on payment method
            payment_method = validated_data.get('payment_method', 'mpesa')
            order_status = 'confirmed' if payment_method == 'cash_on_delivery' else 'pending_payment'
            
            # Create the order
            order = Order.objects.create(
                customer=user,
                delivery_location=delivery_location,
                payment_method_id=validated_data.get('payment_method_id'),
                total_amount=total_amount + delivery_fee,
                delivery_fee=delivery_fee,
                order_status=order_status,
                estimated_delivery_date=validated_data.get('estimated_delivery_date'),
                delivery_time_slot=validated_data.get('delivery_time_slot'),
                special_instructions=validated_data.get('special_instructions')
            )
            
            # Create order items and update inventory
            for cart_item in cart_items:
                listing = cart_item.listing
                
                print(f"DEBUG: Creating order item for listing {listing.listing_id}")
                print(f"DEBUG: Listing farmer: {listing.farm.farmer}")
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    listing=listing,
                    farmer=listing.farm.farmer,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.price_at_addition,
                    total_price=cart_item.quantity * cart_item.price_at_addition
                )
                
                # Update inventory
                listing.quantity_available -= cart_item.quantity
                listing.save()
            
            print(f"DEBUG: All OrderItems created. Order items count: {order.items.count()}")
            print(f"DEBUG: Farmers in order: {list(order.get_farmers())}")
            
            # Clear the cart
            cart_items.delete()
            
            return order


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order item status by farmers"""
    # Restrict choices for farmers to exclude 'delivered'
    item_status = serializers.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('harvested', 'Harvested'),
            ('packed', 'Packed'),
            # 'delivered' is intentionally excluded for farmers
        ]
    )
    
    class Meta:
        model = OrderItem
        fields = ['item_status']
        
    def validate(self, data):
        """
        Validate order item status updates based on payment status and delivery method
        """
        item_status = data.get('item_status')
        order_item = self.instance
        order = order_item.order
        
        if not item_status:
            return data
        
        # Get current status
        current_status = order_item.item_status
        
        # Status progression validation for farmer-updatable statuses
        status_progression = {
            'pending': ['harvested'],
            'harvested': ['packed'],
            'packed': [], # Farmers cannot set to 'delivered'
        }
        
        if item_status not in status_progression.get(current_status, []):
            valid_next = status_progression.get(current_status, [])
            if not valid_next: # If current_status is 'packed' or 'delivered'
                raise serializers.ValidationError(
                    f"Cannot change status from '{current_status}'. This item is already packed or delivered."
                )
            raise serializers.ValidationError(
                f"Cannot change status from '{current_status}' to '{item_status}'. "
                f"Valid next statuses: {valid_next}"
            )
        
        # Payment validation - farmers cannot update status until payment is confirmed
        # EXCEPTION: Cash on Delivery orders can be updated up to 'packed'
        payment_method = order.payment_method
        is_cash_on_delivery = payment_method and payment_method.payment_type == 'CashOnDelivery'
        
        if not is_cash_on_delivery:
            # For non-cash orders, payment must be confirmed before any status updates
            if order.payment_status != 'paid':
                raise serializers.ValidationError(
                    "Cannot update order item status until payment is confirmed. "
                    f"Current payment status: {order.payment_status}"
                )
        
        # Farmers are explicitly prevented from setting 'delivered' status
        if item_status == 'delivered':
            raise serializers.ValidationError("Farmers cannot directly set item status to 'delivered'.")
            
        return data


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for viewing orders with nested items"""
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_location_details = serializers.SerializerMethodField(read_only=True)
    customer_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'order_id', 'order_number', 'customer', 'customer_name', 
            'order_date', 'delivery_location', 'delivery_location_details',
            'payment_method_id', 'total_amount', 'delivery_fee',
            'order_status', 'payment_status', 'estimated_delivery_date',
            'delivery_time_slot', 'special_instructions', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
        
    def get_delivery_location_details(self, obj):
        """Get detailed information about the delivery location"""
        return LocationSerializer(obj.delivery_location).data
        
    def get_customer_name(self, obj):
        """Get the customer's full name"""
        return obj.customer.get_full_name() or obj.customer.phone_number


class AdminOrderSerializer(serializers.ModelSerializer):
    """Admin-specific serializer for orders with complete details"""
    items = AdminOrderItemSerializer(many=True, read_only=True)
    customer = serializers.SerializerMethodField(read_only=True)
    payment_method = serializers.SerializerMethodField(read_only=True)
    delivery_address = serializers.SerializerMethodField(read_only=True)
    delivery = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'order_id', 'order_number', 'customer', 'order_date', 
            'delivery_address', 'payment_method', 'total_amount', 'delivery_fee',
            'order_status', 'payment_status', 'estimated_delivery_date',
            'delivery_time_slot', 'special_instructions', 'items', 'delivery',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
        
    def get_customer(self, obj):
        """Get complete customer information"""
        if not obj.customer:
            return None
            
        return {
            'user_id': obj.customer.user_id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'phone_number': obj.customer.phone_number,
            'email': obj.customer.email,
            'user_role': obj.customer.user_role,
            'is_active': obj.customer.is_active
        }
    
    def get_payment_method(self, obj):
        """Get payment method details"""
        if not obj.payment_method:
            return None
            
        return {
            'payment_method_id': obj.payment_method.payment_method_id,
            'payment_type': obj.payment_method.payment_type,
            'is_default': obj.payment_method.is_default
        }
    
    def get_delivery_address(self, obj):
        """Get delivery address information"""
        if not obj.delivery_location:
            return None
            
        return {
            'location_id': obj.delivery_location.location_id,
            'location_name': obj.delivery_location.location_name,
            'sub_location': obj.delivery_location.sub_location,
            'latitude': obj.delivery_location.latitude,
            'longitude': obj.delivery_location.longitude
        }
    
    def get_delivery(self, obj):
        """Get delivery information if available"""
        if not hasattr(obj, 'delivery'):
            return None
            
        delivery = obj.delivery
        return {
            'delivery_id': delivery.delivery_id,
            'delivery_status': delivery.delivery_status,
            'rider': {
                'user_id': delivery.rider.user_id,
                'first_name': delivery.rider.first_name,
                'last_name': delivery.rider.last_name,
                'phone_number': delivery.rider.phone_number
            } if delivery.rider else None,
            'pickup_time': delivery.pickup_time,
            'delivery_time': delivery.delivery_time,
            'delivery_notes': delivery.delivery_notes
        }
