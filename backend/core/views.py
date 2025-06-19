from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SystemSettings
from .serializers import SystemSettingsSerializer, SystemSettingsCreateUpdateSerializer


class IsAdminUser(permissions.BasePermission):
    """
    Permission that allows access only to admin users
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'admin'


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing system settings
    """
    queryset = SystemSettings.objects.all().order_by('setting_key')
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'setting_key'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SystemSettingsCreateUpdateSerializer
        return SystemSettingsSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def by_key(self, request):
        """
        Get a system setting by its key
        """
        key = request.query_params.get('key')
        if not key:
            return Response({'error': 'Setting key parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        setting = SystemSettings.objects.get_setting(key)
        if setting is None:
            return Response({'error': f'Setting with key {key} not found'}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({'key': key, 'value': setting})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def public(self, request):
        """
        Get public system settings available to all authenticated users
        """
        # Define a list of public setting keys that all users can access
        public_keys = [
            'delivery_fee_per_km',
            'min_order_amount',
            'mpesa_paybill',
            'support_phone'
        ]
        
        settings = SystemSettings.objects.filter(setting_key__in=public_keys)
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)
