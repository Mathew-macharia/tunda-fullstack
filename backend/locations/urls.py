from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, CountyViewSet, SubCountyViewSet, UserAddressViewSet

router = DefaultRouter()
router.register(r'counties', CountyViewSet, basename='county')
router.register(r'sub-counties', SubCountyViewSet, basename='subcounty')
router.register(r'addresses', UserAddressViewSet, basename='useraddress')
router.register(r'', LocationViewSet, basename='location')  # Keep for backward compatibility

urlpatterns = [
    path('', include(router.urls)),
]
