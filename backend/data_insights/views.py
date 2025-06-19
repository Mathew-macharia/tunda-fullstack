from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MarketPrice, WeatherAlert
from .serializers import MarketPriceSerializer, WeatherAlertSerializer
from .permissions import IsAdminOrReadOnly, IsFarmerRiderOrAdminForAlerts
from datetime import date, timedelta

class MarketPriceViewSet(viewsets.ModelViewSet):
    """ViewSet for the MarketPrice model"""
    queryset = MarketPrice.objects.all()
    serializer_class = MarketPriceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'location', 'price_date', 'data_source']
    search_fields = ['product__name', 'location__name']
    ordering_fields = ['price_date', 'average_price', 'created_at']
    ordering = ['-price_date']
    
    @action(detail=False, methods=['get'])
    def product_history(self, request):
        """Return historical prices for a specific product"""
        product_id = request.query_params.get('product_id', None)
        days = request.query_params.get('days', 30)  # Default to 30 days
        
        # Support for backward compatibility
        period = request.query_params.get('period', None)
        if period:
            days = period
        
        try:
            days = int(days)
        except ValueError:
            return Response(
                {"detail": "Days parameter must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if product_id is None:
            return Response(
                {"detail": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate the date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        prices = MarketPrice.objects.filter(
            product_id=product_id,
            price_date__gte=start_date,
            price_date__lte=end_date
        ).order_by('price_date')
        
        serializer = self.get_serializer(prices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def product_history(self, request, pk=None):
        """Return historical prices for a specific product (detail route)"""
        product_id = pk
        days = request.query_params.get('period', 30)  # Default to 30 days
        
        try:
            days = int(days)
        except ValueError:
            return Response(
                {"detail": "Period parameter must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Calculate the date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        prices = MarketPrice.objects.filter(
            product_id=product_id,
            price_date__gte=start_date,
            price_date__lte=end_date
        ).order_by('price_date')
        
        serializer = self.get_serializer(prices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def location_trends(self, request):
        """Return price trends for a specific location"""
        location_id = request.query_params.get('location_id', None)
        days = request.query_params.get('days', 30)  # Default to 30 days
        
        try:
            days = int(days)
        except ValueError:
            return Response(
                {"detail": "Days parameter must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if location_id is None:
            return Response(
                {"detail": "Location ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate the date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        prices = MarketPrice.objects.filter(
            location_id=location_id,
            price_date__gte=start_date,
            price_date__lte=end_date
        ).order_by('price_date')
        
        serializer = self.get_serializer(prices, many=True)
        return Response(serializer.data)


class WeatherAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for the WeatherAlert model"""
    queryset = WeatherAlert.objects.all()
    serializer_class = WeatherAlertSerializer
    permission_classes = [IsFarmerRiderOrAdminForAlerts]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'alert_type', 'severity', 'is_active', 'start_date']
    search_fields = ['alert_message', 'location__name']
    ordering_fields = ['start_date', 'created_at', 'severity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter alerts based on user role"""
        queryset = WeatherAlert.objects.all()
        user = self.request.user
        
        # Admin can see all alerts
        if user.user_role == 'admin':
            return queryset
        
        # Farmers can only see alerts for their farm locations
        if user.user_role == 'farmer':
            from farms.models import Farm
            farm_locations = Farm.objects.filter(farmer=user).values_list('location', flat=True)
            return queryset.filter(location__in=farm_locations, is_active=True)
        
        # Riders can only see alerts for locations in their delivery routes
        if user.user_role == 'rider':
            from delivery.models import DeliveryRoute
            routes = DeliveryRoute.objects.filter(rider=user)
            # Get all unique location IDs from all routes
            location_ids = set()
            for route in routes:
                location_ids.update(route.route_locations)
            return queryset.filter(location__location_id__in=location_ids, is_active=True)
        
        return WeatherAlert.objects.none()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Return all active weather alerts"""
        alerts = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Return all urgent weather alerts"""
        alerts = self.get_queryset().filter(severity='urgent', is_active=True)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
