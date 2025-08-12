from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, ProductViewSet, ProductListingViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'listings', ProductListingViewSet, basename='product-listing')
router.register(r'items', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
