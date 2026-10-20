from __future__ import annotations

from django.contrib.auth.models import Permission
from django.db.models import Q, QuerySet

BUSINESS_PERMISSION_APPS = frozenset(
    {
        "collections_app",
        "collectors",
        "locations",
        "media",
        "specimens",
        "site_content",
        "taxonomy",
        "users",
    }
)

AUTH_PERMISSION_MODELS = frozenset({"group", "user"})


def assignable_permissions(
    queryset: QuerySet[Permission] | None = None,
) -> QuerySet[Permission]:
    """Return only business permissions that may be assigned to application roles."""
    queryset = queryset if queryset is not None else Permission.objects.all()
    return queryset.filter(
        Q(content_type__app_label__in=BUSINESS_PERMISSION_APPS)
        | Q(
            content_type__app_label="auth",
            content_type__model__in=AUTH_PERMISSION_MODELS,
        )
    )
