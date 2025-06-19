from django.contrib import admin
from .models import Notification, Message, SupportTicket

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'notification_id', 'user', 'notification_type',
        'title', 'is_read', 'send_sms', 'created_at'
    )
    list_filter = ('notification_type', 'is_read', 'send_sms', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('notification_id', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'message_id', 'sender', 'recipient',
        'message_type', 'is_read', 'created_at'
    )
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('message_text', 'sender__username', 'recipient__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('message_id', 'created_at')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_number', 'user', 'subject', 'category',
        'priority', 'status', 'assigned_to', 'created_at'
    )
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('ticket_number', 'subject', 'description', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('ticket_id', 'ticket_number', 'created_at', 'resolved_at')
