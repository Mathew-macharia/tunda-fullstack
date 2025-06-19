from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow:
    - Users to manage their own resources
    - Admins to manage all resources
    """
    
    def has_permission(self, request, view):
        # Require authentication for all requests
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow admin to do anything
        if request.user.user_role == 'admin':
            return True
            
        # Allow users to view and modify their own resources
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'recipient'):
            return obj.recipient == request.user or obj.sender == request.user
        
        # Deny permission otherwise
        return False


class IsRecipientOrSenderOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow:
    - Message senders to view their sent messages
    - Message recipients to view and mark messages as read
    - Admins to do anything
    """
    
    def has_permission(self, request, view):
        # Require authentication for all requests
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow admin to do anything
        if request.user.user_role == 'admin':
            return True
            
        # Both sender and recipient can view the message
        if request.method in permissions.SAFE_METHODS:
            return obj.sender == request.user or obj.recipient == request.user
        
        # Only recipient can mark as read (PATCH)
        if request.method == 'PATCH' and 'is_read' in request.data:
            return obj.recipient == request.user
        
        # Only sender can update or delete their message if it hasn't been read
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user and not obj.is_read
        
        return False


class CanManageTickets(permissions.BasePermission):
    """
    Custom permission to allow:
    - Users to create tickets and view their own tickets
    - Admins to manage all tickets
    """
    
    def has_permission(self, request, view):
        # Require authentication for all requests
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Anyone can create a new ticket
        if request.method == 'POST':
            return True
        
        # Admins can list all tickets
        if request.method == 'GET' and view.action == 'list' and request.user.user_role == 'admin':
            return True
        
        # Users can only list their own tickets (filtered in view)
        if request.method == 'GET' and view.action == 'list':
            return True
        
        # Detail view permissions are handled by has_object_permission
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.user_role == 'admin':
            return True
        
        # Users can only view their own tickets
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user
        
        # Users can update their own tickets, but only certain fields
        if request.method in ['PUT', 'PATCH']:
            if obj.user == request.user:
                # Only allow updates to certain fields for non-admin users
                if set(request.data.keys()).issubset({'subject', 'description', 'category'}):
                    # Can't update once ticket is resolved or closed
                    return obj.status not in ['resolved', 'closed']
                return False
            return False
        
        # Only admin can delete tickets
        if request.method == 'DELETE':
            return False
        
        return False
