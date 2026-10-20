from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from apps.collections_app.api.serializers import CollectionSerializer, CollectionWriteSerializer
from apps.collections_app.selectors import list_collections_for_api
from apps.collections_app.services import CollectionService
from apps.common.viewsets.service_viewset import ServiceModelViewSet
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES, CURATOR_WRITE_ROLES, READ_ROLES
from apps.specimens.publication import request_can_include_unpublished


@extend_schema(tags=["Colecciones"])
class CollectionViewSet(ServiceModelViewSet):
    search_fields = [
        "name",
        "description",
        "collection_type",
        "specimens__catalog_code",
        "specimens__species__name",
    ]
    service_class = CollectionService
    read_serializer_class = CollectionSerializer
    write_serializer_class = CollectionWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = {
        "list": READ_ROLES,
        "retrieve": READ_ROLES,
        "create": CURATOR_WRITE_ROLES,
        "update": CURATOR_WRITE_ROLES,
        "partial_update": CURATOR_WRITE_ROLES,
        "destroy": ADMIN_ONLY_ROLES,
    }

    def get_queryset(self):
        return list_collections_for_api(
            dict(self.request.query_params.items()),
            include_unpublished=request_can_include_unpublished(self.request),
        )
