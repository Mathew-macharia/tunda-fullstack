from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddToCartSerializer
from products.models import ProductListing

class IsCustomer(permissions.BasePermission):
    """
    Custom permission to only allow customers to access their cart
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'customer'

class CartViewSet(viewsets.ModelViewSet): # Changed base class to ModelViewSet
    """
    API endpoint for managing customer shopping carts
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]
    
    def get_queryset(self):
        """
        Ensure customers can only access their own cart
        """
        return Cart.objects.filter(customer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """
        Get the current user's cart, or create one if it doesn't exist
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add an item to the cart or update quantity if already exists
        """
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            listing_id = serializer.validated_data['listing_id']
            quantity = serializer.validated_data['quantity']
            
            # Get or create the user's cart
            cart, created = Cart.objects.get_or_create(customer=request.user)
            
            # Get the product listing
            listing = get_object_or_404(ProductListing, listing_id=listing_id)
            
            with transaction.atomic():
                # Check if item already exists in cart
                try:
                    cart_item = CartItem.objects.get(cart=cart, listing=listing)
                    
                    # Update quantity, validating against available stock
                    item_serializer = CartItemSerializer(
                        cart_item,
                        data={'quantity': quantity, 'listing': listing.listing_id},
                        partial=True,
                        context={'request': request}
                    )
                    
                    if item_serializer.is_valid():
                        item_serializer.save()
                        cart_serializer = self.get_serializer(cart)
                        return Response(cart_serializer.data)
                    else:
                        return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        
                except CartItem.DoesNotExist:
                    # Create new cart item
                    item_serializer = CartItemSerializer(
                        data={
                            'cart': cart.cart_id,
                            'listing': listing.listing_id,
                            'quantity': quantity,
                        },
                        context={'request': request, 'cart_id': cart.cart_id}
                    )
                    
                    if item_serializer.is_valid():
                        item_serializer.save()
                        cart_serializer = self.get_serializer(cart)
                        return Response(cart_serializer.data)
                    else:
                        return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """
        Remove an item from the cart
        """
        cart_item_id = request.data.get('cart_item_id')
        if not cart_item_id:
            return Response(
                {'error': 'cart_item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get user's cart
            cart = Cart.objects.get(customer=request.user)
            
            # Ensure the item belongs to user's cart
            cart_item = get_object_or_404(CartItem, cart_item_id=cart_item_id, cart=cart)
            cart_item.delete()
            
            # Return updated cart
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
            
        except Cart.DoesNotExist:
            return Response(
                {'error': 'You do not have an active cart'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """
        Update the quantity of an item in the cart
        """
        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        
        if not cart_item_id or quantity is None:
            return Response(
                {'error': 'cart_item_id and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get user's cart
            cart = Cart.objects.get(customer=request.user)
            
            # Ensure the item belongs to user's cart
            cart_item = get_object_or_404(CartItem, cart_item_id=cart_item_id, cart=cart)
            
            # If quantity is 0 or negative, remove the item
            if float(quantity) <= 0:
                cart_item.delete()
                serializer = self.get_serializer(cart)
                return Response(serializer.data)
                
            # Update quantity
            item_serializer = CartItemSerializer(
                cart_item,
                data={'quantity': quantity, 'listing': cart_item.listing.listing_id},
                partial=True,
                context={'request': request}
            )
            
            if item_serializer.is_valid():
                item_serializer.save()
                cart_serializer = self.get_serializer(cart)
                return Response(cart_serializer.data)
            else:
                return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Cart.DoesNotExist:
            return Response(
                {'error': 'You do not have an active cart'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        """
        Remove all items from the cart
        """
        try:
            # Get user's cart
            cart = Cart.objects.get(customer=request.user)
            
            # Delete all items
            cart.items.all().delete()
            
            # Return empty cart
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
            
        except Cart.DoesNotExist:
            return Response(
                {'error': 'You do not have an active cart'},
                status=status.HTTP_404_NOT_FOUND
            )

    def merge_guest_cart(self, request):
        """
        Merge guest cart items into the authenticated user's cart,
        prioritizing guest cart by overwriting existing items.
        """
        guest_items_data = request.data.get('items', [])
        
        if not guest_items_data:
            return Response(
                {'message': 'No guest cart items provided to merge'},
                status=status.HTTP_200_OK
            )
            
        try:
            with transaction.atomic():
                # Get or create the user's cart
                cart, created = Cart.objects.get_or_create(customer=request.user)
                
                # Clear existing items in the authenticated user's cart
                cart.items.all().delete()
                
                # Add items from the guest cart
                for item_data in guest_items_data:
                    listing_id = item_data.get('listing_id')
                    quantity = item_data.get('quantity')
                    
                    if not listing_id or quantity is None:
                        # Log error but continue with other items
                        print(f"Skipping invalid guest item: {item_data}")
                        continue
                        
                    try:
                        listing = ProductListing.objects.get(listing_id=listing_id)
                        
                        # Create new cart item (since we cleared the cart, no need to check for existence)
                        CartItem.objects.create(
                            cart=cart,
                            listing=listing,
                            quantity=quantity
                        )
                    except ProductListing.DoesNotExist:
                        print(f"ProductListing with ID {listing_id} not found. Skipping item.")
                        continue
                        
                serializer = self.get_serializer(cart)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Authenticated user does not have a cart'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred during merge: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def estimate_delivery_fee(self, request):
        """
        Estimate delivery fee for given address and current cart items with address validation
        """
        try:
            delivery_address = request.data.get('delivery_address')
            
            if not delivery_address:
                return Response(
                    {'error': 'Delivery address is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate required address fields
            required_fields = ['sub_county', 'detailed_address']
            for field in required_fields:
                if field not in delivery_address:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # PHASE 2: Address Validation
            from core.services.address_validation_service import AddressValidationService
            
            validation_service = AddressValidationService()
            validation_result = validation_service.validate_address(delivery_address)
            
            # Continue with delivery fee calculation even if there are warnings
            # (warnings are informational, not blocking)
            
            # Get cart items
            try:
                cart = Cart.objects.get(customer=request.user)
                cart_items = cart.items.all()
                
                if not cart_items.exists():
                    return Response(
                        {'error': 'Cart is empty'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except Cart.DoesNotExist:
                return Response(
                    {'error': 'Cart not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create temporary address object for calculation
            from locations.models import SubCounty, UserAddress
            
            try:
                subcounty = SubCounty.objects.get(sub_county_id=delivery_address['sub_county'])
            except SubCounty.DoesNotExist:
                return Response(
                    {'error': 'Invalid sub-county selected'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create temporary address-like object that matches AddressService expectations
            class TempAddress:
                def __init__(self, subcounty, detailed_address, delivery_address_dict):
                    self.sub_county = subcounty
                    self.county = subcounty.county
                    self.detailed_address = detailed_address
                    self.location_name = delivery_address_dict.get('location_name', '')
                    self.latitude = delivery_address_dict.get('latitude')
                    self.longitude = delivery_address_dict.get('longitude')
            
            temp_address = TempAddress(subcounty, delivery_address['detailed_address'], delivery_address)
            
            # Calculate delivery fee using centralized logic with distance tracking
            from orders.models import Order
            from core.services.address_service import AddressService
            from core.models import SystemSettings
            from decimal import Decimal
            
            # Get system settings
            base_fee = SystemSettings.objects.get_setting('base_delivery_fee', Decimal('50.00'))
            fee_per_km = SystemSettings.objects.get_setting('delivery_fee_per_km', Decimal('5.00'))
            free_threshold = SystemSettings.objects.get_setting('free_delivery_threshold', Decimal('1000.00'))
            
            # Calculate delivery fee and get distance information
            calculation_results = Order.calculate_delivery_fee_for_cart(cart_items, temp_address)
            
            delivery_fee = calculation_results['total_fee']
            distance_km = calculation_results['distance_km']
            calculation_method = calculation_results['calculation_method']
            address_used_for_calculation = calculation_results['address_used_for_calculation']
            geocoding_confidence = calculation_results['geocoding_confidence']
            
            # Calculate subtotal
            subtotal = sum(item.quantity * item.price_at_addition for item in cart_items)
            
            response_data = {
                'delivery_fee': float(delivery_fee),
                'distance_km': distance_km,
                'subtotal': float(subtotal),
                'is_free_delivery': delivery_fee == 0 and subtotal >= free_threshold,
                'calculation_details': {
                    'base_fee': float(base_fee),
                    'fee_per_km': float(fee_per_km),
                    'free_delivery_threshold': float(free_threshold),
                    'calculation_method': calculation_method
                },
                'farms_count': len(set(item.listing.farm for item in cart_items)),
                'message': f'Delivery fee calculated using {calculation_method} method',
                # PHASE 2: Include address validation results
                'address_validation': {
                    'is_valid': validation_result['is_valid'],
                    'warnings': validation_result['warnings'],
                    'suggestions': validation_result['suggestions'],
                    'confidence': validation_result['confidence'],
                    'mismatch_detected': validation_result['mismatch_detected'],
                    'detected_location': validation_result.get('detected_location')
                },
                # Address resolution details - shows which address was actually used for calculation
                'address_resolution': {
                    'address_used': address_used_for_calculation,
                    'geocoding_confidence': geocoding_confidence,
                    'input_address': f"{delivery_address.get('detailed_address', '')}, {subcounty.sub_county_name}, {subcounty.county.county_name}",
                    'explanation': 'Shows which address was actually used for distance calculation vs what you entered'
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to calculate delivery fee: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def address_autocomplete(self, request):
        """
        PHASE 3: Get address autocomplete suggestions
        """
        try:
            query = request.query_params.get('q', '').strip()
            limit = int(request.query_params.get('limit', 5))
            
            if not query or len(query) < 2:
                return Response(
                    {'suggestions': []},
                    status=status.HTTP_200_OK
                )
            
            from core.services.address_validation_service import AddressValidationService
            
            validation_service = AddressValidationService()
            suggestions = validation_service.get_autocomplete_suggestions(query, limit)
            
            return Response(
                {'suggestions': suggestions},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get address suggestions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
