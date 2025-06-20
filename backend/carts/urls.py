from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

router = DefaultRouter()
router.register(r'', CartViewSet, basename='cart')

urlpatterns = [
    path('merge_guest_cart/', CartViewSet.as_view({'post': 'merge_guest_cart'}), name='cart-merge-guest-cart'),
    path('', include(router.urls)),
]
