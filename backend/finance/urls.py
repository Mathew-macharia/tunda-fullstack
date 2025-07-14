from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayoutViewSet

router = DefaultRouter()
router.register('payouts', PayoutViewSet, basename='payout')

urlpatterns = [
    path('', include(router.urls)),
    path('farmer-earnings/', PayoutViewSet.as_view({'get': 'farmer_earnings'}), name='farmer-earnings'),
    path('rider-earnings/', PayoutViewSet.as_view({'get': 'rider_earnings'}), name='rider-earnings'),
    path('rider-transactions/', PayoutViewSet.as_view({'get': 'rider_transactions'}), name='rider-transactions'),
]
