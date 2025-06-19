from rest_framework import permissions

class IsAdminOrRecipientReadOnly(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admin users to perform any action
    - Recipient users to only view their own payouts
    """
    
    def has_permission(self, request, view):
        # Require authentication for all requests
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin can do anything
        if request.user.user_role == 'admin':
            return True
        
        # For special admin-only actions, exit early if not admin
        if view.action in ['process', 'fail']:
            return request.user.user_role == 'admin'
        
        # Farmers and riders can only list and retrieve payouts
        if request.method in permissions.SAFE_METHODS and request.user.user_role in ['farmer', 'rider']:
            return True
        
        # Others can't do anything
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.user_role == 'admin':
            return True
        
        # Farmers and riders can only view their own payouts
        if request.method in permissions.SAFE_METHODS and obj.user == request.user:
            return True
        
        # Others can't do anything
        return False
