from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admin users to perform any action
    - All other users to only view data
    """
    
    def has_permission(self, request, view):
        # Allow GET, HEAD or OPTIONS requests for anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_authenticated and request.user.user_role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_authenticated and request.user.user_role == 'admin'


class IsFarmerRiderOrAdminForAlerts(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admins to perform all actions
    - Farmers and riders to view alerts relevant to their locations
    """
    
    def has_permission(self, request, view):
        # Require authentication for all requests
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admins can do anything
        if request.user.user_role == 'admin':
            return True
            
        # Farmers and riders can view alerts
        if request.method in permissions.SAFE_METHODS and request.user.user_role in ['farmer', 'rider']:
            return True
        
        # Others can't do anything
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.user_role == 'admin':
            return True
            
        # Farmers and riders can only view alerts for their locations
        if request.method in permissions.SAFE_METHODS and request.user.user_role in ['farmer', 'rider']:
            # For farmers, check if alert location matches any of their farm locations
            if request.user.user_role == 'farmer':
                from farms.models import Farm
                return Farm.objects.filter(farmer=request.user, location=obj.location).exists()
            
            # For riders, check if alert location is in their delivery routes
            if request.user.user_role == 'rider':
                from delivery.models import DeliveryRoute
                # Get all the rider's routes
                routes = DeliveryRoute.objects.filter(rider=request.user)
                # Check if any route includes this location
                for route in routes:
                    if str(obj.location.location_id) in route.route_locations:
                        return True
                return False
        
        # Others can't do anything
        return False
