from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.collections_app.models import Collection
from apps.collectors.models import Collector
from apps.common.api.ids import decode_query_id
from apps.common.viewsets.service_viewset import ServiceModelViewSet
from apps.locations.models import Climate, Habitat, Location
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES, DATA_ENTRY_WRITE_ROLES, READ_ROLES
from apps.specimens.api.serializers import (
    AdminSpecimenSerializer,
    SpecimenListSerializer,
    SpecimenLocationOptionSerializer,
    SpecimenNamedOptionSerializer,
    SpecimenWriteSerializer,
)
from apps.specimens.publication import request_can_include_unpublished
from apps.specimens.selectors import search_specimens_for_api
from apps.specimens.services import SpecimenService
from apps.taxonomy.models import Family, Genus, Species


@extend_schema(tags=["Especimenes"])
class SpecimenViewSet(ServiceModelViewSet):
    search_fields = [
        "catalog_code",
        "collection_number",
        "morphological_description",
        "species__name",
        "species__genus__name",
        "species__genus__family__name",
        "species__common_names__common_name",
        "collector__name",
        "location_links__location__name",
        "location_links__climate__name",
        "location_links__habitat__name",
    ]
    service_class = SpecimenService
    read_serializer_class = AdminSpecimenSerializer
    write_serializer_class = SpecimenWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = {
        "list": READ_ROLES,
        "retrieve": READ_ROLES,
        "create": DATA_ENTRY_WRITE_ROLES,
        "update": DATA_ENTRY_WRITE_ROLES,
        "partial_update": DATA_ENTRY_WRITE_ROLES,
        "destroy": ADMIN_ONLY_ROLES,
        "form_options": READ_ROLES,
    }
    required_permissions_by_action = {
        "form_options": "specimens.view_specimen",
    }

    def get_serializer_class(self):
        if self.action == "list" and self.request.query_params.get("view") == "summary":
            return SpecimenListSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        params = dict(self.request.query_params.items())
        for key, model in (
            ("family", Family),
            ("genus", Genus),
            ("species", Species),
            ("collector", Collector),
            ("location", Location),
            ("collection", Collection),
        ):
            decoded = decode_query_id(params, f"{key}_id", model)
            if decoded is None:
                decoded = decode_query_id(params, key, model)
            if decoded is not None:
                params[key] = decoded
        queryset = search_specimens_for_api(
            params,
            include_unpublished=request_can_include_unpublished(self.request),
        )
        if self.action == "list" and self.request.query_params.get("view") == "summary":
            return (
                queryset.select_related(None)
                .select_related("species__genus__family", "collector")
                .prefetch_related(None)
                .prefetch_related("location_links__location")
            )
        return queryset

    @action(detail=False, methods=["get"], url_path="form-options")
    def form_options(self, request: Request) -> Response:
        species = Species.objects.order_by("name").only("id", "name")
        collectors = Collector.objects.order_by("name").only("id", "name")
        locations = Location.objects.order_by("name").only(
            "id", "name", "latitude", "longitude", "comment"
        )
        climates = Climate.objects.order_by("name").only("id", "name")
        habitats = Habitat.objects.order_by("name").only("id", "name")
        return Response(
            {
                "species": SpecimenNamedOptionSerializer(species, many=True).data,
                "collectors": SpecimenNamedOptionSerializer(collectors, many=True).data,
                "locations": SpecimenLocationOptionSerializer(locations, many=True).data,
                "climates": SpecimenNamedOptionSerializer(climates, many=True).data,
                "habitats": SpecimenNamedOptionSerializer(habitats, many=True).data,
            }
        )
