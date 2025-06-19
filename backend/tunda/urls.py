from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/farms/', include('farms.urls')),
    path('api/products/', include('products.urls')),
    path('api/carts/', include('carts.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/core/', include('core.urls')),
    path('api/delivery/', include('delivery.urls')),
    
    # New features
    path('api/feedback/', include('feedback.urls')),
    path('api/insights/', include('data_insights.urls')),
    path('api/communication/', include('communication.urls')),
    path('api/finance/', include('finance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)