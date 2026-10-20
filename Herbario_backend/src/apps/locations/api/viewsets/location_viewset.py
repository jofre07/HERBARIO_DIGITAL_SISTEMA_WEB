from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from apps.common.viewsets.service_viewset import ServiceModelViewSet
from apps.locations.api.serializers import (
    ClimateHabitatSerializer,
    ClimateHabitatWriteSerializer,
    ClimateSerializer,
    HabitatSerializer,
    LocationSerializer,
    LocationWriteSerializer,
)
from apps.locations.models import Climate, Habitat
from apps.locations.selectors import list_climate_habitats_for_api, list_locations_for_api
from apps.locations.services import (
    ClimateHabitatService,
    ClimateService,
    HabitatService,
    LocationService,
)
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES, DATA_ENTRY_WRITE_ROLES, READ_ROLES


@extend_schema(tags=["Ubicaciones"])
class LocationViewSet(ServiceModelViewSet):
    search_fields = ["name", "comment", "latitude", "longitude"]
    service_class = LocationService
    read_serializer_class = LocationSerializer
    write_serializer_class = LocationWriteSerializer
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
        return list_locations_for_api()


@extend_schema(tags=["Ubicaciones"])
class ClimateHabitatViewSet(ServiceModelViewSet):
    search_fields = ["location__name", "climate__name", "habitat__name"]
    service_class = ClimateHabitatService
    read_serializer_class = ClimateHabitatSerializer
    write_serializer_class = ClimateHabitatWriteSerializer
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
        return list_climate_habitats_for_api()


class EnvironmentalCatalogViewSet(ServiceModelViewSet):
    search_fields = ["name"]
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = {
        "list": READ_ROLES,
        "retrieve": READ_ROLES,
        "create": DATA_ENTRY_WRITE_ROLES,
        "update": DATA_ENTRY_WRITE_ROLES,
        "partial_update": DATA_ENTRY_WRITE_ROLES,
        "destroy": ADMIN_ONLY_ROLES,
    }


@extend_schema(tags=["Climas"])
class ClimateViewSet(EnvironmentalCatalogViewSet):
    service_class = ClimateService
    read_serializer_class = ClimateSerializer
    write_serializer_class = ClimateSerializer

    def get_queryset(self):
        return Climate.objects.order_by("name")


@extend_schema(tags=["Hábitats"])
class HabitatViewSet(EnvironmentalCatalogViewSet):
    service_class = HabitatService
    read_serializer_class = HabitatSerializer
    write_serializer_class = HabitatSerializer

    def get_queryset(self):
        return Habitat.objects.order_by("name")
