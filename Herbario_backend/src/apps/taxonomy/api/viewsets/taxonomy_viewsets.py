from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from apps.common.api.viewsets.mixins import EncodedLookupMixin
from apps.common.viewsets.service_viewset import ServiceModelViewSet
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES, CURATOR_WRITE_ROLES, READ_ROLES
from apps.taxonomy.api.serializers import (
    CommonNameSerializer,
    CommonNameWriteSerializer,
    ConservationStatusSerializer,
    ConservationStatusWriteSerializer,
    FamilySerializer,
    FamilyWriteSerializer,
    GenusSerializer,
    GenusWriteSerializer,
    LanguageSerializer,
    SpeciesSerializer,
    SpeciesWriteSerializer,
    StatusSerializer,
    StatusWriteSerializer,
    TranslationSerializer,
    TranslationWriteSerializer,
)
from apps.taxonomy.selectors import (
    list_common_names_for_api,
    list_conservation_statuses_for_api,
    list_families_for_api,
    list_genera_for_api,
    list_languages_for_api,
    list_species_for_api,
    list_statuses_for_api,
    list_translations_for_api,
)
from apps.taxonomy.services import (
    CommonNameService,
    ConservationStatusService,
    FamilyService,
    GenusService,
    SpeciesService,
    StatusService,
    TranslationService,
)

TAXONOMY_ROLES_BY_ACTION = {
    "list": READ_ROLES,
    "retrieve": READ_ROLES,
    "create": CURATOR_WRITE_ROLES,
    "update": CURATOR_WRITE_ROLES,
    "partial_update": CURATOR_WRITE_ROLES,
    "destroy": ADMIN_ONLY_ROLES,
}


@extend_schema(tags=["Taxonomia-Family"])
class FamilyViewSet(ServiceModelViewSet):
    search_fields = ["name", "comment"]
    service_class = FamilyService
    read_serializer_class = FamilySerializer
    write_serializer_class = FamilyWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = TAXONOMY_ROLES_BY_ACTION

    def get_queryset(self):
        return list_families_for_api()


@extend_schema(tags=["Taxonomia-Genus"])
class GenusViewSet(ServiceModelViewSet):
    search_fields = ["name", "family__name", "comment"]
    service_class = GenusService
    read_serializer_class = GenusSerializer
    write_serializer_class = GenusWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = TAXONOMY_ROLES_BY_ACTION

    def get_queryset(self):
        return list_genera_for_api()


@extend_schema(tags=["Taxonomia-Species"])
class SpeciesViewSet(ServiceModelViewSet):
    search_fields = ["name", "genus__name", "genus__family__name", "comment"]
    service_class = SpeciesService
    read_serializer_class = SpeciesSerializer
    write_serializer_class = SpeciesWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = TAXONOMY_ROLES_BY_ACTION

    def get_queryset(self):
        return list_species_for_api()


@extend_schema(tags=["Taxonomia-Language"])
class LanguageViewSet(EncodedLookupMixin, viewsets.ReadOnlyModelViewSet):
    search_fields = ["code", "name", "native_name"]
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = {
        "list": READ_ROLES,
        "retrieve": READ_ROLES,
    }

    def get_queryset(self):
        return list_languages_for_api()


@extend_schema(tags=["Taxonomia"])
class StatusViewSet(ServiceModelViewSet):
    search_fields = ["code", "name", "description"]
    service_class = StatusService
    read_serializer_class = StatusSerializer
    write_serializer_class = StatusWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = TAXONOMY_ROLES_BY_ACTION

    def get_queryset(self):
        return list_statuses_for_api()


@extend_schema(tags=["Taxonomia-CommonName"])
class CommonNameViewSet(ServiceModelViewSet):
    search_fields = [
        "species__name",
        "language__code",
        "language__name",
        "common_name",
        "dialect",
        "region",
    ]
    service_class = CommonNameService
    read_serializer_class = CommonNameSerializer
    write_serializer_class = CommonNameWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = TAXONOMY_ROLES_BY_ACTION

    def get_queryset(self):
        return list_common_names_for_api()


@extend_schema(tags=["Taxonomia-Translation"])
class TranslationViewSet(ServiceModelViewSet):
    search_fields = [
        "common_name__common_name",
        "language__code",
        "language__name",
        "translated_name",
    ]
    service_class = TranslationService
    read_serializer_class = TranslationSerializer
    write_serializer_class = TranslationWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = TAXONOMY_ROLES_BY_ACTION

    def get_queryset(self):
        return list_translations_for_api()


@extend_schema(tags=["Taxonomia-ConservationStatus"])
class ConservationStatusViewSet(ServiceModelViewSet):
    search_fields = ["species__name", "status__code", "status__name"]
    service_class = ConservationStatusService
    read_serializer_class = ConservationStatusSerializer
    write_serializer_class = ConservationStatusWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = TAXONOMY_ROLES_BY_ACTION

    def get_queryset(self):
        return list_conservation_statuses_for_api()
