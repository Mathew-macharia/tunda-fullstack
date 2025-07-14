from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Notification, Message, SupportTicket, FAQ
from .serializers import (
    NotificationSerializer, MessageSerializer, 
    SupportTicketSerializer, AdminTicketUpdateSerializer, FAQSerializer
)
from .permissions import IsOwnerOrAdmin, IsRecipientOrSenderOrAdmin, CanManageTickets

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for the Notification model"""
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter notifications based on user role"""
        user = self.request.user
        
        # Admin can see all notifications if requested
        if user.user_role == 'admin' and self.request.query_params.get('all', '').lower() == 'true':
            return Notification.objects.all()
        
        # Otherwise, users can only see their own notifications
        return Notification.objects.filter(user=user)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def bulk_create(self, request):
        """Create notifications for multiple users at once"""
        user_ids = request.data.get('user_ids', [])
        notification_data = request.data.get('notification_data', {})
        
        if not user_ids or not notification_data:
            return Response(
                {"detail": "Both user_ids and notification_data are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_notifications = []
        for user_id in user_ids:
            notification = Notification.objects.create(
                user_id=user_id,
                notification_type=notification_data.get('notification_type'),
                title=notification_data.get('title'),
                message=notification_data.get('message'),
                send_sms=notification_data.get('send_sms', False),
                related_id=notification_data.get('related_id')
            )
            created_notifications.append(notification)
        
        serializer = self.get_serializer(created_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for the current user"""
        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        
        return Response({"detail": f"{count} notifications marked as read"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for the Message model"""
    serializer_class = MessageSerializer
    permission_classes = [IsRecipientOrSenderOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sender', 'recipient', 'order', 'is_read', 'message_type']
    search_fields = ['message_text']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        """Filter messages based on user role"""
        user = self.request.user
        
        # Admin can see all messages if requested
        if user.user_role == 'admin' and self.request.query_params.get('all', '').lower() == 'true':
            return Message.objects.all()
        
        # Otherwise, users can only see messages they sent or received
        return Message.objects.filter(sender=user) | Message.objects.filter(recipient=user)
    
    @action(detail=False, methods=['get'])
    def inbox(self, request):
        """Return all messages received by the current user"""
        messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Return all messages sent by the current user"""
        messages = Message.objects.filter(sender=request.user).order_by('-created_at')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Return all messages between the current user and another user"""
        other_user_id = request.query_params.get('user_id', None)
        order_id = request.query_params.get('order_id', None)
        
        if not other_user_id:
            return Response(
                {"detail": "User ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get messages between the two users
        queryset = Message.objects.filter(
            (models.Q(sender=request.user) & models.Q(recipient_id=other_user_id)) |
            (models.Q(sender_id=other_user_id) & models.Q(recipient=request.user))
        )
        
        # Filter by order if specified
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        messages = queryset.order_by('created_at')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific message as read"""
        message = self.get_object()
        
        # Only the recipient can mark a message as read
        if message.recipient != request.user:
            return Response(
                {"detail": "You can only mark messages you received as read"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_read = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)


class SupportTicketViewSet(viewsets.ModelViewSet):
    """ViewSet for the SupportTicket model"""
    permission_classes = [CanManageTickets]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'assigned_to']
    search_fields = ['ticket_number', 'subject', 'description']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action and user role"""
        user = self.request.user
        
        # For admin updates, use simplified serializer
        if self.action in ['update', 'partial_update'] and user.user_role == 'admin':
            return AdminTicketUpdateSerializer
        
        return SupportTicketSerializer
    
    def get_queryset(self):
        """Filter tickets based on user role"""
        user = self.request.user
        
        # Admin can see all tickets
        if user.user_role == 'admin':
            return SupportTicket.objects.all()
        
        # Users can only see their own tickets
        return SupportTicket.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Set the user field to the authenticated user when creating a ticket"""
        user = self.request.user
        
        # For non-admin users, always set the user to the authenticated user
        if user.user_role != 'admin':
            serializer.save(user=user)
        else:
            # For admin users, use the user from serializer or default to themselves
            serializer.save()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def unassigned(self, request):
        """Return all unassigned tickets"""
        tickets = SupportTicket.objects.filter(assigned_to=None, status='open')
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def assigned_to_me(self, request):
        """Return all tickets assigned to the current admin"""
        tickets = SupportTicket.objects.filter(assigned_to=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign a ticket to an admin"""
        # Check if user is admin
        if request.user.user_role != 'admin':
            return Response({"detail": "Only admin users can assign tickets"}, 
                            status=status.HTTP_403_FORBIDDEN)
        ticket = self.get_object()
        # Accept either 'admin_id' or 'assigned_to' for backward compatibility
        admin_id = request.data.get('admin_id', request.data.get('assigned_to', None))
        
        if not admin_id:
            return Response(
                {"detail": "Admin ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the assigned user is an admin
        from users.models import User
        try:
            admin = User.objects.get(user_id=admin_id, user_role='admin')
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid admin ID or user is not an admin"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.assigned_to = admin
        if ticket.status == 'open':
            ticket.status = 'in_progress'
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a ticket as resolved"""
        # Check if user is admin
        if request.user.user_role != 'admin':
            return Response({"detail": "Only admin users can resolve tickets"}, 
                            status=status.HTTP_403_FORBIDDEN)
        ticket = self.get_object()
        resolution_notes = request.data.get('resolution_notes', None)
        
        if not resolution_notes:
            return Response(
                {"detail": "Resolution notes are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = 'resolved'
        ticket.resolution_notes = resolution_notes
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the FAQ model - read-only for regular users"""
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_role', 'is_active']
    search_fields = ['question', 'answer']
    ordering_fields = ['order_index', 'created_at']
    ordering = ['order_index', 'created_at']
    
    def get_queryset(self):
        """Filter FAQs based on user role and active status"""
        user = self.request.user
        queryset = FAQ.objects.filter(is_active=True)
        
        # Filter by target role
        if user.user_role in ['customer', 'farmer', 'rider']:
            queryset = queryset.filter(target_role__in=[user.user_role, 'all'])
        
        return queryset


class AdminFAQViewSet(viewsets.ModelViewSet):
    """ViewSet for FAQ management by admins"""
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FAQ.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_role', 'is_active']
    search_fields = ['question', 'answer']
    ordering_fields = ['order_index', 'created_at']
    ordering = ['order_index', 'created_at']
