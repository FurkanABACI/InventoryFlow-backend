from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.choices import UserRole


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None

    if user.is_superuser:
        return UserRole.ADMIN

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    if user.is_staff:
        return UserRole.OPERATIONS

    return UserRole.DEPARTMENT


def get_user_department(user):
    profile = getattr(user, "profile", None)
    return profile.department if profile else ""


def can_manage_inventory(user):
    return get_user_role(user) in (UserRole.ADMIN, UserRole.OPERATIONS)


class IsInventoryManager(BasePermission):
    message = "Bu islem icin admin veya idari isler yetkisi gerekir."

    def has_permission(self, request, view):
        return can_manage_inventory(request.user)


class IsInventoryManagerOrReadOnly(BasePermission):
    message = "Bu islem icin admin veya idari isler yetkisi gerekir."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return can_manage_inventory(request.user)


class IsAdminOrReadOnly(BasePermission):
    message = "Bu islem icin admin veya idari isler yetkisi gerekir."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return can_manage_inventory(request.user)
