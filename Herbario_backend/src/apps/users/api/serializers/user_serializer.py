from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import serializers

from apps.common.api.ids import (
    EncodedIDField,
    EncodedPrimaryKeyRelatedField,
    encode_external_id,
    model_namespace,
)
from apps.common.api.validators import validate_no_html
from apps.roles.models import Role
from apps.roles.permission_catalog import assignable_permissions
from apps.roles.repositories.membership_repository import (
    get_user_effective_permission_details,
    get_user_permission_details,
    get_user_permission_ids,
    get_user_role_ids,
    get_user_role_names,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    permission_ids = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    effective_permissions = serializers.SerializerMethodField()
    role_ids = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "role_ids",
            "roles",
            "permission_ids",
            "permissions",
            "effective_permissions",
        ]

    def get_role_ids(self, user) -> list[str]:
        return [
            encode_external_id(role_id, namespace=model_namespace(Role))
            for role_id in get_user_role_ids(user_id=user.pk)
        ]

    def get_roles(self, user) -> list[str]:
        return get_user_role_names(user_id=user.pk)

    def get_permission_ids(self, user) -> list[str]:
        return [
            encode_external_id(permission_id, namespace=model_namespace(Permission))
            for permission_id in get_user_permission_ids(user_id=user.pk)
        ]

    def get_permissions(self, user) -> list[str]:
        return [
            f"{perm['app_label']}.{perm['codename']}"
            for perm in get_user_permission_details(user_id=user.pk)
        ]

    def get_effective_permissions(self, user) -> list[str]:
        return [
            f"{perm['app_label']}.{perm['codename']}"
            for perm in get_user_effective_permission_details(user_id=user.pk)
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value: str) -> str:
        validate_no_html(value)
        return value
    role_ids = EncodedPrimaryKeyRelatedField(
        source="roles",
        queryset=Role.objects.all(),
        many=True,
        allow_empty=False,
    )
    permission_ids = EncodedPrimaryKeyRelatedField(
        source="permissions",
        queryset=assignable_permissions(),
        many=True,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "is_active",
            "role_ids",
            "permission_ids",
        ]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "is_active": {"required": False},
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    def validate_password(self, value: str) -> str:
        validate_no_html(value)
        return value
    role_ids = EncodedPrimaryKeyRelatedField(
        source="roles",
        queryset=Role.objects.all(),
        many=True,
        allow_empty=False,
        required=False,
    )
    permission_ids = EncodedPrimaryKeyRelatedField(
        source="permissions",
        queryset=assignable_permissions(),
        many=True,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "is_active",
            "role_ids",
            "permission_ids",
        ]
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False, "allow_blank": True},
            "is_active": {"required": False},
        }
