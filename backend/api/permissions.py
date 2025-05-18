from rest_framework.permissions import BasePermission

from api.models import SystemRole

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == SystemRole.ADMIN
    
class IsRegularUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "user"


#Trata logicamente as permissões que o usuário pode ter no sistema