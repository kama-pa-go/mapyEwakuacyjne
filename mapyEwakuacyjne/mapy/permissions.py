from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Uprawnienie zezwalające tylko właścicielom obiektu na edytowanie.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        
        if hasattr(obj, 'uzytkownik'):
            return obj.uzytkownik == request.user
        elif hasattr(obj, 'trasa'):
            return obj.trasa.uzytkownik == request.user
        return False