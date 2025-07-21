from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal
from datetime import date
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

    def create(self, request, *args, **kwargs):
        """Create a new payout request with minimum amount validation"""
        user = request.user
        requested_amount = Decimal(request.data.get('amount', '0.00'))

        min_withdrawal_amount = SystemSettings.objects.get_setting('min_withdrawal_amount', Decimal('200.00'))
        
        if requested_amount < min_withdrawal_amount:
            return Response(
                {"detail": f"Minimum withdrawal amount is KES {min_withdrawal_amount}. Requested amount is too low."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing pending payouts
        has_pending_payout = Payout.objects.filter(
            user=user,
            status='pending'
        ).exists()

        if has_pending_payout:
            return Response(
                {"detail": "You already have a pending payout request. Please wait for it to be processed before requesting another."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch available balance based on user role
        if user.user_role == 'farmer':
            earnings_data = self.farmer_earnings(request).data
        elif user.user_role == 'rider':
            earnings_data = self.rider_earnings(request).data
        else:
            return Response(
                {"detail": "User role not supported for payouts."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        available_balance = earnings_data.get('available_balance', Decimal('0.00'))

        if requested_amount > available_balance:
            return Response(
                {"detail": f"Requested amount KES {requested_amount} exceeds available balance of KES {available_balance}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add user to the request data
        data = request.data.copy()
        data['user'] = user.user_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def rider_earnings(self, request):
        """Get rider earnings statistics"""
        user = request.user
        if user.user_role != 'rider':
            return Response(
                {"detail": "Only riders can access rider earnings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get system settings for withdrawal and clearance
        min_withdrawal_amount = SystemSettings.objects.get_setting('min_withdrawal_amount', Decimal('200.00'))
        clearance_threshold_amount = SystemSettings.objects.get_setting('clearance_threshold_amount', Decimal('20000.00'))

        # Get completed deliveries
        completed_deliveries = Delivery.objects.filter(
            rider=user,
            delivery_status='delivered'
        )
        
        # Calculate total earnings
        total_earnings = completed_deliveries.aggregate(
            Sum('order__delivery_fee')
        )['order__delivery_fee__sum'] or Decimal('0.00')
        
        # Calculate Withholding Tax (WHT)
        wht_rate = SystemSettings.objects.get_setting('wht_rate', Decimal('0.03'))
        wht_threshold = SystemSettings.objects.get_setting('wht_threshold', Decimal('24000.00'))
        
        # Get cumulative gross delivery earnings for the current month
        current_month_start = date.today().replace(day=1)
        monthly_gross_earnings = Delivery.objects.filter(
            rider=user,
            delivery_status='delivered',
            created_at__gte=current_month_start
        ).aggregate(Sum('order__delivery_fee'))['order__delivery_fee__sum'] or Decimal('0.00')
        
        withholding_tax = Decimal('0.00')
        if monthly_gross_earnings > wht_threshold:
            withholding_tax = (total_earnings * wht_rate).quantize(Decimal('0.01')) # Apply WHT to total earnings if threshold met
        
        net_total_earnings = total_earnings - withholding_tax

        # Sum of pending payouts that require clearance
        pending_payouts_for_clearance = Payout.objects.filter(
            user=user,
            status='pending',
            amount__gte=clearance_threshold_amount
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Sum of processed payouts
        processed_payouts = Payout.objects.filter(
            user=user,
            status='processed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Available balance: total net earnings minus pending payouts for clearance and processed payouts
        available_balance = max(Decimal('0.00'), net_total_earnings - pending_payouts_for_clearance - processed_payouts)
        
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
            'pending_balance': pending_payouts_for_clearance, # This now reflects only requested payouts pending clearance
            'available_balance': available_balance,
            'withholding_tax': withholding_tax,
            'min_withdrawal_amount': min_withdrawal_amount,
            'clearance_threshold_amount': clearance_threshold_amount,
            'recent_transactions': [
                {
                    'date': txn.payment_date,
                    'amount': txn.order.delivery_fee,
                    'description': f"Delivery fee for Order #{txn.order.order_number}",
                    'type': 'credit'
                } for txn in recent_transactions
            ]
        })
    
    @action(detail=False, methods=['get'])
    def rider_transactions(self, request):
        """Get rider's recent payment transactions related to deliveries"""
        user = request.user
        if user.user_role != 'rider':
            return Response(
                {"detail": "Only riders can access rider transactions"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get recent transactions related to deliveries assigned to the rider
        recent_transactions = PaymentTransaction.objects.filter(
            order__delivery__rider=user,
            payment_status='completed'
        ).order_by('-payment_date')[:10] # Limit to 10 recent transactions

        # Format transactions for response
        formatted_transactions = [
            {
                'id': txn.transaction_id,
                'date': txn.payment_date,
                'amount': txn.order.delivery_fee, # Assuming delivery_fee is the relevant amount for rider transactions
                'description': f"Delivery fee for Order #{txn.order.order_number}",
                'type': 'credit' # Assuming all these are credits to the rider
            }
            for txn in recent_transactions
        ]
        return Response({
            'results': formatted_transactions,
            'count': len(formatted_transactions)
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
        
        # Get system settings for withdrawal and clearance
        min_withdrawal_amount = SystemSettings.objects.get_setting('min_withdrawal_amount', Decimal('200.00'))
        clearance_threshold_amount = SystemSettings.objects.get_setting('clearance_threshold_amount', Decimal('20000.00'))

        # Get fee rates from system settings
        vat_rate = SystemSettings.objects.get_setting('vat_rate', Decimal('0.16'))
        transaction_fee_rate = SystemSettings.objects.get_setting('transaction_fee_rate', Decimal('0.015'))
        platform_fee_rate = SystemSettings.objects.get_setting('platform_fee_rate', Decimal('0.10'))
        
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
        
        # Calculate fees based on the new model
        platform_fee_amount = (gross_revenue * platform_fee_rate).quantize(Decimal('0.01'))
        vat = (platform_fee_amount * vat_rate).quantize(Decimal('0.01')) # VAT is 16% of the 10% Platform Fee
        transaction_fee = (gross_revenue * transaction_fee_rate).quantize(Decimal('0.01'))
        total_fees = platform_fee_amount + vat + transaction_fee
        
        # Calculate net revenue
        net_revenue = gross_revenue - total_fees
        
        # Sum of pending payouts that require clearance
        pending_payouts_for_clearance = Payout.objects.filter(
            user=user,
            status='pending',
            amount__gte=clearance_threshold_amount
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Sum of processed payouts
        processed_payouts = Payout.objects.filter(
            user=user,
            status='processed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Available balance: total net revenue minus pending payouts for clearance and processed payouts
        available_balance = max(Decimal('0.00'), net_revenue - pending_payouts_for_clearance - processed_payouts)
        
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
                'platform_fee': platform_fee_amount,
                'total_fees': total_fees
            },
            'net_revenue': net_revenue,
            'completed_orders': completed_items.values('order').distinct().count(),
            'pending_orders': OrderItem.objects.filter(
                farmer=user,
                order__payment_status='paid',
                item_status__in=['pending', 'harvested', 'packed']
            ).values('order').distinct().count(),
            'pending_balance': pending_payouts_for_clearance, # This now reflects only requested payouts pending clearance
            'available_balance': available_balance,
            'min_withdrawal_amount': min_withdrawal_amount,
            'clearance_threshold_amount': clearance_threshold_amount,
            'recent_transactions': [
                {
                    'date': txn.payment_date,
                    'amount': sum(item.total_price for item in txn.order.items.filter(farmer=user)),
                    'vat': sum((item.total_price * platform_fee_rate) * vat_rate for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
                    'transaction_fee': sum(item.total_price * transaction_fee_rate for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
                    'platform_fee': sum(item.total_price * platform_fee_rate for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
                    'net_amount': sum(item.total_price - ((item.total_price * platform_fee_rate) + ((item.total_price * platform_fee_rate) * vat_rate) + (item.total_price * transaction_fee_rate)) for item in txn.order.items.filter(farmer=user)).quantize(Decimal('0.01')),
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
