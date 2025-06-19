from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Location, County, SubCounty, UserAddress
from .serializers import LocationSerializer, CountySerializer, SubCountySerializer, UserAddressSerializer

class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow only owners of a location to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing counties (read-only reference data)
    """
    queryset = County.objects.all().order_by('county_name')
    serializer_class = CountySerializer
    permission_classes = [permissions.AllowAny]  # Public reference data
    
    @action(detail=True, methods=['get'])
    def sub_counties(self, request, pk=None):
        """
        Get all sub-counties for a specific county
        """
        county = self.get_object()
        sub_counties = county.sub_counties.all().order_by('sub_county_name')
        serializer = SubCountySerializer(sub_counties, many=True)
        return Response(serializer.data)

class SubCountyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing sub-counties (read-only reference data)
    """
    queryset = SubCounty.objects.all().select_related('county').order_by('sub_county_name')
    serializer_class = SubCountySerializer
    permission_classes = [permissions.AllowAny]  # Public reference data

    def get_queryset(self):
        """
        Optionally filter sub-counties by county
        """
        queryset = super().get_queryset()
        county_id = self.request.query_params.get('county', None)
        if county_id is not None:
            queryset = queryset.filter(county=county_id)
        return queryset

class UserAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user delivery addresses
    """
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        Return addresses for the current user only
        """
        return UserAddress.objects.filter(user=self.request.user).select_related('county', 'sub_county')
    
    def perform_create(self, serializer):
        """
        Set the current user when creating an address
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """
        Get the user's default address if one exists
        """
        try:
            address = UserAddress.objects.get(user=request.user, is_default=True)
            serializer = self.get_serializer(address)
            return Response(serializer.data)
        except UserAddress.DoesNotExist:
            return Response(
                {"detail": "No default address set."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Set an address as the user's default
        """
        address = self.get_object()
        
        # Unset any previous default address
        UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this address as default
        address.is_default = True
        address.save()
        
        serializer = self.get_serializer(address)
        return Response(serializer.data)

# Keep the old LocationViewSet for backward compatibility
class LocationViewSet(viewsets.ModelViewSet):
    """
    DEPRECATED: Use UserAddressViewSet instead
    ViewSet for viewing and editing user locations.
    """
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        This view returns a list of all locations for the currently authenticated user.
        """
        return Location.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Set the current user when creating a location
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """
        Get the user's default location if one exists.
        """
        try:
            location = Location.objects.get(user=request.user, is_default=True)
            serializer = self.get_serializer(location)
            return Response(serializer.data)
        except Location.DoesNotExist:
            return Response(
                {"detail": "No default location set."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Set a location as the user's default.
        """
        location = self.get_object()
        
        # Unset any previous default location
        Location.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this location as default
        location.is_default = True
        location.save()
        
        serializer = self.get_serializer(location)
        return Response(serializer.data)
