from __future__ import annotations

from django.contrib.auth.models import Permission
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from apps.common.viewsets.service_viewset import ServiceModelViewSet
from apps.roles.api.serializers import PermissionSerializer, RoleSerializer, RoleWriteSerializer
from apps.roles.permission_catalog import assignable_permissions
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES
from apps.roles.selectors import list_roles_for_api
from apps.roles.services import RoleService


@extend_schema(tags=["Roles"])
class RoleViewSet(ServiceModelViewSet):
    search_fields = ["name", "permissions__name", "permissions__codename"]
    service_class = RoleService
    read_serializer_class = RoleSerializer
    write_serializer_class = RoleWriteSerializer
    permission_classes = [HasRolePermission]
    required_roles = ADMIN_ONLY_ROLES

    def get_queryset(self):
        return list_roles_for_api()


@extend_schema(tags=["Permisos"])
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    search_fields = ["name", "codename", "content_type__app_label"]
    serializer_class = PermissionSerializer
    permission_classes = [HasRolePermission]
    required_roles = ADMIN_ONLY_ROLES
    required_permissions_by_action = {
        "list": "auth.view_group",
        "retrieve": "auth.view_group",
    }
    pagination_class = None

    def get_queryset(self):
        return assignable_permissions(Permission.objects.select_related("content_type")).order_by(
            "content_type__app_label",
            "codename",
        )
