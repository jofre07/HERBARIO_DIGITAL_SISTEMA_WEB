from __future__ import annotations

from django.contrib.auth.models import Permission
from rest_framework import serializers

from apps.common.api.ids import (
    EncodedIDField,
    EncodedPrimaryKeyRelatedField,
    encode_external_id,
    model_namespace,
)
from apps.common.api.validators import validate_letters_spaces
from apps.roles.models import Role
from apps.roles.permission_catalog import assignable_permissions


class PermissionSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    permission = serializers.SerializerMethodField()
    content_type = serializers.CharField(source="content_type.app_label")

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type", "permission"]

    def get_permission(self, permission: Permission) -> str:
        return f"{permission.content_type.app_label}.{permission.codename}"


class RoleSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    permission_ids = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "name", "permission_ids", "permissions"]

    def get_permission_ids(self, role: Role) -> list[str]:
        return [
            encode_external_id(permission_id, namespace=model_namespace(Permission))
            for permission_id in assignable_permissions(role.permissions.all()).values_list(
                "id", flat=True
            )
        ]

    def get_permissions(self, role: Role) -> list[str]:
        return [
            f"{permission.content_type.app_label}.{permission.codename}"
            for permission in assignable_permissions(
                role.permissions.select_related("content_type")
            )
        ]


class RoleWriteSerializer(serializers.ModelSerializer):
    permission_ids = EncodedPrimaryKeyRelatedField(
        source="permissions",
        queryset=assignable_permissions(),
        many=True,
        required=False,
    )

    class Meta:
        model = Role
        fields = ["name", "permission_ids"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value
