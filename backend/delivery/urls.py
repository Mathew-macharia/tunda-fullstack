from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VehicleViewSet, DeliveryViewSet, DeliveryRouteViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
router.register(r'routes', DeliveryRouteViewSet, basename='delivery-route')

urlpatterns = [
    path('', include(router.urls)),
]
