from __future__ import annotations

from typing import Any

from django.contrib.auth.models import Permission
from django.db import connection, transaction

from apps.common.exceptions import ConflictError, NotFoundError
from apps.roles.models import Role
from apps.roles.repositories.membership_repository import (
    replace_user_permissions,
    replace_user_roles,
)
from apps.users.repositories import UserRepository
from apps.users.selectors import get_user_by_id, list_users_for_api


class UserService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]):
        permission_values = data.pop("permissions", [])
        role_values = data.pop("roles")
        username = data["username"]

        if self.repository.get_by_username(username):
            raise ConflictError(f"El usuario '{username}' ya existe.")

        roles = self._resolve_roles(role_values)
        permissions = self._resolve_permissions(permission_values)
        user = self.repository.create_user(**data)
        self._replace_roles(user=user, roles=roles)
        self._replace_permissions(user=user, permissions=permissions)
        return user

    @transaction.atomic
    def update(self, instance, *, data: dict[str, Any]):
        permission_values = data.pop("permissions", None)
        role_values = data.pop("roles", None)
        password = data.pop("password", None)

        if "username" in data and data["username"] != instance.username:
            if self.repository.username_exists_except(
                username=data["username"],
                user_id=instance.pk,
            ):
                raise ConflictError(f"El usuario '{data['username']}' ya existe.")

        for field, value in data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)

        user = self.repository.save(instance)
        if role_values is not None:
            self._replace_roles(user=user, roles=self._resolve_roles(role_values))
        if permission_values is not None:
            self._replace_permissions(
                user=user,
                permissions=self._resolve_permissions(permission_values),
            )
        return user

    @transaction.atomic
    def soft_delete(self, instance) -> None:
        instance.is_active = False
        self.repository.save(instance)
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE auth_user SET deleted=TRUE WHERE id=%s",
                [instance.pk],
            )

    def _resolve_roles(self, role_values: list[Role | str]) -> list[Role]:
        if all(isinstance(role, Role) for role in role_values):
            return list(role_values)

        role_names = [role for role in role_values if isinstance(role, str)]
        roles = list(Role.objects.filter(name__in=role_names))
        found_names = {role.name for role in roles}
        missing_names = sorted(set(role_names) - found_names)
        if missing_names:
            raise NotFoundError(f"No se encontraron los roles: {', '.join(missing_names)}.")
        return roles

    def _replace_roles(self, *, user, roles: list[Role]) -> None:
        unique_roles = {role.pk: role for role in roles}
        replace_user_roles(user_id=user.pk, role_ids=list(unique_roles.keys()))

    def _resolve_permissions(self, permission_values: list[Permission | str]) -> list[Permission]:
        if all(isinstance(permission, Permission) for permission in permission_values):
            return list(permission_values)

        permission_codenames = [
            permission for permission in permission_values if isinstance(permission, str)
        ]
        permissions = list(Permission.objects.filter(codename__in=permission_codenames))
        found_codenames = {permission.codename for permission in permissions}
        missing_codenames = sorted(set(permission_codenames) - found_codenames)
        if missing_codenames:
            raise NotFoundError(
                f"No se encontraron los permisos: {', '.join(missing_codenames)}."
            )
        return permissions

    def _replace_permissions(self, *, user, permissions: list[Permission]) -> None:
        unique_permissions = {permission.pk: permission for permission in permissions}
        replace_user_permissions(user_id=user.pk, permission_ids=list(unique_permissions.keys()))

    def create_user(self, username: str, email: str, password: str):
        return self.repository.create_user(username=username, email=email, password=password)

    def list_users(self):
        return list_users_for_api()

    def get_user(self, user_id: int):
        return get_user_by_id(user_id)
