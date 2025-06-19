from rest_framework import permissions

class IsReviewerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow:
    - Anyone to read reviews
    - Owners to update/delete their own reviews
    - Admins to moderate reviews (update visibility)
    """
    
    def has_permission(self, request, view):
        # Allow GET, HEAD or OPTIONS requests for anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # POST requests require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD or OPTIONS requests for anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow reviewers to update/delete their own reviews
        if obj.reviewer == request.user:
            return True
        
        # Allow admins to update (for moderation purposes)
        if request.user.user_role == 'admin':
            # If admin is only updating visibility, allow it
            if set(request.data.keys()) <= {'is_visible'}:
                return True
        
        # Deny permission otherwise
        return False
