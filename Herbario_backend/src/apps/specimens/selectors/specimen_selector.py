from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.specimens.models import Specimen


def list_specimens_for_api(*, include_unpublished: bool = False) -> QuerySet[Specimen]:
    qs = Specimen.objects.all()
    if not include_unpublished:
        qs = qs.filter(is_published=True)
    return (
        qs.select_related(
            "species",
            "species__genus",
            "species__genus__family",
            "collector",
        )
        .prefetch_related(
            "images__variants",
            "location_links__location",
            "location_links__climate",
            "location_links__habitat",
            "species__conservation_statuses__status",
        )
        .order_by("catalog_code")
    )


def get_specimen_by_id(specimen_id: int, *, include_unpublished: bool = False) -> Specimen | None:
    return (
        list_specimens_for_api(include_unpublished=include_unpublished)
        .filter(pk=specimen_id)
        .first()
    )


def search_specimens_for_api(
    params: dict, *, include_unpublished: bool = False
) -> QuerySet[Specimen]:
    qs = list_specimens_for_api(include_unpublished=include_unpublished)
    if query := params.get("q"):
        qs = qs.filter(
            Q(catalog_code__icontains=query)
            | Q(collection_number__icontains=query)
            | Q(morphological_description__icontains=query)
            | Q(species__name__icontains=query)
            | Q(species__genus__name__icontains=query)
            | Q(species__genus__family__name__icontains=query)
            | Q(species__common_names__common_name__icontains=query)
            | Q(collector__name__icontains=query)
            | Q(location_links__location__name__icontains=query)
        )
    if family := params.get("family"):
        qs = qs.filter(species__genus__family_id=family)
    if family_name := params.get("family_name"):
        qs = qs.filter(species__genus__family__name__icontains=family_name)
    if genus := params.get("genus"):
        qs = qs.filter(species__genus_id=genus)
    if genus_name := params.get("genus_name"):
        qs = qs.filter(species__genus__name__icontains=genus_name)
    if species := params.get("species"):
        qs = qs.filter(species_id=species)
    if species_name := params.get("species_name"):
        qs = qs.filter(species__name__icontains=species_name)
    if common_name := params.get("common_name"):
        qs = qs.filter(species__common_names__common_name__icontains=common_name)
    if collector := params.get("collector"):
        qs = qs.filter(collector_id=collector)
    if collector_name := params.get("collector_name"):
        qs = qs.filter(collector__name__icontains=collector_name)
    if location := params.get("location"):
        qs = qs.filter(location_links__location_id=location)
    if location_name := params.get("location_name"):
        qs = qs.filter(location_links__location__name__icontains=location_name)
    if collection := params.get("collection"):
        qs = qs.filter(collections__id=collection)
    if climate := params.get("climate"):
        qs = qs.filter(location_links__climate__name__icontains=climate)
    if habitat := params.get("habitat"):
        qs = qs.filter(location_links__habitat__name__icontains=habitat)
    if conservation := params.get("conservation_status"):
        qs = qs.filter(
            Q(species__conservation_statuses__status__code__icontains=conservation)
            | Q(species__conservation_statuses__status__name__icontains=conservation)
        )
    if date_from := params.get("collection_date_from"):
        qs = qs.filter(collection_date__gte=date_from)
    if date_to := params.get("collection_date_to"):
        qs = qs.filter(collection_date__lte=date_to)
    ordering = params.get("ordering", "catalog_code")
    allowed = {
        "catalog_code",
        "collection_date",
        "-catalog_code",
        "-collection_date",
        "species__name",
        "-species__name",
    }
    if ordering in allowed:
        qs = qs.order_by(ordering)
    return qs.distinct()
