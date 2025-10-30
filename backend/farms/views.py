from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Farm
from .serializers import FarmSerializer

class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow users with farmer role to create farms.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request for list/detail views
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to farmers
        return request.user.is_authenticated and request.user.user_role == 'farmer'

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow farm owners to view or edit their farms.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the farm
        return obj.farmer == request.user

class FarmViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing farms.
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmer]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['farm_name', 'farm_description']
    ordering_fields = ['farm_name', 'created_at', 'total_acreage']
    ordering = ['-created_at']  # Default ordering
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            # For update and delete actions, add IsOwner permission
            permission_classes = [permissions.IsAuthenticated, IsFarmer, IsOwner]
        elif self.action == 'list':
            # Allow any user (authenticated or not) to view the list of farms
            permission_classes = [permissions.AllowAny]
        else:
            # For other actions (like create, retrieve), require authentication and farmer role
            permission_classes = [permissions.IsAuthenticated, IsFarmer]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        This view returns a list of all farms for the currently authenticated user
        if they are a farmer, or an empty queryset otherwise.
        
        For the 'list' action, it returns all farms for any user (authenticated or not).
        """
        user = self.request.user
        
        # If the action is 'list', return all farms for any user
        if self.action == 'list':
            return Farm.objects.all()

        # If user is an admin, return all farms for other actions
        if user.is_authenticated and user.user_role == 'admin':
            return Farm.objects.all()
        
        # If user is a farmer, return their farms for other actions
        elif user.is_authenticated and user.user_role == 'farmer':
            queryset = Farm.objects.filter(farmer=user)
            
            # Filter by location_id if provided
            location_id = self.request.query_params.get('location_id', None)
            if location_id is not None:
                queryset = queryset.filter(location_id=location_id)
                
            return queryset
            
        # Otherwise return empty queryset
        return Farm.objects.none()
    
    def create(self, request, *args, **kwargs):
        # Ensure user is a farmer
        if request.user.user_role != 'farmer':
            return Response(
                {"detail": "Only farmers can create farms."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def organic(self, request):
        """
        Filter farms that are certified organic.
        """
        user = request.user
        
        if user.user_role == 'farmer':
            # Farmers can only see their own organic farms
            queryset = Farm.objects.filter(farmer=user, is_certified_organic=True)
        elif user.user_role == 'admin':
            # Admins can see all organic farms
            queryset = Farm.objects.filter(is_certified_organic=True)
        else:
            queryset = Farm.objects.none()
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_weather_zone(self, request):
        """
        Filter farms by weather zone.
        """
        user = request.user
        weather_zone = request.query_params.get('zone', None)
        
        if not weather_zone:
            return Response(
                {"detail": "Weather zone parameter 'zone' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if user.user_role == 'farmer':
            # Farmers can only see their own farms in the specified weather zone
            queryset = Farm.objects.filter(farmer=user, weather_zone=weather_zone)
        elif user.user_role == 'admin':
            # Admins can see all farms in the specified weather zone
            queryset = Farm.objects.filter(weather_zone=weather_zone)
        else:
            queryset = Farm.objects.none()
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
