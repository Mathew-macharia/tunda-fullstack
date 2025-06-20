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
