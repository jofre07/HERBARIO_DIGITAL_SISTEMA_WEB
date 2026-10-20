from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.common.exceptions import ConflictError, NotFoundError
from apps.roles.models import Role
from apps.roles.repositories import RoleRepository
from apps.roles.repositories.membership_repository import replace_role_permissions


class RoleService:
    def __init__(self, repository: RoleRepository | None = None) -> None:
        self.repository = repository or RoleRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Role:
        permissions = data.pop("permissions", [])
        if self.repository.get_by_name(data["name"]):
            raise ConflictError(f"El rol '{data['name']}' ya existe.")
        role = self.repository.create(name=data["name"])
        self._replace_permissions(role, permissions)
        return role

    @transaction.atomic
    def update(self, instance: Role, *, data: dict[str, Any]) -> Role:
        permissions = data.pop("permissions", None)
        if "name" in data and data["name"] != instance.name:
            if self.repository.get_by_name(data["name"]):
                raise ConflictError(f"El rol '{data['name']}' ya existe.")
            instance.name = data["name"]
        role = self.repository.save(instance)
        if permissions is not None:
            self._replace_permissions(role, permissions)
        return role

    @transaction.atomic
    def soft_delete(self, instance: Role) -> None:
        self.repository.soft_delete(instance)

    def _replace_permissions(self, role: Role, permissions) -> None:
        permission_ids = [permission.pk for permission in permissions]
        found_permissions = list(self.repository.list_permissions_by_ids(permission_ids))
        found_ids = {permission.pk for permission in found_permissions}
        missing_ids = sorted(set(permission_ids) - found_ids)
        if missing_ids:
            raise NotFoundError(
                f"No se encontraron los permisos: {', '.join(map(str, missing_ids))}."
            )
        replace_role_permissions(role_id=role.pk, permission_ids=found_ids)
