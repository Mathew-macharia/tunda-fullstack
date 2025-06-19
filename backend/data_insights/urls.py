from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarketPriceViewSet, WeatherAlertViewSet

router = DefaultRouter()
router.register('market-prices', MarketPriceViewSet, basename='market-price')
router.register('weather-alerts', WeatherAlertViewSet, basename='weather-alert')

urlpatterns = [
    path('', include(router.urls)),
]
