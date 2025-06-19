from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import PaymentMethod, PaymentTransaction
from .serializers import (
    PaymentMethodSerializer, PaymentMethodCreateUpdateSerializer,
    PaymentTransactionSerializer, PaymentTransactionCreateSerializer,
    PaymentCallbackSerializer
)


class IsCustomerUser(permissions.BasePermission):
    """
    Permission that allows access only to customer users
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'customer'


class IsAdminUser(permissions.BasePermission):
    """
    Permission that allows access only to admin users
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'admin'


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment methods
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsCustomerUser]
    
    def get_queryset(self):
        """
        Return only the payment methods belonging to the current user
        """
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentMethodCreateUpdateSerializer
        return PaymentMethodSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Set a payment method as the default for the user
        """
        payment_method = self.get_object()
        
        # Update all payment methods to not be default
        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
        
        # Set this payment method as default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = self.get_serializer(payment_method)
        return Response(serializer.data)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment transactions
    """
    serializer_class = PaymentTransactionSerializer
    
    def get_permissions(self):
        """
        Return different permissions depending on the action
        """
        if self.action == 'callback':
            # Allow unauthenticated access to the callback endpoint
            # In production, this should be secured with API keys or signatures
            return [permissions.AllowAny()]
        elif self.action in ['list', 'retrieve'] and self.request.user.user_role == 'admin':
            return [IsAdminUser()]
        else:
            return [IsCustomerUser()]
    
    def get_queryset(self):
        """
        Return only the payment transactions relevant to the current user
        Admin users can see all transactions
        """
        user = self.request.user
        if user.user_role == 'admin':
            return PaymentTransaction.objects.all()
        return PaymentTransaction.objects.filter(order__customer=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentTransactionCreateSerializer
        elif self.action == 'callback':
            return PaymentCallbackSerializer
        return PaymentTransactionSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def callback(self, request):
        """
        Handle payment callback from payment provider
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.update_transaction(serializer.validated_data)
            response_serializer = PaymentTransactionSerializer(transaction)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def simulate_payment(self, request, pk=None):
        """
        Simulate a successful payment for testing purposes
        """
        payment_transaction = self.get_object()
        
        # Only allow simulating pending transactions
        if payment_transaction.payment_status != 'pending':
            return Response(
                {'error': 'Can only simulate payment for pending transactions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update transaction to completed
        payment_transaction.payment_status = 'completed'
        payment_transaction.payment_date = timezone.now()
        payment_transaction.transaction_code = f'SIM-{timezone.now().timestamp()}'
        payment_transaction.save()
        
        # Update order status
        payment_transaction.update_order_status()
        
        serializer = self.get_serializer(payment_transaction)
        return Response(serializer.data)
