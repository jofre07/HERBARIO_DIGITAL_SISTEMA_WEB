from __future__ import annotations

from typing import Any

from django.db import connection

from apps.roles.models import Role


def list_roles_for_api() -> Any:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM auth_group WHERE deleted=FALSE ORDER BY name")
        ids = [row[0] for row in cursor.fetchall()]
    return Role.objects.prefetch_related("permissions").filter(pk__in=ids).order_by("name")
