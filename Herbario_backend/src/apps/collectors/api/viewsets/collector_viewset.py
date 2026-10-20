from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from apps.collectors.api.serializers import CollectorSerializer, CollectorWriteSerializer
from apps.collectors.selectors import list_collectors_for_api
from apps.collectors.services import CollectorService
from apps.common.viewsets.service_viewset import ServiceModelViewSet
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES, DATA_ENTRY_WRITE_ROLES, READ_ROLES


@extend_schema(tags=["Colectores"])
class CollectorViewSet(ServiceModelViewSet):
    search_fields = ["name", "comment"]
    service_class = CollectorService
    read_serializer_class = CollectorSerializer
    write_serializer_class = CollectorWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = {
        "list": READ_ROLES,
        "retrieve": READ_ROLES,
        "create": DATA_ENTRY_WRITE_ROLES,
        "update": DATA_ENTRY_WRITE_ROLES,
        "partial_update": DATA_ENTRY_WRITE_ROLES,
        "destroy": ADMIN_ONLY_ROLES,
    }

    def get_queryset(self):
        return list_collectors_for_api()
