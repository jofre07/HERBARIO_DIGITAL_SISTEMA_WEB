from __future__ import annotations

from django.contrib.auth.models import Permission
from django.db import connection

from apps.common.repositories.base_repository import BaseRepository
from apps.roles.models import Role


class RoleRepository(BaseRepository[Role]):
    model = Role

    def get_by_name(self, name: str) -> Role | None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM auth_group WHERE name=%s AND deleted=FALSE",
                [name],
            )
            row = cursor.fetchone()
            if row:
                return Role.objects.get(pk=row[0])
            return None

    def create(self, **data) -> Role:
        return Role.objects.create(**data)

    def save(self, instance: Role) -> Role:
        instance.save()
        return instance

    def soft_delete(self, instance: Role) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE auth_group SET deleted=TRUE WHERE id=%s",
                [instance.pk],
            )

    def list_permissions_by_ids(self, permission_ids: list[int]):
        return Permission.objects.filter(pk__in=permission_ids)

    def list_all(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM auth_group WHERE deleted=FALSE ORDER BY name")
            ids = [row[0] for row in cursor.fetchall()]
            return list(Role.objects.filter(pk__in=ids).order_by("name"))
