from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Vehicle, Delivery, DeliveryRoute
from .serializers import (
    VehicleSerializer, 
    DeliverySerializer, 
    DeliveryUpdateSerializer,
    DeliveryRouteSerializer
)
from users.models import User
from orders.models import Order


class IsRiderOrAdmin(permissions.BasePermission):
    """Custom permission to only allow riders to access their own data or admins to access all"""
    
    def has_permission(self, request, view):
        # Allow authenticated requests only
        if not request.user.is_authenticated:
            return False
        
        # Admin users can do anything
        if request.user.user_role == 'admin':
            return True
        
        # Riders can only access their own data
        return request.user.user_role == 'rider'
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.user_role == 'admin':
            return True
        
        # Riders can only access their own data
        if hasattr(obj, 'rider'):
            return obj.rider == request.user
        elif hasattr(obj, 'rider_id'):
            return obj.rider_id == request.user.id
        
        return False


class IsCustomerForOwnOrders(permissions.BasePermission):
    """Custom permission to allow customers to view their own order deliveries"""
    
    def has_permission(self, request, view):
        # Allow authenticated requests only
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.user_role == 'admin':
            return True
        
        # Riders can access deliveries assigned to them
        if request.user.user_role == 'rider' and obj.rider == request.user:
            return True
        
        # Customers can only access deliveries for their own orders
        if request.user.user_role == 'customer':
            return obj.order.customer == request.user
        
        return False


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for Vehicle model"""
    serializer_class = VehicleSerializer
    permission_classes = [IsRiderOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_role == 'admin':
            return Vehicle.objects.all()
        elif user.user_role == 'rider':
            return Vehicle.objects.filter(rider=user)
        return Vehicle.objects.none()
    
    def perform_create(self, serializer):
        # If a rider is creating their own vehicle, ensure rider is set to the current user
        user = self.request.user
        if user.user_role == 'rider':
            serializer.save(rider=user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """Toggle the is_active status of a vehicle"""
        vehicle = self.get_object()
        vehicle.is_active = not vehicle.is_active
        vehicle.save()
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)


class DeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet for Delivery model"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['delivery_status']
    ordering_fields = ['created_at', 'pickup_time', 'delivery_time']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return DeliveryUpdateSerializer
        return DeliverySerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_role == 'admin':
            # For admin, fetch all deliveries, but ensure rider and order customer exist
            return Delivery.objects.select_related('rider', 'order__customer').filter(rider__isnull=False, order__customer__isnull=False)
        elif user.user_role == 'rider':
            return Delivery.objects.filter(rider=user)
        elif user.user_role == 'customer':
            return Delivery.objects.filter(order__customer=user)
        return Delivery.objects.none()
    
    def get_permissions(self):
        """Set custom permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsCustomerForOwnOrders]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsRiderOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Override create method to check permissions before serializer validation"""
        user = request.user
        if user.user_role != 'admin':
            return Response(
                {"detail": "Only admins can create new deliveries."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update the delivery status"""
        delivery = self.get_object()
        
        # Only the assigned rider or an admin can update the status
        if request.user.user_role != 'admin' and (delivery.rider != request.user):
            return Response(
                {"detail": "You do not have permission to update this delivery status."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Extract status from request data
        new_status = request.data.get('delivery_status')
        notes = request.data.get('delivery_notes', '')
        
        if not new_status:
            return Response(
                {"detail": "Delivery status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status transition
        current_status = delivery.delivery_status
        valid_transitions = {
            'pending_pickup': ['on_the_way', 'failed'],
            'on_the_way': ['delivered', 'failed'],
            'delivered': [],  # Terminal state
            'failed': []      # Terminal state
        }
        
        if new_status not in valid_transitions[current_status]:
            return Response(
                {"detail": f"Cannot change delivery status from '{current_status}' to '{new_status}'. "
                        f"Valid transitions are: {valid_transitions[current_status]}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the delivery status
        delivery.delivery_status = new_status
        if notes:
            delivery.delivery_notes = notes
        delivery.save()
        
        serializer = DeliverySerializer(delivery)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_deliveries(self, request):
        """Get deliveries assigned to the current user (rider)"""
        user = request.user
        if user.user_role != 'rider':
            return Response(
                {"detail": "Only riders can access their deliveries."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = Delivery.objects.filter(
            rider=user,
            order__customer__isnull=False
        ).select_related('order', 'order__customer').prefetch_related(
            'order__items',
            'order__items__listing__product',
            'order__items__listing__farm'
        )
        
        # Manually apply filtering and ordering for custom action
        filtered_queryset = self.filter_queryset(queryset)
        
        serializer = DeliverySerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_orders_delivery(self, request):
        """Get deliveries for the current user's orders (customer)"""
        user = request.user
        if user.user_role != 'customer':
            return Response(
                {"detail": "Only customers can access their order deliveries."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        deliveries = Delivery.objects.filter(order__customer=user).select_related('order').prefetch_related(
            'order__items',
            'order__items__listing__product',
            'order__items__listing__farm'
        )
        serializer = DeliverySerializer(deliveries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_rider(self, request, pk=None):
        """Assign a rider to a delivery (Admin only)"""
        if request.user.user_role != 'admin':
            return Response(
                {"detail": "Only admins can assign riders to deliveries."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        delivery = self.get_object()
        rider_id = request.data.get('rider_id')
        
        if not rider_id:
            return Response(
                {"detail": "rider_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rider = User.objects.get(user_id=rider_id, user_role='rider')
        except User.DoesNotExist:
            return Response(
                {"detail": "Rider not found or user is not a rider."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Assign the rider
        delivery.rider = rider
        delivery.save()
        
        serializer = DeliverySerializer(delivery)
        return Response({
            "detail": f"Rider {rider.get_full_name()} successfully assigned to delivery.",
            "delivery": serializer.data
        })

    @action(detail=False, methods=['get'])
    def available_riders(self, request):
        """Get list of available riders (Admin only)"""
        if request.user.user_role != 'admin':
            return Response(
                {"detail": "Only admins can view available riders."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all riders who are active
        riders = User.objects.filter(user_role='rider', is_active=True)
        
        rider_data = []
        for rider in riders:
            # Count active deliveries for each rider
            active_deliveries_count = Delivery.objects.filter(
                rider=rider,
                delivery_status__in=['pending_pickup', 'on_the_way']
            ).count()
            
            rider_data.append({
                'user_id': rider.user_id,
                'first_name': rider.first_name,
                'last_name': rider.last_name,
                'full_name': rider.get_full_name(),
                'phone_number': rider.phone_number,
                'email': rider.email,
                'active_deliveries_count': active_deliveries_count,
                'has_vehicle': hasattr(rider, 'vehicle') and rider.vehicle.is_active
            })
        
        return Response(rider_data)


class DeliveryRouteViewSet(viewsets.ModelViewSet):
    """ViewSet for DeliveryRoute model"""
    serializer_class = DeliveryRouteSerializer
    permission_classes = [IsRiderOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_role == 'admin':
            return DeliveryRoute.objects.all()
        elif user.user_role == 'rider':
            return DeliveryRoute.objects.filter(rider=user)
        return DeliveryRoute.objects.none()
    
    def perform_create(self, serializer):
        # If a rider is creating their own route, ensure rider is set to the current user
        user = self.request.user
        if user.user_role == 'rider':
            serializer.save(rider=user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def active_routes(self, request):
        """Get active routes for the current user (rider)"""
        user = request.user
        if user.user_role == 'rider':
            routes = DeliveryRoute.objects.filter(rider=user, is_active=True)
        elif user.user_role == 'admin':
            routes = DeliveryRoute.objects.filter(is_active=True)
        else:
            return Response(
                {"detail": "You do not have permission to view routes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DeliveryRouteSerializer(routes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """Toggle the is_active status of a route"""
        route = self.get_object()
        route.is_active = not route.is_active
        route.save()
        serializer = self.get_serializer(route)
        return Response(serializer.data)
