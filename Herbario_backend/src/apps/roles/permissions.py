from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.roles.repositories.membership_repository import user_has_permission, user_has_role
from apps.roles.roles import ROLE_PUBLIC


class HasRolePermission(BasePermission):
    """Authorize model actions using effective permissions, with role fallback."""

    action_permissions = {
        "list": "view",
        "retrieve": "view",
        "create": "add",
        "update": "change",
        "partial_update": "change",
        "destroy": "delete",
    }

    def has_permission(self, request, view) -> bool:
        action = getattr(view, "action", None)
        required_roles = self._get_required_roles(view, action)

        if required_roles is None:
            return True

        if ROLE_PUBLIC in required_roles and request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        required_permission = self._get_required_permission(view, action)
        if required_permission:
            return user_has_permission(user_id=user.pk, permission=required_permission)

        return user_has_role(user_id=user.pk, role_names=list(required_roles))

    def _get_required_permission(self, view, action: str | None) -> str | None:
        permissions_by_action = getattr(view, "required_permissions_by_action", {})
        if action in permissions_by_action:
            return permissions_by_action[action]

        permission_action = self.action_permissions.get(action)
        if not permission_action:
            return None

        serializer_class = view.get_serializer_class()
        model = getattr(getattr(serializer_class, "Meta", None), "model", None)
        if model is None:
            return None
        return f"{model._meta.app_label}.{permission_action}_{model._meta.model_name}"

    def _get_required_roles(self, view, action: str | None):
        roles_by_action = getattr(view, "required_roles_by_action", {})
        if action in roles_by_action:
            return roles_by_action[action]
        return getattr(view, "required_roles", None)
