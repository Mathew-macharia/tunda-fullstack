from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileView, ChangePasswordView, create_user_with_email, AdminUserViewSet

# Create a router for admin viewsets
router = DefaultRouter()
router.register(r'admin', AdminUserViewSet, basename='admin-user')

urlpatterns = [
    # Custom user endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('register/', create_user_with_email, name='user-register-custom'),  # Custom registration with email fix
    
    # Admin endpoints
    path('', include(router.urls)),
    
    # Djoser endpoints (authentication, default user management)
    path('', include('djoser.urls')),        # /users/, /users/me/, etc.
    path('', include('djoser.urls.jwt')),    # /jwt/create/, /jwt/refresh/, etc.
]