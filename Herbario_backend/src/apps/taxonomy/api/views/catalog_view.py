from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.common.api.ids import InvalidExternalID, decode_external_id, decode_query_id, model_namespace
from apps.common.api.viewsets.mixins import EncodedLookupMixin
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import READ_ROLES
from apps.taxonomy.api.serializers import SpeciesCatalogDetailSerializer, SpeciesCatalogSerializer
from apps.taxonomy.models import Family, Genus, Species
from apps.taxonomy.selectors import list_species_catalog_for_api
from apps.media.api.serializers import HerbariumImageSerializer
from apps.media.selectors import list_media_for_api


@extend_schema(tags=["Taxonomia"])
class SpeciesCatalogView(ListAPIView):
    serializer_class = SpeciesCatalogSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles = READ_ROLES

    def get_queryset(self):
        params = dict(self.request.query_params.items())
        for key, model in (("family", Family), ("genus", Genus), ("species", Species)):
            decoded = decode_query_id(params, f"{key}_id", model)
            if decoded is None:
                decoded = decode_query_id(params, key, model)
            if decoded is not None:
                params[key] = decoded
        return list_species_catalog_for_api(params)


@extend_schema(tags=["Taxonomia"])
class PublicSpeciesCatalogDetailView(EncodedLookupMixin, RetrieveAPIView):
    serializer_class = SpeciesCatalogDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return list_species_catalog_for_api()


@extend_schema(tags=["Imagenes"])
class PublicSpeciesImagesView(ListAPIView):
    serializer_class = HerbariumImageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        try:
            species_id = decode_external_id(
                self.kwargs["pk"],
                namespace=model_namespace(Species),
            )
        except InvalidExternalID as exc:
            raise NotFound("El identificador proporcionado no es válido.") from exc

        if not list_species_catalog_for_api().filter(pk=species_id).exists():
            raise NotFound("La especie solicitada no está disponible.")

        return list_media_for_api(include_unpublished=False).filter(
            specimen__species_id=species_id
        )
