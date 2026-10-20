from __future__ import annotations

from django.db.models import Count, Q, QuerySet

from apps.locations.models import ClimateHabitat, Location


def list_locations_for_api() -> QuerySet[Location]:
    return Location.objects.annotate(
        specimen_count=Count(
            "specimen_links",
            filter=Q(specimen_links__specimen__deleted=False),
        )
    ).order_by("name")


def list_climate_habitats_for_api() -> QuerySet[ClimateHabitat]:
    return ClimateHabitat.objects.select_related("location", "climate", "habitat").order_by("id")


def list_map_points_for_api() -> QuerySet:
    from apps.specimens.models import SpecimenLocation

    return (
        SpecimenLocation.objects.filter(
            specimen__deleted=False,
            specimen__is_published=True,
            location__deleted=False,
        )
        .select_related(
            "location",
            "climate",
            "habitat",
            "specimen",
            "specimen__collector",
            "specimen__species",
            "specimen__species__genus",
            "specimen__species__genus__family",
        )
        .prefetch_related(
            "specimen__images__variants",
            "specimen__species__common_names",
        )
        .order_by("specimen__catalog_code", "order")
    )
