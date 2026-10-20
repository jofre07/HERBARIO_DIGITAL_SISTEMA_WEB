from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.collections_app.models import Collection
from apps.collectors.models import Collector
from apps.common.api.ids import decode_query_id
from apps.common.api.viewsets.mixins import EncodedLookupMixin
from apps.locations.models import Location
from apps.specimens.api.serializers import SpecimenSerializer
from apps.specimens.selectors import search_specimens_for_api
from apps.taxonomy.models import Family, Genus, Species


@extend_schema(tags=["Especimenes publicos"])
class PublicSpecimenViewSet(EncodedLookupMixin, viewsets.ReadOnlyModelViewSet):
    """Public, read-only access to published specimens."""

    serializer_class = SpecimenSerializer
    permission_classes = [AllowAny]
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
        return search_specimens_for_api(params, include_unpublished=False)
