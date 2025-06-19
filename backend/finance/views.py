from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal
from .models import Payout
from .serializers import PayoutSerializer
from .permissions import IsAdminOrRecipientReadOnly
from orders.models import Order, OrderItem
from delivery.models import Delivery
from payments.models import PaymentTransaction
from core.models import SystemSettings

class PayoutViewSet(viewsets.ModelViewSet):
    """ViewSet for the Payout model"""
    serializer_class = PayoutSerializer
    permission_classes = [IsAdminOrRecipientReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user', 'order']
    search_fields = ['transaction_reference', 'notes']
    ordering_fields = ['payout_date', 'processed_date', 'amount']
    ordering = ['-payout_date']
    
    def get_queryset(self):
        """Filter payouts based on user role"""
        user = self.request.user
        
        # Admin can see all payouts
        if user.user_role == 'admin':
            return Payout.objects.all()
        
        # Farmers and riders can only see their own payouts
        return Payout.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def rider_earnings(self, request):
        """Get rider earnings statistics"""
        user = request.user
        if user.user_role != 'rider':
            return Response(
                {"detail": "Only riders can access rider earnings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get completed deliveries
        completed_deliveries = Delivery.objects.filter(
            rider=user,
            delivery_status='delivered'
        )
        
        # Calculate total earnings
        total_earnings = completed_deliveries.aggregate(
            Sum('delivery_fee')
        )['delivery_fee__sum'] or Decimal('0.00')
        
        # Get pending deliveries (delivered but not yet cleared for payout)
        pending_deliveries = completed_deliveries.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=48)
        )
        pending_balance = pending_deliveries.aggregate(
            Sum('delivery_fee')
        )['delivery_fee__sum'] or Decimal('0.00')
        
        # Calculate available balance (completed deliveries older than 48 hours)
        available_deliveries = completed_deliveries.filter(
            created_at__lt=timezone.now() - timezone.timedelta(hours=48)
        )
        available_balance = available_deliveries.aggregate(
            Sum('delivery_fee')
        )['delivery_fee__sum'] or Decimal('0.00')
        
        # Subtract processed payouts
        processed_payouts = Payout.objects.filter(
            user=user,
            status='processed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        available_balance = max(Decimal('0.00'), available_balance - processed_payouts)
        
        # Get recent transactions
        recent_transactions = PaymentTransaction.objects.filter(
            order__delivery__rider=user,
            payment_status='completed'
        ).order_by('-payment_date')[:10]
        
        return Response({
            'total_earnings': total_earnings,
            'completed_deliveries': completed_deliveries.count(),
            'active_deliveries': Delivery.objects.filter(
                rider=user,
                delivery_status__in=['assigned', 'picked_up']
            ).count(),
            'pending_balance': pending_balance,
            'available_balance': available_balance,
            'recent_transactions': [
                {
                    'date': txn.payment_date,
                    'amount': txn.order.delivery.delivery_fee,
                    'description': f"Delivery fee for Order #{txn.order.order_number}",
                    'type': 'credit'
                } for txn in recent_transactions
            ]
        })
    
    @action(detail=False, methods=['get'])
    def farmer_earnings(self, request):
        """Get farmer earnings statistics"""
        user = request.user
        if user.user_role != 'farmer':
            return Response(
                {"detail": "Only farmers can access farmer earnings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get fee rates from system settings
        vat_rate = Decimal('0.16')  # 16% VAT
        transaction_fee_rate = Decimal('0.02')  # 2% transaction fee
        platform_fee_rate = Decimal('0.10')  # 10% platform fee
        
        # Get completed and paid order items
        completed_items = OrderItem.objects.filter(
            farmer=user,
            order__payment_status='paid',
            item_status='delivered'
        )
        
        # Calculate gross revenue
        gross_revenue = completed_items.aggregate(
            Sum('total_price')
        )['total_price__sum'] or Decimal('0.00')
        
        # Calculate fees
        vat = (gross_revenue * vat_rate).quantize(Decimal('0.01'))
        transaction_fee = (gross_revenue * transaction_fee_rate).quantize(Decimal('0.01'))
        platform_fee = (gross_revenue * platform_fee_rate).quantize(Decimal('0.01'))
        total_fees = vat + transaction_fee + platform_fee
        
        # Calculate net revenue
        net_revenue = gross_revenue - total_fees
        
        # Get pending items (delivered but not yet cleared for payout)
        pending_items = completed_items.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=48)
        )
        pending_gross = pending_items.aggregate(
            Sum('total_price')
        )['total_price__sum'] or Decimal('0.00')
        pending_fees = (pending_gross * (vat_rate + transaction_fee_rate + platform_fee_rate)).quantize(Decimal('0.01'))
        pending_balance = pending_gross - pending_fees
        
        # Calculate available balance (completed items older than 48 hours)
        available_items = completed_items.filter(
            created_at__lt=timezone.now() - timezone.timedelta(hours=48)
        )
        available_gross = available_items.aggregate(
            Sum('total_price')
        )['total_price__sum'] or Decimal('0.00')
        available_fees = (available_gross * (vat_rate + transaction_fee_rate + platform_fee_rate)).quantize(Decimal('0.01'))
        available_balance = available_gross - available_fees
        
        # Subtract processed payouts
        processed_payouts = Payout.objects.filter(
            user=user,
            status='processed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        available_balance = max(Decimal('0.00'), available_balance - processed_payouts)
        
        # Get recent transactions
        recent_transactions = PaymentTransaction.objects.filter(
            order__items__farmer=user,
            payment_status='completed'
        ).distinct().order_by('-payment_date')[:10]
        
        return Response({
            'gross_revenue': gross_revenue,
            'fees': {
                'vat': vat,
                'transaction_fee': transaction_fee,
                'platform_fee': platform_fee,
                'total_fees': total_fees
            },
            'net_revenue': net_revenue,
            'completed_orders': completed_items.values('order').distinct().count(),
            'pending_orders': OrderItem.objects.filter(
                farmer=user,
                order__payment_status='paid',
                item_status__in=['pending', 'harvested', 'packed']
            ).values('order').distinct().count(),
            'pending_balance': pending_balance,
            'available_balance': available_balance,
            'recent_transactions': [
                {
                    'date': txn.payment_date,
                    'amount': sum(item.total_price for item in txn.order.items.filter(farmer=user)),
                    'vat': sum(item.total_price * vat_rate for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
                    'transaction_fee': sum(item.total_price * transaction_fee_rate for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
                    'platform_fee': sum(item.total_price * platform_fee_rate for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
                    'net_amount': sum(item.total_price * (1 - (vat_rate + transaction_fee_rate + platform_fee_rate)) for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
                    'description': f"Payment for Order #{txn.order.order_number}",
                    'type': 'credit'
                } for txn in recent_transactions
            ]
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Return payout statistics for the current user"""
        user = request.user
        
        # For admin, get global stats
        if user.user_role == 'admin':
            # Make sure we get Decimal objects for amount fields
            pending_amount = Payout.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            processed_amount = Payout.objects.filter(status='processed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            failed_amount = Payout.objects.filter(status='failed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            stats = {
                'total_pending': Payout.objects.filter(status='pending').count(),
                'total_processed': Payout.objects.filter(status='processed').count(),
                'total_failed': Payout.objects.filter(status='failed').count(),
                'amount_pending': pending_amount,
                'amount_processed': processed_amount,
                'amount_failed': failed_amount,
            }
        else:
            # For farmers and riders, get personal stats
            pending_amount = Payout.objects.filter(user=user, status='pending').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            processed_amount = Payout.objects.filter(user=user, status='processed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            failed_amount = Payout.objects.filter(user=user, status='failed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            stats = {
                'total_pending': Payout.objects.filter(user=user, status='pending').count(),
                'total_processed': Payout.objects.filter(user=user, status='processed').count(),
                'total_failed': Payout.objects.filter(user=user, status='failed').count(),
                'amount_pending': pending_amount,
                'amount_processed': processed_amount,
                'amount_failed': failed_amount,
            }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a pending payout"""
        # Check if user is admin
        if request.user.user_role != 'admin':
            return Response({"detail": "Only admin users can process payouts"}, 
                            status=status.HTTP_403_FORBIDDEN)
        payout = self.get_object()
        
        if payout.status != 'pending':
            return Response(
                {"detail": f"Cannot process a payout with status '{payout.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction_reference = request.data.get('transaction_reference', None)
        if not transaction_reference:
            return Response(
                {"detail": "Transaction reference is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payout.status = 'processed'
        payout.transaction_reference = transaction_reference
        payout.processed_date = timezone.now()
        payout.save()
        
        serializer = self.get_serializer(payout)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """Mark a pending payout as failed"""
        # Check if user is admin
        if request.user.user_role != 'admin':
            return Response({"detail": "Only admin users can mark payouts as failed"}, 
                            status=status.HTTP_403_FORBIDDEN)
        payout = self.get_object()
        
        if payout.status != 'pending':
            return Response(
                {"detail": f"Cannot mark a payout with status '{payout.status}' as failed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = request.data.get('notes', None)
        if not notes:
            return Response(
                {"detail": "Notes explaining the failure reason are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payout.status = 'failed'
        payout.notes = notes
        payout.save()
        
        serializer = self.get_serializer(payout)
        return Response(serializer.data)
