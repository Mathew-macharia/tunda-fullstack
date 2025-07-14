from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, MessageViewSet, SupportTicketViewSet, FAQViewSet, AdminFAQViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('messages', MessageViewSet, basename='message')
router.register('support-tickets', SupportTicketViewSet, basename='support-ticket')
router.register('faqs', FAQViewSet, basename='faq')
router.register('admin/faqs', AdminFAQViewSet, basename='admin-faq')

urlpatterns = [
    path('', include(router.urls)),
]
