from rest_framework import permissions


class IsBusinessOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.can_manage_business


class IsBusinessMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.business is not None


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_owner


class BusinessFilter:
    def filter_by_business(self, queryset, request):
        if not hasattr(request, "business") or request.business is None:
            return queryset.none()
        return queryset.filter(business=request.business)
