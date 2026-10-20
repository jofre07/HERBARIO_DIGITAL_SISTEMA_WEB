from __future__ import annotations

from apps.roles.repositories.membership_repository import user_has_permission


def request_can_include_unpublished(request) -> bool:
    requested = str(request.query_params.get("include_unpublished", "")).lower()
    if requested not in {"1", "true", "yes"}:
        return False
    user = request.user
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user_has_permission(user_id=user.pk, permission="specimens.view_specimen")
