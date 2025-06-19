from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, MessageViewSet, SupportTicketViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('messages', MessageViewSet, basename='message')
router.register('support-tickets', SupportTicketViewSet, basename='support-ticket')

urlpatterns = [
    path('', include(router.urls)),
]
