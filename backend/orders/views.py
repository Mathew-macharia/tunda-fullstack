from rest_framework import viewsets, status, permissions, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils import timezone
import csv
from decimal import Decimal # Import Decimal

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, 
    OrderItemSerializer, OrderItemUpdateSerializer,
    AdminOrderSerializer
)
from products.models import ProductListing
from core.models import SystemSettings # Import SystemSettings


class IsCustomer(permissions.BasePermission):
    """
    Custom permission to only allow customers to access their own orders
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'customer'
        
    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user


class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow farmers to access their order items
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'farmer'


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_role == 'admin'


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing customer orders.
    Customers can create, view, and manage their orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    http_method_names = ['get', 'post', 'head', 'options']  # Explicitly allow POST
    
    def get_queryset(self):
        """
        Ensure customers can only access their own orders
        """
        return Order.objects.filter(customer=self.request.user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action
        """
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new order from the customer's cart
        """
        print(f"DEBUG: Received order creation request")
        print(f"DEBUG: Request data: {request.data}")
        print(f"DEBUG: User: {request.user}")
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.save()
                    response_serializer = OrderSerializer(order, context={'request': request})
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"DEBUG: Exception during order creation: {str(e)}")
                import traceback
                traceback.print_exc()
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            print(f"DEBUG: Serializer validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order and restore inventory
        """
        order = self.get_object()
        
        # Check if order can be cancelled
        if order.order_status in ['delivered', 'out_for_delivery']:
            return Response(
                {"error": f"Cannot cancel an order with status '{order.order_status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Restore inventory for each order item
                for item in order.items.all():
                    listing = item.listing
                    listing.quantity_available += item.quantity
                    listing.save()
                
                # Update order status
                order.order_status = 'cancelled'
                if order.payment_status == 'paid':
                    order.payment_status = 'refunded'  # Will need to integrate with payment system later
                order.save()
                
                serializer = self.get_serializer(order)
                return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing all orders in the system.
    """
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__phone_number']
    ordering_fields = ['created_at', 'total_amount', 'order_status', 'payment_status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Order.objects.select_related('customer').filter(customer__isnull=False)
        
        # Filter by status
        order_status = self.request.query_params.get('order_status', None)
        if order_status:
            queryset = queryset.filter(order_status=order_status)
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status', None)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by customer role
        customer_role = self.request.query_params.get('customer_role', None)
        if customer_role:
            queryset = queryset.filter(customer__user_role=customer_role)
        
        # Filter by date range
        date_range = self.request.query_params.get('date_range', None)
        if date_range:
            now = timezone.now()
            if date_range == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_range == 'week':
                start_date = now - timedelta(days=7)
            elif date_range == 'month':
                start_date = now - timedelta(days=30)
            elif date_range == 'year':
                start_date = now - timedelta(days=365)
            else:
                start_date = None
            
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get order statistics for admin dashboard
        """
        total_orders = Order.objects.count()
        
        # Order status counts
        status_stats = Order.objects.values('order_status').annotate(count=Count('order_status'))
        status_counts = {
            'total': total_orders,
            'pending': 0,
            'confirmed': 0,
            'processing': 0,
            'out_for_delivery': 0,
            'delivered': 0,
            'cancelled': 0
        }
        
        for stat in status_stats:
            if stat['order_status'] in status_counts:
                status_counts[stat['order_status']] = stat['count']
        
        # Payment status counts
        payment_stats = Order.objects.values('payment_status').annotate(count=Count('payment_status'))
        payment_counts = {
            'pending': 0,
            'paid': 0,
            'failed': 0,
            'refunded': 0
        }
        
        for stat in payment_stats:
            if stat['payment_status'] in payment_counts:
                payment_counts[stat['payment_status']] = stat['count']
        
        # Gross Revenue (Total Sales)
        total_gross_revenue = Order.objects.filter(payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Monthly Gross Revenue
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_gross_revenue = Order.objects.filter(
            payment_status='paid',
            created_at__gte=current_month_start
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # Platform Revenue (Net Revenue from Fees)
        # Get fee rates from system settings
        vat_rate = SystemSettings.objects.get_setting('vat_rate', Decimal('0.16'))
        transaction_fee_rate = SystemSettings.objects.get_setting('transaction_fee_rate', Decimal('0.015'))
        platform_fee_rate = SystemSettings.objects.get_setting('platform_fee_rate', Decimal('0.10'))

        # Calculate total fees from all paid and delivered order items
        paid_delivered_items = OrderItem.objects.filter(
            order__payment_status='paid',
            item_status='delivered'
        )

        total_platform_fees = Decimal('0.00')
        total_vat_on_platform_fees = Decimal('0.00')
        total_transaction_fees = Decimal('0.00')
        total_delivery_fees_collected = Decimal('0.00') # Total delivery fees collected from customers

        for item in paid_delivered_items:
            item_gross_revenue = item.total_price
            
            platform_fee = (item_gross_revenue * platform_fee_rate).quantize(Decimal('0.01'))
            vat_on_platform_fee = (platform_fee * vat_rate).quantize(Decimal('0.01'))
            transaction_fee = (item_gross_revenue * transaction_fee_rate).quantize(Decimal('0.01'))
            
            total_platform_fees += platform_fee
            total_vat_on_platform_fees += vat_on_platform_fee
            total_transaction_fees += transaction_fee
        
        # Sum all delivery fees from paid orders (these are passed to riders, not platform revenue)
        total_delivery_fees_collected = Order.objects.filter(payment_status='paid').aggregate(
            total=Sum('delivery_fee')
        )['total'] or Decimal('0.00')

        # Sum of all fees that are platform revenue
        net_platform_revenue = (total_platform_fees + total_vat_on_platform_fees + total_transaction_fees).quantize(Decimal('0.01'))

        # Monthly platform revenue
        monthly_paid_delivered_items = OrderItem.objects.filter(
            order__payment_status='paid',
            item_status='delivered',
            order__created_at__gte=current_month_start
        )

        monthly_platform_fees = Decimal('0.00')
        monthly_vat_on_platform_fees = Decimal('0.00')
        monthly_transaction_fees = Decimal('0.00')
        monthly_delivery_fees_collected = Decimal('0.00')

        for item in monthly_paid_delivered_items:
            item_gross_revenue = item.total_price
            
            platform_fee = (item_gross_revenue * platform_fee_rate).quantize(Decimal('0.01'))
            vat_on_platform_fee = (platform_fee * vat_rate).quantize(Decimal('0.01'))
            transaction_fee = (item_gross_revenue * transaction_fee_rate).quantize(Decimal('0.01'))
            
            monthly_platform_fees += platform_fee
            monthly_vat_on_platform_fees += vat_on_platform_fee
            monthly_transaction_fees += transaction_fee
        
        monthly_delivery_fees_collected = Order.objects.filter(
            payment_status='paid',
            created_at__gte=current_month_start
        ).aggregate(total=Sum('delivery_fee'))['total'] or Decimal('0.00')

        monthly_net_platform_revenue = (monthly_platform_fees + monthly_vat_on_platform_fees + monthly_transaction_fees).quantize(Decimal('0.01'))
        
        return Response({
            'orders': status_counts,
            'payments': payment_counts,
            'gross_revenue': { # Renamed from 'revenue' to 'gross_revenue'
                'total': float(total_gross_revenue),
                'monthly': float(monthly_gross_revenue)
            },
            'platform_revenue': { # New field for platform's net revenue
                'total': float(net_platform_revenue),
                'monthly': float(monthly_net_platform_revenue),
                'total_platform_fees': float(total_platform_fees),
                'total_vat_on_platform_fees': float(total_vat_on_platform_fees),
                'total_transaction_fees': float(total_transaction_fees),
                'monthly_platform_fees': float(monthly_platform_fees),
                'monthly_vat_on_platform_fees': float(monthly_vat_on_platform_fees),
                'monthly_transaction_fees': float(monthly_transaction_fees),
            },
            'delivery_fees': { # New field for delivery fees collected (pass-through)
                'total_collected': float(total_delivery_fees_collected),
                'monthly_collected': float(monthly_delivery_fees_collected)
            }
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export orders to CSV
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Customer', 'Phone', 'Status', 'Payment Status',
            'Total Amount', 'Delivery Fee', 'Created', 'Estimated Delivery'
        ])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                f"{order.customer.first_name} {order.customer.last_name}",
                order.customer.phone_number,
                order.order_status,
                order.payment_status,
                float(order.total_amount),
                float(order.delivery_fee),
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.estimated_delivery_date.strftime('%Y-%m-%d') if order.estimated_delivery_date else ''
            ])
        
        return response

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update order status (admin only)
        """
        order = self.get_object()
        new_status = request.data.get('order_status')
        
        if not new_status:
            return Response(
                {'error': 'order_status is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.order_status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_payment_status(self, request, pk=None):
        """
        Update payment status (admin only)
        """
        order = self.get_object()
        new_status = request.data.get('payment_status')
        
        if not new_status:
            return Response(
                {'error': 'payment_status is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = [choice[0] for choice in Order.PAYMENT_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.payment_status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class FarmerOrderItemViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """
    API endpoint for farmers to view and update their order items
    """
    permission_classes = [IsFarmer]
    
    def get_queryset(self):
        """
        Ensure farmers can only access order items for their listings
        """
        return OrderItem.objects.filter(farmer=self.request.user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action
        """
        if self.action in ['update', 'partial_update']:
            return OrderItemUpdateSerializer
        return OrderItemSerializer
    
    def update(self, request, *args, **kwargs):
        """
        Update order item status
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Ensure the farmer can only update their own items
        if instance.farmer != request.user:
            return Response(
                {"error": "You do not have permission to update this order item."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            
            # Check if all items in the order have been updated to 'packed' status
            # If so, update the order status to 'processing'
            order = instance.order
            all_items = order.items.all()
            all_packed = all(item.item_status == 'packed' for item in all_items)
            
            if all_packed and order.order_status == 'confirmed':
                order.order_status = 'processing'
                order.save()
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending order items for the farmer
        """
        pending_items = self.get_queryset().filter(item_status='pending')
        serializer = self.get_serializer(pending_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def harvested(self, request):
        """
        Get all harvested order items for the farmer
        """
        harvested_items = self.get_queryset().filter(item_status='harvested')
        serializer = self.get_serializer(harvested_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def packed(self, request):
        """
        Get all packed order items for the farmer
        """
        packed_items = self.get_queryset().filter(item_status='packed')
        serializer = self.get_serializer(packed_items, many=True)
        return Response(serializer.data)
