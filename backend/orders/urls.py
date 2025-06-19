from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, FarmerOrderItemViewSet, AdminOrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'admin-orders', AdminOrderViewSet, basename='admin-order')
router.register(r'farmer-order-items', FarmerOrderItemViewSet, basename='farmer-order-item')

urlpatterns = [
    path('', include(router.urls)),
]
