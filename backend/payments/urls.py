from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentMethodViewSet, PaymentTransactionViewSet, PaymentSessionViewSet

router = DefaultRouter()
router.register('methods', PaymentMethodViewSet, basename='payment-method')
router.register('transactions', PaymentTransactionViewSet, basename='payment-transaction')
router.register('sessions', PaymentSessionViewSet, basename='payment-session')

urlpatterns = [
    path('', include(router.urls)),
]
