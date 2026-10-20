from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from apps.collectors.models import Collector
from apps.common.api.ids import decode_query_id
from apps.locations.models import Location
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import READ_ROLES
from apps.specimens.api.serializers import SpecimenSerializer
from apps.specimens.selectors import search_specimens_for_api
from apps.taxonomy.models import Family, Genus, Species


@extend_schema(tags=["Especimenes"])
class SpecimenSearchView(ListAPIView):
    serializer_class = SpecimenSerializer
    permission_classes = [HasRolePermission]
    required_roles = READ_ROLES

    def get_queryset(self):
        params = dict(self.request.query_params.items())
        for key, model in (
            ("family", Family),
            ("genus", Genus),
            ("species", Species),
            ("collector", Collector),
            ("location", Location),
        ):
            decoded = decode_query_id(params, f"{key}_id", model)
            if decoded is None:
                decoded = decode_query_id(params, key, model)
            if decoded is not None:
                params[key] = decoded
        return search_specimens_for_api(params)
