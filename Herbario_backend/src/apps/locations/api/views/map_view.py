from __future__ import annotations

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.collectors.models import Collector
from apps.common.api.ids import decode_query_id
from apps.locations.api.serializers import MapPointSerializer
from apps.locations.selectors import list_map_points_for_api
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import READ_ROLES
from apps.taxonomy.models import Family, Genus, Species


@extend_schema(tags=["Ubicaciones"])
class MapPointsView(ListAPIView):
    serializer_class = MapPointSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles = READ_ROLES

    def get_queryset(self):
        qs = list_map_points_for_api()
        family_id = decode_query_id(self.request.query_params, "family_id", Family)
        genus_id = decode_query_id(self.request.query_params, "genus_id", Genus)
        species_id = decode_query_id(self.request.query_params, "species_id", Species)
        collector_id = decode_query_id(self.request.query_params, "collector_id", Collector)
        family_id = family_id or decode_query_id(self.request.query_params, "family", Family)
        genus_id = genus_id or decode_query_id(self.request.query_params, "genus", Genus)
        species_id = species_id or decode_query_id(self.request.query_params, "species", Species)
        collector_id = collector_id or decode_query_id(
            self.request.query_params, "collector", Collector
        )
        common_name = self.request.query_params.get("common_name")
        collector_name = self.request.query_params.get("collector_name")
        conservation = self.request.query_params.get("conservation_status")
        if family_id:
            qs = qs.filter(specimen__species__genus__family_id=family_id)
        if family_name := self.request.query_params.get("family_name"):
            qs = qs.filter(specimen__species__genus__family__name__icontains=family_name)
        if genus_id:
            qs = qs.filter(specimen__species__genus_id=genus_id)
        if genus_name := self.request.query_params.get("genus_name"):
            qs = qs.filter(specimen__species__genus__name__icontains=genus_name)
        if species_id:
            qs = qs.filter(specimen__species_id=species_id)
        if species_name := self.request.query_params.get("species_name"):
            qs = qs.filter(specimen__species__name__icontains=species_name)
        if common_name:
            qs = qs.filter(specimen__species__common_names__common_name__icontains=common_name)
        if collector_id:
            qs = qs.filter(specimen__collector_id=collector_id)
        if collector_name:
            qs = qs.filter(specimen__collector__name__icontains=collector_name)
        if conservation:
            qs = qs.filter(
                Q(specimen__species__conservation_statuses__status__code__icontains=conservation)
                | Q(specimen__species__conservation_statuses__status__name__icontains=conservation)
            )
        return qs.distinct()
