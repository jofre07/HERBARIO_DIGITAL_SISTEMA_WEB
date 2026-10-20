from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.common.api.ids import encode_external_id, model_namespace
from apps.roles.permission_catalog import assignable_permissions
from apps.roles.repositories.membership_repository import (
    get_user_effective_permission_details,
    get_user_role_names,
)

User = get_user_model()


class LoginTokenSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "No existe una cuenta activa con las credenciales ingresadas."
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        roles = get_user_role_names(user_id=user.pk)
        if user.is_superuser:
            permissions = [
                f"{permission.content_type.app_label}.{permission.codename}"
                for permission in assignable_permissions()
                .select_related("content_type")
                .order_by("content_type__app_label", "codename")
            ]
        else:
            permissions = [
                f"{permission['app_label']}.{permission['codename']}"
                for permission in get_user_effective_permission_details(user_id=user.pk)
            ]
        data["user"] = {
            "id": encode_external_id(user.id, namespace=model_namespace(User)),
            "username": user.username,
            "email": user.email,
            "roles": roles,
            "permissions": permissions,
        }
        return data
