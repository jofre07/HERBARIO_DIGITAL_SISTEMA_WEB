from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import ExtractYear
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.collections_app.models import Collection
from apps.collectors.models import Collector
from apps.locations.models import Location
from apps.media.models import HerbariumImage
from apps.specimens.models import Specimen
from apps.specimens.publication import request_can_include_unpublished
from apps.taxonomy.models import Family, Genus, Species, Status


class DashboardChartPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.IntegerField()


class DashboardChartsSerializer(serializers.Serializer):
    specimens_by_family = DashboardChartPointSerializer(many=True)
    specimens_by_year = DashboardChartPointSerializer(many=True)
    species_by_conservation_status = DashboardChartPointSerializer(many=True)


class HerbariumStatsSerializer(serializers.Serializer):
    species = serializers.IntegerField()
    specimens = serializers.IntegerField()
    families = serializers.IntegerField()
    genera = serializers.IntegerField()
    images = serializers.IntegerField()
    collectors = serializers.IntegerField()
    locations = serializers.IntegerField()
    collections = serializers.IntegerField()
    users = serializers.IntegerField()
    charts = DashboardChartsSerializer()


def _dashboard_charts(*, include_unpublished: bool) -> dict[str, list[dict[str, str | int]]]:
    publication_filter = Q()
    status_publication_filter = Q()
    if not include_unpublished:
        publication_filter = Q(genera__species__specimens__is_published=True)
        status_publication_filter = Q(
            species_statuses__species__specimens__is_published=True
        )
    specimens_by_family = (
        Family.objects.annotate(
            total=Count(
                "genera__species__specimens",
                filter=Q(
                    genera__deleted=False,
                    genera__species__deleted=False,
                    genera__species__specimens__deleted=False,
                )
                & publication_filter,
                distinct=True,
            )
        )
        .filter(total__gt=0)
        .order_by("-total", "name")[:10]
    )
    specimens_by_year = (
        Specimen.objects.filter(
            Q() if include_unpublished else Q(is_published=True)
        )
        .exclude(collection_date__isnull=True)
        .annotate(year=ExtractYear("collection_date"))
        .values("year")
        .annotate(total=Count("id"))
        .order_by("year")
    )
    species_by_status = (
        Status.objects.annotate(
            total=Count(
                "species_statuses__species",
                filter=Q(
                    species_statuses__deleted=False,
                    species_statuses__species__deleted=False,
                )
                & status_publication_filter,
                distinct=True,
            )
        )
        .filter(total__gt=0)
        .order_by("-total", "code")
    )

    return {
        "specimens_by_family": [
            {"label": family.name, "value": family.total} for family in specimens_by_family
        ],
        "specimens_by_year": [
            {"label": str(row["year"]), "value": row["total"]} for row in specimens_by_year
        ],
        "species_by_conservation_status": [
            {"label": status.code, "value": status.total} for status in species_by_status
        ],
    }


@extend_schema(
    tags=["Sistema"],
    responses=HerbariumStatsSerializer,
)
class HerbariumStatsView(APIView):
    permission_classes = [IsAuthenticated]
    public_only = False

    def get(self, request):
        User = get_user_model()
        include_unpublished = False if self.public_only else request_can_include_unpublished(request)
        specimen_filter = Q()
        related_specimen_filter = Q()
        if not include_unpublished:
            specimen_filter = Q(is_published=True)
            related_specimen_filter = Q(specimens__is_published=True)
        return Response(
            {
                "species": Species.objects.filter(related_specimen_filter).distinct().count(),
                "specimens": Specimen.objects.filter(specimen_filter).count(),
                "families": Family.objects.filter(
                    Q() if include_unpublished else Q(
                        genera__species__specimens__is_published=True
                    )
                ).distinct().count(),
                "genera": Genus.objects.filter(
                    Q() if include_unpublished else Q(species__specimens__is_published=True)
                ).distinct().count(),
                "images": HerbariumImage.objects.filter(
                    Q() if include_unpublished else Q(specimen__is_published=True)
                ).count(),
                "collectors": Collector.objects.filter(related_specimen_filter).distinct().count(),
                "locations": Location.objects.filter(
                    specimen_links__specimen__deleted=False,
                    **({} if include_unpublished else {
                        "specimen_links__specimen__is_published": True
                    }),
                )
                .distinct()
                .count(),
                "collections": Collection.objects.filter(related_specimen_filter)
                .distinct()
                .count(),
                "users": User.objects.count(),
                "charts": _dashboard_charts(include_unpublished=include_unpublished),
            }
        )
