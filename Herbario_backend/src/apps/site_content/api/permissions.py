from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.roles.repositories.membership_repository import user_has_permission


class AboutPageContentPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        action = "view" if request.method in SAFE_METHODS else "change"
        return user_has_permission(
            user_id=user.pk,
            permission=f"site_content.{action}_aboutpagecontent",
        )
