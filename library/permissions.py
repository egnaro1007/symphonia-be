from rest_framework.permissions import BasePermission, SAFE_METHODS
from library.models import Playlist

class CanAcessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Playlist):
            if obj.owner == request.user:
                return True
            
            if request.method in SAFE_METHODS:
                return obj.is_accessible_by(request.user)
            
            return False
        
        return super().has_object_permission(request, view, obj)
    